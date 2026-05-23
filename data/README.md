# Data Folder

This folder will hold public, reviewable project data. Keep canonical data in
plain text, JSON, JSONL, Markdown, or CSV so contributors can inspect changes in
Git.

Recommended layout:

```text
data/
  raw/
    public/
    private/
  processed/
  annotations/
  lexicon/
  context/
  cache/
```

Only commit material that is public-domain, permission-cleared, or created for
this project.

Do not commit:

- private notes;
- copyrighted scans;
- copyrighted modern translations;
- model files;
- generated vector databases;
- cache files.

Use `data/raw/private/` for local-only material that cannot be published. That
path is ignored by Git.

Starter templates live in `data/templates/`. The recommended first corpus target
is Bulleh Shah, so the template IDs use `bulleh_shah_*` naming.

For manual entry, use `data/working/`. Start by copying
`data/working/bulleh_shah_entry_template.md` and filling in original text,
transliteration, literal gloss, literary translation, tashreeh, and source notes.

The automation CLI can convert working entries into `data/processed/poems.jsonl`:

```powershell
.\scripts\abshaar.ps1 build-data
```
