from __future__ import annotations

import json
import os
import random
import time
from pathlib import Path
from typing import Any

import httpx

from .parsing import parse_paw_output
from .predictions import Detection


class PawApiDetector:
    """Run a compiled PAW program through the remote generic inference API."""

    def __init__(
        self,
        manifest_path: str | Path,
        *,
        endpoint: str = "https://programasweights.com/api/v1/infer",
        api_key_env: str = "PAW_API_KEY",
        max_tokens: int = 768,
        timeout_seconds: float = 120.0,
        max_attempts: int = 10,
    ) -> None:
        self.manifest_path = Path(manifest_path)
        self.manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        self.program_id = str(self.manifest["program_id"])
        self.output_format = str(self.manifest.get("output_format", "json_text_type"))
        self.endpoint = endpoint
        self.max_tokens = max_tokens
        self.max_attempts = max_attempts
        api_key = os.environ.get(api_key_env, "").strip()
        headers = {"X-API-Key": api_key} if api_key else {}
        self.client = httpx.Client(
            headers=headers,
            timeout=timeout_seconds,
            follow_redirects=True,
        )

    @property
    def metadata(self) -> dict[str, Any]:
        return {
            "backend": "paw-api",
            "endpoint": self.endpoint,
            "program_id": self.program_id,
            "compiler": self.manifest.get("compiler"),
            "compiler_snapshot": self.manifest.get("compiler_snapshot"),
            "spec_sha256": self.manifest.get("spec_sha256"),
            "output_format": self.output_format,
            "max_tokens": self.max_tokens,
            "max_attempts": self.max_attempts,
        }

    def __call__(self, text: str) -> Detection:
        try:
            response: httpx.Response | None = None
            for attempt in range(1, self.max_attempts + 1):
                response = self.client.post(
                    self.endpoint,
                    json={
                        "program_id": self.program_id,
                        "input": text,
                        "max_tokens": self.max_tokens,
                        "temperature": 0,
                    },
                )
                if response.status_code not in {429, 502, 503, 504}:
                    break
                if attempt == self.max_attempts:
                    break
                retry_after = response.headers.get("Retry-After", "")
                try:
                    delay = float(retry_after)
                except ValueError:
                    delay = min(30.0, 0.5 * 2 ** (attempt - 1))
                time.sleep(max(0.0, delay) + random.uniform(0.0, 0.25))
            if response is None:
                raise RuntimeError("inference request was not attempted")
            response.raise_for_status()
            payload = response.json()
            raw = payload.get("output")
            if not isinstance(raw, str):
                raise ValueError("inference response did not contain a string output")
            parsed = parse_paw_output(text, raw, output_format=self.output_format)
            return Detection(
                spans=parsed.spans,
                raw_output=raw,
                malformed=parsed.malformed,
                unmatched_values=parsed.unmatched_values,
            )
        except Exception as exc:
            return Detection(spans=(), error=f"{type(exc).__name__}: {exc}")
