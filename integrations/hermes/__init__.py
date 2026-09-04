"""Hermes Agent plugin: local PAW PII redaction via middleware + tools.

Install (standalone plugin path — not a core in-tree provider):

  # From a clone of this repo
  mkdir -p ~/.hermes/plugins
  ln -s "$(pwd)/integrations/hermes" ~/.hermes/plugins/paw-pii
  hermes plugins enable paw-pii

  # Or: hermes plugins install kvnloo/pii  (when index/subdir install is wired)

Requires programasweights + ``pip install -e .`` from the repo root (or
PYTHONPATH=src). Auto-redaction uses Hermes middleware:

  - llm_request  — scrub provider kwargs before egress
  - tool_execution — scrub tool results before they re-enter context

Env:
  PAW_PII_DISABLE=1       master off
  PAW_PII_AUTO_LLM=0      disable llm_request middleware
  PAW_PII_AUTO_TOOLS=0    disable tool_execution middleware
  PAW_PII_PROGRAM_ID=...  override published program id
  PAW_PII_PLACEHOLDER=... default [PII]
"""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_REPO_SRC = Path(__file__).resolve().parents[2] / "src"
if _REPO_SRC.is_dir() and str(_REPO_SRC) not in sys.path:
    sys.path.insert(0, str(_REPO_SRC))

TOOLSET = "paw_pii"


def _service(placeholder: str | None = None):
    from paw_pii.service import LocalPiiService, get_service

    if placeholder:
        return LocalPiiService(
            program_id=os.environ.get("PAW_PII_PROGRAM_ID"),
            placeholder=placeholder,
        )
    return get_service(
        program_id=os.environ.get("PAW_PII_PROGRAM_ID"),
        placeholder=os.environ.get("PAW_PII_PLACEHOLDER", "[PII]"),
    )


def _enabled() -> bool:
    return os.environ.get("PAW_PII_DISABLE", "").lower() not in {"1", "true", "yes", "on"}


def _flag(name: str, default: str = "1") -> bool:
    return os.environ.get(name, default).lower() not in {"0", "false", "no", "off"}


def _redact_request(request: dict[str, Any]) -> dict[str, Any]:
    service = _service()
    updated = dict(request)
    if isinstance(updated.get("messages"), list):
        updated["messages"] = service.redact_messages(updated["messages"])
    if "input" in updated:
        if isinstance(updated["input"], str):
            updated["input"] = service.redact(updated["input"])
        elif isinstance(updated["input"], list):
            updated["input"] = service.redact_messages(updated["input"])
    if isinstance(updated.get("prompt"), str):
        updated["prompt"] = service.redact(updated["prompt"])
    return updated


def _on_llm_request(**kwargs: Any) -> dict[str, Any] | None:
    if not _enabled() or not _flag("PAW_PII_AUTO_LLM"):
        return None
    request = kwargs.get("request")
    if not isinstance(request, dict):
        return None
    try:
        return {
            "request": _redact_request(request),
            "source": "paw-pii",
            "reason": "local PII redaction before provider egress",
        }
    except Exception:  # noqa: BLE001 — Hermes middleware is fail-open
        logger.exception("paw-pii llm_request middleware failed")
        return None


def _redact_tool_result(result: Any) -> Any:
    service = _service()
    keys = ("content", "text", "output", "stdout", "stderr")
    if isinstance(result, str):
        return service.redact(result)
    if isinstance(result, dict):
        return service._redact_value(result, content_keys=keys)
    if isinstance(result, list):
        return [service._redact_value(item, content_keys=keys) for item in result]
    return result


def _on_tool_execution(**kwargs: Any) -> Any:
    next_call = kwargs["next_call"]
    result = next_call(kwargs.get("args"))
    if not _enabled() or not _flag("PAW_PII_AUTO_TOOLS"):
        return result
    try:
        return _redact_tool_result(result)
    except Exception:  # noqa: BLE001
        logger.exception("paw-pii tool_execution middleware failed")
        return result


def _handle_detect_pii(text: str = "", placeholder: str = "[PII]", **_: Any) -> dict[str, Any]:
    return _service(placeholder=placeholder or None).detect(text).to_dict()


def _handle_redact_pii(text: str = "", placeholder: str = "[PII]", **_: Any) -> str:
    return _service(placeholder=placeholder or None).redact(text)


DETECT_SCHEMA = {
    "name": "detect_pii",
    "description": (
        "Detect PII locally with ProgramAsWeights. Returns typed spans and a redacted copy."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "text": {"type": "string", "description": "Text to scan"},
            "placeholder": {"type": "string", "description": "Replacement token", "default": "[PII]"},
        },
        "required": ["text"],
    },
}

REDACT_SCHEMA = {
    "name": "redact_pii",
    "description": "Redact PII from text locally and return the scrubbed string.",
    "parameters": {
        "type": "object",
        "properties": {
            "text": {"type": "string", "description": "Text to redact"},
            "placeholder": {"type": "string", "description": "Replacement token", "default": "[PII]"},
        },
        "required": ["text"],
    },
}


def register(ctx: Any) -> None:
    """Hermes PluginContext entrypoint."""

    register_tool = getattr(ctx, "register_tool", None)
    if callable(register_tool):
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

    register_middleware = getattr(ctx, "register_middleware", None)
    if callable(register_middleware):
        register_middleware("llm_request", _on_llm_request)
        register_middleware("tool_execution", _on_tool_execution)
        logger.info("paw-pii registered llm_request + tool_execution middleware")
    else:
        logger.warning("paw-pii host lacks register_middleware; tools only")

    logger.info("paw-pii Hermes plugin registered")
