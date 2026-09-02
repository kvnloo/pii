#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from paw_pii.dataset import (
    DATASET_LANGUAGES,
    DATASET_REPO,
    DATASET_REVISION,
    HuggingFaceDatasetSource,
    deterministic_sample,
    summarize_documents,
)
from paw_pii.io import write_documents


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Cache a deterministic ai4privacy sample")
    parser.add_argument("--split", choices=("train", "validation"), required=True)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--limit", type=int, default=0, help="total rows; 0 means all")
    group.add_argument("--per-language", type=int, default=0)
    parser.add_argument("--languages", nargs="+", default=list(DATASET_LANGUAGES))
    parser.add_argument("--seed", default="paw-pii-v1")
    parser.add_argument("--revision", default=DATASET_REVISION)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    source = HuggingFaceDatasetSource(split=args.split, revision=args.revision)
    documents = deterministic_sample(
        source.stream(),
        limit=args.limit,
        per_language=args.per_language,
        languages=tuple(args.languages),
        seed=args.seed,
    )
    count = write_documents(args.output, documents)
    digest = hashlib.sha256(args.output.read_bytes()).hexdigest()
    manifest = {
        "dataset": DATASET_REPO,
        "revision": args.revision,
        "split": args.split,
        "selection": {
            "limit": args.limit,
            "per_language": args.per_language,
            "languages": args.languages,
            "seed": args.seed,
            "method": "smallest sha256(seed + NUL + row id)",
        },
        "jsonl_sha256": digest,
        "summary": summarize_documents(documents),
    }
    manifest_path = args.output.with_suffix(args.output.suffix + ".manifest.json")
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(f"wrote {count} documents to {args.output}")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
