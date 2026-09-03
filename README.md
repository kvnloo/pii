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

On a frozen multilingual sample of 171 documents from the AI4Privacy validation split, the published program reached:

- **0.8366 typed-character F1**
- **0.8830 label-agnostic extraction F1**
- **95.0% type accuracy** on characters where the prediction and annotation overlap

Specifications were developed only on a separate 477-document sample from the training split. The held-out sample was evaluated after the winner was frozen.

See [`RESULTS.md`](RESULTS.md) for every specification, compiled program, failed run, and benchmark result.

## Reproduce the benchmark

The benchmark implementation is under [`scripts/`](scripts), the parser and metrics are under [`src/paw_pii/`](src/paw_pii), and tests are under [`tests/`](tests). Downloaded datasets, model checkpoints, and generated prediction files are intentionally excluded from Git.

```bash
PYTHONPATH=src python -m pytest -q
```

## License

MIT
