from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from .types import Span


@dataclass(frozen=True)
class Detection:
    spans: tuple[Span, ...]
    raw_output: str | None = None
    malformed: bool = False
    unmatched_values: tuple[str, ...] = ()
    error: str | None = None

    def to_dict(self, document_id: str, elapsed_seconds: float) -> dict[str, Any]:
        return {
            "id": document_id,
            "spans": [span.to_dict() for span in self.spans],
            "raw_output": self.raw_output,
            "malformed": self.malformed,
            "unmatched_values": list(self.unmatched_values),
            "error": self.error,
            "elapsed_seconds": elapsed_seconds,
        }


class Detector(Protocol):
    @property
    def metadata(self) -> dict[str, Any]: ...

    def __call__(self, text: str) -> Detection: ...
