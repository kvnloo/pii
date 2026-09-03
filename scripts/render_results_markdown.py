#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = ROOT / "results"
SPECS_DIR = ROOT / "specs"
OUTPUT = ROOT / "RESULTS.md"


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def decimal(value: object, digits: int = 4) -> str:
    if not isinstance(value, (int, float)):
        return "—"
    return f"{value:.{digits}f}"


def integer(value: object) -> str:
    if not isinstance(value, (int, float)):
        return "—"
    return str(int(value))


def short_path(path: object) -> str:
    if not isinstance(path, str):
        return "—"
    return Path(path).name


def validate_spec(path: Path, text: str) -> None:
    if "\r" in text:
        raise ValueError(f"{path}: CR character found")
    for line_number, line in enumerate(text.splitlines(), start=1):
        if line != line.rstrip():
            raise ValueError(f"{path}:{line_number}: trailing whitespace")
    lines = text.splitlines()
    for index in range(1, len(lines)):
        previous = lines[index - 1]
        current = lines[index]
        if not previous or not current:
            continue
        if current.startswith(("- ", "Input:", "Output:")):
            continue
        raise ValueError(f"{path}:{index + 1}: adjacent prose lines look like a soft wrap")


def summary_rows() -> list[str]:
    rows: list[str] = []
    for path in sorted(RESULTS_DIR.glob("*.summary.json")):
        result = read_json(path)
        backend = result.get("backend", {})
        metrics = result.get("metrics", {})
        extraction = metrics.get("character", {})
        backend_name = backend.get("backend", "")
        is_typed = "typed" in path.name or "-type-" in path.name or backend_name.endswith("typer")
        typed = metrics.get("typed_character", {}) if is_typed else {}
        type_accuracy = metrics.get("type_accuracy_on_overlapping_characters") if is_typed else None
        diagnostics = result.get("diagnostics", {})
        timing = result.get("timing", {})
        compiler = backend.get("compiler") or backend.get("backend") or "—"
        program_id = backend.get("program_id") or "—"
        seconds = timing.get("inference_seconds", timing.get("typing_inference_seconds"))
        rows.append(
            "| "
            + " | ".join(
                [
                    f"`{path.name}`",
                    f"`{short_path(result.get('data'))}`",
                    f"`{compiler}`",
                    f"`{program_id}`",
                    integer(diagnostics.get("errors")),
                    decimal(extraction.get("precision")),
                    decimal(extraction.get("recall")),
                    decimal(extraction.get("f1")),
                    decimal(typed.get("precision")),
                    decimal(typed.get("recall")),
                    decimal(typed.get("f1")),
                    decimal(type_accuracy),
                    decimal(seconds, 1),
                ]
            )
            + " |"
        )
    return rows


def program_rows() -> list[str]:
    rows: list[str] = []
    for path in sorted(RESULTS_DIR.glob("*.json")):
        if path.name.endswith(".summary.json"):
            continue
        try:
            manifest = read_json(path)
        except (json.JSONDecodeError, OSError):
            continue
        if not manifest.get("program_id") or not manifest.get("spec"):
            continue
        public = manifest.get("public")
        if public is True:
            public_text = "yes"
        elif public is False:
            public_text = "no"
        else:
            public_text = "—"
        rows.append(
            "| "
            + " | ".join(
                [
                    f"`{path.name}`",
                    f"`{manifest.get('compiler', '—')}`",
                    f"`{manifest.get('compiler_kind', '—')}`",
                    f"`{manifest['program_id']}`",
                    public_text,
                    f"`{manifest.get('base_program_id', '—')}`",
                    f"`{manifest.get('spec_path', '—')}`",
                    f"`{str(manifest.get('spec_sha256', '—'))[:12]}`",
                ]
            )
            + " |"
        )
    return rows


def headline_sections() -> list[str]:
    lines: list[str] = []
    benchmark_path = ROOT / "artifacts" / "benchmark-comparison.json"
    optimization_path = ROOT / "artifacts" / "train500-optimization.json"
    finetune_path = ROOT / "artifacts" / "finetune-optimization.json"
    if benchmark_path.exists():
        benchmark = read_json(benchmark_path)
        systems = benchmark["systems"]
        lines.extend(
            [
                "## Frozen held-out comparison before the finetune search",
                "",
                "| System | Extraction precision | Extraction recall | Extraction F1 |",
                "| --- | ---: | ---: | ---: |",
            ]
        )
        for name, payload in systems.items():
            metric = payload["character"]
            lines.append(
                f"| {name} | {decimal(metric['precision'])} | "
                f"{decimal(metric['recall'])} | {decimal(metric['f1'])} |"
            )
        lines.append("")
    if optimization_path.exists():
        optimization = read_json(optimization_path)
        untyped = optimization["untyped"]
        typed = optimization["single_pass_typed"]
        lines.extend(
            [
                "## Standard compiler search on the 477-document training-development set",
                "",
                "### Label-agnostic extraction",
                "",
                "| Candidate | Program | Extraction F1 |",
                "| --- | --- | ---: |",
            ]
        )
        for candidate in untyped["candidates_on_training_development"]:
            lines.append(
                f"| {candidate['name']} | `{candidate['program_id']}` | "
                f"{decimal(candidate['f1'])} |"
            )
        held_out = untyped["held_out_test"]
        lines.extend(
            [
                "",
                (
                    f"Frozen winner `{untyped['winner']['program_id']}`: held-out "
                    f"extraction F1 {decimal(held_out['f1'])} "
                    f"(precision {decimal(held_out['precision'])}, "
                    f"recall {decimal(held_out['recall'])})."
                ),
                "",
                "### One-pass typed extraction",
                "",
                "| Candidate | Program | Extraction F1 | Typed F1 |",
                "| --- | --- | ---: | ---: |",
            ]
        )
        for candidate in typed["candidates_on_training_development"]:
            lines.append(
                f"| {candidate['name']} | `{candidate['program_id']}` | "
                f"{decimal(candidate['extraction_f1'])} | "
                f"{decimal(candidate['typed_f1'])} |"
            )
        typed_held_out = typed["held_out_test"]
        lines.extend(
            [
                "",
                (
                    f"Frozen winner `{typed['winner']['program_id']}`: held-out "
                    f"extraction F1 {decimal(typed_held_out['extraction']['f1'])}, "
                    f"typed F1 {decimal(typed_held_out['typed']['f1'])}, and "
                    "overlapping-character type accuracy "
                    f"{decimal(typed_held_out['type_accuracy_on_overlapping_characters'])}."
                ),
                "",
            ]
        )
    if finetune_path.exists():
        finetune = read_json(finetune_path)
        untyped = finetune["label_agnostic_extraction"]
        two_stage = finetune["label_agnostic_then_classify"]
        one_pass = finetune["single_program_typed"]
        pii_tracer = finetune["pii_tracer_reference"]
        pii_tracer_gap = decimal(abs(pii_tracer["paw_extraction_f1_gap"]))
        two_stage_accuracy = decimal(
            two_stage["held_out"]["type_accuracy_on_overlapping_characters"]
        )
        one_pass_accuracy = decimal(
            one_pass["held_out"]["type_accuracy_on_overlapping_characters"]
        )
        lines.extend(
            [
                "## Finetune-compiler search on the frozen 477-document development set",
                "",
                finetune["protocol"],
                "",
                "### Label-agnostic extraction",
                "",
                "| Candidate | Spec | Program | Public | Precision | Recall | F1 | Errors |",
                "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |",
            ]
        )
        for candidate in untyped["candidates"]:
            development = candidate["development"]
            lines.append(
                f"| {candidate['name']} | `{candidate['spec_path']}` | "
                f"`{candidate['program_id']}` | {'yes' if candidate['public'] else 'no'} | "
                f"{decimal(development['precision'])} | {decimal(development['recall'])} | "
                f"{decimal(development['f1'])} | {integer(development['errors'])} |"
            )
        untyped_held_out = untyped["held_out"]
        lines.extend(
            [
                "",
                (
                    f"Frozen winner `{untyped['winner']['program_id']}`: held-out extraction "
                    f"F1 {decimal(untyped_held_out['f1'])} (precision "
                    f"{decimal(untyped_held_out['precision'])}, recall "
                    f"{decimal(untyped_held_out['recall'])})."
                ),
                (
                    f"PII-Tracer reaches {decimal(pii_tracer['f1'])} extraction F1 on "
                    f"the same held-out sample, a {pii_tracer_gap} "
                    "absolute advantage; PAW has higher precision but lower recall."
                ),
                "",
                "### Label-agnostic extraction followed by type classification",
                "",
                "| Classifier candidate | Spec | Program | Context characters | Typed F1 | "
                "Type accuracy on overlap | Errors |",
                "| --- | --- | --- | ---: | ---: | ---: | ---: |",
            ]
        )
        for candidate in two_stage["classifier_candidates"]:
            development = candidate["development"]
            lines.append(
                f"| {candidate['name']} | `{candidate['spec_path']}` | "
                f"`{candidate['program_id']}` | {candidate['context_characters']} | "
                f"{decimal(development['typed_f1'])} | "
                f"{decimal(development['type_accuracy_on_overlapping_characters'])} | "
                f"{integer(development['errors'])} |"
            )
        two_stage_held_out = two_stage["held_out"]
        lines.extend(
            [
                "",
                (
                    f"Frozen pipeline `{two_stage['winner']['extractor_program_id']}` → "
                    f"`{two_stage['winner']['classifier_program_id']}` with "
                    f"{two_stage['winner']['context_characters']} context characters: held-out "
                    f"extraction F1 {decimal(two_stage_held_out['extraction_f1'])}, typed F1 "
                    f"{decimal(two_stage_held_out['typed_f1'])}, and overlapping-character type "
                    f"accuracy {two_stage_accuracy}."
                ),
                "",
                "### Single-program typed extraction",
                "",
                "| Candidate | Spec | Program | Public | Extraction F1 | Typed F1 | "
                "Type accuracy on overlap | Errors |",
                "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |",
            ]
        )
        for candidate in one_pass["candidates"]:
            development = candidate["development"]
            lines.append(
                f"| {candidate['name']} | `{candidate['spec_path']}` | "
                f"`{candidate['program_id']}` | {'yes' if candidate['public'] else 'no'} | "
                f"{decimal(development['extraction_f1'])} | "
                f"{decimal(development['typed_f1'])} | "
                f"{decimal(development['type_accuracy_on_overlapping_characters'])} | "
                f"{integer(development['errors'])} |"
            )
        one_pass_held_out = one_pass["held_out"]
        lines.extend(
            [
                "",
                (
                    f"Frozen winner `{one_pass['winner']['program_id']}`: held-out extraction "
                    f"F1 {decimal(one_pass_held_out['extraction_f1'])}, typed F1 "
                    f"{decimal(one_pass_held_out['typed_f1'])}, and overlapping-character type "
                    f"accuracy {one_pass_accuracy}."
                ),
                "",
                "### Compile failures retained in the audit trail",
                "",
            ]
        )
        for failure in finetune["compile_failures"]:
            lines.append(
                f"- `{failure['spec_path']}` ({integer(failure['spec_characters'])} characters), "
                f"job `{failure['job_id']}`: {failure['error']}."
            )
        lines.append("")
    return lines


def exact_specs() -> list[str]:
    lines = ["## Exact current specifications", ""]
    for path in sorted(SPECS_DIR.glob("*.txt")):
        text = path.read_text(encoding="utf-8").strip()
        validate_spec(path, text)
        digest = hashlib.sha256(text.encode()).hexdigest()
        lines.extend(
            [
                "<details>",
                (
                    f"<summary><code>{path.relative_to(ROOT)}</code> — "
                    f"SHA-256 <code>{digest}</code></summary>"
                ),
                "",
                "```text",
                text,
                "```",
                "",
                "</details>",
                "",
            ]
        )
    return lines


def main() -> None:
    lines = [
        "# PAW PII experiment log",
        "",
        f"Generated at {datetime.now(UTC).isoformat()} by `scripts/render_results_markdown.py`.",
        "",
        (
            "This file records every benchmark summary currently present under "
            "`results/` and embeds every current specification verbatim. The renderer "
            "rejects CR characters, trailing whitespace, and adjacent prose lines that "
            "look like editor-inserted soft wrapping."
        ),
        "",
        "## Protocol",
        "",
        (
            "- Specification development uses only "
            "`data/cache/train-development-500.jsonl`: 477 documents, 200,901 "
            "characters, and 3,363 annotated spans selected from complete AI4Privacy "
            "training groups."
        ),
        (
            "- Final evaluation uses `data/cache/held-out-test.jsonl`: 171 documents, "
            "72,069 characters, and 1,073 spans selected from the AI4Privacy "
            "validation split."
        ),
        (
            "- The held-out sample is opened only after a winner is frozen; no later "
            "specification tuning uses it."
        ),
        (
            "- Files ending in `-reparsed.summary.json` rescore the same cached raw "
            "outputs after parser improvements; they do not make additional inference "
            "calls."
        ),
        (
            "- Extraction scores are micro-averaged character precision, recall, and "
            "F1. Typed F1 requires both character coverage and the canonical nine-way "
            "type to match."
        ),
        "- All new compiles are public.",
        "",
        *headline_sections(),
        "## Compiled-program ledger",
        "",
        (
            "Every manifest that records an exact specification is listed here. Public "
            "status is copied from the compile response or manifest; an em dash means "
            "the older manifest did not record it."
        ),
        "",
        "| Manifest | Compiler | Kind | Program | Public | Base program | Spec | Spec SHA-256 |",
        "| --- | --- | --- | --- | ---: | --- | --- | --- |",
        *program_rows(),
        "",
        "## Complete result-file ledger",
        "",
        (
            "Rows with nonzero errors are retained as failed or partial runs and are "
            "not used for model selection."
        ),
        "",
        (
            "| Result file | Data | Compiler/backend | Program | Errors | Extract P | "
            "Extract R | Extract F1 | Typed P | Typed R | Typed F1 | Type accuracy on "
            "overlap | Inference seconds |"
        ),
        "| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        *summary_rows(),
        "",
        *exact_specs(),
    ]
    OUTPUT.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    print(OUTPUT)


if __name__ == "__main__":
    main()
