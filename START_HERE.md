# START HERE — The Abshaar One-Stop Guide

> This is your command center. Open it at the start of every work session.
> It tells you **where the project stands, what to do next, how to run everything,
> what to learn, and how to do the editorial work** — without needing to dig
> through the other docs first.
>
> Last updated: **2026-07-04**
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

---

## Part 1 — The project in 60 seconds

**Abshaar is a local-first, open-source archive and AI-assisted *interpretation*
system for South Asian mystical poetry** (Punjabi, Urdu, Persian-influenced,
Braj/Bhakti, Sufi). It is **not** a one-click translator.

The single most important idea:

> A poem is a layered cultural object, not ordinary text. Abshaar keeps the
> layers **separate and visible**: original script → transliteration → literal
> gloss → literary translation → *tashreeh* (explanation) → glossary → poet
> context → sources. The reader always sees what is fact and what is
> interpretation.

The second most important idea:

> **The model is not the project.** The corpus, the annotations, the
> source-grounding, and the human review are worth as much as any model. A great
> model on a weak dataset still sounds shallow. So: **archive first, AI second.**

The first concrete target is a **Bulleh Shah Explorer**: ~10–20 carefully
reviewed works with original text, transliteration, translation layers, glossary,
tashreeh, and source-grounded Q&A.

---

## Part 2 — Where things stand & your next moves

### 2.1 Current state (verified 2026-06-27)

The **infrastructure is built; the corpus is empty.** Running `status` reports:

| Thing | Count |
|---|---|
| Working Markdown entries | 0 |
| Processed poem records | 0 |
| Poems marked public | 0 |
| Glossary terms | 0 |
| Sources | 0 |
| People / events / themes | 0 / 0 / 0 |
| Human reviews | 0 |
| Model outputs | 0 |
| Validation errors / warnings | 0 / 0 |

What *exists* and works: the Python CLI (`abshaar`), the Markdown→JSONL pipeline,
validation, website export, prompt-pack builder, optional Ollama drafting,
passing tests, and full planning docs. What's *missing* is **content** — not code.

> Reality check: validation passes because there is nothing to check yet. That is
> not "done"; it's "empty." Your job from here is editorial, not engineering.

### 2.2 Open decisions that block real progress

You can't enter poems well until you lock these down. Decide them once, write them
down (a short note in `docs/` or in source records), and stop re-deciding:

- [ ] **First source edition.** Which *specific* public-domain or
      permission-cleared Bulleh Shah source will you transcribe from? (Edition,
      editor, year, URL/citation.) See [Part 5.2](#52-sourcing--copyright-the-rule-that-protects-the-project).
- [ ] **Transliteration standard (`project-latin-v1`).** A short, consistent
      Latin scheme. Don't try to be scholarly on day one. See [Part 5.3](#53-the-transliteration-standard-project-latin-v1).
- [ ] **Licenses.** Recommended default: **MIT or Apache-2.0** for code;
      **mark public-domain source text as such**; **CC BY-SA 4.0** for *your*
      translations and tashreeh.
- [ ] **Review rubric.** The 1–5 scale you'll score translations against (a
      starter rubric is in [Part 5.5](#55-the-review-rubric-your-quality-bar)).

### 2.3 Your next 5 moves (do these in order)

This is the immediate path. Each move is small and verifiable. Commands are
shown in PowerShell; on macOS/Linux use `./scripts/abshaar.sh` in place of
`.\scripts\abshaar.ps1` (see [4.1](#41-one-time-setup-only-if-not-already-done)).

1. **Pick the first source** and record it. Create
   `data/context/sources.jsonl` with one entry (use
   `data/templates/sources.template.jsonl` as the shape). Verify: the file exists
   and `validate` still passes.
2. **Create your first poem entry:**
   ```powershell
   .\scripts\abshaar.ps1 new-entry --title "Ranjha Ranjha kardi"
   ```
   This makes `data/working/bulleh_shah_0001.md`. Verify: the file appears.
3. **Fill the entry** completely — original, script notes, transliteration,
   literal gloss, literary translation, tashreeh, key terms, themes, source notes,
   review notes. (See [Part 5.4](#54-how-to-fill-a-poem-entry-field-by-field).)
   Save as **UTF-8**.
4. **Build and validate:**
   ```powershell
   .\scripts\abshaar.ps1 build-data
   .\scripts\abshaar.ps1 validate
   ```
   Verify: 1 processed poem, 0 errors. Warnings about placeholders mean the entry
   isn't finished — keep going until they're gone.
5. **Repeat to 3 pilot poems**, then review them honestly against the rubric.
   Once the pattern feels stable, scale toward the first gold set (below).

### 2.4 The milestone ladder

You always know what "stage" you're in by which rung is true:

| Rung | Definition of done | You're here when… |
|---|---|---|
| **Pilot** | 1–3 fully filled, validated poems | *(next up)* |
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

Useful flags:

- `new-entry --id bulleh_shah_0020` — set the ID manually instead of auto.
- `new-entry --poet-id shah_hussain` — start a different poet.
- `build-data --include-placeholders` — include unfinished entries (normally skipped).
- `prompt-pack --all` — build packs for every processed poem.

### 4.3 The two loops you'll actually run

**Daily editorial loop** (no AI needed). Windows shown; macOS/Linux: swap in
`./scripts/abshaar.sh`.

```powershell
.\scripts\abshaar.ps1 status          # where am I?
.\scripts\abshaar.ps1 new-entry --title "..."   # if starting a poem
# ...edit the Markdown file in data/working/...
.\scripts\abshaar.ps1 build-data
.\scripts\abshaar.ps1 validate        # fix every error; clear placeholder warnings
```

**Full local build** (run before committing a batch of edits):

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
git add .             # stage changes
git commit -m "Add first Bulleh Shah pilot entry"
git push              # send to GitHub
```

Commit after each meaningful chunk of work. The commit message is a note to your
future self about *why* something changed.

---

## Part 5 — The editorial & sourcing track

This is the part the ML roadmap mostly assumes you already know. **It is the real
bottleneck of the project.** Great ML cannot rescue a thin or unsafe corpus.

### 5.1 The five layers you produce for every poem

Keep these strictly separate. Never let one silently replace another.

| Layer | What it is | The trap to avoid |
|---|---|---|
| **Original** | the poem in its source script (Shahmukhi, Gurmukhi, etc.) — the authority | replacing it with transliteration |
| **Transliteration** | a Latin reading aid for people who can't read the script | treating it as "the text" |
| **Literal gloss** | plain, close English meaning, line by line | smuggling in interpretation |
| **Literary translation** | readable English that keeps poetic force | flattening the imagery |
| **Tashreeh** | explanation of metaphor, culture, Sufi meaning, ambiguity | stating one reading as the only truth |

### 5.2 Sourcing & copyright (the rule that protects the project)

Classical poems may be public domain, but **modern editions, translations,
annotations, recordings, and website metadata often are not.**

**Safe to use:** public-domain editions; your own translations; your own
annotations; permission-cleared material; short bibliographic metadata with
attribution; source links and citations.

**Do not:** copy modern translations into the data without permission; scrape
whole websites; upload copyrighted scans; mix private notes into public files.

> Ajab Shahar and similar sites are excellent **design/editorial references**, but
> their work is copyrighted unless stated otherwise. Learn from the structure;
> don't ingest the content.

For every source, record: name, editor/author, year, URL or citation, **rights
status**, and **allowed uses** — *before* you mark anything publishable. Private,
unpublishable material goes in `data/raw/private/` (Git-ignored).

### 5.3 The transliteration standard (`project-latin-v1`)

Start simple. You can add a scholarly system later as a *second* field; never
overwrite the first.

Rules:

- Plain Latin characters; avoid decorative diacritics at first.
- Keep repeated sounds consistent (so search and glossary links work).
- Prioritize readability for English-speaking learners.
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
- **# Literal Gloss** — plain meaning, line by line. Resist interpreting.
- **# Literary Translation** — the readable English poem/prose.
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
