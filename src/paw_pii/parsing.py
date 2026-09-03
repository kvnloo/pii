from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any

from .types import Span

_JSON_STRING = r'"(?:\\.|[^"\\])*"'
_JSON_STRING_RE = re.compile(_JSON_STRING)
_TYPED_PAIR = re.compile(rf"\[\s*(?P<value>{_JSON_STRING})\s*,\s*(?P<label>{_JSON_STRING})\s*\]")


@dataclass(frozen=True)
class ParseResult:
    spans: tuple[Span, ...]
    malformed: bool = False
    unmatched_values: tuple[str, ...] = ()


def _extract_json(text: str) -> Any:
    cleaned = text.strip()
    fenced = re.fullmatch(r"```(?:json)?\s*(.*?)\s*```", cleaned, flags=re.DOTALL | re.I)
    if fenced:
        cleaned = fenced.group(1)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        left = cleaned.find("[")
        right = cleaned.rfind("]")
        if left >= 0 and right > left:
            return json.loads(cleaned[left : right + 1])
        raise


def _all_exact_occurrences(text: str, value: str) -> list[tuple[int, int]]:
    if not value:
        return []
    return [(match.start(), match.end()) for match in re.finditer(re.escape(value), text)]


def _extract_partial_typed_pairs(text: str) -> list[list[str]]:
    """Recover complete typed pairs when a later item makes the JSON invalid."""

    pairs: list[list[str]] = []
    for match in _TYPED_PAIR.finditer(text):
        try:
            value = json.loads(match.group("value"))
            label = json.loads(match.group("label"))
        except json.JSONDecodeError:
            continue
        pairs.append([value, label])
    return pairs


def _extract_partial_untyped_values(text: str) -> list[str]:
    """Recover complete strings from a truncated flat JSON array."""

    left = text.find("[")
    if left < 0:
        return []
    array_text = text[left:].lstrip()
    if array_text.startswith(("[[", "[{")):
        return []
    values: list[str] = []
    for match in _JSON_STRING_RE.finditer(array_text):
        try:
            value = json.loads(match.group(0))
        except json.JSONDecodeError:
            continue
        if isinstance(value, str):
            values.append(value)
    return values


def parse_paw_output(source: str, output: str) -> ParseResult:
    """Parse exact copied strings and map every occurrence back to source offsets."""

    partially_recovered = False
    try:
        payload = _extract_json(output)
    except (json.JSONDecodeError, TypeError, ValueError):
        payload = _extract_partial_typed_pairs(output)
        if not payload:
            payload = _extract_partial_untyped_values(output)
        if not payload:
            return ParseResult(spans=(), malformed=True)
        partially_recovered = True

    if not isinstance(payload, list):
        return ParseResult(spans=(), malformed=True)

    spans: set[Span] = set()
    unmatched: list[str] = []
    malformed = partially_recovered
    for item in payload:
        if isinstance(item, str):
            value = item
            label = "other_pii"
        elif isinstance(item, dict):
            value = item.get("text", item.get("value"))
            label = item.get("type", item.get("label", "other_pii"))
        elif isinstance(item, list) and len(item) == 2:
            value, label = item
        else:
            malformed = True
            continue

        if not isinstance(value, str) or not isinstance(label, str):
            malformed = True
            continue

        occurrences = _all_exact_occurrences(source, value)
        if not occurrences:
            unmatched.append(value)
            continue
        for start, end in occurrences:
            spans.add(Span(start=start, end=end, label=label, value=value))

    return ParseResult(
        spans=tuple(sorted(spans)),
        malformed=malformed,
        unmatched_values=tuple(unmatched),
    )
