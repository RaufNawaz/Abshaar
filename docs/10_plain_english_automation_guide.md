# Plain-English Automation Guide

This file explains what the project currently automates, how it works, and what
can be automated next. It assumes no computer science background.

## The Big Picture

Think of Abshaar as an assembly line for poetry.

The human should focus on the things humans are best at:

- choosing trustworthy sources;
- deciding whether a text is legally safe to publish;
- correcting transliteration;
- judging poetic meaning;
- approving translations;
- writing or checking tashreeh.

The computer should handle repetitive tasks:

- creating new poem files;
- turning typed entries into structured data;
- checking for missing fields;
- preparing model prompts;
- exporting website data;
- running basic tests before changes are accepted.

The goal is not to remove the human. The goal is to make the human spend less
time on formatting, file management, and repetitive checking.

## Current Automation Level

The project now has a command-line helper called `abshaar`. On Windows, you run
it through PowerShell using:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\abshaar.ps1 status
```

If the command looks scary, read it like this:

- `powershell`: use Windows PowerShell;
- `-ExecutionPolicy Bypass`: allow this local project script to run once;
- `-File .\scripts\abshaar.ps1`: run the Abshaar helper script;
- `status`: ask it for the project status.

On macOS/Linux, the same helper is a shell script, so it's simpler:

```bash
./scripts/abshaar.sh status
```

Every command later in this guide that starts with
`powershell -ExecutionPolicy Bypass -File .\scripts\abshaar.ps1` has the same
macOS/Linux equivalent: drop that prefix and run `./scripts/abshaar.sh` with
the same words that follow it.

## Current Commands

### `status`

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\abshaar.ps1 status
```

Shows a plain summary:

- how many working poem files exist;
- how many structured poem records exist;
- how many poems are marked public;
- how many glossary terms, sources, people, events, themes, reviews, and model
  outputs exist;
- how many validation errors or warnings exist.

Use this when you want to know where the project stands.

### `new-entry`

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\abshaar.ps1 new-entry --title "First line here"
```

Creates a new Markdown file in:

```text
data/working/
```

You no longer have to manually choose the next ID. If the last entry is
`bulleh_shah_0003`, the tool will create `bulleh_shah_0004`.

You can still provide an ID manually:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\abshaar.ps1 new-entry --id bulleh_shah_0020 --title "First line here"
```

### `build-data`

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\abshaar.ps1 build-data
```

Turns the human-friendly Markdown files into machine-friendly JSONL:

```text
data/working/*.md
  -> data/processed/poems.jsonl
```

This is important because humans should edit Markdown, while models and websites
should read JSONL.

### `validate`

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\abshaar.ps1 validate
```

Checks the project for common problems:

- missing original text;
- missing transliteration;
- missing translation;
- placeholder text still left in a file;
- unsafe publication settings;
- broken JSONL;
- duplicate IDs.

This is like a spell-checker for the structure of the archive. It cannot tell
whether a translation is spiritually or poetically correct, but it can catch many
formatting and safety mistakes.

### `export-site`

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\abshaar.ps1 export-site
```

Creates website-ready JSON files in:

```text
data/site/
```

Only poems marked as safe and publishable are exported publicly.

### `prompt-pack`

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\abshaar.ps1 prompt-pack --poem-id bulleh_shah_0001
```

Creates a prompt package for one poem. A prompt package is the bundle of
information that will be sent to the AI model:

- original poem;
- transliteration;
- existing literal gloss;
- existing translation;
- existing tashreeh;
- glossary context;
- theme context;
- poet context.

You can also build prompt packs for every processed poem:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\abshaar.ps1 prompt-pack --all
```

### `ai-check`

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\abshaar.ps1 ai-check
```

Checks whether the local AI setup is ready:

- is Ollama installed?
- is Ollama running?
- are any local models installed?
- are optional Python AI packages installed?

This does not generate translations. It only checks readiness.

### `draft`

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\abshaar.ps1 draft --poem-id bulleh_shah_0001 --model qwen3:8b
```

Sends one poem prompt to the local AI model through Ollama and saves the raw model
output in:

```text
data/annotations/model_outputs.jsonl
```

The model output is marked `needs_review`. It is not automatically published.

### `extract-gurmukhi-pdf`

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\abshaar.ps1 extract-gurmukhi-pdf --input "Bulleh Shah\Kafian - Baba Bulleh Shah (Baba Bulle Shah) (z-library.sk, 1lib.sk, z-lib.sk).pdf"
```

Collects every consecutively numbered work in a local Gurmukhi PDF as a separate
source witness. It records titles, page spans, source checksums, and extraction
warnings. It does not change the 72 poem files. For the current PunjabLibrary
PDF, the full text stays private and every record needs visual review because the
page image is clear but the PDF's hidden text layer sometimes corrupts letters.

This command needs the optional PDF package: `python3 -m pip install -e '.[pdf]'`.

### `build_all`

The wrappers now include unfinished entries automatically, so the 72-entry
processed draft corpus is preserved.

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\build_all.ps1
```

Runs the main non-AI automation steps:

1. create missing folders;
2. validate current data;
3. build JSONL data from Markdown;
4. validate again;
5. export website data;
6. show project status.

Use this before committing or uploading changes.

## How the Current Workflow Works

The current workflow is:

```text
You type a poem in Markdown
  -> automation converts it to JSONL
  -> automation validates it
  -> automation prepares model prompt packs
  -> optional local AI creates a draft
  -> human reviews the draft
  -> automation exports public website data
```

The most important design choice is this:

```text
Humans edit Markdown.
Computers read JSONL.
```

That keeps the project easier for non-technical contributors.

## What Still Requires a Human

These parts should still require a human for now:

- deciding whether a source is legally safe;
- selecting which edition or source text to trust;
- checking original-script accuracy;
- checking transliteration;
- checking whether a metaphor is interpreted correctly;
- approving the final translation;
- approving the final tashreeh;
- deciding whether a model output is publishable.

For this project, full automation would be risky if it makes the archive sound
confident but wrong.

## Best Next Automation Opportunities

These are the best next steps, ordered from safest to riskiest.

## 1. Source Intake Assistant

Current problem:

You will eventually have many sources, and manually typing source metadata will
be repetitive.

Automation idea:

Create a command:

```powershell
abshaar add-source
```

It would ask simple questions:

- source title;
- author/editor;
- year;
- URL;
- rights status;
- allowed uses;
- notes.

Then it would append a clean record to:

```text
data/context/sources.jsonl
```

Human still needed:

The tool should not decide copyright status by itself. It should only help record
your decision.

## 2. Glossary Term Assistant

Current problem:

Terms like `ishq`, `murshid`, `haq`, `nafs`, and `fana` will appear repeatedly.

Automation idea:

Create a command that scans poem entries and suggests glossary terms:

```powershell
abshaar suggest-terms --poem-id bulleh_shah_0001
```

It could detect repeated known terms and ask whether to add them to the poem.

Human still needed:

A person should write or approve the poet-specific meaning.

## 3. Auto Prompt Packs for Changed Poems

Current problem:

Right now you manually run `prompt-pack`.

Automation idea:

When a poem changes, the system could automatically rebuild only that poem's
prompt pack.

Possible command:

```powershell
abshaar refresh
```

It would run:

- build data;
- validate;
- rebuild changed prompt packs;
- export website data.

Human still needed:

Only to review generated model output.

## 4. Transliteration Draft Assistant

Current problem:

Typing transliteration is slow.

Automation idea:

Use script-specific transliteration libraries where reliable:

- Gurmukhi to Latin;
- Devanagari to Latin;
- Urdu/Shahmukhi to rough Latin.

The command might be:

```powershell
abshaar draft-transliteration --poem-id bulleh_shah_0001
```

Human still needed:

Transliteration must be reviewed. Shahmukhi and Urdu-style scripts often omit
vowels, so automatic transliteration can be wrong.

## 5. Script and Language Detection

Current problem:

You currently label scripts manually.

Automation idea:

Detect script automatically:

- Perso-Arabic/Shahmukhi;
- Gurmukhi;
- Devanagari;
- Latin.

This is safer than full language detection because Unicode ranges can identify
scripts fairly reliably.

Human still needed:

Language labels still need review, especially for mixed Punjabi, Persian, Urdu,
Braj, Arabic, and Hindi.

## 6. Model Draft Review Interface

Current problem:

Model outputs are stored in JSONL, which is not pleasant to review.

Automation idea:

Build a small local review page where you can see:

- original;
- transliteration;
- model translation;
- model tashreeh;
- correction boxes;
- score buttons;
- save review.

Human still needed:

The reviewer still decides what is correct.

This would reduce technical friction a lot.

## 7. Website Auto-Generation

Current problem:

The website has not been built yet.

Automation idea:

Once the Astro website exists, the export command can copy `data/site/` into the
website and run the static build.

Possible command:

```powershell
abshaar build-website
```

Human still needed:

Design decisions, content review, and publication approval.

## 8. AI Explanation Drafting in Batches

Current problem:

Drafting one poem at a time is slow.

Automation idea:

Create:

```powershell
abshaar draft --all
```

It would generate drafts for all poems that do not already have model outputs.

Human still needed:

Every output should still be reviewed before publication.

## 9. Evaluation Automation

Current problem:

Eventually you need to know whether the model is improving.

Automation idea:

Create a fixed evaluation set and score model outputs using a rubric. Some
scores can be AI-assisted, but human scoring should remain the gold standard.

Possible command:

```powershell
abshaar evaluate
```

Human still needed:

Human evaluation remains necessary because poetic and metaphysical accuracy
cannot be trusted to automatic scores alone.

## 10. Fine-Tuning Dataset Builder

Current problem:

Fine-tuning requires clean training examples.

Automation idea:

When enough human reviews exist, generate training data automatically:

```powershell
abshaar export-training-data
```

It would create instruction-response examples from reviewed poems only.

Human still needed:

A person must confirm that all training examples are legally safe and high
quality.

## Recommended Automation Roadmap

Do these next:

1. Add `add-source`.
2. Add automatic script detection.
3. Add `suggest-terms`.
4. Add `refresh`.
5. Add a local review interface.
6. Add website build automation.
7. Add batch drafting.
8. Add evaluation automation.
9. Add training-data export.

This order is deliberate. It automates low-risk formatting and project management
before automating interpretation.

## The Safety Rule

Automate repetition, not judgment.

The system can prepare drafts, check structure, detect missing fields, and build
files. But for this project, final meaning, source trust, copyright safety, and
publication approval should remain human decisions.
