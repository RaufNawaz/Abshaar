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
| 1 | Long vowels | doubled (`aa`) / macrons (`ā`) | Doubled dominates by volume (1361 vs 583) and types faster; macrons are more scholarly. Volume favors doubled; the 0043–0051 run proves macrons were also deliberate. Rauf's call. | I would prefered macrons but doubled is also fine
| 2 | Retroflex ṭ/ḍ/ṛ | dots / unmarked / digraph | Dots are already used ×395 and carry real phonemic contrast in Punjabi; unmarked loses information that cannot be mechanically recovered. | use dots as they are part of the language 
| 3 | Nasal marking | one mark (which?) / positional rules | Four marks in use is untenable; the spec must pick one (or bare `n` + explicit rules for ṇ). | use whatever makes it most true to the language of punjabi 
| 4 | ʿAin | `ʿ` / `'` / unmarked | ×12 vs ×8 vs mostly-unmarked. If letter-mysticism poems (0002!) depend on ain/ghain contrast, unmarked is lossy. | use the symbols of aaiin and ghaiin 
| 5 | Aspiration | digraphs (current) | Already consistent — adopt as-is. | yes use dots and diagraphs 
| 6 | Izafat & compounds | `-e-` + hyphen rules | Only 4 uses; needs a rule either way. | yes izafat is fine and use yphenated e or whatever is appropriate
| 7 | Case | current mixed usage | Titles capitalize; lines vary. Needs one rule. | titles capitalize but other than that it can be mixed 
| 8 | Arabic-loan marks (ḥ ṣ ẓ q) | mark / drop | Sporadic today (×8 total); decide once. | mark 

## 4. Enforcement path — IMPLEMENTED 2026-08-15

Per the project's encode-invariants rule: `lint_translit_v1` in
`src/abshaar/translit.py` reports rejected-style markers (doubled vowels,
legacy nasal marks, apostrophe-ain) as validation warnings on every
`validate` run; `normalize-translit --apply` performed the bulk conversion of
all 72 entries (dry-run is the default); `poems.jsonl`, the KB, and the
training set were regenerated in the same change. The normative spec is §5
below.

## 5. The spec — project-latin-v1 (decided 2026-08-15)

Decisions from Rauf's §3 answers plus his follow-up choices (macron nasal
glyph; keep retroflex ṇ; full loan marking; sentence-case applied but mixed
case tolerated). Implemented by `src/abshaar/translit.py`
(`normalize-translit` CLI, dry-run by default) and linted as validation
warnings; all 72 entries were normalized on 2026-08-15.

| Feature | Rule | Examples |
|---|---|---|
| Long vowels | macrons: `ā ī ū` (never `aa/ee/oo`) | `āwe`, `sīs`, `hū` |
| Short vowels | plain `a i u e o` | `dil`, `na` |
| Diphthongs | `ai`, `au` | `mai`, `aulād` |
| Retroflexes | dots: `ṭ ḍ ṛ ṇ` | `ṭikāna`, `jehṛa`, `paṇī` |
| Nasalization | `n̄` (n + combining macron above, U+0304) | `main̄` |
| Ordinary n | plain `n` | `nāl` |
| Aspiration | digraphs: `kh gh ch chh jh th dh ph bh` | `khabar`, `bhī` |
| ʿAin | `ʿ` (U+02BF) | `ʿAin`, `ʿishq` |
| Ġain (غ) | `ġ` (U+0121) | `ġain` |
| Arabic loans | full marking is the TARGET: `ḥ ṣ ẓ ṭ ẕ q` etc. | `ḥaq`, `ṣūrat` |
| Izafat | `-e-` | `Āl-e-Nabi` |
| Case | line starts capitalized (mechanical); mixed case tolerated, titles capitalized; case is NOT lint-enforced | |

**Mechanical vs review scope (critical honesty note):** the normalizer only
converts what is certain — style conversion (`aa→ā`), legacy nasal marks
(`ṅ ṁ ṉ → n̄`), apostrophe-ain in letter names, and `ghain→ġain` as a letter
name. It CANNOT add marks the text lacks: unmarked ʿain in ordinary words,
unmarked loan consonants (`h` that should be `ḥ`, `s`→`ṣ`, `z`→`ẓ/ẕ`,
`t`→`ṭ` for ط), or retroflex flaps written plain, because those require
reading the Urdu original word-by-word. Full loan marking therefore converges
through the normal review process; the spec defines the target, not the
current coverage. A single short `i`/`u` also stays short even where the
scholarly reading may be long (`kāi`, not `kāī`) — length beyond the source
style's own signals is a review judgment.

**Matching stability:** `normalize_roman` in `source_matching.py` is
style-invariant (`ā`≡`aa`→`a`, `ī`≡`ee`→`i`, `ū`≡`oo`→`u`; `ʿ` dropped), so
witness matching and exact-line detection survive the migration and any
future style edits.

**Known residuals, deliberately untouched:** `á` ×3 (ambiguous, flagged for
review), `ii` ×4, and the mixed velar-nasal cases (`ṅ` before `g`, now `n̄g`)
which a reviewer may prefer as plain `ng`.
