#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from paw_pii.io import read_documents
from paw_pii.metrics import evaluate_documents, evaluate_typed_documents
from paw_pii.paw_typing import PawSpanTyper
from paw_pii.types import Span


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Type cached PII detections with PAW")
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--extraction-predictions", type=Path, required=True)
    parser.add_argument("--type-program-manifest", type=Path, required=True)
    parser.add_argument("--predictions", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--max-documents", type=int, default=0)
    parser.add_argument("--progress-every", type=int, default=10)
    parser.add_argument("--paw-max-tokens", type=int, default=32)
    return parser.parse_args()


def read_rows(path: Path) -> dict[str, dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        return {
            str(row["id"]): row
            for line in handle
            if line.strip()
            for row in [json.loads(line)]
        }


def spans_from_row(row: dict[str, Any]) -> tuple[Span, ...]:
    return tuple(Span.from_dict(span) for span in row.get("spans", []))


def main() -> None:
    args = parse_args()
    documents = list(read_documents(args.data))
    if args.max_documents:
        documents = documents[: args.max_documents]
    extraction_rows = read_rows(args.extraction_predictions)
    cached = read_rows(args.predictions) if args.predictions.exists() else {}
    typer = PawSpanTyper(args.type_program_manifest, max_tokens=args.paw_max_tokens)

    args.predictions.parent.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    errors = malformed = 0
    with args.predictions.open("a", encoding="utf-8") as handle:
        for index, document in enumerate(documents, start=1):
            if document.id not in cached:
                extraction = extraction_rows.get(document.id)
                if extraction is None:
                    raise ValueError(f"missing extraction prediction for {document.id}")
                item_started = time.perf_counter()
                detection = typer(document.text, spans_from_row(extraction))
                row = detection.to_dict(document.id, time.perf_counter() - item_started)
                handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
                handle.flush()
                cached[document.id] = row
            row = cached[document.id]
            errors += bool(row.get("error"))
            malformed += bool(row.get("malformed"))
            if index % args.progress_every == 0 or index == len(documents):
                print(
                    f"{index}/{len(documents)} documents | "
                    f"{time.perf_counter() - started:.1f}s | "
                    f"errors={errors} malformed={malformed}",
                    flush=True,
                )

    ordered_rows = [cached[document.id] for document in documents]
    predictions = [spans_from_row(row) for row in ordered_rows]
    extraction_result = evaluate_documents(documents, predictions)
    typed_result = evaluate_typed_documents(documents, predictions)
    overlapping_characters = extraction_result.counts.true_positive
    inference_seconds = sum(float(row.get("elapsed_seconds", 0.0)) for row in ordered_rows)
    summary = {
        "created_at": datetime.now(UTC).isoformat(),
        "data": str(args.data),
        "extraction_predictions": str(args.extraction_predictions),
        "backend": typer.metadata,
        "metrics": {
            **extraction_result.to_dict(),
            "typed_character": typed_result.counts.to_dict(),
            "typed_exact_document_matches": typed_result.exact_document_matches,
            "typed_exact_document_accuracy": typed_result.exact_document_accuracy,
            "type_accuracy_on_overlapping_characters": (
                typed_result.counts.true_positive / overlapping_characters
                if overlapping_characters
                else 1.0
            ),
        },
        "diagnostics": {"errors": errors, "malformed_outputs": malformed},
        "timing": {
            "typing_inference_seconds": inference_seconds,
            "mean_typing_seconds_per_document": (
                inference_seconds / len(documents) if documents else 0.0
            ),
        },
        "predictions": str(args.predictions),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
