from __future__ import annotations

from collections.abc import Sequence

from .types import Span


def merge_spans(spans: Sequence[Span]) -> tuple[tuple[int, int], ...]:
    merged: list[list[int]] = []
    for span in sorted(spans, key=lambda item: (item.start, item.end)):
        if not merged or span.start > merged[-1][1]:
            merged.append([span.start, span.end])
        else:
            merged[-1][1] = max(merged[-1][1], span.end)
    return tuple((start, end) for start, end in merged)


def redact_text(text: str, spans: Sequence[Span], placeholder: str = "[PII]") -> str:
    output = text
    for start, end in reversed(merge_spans(spans)):
        output = output[:start] + placeholder + output[end:]
    return output
