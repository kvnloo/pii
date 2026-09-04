#!/usr/bin/env python3
"""Minimal stdio MCP server exposing local PII detect/redact tools.

Implements enough of the MCP tools surface for omp, o8, Hermes, and Claude Desktop:
initialize, tools/list, tools/call, ping. No third-party MCP SDK required.
"""

from __future__ import annotations

import json
import sys
from typing import Any

from .service import DEFAULT_PLACEHOLDER, get_service

SERVER_NAME = "paw-pii"
SERVER_VERSION = "0.1.0"
PROTOCOL_VERSION = "2024-11-05"

TOOLS = [
    {
        "name": "detect_pii",
        "description": (
            "Detect personally identifiable information in text using a local "
            "ProgramAsWeights neural program. Returns typed spans and a redacted copy. "
            "Data never leaves the machine."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Text to scan"},
                "placeholder": {
                    "type": "string",
                    "description": f"Replacement for each span (default {DEFAULT_PLACEHOLDER})",
                },
            },
            "required": ["text"],
            "additionalProperties": False,
        },
    },
    {
        "name": "redact_pii",
        "description": (
            "Redact PII from text locally. Returns only the redacted string. "
            "Use before sending prompts, logs, or transcripts to external providers."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Text to redact"},
                "placeholder": {
                    "type": "string",
                    "description": f"Replacement for each span (default {DEFAULT_PLACEHOLDER})",
                },
            },
            "required": ["text"],
            "additionalProperties": False,
        },
    },
]


def _response(req_id: Any, result: Any) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": req_id, "result": result}


def _error(req_id: Any, code: int, message: str) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}}


def _tool_text(payload: Any) -> dict[str, Any]:
    text = payload if isinstance(payload, str) else json.dumps(payload, ensure_ascii=False, indent=2)
    return {"content": [{"type": "text", "text": text}], "isError": False}


def _call_tool(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    text = str(arguments.get("text") or "")
    placeholder = str(arguments.get("placeholder") or DEFAULT_PLACEHOLDER)
    service = get_service(placeholder=placeholder)

    if name == "detect_pii":
        result = service.detect(text)
        body = result.to_dict()
        if result.error:
            return {
                "content": [{"type": "text", "text": json.dumps(body, ensure_ascii=False)}],
                "isError": True,
            }
        return _tool_text(body)

    if name == "redact_pii":
        result = service.detect(text)
        if result.error:
            return {
                "content": [{"type": "text", "text": result.error}],
                "isError": True,
            }
        return _tool_text(result.redacted)

    return {
        "content": [{"type": "text", "text": f"Unknown tool: {name}"}],
        "isError": True,
    }


def handle_message(message: dict[str, Any]) -> dict[str, Any] | None:
    method = message.get("method")
    req_id = message.get("id")
    params = message.get("params") or {}

    # Notifications have no id and need no response.
    if req_id is None and method in {"notifications/initialized", "initialized"}:
        return None

    if method == "initialize":
        return _response(
            req_id,
            {
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": {"tools": {}},
                "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
            },
        )

    if method == "ping":
        return _response(req_id, {})

    if method == "tools/list":
        return _response(req_id, {"tools": TOOLS})

    if method == "tools/call":
        name = params.get("name")
        arguments = params.get("arguments") or {}
        if not isinstance(name, str):
            return _error(req_id, -32602, "tools/call requires string name")
        if not isinstance(arguments, dict):
            return _error(req_id, -32602, "tools/call arguments must be an object")
        return _response(req_id, _call_tool(name, arguments))

    if method == "resources/list":
        return _response(req_id, {"resources": []})

    if method == "prompts/list":
        return _response(req_id, {"prompts": []})

    if req_id is None:
        return None
    return _error(req_id, -32601, f"Method not found: {method}")


def main() -> None:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            message = json.loads(line)
        except json.JSONDecodeError as exc:
            sys.stdout.write(json.dumps(_error(None, -32700, f"Parse error: {exc}")) + "\n")
            sys.stdout.flush()
            continue
        response = handle_message(message)
        if response is not None:
            sys.stdout.write(json.dumps(response, ensure_ascii=False) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
