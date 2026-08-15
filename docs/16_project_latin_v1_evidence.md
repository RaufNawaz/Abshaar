# 16 — project-latin-v1: Evidence Inventory and Decision Sheet

> Written 2026-08-15 (AI-drafted, for Rauf's review). This is NOT the
> transliteration standard — it is the measured state of current practice in
> the 72 entries plus the concrete decisions a `project-latin-v1` spec must
> make. Nothing here prescribes; the counts are from a mechanical scan of
> `data/processed/poems.jsonl` transliteration layers on 2026-08-15.

## 1. Measured current practice

**Two systems coexist, and most entries mix them.**

| Style | Entries | Examples |
|---|---|---|
| Plain doubled vowels only (`aa/ee/oo`) | 21 | 0001–0008 run |
| Macron/dot diacritics only (`ā ī ū ḍ ṭ ṛ`) | 14 | contiguous 0043–0051 run |
| **Mixed within one entry** | **37** | 0013–0026 and others |

The contiguous diacritic-only run (0043–0051) shows the convention drifted by
transcription session, not by poem type.

Character counts across all 72 transliteration layers:

- Long vowels: `aa` ×1361, `ee` ×205, `oo` ×127 versus `ā` ×583, `ī` ×271,
  `ū` ×60. (`ii`/`uu` essentially unused: 4 and 0.)
- Retroflexes: `ṛ` ×213, `ḍ` ×95, `ṭ` ×87 — but plain-style entries write the
  same consonants as bare `r/d/t`, indistinguishable from dentals.
- Nasals: **four different marks in use** — `ṅ` ×87, `ṉ` ×58, `ṁ` ×52,
  `ṇ` ×15 — plus bare `n`.
- ʿAin: marked `ʿ` ×12 and as a plain apostrophe (`'Ain te 'ghain…`) ×~8;
  most occurrences unmarked entirely.
- Aspiration digraphs (consistent and unambiguous): `kh` ×199, `gh` ×113,
  `ch` ×332, `chh` ×60, `sh` ×146, `th` ×91, `ph` ×47, `bh` ×115, `dh` ×77,
  `jh` ×88, `rh` ×12.
- Diphthongs: `ai` ×363, `au` ×63. Hyphens ×46; explicit izafat `-e-` ×4.
- `ḥ` ×5 and `ṣ` ×3 appear sporadically (Arabic-loan marking, not systematic).

## 2. Why this matters now

1. **Training data**: the transliteration task family (288 examples) currently
   teaches BOTH styles, inconsistently — a model trained on it will
   transliterate inconsistently too. Recorded as a known limitation in the
   plan §10 checklist.
2. **Search/matching**: `normalize_roman` strips diacritics, so matching
   tolerates the split — but glossary headwords, future user search, and any
   published text will surface the inconsistency directly.
3. **Review cost**: whichever standard is chosen, 37+ mixed entries need a
   normalization pass; doing it before human review of transliterations avoids
   reviewing text that will then be rewritten.

## 3. Decisions the spec must make (with the evidence-based default)

| # | Decision | Options | What current practice suggests |
|---|---|---|---|
| 1 | Long vowels | doubled (`aa`) / macrons (`ā`) | Doubled dominates by volume (1361 vs 583) and types faster; macrons are more scholarly. Volume favors doubled; the 0043–0051 run proves macrons were also deliberate. Rauf's call. |
| 2 | Retroflex ṭ/ḍ/ṛ | dots / unmarked / digraph | Dots are already used ×395 and carry real phonemic contrast in Punjabi; unmarked loses information that cannot be mechanically recovered. |
| 3 | Nasal marking | one mark (which?) / positional rules | Four marks in use is untenable; the spec must pick one (or bare `n` + explicit rules for ṇ). |
| 4 | ʿAin | `ʿ` / `'` / unmarked | ×12 vs ×8 vs mostly-unmarked. If letter-mysticism poems (0002!) depend on ain/ghain contrast, unmarked is lossy. |
| 5 | Aspiration | digraphs (current) | Already consistent — adopt as-is. |
| 6 | Izafat & compounds | `-e-` + hyphen rules | Only 4 uses; needs a rule either way. |
| 7 | Case | current mixed usage | Titles capitalize; lines vary. Needs one rule. |
| 8 | Arabic-loan marks (ḥ ṣ ẓ q) | mark / drop | Sporadic today (×8 total); decide once. |

## 4. Enforcement path (after Rauf decides)

Per the project's encode-invariants rule: add a `translit-lint` check that
scans transliteration layers for the rejected style's markers (e.g., macrons
if doubled wins) and fails validation; add a mechanical normalizer for the
bulk conversion; regenerate `poems.jsonl`, the KB, and the training set; and
record the spec as `docs/16` §5 (replacing this sheet's placeholder).

## 5. The spec (placeholder)

Not yet decided. When Rauf picks the options in §3, write the normative spec
here with examples from the five-poem review slice, then implement the linter
and normalizer in the same change.
