from paw_pii.metrics import (
    bootstrap_f1_interval,
    character_counts,
    diagnostic_breakdown,
    evaluate_documents,
    evaluate_typed_documents,
    paired_bootstrap_f1_difference,
    typed_character_counts,
)
from paw_pii.types import Document, Span


def test_character_counts_are_label_agnostic() -> None:
    text = "Email me at a@b.co today"
    gold = [Span(12, 18, "EMAIL", "a@b.co")]
    predicted = [Span(12, 18, "private_email", "a@b.co")]

    counts = character_counts(text, gold, predicted)

    assert counts.true_positive == 6
    assert counts.false_positive == 0
    assert counts.false_negative == 0
    assert counts.f1 == 1.0


def test_typed_character_counts_map_gold_taxonomy() -> None:
    text = "Email me at a@b.co today"
    gold = [Span(12, 18, "EMAIL", "a@b.co")]
    predicted = [Span(12, 18, "private_email", "a@b.co")]

    counts = typed_character_counts(text, gold, predicted)

    assert counts.true_positive == 6
    assert counts.false_positive == 0
    assert counts.false_negative == 0


def test_wrong_type_is_penalized_even_when_offsets_match() -> None:
    text = "Email me at a@b.co today"
    gold = [Span(12, 18, "EMAIL", "a@b.co")]
    predicted = [Span(12, 18, "private_person", "a@b.co")]

    counts = typed_character_counts(text, gold, predicted)

    assert counts.true_positive == 0
    assert counts.false_positive == 6
    assert counts.false_negative == 6


def test_typed_evaluation_maps_address_components_to_one_type() -> None:
    document = Document("1", "NY 12446", (Span(0, 2, "STATE"), Span(3, 8, "POSTCODE")))
    predicted = ((
        Span(0, 2, "private_address"),
        Span(3, 8, "private_address"),
    ),)

    result = evaluate_typed_documents([document], predicted)

    assert result.counts.f1 == 1.0
    assert result.exact_document_accuracy == 1.0


def test_overlapping_spans_count_each_character_once() -> None:
    text = "abcdefghij"
    counts = character_counts(
        text,
        [Span(1, 5), Span(4, 8)],
        [Span(2, 7)],
    )

    assert counts.true_positive == 5
    assert counts.false_positive == 0
    assert counts.false_negative == 2


def test_evaluate_requires_one_prediction_per_document() -> None:
    documents = [Document("1", "abc", (Span(0, 1),))]

    try:
        evaluate_documents(documents, [])
    except ValueError as exc:
        assert "fewer" in str(exc)
    else:
        raise AssertionError("expected a row-count error")


def test_diagnostic_breakdown_reports_language_and_label_recall() -> None:
    documents = [Document("1", "Alice", (Span(0, 5, "NAME"),), "English")]
    predictions = [(Span(0, 3, "other"),)]

    breakdown = diagnostic_breakdown(documents, predictions)

    assert breakdown["by_language"]["English"]["recall"] == 0.6
    assert breakdown["gold_character_recall_by_label"]["NAME"]["recall"] == 0.6


def test_bootstrap_is_reproducible() -> None:
    rows = [character_counts("abc", [Span(0, 2)], [Span(0, 1)])]

    assert bootstrap_f1_interval(rows, iterations=20) == bootstrap_f1_interval(
        rows, iterations=20
    )


def test_paired_bootstrap_reports_observed_difference() -> None:
    first = [character_counts("abc", [Span(0, 2)], [Span(0, 2)])]
    second = [character_counts("abc", [Span(0, 2)], [Span(0, 1)])]

    interval = paired_bootstrap_f1_difference(first, second, iterations=20)

    assert interval["estimate"] == 1.0 - 2 / 3
    assert interval["low"] == interval["high"] == interval["estimate"]
