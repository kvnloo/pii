from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import programasweights as paw

from .parsing import parse_paw_output
from .predictions import Detection


class PawDetector:
    def __init__(
        self,
        manifest_path: str | Path,
        *,
        n_ctx: int = 2048,
        n_gpu_layers: int = -1,
        max_tokens: int = 768,
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
            "backend": "paw",
            "program_id": self.program_id,
            "compiler": self.manifest.get("compiler"),
            "compiler_snapshot": self.manifest.get("compiler_snapshot"),
            "spec_sha256": self.manifest.get("spec_sha256"),
            "max_tokens": self.max_tokens,
        }

    def __call__(self, text: str) -> Detection:
        try:
            raw = self.function(text, max_tokens=self.max_tokens, temperature=0.0)
            parsed = parse_paw_output(text, raw)
            return Detection(
                spans=parsed.spans,
                raw_output=raw,
                malformed=parsed.malformed,
                unmatched_values=parsed.unmatched_values,
            )
        except Exception as exc:
            return Detection(spans=(), error=f"{type(exc).__name__}: {exc}")
