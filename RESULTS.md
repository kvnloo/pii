# PAW PII experiment log

Generated at 2026-09-03T16:29:51.257008+00:00 by `scripts/render_results_markdown.py`.

This file records every benchmark summary currently present under `results/` and embeds every current specification verbatim. The renderer rejects CR characters, trailing whitespace, and adjacent prose lines that look like editor-inserted soft wrapping.

## Protocol

- The historical specification search used `data/cache/train-development-500.jsonl`: 477 documents, 200,901 characters, and 3,363 annotated spans selected from complete AI4Privacy training groups.
- Its historical final evaluation used `data/cache/held-out-test.jsonl`: 171 documents, 72,069 characters, and 1,073 spans selected from the AI4Privacy validation split.
- The new compact-spec and output-format search uses fresh, complete, group-disjoint AI4Privacy training groups: 497 search documents, 522 selection documents, and 512 sealed-test documents. All three splits exclude the historical development groups.
- Candidate editing used only the fresh search split. The candidate set was frozen before selection; the winner was frozen before the sealed test was opened; only that winner was evaluated on sealed test.
- Files ending in `-reparsed.summary.json` rescore the same cached raw outputs after parser improvements; they do not make additional inference calls.
- Extraction scores are micro-averaged character precision, recall, and F1. Typed F1 requires both character coverage and the canonical nine-way type to match.
- All new compiles are public.

## Frozen held-out comparison before the finetune search

| System | Extraction precision | Extraction recall | Extraction F1 |
| --- | ---: | ---: | ---: |
| PAW-Finetuned | 0.7920 | 0.9558 | 0.8662 |
| PAW-Standard | 0.8884 | 0.8763 | 0.8823 |
| PII-Tracer | 0.8856 | 0.9988 | 0.9388 |

## Standard compiler search on the 477-document training-development set

### Label-agnostic extraction

| Candidate | Program | Extraction F1 |
| --- | --- | ---: |
| v2-unwrapped | `62ad5f23c25d28feb8d9` | 0.8716 |
| v3-unwrapped | `926a5dde263a01ee3aba` | 0.8876 |
| v4 | `3f49aef230cd5137c018` | 0.8608 |
| v5 | `1246ff68791dd575c6fb` | 0.8861 |
| v6 | `efec3da668a9219b5672` | 0.8663 |
| v8 | `b098f2474256dc8387c4` | 0.8800 |

Frozen winner `926a5dde263a01ee3aba`: held-out extraction F1 0.8832 (precision 0.8687, recall 0.8981).

### One-pass typed extraction

| Candidate | Program | Extraction F1 | Typed F1 |
| --- | --- | ---: | ---: |
| typed-v4-object-baseline | `88108e7c09b0d0647261` | 0.8586 | 0.6963 |
| typed-v5 | `09e62d3fc156e8727b2b` | 0.8642 | 0.7120 |
| typed-v6 | `b6d75fb98aed4f9a9a8c` | 0.8268 | 0.6262 |
| typed-v7 | `a24c81954a02a4278090` | 0.8735 | 0.7583 |
| typed-v8 | `70c52fb8c07d1e2b0f91` | 0.8722 | 0.7536 |
| typed-v9 | `0b5d25bf37b5b09025df` | 0.8707 | 0.7420 |

Frozen winner `a24c81954a02a4278090`: held-out extraction F1 0.8505, typed F1 0.7668, and overlapping-character type accuracy 0.9047.

## Finetune-compiler search on the frozen 477-document development set

All specification and context-window choices were made on the 477-document training-development set. Each architecture's winner was frozen before its first and only run on the validation-derived held-out set; no tuning followed held-out evaluation. Every successful compile in this search was public.

### Label-agnostic extraction

| Candidate | Spec | Program | Public | Precision | Recall | F1 | Errors |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| unwrapped-v3 | `specs/pii-detector-v3.txt` | `5c1dd556e6856784df12` | yes | 0.8792 | 0.9494 | 0.9130 | 0 |
| unwrapped-v6 | `specs/pii-detector-v6.txt` | `08bf7c7e6abcbbf52e14` | yes | 0.8819 | 0.9433 | 0.9116 | 0 |
| ft-v1-targeted | `specs/pii-detector-ft-v1.txt` | `b263201af3d35848fbb3` | yes | 0.9162 | 0.9170 | 0.9166 | 0 |
| ft-v2-balanced | `specs/pii-detector-ft-v2.txt` | `fd5cf07ef9fd59d15b9b` | yes | 0.9034 | 0.9247 | 0.9139 | 0 |
| ft-v3-deduplicated-values | `specs/pii-detector-ft-v3.txt` | `3cd1943e8c75147e28da` | yes | 0.9188 | 0.9039 | 0.9113 | 0 |
| ft-v4-occurrence-aware | `specs/pii-detector-ft-v4.txt` | `51c7f878cae07de144bd` | yes | 0.9349 | 0.8970 | 0.9155 | 0 |

Frozen winner `b263201af3d35848fbb3`: held-out extraction F1 0.9103 (precision 0.9025, recall 0.9182).
PII-Tracer reaches 0.9388 extraction F1 on the same held-out sample, a 0.0285 absolute advantage; PAW has higher precision but lower recall.

### Label-agnostic extraction followed by type classification

| Classifier candidate | Spec | Program | Context characters | Typed F1 | Type accuracy on overlap | Errors |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| classifier-v2-context-24 | `specs/pii-type-classifier-v2.txt` | `5603f8370b2df0e4bd27` | 24 | 0.7201 | 0.7863 | 0 |
| classifier-ft-v1-context-24 | `specs/pii-type-classifier-ft-v1.txt` | `91bf7b6cc82d95b24693` | 24 | 0.7806 | 0.8551 | 0 |
| classifier-ft-v2-context-24 | `specs/pii-type-classifier-ft-v2.txt` | `2ebae87e0748d1a62a4b` | 24 | 0.7954 | 0.8701 | 0 |
| classifier-ft-v2-context-48 | `specs/pii-type-classifier-ft-v2.txt` | `2ebae87e0748d1a62a4b` | 48 | 0.7960 | 0.8712 | 0 |
| classifier-ft-v2-context-64 | `specs/pii-type-classifier-ft-v2.txt` | `2ebae87e0748d1a62a4b` | 64 | 0.7929 | 0.8682 | 0 |

Frozen pipeline `b263201af3d35848fbb3` → `2ebae87e0748d1a62a4b` with 48 context characters: held-out extraction F1 0.9103, typed F1 0.7947, and overlapping-character type accuracy 0.8744.

### Single-program typed extraction

| Candidate | Spec | Program | Public | Extraction F1 | Typed F1 | Type accuracy on overlap | Errors |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| typed-v7 | `specs/pii-detector-typed-v7.txt` | `ee8e65ca8120ba86d76a` | yes | 0.8778 | 0.7917 | 0.9075 | 0 |
| typed-ft-v1-targeted | `specs/pii-detector-typed-ft-v1.txt` | `73a0e38b8bbe3427cd1d` | yes | 0.9061 | 0.8221 | 0.9122 | 0 |
| typed-ft-v3-compact-high-recall | `specs/pii-detector-typed-ft-v3.txt` | `59d3c0f5e576b07df4a9` | yes | 0.8679 | 0.8201 | 0.9510 | 0 |
| typed-ft-v4-balanced | `specs/pii-detector-typed-ft-v4.txt` | `796978fe50b4701d96a4` | yes | 0.8535 | 0.7865 | 0.9266 | 0 |

Frozen winner `73a0e38b8bbe3427cd1d`: held-out extraction F1 0.8830, typed F1 0.8366, and overlapping-character type accuracy 0.9499.

### Compile failures retained in the audit trail

- `specs/pii-detector-typed-ft-v2.txt` (14524 characters), job `bb48be04465c40f489db67d2af67b01c`: HTTP 422 Unprocessable Entity from the finetune compile provider; no program was produced.

## Fresh group-disjoint compact-spec and output-format search

The search set contains 497 documents, the selection set contains 522, and the sealed test contains 512. Complete source groups are pairwise disjoint and exclude the historical development groups. Candidate editing used only search; the candidate set was then frozen for selection, and only the selection winner was opened on sealed test.

### Search-set candidates

| Candidate | Spec characters | Output shape | Program | Extract P | Extract R | Extract F1 | Typed P | Typed R | Typed F1 | Errors |
| --- | ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| published-baseline | 8209 | JSON [text,type] pairs | `73a0e38b8bbe3427cd1d` | 0.8912 | 0.9168 | 0.9038 | 0.8294 | 0.8658 | 0.8472 | 0 |
| compact-zero-example | 2234 | JSON [text,type] pairs | `af7dc8a9606e3c3a7c6b` | 0.8635 | 0.9468 | 0.9032 | 0.7984 | 0.8851 | 0.8395 | 0 |
| compact-three-example-text-first | 3089 | JSON [text,type] pairs | `a6f44175f8750d57e148` | 0.8691 | 0.9430 | 0.9045 | 0.8096 | 0.8882 | 0.8471 | 0 |
| compact-three-example-type-first | 3089 | JSON [type,text] pairs | `021a90c2c6cd7b103909` | 0.8589 | 0.9322 | 0.8940 | 0.7706 | 0.8490 | 0.8079 | 0 |
| compact-three-example-tsv | 3002 | TSV type then text | `f8c67de4cd93553cd38f` | 0.8167 | 0.9404 | 0.8742 | 0.7403 | 0.8643 | 0.7975 | 0 |
| compact-three-example-objects | 3350 | JSON objects with text and type | `75af38369b880b3b680b` | 0.8611 | 0.9373 | 0.8976 | 0.7891 | 0.8689 | 0.8271 | 0 |
| compact-restraint-v2 | 3907 | JSON [text,type] pairs | `84e670f39693f2f67a65` | 0.8759 | 0.9482 | 0.9106 | 0.8109 | 0.8873 | 0.8473 | 0 |

Compact text-first JSON tied the baseline on search: its typed-F1 change was -0.0001 with a 95% paired-bootstrap interval [-0.0235, 0.0229]. The targeted restraint variant also tied on typed F1 while appearing to improve extraction, but its extraction interval [-0.0072, 0.0215] still included zero.

Among alternate encodings, text-first compact JSON was clearly strongest. Reversing the pair order, using TSV, and using verbose JSON objects reduced typed F1 to 0.8079, 0.7975, and 0.8271 respectively. Zero-example JSON reached 0.8395, indicating that a few examples materially help the small interpreter.

### Independent selection

| Finalist | Program | Extract P | Extract R | Extract F1 | Typed P | Typed R | Typed F1 | Errors |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| published-baseline | `73a0e38b8bbe3427cd1d` | 0.8892 | 0.9203 | 0.9045 | 0.8163 | 0.8488 | 0.8323 | 0 |
| compact-three-example-text-first | `a6f44175f8750d57e148` | 0.8431 | 0.9393 | 0.8886 | 0.7848 | 0.8758 | 0.8278 | 0 |
| compact-restraint-v2 | `84e670f39693f2f67a65` | 0.8369 | 0.9252 | 0.8788 | 0.7537 | 0.8366 | 0.7929 | 0 |

The search-set tie did not generalize. Compact text-first JSON lost 0.0159 extraction F1 versus baseline; its 95% interval [-0.0316, -0.0006] excludes zero. Its typed-F1 difference remained uncertain.

The targeted restraint variant overfit more strongly, losing 0.0256 extraction F1 and 0.0393 typed F1. Both paired-bootstrap intervals exclude zero.

Winner: `73a0e38b8bbe3427cd1d` using `specs/pii-detector-typed-ft-v1.txt`. It had the strongest extraction and typed F1 on the independent selection set. The compact three-example candidate had statistically worse extraction, while compact-restraint-v2 had statistically worse extraction and typed F1. Specification length does not complicate the public one-program inference interface because compilation happens once.

### Sealed result

The frozen winner scored extraction F1 0.9085 (precision 0.9005, recall 0.9167) and typed F1 0.8464 (precision 0.8384, recall 0.8546) on the untouched 512-document sealed set. Type accuracy on overlapping characters was 0.9394; inference errors were 0.

### Decision

Keep the existing public one-pass typed program. Compact text-first JSON pairs are the best alternative shape, but simplifying the specification did not generalize. Do not switch to zero-shot, reversed pairs, TSV, or JSON objects based on these results.

- JSON is already the right family, but compact pairs outperform verbose objects and text-first order strongly outperforms type-first order.
- Three examples recover most of the zero-example loss, so examples are useful even for the 0.6B interpreter.
- TSV eliminated malformed outputs but still produced far worse F1, showing that syntactic validity was not the main bottleneck.
- The compact candidates traded precision for recall. Their apparent search-set gains did not survive independent selection, especially for the targeted restraint variant.
- The long specification remains worthwhile for accuracy because users call only the compiled program ID; its length does not make the README or inference interface more complex.

A post-selection compatibility check on the historical development set agreed: baseline typed F1 was 0.8221, versus 0.7939 for compact-three and 0.7873 for compact-restraint-v2. These runs did not affect selection.

## Compiled-program ledger

Every manifest that records an exact specification is listed here. Public status is copied from the compile response or manifest; an em dash means the older manifest did not record it.

| Manifest | Compiler | Kind | Program | Public | Base program | Spec | Spec SHA-256 |
| --- | --- | --- | --- | ---: | --- | --- | --- |
| `paw-finetuned-extractor-ft-v1-public.json` | `paw-ft-bs48` | `finetune_lora` | `b263201af3d35848fbb3` | yes | `8391850e016111dcf1cb` | `specs/pii-detector-ft-v1.txt` | `3acfa184dd9c` |
| `paw-finetuned-extractor-ft-v2-public.json` | `paw-ft-bs48` | `finetune_lora` | `fd5cf07ef9fd59d15b9b` | yes | `13c07f47924a21a263f1` | `specs/pii-detector-ft-v2.txt` | `0d186ae98b76` |
| `paw-finetuned-extractor-ft-v3-public.json` | `paw-ft-bs48` | `finetune_lora` | `3cd1943e8c75147e28da` | yes | `2e2e3e46afa6000be679` | `specs/pii-detector-ft-v3.txt` | `15ff492c26a8` |
| `paw-finetuned-extractor-ft-v4-public.json` | `paw-ft-bs48` | `finetune_lora` | `51c7f878cae07de144bd` | yes | `0532bfba3c11c7b26386` | `specs/pii-detector-ft-v4.txt` | `708f29fc8f9a` |
| `paw-finetuned-type-classifier-ft-v1-public.json` | `paw-ft-bs48` | `finetune_lora` | `91bf7b6cc82d95b24693` | yes | `5e5a7a161856b780fd44` | `specs/pii-type-classifier-ft-v1.txt` | `863546c871d7` |
| `paw-finetuned-type-classifier-ft-v2-public.json` | `paw-ft-bs48` | `finetune_lora` | `2ebae87e0748d1a62a4b` | yes | `00f021ca1ff122188469` | `specs/pii-type-classifier-ft-v2.txt` | `f505e824aba4` |
| `paw-finetuned-type-classifier-v2-public.json` | `paw-ft-bs48` | `finetune_lora` | `5603f8370b2df0e4bd27` | yes | `14451a1c1a7ac3720f79` | `specs/pii-type-classifier-v2.txt` | `c8ad02530828` |
| `paw-finetuned-typed-compact-restraint-v2-public.json` | `paw-ft-bs48` | `finetune_lora` | `84e670f39693f2f67a65` | yes | `38b7ea8c22840954999e` | `specs/pii-detector-typed-compact-restraint-v2.txt` | `695cfb888890` |
| `paw-finetuned-typed-compact-three-objects-v1-public.json` | `paw-ft-bs48` | `finetune_lora` | `75af38369b880b3b680b` | yes | `735aa72a439717022ee3` | `specs/pii-detector-typed-compact-three-objects-v1.txt` | `b370dd6243dd` |
| `paw-finetuned-typed-compact-three-text-type-v1-public.json` | `paw-ft-bs48` | `finetune_lora` | `a6f44175f8750d57e148` | yes | `b73867e45b9db559bbe2` | `specs/pii-detector-typed-compact-three-text-type-v1.txt` | `c5cf3e9ca32c` |
| `paw-finetuned-typed-compact-three-tsv-v1-public.json` | `paw-ft-bs48` | `finetune_lora` | `f8c67de4cd93553cd38f` | yes | `9e5241ed95e1e21de7cd` | `specs/pii-detector-typed-compact-three-tsv-v1.txt` | `c77a491e4163` |
| `paw-finetuned-typed-compact-three-type-text-v1-public.json` | `paw-ft-bs48` | `finetune_lora` | `021a90c2c6cd7b103909` | yes | `6c1abf40fc5733e37c29` | `specs/pii-detector-typed-compact-three-type-text-v1.txt` | `816e4a25e226` |
| `paw-finetuned-typed-compact-zero-v1-public.json` | `paw-ft-bs48` | `finetune_lora` | `af7dc8a9606e3c3a7c6b` | yes | `7bf73f09acaa18fd7a1d` | `specs/pii-detector-typed-compact-zero-v1.txt` | `7fcaf93482a8` |
| `paw-finetuned-typed-ft-v1-public.json` | `paw-ft-bs48` | `finetune_lora` | `73a0e38b8bbe3427cd1d` | yes | `b28c5b6797a4730cfcf4` | `specs/pii-detector-typed-ft-v1.txt` | `376fae3801e2` |
| `paw-finetuned-typed-ft-v3-public.json` | `paw-ft-bs48` | `finetune_lora` | `59d3c0f5e576b07df4a9` | yes | `1f2bc8cf422157078041` | `specs/pii-detector-typed-ft-v3.txt` | `99ee309c2064` |
| `paw-finetuned-typed-ft-v4-public.json` | `paw-ft-bs48` | `finetune_lora` | `796978fe50b4701d96a4` | yes | `80c2f5252257a1916320` | `specs/pii-detector-typed-ft-v4.txt` | `6332033b0f8d` |
| `paw-finetuned-typed-v7-public.json` | `paw-ft-bs48` | `finetune_lora` | `ee8e65ca8120ba86d76a` | yes | `a24c81954a02a4278090` | `specs/pii-detector-typed-v7.txt` | `e7df315d3e5e` |
| `paw-finetuned-v3-unwrapped-public.json` | `paw-ft-bs48` | `finetune_lora` | `5c1dd556e6856784df12` | yes | `926a5dde263a01ee3aba` | `specs/pii-detector-v3.txt` | `5d79d565fc46` |
| `paw-finetuned-v6-public.json` | `paw-ft-bs48` | `finetune_lora` | `08bf7c7e6abcbbf52e14` | yes | `efec3da668a9219b5672` | `specs/pii-detector-v6.txt` | `61d01ac67866` |
| `paw-standard-type-classifier-v2-unwrapped.json` | `paw-4b-qwen3-0.6b` | `mapper_lora` | `14451a1c1a7ac3720f79` | — | `—` | `specs/pii-type-classifier-v2.txt` | `c8ad02530828` |
| `paw-standard-type-classifier-v2.json` | `paw-4b-qwen3-0.6b` | `mapper_lora` | `a2451b2cf887000e94a4` | — | `—` | `specs/pii-type-classifier-v2.txt` | `7052f551f58a` |
| `paw-standard-typed-v4.json` | `paw-4b-qwen3-0.6b` | `mapper_lora` | `88108e7c09b0d0647261` | — | `—` | `specs/pii-detector-typed-v4.txt` | `506340836dac` |
| `paw-standard-typed-v5.json` | `paw-4b-qwen3-0.6b` | `mapper_lora` | `09e62d3fc156e8727b2b` | yes | `—` | `specs/pii-detector-typed-v5.txt` | `23319200618c` |
| `paw-standard-typed-v6.json` | `paw-4b-qwen3-0.6b` | `mapper_lora` | `b6d75fb98aed4f9a9a8c` | yes | `—` | `specs/pii-detector-typed-v6.txt` | `0b760ac100db` |
| `paw-standard-typed-v7.json` | `paw-4b-qwen3-0.6b` | `mapper_lora` | `a24c81954a02a4278090` | yes | `—` | `specs/pii-detector-typed-v7.txt` | `e7df315d3e5e` |
| `paw-standard-typed-v8.json` | `paw-4b-qwen3-0.6b` | `mapper_lora` | `70c52fb8c07d1e2b0f91` | yes | `—` | `specs/pii-detector-typed-v8.txt` | `99ea5102b2e1` |
| `paw-standard-typed-v9.json` | `paw-4b-qwen3-0.6b` | `mapper_lora` | `0b5d25bf37b5b09025df` | yes | `—` | `specs/pii-detector-typed-v9.txt` | `704dac3ff661` |
| `paw-standard-typer-v1.json` | `paw-4b-qwen3-0.6b` | `mapper_lora` | `dddd7aaa555d7782583e` | — | `—` | `specs/pii-typer-v1.txt` | `3e3fb2182547` |
| `paw-standard-v1-unwrapped.json` | `paw-4b-qwen3-0.6b` | `mapper_lora` | `f09d9e8f81946b54b9c3` | — | `—` | `specs/pii-detector-v1.txt` | `d7a09102aac8` |
| `paw-standard-v1.json` | `paw-4b-qwen3-0.6b` | `—` | `04f8a0b669efa431b4b0` | — | `—` | `specs/pii-detector-v1.txt` | `5442e4a42f44` |
| `paw-standard-v2-unwrapped.json` | `paw-4b-qwen3-0.6b` | `mapper_lora` | `62ad5f23c25d28feb8d9` | — | `—` | `specs/pii-detector-v2.txt` | `416e8b966eb4` |
| `paw-standard-v2.json` | `paw-4b-qwen3-0.6b` | `—` | `1c5eec7b1781d76ce816` | — | `—` | `specs/pii-detector-v2.txt` | `28e1bed833f5` |
| `paw-standard-v3-unwrapped.json` | `paw-4b-qwen3-0.6b` | `mapper_lora` | `926a5dde263a01ee3aba` | yes | `—` | `specs/pii-detector-v3.txt` | `5d79d565fc46` |
| `paw-standard-v3.json` | `paw-4b-qwen3-0.6b` | `—` | `d71e2fb30e99b0edd992` | — | `—` | `specs/pii-detector-v3.txt` | `54f0a0dc7137` |
| `paw-standard-v4.json` | `paw-4b-qwen3-0.6b` | `mapper_lora` | `3f49aef230cd5137c018` | — | `—` | `specs/pii-detector-v4.txt` | `057fcec2d57c` |
| `paw-standard-v5.json` | `paw-4b-qwen3-0.6b` | `mapper_lora` | `1246ff68791dd575c6fb` | — | `—` | `specs/pii-detector-v5.txt` | `bb77b78b086b` |
| `paw-standard-v6.json` | `paw-4b-qwen3-0.6b` | `mapper_lora` | `efec3da668a9219b5672` | — | `—` | `specs/pii-detector-v6.txt` | `61d01ac67866` |
| `paw-standard-v8.json` | `paw-4b-qwen3-0.6b` | `mapper_lora` | `b098f2474256dc8387c4` | yes | `—` | `specs/pii-detector-v8.txt` | `3cffc79c7a98` |

## Complete result-file ledger

Rows with nonzero errors are retained as failed or partial runs and are not used for model selection.

| Result file | Data | Compiler/backend | Program | Errors | Extract P | Extract R | Extract F1 | Typed P | Typed R | Typed F1 | Type accuracy on overlap | Inference seconds |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `fresh-sealed-test-v2-paw-finetuned-typed-ft-v1-final.summary.json` | `fresh-sealed-test-v2.jsonl` | `paw-ft-bs48` | `73a0e38b8bbe3427cd1d` | 0 | 0.9005 | 0.9167 | 0.9085 | 0.8384 | 0.8546 | 0.8464 | 0.9394 | 941.8 |
| `fresh-search-v2-paw-finetuned-typed-compact-restraint-v2.summary.json` | `fresh-search-v2.jsonl` | `paw-ft-bs48` | `84e670f39693f2f67a65` | 0 | 0.8759 | 0.9482 | 0.9106 | 0.8109 | 0.8873 | 0.8473 | 0.9357 | 858.6 |
| `fresh-search-v2-paw-finetuned-typed-compact-three-objects-v1.summary.json` | `fresh-search-v2.jsonl` | `paw-ft-bs48` | `75af38369b880b3b680b` | 0 | 0.8611 | 0.9373 | 0.8976 | 0.7891 | 0.8689 | 0.8271 | 0.9270 | 1130.0 |
| `fresh-search-v2-paw-finetuned-typed-compact-three-text-type-v1.summary.json` | `fresh-search-v2.jsonl` | `paw-ft-bs48` | `a6f44175f8750d57e148` | 0 | 0.8691 | 0.9430 | 0.9045 | 0.8096 | 0.8882 | 0.8471 | 0.9420 | 987.5 |
| `fresh-search-v2-paw-finetuned-typed-compact-three-tsv-v1.summary.json` | `fresh-search-v2.jsonl` | `paw-ft-bs48` | `f8c67de4cd93553cd38f` | 0 | 0.8167 | 0.9404 | 0.8742 | 0.7403 | 0.8643 | 0.7975 | 0.9191 | 874.8 |
| `fresh-search-v2-paw-finetuned-typed-compact-three-type-text-v1.summary.json` | `fresh-search-v2.jsonl` | `paw-ft-bs48` | `021a90c2c6cd7b103909` | 0 | 0.8589 | 0.9322 | 0.8940 | 0.7706 | 0.8490 | 0.8079 | 0.9107 | 926.3 |
| `fresh-search-v2-paw-finetuned-typed-compact-zero-v1.summary.json` | `fresh-search-v2.jsonl` | `paw-ft-bs48` | `af7dc8a9606e3c3a7c6b` | 0 | 0.8635 | 0.9468 | 0.9032 | 0.7984 | 0.8851 | 0.8395 | 0.9348 | 927.8 |
| `fresh-search-v2-paw-finetuned-typed-ft-v1-baseline.summary.json` | `fresh-search-v2.jsonl` | `paw-ft-bs48` | `73a0e38b8bbe3427cd1d` | 0 | 0.8912 | 0.9168 | 0.9038 | 0.8294 | 0.8658 | 0.8472 | 0.9443 | 813.5 |
| `fresh-selection-v2-paw-finetuned-typed-compact-restraint-v2.summary.json` | `fresh-selection-v2.jsonl` | `paw-ft-bs48` | `84e670f39693f2f67a65` | 0 | 0.8369 | 0.9252 | 0.8788 | 0.7537 | 0.8366 | 0.7929 | 0.9079 | 947.2 |
| `fresh-selection-v2-paw-finetuned-typed-compact-three-text-type-v1.summary.json` | `fresh-selection-v2.jsonl` | `paw-ft-bs48` | `a6f44175f8750d57e148` | 0 | 0.8431 | 0.9393 | 0.8886 | 0.7848 | 0.8758 | 0.8278 | 0.9363 | 795.6 |
| `fresh-selection-v2-paw-finetuned-typed-ft-v1-baseline.summary.json` | `fresh-selection-v2.jsonl` | `paw-ft-bs48` | `73a0e38b8bbe3427cd1d` | 0 | 0.8892 | 0.9203 | 0.9045 | 0.8163 | 0.8488 | 0.8323 | 0.9262 | 907.4 |
| `held-out-test-paw-finetuned-extractor-ft-v1-final.summary.json` | `held-out-test.jsonl` | `paw-ft-bs48` | `b263201af3d35848fbb3` | 0 | 0.9025 | 0.9182 | 0.9103 | — | — | — | — | 170.1 |
| `held-out-test-paw-finetuned-two-stage-ft-v1-ft-v2-ctx48-final.summary.json` | `held-out-test.jsonl` | `paw-ft-bs48` | `2ebae87e0748d1a62a4b` | 0 | 0.9025 | 0.9182 | 0.9103 | 0.7867 | 0.8029 | 0.7947 | 0.8744 | 213.1 |
| `held-out-test-paw-finetuned-typed-ft-v1-final.summary.json` | `held-out-test.jsonl` | `paw-ft-bs48` | `73a0e38b8bbe3427cd1d` | 0 | 0.8535 | 0.9147 | 0.8830 | 0.8065 | 0.8689 | 0.8366 | 0.9499 | 215.7 |
| `held-out-test-paw-finetuned-v3.summary.json` | `held-out-test.jsonl` | `paw-ft-bs48` | `4cd2c6c58a9c0cf42fdd` | 0 | 0.7920 | 0.9558 | 0.8662 | — | — | — | — | 325.0 |
| `held-out-test-paw-standard-typed-v7.summary.json` | `held-out-test.jsonl` | `paw-4b-qwen3-0.6b` | `a24c81954a02a4278090` | 0 | 0.8028 | 0.9043 | 0.8505 | 0.7215 | 0.8182 | 0.7668 | 0.9047 | 271.8 |
| `held-out-test-paw-standard-v3-typed-v2-ctx24.summary.json` | `held-out-test.jsonl` | `paw-4b-qwen3-0.6b` | `a2451b2cf887000e94a4` | 0 | 0.8884 | 0.8763 | 0.8823 | 0.7155 | 0.7064 | 0.7109 | 0.8061 | 90.7 |
| `held-out-test-paw-standard-v3-unwrapped.summary.json` | `held-out-test.jsonl` | `paw-4b-qwen3-0.6b` | `926a5dde263a01ee3aba` | 0 | 0.8687 | 0.8981 | 0.8832 | — | — | — | — | 401.2 |
| `held-out-test-paw-standard-v3.summary.json` | `held-out-test.jsonl` | `paw-4b-qwen3-0.6b` | `d71e2fb30e99b0edd992` | 0 | 0.8884 | 0.8763 | 0.8823 | — | — | — | — | 331.6 |
| `held-out-test-pplx.summary.json` | `held-out-test.jsonl` | `pplx-pii-tracer` | `—` | 0 | 0.8856 | 0.9988 | 0.9388 | — | — | — | — | 379.7 |
| `train-development-500-paw-finetuned-extractor-ft-v1-reparsed-type-ft-v1-ctx24.summary.json` | `train-development-500.jsonl` | `paw-ft-bs48` | `91bf7b6cc82d95b24693` | 0 | 0.9162 | 0.9170 | 0.9166 | 0.7772 | 0.7841 | 0.7806 | 0.8551 | 712.5 |
| `train-development-500-paw-finetuned-extractor-ft-v1-reparsed-type-ft-v2-ctx24.summary.json` | `train-development-500.jsonl` | `paw-ft-bs48` | `5603f8370b2df0e4bd27` | 0 | 0.9162 | 0.9170 | 0.9166 | 0.7191 | 0.7210 | 0.7201 | 0.7863 | 710.5 |
| `train-development-500-paw-finetuned-extractor-ft-v1-reparsed-type-ft-v2-targeted-ctx24.summary.json` | `train-development-500.jsonl` | `paw-ft-bs48` | `2ebae87e0748d1a62a4b` | 0 | 0.9162 | 0.9170 | 0.9166 | 0.7930 | 0.7978 | 0.7954 | 0.8701 | 727.2 |
| `train-development-500-paw-finetuned-extractor-ft-v1-reparsed-type-ft-v2-targeted-ctx48.summary.json` | `train-development-500.jsonl` | `paw-ft-bs48` | `2ebae87e0748d1a62a4b` | 0 | 0.9162 | 0.9170 | 0.9166 | 0.7932 | 0.7989 | 0.7960 | 0.8712 | 717.2 |
| `train-development-500-paw-finetuned-extractor-ft-v1-reparsed-type-ft-v2-targeted-ctx64.summary.json` | `train-development-500.jsonl` | `paw-ft-bs48` | `2ebae87e0748d1a62a4b` | 0 | 0.9162 | 0.9170 | 0.9166 | 0.7898 | 0.7961 | 0.7929 | 0.8682 | 712.9 |
| `train-development-500-paw-finetuned-extractor-ft-v1-reparsed.summary.json` | `train-development-500.jsonl` | `paw-ft-bs48` | `b263201af3d35848fbb3` | 0 | 0.9162 | 0.9170 | 0.9166 | — | — | — | — | 508.3 |
| `train-development-500-paw-finetuned-extractor-ft-v1-type-ft-v2-ctx24.summary.json` | `train-development-500.jsonl` | `paw-ft-bs48` | `5603f8370b2df0e4bd27` | 0 | 0.9157 | 0.9107 | 0.9132 | 0.7184 | 0.7157 | 0.7170 | 0.7859 | 607.6 |
| `train-development-500-paw-finetuned-extractor-ft-v1-type-ft-v2-ctx64.summary.json` | `train-development-500.jsonl` | `paw-ft-bs48` | `5603f8370b2df0e4bd27` | 0 | 0.9157 | 0.9107 | 0.9132 | 0.5211 | 0.5192 | 0.5202 | 0.5701 | 1101.1 |
| `train-development-500-paw-finetuned-extractor-ft-v1.summary.json` | `train-development-500.jsonl` | `paw-ft-bs48` | `b263201af3d35848fbb3` | 0 | 0.9157 | 0.9107 | 0.9132 | — | — | — | — | 508.3 |
| `train-development-500-paw-finetuned-extractor-ft-v2-reparsed.summary.json` | `train-development-500.jsonl` | `paw-ft-bs48` | `fd5cf07ef9fd59d15b9b` | 0 | 0.9034 | 0.9247 | 0.9139 | — | — | — | — | 501.9 |
| `train-development-500-paw-finetuned-extractor-ft-v2.summary.json` | `train-development-500.jsonl` | `paw-ft-bs48` | `fd5cf07ef9fd59d15b9b` | 0 | 0.9031 | 0.9205 | 0.9117 | — | — | — | — | 501.9 |
| `train-development-500-paw-finetuned-extractor-ft-v3-reparsed.summary.json` | `train-development-500.jsonl` | `paw-ft-bs48` | `3cd1943e8c75147e28da` | 0 | 0.9188 | 0.9039 | 0.9113 | — | — | — | — | 491.7 |
| `train-development-500-paw-finetuned-extractor-ft-v3.summary.json` | `train-development-500.jsonl` | `paw-ft-bs48` | `3cd1943e8c75147e28da` | 0 | 0.9188 | 0.9039 | 0.9113 | — | — | — | — | 491.7 |
| `train-development-500-paw-finetuned-extractor-ft-v4.summary.json` | `train-development-500.jsonl` | `paw-ft-bs48` | `51c7f878cae07de144bd` | 0 | 0.9349 | 0.8970 | 0.9155 | — | — | — | — | 491.5 |
| `train-development-500-paw-finetuned-typed-compact-restraint-v2.summary.json` | `train-development-500.jsonl` | `paw-ft-bs48` | `84e670f39693f2f67a65` | 0 | 0.8490 | 0.9117 | 0.8792 | 0.7563 | 0.8209 | 0.7873 | 0.9004 | 821.7 |
| `train-development-500-paw-finetuned-typed-compact-three-text-type-v1.summary.json` | `train-development-500.jsonl` | `paw-ft-bs48` | `a6f44175f8750d57e148` | 0 | 0.8300 | 0.9321 | 0.8781 | 0.7475 | 0.8465 | 0.7939 | 0.9083 | 934.1 |
| `train-development-500-paw-finetuned-typed-ft-v1-live.summary.json` | `train-development-500.jsonl` | `paw-ft-bs48` | `73a0e38b8bbe3427cd1d` | 0 | 0.9048 | 0.9075 | 0.9061 | 0.8164 | 0.8278 | 0.8221 | 0.9122 | 653.1 |
| `train-development-500-paw-finetuned-typed-ft-v1.summary.json` | `train-development-500.jsonl` | `paw-ft-bs48` | `73a0e38b8bbe3427cd1d` | 477 | 1.0000 | 0.0000 | 0.0000 | 1.0000 | 0.0000 | 0.0000 | 1.0000 | 0.2 |
| `train-development-500-paw-finetuned-typed-ft-v3.summary.json` | `train-development-500.jsonl` | `paw-ft-bs48` | `59d3c0f5e576b07df4a9` | 0 | 0.8358 | 0.9025 | 0.8679 | 0.7851 | 0.8583 | 0.8201 | 0.9510 | 683.0 |
| `train-development-500-paw-finetuned-typed-ft-v4.summary.json` | `train-development-500.jsonl` | `paw-ft-bs48` | `796978fe50b4701d96a4` | 0 | 0.9018 | 0.8101 | 0.8535 | 0.8259 | 0.7506 | 0.7865 | 0.9266 | 615.9 |
| `train-development-500-paw-finetuned-typed-v7.summary.json` | `train-development-500.jsonl` | `paw-ft-bs48` | `ee8e65ca8120ba86d76a` | 0 | 0.8516 | 0.9056 | 0.8778 | 0.7637 | 0.8219 | 0.7917 | 0.9075 | 867.8 |
| `train-development-500-paw-finetuned-v3-unwrapped-reparsed.summary.json` | `train-development-500.jsonl` | `paw-ft-bs48` | `5c1dd556e6856784df12` | 0 | 0.8792 | 0.9494 | 0.9130 | — | — | — | — | 510.6 |
| `train-development-500-paw-finetuned-v3-unwrapped.summary.json` | `train-development-500.jsonl` | `paw-ft-bs48` | `5c1dd556e6856784df12` | 0 | 0.8798 | 0.9464 | 0.9119 | — | — | — | — | 510.6 |
| `train-development-500-paw-finetuned-v6-reparsed.summary.json` | `train-development-500.jsonl` | `paw-ft-bs48` | `08bf7c7e6abcbbf52e14` | 0 | 0.8819 | 0.9433 | 0.9116 | — | — | — | — | 588.8 |
| `train-development-500-paw-finetuned-v6.summary.json` | `train-development-500.jsonl` | `paw-ft-bs48` | `08bf7c7e6abcbbf52e14` | 0 | 0.8821 | 0.9311 | 0.9060 | — | — | — | — | 588.8 |
| `train-development-500-paw-standard-typed-v4.summary.json` | `train-development-500.jsonl` | `paw-4b-qwen3-0.6b` | `88108e7c09b0d0647261` | 0 | 0.8708 | 0.8466 | 0.8586 | 0.7030 | 0.6898 | 0.6963 | 0.8148 | 983.2 |
| `train-development-500-paw-standard-typed-v5.summary.json` | `train-development-500.jsonl` | `paw-4b-qwen3-0.6b` | `09e62d3fc156e8727b2b` | 0 | 0.8598 | 0.8688 | 0.8642 | 0.7048 | 0.7194 | 0.7120 | 0.8281 | 727.7 |
| `train-development-500-paw-standard-typed-v6.summary.json` | `train-development-500.jsonl` | `paw-4b-qwen3-0.6b` | `b6d75fb98aed4f9a9a8c` | 0 | 0.8816 | 0.7785 | 0.8268 | 0.6650 | 0.5916 | 0.6262 | 0.7599 | 679.2 |
| `train-development-500-paw-standard-typed-v7-reparsed.summary.json` | `train-development-500.jsonl` | `paw-4b-qwen3-0.6b` | `a24c81954a02a4278090` | 0 | 0.8484 | 0.9001 | 0.8735 | 0.7329 | 0.7855 | 0.7583 | 0.8727 | 763.0 |
| `train-development-500-paw-standard-typed-v7.summary.json` | `train-development-500.jsonl` | `paw-4b-qwen3-0.6b` | `a24c81954a02a4278090` | 0 | 0.8531 | 0.8796 | 0.8662 | 0.7368 | 0.7675 | 0.7518 | 0.8725 | 763.0 |
| `train-development-500-paw-standard-typed-v8.summary.json` | `train-development-500.jsonl` | `paw-4b-qwen3-0.6b` | `70c52fb8c07d1e2b0f91` | 0 | 0.8653 | 0.8792 | 0.8722 | 0.7441 | 0.7634 | 0.7536 | 0.8683 | 763.9 |
| `train-development-500-paw-standard-typed-v9.summary.json` | `train-development-500.jsonl` | `paw-4b-qwen3-0.6b` | `0b5d25bf37b5b09025df` | 0 | 0.8692 | 0.8722 | 0.8707 | 0.7373 | 0.7467 | 0.7420 | 0.8561 | 753.1 |
| `train-development-500-paw-standard-v2-unwrapped.summary.json` | `train-development-500.jsonl` | `paw-4b-qwen3-0.6b` | `62ad5f23c25d28feb8d9` | 0 | 0.8748 | 0.8684 | 0.8716 | — | — | — | — | 495.7 |
| `train-development-500-paw-standard-v3-unwrapped-retry1.summary.json` | `train-development-500.jsonl` | `paw-4b-qwen3-0.6b` | `926a5dde263a01ee3aba` | 0 | 0.9018 | 0.8739 | 0.8876 | — | — | — | — | 640.4 |
| `train-development-500-paw-standard-v3-unwrapped.summary.json` | `train-development-500.jsonl` | `paw-4b-qwen3-0.6b` | `926a5dde263a01ee3aba` | 424 | 0.9278 | 0.1043 | 0.1875 | — | — | — | — | 90.6 |
| `train-development-500-paw-standard-v4.summary.json` | `train-development-500.jsonl` | `paw-4b-qwen3-0.6b` | `3f49aef230cd5137c018` | 0 | 0.8680 | 0.8537 | 0.8608 | — | — | — | — | 531.9 |
| `train-development-500-paw-standard-v5.summary.json` | `train-development-500.jsonl` | `paw-4b-qwen3-0.6b` | `1246ff68791dd575c6fb` | 0 | 0.8758 | 0.8966 | 0.8861 | — | — | — | — | 522.4 |
| `train-development-500-paw-standard-v6.summary.json` | `train-development-500.jsonl` | `paw-4b-qwen3-0.6b` | `efec3da668a9219b5672` | 0 | 0.8989 | 0.8360 | 0.8663 | — | — | — | — | 488.4 |
| `train-development-500-paw-standard-v8.summary.json` | `train-development-500.jsonl` | `paw-4b-qwen3-0.6b` | `b098f2474256dc8387c4` | 0 | 0.8906 | 0.8696 | 0.8800 | — | — | — | — | 515.7 |
| `train-development-paw-standard-typed-v4-88108e7c.summary.json` | `train-development.jsonl` | `paw-4b-qwen3-0.6b` | `88108e7c09b0d0647261` | 0 | 0.8187 | 0.8827 | 0.8495 | 0.6519 | 0.7078 | 0.6787 | 0.8018 | 166.6 |
| `train-development-paw-standard-typed-v4.summary.json` | `train-development.jsonl` | `paw-4b-qwen3-0.6b` | `32b6d8ac7ca47b763267` | 0 | 0.8690 | 0.8875 | 0.8781 | 0.6257 | 0.6457 | 0.6355 | 0.7276 | 194.0 |
| `train-development-paw-standard-v1-unwrapped.summary.json` | `train-development.jsonl` | `paw-4b-qwen3-0.6b` | `f09d9e8f81946b54b9c3` | 0 | 0.8236 | 0.7924 | 0.8077 | — | — | — | — | 98.3 |
| `train-development-paw-standard-v2-unwrapped.summary.json` | `train-development.jsonl` | `paw-4b-qwen3-0.6b` | `62ad5f23c25d28feb8d9` | 0 | 0.8765 | 0.8725 | 0.8745 | — | — | — | — | 144.2 |
| `train-development-paw-standard-v2.summary.json` | `train-development.jsonl` | `paw-4b-qwen3-0.6b` | `1c5eec7b1781d76ce816` | 0 | 0.8735 | 0.8738 | 0.8737 | — | — | — | — | 98.4 |
| `train-development-paw-standard-v3-typed-v2-ctx24.summary.json` | `train-development.jsonl` | `paw-4b-qwen3-0.6b` | `a2451b2cf887000e94a4` | 0 | 0.9179 | 0.8932 | 0.9054 | 0.7317 | 0.7122 | 0.7218 | 0.7973 | 31.8 |
| `train-development-paw-standard-v3-typed-v2.summary.json` | `train-development.jsonl` | `paw-4b-qwen3-0.6b` | `a2451b2cf887000e94a4` | 0 | 0.9179 | 0.8932 | 0.9054 | 0.5217 | 0.5083 | 0.5149 | 0.5690 | 48.8 |
| `train-development-paw-standard-v3-unwrapped-typed-v2-unwrapped.summary.json` | `train-development.jsonl` | `paw-4b-qwen3-0.6b` | `14451a1c1a7ac3720f79` | 0 | 0.9014 | 0.9128 | 0.9071 | 0.7383 | 0.7481 | 0.7432 | 0.8195 | 238.4 |
| `train-development-paw-standard-v3-unwrapped.summary.json` | `train-development.jsonl` | `paw-4b-qwen3-0.6b` | `926a5dde263a01ee3aba` | 0 | 0.9014 | 0.9128 | 0.9071 | — | — | — | — | 123.9 |
| `train-development-paw-standard-v3.summary.json` | `train-development.jsonl` | `paw-4b-qwen3-0.6b` | `d71e2fb30e99b0edd992` | 0 | 0.9179 | 0.8932 | 0.9054 | — | — | — | — | 145.4 |
| `train-development-paw.summary.json` | `train-development.jsonl` | `paw-4b-qwen3-0.6b` | `04f8a0b669efa431b4b0` | 0 | 0.8333 | 0.7170 | 0.7708 | — | — | — | — | 109.4 |

## Exact current specifications

<details>
<summary><code>specs/pii-detector-ft-v1.txt</code> — SHA-256 <code>3acfa184dd9cb26d10b55e6a0f3918c29f90518f8dca9da0b2a5bb163b01bdd3</code></summary>

```text
Extract every AI4Privacy-style PII value from the input. Return ONLY a valid compact JSON array of exact substrings copied from the input, or [] when there is no PII. Return one array item per annotated field. Never combine adjacent fields, include a field name or separator, translate text, normalize formatting, repair punctuation, or invent text.

The PII field types are birth date, date, time, building number, street, city, state/province, postcode, country, apartment/secondary address, geographic coordinates, given name, surname, full personal name, personal title, sex/gender, username, email, telephone/fax, IP address, ID card, passport, driver's license, social number, password/PIN/passcode/secret/token, bank/card/account ID, and card issuer.

Follow the annotated field or repeating record schema rather than treating every realistic-looking value as PII. PII labels may be English, Dutch, French, German, Italian, or Spanish and may appear in prose, JSON, XML, HTML, Markdown, YAML, forms, tables, messages, fragments, or dense delimiter-separated records. Extract short ordinary-looking values such as M, F, H, GB, NL, ENG, 13, 163, Dr, Ms, or a three-letter identifier when their field identifies a listed PII type.

Rules:
- Scan through the final character and return every PII value. In repeated records, infer the columns from the header or a complete record and apply exactly those PII columns to every later record.
- In CSV or tables, do not return the row number from a generic ID or index column. An ID is PII only when its field means ID card, passport, driver's license, social number, bank/card/account/customer/order identifier, or another personal account identifier.
- Never return values from comment, note, agreement, waiver, admission status, description, usage, monitoring, security, restriction, perspective, grammatical person, project, course, program, activity, or ordinary location fields unless the value itself occupies an explicitly listed PII field.
- Generic role words such as candidate, participant, student, member, user, client, customer, support, instructor, and trainee are not part of a personal name. If a personal name follows such a role, return only the name.
- Separators such as ..., ampersand, comma, pipe, colon, semicolon, newline, and visible backslash+n can divide fields. Split neighboring fields and preserve every character inside each value.
- Extract a date or time when it fills a DATE, TIME, BOD, birth-date, appointment, deadline, signature-date, or equivalent personal field. Do not extract an administrative period merely because its key contains Start Date or End Date.
- Usernames may be random letters/digits, dotted names, initials, bracketed values, or identifiers before a colon in a participant or message list. Do not return the surrounding brackets.
- Bracketed personal values are PII, except generic underscore placeholders such as [CURRENT_DATE], [UNIVERSITY_NAME], [YOUR_NAME], and [FIELD_OF_STUDY].
- Split every annotated address component. A repeating unlabeled address row may use telephone, country, building, street, city, state, postcode, secondary address, and surname as separate columns.
- When a name is followed by an ID in parentheses, separate them. Return the name only if it is an annotated personal-name field; return the parenthesized ID when it is a listed personal identifier.
- A complete value at the start or end of a chunk is valid. Ignore only a visibly severed fragment that cannot be identified.

Input: ID,SOCIALNUMBER,TEL,COMMENTS\n1,777 064 4987,007.200-193-8263,"Plan and implement engaging course content."\n2,710.076.3818,099 3802-9499,"Integrate multimedia into the course."
Output: ["777 064 4987","007.200-193-8263","710.076.3818","099 3802-9499"]

Input: ID,TITLE,IDCARD,DRIVERLICENSE,AGREEMENT\n1,"Baron","CUL","KQ84LLYHL6","Property damage liability waiver is granted."\n2,"Prinses","98118263685763","077780822","Final waiver documented and signed off."
Output: ["Baron","CUL","KQ84LLYHL6","Prinses","98118263685763","077780822"]

Input: {"Schedule_A":{"Time":"20:19","Usage":"Available for basketball training","Monitoring":"Supervised by coaches","Security":"Key provided to club personnel"},"Schedule_B":{"Time":"6:01","Restrictions":"No outdoor shoes"}}
Output: ["20:19","6:01"]

Input: nolwen.pedetti2003 participó desde una perspectiva Formal en Tercera Persona Singular. H ofreció su opinión desde la Tercera Persona Singular, Set II. gejpgb21 se unió a la conversación.
Output: ["nolwen.pedetti2003","H","gejpgb21"]

Input: **Candidat Étienne**\n- Autre\n- Huissier\n- mathe.vuketic1998\n- Z0603982423869\n- +33 63.728-6394
Output: ["Étienne","Autre","Huissier","mathe.vuketic1998","Z0603982423869","+33 63.728-6394"]

Input: {"name":"Lucas Fischer","sex":"W","driver_license":"Y3.11.WIV90R7.3","password":"4%/a+(2$UIn"},{"name":"Max Mustermann","sex":"Männlich","driver_license":"Z4-24-K1BQN0Z-1","password":"Lu5\\end"}
Output: ["Lucas Fischer","W","Y3.11.WIV90R7.3","4%/a+(2$UIn","Max Mustermann","Männlich","Z4-24-K1BQN0Z-1","Lu5\\end"]

Input: tfjasta87868@gmail.com...2 57 01 85136 028 30...B@tutanota.com...2.49.03.19524.337.91...16zedije.pushparajan@protonmail.com...281026534565850...278-32-5098...[46.63, -0.7]
Output: ["tfjasta87868@gmail.com","2 57 01 85136 028 30","B@tutanota.com","2.49.03.19524.337.91","16zedije.pushparajan@protonmail.com","281026534565850","278-32-5098","[46.63, -0.7]"]

Input: Strategic_Plan: Piano Strategico per l'Attrazione degli Studenti. Activity_Name: Virtual Reality Integration in Educational Curriculum. Policy: Property damage liability waiver is granted. Participants: Tercera Persona Singular, Set I.
Output: []
```

</details>

<details>
<summary><code>specs/pii-detector-ft-v2.txt</code> — SHA-256 <code>0d186ae98b7614b602ba33a9ab3091f5f710d3bf599a13231a477d20eaa73acb</code></summary>

```text
Extract every AI4Privacy-style PII value from the input. Return ONLY a valid compact JSON array of exact substrings copied from the input, or [] when there is no PII. Return one array item per PII field. Never combine adjacent fields, include a field name or separator, translate text, normalize formatting, repair punctuation, invent text, or add explanation.

The PII field types are birth date, date, time, building number, street, city, state/province, postcode, country, apartment/secondary address, geographic coordinates, given name, surname, full personal name, personal title, sex/gender, username, email, telephone/fax, IP address, ID card, passport, driver's license, social number, password/PIN/passcode/secret/token, bank/card/account ID, and card issuer.

Follow the field or repeating record schema rather than a subjective sensitivity judgment. PII labels may be English, Dutch, French, German, Italian, or Spanish and may appear in prose, JSON, XML, HTML, Markdown, YAML, forms, tables, messages, fragments, or dense delimiter-separated records. Extract short ordinary-looking values such as M, F, H, GB, NL, ENG, 13, 163, Dr, Ms, or a three-letter identifier when their field or recurring column identifies a listed PII type.

Rules:
- Scan through the final character and return every PII value. In repeated records, infer the columns from the header or a complete record and apply those PII columns to every later record.
- In CSV or tables, do not return the row number from a generic ID or index column. An ID is PII when its field means ID card, passport, driver's license, social number, bank/card/account/customer/order identifier, or another personal account identifier.
- Never return values from comment, note, agreement, waiver, admission status, description, usage, monitoring, security, restriction, perspective, grammatical person, project, course, program, or activity fields. Do not return institutions, organizations, medical conditions, ordinary topics, or arbitrary prose.
- Generic role words such as candidate, participant, student, member, user, client, customer, support, instructor, and trainee are not part of a personal name. If a personal name follows such a role, return only the name.
- Separators such as ..., ampersand, comma, pipe, colon, semicolon, newline, and visible backslash+n can divide fields. Split neighboring fields and preserve every character inside each value.
- Extract dates and times from date/time fields, schedules, appointments, deadlines, signatures, or phrases like "from the date ..." in any of the six languages. A bare number or number followed by h can be a time when it fills a recurring time column.
- Usernames may be random letters/digits, dotted names, initials, bracketed values, or identifiers before a colon in a participant or message list. Do not return surrounding brackets.
- Bracketed personal values are PII, except generic underscore placeholders such as [CURRENT_DATE], [UNIVERSITY_NAME], [YOUR_NAME], and [FIELD_OF_STUDY].
- Split every address component. A repeating unlabeled address row may use telephone, country, building, street, city, state, postcode, secondary address, and surname as separate columns.
- When a name is followed by an ID in parentheses, separate them. Return the name only if it is a personal-name field; return the parenthesized ID when it is a listed personal identifier.
- A complete value at the start or end of a chunk is valid. Ignore only a visibly severed fragment that cannot be identified.

Input: ID,SOCIALNUMBER,TEL,COMMENTS\n1,777 064 4987,007.200-193-8263,"Plan and implement engaging course content."\n2,710.076.3818,099 3802-9499,"Integrate multimedia into the course."
Output: ["777 064 4987","007.200-193-8263","710.076.3818","099 3802-9499"]

Input: ID,TITLE,IDCARD,DRIVERLICENSE,AGREEMENT\n1,"Baron","CUL","KQ84LLYHL6","Property damage liability waiver is granted."\n2,"Prinses","98118263685763","077780822","Final waiver documented and signed off."
Output: ["Baron","CUL","KQ84LLYHL6","Prinses","98118263685763","077780822"]

Input: {"Schedule_A":{"Time":"20:19","Usage":"Available for basketball training","Monitoring":"Supervised by coaches","Security":"Key provided to club personnel"},"Schedule_B":{"Time":"6:01","Restrictions":"No outdoor shoes"}}
Output: ["20:19","6:01"]

Input: nolwen.pedetti2003 participó desde una perspectiva Formal en Tercera Persona Singular. H ofreció su opinión desde la Tercera Persona Singular, Set II. gejpgb21 se unió a la conversación.
Output: ["nolwen.pedetti2003","H","gejpgb21"]

Input: Date: 2023-12-17T00:00:00\nHeure: 6:24\nBâtiment: 75\nParticipants: Perspective du Troisième Personne Pluriel Ensemble II
Output: ["2023-12-17T00:00:00","6:24","75"]

Input: País: US; Dirección: 927, Calle: Shaft Road, Ciudad: Wawarsing, Estado: NY, Código Postal: 12446; Nombre: Úrsula (00477097062)
Output: ["US","927","Shaft Road","Wawarsing","NY","12446","00477097062"]

Input: tfjasta87868@gmail.com...2 57 01 85136 028 30...B@tutanota.com...2.49.03.19524.337.91...16zedije.pushparajan@protonmail.com...281026534565850...278-32-5098...[46.63, -0.7]
Output: ["tfjasta87868@gmail.com","2 57 01 85136 028 30","B@tutanota.com","2.49.03.19524.337.91","16zedije.pushparajan@protonmail.com","281026534565850","278-32-5098","[46.63, -0.7]"]

Input: Date: [CURRENT_DATE]; Title: [Madame]; Born: [juin/47]; ID: [5716022019873]; School: [UNIVERSITY_NAME]
Output: ["Madame","juin/47","5716022019873"]

Input: Strategic_Plan: Piano Strategico per l'Attrazione degli Studenti. Activity_Name: Virtual Reality Integration in Educational Curriculum. Policy: Property damage liability waiver is granted. Participants: Tercera Persona Singular, Set I.
Output: []
```

</details>

<details>
<summary><code>specs/pii-detector-ft-v3.txt</code> — SHA-256 <code>15ff492c26a8fc3496a0d1a3a4a815e812cbb51cd7ff2e32e52a790a3a0ad8c1</code></summary>

```text
Extract every AI4Privacy-style PII value from the input. Return ONLY a valid compact JSON array of exact substrings copied from the input, or [] when there is no PII. Return each distinct extracted substring at most once; one item is sufficient when the same exact value occurs in several annotated fields. Never loop, repeat an array item, combine adjacent fields, include a field name or separator, translate text, normalize formatting, repair punctuation, invent text, or add explanation.

The PII field types are birth date, date, time, building number, street, city, state/province, postcode, country, apartment/secondary address, geographic coordinates, given name, surname, full personal name, personal title, sex/gender, username, email, telephone/fax, IP address, ID card, passport, driver's license, social number, password/PIN/passcode/secret/token, bank/card/account ID, and card issuer.

Follow the annotated field or repeating record schema rather than treating every realistic-looking value as PII. PII labels may be English, Dutch, French, German, Italian, or Spanish and may appear in prose, JSON, XML, HTML, Markdown, YAML, forms, tables, messages, fragments, or dense delimiter-separated records. Extract short ordinary-looking values such as M, F, H, GB, NL, ENG, 13, 163, Dr, Ms, or a three-letter identifier when their field identifies a listed PII type.

Rules:
- Scan through the final character and return every distinct PII value once. In repeated records, infer the columns from the header or a complete record and apply exactly those PII columns to every later record.
- In CSV or tables, do not return the row number from a generic ID or index column. An ID is PII only when its field means ID card, passport, driver's license, social number, bank/card/account/customer/order identifier, or another personal account identifier.
- Never return values from comment, note, agreement, waiver, admission status, description, usage, monitoring, security, restriction, perspective, grammatical person, project, course, program, activity, report metadata, or ordinary location fields unless the value itself occupies an explicitly listed personal PII field.
- Generic role words such as candidate, participant, student, member, user, client, customer, support, instructor, and trainee are not part of a personal name. If an annotated personal name follows such a role, return only the name.
- Separators such as ..., ampersand, comma, pipe, colon, semicolon, newline, and visible backslash+n can divide fields. Split neighboring fields and preserve every character inside each value. Never return Markdown table separator dashes or a missing-value marker such as -.
- Extract a date or time when it fills a DATE, TIME, BOD, birth-date, appointment, deadline, signature-date, or equivalent personal field. Do not extract an administrative period merely because its key contains Start Date or End Date.
- Usernames may be random letters/digits, dotted names, initials, bracketed values, or identifiers before a colon in a participant or message list. Do not return the surrounding brackets.
- Bracketed personal values are PII, except generic underscore placeholders such as [CURRENT_DATE], [UNIVERSITY_NAME], [YOUR_NAME], and [FIELD_OF_STUDY]. In a long bracketed list, return each distinct personal value once and continue scanning later fields.
- Split every annotated address component. A repeating unlabeled address row may use telephone, country, building, street, city, state, postcode, secondary address, and surname as separate columns.
- When a name is followed by an ID in parentheses, separate them. Return the name only if it is an annotated personal-name field; return the parenthesized ID when it is a listed personal identifier.
- A complete value at the start or end of a chunk is valid. Ignore only a visibly severed fragment that cannot be identified. After collecting the final field, close the JSON array immediately.

Input: ID,SOCIALNUMBER,TEL,COMMENTS\n1,777 064 4987,007.200-193-8263,"Plan and implement engaging course content."\n2,710.076.3818,099 3802-9499,"Integrate multimedia into the course."
Output: ["777 064 4987","007.200-193-8263","710.076.3818","099 3802-9499"]

Input: ID,TITLE,IDCARD,DRIVERLICENSE,AGREEMENT\n1,"Baron","CUL","KQ84LLYHL6","Property damage liability waiver is granted."\n2,"Prinses","98118263685763","077780822","Final waiver documented and signed off."
Output: ["Baron","CUL","KQ84LLYHL6","Prinses","98118263685763","077780822"]

Input: {"Schedule_A":{"Time":"20:19","Usage":"Available for basketball training","Monitoring":"Supervised by coaches","Security":"Key provided to club personnel"},"Schedule_B":{"Time":"6:01","Restrictions":"No outdoor shoes"}}
Output: ["20:19","6:01"]

Input: nolwen.pedetti2003 participó desde una perspectiva Formal en Tercera Persona Singular. H ofreció su opinión desde la Tercera Persona Singular, Set II. gejpgb21 se unió a la conversación.
Output: ["nolwen.pedetti2003","H","gejpgb21"]

Input: **Candidat Étienne**\n- Autre\n- Huissier\n- mathe.vuketic1998\n- Z0603982423869\n- +33 63.728-6394
Output: ["Étienne","Autre","Huissier","mathe.vuketic1998","Z0603982423869","+33 63.728-6394"]

Input: {"name":"Lucas Fischer","sex":"W","driver_license":"Y3.11.WIV90R7.3","password":"4%/a+(2$UIn"},{"name":"Max Mustermann","sex":"Männlich","driver_license":"Z4-24-K1BQN0Z-1","password":"Lu5\\end"}
Output: ["Lucas Fischer","W","Y3.11.WIV90R7.3","4%/a+(2$UIn","Max Mustermann","Männlich","Z4-24-K1BQN0Z-1","Lu5\\end"]

Input: En signant ce document, l'étudiant [Femme] accepte les modalités. De plus, [F], [H], [H], [Préfère ne pas divulguer], [Femme], [Non-binaire], et [F] seront tenus responsables. La signature a été validée à [03:10]. Fait à [France], le [décembre/89]. [F0.FRA.36PP7050.0.990329.MATHUSA], [99HS57424], [kanber19]
Output: ["Femme","F","H","Préfère ne pas divulguer","Non-binaire","03:10","France","décembre/89","F0.FRA.36PP7050.0.990329.MATHUSA","99HS57424","kanber19"]

Input: Energy assessments such as qxafnhrnawspkykb83 and Haftner, lauralie.canossi and Canossi, 07jungmichel and Jungmichel, MI1990 and Muscas, lppeobjfn3359 and Maistrello Palankon, dávila and Dávila, boves2003 and Boves, provide insights. The assessments are scheduled in Didcot on 2019-09-29T00:00:00, starting at half past 16.
Output: ["qxafnhrnawspkykb83","Haftner","lauralie.canossi","Canossi","07jungmichel","Jungmichel","MI1990","Muscas","lppeobjfn3359","Maistrello","Palankon","dávila","Dávila","boves2003","Boves","Didcot","2019-09-29T00:00:00","half past 16"]

Input: Date: 2023-12-17T00:00:00\nHeure: 6:24\nBâtiment: 75\nParticipants: Membres de la Perspective du Troisième Personne Pluriel Ensemble II; Membres de la Perspective du Deuxième Personne Pluriel Formelle
Output: ["2023-12-17T00:00:00","6:24","75"]

Input: tfjasta87868@gmail.com...2 57 01 85136 028 30...B@tutanota.com...2.49.03.19524.337.91...16zedije.pushparajan@protonmail.com...281026534565850...278-32-5098...[46.63, -0.7]
Output: ["tfjasta87868@gmail.com","2 57 01 85136 028 30","B@tutanota.com","2.49.03.19524.337.91","16zedije.pushparajan@protonmail.com","281026534565850","278-32-5098","[46.63, -0.7]"]

Input: Strategic_Plan: Piano Strategico per l'Attrazione degli Studenti. Activity_Name: Virtual Reality Integration in Educational Curriculum. Policy: Property damage liability waiver is granted. Participants: Tercera Persona Singular, Set I.
Output: []
```

</details>

<details>
<summary><code>specs/pii-detector-ft-v4.txt</code> — SHA-256 <code>708f29fc8f9a68a3f3c0123ec03bb65fcfb2b8405592c4377f2afaa2a69090bf</code></summary>

```text
Extract every AI4Privacy-style PII value from the input. Return ONLY a valid compact JSON array of exact substrings copied from the input, or [] when there is no PII. Return one array item per annotated field occurrence. If an identical value occurs in multiple PII fields, return it once for each occurrence; never return a value more times than it occurs as PII in the input. Never loop, repeat an output cycle, combine adjacent fields, include a field name or separator, translate text, normalize formatting, repair punctuation, invent text, or add explanation.

The PII field types are birth date, date, time, building number, street, city, state/province, postcode, country, apartment/secondary address, geographic coordinates, given name, surname, full personal name, personal title, sex/gender, username, email, telephone/fax, IP address, ID card, passport, driver's license, social number, password/PIN/passcode/secret/token, bank/card/account ID, and card issuer.

Follow the annotated field or repeating record schema rather than treating every realistic-looking value as PII. PII labels may be English, Dutch, French, German, Italian, or Spanish and may appear in prose, JSON, XML, HTML, Markdown, YAML, forms, tables, messages, fragments, or dense delimiter-separated records. Extract short ordinary-looking values such as M, F, H, GB, NL, ENG, 13, 163, Dr, Ms, or a three-letter identifier when their field identifies a listed PII type.

Rules:
- Scan through the final character and return every PII occurrence. In repeated records, infer the columns from the header or a complete record and apply exactly those PII columns to every later record.
- In CSV or tables, do not return the row number from a generic ID or index column. An ID is PII only when its field means ID card, passport, driver's license, social number, bank/card/account/customer/order identifier, or another personal account identifier.
- Never return values from comment, note, agreement, waiver, admission status, description, usage, monitoring, security, restriction, perspective, grammatical person, project, course, program, activity, report metadata, or ordinary location fields unless the value itself occupies an explicitly listed PII field.
- Generic role words such as candidate, participant, student, member, user, client, customer, support, instructor, and trainee are not part of a personal name. If a personal name follows such a role, return only the name.
- Separators such as ..., ampersand, comma, pipe, colon, semicolon, newline, visible backslash+n, HTML tags, and list markers can divide fields. Split neighboring fields and preserve every character inside each value. Never return Markdown separator dashes or a missing-value marker such as -.
- Extract a date or time when it fills a DATE, TIME, BOD, birth-date, appointment, deadline, signature-date, or equivalent personal field. Do not extract an administrative period merely because its key contains Start Date or End Date.
- Usernames may be random letters/digits, dotted names, initials, bracketed values, or identifiers before a colon in a participant or message list. Do not return surrounding brackets.
- Bracketed personal values are PII, except generic underscore placeholders such as [CURRENT_DATE], [UNIVERSITY_NAME], [YOUR_NAME], and [FIELD_OF_STUDY].
- Split every annotated address component. A repeating unlabeled address row may use telephone, country, building, street, city, state, postcode, secondary address, and surname as separate columns.
- When a name is followed by an ID in parentheses, separate them. Return the name only if it is an annotated personal-name field; return the parenthesized ID when it is a listed personal identifier.
- After collecting the final field, close the JSON array immediately. A complete value at a chunk boundary is valid; ignore only a visibly severed fragment that cannot be identified.

Input: ID,SOCIALNUMBER,TEL,COMMENTS\n1,777 064 4987,007.200-193-8263,"Plan and implement engaging course content."\n2,710.076.3818,099 3802-9499,"Integrate multimedia into the course."
Output: ["777 064 4987","007.200-193-8263","710.076.3818","099 3802-9499"]

Input: ID,TITLE,IDCARD,DRIVERLICENSE,AGREEMENT\n1,"Baron","CUL","KQ84LLYHL6","Property damage liability waiver is granted."\n2,"Prinses","98118263685763","077780822","Final waiver documented and signed off."
Output: ["Baron","CUL","KQ84LLYHL6","Prinses","98118263685763","077780822"]

Input: nolwen.pedetti2003 participó desde una perspectiva Formal en Tercera Persona Singular. H ofreció su opinión desde la Tercera Persona Singular, Set II. gejpgb21 se unió a la conversación.
Output: ["nolwen.pedetti2003","H","gejpgb21"]

Input: **Candidat Étienne**\n- Autre\n- Huissier\n- mathe.vuketic1998\n- Z0603982423869\n- +33 63.728-6394
Output: ["Étienne","Autre","Huissier","mathe.vuketic1998","Z0603982423869","+33 63.728-6394"]

Input: {"name":"Lucas Fischer","sex":"W","driver_license":"Y3.11.WIV90R7.3","password":"4%/a+(2$UIn"},{"name":"Max Mustermann","sex":"Männlich","driver_license":"Z4-24-K1BQN0Z-1","password":"Lu5\\end"}
Output: ["Lucas Fischer","W","Y3.11.WIV90R7.3","4%/a+(2$UIn","Max Mustermann","Männlich","Z4-24-K1BQN0Z-1","Lu5\\end"]

Input: En signant ce document, l'étudiant [Femme] accepte les modalités. De plus, [F], [H], [H], [Préfère ne pas divulguer], [Femme], [Non-binaire], et [F] seront tenus responsables. La signature a été validée à [03:10]. Fait à [France], le [décembre/89]. [F0.FRA.36PP7050.0.990329.MATHUSA], [99HS57424], [kanber19]
Output: ["Femme","F","H","H","Préfère ne pas divulguer","Femme","Non-binaire","F","03:10","France","décembre/89","F0.FRA.36PP7050.0.990329.MATHUSA","99HS57424","kanber19"]

Input: Energy assessments such as qxafnhrnawspkykb83 and Haftner, lauralie.canossi and Canossi, 07jungmichel and Jungmichel, MI1990 and Muscas, lppeobjfn3359 and Maistrello Palankon, dávila and Dávila, boves2003 and Boves, provide insights. The assessments are scheduled in Didcot on 2019-09-29T00:00:00, starting at half past 16.
Output: ["qxafnhrnawspkykb83","Haftner","lauralie.canossi","Canossi","07jungmichel","Jungmichel","MI1990","Muscas","lppeobjfn3359","Maistrello","Palankon","dávila","Dávila","boves2003","Boves","Didcot","2019-09-29T00:00:00","half past 16"]

Input: - id(1) - 084.910-0987, Nederland, 770, Tiendweg, Lopik, UT, 3411, Kamenova\n- id(2) - +26.82 907.1047, NL, 414, Bruininxdeelse Kade, Leerdam, ZH, 4143 LM, Section 740, Krane
Output: ["084.910-0987","Nederland","770","Tiendweg","Lopik","UT","3411","Kamenova","+26.82 907.1047","NL","414","Bruininxdeelse Kade","Leerdam","ZH","4143 LM","Section 740","Krane"]

Input: | ID | DATA | USERNAME | SOCIALNUMBER | COUNTRY | BUILDING | STREET | CITY | STATE | POSTCODE | SECADDRESS |\n|----|------|----------|-------------|---------|----------|-------|------|-------|---------|------------|\n| 1 | "giugno/64" | "baenziger" | "Sti-Bae-26-I-52-2-LFB" | "IT" | "167" | "Via San Donato-San Giorgio" | "Taranto" | "75" | "74122" | "Loft 253" |\n| 2 | "agosto/90" | "5622NFSAF" | "NanSpe22N146KCY" | "IT" | "512" | "Strada Provinciale 41 della Rassinata" | "Arezzo" | "52" | "52100" | - |
Output: ["giugno/64","baenziger","Sti-Bae-26-I-52-2-LFB","IT","167","Via San Donato-San Giorgio","Taranto","75","74122","Loft 253","agosto/90","5622NFSAF","NanSpe22N146KCY","IT","512","Strada Provinciale 41 della Rassinata","Arezzo","52","52100"]

Input: Date: 2023-12-17T00:00:00\nHeure: 6:24\nBâtiment: 75\nParticipants: Membres de la Perspective du Troisième Personne Pluriel Ensemble II; Membres de la Perspective du Deuxième Personne Pluriel Formelle
Output: ["2023-12-17T00:00:00","6:24","75"]

Input: Strategic_Plan: Piano Strategico per l'Attrazione degli Studenti. Activity_Name: Virtual Reality Integration in Educational Curriculum. Policy: Property damage liability waiver is granted. Participants: Tercera Persona Singular, Set I.
Output: []
```

</details>

<details>
<summary><code>specs/pii-detector-typed-compact-restraint-v2.txt</code> — SHA-256 <code>695cfb888890147c3548f2247c9db009e6e529695f3125098e114c060d5c67ed</code></summary>

```text
Extract every AI4Privacy-style PII field from the input. Return ONLY a compact JSON array of [text,type] pairs, or [] when there is no PII. Copy text exactly from the input. Use only these types: private_person, private_email, private_phone, private_address, private_url, private_date, account_number, secret, other_pii.

Types:
- private_person: personal name, surname, title, or username.
- private_email: email address.
- private_phone: telephone or fax number.
- private_address: building, street, city, state or province, postcode, country, secondary address, or coordinates.
- private_url: personal URL or IPv4 or IPv6 address.
- private_date: birth date, annotated personal date, or time.
- account_number: ID card, passport, driver's license, social number, or personal bank, card, customer, order, or account identifier.
- secret: password, PIN, passcode, API key, authentication token, or secret.
- other_pii: sex or gender value, or PII not covered above.

Policy:
- Prefer a field label, table header, or record schema over visual shape.
- Use private_person only for a field marked name, title, or username, or when context clearly introduces a person. Capitalization, quotation, or an alphanumeric shape alone does not make text a person.
- An email is always private_email, an IP address is private_url, a telephone field is private_phone, and an ID, passport, license, social, bank, card, customer, order, or account field is account_number, regardless of visual shape.
- A password, PIN, passcode, key, or token field is secret, including a masked password. Security products, controls, policies, permissions, and access modes are not secrets.
- In an unlabeled repeating sequence, infer the field cycle from the nearest header or complete record and apply it through the final complete field.
- Outside a PII field or schema, extract only a self-identifying email, IP, phone, credential, or clear personal name. Ignore generic prose, roles, row indices, projects, activities, comments, statuses, placeholders, organizations, and ordinary locations.
- Copy only the value, never its field label, role prefix, separator, surrounding prose, or brackets unless brackets are part of coordinates. Split adjacent fields instead of combining them.
- Preserve spelling, punctuation, whitespace, accents, and capitalization. Never translate, normalize, repair, truncate, or invent a value.
- Short values are valid when their field identifies them, including initials, titles, usernames, sex values, country or state codes, building numbers, and short times.
- Scan the complete input and return each distinct [text,type] pair once in first-occurrence order. Do not repeat an output cycle.

Input: Name: Ada Lovelace; Email: ada@example.com; PIN: 4821; Note: Call after lunch.
Output: [["Ada Lovelace","private_person"],["ada@example.com","private_email"],["4821","secret"]]

Input: EMAIL,SOCIALNUMBER,IP,TEL\nK@x.co,1-72-09-38517-757-27,67.176.53.168,099 3802-9499
Output: [["K@x.co","private_email"],["1-72-09-38517-757-27","account_number"],["67.176.53.168","private_url"],["099 3802-9499","private_phone"]]

Input: SEX&BOD&USERNAME&COUNTRY&BUILDING&STREET&CITY&STATE&POSTCODE&TIME\nFemme&18 mars 1941&lina.rossi&FR&17&Rue des Fleurs&Lyon&ARA&69003&8:17
Output: [["Femme","other_pii"],["18 mars 1941","private_date"],["lina.rossi","private_person"],["FR","private_address"],["17","private_address"],["Rue des Fleurs","private_address"],["Lyon","private_address"],["ARA","private_address"],["69003","private_address"],["8:17","private_date"]]

Input: Username: moon47; Password: ********; Role: Administrator; Access: Read/Write; Security: Firewall, Malware Scan; Status: Active.
Output: [["moon47","private_person"],["********","secret"]]

Input: Project: Allergy education; Activity: Monitor allergies; Role: Instructor; Access: Limited; Security: Endpoint protection; Status: Active.
Output: []
```

</details>

<details>
<summary><code>specs/pii-detector-typed-compact-three-objects-v1.txt</code> — SHA-256 <code>b370dd6243ddba0aba4cf50bba180a70731f058eccf7c5ee15923cbb97769254</code></summary>

```text
Extract every AI4Privacy-style PII field from the input. Return ONLY a compact JSON array of objects, or [] when there is no PII. Every object must be {"text":"exact copied text","type":"one allowed type"}. Use only these types: private_person, private_email, private_phone, private_address, private_url, private_date, account_number, secret, other_pii.

Types:
- private_person: personal name, surname, title, or username.
- private_email: email address.
- private_phone: telephone or fax number.
- private_address: building, street, city, state or province, postcode, country, secondary address, or coordinates.
- private_url: personal URL or IPv4 or IPv6 address.
- private_date: birth date, annotated personal date, or time.
- account_number: ID card, passport, driver's license, social number, or personal bank, card, customer, order, or account identifier.
- secret: password, PIN, passcode, API key, authentication token, or secret.
- other_pii: sex or gender value, or PII not covered above.

Policy:
- Prefer an explicit field label, table header, or repeating record schema over the visual shape of a value. A social number remains account_number when it resembles a phone or IP address.
- In an unlabeled repeating sequence, infer the field cycle from the nearest header or complete record and apply that cycle through the final complete field.
- Outside a PII field or record schema, extract only self-identifying values such as an email address, IP address, phone number, credential, or clearly personal name. Do not extract generic prose, roles, row indices, project names, activities, comments, statuses, or placeholders.
- Copy only the value, never its field label, role prefix, separator, surrounding prose, or brackets unless brackets are part of coordinates. Split adjacent fields instead of combining them.
- Preserve spelling, punctuation, whitespace, accents, and capitalization. Never translate, normalize, repair, truncate, or invent a value.
- Short values are valid when their field identifies them, including initials, titles, usernames, sex values, country or state codes, building numbers, and short times.
- Scan the complete input and return each distinct object once in first-occurrence order. Do not repeat an output cycle.

Input: Name: Ada Lovelace; Email: ada@example.com; PIN: 4821; Note: Call after lunch.
Output: [{"text":"Ada Lovelace","type":"private_person"},{"text":"ada@example.com","type":"private_email"},{"text":"4821","type":"secret"}]

Input: EMAIL,SOCIALNUMBER,IP,TEL\nK@x.co,1-72-09-38517-757-27,67.176.53.168,099 3802-9499
Output: [{"text":"K@x.co","type":"private_email"},{"text":"1-72-09-38517-757-27","type":"account_number"},{"text":"67.176.53.168","type":"private_url"},{"text":"099 3802-9499","type":"private_phone"}]

Input: SEX&BOD&USERNAME&COUNTRY&BUILDING&STREET&CITY&STATE&POSTCODE&TIME\nFemme&18 mars 1941&lina.rossi&FR&17&Rue des Fleurs&Lyon&ARA&69003&8:17
Output: [{"text":"Femme","type":"other_pii"},{"text":"18 mars 1941","type":"private_date"},{"text":"lina.rossi","type":"private_person"},{"text":"FR","type":"private_address"},{"text":"17","type":"private_address"},{"text":"Rue des Fleurs","type":"private_address"},{"text":"Lyon","type":"private_address"},{"text":"ARA","type":"private_address"},{"text":"69003","type":"private_address"},{"text":"8:17","type":"private_date"}]
```

</details>

<details>
<summary><code>specs/pii-detector-typed-compact-three-text-type-v1.txt</code> — SHA-256 <code>c5cf3e9ca32c8cf7b8fac3598b2d34084547b858b18e4c09a272ab82bd378fba</code></summary>

```text
Extract every AI4Privacy-style PII field from the input. Return ONLY a compact JSON array of [text,type] pairs, or [] when there is no PII. Copy text exactly from the input. Use only these types: private_person, private_email, private_phone, private_address, private_url, private_date, account_number, secret, other_pii.

Types:
- private_person: personal name, surname, title, or username.
- private_email: email address.
- private_phone: telephone or fax number.
- private_address: building, street, city, state or province, postcode, country, secondary address, or coordinates.
- private_url: personal URL or IPv4 or IPv6 address.
- private_date: birth date, annotated personal date, or time.
- account_number: ID card, passport, driver's license, social number, or personal bank, card, customer, order, or account identifier.
- secret: password, PIN, passcode, API key, authentication token, or secret.
- other_pii: sex or gender value, or PII not covered above.

Policy:
- Prefer an explicit field label, table header, or repeating record schema over the visual shape of a value. A social number remains account_number when it resembles a phone or IP address.
- In an unlabeled repeating sequence, infer the field cycle from the nearest header or complete record and apply that cycle through the final complete field.
- Outside a PII field or record schema, extract only self-identifying values such as an email address, IP address, phone number, credential, or clearly personal name. Do not extract generic prose, roles, row indices, project names, activities, comments, statuses, or placeholders.
- Copy only the value, never its field label, role prefix, separator, surrounding prose, or brackets unless brackets are part of coordinates. Split adjacent fields instead of combining them.
- Preserve spelling, punctuation, whitespace, accents, and capitalization. Never translate, normalize, repair, truncate, or invent a value.
- Short values are valid when their field identifies them, including initials, titles, usernames, sex values, country or state codes, building numbers, and short times.
- Scan the complete input and return each distinct [text,type] pair once in first-occurrence order. Do not repeat an output cycle.

Input: Name: Ada Lovelace; Email: ada@example.com; PIN: 4821; Note: Call after lunch.
Output: [["Ada Lovelace","private_person"],["ada@example.com","private_email"],["4821","secret"]]

Input: EMAIL,SOCIALNUMBER,IP,TEL\nK@x.co,1-72-09-38517-757-27,67.176.53.168,099 3802-9499
Output: [["K@x.co","private_email"],["1-72-09-38517-757-27","account_number"],["67.176.53.168","private_url"],["099 3802-9499","private_phone"]]

Input: SEX&BOD&USERNAME&COUNTRY&BUILDING&STREET&CITY&STATE&POSTCODE&TIME\nFemme&18 mars 1941&lina.rossi&FR&17&Rue des Fleurs&Lyon&ARA&69003&8:17
Output: [["Femme","other_pii"],["18 mars 1941","private_date"],["lina.rossi","private_person"],["FR","private_address"],["17","private_address"],["Rue des Fleurs","private_address"],["Lyon","private_address"],["ARA","private_address"],["69003","private_address"],["8:17","private_date"]]
```

</details>

<details>
<summary><code>specs/pii-detector-typed-compact-three-tsv-v1.txt</code> — SHA-256 <code>c77a491e416303082ef15949e42e266467445fc29a3d7d81f61816bfa795616e</code></summary>

```text
Extract every AI4Privacy-style PII field from the input. Return ONLY one result per line as type, one literal tab, then text. Return NONE when there is no PII. Copy text exactly from the input. Use only these types: private_person, private_email, private_phone, private_address, private_url, private_date, account_number, secret, other_pii.

Types:
- private_person: personal name, surname, title, or username.
- private_email: email address.
- private_phone: telephone or fax number.
- private_address: building, street, city, state or province, postcode, country, secondary address, or coordinates.
- private_url: personal URL or IPv4 or IPv6 address.
- private_date: birth date, annotated personal date, or time.
- account_number: ID card, passport, driver's license, social number, or personal bank, card, customer, order, or account identifier.
- secret: password, PIN, passcode, API key, authentication token, or secret.
- other_pii: sex or gender value, or PII not covered above.

Policy:
- Prefer an explicit field label, table header, or repeating record schema over the visual shape of a value. A social number remains account_number when it resembles a phone or IP address.
- In an unlabeled repeating sequence, infer the field cycle from the nearest header or complete record and apply that cycle through the final complete field.
- Outside a PII field or record schema, extract only self-identifying values such as an email address, IP address, phone number, credential, or clearly personal name. Do not extract generic prose, roles, row indices, project names, activities, comments, statuses, or placeholders.
- Copy only the value, never its field label, role prefix, separator, surrounding prose, or brackets unless brackets are part of coordinates. Split adjacent fields instead of combining them.
- Preserve spelling, punctuation, whitespace, accents, and capitalization. Never translate, normalize, repair, truncate, or invent a value.
- Short values are valid when their field identifies them, including initials, titles, usernames, sex values, country or state codes, building numbers, and short times.
- Scan the complete input and return each distinct type-tab-text row once in first-occurrence order. Do not repeat an output cycle.

Input: Name: Ada Lovelace; Email: ada@example.com; PIN: 4821; Note: Call after lunch.
Output:
private_person	Ada Lovelace
private_email	ada@example.com
secret	4821

Input: EMAIL,SOCIALNUMBER,IP,TEL\nK@x.co,1-72-09-38517-757-27,67.176.53.168,099 3802-9499
Output:
private_email	K@x.co
account_number	1-72-09-38517-757-27
private_url	67.176.53.168
private_phone	099 3802-9499

Input: SEX&BOD&USERNAME&COUNTRY&BUILDING&STREET&CITY&STATE&POSTCODE&TIME\nFemme&18 mars 1941&lina.rossi&FR&17&Rue des Fleurs&Lyon&ARA&69003&8:17
Output:
other_pii	Femme
private_date	18 mars 1941
private_person	lina.rossi
private_address	FR
private_address	17
private_address	Rue des Fleurs
private_address	Lyon
private_address	ARA
private_address	69003
private_date	8:17
```

</details>

<details>
<summary><code>specs/pii-detector-typed-compact-three-type-text-v1.txt</code> — SHA-256 <code>816e4a25e22670fdbf95136678f67fa1309994e9b80d0f38f5d30d2e8010e2c7</code></summary>

```text
Extract every AI4Privacy-style PII field from the input. Return ONLY a compact JSON array of [type,text] pairs, or [] when there is no PII. Copy text exactly from the input. Use only these types: private_person, private_email, private_phone, private_address, private_url, private_date, account_number, secret, other_pii.

Types:
- private_person: personal name, surname, title, or username.
- private_email: email address.
- private_phone: telephone or fax number.
- private_address: building, street, city, state or province, postcode, country, secondary address, or coordinates.
- private_url: personal URL or IPv4 or IPv6 address.
- private_date: birth date, annotated personal date, or time.
- account_number: ID card, passport, driver's license, social number, or personal bank, card, customer, order, or account identifier.
- secret: password, PIN, passcode, API key, authentication token, or secret.
- other_pii: sex or gender value, or PII not covered above.

Policy:
- Prefer an explicit field label, table header, or repeating record schema over the visual shape of a value. A social number remains account_number when it resembles a phone or IP address.
- In an unlabeled repeating sequence, infer the field cycle from the nearest header or complete record and apply that cycle through the final complete field.
- Outside a PII field or record schema, extract only self-identifying values such as an email address, IP address, phone number, credential, or clearly personal name. Do not extract generic prose, roles, row indices, project names, activities, comments, statuses, or placeholders.
- Copy only the value, never its field label, role prefix, separator, surrounding prose, or brackets unless brackets are part of coordinates. Split adjacent fields instead of combining them.
- Preserve spelling, punctuation, whitespace, accents, and capitalization. Never translate, normalize, repair, truncate, or invent a value.
- Short values are valid when their field identifies them, including initials, titles, usernames, sex values, country or state codes, building numbers, and short times.
- Scan the complete input and return each distinct [type,text] pair once in first-occurrence order. Do not repeat an output cycle.

Input: Name: Ada Lovelace; Email: ada@example.com; PIN: 4821; Note: Call after lunch.
Output: [["private_person","Ada Lovelace"],["private_email","ada@example.com"],["secret","4821"]]

Input: EMAIL,SOCIALNUMBER,IP,TEL\nK@x.co,1-72-09-38517-757-27,67.176.53.168,099 3802-9499
Output: [["private_email","K@x.co"],["account_number","1-72-09-38517-757-27"],["private_url","67.176.53.168"],["private_phone","099 3802-9499"]]

Input: SEX&BOD&USERNAME&COUNTRY&BUILDING&STREET&CITY&STATE&POSTCODE&TIME\nFemme&18 mars 1941&lina.rossi&FR&17&Rue des Fleurs&Lyon&ARA&69003&8:17
Output: [["other_pii","Femme"],["private_date","18 mars 1941"],["private_person","lina.rossi"],["private_address","FR"],["private_address","17"],["private_address","Rue des Fleurs"],["private_address","Lyon"],["private_address","ARA"],["private_address","69003"],["private_date","8:17"]]
```

</details>

<details>
<summary><code>specs/pii-detector-typed-compact-zero-v1.txt</code> — SHA-256 <code>7fcaf93482a85c514e5786b303a7ad8f5d290e990e2f06f1f81e3ff93b66708d</code></summary>

```text
Extract every AI4Privacy-style PII field from the input. Return ONLY a compact JSON array of [text,type] pairs, or [] when there is no PII. Copy text exactly from the input. Use only these types: private_person, private_email, private_phone, private_address, private_url, private_date, account_number, secret, other_pii.

Types:
- private_person: personal name, surname, title, or username.
- private_email: email address.
- private_phone: telephone or fax number.
- private_address: building, street, city, state or province, postcode, country, secondary address, or coordinates.
- private_url: personal URL or IPv4 or IPv6 address.
- private_date: birth date, annotated personal date, or time.
- account_number: ID card, passport, driver's license, social number, or personal bank, card, customer, order, or account identifier.
- secret: password, PIN, passcode, API key, authentication token, or secret.
- other_pii: sex or gender value, or PII not covered above.

Policy:
- Prefer an explicit field label, table header, or repeating record schema over the visual shape of a value. A social number remains account_number when it resembles a phone or IP address.
- In an unlabeled repeating sequence, infer the field cycle from the nearest header or complete record and apply that cycle through the final complete field.
- Outside a PII field or record schema, extract only self-identifying values such as an email address, IP address, phone number, credential, or clearly personal name. Do not extract generic prose, roles, row indices, project names, activities, comments, statuses, or placeholders.
- Copy only the value, never its field label, role prefix, separator, surrounding prose, or brackets unless brackets are part of coordinates. Split adjacent fields instead of combining them.
- Preserve spelling, punctuation, whitespace, accents, and capitalization. Never translate, normalize, repair, truncate, or invent a value.
- Short values are valid when their field identifies them, including initials, titles, usernames, sex values, country or state codes, building numbers, and short times.
- Scan the complete input and return each distinct [text,type] pair once in first-occurrence order. Do not repeat an output cycle.
```

</details>

<details>
<summary><code>specs/pii-detector-typed-ft-v1.txt</code> — SHA-256 <code>376fae3801e2e23543ae11922fc70baf4e2906a8349658cdf681477fd3fd04e4</code></summary>

```text
Extract every AI4Privacy-style PII value from the input and assign its canonical nine-way type. Return ONLY a valid compact JSON array of [text,type] pairs, or [] when there is no PII. In every pair, text must be an exact substring copied from the input and type must be exactly one of private_person, private_email, private_phone, private_address, private_url, private_date, account_number, secret, or other_pii. Return one pair per annotated field. Never combine adjacent fields, include a field name or separator in text, translate text, normalize formatting, repair punctuation, invent text, use another label, or add explanation.

Type mapping:
- private_person: given name, surname, full personal name, personal title, or username.
- private_email: email address.
- private_phone: telephone or fax number.
- private_address: building number, street, city, state/province, postcode, country, apartment/secondary address, or geographic coordinates.
- private_url: personal/private URL or any IPv4/IPv6 address.
- private_date: birth date, other annotated personal date, or time.
- account_number: ID card, passport, driver's license, social number, bank/card/customer/order/account identifier.
- secret: password, PIN, passcode, API key, authentication token, or secret.
- other_pii: sex/gender value or PII not covered above.

Follow the annotated field or repeating record schema, not a subjective sensitivity judgment or the visual shape alone. A username is private_person; a title is private_person; an IP address is private_url; a social number, passport, driver's license, or ID card is account_number; a password or PIN is secret; a time is private_date; a building, postcode, country, or coordinate is private_address; and a sex/gender value is other_pii. Labels may be English, Dutch, French, German, Italian, or Spanish. Inputs may be prose, JSON, XML, HTML, Markdown, YAML, forms, tables, messages, fragments, or dense delimiter-separated records. Extract short values such as M, F, H, GB, NL, ENG, 13, 163, Dr, Ms, or a three-letter identifier when their field identifies a listed PII type.

Rules:
- Scan through the final character and return every PII field. In repeated records, infer the columns from the header or a complete record and apply exactly those columns and types to every later record.
- In CSV or tables, do not return the row number from a generic ID or index column. An ID is account_number only when its field means ID card, passport, driver's license, social number, bank/card/account/customer/order identifier, or another personal account identifier.
- Never return values from comment, note, agreement, waiver, admission status, description, usage, monitoring, security, restriction, perspective, grammatical person, project, course, program, activity, or ordinary location fields unless the value itself occupies an explicitly listed PII field.
- Generic role words such as candidate, participant, student, member, user, client, customer, support, instructor, and trainee are not part of a personal name. If a personal name follows such a role, return only the name as private_person.
- Separators such as ..., ampersand, comma, pipe, colon, semicolon, newline, and visible backslash+n can divide fields. Split neighboring fields and preserve every character inside each text value.
- Extract a date or time when it fills a DATE, TIME, BOD, birth-date, appointment, deadline, signature-date, or equivalent personal field. Do not extract an administrative period merely because its key contains Start Date or End Date.
- Usernames may be random letters/digits, dotted names, initials, bracketed values, or identifiers before a colon in a participant or message list. Do not include surrounding brackets in text.
- Bracketed personal values are PII, except generic underscore placeholders such as [CURRENT_DATE], [UNIVERSITY_NAME], [YOUR_NAME], and [FIELD_OF_STUDY].
- Split every annotated address component into a separate private_address pair. A repeating unlabeled address row may use telephone, country, building, street, city, state, postcode, secondary address, and surname as separate columns with private_phone, private_address, and private_person types.
- When a name is followed by an ID in parentheses, separate them. Return the name only if it is an annotated personal-name field; return the parenthesized ID as account_number when it is a listed personal identifier.
- A complete value at the start or end of a chunk is valid. Ignore only a visibly severed fragment that cannot be identified.

Input: ID,SOCIALNUMBER,TEL,COMMENTS\n1,777 064 4987,007.200-193-8263,"Plan and implement engaging course content."\n2,710.076.3818,099 3802-9499,"Integrate multimedia into the course."
Output: [["777 064 4987","account_number"],["007.200-193-8263","private_phone"],["710.076.3818","account_number"],["099 3802-9499","private_phone"]]

Input: ID,TITLE,IDCARD,DRIVERLICENSE,AGREEMENT\n1,"Baron","CUL","KQ84LLYHL6","Property damage liability waiver is granted."\n2,"Prinses","98118263685763","077780822","Final waiver documented and signed off."
Output: [["Baron","private_person"],["CUL","account_number"],["KQ84LLYHL6","account_number"],["Prinses","private_person"],["98118263685763","account_number"],["077780822","account_number"]]

Input: {"Schedule_A":{"Time":"20:19","Usage":"Available for basketball training","Monitoring":"Supervised by coaches","Security":"Key provided to club personnel"},"Schedule_B":{"Time":"6:01","Restrictions":"No outdoor shoes"}}
Output: [["20:19","private_date"],["6:01","private_date"]]

Input: nolwen.pedetti2003 participó desde una perspectiva Formal en Tercera Persona Singular. H ofreció su opinión desde la Tercera Persona Singular, Set II. gejpgb21 se unió a la conversación.
Output: [["nolwen.pedetti2003","private_person"],["H","private_person"],["gejpgb21","private_person"]]

Input: **Candidat Étienne**\n- Autre\n- Huissier\n- mathe.vuketic1998\n- Z0603982423869\n- +33 63.728-6394
Output: [["Étienne","private_person"],["Autre","other_pii"],["Huissier","private_person"],["mathe.vuketic1998","private_person"],["Z0603982423869","account_number"],["+33 63.728-6394","private_phone"]]

Input: Femme&18 mars 1941&sgummala@gmail.com&IWM&00817 090 768.6978&NL&353&Melis Stokelaan&Den Haag&ZH&2533 EL&Pod 9&8:17
Output: [["Femme","other_pii"],["18 mars 1941","private_date"],["sgummala@gmail.com","private_email"],["IWM","account_number"],["00817 090 768.6978","private_phone"],["NL","private_address"],["353","private_address"],["Melis Stokelaan","private_address"],["Den Haag","private_address"],["ZH","private_address"],["2533 EL","private_address"],["Pod 9","private_address"],["8:17","private_date"]]

Input: 2-60-03-76248-281-75,67.176.53.168...2.53.06.25467.868.33,126.207.172.140...[47.4, -1.59551]...00:08:32
Output: [["2-60-03-76248-281-75","account_number"],["67.176.53.168","private_url"],["2.53.06.25467.868.33","account_number"],["126.207.172.140","private_url"],["[47.4, -1.59551]","private_address"],["00:08:32","private_date"]]

Input: - id(1) - 084.910-0987, Nederland, 770, Tiendweg, Lopik, UT, 3411, Kamenova\n- id(2) - +26.82 907.1047, NL, 414, Bruininxdeelse Kade, Leerdam, ZH, 4143 LM, Section 740, Krane
Output: [["084.910-0987","private_phone"],["Nederland","private_address"],["770","private_address"],["Tiendweg","private_address"],["Lopik","private_address"],["UT","private_address"],["3411","private_address"],["Kamenova","private_person"],["+26.82 907.1047","private_phone"],["NL","private_address"],["414","private_address"],["Bruininxdeelse Kade","private_address"],["Leerdam","private_address"],["ZH","private_address"],["4143 LM","private_address"],["Section 740","private_address"],["Krane","private_person"]]

Input: Password: d.20GBm!3!; PIN: 4821; Passport: P88W6668O; IP: 213.36.161.135; Sex: F
Output: [["d.20GBm!3!","secret"],["4821","secret"],["P88W6668O","account_number"],["213.36.161.135","private_url"],["F","other_pii"]]

Input: Strategic_Plan: Piano Strategico per l'Attrazione degli Studenti. Activity_Name: Virtual Reality Integration in Educational Curriculum. Policy: Property damage liability waiver is granted. Participants: Tercera Persona Singular, Set I.
Output: []
```

</details>

<details>
<summary><code>specs/pii-detector-typed-ft-v2.txt</code> — SHA-256 <code>a751c7a182ef90a0ced66de641ebdce78bdfec60985447125e6e19dab25cb0bd</code></summary>

```text
Extract every AI4Privacy-style PII value from the input and assign its canonical nine-way type. Return ONLY a valid compact JSON array of [text,type] pairs, or [] when there is no PII. In every pair, text must be an exact substring copied from the input and type must be exactly one of private_person, private_email, private_phone, private_address, private_url, private_date, account_number, secret, or other_pii. Return one pair per annotated field. Never combine adjacent fields, include a field name or separator in text, translate text, normalize formatting, repair punctuation, invent text, use another label, or add explanation.

Type mapping:
- private_person: given name, surname, full personal name, personal title, or username.
- private_email: email address.
- private_phone: telephone or fax number.
- private_address: building number, street, city, state/province, postcode, country, apartment/secondary address, or geographic coordinates.
- private_url: personal/private URL or any IPv4/IPv6 address.
- private_date: birth date, other annotated personal date, or time.
- account_number: ID card, passport, driver's license, social number, bank/card/customer/order/account identifier.
- secret: password, PIN, passcode, API key, authentication token, or secret.
- other_pii: sex/gender value or PII not covered above.

Follow the annotated field or repeating record schema, not a subjective sensitivity judgment or the visual shape alone. A username is private_person; a title is private_person; an IP address is private_url; a social number, passport, driver's license, or ID card is account_number; a password or PIN is secret; a time is private_date; a building, postcode, country, or coordinate is private_address; and a sex/gender value is other_pii. Labels may be English, Dutch, French, German, Italian, or Spanish. Inputs may be prose, JSON, XML, HTML, Markdown, YAML, forms, tables, messages, fragments, or dense delimiter-separated records. Extract short values such as M, F, H, GB, NL, ENG, 13, 163, Dr, Ms, or a three-letter identifier when their field identifies a listed PII type.

Rules:
- Scan through the final character and return every PII field. In repeated records, infer the columns from the header or a complete record and apply exactly those columns and types to every later record.
- In CSV or tables, do not return the row number from a generic ID or index column. An ID is account_number only when its field means ID card, passport, driver's license, social number, bank/card/account/customer/order identifier, or another personal account identifier.
- Never return values from comment, note, agreement, waiver, admission status, description, usage, monitoring, security, restriction, perspective, grammatical person, project, course, program, activity, or ordinary location fields unless the value itself occupies an explicitly listed PII field.
- Generic role words such as candidate, participant, student, member, user, client, customer, support, instructor, and trainee are not part of a personal name. If a personal name follows such a role, return only the name as private_person.
- Separators such as ..., ampersand, comma, pipe, colon, semicolon, newline, and visible backslash+n can divide fields. Split neighboring fields and preserve every character inside each text value.
- Extract a date or time when it fills a DATE, TIME, BOD, birth-date, appointment, deadline, signature-date, or equivalent personal field. Do not extract an administrative period merely because its key contains Start Date or End Date. Month/year forms such as juillet/00, novembre/70, März/93, août/64 and hour forms such as 11h are private_date when they occupy date, birth-date, or time positions.
- Usernames may be random letters/digits, dotted names, initials, bracketed values, or identifiers before a colon in a participant or message list. Do not include surrounding brackets in text.
- Bracketed personal values are PII, except generic underscore placeholders such as [CURRENT_DATE], [UNIVERSITY_NAME], [YOUR_NAME], and [FIELD_OF_STUDY].
- Split every annotated address component into a separate private_address pair. A repeating unlabeled address row may use telephone, country, building, street, city, state, postcode, secondary address, and surname as separate columns with private_phone, private_address, and private_person types.
- When a name is followed by an ID in parentheses, separate them. Return the name only if it is an annotated personal-name field; return the parenthesized ID as account_number when it is a listed personal identifier.
- Every complete string containing @ and an email domain is private_email, even when the local part is one letter, all capitals, numeric, or username-like.
- An IPv4 or IPv6 address is always private_url, never secret or account_number. A dotted number is IPv4 only when it has exactly four valid octets; longer dotted, dashed, spaced, or plain numbers in a SOCIALNUMBER position are account_number.
- A passport, driver's-license, ID-card, or social-number value is account_number regardless of whether it resembles a phone number, address, URL, password, or random identifier. Do not label a value secret without an explicit password, PIN, passcode, key, token, or secret field or a schema that establishes that field.
- In alternating EMAIL,SOCIALNUMBER records, every email is private_email and each following social number is account_number. In alternating SOCIALNUMBER,IP records, every social number is account_number and every IP is private_url; preserve this alternation through the final record.
- In a repeated title-plus-sex record, split the title and sex value. Titles such as Pres, Ambassador, Profesor, Príncipe, Cde, Baron, Duchesse, Roi, and Pape are private_person; sex values such as M, F, H, W, V, male, female, masculine, feminine, Masculino, Femmina, Männlich, Vrouw, Non-binaire, Otro, Autre, or Prefiero no revelar are other_pii.
- In a pattern written as - id(n) - telephone, country, building, street, city, state, postcode, optional secondary address, surname, ignore the generic id(n), extract only the telephone as private_phone without the prefix, assign address components to private_address, and assign the final surname to private_person.
- Return each annotated substring once per occurrence and stop after the last input field. Never repeat an output cycle to fill the token budget.
- A complete value at the start or end of a chunk is valid. Ignore only a visibly severed fragment that cannot be identified.

Input: ID,SOCIALNUMBER,TEL,COMMENTS\n1,777 064 4987,007.200-193-8263,"Plan and implement engaging course content."\n2,710.076.3818,099 3802-9499,"Integrate multimedia into the course."
Output: [["777 064 4987","account_number"],["007.200-193-8263","private_phone"],["710.076.3818","account_number"],["099 3802-9499","private_phone"]]

Input: ID,TITLE,IDCARD,DRIVERLICENSE,AGREEMENT\n1,"Baron","CUL","KQ84LLYHL6","Property damage liability waiver is granted."\n2,"Prinses","98118263685763","077780822","Final waiver documented and signed off."
Output: [["Baron","private_person"],["CUL","account_number"],["KQ84LLYHL6","account_number"],["Prinses","private_person"],["98118263685763","account_number"],["077780822","account_number"]]

Input: {"Schedule_A":{"Time":"20:19","Usage":"Available for basketball training","Monitoring":"Supervised by coaches","Security":"Key provided to club personnel"},"Schedule_B":{"Time":"6:01","Restrictions":"No outdoor shoes"}}
Output: [["20:19","private_date"],["6:01","private_date"]]

Input: nolwen.pedetti2003 participó desde una perspectiva Formal en Tercera Persona Singular. H ofreció su opinión desde la Tercera Persona Singular, Set II. gejpgb21 se unió a la conversación.
Output: [["nolwen.pedetti2003","private_person"],["H","private_person"],["gejpgb21","private_person"]]

Input: **Candidat Étienne**\n- Autre\n- Huissier\n- mathe.vuketic1998\n- Z0603982423869\n- +33 63.728-6394
Output: [["Étienne","private_person"],["Autre","other_pii"],["Huissier","private_person"],["mathe.vuketic1998","private_person"],["Z0603982423869","account_number"],["+33 63.728-6394","private_phone"]]

Input: Femme&18 mars 1941&sgummala@gmail.com&IWM&00817 090 768.6978&NL&353&Melis Stokelaan&Den Haag&ZH&2533 EL&Pod 9&8:17
Output: [["Femme","other_pii"],["18 mars 1941","private_date"],["sgummala@gmail.com","private_email"],["IWM","account_number"],["00817 090 768.6978","private_phone"],["NL","private_address"],["353","private_address"],["Melis Stokelaan","private_address"],["Den Haag","private_address"],["ZH","private_address"],["2533 EL","private_address"],["Pod 9","private_address"],["8:17","private_date"]]

Input: 2-60-03-76248-281-75,67.176.53.168...2.53.06.25467.868.33,126.207.172.140...[47.4, -1.59551]...00:08:32
Output: [["2-60-03-76248-281-75","account_number"],["67.176.53.168","private_url"],["2.53.06.25467.868.33","account_number"],["126.207.172.140","private_url"],["[47.4, -1.59551]","private_address"],["00:08:32","private_date"]]

Input: - id(1) - 084.910-0987, Nederland, 770, Tiendweg, Lopik, UT, 3411, Kamenova\n- id(2) - +26.82 907.1047, NL, 414, Bruininxdeelse Kade, Leerdam, ZH, 4143 LM, Section 740, Krane
Output: [["084.910-0987","private_phone"],["Nederland","private_address"],["770","private_address"],["Tiendweg","private_address"],["Lopik","private_address"],["UT","private_address"],["3411","private_address"],["Kamenova","private_person"],["+26.82 907.1047","private_phone"],["NL","private_address"],["414","private_address"],["Bruininxdeelse Kade","private_address"],["Leerdam","private_address"],["ZH","private_address"],["4143 LM","private_address"],["Section 740","private_address"],["Krane","private_person"]]

Input: Password: d.20GBm!3!; PIN: 4821; Passport: P88W6668O; IP: 213.36.161.135; Sex: F
Output: [["d.20GBm!3!","secret"],["4821","secret"],["P88W6668O","account_number"],["213.36.161.135","private_url"],["F","other_pii"]]

Input: tfjasta87868@gmail.com...2 57 01 85136 028 30...B@tutanota.com...2.49.03.19524.337.91...16zedije.pushparajan@protonmail.com...281026534565850...vorwpbmukqk371354@aol.com...278-32-5098...K@tutanota.com...1-72-09-38517-757-27...tervel@protonmail.com...1-37-05-86277-936-49...SEC2003@tutanota.com...915 878 5014...K2002@gmail.com...439515942620...gleison.coppey9@yahoo.com...1.35.08.74766.481.58...amrah.sarbat@tutanota.com...255090873523967...[46.63, -0.7]
Output: [["tfjasta87868@gmail.com","private_email"],["2 57 01 85136 028 30","account_number"],["B@tutanota.com","private_email"],["2.49.03.19524.337.91","account_number"],["16zedije.pushparajan@protonmail.com","private_email"],["281026534565850","account_number"],["vorwpbmukqk371354@aol.com","private_email"],["278-32-5098","account_number"],["K@tutanota.com","private_email"],["1-72-09-38517-757-27","account_number"],["tervel@protonmail.com","private_email"],["1-37-05-86277-936-49","account_number"],["SEC2003@tutanota.com","private_email"],["915 878 5014","account_number"],["K2002@gmail.com","private_email"],["439515942620","account_number"],["gleison.coppey9@yahoo.com","private_email"],["1.35.08.74766.481.58","account_number"],["amrah.sarbat@tutanota.com","private_email"],["255090873523967","account_number"],["[46.63, -0.7]","private_address"]]

Input: juillet/00, 01:12:35, Chemin de l'Étang...ssiksou, 2002-07-25T00:00:00...1970bixio.gourlaouen, novembre/70...1993bolombo, 17/05/1993...elloh, 20 mai 1966...ogozhkyfqekpqzm49, 6 juillet 1997...bekic, 27/05/1983...seon.iannucci, 07/10/1965...bcbteuwprkwrpq23, 1993-09-04T00:00:00...georgette.sandonà, 1983-09-26T00:00:00...vondergroeben, août/64...
Output: [["juillet/00","private_date"],["01:12:35","private_date"],["Chemin de l'Étang","private_address"],["ssiksou","private_person"],["2002-07-25T00:00:00","private_date"],["1970bixio.gourlaouen","private_person"],["novembre/70","private_date"],["1993bolombo","private_person"],["17/05/1993","private_date"],["elloh","private_person"],["20 mai 1966","private_date"],["ogozhkyfqekpqzm49","private_person"],["6 juillet 1997","private_date"],["bekic","private_person"],["27/05/1983","private_date"],["seon.iannucci","private_person"],["07/10/1965","private_date"],["bcbteuwprkwrpq23","private_person"],["1993-09-04T00:00:00","private_date"],["georgette.sandonà","private_person"],["1983-09-26T00:00:00","private_date"],["vondergroeben","private_person"],["août/64","private_date"]]

Input: 3 FRA 31XS5675 6 061229 LUANN\n- Giocatore D: \n   - XJW091723R\n   - 0263907438\n- Giocatore E: \n   - ACJ562952F\n   - 9135062264\n- Giocatore F: \n   - POB048638B\n   - 2398226009\n- Giocatore G: \n   - KST285730Q\n   - 4395026092
Output: [["XJW091723R","account_number"],["0263907438","account_number"],["ACJ562952F","account_number"],["9135062264","account_number"],["POB048638B","account_number"],["2398226009","account_number"],["KST285730Q","account_number"],["4395026092","account_number"]]

Input: n: R8.31.PFSGVVM.8\n   - Pass: U73K2612E\n\n4. Schüler D:\n   - Führerschein: C6.27.SPSVM67.4\n   - Pass: P88W6668O\n\n5. Schüler E:\n   - Führerschein: C1.45.S3BCML8.3\n   - Pass: C98V6099G\n\n6. Schüler F:\n   - Führerschein: M2923BZ8ND49\n   - Pass: Y17Q7977Z\n\n7. Schüler G:\n   - Führerschein: T8327MKT2SW5\n   - Pass: A92H5631K\n\n8. Schüler H:\n   - Führerschein: A5.29.U
Output: [["R8.31.PFSGVVM.8","account_number"],["U73K2612E","account_number"],["C6.27.SPSVM67.4","account_number"],["P88W6668O","account_number"],["C1.45.S3BCML8.3","account_number"],["C98V6099G","account_number"],["M2923BZ8ND49","account_number"],["Y17Q7977Z","account_number"],["T8327MKT2SW5","account_number"],["A92H5631K","account_number"],["A5.29.U","account_number"]]

Input: <li><strong>Pres Masculino</strong></li><li><strong>Ambassador Prefiero no revelar</strong></li><li><strong>Profesor Otro</strong></li><li><strong>Príncipe Masculino</strong></li><li><strong>Cde M</strong></li><p>Fecha de creación: 09/06/2005 - Hora: 10:01</p>
Output: [["Pres","private_person"],["Masculino","other_pii"],["Ambassador","private_person"],["Prefiero no revelar","other_pii"],["Profesor","private_person"],["Otro","other_pii"],["Príncipe","private_person"],["Masculino","other_pii"],["Cde","private_person"],["M","other_pii"],["09/06/2005","private_date"],["10:01","private_date"]]

Input: Strategic_Plan: Piano Strategico per l'Attrazione degli Studenti. Activity_Name: Virtual Reality Integration in Educational Curriculum. Policy: Property damage liability waiver is granted. Participants: Tercera Persona Singular, Set I.
Output: []
```

</details>

<details>
<summary><code>specs/pii-detector-typed-ft-v3.txt</code> — SHA-256 <code>99ee309c206469196ca0fa8358ca280c6edbe835b2e27d6e4538062f99ac15b7</code></summary>

```text
Extract every AI4Privacy-style PII value and type. Return ONLY a compact valid JSON array of [text,type] pairs, or []. Text must be an exact input substring and type exactly private_person, private_email, private_phone, private_address, private_url, private_date, account_number, secret, or other_pii. Return one pair per annotated field. Never combine fields, include labels or separators, normalize or invent text, repeat a cycle, or explain.

Type mapping:
- private_person: personal name, surname, title, or username.
- private_email: email address.
- private_phone: telephone or fax number.
- private_address: building, street, city, state/province, postcode, country, secondary address, or coordinates.
- private_url: personal URL or IPv4/IPv6 address.
- private_date: birth date, personal date, or time.
- account_number: ID card, passport, driver's license, social number, or personal bank/card/customer/order/account identifier.
- secret: password, PIN, passcode, API key, authentication token, or secret.
- other_pii: sex/gender or PII not covered above.

Rules:
- Scan through the final character. Infer every column from a header or complete record and preserve the schema in later rows. Return each annotated occurrence once, then close the array.
- Ignore generic ID/index columns and values in comments, notes, agreements, statuses, descriptions, restrictions, perspective, project, course, program, or activity fields.
- Split neighboring fields at ..., ampersand, comma, pipe, colon, semicolon, newline, visible backslash+n, HTML tags, or list boundaries. Preserve all characters inside each value but no surrounding brackets unless coordinates include brackets.
- A username or title is private_person; an IP is private_url; a social number, passport, driver's license, or ID card is account_number; a password/PIN is secret; a time/date is private_date; an address component is private_address; and a sex/gender value is other_pii.
- Every complete string with @ and an email domain is private_email, including one-letter, uppercase, numeric, or username-like local parts.
- In alternating EMAIL,SOCIALNUMBER sequences, @ values are private_email and alternating numeric, dotted, dashed, spaced, or alphanumeric values are account_number. In alternating SOCIALNUMBER,IP sequences, valid four-octet IPv4 and colon-delimited IPv6 values are private_url and the alternating values are account_number.
- A social number, passport, license, or ID is account_number even if it resembles a phone, IP, password, address, or name. Use secret only for an explicit password, PIN, passcode, key, token, or secret field.
- Month/year dates such as juillet/00, novembre/70, März/93, and août/64 and hours such as 11h are private_date in date/time positions.
- Split title-plus-sex records: the title is private_person and M, F, H, W, V, Masculino, Femmina, Männlich, Vrouw, Non-binaire, Otro, Autre, or Prefiero no revelar is other_pii in a sex position.
- In - id(n) - telephone, country, building, street, city, state, postcode, optional secondary address, surname rows, ignore id(n), return the telephone alone as private_phone, address fields as private_address, and surname as private_person.
- Generic roles are not part of a name. Generic underscore placeholders are not PII.

Input: tfjasta87868@gmail.com...2 57 01 85136 028 30...B@tutanota.com...2.49.03.19524.337.91...16zedije.pushparajan@protonmail.com...281026534565850...vorwpbmukqk371354@aol.com...278-32-5098...K@tutanota.com...1-72-09-38517-757-27...tervel@protonmail.com...1-37-05-86277-936-49...SEC2003@tutanota.com...915 878 5014...K2002@gmail.com...439515942620...[46.63, -0.7]
Output: [["tfjasta87868@gmail.com","private_email"],["2 57 01 85136 028 30","account_number"],["B@tutanota.com","private_email"],["2.49.03.19524.337.91","account_number"],["16zedije.pushparajan@protonmail.com","private_email"],["281026534565850","account_number"],["vorwpbmukqk371354@aol.com","private_email"],["278-32-5098","account_number"],["K@tutanota.com","private_email"],["1-72-09-38517-757-27","account_number"],["tervel@protonmail.com","private_email"],["1-37-05-86277-936-49","account_number"],["SEC2003@tutanota.com","private_email"],["915 878 5014","account_number"],["K2002@gmail.com","private_email"],["439515942620","account_number"],["[46.63, -0.7]","private_address"]]

Input: 2-60-03-76248-281-75,67.176.53.168...2.53.06.25467.868.33,126.207.172.140...2-48-01-24327-318-13,6a56:cd26:f4a2:15b9:372f:afff:8764:c0f3...1.50.12.71501.796.58,9ee3:624b:2c52:ff73:b147:d96a:8da:6064...1 70 03 66791 501 11,962:2d18:c84a:dc4a:7ebf:657b:dce1:9b57...239064649446220,0.30.156.50...[47.4, -1.59551]...00:08:32
Output: [["2-60-03-76248-281-75","account_number"],["67.176.53.168","private_url"],["2.53.06.25467.868.33","account_number"],["126.207.172.140","private_url"],["2-48-01-24327-318-13","account_number"],["6a56:cd26:f4a2:15b9:372f:afff:8764:c0f3","private_url"],["1.50.12.71501.796.58","account_number"],["9ee3:624b:2c52:ff73:b147:d96a:8da:6064","private_url"],["1 70 03 66791 501 11","account_number"],["962:2d18:c84a:dc4a:7ebf:657b:dce1:9b57","private_url"],["239064649446220","account_number"],["0.30.156.50","private_url"],["[47.4, -1.59551]","private_address"],["00:08:32","private_date"]]

Input: juillet/00, 01:12:35, Chemin de l'Étang...ssiksou, 2002-07-25T00:00:00...1970bixio.gourlaouen, novembre/70...1993bolombo, 17/05/1993...elloh, 20 mai 1966...ogozhkyfqekpqzm49, 6 juillet 1997...bekic, 27/05/1983...seon.iannucci, 07/10/1965...bcbteuwprkwrpq23, août/64
Output: [["juillet/00","private_date"],["01:12:35","private_date"],["Chemin de l'Étang","private_address"],["ssiksou","private_person"],["2002-07-25T00:00:00","private_date"],["1970bixio.gourlaouen","private_person"],["novembre/70","private_date"],["1993bolombo","private_person"],["17/05/1993","private_date"],["elloh","private_person"],["20 mai 1966","private_date"],["ogozhkyfqekpqzm49","private_person"],["6 juillet 1997","private_date"],["bekic","private_person"],["27/05/1983","private_date"],["seon.iannucci","private_person"],["07/10/1965","private_date"],["bcbteuwprkwrpq23","private_person"],["août/64","private_date"]]

Input: - id(1) - 084.910-0987, Nederland, 770, Tiendweg, Lopik, UT, 3411, Kamenova\n- id(2) - +26.82 907.1047, NL, 414, Bruininxdeelse Kade, Leerdam, ZH, 4143 LM, Section 740, Krane
Output: [["084.910-0987","private_phone"],["Nederland","private_address"],["770","private_address"],["Tiendweg","private_address"],["Lopik","private_address"],["UT","private_address"],["3411","private_address"],["Kamenova","private_person"],["+26.82 907.1047","private_phone"],["NL","private_address"],["414","private_address"],["Bruininxdeelse Kade","private_address"],["Leerdam","private_address"],["ZH","private_address"],["4143 LM","private_address"],["Section 740","private_address"],["Krane","private_person"]]

Input: 3 FRA 31XS5675 6 061229 LUANN\n- Giocatore D:\n- XJW091723R\n- 0263907438\n- Giocatore E:\n- ACJ562952F\n- 9135062264\n- Giocatore F:\n- POB048638B\n- 2398226009
Output: [["XJW091723R","account_number"],["0263907438","account_number"],["ACJ562952F","account_number"],["9135062264","account_number"],["POB048638B","account_number"],["2398226009","account_number"]]

Input: <li><strong>Pres Masculino</strong></li><li><strong>Ambassador Prefiero no revelar</strong></li><li><strong>Profesor Otro</strong></li><li><strong>Príncipe Masculino</strong></li><li><strong>Cde M</strong></li><p>Fecha: 09/06/2005 - Hora: 10:01</p>
Output: [["Pres","private_person"],["Masculino","other_pii"],["Ambassador","private_person"],["Prefiero no revelar","other_pii"],["Profesor","private_person"],["Otro","other_pii"],["Príncipe","private_person"],["Masculino","other_pii"],["Cde","private_person"],["M","other_pii"],["09/06/2005","private_date"],["10:01","private_date"]]
```

</details>

<details>
<summary><code>specs/pii-detector-typed-ft-v4.txt</code> — SHA-256 <code>6332033b0f8d3342c0b0fd85127c3e7f5280ab3a2702fcf2cf8cf5e99ef05856</code></summary>

```text
Extract every AI4Privacy-style PII value from the input and assign its canonical nine-way type. Return ONLY a valid compact JSON array of [text,type] pairs, or [] when there is no PII. In every pair, text must be an exact substring copied from the input and type must be exactly one of private_person, private_email, private_phone, private_address, private_url, private_date, account_number, secret, or other_pii. Return one pair per annotated field occurrence. Never combine adjacent fields, include a field name or separator in text, translate text, normalize formatting, repair punctuation, invent text, repeat a value beyond its occurrences, use another label, or add explanation.

Type mapping:
- private_person: given name, surname, full personal name, personal title, or username.
- private_email: email address.
- private_phone: telephone or fax number.
- private_address: building number, street, city, state/province, postcode, country, apartment/secondary address, or geographic coordinates.
- private_url: personal/private URL or any IPv4/IPv6 address.
- private_date: birth date, other annotated personal date, or time.
- account_number: ID card, passport, driver's license, social number, bank/card/customer/order/account identifier.
- secret: password, PIN, passcode, API key, authentication token, or secret.
- other_pii: sex/gender value or PII not covered above.

Rules:
- Follow an explicit field label, table header, repeating record schema, or strongly established alternation instead of guessing from visual shape alone. Infer the columns from a header or complete record and apply exactly those columns and types through the final complete record.
- Scan through the final character, but return only values supported by a listed PII field or an established PII schema. Do not turn ordinary prose into names, addresses, dates, URLs, or secrets merely because it contains plausible-looking words or numbers.
- In CSV or tables, ignore a generic ID/index column. An ID is account_number only when its field means ID card, passport, driver's license, social number, bank/card/account/customer/order identifier, or another personal account identifier.
- Never return values from comment, note, agreement, waiver, admission status, description, usage, monitoring, security, restriction, perspective, grammatical person, project, course, program, activity, or ordinary location fields unless the value occupies a separately established PII field.
- Generic role words such as candidate, participant, student, member, user, client, customer, support, instructor, trainee, and player are not personal names. If a personal name follows such a role, return only the name.
- Split fields at ..., ampersand, comma, pipe, colon, semicolon, newline, visible backslash+n, HTML tags, or list boundaries. Preserve every character inside each value, but exclude surrounding labels, list markers, quotes, brackets, and separators unless brackets are part of geographic coordinates.
- Every complete email address is private_email, including one-letter, all-capital, numeric, or username-like local parts. An IPv4 or IPv6 address is private_url, never secret or account_number. A dotted number is IPv4 only when it has exactly four valid octets.
- A social number, passport, driver's license, or ID card is account_number even when it resembles a phone, IP, password, address, or name. Use secret only for an explicit password, PIN, passcode, key, token, or secret field.
- In alternating EMAIL,SOCIALNUMBER records, every email is private_email and each following social number is account_number. In alternating SOCIALNUMBER,IP records, every social number is account_number and every IP is private_url. Preserve the alternation through the final complete pair.
- A username and a personal title are private_person. A time or personal date is private_date. Address components are separate private_address values. A sex/gender field is other_pii.
- In repeated title-plus-sex records, split each title from its sex value. M, F, H, W, V, Masculino, Femmina, Männlich, Vrouw, Non-binaire, Otro, Autre, and Prefiero no revelar are other_pii only in a sex/gender position.
- In a pattern written as - id(n) - telephone, country, building, street, city, state, postcode, optional secondary address, surname, ignore id(n), return the telephone alone as private_phone, address fields as private_address, and the final surname as private_person.
- Bracketed personal values remain PII, except generic underscore placeholders such as [CURRENT_DATE], [UNIVERSITY_NAME], [YOUR_NAME], and [FIELD_OF_STUDY]. Ignore a visibly severed fragment that cannot be identified.

Input: ID,SOCIALNUMBER,TEL,COMMENTS\n1,777 064 4987,007.200-193-8263,"Plan and implement engaging course content."\n2,710.076.3818,099 3802-9499,"Integrate multimedia into the course."
Output: [["777 064 4987","account_number"],["007.200-193-8263","private_phone"],["710.076.3818","account_number"],["099 3802-9499","private_phone"]]

Input: tfjasta87868@gmail.com...2 57 01 85136 028 30...B@tutanota.com...2.49.03.19524.337.91...K@tutanota.com...1-72-09-38517-757-27...[46.63, -0.7]
Output: [["tfjasta87868@gmail.com","private_email"],["2 57 01 85136 028 30","account_number"],["B@tutanota.com","private_email"],["2.49.03.19524.337.91","account_number"],["K@tutanota.com","private_email"],["1-72-09-38517-757-27","account_number"],["[46.63, -0.7]","private_address"]]

Input: 2-60-03-76248-281-75,67.176.53.168...2.53.06.25467.868.33,126.207.172.140...2-48-01-24327-318-13,6a56:cd26:f4a2:15b9:372f:afff:8764:c0f3...[47.4, -1.59551]...00:08:32
Output: [["2-60-03-76248-281-75","account_number"],["67.176.53.168","private_url"],["2.53.06.25467.868.33","account_number"],["126.207.172.140","private_url"],["2-48-01-24327-318-13","account_number"],["6a56:cd26:f4a2:15b9:372f:afff:8764:c0f3","private_url"],["[47.4, -1.59551]","private_address"],["00:08:32","private_date"]]

Input: <li><strong>Pres Masculino</strong></li><li><strong>Ambassador Prefiero no revelar</strong></li><li><strong>Profesor Otro</strong></li><li><strong>Cde M</strong></li><p>Fecha: 09/06/2005 - Hora: 10:01</p>
Output: [["Pres","private_person"],["Masculino","other_pii"],["Ambassador","private_person"],["Prefiero no revelar","other_pii"],["Profesor","private_person"],["Otro","other_pii"],["Cde","private_person"],["M","other_pii"],["09/06/2005","private_date"],["10:01","private_date"]]

Input: - id(1) - 084.910-0987, Nederland, 770, Tiendweg, Lopik, UT, 3411, Kamenova\n- id(2) - +26.82 907.1047, NL, 414, Bruininxdeelse Kade, Leerdam, ZH, 4143 LM, Section 740, Krane
Output: [["084.910-0987","private_phone"],["Nederland","private_address"],["770","private_address"],["Tiendweg","private_address"],["Lopik","private_address"],["UT","private_address"],["3411","private_address"],["Kamenova","private_person"],["+26.82 907.1047","private_phone"],["NL","private_address"],["414","private_address"],["Bruininxdeelse Kade","private_address"],["Leerdam","private_address"],["ZH","private_address"],["4143 LM","private_address"],["Section 740","private_address"],["Krane","private_person"]]

Input: Password: d.20GBm!3!; PIN: 4821; Passport: P88W6668O; IP: 213.36.161.135; Sex: F; Email: A@protonmail.com
Output: [["d.20GBm!3!","secret"],["4821","secret"],["P88W6668O","account_number"],["213.36.161.135","private_url"],["F","other_pii"],["A@protonmail.com","private_email"]]

Input: Strategic_Plan: Piano Strategico per l'Attrazione degli Studenti. Activity_Name: Virtual Reality Integration in Educational Curriculum. Policy: Property damage liability waiver is granted. Participants: Tercera Persona Singular, Set I.
Output: []
```

</details>

<details>
<summary><code>specs/pii-detector-typed-v5.txt</code> — SHA-256 <code>23319200618ce4014a44732eae3e2e77b7b352d1ef9c0bcc757ccb20612a4dd8</code></summary>

```text
Extract every AI4Privacy-style PII value from the input and assign its nine-way type. Return ONLY a valid compact JSON array of [text,type] pairs, or [] when there is no PII. In each pair, text must be an exact substring copied from the input and type must be one of private_person, private_email, private_phone, private_address, private_url, private_date, account_number, secret, or other_pii. No objects, explanations, labels outside the pairs, or surrounding text. Never combine separate source fields into one text value.

Type mapping:
- private_person: given name, surname, full personal name, personal title, or username.
- private_email: email address.
- private_phone: telephone or fax number.
- private_address: building number, street, city, state/province, postcode, country, apartment/secondary address, or geographic coordinates.
- private_url: personal/private URL or any IPv4/IPv6 address.
- private_date: birth date, other personal date, or time.
- account_number: ID card, passport, driver's license, social number, bank/card/customer/order/account identifier.
- secret: password, PIN, passcode, API key, authentication token, or secret.
- other_pii: sex/gender value or PII not covered above.

Follow the source field and record structure, not a subjective sensitivity judgment or the visual shape alone. A username is private_person and an IP address is private_url. A numeric password is secret, while a random-looking passport/license/ID/account value is account_number. A sex/gender field is other_pii. Extract short values such as M, F, GB, NL, ENG, 13, 163, Dr, Ms, or a three-letter ID when context identifies a PII field. Fields and prose may be English, Dutch, French, German, Italian, or Spanish. Inputs may be prose, JSON, XML, Markdown, YAML, forms, tables, lists, messages, or fragments.

Important patterns:
- Extract dates and times in labeled fields, schedules, appointments, deadlines, or phrases like "from the date ..." in any of the six languages.
- Usernames can be random letters/digits, dotted names, initials, bracketed values, or identifiers before a colon in a participant/message list.
- Bracketed personal values are PII, but generic template placeholders containing underscores such as [CURRENT_DATE], [UNIVERSITY_NAME], [YOUR_NAME], and [FIELD_OF_STUDY] are not.
- Split each address component into its own private_address pair. Do not merge a building, street, city, state, country, or postcode.
- When a name is followed by an ID in parentheses, separate them and assign account_number to the ID.
- Ignore an incomplete value cut off at the very start or end. Never guess, complete, translate, or normalize text; copy it exactly.
- Do not extract organization names, universities, medical conditions, ordinary topics, or generic role descriptions unless explicitly one of the listed personal fields.

Input: Hi, I'm Daniel Whitfield. Email daniels@meridiancap.com or call 415-555-0123.
Output: [["Daniel Whitfield","private_person"],["daniels@meridiancap.com","private_email"],["415-555-0123","private_phone"]]

Input: - Meeting at 2:33 PM\n- N23 - Meeting at 11:29pm\n- wennmann27 - Meeting at 4:45 PM
Output: [["2:33 PM","private_date"],["N23","private_person"],["11:29pm","private_date"],["wennmann27","private_person"],["4:45 PM","private_date"]]

Input: Beste deelnemers:\n- **JVT:** welkom.\n- **BYH:** bedankt.\nDatum: 2040-05-07T00:00:00
Output: [["JVT","private_person"],["BYH","private_person"],["2040-05-07T00:00:00","private_date"]]

Input: Geachte [20amara]. [Minister]: welkom. Background(augustus/39)
Output: [["20amara","private_person"],["Minister","private_person"],["augustus/39","private_date"]]

Input: País: US; Dirección: 927, Calle: Shaft Road, Ciudad: Wawarsing, Estado: NY, Código Postal: 12446; Nombre: Úrsula (00477097062)
Output: [["US","private_address"],["927","private_address"],["Shaft Road","private_address"],["Wawarsing","private_address"],["NY","private_address"],["12446","private_address"],["00477097062","account_number"]]

Input: Profile URL: https://portal.example/u/maya; IP: 192.168.1.8; PIN: 4821; Sex: F
Output: [["https://portal.example/u/maya","private_url"],["192.168.1.8","private_url"],["4821","secret"],["F","other_pii"]]

Input: Date: [CURRENT_DATE]; Title: [Madame]; Born: [juin/47]; ID: [5716022019873]; School: [UNIVERSITY_NAME]
Output: [["Madame","private_person"],["juin/47","private_date"],["5716022019873","account_number"]]

Input: The university reviewed the application and scheduled a general discussion.
Output: []
```

</details>

<details>
<summary><code>specs/pii-detector-typed-v6.txt</code> — SHA-256 <code>0b760ac100dbc02cd41e57320775827a0ff1cd840355e4feea0b83f3409eae57</code></summary>

```text
Extract every AI4Privacy-style PII value and assign its nine-way type. Return ONLY a valid compact JSON array of [text,type] pairs, or [] when there is no PII. text must be copied exactly from the input. type must be exactly one of private_person, private_email, private_phone, private_address, private_url, private_date, account_number, secret, other_pii. Never copy a source field name such as DRIVERLICENSE_A into type. No objects, explanations, or text outside the array. Never combine separate fields.

Map source fields as follows, ignoring record suffixes such as _A, _B, _BG, or digits:
- GIVENNAME, LASTNAME, NAME, TITLE, USERNAME -> private_person.
- EMAIL -> private_email.
- TEL, PHONE, FAX -> private_phone.
- BUILDING, STREET, CITY, STATE, POSTCODE, COUNTRY, SECADDRESS, GEOCOORD -> private_address.
- URL, IP -> private_url.
- BOD, DATE, TIME -> private_date.
- IDCARD, PASSPORT, DRIVERLICENSE, SOCIALNUMBER, ACCOUNTNUMBER, BANKACCOUNT, CARDNUMBER, customer/order/account ID -> account_number.
- PASS, PASSWORD, PIN, PASSCODE, API key, TOKEN, SECRET -> secret.
- SEX, GENDER -> other_pii.

Use the field meaning, not the value's shape. A username is private_person. An IP address is private_url. Any passport, driver's license, national/social number, identity card, customer ID, or account number is account_number even when random-looking; never call it private_person or secret. A password/PIN/token is secret even when numeric. A sex/gender value is other_pii even when it resembles a name. In German, Pass or Passnummer means passport and is account_number, while Passwort or Kennwort is secret. Italian Codice Fiscale and Carta d'Identità, Dutch rijbewijs and paspoort, French passeport/permis/numéro social, and Spanish pasaporte/DNI/licencia are account_number.

Follow explicit fields and repeated columns. Extract short values such as M, F, H, GB, NL, ENG, 13, 163, Dr, or a three-letter ID when context identifies a PII field. Text may be English, Dutch, French, German, Italian, or Spanish and may be prose, JSON, XML, HTML, Markdown, YAML, a table, CSV, list, fragment, or delimiter-only sequence. In a repeated unlabeled sequence, infer the type pattern from recognizable values and preserve it across every row. Scan to the end and output every value.

Do not extract organizations, universities, course/project/activity names, ordinary topics, generic role descriptions, or generic underscore placeholders such as [CURRENT_DATE], [UNIVERSITY_NAME], [YOUR_NAME], and [FIELD_OF_STUDY]. A complete value at a chunk boundary is valid; ignore only a visibly severed fragment. Never guess, translate, normalize, or alter text.

Input: {"DRIVERLICENSE_A":"AR6ZOGUIQLB","LASTNAME1_A":"Valverde","PASSPORT_B":"U73K2612E","TIME_BG":"3h","DATE_BG":"augustus 6e, 2015"}
Output: [["AR6ZOGUIQLB","account_number"],["Valverde","private_person"],["U73K2612E","account_number"],["3h","private_date"],["augustus 6e, 2015","private_date"]]

Input: Führerschein: C6.27.SPSVM67.4\nPass: P88W6668O\nPasswort: d.20GBm!3!
Output: [["C6.27.SPSVM67.4","account_number"],["P88W6668O","account_number"],["d.20GBm!3!","secret"]]

Input: Codice Fiscale: Bor Rot 24 D 56 0 CSO\nCarta d'Identità: UML711382U\nPassword: lx6QKu9}n2]
Output: [["Bor Rot 24 D 56 0 CSO","account_number"],["UML711382U","account_number"],["lx6QKu9}n2]","secret"]]

Input: 08synar.fogliadini@aol.com, 1 65 12 17708 422 33, leruijter@aol.com, 2-51-03-16321-225-58, 11h, [44.82273, -0.17]
Output: [["08synar.fogliadini@aol.com","private_email"],["1 65 12 17708 422 33","account_number"],["leruijter@aol.com","private_email"],["2-51-03-16321-225-58","account_number"],["11h","private_date"],["[44.82273, -0.17]","private_address"]]

Input: BOD,USERNAME,EMAIL,DRIVERLICENSE,TEL,PASS,LASTNAME\n1987-02-24T00:00:00,1987KSE,busuxscsix1023@outlook.com,K289PKKWX6I5,0006 23.444 8001,B_0r,Karaman
Output: [["1987-02-24T00:00:00","private_date"],["1987KSE","private_person"],["busuxscsix1023@outlook.com","private_email"],["K289PKKWX6I5","account_number"],["0006 23.444 8001","private_phone"],["B_0r","secret"],["Karaman","private_person"]]

Input: Name: Vrouw; Email: Vrouw@mail.com; Gender: Vrouw
Output: [["Vrouw","private_person"],["Vrouw@mail.com","private_email"],["Vrouw","other_pii"]]

Input: Hi, I'm Daniel Whitfield. Email daniels@meridiancap.com or call 415-555-0123.
Output: [["Daniel Whitfield","private_person"],["daniels@meridiancap.com","private_email"],["415-555-0123","private_phone"]]

Input: País: US; Dirección: 927, Calle: Shaft Road, Ciudad: Wawarsing, Estado: NY, Código Postal: 12446; Nombre: Úrsula (00477097062)
Output: [["US","private_address"],["927","private_address"],["Shaft Road","private_address"],["Wawarsing","private_address"],["NY","private_address"],["12446","private_address"],["00477097062","account_number"]]

Input: Date: [CURRENT_DATE]; Title: [Madame]; Born: [juin/47]; ID: [5716022019873]; School: [UNIVERSITY_NAME]
Output: [["Madame","private_person"],["juin/47","private_date"],["5716022019873","account_number"]]

Input: The university reviewed the application and scheduled a general discussion.
Output: []
```

</details>

<details>
<summary><code>specs/pii-detector-typed-v7.txt</code> — SHA-256 <code>e7df315d3e5e0c4bf9a75ab10787326c6a41a0cd99a202a3a1c8b2b2ade34974</code></summary>

```text
Extract every AI4Privacy-style PII value from the input and assign its nine-way type. Return ONLY a valid compact JSON array of [text,type] pairs, or [] when there is no PII. In each pair, text must be an exact substring copied from the input and type must be exactly one of private_person, private_email, private_phone, private_address, private_url, private_date, account_number, secret, or other_pii. Never use or copy any other type name, including source field names with suffixes. No objects, explanations, labels outside the pairs, or surrounding text. Never combine separate source fields into one text value.

Type mapping:
- private_person: given name, surname, full personal name, personal title, or username.
- private_email: email address.
- private_phone: telephone or fax number.
- private_address: building number, street, city, state/province, postcode, country, apartment/secondary address, or geographic coordinates.
- private_url: personal/private URL or any IPv4/IPv6 address.
- private_date: birth date, other personal date, or time.
- account_number: ID card, passport, driver's license, social number, bank/card/customer/order/account identifier.
- secret: password, PIN, passcode, API key, authentication token, or secret.
- other_pii: sex/gender value or PII not covered above.

Follow the source field and record structure, not a subjective sensitivity judgment or the visual shape alone. A username is private_person and an IP address is private_url. A numeric password is secret, while a random-looking passport/license/ID/account value is account_number. A sex/gender field is other_pii. Extract short values such as M, F, GB, NL, ENG, 13, 163, Dr, Ms, or a three-letter ID when context identifies a PII field. Fields and prose may be English, Dutch, French, German, Italian, or Spanish. Inputs may be prose, JSON, XML, Markdown, YAML, forms, tables, lists, messages, or fragments.

Important patterns:
- Extract dates and times in labeled fields, schedules, appointments, deadlines, or phrases like "from the date ..." in any of the six languages.
- Usernames can be random letters/digits, dotted names, initials, bracketed values, or identifiers before a colon in a participant/message list.
- Bracketed personal values are PII, but generic template placeholders containing underscores such as [CURRENT_DATE], [UNIVERSITY_NAME], [YOUR_NAME], and [FIELD_OF_STUDY] are not.
- Split each address component into its own private_address pair. Do not merge a building, street, city, state, country, or postcode.
- When a name is followed by an ID in parentheses, separate them and assign account_number to the ID.
- Ignore an incomplete value cut off at the very start or end. Never guess, complete, translate, or normalize text; copy it exactly.
- Do not extract organization names, universities, medical conditions, ordinary topics, or generic role descriptions unless explicitly one of the listed personal fields.

Input: Hi, I'm Daniel Whitfield. Email daniels@meridiancap.com or call 415-555-0123.
Output: [["Daniel Whitfield","private_person"],["daniels@meridiancap.com","private_email"],["415-555-0123","private_phone"]]

Input: - Meeting at 2:33 PM\n- N23 - Meeting at 11:29pm\n- wennmann27 - Meeting at 4:45 PM
Output: [["2:33 PM","private_date"],["N23","private_person"],["11:29pm","private_date"],["wennmann27","private_person"],["4:45 PM","private_date"]]

Input: Beste deelnemers:\n- **JVT:** welkom.\n- **BYH:** bedankt.\nDatum: 2040-05-07T00:00:00
Output: [["JVT","private_person"],["BYH","private_person"],["2040-05-07T00:00:00","private_date"]]

Input: Geachte [20amara]. [Minister]: welkom. Background(augustus/39)
Output: [["20amara","private_person"],["Minister","private_person"],["augustus/39","private_date"]]

Input: País: US; Dirección: 927, Calle: Shaft Road, Ciudad: Wawarsing, Estado: NY, Código Postal: 12446; Nombre: Úrsula (00477097062)
Output: [["US","private_address"],["927","private_address"],["Shaft Road","private_address"],["Wawarsing","private_address"],["NY","private_address"],["12446","private_address"],["00477097062","account_number"]]

Input: Profile URL: https://portal.example/u/maya; IP: 192.168.1.8; PIN: 4821; Sex: F
Output: [["https://portal.example/u/maya","private_url"],["192.168.1.8","private_url"],["4821","secret"],["F","other_pii"]]

Input: {"DRIVERLICENSE_A":"AR6ZOGUIQLB","LASTNAME1_A":"Valverde","PASSPORT_B":"U73K2612E","TIME_BG":"3h","DATE_BG":"augustus 6e, 2015"}
Output: [["AR6ZOGUIQLB","account_number"],["Valverde","private_person"],["U73K2612E","account_number"],["3h","private_date"],["augustus 6e, 2015","private_date"]]

Input: Führerschein: C6.27.SPSVM67.4\nPass: P88W6668O\nPasswort: d.20GBm!3!
Output: [["C6.27.SPSVM67.4","account_number"],["P88W6668O","account_number"],["d.20GBm!3!","secret"]]

Input: Codice Fiscale: Bor Rot 24 D 56 0 CSO\nCarta d'Identità: UML711382U\nPassword: lx6QKu9}n2]
Output: [["Bor Rot 24 D 56 0 CSO","account_number"],["UML711382U","account_number"],["lx6QKu9}n2]","secret"]]

Input: Date: [CURRENT_DATE]; Title: [Madame]; Born: [juin/47]; ID: [5716022019873]; School: [UNIVERSITY_NAME]
Output: [["Madame","private_person"],["juin/47","private_date"],["5716022019873","account_number"]]

Input: The university reviewed the application and scheduled a general discussion.
Output: []
```

</details>

<details>
<summary><code>specs/pii-detector-typed-v8.txt</code> — SHA-256 <code>99ea5102b2e174539cf0fe00d9ace2e52ca39b48394b0d93acc0be460abbb2d3</code></summary>

```text
Extract every AI4Privacy-style PII value from the input and assign its nine-way type. Return ONLY a valid compact JSON array of [text,type] pairs, or [] when there is no PII. In each pair, text must be an exact substring copied from the input and type must be exactly one of private_person, private_email, private_phone, private_address, private_url, private_date, account_number, secret, or other_pii. Never use or copy any other type name, including source field names with suffixes. No objects, explanations, labels outside the pairs, or surrounding text. Never combine separate source fields into one text value.

Type mapping:
- private_person: given name, surname, full personal name, personal title, or username.
- private_email: email address.
- private_phone: telephone or fax number.
- private_address: building number, street, city, state/province, postcode, country, apartment/secondary address, or geographic coordinates.
- private_url: personal/private URL or any IPv4/IPv6 address.
- private_date: birth date, other personal date, or time.
- account_number: ID card, passport, driver's license, social number, bank/card/customer/order/account identifier.
- secret: password, PIN, passcode, API key, authentication token, or secret.
- other_pii: sex/gender value or PII not covered above.

Follow the source field and record structure, not a subjective sensitivity judgment or the visual shape alone. A username is private_person and an IP address is private_url. A numeric password is secret, while a random-looking passport/license/ID/account value is account_number. A sex/gender field is other_pii. Extract short values such as M, F, GB, NL, ENG, 13, 163, Dr, Ms, or a three-letter ID when context identifies a PII field. Fields and prose may be English, Dutch, French, German, Italian, or Spanish. Inputs may be prose, JSON, XML, Markdown, YAML, forms, tables, lists, messages, or fragments.

Important patterns:
- Extract dates and times in labeled fields, schedules, appointments, deadlines, or phrases like "from the date ..." in any of the six languages.
- Usernames can be random letters/digits, dotted names, initials, bracketed values, or identifiers before a colon in a participant/message list.
- Bracketed personal values are PII, but generic template placeholders containing underscores such as [CURRENT_DATE], [UNIVERSITY_NAME], [YOUR_NAME], and [FIELD_OF_STUDY] are not.
- Split each address component into its own private_address pair. Do not merge a building, street, city, state, country, or postcode.
- When a name is followed by an ID in parentheses, separate them and assign account_number to the ID.
- Ignore an incomplete value cut off at the very start or end. Never guess, complete, translate, or normalize text; copy it exactly.
- Do not extract organization names, universities, medical conditions, ordinary topics, or generic role descriptions unless explicitly one of the listed personal fields.

Input: Hi, I'm Daniel Whitfield. Email daniels@meridiancap.com or call 415-555-0123.
Output: [["Daniel Whitfield","private_person"],["daniels@meridiancap.com","private_email"],["415-555-0123","private_phone"]]

Input: - Meeting at 2:33 PM\n- N23 - Meeting at 11:29pm\n- wennmann27 - Meeting at 4:45 PM
Output: [["2:33 PM","private_date"],["N23","private_person"],["11:29pm","private_date"],["wennmann27","private_person"],["4:45 PM","private_date"]]

Input: Beste deelnemers:\n- **JVT:** welkom.\n- **BYH:** bedankt.\nDatum: 2040-05-07T00:00:00
Output: [["JVT","private_person"],["BYH","private_person"],["2040-05-07T00:00:00","private_date"]]

Input: Geachte [20amara]. [Minister]: welkom. Background(augustus/39)
Output: [["20amara","private_person"],["Minister","private_person"],["augustus/39","private_date"]]

Input: País: US; Dirección: 927, Calle: Shaft Road, Ciudad: Wawarsing, Estado: NY, Código Postal: 12446; Nombre: Úrsula (00477097062)
Output: [["US","private_address"],["927","private_address"],["Shaft Road","private_address"],["Wawarsing","private_address"],["NY","private_address"],["12446","private_address"],["00477097062","account_number"]]

Input: Profile URL: https://portal.example/u/maya; IP: 192.168.1.8; PIN: 4821; Sex: F
Output: [["https://portal.example/u/maya","private_url"],["192.168.1.8","private_url"],["4821","secret"],["F","other_pii"]]

Input: {"DRIVERLICENSE_A":"AR6ZOGUIQLB","LASTNAME1_A":"Valverde","PASSPORT_B":"U73K2612E","TIME_BG":"3h","DATE_BG":"augustus 6e, 2015"}
Output: [["AR6ZOGUIQLB","account_number"],["Valverde","private_person"],["U73K2612E","account_number"],["3h","private_date"],["augustus 6e, 2015","private_date"]]

Input: Führerschein: C6.27.SPSVM67.4\nPass: P88W6668O\nPasswort: d.20GBm!3!
Output: [["C6.27.SPSVM67.4","account_number"],["P88W6668O","account_number"],["d.20GBm!3!","secret"]]

Input: Codice Fiscale: Bor Rot 24 D 56 0 CSO\nCarta d'Identità: UML711382U\nPassword: lx6QKu9}n2]
Output: [["Bor Rot 24 D 56 0 CSO","account_number"],["UML711382U","account_number"],["lx6QKu9}n2]","secret"]]

Input: 2-60-03-76248-281-75,67.176.53.168...2.53.06.25467.868.33,126.207.172.140...[47.4, -1.59551]...00:08:32
Output: [["2-60-03-76248-281-75","account_number"],["67.176.53.168","private_url"],["2.53.06.25467.868.33","account_number"],["126.207.172.140","private_url"],["[47.4, -1.59551]","private_address"],["00:08:32","private_date"]]

Input: **Candidat Henri**\n- Écuyer\n- Q0121990\n**Candidat Isabelle**\n- Duchesse\n- T1904358317741
Output: [["Écuyer","private_person"],["Q0121990","account_number"],["Duchesse","private_person"],["T1904358317741","account_number"]]

Input: Weitere Bewerber:\n- W68O4084J\n- C99W5481I\n- R58H7016C\nHintergrundinformationen:\nUhrzeit: 2h\nGebäude: 101
Output: [["W68O4084J","account_number"],["C99W5481I","account_number"],["R58H7016C","account_number"],["2h","private_date"],["101","private_address"]]

Input: Date: [CURRENT_DATE]; Title: [Madame]; Born: [juin/47]; ID: [5716022019873]; School: [UNIVERSITY_NAME]
Output: [["Madame","private_person"],["juin/47","private_date"],["5716022019873","account_number"]]

Input: The university reviewed the application and scheduled a general discussion.
Output: []
```

</details>

<details>
<summary><code>specs/pii-detector-typed-v9.txt</code> — SHA-256 <code>704dac3ff66198ff5e41b639888d2dc31441cc3d0acf097c839fdbf6d5470e8b</code></summary>

```text
Extract every AI4Privacy-style PII value from the input and assign its nine-way type. Return ONLY a valid compact JSON array of [text,type] pairs, or [] when there is no PII. In each pair, text must be an exact substring copied from the input and type must be exactly one of private_person, private_email, private_phone, private_address, private_url, private_date, account_number, secret, or other_pii. Never use or copy any other type name, including source field names with suffixes. No objects, explanations, labels outside the pairs, or surrounding text. Never combine separate source fields into one text value.

Type mapping:
- private_person: given name, surname, full personal name, personal title, or username.
- private_email: email address.
- private_phone: telephone or fax number.
- private_address: building number, street, city, state/province, postcode, country, apartment/secondary address, or geographic coordinates.
- private_url: personal/private URL or any IPv4/IPv6 address.
- private_date: birth date, other personal date, or time.
- account_number: ID card, passport, driver's license, social number, bank/card/customer/order/account identifier.
- secret: password, PIN, passcode, API key, authentication token, or secret.
- other_pii: sex/gender value or PII not covered above.

Follow the source field and record structure, not a subjective sensitivity judgment or the visual shape alone. A username is private_person and an IP address is private_url. A numeric password is secret, while a random-looking passport/license/ID/account value is account_number. A sex/gender field is other_pii. Extract short values such as M, F, GB, NL, ENG, 13, 163, Dr, Ms, or a three-letter ID when context identifies a PII field. Fields and prose may be English, Dutch, French, German, Italian, or Spanish. Inputs may be prose, JSON, XML, Markdown, YAML, forms, tables, lists, messages, or fragments.

Important patterns:
- Extract dates and times in labeled fields, schedules, appointments, deadlines, or phrases like "from the date ..." in any of the six languages.
- Usernames can be random letters/digits, dotted names, initials, bracketed values, or identifiers before a colon in a participant/message list.
- Bracketed personal values are PII, but generic template placeholders containing underscores such as [CURRENT_DATE], [UNIVERSITY_NAME], [YOUR_NAME], and [FIELD_OF_STUDY] are not.
- Split each address component into its own private_address pair. Do not merge a building, street, city, state, country, or postcode.
- When a name is followed by an ID in parentheses, separate them and assign account_number to the ID.
- Ignore an incomplete value cut off at the very start or end. Never guess, complete, translate, or normalize text; copy it exactly.
- Do not extract organization names, universities, medical conditions, ordinary topics, or generic role descriptions unless explicitly one of the listed personal fields.

Input: Hi, I'm Daniel Whitfield. Email daniels@meridiancap.com or call 415-555-0123.
Output: [["Daniel Whitfield","private_person"],["daniels@meridiancap.com","private_email"],["415-555-0123","private_phone"]]

Input: - Meeting at 2:33 PM\n- N23 - Meeting at 11:29pm\n- wennmann27 - Meeting at 4:45 PM
Output: [["2:33 PM","private_date"],["N23","private_person"],["11:29pm","private_date"],["wennmann27","private_person"],["4:45 PM","private_date"]]

Input: Beste deelnemers:\n- **JVT:** welkom.\n- **BYH:** bedankt.\nDatum: 2040-05-07T00:00:00
Output: [["JVT","private_person"],["BYH","private_person"],["2040-05-07T00:00:00","private_date"]]

Input: Geachte [20amara]. [Minister]: welkom. Background(augustus/39)
Output: [["20amara","private_person"],["Minister","private_person"],["augustus/39","private_date"]]

Input: País: US; Dirección: 927, Calle: Shaft Road, Ciudad: Wawarsing, Estado: NY, Código Postal: 12446; Nombre: Úrsula (00477097062)
Output: [["US","private_address"],["927","private_address"],["Shaft Road","private_address"],["Wawarsing","private_address"],["NY","private_address"],["12446","private_address"],["00477097062","account_number"]]

Input: Profile URL: https://portal.example/u/maya; IP: 192.168.1.8; PIN: 4821; Sex: F
Output: [["https://portal.example/u/maya","private_url"],["192.168.1.8","private_url"],["4821","secret"],["F","other_pii"]]

Input: {"DRIVERLICENSE_A":"AR6ZOGUIQLB","LASTNAME1_A":"Valverde","PASSPORT_B":"U73K2612E","TIME_BG":"3h","DATE_BG":"augustus 6e, 2015"}
Output: [["AR6ZOGUIQLB","account_number"],["Valverde","private_person"],["U73K2612E","account_number"],["3h","private_date"],["augustus 6e, 2015","private_date"]]

Input: Führerschein: C6.27.SPSVM67.4\nPass: P88W6668O\nPasswort: d.20GBm!3!
Output: [["C6.27.SPSVM67.4","account_number"],["P88W6668O","account_number"],["d.20GBm!3!","secret"]]

Input: Codice Fiscale: Bor Rot 24 D 56 0 CSO\nCarta d'Identità: UML711382U\nPassword: lx6QKu9}n2]
Output: [["Bor Rot 24 D 56 0 CSO","account_number"],["UML711382U","account_number"],["lx6QKu9}n2]","secret"]]

Input: **Candidat Henri**\n- Écuyer\n- Q0121990\n**Candidat Isabelle**\n- Duchesse\n- T1904358317741
Output: [["Écuyer","private_person"],["Q0121990","account_number"],["Duchesse","private_person"],["T1904358317741","account_number"]]

Input: Weitere Bewerber:\n- W68O4084J\n- C99W5481I\n- R58H7016C\nHintergrundinformationen:\nUhrzeit: 2h\nGebäude: 101
Output: [["W68O4084J","account_number"],["C99W5481I","account_number"],["R58H7016C","account_number"],["2h","private_date"],["101","private_address"]]

Input: Date: [CURRENT_DATE]; Title: [Madame]; Born: [juin/47]; ID: [5716022019873]; School: [UNIVERSITY_NAME]
Output: [["Madame","private_person"],["juin/47","private_date"],["5716022019873","account_number"]]

Input: The university reviewed the application and scheduled a general discussion.
Output: []
```

</details>

<details>
<summary><code>specs/pii-detector-v1.txt</code> — SHA-256 <code>d7a09102aac80e67ff41c45d73399a7a7e1aab5ffc83f81e85459bf08f9c585a</code></summary>

```text
Extract every substring in the input that is private, personal, identifying, contact, account, location, or secret information. Return ONLY a valid JSON array of strings. Copy each string exactly from the input, with identical spelling, accents, spacing, and punctuation inside the value. Return [] when there is no PII. Do not explain the answer. Do not include field labels or surrounding prose.

Include all values in these groups:
- A person's identity: full or partial names, initials, titles attached to a name, aliases, usernames, handles, customer or employee identities.
- Contact and online identity: email, phone, fax, URL, IP address, MAC address, social profile, hostname, and device identifiers.
- Government, financial, medical, vehicle, and account identifiers: social numbers, passports, national IDs, driver's licenses, tax IDs, bank accounts, cards, routing codes, insurance numbers, license plates, serial numbers.
- Credentials and secrets: passwords, PINs, API keys, tokens, access codes, cryptographic keys, and security answers.
- Personal location: street, building number, apartment, postcode, city, county, state or province, country, GPS coordinates, and complete addresses.
- Personal facts that identify or distinguish someone: birth date, any date or time recorded in a person's file, age, gender, nationality, job, employer, education, and similar structured-record values.

When text is formatted as a form, record, table, profile, application, account, or message, treat the value after a PII-like field label as PII even when the value is short or unusual. Extract the value, not the label. Prefer one complete span per value instead of splitting it into pieces.

Input: Hi, I'm Daniel Whitfield. Email daniels@meridiancap.com or call 415-555-0123.
Output: ["Daniel Whitfield","daniels@meridiancap.com","415-555-0123"]

Input: Applicant: Zoë García | Passport: XG 440-19 | Country: Spain | Password: r]iD1#8
Output: ["Zoë García","XG 440-19","Spain","r]iD1#8"]

Input: The release is scheduled after the final review. No user details are present.
Output: []
```

</details>

<details>
<summary><code>specs/pii-detector-v2.txt</code> — SHA-256 <code>416e8b966eb4c0d0ce4fe888d7fc9edcd67fee7aed5c18d94b659264efc25bc7</code></summary>

```text
Extract every PII field value from the input. This task follows the ai4privacy PII-masking definition: a value counts because it belongs to a listed field, even if it looks harmless or would not be sensitive by itself.

Return ONLY a valid JSON array of strings. Copy every value exactly from the input, preserving accents, case, spaces, and punctuation inside that value. Return [] if none are present. Do not explain. Each array item must contain one value only. Never combine several fields, include a field name, include a colon, or copy surrounding prose. Real line breaks and the two visible characters backslash+n both separate fields and must not be copied into a value.

Extract values belonging to ALL of these field types:
- BOD or birth date; DATE; TIME.
- BUILDING number; STREET; CITY; STATE or province; POSTCODE; COUNTRY; secondary address or apartment; geographic coordinates.
- GIVEN NAME, LAST NAME, full name, TITLE, SEX.
- USERNAME, login, alias, handle.
- EMAIL, telephone or fax, IP address.
- ID card, passport, driver's license, social-security or social number.
- Password, PIN, secret, API key, token.
- Bank/card/account identifier or card issuer.

Field labels may be English, Dutch, French, German, Italian, or Spanish, and may appear in JSON, XML, Markdown, tables, lists, forms, profiles, messages, or fragments cut from a longer record. Recognize common translated labels such as naam/nom/name/nome/nombre, datum/date/data/fecha, tijd/heure/Zeit/ora/hora, adres/adresse/indirizzo/dirección, land/pays/Land/paese/país, gebruiker or utilisateur or Benutzer or utente or usuario, and wachtwoord or mot de passe or Passwort or password or contraseña.

Important benchmark rules:
- Extract every date and time that is presented as a record value, meeting time, appointment time, deadline, or background date.
- Extract short values such as M, F, GB, NL, ENG, 13, 163, Dr, Ms, Mw, or an all-capital three-letter ID when their field or record context indicates one of the listed types.
- A username can look like a name, random letters, digits, initials, or text inside brackets. In a schedule like "user17 - Meeting at 9:45", both the username and time are values.
- Keep a compound address component together, but return separate address fields separately when labels or delimiters separate them.
- Do not extract organization names, universities, medical conditions, ordinary topics, generic role descriptions, or unlabeled prose unless they are themselves one of the listed values.

Input: Hi, I'm Daniel Whitfield. Email daniels@meridiancap.com or call 415-555-0123.
Output: ["Daniel Whitfield","daniels@meridiancap.com","415-555-0123"]

Input: user17 - Meeting at 9:45 PM; kpeters88 - Meeting at 13
Output: ["user17","9:45 PM","kpeters88","13"]

Input: Tijd: 4:50\\nPostcode: 5575 XP\\nDatum: 30/10/1998\\nLand: NL
Output: ["4:50","5575 XP","30/10/1998","NL"]

Input: <Title>Mw</Title><Username>20amara</Username><Sex>F</Sex><Building>945</Building>
Output: ["Mw","20amara","F","945"]

Input: The university reviewed the application and scheduled a general discussion.
Output: []
```

</details>

<details>
<summary><code>specs/pii-detector-v3.txt</code> — SHA-256 <code>5d79d565fc462be15c82bffebfe00ef34480690df52498564cac8fd34f1a0be1</code></summary>

```text
Extract all ai4privacy-style PII values from the input. Return ONLY a valid JSON array of exact substrings copied from the input. Return [] if there are none. No explanation, labels, or surrounding text. One value per array item: never combine multiple fields or include the colon/field name between them.

The PII field types are: birth date, date, time, building number, street, city, state/province, postcode, country, secondary address/apartment, geographic coordinates, given name, surname, full name, personal title, sex, username, email, telephone/fax, IP address, ID card, passport, driver's license, social number, password/PIN/secret/token, bank/card/account ID, and card issuer.

Follow the field structure, not a subjective sensitivity judgment. Extract short or ordinary-looking values such as M, F, GB, NL, ENG, 13, 163, Dr, Ms, or a three-letter ID when their context identifies a listed field. Labels may be English, Dutch, French, German, Italian, or Spanish. Inputs may be prose, JSON, XML, Markdown, YAML, forms, tables, lists, messages, or fragments. A real line break or visible backslash+n can separate fields.

Important patterns:
- Extract dates and times in labeled fields, schedules, appointments, deadlines, or phrases like "from the date ..." in any of the six languages.
- Usernames can be random letters/digits, dotted names, initials, bracketed values, or identifiers before a colon in a participant/message list.
- Bracketed personal values are still PII. But do not extract generic template placeholders containing an underscore, such as [CURRENT_DATE], [UNIVERSITY_NAME], [YOUR_NAME], or [FIELD_OF_STUDY].
- In an address record, split every labeled component: a value like "927, Calle: Shaft Road, Ciudad: Wawarsing, Estado: NY" must become "927", "Shaft Road", "Wawarsing", "NY" rather than one long item.
- When a name is followed by an ID in parentheses, separate them. Extract the name only when the dataset explicitly treats it as a personal name; always extract the parenthesized ID.
- Ignore an incomplete value cut off at the very start or end of the input. Do not guess, complete, or translate a value. Copy source text exactly.
- Do not extract organization names, universities, medical conditions, ordinary topics, or generic role descriptions unless explicitly one of the listed personal fields.

Input: Hi, I'm Daniel Whitfield. Email daniels@meridiancap.com or call 415-555-0123.
Output: ["Daniel Whitfield","daniels@meridiancap.com","415-555-0123"]

Input: - Meeting at 2:33 PM\n- N23 - Meeting at 11:29pm\n- wennmann27 - Meeting at 4:45 PM
Output: ["2:33 PM","N23","11:29pm","wennmann27","4:45 PM"]

Input: Beste deelnemers:\n- **JVT:** welkom.\n- **BYH:** bedankt.\nDatum: 2040-05-07T00:00:00
Output: ["JVT","BYH","2040-05-07T00:00:00"]

Input: Geachte [20amara]. [Minister]: welkom. Background(augustus/39)
Output: ["20amara","Minister","augustus/39"]

Input: País: US; Dirección: 927, Calle: Shaft Road, Ciudad: Wawarsing, Estado: NY, Código Postal: 12446; Nombre: Úrsula (00477097062)
Output: ["US","927","Shaft Road","Wawarsing","NY","12446","00477097062"]

Input: Date: [CURRENT_DATE]; Title: [Madame]; Born: [juin/47]; ID: [5716022019873]; School: [UNIVERSITY_NAME]
Output: ["Madame","juin/47","5716022019873"]

Input: The university reviewed the application and scheduled a general discussion.
Output: []
```

</details>

<details>
<summary><code>specs/pii-detector-v4.txt</code> — SHA-256 <code>057fcec2d57c4c5b2236f8ddceece79134472290c18ebc6f4ca6798000009722</code></summary>

```text
Reproduce the AI4Privacy PII annotations in the input. Return ONLY a valid JSON array of exact substrings copied from the input, or [] when none are annotated. Return every annotated value through the final character of the input, including dense and repeated records. Never return a representative subset. Use one array item per field; never merge adjacent fields. Every returned string must occur literally in the input: preserve spelling, accents, punctuation, brackets, and capitalization, and never translate or normalize it.

The annotation fields are BOD/birth date, DATE, TIME, BUILDING, STREET, CITY, STATE/province, POSTCODE, COUNTRY, SECADDRESS/apartment, GEOCOORD, GIVENNAME, LASTNAME, full personal name, TITLE, SEX/gender, USERNAME, EMAIL, TEL/fax, IP, IDCARD, PASSPORT, DRIVERLICENSE, SOCIALNUMBER, PASS/password/PIN/secret/token, bank/card/account ID, and card issuer.

Use the record structure rather than subjective sensitivity. Field names and surrounding prose may be English, Dutch, French, German, Italian, or Spanish. Inputs may be prose, JSON, XML, HTML, Markdown, YAML, tables, fragments, or delimiter-only records. Short ordinary values such as M, F, H, GB, NL, IT, ENG, 13, 163, Dr, Mme, or a three-letter ID are annotations when their field or repeating column identifies them.

Rules:
- Scan to the end. In repeated records, infer the column pattern from the first complete record and extract every corresponding value from later records.
- Separators such as ..., &, commas, pipes, colons, newlines, and visible backslash+n often divide fields. Split values at those separators unless punctuation belongs inside the value, such as an email, IPv6 address, password, coordinate pair, or formatted identifier.
- Extract every email, telephone/fax number, IPv4/IPv6 address, credential, social number, personal ID, passport, driver's license, and username in dense machine-generated sequences.
- Extract dates and times in labeled fields, schedules, appointments, deadlines, signatures, and phrases such as "Fait le", "a partire dalla data", or "from the date". Preserve localized month spelling. A bare hour such as 2, 3h, 4h, or 5 can be TIME when it occupies a recurring time field.
- Extract every component of an address record separately, including short countries, building numbers, streets, cities, states, postcodes, secondary addresses, and surnames. A repeated unlabeled row may encode telephone, country, building, street, city, state, postcode, secondary address, surname in that order.
- Extract uncommon personal titles when they occupy a title field or a title-and-ID list, including Écuyer, Duchesse, Général, Prince, Dame, Baron, Sœur, Abbé, Infant, Meneer, and Mevrouw. Do not mistake a nearby "Candidat Name" heading for an annotated name when only its following title and ID are fields.
- Extract sex/gender field values including single letters and localized words. Extract passwords with all punctuation that belongs to the value, including a leading quote if the source value begins with one.
- Bracketed personal values are annotations, but generic template placeholders containing underscores such as [CURRENT_DATE], [UNIVERSITY_NAME], [YOUR_NAME], and [FIELD_OF_STUDY] are not.
- Do not output institutions, organizations, project/course/activity names, ordinary prose, generic participant labels, or grammatical perspective descriptions such as "Perspective du Troisième Personne Pluriel" or "Tercera Persona Singular".
- A complete value at a chunk boundary is valid. Ignore only a visibly severed fragment that cannot be identified. Do not guess missing characters.

Input: tfjasta87868@gmail.com...2.49.03.19524.337.91...B@tutanota.com...278-32-5098...[46.63, -0.7]
Output: ["tfjasta87868@gmail.com","2.49.03.19524.337.91","B@tutanota.com","278-32-5098","[46.63, -0.7]"]

Input: - id(1) - 084.910-0987, Nederland, 770, Tiendweg, Lopik, UT, 3411, Kamenova\n- id(2) - +26.82 907.1047, NL, 414, Bruininxdeelse Kade, Leerdam, ZH, 4143 LM, Section 740, Krane
Output: ["084.910-0987","Nederland","770","Tiendweg","Lopik","UT","3411","Kamenova","+26.82 907.1047","NL","414","Bruininxdeelse Kade","Leerdam","ZH","4143 LM","Section 740","Krane"]

Input: **Candidat Henri**\n- Écuyer\n- Q0121990\n**Candidat Isabelle**\n- Duchesse\n- T1904358317741
Output: ["Écuyer","Q0121990","Duchesse","T1904358317741"]

Input: Date: 2023-12-17T00:00:00\nHeure: 6:24\nBâtiment: 75\nParticipants: Perspective du Troisième Personne Pluriel Ensemble II
Output: ["2023-12-17T00:00:00","6:24","75"]

Input: Fait le septembre 28, 2026. Mot de passe : "t50C\nHeure de connexion : 5
Output: ["septembre 28, 2026","\"t50C","5"]

Input: Date: [CURRENT_DATE]; Title: [Madame]; Born: [juin/47]; ID: [5716022019873]; School: [UNIVERSITY_NAME]
Output: ["Madame","juin/47","5716022019873"]

Input: The university reviewed a strategic plan for virtual reality integration and invited generic participant groups.
Output: []
```

</details>

<details>
<summary><code>specs/pii-detector-v5.txt</code> — SHA-256 <code>bb77b78b086b92829c18d08d8336d40ca7ba162d7121df62e0113fddbce90911</code></summary>

```text
Extract all ai4privacy-style PII values from the input. Return ONLY a valid JSON array of exact substrings copied from the input. Return [] if there are none. No explanation, labels, or surrounding text. One value per array item: never combine multiple fields or include the colon/field name between them. Copy literally: never translate, normalize, correct, or drop punctuation from a value.

The PII field types are: birth date, date, time, building number, street, city, state/province, postcode, country, secondary address/apartment, geographic coordinates, given name, surname, full name, personal title, sex, username, email, telephone/fax, IP address, ID card, passport, driver's license, social number, password/PIN/secret/token, bank/card/account ID, and card issuer.

Follow the field structure, not a subjective sensitivity judgment. Extract short or ordinary-looking values such as M, F, H, GB, NL, ENG, 13, 163, Dr, Ms, or a three-letter ID when their context identifies a listed field. Labels may be English, Dutch, French, German, Italian, or Spanish. Inputs may be prose, JSON, XML, HTML, Markdown, YAML, forms, tables, lists, messages, fragments, or delimiter-only records. A real line break or visible backslash+n can separate fields.

Important patterns:
- Continue through the entire input and return every PII value, not merely the first values or a representative subset. In repeated records, infer the schema from a complete record and apply it to every later record.
- Separators such as ..., &, commas, pipes, colons, and newlines can divide dense fields. Do not merge neighboring values across a separator.
- Extract dates and times in labeled fields, schedules, appointments, deadlines, or phrases like "from the date ..." in any of the six languages. A bare number or number plus h can be a time in a time field.
- Usernames can be random letters/digits, dotted names, initials, bracketed values, or identifiers before a colon in a participant/message list.
- Bracketed personal values are still PII. But do not extract generic template placeholders containing an underscore, such as [CURRENT_DATE], [UNIVERSITY_NAME], [YOUR_NAME], or [FIELD_OF_STUDY].
- In an address record, split every labeled component. In a repeated unlabeled address row, the recurring order may be telephone, country, building, street, city, state, postcode, secondary address, surname.
- When a name is followed by an ID in parentheses, separate them. Extract the name only when the dataset explicitly treats it as a personal name; always extract the parenthesized ID.
- A complete value at the start or end of a chunk is valid. Ignore only a visibly cut-off fragment that cannot be identified. Do not guess or complete it.
- Do not extract organization names, universities, project/course names, medical conditions, ordinary topics, generic role descriptions, or grammatical perspective phrases such as "Perspective du Troisième Personne Pluriel" and "Tercera Persona Singular" unless explicitly one of the listed personal fields.

Input: Hi, I'm Daniel Whitfield. Email daniels@meridiancap.com or call 415-555-0123.
Output: ["Daniel Whitfield","daniels@meridiancap.com","415-555-0123"]

Input: - Meeting at 2:33 PM\n- N23 - Meeting at 11:29pm\n- wennmann27 - Meeting at 4:45 PM
Output: ["2:33 PM","N23","11:29pm","wennmann27","4:45 PM"]

Input: tfjasta87868@gmail.com...2.49.03.19524.337.91...B@tutanota.com...278-32-5098...[46.63, -0.7]
Output: ["tfjasta87868@gmail.com","2.49.03.19524.337.91","B@tutanota.com","278-32-5098","[46.63, -0.7]"]

Input: Beste deelnemers:\n- **JVT:** welkom.\n- **BYH:** bedankt.\nDatum: 2040-05-07T00:00:00
Output: ["JVT","BYH","2040-05-07T00:00:00"]

Input: Geachte [20amara]. [Minister]: welkom. Background(augustus/39)
Output: ["20amara","Minister","augustus/39"]

Input: País: US; Dirección: 927, Calle: Shaft Road, Ciudad: Wawarsing, Estado: NY, Código Postal: 12446; Nombre: Úrsula (00477097062)
Output: ["US","927","Shaft Road","Wawarsing","NY","12446","00477097062"]

Input: Date: 2023-12-17T00:00:00\nHeure: 6:24\nBâtiment: 75\nParticipants: Perspective du Troisième Personne Pluriel Ensemble II
Output: ["2023-12-17T00:00:00","6:24","75"]

Input: Date: [CURRENT_DATE]; Title: [Madame]; Born: [juin/47]; ID: [5716022019873]; School: [UNIVERSITY_NAME]
Output: ["Madame","juin/47","5716022019873"]

Input: The university reviewed the application and scheduled a general discussion.
Output: []
```

</details>

<details>
<summary><code>specs/pii-detector-v6.txt</code> — SHA-256 <code>61d01ac6786651cac71ed91648785fbd91253955ea69108bcc1d66a7353e4c4f</code></summary>

```text
Extract all AI4Privacy-style PII values from the input. Return ONLY a valid JSON array of exact substrings copied from the input, or [] if there are none. No explanation, labels, or surrounding text. One array item per field: never combine adjacent fields. Every returned item must occur literally in the source; never translate, normalize, correct, or invent text.

PII fields are birth date, date, time, building number, street, city, state/province, postcode, country, secondary address/apartment, geographic coordinates, given name, surname, full personal name, personal title, sex, username, email, telephone/fax, IP address, ID card, passport, driver's license, social number, password/PIN/secret/token, bank/card/account ID, and card issuer.

Follow explicit fields and repeating record structure, not a subjective sensitivity judgment. Extract short ordinary-looking values such as M, F, H, GB, NL, ENG, 13, 163, Dr, Ms, or a three-letter ID when a field or column identifies them. Text and field names may be English, Dutch, French, German, Italian, or Spanish. Inputs may be prose, JSON, XML, HTML, Markdown, YAML, tables, messages, fragments, or dense delimiter-separated records.

Rules:
- Scan through the final character and return every PII value, not a sample. If records repeat, infer the columns from a complete record and process all later records.
- The separators ..., &, comma, pipe, colon, newline, and visible backslash+n can divide fields. Split neighboring fields instead of returning them together.
- Extract dates and times from explicit date/time fields, appointments, deadlines, signatures, and schedules. A bare number or number followed by h can be a time when it fills a time field.
- Usernames can be random letters/digits, dotted names, initials, bracketed values, or identifiers before a colon in a participant list.
- Bracketed personal values are PII, except generic underscore placeholders such as [CURRENT_DATE], [UNIVERSITY_NAME], [YOUR_NAME], and [FIELD_OF_STUDY].
- Split every labeled address component. A repeating unlabeled address row can use telephone, country, building, street, city, state, postcode, secondary address, surname.
- When a name is followed by an ID in parentheses, separate them. Extract the name only when it is an annotated personal-name field; always extract the parenthesized ID.
- Do not return institutions, organizations, project/course/activity names, policy or waiver prose, ordinary topics, generic participant or student labels, grammatical perspective descriptions, or arbitrary sentences. A key or heading alone does not make its value PII.
- A complete value at a chunk boundary remains valid. Ignore only a visibly severed fragment that cannot be identified.

Input: Hi, I'm Daniel Whitfield. Email daniels@meridiancap.com or call 415-555-0123.
Output: ["Daniel Whitfield","daniels@meridiancap.com","415-555-0123"]

Input: tfjasta87868@gmail.com...2.49.03.19524.337.91...B@tutanota.com...278-32-5098...[46.63, -0.7]
Output: ["tfjasta87868@gmail.com","2.49.03.19524.337.91","B@tutanota.com","278-32-5098","[46.63, -0.7]"]

Input: - id(1) - 084.910-0987, Nederland, 770, Tiendweg, Lopik, UT, 3411, Kamenova\n- id(2) - +26.82 907.1047, NL, 414, Bruininxdeelse Kade, Leerdam, ZH, 4143 LM, Section 740, Krane
Output: ["084.910-0987","Nederland","770","Tiendweg","Lopik","UT","3411","Kamenova","+26.82 907.1047","NL","414","Bruininxdeelse Kade","Leerdam","ZH","4143 LM","Section 740","Krane"]

Input: - Meeting at 2:33 PM\n- N23 - Meeting at 11:29pm\n- wennmann27 - Meeting at 4:45 PM
Output: ["2:33 PM","N23","11:29pm","wennmann27","4:45 PM"]

Input: **Candidat Henri**\n- Écuyer\n- Q0121990\n**Candidat Isabelle**\n- Duchesse\n- T1904358317741
Output: ["Écuyer","Q0121990","Duchesse","T1904358317741"]

Input: Date: 2023-12-17T00:00:00\nHeure: 6:24\nBâtiment: 75\nParticipants: Perspective du Troisième Personne Pluriel Ensemble II
Output: ["2023-12-17T00:00:00","6:24","75"]

Input: Date: [CURRENT_DATE]; Title: [Madame]; Born: [juin/47]; ID: [5716022019873]; School: [UNIVERSITY_NAME]
Output: ["Madame","juin/47","5716022019873"]

Input: Strategic_Plan: Piano Strategico per l'Attrazione degli Studenti. Activity_Name: Virtual Reality Integration in Educational Curriculum. Policy: Property damage liability waiver is granted. Participants: Tercera Persona Singular, Set I.
Output: []

Input: The university reviewed the application and scheduled a general discussion.
Output: []
```

</details>

<details>
<summary><code>specs/pii-detector-v8.txt</code> — SHA-256 <code>3cffc79c7a9827b4332b5599011c5d3f6ca8763aa822d4c2dc6a1908bce9cffa</code></summary>

```text
Extract all ai4privacy-style PII values from the input. Return ONLY a valid JSON array of exact substrings copied from the input. Return [] if there are none. No explanation, labels, or surrounding text. One value per array item: never combine multiple fields or include the colon/field name between them.

The PII field types are: birth date, date, time, building number, street, city, state/province, postcode, country, secondary address/apartment, geographic coordinates, given name, surname, full name, personal title, sex, username, email, telephone/fax, IP address, ID card, passport, driver's license, social number, password/PIN/secret/token, bank/card/account ID, and card issuer.

Follow the field structure, not a subjective sensitivity judgment. Extract short or ordinary-looking values such as M, F, GB, NL, ENG, 13, 163, Dr, Ms, or a three-letter ID when their context identifies a listed field. Labels may be English, Dutch, French, German, Italian, or Spanish. Inputs may be prose, JSON, XML, Markdown, YAML, forms, tables, lists, messages, or fragments. A real line break or visible backslash+n can separate fields.

Important patterns:
- Extract dates and times in labeled fields, schedules, appointments, deadlines, or phrases like "from the date ..." in any of the six languages.
- Usernames can be random letters/digits, dotted names, initials, bracketed values, or identifiers before a colon in a participant/message list.
- Bracketed personal values are still PII. But do not extract generic template placeholders containing an underscore, such as [CURRENT_DATE], [UNIVERSITY_NAME], [YOUR_NAME], or [FIELD_OF_STUDY].
- In an address record, split every labeled component: a value like "927, Calle: Shaft Road, Ciudad: Wawarsing, Estado: NY" must become "927", "Shaft Road", "Wawarsing", "NY" rather than one long item.
- When a name is followed by an ID in parentheses, separate them. Extract the name only when the dataset explicitly treats it as a personal name; always extract the parenthesized ID.
- Ignore an incomplete value cut off at the very start or end of the input. Do not guess, complete, or translate a value. Copy source text exactly.
- Do not extract organization names, universities, medical conditions, ordinary topics, or generic role descriptions unless explicitly one of the listed personal fields.

Input: Hi, I'm Daniel Whitfield. Email daniels@meridiancap.com or call 415-555-0123.
Output: ["Daniel Whitfield","daniels@meridiancap.com","415-555-0123"]

Input: - Meeting at 2:33 PM\n- N23 - Meeting at 11:29pm\n- wennmann27 - Meeting at 4:45 PM
Output: ["2:33 PM","N23","11:29pm","wennmann27","4:45 PM"]

Input: Beste deelnemers:\n- **JVT:** welkom.\n- **BYH:** bedankt.\nDatum: 2040-05-07T00:00:00
Output: ["JVT","BYH","2040-05-07T00:00:00"]

Input: Geachte [20amara]. [Minister]: welkom. Background(augustus/39)
Output: ["20amara","Minister","augustus/39"]

Input: País: US; Dirección: 927, Calle: Shaft Road, Ciudad: Wawarsing, Estado: NY, Código Postal: 12446; Nombre: Úrsula (00477097062)
Output: ["US","927","Shaft Road","Wawarsing","NY","12446","00477097062"]

Input: tfjasta87868@gmail.com...2.49.03.19524.337.91...B@tutanota.com...278-32-5098...[46.63, -0.7]
Output: ["tfjasta87868@gmail.com","2.49.03.19524.337.91","B@tutanota.com","278-32-5098","[46.63, -0.7]"]

Input: Date: 2023-12-17T00:00:00\nHeure: 6:24\nBâtiment: 75\nParticipants: Perspective du Troisième Personne Pluriel Ensemble II
Output: ["2023-12-17T00:00:00","6:24","75"]

Input: Date: [CURRENT_DATE]; Title: [Madame]; Born: [juin/47]; ID: [5716022019873]; School: [UNIVERSITY_NAME]
Output: ["Madame","juin/47","5716022019873"]

Input: The university reviewed the application and scheduled a general discussion.
Output: []
```

</details>

<details>
<summary><code>specs/pii-type-classifier-ft-v1.txt</code> — SHA-256 <code>863546c871d721b2e55f65599d4990c13ecf3b82bab721aa381c602b29f82023</code></summary>

```text
Classify the one already-detected PII value enclosed by <PII> and </PII> in its source context. Return exactly one label and nothing else. The only valid labels are private_person, private_email, private_phone, private_address, private_url, private_date, account_number, secret, and other_pii.

Type mapping:
- private_person: given name, surname, full personal name, personal title, or username.
- private_email: email address.
- private_phone: telephone or fax number.
- private_address: building number, street, city, state/province, postcode, country, apartment/secondary address, or geographic coordinates.
- private_url: personal/private URL or any IPv4/IPv6 address.
- private_date: birth date, other personal date, or time.
- account_number: ID card, passport, driver's license, social number, bank/card/customer/order/account identifier.
- secret: password, PIN, passcode, API key, authentication token, or secret.
- other_pii: sex/gender value or PII not covered above.

Use the field label when it is visible. Otherwise infer the repeating local schema from the values immediately before and after <PII>. Do not copy a neighbor's type merely because it is nearby. In alternating dense sequences, recognize each column independently: email is private_email, social or government ID is account_number, IP is private_url, time/date is private_date, username/name/title is private_person, telephone is private_phone, address component is private_address, password is secret, and sex/gender is other_pii. A dotted social number can resemble an IP but has groups or octets outside valid IPv4 structure. A social number can resemble a telephone but is account_number in an email/social-number sequence. A random-looking username is private_person. A numeric password is secret. A random-looking passport/license/ID is account_number, never secret.

Input: Email: <PII>maya@example.com</PII>
Output: private_email

Input: Call <PII>+1 (416) 555-0148</PII> today.
Output: private_phone

Input: Address: <PII>927 Shaft Road</PII>, Wawarsing, NY.
Output: private_address

Input: Coordinates: <PII>[51.9, 5.2147]</PII>
Output: private_address

Input: IP: <PII>192.168.1.8</PII>
Output: private_url

Input: Birth date: <PII>April 12, 1990</PII>
Output: private_date

Input: Passport: <PII>X1234567</PII>
Output: account_number

Input: Password: <PII>?b.6vBl</PII>
Output: secret

Input: Username: <PII>13ritz</PII>
Output: private_person

Input: Título: <PII>Señora</PII>
Output: private_person

Input: Sex: <PII>F</PII>
Output: other_pii

Input: tfjasta87868@gmail.com...<PII>2 57 01 85136 028 30</PII>...B@tutanota.com
Output: account_number

Input: 2-60-03-76248-281-75,<PII>67.176.53.168</PII>...2.53.06.25467.868.33
Output: private_url

Input: 67.176.53.168...<PII>2.53.06.25467.868.33</PII>,126.207.172.140
Output: account_number

Input: 2.53.06.25467.868.33,<PII>126.207.172.140</PII>...2-48-01-24327-318-13
Output: private_url

Input: irfotmpiitecnl380411@protonmail.com&<PII>QCJ320742T</PII>&12:14 - SR@outlook.com
Output: account_number

Input: protonmail.com&QCJ320742T&<PII>12:14</PII> - SR@outlook.com
Output: private_date

Input: juillet/00, 01:12:35, Chemin de l'Étang...<PII>ssiksou</PII>, 2002-07-25T00:00:00
Output: private_person

Input: Chemin de l'Étang...ssiksou, <PII>2002-07-25T00:00:00</PII>...1970bixio.gourlaouen
Output: private_date

Input: 1987-02-24T00:00:00,<PII>1987KSE</PII>,busuxscsix1023@outlook.com,K289PKKWX6I5
Output: private_person

Input: 1987KSE,busuxscsix1023@outlook.com,<PII>K289PKKWX6I5</PII>,0006 23.444 8001,B_0r
Output: account_number

Input: K289PKKWX6I5,<PII>0006 23.444 8001</PII>,B_0r,Karaman,Sylka
Output: private_phone

Input: 0006 23.444 8001,<PII>B_0r</PII>,Karaman,Sylka,Ezavi
Output: secret

Input: B_0r,<PII>Karaman</PII>,Sylka,Ezavi
Output: private_person

Input: 084.910-0987, Nederland, <PII>770</PII>, Tiendweg, Lopik, UT, 3411
Output: private_address

Input: Lopik, UT, <PII>3411</PII>, Kamenova
Output: private_address

Input: UT, 3411, <PII>Kamenova</PII>\n- id(2) - +26.82 907.1047
Output: private_person

Input: **Candidat Henri**\n- Écuyer\n- <PII>Q0121990</PII>\n**Candidat Isabelle**
Output: account_number

Input: **Candidat Henri**\n- <PII>Écuyer</PII>\n- Q0121990
Output: private_person

Input: Wachtwoord: <PII>4821</PII>
Output: secret

Input: Passnummer: <PII>Q30J2786Y</PII>, Land: Deutschland
Output: account_number

Input: Geslacht: <PII>Vrouw</PII>
Output: other_pii
```

</details>

<details>
<summary><code>specs/pii-type-classifier-ft-v2.txt</code> — SHA-256 <code>f505e824aba4cf2efa6edd618a8c2857d1ad68d17bba8c57981d4692365c0e3d</code></summary>

```text
Classify the one already-detected PII substring enclosed by <PII> and </PII> in its source context. Return exactly one label and nothing else. The only valid labels are private_person, private_email, private_phone, private_address, private_url, private_date, account_number, secret, and other_pii.

Type mapping:
- private_person: given name, surname, full personal name, personal title, or username.
- private_email: email address.
- private_phone: telephone or fax number.
- private_address: building number, street, city, state/province, postcode, country, apartment/secondary address, or geographic coordinates.
- private_url: personal/private URL or any IPv4/IPv6 address.
- private_date: birth date, other personal date, or time.
- account_number: ID card, passport, driver's license, social number, bank/card/customer/order/account identifier.
- secret: password, PIN, passcode, API key, authentication token, or secret.
- other_pii: sex/gender value or PII not covered above.

Rules:
- Use a visible field label when available. Otherwise infer the repeating local schema from both neighbors and delimiter position, not from the visual shape of the value alone.
- In an address row, the telephone is private_phone; country, building, street, city, state, postcode, and secondary-address fields are private_address; and the trailing surname is private_person. Short country/state codes and bare building/postcode numbers remain private_address in those positions.
- In alternating EMAIL,SOCIALNUMBER sequences, every @ value is private_email and the alternating numeric, dotted, dashed, spaced, or alphanumeric social number is account_number.
- In alternating SOCIALNUMBER,IP sequences, valid four-octet IPv4 and colon-delimited IPv6 values are private_url; the alternating social numbers are account_number even when dotted like an invalid IP.
- A complete value containing @ and an email domain is private_email even when its local part is one letter, numeric, capitalized, or username-like.
- A social number, passport, driver's license, or ID-card value is account_number even when it resembles a phone number, address, password, or person. A value is secret only when its own field or established schema means password, PIN, passcode, key, token, or secret.
- Usernames and personal titles are private_person. Random letters/digits, initials, email-like prefixes without an email domain, and names that resemble locations can be usernames or names when their schema says so.
- Times and dates are private_date, including month/year forms such as juillet/00, novembre/70, März/93, août/64 and hour forms such as 11h.
- Sex/gender values are other_pii, including M, F, H, W, V, male, female, masculine, feminine, Masculino, Femmina, Männlich, Vrouw, Non-binaire, Otro, Autre, and Prefiero no revelar when they occupy a sex field or alternate with titles.
- Ignore a neighboring generic ID or row index when deciding the marked value's type.

Input: Email: <PII>maya@example.com</PII>
Output: private_email

Input: Call <PII>+1 (416) 555-0148</PII> today.
Output: private_phone

Input: Address: <PII>927 Shaft Road</PII>, Wawarsing, NY.
Output: private_address

Input: Coordinates: <PII>[51.9, 5.2147]</PII>
Output: private_address

Input: IP: <PII>192.168.1.8</PII>
Output: private_url

Input: Birth date: <PII>April 12, 1990</PII>
Output: private_date

Input: Passport: <PII>X1234567</PII>
Output: account_number

Input: Password: <PII>?b.6vBl</PII>
Output: secret

Input: Username: <PII>13ritz</PII>
Output: private_person

Input: Título: <PII>Señora</PII>
Output: private_person

Input: Sex: <PII>F</PII>
Output: other_pii

Input: tfjasta87868@gmail.com...<PII>2 57 01 85136 028 30</PII>...B@tutanota.com
Output: account_number

Input: 2 57 01 85136 028 30...<PII>B@tutanota.com</PII>...2.49.03.19524.337.91
Output: private_email

Input: 278-32-5098...<PII>K@tutanota.com</PII>...1-72-09-38517-757-27
Output: private_email

Input: SEC2003@tutanota.com...<PII>915 878 5014</PII>...K2002@gmail.com
Output: account_number

Input: 67.176.53.168...<PII>2.53.06.25467.868.33</PII>,126.207.172.140
Output: account_number

Input: 2.53.06.25467.868.33,<PII>126.207.172.140</PII>...2-48-01-24327-318-13
Output: private_url

Input: 1 70 03 66791 501 11,<PII>962:2d18:c84a:dc4a:7ebf:657b:dce1:9b57</PII>...239064649446220
Output: private_url

Input: 239064649446220,<PII>0.30.156.50</PII>...204061804707458
Output: private_url

Input: 25.71.134.73...<PII>1-81-03-32430-206-32</PII>,260c:701:cf04:474:752b:fb83:472:8558
Output: account_number

Input: 1-81-03-32430-206-32,<PII>260c:701:cf04:474:752b:fb83:472:8558</PII>...194101040825555
Output: private_url

Input: juillet/00, 01:12:35, Chemin de l'Étang...<PII>ssiksou</PII>, 2002-07-25T00:00:00
Output: private_person

Input: Chemin de l'Étang...ssiksou, <PII>2002-07-25T00:00:00</PII>...1970bixio.gourlaouen
Output: private_date

Input: 1970bixio.gourlaouen, <PII>novembre/70</PII>...1993bolombo
Output: private_date

Input: <PII>1993bolombo</PII>, 17/05/1993...elloh
Output: private_person

Input: seon.iannucci, <PII>07/10/1965</PII>...bcbteuwprkwrpq23
Output: private_date

Input: vondergroeben, <PII>août/64</PII>...
Output: private_date

Input: - id(6) - <PII>0124-50490865</PII>, NL, 965, Rieteiland
Output: private_phone

Input: 0124-50490865, <PII>NL</PII>, 965, Rieteiland
Output: private_address

Input: 0124-50490865, NL, <PII>965</PII>, Rieteiland, Rijswijk Strijp
Output: private_address

Input: NL, 965, <PII>Rieteiland</PII>, Rijswijk Strijp, Zuid-Holland
Output: private_address

Input: Rieteiland, <PII>Rijswijk Strijp</PII>, Zuid-Holland, 2285
Output: private_address

Input: Rijswijk Strijp, <PII>Zuid-Holland</PII>, 2285, Cudlipp
Output: private_address

Input: Zuid-Holland, <PII>2285</PII>, Cudlipp\n- id(7) - 0131 93-287-2456
Output: private_address

Input: Zuid-Holland, 2285, <PII>Cudlipp</PII>\n- id(7) - 0131 93-287-2456
Output: private_person

Input: 5622NFSAF, NanSpe22N146KCY, <PII>IT</PII>, 512, Strada Provinciale 41
Output: private_address

Input: IT, <PII>512</PII>, Strada Provinciale 41 della Rassinata, Arezzo
Output: private_address

Input: 512, Strada Provinciale 41 della Rassinata, <PII>Arezzo</PII>, 52, 52100
Output: private_address

Input: Arezzo, <PII>52</PII>, 52100, -
Output: private_address

Input: Arezzo, 52, <PII>52100</PII>, -
Output: private_address

Input: 167, Via San Donato-San Giorgio, Taranto, 75, 74122, <PII>Loft 253</PII>
Output: private_address

Input: Giocatore D:\n- <PII>XJW091723R</PII>\n- 0263907438\nGiocatore E:
Output: account_number

Input: Giocatore D:\n- XJW091723R\n- <PII>0263907438</PII>\nGiocatore E:
Output: account_number

Input: Führerschein: C6.27.SPSVM67.4\n- Pass: <PII>P88W6668O</PII>\n5. Schüler E:
Output: account_number

Input: <PII>Vrouw</PII>, Vrouw@mail.com, V, V@mail.com
Output: other_pii

Input: Pres <PII>Masculino</PII></strong></li><li><strong>Ambassador
Output: other_pii

Input: Profesor <PII>Otro</PII></strong></li><li><strong>Príncipe
Output: other_pii

Input: Ambassador <PII>Prefiero no revelar</PII></strong></li>
Output: other_pii

Input: M - 04/08/1956 - LBOA0459@hotmail.com\n3. <PII>Männlich</PII> - Oktober 17., 1953
Output: other_pii

Input: 76137 - <PII>dedb:84d9:6a62:d446:d296:bc32:2088:c014</PII> - d.20GBm!3!
Output: private_url

Input: dedb:84d9:6a62:d446:d296:bc32:2088:c014 - <PII>d.20GBm!3!</PII>\n2. M
Output: secret
```

</details>

<details>
<summary><code>specs/pii-type-classifier-v2.txt</code> — SHA-256 <code>c8ad02530828d02f4fc2084184fd438437df67a6caf0ee45a80b57ef542bdc69</code></summary>

```text
Classify the one already-detected PII value enclosed by <PII> and </PII> in its source context. Return exactly one label and nothing else. The only valid labels are private_person, private_email, private_phone, private_address, private_url, private_date, account_number, secret, and other_pii.

Use these meanings:
- private_person: name, surname, personal title, or username.
- private_email: email address.
- private_phone: telephone or fax number.
- private_address: building number, street, city, state/province, postcode, country, apartment/secondary address, or geographic coordinates.
- private_url: private/personal URL or any IPv4/IPv6 address.
- private_date: birth date, other personal date, or time.
- account_number: ID card, passport, driver's license, social number, bank, card, customer, order, or other account identifier.
- secret: password, PIN, passcode, API key, authentication token, or secret.
- other_pii: sex/gender value or PII not covered above.

Use the nearby field label whenever present. Labels may be English, Dutch, French, German, Italian, or Spanish. A password/PIN/passcode/API-key/token is secret even when it is only digits. A passport/license/ID/account value is account_number even when it looks random or secret. A username is private_person. An IP address is private_url. A sex/gender value is other_pii.

Input: Please email <PII>Maya Chen</PII> at maya@example.com.
Output: private_person

Input: Email: <PII>maya@example.com</PII>
Output: private_email

Input: Call <PII>+1 (416) 555-0148</PII> today.
Output: private_phone

Input: Address: <PII>927 Shaft Road</PII>, Wawarsing, NY.
Output: private_address

Input: Ciudad: <PII>Sevilla</PII>
Output: private_address

Input: IP: <PII>192.168.1.8</PII>
Output: private_url

Input: Adresse IP: <PII>8155:db8d:ec22:b258:a9f0:5524:ee3a:63e6</PII>
Output: private_url

Input: Profile URL: <PII>https://portal.example/u/maya</PII>
Output: private_url

Input: Birth date: <PII>April 12, 1990</PII>
Output: private_date

Input: Datum: <PII>2040-05-07T00:00:00</PII>
Output: private_date

Input: Passport: <PII>X1234567</PII>
Output: account_number

Input: Rijbewijs: <PII>45QFSK</PII>
Output: account_number

Input: Passnummer: <PII>Q30J2786Y</PII>, Land: Deutschland
Output: account_number

Input: order_id: <PII>AC-29418</PII>
Output: account_number

Input: Temporary PIN: <PII>4821</PII>
Output: secret

Input: PIN: <PII>4821</PII>
Output: secret

Input: Passcode: <PII>938201</PII>
Output: secret

Input: Wachtwoord: <PII>?b.6vBl</PII>
Output: secret

Input: Password: <PII>hunter2</PII>
Output: secret

Input: API token: <PII>sk-live-7XQ92</PII>
Output: secret

Input: Username: <PII>maya_c</PII>
Output: private_person

Input: Gebruikersnaam: <PII>13ritz</PII>
Output: private_person

Input: Título: <PII>Señora</PII>
Output: private_person

Input: Sex: <PII>F</PII>
Output: other_pii

Input: Geslacht: <PII>Vrouw</PII>
Output: other_pii

Input: Coordinates: <PII>[51.9, 5.2147]</PII>
Output: private_address
```

</details>
