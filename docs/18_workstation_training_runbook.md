# 18 — Off-machine training runbook (Windows/CUDA and Apple Silicon)

> Written 2026-08-31. How to train the Bulleh Shah LoRA on a machine that is
> not this MacBook Air — an NVIDIA workstation or another Apple Silicon Mac —
> and bring the result back into the archive. Companion to
> `docs/17_training_runbook.md`, which stays authoritative for everything that
> happens *on* the serving Mac (Phases 2–4 gates, §6 fuse/serve/acceptance).

---

## 1. Why this exists

The M4 Air is a 16 GB, fanless machine; `docs/17` caps local LoRA training at
Qwen3-4B and paces runs around thermal throttling. Two other machines remove
that ceiling entirely:

| Path | Machine | Toolchain | Produces |
|---|---|---|---|
| A | This Air | mlx-lm | 4B adapter, thermally paced |
| B | Rented cloud GPU | Axolotl (`training/axolotl_qwen3_8b.yml`) | 8B QLoRA, ~$5–20 |
| **C** | **Any Apple Silicon Mac** | **mlx-lm** | **8B adapter; GGUF only from a bf16 base** |
| **D** | **Windows + NVIDIA workstation** | **PyTorch + peft** | **8B adapter *and* a Q4_K_M GGUF** |

Paths C and D are what this document covers. Both are shipped as
self-contained bundles: no repository checkout, no private corpus, no admin
rights, one folder that holds everything.

**Prefer D when a workstation is available.** It is the only path that ends
with an Ollama-servable GGUF without a second heavy machine, because merging
and quantising an 8B model needs memory the Air does not have.

## 2. Build the bundles (on this Mac)

```bash
./scripts/export_training_bundle.sh                 # both targets
./scripts/export_training_bundle.sh --target windows
```

Sources live in `training/bundle_src/{mac,windows}/` and are committed;
outputs land in `training/dist/` and are gitignored build artefacts:

```
training/dist/
  mac/  windows/                          the unpacked bundles
  abshaar_mac_bundle.zip                  ~230 KB
  abshaar_windows_bundle.zip              ~245 KB
  abshaar_*_bundle.zip.b64.txt            email-safe copies
  EMAIL_ME.md                             how to move them and decode them
```

**Why a base64 `.txt` as well as a ZIP:** Gmail and most corporate filters
block `.ps1`, `.cmd` and `.py` attachments *including inside archives*, and
reject the whole message. The `.txt` always arrives; `certutil -decode` on
Windows or `base64 -D` on macOS restores the ZIP. Use the plain ZIP for a
drive, Drive/iCloud, or AirDrop.

### What travels, and what must not

Only `dataset/{train,valid,eval,probes}.jsonl` — the gated output of
`export-mlx-dataset` and the same generator's held-out split and probe set,
all past the 8-gram leak scan against Rafat's copyrighted translations. **No
private knowledge base, no Sufinama or PunjabLibrary witness texts, no
reference translations, no git history.** Each bundle's `MANIFEST.md` states
the counts and SHA-256 of every file it carries. Do not add corpus material
to a bundle to make something convenient.

## 3. Run it (on the other machine)

Windows workstation — read `README_WINDOWS.md` first, then:

```powershell
.\RUN_ALL.ps1 -Root D:\abshaar-work        # or double-click RUN_ALL.cmd
```

Apple Silicon Mac — read `README_MAC.md` first, then:

```bash
chmod +x *.sh && ./run_all.sh -r ~/abshaar-work
```

Both run the same five stages: bootstrap → train → merge/fuse (+GGUF) →
base-vs-tuned generations → pack the outbox.

### The wipe-on-sign-out rule

Rauf's Windows workstation **deletes all data when he signs out**. Every
design choice in the bundles follows from that:

- one work root holds the venv, the model cache, checkpoints and results —
  nothing is written to the user profile;
- every stage drops a marker in `<root>/.stages`, so an interrupted run
  resumes rather than restarts;
- training checkpoints frequently (every 50 steps on CUDA, every 200
  iterations on MLX) and both trainers accept `--resume`/`-Resume`;
- the final stage prints an explicit "copy this off before you sign out"
  checklist with sizes and a `SHA256SUMS.txt` to verify the copy;
- pointing `-Root` at an external drive makes even the ~20 GB of downloads
  survive to the next session.

Treat any shared Mac the same way.

## 4. Bring it back

| Artefact | Size | Route |
|---|---|---|
| `abshaar_results_small.zip` | ~100–300 MB | Adapter, `train_summary.json`, `env_report.json`, base/tuned generations, logs. Email or upload. |
| `outbox/model/*.gguf` + `Modelfile.abshaar-bulleh` | ~5 GB Q4_K_M | Drive or cloud. This is the servable model. |

Then, in the repository:

```bash
./scripts/import_trained_adapter.sh /path/to/outbox/adapter/<model-slug>
```

That copies the adapter into `training/adapters/`, verifies it looks like a
real adapter directory (mlx-lm's `adapters.safetensors` or peft's
`adapter_model.safetensors`) and prints its SHA-256 for `OFFLOADING.md` and
`training/EVAL_MATRIX.md`.

With the GGUF, from the folder holding it and the Modelfile:

```bash
ollama create abshaar-bulleh -f Modelfile.abshaar-bulleh
```

Then continue at `docs/17_training_runbook.md` §6.

## 5. What off-machine training does not settle

The generations in `outbox/generations/` are **evidence, not the acceptance
evaluation**. Acceptance is measured here, by `abshaar run-eval` — judge
model, RAG, the rubric in `src/abshaar/evaluate.py` — against baseline rows
that **do not exist yet**: `data/processed/training/eval_baseline.md` is
absent, and `build-index`, the Phase 2 RAG smoke test and the three Phase 4
baseline runs are all still outstanding on this Mac.

Training elsewhere does not move that gate; it means the tuned model is ready
and waiting when the baselines are measured. The criterion is unchanged:
**tuned+RAG ≥ base+RAG on factual AND tuned ≥ base on honesty.** A model that
hallucinates more than base is rejected regardless of style gains.

Known blocker for that Mac-side work, found 2026-08-31: `torch` in `.venv`
does not import (Python 3.9 venv, torch 2.8.0 wheel → circular-import
failure), so `build-index` and anything else touching
`sentence_transformers`/`chromadb` will fail until the venv is rebuilt on
Python 3.11/3.12. `ai-check` does not catch this because it uses
`importlib.util.find_spec`, which never imports the package. See
`OFFLOADING.md`.

## 6. Design notes (why the bundles look like this)

- **No Axolotl/TRL/DeepSpeed/bitsandbytes on the Windows path.** Each is a
  recurring Windows breakage and none is needed: an 8B bf16 LoRA fits in
  48 GB of VRAM. `train_lora_cuda.py` is plain `transformers.Trainer` + `peft`
  and can be read end to end.
- **Loss on assistant turns only**, by masking the longest common prefix
  between the templated prompt and the templated full conversation — template
  agnostic, and verified against all 1,038 training rows.
- **`enable_thinking=False`** everywhere: the dataset contains no reasoning
  traces, and Qwen3's default template opens a `<think>` block.
- **torch from `--index-url .../whl/cu128`, never `--extra-index-url`** — on
  Windows the default PyPI wheel is CPU-only and pip prefers it. `check_env.py`
  exits non-zero if CUDA ends up unavailable, rather than letting a silent
  CPU run start.
- **bf16, not 4-bit, while training** — drops the bitsandbytes dependency and
  is faster; the card has the memory.
- **The GGUF step is best-effort and says so.** It pulls llama.cpp from
  GitHub; if that fails the adapter is still intact and the script reports the
  failure instead of pretending.
