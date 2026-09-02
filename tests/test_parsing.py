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


def test_hallucinated_values_do_not_become_spans() -> None:
    result = parse_paw_output("Alice", '[{"text":"Bob","type":"private_person"}]')

    assert result.spans == ()
    assert result.unmatched_values == ("Bob",)
