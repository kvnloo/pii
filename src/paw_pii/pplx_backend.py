from __future__ import annotations

from pathlib import Path
from typing import Any

import torch
from transformers import AutoModel, AutoTokenizer

from .predictions import Detection
from .types import Span

PII_TRACER_REPO = "perplexity-ai/pplx-pii-masking"
PII_TRACER_REVISION = "f1f90a53823f5df0a1344c1e137d9fffdaab54d6"


def _resolve_device(requested: str) -> str:
    if requested != "auto":
        return requested
    if torch.cuda.is_available():
        return "cuda"
    if torch.backends.mps.is_available():
        return "mps"
    return "cpu"


class PiiTracerDetector:
    def __init__(self, model_dir: str | Path, *, device: str = "auto") -> None:
        self.model_dir = Path(model_dir).resolve()
        self.device = _resolve_device(device)
        self.model = AutoModel.from_pretrained(
            str(self.model_dir),
            trust_remote_code=True,
            local_files_only=True,
        )
        self.model.tokenizer = AutoTokenizer.from_pretrained(
            str(self.model_dir),
            trust_remote_code=True,
            local_files_only=True,
        )
        self.model.to(self.device)
        self.model.eval()

    @property
    def metadata(self) -> dict[str, Any]:
        return {
            "backend": "pplx-pii-tracer",
            "model_repo": PII_TRACER_REPO,
            "model_revision": PII_TRACER_REVISION,
            "model_dir": str(self.model_dir),
            "device": self.device,
        }

    def __call__(self, text: str) -> Detection:
        try:
            output = self.model.predict(text)
            raw_spans = output[0] if isinstance(output, tuple) else output
            spans = tuple(
                Span(
                    start=int(item.start),
                    end=int(item.end),
                    label=str(item.label),
                    value=text[int(item.start) : int(item.end)],
                ).validate(text)
                for item in raw_spans
            )
            return Detection(spans=spans)
        except Exception as exc:
            return Detection(spans=(), error=f"{type(exc).__name__}: {exc}")
