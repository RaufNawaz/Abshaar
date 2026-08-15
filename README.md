# Abshaar

Abshaar is an open-source, local-first project for translating and explaining
Punjabi, Urdu, Persian-influenced, Braj/Bhakti, and Sufi poetry in English
without flattening the metaphysical, cultural, and poetic meaning carried by the
original language.

The goal is not to build a one-click literal translator. The goal is to build a
human-guided translation and interpretation system: original text, transliteration,
literal gloss, literary translation, tashreeh, glossary, poet context, timeline,
and source-grounded question answering.

## Core Idea

Most current translation systems treat a poem as ordinary text. Abshaar should
treat each verse as a layered cultural object.

The system should:

- preserve the original text and script wherever possible;
- identify language and script shifts inside the same work;
- generate a literal translation as a baseline, not the final answer;
- retrieve poet-specific context before explaining a metaphor;
- produce a literary translation and a separate tashreeh;
- show the reader what is interpretation and what is directly grounded in source;
- learn from human review over time through annotated examples and later LoRA
  fine-tuning.

## Recommended Architecture

Start with a simple pipeline, then improve each piece:

1. Corpus: public-domain or permission-cleared poems, metadata, transliteration,
   glossary entries, poet biographies, timeline events, and theme tags.
2. Baseline translation: IndicTrans2 for supported Indic languages and NLLB-200
   as a fallback for broader multilingual translation.
3. Interpretive model: a local open-weight LLM such as Qwen3 for tashreeh,
   literary rendering, and source-grounded answers.
4. Retrieval: multilingual embeddings, preferably BGE-M3, over poet notes,
   glossary entries, poem annotations, and historical context.
5. Review loop: human critique is stored as structured data, then used for
   evaluation and later fine-tuning.
6. Public website: a static GitHub Pages site for poems, timelines, glossary, and
   search; optional AI chat can run locally in the browser or through a separate
   self-hosted backend.

## Start Here

- [One-Stop Project Guide](START_HERE.md)
- [Current Handoff / Project State](OFFLOADING.md)
- [Project Roadmap](docs/01_project_roadmap.md)
- [Model Strategy](docs/02_model_strategy.md)
- [Data and Annotation Guide](docs/03_data_and_annotation_guide.md)
- [Website Architecture](docs/04_website_architecture.md)
- [Local Setup Guide](docs/05_local_setup.md)
- [Open Source and Governance](docs/06_open_source_governance.md)
- [Step-by-Step LaTeX Implementation Guide](docs/07_step_by_step_implementation_guide.tex)
- [Text Entry and Transliteration Workflow](docs/08_text_entry_transliteration_workflow.md)
- [Automation Infrastructure](docs/09_automation_infrastructure.md)
- [Plain-English Automation Guide](docs/10_plain_english_automation_guide.md)
- [Codex Handoff Automation](docs/11_codex_handoff_automation.md)
- [Sufinama Source Ingestion](docs/12_sufinama_source_ingestion.md)
- [PunjabLibrary Gurmukhi PDF Ingestion](docs/13_gurmukhi_pdf_ingestion.md)
- [Bulleh Shah Research and Sufinama Inventory](docs/14_bulleh_shah_research_and_sufinama_inventory.md)
- [Contributing](CONTRIBUTING.md)
- [Content License](CONTENT_LICENSE.md)
- [Data Folder](data/README.md)
- [Dataset Templates](data/templates/)

## Important Principle

Record the source, authorization scope, and provenance of every acquired
collection. Private collaboration-authorized research and training may proceed
within the granted scope; public release and redistribution are separate
decisions. Never erase source boundaries when combining editions or witnesses.

## Current Project Stage

The repository is now in the **corpus-complete, editorial-review stage for its
first source collection**. The live working tree contains 72 Bulleh Shah poem
entries: one Sufinama pilot plus all 71 poems from Taufiq Rafat's 1982 selection.
The Rafat entries include visually transcribed Shahmukhi originals,
`project-latin-v1` transliterations, a gated copyrighted reference translation,
and Claude-drafted English. None are public or training-cleared. Human literary
translations, tashreeh, glossary links, themes, formal reviews, and source-text
verification remain unfinished. See `OFFLOADING.md` and
`Bulleh Shah/CORPUS_BUILD_LOG.md` for the exact current state and risks.

The authorized Sufinama acquisition now contains two source-separated layers:
76 UUID-paired kaafi witnesses and 48 non-kaafi category witnesses (3 kalaam,
23 dohas, 7 shabads, 12 dohras, athvara, barahmasa, and holi). Both collectors
preserve returned script layers, stable content/line/token IDs, raw checksums,
source-unavailable language views, and review-only crosswalks. Reprocessing can
run entirely offline from the saved cache.

A third, source-separated witness catalog now covers all 160 numbered kafis in a
local 149-page PunjabLibrary Gurmukhi PDF. The full embedded-text extraction is
kept private and review-required because the text layer visibly corrupts some
Gurmukhi characters and the 2017 digital edition's rights are unknown. Rendered
PDF pages remain authoritative.

The first sourced biography/context pass adds 11 claim-level notes, 6 cautious
timeline events, and a 13-category inventory of Bulleh Shah material on
Sufinama. The 48 listed kalaam/doha/shabad/dohra/athvara/barahmasa/holi records
are now acquired as separate category witnesses. Quotes, e-book, video, and
blog/profile material remain metadata/research targets. Categories overlap and
are not unique-work totals.

The immediate milestone is to turn a deliberately selected 5-poem subset into a
fully reviewed vertical slice, then scale that editorial workflow toward a
20-poem gold corpus. The website and RAG prototypes should follow reviewed,
rights-safe data rather than precede it.

## Shared AI Workflow

Codex and Claude may both work in this repository. Each assistant must read
`AGENTS.md` and `OFFLOADING.md`, preserve existing working-tree changes, update
all affected documentation after substantive work, and record verification and
next steps in `OFFLOADING.md`. Claude-specific startup instructions are mirrored
in `CLAUDE.md`.

## Automation

Use the local automation CLI. On Windows, through PowerShell:

```powershell
.\scripts\abshaar.ps1 validate
.\scripts\abshaar.ps1 status
.\scripts\abshaar.ps1 new-entry --title "First line here"
.\scripts\abshaar.ps1 build-data
.\scripts\abshaar.ps1 export-site
.\scripts\abshaar.ps1 acquire-sufinama --discover-only
.\scripts\abshaar.ps1 acquire-sufinama-texts --offline --transport curl
.\scripts\abshaar.ps1 extract-gurmukhi-pdf --input "Bulleh Shah\Kafian - Baba Bulleh Shah (Baba Bulle Shah) (z-library.sk, 1lib.sk, z-lib.sk).pdf"
```

If PowerShell blocks local scripts, use
`powershell -ExecutionPolicy Bypass -File .\scripts\abshaar.ps1 validate`.
The `build_all` wrapper now preserves unfinished entries by passing
`--include-placeholders` during the rebuild.

On macOS/Linux, use the matching shell script (same arguments):

```bash
./scripts/abshaar.sh validate
./scripts/abshaar.sh status
./scripts/abshaar.sh new-entry --title "First line here"
./scripts/abshaar.sh build-data
./scripts/abshaar.sh export-site
./scripts/abshaar.sh acquire-sufinama --discover-only
./scripts/abshaar.sh acquire-sufinama-texts --offline --transport curl
./scripts/abshaar.sh extract-gurmukhi-pdf --input "Bulleh Shah/Kafian - Baba Bulleh Shah (Baba Bulle Shah) (z-library.sk, 1lib.sk, z-lib.sk).pdf"
```

If `permission denied`, run `chmod +x scripts/*.sh` once. For a complete local
check, use `./scripts/build_all.sh`.

The expert-model training pipeline (knowledge base, RAG index, grounded `ask`,
gated training-data generation, evaluation, local LoRA) is driven by the same
CLI — `extract-lexicon`, `build-clusters`, `build-kb`, `build-index`, `ask`,
`export-training-corpus`, `generate-training-data`, `build-probes`,
`run-eval`, `export-mlx-dataset` — and documented end to end in
[docs/15](docs/15_bulleh_shah_expert_model_implementation_plan.md). The
AI-stack commands need the project venv (`python3 -m venv .venv &&
.venv/bin/pip install -r requirements.txt`); both wrappers prefer `.venv`
automatically when it exists.

See [Automation Infrastructure](docs/09_automation_infrastructure.md) for the
full command reference, or [Plain-English Automation Guide](docs/10_plain_english_automation_guide.md)
for a non-technical explanation.
