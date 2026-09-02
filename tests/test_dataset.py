from paw_pii.dataset import deterministic_sample, row_to_document
from paw_pii.types import Document


def test_deterministic_sample_is_order_independent() -> None:
    documents = [Document(str(index), str(index), ()) for index in range(20)]

    forward = deterministic_sample(documents, limit=5, seed="x")
    backward = deterministic_sample(reversed(documents), limit=5, seed="x")

    assert [document.id for document in forward] == [document.id for document in backward]


def test_deterministic_sample_can_balance_languages() -> None:
    documents = [
        Document(f"en-{index}", "x", (), "English") for index in range(5)
    ] + [Document(f"fr-{index}", "x", (), "French") for index in range(5)]

    selected = deterministic_sample(
        documents,
        per_language=2,
        languages=("English", "French"),
    )

    assert [document.language for document in selected].count("English") == 2
    assert [document.language for document in selected].count("French") == 2


def test_dataset_offsets_are_authoritative_when_stored_value_is_wrong() -> None:
    document = row_to_document(
        {
            "id": "bad-value",
            "source_text": "hello Alice",
            "language": "English",
            "privacy_mask": [{"start": 6, "end": 11, "label": "NAME", "value": "Bob"}],
        }
    )

    assert document.spans[0].value == "Alice"
    assert document.metadata == {
        "source_value_mismatches": [
            {"start": 6, "end": 11, "stored_value": "Bob", "observed_value": "Alice"}
        ],
        "invalid_source_spans": [],
    }


def test_dataset_clips_out_of_bounds_span_and_records_it() -> None:
    document = row_to_document(
        {
            "id": "bad-offset",
            "source_text": "Alice",
            "language": "English",
            "privacy_mask": [{"start": 0, "end": 9, "label": "NAME", "value": "Alice Doe"}],
        }
    )

    assert document.spans[0].value == "Alice"
    assert document.metadata is not None
    assert document.metadata["invalid_source_spans"][0]["action"] == "clipped"
