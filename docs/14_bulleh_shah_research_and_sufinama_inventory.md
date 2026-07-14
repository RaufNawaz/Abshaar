# Bulleh Shah Research and Sufinama Inventory

## Research purpose

This note records the first internet research pass on Bulleh Shah's life,
historical context, textual transmission, and the non-kaafi material listed on
Sufinama. It deliberately separates conventional biography, later tradition,
modern scholarly inference, official shrine information, and catalog metadata.

## Main historical finding

The safest biographical conclusion is that the traditional outline is clearer
than its details. Bulleh Shah is conventionally identified as Abdullah Shah,
dated around 1680 to 1757 or 1758, associated with Kasur, and linked to Shah
Inayat Qadiri of Lahore. Birthplace, exact dates, education, family episodes,
meeting stories, and formal Sufi-order status are not securely documented.

Ashna Hussain's 2018 Western Sydney University thesis is especially useful
because it states the methodological problem directly: most biography is
reconstructed from later sources and the poetry itself, while different
religious and intellectual traditions produce different portraits. It also
argues that performance helped preserve the poetry while encouraging variation,
recombination, and uncertain attribution. This supports Abshaar's decision to
store source witnesses separately and cluster variants only after review.

## Sourced biographical outline

| Topic | Working conclusion | Confidence |
|---|---|---|
| Name | Conventionally Abdullah Shah; poetic name Bulleh/Bullhe Shah | Medium-high |
| Dates | c. 1680-1757 is conventional; 1758 also appears | Medium |
| Birthplace | Disputed between Uch Gillanian/Bahawalpur and Pandoke/Qasur traditions | Low-medium |
| Childhood | Later accounts place the family in Pandoke and his father at the mosque | Medium-low |
| Education | Later sources place higher study in Kasur and infer Arabic/Persian/Islamic learning | Medium |
| Murshid | Strong association with Shah Inayat Qadiri of Lahore | High relative to other life details |
| Qadiri identity | Commonly inferred through Shah Inayat; direct formal documentation not conclusive | Medium |
| Death/burial | Conventional death in 1757/58; shrine and commemoration in Kasur | Medium-high |
| Corpus | No definitive corpus; oral/performance transmission created variants and attribution problems | High as a scholarly caution |

Claim-level details are in
`data/context/biographical_claims.jsonl`; the cautious timeline is in
`data/context/events.jsonl`; the person summary is in
`data/context/people.jsonl`.

## Sufinama content inventory

Sufinama's Bulleh Shah “All” page reported these categories on 2026-07-12:

| Category | Reported count | Current Abshaar status |
|---|---:|---|
| Kaafi | 76 | Full authorized witness acquisition complete |
| Kalaam | 3 | Normalized source witnesses acquired; overlaps require review |
| Doha | 23 | All inline UUID/line/token witnesses acquired |
| Shabad | 7 | Normalized source witnesses acquired; titles overlap known kafis |
| Dohra | 12 | Normalized source witnesses acquired; keep distinct from doha |
| Athvara | 1 | Normalized source witness acquired |
| Barahmasa | 1 | Normalized source witness acquired |
| Holi | 1 | Normalized source witness acquired; overlaps a kaafi |
| Sufi Quotes | 24 reported | Editorial English layer; count discrepancy (one page showed 21) |
| E-book | 1 | Navigation metadata only; page fetch failed |
| Video | 164 | Performance/reception media, not unique poems |
| Blog | 1 reported | Category page exposed no identifiable article |
| Profile | 1 | Used in biographical research with cautions |

These numbers must not be added together as unique works. At minimum, the Holi
item overlaps a kaafi, the seven shabad titles resemble known kafis, and the
three kalaam items include works already present in other corpus layers. The
inventory is therefore stored as category-level source metadata in
`data/context/sufinama_bulleh_shah_inventory.jsonl`.

On 2026-07-13, the authorized collector acquired all 48 records in those seven
textual categories without changing the 72 working Markdown entries. The source
served 47 records with Devanagari, 8 with Urdu, and 7 with both Roman layers;
41 of 144 requested language views were unavailable at source and 0 were fetch
or parse errors. These are source-category records, not 48 newly established
compositions. The normalized witnesses, catalog, cache audit, and separate
crosswalk are documented in `docs/12_sufinama_source_ingestion.md`.

## Sources consulted

- [Ashna Hussain, *Politics, Poetry and Pluralism: Bulleh Shah in the Late Mughal Empire* (Western Sydney University, 2018)](https://researchers.westernsydney.edu.au/en/studentTheses/politics-poetry-and-pluralism-bulleh-shah-in-the-late-mughal-empi/)
- [Sufinama: Profile of Bulleh Shah](https://sufinama.org/poets/bulleh-shah/profile)
- [Sufinama: All works/content for Bulleh Shah](https://sufinama.org/poets/bulleh-shah/all)
- [Government of Punjab Auqaf: Hazrat Baba Bulleh Shah, Kasur](https://auqaf.punjab.gov.pk/shrine-baba-bulleh-shah)

## Next research and acquisition steps

1. Review the 48-record non-kaafi crosswalk and the 76-record kaafi crosswalk;
   assign exact/variant/excerpt/possible/unmatched relationships without
   overwriting source text.
2. Deduplicate only through reviewed `canonical_work_id` relationships. Keep the
   original Sufinama category on every record.
3. Keep Sufinama's English quotes separate as editorial translations/excerpts;
   do not treat them as Bulleh Shah's English text.
4. Acquire bibliographic metadata for the one e-book and article/blog before
   considering any full-text use.
5. Use the 164 video records later as performance/reception metadata, with
   performer, platform, and composition links—not as 164 unique works.
6. Seek earlier biographical and textual sources cited by modern scholarship,
   especially nineteenth-century tazkira/hagiographical works and Faqir Muhammad
   Faqir's critical corpus work, while preserving their genre and distance from
   Bulleh Shah's lifetime.
