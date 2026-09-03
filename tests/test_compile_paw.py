from __future__ import annotations

from typing import Any

import pytest

from scripts import compile_paw


class FakeResponse:
    def __init__(self, payload: dict[str, Any]) -> None:
        self.payload = payload

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict[str, Any]:
        return self.payload


def test_cached_public_compile_stays_public(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        compile_paw.httpx,
        "post",
        lambda *args, **kwargs: FakeResponse({"cached": True, "program_id": "program"}),
    )
    monkeypatch.setattr(
        compile_paw.httpx,
        "get",
        lambda *args, **kwargs: FakeResponse({"id": "program", "public": True}),
    )

    def unexpected_patch(*args: object, **kwargs: object) -> FakeResponse:
        raise AssertionError("an already-public program must not be patched")

    monkeypatch.setattr(compile_paw.httpx, "patch", unexpected_patch)

    program, _ = compile_paw.precheck_cached_program(
        "https://example.test",
        {"spec": "long enough spec", "compiler": "paw-test", "public": True},
        {},
    )

    assert program is not None
    assert program["public"] is True


def test_cached_private_compile_is_published_when_requested(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        compile_paw.httpx,
        "post",
        lambda *args, **kwargs: FakeResponse({"cached": True, "program_id": "program"}),
    )
    monkeypatch.setattr(
        compile_paw.httpx,
        "get",
        lambda *args, **kwargs: FakeResponse({"id": "program", "public": False}),
    )
    patch_calls: list[tuple[str, dict[str, Any]]] = []

    def publish(url: str, **kwargs: Any) -> FakeResponse:
        patch_calls.append((url, kwargs))
        return FakeResponse({"ok": True, "public": True})

    monkeypatch.setattr(compile_paw.httpx, "patch", publish)

    program, _ = compile_paw.precheck_cached_program(
        "https://example.test",
        {"spec": "long enough spec", "compiler": "paw-test", "public": True},
        {"X-API-Key": "test"},
    )

    assert program is not None
    assert program["public"] is True
    assert patch_calls == [
        (
            "https://example.test/api/v1/programs/program",
            {
                "json": {"public": True},
                "headers": {"X-API-Key": "test"},
                "timeout": 30.0,
            },
        )
    ]


def test_cached_public_compile_cannot_be_recorded_as_private(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        compile_paw.httpx,
        "post",
        lambda *args, **kwargs: FakeResponse({"cached": True, "program_id": "program"}),
    )
    monkeypatch.setattr(
        compile_paw.httpx,
        "get",
        lambda *args, **kwargs: FakeResponse({"id": "program", "public": True}),
    )

    with pytest.raises(RuntimeError, match="already public"):
        compile_paw.precheck_cached_program(
            "https://example.test",
            {"spec": "long enough spec", "compiler": "paw-test", "public": False},
            {},
        )
