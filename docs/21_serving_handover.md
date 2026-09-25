# 21 — Getting to a model that answers questions

> Written 2026-09-24. Read this with `training/EVAL_MATRIX.md`.
> If the session that started this died, **run `./scripts/rag_pipeline.sh status`
> and carry on** — every stage is resumable and skips itself if finished.

## The one-line version

```bash
./scripts/rag_pipeline.sh            # runs whatever is not yet done
./scripts/rag_pipeline.sh status     # what is done; runs nothing
./scripts/rag_pipeline.sh --redo 3   # force a stage again
```

## What changed on 2026-09-24

1. **The `torch` blocker is gone.** `OFFLOADING.md` §9 carried it as the thing
   gating `build-index`, chromadb, the Phase 2 gate, every baseline and
   `docs/20` §5. All six packages now import on the *unchanged* Python 3.9.6
   venv (torch 2.8.0, sentence_transformers 5.1.2, chromadb 1.5.9,
   transformers 4.57.6, ollama, mlx_lm 0.29.1) and MPS is available.
   **The venv rebuild in `docs/19` Part 6 is not needed.** Cause of the
   original failure unknown — do not delete the venv to "fix" anything
   without re-testing.
2. **Run 2's provenance is closed** (commit `1db2005`). Its dataset stays out
   of git — Rafat's translations, and `probes.jsonl` carries his published
   English verbatim — but `data/processed/training_max/SHA256SUMS.txt` is
   committed, so the hashes in EVAL_MATRIX are checkable.
3. **Run 2's peak memory was 54.4 GB**, not recorded before. It climbed until
   iteration 225. Training stays off-machine; inference does not.

## Why RAG before the tuned model

Run 2 improved validation loss 12.3% and converged. But validation loss
measures reproducing a corpus that is 217 of 288 interpretive layers
AI-authored with **0 human reviews**. The gain is in form, not knowledge —
which is exactly the division of labour `docs/15` designed: **LoRA teaches
form and honesty, RAG supplies facts at query time.**

So retrieval is what makes the thing able to answer. It also has to exist
first regardless, because the acceptance criterion is literally
`tuned+RAG ≥ base+RAG on factual AND tuned ≥ base on honesty`.

Cost ordering, measured rather than assumed:

| | needs | on disk already? |
|---|---|---|
| base + RAG | qwen3:8b (7.2 GB), BGE-M3 (2.4 GB), chromadb | **yes, all of it** |
| tuned (mlx) | `mlx-community/Qwen3-8B-4bit` ~4.5 GB | **no** — run 2 trained on another machine (`/Users/ran710/`) |
| tuned in Ollama | the above + fp16 fuse (~16 GB) + llama.cpp GGUF | no |

Decision (Rauf, 2026-09-24): serve the adapter with **mlx-lm
`--adapter-path`**, not fuse→GGUF. Cheaper, and the adapter stays swappable
between runs. Consequence: `rag.py:ask()` calls `run_ollama_chat`, so wiring
tuned+RAG needs a shim pointing at an mlx server — **not yet written.**

## What ran on 2026-09-24 (stages 1-3 complete)

**The archive answers questions.** All 1,306 records embedded; base qwen3:8b +
RAG answered all six demo questions with resolvable citations.

Two things measured that contradict what was assumed going in:

- **build-index takes ~50 minutes on this Air**, not the "few minutes" a token
  count suggests. BGE-M3 runs 27-55 records/min and slows sharply on the long
  records at the tail. It is now resumable (`scripts/build_index_resumable.py`),
  so an interrupted run costs one batch of 32 rather than the whole job.
- **The citation gate fires on real hallucinations.** qwen3:8b cited
  `kb:bio_claim_bulleh_shah_inayat:original` — a `:original` suffix that exists
  on poem-layer ids but not on biographical claims. `ask` exits non-zero, which
  is right; the pipeline now records the rejection and continues instead of
  losing the remaining questions to `set -e`.

The behaviour that says the design works: asked about the 1947 partition,
retrieval returned **eight records above the 0.35 threshold** (top 0.5577), so
the cheap min_score decline never fired — the model read them and declined on
the substance, naming the century mismatch. And the birth-year answer carried
the dispute forward (c. 1680, contested, no contemporary records) instead of
flattening it to a number.

Outputs regenerate; they are gitignored. `training/rag_outputs/`.

## Stages

| # | Stage | Invokes a model? | Notes |
|---|---|---|---|
| 1 | `build-index` | embedding only | 1,306 records, ~172k tokens, BGE-M3 on MPS. All-or-nothing: absent `manifest.json` means a dead run, so the dir is cleared first. |
| 2 | retrieval smoke | **no** | `ask --retrieve-only`. Proves the index with zero generation. |
| 3 | base + RAG answers | yes | → `training/rag_outputs/answers_base_rag.md` |
| 4 | baseline, bare | yes | fills EVAL_MATRIX `base` row |
| 5 | baseline, + RAG | yes | fills EVAL_MATRIX `base+RAG` row |
| 6 | fetch mlx base | no | ~4.5 GB, one time |
| 7 | tuned answers | yes | run 2 adapter, **no RAG** — the LoRA alone |

Use `data/processed/training/probes.jsonl` for evals, **not** the max build's:
the latter has 5 `reference_translation` probes that score a model on
reproducing Rafat's copyrighted English.

## Still open after this

- **tuned+RAG is not wired.** Stage 7 is the LoRA alone. The shim above is the
  remaining code.
- `ai-check` still uses `find_spec` (`src/abshaar/ollama_client.py:43`), so it
  reports packages healthy whether or not they import. It is why the torch
  breakage was recorded late and its repair was not noticed at all.
- The corpus ceiling in `docs/20` is untouched by any of this. Nothing here
  makes the archive more scholarly; it makes what exists reachable.
