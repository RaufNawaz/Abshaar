# EVAL_MATRIX.md

Comparison of base / base+RAG / tuned / tuned+RAG for the Bulleh Shah expert
model. **The acceptance rows are not filled in yet** — they require the
Mac-side gate (venv rebuild → `build-index` → RAG smoke test → three baseline
runs), none of which has been run. See `docs/19` Part 6.

## Where the artifacts actually live

Not everything this file cites is in git, deliberately. Checked 2026-09-24:

| Artifact | Location | In git? |
|---|---|---|
| Run 1 / run 2 adapters | `training/adapters/mlx-community_Qwen3-8B-4bit{,-run2}/` | No — `training/adapters/` and `*.safetensors` are ignored (size). SHA-256 recorded in the run tables below. |
| Run 1 / run 2 training logs | `training/logs/run{1,2}-train-*.log` | **Yes**, as of 2026-09-24. The `*.log` ignore rule was LaTeX-scoped so the validation curves below are checkable against their source. |
| Run 2 `train_summary.json` | `training/logs/run2-train_summary.json` | Yes |
| Standard build (run 1's dataset) | `data/processed/training/` | Yes |
| Max build (run 2's dataset) | `data/processed/training_max/` | No — it includes Rafat's reference translations, and `probes.jsonl` carries his published English verbatim. `MANIFEST.md` and `SHA256SUMS.txt` **are** committed, so the dataset hashes below can be verified against the files on disk. |
| `run2_results.zip` | repo root | No — sealed local copy of what the training machine produced; all 5 checksums re-verified 2026-09-24 against the imported files. |

To re-verify the run 2 dataset: `cd data/processed/training_max && shasum -a 256 -c SHA256SUMS.txt`.

## Training runs

### Run 1 — 2026-08-31

| Field | Value |
|---|---|
| Base model | `mlx-community/Qwen3-8B-4bit` |
| Toolchain | mlx-lm, LoRA rank 8, 16 layers, 9.699 M trainable params (0.118%) |
| Dataset | standard build, 1,038 train / 143 valid (`train.jsonl` sha256 `c8aa7676…`) |
| Hyperparameters | batch 2, lr 1e-5, adam, max_seq_length 2048, mask_prompt **false** |
| Planned / actual iterations | 1560 planned, **stopped at ~800** |
| Adapter kept | iteration 600 checkpoint |
| Adapter sha256 | `ec67f93d8224f1c83285eb76f13a8e98012ac41a8ca8b821f3858d67cdca7b17` |
| Peak memory | 24.4 GB |
| Speed | 0.315–0.435 it/s (~3.2 s/iter), ~131–144 tokens/s |

Validation curve (val_batches 25 = a random 50 of 143 examples each time, so
individual points are noisy — see the note below):

| iter | val | train | gap |
|---|---|---|---|
| 1 | 3.526 | — | — |
| 100 | 1.437 | 0.969 | +0.468 |
| 200 | **1.389** | 0.900 | +0.489 |
| 300 | 1.528 | 0.862 | +0.666 |
| 400 | 1.553 | 0.742 | +0.811 |
| 500 | 1.458 | 0.666 | +0.792 |
| 600 | **1.305** | 0.811 | +0.494 |
| 700 | 1.313 | 0.757 | +0.556 |
| 800 | 1.518 | 0.390 | +1.128 |

**Reading:** 94% of the improvement arrived by iteration 100. After that,
validation never improved meaningfully while train loss fell 0.969 → 0.390
and the train/val gap widened 0.468 → 1.128. That gap, not any single
validation point, is the overfitting evidence — the points themselves swing
±0.1 because each scored a different random third of the validation set.
Iteration 600 (1.305) and iteration 200 (1.389) are statistically
indistinguishable; 600 was kept as the lowest observed.

Log: `training/logs/run1-train-20260831-160232.log`.

### Run 2 — 2026-08-31, completed

| Field | Value |
|---|---|
| Base model | `mlx-community/Qwen3-8B-4bit` |
| Warm start | run 1's iteration-600 adapter |
| Dataset | max build, 1,576 train / 207 valid (Rafat + Sufinama witnesses included) |
| Hyperparameters | batch 2, lr 1e-5, **mask_prompt true**, **max_seq_length 4096**, **val_batches 103 (whole set)** |
| Iterations | 400 (~0.51 epochs) |
| Adapter kept | **iteration 400 — the final one** |
| Adapter sha256 | `66c1239724991c1c907cc2fa9a76a7f82427962dbfdf3ad8cfe70a8cff6fe85b` |
| Dataset sha256 | train `6def930a…` / valid `9b8a4e25…` |
| Runtime | 66 min — 36 min training (5.4 s/iter) + 30 min validating |
| Peak memory | **54.438 GB** — read from the log 2026-09-24, not previously recorded |
| Environment | mlx 0.32.2, Python 3.11.3, macOS 14.7.2 arm64 |
| Log | `training/logs/run2-train-20260831-172050.log` |

| iter | val | change |
|---|---|---|
| 1 | 1.343 | — (this is run 1's adapter, scored on run 2's terms) |
| 100 | 1.218 | −0.125 |
| 200 | 1.189 | −0.029 |
| 300 | 1.185 | −0.004 |
| 400 | **1.178** | −0.007 |

**Monotonically decreasing at every point** — a different character from run 1's
1.305/1.553/1.389 oscillation, and the direct result of validating over the
whole 207-example set instead of a random 50. The curve is now readable.

**Run 2 beats run 1 by 12.3%, measured identically.** The iteration-1 value
(1.343) is run 1's adapter evaluated on run 2's validation set with run 2's
masked loss, so 1.343 → 1.178 is a like-for-like comparison rather than a
cross-run one. Caveat that only strengthens it: run 2's eval split was drawn
from a different cluster pool and may contain material run 1 trained on, which
would flatter run 1 — unverified, and run 1 lost anyway.

**Converged.** The first 100 iterations delivered 76% of the total gain; the
last 200 delivered 0.011. A run 3 is not worth its wall clock — the lever is
corpus work (`docs/20`), not more steps.

No overfitting signature: validation never turned up, unlike run 1. The larger
dataset genuinely had more to teach, which is the first empirical support for
the max build being worth it.

**Peak memory climbed all run, and ended at 54.4 GB** (16.9 GB at iter 25 →
22.3 at 50 → 41.6 at 100 → 54.4 from iter 225 on). Same mechanism as run 1 —
MLX's peak tracks the longest sequence seen so far — but more than double run
1's 24.4 GB, because `max_seq_length` 4096 stops truncating the long kafis.

Two consequences. Run 2 could not have run on the 16 GB Air under any
batching; at 4096 tokens this recipe needs a 64 GB-class machine, so training
stays off-machine. And the figure only stabilised after iteration 225, which
is late — any memory number read before then understates by 3x.

Cost: 66 minutes total — 36 training, 30 measuring. Time per iteration rose
3.2 s → 5.4 s because `max_seq_length` 4096 stops truncating the long kafis,
which is the point. The 30 minutes of validation is what bought a readable
curve, and it is the reason the checkpoint choice was trivial this time.

### Run 3 — not recommended

Changes, each with a reason from run 1 rather than a guess:

| Change | Why |
|---|---|
| Dataset → max build (1,576 / 207) | Run 1 saturated in ~200 iterations; the lever is more and more varied data, not more steps |
| `--mask-prompt` on | Run 1 computed loss over the question as well as the answer |
| `--max-seq-length` 4096 | 2048 truncated the longest examples mid-answer |
| `--val-batches` = whole set | 25 batches scored a random third, making the curve unreadable |
| `--eval-every 100` with matching saves | Run 1 saved every 200 while validating every 100, so half the minima had no checkpoint |
| ~400 iterations, lr 1e-5 | Both from run 1's curve, not from assumption |
| Warm start from run 1's iteration-600 adapter | Builds on the run rather than repeating it |

## Run 2 served, without RAG — 2026-09-24

First time the tuned adapter answered anything. `mlx_lm generate` with
`--adapter-path training/adapters/mlx-community_Qwen3-8B-4bit-run2` against the
4-bit base. **Peak memory 4.8 GB, ~17 tokens/sec** — inference fits the 16 GB
Air with room to spare, against 54.4 GB to train it.

**It fabricates citations.** Asked who Bulleh Shah's murshid was "and what does
the archive cite for that", it named Shah Inayat of Qasur correctly, then
attributed that to:

> *Bulleh Shah: The Sufi Poet of Pakistan* (2006) by Asma Afsar Abbas and
> *Bulleh Shah: The Sufinama* (1997) by Shah Inayat of Qasur himself

Neither exists. `grep -ri` finds "Asma Afsar Abbas" and "The Sufinama (1997)"
nowhere in the repository; the archive's seven real sources are Rafat's
Vanguard selection, four Rekhta/Sufinama records, Ashna Hussain's thesis, the
PunjabLibrary Kafian PDF and the Punjab Auqaf shrine page. The second invention
is self-refuting — Shah Inayat died around 1728 and cannot have authored a 1997
book — and the model delivered both in the archive's own voice: "This is stated
in the archive's records."

It also degenerates. On the Ranjha couplet it repeated one sentence for the
full 400-token budget.

**What this settles.** The corpus ceiling recorded in `docs/20` is not an
abstraction: LoRA on 1,576 templated examples taught register and confidence
without teaching a single verifiable fact, so the model reaches for
bibliography-shaped text and invents it. This is the failure mode RULE 2 exists
to prevent, arriving from the model rather than from an agent.

It also justifies the ordering: base + RAG declined the 1947 question on the
substance and cited eight real retrieved ids; tuned-without-RAG invented two
sources on a question it half-knew. **Nothing tuned should be served without
retrieval and the citation gate in front of it.** The gate already catches this
class — it rejected `kb:bio_claim_bulleh_shah_inayat:original` from base+RAG in
the same session — but it only runs on the `ask` path, which the tuned model is
not yet wired into.

Outputs: `training/rag_outputs/answers_tuned_norag.md` (gitignored; regenerate
with `./scripts/rag_pipeline.sh --redo 7 7`).

## Acceptance rows — NOT YET MEASURED

| Model | factual | honesty | notes |
|---|---|---|---|
| `qwen3:8b` base | — | — | blocked: baselines never run |
| `qwen3:8b` + RAG | — | — | blocked: `build-index` needs the venv rebuild |
| tuned | — | — | needs the fuse/serve step |
| tuned + RAG | — | — | |

**Acceptance criterion (plan §3 Phase 5, verbatim): tuned+RAG ≥ base+RAG on
factual AND tuned ≥ base on honesty.** A model that hallucinates more than
base is rejected regardless of style gains.
