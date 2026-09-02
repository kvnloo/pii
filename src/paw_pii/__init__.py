"""Benchmark utilities for the ProgramAsWeights PII detector."""

from .metrics import CharacterCounts, EvaluationResult, evaluate_documents
from .types import Document, Span

__all__ = [
    "CharacterCounts",
    "Document",
    "EvaluationResult",
    "Span",
    "evaluate_documents",
]
