from __future__ import annotations

import json
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

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
    ) -> None:
        self.manifest_path = Path(manifest_path)
        self.manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        self.program_id = str(self.manifest["program_id"])
        self.max_tokens = max_tokens
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
        }

    def __call__(self, source: str, spans: tuple[Span, ...]) -> Detection:
        if not spans:
            return Detection(spans=())
        try:
            candidates = build_type_candidates(source, spans)
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
                replace(span, label=labels[index])
                for index, span in enumerate(spans)
            )
            return Detection(
                spans=typed_spans,
                raw_output=json.dumps(raw_outputs, ensure_ascii=False),
                malformed=malformed,
            )
        except Exception as exc:
            return Detection(spans=(), error=f"{type(exc).__name__}: {exc}")
