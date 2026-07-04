# Text Entry and Transliteration Workflow

This project should not ask contributors to type long poems directly into JSONL.
JSONL is good for machines, but Markdown is better for human entry and review.

Recommended workflow:

1. Type or paste the original poem into a Markdown entry file.
2. Add transliteration in Latin script.
3. Add literal gloss.
4. Add literary translation.
5. Add tashreeh.
6. Add glossary terms and source notes.
7. Review the entry.
8. Convert the reviewed entry into JSONL later.

## Which Scripts Go Where

Store scripts separately. Do not replace the original script with
transliteration.

| Field | What Goes Here |
| --- | --- |
| `original_text` | The poem in its source script, such as Shahmukhi, Gurmukhi, Perso-Arabic, Devanagari, or another source script. |
| `transliteration` | Latin-script pronunciation guide typed by you. |
| `literal_gloss` | Plain English meaning, close to the original. |
| `literary_translation` | Readable English translation. |
| `tashreeh` | Explanation of meaning, metaphor, cultural context, and alternate readings. |

For Bulleh Shah, the most likely source scripts are:

- Shahmukhi/Perso-Arabic script for Punjabi;
- Gurmukhi script if using a Gurmukhi source;
- Urdu/Perso-Arabic for Urdu or Persian-influenced materials;
- Latin transliteration for readers who cannot read the original script.

## Best File Format for Manual Entry

Use one Markdown file per poem while drafting:

```text
data/working/bulleh_shah_0001.md
data/working/bulleh_shah_0002.md
data/working/bulleh_shah_0003.md
```

Why Markdown first:

- easier to type multiline poetry;
- easier to review in GitHub;
- fewer quote/comma escaping problems than JSON;
- can hold source notes, questions, and review comments;
- can later be converted to JSONL for model use.

## Encoding Rule

All files should be saved as UTF-8.

In VS Code:

1. Look at the bottom-right encoding label.
2. It should say `UTF-8`.
3. If not, click it.
4. Choose `Save with Encoding`.
5. Select `UTF-8`.

This allows Punjabi, Urdu, Persian, Hindi, Braj, Arabic-derived scripts, and
diacritics to live in the same repository.

## Keyboard Setup

On Windows, add keyboards through:

```text
Settings -> Time & language -> Language & region -> Add a language
```

On macOS, add keyboards through:

```text
System Settings -> Keyboard -> Input Sources -> Add Input Source
```

Useful keyboards:

- Punjabi for Gurmukhi;
- Urdu (Pakistan) for Urdu/Shahmukhi-style Perso-Arabic entry;
- Persian for Persian text;
- Hindi for Devanagari/Braj sources.

You can also paste source text from a reliable source, but only if the source is
public-domain, permission-cleared, or allowed by license.

## Recommended Transliteration Style

Start with a simple project transliteration instead of trying to solve every
scholarly system on day one.

Rules for `project-latin-v1`:

- write in plain Latin characters;
- preserve repeated sounds consistently;
- avoid decorative diacritics at first;
- prioritize readability for English-speaking learners;
- add pronunciation notes when needed;
- keep original script as the authority.

Example policy:

```text
Original script: authoritative
Transliteration: reading aid
Literal gloss: meaning aid
Literary translation: English poem/prose rendering
Tashreeh: explanation and interpretation
```

If later you want a formal scholarly transliteration system, add it as a second
field rather than overwriting the first.

## Manual Entry Template

Use this structure for each poem:

```markdown
---
id: bulleh_shah_0001
poet_id: bulleh_shah
title: "[first line or working title]"
work_type: "kafi_or_selected_stanza"
source_ids:
  - source_bulleh_0001
rights_status: "verify_before_publication"
review_status: "draft"
---

# Original

[Paste or type original source-script text here.]

# Transliteration

[Type Latin transliteration here.]

# Literal Gloss

[Plain English gloss, line by line.]

# Literary Translation

[Readable English translation.]

# Tashreeh

[Explain metaphor, cultural context, metaphysical meaning, and ambiguity.]

# Key Terms

- ishq:
- murshid:
- haq:

# Themes

- divine_love
- ritual_critique

# Source Notes

[Where did the original text come from? What is the license/status?]

# Review Notes

[Questions, uncertainties, alternate readings, corrections.]
```

## Line-by-Line Entry

For poetry, preserve line boundaries. A good entry can use this pattern:

```markdown
# Original

Line 1 in original script
Line 2 in original script

# Transliteration

Line 1 transliteration
Line 2 transliteration

# Literal Gloss

Line 1: literal gloss
Line 2: literal gloss

# Literary Translation

Line 1 English rendering
Line 2 English rendering
```

This makes alignment easier later.

## How This Becomes JSONL

The Markdown file is the human working format. Later, a script should parse it
into:

```text
data/processed/poems.jsonl
```

The JSONL record should preserve:

- original text;
- script label;
- transliteration;
- line segmentation;
- literal gloss;
- literary translation;
- tashreeh;
- source notes;
- review status.

## Quality Checks Before Publishing

Before a poem is marked publishable:

- original source is verified;
- text is saved as UTF-8;
- line breaks are preserved;
- script is labeled;
- transliteration is complete;
- literal gloss is separate from literary translation;
- tashreeh is separate from translation;
- glossary terms are linked;
- uncertainties are marked;
- no copyrighted material is published without permission.

## Practical Recommendation

For the first 20 Bulleh Shah entries, do everything manually in Markdown. Do not
start with automation. Once the pattern feels stable, create a parser that
converts the Markdown entries into JSONL for the model pipeline and website.
