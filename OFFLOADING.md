# OFFLOADING.md

Last updated: 2026-08-16

## 1. Project Overview

Abshaar is an open-source, local-first archive and AI-assisted translation and explanation system for Punjabi, Urdu, Persian-influenced, Braj/Bhakti, and Sufi poetry. Its purpose is to preserve original script, transliteration, translation layers, tashreeh, sources, glossary meaning, historical context, uncertainty, and human review without flattening cultural or metaphysical meaning. The first corpus target is Bulleh Shah, with the explicit long-term goal of training a source-grounded model that can become an expert on his poetry, language, textual variants, concepts, life, and historical reception. The live working tree contains 72 draft poem entries, 76 normalized Sufinama kaafi witnesses, 48 normalized non-kaafi Sufinama category witnesses, and a private 160-record PunjabLibrary Gurmukhi witness, plus sourced biography, a cautious timeline, and a complete category inventory.

### Main Objective

- Build a multi-source, source-aligned and human-reviewed Bulleh Shah corpus from the 72 existing entries, 76 Sufinama kaafi witnesses, 48 non-kaafi Sufinama witnesses, 160 PunjabLibrary Gurmukhi witnesses, and sourced historical context; use canonical-work clusters and evidence-aware annotations to prepare training/evaluation data for a future Bulleh Shah expert model.

### Current Stage

- Rafat source collection complete; Sufinama 76-kaafi and 48-record non-kaafi textual acquisition complete; PunjabLibrary 160-item Gurmukhi extraction complete but textually unverified; biography/context research and all Sufinama categories are inventoried. **AI-drafted interpretive layers (Literary Translation, Tashreeh, Key Terms, Themes) are now complete for all 72 entries** (commits `663bec2`, `bfbd30e`, `2651e33`, 2026-07-13/14).
- Verified live on 2026-08-15: clean working tree on `draft`, 4 commits ahead of `origin/draft` (unpushed); 72 working entries, 72 processed records, 7 sources, 76 + 48 Sufinama witnesses, 160 Gurmukhi records, 124 candidate-match records, 1 person, 11 biographical claims, 6 timeline events, 13 inventory categories, 0 public poems, 0 extracted glossary/themes/reviews/model outputs, 0 validation errors, **34 warnings (all false positives — see below)**, 19 passing tests. `.git/index.lock` no longer exists.
- **Finding (2026-08-15): the remaining 34 placeholder warnings are all false positives.** `has_placeholder` in `src/abshaar/text.py` flags ANY `[bracketed text]`; the 17 flagged entries contain only legitimate uncertainty annotations (`[uncertain line — …]`), supplied words, and `[[cross-references]]`. Zero genuine template placeholders remain. Fix the check (plan Phase 0.1), never the entry content.

### Current Working Direction

- Execute `docs/15_bulleh_shah_expert_model_implementation_plan.md` (written 2026-08-15 at Rauf's direction): a 6-phase, low-human-intervention pipeline to a private Bulleh Shah expert system (base Qwen3 + RAG over a consolidated knowledge base + LoRA on synthetic grounded instruction data + honesty training + eval suite), each phase executable by cheaper models with mechanical acceptance gates. It supersedes the ordering of §7 below where they conflict; rights rules are unchanged.
- **Progress as of 2026-08-15 evening:** Phases 0–1 complete and gate-verified; Phase 2 code complete (index build was downloading BGE-M3); Phase 3 core dataset complete (1,178 gated examples) with the paraphrase-augmentation command implemented but not run; Phase 4 harness and probes complete, baselines not yet run; Phase 5/6 scaffolding committed. Devanagari-aware matching added and both crosswalks regenerated (0 candidate-less records remain, all `needs_review`).
- **STANDING CONSTRAINT (Rauf, 2026-08-15; reaffirmed 2026-08-16): do not run the Ollama models (smoke test, baselines, `ask`, `augment-training-data`, `run-eval`, or any generation) until he explicitly says so.** On 2026-08-16 Rauf added the reason and timing: he will only run the model in a cool environment so the laptop does not run hot, in a few days — until then, non-model work continues. This also covers the compute-heavy `build-index` embedding step. Training (Phase 5) also waits because baselines must precede it.
- **Download/prep state — COMPLETE as of 2026-08-16.** `qwen3:4b` and `qwen3:8b` both pulled (confirmed via `ollama list`); **mlx-lm 0.29.1 installed into `.venv` and import-verified** (the cp39 wheel works on the Python 3.9 venv — the runbook §7 venv-rebuild contingency was NOT needed); BGE-M3 fully downloaded (2.4 GB in `~/.cache/huggingface`); `ollama serve` is running. `./scripts/abshaar.sh ai-check` (a status check only — CLI presence, API reachability, package list; no generation) confirms: Ollama 0.32.13, API available, both models installed, all five optional Python packages (ollama, sentence_transformers, chromadb, transformers, torch) installed. **The only precondition-checklist item not yet done is the Chroma index build (`build-index`), deliberately deferred — it embeds ~1,303 KB records, which is real sustained compute and the reason Rauf wants to wait for a cool environment.** When he authorizes it, the runbook's §1 preconditions checklist should otherwise pass immediately; start at `build-index` then Step 2 (RAG smoke test).
- **Crosswalk review AI first pass complete (2026-08-16):** all 124 match records classified (1 exact_witness / 30 variant / 10 excerpt / 1 possible / 82 unmatched) with per-record evidence and notes; every record carries `human_confirmed: false` pending Rauf's confirmation. See §2 entry and `docs/12` §"Crosswalk classification".
- The earlier direction items (crosswalk review, Gurmukhi correction, five-poem human gold slice) remain valid quality work but are no longer blocking; the plan replaces human review gates with conservative automation plus validators, with accepted risks recorded in the plan §9.

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

- Completed AI-drafted interpretive layers for all 72 entries on 2026-07-13/14 (commits `663bec2`, `bfbd30e`, `2651e33`).
  - Details: Every entry (including pilot 0001 and the athwara/baramaha day/season poems) now has a Literary Translation, analytical Tashreeh, Key Terms, and Themes, drafted by Claude and labeled for human review. This work was committed but was not recorded here or in the corpus build log at the time; recorded retroactively on 2026-08-15 after live verification.
  - Why it matters: The corpus is now fully drafted across all layers; the bottleneck moved from drafting to consolidation, verification, and training infrastructure.
  - Files affected: `data/working/bulleh_shah_0001.md`–`_0072.md`, `data/processed/poems.jsonl`.

- Executed Phase 0 of the training plan on 2026-08-15 (Claude).
  - Details: (0.1) Replaced the blanket bracket regex in `src/abshaar/text.py` with template-slot and instruction-verb patterns; validation is now 0 errors/0 warnings with all 72 entries byte-identical, verified by a full scan of all 43 corpus bracket spans and all 7 template placeholders. (0.2) `# Literal Translation` sections carrying a published-reference citation now serialize as `reference_translation` (`rights: copyrighted`, `publishable: false`, `trainable: false`); 71 Rafat entries take that path while 0001 keeps its genuine Claude-drafted `literal_gloss` — a discovery that corrected the plan's original "zero literal_gloss" gate. AI-drafted attribution notes now set `created_by: ai`/`model: claude` (72/72 literary translations, tashreeh). Validation errors on any trainable reference; `export-site` strips reference translations defensively. (0.3) New `src/abshaar/training_export.py` + `export-training-corpus` CLI: emits only trainable layers and fails (exit 1) on any 8-gram overlap with reference translations. Its FIRST LIVE RUN caught 3 real leaks — the tashreeh of 0007/0017/0033 quoted Rafat verbatim — fixed by paraphrase in those three entries (the only content edits). Final export: 360 trainable layers, 9 flagged uncertain.
  - Verification: 29/29 tests (3 new test files/cases), `./scripts/build_all.sh` clean (0 errors/0 warnings), gate script confirming 72 records / 71 reference + 1 gloss / flag correctness, live leak-scan pass after the fixes.
  - Why it matters: The rights constraint is now a failing check rather than an intention, and it has already proven itself by catching real copyright leakage that every previous review missed.
  - Files affected: `src/abshaar/{text,markdown_entry,validation,export,cli,training_export}.py`, `tests/{test_text,test_markdown_entry,test_training_export}.py`, `data/templates/poems.template.jsonl`, `docs/03_data_and_annotation_guide.md`, `data/working/bulleh_shah_{0007,0017,0033}.md`, `data/processed/poems.jsonl`, `data/processed/training/trainable_layers.jsonl`, `docs/15_bulleh_shah_expert_model_implementation_plan.md`, `Bulleh Shah/CORPUS_BUILD_LOG.md`.

- Executed Phase 1 of the training plan on 2026-08-15 (Claude).
  - Details: (1.1) New `src/abshaar/lexicon.py` + `extract-lexicon` CLI mechanically parses every entry's Key Terms/Themes sections into `data/lexicon/terms.jsonl` (321 terms; headword, per-poem meaning, `do_not_flatten_to`, example poems, `review_status: ai_draft`) and `data/context/themes.jsonl` (297 themes). Every entry contributed ≥1 term. (1.2) New `src/abshaar/clusters.py` + `build-clusters`: union-find over crosswalk exact matches — ALL score-1.0 candidates merge (strengthened mid-execution because kaafi-12 scored 1.0 against both 0001 and 0029; the top-candidate-only rule would have left that variant pair splittable). Result: 343 clusters / 356 members / 12 multi-member, sub-1.0 candidates ≥0.85 kept as `related_candidates`, deterministic rerun verified. (1.3) New `src/abshaar/knowledge_base.py` + `build-kb`: 1,303 records in `data/processed/private/knowledge_base.jsonl` (72 originals, 72 transliterations, 1 gloss, 71 AI + 72 literary translations, 72 tashreeh, 321 terms, 297 themes, 11 claims, 6 events, 7 sources, 289 Sufinama witness view-texts, 12 cluster relations), each with kind/rights/trainable/uncertainty/provenance; every record leak-scanned against the Rafat reference index. Also installed the AI stack into `.venv` (chromadb, sentence-transformers, torch — import-verified); Ollama itself is NOT installed yet.
  - Verification: 35/35 tests; `validate` clean including the three new JSONL outputs; determinism (md5 diff on rerun); 356 members each in exactly one cluster; 0001/0029/kaafi-12 confirmed in one cluster.
  - Why it matters: The KB is the retrieval and generation substrate for Phases 2–3; the cluster layer makes train/eval splits leak-safe by construction.
  - Files affected: `src/abshaar/{lexicon,clusters,knowledge_base,cli,validation,training_export}.py`, `tests/test_lexicon_and_clusters.py`, `data/lexicon/terms.jsonl`, `data/context/{themes,canonical_clusters}.jsonl`, `data/processed/private/knowledge_base.jsonl`, `data/processed/training/trainable_layers.jsonl` (regenerated with `id` field), `docs/15_…plan.md`, `OFFLOADING.md`.

- Decided and applied `project-latin-v1` transliteration normalization on 2026-08-15 (Rauf's decisions; Claude implementation).
  - Details: Rauf answered the docs/16 §3 decision sheet (inline + follow-up questions): macron long vowels, dotted retroflexes, nasal inventory n / n̄ (n+combining macron above) / retroflex ṇ, `ʿ` for ʿain and `ġ` for ġain, aspiration digraphs, `-e-` izafat, line starts capitalized with mixed case tolerated, full Arabic-loan marking as the review-time target. Implementation: `src/abshaar/translit.py` (`normalize-translit` CLI, dry-run default) converted all 72 entries' Transliteration sections; `lint_translit_v1` now runs inside `validate` as warnings; `normalize_roman` was made style-invariant (ā≡aa→a, ī≡ee→i, ū≡oo→u, ʿ dropped) so matching keys survive style changes. Only mechanically-certain conversions were applied — unmarked ʿain/loan consonants and vowel-length beyond the style's own signals remain review work (spec §5 records this honestly). Both crosswalks, clusters, KB, dataset, mlx export, probes, trainable layers, and the review queue were regenerated.
  - Verification: protected-section SHA-1 (Original + all translation/tashreeh sections) identical before/after (`30f12950…`); normalizer idempotent (second apply = 0 changes); 67/67 tests; `validate` 0 errors / 0 warnings; exact-match regression check: 13 exact witness pairs before, **16 after — none lost, 3 GAINED** (witnesses of 0010, 0033, 0054 had been hidden by the style mismatch), so multi-member clusters grew 12→15 and the dataset 1,178→1,181 (variant_awareness 12→15).
  - Bugs hit and fixed during execution: `Path.write_text(newline=)` fails on the Python 3.9 venv (same class as the 2026-07-12 sufinama cache bug — fixed with `Path.open`); the section splice initially ate the blank line before the next heading (fixed, re-applied); same-quote f-string nesting is a syntax error on 3.9 (my gate snippet, rewritten).
  - Why it matters: the corpus now has one consistent transliteration standard enforced by a failing-loudly lint, the training set no longer teaches two styles, and style-invariant matching immediately paid for itself by surfacing 3 real witness matches.
  - Files affected: `src/abshaar/{translit,source_matching,validation,cli}.py`, `tests/test_translit.py`, all 72 `data/working/bulleh_shah_00*.md` (Transliteration sections only), `docs/16` (§4–§5 spec), `START_HERE.md` §5.3, `docs/08`, regenerated `data/processed/**` and `data/context/{source_matches,sufinama_text_source_matches,canonical_clusters,themes}.jsonl`, `data/lexicon/terms.jsonl`, `data/annotations/crosswalk_review_queue.md`.

- Continued non-model work while Ollama/BGE-M3 downloads ran, per Rauf's instruction not to run the Ollama models until he says so (2026-08-15, Claude).
  - Details: (a) Documented all 12 new pipeline commands in `START_HERE.md` §4.2 and `README.md` (AGENTS.md canonical-doc obligation). (b) Added 7 pipeline counters to `status` (clusters, KB, trainable layers, examples, probes). (c) Unit tests for the eval harness (scoring regexes, token-F1, probe builder, baseline-table replace-not-duplicate). (d) **Devanagari-aware matching**: new `src/abshaar/devanagari.py` (approximate rule-based transliteration, comparison-only, nukta upgrades handled post-NFC); matcher gains two Devanagari signals hard-capped at 0.98 so they can never hit the 1.0 auto-merge threshold; both Sufinama manifests carry the devanagari layers. Offline rebuilds: candidate-less records went from 40/48 (non-kaafi) and 3/76 (kaafi) to **0 in both**, with exact-1.0 counts unchanged (1 and 11) — the cap held. Downstream rebuild (clusters/KB/dataset/probes) byte-stable except cluster `related_candidates`. (e) `augment-training-data` CLI (LLM paraphrase of questions only, answers verbatim, verifier gate + full gate re-run) implemented and unit-tested with a stubbed chat function — NOT run live, awaiting Rauf's go-ahead on model runs. (f) Phase 5/6 scaffolding committed: `training/axolotl_qwen3_8b.yml` (Path B), `training/Modelfile.abshaar-bulleh`, `training/README.md`; `training/adapters|fused` gitignored.
  - Verification: 58/58 tests; `validate` clean; before/after candidate-coverage counts measured on the live crosswalks.
  - Why it matters: The long-standing Devanagari gap is closed at the matching layer (review still pending), and every remaining model-dependent step is one command with its gates already tested.
  - Files affected: `src/abshaar/{devanagari,source_matching,sufinama,status,augment,cli}.py`, `tests/{test_devanagari,test_evaluate,test_augment}.py`, `START_HERE.md`, `README.md`, `.gitignore`, `training/*`, `data/context/{source_matches,sufinama_text_source_matches,canonical_clusters}.jsonl`, `docs/12_sufinama_source_ingestion.md`.

- Executed Phases 2–4 infrastructure of the training plan on 2026-08-15 (Claude).
  - Details: (Phase 2) `src/abshaar/rag.py` — `build-index` embeds the KB with BGE-M3 into Chroma at gitignored `data/cache/chroma/`; `ask` retrieves top-k, answers via local Ollama under strict grounding rules (cite kb ids, preserve qualifiers, decline below score threshold 0.35), strips qwen3 `<think>` blocks, and exits non-zero on citations of non-retrieved records. Both wrappers now prefer `.venv` python. `scripts/rag_smoke_test.py` is the 12-question gate. (Phase 3) `generate-training-data` produced 1,178 chat-format examples (1,035 train / 143 eval, 9 task families) by MECHANICAL TEMPLATING from KB records — answers are corpus text with attribution notes stripped; honesty family 99 examples (false premises, fake titles, misattributions, out-of-scope, disputed-fact refusals); all four gates pass and output is deterministic. (Phase 4) `build-probes` wrote the fixed 50-probe set (25 factual from held-out clusters, 15 fresh honesty traps, 10 disputed); `run-eval` scores bare or `--rag` runs into `eval_baseline.md`. (Phase 5 prep) `export-mlx-dataset` + `scripts/train_lora.sh`. Installed Ollama 0.32.13 via Homebrew and started the server; qwen3:4b/8b pulls and the BGE-M3 index build were still downloading at the time of this entry.
  - Verification: 43/43 tests; `validate` clean; dataset determinism via md5 diff; example spot-checks across all families.
  - Why it matters: Everything up to actual baseline-eval and LoRA execution is code-complete and gate-checked; the remaining steps are compute, not design.
  - Files affected: `src/abshaar/{rag,dataset_gen,evaluate,cli}.py`, `scripts/{abshaar.sh,abshaar.ps1,rag_smoke_test.py,train_lora.sh}`, `tests/{test_rag,test_dataset_gen}.py`, `data/processed/training/{train,eval,probes}.jsonl`, `data/processed/training/mlx/`, `data/processed/training/MANIFEST.md`, plan §10 checklist.

- Built three background/offload tools for the model-dependent pipeline on 2026-08-16 (Claude), after Rauf asked (a) how resource-intensive the remaining steps are and (b) for "a smart system" that lets other work keep running, then mentioned he may also have access to Harvard Mac Studio workstations for training.
  - Details: `scripts/thermal_aware_pipeline.sh` — a resumable runner for docs/17 Phases 2-5 that runs each stage at background scheduling priority (`taskpolicy -c background` + `nice -n 15`, the same QoS mechanism macOS uses for Spotlight/Time Machine, so foreground work stays responsive) and pauses instead of piling on load when `pmset -g therm` reports the CPU already thermally throttled (verified on this machine: no thermal event has ever fired, so `pmset -g therm` currently reports no `CPU_Speed_Limit` field at all — the parser fails open, i.e. treats missing data as "not hot," rather than blocking forever on a metric that may never appear). It requires `training/RUN_AUTHORIZED` (a new, durable, gitignored, machine-local file) to exist before touching Ollama/MLX — a deliberate opt-in switch, additional to and independent of the chat-based authorization the runbook already requires, so a future/different session can't restart heavy compute based on stale chat context alone. Has a `status` subcommand (no side effects; also reports Low Power Mode state — confirmed ON on this machine, which trades speed for less heat) and a `selftest` subcommand that exercises the resume/skip/priority logic with fake commands, touching no model and no auth file.
  - Also built, once Rauf said the Harvard workstations are Mac Studios (same Apple-Silicon/mlx toolchain, just far more unified memory and real fans — no CUDA/axolotl bridging needed): `scripts/export_training_bundle.sh`, which packages ONLY `data/processed/training/mlx/{train,valid}.jsonl` (confirmed by inspection: `{"messages":[...]}` chat examples only, already leak-scanned/gated — no private KB, no witness texts, no Rafat copyrighted material, no git history) plus a self-contained `train_standalone.sh` and a `MANIFEST.md` (record counts, SHA-256s, exact run command, and an explicit recommendation to try `mlx-community/Qwen3-8B-4bit` there instead of 4B, since an 8b baseline already exists in `eval_baseline.md` and the M4's "don't start with 8B" caution was a RAM/thermal limit that doesn't apply on a Mac Studio) into `training/portable_bundle/`. `scripts/import_trained_adapter.sh` takes the returned adapter directory, validates it contains a `.safetensors` file, copies it into `training/adapters/`, and prints its SHA-256 for the OFFLOADING/EVAL_MATRIX record the runbook already asks for.
  - Verification: `thermal_aware_pipeline.sh selftest` passes (thermal check reads 0/not-hot, priority wrapper runs, resume-skip logic correct); `status` correctly reports `Authorized: NO` before any `RUN_AUTHORIZED` file exists; `export_training_bundle.sh` run live — produced a 1,181-line dataset bundle (1038 train + 143 valid, matching the source exactly) with a syntactically valid standalone script; `import_trained_adapter.sh` tested against a missing-arg case, an empty-directory case, and a real fake-adapter case (all three behaved correctly; test artifacts removed). All three scripts are `chmod +x`; none has a `.ps1` twin (macOS-only by nature: `pmset`/`taskpolicy`/mlx-lm don't exist on Windows — same precedent as the pre-existing `train_lora.sh`). 83/83 tests still pass; `validate` clean (these are shell scripts outside the Python package).
  - Why it matters: turns a one-off verbal "wait for a cool day" into two durable, inspectable mechanisms — an automatic thermal/priority guard for running locally, and a rights-safe export path for running on better hardware entirely — instead of relying on Rauf remembering to ask again each session.
  - Files affected: `scripts/{thermal_aware_pipeline,export_training_bundle,import_trained_adapter}.sh` (new), `training/README.md`, `docs/17_training_runbook.md` §5, `.gitignore` (added `training/{portable_bundle,pipeline_logs,RUN_AUTHORIZED}`).

- Classified the entire 124-record Sufinama crosswalk (AI first pass) on 2026-08-16 (Claude), while model runs stayed blocked on Rauf's thermal constraint.
  - Details: New `src/abshaar/crosswalk_review.py` + two CLI commands. `crosswalk-evidence` computes deterministic TWO-WAY LINE COVERAGE (share of each side's lines with a counterpart at similarity ≥0.80 strong / ≥0.60 loose / 0.55 on the approximate Devanagari channel) for every match record and candidate, plus per-line alignments, into `data/annotations/crosswalk_evidence.md` — built because the matcher's score is a max over line pairs, so one shared refrain scores 0.6–0.9 between different poems. Claude then read the alignments for all 77 records with nonzero coverage and authored `data/annotations/crosswalk_classifications.jsonl` (one decision per record: status, poem_id, evidence note, `human_confirmed: false`); the 47 zero-coverage records defaulted to `unmatched` with a mechanical note after an eyeball pass over their first lines. `apply-crosswalk-review` validates the whole file (taxonomy, completeness, poem_id must be a stored candidate, unmatched must carry none) BEFORE writing anything, then rewrites both match files idempotently, setting `match_status` + a `match_review` provenance block.
  - Results: 1 exact_witness, 30 variant, 10 excerpt, 1 possible, 82 unmatched. Notable textual findings (all in the notes): kaafi-44 is a composite page (a distinct "Main kyun kar jawan Kaabe nun" kafi + ALL of 0059); the athvara witness contains 0068+0069 as day-sections and the barahmasa contains 0070+0071 as month-sections; kaafi-62 reads maTi where 0046 reads mai throughout; kaafi-50's closing couplet belongs to 0017 not 0032 (stanza recombination); the 0006 doha witnesses give a jurriyan/churiyan reading lead; five works appear under two Sufinama categories (holi=kaafi, kalaam-1=kaafi, shabad-4=kaafi-20, two doha/dohra pairs); many score-1.0 auto-merged records are NOT full exact witnesses but fuller/shorter recensions — the merge stays textually justified, but only kaafi-12→0001 is a true line-for-line exact witness.
  - Verification: apply run twice → byte-identical files (124 records changed exactly once); `build-clusters` rerun → md5-identical `canonical_clusters.jsonl` (nothing consumes `match_status`); `validate` clean; 83/83 tests (16 new in `tests/test_crosswalk_review.py`: coverage math, proposal rules, apply validation failure modes, idempotency, no-partial-write).
  - Why it matters: the top standing "Urgent" item (crosswalk review) moved from unstarted to human-confirmation-only, with the judgment layer stored as an editable, re-appliable file rather than chat text.
  - Files affected: `src/abshaar/{crosswalk_review,cli}.py`, `tests/test_crosswalk_review.py`, `data/annotations/{crosswalk_evidence.md,crosswalk_classifications.jsonl,crosswalk_review_queue.md}`, `data/context/{source_matches,sufinama_text_source_matches}.jsonl`, `scripts/build_review_queue.py` (status column), `docs/12_sufinama_source_ingestion.md`, `docs/17_training_runbook.md` §8.4, `START_HERE.md`, `README.md`.

- Audited live state and wrote the expert-model implementation plan on 2026-08-15 (Claude).
  - Details: Verified corpus/validation/test state live (figures in §1). Discovered that all 34 remaining placeholder warnings are false positives of the blanket `\[[^\]]+\]` regex — the flagged brackets are uncertainty annotations, supplied words, and cross-references, not unfinished slots. Confirmed hardware: Apple M4, 16 GB RAM (local MLX LoRA on a 4B model feasible). Confirmed `.git/index.lock` no longer exists. Wrote `docs/15_bulleh_shah_expert_model_implementation_plan.md`: 6 phases (safety rails/schema fixes → knowledge-base consolidation → RAG index → synthetic training-data factory with rights firewall and honesty examples → eval baseline → LoRA training and serving), each with executor prompts for cheaper models, mechanical exit-nonzero gates, and a list of Rauf's few required actions.
  - Verification: `./scripts/abshaar.sh status` and `validate` (0 errors / 34 warnings), 19/19 unit tests, bracket-content scan of all 17 flagged entries, `sysctl hw.memsize`, `git status`/`git log`.
  - Why it matters: The project now has a concrete, delegable path from the drafted corpus to a trained-and-evaluated private expert model, with rights protection encoded as failing checks rather than intentions.
  - Files affected: `docs/15_bulleh_shah_expert_model_implementation_plan.md` (new), `OFFLOADING.md`, `Bulleh Shah/CORPUS_BUILD_LOG.md`.

## 3. Current State

| Item | Current Status | Notes |
|---|---|---|
| Repository path | Verified | `/Users/rauf/Desktop/Desktop - rauf’s MacBook Air/Harvard/Abshaar` |
| Current OS/shell | Verified | macOS with zsh; use `./scripts/*.sh`. Keep matching PowerShell instructions for Windows. |
| Git branch | Verified 2026-08-15 | `draft`, tracking `origin/draft`; HEAD `2651e33`, **4 commits ahead of origin (unpushed)**. |
| Git remote | Verified | `https://github.com/RaufNawaz/Abshaar.git`; Rauf confirmed the repository is private. |
| Working tree | Clean at HEAD | Verified clean on 2026-08-15 before the plan/handoff edits of that date. Still shared with Codex — inspect `git status` before editing. |
| Git lock | Resolved | `.git/index.lock` no longer exists (verified 2026-08-15). |
| Python package | Working | `abshaar` 0.1.0, Python >=3.11, standard-library core. |
| CLI | Working | Twelve commands, including `acquire-sufinama`, `match-source-manifest`, and `extract-gurmukhi-pdf`. |
| Working corpus | 72 draft files | 0001 Sufinama pilot; 0002-0072 all 71 Rafat poems. |
| Processed corpus | 72 JSONL records | `data/processed/poems.jsonl`, approximately 493 KB; generated with placeholders included. |
| Public poems | 0 | All source notes say publication=no; review statuses remain draft. |
| Training state | Private research | Existing Markdown source notes still say training=no; Rauf states the Sufinama collaboration authorizes private academic acquisition/training. Reconcile field values after the witness dataset is verified. |
| Sources | 7 | Added the Western Sydney thesis, Sufinama profile, and Government of Punjab Auqaf shrine profile to the prior four source records. |
| Sufinama catalog | 76 paired items | `data/context/sufinama_source_items.jsonl` has 76 unique UUIDs and Roman URLs. |
| Sufinama witness texts | Complete and audited | 76 normalized records; 152 cached snapshots; 145 requested views ok, 7 source-unavailable, 0 errors. |
| Source matches | 76 records, AI-classified 2026-08-16 | Every record carries `match_status` + `match_review` (`human_confirmed: false`): 1 exact_witness, 22 variant, 5 excerpt, 1 possible, 47 unmatched. Evidence: `data/annotations/crosswalk_evidence.md`; decisions: `crosswalk_classifications.jsonl`. |
| Sufinama non-kaafi catalog | Complete | 48 unique category records in `data/context/sufinama_text_source_items.jsonl`: 3 kalaam, 23 dohas, 7 shabads, 12 dohras, athvara, barahmasa, and holi. |
| Sufinama non-kaafi witnesses | Complete and audited | 48 normalized records; 0 errors; 41 source-unavailable requested views; 7 plain Roman, 7 diacritic Roman, 8 Urdu, 47 Devanagari; all 48 have mapping IDs. |
| Sufinama non-kaafi matches | 48 records, AI-classified 2026-08-16 | 8 variant, 5 excerpt, 35 unmatched (`human_confirmed: false` on all). The athvara/barahmasa witnesses contain entries 0068+0069 / 0070+0071 as sections; several works repeat across Sufinama categories. |
| PunjabLibrary Gurmukhi catalog | Complete, review required | 160 numbered records with page spans in `data/context/punjab_library_source_items.jsonl`. |
| PunjabLibrary Gurmukhi witness | Private, extracted, unverified | 160 full-text records in ignored `data/processed/private/punjab_library_bulleh_shah_kafian.jsonl`; embedded text is defective and PDF page images are authoritative. |
| People | 1 sourced draft | Bulleh Shah record now foregrounds disputed dates/birthplace and later-source limitations. |
| Biographical claims | 11 sourced drafts | Claim-level evidence status, confidence, caution, and source IDs are in `data/context/biographical_claims.jsonl`. |
| Timeline events | 6 sourced drafts | Cautious life/historical events; exact dates remain unknown for education and discipleship. |
| Sufinama content inventory | 13 categories | Includes profile, kaafi, kalaam, doha, shabad, dohra, athvara, barahmasa, holi, quotes, e-book, video, and blog. |
| Glossary/themes/reviews/model outputs | 0 extracted | Key Terms and Themes now exist INSIDE all 72 entries but have not been extracted to `data/lexicon/`/`data/context/themes.jsonl` (plan Phase 1.1). Reviews/model outputs remain 0. |
| Interpretive layers | Complete as AI drafts | All 72 entries have Literary Translation, Tashreeh, Key Terms, Themes (Claude-drafted, `review_status: draft`). 0001 has a genuine AI-drafted `# Literal Gloss` (Claude, not Rafat) and still has NO `# AI Translation` section. Rafat reference translations in 0002–0072 are copyrighted; serialization fixed by plan Phase 0.2 (`reference_translation`, `trainable: false`). |
| Original-text confidence | Needs human review | Shahmukhi was visually read from calligraphic pages. Many entries explicitly flag high-uncertainty readings. |
| Validation | Clean | 0 errors / 0 warnings since plan Phase 0.1 fixed the bracket regex (2026-08-15); verified again 2026-08-16 after the crosswalk classification apply. |
| Hardware | Verified 2026-08-15 | Apple M4, 16 GB RAM. Local MLX LoRA on Qwen3-4B feasible; 8B-4bit marginal. |
| Implementation plan | Written 2026-08-15 | `docs/15_bulleh_shah_expert_model_implementation_plan.md` — authoritative next-steps document; §10 checklist tracks phase progress. |
| Tests | Passing | 83 tests (verified 2026-08-16): the original ingestion/build/matching coverage plus translit, devanagari, eval-harness, augmentation, RAG/dataset gates, and the new crosswalk-review module (coverage math, proposal rules, apply validation/idempotency/no-partial-write). |
| Full-build wrappers | Fixed and verified | Both include placeholders; live macOS build preserved 72 working and processed records. |
| Site data | Generated/ignored | `export-site` was rerun after research and exports 1 person, 6 events, 7 sources, and 0 public poems; directory is Git-ignored. |
| Website | Not implemented | Architecture is planned; there is no `website/` application yet. |
| Local AI environment | Fully prepped | `ai-check` (2026-08-16): Ollama 0.32.13, API available, `qwen3:4b` + `qwen3:8b` both pulled, all 5 optional Python packages installed (`ollama`, `sentence_transformers`, `chromadb`, `transformers`, `torch`), plus mlx-lm 0.29.1 import-verified. Only the Chroma index build (`build-index`, real embedding compute) remains — deliberately deferred to the cool-environment session. |
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
- ~~The current matcher cannot compare Devanagari-only non-kaafi witnesses~~ — resolved 2026-08-15 with an approximate comparison-only Devanagari→Roman transliteration (score-capped at 0.98); 0 records now lack candidates, all still `needs_review`.
- No formal five-poem editorial slice, transliteration standard, or instantiated review workflow has been selected.

### Current Open Questions

Resolved since these were last written (kept here only long enough to show
they are closed, then should be deleted on the next full OFFLOADING pass):
- ~~Which Sufinama witnesses are exact/variant/excerpt/possible/unmatched~~ —
  answered by the AI first pass (2026-08-16), pending Rauf's confirmation
  (see §7 Urgent).
- ~~What `canonical_work_id` scheme...~~ — implemented in
  `src/abshaar/clusters.py` (union-find over exact matches;
  `cluster_confidence: auto_exact_match` vs `unreviewed`).
- ~~Should the schema add an explicit `reference_translation` kind...~~ —
  done in plan Phase 0.2 (2026-08-15): Rafat text serializes as
  `reference_translation` (`rights: copyrighted`, `trainable: false`); 0001
  keeps a genuine `literal_gloss`.
- ~~How should `project-latin-v1` represent...~~ — decided and implemented
  2026-08-15 (`docs/16` §5, `src/abshaar/translit.py`).

Still open:

- What written Sufinama collaboration/authorization reference should be stored with the source record? Needs verification.
- What reviewed Devanagari-to-project-latin/Shahmukhi method should support matching without inventing source text? (Current `devanagari.py` transliteration is rule-based/approximate and explicitly capped at 0.98 for this reason — see standing findings. A more accurate method is still open.)
- Which five poem IDs should form the first fully reviewed vertical slice? (A recommended set exists in §7 but is not a recorded decision.)
- Which source edition should be used to verify Shahmukhi and variants?
- Who will act as language/source reviewer beyond Rauf, and what evidence is required before `publishable`?
- The ʿain/Arabic-loan mark upgrade (docs/16 §5) requires reading each Urdu original word-by-word against its transliteration — a bilingual scholarly judgment call, not something to automate or infer.

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
- Model runs happen only in a cool environment (thermal concern, 2026-08-16); until Rauf says go, sessions do non-model work. Network-only prep (model pulls, pip installs) is acceptable.
- Keep `origin/draft` on GitHub up to date after commits (Rauf, 2026-08-16) so he can work from other devices; the repository stays private.

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
- Validation now shows 0 errors / 34 warnings, and **all 34 are false positives**: the placeholder regex flags any `[bracketed text]`, but the flagged brackets in 17 entries are uncertainty annotations, supplied words, and `[[cross-references]]` — the corpus's honesty conventions. Never edit entries to silence these; fix the check (plan Phase 0.1).
- All 72 entries now carry AI-drafted interpretive layers (`review_status: draft`). The project still has no formal review records, extracted glossary, Q&A dataset, website, or RAG system. AI-draft completion does not equal human-reviewed corpus completion; the plan accepts this trade explicitly.
- Rauf's directive (2026-08-15): reach training-readiness within days with his own work minimized or eliminated, executable by cheaper models. `docs/15_bulleh_shah_expert_model_implementation_plan.md` is the response: RAG + LoRA on synthetic grounded data with mechanical gates instead of human review gates. The five-poem reviewed vertical slice remains the right eventual quality investment but is no longer the immediate path.
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

**As of 2026-08-15, the authoritative next-steps document is
`docs/15_bulleh_shah_expert_model_implementation_plan.md`** (6 phases:
safety rails/schema fixes → knowledge base → RAG → training-data factory →
eval baseline → LoRA training/serving, with per-phase executor prompts and
gates). Start with its Phase 0. The checklist below is retained because its
items remain valid quality work; several are absorbed by plan phases
(translation schema → Phase 0.2; clustering → Phase 1.2 in conservative
automated form; crosswalk review and the five-poem human gold slice are
deferred, with the risk accepted in the plan §9).

### Urgent

- [x] ~~Review `data/context/source_matches.jsonl` and classify exact witness, variant, excerpt/full, possible, and unmatched relations~~ — AI first pass complete 2026-08-16 (all 76 classified with line-coverage evidence; no auto-merge changes). **Remaining: Rauf confirms/edits `data/annotations/crosswalk_classifications.jsonl` and re-runs `apply-crosswalk-review`; the `possible` record (kaafi-7 vs 0007) and the composite kaafi-44 page need human eyes first.**
- [x] ~~Review `data/context/sufinama_text_source_matches.jsonl`~~ — AI first pass complete 2026-08-16 (all 48 classified; kalaam → `bulleh_shah_0025` confirmed variant/near-exact; category overlaps documented). **Remaining: human confirmation, same file/workflow as above.**
- [x] ~~Add a `canonical_work_id`/work-cluster layer~~ — done (`src/abshaar/clusters.py`, union-find over exact matches; 340 clusters / 356 members as of the 2026-08-16 rebuild).
- [x] ~~Add a Devanagari matching/transliteration layer~~ — done 2026-08-15 (comparison-only, capped at 0.98, 0 candidate-less records remain); the *review* of those candidates is still open.
- [ ] Decide which training path to use next: local M4 (`scripts/thermal_aware_pipeline.sh`, background-friendly, thermally paced) vs. a Harvard Mac Studio (`scripts/export_training_bundle.sh` / `import_trained_adapter.sh`, Path C in `training/README.md`) — both built 2026-08-16, neither yet run. If going the Mac Studio route, also decide whether to train Qwen3-8B there instead of 4B (an 8b baseline already exists; see the bundle's MANIFEST for the reasoning).
- [ ] Human-check the 160 PunjabLibrary headings against rendered pages, starting with the five-poem review slice, and record cross-script witness relationships without assuming source-order identity.
- [x] ~~Verify whether any active Git process owns `.git/index.lock`~~ — resolved; the lock no longer exists (verified 2026-08-15).
- [x] ~~Push the waiting commits on `draft` to `origin/draft`~~ — pushed; verified in sync 2026-08-16. **Standing instruction (Rauf, 2026-08-16): keep the GitHub repo up to date after committing so he can work from other devices. The repo must stay PRIVATE — the tree contains Rafat's copyrighted reference translations and Sufinama witness texts; never change visibility to public.**
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
> Current state (verified 2026-08-15): clean tree on `draft`, 4 unpushed commits; 72 draft Bulleh Shah entries with COMPLETE AI-drafted interpretive layers (literary translation, tashreeh, key terms, themes — all `review_status: draft`); 76 normalized Sufinama kaafi witnesses, 48 non-kaafi witnesses, 160 ignored/private PunjabLibrary Gurmukhi witnesses; 7 sources, 11 biographical claims, 6 timeline events, 13-category Sufinama inventory. Validation: 0 errors, 34 warnings that are ALL false positives of the bracket regex (uncertainty annotations, not placeholders — fix the check, never the entries). 19 tests pass. Hardware: Apple M4, 16 GB RAM.
>
> Important files: `docs/15_bulleh_shah_expert_model_implementation_plan.md` (the authoritative plan), `START_HERE.md`, `OFFLOADING.md`, `Bulleh Shah/CORPUS_BUILD_LOG.md`, `docs/12`–`14`, `data/context/*.jsonl` catalogs/matches/claims, `src/abshaar/`, and the 72 working entries.
>
> Immediate work: follow **`docs/17_training_runbook.md`** step by step — it is the complete, self-contained guide for the remaining model-dependent work (preconditions checklist, smoke test, baselines, optional augmentation, LoRA training, fuse/serve, acceptance criteria, troubleshooting for this machine's known failure modes). **Do NOT run any Ollama model (ask/run-eval/augment/smoke test/training) until Rauf explicitly authorizes it in your session — this is a standing instruction from 2026-08-15; the runbook's §0 explains what counts as authorization.** Never start a step while the previous step's gate fails, and never weaken a gate.
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
| Devanagari matching is approximate | The 2026-08-15 transliteration layer is rule-based (no schwa deletion), so its similarity scores are indicative, not proof; it is capped at 0.98 to keep it out of auto-merge. | Human-review Devanagari-signal candidates before assigning any canonical-work relationship; never store transliterated output as witness text. |
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
| The project venv is Python 3.9 while `pyproject.toml` requires >=3.11 | Two 3.9-only breakages already occurred (`write_text(newline=)`, same-quote f-strings); `mlx-lm` may require >=3.10. | If the mlx-lm install fails for version reasons, install a newer Python (e.g. `brew install python@3.12`), recreate `.venv`, and reinstall requirements (multi-GB). |
| Website and RAG are not implemented | Roadmap language may imply more product functionality than exists. | Treat them as later milestones after reviewed, rights-safe poems exist. |

## 10. Compact Version

Abshaar is a private, local-first archive and AI-assisted interpretation project shared by Codex and Claude, whose goal is a source-grounded Bulleh Shah expert model. The live tree (verified 2026-08-15: clean, 4 unpushed commits on `draft`) contains 72 poem entries with complete AI-drafted interpretive layers, 76 + 48 normalized Sufinama witnesses, 160 private PunjabLibrary Gurmukhi witnesses, 7 sources, 11 claim-level biography records, 6 timeline events, and a 13-category inventory. Validation: 0 errors, 34 warnings that are all bracket-regex false positives (uncertainty annotations — fix the check, not the entries); 19 tests pass. The authoritative next-steps document is `docs/15_bulleh_shah_expert_model_implementation_plan.md`: a 6-phase, cheap-model-executable pipeline (schema/rights fixes → knowledge base → RAG → synthetic training data with a Rafat leak scanner and honesty examples → eval baseline → local MLX LoRA on Qwen3-4B, M4/16 GB verified) whose gates are commands that exit non-zero. Rafat's English is copyrighted and must never enter training data; Sufinama/PunjabLibrary material stays private. Never overwrite source variants; update affected docs and `OFFLOADING.md` after substantive work.
