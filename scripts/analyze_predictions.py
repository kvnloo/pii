#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from paw_pii.io import read_documents
from paw_pii.metrics import character_counts
from paw_pii.types import Span


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Inspect the largest PII benchmark errors")
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


def positions(spans: tuple[Span, ...]) -> set[int]:
    return {
        position
        for span in spans
        for position in range(span.start, span.end)
    }


def span_view(span: Span, covered: set[int]) -> dict[str, object]:
    span_positions = set(range(span.start, span.end))
    overlap = len(span_positions & covered)
    return {
        "value": span.value,
        "label": span.label,
        "start": span.start,
        "end": span.end,
        "covered_fraction": overlap / len(span_positions),
    }


def main() -> None:
    args = parse_args()
    prediction_rows = read_predictions(args.predictions)
    errors: list[dict[str, object]] = []

    for document in read_documents(args.data):
        row = prediction_rows[document.id]
        predicted = tuple(Span.from_dict(span) for span in row.get("spans", []))
        counts = character_counts(document.text, document.spans, predicted)
        gold_positions = positions(document.spans)
        predicted_positions = positions(predicted)
        errors.append(
            {
                "id": document.id,
                "language": document.language,
                "error_characters": counts.false_negative + counts.false_positive,
                "false_negative": counts.false_negative,
                "false_positive": counts.false_positive,
                "text": document.text,
                "missed_or_partial_gold": [
                    span_view(span, predicted_positions)
                    for span in document.spans
                    if not set(range(span.start, span.end)) <= predicted_positions
                ],
                "false_or_partial_predictions": [
                    span_view(span, gold_positions)
                    for span in predicted
                    if not set(range(span.start, span.end)) <= gold_positions
                ],
                "raw_output": row.get("raw_output"),
            }
        )

    errors.sort(key=lambda item: int(item["error_characters"]), reverse=True)
    print(json.dumps(errors[: args.limit], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
