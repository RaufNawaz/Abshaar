# 20 — Corpus next steps

> Written 2026-08-31, after run 1 of the LoRA training showed that the
> model's quality ceiling is set by the corpus rather than by training.
> This is the work that raises the ceiling. Companion to
> `docs/15` (the model plan) and `docs/19` (the training walkthrough).

---

## 0. Why this document exists

Measured on 2026-08-31 from the live tree:

| | |
|---|---|
| Interpretive layers authored by AI | **217 of 288** (72 `ai_translation`, 72 `literary_translation`, 72 `tashreeh`, 1 `literal_gloss`) |
| Interpretive layers authored by a human | **71** — and all of them are Taufiq Rafat's published translations, not the project's own scholarship |
| Human review records | **0** |
| Poems in the archive | 72, against several hundred kafis attributed to Bulleh Shah |
| Training examples | 1,038, generated from roughly ten question templates |

Run 1 confirmed the same limit mechanically: validation loss reached its floor
in about 200 iterations while train loss kept falling. The model learned the
templates and then began memorising. **No amount of further training moves
that ceiling.** A tuned model on today's corpus is a model that reproduces
Claude's readings of 72 poems, fluently and unverifiably.

Everything below is ordered by how much it raises the ceiling per hour spent.

---

## 1. First: the review loop is not wired

Before any human review work, know this — **nothing consumes
`data/annotations/reviews.jsonl`.** It is counted in `status.py:22` and
schema-checked in `validation.py:181`, and that is all. `dataset_gen.py` draws
from poem layers, terms, themes, biographical claims, cluster relations and
witnesses; it has no notion of a human correction and no preference for
`created_by: human` over `created_by: ai`.

So today, writing fifty careful reviews would change nothing about what the
model trains on.

**Fix this before doing the review work, not after**, or the reviews sit
inert and the effort reads as wasted. Two changes, both small:

1. `markdown_entry.py` — when a corrected translation or tashreeh exists for
   an entry, serialize it as an additional layer with `created_by: human` and
   `supersedes: <original layer id>`.
2. `dataset_gen.py` — when building the `translation` and `tashreeh`
   families, prefer a human layer over an AI one for the same poem, and record
   which was used in the example's provenance.

A test should assert that a poem with a human correction never emits the AI
version for that family. Until that test exists, the loop is not closed.

Estimated effort: half a day, and it is the prerequisite for everything in §2.

---

## 2. The five-poem gold slice

The highest-value work in the project, deferred since it began.

**Recommended slice** (from `OFFLOADING.md` §7 — a recommendation, not yet a
recorded decision, so confirm or revise before starting):

| Entry | Why this one |
|---|---|
| `bulleh_shah_0002` | Alif/foundational vocabulary; sets the terminology precedent |
| `bulleh_shah_0029` | Ranjha/identity; cross-source comparison with 0001 |
| `bulleh_shah_0031` | Ritual critique; the register that is easiest to flatten |
| `bulleh_shah_0035` | Long three-spread kafi with high-uncertainty readings |
| `bulleh_shah_0038` | Very short Names couplet; tests the short-form case |

**For each, produce:**

1. Verified Shahmukhi against a real edition (see §3 — no edition is selected
   yet, which blocks true verification; until then, record what was checked
   and against what).
2. `project-latin-v1` transliteration, corrected by hand.
3. **Rauf's own literal gloss** — not AI-drafted, not Rafat's.
4. **Rauf's own literary translation.**
5. Tashreeh written or substantially rewritten by hand.
6. Key terms and themes with poet-specific meanings and `do_not_flatten_to`
   guidance.
7. A `reviews.jsonl` record using the existing schema in
   `data/templates/reviews.template.jsonl` — it already has the seven scoring
   dimensions (source fidelity, metaphor fidelity, poet-specific context,
   literary quality, beginner clarity, humility about uncertainty, citation
   discipline), a `problems[]` list, corrected text fields and a
   `publishable` flag.

**Why five and not seventy-two:** five is enough to fix the editorial
standard, expose where the AI drafts systematically fail, and give the
training set a human-authored anchor for each family. Scaling to seventy-two
without first learning what the standard is means doing it twice.

**What to watch for:** the `problems[].type` values across five poems are the
most valuable output here. If four of five reviews say `too_literal`, that is
a finding about the AI drafts as a class, and it should be recorded in
`Bulleh Shah/CORPUS_BUILD_LOG.md` — not silently fixed poem by poem.

---

## 3. Resolve the translation schema

Open since 2026-07-12 and now blocking clean work.

`# Literal Translation` in the Rafat entries holds **Rafat's published
literary translation**, serialized as `reference_translation`. The field named
`literal_gloss` therefore contains something that is neither literal nor the
project's. Exactly one genuine `literal_gloss` exists across 72 entries.

Decide and migrate:

- an explicit slot for a third-party reference translation, distinct from
- `literal_gloss` reserved for Rauf's own close rendering, and
- `literary_translation` for the polished English.

Then update the template, `markdown_entry.py`, the parser test, and
`docs/03`/`docs/08`. Do this **before** the gold slice, or the five entries
get authored into the wrong slots and have to be redone.

Also outstanding here: **no public-domain or permission-cleared comparison
edition has been selected** for verifying the visually-transcribed Shahmukhi.
Until one is, "verified" in §2 means "checked against the scan", which is
weaker and should be recorded as such rather than described as verification.

---

## 4. Confirm the 124 crosswalk classifications

An AI first pass classified all 124 Sufinama match records on 2026-08-16 with
per-record line-coverage evidence, and every one carries
`human_confirmed: false`. Run 2 of the training now trains on witness-derived
examples built from those unconfirmed relationships.

The work: read `data/annotations/crosswalk_evidence.md`, edit
`data/annotations/crosswalk_classifications.jsonl`, re-run
`abshaar apply-crosswalk-review`. Start with the two the notes flag as
genuinely uncertain — the single `possible` record (kaafi-7 vs 0007) and the
composite kaafi-44 page.

Cheaper than §2 per record, and it upgrades 289 knowledge-base records plus
the `variant_awareness` and `script_conversion` training families from
"AI-asserted" to "confirmed".

---

## 5. Question diversity

`abshaar augment-training-data --generator qwen3:8b --verifier qwen3:4b` is
implemented, gated (it aborts if the verifier rejects >30%), and **has never
been run**. Run 1's saturation at ~200 iterations is partly a diversity
problem: ten templates cannot teach ten thousand phrasings.

Requires the Mac-side AI stack, so it is blocked behind the venv rebuild in
`docs/19` Part 6. Cheap once unblocked, and it needs no human hours.

---

## 6. More poems

The 160 PunjabLibrary Gurmukhi items are the obvious corpus expansion and are
**not** currently usable: the embedded PDF text is defective (missing and
misordered characters; the page images are authoritative), and rights in the
2017 digital transcription are unknown.

Two prerequisites, in order: establish the rights position, then either
correct the extraction or re-OCR from the page images with human checking.
Neither is small. Treat this as the second phase, after the standard from §2
exists to author new entries against.

---

## 7. What not to do

- **More training runs on today's corpus.** Run 1 established the ceiling;
  run 2 tests whether the max dataset lifts it. A third run without corpus
  changes tests nothing.
- **More epochs.** Validation floored at ~200 iterations. Additional steps
  bought overfitting, measurably.
- **A larger base model.** The constraint is what the data can teach, not what
  the model can hold. A 32B model trained on the same 1,038 templated examples
  learns the same templates.
- **Publishing anything yet.** `Poems marked public: 0` is correct. Nothing
  has been human-verified, and the archive's own standard is that human
  review is the core asset.

---

## 8. Sequence

| Order | Work | Blocks | Human hours |
|---|---|---|---|
| 1 | §3 translation schema | §2 (entries would be authored into the wrong slots) | ~2 |
| 2 | §1 wire the review loop | §2 mattering at all | ~4 |
| 3 | §2 five-poem gold slice | Everything downstream; sets the standard | 15–30 |
| 4 | §4 crosswalk confirmation | Trust in witness-derived training data | 4–8 |
| 5 | §5 augmentation | — (needs the venv rebuild first) | ~0 |
| 6 | §6 corpus expansion | Needs §2's standard and a rights answer | large |

Steps 1 and 2 are code and take a day between them. Step 3 is the one that
actually changes what the model knows, and it is the one only Rauf can do.
