# START HERE — The Abshaar One-Stop Guide

> This is your command center. Open it at the start of every work session.
> It tells you **where the project stands, what to do next, how to run everything,
> what to learn, and how to do the editorial work** — without needing to dig
> through the other docs first.
>
> Last updated: **2026-07-12**
> If you only read one file in this repo, read this one.

---

## 0. How to use this document

This guide is split into six parts. You don't read it front-to-back every time.
You jump to the part you need:

| If you want to… | Go to |
|---|---|
| Remember what this project even is | [Part 1 — The project in 60 seconds](#part-1--the-project-in-60-seconds) |
| Know what to do *right now* | [Part 2 — Where things stand & your next moves](#part-2--where-things-stand--your-next-moves) |
| Understand how the machine fits together | [Part 3 — The mental model](#part-3--the-mental-model) |
| Actually run the tools | [Part 4 — The workflow & command playbook](#part-4--the-workflow--command-playbook) |
| Do the poem/sourcing/translation work | [Part 5 — The editorial & sourcing track](#part-5--the-editorial--sourcing-track) |
| Learn the technical skills (from scratch) | [Part 6 — The learning track](#part-6--the-learning-track) |
| Look something up fast | [Appendix — Quick reference](#appendix--quick-reference) |

Two house rules carried over from `AGENTS.md`:

1. **Use whichever shell matches your current machine.** Commands below are
   shown in PowerShell (Windows); on macOS/Linux use the matching `.sh` script
   in `scripts/` — see [4.1](#41-one-time-setup-only-if-not-already-done) —
   the arguments are identical either way.
2. **After any substantive work, update `OFFLOADING.md`.** That file is the
   "save game" that lets you (or any AI assistant) resume without re-explaining
   everything.
3. **Codex and Claude share the live working tree.** Before editing, read
   `OFFLOADING.md`, inspect `git status` and the target-file diff, and preserve
   pre-existing changes. After running anything that changes project state,
   update the affected canonical docs and the handoff before stopping.

---

## Part 1 — The project in 60 seconds

**Abshaar is a local-first, open-source archive and AI-assisted *interpretation*
system for South Asian mystical poetry** (Punjabi, Urdu, Persian-influenced,
Braj/Bhakti, Sufi). It is **not** a one-click translator.

The single most important idea:

> A poem is a layered cultural object, not ordinary text. Abshaar keeps the
> layers **separate and visible**: original script → transliteration → private
> reference (when legally allowed) → AI draft → human literal gloss → human
> literary translation → *tashreeh* (explanation) → glossary → poet context
> → sources. The reader always sees what is fact, draft, and interpretation.

The second most important idea:

> **The model is not the project.** The corpus, the annotations, the
> source-grounding, and the human review are worth as much as any model. A great
> model on a weak dataset still sounds shallow. So: **archive first, AI second.**

The first concrete target is a **Bulleh Shah Explorer**: select ~10–20 works from
the 72-entry working corpus and turn them into carefully verified, rights-safe,
human-reviewed entries with original text, transliteration, translation layers,
glossary, tashreeh, and source-grounded Q&A.

---

## Part 2 — Where things stand & your next moves

### 2.1 Current state (verified 2026-07-12)

The **infrastructure and first source corpus are built; editorial review is now
the bottleneck.** Running `./scripts/abshaar.sh status` on macOS reports:

| Thing | Count |
|---|---|
| Working Markdown entries | 72 |
| Processed poem records | 72 |
| Poems marked public | 0 |
| Glossary terms | 0 |
| Sources | 7 |
| People / events / themes | 1 / 6 / 0 |
| Human reviews | 0 |
| Model outputs | 0 |
| Sufinama catalog items | 76 paired Roman/Urdu records |
| Sufinama non-kaafi text items | 48 category witnesses |
| PunjabLibrary Gurmukhi catalog items | 160 numbered records |
| Sourced biographical claims | 11 |
| Sufinama content categories inventoried | 13 |
| Source-manifest matches awaiting review | 76 kaafi + 48 non-kaafi candidate records |
| Validation errors / warnings | 0 / 144 |

Corpus composition:

- `bulleh_shah_0001`: Sufinama pilot, original + transliteration; interpretation
  is unfinished and it does not yet have the newer `# AI Translation` section.
- `bulleh_shah_0002` through `_0072`: all 71 poems from Taufiq Rafat's
  *Bulleh Shah: A Selection*; Shahmukhi was visually transcribed from calligraphic
  pages, transliterations and Claude translations were drafted, and Rafat's
  copyrighted English is retained only as gated private reference material.
- All 72 entries remain `draft`, non-public, and barred from model training.
- The 144 warnings are intentional duplicate placeholder warnings: once for each
  unfinished Markdown entry and once for each generated JSONL record.

The Python CLI, Markdown→JSONL parser, validation, website export, prompt-pack
builder, Sufinama acquisition/matching pipeline, Gurmukhi PDF importer, and
optional Ollama integration exist. Nineteen unit tests pass. Structural
validation cannot verify Shahmukhi accuracy, translation quality, copyright
permission, or interpretive soundness.

The `build_all` wrappers were fixed on 2026-07-12 and now preserve all 72 draft
records by passing `--include-placeholders`.

The first internet-research pass now documents 11 claim-level biographical
statements and 6 cautious timeline events. It also inventories 13 Sufinama
content categories. The central caution is that both the biography and corpus
are partly reconstructed from later sources and performance transmission;
Sufinama's category counts overlap and are not unique-work totals.

### 2.2 Open decisions that block real progress

- [x] **Private repository and build safety.** Rauf confirmed the repository is
      private. Both full-build wrappers now preserve unfinished entries.
- [x] **Complete Sufinama acquisition.** The corpus now has 76 normalized
      witnesses, 152 cached raw snapshots, zero fetch/parse errors, seven
      source-unavailable requested views, and a regenerated full-text crosswalk.
- [x] **Acquire non-kaafi Sufinama texts.** The corpus now also has 48
      source-category witnesses with zero fetch/parse errors, 41 honest
      source-unavailable language views, and a separate review-only crosswalk.
- [ ] **Pilot selection.** Choose 5 poems representing short/long forms, easier
      and harder transcriptions, and core themes. Do not try to review all 72 at
      once.
- [ ] **Source verification edition.** Select a public-domain or
      permission-cleared Kulliyat/edition against which to verify the visually
      transcribed Shahmukhi, especially files containing explicit
      high-uncertainty readings.
- [ ] **Translation-field semantics.** The current `literal_gloss` JSON field
      stores Rafat's literary reference translation for entries 0002–0072, not a
      true literal gloss. Decide and migrate to an unambiguous schema before
      creating review or training data.
- [ ] **Transliteration and review standards.** Formalize `project-latin-v1` and
      the 1–5 review rubric before scaling human review.

### 2.3 Your next 5 moves (do these in order)

1. **Review the generated source crosswalk** for exact matches, variants,
   excerpts, duplicates, and Sufinama-only works. Never overwrite a witness.
2. **Add canonical-work clusters.** Assign a stable `canonical_work_id` only
   after reviewing the witness relationships; split training/evaluation data by
   cluster so variants cannot leak across partitions.
3. **Choose a 5-poem vertical slice.** Record the selected IDs and why each was
   chosen in `OFFLOADING.md` or a dedicated editorial plan. Include at least one
   short poem, one long poem, one core Bulleh Shah theme, and one uncertain text.
   A balanced starting proposal is 0002, 0029, 0031, 0035, and 0038; confirm it
   before editing because it has not yet been approved by Rauf.
4. **Freeze the editorial contract.** Write the `project-latin-v1` rules, define
   the three translation fields precisely, and turn the review rubric into a
   reusable checklist/record format.
5. **Verify and fully annotate poem 1 of the slice.** Cross-check Shahmukhi
   against an approved edition; correct transliteration; write Rauf's literal
   gloss, literary translation, tashreeh, key terms, themes, and review record.
After each source or poem batch, rebuild and validate:
   ```bash
   ./scripts/abshaar.sh build-data --include-placeholders
   ./scripts/abshaar.sh validate
   PYTHONPATH=src python3 -m unittest discover -s tests -v
   ```
   Then update every affected guide/template plus `OFFLOADING.md` and repeat the
   review workflow for the remaining four pilot poems.

### 2.4 The milestone ladder

You always know what "stage" you're in by which rung is true:

| Rung | Definition of done | You're here when… |
|---|---|---|
| **Transcription corpus** | 72 structurally valid draft entries | **complete** |
| **Reviewed vertical slice** | 5 verified, fully annotated poems + review records | *(next up)* |
| **Gold corpus MVP** | 20 works + 20 glossary terms + 10 events + 10 themes + 10 source notes + 50 grounded Q&A pairs | corpus is real and reviewable |
| **AI pipeline** | baselines compared; RAG answers cite notes | you can ask a question and get a sourced answer |
| **Website MVP** | Bulleh Shah Explorer with 10–20 polished poems + search + feedback | the project is public |
| **Fine-tune** | a small LoRA on 500–2,000+ reviewed examples | only after lots of review data exists |

Do **not** skip rungs. Fine-tuning before you have reviewed data makes the model
worse, not better.

---

## Part 3 — The mental model

### 3.1 The eight layers

Abshaar is built in layers. The MVP only needs the first few; the rest come later.

| Layer | What it does | Need it for MVP? |
|---|---|---|
| Corpus | stores original poems, metadata, sources | **Yes — now** |
| Transliteration | Latin reading aid alongside the script | **Yes — now** |
| Translation | literal + literary English | **Yes — now** |
| Interpretation | tashreeh: metaphor, Sufi/cultural context | **Yes — now** |
| Retrieval (RAG) | fetches approved notes before answering | **Yes — soon** |
| Human review | people correct drafts; corrections become data | **Yes — ongoing** |
| Fine-tuning | teaches a model your house style | No — much later |
| Website | makes it public and usable | After corpus is strong |

### 3.2 The golden rule of the workflow

> **Humans edit Markdown. Computers read JSONL.**

You type poems into friendly Markdown files in `data/working/`. The automation
converts them into machine-friendly JSONL in `data/processed/`. You never
hand-write JSONL.

### 3.3 The pipeline (how a poem travels)

```text
You type a poem in Markdown        data/working/bulleh_shah_0001.md
   │  build-data
   ▼
Structured record                  data/processed/poems.jsonl
   │  validate           (catches missing fields, placeholders, unsafe publishing)
   ▼
Prompt pack                        data/cache/prompt_packs/bulleh_shah_0001.json
   │  draft (optional, local AI via Ollama)
   ▼
Model draft (needs_review)         data/annotations/model_outputs.jsonl
   │  human review        (you correct it; correction is the real asset)
   ▼
Reviewed data                      data/annotations/reviews.jsonl
   │  export-site         (only publishable, rights-cleared poems go public)
   ▼
Website JSON                       data/site/*.json  →  the public site
```

### 3.4 The model stack (what plays each role)

You do **not** train these. You use existing open models.

| Job | Tool | Why |
|---|---|---|
| Baseline translation | **IndicTrans2** (fallback: **NLLB-200**) | built for Indic languages; gives a literal starting point, not the final answer |
| Interpretation / tashreeh | **Qwen3** via **Ollama** (local) | strong multilingual instruction-following, runs on your machine, Apache-2.0 |
| Retrieval (search by meaning) | **BGE-M3** embeddings + **Chroma** | multilingual; good for Urdu/Punjabi/Persian |
| Fine-tuning (later) | **LoRA / QLoRA** | adapts style cheaply, only after enough reviewed data |

Website plan of record (per the repo docs): a **static Astro site on GitHub
Pages**. (The 63-page roadmap also mentions Gradio/Next.js+FastAPI as faster or
heavier alternatives — fine as a quick demo, but the committed path is static.)

---

## Part 4 — The workflow & command playbook

### 4.1 One-time setup (only if not already done)

**Windows (PowerShell):**

```powershell
cd "D:\Harvard\Poetry Model Project"

# Optional: a clean Python environment (Python 3.11+)
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip

# Local AI (only when you reach the AI step)
# Install Ollama from https://ollama.com/ then:
ollama pull qwen3:8b      # use qwen3:4b on a weaker laptop, qwen3:14b on a strong one
```

If PowerShell blocks the project scripts, prefix any command with
`powershell -ExecutionPolicy Bypass -File`, e.g.:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\abshaar.ps1 status
```

The `scripts\abshaar.ps1` wrapper sets things up for you, so you don't need to
install the package to use the CLI.

**macOS (zsh/bash):**

```bash
cd ~/Harvard/"Poetry Model Project"

# Optional: a clean Python environment (Python 3.11+)
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip

# Local AI (only when you reach the AI step)
# Install Ollama from https://ollama.com/ then:
ollama pull qwen3:8b      # use qwen3:4b on a weaker laptop, qwen3:14b on a strong one
```

If `./scripts/abshaar.sh` isn't executable, run `chmod +x scripts/*.sh` once.
The `scripts/abshaar.sh` wrapper mirrors `abshaar.ps1` — same arguments, same
behavior, no need to install the package to use the CLI.

### 4.2 Every command, what it does, when to use it

Run all of these from the repo root. Shown in PowerShell; on macOS/Linux
substitute `./scripts/abshaar.sh` for `.\scripts\abshaar.ps1` — the arguments
are identical.

| Command | What it does | When |
|---|---|---|
| `.\scripts\abshaar.ps1 init` | creates expected folders | first time / if folders missing |
| `.\scripts\abshaar.ps1 status` | counts everything + validation summary | start of every session |
| `.\scripts\abshaar.ps1 new-entry --title "First line"` | makes a new Markdown poem from the template; auto-numbers the ID | starting a new poem |
| `.\scripts\abshaar.ps1 build-data` | converts `data/working/*.md` → `data/processed/poems.jsonl` | after editing entries |
| `.\scripts\abshaar.ps1 validate` | checks structure, placeholders, duplicate IDs, broken JSONL, unsafe publishing | after every change |
| `.\scripts\abshaar.ps1 export-site` | writes public JSON to `data/site/` | when poems are publishable |
| `.\scripts\abshaar.ps1 prompt-pack --poem-id bulleh_shah_0001` | builds the AI prompt bundle for one poem (add `--all` for every poem) | before drafting with AI |
| `.\scripts\abshaar.ps1 ai-check` | checks if Ollama + AI packages are ready | before any AI step |
| `.\scripts\abshaar.ps1 draft --poem-id bulleh_shah_0001 --model qwen3:8b` | sends the prompt pack to local Ollama, saves a draft marked `needs_review` | to get an AI first draft |
| `.\scripts\abshaar.ps1 acquire-sufinama --discover-only` | discovers and UUID-pairs the 76 Roman/Urdu Sufinama catalog items | before a source acquisition |
| `.\scripts\abshaar.ps1 acquire-sufinama --transport curl` | caches and normalizes authorized Sufinama Urdu plus two Roman layers, then builds a crosswalk | to refresh the Sufinama witness corpus |
| `.\scripts\abshaar.ps1 acquire-sufinama --offline --transport curl` | rebuilds normalized witnesses, audit statistics, and matching outputs from the saved catalog/cache | after parser or matcher changes; no site requests |
| `.\scripts\abshaar.ps1 acquire-sufinama-texts --discover-only --transport curl` | discovers the 48 kalaam/doha/shabad/dohra/athvara/barahmasa/holi category records | before refreshing the non-kaafi source layer |
| `.\scripts\abshaar.ps1 acquire-sufinama-texts --offline --transport curl` | rebuilds the 48 non-kaafi witnesses and their separate crosswalk from cache | after parser or matcher changes; no site requests |
| `.\scripts\abshaar.ps1 match-source-manifest --manifest <path>` | matches any local source manifest to the 72 working entries without overwriting them | after importing another source collection |
| `.\scripts\abshaar.ps1 extract-gurmukhi-pdf --input <pdf>` | extracts consecutively numbered Gurmukhi works into a private witness plus reviewable catalog | after receiving a local Gurmukhi source PDF |
| `.\scripts\abshaar.ps1 export-training-corpus` | exports rights-safe trainable layers; **fails loudly** if any text overlaps a copyrighted reference translation | before building training data |
| `.\scripts\abshaar.ps1 extract-lexicon` | mechanically parses every entry's Key Terms/Themes into `data/lexicon/terms.jsonl` + `data/context/themes.jsonl` | after entry Key Terms change |
| `.\scripts\abshaar.ps1 build-clusters` | builds conservative canonical-work clusters from the crosswalks (only exact 1.0 matches merge) | after crosswalks or matcher change |
| `.\scripts\abshaar.ps1 crosswalk-evidence` | writes deterministic two-way line-coverage evidence + alignments for every crosswalk match record to `data/annotations/crosswalk_evidence.md` | before classifying or reviewing crosswalk matches |
| `.\scripts\abshaar.ps1 apply-crosswalk-review` | applies `data/annotations/crosswalk_classifications.jsonl` onto both match files; refuses malformed/incomplete/out-of-taxonomy input | after editing a classification decision |
| `.\scripts\abshaar.ps1 build-kb` | consolidates poem layers, lexicon, biography, witnesses into the private knowledge base (leak-scanned) | after any KB input changes |
| `.\scripts\abshaar.ps1 build-index` | embeds the knowledge base with BGE-M3 into the local Chroma index (needs `.venv` AI stack) | after `build-kb` |
| `.\scripts\abshaar.ps1 ask "question"` | grounded retrieval + local-Ollama answer with kb citations; declines out-of-corpus questions | to query the archive |
| `.\scripts\abshaar.ps1 generate-training-data` | builds the templated train/eval instruction dataset with all gates (leak scan, dedup, hedging, cluster-safe split) | after KB or lexicon changes |
| `.\scripts\abshaar.ps1 build-probes` | builds the fixed 50-probe eval set (factual/honesty/disputed) | once per eval design |
| `.\scripts\abshaar.ps1 run-eval --model qwen3:8b [--rag]` | scores a model over the probes into `eval_baseline.md` | before AND after any fine-tune |
| `.\scripts\abshaar.ps1 export-mlx-dataset` | writes messages-only train/valid JSONL for `mlx_lm.lora` | before local LoRA training |
| `./scripts/train_lora.sh` (macOS only) | runs the local MLX LoRA fine-tune on Apple Silicon | Phase 5 of the training plan |

The training-pipeline commands follow
`docs/15_bulleh_shah_expert_model_implementation_plan.md` — read its §0 and
§2 (rights constraints) before running any of them.

Useful flags:

- `new-entry --id bulleh_shah_0020` — set the ID manually instead of auto.
- `new-entry --poet-id shah_hussain` — start a different poet.
- `build-data --include-placeholders` — include unfinished entries. This flag is
  currently required to preserve the 72-entry draft corpus.
- `prompt-pack --all` — build packs for every processed poem.

### 4.3 The two loops you'll actually run

**Daily editorial loop** (no AI needed). Windows shown; macOS/Linux: swap in
`./scripts/abshaar.sh`.

```powershell
.\scripts\abshaar.ps1 status          # where am I?
.\scripts\abshaar.ps1 new-entry --title "..."   # if starting a poem
# ...edit the Markdown file in data/working/...
.\scripts\abshaar.ps1 build-data --include-placeholders
.\scripts\abshaar.ps1 validate        # fix every error; clear placeholder warnings
```

**Full local build:** both wrappers preserve placeholder-bearing drafts by
calling `build-data --include-placeholders`.

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\build_all.ps1
```

macOS/Linux:

```bash
./scripts/build_all.sh
```

That runs, in order: `init` → `validate` → `build-data` → `validate` →
`export-site` → `status`.

### 4.4 Running the tests

```powershell
$env:PYTHONPATH = "src"
py -m unittest discover -s tests
```

### 4.5 What `validate` actually checks (and what it does NOT)

It checks: missing required fields, empty original text, empty transliteration,
missing literal/literary translation, leftover placeholder text, broken JSONL,
duplicate IDs, and **unsafe publication settings** (a poem can only be public if
its `rights_status` is `public-domain`, `permission-cleared`, or
`project-original`).

It does **not** judge whether a translation is accurate, whether a metaphor is
read correctly, or whether a source is trustworthy. **That is your job.** Think of
`validate` as a spell-checker for structure and safety, not for meaning.

### 4.6 Git basics (your project's memory)

```powershell
git status            # what changed
git add <exact-files> # stage only intended files; avoid broad staging
git commit -m "Add first Bulleh Shah pilot entry"
git push              # send to GitHub
```

Commit after each meaningful chunk of work. The commit message is a note to your
future self about *why* something changed.

---

## Part 5 — The editorial & sourcing track

This is the part the ML roadmap mostly assumes you already know. **It is the real
bottleneck of the project.** Great ML cannot rescue a thin or unsafe corpus.

### 5.1 The layers you produce for every poem

Keep these strictly separate. Never let one silently replace another.

| Layer | What it is | The trap to avoid |
|---|---|---|
| **Original** | the poem in its source script (Shahmukhi, Gurmukhi, etc.) — the authority | replacing it with transliteration |
| **Transliteration** | a Latin reading aid for people who can't read the script | treating it as "the text" |
| **Reference translation** | a cited comparison text, kept private when copyrighted | mistaking a literary rendering for a literal gloss or publishing it without permission |
| **AI translation** | a clearly labeled model draft for human review | treating model output as approved scholarship |
| **Literal gloss** | Rauf's plain, close English meaning, line by line | smuggling in interpretation |
| **Literary translation** | Rauf's readable English that keeps poetic force | flattening the imagery |
| **Tashreeh** | explanation of metaphor, culture, Sufi meaning, ambiguity | stating one reading as the only truth |

### 5.2 Sourcing & copyright (the rule that protects the project)

Classical poems may be public domain, but **modern editions, translations,
annotations, recordings, and website metadata often are not.**

**Safe to use:** public-domain editions; your own translations; your own
annotations; permission-cleared material; short bibliographic metadata with
attribution; source links and citations.

**Do not:** acquire or redistribute a collection outside its authorization
scope; mix private notes into public files; or erase which source supplied which
text. Rauf has stated that the current Sufinama bulk acquisition is an authorized
collaborative research task, so it may proceed as a private, attributed source
witness dataset. Public release remains a separate decision.

> Ajab Shahar and similar sites are excellent **design/editorial references**, but
> their work is copyrighted unless stated otherwise. Learn from the structure;
> don't ingest the content.

For every source, record: name, editor/author, year, URL or citation, **rights
status**, and **allowed uses** — *before* you mark anything publishable. Private,
unpublishable material goes in `data/raw/private/` (Git-ignored).

### 5.3 The transliteration standard (`project-latin-v1`)

**Decided 2026-08-15 — the normative spec is `docs/16_project_latin_v1_evidence.md` §5.**
In brief: macron long vowels (`ā ī ū`), dotted retroflexes (`ṭ ḍ ṛ ṇ`),
nasalization `n̄`, aspiration digraphs, `ʿ` for ʿain and `ġ` for ġain, `-e-`
izafat, line starts capitalized (mixed case tolerated), and full Arabic-loan
marking (`ḥ ṣ ẓ …`) as the review-time target. All 72 entries were normalized
mechanically with `./scripts/abshaar.sh normalize-translit --apply`
(dry-run without the flag); `validate` warns on rejected-style markers.

Rules that still stand:

- Keep repeated sounds consistent (so search and glossary links work).
- Add a pronunciation note when a sound is genuinely ambiguous.
- **The original script stays the authority.** Transliteration is a reading aid.

Caution for Shahmukhi/Urdu: these scripts often omit short vowels, so **automatic
transliteration will guess wrong.** Always type/verify by hand or with a native
speaker.

### 5.4 How to fill a poem entry, field by field

`new-entry` gives you a Markdown file with these sections. Here's what each wants:

- **Front matter** (`id`, `poet_id`, `title`, `work_type`, `source_ids`,
  `rights_status`, `review_status`): keep `rights_status: verify_before_publication`
  until you've confirmed it; move `review_status` from `draft` → `publishable`
  only when it truly passes the rubric.
- **# Original** — paste/type the source-script text, preserving line breaks.
- **# Script Notes** — `Script:` (e.g. Shahmukhi), `Language spans:` (e.g.
  Punjabi/Persian), plus any notes on mixed language.
- **# Transliteration** — Latin, line by line, matching the original's lines.
- **# Literal Translation** — currently the cited reference translation slot.
  For the Rafat corpus it contains copyrighted private-reference text and maps to
  `literal_gloss` in JSON; this semantic mismatch must be resolved before review
  or public export.
- **# AI Translation** — a clearly labeled model draft; record model and review
  status, and never treat it as final.
- **# Literary Translation** — Rauf's own readable English poem/prose rendering.
- **# Tashreeh** — explain the metaphor *after* showing it; mark alternate
  readings and uncertainty; keep religious vocabulary precise (don't blur Ram,
  Allah, haq, guru, murshid, naam, ishq into "generic spirituality").
- **# Key Terms** — recurring concepts (`ishq`, `murshid`, `haq`, `nafs`, `fana`,
  `yaar`…). These become glossary links.
- **# Themes** — e.g. `divine_love`, `ritual_critique`, `ego_and_annihilation`.
- **# Source Notes** — source ID/title/URL, rights status, "Can this be
  published? yes/no/unknown", "Can this be used for training? yes/no/unknown".
- **# Review Notes** — your open questions, uncertainties, alternate readings,
  reviewer, date.

Then `build-data` turns this into a structured record automatically (it segments
lines, builds glossary/theme IDs, and gates publication on rights + review).

### 5.5 The review rubric (your quality bar)

Score each translation 1–5 on these. A poem isn't "publishable" until it's strong
across the board and honest about uncertainty.

| Dimension | The question |
|---|---|
| Literal accuracy | Does it preserve the basic meaning? |
| Poetic force | Does the English carry the emotional energy? |
| Cultural fidelity | Does it avoid flattening references? |
| Metaphor preservation | Does it keep the core images? |
| Register | Does it preserve mystical / folk / devotional / ironic tone? |
| Readability | Can a new English reader follow it? |
| Honesty | Does it separate translation from interpretation? |

When you correct an AI draft, **store the correction with its error tags**
(`over_interpretation`, `cultural_flattening`, `register_mismatch`,
`metaphor_loss`, `hallucinated_context`, `script_error`, `transliteration_error`,
…). These reviewed corrections are the dataset you'd eventually fine-tune on.

### 5.6 Building the glossary

Terms like `ishq`, `murshid`, `haq`, `nafs`, `fana`, `Ranjha`, `Heer` recur
constantly. For each, record: literal meaning, **poet-specific** interpretive
meaning, `do_not_flatten_to` (e.g. ishq ≠ "romantic love"), related terms,
example poems, sources, and a confidence label. Aim for ~20–25 entries for the
gold set. This is what lets RAG answer "what does Ranjha mean here?" with a
*sourced* answer instead of a guess.

---

## Part 6 — The learning track

You said you're learning ML close to from scratch. Good news: **you can build the
entire MVP (corpus + RAG + website) with almost no deep ML.** The math-heavy
parts (training loops, gradient descent, LoRA) are only needed for fine-tuning,
which is the *last* rung and may be months away.

So this track is ordered by **what you actually need next**, not by academic
tidiness.

### 6.1 What to learn *now* vs *later*

| Priority | Topic | Why now/later |
|---|---|---|
| **Now** | Python basics (read/run/edit scripts) | everything depends on it |
| **Now** | Files: JSON, JSONL, CSV, **UTF-8** | your whole corpus is structured text |
| **Now** | Git/GitHub basics | the project's shared memory |
| **Now** | Corpus/data design + validation | this *is* the MVP |
| **Soon** | Running translation baselines (IndicTrans2/NLLB/LLM) | your first real AI output |
| **Soon** | Evaluation + human review (rubric, error tags) | how you avoid fooling yourself |
| **Soon** | Embeddings + RAG | source-grounded Q&A, the headline feature |
| **Later** | ML foundations (loss, gradient descent, overfitting) | only meaningful once you fine-tune |
| **Later** | PyTorch + the training loop | same |
| **Later** | Fine-tuning (LoRA/QLoRA) | only after 500–2,000+ reviewed examples |

> The practical takeaway: spend your first months on Python + data + editorial +
> RAG. Treat Phases 5, 6, and 11 of the big roadmap as **deferred** until the
> corpus justifies them.

### 6.2 Plain-English concepts you'll keep hearing

- **Token** — a chunk of text a model processes (often a word-piece, e.g.
  `un` + `believable`). Models see tokens, not words. Non-English scripts tokenize
  less cleanly, which is why quality varies.
- **Embedding** — a list of numbers representing a piece of text's meaning. Texts
  with similar meaning have similar embeddings, which is how "search by meaning"
  works.
- **RAG (retrieval-augmented generation)** — before the model answers, you
  *retrieve* relevant approved notes and feed them in, then tell the model to
  answer using only those notes and cite them. This is how you stop a model from
  confidently making things up.
- **Baseline** — the simplest system you compare against. A fancy model is
  pointless if it isn't clearly better than the baseline.
- **Translation model vs. LLM vs. embedding model** — three different jobs:
  convert text (translation), explain/structure/answer (LLM), find relevant notes
  (embeddings). One model is not enough; Abshaar uses all three.
- **Fine-tuning / LoRA / QLoRA** — gently adapting an existing model to your house
  style using your reviewed examples. LoRA trains small "adapter" weights instead
  of the whole model; QLoRA does it with less memory. Style, not knowledge —
  knowledge stays in the inspectable corpus/RAG.
- **Overfitting** — when a model memorizes its training examples but fails on new
  poems. Why you always test on unseen poems.

### 6.3 The best resources, by stage (free)

Don't collect courses — do them in order, only as far as you currently need.

**Python + tools (now)**
- CS50's Python — https://cs50.harvard.edu/python/
- Kaggle Python — https://www.kaggle.com/learn/python
- Kaggle Pandas — https://www.kaggle.com/learn/pandas
- GitHub Skills — https://skills.github.com/

**NLP / models (soon)**
- Hugging Face LLM course — https://huggingface.co/learn/llm-course/chapter1/1
- The Illustrated Transformer — https://jalammar.github.io/illustrated-transformer/
- Sentence-Transformers (embeddings) — https://www.sbert.net/
- BGE-M3 — https://huggingface.co/BAAI/bge-m3

**Translation baselines (soon)**
- IndicTrans2 — https://github.com/AI4Bharat/IndicTrans2
- NLLB paper — https://arxiv.org/abs/2207.04672

**RAG (soon)**
- RAG paper — https://arxiv.org/abs/2005.11401
- LlamaIndex RAG guide — https://developers.llamaindex.ai/python/framework/understanding/rag/
- Chroma — https://docs.trychroma.com/

**ML foundations + fine-tuning (later)**
- Google ML Crash Course — https://developers.google.com/machine-learning/crash-course
- PyTorch 60-Minute Blitz — https://docs.pytorch.org/tutorials/beginner/deep_learning_60min_blitz.html
- fast.ai — https://course.fast.ai/
- PEFT / LoRA guide — https://huggingface.co/docs/peft/developer_guides/lora
- QLoRA paper — https://arxiv.org/abs/2305.14314

### 6.4 A realistic rhythm

You don't need to "finish learning ML" before contributing. Each week: do a
little study from the stage you're in, then immediately apply it to a real poem or
a real script in this repo. The corpus grows *and* your skills grow at the same
time. The full 63-page roadmap (`Abshaar_Chronological_ML_Roadmap.pdf`) remains
your detailed syllabus — this guide tells you which parts to do when.

---

## Appendix — Quick reference

### A. File & folder map

```text
START_HERE.md          ← you are here (the command center)
README.md              project intro
AGENTS.md              rules for AI assistants (offloading discipline)
OFFLOADING.md          the "save game" / handoff document — update after work
pyproject.toml         Python package config

docs/                  the deep-dive blueprints (01 roadmap … 11 codex automation)
Abshaar_Chronological_ML_Roadmap.pdf   the 63-page learning syllabus

src/abshaar/           the CLI source code
  cli.py               commands
  markdown_entry.py    Markdown → poem record parser
  validation.py        the checks
  export.py            website JSON export
  prompts.py           prompt-pack builder
  ollama_client.py     local AI integration
  status.py jsonl.py text.py paths.py   helpers

scripts/               CLI wrappers: abshaar.ps1/build_all.ps1 (Windows),
                       abshaar.sh/build_all.sh (macOS/Linux)

data/
  raw/public/          public-domain source text
  raw/private/         local-only, NOT published (Git-ignored)
  working/             ← you write poems here (Markdown)
  processed/poems.jsonl    ← generated from working/
  lexicon/terms.jsonl      glossary
  context/             sources / people / events / themes (.jsonl)
  annotations/         reviews.jsonl + model_outputs.jsonl
  templates/           starter shapes for each data type
  cache/               generated prompt packs (disposable)
  site/                generated public website JSON
tests/                 unit tests
```

### B. ID conventions

- Poems: `bulleh_shah_0001`, `bulleh_shah_0002`, … (auto-incremented by `new-entry`).
- Glossary terms: `term_<slug>_<poet_id>` (e.g. `term_ishq_bulleh_shah`).
- Themes: `theme_<slug>` (e.g. `theme_divine_love`).
- Sources: `source_bulleh_0001`, etc.

### C. Publishing gate (why a poem won't go public)

A poem is exported to the site only when **both**:
1. its source notes say "Can this be published? **yes**", **and**
2. `review_status` is **`publishable`**,
and its `rights_status` is one of `public-domain` / `permission-cleared` /
`project-original`. Otherwise it stays private — by design.

### D. Mini-glossary of technical terms

token · embedding · RAG · baseline · fine-tuning · LoRA · QLoRA · overfitting ·
inference · checkpoint — all defined in [Part 6.2](#62-plain-english-concepts-youll-keep-hearing).

### E. Troubleshooting

- **"running scripts is disabled" (Windows)** → prefix with
  `powershell -ExecutionPolicy Bypass -File ...`.
- **"permission denied" running `./scripts/abshaar.sh` (macOS/Linux)** → run
  `chmod +x scripts/*.sh` once.
- **`validate` shows placeholder warnings** → the entry still has `[bracketed]`
  template text; finish it.
- **`draft` fails** → run `ai-check`; make sure Ollama is installed, running, and
  has the model pulled (`ollama pull qwen3:8b`).
- **Non-English text looks broken** → the file isn't UTF-8. Re-save as UTF-8 (in
  VS Code, click the encoding label, "Save with Encoding" → UTF-8).

---

*This guide is meant to stay current. When the project state changes, update
[Part 2](#part-2--where-things-stand--your-next-moves) and the "Last updated"
date at the top — and remember to update `OFFLOADING.md` too.*
