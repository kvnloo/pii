#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from paw_pii.paw_backend import PawDetector
from paw_pii.redaction import redact_text


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Redact text with a local PAW PII program")
    parser.add_argument("--program-manifest", type=Path, required=True)
    parser.add_argument("--text", help="text to scan; reads stdin when omitted")
    parser.add_argument("--placeholder", default="[PII]")
    parser.add_argument("--json", action="store_true", help="emit structured output")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    text = args.text if args.text is not None else sys.stdin.read()
    detector = PawDetector(args.program_manifest)
    detection = detector(text)
    if detection.error:
        raise SystemExit(detection.error)
    redacted = redact_text(text, detection.spans, args.placeholder)
    if args.json:
        print(json.dumps({
            "redacted": redacted,
            "values": [span.value for span in detection.spans],
            "malformed_model_output": detection.malformed,
            "unmatched_model_values": list(detection.unmatched_values),
        }, ensure_ascii=False, indent=2))
    else:
        print(redacted)


if __name__ == "__main__":
    main()
