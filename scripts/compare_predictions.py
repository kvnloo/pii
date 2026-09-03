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
    evaluate_typed_documents,
    paired_bootstrap_f1_difference,
    typed_character_counts,
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
    parser.add_argument("--details-limit", type=int, default=20)
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
    typed_per_document: dict[str, list[Any]] = {
        name: [
            typed_character_counts(document.text, document.spans, prediction)
            for document, prediction in zip(documents, predictions, strict=True)
        ]
        for name, predictions in systems.items()
    }
    report = {
        "data": str(args.data),
        "documents": len(documents),
        "systems": {
            name: {
                **evaluate_documents(documents, predictions).to_dict(),
                "typed_character": evaluate_typed_documents(
                    documents, predictions
                ).counts.to_dict(),
            }
            for name, predictions in systems.items()
        },
        "paired_f1_difference_from_reference": {
            name: paired_bootstrap_f1_difference(
                per_document[name],
                per_document[args.reference],
            )
            for name in systems
            if name != args.reference
        },
        "paired_typed_f1_difference_from_reference": {
            name: paired_bootstrap_f1_difference(
                typed_per_document[name],
                typed_per_document[args.reference],
            )
            for name in systems
            if name != args.reference
        },
        "largest_error_character_changes": {},
    }
    reference_rows = per_document[args.reference]
    for name, rows in per_document.items():
        if name == args.reference:
            continue
        changes = [
            {
                "id": document.id,
                "language": document.language,
                "improvement": (
                    reference.false_negative
                    + reference.false_positive
                    - candidate.false_negative
                    - candidate.false_positive
                ),
                "reference_fn": reference.false_negative,
                "reference_fp": reference.false_positive,
                "candidate_fn": candidate.false_negative,
                "candidate_fp": candidate.false_positive,
            }
            for document, reference, candidate in zip(
                documents, reference_rows, rows, strict=True
            )
        ]
        report["largest_error_character_changes"][name] = {
            "improvements": sorted(
                changes, key=lambda row: int(row["improvement"]), reverse=True
            )[: args.details_limit],
            "regressions": sorted(changes, key=lambda row: int(row["improvement"]))[
                : args.details_limit
            ],
        }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
