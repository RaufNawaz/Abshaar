# Abshaar — Bulleh Shah expert model, Windows/CUDA training bundle

Self-contained. Unzip it on the workstation, run one command, carry the
results off before you sign out. No repository checkout, no network shares,
no admin rights required.

---

## 0. The rule that matters most on this machine

**The workstation deletes all data at sign-out.** Everything this bundle
creates lives under one folder you choose (`-Root`), and the last stage
(`04_pack_outbox.ps1`) gathers the results into `<Root>\outbox` plus a small
ZIP. Nothing you do not copy off survives.

Practical consequences, built into the scripts:

- One folder holds the venv, the Hugging Face cache, checkpoints and results.
  Nothing is written to your user profile.
- Every stage writes a marker under `<Root>\.stages`, so re-running after an
  interruption resumes instead of starting over.
- Training checkpoints every 50 optimizer steps; `-Resume` continues from the
  newest one.
- If you have an external drive or a persistent network folder, point `-Root`
  at it (`-Root E:\abshaar-work`) and even the 20 GB of downloads survive to
  the next session.

---

## 1. Quick start

```powershell
# In PowerShell, from the unzipped folder:
.\RUN_ALL.ps1 -Root D:\abshaar-work
```

If PowerShell refuses to run scripts (a locked-down machine usually does),
double-click `RUN_ALL.cmd` instead, or run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\RUN_ALL.ps1 -Root D:\abshaar-work
```

That runs, in order: bootstrap → train → merge + GGUF export → base-vs-tuned
generations → pack the outbox. Expect **60–120 minutes total on an RTX
6000-class card**, most of it downloading (~20 GB) rather than computing.

You need roughly **80 GB of free disk** for the 8B path.

### Running the stages by hand

```powershell
.\00_bootstrap.ps1    -Root D:\abshaar-work    # python, torch+CUDA, libraries, base weights
.\01_train.ps1        -Root D:\abshaar-work    # LoRA fine-tune  (add -Resume to continue)
.\02_merge_export.ps1 -Root D:\abshaar-work    # merge adapter, export Q4_K_M GGUF
.\03_generate.ps1     -Root D:\abshaar-work    # base vs tuned answers on eval + probes
.\04_pack_outbox.ps1  -Root D:\abshaar-work    # collect, checksum, zip, and warn
```

Useful switches: `-Model Qwen/Qwen3-4B` (smaller/faster), `-Epochs 2`,
`-SkipGguf`, `-SkipGenerate`, `-TorchIndex https://download.pytorch.org/whl/cu124`.

---

## 2. What is in this bundle

| Path | What it is |
|---|---|
| `dataset/train.jsonl`, `valid.jsonl` | The gated training split (chat-format examples). |
| `dataset/eval.jsonl`, `probes.jsonl` | Held-out eval examples and the 50 honesty/disputed-fact probes. |
| `train_lora_cuda.py` | The trainer: plain `transformers.Trainer` + `peft`, loss on assistant turns only. |
| `merge_adapter.py` | Merges the LoRA into the base weights for GGUF export. |
| `generate_outputs.py` | Base-vs-tuned answers on the eval set and probes. |
| `check_env.py`, `download_model.py` | Environment report; base-model pre-download. |
| `*.ps1`, `RUN_ALL.cmd` | The five stages, an orchestrator, and a double-clickable launcher. |
| `MANIFEST.md` | Exact example counts and SHA-256 of each dataset file. |

**Rights:** the dataset files are the output of the repository's
`export-mlx-dataset`, already gated by an 8-gram leak scan against the
copyrighted reference translations. Nothing else from the archive is here —
no private knowledge base, no Sufinama or PunjabLibrary witness texts, no
reference translations, no git history. That is what makes this bundle safe
to carry onto a shared machine. Do not add corpus files to it.

---

## 3. Why these tools and not the obvious ones

- **No Axolotl, no TRL, no DeepSpeed, no bitsandbytes on the default path.**
  Each is a recurring source of Windows-specific breakage, and none is needed:
  an 8B bf16 LoRA fits comfortably in 48 GB of VRAM. The trainer is ~350 lines
  of `transformers` + `peft` you can read in one sitting.
- **No 4-bit quantisation while training.** bf16 avoids the bitsandbytes
  dependency entirely and trains faster. Use `--load-in-4bit`-style setups only
  if you move to a model too large for the card.
- **`sdpa` attention, not flash-attn**, which has no reliable Windows wheels.
- **torch from `--index-url https://download.pytorch.org/whl/cu128`**, never
  `--extra-index-url`: on Windows the default PyPI `torch` wheel is CPU-only
  and pip will happily prefer it. `check_env.py` fails loudly if that happens.

`cu128` covers both RTX 6000 Ada (sm_89) and RTX PRO 6000 Blackwell (sm_120).
On an older card, pass `-TorchIndex https://download.pytorch.org/whl/cu124`.

---

## 4. What to carry home, and what it is for

After `04_pack_outbox.ps1`:

| Artefact | Size | Why you want it |
|---|---|---|
| `abshaar_results_small.zip` | ~100–300 MB | The LoRA adapter, `train_summary.json` (hyperparameters, dataset SHA-256, losses), `env_report.json`, base/tuned generations, run logs. **Email-able.** |
| `outbox\model\*.gguf` + `Modelfile.abshaar-bulleh` | ~5 GB (Q4_K_M) | The servable model. `ollama create abshaar-bulleh -f Modelfile.abshaar-bulleh` on the Mac. Too big to email — use a drive or cloud storage. |

Back in the repository on the Mac:

```bash
./scripts/import_trained_adapter.sh /path/to/outbox/adapter/Qwen_Qwen3-8B
```

then continue from `docs/17_training_runbook.md` §6 (import to Ollama →
acceptance eval). `docs/18_workstation_training_runbook.md` has the full
round-trip.

---

## 5. What this bundle does *not* settle

The generations in `outbox\generations\` are evidence, not the project's
acceptance evaluation. Acceptance is measured on the Mac by
`abshaar run-eval` (judge model, RAG, the rubric in `src/abshaar/evaluate.py`)
against **baseline rows that do not exist yet** — `build-index`, the RAG smoke
test and the three baseline runs are still outstanding on the Mac. Training
here does not remove that gate; it just means the tuned model is ready and
waiting when the baselines are measured.

The criterion, unchanged: tuned+RAG ≥ base+RAG on factual **and** tuned ≥ base
on honesty. A model that hallucinates more than base is rejected regardless of
how much better its style reads.

---

## 6. Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `...cannot be loaded because running scripts is disabled` | Execution policy | Use `RUN_ALL.cmd`, or `powershell -ExecutionPolicy Bypass -File ...` |
| `check_env.py` exits 1, `cuda_available: false` | CPU-only torch installed | `venv\Scripts\python.exe -m pip install --force-reinstall --index-url https://download.pytorch.org/whl/cu128 torch` |
| torch version has no `+cu` suffix | Same as above | Same as above |
| `CUDA out of memory` | Card smaller than assumed | `-Model Qwen/Qwen3-4B`, or `01_train.ps1 -BatchSize 1 -GradAccum 16` |
| Python not found / Store shim opens | No usable Python | The bootstrap installs a private Python 3.12 under `<Root>\python312`; re-run it |
| Model download stalls | HF CDN hiccup | Re-run `00_bootstrap.ps1`; `snapshot_download` resumes |
| GGUF step fails | GitHub unreachable, or no prebuilt binary | Non-fatal. Carry the adapter home and convert later |
| Training loss is `nan` | fp16 on a card without bf16 | Check `env_report.json`; an RTX 6000 should report `bf16_supported: true` |
