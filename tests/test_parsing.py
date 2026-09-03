from paw_pii.parsing import parse_paw_output


def test_parse_json_objects_and_repeated_values() -> None:
    source = "Call 555-0100. Again: 555-0100."
    result = parse_paw_output(
        source,
        '[{"text":"555-0100","type":"private_phone"}]',
    )

    assert not result.malformed
    assert [(span.start, span.end) for span in result.spans] == [(5, 13), (22, 30)]


def test_parse_fenced_json() -> None:
    result = parse_paw_output("Alice", '```json\n["Alice"]\n```')

    assert len(result.spans) == 1
    assert result.spans[0].value == "Alice"


def test_parse_compact_typed_pairs() -> None:
    source = "Maya: maya@example.com"
    result = parse_paw_output(
        source,
        '[["Maya","private_person"],["maya@example.com","private_email"]]',
    )

    assert not result.malformed
    assert [(span.value, span.label) for span in result.spans] == [
        ("Maya", "private_person"),
        ("maya@example.com", "private_email"),
    ]


def test_parse_compact_label_first_pairs() -> None:
    source = "Maya: maya@example.com"
    result = parse_paw_output(
        source,
        '[["private_person","Maya"],["private_email","maya@example.com"]]',
        output_format="json_type_text",
    )

    assert not result.malformed
    assert [(span.value, span.label) for span in result.spans] == [
        ("Maya", "private_person"),
        ("maya@example.com", "private_email"),
    ]


def test_parse_label_first_tsv_without_stripping_values() -> None:
    source = "Name:  Maya \nEmail: maya@example.com"
    result = parse_paw_output(
        source,
        "private_person\t Maya \nprivate_email\tmaya@example.com",
        output_format="tsv_type_text",
    )

    assert not result.malformed
    assert [(span.value, span.label) for span in result.spans] == [
        (" Maya ", "private_person"),
        ("maya@example.com", "private_email"),
    ]


def test_parse_label_first_tsv_none_and_malformed_line() -> None:
    assert parse_paw_output("No PII", "NONE", output_format="tsv_type_text").spans == ()

    result = parse_paw_output(
        "Alice",
        "private_person\tAlice\nnot a row",
        output_format="tsv_type_text",
    )
    assert result.malformed
    assert [span.value for span in result.spans] == ["Alice"]


def test_parse_label_first_tsv_preserves_final_value_spaces() -> None:
    result = parse_paw_output(
        "Name: Alice ",
        "private_person\tAlice ",
        output_format="tsv_type_text",
    )

    assert not result.malformed
    assert [span.value for span in result.spans] == ["Alice "]


def test_hallucinated_values_do_not_become_spans() -> None:
    result = parse_paw_output("Alice", '[{"text":"Bob","type":"private_person"}]')

    assert result.spans == ()
    assert result.unmatched_values == ("Bob",)


def test_recover_complete_pairs_before_truncated_json() -> None:
    source = "Alice at 10:30"
    result = parse_paw_output(
        source,
        '[["Alice","private_person"],["10:30","private_date"],["broken',
    )

    assert result.malformed
    assert [(span.value, span.label) for span in result.spans] == [
        ("Alice", "private_person"),
        ("10:30", "private_date"),
    ]


def test_recover_complete_strings_before_truncated_json() -> None:
    source = "Alice at 10:30"
    result = parse_paw_output(source, '["Alice","10:30","broken')

    assert result.malformed
    assert [(span.value, span.label) for span in result.spans] == [
        ("Alice", "other_pii"),
        ("10:30", "other_pii"),
    ]


def test_do_not_treat_truncated_typed_pair_labels_as_values() -> None:
    result = parse_paw_output("Alice", '[["Alice","private_person"')

    assert result.malformed
    assert result.spans == ()
