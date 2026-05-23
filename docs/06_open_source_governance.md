# Open Source and Governance

This project is a public-service archive, so trust matters as much as model
quality.

## Licenses

Recommended default:

- code: MIT or Apache-2.0;
- project documentation: CC BY 4.0;
- original public-domain texts: mark as public domain with source;
- human translations and tashreeh: CC BY-SA 4.0;
- private notes and copyrighted material: do not publish.

Before the first public release, add:

- `LICENSE`;
- `CONTRIBUTING.md`;
- `CODE_OF_CONDUCT.md`;
- `CITATION.cff`;
- source and attribution page.

## Contribution Types

Accept contributions in small, reviewable units:

- source correction;
- transliteration correction;
- translation suggestion;
- tashreeh suggestion;
- glossary entry;
- timeline event;
- source citation;
- bug report;
- website improvement.

Every content contribution should include:

- contributor name or handle;
- source;
- license status;
- confidence level;
- notes on uncertainty.

## Review Roles

Suggested roles:

- maintainer: approves repository changes;
- language reviewer: checks source language and transliteration;
- interpretation reviewer: checks tashreeh and cultural context;
- technical reviewer: checks model pipeline and website;
- source reviewer: checks citation and license status.

The same person can hold multiple roles at the beginning.

## Model Transparency

Every model-generated output should record:

- model name;
- model version or tag;
- prompt template version;
- retrieval context IDs;
- date generated;
- reviewer status;
- whether it is safe to publish.

Readers should be able to distinguish:

- original text;
- human translation;
- model draft;
- reviewed model-assisted translation;
- commentary;
- speculation or alternate interpretation.

## Data Ethics

Avoid extracting community knowledge without reciprocity. If singers, teachers,
scholars, or community members contribute, credit them clearly and respect usage
limits.

For oral traditions:

- record performer/source consent;
- distinguish performer variation from textual error;
- do not treat one printed version as the only authentic version;
- preserve region, genre, and performance context where known.

## Public Roadmap

Keep a public roadmap with these milestones:

1. Corpus MVP.
2. Local translation assistant.
3. Static website prototype.
4. Reviewed glossary.
5. Timeline explorer.
6. Static FAQ/search.
7. Optional local chatbot.
8. Fine-tuned model release, only when data quality is strong enough.

The project should stay legible. A future contributor should be able to open the
repo, read the docs, run the local prototype, and add one poem without needing to
understand the entire ML stack.
