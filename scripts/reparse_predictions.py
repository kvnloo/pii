#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from paw_pii.io import read_documents
from paw_pii.parsing import parse_paw_output


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Reparse cached PAW raw outputs")
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--predictions", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    documents = {document.id: document for document in read_documents(args.data)}
    rows: dict[str, dict[str, object]] = {}
    with args.predictions.open(encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            row = json.loads(line)
            if row.get("error"):
                continue
            rows[str(row["id"])] = row

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as handle:
        for document_id, document in documents.items():
            row = rows[document_id]
            raw_output = row.get("raw_output")
            if not isinstance(raw_output, str):
                raise ValueError(f"prediction {document_id} has no raw output")
            parsed = parse_paw_output(document.text, raw_output)
            updated = {
                **row,
                "spans": [span.to_dict() for span in parsed.spans],
                "malformed": parsed.malformed,
                "unmatched_values": list(parsed.unmatched_values),
            }
            handle.write(json.dumps(updated, ensure_ascii=False, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
