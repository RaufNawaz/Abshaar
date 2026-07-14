# OFFLOADING.md

Last updated: 2026-07-13

## 1. Project Overview

Abshaar is an open-source, local-first archive and AI-assisted translation and explanation system for Punjabi, Urdu, Persian-influenced, Braj/Bhakti, and Sufi poetry. Its purpose is to preserve original script, transliteration, translation layers, tashreeh, sources, glossary meaning, historical context, uncertainty, and human review without flattening cultural or metaphysical meaning. The first corpus target is Bulleh Shah, with the explicit long-term goal of training a source-grounded model that can become an expert on his poetry, language, textual variants, concepts, life, and historical reception. The live working tree contains 72 draft poem entries, 76 normalized Sufinama kaafi witnesses, 48 normalized non-kaafi Sufinama category witnesses, and a private 160-record PunjabLibrary Gurmukhi witness, plus sourced biography, a cautious timeline, and a complete category inventory.

### Main Objective

- Build a multi-source, source-aligned and human-reviewed Bulleh Shah corpus from the 72 existing entries, 76 Sufinama kaafi witnesses, 48 non-kaafi Sufinama witnesses, 160 PunjabLibrary Gurmukhi witnesses, and sourced historical context; use canonical-work clusters and evidence-aware annotations to prepare training/evaluation data for a future Bulleh Shah expert model.

### Current Stage

- Rafat source collection complete; Sufinama 76-kaafi and 48-record non-kaafi textual acquisition complete; PunjabLibrary 160-item Gurmukhi extraction complete but textually unverified; biography/context research and all Sufinama categories are inventoried. Canonical clustering, cross-script matching, and editorial review are now the principal bottlenecks.
- Verified on 2026-07-13: 72 working entries, 72 processed records, 7 sources, 76 normalized Sufinama kaafi witnesses, 48 normalized non-kaafi category witnesses, 160 Gurmukhi catalog/witness records, 124 Sufinama candidate-match records, 1 person, 11 sourced biographical claims, 6 timeline events, 13 Sufinama inventory categories, 0 public poems, 0 glossary/themes/reviews/model outputs, 0 validation errors, 144 expected placeholder warnings, and 19 passing tests.

### Current Working Direction

- Review the 76-record kaafi crosswalk and 48-record non-kaafi crosswalk without changing the 72 Markdown entries, then define canonical-work clusters so variants remain source-separated and cannot leak across training/evaluation splits.
- Correct or replace the defective Gurmukhi embedded-text layer, then create reviewed cross-script first-line links from the 160 Gurmukhi witnesses to Sufinama/Rafat clusters.
- Add Devanagari-aware matching or reviewed transliteration for the 40 non-kaafi records that currently have no candidate because the matcher only compares Roman and Urdu.
- Settle translation-field semantics and editorial standards, then fully annotate a representative five-poem vertical slice.

## 2. What Has Been Done

- Built the repository foundation and planning blueprint.
  - Details: Added the Python package, data directories and templates, project roadmap, model strategy, data guide, website architecture, setup guide, governance guidance, implementation manual, automation guides, contribution guidance, and content-license guidance.
  - Why it matters: The project has a clear archive-first and human-review-first strategy rather than starting with fine-tuning or a chatbot.
  - Files affected: `src/abshaar/`, `data/templates/`, `docs/`, `README.md`, `CONTRIBUTING.md`, `CONTENT_LICENSE.md`, `LICENSE`, and project configuration files.

- Implemented a standard-library Python CLI and cross-platform wrappers.
  - Details: Commands include `init`, `status`, `new-entry`, `build-data`, `validate`, `export-site`, `prompt-pack`, `ai-check`, and `draft`. Windows wrappers use PowerShell; macOS/Linux wrappers use shell scripts.
  - Why it matters: Humans can author Markdown while automation produces JSONL, validation results, prompt packs, and site data.
  - Files affected: `src/abshaar/*.py`, `scripts/abshaar.ps1`, `scripts/abshaar.sh`, `scripts/build_all.ps1`, `scripts/build_all.sh`, and `.github/workflows/validate.yml`.

- Created the one-stop project guide and handoff system.
  - Details: `START_HERE.md` is the command center. `AGENTS.md` requires a detailed CRAFT handoff after substantive work. Windows-only Codex handoff helpers exist in `codex_with_handoff.py` and `scripts/cxh*`.
  - Why it matters: Work can resume in a new chat or tool without reconstructing project history.
  - Files affected: `START_HERE.md`, `AGENTS.md`, `OFFLOADING.md`, `docs/11_codex_handoff_automation.md`, `codex_with_handoff.py`, and `scripts/cxh*`.

- Added macOS support on 2026-07-04.
  - Details: Added shell wrappers and cross-platform documentation. The Python core was already OS-independent. The Codex handoff wrapper remains intentionally Windows-specific.
  - Why it matters: The user works on both Windows and macOS.
  - Files affected: `scripts/*.sh`, `.gitattributes`, `AGENTS.md`, `README.md`, `START_HERE.md`, and setup/automation docs.

- Created the first Sufinama pilot entry and context records on 2026-07-04.
  - Details: Added `bulleh_shah_0001`, a Sufinama source record, a Bulleh Shah person record, and a draft Sufinama/Rekhta permission email. The entry includes original Shahmukhi and project transliteration; interpretation remains unfinished.
  - Why it matters: It proved the Markdown-to-JSONL workflow on real material and established a cautious citation/copyright posture.
  - Files affected: `data/working/bulleh_shah_0001.md`, `data/context/sources.jsonl`, `data/context/people.jsonl`, `data/processed/poems.jsonl`, and `outreach_sufinama_email.md`.

- Completed transcription of the 71-poem Taufiq Rafat selection from 2026-07-04 through 2026-07-06.
  - Details: Entries `bulleh_shah_0002` through `bulleh_shah_0072` contain visually transcribed calligraphic Shahmukhi, project-latin transliteration, Rafat's copyrighted English as a gated private reference, and Claude-drafted English. Interpretive layers remain TODO. Multi-spread and high-uncertainty readings are documented per file and in the corpus build log.
  - Why it matters: The first source collection is fully represented in draft form, so the bottleneck is now verification and scholarship rather than ingestion volume.
  - Files affected: `data/working/bulleh_shah_0002.md` through `data/working/bulleh_shah_0072.md`, `data/processed/poems.jsonl`, `data/context/sources.jsonl`, and `Bulleh Shah/CORPUS_BUILD_LOG.md`.

- Added a third translation slot during the corpus build.
  - Details: `src/abshaar/markdown_entry.py` now recognizes `# Literal Translation`, `# AI Translation`, and `# Literary Translation`; it emits JSON kinds `literal_gloss`, `ai_translation`, and `literary_translation`. The AI record is attributed to Claude.
  - Why it matters: Reference, model, and human renderings can be distinguished, but a semantic mismatch remains: Rafat's literary reference currently occupies the field named `literal_gloss`.
  - Files affected: `src/abshaar/markdown_entry.py`, `data/working/bulleh_shah_entry_template.md`, and all Rafat working entries.

- Audited the complete live repository on 2026-07-12.
  - Details: Read the core guides, all Python modules, scripts, tests, schemas, source/context records, corpus build log, working-entry patterns, Git state, and current validation/test output. Confirmed the current branch is `draft`, tracking `origin/draft`, with origin `https://github.com/RaufNawaz/Abshaar.git`. Did not alter poem content or regenerate `poems.jsonl`.
  - Verification: `./scripts/abshaar.sh status` confirmed 72 working and 72
    processed records; `./scripts/abshaar.sh validate` confirmed 0 errors and
    144 warnings; `PYTHONPATH=src python3 -m unittest discover -s tests -v`
    passed 2 tests; the poem template parsed with `python3 -m json.tool`;
    `git diff --check` passed; and `git check-ignore` confirmed the source PDFs
    are ignored. A first `py_compile` attempt failed because macOS Python tried
    to write bytecode under a sandbox-blocked Library cache; rerunning with
    `PYTHONPYCACHEPREFIX=/tmp/abshaar-pycache` succeeded.
  - Why it matters: Older documentation still described an empty or one-poem corpus and could have sent future assistants in the wrong direction.
  - Files affected: Documentation and coordination files only, plus one parser test and one JSONL template.

- Added shared Codex/Claude continuity safeguards on 2026-07-12.
  - Details: Added a multi-assistant workflow to `AGENTS.md`, created `CLAUDE.md`, updated the README and command center, required inspection of live diffs before edits, prohibited automatic removal of `.git/index.lock`, and required affected canonical docs plus `OFFLOADING.md` to be updated after substantive state changes.
  - Why it matters: Codex and Claude can now work from the same explicit continuity and non-overwrite rules.
  - Files affected: `AGENTS.md`, `CLAUDE.md`, `README.md`, and `START_HERE.md`.

- Added source-file and build-safety documentation on 2026-07-12.
  - Details: Added `Bulleh Shah/*.pdf` to `.gitignore` so local source scans cannot be staged accidentally. Identified the missing-placeholder build risk; the wrappers were subsequently fixed and verified later in this task.
  - Why it matters: It reduces the risk of staging source scans or destroying the generated draft corpus.
  - Files affected: `.gitignore`, `START_HERE.md`, `docs/09_automation_infrastructure.md`, `docs/10_plain_english_automation_guide.md`, and this handoff.

- Synchronized documentation and tests with the three-translation parser on 2026-07-12.
  - Details: Updated the data guide, transliteration workflow, poem JSONL template, and parser test to recognize and verify an `ai_translation` record. Explicitly documented the unresolved reference-translation versus literal-gloss mismatch.
  - Why it matters: Future contributors will see the real schema and the gap that must be resolved before review/training data are created.
  - Files affected: `docs/03_data_and_annotation_guide.md`, `docs/08_text_entry_transliteration_workflow.md`, `data/templates/poems.template.jsonl`, and `tests/test_markdown_entry.py`.

- Fixed and verified both full-build wrappers on 2026-07-12.
  - Details: `scripts/build_all.sh` and `scripts/build_all.ps1` now invoke
    `build-data --include-placeholders`. Added `tests/test_build_all.py` to keep
    both wrappers in parity. Ran the live macOS full build successfully.
  - Verification: The build wrote 72 processed poem records, reported 0 errors
    and 144 expected warnings, exported 3 sources, and preserved the aggregate
    SHA-1 of all 72 Markdown files exactly. The processed JSONL hash changed
    because it was regenerated from the current parser/working files, but its
    record count remained 72. PowerShell runtime was unavailable on this Mac;
    command parity is covered by the regression test.
  - Files affected: `scripts/build_all.sh`, `scripts/build_all.ps1`,
    `tests/test_build_all.py`, generated `data/processed/poems.jsonl`, and ignored
    `data/site/*.json`.

- Built the Sufinama acquisition and source-matching pipeline on 2026-07-12.
  - Details: Added `acquire-sufinama` and `match-source-manifest` CLI commands.
    The collector pairs language catalogs by stable UUID, caches raw Roman/Urdu
    pages, preserves diacritic Roman, plain Roman, Urdu, stanza IDs, line IDs,
    and token mapping IDs, writes normalized private witnesses, and generates a
    non-destructive crosswalk. Matching compares titles and all poem lines.
  - Verification: Live discovery completed with 76 paired records and 76 unique
    UUIDs. Full acquisition later wrote 76 normalized witnesses from 152 cached
    snapshots and regenerated 76 full-text, review-required candidate records.
    For kaafi-12 it ranked `bulleh_shah_0001` at 1.0 and `_0029` as a related
    candidate. Fourteen unit tests now pass, including cache portability,
    redirect normalization, script classification, coverage auditing, catalog
    UUID pairing, catalog-field aliases, and three-layer/alignment parsing.
  - Files affected: `src/abshaar/sufinama.py`,
    `src/abshaar/source_matching.py`, `src/abshaar/cli.py`,
    `src/abshaar/status.py`, `src/abshaar/validation.py`,
    `tests/test_sufinama.py`, `tests/test_source_matching.py`,
    `data/context/sufinama_source_items.jsonl`,
    `data/context/source_matches.jsonl`, source/template records, and ingestion
    documentation.

- Attempted the authorized Sufinama detail-page acquisition on 2026-07-12.
  - Details: Rauf stated he works with Sufinama, this is a collaborative research
    project, and he was instructed to scrape the site. The first full run using
    urllib reached the worker pool but stalled before writing cache files; it was
    interrupted. Curl transport and progress output were added. The follow-up
    one-record smoke test was rejected before execution because the environment's
    external-access approval quota was exhausted until a later time.
  - Why it matters: This failed attempt established the exact cache-write and
    network-approval failure modes; both were resolved later the same day.
  - Files affected: The 76-record catalog and implementation were preserved.

- Completed and audited the authorized Sufinama bulk acquisition on 2026-07-12.
  - Details: After the external limit reset, the first curl bulk run exposed a
    cross-platform cache-write bug: `Path.write_text()` rejected the `newline`
    argument and produced 152 view errors. Replaced it with portable
    `Path.open()`, added cache regression coverage, normalized `/ghazals/`
    redirects to `/kaafi/`, added matching curl language headers, classified
    scripts by dominant Unicode range so Devanagari cannot be mislabeled Roman,
    preserved redirected alternate-language layers, distinguished source-level
    `unavailable` views from real errors, and added offline cache reprocessing
    plus a run audit.
  - Verification: Final acquisition and offline rebuild each wrote 76 unique
    normalized witnesses. The cache contains 152 snapshots (33 MB) with 152
    recorded hashes and 149 distinct hashes. Availability is 145 `ok`, 7
    `unavailable`, and 0 `error`; the seven unavailable requests are three poems
    whose Roman and Urdu URLs both redirect to Hindi plus one poem whose Roman
    URL redirects to Urdu. Coverage is 72 plain Roman, 72 diacritic Roman, 73
    Urdu, and 3 Devanagari records. All 76 have mapping IDs, and all 72 witnesses
    containing both Roman and Urdu have identical stanza/line ID sequences and
    per-line mapping-ID sets.
    The full-text matcher produced 76 `needs_review` records: 11 top candidates
    score 1.0, 23 score at least 0.85, and 3 have no candidate among the existing
    72 entries. No canonical Markdown entry was modified.
  - Why it matters: The requested source corpus now exists as a reproducible,
    source-separated, private research dataset and can be rebuilt without
    network access.
  - Files affected: `src/abshaar/sufinama.py`, `src/abshaar/cli.py`,
    `tests/test_sufinama.py`, `.gitignore`,
    `data/raw/private/sufinama/*.html` (ignored),
    `data/processed/private/sufinama_bulleh_shah_kaafi.jsonl`,
    `data/processed/private/sufinama_run.json`,
    `data/processed/private/sufinama_match_manifest.jsonl` (ignored),
    `data/context/sufinama_source_items.jsonl`, and
    `data/context/source_matches.jsonl`.

- Extracted and audited the 160-work PunjabLibrary Gurmukhi witness on 2026-07-12.
  - Details: Added `extract-gurmukhi-pdf`, an optional-`pypdf` importer that segments consecutively numbered works, preserves page spans and raw embedded text, records source and parser checksums, and refuses partial ordinal sequences. It wrote a 160-item reviewable catalog and a separate ignored full-text witness without changing the 72 Markdown entries.
  - Verification: The exact extraction command was `PYTHONPATH=src /Users/rauf/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m abshaar extract-gurmukhi-pdf --input 'Bulleh Shah/Kafian - Baba Bulleh Shah (Baba Bulle Shah) (z-library.sk, 1lib.sk, z-lib.sk).pdf'`. Result: 149 pages, 160 unique ordinals 1–160, 0 missing, 0 duplicates, 0 empty titles, 0 empty texts, 120,133 extracted characters, and source SHA-256 `f4a6a1ba5274d30bc6d58b4e37afe85ffd9df4e5a9fe9474e8622b21094fa074`. A rendered page-2 sample proved that page images are clear but the embedded text drops/misorders some Gurmukhi characters. `PYTHONPATH=src /Users/rauf/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m abshaar export-site` then regenerated ignored site data with 4 sources and 0 public poems. Sixteen unit tests pass; validation remains 0 errors/144 warnings; `py_compile` and `git diff --check` pass. Ruff was not run because it is absent from both the bundled runtime and system path.
  - Why it matters: The project now has a much broader 160-work Gurmukhi witness for future cross-script verification while preserving honest quality and rights boundaries.
  - Files affected: `src/abshaar/gurmukhi_pdf.py`, `src/abshaar/cli.py`, `src/abshaar/status.py`, `src/abshaar/validation.py`, `tests/test_gurmukhi_pdf.py`, `pyproject.toml`, `data/context/punjab_library_source_items.jsonl`, `data/context/sources.jsonl`, ignored `data/processed/private/punjab_library_*`, `docs/13_gurmukhi_pdf_ingestion.md`, and related project guides/logs.

- Researched Bulleh Shah's life, textual history, and other Sufinama content on 2026-07-12.
  - Details: Used Sufinama's English/Hindi/Urdu profile and All/category pages, Ashna Hussain's 2018 Western Sydney University master's thesis, and the Government of Punjab Auqaf shrine page. Rewrote the person record to distinguish conventional facts from disputed details; added 11 claim-level notes with confidence/cautions, 6 timeline events, 3 new source records, and a 13-category Sufinama inventory.
  - Findings: Birthplace and exact dates are disputed; Shah Inayat Qadiri is the strongest recurring teacher association; corpus boundaries are uncertain because performance transmission preserves and recombines material. Beyond 76 kaafis, Sufinama reports 3 kalaam, 23 dohe, 7 shabads, 12 dohras, 1 athvara, 1 barahmasa, 1 holi, 24 quotes (with one page reporting 21), 1 e-book, 164 videos, 1 blog, and a profile. These categories overlap and are not additive unique-work counts.
  - Failed attempt: A read-only command using `SufinamaClient(..., transport='curl')` was prepared to test a non-kaafi detail page, but execution was rejected because the external-access approval quota was exhausted until 4:56 PM. The command did not run; no retry or workaround was attempted.
  - Verification: `abshaar status` reports 7 sources, 11 biographical claims, 6 events, and 13 inventory categories. All new JSONL parsed; project validation remains 0 errors/144 existing warnings. `export-site` regenerated ignored outputs with 1 person, 6 events, 7 sources, and 0 public poems.
  - Why it matters: The corpus now has a historically cautious knowledge layer and a complete map of Sufinama content that can drive the next authorized acquisition without double-counting overlapping categories.
  - Files affected: `data/context/people.jsonl`, `data/context/sources.jsonl`, `data/context/biographical_claims.jsonl`, `data/context/events.jsonl`, `data/context/sufinama_bulleh_shah_inventory.jsonl`, `docs/14_bulleh_shah_research_and_sufinama_inventory.md`, status/validation code, and project guides/logs.

- Acquired and audited all 48 inventoried non-kaafi Sufinama textual records on 2026-07-13.
  - Details: Added `acquire-sufinama-texts`, generalized the UUID catalog parser beyond kaafi, added an inline-doha parser, requested default/Urdu/Hindi views, preserved actual returned script layers plus stable UUID/stanza/line/token IDs, cached raw HTML, and generated a separate non-destructive crosswalk. The records cover 3 kalaam, 23 dohas, 7 shabads, 12 dohras, 1 athvara, 1 barahmasa, and 1 holi. They remain source-category witnesses with `canonical_work_id: null`, not claims of 48 unique works.
  - Commands: `./scripts/abshaar.sh acquire-sufinama-texts --discover-only --transport curl`; `./scripts/abshaar.sh acquire-sufinama-texts --transport curl`; and `./scripts/abshaar.sh acquire-sufinama-texts --offline --transport curl`.
  - Results: Live discovery found exactly 48 unique category records. Full acquisition wrote 48 normalized records and 48 `needs_review` matches with 0 errors, 41 source-unavailable requested views, 78 raw snapshot files referenced by records, and layer coverage of 7 plain Roman, 7 diacritic Roman, 8 Urdu, and 47 Devanagari records. All 48 contain token mapping IDs. The offline rebuild reproduced the same counts without network access.
  - Matching: One exact candidate links a kalaam witness to `bulleh_shah_0025`; 40 records have no candidate because most are Devanagari-only and the matcher currently compares only Roman and Urdu. Absence of a candidate is not evidence of a new canonical work.
  - Verification: The cache-only rebuild passed; 19 unit tests passed; `py_compile` passed with `PYTHONPYCACHEPREFIX=/tmp/abshaar-pycache`; validation remained 0 errors/144 expected warnings; status reported 48 non-kaafi items and 48 matches; and `git diff --check` passed with only the pre-existing CRLF warning for `scripts/build_all.ps1`.
  - Why it matters: The project now preserves all Sufinama textual categories inventoried for Bulleh Shah, materially broadening form and variant coverage while keeping training/evaluation provenance safe.
  - Files affected: `src/abshaar/sufinama.py`, `src/abshaar/cli.py`, `src/abshaar/status.py`, `src/abshaar/validation.py`, `tests/test_sufinama.py`, `.gitignore`, `data/context/sufinama_text_source_items.jsonl`, `data/context/sufinama_text_source_matches.jsonl`, `data/context/sufinama_bulleh_shah_inventory.jsonl`, `data/context/sources.jsonl`, `data/processed/private/sufinama_bulleh_shah_other_texts.jsonl`, `data/processed/private/sufinama_texts_run.json`, the ignored raw cache/match manifest, and affected project guides/logs.

## 3. Current State

| Item | Current Status | Notes |
|---|---|---|
| Repository path | Verified | `/Users/rauf/Desktop/Desktop - rauf’s MacBook Air/Harvard/Abshaar` |
| Current OS/shell | Verified | macOS with zsh; use `./scripts/*.sh`. Keep matching PowerShell instructions for Windows. |
| Git branch | Verified | `draft`, tracking `origin/draft`; HEAD `d52e7c9`. |
| Git remote | Verified | `https://github.com/RaufNawaz/Abshaar.git`; Rauf confirmed the repository is private. |
| Working tree | Dirty/shared | Many uncommitted and untracked corpus files plus Claude parser/template changes and this documentation audit. Preserve all work. |
| Git lock | Present | `.git/index.lock` is a 0-byte file dated 2026-07-11 17:23 local time. It may be stale or may indicate another process. Do not remove without verification. |
| Python package | Working | `abshaar` 0.1.0, Python >=3.11, standard-library core. |
| CLI | Working | Twelve commands, including `acquire-sufinama`, `match-source-manifest`, and `extract-gurmukhi-pdf`. |
| Working corpus | 72 draft files | 0001 Sufinama pilot; 0002-0072 all 71 Rafat poems. |
| Processed corpus | 72 JSONL records | `data/processed/poems.jsonl`, approximately 493 KB; generated with placeholders included. |
| Public poems | 0 | All source notes say publication=no; review statuses remain draft. |
| Training state | Private research | Existing Markdown source notes still say training=no; Rauf states the Sufinama collaboration authorizes private academic acquisition/training. Reconcile field values after the witness dataset is verified. |
| Sources | 7 | Added the Western Sydney thesis, Sufinama profile, and Government of Punjab Auqaf shrine profile to the prior four source records. |
| Sufinama catalog | 76 paired items | `data/context/sufinama_source_items.jsonl` has 76 unique UUIDs and Roman URLs. |
| Sufinama witness texts | Complete and audited | 76 normalized records; 152 cached snapshots; 145 requested views ok, 7 source-unavailable, 0 errors. |
| Source matches | 76 full-text records | All need human review; 11 top scores are 1.0, 23 are at least 0.85, and 3 have no existing candidate. |
| Sufinama non-kaafi catalog | Complete | 48 unique category records in `data/context/sufinama_text_source_items.jsonl`: 3 kalaam, 23 dohas, 7 shabads, 12 dohras, athvara, barahmasa, and holi. |
| Sufinama non-kaafi witnesses | Complete and audited | 48 normalized records; 0 errors; 41 source-unavailable requested views; 7 plain Roman, 7 diacritic Roman, 8 Urdu, 47 Devanagari; all 48 have mapping IDs. |
| Sufinama non-kaafi matches | 48 review-required records | One exact candidate (`kalaam` → `bulleh_shah_0025`); 40 have no candidate because the current matcher does not transliterate Devanagari. |
| PunjabLibrary Gurmukhi catalog | Complete, review required | 160 numbered records with page spans in `data/context/punjab_library_source_items.jsonl`. |
| PunjabLibrary Gurmukhi witness | Private, extracted, unverified | 160 full-text records in ignored `data/processed/private/punjab_library_bulleh_shah_kafian.jsonl`; embedded text is defective and PDF page images are authoritative. |
| People | 1 sourced draft | Bulleh Shah record now foregrounds disputed dates/birthplace and later-source limitations. |
| Biographical claims | 11 sourced drafts | Claim-level evidence status, confidence, caution, and source IDs are in `data/context/biographical_claims.jsonl`. |
| Timeline events | 6 sourced drafts | Cautious life/historical events; exact dates remain unknown for education and discipleship. |
| Sufinama content inventory | 13 categories | Includes profile, kaafi, kalaam, doha, shabad, dohra, athvara, barahmasa, holi, quotes, e-book, video, and blog. |
| Glossary/themes/reviews/model outputs | 0 | These remain the largest content gaps after text and source-relationship verification. |
| Translations | Mixed draft state | 71 Rafat entries have an AI section; 0001 predates it. Rafat reference translations are copyrighted and are incorrectly serialized as `literal_gloss`. |
| Original-text confidence | Needs human review | Shahmukhi was visually read from calligraphic pages. Many entries explicitly flag high-uncertainty readings. |
| Validation | Structurally passing | 0 errors, 144 warnings. Warnings are placeholders in 72 Markdown entries plus the same 72 processed records. |
| Tests | Passing | 19 tests cover build wrapper parity, Markdown translation slots, Gurmukhi PDF segmentation/auditing, source matching/catalog aliases, status IDs, Sufinama cache portability and offline network blocking, URL normalization, dominant-script handling, kaafi/non-kaafi catalog parsing, inline-doha separation, requested-view availability, audit metrics, and alignment parsing. |
| Full-build wrappers | Fixed and verified | Both include placeholders; live macOS build preserved 72 working and processed records. |
| Site data | Generated/ignored | `export-site` was rerun after research and exports 1 person, 6 events, 7 sources, and 0 public poems; directory is Git-ignored. |
| Website | Not implemented | Architecture is planned; there is no `website/` application yet. |
| Local AI environment | Needs verification | Ollama/API/model and optional AI packages were not checked during this audit. |
| Source scans | Local/untracked | PDFs under `Bulleh Shah/` must remain local; a new ignore rule protects them from accidental staging. |
| Corpus build log | Current through completion | `Bulleh Shah/CORPUS_BUILD_LOG.md` is the detailed source-specific history. |
| Rafat ingestion helper | Legacy; do not run | `Bulleh Shah/build_entries_from_rafat.py` predates the final three-slot layout and is retained as provenance only. |
| External acquisition | Complete | Both Sufinama source layers were acquired live and rebuilt offline; use their `--offline` commands for deterministic cache-only rebuilding. |

### Current Known Working Commands

Run from the repository root on macOS:

- `./scripts/abshaar.sh status`
- `./scripts/abshaar.sh validate`
- `./scripts/build_all.sh`
- `./scripts/abshaar.sh acquire-sufinama --discover-only`
- `./scripts/abshaar.sh acquire-sufinama --offline --transport curl`
- `./scripts/abshaar.sh acquire-sufinama-texts --discover-only --transport curl`
- `./scripts/abshaar.sh acquire-sufinama-texts --offline --transport curl`
- `./scripts/abshaar.sh match-source-manifest --manifest data/context/sufinama_source_items.jsonl`
- `./scripts/abshaar.sh extract-gurmukhi-pdf --input "Bulleh Shah/Kafian - Baba Bulleh Shah (Baba Bulle Shah) (z-library.sk, 1lib.sk, z-lib.sk).pdf"`
- `PYTHONPATH=src python3 -m unittest discover -s tests -v`
- `git status --short --branch`

Safe rebuild while unfinished entries remain:

- `./scripts/abshaar.sh build-data --include-placeholders`
- `./scripts/abshaar.sh validate`

Windows equivalents:

- `powershell -ExecutionPolicy Bypass -File .\\scripts\\abshaar.ps1 status`
- `powershell -ExecutionPolicy Bypass -File .\\scripts\\abshaar.ps1 validate`
- `powershell -ExecutionPolicy Bypass -File .\\scripts\\abshaar.ps1 build-data --include-placeholders`
- `$env:PYTHONPATH='src'; py -m unittest discover -s tests -v`

### Current Blockers

- Translation field semantics are inconsistent: a copyrighted literary reference is stored as `literal_gloss`.
- No public-domain or permission-cleared comparison edition has been selected for systematic verification of the visually transcribed Shahmukhi.
- The PunjabLibrary PDF's embedded Gurmukhi text is not trustworthy enough for canonical use, and rights in the 2017 digital transcription are unknown.
- The current matcher cannot compare Devanagari-only non-kaafi witnesses to project-latin/Shahmukhi entries, leaving 40 candidate lists empty.
- No formal five-poem editorial slice, transliteration standard, or instantiated review workflow has been selected.

### Current Open Questions

- What written Sufinama collaboration/authorization reference should be stored with the source record? Needs verification.
- Which Sufinama witnesses are exact matches, variants, excerpts, or new works relative to the 72 entries?
- What reviewed Devanagari-to-project-latin/Shahmukhi method should support matching without inventing source text?
- What `canonical_work_id` scheme should cluster source witnesses without merging their text?
- Which five poem IDs should form the first fully reviewed vertical slice?
- Which source edition should be used to verify Shahmukhi and variants?
- Should the schema add an explicit `reference_translation` kind and restore `literal_gloss` to Rauf's own close translation?
- How should `project-latin-v1` represent aspiration, long vowels, retroflex consonants, ain/ghain, and dialect variation?
- Who will act as language/source reviewer beyond Rauf, and what evidence is required before `publishable`?

## 4. Key Decisions and Rationale

| Decision | Rationale | Alternatives Considered | Effect on Future Work |
|---|---|---|---|
| Build an archive and annotation system before an AI product | Corpus quality, provenance, and human feedback determine model usefulness. | Chatbot first; bulk fine-tuning first | Editorial work and data integrity remain the immediate priority. |
| Use Markdown for human editing and JSONL for machines | Poetry and notes are easier to review in Markdown; automation can normalize data. | Hand-edit JSONL | Working entries remain canonical; processed JSONL is generated. |
| Start with Bulleh Shah | Existing source interest and templates provided a narrow initial corpus. | Kabir, Shah Hussain, Waris Shah, Baba Farid | The first gold corpus and website target Bulleh Shah. |
| Use the 71-poem Rafat selection as the first complete source collection | It provides facing Shahmukhi originals and English references with a clear page map. | Sufinama-only; Gurmukhi volume; other edition | 0002-0072 mirror Rafat poem order; human verification remains essential. |
| Keep all current poems non-public and non-training | Rafat's English is copyrighted and original transcriptions/reviews are unfinished. | Publish drafts; train on reference translations | Publication and training gates must stay closed until rights and review are explicit. |
| Preserve separate reference, AI, human, and interpretive layers | The project must reveal provenance and avoid hiding interpretation. | One blended English field | Schema migration is required because the current parser does not cleanly implement this principle. |
| Use a five-poem vertical slice next | Reviewing all 72 simultaneously would be slow and inconsistent. | Continue bulk ingestion; annotate all 72 at once | Standards can be tested and revised on a bounded representative set. |
| Add shared Codex/Claude startup and handoff rules | Both assistants edit the same working tree and can otherwise overwrite or misreport each other's work. | Rely on chat memory or Git commits alone | Both agents must inspect live state, update affected docs, and preserve concurrent changes. |
| Ignore local source PDFs | Project policy prohibits committing copyrighted scans. | Depend on manual staging discipline | `Bulleh Shah/*.pdf` is now ignored; bibliographic metadata and build logs remain available. |
| Treat Sufinama items as separate source witnesses | Roman/Urdu views and Rafat entries may represent variants or excerpts of one canonical work. | Append text into existing Markdown; add source ID without variant modeling | Acquisition never overwrites the 72 entries; crosswalk and future canonical-work clusters carry relationships. |
| Rely on Rauf's stated Sufinama collaboration authorization for private research acquisition | Rauf explicitly stated he works for Sufinama and was instructed to scrape the data. | Stop at citation-only metadata | Source record marks authorization as user-attested; written authorization details remain Needs verification. |
| Pair Sufinama language views by UUID | Roman and Urdu popularity order differs, while UUID sets match. | Zip items by rank or infer numbered slugs | The catalog has 76 deterministic paired records despite special/noncontiguous slugs. |
| Keep PunjabLibrary full text private and review-required | The underlying poems are public domain, but the 2017 digital edition's rights are unknown and its embedded text is visibly defective. | Commit the extraction as canonical; discard the source | Catalog metadata remains reviewable while full text stays ignored until rights and text are verified. |
| Store biography as claim-level evidence, not one seamless life story | Modern scholarship and Sufinama both expose disputed or internally inconsistent details. | Copy a popular biography into `people.jsonl` as fact | Future review can accept, reject, or refine individual claims without rewriting the whole biography. |
| Treat Sufinama category counts as overlapping source metadata | Kalaam, shabad, holi, kaafi, and performance categories visibly repeat compositions. | Add all displayed counts as unique poems | Future acquisition preserves category provenance and deduplicates only through reviewed canonical-work clusters. |
| Store non-kaafi material in a separate 48-record witness corpus and crosswalk | The seven categories mix detail pages and inline dohas, often redirect language requests, and overlap kaafis. | Append them to the 76-kaafi file; create 48 new Markdown poems; deduplicate automatically | Source category, actual returned scripts, UUID/line/token provenance, and uncertainty remain visible; no canonical poem or training split changes until review. |

## 5. User Preferences and Instructions

### Persistent Preferences

- Use detailed, practical, precise, implementation-focused documentation.
- Prevent context loss across Codex, Claude, new chats, machines, and coding environments.
- Use the CRAFT method for `OFFLOADING.md`.
- Use clear Markdown headings, bullets, checklists, tables, paths, commands, errors, and decisions.
- Do not invent facts. Mark unknown or unverified claims as `Unknown` or `Needs verification`.
- Match commands to the active OS: PowerShell on Windows; zsh/bash on macOS.
- Preserve cross-platform scripts: when adding a project script, normally add both `.ps1` and `.sh` versions.
- Preserve original text and keep transliteration, reference translation, AI drafts, human translation, and tashreeh distinguishable.
- The user prioritizes building the private academic/training corpus now and does not want publication-focused copyright discussion to block research work.
- The user's end goal is to train a model that is genuinely expert on Bulleh Shah; corpus expansion must therefore support textual expertise, variant awareness, interpretation, biography/history, and leakage-safe evaluation rather than raw text volume alone.
- The user states he works with Sufinama and has been instructed to scrape the Bulleh Shah data for this collaborative research project.

### Project-Specific Instructions

- Read `AGENTS.md`, `CLAUDE.md`, `OFFLOADING.md`, and relevant task logs before substantive work.
- Update `OFFLOADING.md` after every substantive task, including code, data, research, analysis, architectural decisions, generated outputs, and documentation changes.
- Also update every canonical guide, template, schema, test, or build log affected by a change; the handoff is not a substitute for source documentation.
- Before editing, inspect `git status` and the diff for target files. Treat pre-existing changes as user/other-agent work.
- After state-changing commands, document the exact command, flags, output, errors, and resulting files.
- Re-read target files before editing when Claude or Codex may be concurrently active.
- Use explicit staging paths. Do not run `git add .`.
- Do not remove `.git/index.lock` automatically.

### Things to Avoid

- Do not overwrite, revert, delete, stage, or commit another assistant's changes without explicit authorization.
- Do not claim the working tree is clean; it is currently heavily modified and untracked.
- Do not run plain `build-data` while the canonical processed corpus is expected to include unfinished entries.
- Do not erase provenance, source-specific text layers, UUIDs, line IDs, token IDs, or authorization status even in a private training dataset.
- Do not append Sufinama witness text into a Rafat Markdown entry or treat a source ID as proof that two textual versions are identical.
- Do not treat validation as evidence of poetic, linguistic, historical, or legal correctness.
- Do not proceed to website chat, RAG, or fine-tuning before a reviewed and rights-safe corpus slice exists.

## 6. Important Context a New Chat Must Know

- The live filesystem is substantially ahead of the last commit and older handoff text. Never infer project state from Git history alone.
- `Bulleh Shah/CORPUS_BUILD_LOG.md` is the authoritative detailed history of the 71-poem Rafat transcription effort.
- `Bulleh Shah/build_entries_from_rafat.py` is a legacy ingestion helper; its template is stale and it must not overwrite the completed corpus.
- Entry numbering is source-order based: 0001 is the Sufinama pilot; 0002-0072 equal Rafat poems 1-71.
- The Rafat Shahmukhi pages are calligraphic Nastaliq and were visually transcribed. Structural validation cannot verify those readings. High-uncertainty notes are embedded in many entries.
- The repository is private per Rauf. Rafat's English remains a distinct reference layer; existing source-note training flags have not yet been reconciled with the current private-research direction.
- The parser currently labels the Rafat reference slot as `literal_gloss`, even though Rafat's renderings are literary adaptations. This is a data-model problem, not merely a heading preference.
- The first Sufinama pilot predates the three-slot layout and lacks `# AI Translation`.
- `data/processed/poems.jsonl` contains unfinished entries only because it was built with `--include-placeholders`.
- Both full-build wrappers now include that flag and were verified to preserve 72 records.
- The 144 validation warnings are expected but meaningful: every poem still has editorial TODO content, and each warning appears once in Markdown and once in processed JSONL.
- The project has no formal review records, glossary, themes, Q&A, website, or RAG system yet; it does have 6 cautious timeline events. Bulk transcription completion does not equal corpus MVP completion.
- The immediate value lies in a five-poem reviewed vertical slice that proves the complete editorial, source, rights, and review workflow.
- Codex and Claude share this repository. The next assistant must merge useful concurrent changes rather than replacing files from memory.
- Sufinama discovery is complete: 76 paired UUID records are stored in `data/context/sufinama_source_items.jsonl`; the catalog includes numbered and special slugs and some page-two records whose displayed titles are not Roman.
- `src/abshaar/sufinama.py` implements raw caching, three-view parsing, alignment preservation, checksums, resume/refresh, and crosswalk generation. Use curl transport on this Mac.
- The full witness acquisition is complete. Seven requested language views are
  unavailable at the source: three witnesses redirect both requested views to
  Hindi, and one redirects its Roman request to Urdu. These are retained as
  alternate-language layers and are not counted as acquisition errors.
- Offline rebuilding is supported with `acquire-sufinama --offline`; it reads the
  saved catalog and all 152 cached snapshots without contacting Sufinama.
- Non-kaafi Sufinama acquisition is also complete: 48 source-category witnesses
  and 48 separate match records are stored in the new `sufinama_text_*` files.
  Rebuild with `acquire-sufinama-texts --offline --transport curl`. The 41
  unavailable requested views are source limitations, not errors or missing data
  to synthesize.
- Forty non-kaafi match records have no candidate because most returned text is
  Devanagari and `source_matching.py` currently compares only Roman and Arabic
  scripts. Do not classify those records as unique works on that basis.
- The 72 Markdown entries were hash-verified unchanged after running the fixed full build. Source ingestion must continue to preserve them.
- The PunjabLibrary importer preserves 160 numbered Gurmukhi witnesses as a separate collection. `data/context/punjab_library_source_items.jsonl` is the reviewable catalog; the full text and run audit are ignored/private. Do not copy extracted text into poem entries without page-image verification.
- The biography layer is intentionally cautious. `data/context/biographical_claims.jsonl` distinguishes multiple-source conventions, later tradition, scholarly inference, disputes, and present-day official evidence.
- Sufinama's 13 inventoried categories overlap. The inventory is a source map, not a claim that the site contains 312 unique Bulleh Shah works/media objects.

## 7. Next Steps

### Urgent

- [ ] Review `data/context/source_matches.jsonl` and classify exact witness, variant, excerpt/full, possible, and unmatched relations; do not auto-merge.
- [ ] Review `data/context/sufinama_text_source_matches.jsonl`, beginning with the exact kalaam → `bulleh_shah_0025` candidate and the known category overlaps; do not treat 40 empty candidate lists as unmatched works.
- [ ] Add a `canonical_work_id`/work-cluster layer so source variants can be grouped and kept out of opposite train/evaluation splits.
- [ ] Add a reviewed Devanagari matching/transliteration layer so the 47 Devanagari non-kaafi witnesses can be compared without erasing their original source text.
- [ ] Human-check the 160 PunjabLibrary headings against rendered pages, starting with the five-poem review slice, and record cross-script witness relationships without assuming source-order identity.
- [ ] Verify whether any active Git process owns `.git/index.lock`; remove it only after confirming it is stale and only with user authorization if removal is needed.
- [ ] Decide the translation schema: add an explicit private/reference translation field or storage path, reserve `literal_gloss` for Rauf's own close translation, migrate the template/parser/records, and document the decision.
- [ ] Select and document a representative five-poem review slice. Recommended
  starting set: `bulleh_shah_0002` (Alif/foundational vocabulary), `_0029`
  (Ranjha/identity and cross-source comparison with 0001), `_0031` (ritual
  critique), `_0035` (long three-spread, high-uncertainty anti-scholastic kafi),
  and `_0038` (very short Names couplet). Confirm or revise this set before
  editing; it is a recommendation, not a recorded user decision.
- [ ] Select a public-domain or permission-cleared Kulliyat/edition for Shahmukhi verification and record it in `data/context/sources.jsonl`.

### Soon

- [ ] Write a concrete `project-latin-v1` specification with examples from the selected five poems.
- [ ] Turn the review rubric into a reusable checklist and create the first `data/annotations/reviews.jsonl` record shape for source text, transliteration, AI draft, human translation, tashreeh, and rights.
- [ ] Fully review one selected poem end to end: verify Shahmukhi, correct transliteration, write Rauf's literal gloss and literary translation, write tashreeh, add terms/themes, and record reviewer/confidence/source evidence.
- [ ] Rebuild with `./scripts/abshaar.sh build-data --include-placeholders`, validate, run tests, and confirm the processed count remains 72.
- [ ] Repeat the same workflow for the other four selected poems and revise the standard only through explicit documented decisions.
- [ ] Add the first glossary entries and themes from the reviewed slice, with poet-specific meanings and `do_not_flatten_to` guidance.
- [ ] Store the written collaboration/authorization reference, if available, with the Sufinama source record.
- [ ] Add saved live HTML fixtures after acquisition and regression tests for interior-line matches, 0001/0029 variant clustering, deterministic reruns, and non-mutation of all 72 entries.

### Optional Improvements

- [ ] Add source-intake and review-assistant commands after the editorial contract is stable.
- [ ] Build a local review interface once at least five poems have real review records.
- [ ] Prototype the static Astro website only after at least five poems are publishable and rights-cleared.
- [ ] Add retrieval and source-grounded Q&A after glossary, themes, people, and reviewed tashreeh exist.
- [ ] Evaluate local Ollama/model readiness only when the reviewed corpus can provide grounded context.
- [ ] Defer LoRA/QLoRA until there are at least 500 high-quality, legally usable reviewed examples.

## 8. Restart Prompt

Copy and paste this into a new chat or Codex session:

> I am continuing the Abshaar project, a local-first, human-reviewed archive and AI-assisted interpretation system for South Asian mystical poetry.
>
> First, read `AGENTS.md`, `CLAUDE.md`, `OFFLOADING.md`, and `Bulleh Shah/CORPUS_BUILD_LOG.md`. Then run `git status --short --branch` and inspect the diff for every file you may edit. Codex and Claude share this working tree, so preserve all pre-existing modified and untracked work.
>
> Current state: the live macOS working tree contains 72 draft Bulleh Shah entries, 76 normalized Sufinama kaafi witnesses, 48 normalized non-kaafi Sufinama category witnesses, and 160 ignored/private PunjabLibrary Gurmukhi witnesses. Internet research adds 7 total source records, 11 sourced biographical claims, 6 timeline events, and a 13-category Sufinama inventory. The 48 non-kaafi records cover all inventoried kalaam, doha, shabad, dohra, athvara, barahmasa, and holi items, but these categories overlap and are not unique-work totals. Validation is 0 errors/144 expected warnings; 19 tests pass.
>
> Important files: `START_HERE.md`, `OFFLOADING.md`, `docs/12_sufinama_source_ingestion.md`, `docs/13_gurmukhi_pdf_ingestion.md`, `docs/14_bulleh_shah_research_and_sufinama_inventory.md`, `Bulleh Shah/CORPUS_BUILD_LOG.md`, `data/context/biographical_claims.jsonl`, `data/context/events.jsonl`, `data/context/sufinama_bulleh_shah_inventory.jsonl`, the three source-item catalogs, both Sufinama match files, both normalized Sufinama witness files, `src/abshaar/sufinama.py`, `src/abshaar/gurmukhi_pdf.py`, and the 72 working entries.
>
> Immediate work: review and classify the 76-record kaafi and 48-record non-kaafi crosswalks; add reviewed Devanagari matching; introduce canonical work clusters; split future training/evaluation data by cluster; then resolve translation schema semantics and annotate a representative poem slice. Rebuild both Sufinama outputs without network access using `./scripts/abshaar.sh acquire-sufinama --offline --transport curl` and `./scripts/abshaar.sh acquire-sufinama-texts --offline --transport curl`.
>
> Safety: `build_all` is fixed and safe for the current drafts. Never overwrite the 72 Markdown entries with Sufinama data; keep each source witness separate and preserve UUID/line/token provenance. Do not remove `.git/index.lock` without verifying it is stale.
>
> Follow these preferences:
> - Use precise, practical Markdown.
> - Preserve context and concurrent work.
> - Do not invent facts.
> - Mark unknowns as “Unknown” or “Needs verification.”
> - Match commands to the active OS.
> - Update all affected canonical docs and `OFFLOADING.md` after substantive work.

## 9. Risks, Gaps, and Things to Verify

| Risk, Gap, or Unknown | Why It Matters | How to Verify or Resolve |
|---|---|---|
| Sufinama authorization is user-attested but no written reference is stored | Future collaborators need to know the scope of the research authorization. | Add an email, agreement ID, or internal reference to the source record when available. |
| Requested Sufinama language views are unavailable | The kaafi run has 7 unavailable views and the non-kaafi run has 41; redirects often return Hindi/Devanagari instead of requested Urdu/Roman. | Preserve returned layers and `unavailable` statuses; seek partner exports or add reviewed project transliteration only as a separate layer. |
| Both Sufinama crosswalks are machine-generated | Similarity scores do not establish identity, variant type, completeness, or source dependence. | Human-review all 76 kaafi and 48 non-kaafi records before assigning `canonical_work_id` or training splits. |
| Gurmukhi embedded text is defective | Visual inspection showed clear rendered text but missing/misordered extracted characters and irregular spaces. | Use page images as authority; obtain a clean rights-cleared text or human-correct selected records before matching/training. |
| PunjabLibrary digital-edition rights are unknown | Public-domain poems do not automatically establish rights in a 2017 selection/transcription/typography. | Keep the full extraction ignored/private; verify edition terms or obtain permission before committing or redistributing it. |
| Biography rests mostly on later evidence | Popular accounts often present disputed birthplace, education, and hagiographic anecdotes as settled fact. | Review claim-by-claim; seek earlier tazkira/hagiographical sources and critical scholarship; preserve evidence type and uncertainty. |
| Sufinama work categories overlap | Counts for kaafi, kalaam, shabad, holi, video, and other views can repeat the same composition. | Preserve category metadata and assign canonical-work relationships only after item-level review. |
| Devanagari-only matching is unsupported | Forty non-kaafi records have no candidate because the matcher compares only Roman and Urdu, not because they are necessarily new works. | Add reviewed Devanagari transliteration/matching and rerun the separate crosswalk before clustering. |
| Rafat reference translations are in working files | They are copyrighted and should not enter a public/open corpus. | Decide private-Git versus Git-ignored storage; migrate before public release. |
| Source PDFs are local | Accidental staging would redistribute scans. | The new ignore rule protects `Bulleh Shah/*.pdf`; verify with `git check-ignore -v`. |
| Source variants can leak across train/evaluation splits | 0001 and 0029 already show that one work can have multiple witnesses. | Introduce canonical-work clusters and split datasets by cluster. |
| Translation-field semantics are wrong | Rafat's literary adaptation is serialized as a literal gloss, contaminating review/training meaning. | Introduce a reference kind/storage layer and migrate data before creating gold records. |
| 0001 lacks the AI section | It does not conform to the newer template and always serializes an empty AI record. | Decide whether AI is optional; update validation/schema or add a reviewed draft explicitly. |
| Shahmukhi readings are unverified | Calligraphic visual transcription includes uncertain lines and possible character errors. | Cross-check selected poems against a reliable edition and use a native/scholarly reviewer. |
| Transliteration scheme is informal | Search, alignment, and glossary consistency will drift. | Write and test `project-latin-v1` before reviewing many entries. |
| No formal reviews exist | Human corrections are the project's intended core asset. | Define the review record and complete a five-poem vertical slice. |
| Validation is structural only | Zero errors can create false confidence about meaning and rights. | Use separate source, linguistic, interpretive, and rights review gates. |
| Live Sufinama parser fixtures are not stored | Synthetic tests pass but cannot cover every live page variant or redirect. | Save authorized representative fixtures after acquisition and add deterministic parser regressions. |
| `.git/index.lock` exists | Git write operations may fail or conflict with another process. | Verify process ownership/activity; do not delete automatically. |
| Working tree is heavily uncommitted | Concurrent work is vulnerable to accidental overwrite or broad staging. | Use explicit files, inspect diffs, coordinate Codex/Claude, and commit only with user authorization. |
| Some catalog page-two records display Hindi/Urdu rather than Roman | A Roman view may be missing or redirect for some witnesses. | Preserve per-view availability/errors and quarantine rather than failing the whole corpus. |
| Ollama and optional AI packages are unverified | Local drafting commands may fail. | Run `./scripts/abshaar.sh ai-check` later, when AI drafting is actually needed. |
| Website and RAG are not implemented | Roadmap language may imply more product functionality than exists. | Treat them as later milestones after reviewed, rights-safe poems exist. |

## 10. Compact Version

Abshaar is a private, local-first, human-reviewed archive and AI-assisted interpretation project shared by Codex and Claude, with the long-term goal of training a source-grounded Bulleh Shah expert model. The live tree contains 72 draft poem entries, 76 normalized Sufinama kaafi witnesses, 48 normalized non-kaafi Sufinama category witnesses, and 160 private PunjabLibrary Gurmukhi witnesses. Sourced research adds 7 sources, 11 claim-level biography records, 6 timeline events, and a 13-category inventory. The key cautions are disputed life details, uncertain corpus boundaries, defective Gurmukhi embedded text, overlapping source categories, 40 Devanagari-heavy match records without candidates, and no completed human-reviewed gold slice. Validation has 0 errors/144 expected warnings and 19 tests pass. Next, review both Sufinama crosswalks, add Devanagari-aware matching and canonical clusters, resolve translation-field semantics, and build the five-poem gold slice. Never overwrite source variants or remove `.git/index.lock` automatically; update affected docs and `OFFLOADING.md` after substantive work.
