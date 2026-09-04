"""Local ProgramAsWeights PII detection, redaction, and harness integrations."""

from .metrics import CharacterCounts, EvaluationResult, evaluate_documents, evaluate_typed_documents
from .redaction import merge_spans, redact_text
from .service import DEFAULT_PROGRAM_ID, LocalPiiService, RedactionResult, get_service
from .taxonomy import PII_TYPES, canonical_pii_type
from .types import Document, Span

__all__ = [
    "CharacterCounts",
    "DEFAULT_PROGRAM_ID",
    "Document",
    "EvaluationResult",
    "LocalPiiService",
    "PII_TYPES",
    "RedactionResult",
    "Span",
    "canonical_pii_type",
    "evaluate_documents",
    "evaluate_typed_documents",
    "get_service",
    "merge_spans",
    "redact_text",
]
