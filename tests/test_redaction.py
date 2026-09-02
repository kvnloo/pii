from paw_pii.redaction import merge_spans, redact_text
from paw_pii.types import Span


def test_redact_text_replaces_spans_from_right_to_left() -> None:
    text = "Alice: a@example.com"
    spans = (Span(0, 5), Span(7, 20))

    assert redact_text(text, spans) == "[PII]: [PII]"


def test_merge_spans_combines_overlaps() -> None:
    assert merge_spans((Span(1, 5), Span(4, 8), Span(10, 11))) == ((1, 8), (10, 11))
