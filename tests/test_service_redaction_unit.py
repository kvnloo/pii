"""Unit tests that do not require the PAW runtime model download."""

from __future__ import annotations

from paw_pii.redaction import merge_spans, redact_text
from paw_pii.types import Span


def test_merge_and_redact_overlapping_spans() -> None:
    text = "Ada Lovelace lives at 1 Infinite Loop"
    spans = (
        Span(0, 3, "private_person", "Ada"),
        Span(0, 12, "private_person", "Ada Lovelace"),
        Span(22, 38, "private_address", "1 Infinite Loop"),
    )
    assert merge_spans(spans) == ((0, 12), (22, 38))
    assert redact_text(text, spans, "[PII]") == "[PII] lives at [PII]"


def test_redact_preserves_non_pii() -> None:
    text = "no secrets here"
    assert redact_text(text, (), "[X]") == text
