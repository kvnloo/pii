from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any

from .types import Span


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


def parse_paw_output(source: str, output: str) -> ParseResult:
    """Parse exact copied strings and map every occurrence back to source offsets."""

    try:
        payload = _extract_json(output)
    except (json.JSONDecodeError, TypeError, ValueError):
        return ParseResult(spans=(), malformed=True)

    if not isinstance(payload, list):
        return ParseResult(spans=(), malformed=True)

    spans: set[Span] = set()
    unmatched: list[str] = []
    malformed = False
    for item in payload:
        if isinstance(item, str):
            value = item
            label = "other_pii"
        elif isinstance(item, dict):
            value = item.get("text", item.get("value"))
            label = item.get("type", item.get("label", "other_pii"))
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
