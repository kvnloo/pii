#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from paw_pii.io import read_documents
from paw_pii.metrics import (
    diagnostic_breakdown,
    evaluate_documents,
    evaluate_typed_documents,
    typed_diagnostic_breakdown,
)
from paw_pii.paw_typing import PawApiSpanTyper, PawSpanTyper
from paw_pii.types import Span


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Type cached PII detections with PAW")
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--extraction-predictions", type=Path, required=True)
    parser.add_argument("--type-program-manifest", type=Path, required=True)
    parser.add_argument("--backend", choices=("paw", "paw-api"), default="paw")
    parser.add_argument("--predictions", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--max-documents", type=int, default=0)
    parser.add_argument("--progress-every", type=int, default=10)
    parser.add_argument("--paw-max-tokens", type=int, default=32)
    parser.add_argument("--context-characters", type=int, default=24)
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument(
        "--paw-api-url",
        default="https://programasweights.com/api/v1/infer",
    )
    parser.add_argument("--paw-api-key-env", default="PAW_API_KEY")
    return parser.parse_args()


def read_rows(path: Path) -> dict[str, dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        return {
            str(row["id"]): row
            for line in handle
            if line.strip()
            for row in [json.loads(line)]
            if not row.get("error")
        }


def spans_from_row(row: dict[str, Any]) -> tuple[Span, ...]:
    return tuple(Span.from_dict(span) for span in row.get("spans", []))


def run_typing(
    typer: PawSpanTyper | PawApiSpanTyper,
    document_id: str,
    text: str,
    spans: tuple[Span, ...],
) -> dict[str, Any]:
    started = time.perf_counter()
    detection = typer(text, spans)
    return detection.to_dict(document_id, time.perf_counter() - started)


def main() -> None:
    args = parse_args()
    documents = list(read_documents(args.data))
    if args.max_documents:
        documents = documents[: args.max_documents]
    extraction_rows = read_rows(args.extraction_predictions)
    cached = read_rows(args.predictions) if args.predictions.exists() else {}
    if args.backend == "paw-api":
        typer: PawSpanTyper | PawApiSpanTyper = PawApiSpanTyper(
            args.type_program_manifest,
            endpoint=args.paw_api_url,
            api_key_env=args.paw_api_key_env,
            max_tokens=args.paw_max_tokens,
            context_characters=args.context_characters,
        )
    else:
        typer = PawSpanTyper(
            args.type_program_manifest,
            max_tokens=args.paw_max_tokens,
            context_characters=args.context_characters,
        )

    args.predictions.parent.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    with args.predictions.open("a", encoding="utf-8") as handle:
        missing = [document for document in documents if document.id not in cached]
        if args.workers > 1:
            if args.backend != "paw-api":
                raise SystemExit("--workers greater than 1 requires --backend paw-api")
            with ThreadPoolExecutor(max_workers=args.workers) as executor:
                futures = {}
                for document in missing:
                    extraction = extraction_rows.get(document.id)
                    if extraction is None:
                        raise ValueError(f"missing extraction prediction for {document.id}")
                    futures[
                        executor.submit(
                            run_typing,
                            typer,
                            document.id,
                            document.text,
                            spans_from_row(extraction),
                        )
                    ] = document
                for completed, future in enumerate(as_completed(futures), start=1):
                    document = futures[future]
                    row = future.result()
                    handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
                    handle.flush()
                    cached[document.id] = row
                    if completed % args.progress_every == 0 or completed == len(missing):
                        print(
                            f"{completed}/{len(missing)} new documents | "
                            f"{time.perf_counter() - started:.1f}s",
                            flush=True,
                        )
        else:
            for index, document in enumerate(missing, start=1):
                extraction = extraction_rows.get(document.id)
                if extraction is None:
                    raise ValueError(f"missing extraction prediction for {document.id}")
                row = run_typing(
                    typer,
                    document.id,
                    document.text,
                    spans_from_row(extraction),
                )
                handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
                handle.flush()
                cached[document.id] = row
                if index % args.progress_every == 0 or index == len(missing):
                    print(
                        f"{index}/{len(missing)} new documents | "
                        f"{time.perf_counter() - started:.1f}s",
                        flush=True,
                    )

    ordered_rows = [cached[document.id] for document in documents]
    errors = sum(bool(row.get("error")) for row in ordered_rows)
    malformed = sum(bool(row.get("malformed")) for row in ordered_rows)
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
        "diagnostic_breakdown": diagnostic_breakdown(documents, predictions),
        "typed_diagnostic_breakdown": typed_diagnostic_breakdown(documents, predictions),
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
