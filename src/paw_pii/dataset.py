from __future__ import annotations

import hashlib
import heapq
import re
from collections import Counter, defaultdict
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from typing import Any

from .types import Document, Span

DATASET_REPO = "ai4privacy/pii-masking-300k"
DATASET_REVISION = "c8c77895a005822682b66ab547fc0422579bc1d3"
DATASET_LANGUAGES = ("English", "Dutch", "French", "German", "Italian", "Spanish")
TRAIN_FILES = {
    "English": "data/train/1english_openpii_30k.jsonl",
    "Dutch": "data/train/dutch_openpii_28k.jsonl",
    "French": "data/train/french_openpii_31k.jsonl",
    "German": "data/train/german_openpii_30k.jsonl",
    "Italian": "data/train/italian_openpii_29k.jsonl",
    "Spanish": "data/train/spanish_openpii_29k.jsonl",
}


def row_to_document(row: dict[str, Any]) -> Document:
    text = str(row["source_text"])
    spans: list[Span] = []
    mismatches: list[dict[str, Any]] = []
    invalid_spans: list[dict[str, Any]] = []
    for item in row.get("privacy_mask", []):
        original_start, original_end = int(item["start"]), int(item["end"])
        start, end = max(0, original_start), min(len(text), original_end)
        if start != original_start or end != original_end:
            invalid_spans.append(
                {
                    "start": original_start,
                    "end": original_end,
                    "clipped_start": start,
                    "clipped_end": end,
                    "stored_value": str(item["value"]),
                    "action": "clipped" if end > start else "dropped",
                }
            )
        if end <= start:
            continue
        observed = text[start:end]
        stored = str(item["value"])
        if observed != stored:
            mismatches.append(
                {
                    "start": start,
                    "end": end,
                    "stored_value": stored,
                    "observed_value": observed,
                }
            )
        spans.append(
            Span(
                start=start,
                end=end,
                label=str(item["label"]),
                value=observed,
            )
        )
    return Document(
        id=str(row["id"]),
        text=text,
        spans=tuple(spans),
        language=str(row.get("language")) if row.get("language") else None,
        metadata=(
            {
                "source_value_mismatches": mismatches,
                "invalid_source_spans": invalid_spans,
            }
            if mismatches or invalid_spans
            else None
        ),
    ).validate()


def stable_priority(document_id: str, seed: str) -> int:
    digest = hashlib.sha256(f"{seed}\0{document_id}".encode()).digest()
    return int.from_bytes(digest[:8], "big")


def _select_smallest(
    documents: Iterable[Document], limit: int, seed: str
) -> list[Document]:
    """Select rows with the smallest stable hash using bounded memory."""

    if limit <= 0:
        return list(documents)
    heap: list[tuple[int, str, Document]] = []
    for document in documents:
        priority = stable_priority(document.id, seed)
        candidate = (-priority, document.id, document)
        if len(heap) < limit:
            heapq.heappush(heap, candidate)
        elif priority < -heap[0][0]:
            heapq.heapreplace(heap, candidate)
    return [item[2] for item in sorted(heap, key=lambda item: (-item[0], item[1]))]


def deterministic_sample(
    documents: Iterable[Document],
    *,
    limit: int = 0,
    per_language: int = 0,
    languages: tuple[str, ...] = DATASET_LANGUAGES,
    seed: str = "paw-pii-v1",
) -> list[Document]:
    if limit and per_language:
        raise ValueError("limit and per_language are mutually exclusive")
    if not per_language:
        return _select_smallest(documents, limit, seed)

    requested = set(languages)
    heaps: dict[str, list[tuple[int, str, Document]]] = defaultdict(list)
    for document in documents:
        language = document.language
        if language not in requested:
            continue
        heap = heaps[language]
        priority = stable_priority(document.id, seed)
        candidate = (-priority, document.id, document)
        if len(heap) < per_language:
            heapq.heappush(heap, candidate)
        elif priority < -heap[0][0]:
            heapq.heapreplace(heap, candidate)

    missing = [language for language in languages if len(heaps[language]) < per_language]
    if missing:
        counts = {language: len(heaps[language]) for language in missing}
        raise ValueError(f"not enough rows for requested languages: {counts}")

    selected = [
        item[2]
        for language in languages
        for item in sorted(heaps[language], key=lambda item: (-item[0], item[1]))
    ]
    return sorted(selected, key=lambda document: (document.language or "", document.id))


def summarize_documents(documents: Iterable[Document]) -> dict[str, Any]:
    docs = list(documents)
    labels = Counter(span.label for document in docs for span in document.spans)
    languages = Counter(document.language or "unknown" for document in docs)
    return {
        "documents": len(docs),
        "documents_with_pii": sum(bool(document.spans) for document in docs),
        "characters": sum(len(document.text) for document in docs),
        "spans": sum(len(document.spans) for document in docs),
        "source_value_mismatches": sum(
            len((document.metadata or {}).get("source_value_mismatches", []))
            for document in docs
        ),
        "invalid_source_spans": sum(
            len((document.metadata or {}).get("invalid_source_spans", []))
            for document in docs
        ),
        "languages": dict(sorted(languages.items())),
        "labels": dict(sorted(labels.items())),
    }


def source_group(document_id: str) -> str:
    """Return the base ID used by ai4privacy for adjacent chunks of one source."""

    return re.sub(r"[A-Za-z]+$", "", document_id)


@dataclass(frozen=True)
class HuggingFaceDatasetSource:
    split: str
    revision: str = DATASET_REVISION

    def stream(self) -> Iterator[Document]:
        from datasets import load_dataset

        rows = load_dataset(
            DATASET_REPO,
            revision=self.revision,
            split=self.split,
            streaming=True,
        )
        for row in rows:
            yield row_to_document(row)
