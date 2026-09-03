from __future__ import annotations

import random
from collections import defaultdict
from collections.abc import Iterable, Sequence
from dataclasses import asdict, dataclass

from .taxonomy import canonical_pii_type, require_pii_type
from .types import Document, Span


@dataclass
class CharacterCounts:
    true_positive: int = 0
    false_positive: int = 0
    false_negative: int = 0

    @property
    def precision(self) -> float:
        denominator = self.true_positive + self.false_positive
        return self.true_positive / denominator if denominator else 1.0

    @property
    def recall(self) -> float:
        denominator = self.true_positive + self.false_negative
        return self.true_positive / denominator if denominator else 1.0

    @property
    def f1(self) -> float:
        denominator = self.precision + self.recall
        return 2 * self.precision * self.recall / denominator if denominator else 0.0

    def add(self, other: CharacterCounts) -> None:
        self.true_positive += other.true_positive
        self.false_positive += other.false_positive
        self.false_negative += other.false_negative

    def to_dict(self) -> dict[str, int | float]:
        return {
            **asdict(self),
            "precision": self.precision,
            "recall": self.recall,
            "f1": self.f1,
        }


@dataclass(frozen=True)
class EvaluationResult:
    counts: CharacterCounts
    documents: int
    documents_with_pii: int
    exact_document_matches: int

    @property
    def exact_document_accuracy(self) -> float:
        return self.exact_document_matches / self.documents if self.documents else 0.0

    def to_dict(self) -> dict[str, int | float | dict[str, int | float]]:
        return {
            "character": self.counts.to_dict(),
            "documents": self.documents,
            "documents_with_pii": self.documents_with_pii,
            "exact_document_matches": self.exact_document_matches,
            "exact_document_accuracy": self.exact_document_accuracy,
        }


def _character_positions(text: str, spans: Sequence[Span]) -> set[int]:
    positions: set[int] = set()
    for span in spans:
        span.validate(text)
        positions.update(range(span.start, span.end))
    return positions


def character_counts(text: str, gold: Sequence[Span], predicted: Sequence[Span]) -> CharacterCounts:
    gold_positions = _character_positions(text, gold)
    predicted_positions = _character_positions(text, predicted)
    return CharacterCounts(
        true_positive=len(gold_positions & predicted_positions),
        false_positive=len(predicted_positions - gold_positions),
        false_negative=len(gold_positions - predicted_positions),
    )


def _typed_character_positions(
    text: str, spans: Sequence[Span], *, gold: bool
) -> set[tuple[int, str]]:
    positions: set[tuple[int, str]] = set()
    for span in spans:
        span.validate(text)
        if gold:
            label = require_pii_type(span.label)
        else:
            # Keep invalid prediction labels distinct so they cannot receive
            # accidental credit as another category.
            label = canonical_pii_type(span.label) or f"invalid:{span.label.strip().lower()}"
        positions.update((position, label) for position in range(span.start, span.end))
    return positions


def typed_character_counts(
    text: str, gold: Sequence[Span], predicted: Sequence[Span]
) -> CharacterCounts:
    """Count characters only when both their offsets and nine-way type match."""

    gold_positions = _typed_character_positions(text, gold, gold=True)
    predicted_positions = _typed_character_positions(text, predicted, gold=False)
    return CharacterCounts(
        true_positive=len(gold_positions & predicted_positions),
        false_positive=len(predicted_positions - gold_positions),
        false_negative=len(gold_positions - predicted_positions),
    )


def bootstrap_f1_interval(
    rows: Sequence[CharacterCounts], *, iterations: int = 2000, seed: int = 20260902
) -> dict[str, float | int]:
    if not rows:
        return {"low": 0.0, "high": 0.0, "iterations": iterations, "seed": seed}
    generator = random.Random(seed)
    scores: list[float] = []
    for _ in range(iterations):
        sample = CharacterCounts()
        for _ in rows:
            sample.add(rows[generator.randrange(len(rows))])
        scores.append(sample.f1)
    scores.sort()
    low_index = int(0.025 * (iterations - 1))
    high_index = int(0.975 * (iterations - 1))
    return {
        "low": scores[low_index],
        "high": scores[high_index],
        "iterations": iterations,
        "seed": seed,
    }


def paired_bootstrap_f1_difference(
    first: Sequence[CharacterCounts],
    second: Sequence[CharacterCounts],
    *,
    iterations: int = 5000,
    seed: int = 20260902,
) -> dict[str, float | int]:
    """Bootstrap the micro-F1 difference (first minus second) by document."""

    if len(first) != len(second):
        raise ValueError("paired systems must have equal row counts")
    if not first:
        return {"estimate": 0.0, "low": 0.0, "high": 0.0, "iterations": iterations, "seed": seed}

    observed_first = CharacterCounts()
    observed_second = CharacterCounts()
    for row in first:
        observed_first.add(row)
    for row in second:
        observed_second.add(row)

    generator = random.Random(seed)
    differences: list[float] = []
    for _ in range(iterations):
        sample_first = CharacterCounts()
        sample_second = CharacterCounts()
        for _ in first:
            index = generator.randrange(len(first))
            sample_first.add(first[index])
            sample_second.add(second[index])
        differences.append(sample_first.f1 - sample_second.f1)
    differences.sort()
    low_index = int(0.025 * (iterations - 1))
    high_index = int(0.975 * (iterations - 1))
    return {
        "estimate": observed_first.f1 - observed_second.f1,
        "low": differences[low_index],
        "high": differences[high_index],
        "iterations": iterations,
        "seed": seed,
    }


def diagnostic_breakdown(
    documents: Sequence[Document], predictions: Sequence[Sequence[Span]]
) -> dict[str, object]:
    if len(documents) != len(predictions):
        raise ValueError("documents and predictions must have equal length")

    per_document: list[CharacterCounts] = []
    by_language: dict[str, CharacterCounts] = defaultdict(CharacterCounts)
    label_covered: dict[str, int] = defaultdict(int)
    label_total: dict[str, int] = defaultdict(int)

    for document, predicted in zip(documents, predictions, strict=True):
        counts = character_counts(document.text, document.spans, predicted)
        per_document.append(counts)
        by_language[document.language or "unknown"].add(counts)
        predicted_positions = _character_positions(document.text, predicted)
        for label in {span.label for span in document.spans}:
            gold_positions = _character_positions(
                document.text, [span for span in document.spans if span.label == label]
            )
            label_covered[label] += len(gold_positions & predicted_positions)
            label_total[label] += len(gold_positions)

    return {
        "f1_bootstrap_95_percent": bootstrap_f1_interval(per_document),
        "by_language": {
            language: counts.to_dict() for language, counts in sorted(by_language.items())
        },
        "gold_character_recall_by_label": {
            label: {
                "covered": label_covered[label],
                "total": total,
                "recall": label_covered[label] / total if total else 1.0,
            }
            for label, total in sorted(label_total.items())
        },
    }


def evaluate_documents(
    documents: Iterable[Document], predictions: Iterable[Sequence[Span]]
) -> EvaluationResult:
    total = CharacterCounts()
    document_count = 0
    documents_with_pii = 0
    exact_matches = 0

    document_iterator = iter(documents)
    prediction_iterator = iter(predictions)
    while True:
        try:
            document = next(document_iterator)
        except StopIteration:
            try:
                next(prediction_iterator)
            except StopIteration:
                break
            raise ValueError("received more prediction rows than documents") from None

        try:
            predicted = tuple(prediction_iterator.__next__())
        except StopIteration:
            raise ValueError("received fewer prediction rows than documents") from None

        counts = character_counts(document.text, document.spans, predicted)
        total.add(counts)
        document_count += 1
        documents_with_pii += bool(document.spans)
        exact_matches += counts.false_positive == 0 and counts.false_negative == 0

    return EvaluationResult(
        counts=total,
        documents=document_count,
        documents_with_pii=documents_with_pii,
        exact_document_matches=exact_matches,
    )


def evaluate_typed_documents(
    documents: Iterable[Document], predictions: Iterable[Sequence[Span]]
) -> EvaluationResult:
    total = CharacterCounts()
    document_count = 0
    documents_with_pii = 0
    exact_matches = 0

    document_iterator = iter(documents)
    prediction_iterator = iter(predictions)
    while True:
        try:
            document = next(document_iterator)
        except StopIteration:
            try:
                next(prediction_iterator)
            except StopIteration:
                break
            raise ValueError("received more prediction rows than documents") from None

        try:
            predicted = tuple(next(prediction_iterator))
        except StopIteration:
            raise ValueError("received fewer prediction rows than documents") from None

        counts = typed_character_counts(document.text, document.spans, predicted)
        total.add(counts)
        document_count += 1
        documents_with_pii += bool(document.spans)
        exact_matches += counts.false_positive == 0 and counts.false_negative == 0

    return EvaluationResult(
        counts=total,
        documents=document_count,
        documents_with_pii=documents_with_pii,
        exact_document_matches=exact_matches,
    )
