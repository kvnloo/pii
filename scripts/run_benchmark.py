#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from paw_pii.io import read_documents
from paw_pii.metrics import diagnostic_breakdown, evaluate_documents, evaluate_typed_documents
from paw_pii.paw_backend import PawDetector
from paw_pii.pplx_backend import PiiTracerDetector
from paw_pii.predictions import Detector
from paw_pii.types import Span


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a local PII benchmark")
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--backend", choices=("paw", "pplx"), required=True)
    parser.add_argument("--model-dir", type=Path)
    parser.add_argument("--program-manifest", type=Path)
    parser.add_argument("--predictions", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--max-documents", type=int, default=0)
    parser.add_argument("--progress-every", type=int, default=25)
    parser.add_argument("--paw-max-tokens", type=int, default=768)
    parser.add_argument("--device", default="auto", help="pplx device: auto, cpu, mps, cuda")
    return parser.parse_args()


def build_detector(args: argparse.Namespace) -> Detector:
    if args.backend == "pplx":
        if args.model_dir is None:
            raise SystemExit("--model-dir is required for --backend pplx")
        return PiiTracerDetector(args.model_dir, device=args.device)
    if args.program_manifest is None:
        raise SystemExit("--program-manifest is required for --backend paw")
    return PawDetector(args.program_manifest, max_tokens=args.paw_max_tokens)


def read_cached_predictions(path: Path) -> dict[str, dict[str, Any]]:
    if not path.exists():
        return {}
    rows: dict[str, dict[str, Any]] = {}
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                row = json.loads(line)
                rows[str(row["id"])] = row
    return rows


def spans_from_prediction(row: dict[str, Any]) -> tuple[Span, ...]:
    return tuple(Span.from_dict(span) for span in row.get("spans", []))


def default_path(data: Path, backend: str, suffix: str) -> Path:
    return Path("results") / f"{data.stem}-{backend}.{suffix}"


def main() -> None:
    args = parse_args()
    documents = list(read_documents(args.data))
    if args.max_documents:
        documents = documents[: args.max_documents]
    detector = build_detector(args)
    predictions_path = args.predictions or default_path(args.data, args.backend, "jsonl")
    output_path = args.output or default_path(args.data, args.backend, "summary.json")
    predictions_path.parent.mkdir(parents=True, exist_ok=True)
    cached = read_cached_predictions(predictions_path)

    started = time.perf_counter()
    errors = malformed = unmatched = 0
    with predictions_path.open("a", encoding="utf-8") as handle:
        for index, document in enumerate(documents, start=1):
            if document.id not in cached:
                item_started = time.perf_counter()
                detection = detector(document.text)
                row = detection.to_dict(document.id, time.perf_counter() - item_started)
                handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
                handle.flush()
                cached[document.id] = row
            row = cached[document.id]
            errors += bool(row.get("error"))
            malformed += bool(row.get("malformed"))
            unmatched += len(row.get("unmatched_values", []))
            if index % args.progress_every == 0 or index == len(documents):
                elapsed = time.perf_counter() - started
                print(
                    f"{index}/{len(documents)} documents | {elapsed:.1f}s | "
                    f"errors={errors} malformed={malformed} unmatched={unmatched}",
                    flush=True,
                )

    ordered_rows = [cached[document.id] for document in documents]
    prediction_spans = [spans_from_prediction(row) for row in ordered_rows]
    result = evaluate_documents(documents, prediction_spans)
    typed_result = evaluate_typed_documents(documents, prediction_spans)
    overlapping_characters = result.counts.true_positive
    inference_seconds = sum(float(row.get("elapsed_seconds", 0.0)) for row in ordered_rows)
    summary = {
        "created_at": datetime.now(UTC).isoformat(),
        "data": str(args.data),
        "backend": detector.metadata,
        "metrics": {
            **result.to_dict(),
            "typed_character": typed_result.counts.to_dict(),
            "typed_exact_document_matches": typed_result.exact_document_matches,
            "typed_exact_document_accuracy": typed_result.exact_document_accuracy,
            "type_accuracy_on_overlapping_characters": (
                typed_result.counts.true_positive / overlapping_characters
                if overlapping_characters
                else 1.0
            ),
        },
        "diagnostic_breakdown": diagnostic_breakdown(documents, prediction_spans),
        "diagnostics": {
            "errors": errors,
            "malformed_outputs": malformed,
            "unmatched_values": unmatched,
        },
        "timing": {
            "inference_seconds": inference_seconds,
            "mean_seconds_per_document": inference_seconds / len(documents) if documents else 0.0,
        },
        "predictions": str(predictions_path),
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
