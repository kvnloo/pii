"""High-level local PII detect + redact service for harness plugins."""

from __future__ import annotations

import json
import os
import threading
from dataclasses import dataclass
from functools import lru_cache
from typing import Any, Sequence

from .parsing import parse_paw_output
from .redaction import redact_text
from .taxonomy import PII_TYPES
from .types import Span

DEFAULT_PROGRAM_ID = "73a0e38b8bbe3427cd1d"
DEFAULT_PLACEHOLDER = "[PII]"


def _import_paw() -> Any:
    import programasweights as paw

    return paw


@dataclass(frozen=True)
class RedactionResult:
    text: str
    redacted: str
    spans: tuple[Span, ...]
    raw_output: str = ""
    malformed: bool = False
    unmatched_values: tuple[str, ...] = ()
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "text": self.text,
            "redacted": self.redacted,
            "spans": [span.to_dict() for span in self.spans],
            "raw_output": self.raw_output,
            "malformed": self.malformed,
            "unmatched_values": list(self.unmatched_values),
            "error": self.error,
            "types": list(PII_TYPES),
        }


class LocalPiiService:
    """Lazy-loaded PAW program wrapper. Thread-safe for concurrent redact calls."""

    def __init__(
        self,
        program_id: str | None = None,
        *,
        placeholder: str = DEFAULT_PLACEHOLDER,
        n_ctx: int = 2048,
        n_gpu_layers: int = -1,
        max_tokens: int = 768,
    ) -> None:
        self.program_id = program_id or os.environ.get("PAW_PII_PROGRAM_ID", DEFAULT_PROGRAM_ID)
        self.placeholder = placeholder
        self.n_ctx = n_ctx
        self.n_gpu_layers = n_gpu_layers
        self.max_tokens = max_tokens
        self._lock = threading.Lock()
        self._fn: Any | None = None

    def _function(self) -> Any:
        if self._fn is not None:
            return self._fn
        with self._lock:
            if self._fn is None:
                paw = _import_paw()
                self._fn = paw.function(
                    self.program_id,
                    n_ctx=self.n_ctx,
                    n_gpu_layers=self.n_gpu_layers,
                )
        return self._fn

    def detect(self, text: str) -> RedactionResult:
        if not text:
            return RedactionResult(text=text, redacted=text, spans=())
        try:
            raw = self._function()(text, max_tokens=self.max_tokens, temperature=0.0)
            parsed = parse_paw_output(text, raw, output_format="json_text_type")
            redacted = redact_text(text, parsed.spans, self.placeholder)
            return RedactionResult(
                text=text,
                redacted=redacted,
                spans=parsed.spans,
                raw_output=raw if isinstance(raw, str) else json.dumps(raw),
                malformed=parsed.malformed,
                unmatched_values=parsed.unmatched_values,
            )
        except Exception as exc:  # noqa: BLE001 — surface to callers as structured error
            return RedactionResult(
                text=text,
                redacted=text,
                spans=(),
                error=f"{type(exc).__name__}: {exc}",
            )

    def redact(self, text: str, *, placeholder: str | None = None) -> str:
        result = self.detect(text)
        if result.error:
            return text
        if placeholder is None or placeholder == self.placeholder:
            return result.redacted
        return redact_text(text, result.spans, placeholder)

    def redact_messages(
        self,
        messages: Sequence[dict[str, Any]],
        *,
        content_keys: Sequence[str] = ("content", "text"),
    ) -> list[dict[str, Any]]:
        """Best-effort recursive string redaction over chat-style message dicts."""

        out: list[dict[str, Any]] = []
        for message in messages:
            out.append(self._redact_value(message, content_keys=content_keys))  # type: ignore[arg-type]
        return out

    def _redact_value(self, value: Any, *, content_keys: Sequence[str]) -> Any:
        if isinstance(value, str):
            return self.redact(value)
        if isinstance(value, list):
            return [self._redact_value(item, content_keys=content_keys) for item in value]
        if isinstance(value, dict):
            result: dict[str, Any] = {}
            for key, item in value.items():
                if key in content_keys or isinstance(item, (str, list, dict)):
                    result[key] = self._redact_value(item, content_keys=content_keys)
                else:
                    result[key] = item
            return result
        return value


@lru_cache(maxsize=4)
def get_service(
    program_id: str | None = None,
    placeholder: str = DEFAULT_PLACEHOLDER,
) -> LocalPiiService:
    return LocalPiiService(program_id=program_id, placeholder=placeholder)
