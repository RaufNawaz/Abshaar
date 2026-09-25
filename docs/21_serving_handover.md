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

## The tuned+RAG shim (built 2026-09-24, commit `409129a`)

`rag.ask()` and `evaluate.run_eval()` called Ollama directly, so the mlx-served
adapter could not be reached through the `ask` path — which made the acceptance
criterion unmeasurable and left "serve it bare" as the only option, the one
configuration that fabricates sources.

Now: **a model string starting `mlx:` routes to a local `mlx_lm.server`,
anything else goes to Ollama unchanged.**

```bash
./scripts/serve_tuned.sh              # run2 (also: run1, base) -> port 8080
./scripts/abshaar.sh ask --model mlx:run2 "..."
./scripts/abshaar.sh run-eval --model mlx:run2 --rag
```

Same temperature 0.3 / top_p 0.9 as the Ollama path, so tuned-vs-base is like
for like. The text after `mlx:` is only a label for `eval_baseline.md`; which
weights load is decided by the server's `--model`/`--adapter-path`.

`tests/test_mlx_client.py` pins the routing both ways. Routing the wrong way is
silent: it would grade qwen3:8b and file the score as the tuned model's.

## Filling the acceptance table

```bash
nohup ./scripts/overnight.sh > training/pipeline_logs/overnight-driver.log 2>&1 &
```

Runs the four evals in the only order the hardware allows — both Ollama
baselines, then qwen3:8b is unloaded (`keep_alive: 0`) before the mlx server
loads the 4-bit 8B, because holding both is ~11 GB on a 16 GB Air. Ollama stays
up for the judge only (qwen3:4b, ~3 GB), which the two-phase eval reaches after
all answering is done, so the two large models are never resident together.

It waits for any `rag_pipeline.sh 4` already in flight rather than racing it,
skips any stage whose marker exists, and writes a timestamped journal to
`training/pipeline_logs/overnight-*.md`.

Then:

```bash
./.venv/bin/python scripts/update_eval_matrix.py          # write the rows
./.venv/bin/python scripts/update_eval_matrix.py --check  # non-zero if stale
```

The acceptance rows and the PASS/FAIL verdict are computed from
`data/processed/training/eval_runs/*.json`, never typed. The verdict is withheld
until all four runs exist — three finished runs plus an assumption must not read
as PASS — and a run with judge failures says so in the row, because those probes
degrade to token-F1.

**Reading progress:** the stage logs go through `tee` and buffer, so they lag.
The honest progress signal is the checkpoint:
`wc -l data/processed/training/eval_runs/*.partial.jsonl`.

## Measured throughput — the Air is the constraint

Numbers from 2026-09-25, on the 16 GB M4 Air with ~6 GB swapped:

| phase | rate | per 50-probe run |
|---|---|---|
| answering, no RAG (qwen3:8b) | ~80 s/probe | ~65 min |
| answering, with RAG (qwen3:8b + 8 records) | ~6 min/probe | ~5 h |
| judging (qwen3:4b, 18 of 50 probes) | 5-10 min/probe | ~2 h |

So one bare run is ~1h40m (measured: stage 4 completed in exactly that, 50/50,
zero failures) and one RAG run is ~7 h. **The full four-run acceptance set is
on the order of 15 hours on this machine**, not an evening.

**`think: false` does not fix the judge.** It was tried: it removes the
`<think>` block but qwen3:4b then reasons at the same length in the visible
content instead, so the call is no faster, and capping `num_predict` truncates
before the digit ever appears (tested at 4, 32 and 64 — no digit). The judge
config was therefore left alone, which also keeps the four runs comparable;
changing a judge between runs of a four-way comparison invalidates it.

If this needs to be faster, the levers are a bigger machine, a non-reasoning
judge model, or fewer probes — not a flag. If fewer probes: the criterion pairs
runs as (bare vs bare) and (RAG vs RAG), so a reduced `--limit` is defensible
as long as **both halves of a pair use the same one**.

## Gotchas found the hard way

- **Do not edit `scripts/rag_pipeline.sh` while it is running.** Bash reads a
  script incrementally from an offset, so an edit mid-run shifts the ground
  under it. Stage 1 finished its work but never wrote its marker, almost
  certainly for this reason. Wait for the stage, or copy the script first.
- **Memory.** Ollama holding qwen3:8b and an mlx server holding the 4-bit 8B is
  ~11 GB on a 16 GB Air, with ~3 GB already swapped. Run the Ollama baselines
  and the mlx work one after the other, not together.
- **`ai-check` now imports** each package rather than `find_spec`-ing it
  (commit `4549b95`), and distinguishes "present but fails to import" from
  "missing". Those need different fixes, and conflating them is what hid the
  torch breakage and then hid its repair.

## Still open after this

- **tuned+RAG has not been measured yet**, though it can now be run. The code
  exists and is tested; what is missing is the run, and the EVAL_MATRIX
  acceptance rows it would fill.
- The corpus ceiling in `docs/20` is untouched by any of this. Nothing here
  makes the archive more scholarly; it makes what exists reachable.
