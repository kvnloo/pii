from __future__ import annotations

import json
from collections.abc import Iterable, Iterator
from pathlib import Path

from .types import Document


def read_documents(path: str | Path) -> Iterator[Document]:
    with Path(path).open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                yield Document.from_dict(json.loads(line))
            except Exception as exc:
                raise ValueError(f"invalid document at {path}:{line_number}") from exc


def write_documents(path: str | Path, documents: Iterable[Document]) -> int:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with destination.open("w", encoding="utf-8") as handle:
        for document in documents:
            handle.write(json.dumps(document.to_dict(), ensure_ascii=False, sort_keys=True) + "\n")
            count += 1
    return count
