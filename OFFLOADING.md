# OFFLOADING.md

Last updated: 2026-06-27

## 1. Project Overview

Abshaar is an open-source, local-first archive and AI-assisted translation/explanation project for Punjabi, Urdu, Persian-influenced, Braj/Bhakti, and Sufi poetry in English. The project's purpose is to preserve original text, transliteration, literal gloss, literary translation, tashreeh, source context, glossary meaning, timelines, and review notes without flattening poetic, cultural, or metaphysical meaning. The repository currently contains a planning/technical blueprint plus a small Python automation package, data templates, working-entry templates, validation/export/status commands, tests, and documentation. The immediate project stage is pre-corpus MVP: the infrastructure exists, validation passes, and the next real milestone is to build the first small gold corpus rather than train or fine-tune models.

### Main Objective

- Build a small, legally safe, human-reviewed corpus MVP for Abshaar, then use it to support local RAG, model-assisted drafting, review workflows, and eventually a static public website.

### Current Stage

- Pre-corpus MVP / infrastructure-ready stage. The repo has automation, templates, docs, and passing tests, but no working poem entries, processed poems, glossary terms, sources, people records, events, themes, reviews, or model outputs yet.

### Current Working Direction

- Choose and document a narrow first corpus scope, then create the first Bulleh Shah source record and 1-3 working poem entries using the Markdown workflow before scaling toward the planned 20-50 work gold dataset.

## 2. What Has Been Done

- Created `START_HERE.md`, a mostly self-contained "command center" guide at the repo root.
  - Details: Single-stop guide with six parts — (1) project in 60 seconds, (2) current state + next 5 moves + open decisions + milestone ladder, (3) mental model (8 layers, golden rule, pipeline diagram, model stack), (4) full workflow & CLI command playbook, (5) editorial & sourcing track (the humanities gap: sourcing/copyright, transliteration standard, field-by-field entry, review rubric, glossary), (6) learning track pitched for an ML near-beginner (now-vs-later priorities, plain-English concepts, staged free resources). Plus an appendix (file map, ID conventions, publishing gate, glossary, troubleshooting). Built per user request as a "one stop shop," confirmed via clarifying questions (command center; all four content tracks; mostly self-contained; learner level = ML near-scratch).
  - Why it matters: Gives the user a single entry point that orients them each session, replaces the need to dig through 11 docs + the 63-page PDF, and explicitly sequences which roadmap phases are MVP-critical vs deferred.
  - Files affected: `START_HERE.md` (new).
  - Verification: All 9 CLI commands and both PowerShell scripts referenced in the guide were grep-checked against `src/abshaar/cli.py` and `scripts/`; state figures match live `abshaar status` output (all zeros, 0 errors/warnings) on 2026-06-27.

- Created and maintained the required `OFFLOADING.md` handoff document.
  - Details: The file follows the CRAFT-style continuity requirements from `AGENTS.md` and is updated after substantive work.
  - Why it matters: The project can be paused and restarted in another Codex/chat/development environment without losing decisions, commands, state, or next steps.
  - Files affected: `OFFLOADING.md`

- Verified the repository identity and purpose from `README.md`.
  - Details: The project is named Abshaar. It is a local-first archive and AI-assisted translation infrastructure for South Asian mystical poetry, not a one-click literal translator.
  - Why it matters: Future work should prioritize corpus quality, source safety, human review, and interpretive structure before model training.
  - Files affected: None.

- Reviewed the core strategy documents.
  - Details: `docs/01_project_roadmap.md` recommends starting with one poet, 20-50 short works, one primary source, one transliteration standard, one translation style guide, and one review rubric. `docs/02_model_strategy.md` recommends AI app first, ML training later, using IndicTrans2/NLLB baselines, Qwen3 through Ollama for interpretation, BGE-M3 for retrieval, and LoRA/QLoRA only after enough reviewed examples. `docs/03_data_and_annotation_guide.md` defines the corpus principles, JSONL schemas, review data, first gold dataset target, and copyright rules.
  - Why it matters: These docs define the correct order of operations: corpus and review infrastructure first, AI/fine-tuning later.
  - Files affected: None.

- Inspected the Python CLI automation.
  - Details: `src/abshaar/cli.py` provides commands: `init`, `status`, `new-entry`, `build-data`, `validate`, `export-site`, `prompt-pack`, `ai-check`, and `draft`. Supporting modules parse Markdown entries, validate JSONL/working entries, generate prompt packs, export website JSON, check Ollama, and summarize project status.
  - Why it matters: The user can begin corpus work through PowerShell without manually managing JSONL structure.
  - Files affected: None.

- Verified current data state.
  - Details: `data/working/` contains `README.md` and `bulleh_shah_entry_template.md`. `data/templates/` contains JSONL templates for poems, sources, terms, people, events, themes, reviews, QA pairs, and model outputs. `data/site/` currently contains generated empty JSON arrays. No actual corpus records exist yet.
  - Why it matters: The next step is content selection and data entry, not infrastructure creation.
  - Files affected: None.

- Ran current project commands.
  - Details: From `D:\Harvard\Poetry Model Project`, the following commands were run successfully:

    ```powershell
    powershell -ExecutionPolicy Bypass -File .\scripts\abshaar.ps1 status
    powershell -ExecutionPolicy Bypass -File .\scripts\abshaar.ps1 validate
    $env:PYTHONPATH='src'; py -3.14 -m unittest discover -s tests
    git status --short
    ```

  - Why it matters: The repo is currently in a clean, working baseline state for local automation and tests.
  - Files affected: None from these commands during this task.

- Verified current command output.
  - Details: `status` reports 0 working Markdown entries, 0 processed poems, 0 public poems, 0 glossary terms, 0 sources, 0 people records, 0 events, 0 themes, 0 reviews, 0 model outputs, 0 validation errors, and 0 validation warnings. `validate` reports `No validation issues found.` Unit tests ran 2 tests and passed. `git status --short` returned no output, indicating a clean working tree at verification time.
  - Why it matters: There are no known repository errors or uncommitted changes blocking first corpus work.
  - Files affected: None.

- Updated this handoff after answering the user's next-step question.
  - Details: Removed obsolete prior claims that shell inspection was blocked, replaced them with verified project state, current commands, risks, and prioritized next actions.
  - Why it matters: Future assistants should not be misled by old sandbox-failure notes.
  - Files affected: `OFFLOADING.md`

## 3. Current State

| Item | Current Status | Notes |
|---|---|---|
| Entry-point guide | Present | `START_HERE.md` at repo root is the mostly self-contained command center; read it first, before the `docs/` set. |
| Repository path | Verified | `D:\Harvard\Poetry Model Project` |
| Operating system | Windows | Prefer PowerShell-compatible commands. |
| Project name | Verified | Abshaar. |
| Project purpose | Verified from README/docs | Local-first archive and AI-assisted translation/explanation system for South Asian mystical poetry. |
| Git working tree | Clean at verification time | `git status --short` returned no output. |
| Python package | Present | Package name `abshaar`, source under `src/abshaar/`, configured in `pyproject.toml`. |
| Python version requirement | Present | `pyproject.toml` says `requires-python = ">=3.11"`. Verification used `py -3.14`. |
| Runtime dependencies | Minimal by default | `pyproject.toml` has no base dependencies. Optional `ai` dependencies include Ollama, sentence-transformers, ChromaDB, transformers, and torch. Optional `dev` dependency includes Ruff. |
| CLI commands | Present | `init`, `status`, `new-entry`, `build-data`, `validate`, `export-site`, `prompt-pack`, `ai-check`, `draft`. |
| Current corpus | Empty | Status reports 0 working entries and 0 processed poems. |
| Working entry template | Present | `data/working/bulleh_shah_entry_template.md` is the first human-friendly poem entry template. |
| Data templates | Present | JSONL templates are in `data/templates/`. |
| Website export data | Empty generated files | `data/site/*.json` currently appears to contain empty arrays. |
| Validation | Passing | `powershell -ExecutionPolicy Bypass -File .\scripts\abshaar.ps1 validate` reports no issues. |
| Tests | Passing | `$env:PYTHONPATH='src'; py -3.14 -m unittest discover -s tests` ran 2 tests successfully. |
| AI setup | Not checked in this task | `ai-check` was not run; Ollama/model availability is unknown. |
| First poet target | Suggested by current template | README recommends Bulleh Shah as starter target; template is named for Bulleh Shah. Final source/poet choice should still be consciously confirmed. |

### Current Known Working Commands

- `powershell -ExecutionPolicy Bypass -File .\scripts\abshaar.ps1 status`
- `powershell -ExecutionPolicy Bypass -File .\scripts\abshaar.ps1 validate`
- `$env:PYTHONPATH='src'; py -3.14 -m unittest discover -s tests`
- `git status --short`

### Current Blockers

- None known for starting the first corpus entry workflow.

### Current Open Questions

- Which exact source edition or public-domain/permission-cleared source should be used for the first Bulleh Shah entries?
- What transliteration standard should be accepted as `project-latin-v1` for the first corpus?
- What translation style guide should govern the first 20-50 works?
- What review rubric should be used for marking entries as publishable?
- Is Ollama installed locally, running, and configured with a model such as `qwen3:8b`? Needs verification before using `ai-check` or `draft`.

## 4. Key Decisions and Rationale

| Decision | Rationale | Alternatives Considered | Effect on Future Work |
|---|---|---|---|
| Treat Abshaar as an archive and annotation system first, AI system second | The roadmap and model strategy explicitly warn that model quality depends on corpus, metadata, and human feedback quality. | Start with chatbot, bulk scraping, or fine-tuning | Next work should create verified data and review structure before expanding AI features. |
| Start with a small gold corpus rather than hundreds of poems | The roadmap recommends 20 deeply annotated poems over 2,000 weakly processed ones. | Large unreviewed corpus | The immediate milestone should be 1-3 pilot entries, then 20-50 reviewed works. |
| Keep humans editing Markdown and computers reading JSONL | The automation guide and CLI support `data/working/*.md` conversion into `data/processed/poems.jsonl`. | Manually author JSONL records | Corpus entry is easier and less error-prone for non-technical editorial work. |
| Preserve separate outputs for original, transliteration, literal gloss, literary translation, and tashreeh | The project's core value is avoiding flattened translation and hiding interpretation. | Single blended translation field | Future prompts, website pages, reviews, and model outputs should maintain these separations. |
| Require source/license review before publication or training use | Copyright/source safety is a repeated project principle. | Treat classical poetry sources as automatically safe | Every source record should include rights status and allowed uses before publication/model training. |
| Use local open-weight models only after corpus scaffolding is usable | Model strategy recommends Qwen3/Ollama and retrieval after data exists. | Fine-tune immediately or depend on hosted APIs | AI tasks should begin with `ai-check`, prompt packs, and single-poem drafts only after entries exist. |

## 5. User Preferences and Instructions

### Persistent Preferences

- The user wants detailed offloading documents after substantive project work.
- The user wants to avoid context loss when moving to a new chat, Codex session, coding environment, or AI tool.
- The user prefers practical, precise, implementation-focused writing.
- The user wants the CRAFT method used when helpful and specifically for `OFFLOADING.md`.
- The user wants clear markdown headings, bullet points, checklists, and tables.
- The user does not want vague summaries.
- The user does not want invented facts.
- Unknown or unverified information should be clearly marked as `Unknown` or `Needs verification`.
- The user is on Windows.
- Prefer PowerShell-compatible commands.
- Do not assume Bash is available.
- Preserve operational details such as filenames, paths, commands, decisions, errors, and next steps.

### Project-Specific Instructions

- Read `AGENTS.md` and `OFFLOADING.md` first when continuing the project.
- Update `OFFLOADING.md` after every substantive task.
- A substantive task includes writing code, editing code, debugging, refactoring, creating or modifying files, reviewing the codebase, creating or editing documentation, creating prompts/templates/workflows/scripts, running analysis, making architectural or structural decisions, researching information that affects the project, changing project direction, or producing output that affects project state or future work.
- Preserve useful prior `OFFLOADING.md` content when updating it.
- Remove or revise obsolete information only when it is clearly outdated, incorrect, or replaced by better verified information.
- If a task fails, still update `OFFLOADING.md` with what was attempted, what failed, error messages, current state, and recommended next steps.
- Before finishing a substantive task, verify whether `OFFLOADING.md` answers the required continuity questions in `AGENTS.md`.

### Things to Avoid

- Do not write vague lines such as "Updated files", "Improved project", "Various files were edited", or "Fixed things."
- Do not invent project details that have not been verified.
- Do not assume Unix tools or Bash are available.
- Do not overwrite important files without inspecting them when inspection is available.
- Do not omit errors, blockers, unresolved issues, commands, paths, or decisions that would help future work.
- Do not claim verification was completed when it was not.
- Do not scrape modern copyrighted translations, annotations, audio, metadata, or scans into training/public data without permission or compatible license.

## 6. Important Context a New Chat Must Know

- Abshaar is not meant to be a generic translation app. It is intended as a careful, source-grounded, human-reviewed interpretive archive for South Asian mystical poetry.
- The project should start with one narrow corpus target. The current template and README point toward Bulleh Shah, but the exact source edition still needs selection and rights verification.
- The immediate data goal from the docs is a first gold dataset: 20 short works, 20 glossary terms, 10 timeline events, 10 themes, 10 source notes, and 50 grounded QA pairs.
- The current actual corpus count is zero. The infrastructure is ready, but the archive still needs real entries.
- Humans should edit Markdown files in `data/working/`; automation converts them to JSONL for models and website export.
- `validate` checks structure, placeholders, duplicate IDs, broken JSONL, and unsafe publication settings. It does not judge poetic accuracy.
- Source trust, copyright safety, transliteration accuracy, translation quality, tashreeh quality, and publication approval must remain human-reviewed.
- The AI path should be staged: create entries, build JSONL, validate, generate prompt packs, optionally draft through local Ollama, store outputs as review-needed records, then add human corrections.
- `OFFLOADING.md` must be updated after substantive work, including analysis and documentation updates.
- Use PowerShell commands from `D:\Harvard\Poetry Model Project` unless the user explicitly requests another shell.

## 7. Next Steps

### Urgent

- [ ] Decide the exact first corpus scope: confirm Bulleh Shah or choose another first poet, select 1 public-domain or permission-cleared source, and define the first 3-5 pilot works.
- [ ] Create an initial source record for the chosen edition/source in the appropriate JSONL file, likely `data/context/sources.jsonl`, using `data/templates/sources.template.jsonl` as reference.
- [ ] Create the first working poem entry with `powershell -ExecutionPolicy Bypass -File .\scripts\abshaar.ps1 new-entry --title "First line here"`.
- [ ] Fill the first entry in `data/working/` with original text, script notes, transliteration, literal gloss, literary translation, tashreeh, key terms, themes, source notes, and review notes.
- [ ] Run `powershell -ExecutionPolicy Bypass -File .\scripts\abshaar.ps1 validate` after the first entry and resolve all errors; treat placeholder warnings as a sign the entry is not ready.

### Soon

- [ ] Run `powershell -ExecutionPolicy Bypass -File .\scripts\abshaar.ps1 build-data` once at least one entry is filled.
- [ ] Run `powershell -ExecutionPolicy Bypass -File .\scripts\abshaar.ps1 export-site` to confirm website-ready JSON exports remain clean.
- [ ] Draft a short translation style guide for `project-latin-v1`, literal gloss style, literary translation style, and tashreeh tone.
- [ ] Add the first 10-20 glossary terms for Bulleh Shah concepts such as `ishq`, `murshid`, `haq`, `nafs`, `fana`, and `yaar`, with poet-specific meanings and source links.
- [ ] Add basic people/theme/event/source records needed to contextualize the first poems.
- [ ] Run `powershell -ExecutionPolicy Bypass -File .\scripts\abshaar.ps1 ai-check` before attempting local model drafting.

### Optional Improvements

- [ ] Add an `abshaar add-source` command to reduce friction when recording source metadata.
- [ ] Add automatic script detection for working entries.
- [ ] Add `abshaar suggest-terms --poem-id ...` to help connect repeated terms to glossary records.
- [ ] Add an `abshaar refresh` command that runs build-data, validate, prompt-pack, and export-site in one pass.
- [ ] Build a small local review interface for model outputs and human corrections.
- [ ] Add a static website prototype after the first publishable poems exist.

## 8. Restart Prompt

Copy and paste this into a new chat or Codex session:

> I am continuing a project with an `AGENTS.md` file and an `OFFLOADING.md` handoff document.
>
> First, read `AGENTS.md` and `OFFLOADING.md`.
>
> The purpose of this project is: Abshaar is an open-source, local-first archive and AI-assisted translation/explanation system for Punjabi, Urdu, Persian-influenced, Braj/Bhakti, and Sufi poetry in English. It should preserve original text, transliteration, literal gloss, literary translation, tashreeh, source context, glossary meaning, timelines, and human review without flattening cultural or metaphysical meaning.
>
> Current state: The repository has planning docs, data templates, a Python package under `src/abshaar/`, PowerShell scripts, working-entry templates, validation/export/status commands, and passing tests. The current corpus is empty: status reports 0 working entries, 0 processed poems, 0 glossary terms, 0 sources, 0 events, 0 themes, 0 reviews, and 0 model outputs. `validate` reports no issues. Unit tests pass.
>
> Important files: `START_HERE.md` (read first — the command-center guide), `AGENTS.md`, `OFFLOADING.md`, `README.md`, `pyproject.toml`, `src/abshaar/cli.py`, `src/abshaar/markdown_entry.py`, `src/abshaar/validation.py`, `src/abshaar/status.py`, `scripts/abshaar.ps1`, `scripts/build_all.ps1`, `data/working/bulleh_shah_entry_template.md`, `data/templates/*.template.jsonl`, `docs/01_project_roadmap.md`, `docs/02_model_strategy.md`, `docs/03_data_and_annotation_guide.md`, and `docs/10_plain_english_automation_guide.md`.
>
> What has already been done: The project infrastructure and documentation are in place. The CLI supports `init`, `status`, `new-entry`, `build-data`, `validate`, `export-site`, `prompt-pack`, `ai-check`, and `draft`. Current verification commands succeeded: `powershell -ExecutionPolicy Bypass -File .\scripts\abshaar.ps1 status`, `powershell -ExecutionPolicy Bypass -File .\scripts\abshaar.ps1 validate`, `$env:PYTHONPATH='src'; py -3.14 -m unittest discover -s tests`, and `git status --short`.
>
> Next steps: Choose the exact first corpus scope, verify a public-domain or permission-cleared Bulleh Shah source, create the first source record, create and fill 1-3 working poem entries in `data/working/`, validate them, build JSONL data, and only then test prompt packs/local AI drafting.
>
> Follow these preferences:
> - Use precise, practical markdown.
> - Preserve context.
> - Do not invent facts.
> - Mark unknowns as "Unknown" or "Needs verification."
> - Prefer PowerShell commands because I am on Windows.
> - Update `OFFLOADING.md` after substantive work.

## 9. Risks, Gaps, and Things to Verify

| Risk, Gap, or Unknown | Why It Matters | How to Verify or Resolve |
|---|---|---|
| First source edition is not selected | Corpus quality and legal safety depend on the source. | Choose a public-domain or permission-cleared source and record it in `data/context/sources.jsonl`. |
| Copyright/license status of first texts is unknown | The project must avoid unsafe public/training data. | Document source name, URL/citation, license, rights status, and allowed uses before marking entries publishable. |
| Transliteration standard is not finalized | Consistency matters for search, glossary links, and model prompts. | Write a short `project-latin-v1` standard or style note before entering many poems. |
| Review rubric is not yet instantiated in project data | Human feedback is the core asset for future model improvement. | Create initial review records or a compact rubric doc before scaling beyond pilot entries. |
| AI environment is unknown | Local drafting depends on Ollama and optional packages/models. | Run `powershell -ExecutionPolicy Bypass -File .\scripts\abshaar.ps1 ai-check`. |
| Website is not built yet | Public output will eventually need pages and search. | Wait until there are publishable poems, then prototype static pages using exported `data/site/*.json`. |
| Test coverage is minimal | Only 2 unit tests currently ran, so behavior outside parser/status basics may be untested. | Add focused tests when changing CLI behavior, validation, export, prompt packs, or draft storage. |
| Empty corpus can make validation look deceptively complete | `validate` passes because there is no data to check. | Re-run validation after adding real working entries and JSONL records. |

## 10. Compact Version

Abshaar lives at `D:\Harvard\Poetry Model Project`. It is a local-first, open-source archive and AI-assisted translation/explanation project for South Asian mystical poetry. The repo has docs, Python automation under `src/abshaar/`, PowerShell scripts, JSONL templates, a Bulleh Shah working-entry template, and passing validation/tests. Current data state is empty: 0 working entries, 0 processed poems, 0 sources, 0 glossary terms, 0 people/events/themes, 0 reviews, and 0 model outputs. Known working commands include `powershell -ExecutionPolicy Bypass -File .\scripts\abshaar.ps1 status`, `powershell -ExecutionPolicy Bypass -File .\scripts\abshaar.ps1 validate`, and `$env:PYTHONPATH='src'; py -3.14 -m unittest discover -s tests`. The next real work is editorial/corpus work: confirm the first poet/source, likely Bulleh Shah; verify public-domain or permission-cleared source status; create a source record; create and fill 1-3 Markdown entries in `data/working/`; validate; build JSONL; then consider prompt packs and local Ollama drafting. The user wants precise markdown, PowerShell commands, no invented facts, unknowns marked clearly, and `OFFLOADING.md` updated after every substantive task.
