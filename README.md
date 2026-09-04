# PII detection with ProgramAsWeights

Detect and type personally identifiable information locally with one compiled [ProgramAsWeights](https://programasweights.com) neural program.

[Try the live demo](https://programasweights.com/pii)

## Python

```bash
pip install programasweights --extra-index-url https://pypi.programasweights.com/simple/
```

```python
import json
import programasweights as paw

detect_pii = paw.function("73a0e38b8bbe3427cd1d")

text = "Name: Ada Lovelace\nEmail: ada@example.com\nPIN: 4821"
print(json.loads(detect_pii(text)))
```

```text
[['Ada Lovelace', 'private_person'], ['ada@example.com', 'private_email'], ['4821', 'secret']]
```

The program downloads once and then runs locally. See [`example.py`](example.py) for the complete runnable example.

## Agent harness plugins

This fork adds first-class adapters so coding agents can scrub PII **on-device** before provider egress:

| Harness | Path | Install |
|---------|------|---------|
| **Oh My Pi (omp)** | [`integrations/omp`](integrations/omp) | `omp plugin link ./integrations/omp` |
| **Hermes Agent** | [`integrations/hermes`](integrations/hermes) | `ln -s $(pwd)/integrations/hermes ~/.hermes/plugins/paw-pii && hermes plugins enable paw-pii` |
| **o8** | [`integrations/o8`](integrations/o8) | Settings → MCP → stdio `python -m paw_pii.mcp_server` (+ worker injection) |
| **Any MCP host** | `python -m paw_pii.mcp_server` | tools: `detect_pii`, `redact_pii` |

Shared library API:

```python
from paw_pii import get_service

service = get_service()
print(service.redact("Email ada@example.com PIN 4821"))
# Email [PII] PIN [PII]
```

CLI:

```bash
pip install -e .
python -m paw_pii.cli redact --text "Name: Ada Lovelace"
python -m paw_pii.mcp_server   # stdio MCP
```

Hermes uses `llm_request` + `tool_execution` middleware for automatic scrubbing. OMP uses `context`, `before_provider_request`, and `tool_result` extension events. o8 attaches the MCP server on the tool-spine (orchestrator + optional worker injection); automatic pre-LLM middleware in o8 core is a separate upstream design discussion.


## Output

The function returns a JSON array of `[text, type]` pairs. Each `text` is copied exactly from the input, and each `type` is one of:

```text
private_person  private_email  private_phone  private_address  private_url
private_date    account_number secret         other_pii
```

## Compile it yourself

The public program was compiled from the English specification in [`spec.txt`](spec.txt). [`compile.py`](compile.py) contains the complete compilation script:

```python
from pathlib import Path
import programasweights as paw

program = paw.compile(
    Path("spec.txt").read_text().strip(),
    compiler="paw-ft-bs48",
    public=True,
)

print(program.id)
```

The published compilation used by this repository is:

```text
73a0e38b8bbe3427cd1d
```

Compiling requires a PAW account and API key. Loading the published program by ID does not require recompiling it.

## Results

On an untouched multilingual set of 512 AI4Privacy documents, the published program reached:

- **0.8464 typed-character F1**
- **0.9085 label-agnostic extraction F1**
- **93.9% type accuracy** on characters where the prediction and annotation overlap

We compared compact JSON, reversed JSON, JSON objects, and TSV outputs on a separate 497-document search set, froze the finalists, and selected the published program on another 522 documents before opening the sealed set. All source groups are disjoint. The original compact `[text, type]` JSON interface won; simplifying its specification did not generalize.

See [`RESULTS.md`](RESULTS.md) for every specification, compiled program, failed run, and benchmark result.

## Reproduce the benchmark

The benchmark implementation is under [`scripts/`](scripts), the parser and metrics are under [`src/paw_pii/`](src/paw_pii), and tests are under [`tests/`](tests). Downloaded datasets, model checkpoints, and generated prediction files are intentionally excluded from Git.

```bash
PYTHONPATH=src python -m pytest -q
```

## License

MIT
