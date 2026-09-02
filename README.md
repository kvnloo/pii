# PAW PII detector

Can an English function description compiled by ProgramAsWeights get close to a
purpose-built 0.6B PII detector trained on roughly 714,000 samples?

This repository answers that question before making a demo or a launch claim.
It evaluates both systems with label-agnostic, micro-averaged character F1—the
headline metric reported by Perplexity for external PII benchmarks.

## Comparison

- **PII-Tracer:** Perplexity's released 0.6B bidirectional encoder and BIOES/Viterbi
  decoder.
- **PAW Standard:** an English specification compiled with
  `paw-4b-qwen3-0.6b`, then run locally.
- **PAW Finetuned Standard:** the exact frozen specification compiled with
  `paw-ft-bs48`, then run locally. This compiler performs per-spec LoRA tuning,
  so results must not be described as "no training."

The first public target is the validation split of
`ai4privacy/pii-masking-300k`, where Perplexity reports 0.950 character F1 for
PII-Tracer. Development examples are drawn only from the training split.

## Result

On a frozen, multilingual sample of 171 validation documents (72,069
characters and 1,073 labeled spans):

- **PII-Tracer:** 0.9388 F1 (0.8856 precision, 0.9988 recall).
- **PAW Standard:** 0.8823 F1 (0.8884 precision, 0.8763 recall).
- **PAW Finetuned Standard:** 0.8662 F1 (0.7920 precision, 0.9558 recall).

The paired PII-Tracer minus PAW Standard gap is 0.0564 F1; a 5,000-resample
paired document bootstrap gives a 95% interval of 0.0318–0.0832. PII-Tracer's
0.9388 sample score has a 0.9228–0.9531 interval, which contains Perplexity's
published 0.950 full-validation result.

The winning PAW program came from a 3,391-character English specification and
compiled in 5.32 seconds. It is a 22.7 MB adapter over a shared 622.7 MB
quantized Qwen3-0.6B runtime. The released PII-Tracer checkpoint is 1.19 GB.
Those storage formats differ, so this is a deployment description rather than
a model-size superiority claim.

Standard compilation uses the pretrained PAW compiler to emit an adapter and
does not run a per-task gradient-training loop. Finetuned Standard does perform
per-spec LoRA training; it raised recall substantially but over-predicted
non-PII record fields, reducing F1. That negative result is retained.

The compact comparison artifact is in
[`artifacts/benchmark-comparison.json`](artifacts/benchmark-comparison.json).

## Try the frozen program locally

Once the private program is available to your PAW account, inference and
redaction happen on the local machine:

```bash
PYTHONPATH=src python scripts/redact.py \
  --program-manifest results/paw-standard-v3.json \
  --text "I'm Daniel Whitfield; email daniels@meridiancap.com" \
  --json
```

The hosted compile step is required once; the downloaded 22.7 MB program and
shared runtime then work offline. The current PAW output is untyped spans, so
the demo uses a neutral `[PII]` replacement.

## Quick start

The commands deliberately cache only deterministic samples unless `--limit 0`
is requested.

```bash
PYTHONPATH=src python scripts/cache_dataset.py \
  --split validation --limit 0 \
  --output data/cache/ai4privacy-validation.jsonl

PYTHONPATH=src python scripts/cache_training_dev.py \
  --groups-per-language 5 \
  --output data/cache/train-development.jsonl

PYTHONPATH=src python scripts/make_splits.py \
  --input data/cache/ai4privacy-validation.jsonl \
  --dev-output data/cache/development.jsonl \
  --test-output data/cache/held-out-test.jsonl

PYTHONPATH=src python scripts/run_benchmark.py \
  --data data/cache/held-out-test.jsonl \
  --backend pplx \
  --model-dir models/pplx-pii-masking
```

Download the exact PII-Tracer revision used here with:

```bash
hf download perplexity-ai/pplx-pii-masking \
  --revision f1f90a53823f5df0a1344c1e137d9fffdaab54d6 \
  --local-dir models/pplx-pii-masking
```

PAW programs are compiled privately. Their IDs and exact compiler snapshots are
written to a local manifest so every reported result identifies the artifact it
used.

```bash
PYTHONPATH=src python scripts/compile_paw.py \
  --spec specs/pii-detector-v3.txt \
  --compiler paw-4b-qwen3-0.6b \
  --manifest results/paw-standard-v3.json

PYTHONPATH=src python scripts/run_benchmark.py \
  --data data/cache/held-out-test.jsonl \
  --backend paw \
  --program-manifest results/paw-standard-v3.json
```

`cache_training_dev.py` reads only a few complete source groups from each raw
training file. `make_splits.py` keeps every chunk from the same ai4privacy
validation source document together and balances the held-out sample by
language. The specification is iterated only against `train-development.jsonl`;
`held-out-test.jsonl` stays unseen until the specification is frozen.

## Metric

For each document, gold and predicted spans are converted into sets of character
positions. Counts are pooled across documents:

```text
precision = predicted PII characters that are gold / predicted PII characters
recall    = gold PII characters that are predicted / gold PII characters
F1        = harmonic mean of precision and recall
```

Category names are ignored, matching Perplexity's external-benchmark protocol.
Malformed or hallucinated PAW values count as no prediction; they are also
recorded for error analysis.

The public dataset contains a small number of stored values and offsets that do
not align with their source text. Character offsets are authoritative. The
caching step records value mismatches, clips offsets to document boundaries,
and drops only spans that contain no valid source character; every count is
reported in the sample manifest.

## Sources and scope

- Perplexity's [PII-TRACE article](https://www.perplexity.ai/hub/blog/pii-trace-detecting-personal-data-before-it-leaves-the-device)
- Released [PII-Tracer checkpoint](https://huggingface.co/perplexity-ai/pplx-pii-masking)
- Public [ai4privacy dataset](https://huggingface.co/datasets/ai4privacy/pii-masking-300k), pinned here to revision
  `c8c77895a005822682b66ab547fc0422579bc1d3`

This result is an external-benchmark sample, not a reproduction of PII-TRACE:
Perplexity had not released the PII-TRACE test set when this comparison was run.
