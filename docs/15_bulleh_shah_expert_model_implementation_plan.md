# 15 — Bulleh Shah Expert Model: Implementation Plan

> Written 2026-08-15. Goal set by Rauf: within days, have the information and
> infrastructure to start training a model that can answer anything about
> Bulleh Shah and his poetry, with Rauf's own work minimized or eliminated, and
> with each step executable by cheaper models (Claude Haiku/Sonnet tier, or
> Codex equivalents).
>
> This plan supersedes the "Next Steps" ordering in `OFFLOADING.md` §7 where
> they conflict. It does NOT supersede the safety rules in `AGENTS.md`,
> `CLAUDE.md`, or the rights constraints below.

---

## 0. Honest framing — read before executing anything

**A LoRA fine-tune alone cannot make a model that "answers anything about
Bulleh Shah."** The corpus is 72 poems, ~124 Sufinama witnesses, 11 sourced
biographical claims, and 6 timeline events. That is enough to teach a model
*style, terminology, format, and honesty*, but factual coverage must come from
**retrieval (RAG) over the corpus**, not from weights. The system that
achieves the stated goal is:

```
base open model (Qwen3)                     ← general language ability
  + RAG over a consolidated knowledge base  ← facts, always cited
  + LoRA on synthetic grounded instruction data ← domain style, honesty, format
  + honesty training (refusal/uncertainty examples) ← "I don't know" behavior
  + eval suite run before AND after training ← proof it works
```

This matches `docs/02_model_strategy.md`. The one deliberate departure from
prior plans: **human review gates are replaced by mechanical validators plus
cross-model verification**, because Rauf has asked for his work to be
minimized. The residual risks of that trade are listed in §9 and are accepted
as the cost of speed. The trained model is **private-research-only** until the
rights items in §8 are cleared.

**Known quality ceiling accepted by this plan:** the Shahmukhi originals are
visual transcriptions of calligraphic Nastaliq and remain unverified by a
native/scholarly reader. Whatever errors they contain will propagate into the
knowledge base and training data. Bracketed uncertainty annotations (e.g.
`[uncertain line — reading uncertain]`) are the corpus's honesty mechanism and
must be **preserved and propagated**, never "cleaned up."

---

## 1. Verified starting state (2026-08-15)

Checked live in the working tree, not inferred from docs:

- Branch `draft`, clean tree, 4 commits ahead of `origin/draft` (unpushed).
- 72 working entries, 72 processed records; **all 72 have complete AI-drafted
  interpretive layers** (Literary Translation, Tashreeh, Key Terms, Themes),
  committed in `2651e33`.
- `./scripts/abshaar.sh validate`: 0 errors, **34 warnings — all false
  positives.** `has_placeholder` in `src/abshaar/text.py` matches ANY
  `[bracketed text]`; the 17 flagged entries (0001, 0009, 0013, 0021, 0022,
  0023, 0028, 0029, 0032, 0035, 0042, 0053, 0058, 0060, 0061, 0062, 0066)
  contain only legitimate uncertainty annotations, supplied words, and
  `[[cross-references]]`. Zero genuine template placeholders remain. Fix the
  check, not the content (Phase 0.1).
- 19/19 unit tests pass
  (`PYTHONPYCACHEPREFIX=/tmp/abshaar-pycache PYTHONPATH=src python3 -m unittest discover -s tests`).
- Witnesses: 76 Sufinama kaafi + 48 non-kaafi (normalized, private), 160
  PunjabLibrary Gurmukhi (private, defective embedded text). Both crosswalks
  machine-generated, unreviewed.
- `data/lexicon/` and `data/annotations/` are empty; glossary/themes exist only
  inside the 72 entry files' `# Key Terms` / `# Themes` sections.
- Templates already exist for the data we need to produce:
  `data/templates/qa_pairs.template.jsonl`, `terms.template.jsonl`,
  `themes.template.jsonl`, `model_outputs.template.jsonl`.
- Hardware: **Apple M4, 16 GB RAM** (`sysctl hw.memsize` → 17179869184).
  MLX LoRA on a 4B model is comfortable; 8B at 4-bit is possible with small
  batch/short sequences (needs verification at run time).
- AI deps declared in `requirements.txt` (ollama, sentence-transformers,
  chromadb, transformers, torch). Install state: needs verification
  (`./scripts/abshaar.sh ai-check`).

---

## 2. Hard constraints (mechanically enforced, never waived)

1. **Rafat's English never enters training data or public output.** It lives
   in the reference-translation layer, `rights: copyrighted`. The training
   exporter (Phase 0.3) hard-excludes it AND runs an n-gram leak scan of every
   produced example against all Rafat text, exiting non-zero on any hit.
2. **PunjabLibrary full text stays private** (`data/processed/private/`,
   gitignored). Excluded from training export until rights are cleared. The
   160-item catalog metadata may be used.
3. **Sufinama witness text**: authorized for private research (user-attested,
   no written reference stored). Usable in the private knowledge base and
   training data; every derived record carries `source_ids`. Not publishable.
4. **Bulleh Shah originals** (any script): public domain. Unrestricted.
5. **No invented facts.** Every generated QA answer must be entailed by cited
   corpus records; the verifier pass (Phase 3.3) enforces this. Biography
   answers must reproduce the uncertainty qualifiers in
   `biographical_claims.jsonl`, not flatten them.
6. **Never modify the 72 working entries** except through Phase 0.1/0.2's
   parser-level changes, which must leave an aggregate content hash of the
   Original/Transliteration sections unchanged.
7. **Cluster-aware splits.** Records sharing a `canonical_work_id` (e.g.
   0001/0029) never straddle train/eval.

---

## 3. Phase plan

Each phase lists: executor tier, tasks, acceptance gate (a command that exits
non-zero on failure), and deliverables. Phases 0–4 are sequential; 5A/5B are
alternatives. A cheaper model runs each phase from the executor prompts in §6.
Rauf's total required actions are listed in §7 (≈15 minutes).

### Phase 0 — Safety rails and schema fixes (Day 1, ~2–3 h, cheap model)

**0.1 Fix the placeholder false positives.**
Replace the blanket `\[[^\]]+\]` regex in `src/abshaar/text.py` with matching
on the actual template placeholder sentences (see
`data/working/bulleh_shah_entry_template.md`: `[Paste or type…]`,
`[Type Latin transliteration…]`, `[AI-drafted English translation…]`,
`[Your own literary translation.]`, `[Explanation of metaphor…]`,
`[first line or working title]`, plus the JSONL template placeholders and
`yes/no/unknown` / `public-domain/permission-cleared`). Add unit tests for
both directions (template text flagged; `[uncertain line]`, `[[xref]]`,
supplied-word brackets NOT flagged). Do not edit any entry.
*Gate:* `validate` → 0 errors, 0 warnings; entry files byte-identical
(`git diff --stat` shows only `src/`, `tests/`).

**0.2 Translation-kind migration.**
`literal_gloss` currently holds Rafat's copyrighted *literary* rendering — a
data-model bug flagged in `OFFLOADING.md`. In `src/abshaar/markdown_entry.py`,
map the `# Literal Translation` section to kind `reference_translation` with
`rights: copyrighted, publishable: false, trainable: false` when its
attribution note mentions Rafat; keep `literal_gloss` reserved for genuine
literal glosses (currently none). Update the entry template,
`data/templates/poems.template.jsonl`, `tests/test_markdown_entry.py`, and
`docs/03_data_and_annotation_guide.md`. Rebuild with
`./scripts/build_all.sh`.
*Gate:* 72 records; zero records of kind `literal_gloss`; every
`reference_translation` carries `trainable: false`; tests pass; aggregate
SHA-1 of all 72 Markdown Original+Transliteration sections unchanged.

**0.3 Rights firewall.**
New module `src/abshaar/training_export.py` + CLI command
`export-training-corpus`: walks processed records, emits only layers with
`trainable != false`, tags every emitted text with `record_id`, `source_ids`,
`rights`, `uncertainty` (true if the layer contains `[uncertain`/`[torn`/
`HIGH-uncertainty` markers). Includes a leak scanner: any emitted example
sharing an 8-gram (word-level, case/punct-normalized) with any Rafat
reference-translation text → print the offending IDs and exit 1. Unit tests
with a synthetic leak.
*Gate:* command runs clean on current corpus; deliberate-leak test fails
loudly.

**0.4 Housekeeping.** Run `ai-check`; `pip install -r requirements.txt` into a
venv if missing; `ollama pull qwen3:8b` and `ollama pull qwen3:4b` (Rauf
action if Ollama isn't installed). Push the 4 waiting commits (Rauf
authorization required).

### Phase 1 — Knowledge base consolidation (Day 1–2, ~3–4 h, cheap model)

**1.1 Extract lexicon and themes from the 72 entries.**
New command `extract-lexicon`: parse each entry's `# Key Terms` and `# Themes`
sections into `data/lexicon/terms.jsonl` and `data/context/themes.jsonl`
following the existing templates; merge duplicate headwords across poems
(union of `example_poems`), keep per-poem meaning notes, set
`review_status: "ai_draft"`. Purely mechanical parsing — no generation.
*Gate:* every one of the 72 entries contributed ≥1 term or is listed in the
run report as having none; `status` shows nonzero glossary terms; JSONL
validates.

**1.2 Conservative canonical clustering (no human review needed).**
New command `build-clusters` reading both crosswalks
(`data/context/source_matches.jsonl`, `sufinama_text_source_matches.jsonl`):
auto-assign a shared `canonical_work_id` **only** for exact-score (1.0)
title+line matches (e.g. kaafi-12 ↔ `bulleh_shah_0001`, with `_0029` as
`related`); every other record becomes its own singleton cluster with
`cluster_confidence: "unreviewed"`. Output
`data/context/canonical_clusters.jsonl`. This deliberately over-fragments
rather than over-merges — safe for split hygiene, refinable later.
*Gate:* every poem entry and witness appears in exactly one cluster; the
0001/0029/kaafi-12 relation is captured; deterministic on rerun.

**1.3 Build the knowledge base.**
New command `build-kb` → `data/processed/knowledge_base.jsonl`: one record per
atomic fact — each poem layer (original, transliteration, AI translation,
literary translation, tashreeh, each key term, each theme), each biographical
claim (with its evidence-type qualifier verbatim), each timeline event, each
source, each cluster relation, plus trainable Sufinama witness layers. Fields:
`kb_id`, `kind`, `text`, `poem_ids`, `canonical_work_id`, `source_ids`,
`rights`, `trainable`, `uncertainty`, `provenance_note`.
*Gate:* record count reported and stable on rerun; zero `trainable: true`
records containing Rafat text (reuse 0.3 scanner); `validate` still clean.

### Phase 2 — RAG index and grounded answering (Day 2, ~2 h, cheap model)

**2.1** New command `build-index`: embed all KB records with BGE-M3
(`sentence-transformers`), store in Chroma under `data/cache/chroma/`
(gitignored; the KB JSONL is canonical, the index is a rebuildable cache —
per `docs/02_model_strategy.md`).
**2.2** New command `ask "<question>"`: retrieve top-k (k=8), compose a
grounded prompt (system rules: answer only from provided records, cite
`kb_id`s, reproduce uncertainty qualifiers, say "not in the corpus" when
retrieval max-score < threshold), generate via existing
`src/abshaar/ollama_client.py` with `qwen3:8b` (fallback `qwen3:4b`).
*Gate:* scripted smoke test of 10 questions with known-good record hits (e.g.
"What does Alif teach in bulleh_shah_0002?", "Where was Bulleh Shah born?" —
must surface the disputed-birthplace qualifier) plus 2 out-of-corpus questions
that must be declined. Non-zero exit if any citation is a nonexistent `kb_id`.

### Phase 3 — Training data factory (Day 2–3, ~4–6 h wall clock, mostly unattended)

Generator model: Claude Haiku via API **or** local `qwen3:8b` (zero-cost
path; slower). Verifier model: must differ from the generator (if generator is
Haiku, verify with qwen3:8b, or vice versa).

**3.1 Task families** (target ≈ 3,000–6,000 examples total from ~72 poems ×
layers × families; exact counts recorded in a manifest):

| Family | Built from | Notes |
|---|---|---|
| translation | original → AI/literary translation layers | never Rafat text |
| transliteration | Shahmukhi ↔ project-latin | mechanical pairs, high volume |
| tashreeh / explanation | tashreeh layers, per-stanza and whole-poem | medium temp |
| term meaning | lexicon records | include `do_not_flatten_to` contrasts |
| themes / comparison | theme records across poems in different clusters | |
| identification | first lines, titles, work_type, source attribution | |
| biography / history | biographical_claims + events ONLY | answer must carry the evidence qualifier |
| variant awareness | cluster relations (0001 vs 0029 etc.) | "these are witnesses of one work" |
| **honesty (≈15%)** | out-of-corpus questions, false premises ("Bulleh Shah's poem about trains…"), misattributions, questions about disputed facts | correct answer = decline / state the dispute |

**3.2 Generation.** New script `scripts/generate_training_data.(sh|ps1)` +
`src/abshaar/dataset_gen.py`: for each KB record batch, prompt the generator
with the record text + strict JSON schema (extend
`data/templates/qa_pairs.template.jsonl` with `task_family`, `generator`,
`verifier_verdict`, `split`). Malformed JSON → retry once → drop and log.

**3.3 Verification.** Second pass, different model: "Is this answer fully
supported by these records? Does it preserve uncertainty qualifiers?" →
keep only `supported`. Log rejection rate; **if >30% rejected, stop and
report** (signals a generator prompt problem, not data to push through).

**3.4 Mechanical gates (all must pass, in order):**
1. Rafat 8-gram leak scan (from 0.3) → exit 1 on hit.
2. Dedup on normalized question text.
3. Schema validation of every line.
4. Uncertainty audit: any example whose source record has `uncertainty: true`
   must contain a hedge/qualifier in its answer.
5. Cluster-aware split: hold out ~10% of clusters (not examples) as eval;
   assert zero cluster overlap between splits.

Output: `data/processed/training/{train,eval}.jsonl` +
`data/processed/training/MANIFEST.md` (counts per family, rejection rates,
generator/verifier models, gate results, exact commands).

### Phase 4 — Eval harness, baseline before training (Day 3, ~1–2 h)

New command `run-eval`: runs a model over `eval.jsonl` + a fixed 50-question
probe set (`data/processed/training/probes.jsonl`: 25 in-corpus factual, 15
honesty traps, 10 disputed-fact questions). Scoring: exact/fuzzy match where
mechanical (identification, transliteration), verifier-model rubric (0–3)
elsewhere; honesty traps scored pass/fail on declining.
**Run it on base `qwen3:4b`, base `qwen3:8b`, and `qwen3:8b`+RAG (`ask`) and
save results BEFORE any training.** No baseline → no training.
*Gate:* results file `data/processed/training/eval_baseline.md` exists with
all three columns filled.

### Phase 5 — LoRA training (Day 3–4)

**Path A (default: local, $0).** MLX on the M4:
```bash
pip install mlx-lm
python -m mlx_lm.lora --model Qwen/Qwen3-4B-MLX-4bit --train \
  --data data/processed/training --batch-size 2 --iters 600 \
  --adapter-path training/adapters/bulleh-qwen3-4b
```
(Exact model repo id and format conversion for train/eval JSONL to be
confirmed by the executor against current mlx-lm docs; record what was
actually run in the manifest. 16 GB fits 4B comfortably; attempt 8B-4bit only
if 4B trains without memory pressure.)

**Path B (quality: cloud, ~$5–20).** Axolotl QLoRA config for `Qwen3-8B`
committed to `training/axolotl_qwen3_8b.yml`; run on a rented single GPU
(e.g. RunPod/Together). Only if Path A quality disappoints and Rauf approves
the spend.

*Gate:* `run-eval` on the tuned model (and tuned+RAG). Acceptance =
**tuned+RAG ≥ base+RAG on factual scores AND ≥ base on honesty traps.** A
model that hallucinates more than base is rejected regardless of style gains.
All configs, logs, and the eval matrix committed under `training/` (adapters
gitignored if large; record SHA-256).

### Phase 6 — Assembly and serving (Day 4, ~1 h)

Fuse or serve adapter (`mlx_lm` serve, or convert to GGUF → Ollama
`Modelfile` named `abshaar-bulleh`); wire `ask --model abshaar-bulleh` so the
default interface is **tuned model + RAG + citations**. Final deliverable: a
one-command Q&A (`./scripts/abshaar.sh ask "..."`) and
`training/EVAL_MATRIX.md` comparing base / base+RAG / LoRA / LoRA+RAG.

---

## 4. What "answer anything and everything" will actually mean at the end

- Anything grounded in: 72 Rafat-selection poems (all layers), 76+48 Sufinama
  witnesses, 160 PunjabLibrary catalog items (metadata), 11 biographical
  claims, 6 timeline events, extracted lexicon/themes → answered with
  citations.
- Questions about disputed facts → answered with the dispute stated.
- Questions outside the corpus (the full kulliyāt is ~150+ kafis; we have a
  fraction) → honestly declined. **This is a feature, not a failure**; the
  honesty training exists precisely so the model says so instead of
  fabricating.
- Expanding coverage later = adding KB records and re-running Phases 1.3→3→5;
  the pipeline is the durable asset, not any single adapter.

## 5. Execution rules for cheaper models

1. Read `AGENTS.md`, `CLAUDE.md`, `OFFLOADING.md`, and this doc §0–§3 before
   any phase. Run `git status --short --branch` first; preserve concurrent
   work.
2. One phase per session. Never start phase N+1 if phase N's gate fails.
3. Every gate is a command that exits non-zero. If a gate fails, fix the
   cause or stop and report — **never weaken a gate or edit corpus content to
   satisfy a check.**
4. Every new command gets a unit test; run the full suite before finishing.
5. Update `OFFLOADING.md` (CRAFT format) and this plan's checklist (§10)
   after each phase; record exact commands, outputs, errors.
6. Anything unknown → write `Needs verification`; never invent model ids,
   flags, dates, or facts about Bulleh Shah.
7. Commit each phase as one coherent unit with a scope prefix
   (`feat:`, `data:`, `docs:`); show `git diff --stat` first; do not push
   unless Rauf asked.

## 6. Ready-to-paste executor prompts

One per phase. Paste into a fresh cheap-model session from the repo root.

> **Phase 0:** I am executing Phase 0 of
> `docs/15_bulleh_shah_expert_model_implementation_plan.md` in this repo.
> Read `AGENTS.md`, `CLAUDE.md`, `OFFLOADING.md`, and that plan's §0–§3 and §5
> first, then run `git status --short --branch`. Do tasks 0.1 (fix placeholder
> false positives in `src/abshaar/text.py` — fix the check, never the entry
> content), 0.2 (migrate the Rafat layer from `literal_gloss` to
> `reference_translation` with `trainable: false`), and 0.3 (build the
> `export-training-corpus` rights firewall with the Rafat 8-gram leak
> scanner). Every task's acceptance gate must pass; add unit tests; the 72
> entry files must remain byte-identical. Then update `OFFLOADING.md` and the
> plan's §10 checklist, and commit as one unit (do not push).

Phases 1–6 use the same prompt with the phase number and task list swapped;
each later prompt must also state: "Do not start; first verify the previous
phase's gate commands still pass."

## 7. Rauf's total required actions (everything else is delegated)

1. Authorize pushing the 4 waiting commits (or decline). ~1 min.
2. If Ollama/models are missing: install Ollama, `ollama pull qwen3:8b qwen3:4b`. ~10 min download time.
3. Decide generator model for Phase 3: Claude Haiku API (faster, small API
   cost) vs local qwen3:8b ($0, slower). Default if silent: local.
4. Decide Path A vs B at Phase 5 (default: A, $0).
5. Optional but strongly recommended: 30 minutes spot-checking 20 random
   training examples flagged in the Phase 3 manifest. Skippable; risk noted
   in §9.
6. Kick off each phase by pasting its §6 prompt.

## 8. Rights posture of the outputs

- The trained adapter, KB, and training data are **private research
  artifacts**. Sufinama-derived and PunjabLibrary-derived content keeps them
  unpublishable as-is.
- Nothing in this plan creates publishable content; the publish gate
  (`include_on_website`) stays untouched at 0 poems.
- Before ANY public release of model, data, or answers: store the Sufinama
  authorization reference, resolve PunjabLibrary edition rights, and confirm
  the Rafat firewall never leaked (re-run the scanner over all artifacts).

## 9. Accepted risks (the price of eliminating human review)

| Risk | Mitigation in this plan | Residual |
|---|---|---|
| Unverified Nastaliq transcriptions become training truth | uncertainty flags propagate to answers; HIGH-uncertainty lines carry hedges | model may state a misread word fluently; fix requires eventual native review |
| AI-drafted tashreeh/translations treated as ground truth | labeled `ai_draft` everywhere; verifier checks internal consistency only | interpretive quality capped at drafting-model quality |
| Verifier model shares generator blind spots | different model family for verify; mechanical gates for leaks/dedup/uncertainty | subtle unsupported claims can survive |
| Conservative clusters miss true variants | over-fragmentation is split-safe; relations refinable later | some eval questions may near-duplicate train items across unlinked variants |
| mlx-lm flags/model ids drift | executor must confirm against live docs and record actuals | phase 5 may need one iteration |
| 16 GB memory pressure on 8B training | default to 4B; 8B only if 4B is comfortable | quality ceiling of 4B model |

## 10. Progress checklist (executors update this)

- [x] Phase 0.1 placeholder check fixed — 0 warnings, entries untouched (2026-08-15)
- [x] Phase 0.2 reference_translation migration — gates passed (2026-08-15).
      Gate correction discovered in execution: entry 0001's literal slot is a
      GENUINE Claude-drafted literal gloss, so the expected outcome is 71
      `reference_translation` + 1 `literal_gloss`, not zero `literal_gloss`.
- [x] Phase 0.3 rights firewall + leak scanner — gates passed (2026-08-15).
      First live run caught 3 REAL leaks: the AI tashreeh of 0007/0017/0033
      quoted Rafat's rendering at ≥8 words. Fixed by paraphrasing those quotes
      in the three entries (rights correction to unreviewed AI drafts, with the
      scholarly points and attributions kept). Export: 360 trainable layers
      (72 original, 72 transliteration, 1 literal_gloss, 71 ai_translation,
      72 literary_translation, 72 tashreeh), 9 flagged uncertain.
- [ ] Phase 0.4 deps/models installed (chromadb/transformers/torch missing per
      `ai-check`; Ollama status: needs verification); push decision: authorized
      and completed 2026-08-15
- [x] Phase 1.1 lexicon + themes extracted (2026-08-15): 321 terms, 297 themes,
      every entry contributed; purely mechanical parse of Key Terms/Themes
      sections, review_status `ai_draft`.
- [x] Phase 1.2 canonical clusters built (2026-08-15): 343 clusters / 356
      members (72 entries + 76 + 48 Sufinama + 160 PunjabLibrary), 12
      multi-member. Rule strengthened during execution: ALL 1.0-score
      candidates of a witness merge (union-find), not just the top one —
      kaafi-12 scored 1.0 against BOTH 0001 and 0029, so the variant pair now
      shares `work_bulleh_shah_0001` and cannot straddle a split. Deterministic
      rerun verified.
- [x] Phase 1.3 knowledge base built (2026-08-15): 1,303 records at
      `data/processed/private/knowledge_base.jsonl` (private dir because it
      embeds Sufinama witness text). All records leak-scanned; deterministic.
- [ ] Phase 2 RAG index + `ask` command, smoke test passed
- [ ] Phase 3 training data generated, verified, gated; manifest written
- [ ] Phase 4 baseline eval saved (base 4B / base 8B / base+RAG)
- [ ] Phase 5 LoRA trained; eval acceptance met (path: ___)
- [ ] Phase 6 `ask --model abshaar-bulleh` serving tuned+RAG; eval matrix committed
