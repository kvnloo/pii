#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from paw_pii.io import read_documents
from paw_pii.metrics import typed_character_counts
from paw_pii.taxonomy import canonical_pii_type, require_pii_type
from paw_pii.types import Span


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Inspect one-pass typed PII errors")
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--predictions", type=Path, required=True)
    parser.add_argument("--limit", type=int, default=20)
    return parser.parse_args()


def read_predictions(path: Path) -> dict[str, dict[str, object]]:
    predictions: dict[str, dict[str, object]] = {}
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            row = json.loads(line)
            if not row.get("error"):
                predictions[str(row["id"])] = row
    return predictions


def overlap(first: Span, second: Span) -> int:
    return max(0, min(first.end, second.end) - max(first.start, second.start))


def main() -> None:
    args = parse_args()
    prediction_rows = read_predictions(args.predictions)
    rows: list[dict[str, object]] = []
    for document in read_documents(args.data):
        row = prediction_rows[document.id]
        predicted = tuple(Span.from_dict(item) for item in row.get("spans", []))
        counts = typed_character_counts(document.text, document.spans, predicted)
        mistakes: list[dict[str, object]] = []
        for gold in document.spans:
            gold_type = require_pii_type(gold.label)
            overlapping = [item for item in predicted if overlap(gold, item)]
            predicted_types = sorted(
                {
                    canonical_pii_type(item.label) or f"invalid:{item.label}"
                    for item in overlapping
                }
            )
            if gold_type not in predicted_types:
                mistakes.append(
                    {
                        "value": gold.value,
                        "source_label": gold.label,
                        "gold_type": gold_type,
                        "predicted_types": predicted_types,
                        "predicted_values": sorted(
                            {item.value for item in overlapping if item.value is not None}
                        ),
                    }
                )
        rows.append(
            {
                "id": document.id,
                "language": document.language,
                "typed_error_characters": counts.false_negative + counts.false_positive,
                "text": document.text,
                "mistakes": mistakes,
                "raw_output": row.get("raw_output"),
            }
        )

    rows.sort(key=lambda item: int(item["typed_error_characters"]), reverse=True)
    print(json.dumps(rows[: args.limit], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
