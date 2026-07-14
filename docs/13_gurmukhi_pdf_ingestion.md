# PunjabLibrary Gurmukhi PDF Ingestion

## Purpose

This workflow preserves the 160 numbered Gurmukhi kafis in the local
PunjabLibrary PDF as a third source witness. It does not merge or overwrite the
72 Rafat/Sufinama-derived working entries. It creates a source catalog that can
later support cross-script matching and canonical-work clustering.

## Source and rights posture

- Source: *Kafian: Baba Bulleh Shah*, a 149-page PDF served by
  `PunjabLibrary.com`.
- PDF metadata: author `Navtej Singh Atwal`; created 2017-06-17 with Microsoft
  Word 2013. The exact editorial role is `Needs verification`.
- The Bulleh Shah compositions are public domain.
- Rights in the 2017 selection, transcription, typography, and PDF edition are
  `unknown`.
- Therefore the full extracted witness and run audit remain under ignored
  `data/processed/private/`. Only the item-level catalog is stored in
  `data/context/` for review.

## Important quality limitation

The PDF renders clean Gurmukhi, but its embedded text layer is defective. Visual
comparison of PDF page 2 showed dropped or misordered characters and irregular
intra-word spacing in extracted text. The importer deliberately does not try to
guess corrections.

Each record states:

- `quality_status: needs_visual_review`;
- `authoritative_representation: source_pdf_page_image`;
- the source page range;
- the PDF SHA-256;
- the extraction method and parser version.

Do not use the extracted string as canonical text or training data until it has
been checked against rendered pages or replaced with a rights-cleared, verified
transcription.

## Command

From the project root on macOS/Linux, with Python 3.11+ and `pypdf` installed:

```bash
./scripts/abshaar.sh extract-gurmukhi-pdf \
  --input "Bulleh Shah/Kafian - Baba Bulleh Shah (Baba Bulle Shah) (z-library.sk, 1lib.sk, z-lib.sk).pdf"
```

On Windows, pass the same arguments through `scripts\abshaar.ps1`.

If needed, install the optional PDF dependency:

```bash
python3 -m pip install -e '.[pdf]'
```

The command expects 160 consecutively numbered works by default. It fails rather
than writing a partial dataset if an ordinal is missing or duplicated.

## Outputs

| Path | Contents | Git posture |
|---|---|---|
| `data/context/punjab_library_source_items.jsonl` | 160 IDs, extracted titles, ordinals, page spans, and review notes | Reviewable catalog metadata |
| `data/processed/private/punjab_library_bulleh_shah_kafian.jsonl` | Full extracted Gurmukhi witness text and extraction warnings | Ignored/private |
| `data/processed/private/punjab_library_gurmukhi_run.json` | PDF hash, page count, parser/dependency versions, and audit totals | Ignored/private |

## Verified 2026-07-12 result

- PDF pages: 149
- Extracted records: 160
- Unique ordinals: 160 (`1` through `160`)
- Missing ordinals: 0
- Duplicate ordinals: 0
- Empty titles: 0
- Empty extracted texts: 0
- Extracted text characters: 120,133
- PDF SHA-256:
  `f4a6a1ba5274d30bc6d58b4e37afe85ffd9df4e5a9fe9474e8622b21094fa074`

## Next editorial work

1. Obtain or identify a clean, rights-cleared Gurmukhi text layer.
2. Human-check the 160 extracted titles against the rendered page headings.
3. Add Gurmukhi-to-Roman transliteration only as a separate project-authored
   layer with explicit provenance.
4. Match Gurmukhi witnesses to Sufinama and Rafat by reviewed cross-script first
   lines; do not infer identity from source order.
5. Assign `canonical_work_id` only after variant/full/excerpt relationships are
   reviewed.
