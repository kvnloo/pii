#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path

from paw_pii.dataset import DATASET_LANGUAGES, source_group, stable_priority, summarize_documents
from paw_pii.io import read_documents, write_documents
from paw_pii.types import Document


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create disjoint, language-balanced development and test samples"
    )
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--dev-groups-per-language", type=int, default=5)
    parser.add_argument("--test-groups-per-language", type=int, default=10)
    parser.add_argument("--languages", nargs="+", default=list(DATASET_LANGUAGES))
    parser.add_argument("--seed", default="paw-pii-v1-splits")
    parser.add_argument("--dev-output", type=Path, required=True)
    parser.add_argument("--test-output", type=Path, required=True)
    return parser.parse_args()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_manifest(
    path: Path,
    *,
    source: Path,
    split_name: str,
    documents: list[Document],
    groups: list[str],
    seed: str,
) -> None:
    manifest = {
        "source": str(source),
        "source_sha256": sha256_file(source),
        "split": split_name,
        "selection": "whole source groups ordered by sha256(seed + NUL + language/group)",
        "seed": seed,
        "groups": groups,
        "summary": summarize_documents(documents),
        "jsonl_sha256": sha256_file(path),
    }
    path.with_suffix(path.suffix + ".manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    args = parse_args()
    by_language_and_group: dict[str, dict[str, list[Document]]] = defaultdict(
        lambda: defaultdict(list)
    )
    for document in read_documents(args.input):
        if document.language in args.languages:
            by_language_and_group[document.language][source_group(document.id)].append(document)

    dev_documents: list[Document] = []
    test_documents: list[Document] = []
    dev_groups: list[str] = []
    test_groups: list[str] = []
    for language in args.languages:
        grouped = by_language_and_group[language]
        ordered = sorted(
            grouped,
            key=lambda group: (stable_priority(f"{language}/{group}", args.seed), group),
        )
        requested = args.dev_groups_per_language + args.test_groups_per_language
        if len(ordered) < requested:
            raise ValueError(f"{language} has only {len(ordered)} groups; need {requested}")
        language_dev = ordered[: args.dev_groups_per_language]
        language_test = ordered[args.dev_groups_per_language : requested]
        dev_groups.extend(f"{language}/{group}" for group in language_dev)
        test_groups.extend(f"{language}/{group}" for group in language_test)
        dev_documents.extend(document for group in language_dev for document in grouped[group])
        test_documents.extend(document for group in language_test for document in grouped[group])

    if set(dev_groups) & set(test_groups):
        raise AssertionError("development and test groups overlap")
    dev_documents.sort(key=lambda document: (document.language or "", document.id))
    test_documents.sort(key=lambda document: (document.language or "", document.id))
    write_documents(args.dev_output, dev_documents)
    write_documents(args.test_output, test_documents)
    write_manifest(
        args.dev_output,
        source=args.input,
        split_name="development",
        documents=dev_documents,
        groups=dev_groups,
        seed=args.seed,
    )
    write_manifest(
        args.test_output,
        source=args.input,
        split_name="held-out-test",
        documents=test_documents,
        groups=test_groups,
        seed=args.seed,
    )
    print(json.dumps({
        "development": summarize_documents(dev_documents),
        "held_out_test": summarize_documents(test_documents),
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
