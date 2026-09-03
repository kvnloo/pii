#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import heapq
import json
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

import requests
from huggingface_hub import hf_hub_url

from paw_pii.dataset import (
    DATASET_LANGUAGES,
    DATASET_REPO,
    DATASET_REVISION,
    TRAIN_FILES,
    row_to_document,
    source_group,
    stable_priority,
    summarize_documents,
)
from paw_pii.io import read_documents, write_documents
from paw_pii.types import Document


@dataclass(frozen=True)
class SelectedGroup:
    language: str
    group: str
    priority: int
    documents: tuple[Document, ...]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Cache fresh disjoint train groups for PAW PII search"
    )
    parser.add_argument("--exclude", type=Path, action="append", default=[])
    parser.add_argument("--search-groups-per-language", type=int, default=30)
    parser.add_argument("--selection-groups-per-language", type=int, default=30)
    parser.add_argument("--test-groups-per-language", type=int, default=30)
    parser.add_argument("--languages", nargs="+", default=list(DATASET_LANGUAGES))
    parser.add_argument("--seed", default="paw-pii-v2-fresh-groups")
    parser.add_argument("--revision", default=DATASET_REVISION)
    parser.add_argument("--search-output", type=Path, required=True)
    parser.add_argument("--selection-output", type=Path, required=True)
    parser.add_argument("--test-output", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    return parser.parse_args()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_excluded_groups(paths: list[Path]) -> dict[str, set[str]]:
    excluded: dict[str, set[str]] = defaultdict(set)
    for path in paths:
        for document in read_documents(path):
            if document.language:
                excluded[document.language].add(source_group(document.id))
    return excluded


def select_language_groups(
    language: str,
    *,
    count: int,
    excluded: set[str],
    seed: str,
    revision: str,
) -> list[SelectedGroup]:
    url = hf_hub_url(
        DATASET_REPO,
        filename=TRAIN_FILES[language],
        repo_type="dataset",
        revision=revision,
    )
    heap: list[tuple[int, str]] = []
    seen_groups: set[str] = set()
    selected_documents: dict[str, list[Document]] = {}
    rows = 0

    def consider(document: Document) -> None:
        group = source_group(document.id)
        if group in selected_documents:
            selected_documents[group].append(document)
            return
        if group in seen_groups:
            return
        seen_groups.add(group)
        if group in excluded:
            return

        priority = stable_priority(f"{language}/{group}", seed)
        candidate = (-priority, group)
        if len(heap) < count:
            heapq.heappush(heap, candidate)
            selected_documents[group] = [document]
        elif priority < -heap[0][0]:
            _, evicted_group = heapq.heapreplace(heap, candidate)
            del selected_documents[evicted_group]
            selected_documents[group] = [document]

    with requests.get(url, stream=True, timeout=(30, 300)) as response:
        response.raise_for_status()
        for raw_line in response.iter_lines(decode_unicode=True):
            if not raw_line:
                continue
            document = row_to_document(json.loads(raw_line))
            if document.language != language:
                raise ValueError(f"expected {language}, found {document.language} in {document.id}")
            consider(document)
            rows += 1
            if rows % 5000 == 0:
                print(f"{language}: scanned {rows} rows", flush=True)

    if len(heap) != count:
        raise ValueError(f"{language}: selected {len(heap)} groups, expected {count}")
    selected = [
        SelectedGroup(
            language=language,
            group=group,
            priority=-negative_priority,
            documents=tuple(selected_documents[group]),
        )
        for negative_priority, group in heap
    ]
    selected.sort(key=lambda item: (item.priority, item.group))
    print(f"{language}: selected {len(selected)} fresh groups from {rows} rows", flush=True)
    return selected


def flatten(groups: list[SelectedGroup]) -> list[Document]:
    documents = [document for group in groups for document in group.documents]
    return sorted(documents, key=lambda document: (document.language or "", document.id))


def main() -> None:
    args = parse_args()
    counts = {
        "search": args.search_groups_per_language,
        "selection": args.selection_groups_per_language,
        "sealed_test": args.test_groups_per_language,
    }
    total_groups = sum(counts.values())
    excluded = read_excluded_groups(args.exclude)
    partitions: dict[str, list[SelectedGroup]] = {name: [] for name in counts}

    for language in args.languages:
        selected = select_language_groups(
            language,
            count=total_groups,
            excluded=excluded.get(language, set()),
            seed=args.seed,
            revision=args.revision,
        )
        start = 0
        for name, count in counts.items():
            partitions[name].extend(selected[start : start + count])
            start += count

    group_sets = {
        name: {f"{group.language}/{group.group}" for group in groups}
        for name, groups in partitions.items()
    }
    names = list(group_sets)
    for index, first in enumerate(names):
        for second in names[index + 1 :]:
            if group_sets[first] & group_sets[second]:
                raise AssertionError(f"{first} and {second} overlap")

    outputs = {
        "search": args.search_output,
        "selection": args.selection_output,
        "sealed_test": args.test_output,
    }
    split_records: dict[str, object] = {}
    for name, output in outputs.items():
        documents = flatten(partitions[name])
        write_documents(output, documents)
        split_records[name] = {
            "path": str(output),
            "jsonl_sha256": sha256_file(output),
            "groups": sorted(group_sets[name]),
            "summary": summarize_documents(documents),
        }

    manifest = {
        "dataset": DATASET_REPO,
        "revision": args.revision,
        "seed": args.seed,
        "selection": "smallest sha256(seed + NUL + language/group) after excluded groups",
        "excluded": [
            {
                "path": str(path),
                "jsonl_sha256": sha256_file(path),
            }
            for path in args.exclude
        ],
        "groups_per_language": counts,
        "languages": args.languages,
        "splits": split_records,
    }
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
