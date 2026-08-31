# 19 — Mac training walkthrough (exact steps)

> Written 2026-08-31. Every command, in order, for training the Bulleh Shah
> LoRA on a Mac. `docs/18` explains the design; this file is the one you keep
> open while doing it.
>
> Three roles, which may be one machine or two:
> - **Air** — this MacBook (the repository lives here; it serves the model).
> - **Trainer** — the Mac doing the training. A Harvard Mac Studio, or the Air
>   itself (see Appendix A).
> - Every command below is labelled with the machine it runs on.

---

## Part 0 — Read this before you start

**Two independent tracks.** Training and *judging* the tune are separate, and
only one of them is blocked:

| Track | Where | Blocked? |
|---|---|---|
| Produce an adapter (Parts 1–5) | Trainer | No. Start any time. |
| Judge whether the adapter is any good (Part 6) | Air | Yes — needs a venv rebuild and three baseline runs that have never happened. |

You can do Parts 1–5 today and Part 6 later. You cannot skip Part 6 and call
the model accepted.

**The standing constraint** ("don't run models until Rauf says so") is a
constraint on the *assistant*, not on you. You running these commands is the
authorization. If you want an assistant to run them, say so explicitly in
that session.

---

## Part 1 — Decide three things

**1. Which Mac.** A Mac Studio removes the Air's 16 GB / fanless ceiling. The
Air works but is slower and will get hot.

**2. Which base model.**

| Trainer | `-m` value | Note |
|---|---|---|
| Air, 16 GB | `mlx-community/Qwen3-4B-4bit` | The Air's ceiling. |
| Mac Studio, 32 GB+ | `mlx-community/Qwen3-8B-4bit` *(default)* | Matches the `qwen3:8b` baseline Part 6 will measure, so the comparison is apples to apples. |
| Mac Studio, 64 GB+ | `mlx-community/Qwen3-8B-bf16` | The only Mac option that yields an Ollama-servable GGUF (see Part 4). Slower, ~16 GB download. |

**3. How many iterations.** mlx-lm counts optimizer steps, not epochs. At
`--batch-size 2` over 1,038 training examples, **one epoch = 519 iterations**:

| `-i` | Epochs |
|---|---|
| 600 *(default)* | ~1.2 |
| 1040 | ~2 |
| **1560** | **~3 — what the CUDA bundle does by default** |

Use `-i 1560` for a run you intend to evaluate seriously. 600 is a cheap
first pass to prove the pipeline runs.

---

## Part 2 — On the **Air**: build the bundle and move it

### 2.1 Build

```bash
cd "/Users/rauf/Desktop/Desktop - rauf’s MacBook Air/Harvard/Abshaar"
./scripts/export_training_bundle.sh --target mac
```

(That directory name uses a curly apostrophe, `’`. Tab-complete it rather
than retyping it, and never locate it with `find` — a straight-apostrophe
twin exists on the Desktop for a different project.)

Expected tail:

```
Wrote training/dist/mac/
  training/dist/abshaar_mac_bundle.zip (232K)
  training/dist/abshaar_mac_bundle.zip.b64.txt (308K)

Checksums of the shippable archives:
<sha256>  training/dist/abshaar_mac_bundle.zip
```

**Write that SHA-256 down.** You will compare it after the transfer.

### 2.2 Sanity-check what you are about to carry

```bash
cat training/dist/mac/MANIFEST.md
wc -l training/dist/mac/dataset/*.jsonl
```

Expect exactly four files — 1038 train, 143 valid, 143 eval, 50 probes — and
nothing else from the corpus. If you see any other data file in `dataset/`,
stop: something has gone wrong with the rights gate.

### 2.3 Move it to the Trainer — pick one

**AirDrop / USB / iCloud (simplest):** send
`training/dist/abshaar_mac_bundle.zip`.

**Email (needs the `.txt`):** attach
`training/dist/abshaar_mac_bundle.zip.b64.txt`, not the ZIP. Mail filters
block `.py` attachments inside archives and bounce the whole message. On the
Trainer:

```bash
base64 -D -i abshaar_mac_bundle.zip.b64.txt -o abshaar_mac_bundle.zip
```

**Verify the transfer** on the Trainer before doing anything else:

```bash
shasum -a 256 abshaar_mac_bundle.zip     # must match what 2.1 printed
```

---

## Part 3 — On the **Trainer**: run it

### 3.1 Unpack

```bash
cd ~/Downloads
unzip abshaar_mac_bundle.zip
cd mac
chmod +x *.sh          # only needed if the transfer dropped the exec bit
```

Paths with spaces are fine — that is tested.

### 3.2 The one command

```bash
./run_all.sh -r ~/abshaar-work -m mlx-community/Qwen3-8B-4bit -i 1560
```

That runs all five stages in order. **If you would rather watch each stage,
skip to 3.3.** Either way, everything lands under `~/abshaar-work`, and every
stage is resumable — see Appendix B.

### 3.3 Stage by stage (same work, more visibility)

**Stage 0 — bootstrap.** Creates the venv, installs mlx-lm, downloads the
base model into the bundle's own cache (nothing touches `~/.cache`).

```bash
./00_bootstrap.sh -r ~/abshaar-work -m mlx-community/Qwen3-8B-4bit
```

Expect, in order: a `Machine:` / `Memory:` / `Free disk:` line; `1/3 Python`
naming the interpreter it chose; `2/3` ending in a JSON blob reporting `mlx`
and `mlx_lm` versions; `3/3` downloading the model (roughly 4–5 GB for the 4-bit
8B, ~16 GB for bf16); then `Bootstrap complete`.

If it prints `This is not an Apple Silicon Mac`, you are on an Intel machine
and MLX will not work — use the Windows bundle or a different Mac.

**Stage 1 — train.**

```bash
./01_train.sh -r ~/abshaar-work -m mlx-community/Qwen3-8B-4bit -i 1560
```

mlx-lm prints a training-loss line every 25 iterations and a validation-loss
line every 100. **What to watch:** validation loss should fall for at least
the first few hundred iterations. If it rises from the very start, stop and
report it — that indicates a data or chat-template problem, not a
hyperparameter to tweak.

**Measured, 2026-08-31, first real run** — `mlx-community/Qwen3-8B-4bit`,
batch 2, 1560 iters, on an Apple Silicon Mac:

| Quantity | Value |
|---|---|
| Trainable parameters | 9.699 M of 8190.735 M (0.118%) — mlx-lm's default 16 layers |
| Speed | 0.315 it/s ≈ **3.2 s per iteration**, ~131 tokens/s |
| Peak memory | **11.0 GB** |
| Validation pass | ~65 s, every 100 iterations (15 of them) |
| Iter 1 val loss | 3.526 (this is the untrained baseline) |
| Iter 25 train loss | 2.435 |
| **Projected wall clock** | **~83 min training + ~16 min validating ≈ 100 min** |

Two things follow from those numbers. **11 GB peak** is comfortable on a Mac
Studio but close to the ceiling on a 16 GB Air — if this is the Air, expect
memory pressure and sustained heat across ~100 minutes. And mlx-lm's default
**learning rate is 1e-5**, which is conservative for LoRA (the CUDA bundle
uses 2e-4). It trains — loss fell from 3.526 to 2.435 within 25 iterations —
but if the final validation loss plateaus higher than you want, raising the
learning rate is the first lever to try on a second run, not more iterations.

The stage ends by printing the adapter's SHA-256 and writing
`~/abshaar-work/runs/<model-slug>/train_summary.json` (hyperparameters,
dataset hashes, runtime). Keep that file; Part 6 wants those numbers.

**Stage 2 — fuse, and export GGUF if the base allows it.**

```bash
./02_fuse_export.sh -r ~/abshaar-work -m mlx-community/Qwen3-8B-4bit
```

From a **4-bit** base this fuses successfully and then tells you it cannot
make a GGUF, because llama.cpp cannot read quantised MLX weights. That is
expected, not a failure — see Part 4 for what it means. From a **bf16** base
it converts and quantises to Q4_K_M and writes an Ollama `Modelfile`.

**Stage 3 — base vs tuned answers.** *Optional, and usually the longest
stage:* MLX generates one prompt at a time, and this is 193 items × 2 models.

```bash
./03_generate.sh -r ~/abshaar-work -m mlx-community/Qwen3-8B-4bit
# time-boxed variant:
./03_generate.sh -r ~/abshaar-work -m mlx-community/Qwen3-8B-4bit --limit 20 --max-tokens 256
```

These answers are **evidence, not the acceptance evaluation** — they let you
see immediately whether the tune produces sane Bulleh Shah answers or
gibberish, before you lose access to the machine. The scored comparison is
Part 6, on the Air.

**Stage 4 — pack.** Not optional if the Trainer is shared or wiped.

```bash
./04_pack_outbox.sh -r ~/abshaar-work -m mlx-community/Qwen3-8B-4bit
```

Ends with a `BEFORE YOU LOG OUT OF THIS MACHINE` banner listing, with real
sizes, exactly what to copy and in what order.

---

## Part 4 — Copy off the Trainer (exactly what)

`04_pack_outbox.sh` has already gathered everything into one place. **There
are only two things to copy, and usually only one.**

### 1. The ZIP — always

```
<work root>/abshaar_results_small.zip
```

That single file is the whole result. Verified contents:

```
adapter/<model-slug>/adapters.safetensors        ← the trained weights
adapter/<model-slug>/adapter_config.json         ← rank / layer count
adapter/<model-slug>/000NNNN_adapters.safetensors  (periodic checkpoints)
train_summary.json                               ← hyperparameters, dataset SHA-256, runtime
logs/train-<timestamp>.log                       ← the loss curve
generations/base_eval.jsonl                      ← only if you ran stage 3
generations/base_probes.jsonl
generations/tuned_eval.jsonl
generations/tuned_probes.jsonl
SHA256SUMS.txt                                   ← to verify the copy landed
```

**On size:** mlx-lm writes a checkpoint into the adapter folder every 200
iterations, so a 1560-iteration run leaves 7 of them plus the final weights —
eight copies of the adapter. They are kept by default because they let you
fall back to an earlier checkpoint if validation loss turned upward. If you
just want to email the thing, re-run the stage with `--slim`:

```bash
./04_pack_outbox.sh -r ~/abshaar-work -m mlx-community/Qwen3-8B-4bit --slim
```

which drops the intermediate checkpoints and keeps the final adapter. In a
test run that took the ZIP from 81 MB to 8.6 MB.

### 2. The GGUF — only if stage 2 produced one

```
<work root>/outbox/model/*.gguf
<work root>/outbox/model/Modelfile.abshaar-bulleh
```

5–16 GB, so a drive or cloud storage, not email. This only exists if you
trained from a **bf16** base. From a 4-bit base there is no GGUF and that is
expected — the adapter is the reproducible artefact, and you can re-fuse
from a 4-bit base on the Air later without trouble (the 4-bit 8B is ~4.5 GB;
it is *bf16* fusing that the Air's 16 GB cannot do).

### What NOT to copy

Everything else under the work root is reproducible and large — leave it:

| Path | Why not |
|---|---|
| `venv/` | Rebuilt by `00_bootstrap.sh` in minutes |
| `cache/huggingface/` | The base model, re-downloadable from Hugging Face |
| `runs/<slug>/fused/` | Re-fusable from base + adapter |
| `runs/<slug>/adapter/` | Already copied into the ZIP |
| `tools/`, `downloads/`, `.stages/` | Scratch |

### Verify before you log out

```bash
cd <wherever you unpacked the ZIP> && shasum -c SHA256SUMS.txt
```

Every line must say `OK`. Then log out.

## Part 5 — On the **Air**: import the adapter

```bash
cd "/Users/rauf/Desktop/Desktop - rauf’s MacBook Air/Harvard/Abshaar"
./scripts/import_trained_adapter.sh /path/to/outbox/adapter/mlx-community_Qwen3-8B-4bit
```

It copies the adapter into `training/adapters/`, refuses if a directory of
that name already exists, and prints the SHA-256. Record that hash, the
final validation loss and the training arguments in `OFFLOADING.md` and
`training/EVAL_MATRIX.md`.

If you brought back a GGUF:

```bash
cd /path/to/outbox/model
ollama create abshaar-bulleh -f Modelfile.abshaar-bulleh
ollama list      # abshaar-bulleh should appear
```

---

## Part 6 — The acceptance gate (what is actually outstanding)

Training elsewhere does not move this. Nothing here has been run yet, and
`data/processed/training/eval_baseline.md` does not exist. All of it runs on
the **Air**. Steps 6.1–6.3 do not depend on the tune at all — you can run
them while the Trainer is training.

### 6.1 Rebuild the venv (blocking, ~10 min plus a multi-GB download)

`torch` does not import in the current `.venv` — torch 2.8.0 was installed
into a Python 3.9 venv and fails with a circular-import error.
`sentence_transformers` and `chromadb` fail the same way, so `build-index`
and every RAG command are dead until this is fixed. (`ai-check` reports these
packages as installed because it uses `importlib.util.find_spec`, which never
imports them.)

`/opt/homebrew/bin/python3.12` (3.12.13) is already on this machine, so:

```bash
cd "/Users/rauf/Desktop/Desktop - rauf’s MacBook Air/Harvard/Abshaar"
mv .venv .venv-py39-broken                       # reversible; do not rm yet
/opt/homebrew/bin/python3.12 -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -r requirements.txt        # multi-GB: torch, transformers, chromadb
.venv/bin/pip install mlx-lm
.venv/bin/python -c "import torch, sentence_transformers, chromadb, mlx_lm; print('stack ok')"
```

Only after `stack ok` prints, delete the old one:
`rm -rf .venv-py39-broken`.

Then re-run the cheap checks:

```bash
PYTHONPYCACHEPREFIX=/tmp/abshaar-pycache PYTHONPATH=src python3 -m unittest discover -s tests
./scripts/abshaar.sh validate
```

### 6.2 Build the RAG index (sustained compute — the "cool environment" step)

```bash
ollama serve &                       # if not already running
./scripts/abshaar.sh build-index
cat data/cache/chroma/manifest.json  # expect embed_model bge-m3, ~1303 records
```

This embeds the whole knowledge base. BGE-M3 is already cached (2.4 GB), so
there is no download, but this is the step that heats the machine.

### 6.3 Phase 2 gate, then the three baselines

```bash
.venv/bin/python scripts/rag_smoke_test.py --model qwen3:8b
# pass = "SMOKE TEST PASSED: 12/12 checks clean."
```

Do not proceed while it fails; `docs/17` §2 has the triage table.

```bash
./scripts/abshaar.sh run-eval --model qwen3:4b --judge qwen3:8b
./scripts/abshaar.sh run-eval --model qwen3:8b --judge qwen3:4b
./scripts/abshaar.sh run-eval --model qwen3:8b --rag  --judge qwen3:4b
```

Each appends a row to `data/processed/training/eval_baseline.md`
(50 probes per run; `docs/17` §3 estimates 30–60 minutes for all three). The
judge must differ from the model being scored. If **+RAG does not beat bare
8b on factual**, stop and investigate retrieval before trusting any later
comparison.

**No baseline rows → no accepted model. This gate is absolute.**

### 6.4 Score the tuned model (needs Part 5's `ollama create`)

```bash
./scripts/abshaar.sh run-eval --model abshaar-bulleh --judge qwen3:8b
./scripts/abshaar.sh run-eval --model abshaar-bulleh --rag --judge qwen3:8b
```

### 6.5 Decide

**Accept only if: tuned+RAG ≥ base+RAG on factual AND tuned ≥ base on
honesty.** A model that hallucinates more than base is rejected regardless of
how much better its style reads. Delete nothing either way — write the
four-row table into `training/EVAL_MATRIX.md` with the adapter SHA-256,
training arguments and dataset counts, and record the outcome truthfully in
`OFFLOADING.md`.

---

## Appendix A — Doing everything on the Air

Same commands, one machine, two changes: use
`-m mlx-community/Qwen3-4B-4bit`, and consider the thermal wrapper instead of
`run_all.sh` for the local path:

```bash
./scripts/thermal_aware_pipeline.sh status     # no side effects
touch training/RUN_AUTHORIZED                  # deliberate opt-in
./scripts/thermal_aware_pipeline.sh run
```

That runs at background scheduling priority and pauses when `pmset -g therm`
reports throttling. It also still requires §6.1's venv rebuild for its
index/eval stages.

## Appendix B — Interruptions and resuming

Every stage writes a marker in `<root>/.stages` and is skipped on re-run.
Re-running `./run_all.sh` with the same `-r` picks up where it stopped.

- Training specifically: mlx-lm checkpoints every 200 iterations; add
  `--resume` to continue from `adapter/adapters.safetensors`.
- To force a stage to redo, delete its marker, e.g.
  `rm ~/abshaar-work/.stages/train_mlx-community_Qwen3-8B-4bit`.
- Point `-r` at an external drive to keep the downloads across sessions on a
  machine that wipes itself.

## Appendix C — Troubleshooting

| Symptom | Meaning | Do this |
|---|---|---|
| `This is not an Apple Silicon Mac` | Intel | Use the Windows bundle or another Mac |
| `permission denied: ./run_all.sh` | Transfer dropped the exec bit | `chmod +x *.sh` |
| `no venv at ... run ./00_bootstrap.sh first` | Stage run out of order | Run stage 0 |
| Machine swaps hard, training crawls | Model too big for the RAM | `-m mlx-community/Qwen3-4B-4bit` |
| Validation loss rises from iteration 1 | Data or template problem | Stop; report; do not tune hyperparameters around it |
| GGUF step says it is skipping | Quantised fuse | Expected from a 4-bit base — Part 4 |
| Download stalls | HF CDN hiccup | Re-run stage 0; `snapshot_download` resumes |
| `AI stack unavailable` on the Air | Ran outside the venv, or §6.1 not done | Use `./scripts/abshaar.sh`, which prefers `.venv` |

## Appendix D — Where things land

```
~/abshaar-work/
  venv/                                    the bundle's own Python
  cache/huggingface/                       base model weights
  runs/<model-slug>/
    adapter/                               ← the artefact that matters
    fused/                                 fused model (stage 2)
    train_summary.json                     hyperparameters, hashes, runtime
  outbox/
    adapter/<model-slug>/                  copy of the adapter
    generations/{base,tuned}_{eval,probes}.jsonl
    model/*.gguf + Modelfile.abshaar-bulleh   (bf16 runs only)
    logs/  train_summary.json  SHA256SUMS.txt
  abshaar_results_small.zip                ← the thing to carry home
  .stages/                                 resume markers
```
