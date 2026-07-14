# Bulleh Shah Corpus — Build Log (resumable)

> Purpose: a running log so this multi-session task can be resumed if a session
> ends. Read this top-to-bottom to know where things stand and what to do next.
> Complements the repo-wide `OFFLOADING.md`.
>
> Started: 2026-07-04 · Last updated: 2026-07-13

## Goal

Comprehensive corpus of Bulleh Shah's kafis in the Abshaar project format (one
Markdown entry per poem in `data/working/bulleh_shah_XXXX.md`, compiled by
`build-data` into `data/processed/poems.jsonl`). Open-source, academic,
non-commercial.

## Active plan (per user, 2026-07-04)

Build the corpus from **Book C — Taufiq Rafat, "Bulleh Shah: A Selection,
Rendered into English Verse"** (71 poems). For each poem: transcribe the Urdu
original + provide project-latin transliteration + record Rafat's English. Keep a
log (this file) so work can resume across sessions.

## Source books (in `Bulleh Shah/`)

| # | File | Content | Extraction | Rights | Use |
|---|---|---|---|---|---|
| C | `Bulleh Shah, A Selection Rendered into English Verse (Taufiq Rafat)...pdf` | **71 poems**; each = typeset **English** (odd page) facing **handwritten Nastaliq Urdu original** (even page). Plus Translator's Note, Introduction, Glossary (Urdu→English), Index of First Lines. Google/Univ. of Michigan scan. | English: OCR/read cleanly. **Urdu: NOT machine-OCR-able** (calligraphic Nastaliq; tesseract has no Urdu). Only manual visual transcription. | Original verses PD; **Rafat's English COPYRIGHTED** (d. 1998). | **PRIMARY** now |
| A | `Kafian - Baba Bulleh Shah ...pdf` (PunjabLibrary) | 160 Gurmukhi kafis, consecutively numbered across 149 pages | Full source-separated extraction completed 2026-07-12; embedded text is noisy and remains `needs_visual_review` | PD verses; rights in 2017 digital transcription unknown | Private secondary witness + reviewable catalog |
| B | `Bulle Shah ...pdf` (Devanagari/Hindi) | — | — | — | **IGNORE** (user, 2026-07-04) |

## CRITICAL technical reality (2026-07-04)

- **English** in Book C is typeset and OCRs near-perfectly (tesseract `eng`), or I
  read it directly from the page image. High quality.
- **Urdu original** is *handwritten calligraphic Nastaliq*. There is **no reliable
  OCR** for it here (tesseract has only `eng`; calligraphic Nastaliq defeats OCR
  anyway). Method = **I transcribe by visually reading each page image**. This is
  workable but imperfect and every poem's original NEEDS native/scholarly review.
- Therefore throughput is manual: ~71 poems × (read Urdu page + read English page)
  = a real multi-session effort. Hence this log.

## Copyright position

- Bulleh Shah's original verses (any script) = public domain. Safe to include.
- **Taufiq Rafat's English = copyrighted (~until 2068).** Recording it wholesale
  into a repo intended to be public/open-source would be infringement. Current
  safeguard: entries carry `rights_status: verify_before_publication`,
  Source Notes say "Can this be published? no", and the publish-gate keeps them
  off any website export. OPEN DECISION on repo storage below.
- This copy is a z-library scan of a Google/UMich digitization (personal-use grey
  area). Fine for private academic study; not for redistribution.

## Book C page map (for resume)

- PDF offset: **book page + 20 = PDF page** (book p35 "A for Allah" English = PDF
  p55; its Urdu original = book p34 = PDF p54).
- Pattern: **English = the odd book page listed in the Contents; Urdu original =
  the facing even page (book page − 1).** Long poems span extra pages — check each.
- Contents (poem: English book-page): 1 A for Allah 35 · 2 The Difference 37 ·
  3 Wayfarer, arise 39 · 4 I Swallowed the Hook 43 · 5 The Trap 45 · 6 Where is
  your Home 47 · 7 A Safe Place 49 · 8 Embrace me, Love 51 · 9 Left Alone 53 ·
  10 Spell 55 · 11 Heritage 59 · 12 One is Enough 61 · 13 A Topsy-turvy World 65 ·
  14 Not for a Moment 67 · 15 Does Anyone Know 69 · 16 Briefing Bulleh 73 ·
  17 Wanderer, Ho 75 · 18 Accused 77 · 19 The Follower 79 · 20 I'm in a Trap 83 ·
  21 Whatever you Touch 85 · 22 Be Silent Now 87 · 23 Acquaintance 89 · 24 Who's
  Keeping the Gossips Busy 91 · 25 The World's a Fun-fair 95 · 26 With Love my
  Heart Overflows 97 · 27 The Broken Spinning-wheel 99 · 28 The Transformation 101
  · 29 The Lover's Way 103 · 30 Rituals 105 · 31 All Cotton-bolls are White 107 ·
  32 The Buyer 109 · 33 Love comes on Bright New Wings 111 · 34 Enough of Learning
  115 · 35 Stop the Spinning-wheel Girl 121 · 36 Dogs are Better than you 125 ·
  37 Name 127 · 38 Come See Me Once in a While 129 · 39 Lass, Look to your Spinning
  131 · 40 This Mad Lover 137 · 41 Penitence 139 · 42 Who Choose Cold-hearted Dears
  141 · 43 My Love has Come to Call 145 · 44 Up with your Veil, Love 149 · 45 Clay
  151 · 46 The Benighted 153 · 47 I'm Harbouring a Thief 155 · 48 Gather Round me
  157 · 49 Truth Will Out 159 · 50 God has Come Down as Man 163 · 51 I'm Waiting
  165 · 52 I'm Just a Sweepress 167 · 53 The Load 169 · 54 From the First Moment
  171 · 55 Strange are the Ways of my Love 173 · 56 Neither Hindu nor Muslim 177 ·
  57 Obfuscation 179 · 58 The Semi-literate 181 · 59 The Story of Creation 183 ·
  60 Love's Arrival 187 · 61 Honesty 191 · 62 I'm not Talking of Here 193 ·
  63 Desertion 195 · 64 Relatively Speaking 197 · 65 Because of you 199 · 66 Plea
  for Protection 201 · 67 Saturday 203 · 68 Thursday 205 · 69 Spring 207 · 70 Rain
  209 · 71 Knots 211. (Glossary 227, Index of First Lines 237.)

## Decisions made

- 2026-07-04: Build from Book C (Rafat), 71 poems. Ignore Book B. Book A optional.
- 2026-07-04: Urdu originals transcribed by visual reading (no OCR available);
  flagged for human verification.

## Open decisions (asked user 2026-07-04)

1. **Copyright storage for Rafat's English** (repo is meant to be public): keep it
   in entries but gate-private + keep repo private / store English in gitignored
   `data/raw/private/` and keep only PD Urdu public / include openly (risky).
2. **Scope & pace:** all 71 in logged batches vs. a batch of ~10 then review.

## Current state

- Corpus composition: `bulleh_shah_0001` is the Sufinama pilot; entries
  `bulleh_shah_0002` through `_0072` are Rafat poems 1–71. All build and remain
  correctly flagged incomplete because human interpretive/review layers are pending.
- Sources: `source_sufinama_bulleh_0001`, `source_rafat_selection`. Person:
  `bulleh_shah`.
- **CORPUS COMPLETE (2026-07-06).** All 71 Rafat poems are transcribed. `status`:
  72 working / 72 processed / 2 sources / 1 person / 0 public. 0 errors (144 placeholder
  warnings — intentional, interpretive layers remain TODO). Entries: 0001 Ranjha Ranjha
  (Sufinama) + 0002-0072 = Rafat poems 1-71 (entry id = Rafat poem + 1). Multi-spread
  poems: 0011 (Spell), 0013 (One is Enough), 0025 (Who's Keeping the Gossips Busy),
  0034 (Love comes on Bright New Wings), 0035 (Enough of Learning — 3 spreads),
  0040 (Lass Look to your Spinning — 3 spreads), 0043 (Who Choose Cold-hearted Dears),
  0044 (My Love has Come to Call), 0050 (Truth Will Out), 0056 (Strange are the Ways),
  0060 (The Story of Creation), 0061 (Love's Arrival), 0072 (Knots). Poem 71 is the
  last poem in the book (verified: blank leaf + Glossary follow at book p.227).
- **CONFORMANCE (as of 2026-07-06):** Rafat poems 1-71 (entries 0002-0072) ALL conform
  to the 3-slot layout — each has all 11 sections, `# Literal Translation` (Rafat verbatim,
  gated with copyright note), `# AI Translation` (Claude's own rendering of the Urdu), and
  `# Literary Translation` (TODO rauf); every entry gated (publish=no, train=no). The batch
  task's "done" test (`# AI Translation` present) passes for 0002-0072. **The Rafat book is
  fully transcribed — no next poem.** Remaining work is human (rauf): review the flagged
  uncertain Urdu readings, and fill the Literary Translation / Tashreeh / Key Terms / Themes
  interpretive layers.
- COPYRIGHT POSTURE (current, applies to all Rafat entries): Rafat's English **is
  recorded verbatim** but ONLY in `# Literal Translation`, always with the reference/
  copyright note and gated (Can this be published? no; training? no); repo stays
  private. This SUPERSEDES the earlier "cite-not-reproduce" posture. The corpus's real
  public-domain content is the Punjabi original (poet d. 1757), transcribed in full.
- Rendered page images live in the scratch outputs dir (not committed; deleted after each batch).
- **GURMUKHI WITNESS (2026-07-12):** Added a non-destructive importer for Book A
  and extracted all 160 numbered works into ignored
  `data/processed/private/punjab_library_bulleh_shah_kafian.jsonl`. The
  160-record catalog at `data/context/punjab_library_source_items.jsonl`
  preserves ordinals and page spans. Audit: 149 PDF pages, 160 unique ordinals
  1–160, 0 missing, 0 duplicates, 0 empty titles, 0 empty texts, and 120,133
  extracted characters. The PDF SHA-256 is
  `f4a6a1ba5274d30bc6d58b4e37afe85ffd9df4e5a9fe9474e8622b21094fa074`.
  Visual inspection of page 2 confirmed that the page renders correctly but the
  embedded text layer can drop/misorder Gurmukhi characters; never treat the
  extraction as canonical without page-image review.
- **BIOGRAPHY + SUFINAMA INVENTORY (2026-07-12):** Internet research added 11
  claim-level biographical records, 6 cautious timeline events, and a 13-record
  Sufinama category inventory. The key scholarly caution is that Bulleh Shah's
  biography and corpus are not definitive: later traditions disagree on
  birthplace and life details, while performance transmission produced variants
  and attribution problems. Sufinama lists 3 kalaam, 23 dohe, 7 shabads, 12
  dohras, 1 athvara, 1 barahmasa, 1 holi, 24 quotes (one page showed 21), 1
  e-book, 164 videos, 1 blog, and a profile in addition to 76 kaafis. These
  categories overlap and must not be summed as unique works.
- **SUFINAMA NON-KAAFI EXPANSION (2026-07-13):** Added a separate 48-record
  normalized witness corpus covering 3 kalaam, 23 inline dohas, 7 shabads, 12
  dohras, 1 athvara, 1 barahmasa, and 1 holi. The run preserved UUIDs, returned
  script layers, line/token IDs, raw hashes, and requested-view availability;
  it reported 0 errors, 41 source-unavailable views, and layer coverage of 7
  plain Roman, 7 diacritic Roman, 8 Urdu, and 47 Devanagari records. All 48 have
  mapping IDs. The cache-only rebuild reproduced the same structural counts.
  These are overlapping source-category witnesses, not 48 proven unique works,
  and the separate 48-record crosswalk remains human-review-required.

## Historical ingestion procedure (do not resume)

The Rafat corpus is complete. There is no next poem. The steps below are retained
only as provenance for how the batch was built. Do not create or overwrite corpus
entries with the legacy ingestion script; its template predates the final
three-slot translation layout.

1. Read this log + `OFFLOADING.md`.
2. Pick the next poem N from the page map. Render its two pages:
   `pdftoppm -png -r 150 -f <PDF_pg> -l <PDF_pg> "<Book C>.pdf" out` (PDF pg =
   book pg + 20). Read the Urdu (even) page image → transcribe; read/OCR the
   English (odd) page.
3. Create `data/working/bulleh_shah_XXXX.md` from the template; fill Original +
   Transliteration + Literary Translation (Rafat, flagged); leave gloss/tashreeh/
   terms/themes as TODO.
4. `PYTHONPATH=src python3 -m abshaar build-data --include-placeholders` →
   `... validate`. Update this log's Current state + Changelog.

## OCR tooling option — UTRNet (evaluated 2026-07-04)

User has a working Urdu OCR app at `Harvard/End-To-End-Urdu-OCR-WebApp` (UTRNet:
YOLOv8 line detection + CRNN recognition; CC BY-NC-SA, academic use OK; weights
`best_norm_ED.pth` + `yolov8m_UrduDoc.pt` already present). Considered for OCR-ing
the Rafat Urdu pages instead of hand-transcription.

- **Limitation:** UTRNet is trained on PRINTED Nastaliq; Rafat's originals are
  handwritten/calligraphic, so accuracy there is uncertain. Best on printed text.
- **Could not test in the assistant sandbox** (no PyPI/PyTorch network access).
  Must run on the user's Mac.
- **Mac setup delivered** in that folder: `setup_mac.sh`, `requirements-mac.txt`,
  `batch_ocr.py` (folder/PDF -> text, MPS/CPU auto-detect), `README_MAC.md`. Note:
  the bundled `.venv` is a Windows venv and won't run on Mac.
- **Next:** user runs the test in `README_MAC.md` on Rafat PDF pages 54-58, judges
  quality. Good -> OCR the whole book (replaces hand-transcription). Poor -> keep
  hand-transcribing the calligraphy, and/or point UTRNet at a printed edition.

## Changelog

- 2026-07-13 (Sufinama non-kaafi text expansion): Implemented
  `acquire-sufinama-texts`, including a generic UUID catalog parser, inline-doha
  parser, three-request script/redirect preservation, cache/offline rebuild,
  category audit, and separate crosswalk. Live discovery found exactly 48
  records across all seven inventoried textual categories. Full acquisition and
  offline rebuild each wrote 48 records with 0 view errors and 41 honest
  source-unavailable requested views; no working Markdown poem was modified.

- 2026-07-12 (internet research and Sufinama scope expansion): Added sourced
  biography/context records from a Western Sydney University thesis, Sufinama's
  profile, and the Government of Punjab Auqaf shrine page. Added a full category
  inventory for Bulleh Shah's Sufinama presence and documented overlap risks.
  A planned read-only smoke test against a non-kaafi detail page did not run
  because external-access approval quota was exhausted until 4:56 PM; no retry or
  workaround was attempted. Next work is to extend the authorized collector to
  non-kaafi textual categories after the limit resets.

- 2026-07-12 (Gurmukhi source expansion): Built `extract-gurmukhi-pdf`, added
  source/catalog/run provenance, and extracted all 160 numbered PunjabLibrary
  Gurmukhi kafis without modifying any of the 72 working Markdown entries. The
  full witness remains ignored/private because the 2017 digital transcription's
  rights are unknown and its embedded text is visibly defective. Added parser
  tests, a source record, and a dedicated ingestion guide.

- 2026-07-12 (repository-wide audit; no poem-content changes): Re-verified
  `status` at 72 working / 72 processed / 2 sources / 1 person / 0 public, with
  0 errors and 144 expected placeholder warnings. Unit tests pass. Updated the
  shared Codex/Claude workflow and repo handoff to reflect corpus completion,
  copyright risk, schema mismatch, and next editorial steps. Identified that the
  current `build_all` wrappers omit `--include-placeholders` and can overwrite
  the processed corpus with zero records; do not run them until fixed. Added a
  Git ignore rule for the local source PDFs.

- 2026-07-06 (batch run 8 — **CORPUS COMPLETE**): Processed the final **Rafat poems 42-71 →
  entries `bulleh_shah_0043` through `_0072`** (30 poems) in one run by fanning the work out to
  SIX parallel subagents (each ~5 poems: render at 300 dpi, vision-read the Nastaliq, transcribe
  Urdu + project-latin translit + own AI English, write entries in the 3-slot layout). Parent then
  built + validated centrally. Titles: 0043 Who Choose Cold-hearted Dears, 0044 My Love has Come
  to Call, 0045 Up with your Veil Love, 0046 Clay, 0047 The Benighted, 0048 I'm Harbouring a Thief,
  0049 Gather Round Me, 0050 Truth Will Out, 0051 God has Come Down as Man, 0052 I'm Waiting,
  0053 I'm Just a Sweepress, 0054 The Load, 0055 From the First Moment, 0056 Strange are the Ways
  of my Love, 0057 Neither Hindu nor Muslim, 0058 Obfuscation, 0059 The Semi-literate, 0060 The
  Story of Creation, 0061 Love's Arrival, 0062 Honesty, 0063 I'm not Talking of Here, 0064 Desertion,
  0065 Relatively Speaking, 0066 Because of you, 0067 Plea for Protection, 0068 Saturday, 0069
  Thursday, 0070 Spring, 0071 Rain, 0072 Knots. Multi-spread poems this run: 0043, 0044, 0050, 0056,
  0060, 0061, 0072 (each spanning two spreads; verified by continuation). Poem 71 (0072) confirmed
  the last poem — blank leaf + Glossary follow. build-data + validate clean: **72 processed, 0 errors,
  144 placeholder warnings** (intentional); verified all 71 Rafat entries have all 11 sections, are
  copyright-gated (publish=no/train=no) with the reference note, and carry all three translation kinds.
  Temp PNGs deleted/zeroed. **All 71 Rafat poems are now in the corpus — the book is fully transcribed.**
  Remaining work is human (rauf): verify flagged uncertain Urdu readings and fill the interpretive
  layers. Reviewer note — HIGH-uncertainty interior lines flagged in: 0043, 0044, 0045, 0048, 0049,
  0053, 0054, 0060, 0061, 0066, 0067, 0072 (see each file's Review Notes).

- 2026-07-06 (batch run 7): Processed **Rafat poems 36-41 → entries `bulleh_shah_0037`
  through `_0042`** (SIX poems this run, not 8 — stopped early because two of these poems
  span multiple spreads and context/space ran low; poems 42-43 deferred to next run). Vision-read
  the rendered Nastaliq pages at 300 dpi (PDF pp.144-159). New entries: 0037 Dogs are Better
  than you (Kutte teethon utte), 0038 Names (Gal samajh lai te raula keh — couplet, Ram/Rahim/
  Maula), 0039 Come See Me Once in a While (Kadi aa mil yaar pyaariya — topical lament of 18th-c.
  Punjab; names Shah Inayat), 0040 Lass Look to your Spinning (Kar kattan val dhyaan kuṛe — SPANS
  THREE spreads pp.130+132+134 / 131+133+135; 8 stanzas; ends "Bulhe da Sultan"), 0041 This Mad
  Lover (Koi puchho dilbar keh karda — wahdat), 0042 Penitence (Kaisi tauba). Each entry: Urdu
  original transcribed + project-latin transliteration; `# Literal Translation` = Rafat's verbatim
  English (gated, copyright note); `# AI Translation` = Claude's own rendering; interpretive layers
  = TODO (rauf). Confirmed poem 39 spans 3 spreads (the 6-page Contents gap). build-data + validate
  clean: 42 processed, 0 errors, 84 placeholder warnings (intentional); all three translation kinds
  present. Temp PNGs deleted/zeroed (incl. the pre-rendered 160-165 for poems 42-43). Rafat poems
  1-41 (0002-0042) now all conform. **Next batch starts at Rafat poem 42 = `bulleh_shah_0043`**
  (English book p.141 → PDF p.161; Urdu p.140 → PDF p.160). NOTE: poem 42 may span 2 spreads
  (4-page Contents gap 141→145). Reviewer: 0039, 0040, 0042 carry HIGH-uncertainty interior lines.

- 2026-07-06 (batch run 6): Processed **Rafat poems 28-35 → entries `bulleh_shah_0029`
  through `_0036`** by vision-reading the rendered Nastaliq pages at 300 dpi (PDF pp.120-141).
  New entries: 0029 The Transformation (Ranjha Ranjha kar di — same kafi as the Sufinama
  entry 0001, kept distinct by source), 0030 The Lover's Way (Dharamsaal… — couplet),
  0031 Rituals (Roze hajj namaz — names the fiqh text Sharh al-Wiqaya), 0032 All Cotton-bolls
  are White (Sab iko rang kapaahaan da), 0033 The Buyer (Satte vanjaare aae), 0034 Love comes
  on Bright New Wings (Ishq di naveeyon naveen bahaar — SPANS two spreads pp.110+112/111+113;
  antinomian), 0035 Enough of Learning (Ilmon bas kareen o yaar — SPANS THREE spreads
  pp.114+116+118 / 115+117+119; the long anti-scholastic kafi, ends naming murshid Shah Inayat),
  0036 Stop the Spinning-wheel Girl (Kat kuṛe na vat kuṛe). Each entry: Urdu original
  transcribed + project-latin transliteration; `# Literal Translation` = Rafat's verbatim
  English (gated, copyright note); `# AI Translation` = Claude's own rendering; interpretive
  layers = TODO (rauf). Confirmed poem 33 spans 2 spreads and poem 34 spans 3 spreads (the
  4- and 6-page Contents gaps); pages 122-123 (after poem 35) are blank. build-data + validate
  clean: 36 processed, 0 errors, 72 placeholder warnings (intentional); all three translation
  kinds present. Temp PNGs deleted/zeroed. Rafat poems 1-35 (0002-0036) now all conform.
  **Next batch starts at Rafat poem 36 = `bulleh_shah_0037`** (English book p.125 → PDF p.145;
  Urdu p.124 → PDF p.144). NOTE for reviewer: 0030, 0033 and the interior lines of 0034/0035/0036
  carry HIGH-uncertainty calligraphic readings — see each file's Review Notes.

- 2026-07-06 (batch run 5): Processed **Rafat poems 20-27 → entries `bulleh_shah_0021`
  through `_0028`** by vision-reading the rendered Nastaliq pages at 300 dpi (PDF pp.102-119).
  New entries: 0021 I'm in a Trap (Jind kaṛki de munh aai), 0022 Whatever You Touch (Jo rang
  rangiya gohṛa rangiya — quotes hadith "Mūtū qabla an tamūtū"), 0023 Be Silent Now (Chup
  kar ke karin guzaara), 0024 Acquaintance (Bharosa keh ashnaai da — a single couplet),
  0025 Who's Keeping the Gossips Busy (Chalo dekhiye os mastaanṛe nu — SPANS two spreads,
  book pp.90+92 / English pp.91+93; embeds four Qur'anic tags: naḥnu aqrab, fī anfusikum,
  fazkurūnī azkurkum, yadu-Llāhi fawqa aydīhim), 0026 The World's a Fun-fair (Khalq tamaashe
  aai yaar — potter-God image), 0027 With Love my Heart Overflows (Dil loche maahi yaar nu),
  0028 The Broken Spinning-wheel (Ḍhalak gayi charkhe di hatthi — charkha metaphor). Each
  entry: Urdu original transcribed + project-latin transliteration; `# Literal Translation`
  holds Rafat's **verbatim** English (gated, copyright note); `# AI Translation` = Claude's
  own independent rendering of the Urdu; `# Literary Translation` + tashreeh/terms/themes =
  TODO (rauf). Confirmed poem 24 spans two spreads (pp.90/91 + 92/93); no blank pages this
  run. build-data + validate clean: 28 processed, 0 errors, 56 placeholder warnings
  (intentional); all three translation kinds present. Temp PNGs deleted/zeroed. Rafat poems
  1-27 (0002-0028) now all conform. **Next batch starts at Rafat poem 28 = `bulleh_shah_0029`**
  (English book p.101 → PDF p.121; Urdu p.100 → PDF p.120). NOTE for reviewer: entries 0021,
  0025, 0027, 0028 carry HIGH-uncertainty interior lines (hard/dense calligraphy) — see each
  file's Review Notes.

- 2026-07-06 (batch run 4): Processed **Rafat poems 12-19 → entries `bulleh_shah_0013`
  through `_0020`** by vision-reading the rendered Nastaliq pages at 300 dpi (PDF pp.80-99).
  New entries: 0013 One is Enough (Ik nuqte vich gal mukdi ae — SPANS two spreads, book
  pp.60+62 / English pp.61+63), 0014 A Topsy-turvy World (Ulṭe hor zamaane aae), 0015 Not
  for a Moment (a short Si Harfi "alif" excerpt), 0016 Does Anyone Know (Bulha! ki jaana
  main kaun), 0017 Briefing Bulleh (Bulhe nu samjhaavan aaiyaan — the Syed/Rai caste kafi),
  0018 Wanderer Ho (Paandhiya ho!), 0019 Accursed (Patiyaan likhaan main shaam nu — the
  densest/hardest page in the batch), 0020 The Follower (Tere ishq nachaaiyaan). Each entry:
  Urdu original transcribed + project-latin transliteration; `# Literal Translation` holds
  Rafat's **verbatim** English (gated, copyright note); `# AI Translation` = Claude's own
  independent rendering of the Urdu; `# Literary Translation` + tashreeh/terms/themes = TODO
  (rauf). Confirmed poem 12 "One is Enough" spans two spreads (pp.60/61 + 62/63); pages 70-71
  between poems 15 and 16 are blank (ignored). build-data + validate clean: 20 processed, 0
  errors, 40 placeholder warnings (intentional); all three translation kinds present
  (literal_gloss=human, ai_translation=ai, literary_translation). Temp PNGs deleted. Rafat
  poems 1-19 (0002-0020) now all conform. **Next batch starts at Rafat poem 20 =
  `bulleh_shah_0021`** (English book p.83 → PDF p.103; Urdu p.82 → PDF p.102). NOTE for
  reviewer: entries 0015, 0018, 0019, 0020 carry HIGH-uncertainty interior lines (hard
  calligraphy) — see each file's Review Notes.

- 2026-07-06 (batch run 3): Upgraded **Rafat poems 4-11 → entries `bulleh_shah_0005`
  through `_0012`** from the old cite-only layout to the new 3-slot layout. Re-rendered
  PDF pp.62-79 at 300 dpi and vision-verified every Urdu original against the page images
  (all prior transcriptions confirmed faithful; poem 10 "Spell" confirmed spanning book
  pp.54+56 / English pp.55+57). For each entry: `# Literal Translation` now holds Rafat's
  **verbatim** English (gated, copyright note) instead of a cite-only placeholder;
  `# AI Translation` adds Claude's own independent English rendering of the Urdu;
  `# Literary Translation` = TODO (rauf). Transliterations retained; interpretive layers
  (tashreeh/terms/themes) remain bracketed TODO. build-data + validate clean: 12 processed,
  0 errors, 24 placeholder warnings (intentional); all three translation kinds
  (literal_gloss=human, ai_translation=ai, literary_translation) present. Temp PNGs deleted.
  Rafat poems 1-11 (0002-0012) now all conform. **Next batch starts at Rafat poem 12 =
  `bulleh_shah_0013`** (English book p.61 → PDF p.81; Urdu p.60 → PDF p.80).

- 2026-07-04: SCHEMA CHANGE per rauf — added a THIRD translation slot. Parser
  (`src/abshaar/markdown_entry.py`) now maps `# Literal Translation` → literal_gloss
  (holds **Rafat's** English reference), NEW `# AI Translation` → ai_translation
  (**Claude's** own translation of the Urdu, created_by "ai"), and `# Literary
  Translation` → literary_translation (**left for rauf**). Template + scheduled task
  updated to this 3-slot layout. Entries 0002-0004 upgraded (Rafat moved to Literal
  Translation, my AI translation added, Literary = TODO). Unit tests pass; 12 records
  build clean, 3 translation kinds present. Entries 0005-0012 predate the AI slot
  (old cite-only layout) — the task now treats an entry as "done" only if it has an
  `# AI Translation` section, so the NEXT batch run re-processes/overwrites 0005-0012
  to the new layout (that is the next 8-poem batch), then continues at poem 12+.
  This SUPERSEDES the earlier cite-not-reproduce posture: Rafat's full English is now
  recorded in the Literal Translation slot, gated (publish/train = no), repo private.

- 2026-07-04 (batch run 2): Processed **Rafat poems 4-11 → entries `bulleh_shah_0005`
  through `_0012`** by vision-reading the rendered Nastaliq pages (PDF pp.62-79, plus
  76/77 to confirm poem 10's spillover). Urdu originals transcribed + project-latin
  transliteration; Rafat English **cited, not reproduced** (see Copyright posture change
  in Current state). Notable: poem 7 "A Safe Place" is only the famous couplet on the
  page; poem 10 "Spell" spans two spreads (book pp.54+56 / 55+57); poems 8 and 11 have
  hard calligraphy — several interior lines flagged HIGH-uncertainty for rauf's review.
  build-data + validate clean: 12 processed, 0 errors, 24 placeholder warnings (intentional).
  Temp PNGs deleted. Next batch starts at Rafat poem 12 = `bulleh_shah_0013`.

- 2026-07-04: LIVE TEST of the batch workflow succeeded (ran in-session). Transcribed
  Rafat poems 2 ("The Difference" = bulleh_shah_0003) and 3 ("Wayfarer, Arise" =
  bulleh_shah_0004) by vision-reading the page images; Urdu + transliteration +
  Rafat English recorded; build-data + validate clean (4 processed, 0 errors). The
  render→view→transcribe→entry→validate chain works. Corrected the scheduled-task
  page rule (blank pages exist between poems; use English=Contents page, Urdu=that−1,
  ignore blanks). Next batch run starts at Rafat poem 4 (bulleh_shah_0005).

- 2026-07-04: Created ad-hoc scheduled task `bulleh-shah-corpus-batch` (manual/
  on-demand; /Users/rauf/Claude/Scheduled/). Each run transcribes the next up-to-8
  Rafat poems by VISION-reading the rendered page images directly (no OCR engine
  needed — runs offline in-session), writes entries matching bulleh_shah_0002.md,
  builds + validates, and updates this log. ~9 runs to finish the 70 remaining
  poems; at 3-4 runs/day ≈ 2-3 days. NOTE: first run needs tool approvals ("Run
  now" to pre-approve) and confirms the scheduled env can render (pdftoppm) + view
  images. This is an alternative to the user's Mac VLM route — don't run both into
  the same IDs (the task skips existing bulleh_shah_XXXX to avoid dupes).

- 2026-07-04: Routing fix CONFIRMED by user test (English clean via Tesseract, poems
  separated). Urdu still noisy on UTRNet. Per user choice, added a local vision-LLM
  Urdu engine to `batch_ocr.py`: `--urdu-engine ollama` (default, model
  `qwen2.5vl:7b` via Ollama, offline) reads Nastaliq far better than the CRNN;
  `--urdu-engine utrnet` kept as fallback. English stays Tesseract. torch now
  optional (only for utrnet). Added `requests` dep. Next: user pulls the model and
  compares VLM vs CRNN on poem 1.

- 2026-07-04: TESTED on Rafat poems 1-3. Found UTRNet is **Urdu-only** — it turned
  the English pages into gibberish, so the single-engine run lumped all poems
  together and captured no English. FIX: `batch_ocr.py` now **routes by page** —
  even PDF pages -> UTRNet (Urdu original), odd -> Tesseract (English translation);
  needs `brew install tesseract` + `pip install pytesseract`. Verified here:
  Tesseract reads the English page cleanly and pairing now yields correct per-poem
  Urdu+English units. Urdu still needs the reviewer's correction pass (dropped
  alif, char swaps).

- 2026-07-04: Added page-pairing (`assemble_rafat_poems.py` — groups Urdu+English
  per poem via script detection, flags multi-page poems) and `--throttle`/`--limit`
  to `batch_ocr.py` for heat control; documented resource expectations in README_MAC.
- 2026-07-04: Evaluated UTRNet Urdu OCR app; built Mac setup (setup_mac.sh,
  requirements-mac.txt, batch_ocr.py, README_MAC.md). Could not run in sandbox
  (no network for torch). Handoff: user tests on Rafat pages on Mac.

- 2026-07-04: Inspected 3 PDFs. Identified Book C (Rafat) layout: 71 poems,
  typeset English + calligraphic Nastaliq Urdu facing pages. Confirmed English OCRs
  cleanly but Urdu is not machine-OCR-able (manual transcription only). Built
  `bulleh_shah_0002` ("A for Allah") end-to-end as proof. Added `source_rafat_selection`.
  Built page map for all 71. Asked user the 2 open decisions above.
- 2026-07-04 (earlier): Created pilot `bulleh_shah_0001` from Sufinama; Sufinama
  source + Bulleh Shah person records; drafted Sufinama permission email.
