#!/usr/bin/env python3
"""CLI entrypoints for detect/redact used by harness plugins and MCP."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .service import DEFAULT_PLACEHOLDER, DEFAULT_PROGRAM_ID, get_service


def _read_text(args: argparse.Namespace) -> str:
    if args.text is not None:
        return args.text
    if args.file is not None:
        return Path(args.file).read_text(encoding="utf-8")
    return sys.stdin.read()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="paw-pii",
        description="Detect and redact PII locally with the ProgramAsWeights neural program",
    )
    parser.add_argument(
        "--program-id",
        default=None,
        help=f"PAW program id (default env PAW_PII_PROGRAM_ID or {DEFAULT_PROGRAM_ID})",
    )
    parser.add_argument("--placeholder", default=DEFAULT_PLACEHOLDER)
    sub = parser.add_subparsers(dest="command", required=True)

    detect = sub.add_parser("detect", help="Detect PII spans")
    detect.add_argument("--text")
    detect.add_argument("--file", type=Path)
    detect.add_argument("--json", action="store_true", default=True)

    redact = sub.add_parser("redact", help="Redact PII from text")
    redact.add_argument("--text")
    redact.add_argument("--file", type=Path)
    redact.add_argument("--json", action="store_true", help="Emit structured JSON")

    messages = sub.add_parser("redact-messages", help="Redact string fields in a JSON message list")
    messages.add_argument("--file", type=Path, help="JSON file; stdin when omitted")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    service = get_service(program_id=args.program_id, placeholder=args.placeholder)

    if args.command == "detect":
        text = _read_text(args)
        result = service.detect(text)
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
        return 1 if result.error else 0

    if args.command == "redact":
        text = _read_text(args)
        result = service.detect(text)
        if args.json:
            print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
        else:
            print(result.redacted if not result.error else text, end="" if text.endswith("\n") else "\n")
        return 1 if result.error else 0

    if args.command == "redact-messages":
        raw = Path(args.file).read_text(encoding="utf-8") if args.file else sys.stdin.read()
        payload = json.loads(raw)
        if not isinstance(payload, list):
            raise SystemExit("redact-messages expects a JSON array of messages")
        print(json.dumps(service.redact_messages(payload), ensure_ascii=False, indent=2))
        return 0

    parser.error(f"unknown command {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
