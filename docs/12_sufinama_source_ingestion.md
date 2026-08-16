# Sufinama Source Ingestion

Last verified: 2026-07-13

## Purpose

This workflow adds Sufinama's Bulleh Shah kaafi collection and seven non-kaafi
textual categories as separate, traceable source-witness datasets. It does not
overwrite or flatten the 72 existing Markdown entries. Rauf stated that this
acquisition is part of an authorized collaborative research project with
Sufinama.

## Verified Source Structure

The official catalog pages are:

- `https://sufinama.org/poets/bulleh-shah/kaafi`
- `https://sufinama.org/poets/bulleh-shah/kaafi?lang=ur`

Both advertise 76 kaafi. The first response contains 50 items and exposes a
page-two endpoint containing 26 more. The Roman and Urdu rankings differ, so
items are paired by their shared Sufinama content UUID rather than list position.

Individual poems share a stable path; the Urdu view normally adds `?lang=ur`.
Most poems expose a stable content UUID, diacritic Roman, plain Roman,
Urdu/Nastaliq, stanza IDs (`data-p`), line IDs (`data-l`), and token mapping IDs
(`data-m`). Three records redirect both requested views to Hindi, and one record
redirects its Roman request to Urdu. Preserve every returned layer and record
the missing requested view as source-unavailable.

The non-kaafi source layer contains exactly 48 category records: 3 kalaam, 23
dohas, 7 shabads, 12 dohras, 1 athvara, 1 barahmasa, and 1 holi. The 25 records
outside the doha category use detail pages. The 23 dohas are embedded in their
category page, but still expose stable content UUIDs, line IDs, token mapping
IDs, and script layers. Each default, Urdu, and Hindi request is recorded
separately because redirects and missing requested scripts are common.

## Commands

Discover and pair the complete catalog:

```bash
./scripts/abshaar.sh acquire-sufinama --discover-only
```

Acquire all authorized poem views:

```bash
./scripts/abshaar.sh acquire-sufinama --transport curl
```

Resume without refetching cached pages by running the same command. Force a
refresh only when necessary:

```bash
./scripts/abshaar.sh acquire-sufinama --transport curl --refresh
```

Rebuild normalized records, audit statistics, and the full-text crosswalk using
only the saved catalog and cache:

```bash
./scripts/abshaar.sh acquire-sufinama --offline --transport curl
```

Smoke-test a small batch:

```bash
./scripts/abshaar.sh acquire-sufinama --transport curl --limit 1 --workers 1
```

Discover the 48 non-kaafi category records:

```bash
./scripts/abshaar.sh acquire-sufinama-texts --discover-only --transport curl
```

Acquire them live, or rebuild them entirely from cache:

```bash
./scripts/abshaar.sh acquire-sufinama-texts --transport curl
./scripts/abshaar.sh acquire-sufinama-texts --offline --transport curl
```

## Outputs

| Path | Purpose | Git policy |
|---|---|---|
| `data/context/sufinama_source_items.jsonl` | 76 paired UUID/title/URL catalog records | Reviewable metadata |
| `data/raw/private/sufinama/*.html` | Raw Roman and Urdu page snapshots | Ignored/private |
| `data/processed/private/sufinama_bulleh_shah_kaafi.jsonl` | Normalized aligned witness records | Tracked; authorized private-repository research dataset |
| `data/processed/private/sufinama_match_manifest.jsonl` | Full-text input for matching | Ignored/private |
| `data/context/source_matches.jsonl` | Top candidate links to existing poems | Human review required |
| `data/processed/private/sufinama_run.json` | Run counts, parser version, coverage, alignment audit, and errors | Tracked |
| `data/context/sufinama_text_source_items.jsonl` | 48 non-kaafi category/UUID/title/URL records | Reviewable metadata |
| `data/processed/private/sufinama_bulleh_shah_other_texts.jsonl` | Normalized non-kaafi source witnesses | Tracked; authorized private-repository research dataset |
| `data/processed/private/sufinama_texts_match_manifest.jsonl` | Private full-text input for non-kaafi matching | Ignored/private |
| `data/context/sufinama_text_source_matches.jsonl` | Separate candidate links for the 48 records | Human review required |
| `data/processed/private/sufinama_texts_run.json` | Non-kaafi counts, coverage, cache, and error audit | Tracked |

## Witness Record Design

Each normalized record contains the Sufinama UUID and slug, catalog titles,
source/final URLs, separate Urdu/diacritic-Roman/plain-Roman layers, aligned
stanza/line/token arrays, view availability, raw snapshot checksums, and parser
version. Non-kaafi records also preserve their source category, acquisition
mode (`detail` or `inline`), every requested view's returned layers, and a
`canonical_work_id: null` placeholder that must not be filled automatically.
Retrieval time belongs in the run manifest so repeated parsing of the same cache
can remain deterministic.

## Crosswalk Rules

- Treat Sufinama records as source witnesses, not replacements for existing
  poems.
- Compare titles and every Urdu/Roman line; a catalog title can be an interior
  refrain rather than Rafat's first line.
- Review exact, variant, excerpt, possible, and unmatched relations manually.
- `bulleh_shah_0001` is the direct Sufinama kaafi-12 witness.
- `bulleh_shah_0029` is the same canonical work through Rafat but a different
  textual witness; do not merge their text.
- Future data splits should group by canonical work so variants of the same kafi
  cannot leak across train/validation/test partitions.
- Treat the 48 non-kaafi records as category witnesses, not 48 proven new works.
  Kalaam, shabad, holi, and other categories visibly overlap kaafi records.
- Devanagari-only records cannot be reliably matched by the current Roman/Urdu
  matcher; a missing candidate is not evidence that a work is absent.

## Current Run State

- Acquisition completed with 76 unique normalized records and 152 raw snapshots.
- Availability: 145 requested views are `ok`; 7 are `unavailable` because the
  source redirects to a different language; there are 0 fetch/parse errors.
- Layer coverage: 72 plain Roman, 72 diacritic Roman, 73 Urdu, and 3 Devanagari
  records. All 76 records contain mapping IDs.
- All 72 witnesses containing both Roman and Urdu have matching stanza/line ID
  sequences and matching per-line mapping-ID sets. Mapping IDs are compared as
  sets because one Roman token can correspond to multiple Urdu tokens carrying
  the same mapping ID.
- The matcher regenerated 76 full-text candidate records; all remain
  `needs_review`. Eleven have a top score of 1.0, 23 have a top score of at least
  0.85, and 3 have no candidate among the existing 72 entries.
- The first bulk attempt exposed a cross-platform cache-write bug. The corrected
  collector, redirect handling, dominant-script classification, unavailable-view
  modeling, and offline rebuild are covered by regression tests.
- Non-kaafi acquisition completed with 48 unique records, 78 raw snapshot files
  referenced by normalized records, 0 errors, and 41 source-unavailable requested
  views. Coverage is 7 plain Roman, 7 diacritic Roman, 8 Urdu, and 47 Devanagari
  records; all 48 have token mapping IDs.
- Its separate crosswalk contains 48 review-required records. One exact
  Roman/Urdu candidate was found (`kalaam` → `bulleh_shah_0025`); 40 records have
  no candidate because most are Devanagari-only and the matcher does not yet
  transliterate Devanagari. **Resolved 2026-08-15:** `src/abshaar/devanagari.py`
  adds an approximate, comparison-only Devanagari→Roman transliteration; the
  matcher now emits `devanagari_title_to_any_line` / `devanagari_any_line`
  signals, hard-capped at score 0.98 so approximate evidence can never reach
  the 1.0 exact threshold that auto-merges canonical work clusters. After the
  offline rebuild, 0 of 48 non-kaafi and 0 of 76 kaafi records lack candidates
  (previously 40 and 3); exact-1.0 counts are unchanged (1 and 11). All
  Devanagari-signal candidates remain `needs_review` — the transliteration is
  a matching key, never witness text.
- The cache-only non-kaafi rebuild reproduced all 48 records with the same
  category/layer/error counts and made no network requests.

## Crosswalk classification (AI first pass, 2026-08-16)

All 124 match records now carry a `match_status` classification
(`exact_witness` / `variant` / `excerpt` / `possible` / `unmatched`) plus a
`match_review` block recording the classified-against poem, evidence note,
method, and `human_confirmed: false`. The workflow:

1. `abshaar crosswalk-evidence` writes deterministic two-way line-coverage
   evidence and per-line alignments to `data/annotations/crosswalk_evidence.md`.
   Coverage (share of each side's lines with a counterpart at similarity
   ≥ 0.80 strong / ≥ 0.60 loose, 0.55 on the approximate Devanagari channel)
   answers what the matcher's max-similarity score cannot: one shared refrain
   or title can score 0.6–0.9 between otherwise different poems.
2. Decisions live in `data/annotations/crosswalk_classifications.jsonl` —
   one JSON object per record. Edit a line, then re-run
   `abshaar apply-crosswalk-review` (validates the whole file, then rewrites
   both match files atomically and idempotently).
3. `python3 scripts/build_review_queue.py` refreshes the worksheet, which now
   shows each record's status (`(ai)` = awaiting human confirmation).

Conventions: `excerpt` means one text is contained in the other — the note
names the fuller side. `unmatched` means no line-level relation to any of the
72 entries; per plan §9 it is NOT a claim of a unique canonical work.
Devanagari-only judgments are flagged in their notes as
approximate-transliteration evidence.

Results of the first pass: 1 exact_witness, 30 variant, 10 excerpt,
1 possible, 82 unmatched. Notable findings recorded in the notes: the
kaafi-44 page is a composite (a distinct kafi + all of `bulleh_shah_0059`);
the athvara witness contains entries 0068 and 0069 as day-sections and the
barahmasa contains 0070 and 0071 as month-sections; kaafi-62 reads *maTi*
where entry 0046 reads *mai* throughout; kaafi-50's closing couplet matches
entry 0017 rather than 0032 (stanza recombination); the doha witnesses of
0006 supply a *jurriyan*/*churiyan* reading lead; several works appear in two
Sufinama categories (holi=kaafi 53d02f64, kalaam-1=kaafi 9ba747aa,
shabad-4=kaafi-20, and two doha/dohra pairs).

## Verification Expectations

- [x] Confirm 76 catalog records and unique UUIDs.
- [x] Confirm 152 raw snapshots and recorded SHA-256 hashes.
- [x] Inspect view errors and redirects: 0 errors; 7 source-unavailable views.
- [x] Confirm Roman/Urdu stanza and line IDs for all 72 paired witnesses.
- [x] Preserve hidden raw content without duplicating it with visible HTML.
- [ ] Human-review the generated crosswalk. **AI first pass complete
  (2026-08-16, all 76 records classified with evidence; `human_confirmed:
  false`)** — human confirmation still open.
- [x] Prove the 72 existing Markdown entries were not modified.
- [x] Run unit tests, validation, and `build_all`.
- [x] Confirm 48 non-kaafi catalog and normalized records across all 7 categories.
- [x] Confirm 0 non-kaafi view errors and 41 source-unavailable requested views.
- [x] Rebuild all 48 non-kaafi witnesses offline from cache.
- [ ] Human-review the 48-record non-kaafi crosswalk and assign canonical-work
  relationships only where evidence supports them. **AI first pass complete
  (2026-08-16; `human_confirmed: false`)** — human confirmation still open.
