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

## Quick Start

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

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\build_all.ps1
```

This runs:

1. `init`
2. `validate`
3. `build-data`
4. `validate`
5. `export-site`

It is the command to use before committing a batch of data edits.

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
```

## Testing

Run:

```powershell
$env:PYTHONPATH = "src"
py -m unittest discover -s tests
```

The first test checks that a Markdown poem entry can be converted into a poem
record while preserving non-Latin script text.
