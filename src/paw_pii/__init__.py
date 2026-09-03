"""Benchmark utilities for the ProgramAsWeights PII detector."""

from .metrics import CharacterCounts, EvaluationResult, evaluate_documents, evaluate_typed_documents
from .taxonomy import PII_TYPES, canonical_pii_type
from .types import Document, Span

__all__ = [
    "CharacterCounts",
    "Document",
    "EvaluationResult",
    "PII_TYPES",
    "Span",
    "canonical_pii_type",
    "evaluate_documents",
    "evaluate_typed_documents",
]
