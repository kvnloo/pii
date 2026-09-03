from __future__ import annotations

import json
import os
import random
import time
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

import httpx
import programasweights as paw

from .predictions import Detection
from .taxonomy import canonical_pii_type
from .types import Span


@dataclass(frozen=True)
class TypeCandidate:
    id: int
    text: str
    context: str


def build_type_candidates(
    source: str, spans: tuple[Span, ...], *, context_characters: int = 24
) -> tuple[TypeCandidate, ...]:
    candidates: list[TypeCandidate] = []
    for index, span in enumerate(spans):
        span.validate(source)
        candidates.append(
            TypeCandidate(
                id=index,
                text=source[span.start : span.end],
                context=(
                    source[max(0, span.start - context_characters) : span.start]
                    + "<PII>"
                    + source[span.start : span.end]
                    + "</PII>"
                    + source[span.end : min(len(source), span.end + context_characters)]
                ),
            )
        )
    return tuple(candidates)


def parse_type_label(output: str) -> str | None:
    candidate = output.strip().strip("`").strip()
    try:
        decoded = json.loads(candidate)
        if isinstance(decoded, str):
            candidate = decoded.strip()
    except json.JSONDecodeError:
        pass
    canonical = canonical_pii_type(candidate)
    return canonical


class PawSpanTyper:
    def __init__(
        self,
        manifest_path: str | Path,
        *,
        n_ctx: int = 2048,
        n_gpu_layers: int = -1,
        max_tokens: int = 32,
        context_characters: int = 24,
    ) -> None:
        self.manifest_path = Path(manifest_path)
        self.manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        self.program_id = str(self.manifest["program_id"])
        self.max_tokens = max_tokens
        self.context_characters = context_characters
        self.function = paw.function(
            self.program_id,
            n_ctx=n_ctx,
            n_gpu_layers=n_gpu_layers,
        )

    @property
    def metadata(self) -> dict[str, Any]:
        return {
            "backend": "paw-span-typer",
            "program_id": self.program_id,
            "compiler": self.manifest.get("compiler"),
            "compiler_snapshot": self.manifest.get("compiler_snapshot"),
            "spec_sha256": self.manifest.get("spec_sha256"),
            "max_tokens": self.max_tokens,
            "context_characters": self.context_characters,
        }

    def __call__(self, source: str, spans: tuple[Span, ...]) -> Detection:
        if not spans:
            return Detection(spans=())
        try:
            candidates = build_type_candidates(
                source, spans, context_characters=self.context_characters
            )
            raw_outputs: list[str] = []
            labels: list[str] = []
            malformed = False
            for candidate in candidates:
                raw = self.function(
                    candidate.context,
                    max_tokens=self.max_tokens,
                    temperature=0.0,
                )
                raw_outputs.append(raw)
                label = parse_type_label(raw)
                if label is None:
                    malformed = True
                    label = "other_pii"
                labels.append(label)
            typed_spans = tuple(
                replace(span, label=labels[index]) for index, span in enumerate(spans)
            )
            return Detection(
                spans=typed_spans,
                raw_output=json.dumps(raw_outputs, ensure_ascii=False),
                malformed=malformed,
            )
        except Exception as exc:
            return Detection(spans=(), error=f"{type(exc).__name__}: {exc}")


class PawApiSpanTyper:
    """Assign types through the hosted generic PAW inference endpoint."""

    def __init__(
        self,
        manifest_path: str | Path,
        *,
        endpoint: str = "https://programasweights.com/api/v1/infer",
        api_key_env: str = "PAW_API_KEY",
        max_tokens: int = 32,
        context_characters: int = 24,
        timeout_seconds: float = 120.0,
        max_attempts: int = 10,
    ) -> None:
        self.manifest_path = Path(manifest_path)
        self.manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        self.program_id = str(self.manifest["program_id"])
        self.endpoint = endpoint
        self.max_tokens = max_tokens
        self.context_characters = context_characters
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
            "backend": "paw-api-span-typer",
            "endpoint": self.endpoint,
            "program_id": self.program_id,
            "compiler": self.manifest.get("compiler"),
            "compiler_snapshot": self.manifest.get("compiler_snapshot"),
            "spec_sha256": self.manifest.get("spec_sha256"),
            "max_tokens": self.max_tokens,
            "context_characters": self.context_characters,
            "max_attempts": self.max_attempts,
        }

    def infer(self, text: str) -> str:
        response: httpx.Response | None = None
        for attempt in range(1, self.max_attempts + 1):
            response = self.client.post(
                self.endpoint,
                json={
                    "program_id": self.program_id,
                    "input": text,
                    "max_tokens": self.max_tokens,
                    "temperature": 0.0,
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
        output = payload.get("output")
        if not isinstance(output, str):
            raise ValueError("inference response did not contain a string output")
        return output

    def __call__(self, source: str, spans: tuple[Span, ...]) -> Detection:
        if not spans:
            return Detection(spans=())
        try:
            candidates = build_type_candidates(
                source, spans, context_characters=self.context_characters
            )
            raw_outputs: list[str] = []
            labels: list[str] = []
            malformed = False
            for candidate in candidates:
                raw = self.infer(candidate.context)
                raw_outputs.append(raw)
                label = parse_type_label(raw)
                if label is None:
                    malformed = True
                    label = "other_pii"
                labels.append(label)
            typed_spans = tuple(
                replace(span, label=labels[index]) for index, span in enumerate(spans)
            )
            return Detection(
                spans=typed_spans,
                raw_output=json.dumps(raw_outputs, ensure_ascii=False),
                malformed=malformed,
            )
        except Exception as exc:
            return Detection(spans=(), error=f"{type(exc).__name__}: {exc}")
