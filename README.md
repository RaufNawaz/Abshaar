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
- [Contributing](CONTRIBUTING.md)
- [Content License](CONTENT_LICENSE.md)
- [Data Folder](data/README.md)
- [Dataset Templates](data/templates/)

## Important Principle

Do not scrape modern translations, annotations, audio, or metadata into the
training set unless their license allows it or permission is granted. Sites such
as Ajab Shahar are excellent design and editorial references, but their work must
be credited and treated as copyrighted unless stated otherwise.

## Current Project Stage

This repository currently contains the planning and technical blueprint. The
recommended first corpus target is Bulleh Shah, using the starter templates in
`data/templates/`. The next implementation milestone is a small corpus MVP:
20-50 works, one reviewed translation workflow, one static website prototype, and
one local RAG question-answering prototype.

## Automation

Use the local automation CLI through PowerShell:

```powershell
.\scripts\abshaar.ps1 validate
.\scripts\abshaar.ps1 status
.\scripts\abshaar.ps1 new-entry --title "First line here"
.\scripts\abshaar.ps1 build-data
.\scripts\abshaar.ps1 export-site
```

If PowerShell blocks local scripts, use
`powershell -ExecutionPolicy Bypass -File .\scripts\abshaar.ps1 validate`.
For a full local check, use
`powershell -ExecutionPolicy Bypass -File .\scripts\build_all.ps1`.

See [Automation Infrastructure](docs/09_automation_infrastructure.md) for the
full command reference, or [Plain-English Automation Guide](docs/10_plain_english_automation_guide.md)
for a non-technical explanation.
