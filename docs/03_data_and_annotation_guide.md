# Data and Annotation Guide

The dataset is the heart of the project. A good dataset lets the model retrieve,
explain, and improve. A weak dataset will make even a strong model sound shallow.

## Data Principles

- Store the original text, not only the English.
- Keep transliteration separate from translation.
- Keep literal translation separate from literary translation.
- Keep tashreeh separate from both.
- Track source, license, editor, reviewer, and confidence for every entry.
- Prefer phrase-level annotation over word-by-word flattening.
- Let the same word have different meanings for different poets.
- Mark uncertainty openly.

## Repository Data Layout

Recommended structure:

```text
data/
  raw/
    public/
    private/
  processed/
    poems.jsonl
  annotations/
    reviews.jsonl
  lexicon/
    terms.jsonl
  context/
    people.jsonl
    events.jsonl
    themes.jsonl
    sources.jsonl
  cache/
```

Use `data/raw/private/` for texts, scans, or notes that cannot be published.
That folder is ignored by Git.

## Poem Record Schema

Each line in `data/processed/poems.jsonl` should be one JSON object:

```json
{
  "id": "kabir_0001",
  "poet_id": "kabir",
  "title": "Working title or first line",
  "work_type": "couplet",
  "source": {
    "name": "Source name",
    "url": "https://example.org/source",
    "license": "public-domain",
    "notes": "Edition, manuscript, oral source, or uncertainty"
  },
  "original": {
    "text": "[original text here]",
    "script": "Devanagari/Gurmukhi/Shahmukhi/Perso-Arabic/Latin",
    "language_spans": [
      {
        "text": "[span]",
        "language": "Braj/Punjabi/Urdu/Persian/Hindi/unknown",
        "confidence": 0.8
      }
    ]
  },
  "transliteration": {
    "scheme": "project-latin-v1",
    "text": "[transliteration here]"
  },
  "segmentation": [
    {
      "segment_id": "kabir_0001_l1",
      "text": "[line 1]",
      "role": "line"
    }
  ],
  "translations": [
    {
      "kind": "literal_gloss",
      "text": "[literal gloss]",
      "created_by": "human/model",
      "model": null,
      "status": "draft"
    },
    {
      "kind": "literary_translation",
      "text": "[literary translation]",
      "created_by": "human/model",
      "model": null,
      "status": "draft"
    }
  ],
  "tashreeh": [
    {
      "audience": "beginner",
      "text": "[explanation]",
      "status": "draft"
    }
  ],
  "glossary_terms": ["term_ishq", "term_guru"],
  "themes": ["divine_unity", "ritual_critique"],
  "review": {
    "status": "needs_review",
    "reviewer": null,
    "confidence": null
  }
}
```

## Glossary Term Schema

Each line in `data/lexicon/terms.jsonl` should be one JSON object:

```json
{
  "id": "term_ishq_bulleh_shah",
  "headword": "ishq",
  "script_forms": ["[Urdu/Punjabi/Persian forms here]"],
  "transliteration": "ishq",
  "languages": ["Persian", "Urdu", "Punjabi"],
  "basic_meaning": "love",
  "poet_specific_meaning": "Divine longing that dissolves ego and social rank.",
  "do_not_flatten_to": ["romantic love"],
  "related_terms": ["fana", "murshid", "haqiqat"],
  "example_poems": ["bulleh_0003"],
  "sources": ["source_0001"],
  "review_status": "draft"
}
```

The `do_not_flatten_to` field is important. It teaches future contributors and
models that a dictionary equivalent is often not enough.

## Review Schema

Each line in `data/annotations/reviews.jsonl` should capture one review event:

```json
{
  "id": "review_0001",
  "poem_id": "kabir_0001",
  "output_id": "run_2026_05_23_001",
  "reviewer": "Rauf",
  "scores": {
    "source_fidelity": 4,
    "metaphor_fidelity": 3,
    "poet_specific_context": 2,
    "literary_quality": 4,
    "beginner_clarity": 5
  },
  "problems": [
    {
      "type": "missed_context",
      "note": "The model treated the well as a physical image only."
    }
  ],
  "corrected_translation": "[your corrected translation]",
  "corrected_tashreeh": "[your corrected explanation]",
  "style_note": "Preserve the concrete image before explaining the metaphysics.",
  "created_at": "2026-05-23"
}
```

## Annotation Rules

Use these rules when you review outputs:

- Do not replace concrete imagery too quickly with abstract theology.
- Preserve the poet's tone: playful, piercing, intimate, rebellious, devotional,
  satirical, or ecstatic.
- Explain metaphors after the reader has seen the metaphor.
- Avoid claiming that one interpretation is the only correct one unless the
  source tradition strongly supports that claim.
- Mark alternate readings when a line can support more than one serious reading.
- Keep religious vocabulary precise. Do not collapse Ram, Allah, haq, guru,
  murshid, pir, naam, shabad, and ishq into generic spirituality.
- Track oral-performance context separately from printed-text context.

## First Gold Dataset

Build a gold dataset before expanding:

- 20 short works with full human translation and tashreeh;
- 20 glossary terms with poet-specific meanings;
- 10 timeline events;
- 10 themes;
- 10 source notes;
- 50 question-answer pairs grounded in the corpus.

This is enough to prototype retrieval, translation prompting, website pages, and
evaluation.

## Copyright and Source Safety

Original works by classical poets may be public domain, but modern editions,
translations, annotations, recordings, and website metadata may not be.

Safe sources:

- public-domain editions;
- your own translations;
- your own annotations;
- permission-cleared material;
- small bibliographic metadata with attribution;
- source links and citations.

Avoid:

- copying modern translations into training data without permission;
- scraping entire websites;
- uploading copyrighted scans;
- mixing private notes into public JSON files.
