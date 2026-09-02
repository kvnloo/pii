#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from paw_pii.io import read_documents
from paw_pii.metrics import (
    character_counts,
    evaluate_documents,
    paired_bootstrap_f1_difference,
)
from paw_pii.types import Span


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compare PII predictions on identical documents")
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument(
        "--system",
        action="append",
        required=True,
        metavar="NAME=PATH",
        help="repeat for each predictions JSONL",
    )
    parser.add_argument("--reference", required=True, help="system name used for paired gaps")
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def read_prediction_map(path: Path) -> dict[str, tuple[Span, ...]]:
    rows: dict[str, tuple[Span, ...]] = {}
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            item = json.loads(line)
            rows[str(item["id"])] = tuple(Span.from_dict(span) for span in item["spans"])
    return rows


def main() -> None:
    args = parse_args()
    documents = list(read_documents(args.data))
    systems: dict[str, list[tuple[Span, ...]]] = {}
    for definition in args.system:
        if "=" not in definition:
            raise SystemExit(f"invalid --system {definition!r}; expected NAME=PATH")
        name, raw_path = definition.split("=", 1)
        prediction_map = read_prediction_map(Path(raw_path))
        missing = [document.id for document in documents if document.id not in prediction_map]
        if missing:
            raise SystemExit(f"{name} is missing {len(missing)} rows, starting with {missing[0]}")
        systems[name] = [prediction_map[document.id] for document in documents]
    if args.reference not in systems:
        raise SystemExit(f"unknown --reference {args.reference!r}")

    per_document: dict[str, list[Any]] = {
        name: [
            character_counts(document.text, document.spans, prediction)
            for document, prediction in zip(documents, predictions, strict=True)
        ]
        for name, predictions in systems.items()
    }
    report = {
        "data": str(args.data),
        "documents": len(documents),
        "systems": {
            name: evaluate_documents(documents, predictions).to_dict()
            for name, predictions in systems.items()
        },
        "paired_f1_difference_from_reference": {
            name: paired_bootstrap_f1_difference(
                per_document[args.reference],
                per_document[name],
            )
            for name in systems
            if name != args.reference
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
