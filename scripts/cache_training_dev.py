#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
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
    summarize_documents,
)
from paw_pii.io import write_documents
from paw_pii.types import Document


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Cache a small multilingual development set from training files"
    )
    parser.add_argument("--groups-per-language", type=int, default=5)
    parser.add_argument("--languages", nargs="+", default=list(DATASET_LANGUAGES))
    parser.add_argument("--revision", default=DATASET_REVISION)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def read_head_groups(language: str, groups: int, revision: str) -> list[Document]:
    url = hf_hub_url(
        DATASET_REPO,
        filename=TRAIN_FILES[language],
        repo_type="dataset",
        revision=revision,
    )
    selected: list[Document] = []
    selected_groups: list[str] = []
    with requests.get(url, stream=True, timeout=120) as response:
        response.raise_for_status()
        for raw_line in response.iter_lines(decode_unicode=True):
            if not raw_line:
                continue
            row = json.loads(raw_line)
            document = row_to_document(row)
            group = source_group(document.id)
            if group not in selected_groups:
                if len(selected_groups) >= groups:
                    break
                selected_groups.append(group)
            selected.append(document)
    if len(selected_groups) != groups:
        raise RuntimeError(f"{language}: requested {groups} groups, found {len(selected_groups)}")
    return selected


def main() -> None:
    args = parse_args()
    documents = [
        document
        for language in args.languages
        for document in read_head_groups(language, args.groups_per_language, args.revision)
    ]
    documents.sort(key=lambda document: (document.language or "", document.id))
    write_documents(args.output, documents)
    manifest = {
        "dataset": DATASET_REPO,
        "revision": args.revision,
        "split": "train",
        "selection": {
            "method": "first complete source groups in each language file",
            "groups_per_language": args.groups_per_language,
            "languages": args.languages,
        },
        "summary": summarize_documents(documents),
        "jsonl_sha256": hashlib.sha256(args.output.read_bytes()).hexdigest(),
    }
    args.output.with_suffix(args.output.suffix + ".manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
