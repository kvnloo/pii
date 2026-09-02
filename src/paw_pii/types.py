from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True, order=True)
class Span:
    """A half-open character span."""

    start: int
    end: int
    label: str = "pii"
    value: str | None = None

    def validate(self, text: str) -> Span:
        if self.start < 0 or self.end <= self.start or self.end > len(text):
            raise ValueError(f"invalid span [{self.start}, {self.end}) for {len(text)} chars")
        if self.value is not None and text[self.start : self.end] != self.value:
            raise ValueError("span value does not match source text")
        return self

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> Span:
        return cls(
            start=int(value["start"]),
            end=int(value["end"]),
            label=str(value.get("label", "pii")),
            value=value.get("value"),
        )


@dataclass(frozen=True)
class Document:
    id: str
    text: str
    spans: tuple[Span, ...]
    language: str | None = None
    metadata: dict[str, Any] | None = None

    def validate(self) -> Document:
        for span in self.spans:
            span.validate(self.text)
        return self

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "text": self.text,
            "language": self.language,
            "metadata": self.metadata,
            "spans": [span.to_dict() for span in self.spans],
        }

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> Document:
        return cls(
            id=str(value["id"]),
            text=str(value["text"]),
            language=value.get("language"),
            metadata=value.get("metadata"),
            spans=tuple(Span.from_dict(span) for span in value.get("spans", [])),
        ).validate()
