# Model Strategy

This should be an AI-assisted translation system, not a single standalone model
trained from scratch. The strongest open-source path is a modular pipeline:
translation model, interpretive LLM, retrieval system, human feedback, and later
small fine-tunes.

## Short Answer: AI App First, ML Training Later

Build an AI app first:

- it runs locally;
- it uses existing open-source/open-weight models;
- it stores every human correction;
- it retrieves poet-specific context before generating;
- it makes uncertainty visible.

Train or fine-tune later, once you have enough reviewed examples.

Training from scratch would require huge datasets, specialized GPUs, and a large
budget. It would also perform worse than adapting existing models. For this
project, your unique value is the curated corpus, glossary, explanations, and
human feedback.

## Recommended Model Stack

For a complete command-level setup and integration guide, see the standalone
LaTeX implementation manual:
`docs/07_step_by_step_implementation_guide.tex`.

### Baseline Translation

Use IndicTrans2 first for supported Indic languages.

Why:

- it is built specifically for Indic translation;
- it supports all 22 scheduled Indian languages;
- it includes Punjabi, Urdu, Hindi, Sanskrit, Sindhi, and others;
- the model card is MIT licensed;
- AI4Bharat provides training and fine-tuning scripts.

Important limitation:

- it does not solve Persian, Braj Bhasha, dialect mixtures, or mystical
  interpretation by itself;
- it should produce a literal or semantic baseline, not the final translation.

Fallback: use NLLB-200 for broader multilingual coverage. It is useful for
cross-lingual baselines, especially where IndicTrans2 does not cover the source
well. It should still be reviewed carefully for poetry.

### Interpretive LLM

Use Qwen3 locally through Ollama for the first prototype.

Why:

- strong multilingual instruction following;
- Apache-2.0 model license on Hugging Face for Qwen3 models;
- available in small and medium sizes;
- easy local serving through Ollama;
- good fit for explanation, rewriting, comparison, and structured output.

Suggested local tiers:

- laptop with 16 GB RAM: `qwen3:4b` or `qwen3:8b`;
- laptop/desktop with 32 GB RAM: `qwen3:8b` or `qwen3:14b`;
- strong GPU machine: `qwen3:30b` or larger;
- high-quality but heavier alternative: Gemma 3 12B/27B;
- avoid making Llama 3.3 the default because its model card lists only a small
  supported language set and uses a custom license, even though it can be useful
  for English reasoning on powerful hardware.

### Retrieval Model

Use BGE-M3 embeddings for retrieval.

Why:

- multilingual;
- supports long passages;
- MIT licensed;
- works with local Python tooling;
- better suited than English-only embeddings for Urdu/Punjabi/Persian-influenced
  materials.

Store embeddings locally in Chroma, SQLite with a vector extension, or another
small local vector store. For the first version, Chroma is acceptable because it
is easy to use. If you want the simplest long-term static website path, keep
canonical data in JSONL and treat the vector database as a generated cache.

### Fine-Tuning Tools

Use LoRA or QLoRA, not full fine-tuning.

Recommended tools:

- Hugging Face Transformers and PEFT for explicit control;
- Axolotl for YAML-driven training pipelines;
- Unsloth if you want faster local fine-tuning and a friendlier path.

Fine-tune only after the review dataset is large enough. A realistic first
threshold is 500 reviewed examples. A stronger threshold is 2,000+ examples.

## Pipeline Design

The translation pipeline should have separate outputs:

1. literal gloss;
2. direct translation;
3. literary translation;
4. tashreeh;
5. glossary notes;
6. alternate readings;
7. uncertainty notes;
8. citations to retrieved context.

This prevents the model from hiding interpretation inside translation.

## Creativity Control

Use different settings for different tasks:

- language/script detection: deterministic;
- literal translation: low temperature;
- glossary extraction: low temperature;
- tashreeh: medium temperature;
- literary translation: medium temperature;
- alternate readings: medium-high temperature, but clearly marked as alternate.

Never ask for "the best translation" in one step. Use a staged prompt:

1. What does the line literally say?
2. What are the culturally loaded words?
3. How has this poet used these terms elsewhere?
4. What metaphysical reading is plausible?
5. What is uncertain?
6. Now produce a readable English translation.
7. Now produce a beginner-friendly tashreeh.

## What the Model Should Learn From You

The system should learn:

- your preferred English style;
- how much explanation is enough;
- when to preserve an original term instead of translating it;
- how to handle ambiguity;
- how to separate Sikh, Sufi, Bhakti, Islamic, Hindu, and folk contexts without
  collapsing them into one generic spirituality;
- which metaphors should stay concrete and which need explanation.

It should not learn to hallucinate authority. Every major claim should be tied to
a source, a glossary note, or clearly marked as interpretation.

## Website Chatbot Reality Check

A GitHub Pages website cannot run a normal server-side chatbot by itself.

There are three realistic options:

1. Static search and FAQ: free, fast, reliable, best first public version.
2. Browser-local AI with WebLLM: no server, but users need WebGPU-capable devices
   and may download large model files.
3. Separate backend: FastAPI plus Ollama plus vector database. This gives the
   best chatbot but requires hosting or a machine left running.

Recommended order:

1. Launch static website with rich search and curated questions.
2. Add optional local AI mode for advanced users.
3. Add hosted chatbot only if you later have funding or donated infrastructure.

## Key Sources Checked

- AI4Bharat IndicTrans2: https://github.com/AI4Bharat/IndicTrans2
- IndicTrans2 Hugging Face model card: https://huggingface.co/ai4bharat/indictrans2-indic-en-1B
- Hugging Face NLLB docs: https://huggingface.co/docs/transformers/en/model_doc/nllb
- Qwen3 model card: https://huggingface.co/Qwen/Qwen3-8B
- Ollama Qwen3 page: https://ollama.com/library/qwen3
- BGE-M3 model card: https://huggingface.co/BAAI/bge-m3
- WebLLM: https://github.com/mlc-ai/web-llm
- PEFT LoRA docs: https://huggingface.co/docs/peft/en/developer_guides/lora
- Axolotl docs: https://docs.axolotl.ai/
