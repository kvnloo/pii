from paw_pii.paw_typing import (
    build_type_candidates,
    parse_type_label,
)
from paw_pii.types import Span


def test_candidates_include_local_context_and_stable_ids() -> None:
    source = "Email Maya at maya@example.com today"
    spans = (Span(6, 10, value="Maya"), Span(14, 30, value="maya@example.com"))

    candidates = build_type_candidates(source, spans, context_characters=6)

    assert candidates[0].id == 0
    assert candidates[0].text == "Maya"
    assert candidates[0].context == "Email <PII>Maya</PII> at ma"
    assert candidates[1].id == 1


def test_type_parser_accepts_plain_or_json_string_labels() -> None:
    assert parse_type_label("private_person") == "private_person"
    assert parse_type_label('"private_email"') == "private_email"
    assert parse_type_label("private_country") == "private_address"


def test_type_parser_rejects_unknown_or_explanatory_output() -> None:
    assert parse_type_label("name") is None
    assert parse_type_label("The type is private_person") is None
