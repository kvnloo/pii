#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import time
from dataclasses import asdict, is_dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import httpx
import programasweights as paw


class CompileCapacityError(RuntimeError):
    pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compile the frozen PAW PII specification")
    parser.add_argument("--spec", type=Path, default=Path("specs/pii-detector-v1.txt"))
    parser.add_argument("--compiler", default="paw-4b-qwen3-0.6b")
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--name", default="PAW PII detector benchmark")
    parser.add_argument(
        "--output-format",
        choices=("json_text_type", "json_type_text", "tsv_type_text"),
        default="json_text_type",
    )
    parser.add_argument(
        "--public",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="publish the compiled program (default: public)",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=900.0,
        help="overall timeout in seconds; finetune compiles may need several minutes",
    )
    parser.add_argument(
        "--async-compile",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="use the async compile queue (default: enabled for paw-ft compilers)",
    )
    parser.add_argument("--poll-interval", type=float, default=2.0)
    parser.add_argument(
        "--capacity-retry-interval",
        type=float,
        default=30.0,
        help="seconds between retries when all finetune compile slots are active",
    )
    parser.add_argument(
        "--resume-job",
        help="poll an existing async compile job instead of submitting a duplicate",
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


def compile_sync(
    api_url: str,
    body: dict[str, Any],
    headers: dict[str, str],
    timeout: float,
) -> dict[str, Any]:
    response = httpx.post(
        f"{api_url}/api/v1/compile",
        json=body,
        headers=headers,
        timeout=timeout,
    )
    response.raise_for_status()
    return response.json()


def compile_async(
    api_url: str,
    body: dict[str, Any],
    headers: dict[str, str],
    *,
    timeout: float,
    poll_interval: float,
) -> dict[str, Any]:
    response = httpx.post(
        f"{api_url}/api/v1/compile/async",
        json=body,
        headers=headers,
        timeout=min(timeout, 30.0),
    )
    if response.status_code == 429:
        raise CompileCapacityError(response.text)
    response.raise_for_status()
    submitted = response.json()
    job_id = submitted.get("job_id")
    if not isinstance(job_id, str) or not job_id:
        raise RuntimeError("async compile response did not contain a job_id")
    print(f"submitted async compile {job_id}", flush=True)

    return poll_async_job(
        api_url,
        job_id,
        headers,
        timeout=timeout,
        poll_interval=poll_interval,
        initial_status=submitted,
    )


def precheck_cached_program(
    api_url: str,
    body: dict[str, Any],
    headers: dict[str, str],
) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    response = httpx.post(
        f"{api_url}/api/v1/compile/precheck",
        json={"spec": body["spec"], "compiler": body["compiler"]},
        headers=headers,
        timeout=30.0,
    )
    response.raise_for_status()
    precheck = response.json()
    program_id = precheck.get("program_id") if precheck.get("cached") else None
    if not isinstance(program_id, str) or not program_id:
        return None, precheck
    detail_response = httpx.get(
        f"{api_url}/api/v1/programs/{program_id}",
        headers=headers,
        timeout=30.0,
    )
    detail_response.raise_for_status()
    details = detail_response.json()
    requested_public = bool(body["public"])
    cached_public = details.get("public")
    if requested_public and cached_public is False:
        visibility_response = httpx.patch(
            f"{api_url}/api/v1/programs/{program_id}",
            json={"public": True},
            headers=headers,
            timeout=30.0,
        )
        visibility_response.raise_for_status()
        details["public"] = True
    elif not requested_public and cached_public is True:
        raise RuntimeError(
            f"cached program {program_id} is already public; refusing to record it as private"
        )
    return {
        **details,
        "program_id": program_id,
        "status": "ready",
        "cached": True,
    }, precheck


def poll_async_job(
    api_url: str,
    job_id: str,
    headers: dict[str, str],
    *,
    timeout: float,
    poll_interval: float,
    initial_status: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Poll one already-submitted compile without creating another training job."""

    started = time.monotonic()
    last_reported: tuple[object, object] | None = None
    status: dict[str, Any] = initial_status or {"job_id": job_id, "status": "submitted"}
    while time.monotonic() - started < timeout:
        if last_reported is not None or initial_status is not None:
            time.sleep(max(0.25, poll_interval))
        try:
            poll = httpx.get(
                f"{api_url}/api/v1/compile/{job_id}",
                headers=headers,
                timeout=15.0,
            )
            poll.raise_for_status()
        except httpx.HTTPError:
            continue
        status = poll.json()
        marker = (status.get("status"), status.get("percent"))
        if marker != last_reported:
            percent = status.get("percent")
            progress = f" {100 * percent:.0f}%" if isinstance(percent, (int, float)) else ""
            queue = status.get("queue_length")
            queue_text = f" queue={queue}" if queue is not None else ""
            print(f"compile {status.get('status')}{progress}{queue_text}", flush=True)
            last_reported = marker
        if status.get("status") == "ready" and status.get("program_id"):
            program_id = str(status["program_id"])
            detail_response = httpx.get(
                f"{api_url}/api/v1/programs/{program_id}",
                headers=headers,
                timeout=30.0,
            )
            detail_response.raise_for_status()
            details = detail_response.json()
            return {
                **details,
                **status,
                "program_id": program_id,
                "status": "ready",
                "job_id": job_id,
            }
        if status.get("status") in {"failed", "cancelled"}:
            raise RuntimeError(f"compile failed: {status.get('error')}")
    raise TimeoutError(f"compile {job_id} did not finish within {timeout:.0f}s")


def main() -> None:
    args = parse_args()
    spec = args.spec.read_text(encoding="utf-8").strip()
    body = {
        "spec": spec,
        "compiler": args.compiler,
        "name": args.name,
        "tags": ["pii", "privacy", "extraction", "benchmark"],
        "public": args.public,
    }
    headers = {"Content-Type": "application/json"}
    api_key = paw.get_api_key()
    if api_key:
        headers["X-API-Key"] = api_key
    api_url = paw.get_api_url()
    use_async = (
        args.async_compile if args.async_compile is not None else args.compiler.startswith("paw-ft")
    )
    program, precheck = precheck_cached_program(api_url, body, headers)
    if program is not None:
        print(f"using cached program {program['program_id']}", flush=True)
    elif use_async:
        if args.resume_job:
            print(f"resuming async compile {args.resume_job}", flush=True)
            program = poll_async_job(
                api_url,
                args.resume_job,
                headers,
                timeout=args.timeout,
                poll_interval=args.poll_interval,
            )
        else:
            deadline = time.monotonic() + args.timeout
            while program is None:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise TimeoutError("no finetune compile capacity became available")
                try:
                    program = compile_async(
                        api_url,
                        body,
                        headers,
                        timeout=remaining,
                        poll_interval=args.poll_interval,
                    )
                except CompileCapacityError:
                    queue_length = precheck.get("queue_length")
                    wait = min(args.capacity_retry_interval, remaining)
                    print(
                        f"compile capacity full; queue={queue_length}; retrying in {wait:.0f}s",
                        flush=True,
                    )
                    time.sleep(wait)
                    program, precheck = precheck_cached_program(api_url, body, headers)
    else:
        if args.resume_job:
            raise ValueError("--resume-job requires async compilation")
        program = compile_sync(api_url, body, headers, args.timeout)
    if program.get("status") != "ready":
        raise RuntimeError(f"compile failed: {program.get('error')}")

    manifest = {
        "created_at": datetime.now(UTC).isoformat(),
        "program_id": program["program_id"],
        "program_slug": program.get("slug") or program.get("user_slug"),
        "job_id": program.get("job_id"),
        "status": program["status"],
        "public": bool(program.get("public", args.public)),
        "compiler": args.compiler,
        "compiler_snapshot": program.get("compiler_snapshot"),
        "compiler_kind": program.get("compiler_kind"),
        "runtime_id": program.get("runtime_id"),
        "base_program_id": program.get("base_program_id"),
        "cached": program.get("cached"),
        "timings": json_safe(program.get("timings")),
        "spec_path": str(args.spec),
        "spec_sha256": hashlib.sha256(spec.encode()).hexdigest(),
        "spec": spec,
        "output_format": args.output_format,
    }
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
