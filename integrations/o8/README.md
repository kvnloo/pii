# o8 + local PAW PII

o8 has no marketplace plugin format. First-class tool extension is **external MCP** on the tool-spine, with optional **worker injection** for codex/claude-code packets.

This recipe attaches the local ProgramAsWeights PII MCP from this repository so orchestrators and workers can call `detect_pii` / `redact_pii` without sending text to a cloud NER service.

## Prerequisites

1. Python ≥ 3.11 with this package importable:

```bash
cd /path/to/pii
pip install -e .
# programasweights index — see root README
pip install programasweights --extra-index-url https://pypi.programasweights.com/simple/
```

2. Smoke the MCP server:

```bash
printf '%s\n' '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}' | python -m paw_pii.mcp_server
```

## Register in o8 (Settings UI)

1. Open **Settings → MCP**.
2. Add external server:
   - **Name:** `paw-pii` (letters, digits, `_`, `-` only)
   - **Transport:** stdio
   - **Command:** absolute path to `python3` (or a venv python)
   - **Args:** `-m` `paw_pii.mcp_server`
   - **Env (optional):** `PAW_PII_PROGRAM_ID`, `PAW_PII_PLACEHOLDER`
3. Enable the server.
4. Toggle **Attach to supported workers** (`workerInjection`) so codex/claude-code packet workers receive the same stdio MCP.

## Register via API

```bash
curl -sS -X POST "http://127.0.0.1:3000/api/setup/mcp-servers" \
  -H "Authorization: Bearer $O8_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "paw-pii",
    "transport": "stdio",
    "command": "/usr/bin/python3",
    "args": ["-m", "paw_pii.mcp_server"],
    "env": {"PAW_PII_PLACEHOLDER": "[PII]"},
    "enabled": true,
    "workerInjection": true
  }'
```

Enabled externals are assembled into the tool-spine (`src/lib/mcp/tool-spine/build.ts`) for Claude/Codex orchestrator surfaces automatically.

## What this is / is not

| Goal | Supported today? |
|------|------------------|
| Operator/orchestrator can call redact tools | Yes — external MCP |
| Workers (codex/claude-code) can call redact tools | Yes — `workerInjection` |
| Always scrub every LLM egress without a tool call | No — needs a new middleware seam in o8 (open an issue first) |
| Broadcast spectator scrub of names/emails | Partial — existing `broadcast/redaction.ts` covers tokens/paths/env, not NER PII |

## Optional later: builtin spine entry

Mirror `codebase-memory`: resolve `O8_PII_BIN` or `~/.o8/bin/paw-pii-mcp` and add a `builtin:pii` `ServerEntry` in `buildToolRegistry` when present. Prefer shipping as optional/absent-ok so installs without the model stay clean.

## Related upstream docs

- `docs/internals/runtime-adapter-contract.md` — worker MCP injection
- `docs/user/operator-mcp-bridge.md` — operator MCP
- `src/lib/mcp/external-servers.ts` — persistence/CRUD
- `src/lib/broadcast/redaction.ts` — existing credential/path redaction
