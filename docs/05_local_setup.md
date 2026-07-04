# Local Setup Guide

This guide covers both **Windows (PowerShell)** and **macOS (zsh/bash)**. The
Python package and CLI (`abshaar`) are OS-agnostic; only the shell commands and
wrapper scripts differ. Windows steps assume the project lives at
`D:\Harvard\Poetry Model Project`; macOS steps assume it's been cloned to
`~/Harvard/Poetry Model Project` — adjust paths for your actual location.

## 1. Install Required Software

Install these first:

- Git: https://git-scm.com/
- Python 3.11 or 3.12: https://www.python.org/downloads/
- Node.js LTS: https://nodejs.org/
- VS Code: https://code.visualstudio.com/
- Ollama: https://ollama.com/

**macOS:** the easiest way to install most of these is [Homebrew](https://brew.sh):

```bash
brew install git python@3.12 node ollama
brew install --cask visual-studio-code
```

Optional but recommended for heavier ML work:

- Windows: WSL2 with Ubuntu, or NVIDIA GPU drivers and CUDA if you have an NVIDIA GPU.
- macOS: Apple Silicon (M-series) Macs run PyTorch's MPS backend for GPU
  acceleration out of the box — no separate driver install needed.
- Hugging Face account for gated model access where required (both platforms).

## 2. Confirm the Repository

**Windows (PowerShell):**

```powershell
cd "D:\Harvard\Poetry Model Project"
git status --short --branch
```

**macOS (zsh/bash):**

```bash
cd ~/Harvard/"Poetry Model Project"
git status --short --branch
```

If Git shows a branch name, the repository is initialized.

## 3. Create a Python Environment

**Windows (PowerShell):**

```powershell
cd "D:\Harvard\Poetry Model Project"
py -0p
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

`py -0p` shows which Python versions are installed. This project supports Python
3.11 or newer, so Python 3.12, 3.13, or 3.14 are also fine.

If PowerShell blocks activation, run:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Then activate again.

**macOS (zsh/bash):**

```bash
cd ~/Harvard/"Poetry Model Project"
python3 --version
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

If `python3 --version` shows something older than 3.11, install a newer one with
`brew install python@3.12` and use `python3.12 -m venv .venv` instead.

## 4. Install Python Dependencies

The core CLI (`init`, `status`, `new-entry`, `build-data`, `validate`,
`export-site`) has no dependencies — it only uses the standard library, so you
can skip this step entirely until you reach the AI/embedding stage.

When you're ready for local drafting, embeddings, or retrieval, install the
pinned stack from `requirements.txt` (same on Windows and macOS, identical to
the `ai` extra in `pyproject.toml`):

```bash
pip install -r requirements.txt
```

This installs `ollama`, `sentence-transformers`, `chromadb`, `transformers`,
and `torch` — expect a multi-GB download. On Apple Silicon Macs, the installed
torch build already supports the MPS GPU backend with no extra setup.

For future planned features not yet wired into the code (fine-tuning, a
FastAPI backend, tabular data handling), add packages as you build those
parts, e.g. `pip install peft accelerate bitsandbytes fastapi uvicorn pandas
pydantic rich`. Keep the first version simple and CPU-compatible where
possible; on Windows, some GPU training packages are easier through WSL2.

For lint/dev tooling (`ruff`), use:

```bash
pip install -r requirements-dev.txt
```

## 5. Install a Local LLM With Ollama

After installing Ollama:

```powershell
ollama pull qwen3:8b
ollama run qwen3:8b
```

If your computer struggles, try:

```powershell
ollama pull qwen3:4b
```

For stronger machines:

```powershell
ollama pull qwen3:14b
```

The local Ollama API usually runs at:

```text
http://localhost:11434
```

## 6. Translation Models

Use IndicTrans2 for supported Indic-to-English translation. The Hugging Face
model page may require accepting access conditions before downloading.

Model to start with:

```text
ai4bharat/indictrans2-indic-en-1B
```

Fallback:

```text
facebook/nllb-200-distilled-600M
```

Do not commit downloaded model files to Git. They belong in local caches or the
ignored `models/` folder.

## 7. Embeddings and Retrieval

Use BGE-M3 through `sentence-transformers`:

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("BAAI/bge-m3")
embeddings = model.encode(["sample text"])
```

Start by embedding:

- glossary entries;
- tashreeh notes;
- poet biographies;
- timeline events;
- reviewed poem translations.

## 8. Website Setup

When ready to create the website (same commands on Windows and macOS):

```bash
npm create astro@latest website
cd website
npm install
npm run dev
```

For GitHub Pages, add a GitHub Actions workflow later. Do not start with a
complex backend.

## 9. First Working Prototype

The first end-to-end prototype should do this:

1. Load one poem record from JSONL.
2. Run a baseline translation.
3. Retrieve glossary and context.
4. Ask the local LLM for tashreeh.
5. Save the output as a reviewable draft.
6. Let you edit the translation and explanation.
7. Store your review as structured JSON.

Once this works for five poems, scale to 20-50 poems.

## 10. Suggested Future Commands

These are not implemented yet, but this is the shape the CLI should eventually
have (identical on Windows and macOS once `abshaar` is installed or `PYTHONPATH`
points at `src`):

```bash
python -m abshaar ingest data/raw/public/kabir.txt
python -m abshaar translate --poem kabir_0001
python -m abshaar review --poem kabir_0001
python -m abshaar build-index
python -m abshaar export-site
```

Keep the commands boring and predictable. Future contributors should be able to
understand the project without becoming ML engineers first.
