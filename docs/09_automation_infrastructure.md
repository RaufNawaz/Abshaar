# Automation Infrastructure

This repository now includes a small Python automation layer for the project. It
is designed to work before the heavy AI dependencies are installed.

The automation currently handles:

- creating project directories;
- reporting project status;
- creating a new human-friendly Markdown poem entry;
- choosing the next Bulleh Shah poem ID automatically;
- converting Markdown entries into `data/processed/poems.jsonl`;
- validating Markdown and JSONL data;
- exporting website-ready JSON into `data/site/`;
- preparing prompt packs for the local model pipeline;
- checking whether local Ollama is available;
- optionally drafting an interpretation through Ollama.
- discovering, acquiring, aligning, and cross-matching the authorized Sufinama
  Bulleh Shah kaafi source collection.

Current corpus note (verified 2026-07-12): the repository contains 72 unfinished
working entries that are intentionally built with `--include-placeholders`.
Both full-build wrappers now preserve that flag.

## Quick Start

> Commands on this page are shown in PowerShell (Windows). On macOS/Linux, use
> `./scripts/abshaar.sh` and `./scripts/build_all.sh` instead of the `.ps1`
> versions — same arguments, same behavior. See
> [Local Setup Guide](05_local_setup.md) for the macOS install steps.

From PowerShell:

```powershell
cd "D:\Harvard\Poetry Model Project"
.\scripts\abshaar.ps1 validate
```

The PowerShell wrapper sets `PYTHONPATH` for you, so you do not need to install
the package first.

If PowerShell blocks local scripts, run:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\abshaar.ps1 validate
```

On macOS/Linux:

```bash
cd ~/Harvard/"Poetry Model Project"
./scripts/abshaar.sh validate
```

Alternatively, install the package in editable mode:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e .
abshaar validate
```

## Command Reference

### Initialize Directories

```powershell
.\scripts\abshaar.ps1 init
```

Creates expected folders such as `data/working`, `data/processed`,
`data/context`, `data/cache`, `data/site`, `scripts`, and `tests`.

### Create a New Poem Entry

```powershell
.\scripts\abshaar.ps1 new-entry --title "First line here"
```

This creates:

```text
data/working/bulleh_shah_0001.md
```

The ID is chosen automatically. You can still pass `--id` manually if needed.

Then you fill in original script, script notes, transliteration, literal gloss,
literary translation, tashreeh, key terms, themes, source notes, and review
notes.

### Show Project Status

```powershell
.\scripts\abshaar.ps1 status
```

Shows counts for working entries, processed poems, public poems, glossary terms,
sources, timeline events, reviews, model outputs, and validation issues.

### Build Structured Data

```powershell
.\scripts\abshaar.ps1 build-data
```

This reads all poem entries in `data/working/` and writes:

```text
data/processed/poems.jsonl
```

By default, entries with placeholder text are skipped. To include them anyway:

```powershell
.\scripts\abshaar.ps1 build-data --include-placeholders
```

### Validate the Project

```powershell
.\scripts\abshaar.ps1 validate
```

Validation checks:

- invalid JSONL;
- duplicate IDs;
- missing required poem fields;
- empty original text;
- empty transliteration;
- missing literal or literary translation;
- placeholder text that still needs to be replaced;
- unsafe website publication settings.

Warnings do not fail the command. Errors do.

### Export Website Data

```powershell
.\scripts\abshaar.ps1 export-site
```

This writes generated JSON to:

```text
data/site/
```

The generated files include `poems.json`, `glossary.json`, `people.json`,
`events.json`, `themes.json`, `sources.json`, and `search_documents.json`.

Only poems marked with `"publication": {"include_on_website": true}` are exported
as public poems.

### Build a Prompt Pack

```powershell
.\scripts\abshaar.ps1 prompt-pack --poem-id bulleh_shah_0001
```

This writes:

```text
data/cache/prompt_packs/bulleh_shah_0001.json
```

The prompt pack includes the system prompt, poem text, transliteration, existing
gloss and translation, existing tashreeh, retrieved glossary context, retrieved
theme context, and poet context when available.

To build prompt packs for every processed poem:

```powershell
.\scripts\abshaar.ps1 prompt-pack --all
```

### Check Local AI Setup

```powershell
.\scripts\abshaar.ps1 ai-check
```

This checks whether the Ollama CLI is installed, whether the local Ollama API is
running, which local models are available, and whether optional AI Python
packages such as `transformers`, `torch`, `sentence-transformers`, `chromadb`,
and `ollama` are installed.

### Draft With Ollama

```powershell
.\scripts\abshaar.ps1 draft --poem-id bulleh_shah_0001 --model qwen3:8b
```

This sends the prompt pack to local Ollama and appends the raw model output to:

```text
data/annotations/model_outputs.jsonl
```

The output is marked `needs_review`. It is not automatically publishable.

### Acquire the Sufinama Bulleh Shah Collection

Discover and pair the 76 Roman/Urdu catalog items without fetching poem pages:

```powershell
.\scripts\abshaar.ps1 acquire-sufinama --discover-only
```

Run the authorized full acquisition on macOS/Linux with curl transport:

```bash
./scripts/abshaar.sh acquire-sufinama --transport curl
```

The collector pairs by stable Sufinama UUID, caches raw pages under
`data/raw/private/sufinama/`, preserves Urdu plus two Roman layers and source
alignment IDs, writes normalized private witnesses, generates reviewable source
matches, and never modifies the 72 canonical Markdown entries.

Rebuild normalized records and matching outputs from the completed local cache
without making network requests:

```bash
./scripts/abshaar.sh acquire-sufinama --offline --transport curl
```

Useful flags: `--offline`, `--limit`, `--refresh`, `--workers`, `--delay`,
`--transport`, and `--cache-dir`. See
`docs/12_sufinama_source_ingestion.md` for the full workflow.

### Match Another Offline Source Manifest

```powershell
.\scripts\abshaar.ps1 match-source-manifest --manifest data\path\source.jsonl
```

This uses title and all-line Urdu/Roman similarity to produce candidate links.
Every link remains `needs_review`; source witnesses are not merged into canonical
poems automatically.

### Extract a Numbered Gurmukhi PDF Witness

```powershell
.\scripts\abshaar.ps1 extract-gurmukhi-pdf --input "Bulleh Shah\Kafian - Baba Bulleh Shah (Baba Bulle Shah) (z-library.sk, 1lib.sk, z-lib.sk).pdf"
```

This command uses the PDF's embedded text layer to segment consecutively
numbered works. It writes a private full-text witness, a reviewable item catalog,
and an audit record with the source hash, page count, dependency/parser versions,
and ordinal checks. It fails on missing or duplicate ordinals. The current
PunjabLibrary extraction is always marked `needs_visual_review` because rendered
pages are reliable while the embedded Gurmukhi text layer is not.

Install the optional dependency with `python3 -m pip install -e '.[pdf]'`. See
`docs/13_gurmukhi_pdf_ingestion.md` for source, rights, and review details.

## Automation Flow

```text
Markdown entry
  -> build-data
  -> poems.jsonl
  -> validate
  -> prompt-pack
  -> optional Ollama draft
  -> human review
  -> export-site
  -> website
```

## Run the Whole Local Automation Build

Both wrappers invoke `build-data --include-placeholders`, preserving all current
unfinished entries in `data/processed/poems.jsonl`.

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\build_all.ps1
```

This runs:

1. `init`
2. `validate`
3. `build-data --include-placeholders`
4. `validate`
5. `export-site`

Use this before committing a batch of data edits.

## GitHub Actions

The repository includes `.github/workflows/validate.yml`. On GitHub, it will:

1. install the package;
2. run unit tests;
3. run `abshaar validate`.

This gives future contributors a basic safety net before their changes are
merged.

## What Is Intentionally Not Automated Yet

The project does not yet automate source discovery, copyright judgment,
transliteration correctness, final translation approval, publishing model drafts
directly to the website, or fine-tuning. Those should remain human-reviewed until
the corpus and review system are mature.

## Source Code Map

```text
src/abshaar/cli.py             command-line interface
src/abshaar/markdown_entry.py  Markdown entry parser
src/abshaar/jsonl.py           JSONL read/write helpers
src/abshaar/validation.py      project validation checks
src/abshaar/export.py          website data export
src/abshaar/prompts.py         prompt-pack builder
src/abshaar/ollama_client.py   optional local Ollama integration
src/abshaar/gurmukhi_pdf.py    numbered Gurmukhi PDF witness extraction
src/abshaar/sufinama.py        authorized Sufinama acquisition and audit
src/abshaar/source_matching.py non-destructive witness candidate matching
```

## Testing

Run:

```powershell
$env:PYTHONPATH = "src"
py -m unittest discover -s tests
```

The first test checks that a Markdown poem entry can be converted into a poem
record while preserving non-Latin script text.
