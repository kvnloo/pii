#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import asdict, is_dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import httpx
import programasweights as paw


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compile the frozen PAW PII specification")
    parser.add_argument("--spec", type=Path, default=Path("specs/pii-detector-v1.txt"))
    parser.add_argument("--compiler", default="paw-4b-qwen3-0.6b")
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--name", default="PAW PII detector benchmark")
    parser.add_argument(
        "--timeout",
        type=float,
        default=120.0,
        help="HTTP timeout in seconds; finetune compiles may need 600",
    )
    return parser.parse_args()


def json_safe(value: Any) -> Any:
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if is_dataclass(value):
        return json_safe(asdict(value))
    if isinstance(value, dict):
        return {str(key): json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(item) for item in value]
    return str(value)


def main() -> None:
    args = parse_args()
    spec = args.spec.read_text(encoding="utf-8").strip()
    body = {
        "spec": spec,
        "compiler": args.compiler,
        "name": args.name,
        "tags": ["pii", "privacy", "extraction", "benchmark"],
        "public": False,
    }
    headers = {"Content-Type": "application/json"}
    api_key = paw.get_api_key()
    if api_key:
        headers["X-API-Key"] = api_key
    response = httpx.post(
        f"{paw.get_api_url()}/api/v1/compile",
        json=body,
        headers=headers,
        timeout=args.timeout,
    )
    response.raise_for_status()
    program = response.json()
    if program.get("status") != "ready":
        raise RuntimeError(f"compile failed: {program.get('error')}")

    manifest = {
        "created_at": datetime.now(UTC).isoformat(),
        "program_id": program["program_id"],
        "program_slug": program.get("slug"),
        "status": program["status"],
        "compiler": args.compiler,
        "compiler_snapshot": program.get("compiler_snapshot"),
        "compiler_kind": program.get("compiler_kind"),
        "runtime_id": program.get("runtime_id"),
        "timings": json_safe(program.get("timings")),
        "spec_path": str(args.spec),
        "spec_sha256": hashlib.sha256(spec.encode()).hexdigest(),
        "spec": spec,
    }
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
