"""Deferred tool registration for Hermes CLI/TUI sessions.

Hermes loads ``tools.register_tools(ctx)`` when ``plugin.yaml`` declares
``provides_tools``. Keep this module import-light; heavy deps load inside handlers.
"""

from __future__ import annotations

from typing import Any


def register_tools(ctx: Any) -> None:
    # Reuse the package register() tool wiring without re-binding middleware.
    from . import (
        DETECT_SCHEMA,
        REDACT_SCHEMA,
        TOOLSET,
        _handle_detect_pii,
        _handle_redact_pii,
    )

    register_tool = getattr(ctx, "register_tool", None)
    if not callable(register_tool):
        return
    register_tool(
        name="detect_pii",
        toolset=TOOLSET,
        schema=DETECT_SCHEMA,
        handler=_handle_detect_pii,
        description=DETECT_SCHEMA["description"],
    )
    register_tool(
        name="redact_pii",
        toolset=TOOLSET,
        schema=REDACT_SCHEMA,
        handler=_handle_redact_pii,
        description=REDACT_SCHEMA["description"],
    )
