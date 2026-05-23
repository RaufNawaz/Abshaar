# Project Roadmap

This project should be built as an archive and annotation system first, then as
an AI system. The model will only become good if the corpus, metadata, and human
feedback are good.

## Phase 0: Define the First Scope

Time estimate: 1-2 weeks.

Choose a narrow first version:

- one poet, preferably Kabir, Bulleh Shah, Shah Hussain, Waris Shah, or Baba
  Farid;
- 20-50 short works;
- one primary source for original text;
- one accepted transliteration standard;
- one translation style guide;
- one review rubric.

Decisions to make before collecting data:

- What scripts will be stored? Example: Urdu in Perso-Arabic, Punjabi in
  Gurmukhi/Shahmukhi where available, transliteration in Latin.
- Which source texts are public domain or permission-cleared?
- Will the first release include only your translations, or also public-domain
  historical translations?
- Which license will be used for code and annotations?

Recommended default:

- code license: MIT or Apache-2.0;
- original public-domain text: mark source and public-domain status;
- your translations and tashreeh: CC BY-SA 4.0, so future users can improve and
  reuse while preserving attribution.

## Phase 1: Build the Corpus MVP

Time estimate: 2-4 weeks.

Create a small but high-quality dataset before touching fine-tuning.

Minimum files:

- `data/raw/public/`: original public-domain or permission-cleared text;
- `data/processed/poems.jsonl`: normalized poem records;
- `data/annotations/reviews.jsonl`: human review notes;
- `data/lexicon/terms.jsonl`: poet-specific meanings of recurring terms;
- `data/context/people.jsonl`: poets, teachers, singers, commentators;
- `data/context/events.jsonl`: historical and biographical timeline events;
- `data/context/themes.jsonl`: themes such as ishq, tauhid, fana, virah,
  maya, guru, caste, ritual, death, longing.

For each poem, store:

- original text;
- source and license;
- poet;
- approximate date or tradition;
- language/script spans;
- transliteration;
- literal gloss;
- literary translation;
- tashreeh;
- important metaphors;
- glossary links;
- review status.

Do not start with hundreds of poems. Start with a small gold-standard set.
Twenty deeply annotated poems are more valuable than 2,000 weakly processed ones.

## Phase 2: Build the Local AI Pipeline

Time estimate: 3-5 weeks.

The first model pipeline should be modular:

1. Segment the poem into lines, couplets, refrains, and repeated phrases.
2. Detect language/script spans.
3. Generate a literal baseline translation.
4. Retrieve poet context, glossary entries, and related annotated examples.
5. Generate a literary translation.
6. Generate tashreeh separately from the translation.
7. Generate reader notes: metaphors, cultural references, religious terms,
   alternate readings.
8. Run a self-check against the source and retrieved context.
9. Save the output for human review.

Keep each step visible. The model should never silently overwrite the original,
the literal gloss, or the human-approved translation.

## Phase 3: Human Review Loop

Time estimate: ongoing from week 4.

For every generated translation, store your feedback in a structured format:

- `too_literal`: what was flattened;
- `missed_context`: what cultural or metaphysical context was missed;
- `incorrect_claim`: what was factually or doctrinally wrong;
- `better_translation`: your corrected version;
- `better_tashreeh`: your corrected explanation;
- `style_note`: how the tone should change;
- `confidence`: reviewer confidence from 1 to 5.

This becomes the core asset of the project. It is how the system learns your
interpretive preferences without becoming rigid.

## Phase 4: Evaluation Before Fine-Tuning

Time estimate: 2 weeks for first version.

Create a gold evaluation set of 50-100 passages. For each passage, compare model
output against a human-reviewed target using this rubric:

- Source fidelity: does it preserve what the original says?
- Metaphor fidelity: does it preserve the conceptual image?
- Poet-specific meaning: does it use this poet's sense of key terms?
- Cultural grounding: does it explain context without overclaiming?
- Literary quality: does the English read as poetry/prose-poetry rather than
  machine output?
- Humility: does it mark uncertainty and alternate readings?
- Usefulness for beginners: can a new reader understand the stakes?

Use numeric scores, but also keep prose comments. The prose comments matter more
for improvement.

## Phase 5: Fine-Tune Only After Enough Data

Time estimate: after 500-2,000 reviewed examples.

Do not train from scratch. Do not fine-tune too early.

Recommended progression:

1. Prompting plus retrieval.
2. Few-shot examples from your reviewed corpus.
3. LoRA or QLoRA fine-tuning on your translation and tashreeh style.
4. Preference tuning later, if you have pairs of weak output vs corrected output.

Fine-tuning should teach style, format, and interpretive habits. It should not be
used as the only place where knowledge lives. Poet context should remain in the
retrievable corpus, where it can be inspected and corrected.

## Phase 6: Website MVP

Time estimate: 3-6 weeks after corpus MVP.

The first public website should be static and free to host on GitHub Pages.

Minimum pages:

- poet profile;
- interactive timeline;
- works index;
- poem page with original, transliteration, translation, tashreeh, and glossary;
- theme explorer;
- source and credits page;
- contribution guide.

The chatbot should not be the first public feature. Build search and curated
question pages first. A fully open, free chatbot can be added later through
client-side WebLLM or a separate self-hosted local backend.

## Phase 7: Public Contribution System

Time estimate: after first website release.

Accept contributions through pull requests or structured forms:

- new source text;
- correction to transliteration;
- alternate translation;
- glossary entry;
- timeline event;
- source citation;
- reviewer note.

Each contribution should include source information and license status. The
project should prefer fewer verified entries over many uncertain ones.

## Phase 8: Long-Term Vision

Once the system works for one poet, expand carefully:

1. Add a second poet with a different vocabulary and metaphysical world.
2. Compare how the same word changes across poets.
3. Add dialect and script variation.
4. Build a public dictionary from reviewed glossary entries.
5. Add audio recitation and oral-performance notes where permission allows.
6. Add a teacher mode for classrooms and reading groups.

The end goal is not just translation. It is a living, inspectable, community-run
interpretive archive.
