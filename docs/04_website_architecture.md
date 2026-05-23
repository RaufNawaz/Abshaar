# Website Architecture

The website should be a public archive and learning environment first. AI chat is
valuable, but it should sit on top of a strong, browsable corpus.

## Inspiration From Ajab Shahar

Ajab Shahar is useful as an editorial reference because it organizes mystic
poetry through songs, couplets, words, people, reflections, and related pathways.
The project map describes a rich archive of poems, songs, original language,
transliteration, translations, word meanings, people, and reflections.

Abshaar should learn from that structure but add:

- deeper tashreeh for beginner readers;
- poet-specific concept maps;
- interactive historical timelines;
- transparent model-assisted translation workflow;
- source-grounded questions and answers;
- visible uncertainty and alternate readings.

## Recommended Stack

Use a static-first website:

- Astro for content-heavy static pages;
- TypeScript for data safety;
- React islands for interactive timeline and reader controls;
- Markdown/MDX for essays and poet pages;
- JSON generated from `data/processed/` for poems and glossary;
- Pagefind or MiniSearch for static search;
- GitHub Actions for deployment to GitHub Pages.

Why this stack:

- free public hosting on GitHub Pages;
- low maintenance;
- content contributors can edit Markdown/JSON;
- interactive features can be added only where needed;
- the site remains usable without a paid backend.

## Main Pages

### Home

Purpose: invite users directly into the archive, not a marketing page.

Components:

- featured poet;
- featured work;
- theme entry points;
- search;
- latest reviewed translations.

### Poet Page

Purpose: make the poet's world intelligible.

Components:

- short biography;
- timeline;
- map of places if useful;
- major themes;
- language/script notes;
- works list;
- glossary terms associated with this poet;
- recommended reading path.

### Work Page

Purpose: make one poem readable at multiple levels.

Components:

- original text;
- transliteration toggle;
- literal gloss;
- literary translation;
- tashreeh;
- glossary sidebar;
- context notes;
- related works;
- source and license;
- review status.

Reader controls:

- show/hide transliteration;
- show literal/literary side by side;
- beginner/advanced explanation toggle;
- highlight glossary terms;
- copy citation.

### Timeline

Purpose: show how the poet's intellectual and personal world develops.

Timeline event types:

- life event;
- historical event;
- intellectual influence;
- composition or oral tradition;
- manuscript/publication/recording event;
- later reception.

### Themes

Purpose: let readers approach ideas directly.

Example themes:

- divine unity;
- ritual critique;
- love and annihilation;
- longing and separation;
- guru/murshid;
- caste and social order;
- body as metaphor;
- death and impermanence;
- language and names of God.

Each theme page should include:

- short explanation;
- key terms;
- relevant poems;
- poet comparisons;
- beginner questions.

### Ask Page

Purpose: answer reader questions about the poet's ideas.

First version:

- curated FAQ;
- search over poems, glossary, and tashreeh;
- cited answers written by humans or reviewed model outputs.

Later versions:

- browser-local WebLLM mode;
- optional self-hosted backend with FastAPI, Ollama, and a vector database.

## Chatbot Options

### Option A: Static FAQ and Search

Best first release.

Pros:

- free on GitHub Pages;
- fast;
- safe;
- easy for contributors;
- no API keys.

Cons:

- not a true open-ended chatbot.

### Option B: Browser-Local AI

Use WebLLM to run the model in the user's browser.

Pros:

- no server;
- private;
- open-source;
- can be hosted as a static site.

Cons:

- requires WebGPU support;
- model downloads can be large;
- quality depends on the user's device.

### Option C: Separate AI Backend

Use FastAPI plus Ollama plus a vector database.

Pros:

- best chatbot experience;
- can use stronger models;
- easy to log reviewable outputs.

Cons:

- not free unless hosted on donated infrastructure;
- requires maintenance;
- GitHub Pages cannot provide this backend by itself.

Recommended order:

1. Static archive and search.
2. Static FAQ generated from reviewed corpus.
3. Optional local backend for maintainers.
4. Public chatbot later, only if sustainable.

## Backend API for Optional Chat

If a backend is added later, keep it small:

```text
POST /api/translate-draft
POST /api/explain
POST /api/ask
POST /api/review
GET  /api/poems/{id}
GET  /api/search?q=
```

Every answer from `/api/ask` should return:

- answer text;
- cited poem IDs;
- cited glossary terms;
- retrieved context snippets;
- confidence level;
- uncertainty notes.

## Website MVP Checklist

- Astro project created in `website/`;
- GitHub Pages deployment works;
- at least one poet page;
- at least five poem pages;
- one timeline;
- glossary term highlighting;
- search;
- source/credits page;
- contribution page.

Do not build the full AI chat UI before the poem pages are strong. The archive is
the foundation.
