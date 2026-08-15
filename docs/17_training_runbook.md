# 17 — Training Runbook (Phases 2-gate → 6)

> Written 2026-08-15. A self-contained, step-by-step guide for the session
> that executes the model-dependent half of
> `docs/15_bulleh_shah_expert_model_implementation_plan.md`. Everything
> model-independent (Phases 0–4 code, the dataset, project-latin-v1
> normalization) is already done, committed, and gate-verified — do not redo
> it. Follow the steps in order; each has a gate that exits non-zero.

---

## 0. Ground rules (read before anything)

1. Read `AGENTS.md`, `CLAUDE.md`, `OFFLOADING.md`, and this runbook fully.
   Run `git status --short --branch`; preserve concurrent work.
2. **Standing constraint: Rauf must explicitly authorize model runs in the
   current session before you execute Step 2 onward.** If he handed you this
   runbook and said "run the training" (or equivalent), that is the
   authorization — record his exact wording in OFFLOADING. If you only
   inherited the repo without such an instruction, stop and ask.
3. Never weaken a gate to make it pass. Never edit corpus content to satisfy
   a check. If a gate fails, fix the cause or stop and report.
4. Commit each completed step as one unit (scope prefix `feat:`/`data:`/
   `docs:`), update `OFFLOADING.md` (CRAFT) and the plan's §10 checklist
   after every step. Push only if Rauf has authorized pushing (he did on
   2026-08-15; re-confirm if in doubt).
5. All commands run from the repo root on the Mac (zsh). The wrapper
   `./scripts/abshaar.sh` automatically uses `.venv` when present.

## 1. Preconditions checklist

Verify every line; fix before proceeding.

| Check | Command | Expected |
|---|---|---|
| Tree clean, on `draft`, synced | `git status --short --branch` | clean, `## draft...origin/draft` |
| Tests | `PYTHONPYCACHEPREFIX=/tmp/abshaar-pycache PYTHONPATH=src python3 -m unittest discover -s tests` | all pass (68+ tests) |
| Validation | `./scripts/abshaar.sh validate` | `No validation issues found.` |
| Ollama serving | `curl -s localhost:11434/api/tags` | JSON reply (else `ollama serve &`) |
| Models pulled | `ollama list` | `qwen3:4b` AND `qwen3:8b` (else `ollama pull qwen3:8b`) |
| RAG index built | `cat data/cache/chroma/manifest.json` | `{"embed_model": "BAAI/bge-m3", "records": ~1303}` (else `./scripts/abshaar.sh build-index`, needs ~2.3GB download first time) |
| mlx-lm installed | `.venv/bin/python -c "import mlx_lm"` | no error (else `.venv/bin/pip install mlx-lm`; see §7 if it fails) |
| Dataset present | `./scripts/abshaar.sh status` | 1,181 training examples, 50 probes, 360 trainable layers |

**Index staleness rule:** if `build-kb` has run more recently than
`build-index` (check file mtimes), rebuild the index first — it must embed
the current KB.

## 2. Phase 2 gate — retrieval smoke test (~10–20 min)

```bash
.venv/bin/python scripts/rag_smoke_test.py --model qwen3:8b
```

Pass = `SMOKE TEST PASSED: 12/12 checks clean.`

Triage if it fails:
- **In-corpus question declined** → inspect scores with
  `./scripts/abshaar.sh ask "<question>" --retrieve-only`. If retrieval finds
  the right records but below 0.35, the threshold is miscalibrated for
  BGE-M3 on this corpus: lower `DEFAULT_MIN_SCORE` in `src/abshaar/rag.py`
  ONLY with the measured scores recorded in the commit message, and re-run
  the full smoke test including the two out-of-corpus declines (they must
  still decline — that is the other side of the same threshold).
- **Expected record missing from hits** → check the KB record exists
  (`grep <id> data/processed/private/knowledge_base.jsonl`), then whether the
  index is stale (§1 staleness rule).
- **Invented citations** → a generation problem; try qwen3:4b to compare, and
  report rather than patching the validator.

Commit: `feat: Phase 2 gate — RAG smoke test passing` + OFFLOADING entry with
the printed per-question scores.

## 3. Phase 4 gate — baselines BEFORE any training (~30–60 min total)

Run all three; each appends a row to
`data/processed/training/eval_baseline.md`:

```bash
./scripts/abshaar.sh run-eval --model qwen3:4b --judge qwen3:8b
./scripts/abshaar.sh run-eval --model qwen3:8b --judge qwen3:4b
./scripts/abshaar.sh run-eval --model qwen3:8b --rag --judge qwen3:4b
```

Notes: the judge must differ from the scored model. Per-run JSON detail lands
in `data/processed/training/eval_runs/`. Expect the bare models to score low
on factual (they don't know this corpus) and the +RAG run to score higher —
if +RAG does NOT beat bare 8b on factual, something is wrong with retrieval;
stop and investigate before training.

**No baseline rows → no training. This gate is absolute.**

Commit: `data: baseline evals (4b / 8b / 8b+RAG)` with the three summary
lines in the message.

## 4. Optional — augmentation (~1–2 h wall clock, unattended)

Improves question diversity; skippable if time-boxed.

```bash
./scripts/abshaar.sh augment-training-data --generator qwen3:8b --verifier qwen3:4b --limit-per-family 30
```

- Aborts (exit 1) if the verifier rejects >30% — that means the generator
  prompt needs work; report, don't force.
- **If it succeeds you MUST re-export the MLX dataset** (augmented examples
  append to train.jsonl): `./scripts/abshaar.sh export-mlx-dataset`
- Re-run `./scripts/abshaar.sh validate` (augmented rows are validated too).

Commit: `data: paraphrase-augmented training set (+N examples)`.

## 5. Phase 5 — LoRA training, Path A (local M4, ~1–3 h)

```bash
./scripts/abshaar.sh export-mlx-dataset   # idempotent; ensures freshness
./scripts/train_lora.sh                   # defaults: mlx-community/Qwen3-4B-4bit, 600 iters
```

- The default model repo id must be verified against Hugging Face at run
  time (`mlx-community/Qwen3-4B-4bit`); if it doesn't exist, search
  mlx-community for the current Qwen3-4B 4-bit conversion and pass it as
  arg 1. Record the exact id used.
- Memory: 16 GB M4. If memory pressure is fine at 4B, an 8B-4bit attempt is
  optional later; do not start with 8B.
- Watch val loss in the output (`--steps-per-eval 100`); a val loss that
  rises from the start suggests a data or template problem — stop and report.
- Adapters land in `training/adapters/<model>/` (gitignored). Record the
  final val loss and the adapter SHA-256
  (`shasum -a 256 training/adapters/*/adapters.safetensors`) in OFFLOADING.

## 6. Phase 5 gate + Phase 6 — evaluate the tuned model, then serve

`run-eval` talks to Ollama, so the adapter must be fused and imported first:

```bash
.venv/bin/python -m mlx_lm fuse \
  --model mlx-community/Qwen3-4B-4bit \
  --adapter-path training/adapters/<run> \
  --save-path training/fused/<run>
```

Then get it into Ollama — two options, try in order:
1. `mlx_lm fuse --export-gguf` if the installed mlx-lm supports it for Qwen3
   (check `.venv/bin/python -m mlx_lm fuse --help`); point
   `training/Modelfile.abshaar-bulleh`'s FROM at the GGUF and run
   `ollama create abshaar-bulleh -f training/Modelfile.abshaar-bulleh`.
2. Otherwise convert `training/fused/<run>` with llama.cpp's
   `convert_hf_to_gguf.py` (needs `git clone` of llama.cpp; CPU-only, a few
   minutes), then the same `ollama create`.

Acceptance evaluation (all four rows must exist):

```bash
./scripts/abshaar.sh run-eval --model abshaar-bulleh --judge qwen3:8b
./scripts/abshaar.sh run-eval --model abshaar-bulleh --rag --judge qwen3:8b
```

**Acceptance criteria (plan §3 Phase 5, verbatim):** tuned+RAG ≥ base+RAG on
factual AND tuned ≥ base on honesty. A model that hallucinates more than
base is REJECTED regardless of style gains — delete nothing, but do not
declare it the serving model; report and stop.

If accepted:
- Write `training/EVAL_MATRIX.md`: the 4-row table (base 8b / base 8b+RAG /
  tuned / tuned+RAG) plus adapter SHA-256, training args, dataset counts.
- The serving command is `./scripts/abshaar.sh ask "<question>" --model abshaar-bulleh`
  (retrieval + tuned generation + citations). Spot-check 5 questions manually.

Commit: `feat: Phase 5/6 — tuned model accepted and served` (or a truthful
failure report).

## 7. Troubleshooting seen on this machine (2026-08-15)

| Symptom | Cause | Fix |
|---|---|---|
| `no such host … r2.cloudflarestorage.com` / HF CDN errors | transient DNS/resolver failure | wait and retry; verify with `nslookup <host>`; general net can be fine while CDN DNS fails |
| `write_text() got unexpected keyword 'newline'` or same-quote f-string SyntaxError | the venv is Python 3.9 (system python3), despite pyproject's >=3.11 | use `Path.open`; double-quote f-strings; if mlx-lm refuses 3.9: `brew install python@3.12`, recreate `.venv`, reinstall `requirements.txt` (multi-GB) |
| `AI stack unavailable` from build-index/ask | ran outside the venv | wrappers prefer `.venv` automatically; check `.venv/bin/python` exists |
| Answers full of `<think>…</think>` | qwen3 reasoning mode | already stripped in `rag.py`/`evaluate.py`; strip likewise in any new code |
| Pipe-masked failures (`cmd \| tail` exits 0 on failure) | pipe swallows exit codes | never gate on piped commands; this bit two downloads today |
| Ollama API refused | server not running | `ollama serve &` then retry |

## 8. After the run — handoff duties

1. Update `OFFLOADING.md` (§1 stage, §2 entry with exact commands/outputs,
   §7 next steps) and the plan §10 checklist.
2. Add a dated entry to `Bulleh Shah/CORPUS_BUILD_LOG.md` only if corpus
   files changed (augmentation does not touch entries; normalization-type
   changes do).
3. `git push origin draft` (authorized 2026-08-15; re-confirm if unsure).
4. Open items that remain human work regardless of training outcome:
   the 124-record crosswalk review queue
   (`data/annotations/crosswalk_review_queue.md`), ʿain/Arabic-loan mark
   upgrades flagged by `docs/16` §5, the Sufinama written-authorization
   reference, and the five-poem gold review slice.
