"""MCP JSON-RPC surface tests (no model inference)."""

from __future__ import annotations

from paw_pii.mcp_server import TOOLS, handle_message


def test_initialize_and_tools_list() -> None:
    init = handle_message({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
    assert init is not None
    assert init["result"]["serverInfo"]["name"] == "paw-pii"

    listed = handle_message({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
    assert listed is not None
    names = {tool["name"] for tool in listed["result"]["tools"]}
    assert names == {"detect_pii", "redact_pii"}
    assert len(TOOLS) == 2


def test_notification_returns_none() -> None:
    assert handle_message({"jsonrpc": "2.0", "method": "notifications/initialized"}) is None
