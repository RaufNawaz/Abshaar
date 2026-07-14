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

Sufinama source ingestion uses:

- `data/context/sufinama_source_items.jsonl` for the 76-item paired catalog;
- `data/context/source_matches.jsonl` for reviewable candidate links;
- `data/context/sufinama_text_source_items.jsonl` for the 48 non-kaafi textual
  category records;
- `data/context/sufinama_text_source_matches.jsonl` for their reviewable
  candidate links;
- `data/raw/private/sufinama/` for cached raw HTML;
- `data/processed/private/sufinama_bulleh_shah_kaafi.jsonl` for normalized Urdu,
  diacritic Roman, plain Roman, stanza, line, and token-alignment data;
- `data/processed/private/sufinama_bulleh_shah_other_texts.jsonl` for the 3
  kalaam, 23 inline dohas, 7 shabads, 12 dohras, athvara, barahmasa, and holi;
- `data/processed/private/sufinama_texts_run.json` for the non-kaafi acquisition
  audit.

The raw HTML cache remains ignored. Because Rauf states that this is an
authorized Sufinama collaboration and the repository is private, the normalized
Sufinama witness JSONL and its run/audit manifest are commit-eligible. They stay
source-separated and must not overwrite the 72 working Markdown entries.

The 72 Markdown files remain separate source witnesses and are never overwritten
by the acquisition or matching commands.

PunjabLibrary Gurmukhi PDF ingestion uses:

- `data/context/punjab_library_source_items.jsonl` for the 160-item numbered
  catalog, page spans, and review status;
- `data/processed/private/punjab_library_bulleh_shah_kafian.jsonl` for the full
  extracted Gurmukhi text witness;
- `data/processed/private/punjab_library_gurmukhi_run.json` for the source hash,
  parser version, PDF metadata, and extraction audit.

The catalog is reviewable metadata. The full text and run record stay ignored
because rights in the 2017 digital transcription are `unknown`. The extraction
is not canonical: the embedded PDF text layer visibly omits or misorders some
Gurmukhi characters and inserts irregular spaces. Use rendered PDF pages as the
authority and keep every record `needs_review` until a human compares it to the
page image.

Bulleh Shah internet research uses:

- `data/context/biographical_claims.jsonl` for claim-level biography with
  confidence, evidence status, cautions, and source IDs;
- `data/context/events.jsonl` for a cautious life/historical timeline;
- `data/context/sufinama_bulleh_shah_inventory.jsonl` for every content category
  and count reported by Sufinama's Bulleh Shah pages.

Sufinama category counts are not unique-work counts. The 48 non-kaafi records
are source-category witnesses, not 48 newly established compositions. Kaafi,
kalaam, shabad, holi, and other categories overlap. Preserve the category as
source metadata and assign `canonical_work_id` only after item-level review.

Starter templates live in `data/templates/`. The recommended first corpus target
is Bulleh Shah, so the template IDs use `bulleh_shah_*` naming.

For manual entry, use `data/working/`. Start by copying
`data/working/bulleh_shah_entry_template.md` and filling in original text,
transliteration, literal gloss, literary translation, tashreeh, and source notes.

The automation CLI can convert working entries into `data/processed/poems.jsonl`:

```powershell
.\scripts\abshaar.ps1 build-data
```
