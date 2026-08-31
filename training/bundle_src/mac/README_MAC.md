# Abshaar — Bulleh Shah expert model, Apple Silicon training bundle

Self-contained. Copy it to any Apple Silicon Mac (a lab Mac Studio, another
laptop, or this one), run one command, carry the results back. No repository
checkout and no private corpus material comes with it.

---

## 0. Treat the machine as temporary

Everything this bundle creates lives under one folder you choose (`-r`), and
the last stage (`04_pack_outbox.sh`) gathers the results into `<root>/outbox`
plus a small ZIP. On a shared or wiped machine, anything you do not copy off
before logging out is gone — including the compute that produced it.

- One folder holds the venv, the Hugging Face cache, adapters and results.
  Nothing is written to `~/.cache`.
- Each stage writes a marker under `<root>/.stages`, so re-running after an
  interruption resumes instead of restarting.
- mlx-lm checkpoints every 200 iterations; `--resume` continues from the
  newest adapter file.
- Point `-r` at an external drive to keep the ~5–16 GB of downloads between
  sessions.

---

## 1. Quick start

```bash
chmod +x *.sh          # only needed if the ZIP dropped the executable bit
./run_all.sh -r ~/abshaar-work
```

That runs bootstrap → train → fuse (+ GGUF where possible) → base-vs-tuned
generations → pack. On a Mac Studio expect **1–3 hours end to end**; on a
16 GB MacBook Air use the 4B model (below) and expect longer.

### Stages by hand

```bash
./00_bootstrap.sh    -r ~/abshaar-work    # venv, mlx-lm, base weights
./01_train.sh        -r ~/abshaar-work    # LoRA fine-tune (add --resume)
./02_fuse_export.sh  -r ~/abshaar-work    # fuse adapter into base, GGUF if possible
./03_generate.sh     -r ~/abshaar-work    # base vs tuned answers on eval + probes
./04_pack_outbox.sh  -r ~/abshaar-work    # collect, checksum, zip, and warn
```

Common switches: `-m <model repo>`, `-i <iters>`, `--skip-gguf`,
`--skip-generate`, `--resume`.

---

## 2. Which base model

| Machine | Model | Notes |
|---|---|---|
| MacBook Air / Pro, 16 GB | `mlx-community/Qwen3-4B-4bit` | The Air's ceiling. `-m mlx-community/Qwen3-4B-4bit` |
| Mac Studio / 32 GB+ | `mlx-community/Qwen3-8B-4bit` *(default)* | Matches the `qwen3:8b` baseline already planned for the archive, so the tuned model compares against a measured baseline. |
| Mac Studio, 64 GB+ | `mlx-community/Qwen3-8B-bf16` | Only path that yields an Ollama-servable GGUF (see §4). Heavier and slower. |

Anything larger than 8B, or a change from 4-bit to bf16 for the *comparison*
model, needs fresh baseline rows before its scores mean anything — that is a
decision to take deliberately, not a default to slide into.

---

## 3. What is in this bundle

| Path | What it is |
|---|---|
| `dataset/train.jsonl`, `valid.jsonl` | The gated training split, in mlx-lm's expected layout. |
| `dataset/eval.jsonl`, `probes.jsonl` | Held-out eval examples and the 50 honesty/disputed-fact probes. |
| `generate_outputs_mlx.py` | Base-vs-tuned answers on the eval set and probes. |
| `*.sh` | The five stages plus `run_all.sh`. |
| `MANIFEST.md` | Exact example counts and SHA-256 of each dataset file. |

**Rights:** the dataset files are the output of the repository's
`export-mlx-dataset`, already gated by an 8-gram leak scan against the
copyrighted reference translations. Nothing else from the archive is here —
no private knowledge base, no Sufinama or PunjabLibrary witness texts, no
reference translations, no git history. That is what makes this bundle safe
to carry onto a shared machine. Do not add corpus files to it.

---

## 4. The GGUF caveat, stated plainly

The project serves its model through Ollama, which needs a GGUF file. GGUF can
only be produced from a **non-quantised** fuse. If you trained on a 4-bit base
(the memory-safe default), the fused model is quantised MLX and llama.cpp
cannot convert it — `02_fuse_export.sh` detects this and tells you rather than
failing obscurely. You still get:

- a fused MLX model that `mlx_lm.generate` / `mlx_lm.server` can serve, and
- the adapter, which is the reproducible artefact.

For an Ollama-servable GGUF from the Mac path, train from
`mlx-community/Qwen3-8B-bf16` on a Mac with the memory for it. The CUDA
workstation bundle produces the Q4_K_M GGUF directly, which is the reason to
prefer it when a workstation is available.

---

## 5. What to carry home

| Artefact | Size | Why |
|---|---|---|
| `abshaar_results_small.zip` | ~50–300 MB | Adapter, `train_summary.json` (hyperparameters, dataset SHA-256), training logs, base/tuned generations. **Email-able.** |
| `outbox/model/*.gguf` + `Modelfile.abshaar-bulleh` | ~5–16 GB, when produced | The servable model: `ollama create abshaar-bulleh -f Modelfile.abshaar-bulleh`. Use a drive, not email. |

Back in the repository:

```bash
./scripts/import_trained_adapter.sh /path/to/outbox/adapter/<model-slug>
```

then continue from `docs/17_training_runbook.md` §6.

---

## 6. What this bundle does *not* settle

The generations in `outbox/generations/` are evidence, not the project's
acceptance evaluation. Acceptance is `abshaar run-eval` on the serving Mac
(judge model, RAG, the rubric in `src/abshaar/evaluate.py`) against **baseline
rows that do not exist yet** — `build-index`, the RAG smoke test and the three
baseline runs are still outstanding. Training here does not remove that gate.

The criterion, unchanged: tuned+RAG ≥ base+RAG on factual **and** tuned ≥ base
on honesty. A model that hallucinates more than base is rejected regardless of
style.

---

## 7. Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `This is not an Apple Silicon Mac` | Intel Mac | MLX needs Apple Silicon; use the Windows/CUDA bundle |
| `permission denied: ./run_all.sh` | ZIP dropped the exec bit | `chmod +x *.sh` |
| `no module named mlx_lm` | Bootstrap not run, or wrong venv | `./00_bootstrap.sh -r <root>` |
| Training killed / machine swaps hard | Model too large for the RAM | Use `-m mlx-community/Qwen3-4B-4bit` |
| `python -m mlx_lm lora` unknown | Older mlx-lm entry points | Handled: `common.sh` falls back to `python -m mlx_lm.lora` |
| Download stalls | HF CDN hiccup | Re-run `00_bootstrap.sh`; `snapshot_download` resumes |
| GGUF step skipped | Quantised fuse | Expected — see §4 |
