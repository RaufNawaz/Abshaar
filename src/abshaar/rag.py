"""Retrieval-augmented grounded answering over the knowledge base.

The vector index is a rebuildable cache (data/cache/chroma/, gitignored); the
knowledge base JSONL remains canonical. Heavy dependencies are imported inside
functions so the stdlib-only CLI commands stay importable without the .venv.

Answer rules are strict: only retrieved records may be used, every claim needs
a [kb:...] citation, uncertainty qualifiers must be reproduced, and a question
whose best retrieval score is below the threshold is declined rather than
answered from model priors. A cited kb id that was not retrieved is an error.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from abshaar.jsonl import read_jsonl
from abshaar.knowledge_base import KB_PATH
from abshaar.ollama_client import run_ollama_chat


INDEX_DIR = "data/cache/chroma"
COLLECTION_NAME = "abshaar_kb"
EMBED_MODEL = "BAAI/bge-m3"
DEFAULT_MIN_SCORE = 0.35
CITATION_RE = re.compile(r"\[(kb:[^\]\s]+)\]")

SYSTEM_PROMPT = """You are the answering layer of Abshaar, a private scholarly archive on Bulleh Shah.

Rules, in priority order:
1. Answer ONLY from the numbered records provided. Never use outside knowledge, even when you are confident.
2. Cite the record id in square brackets, e.g. [kb:bulleh_shah_0002:original], after each claim.
3. If a record carries uncertainty, dispute, or evidence qualifiers, reproduce that qualification in your answer. Never turn a disputed claim into a settled fact.
4. If the records do not contain the answer, say exactly that: the archive does not currently contain this information. Do not guess.
5. Quote original-language text exactly as written in the records.
Write plainly and precisely."""


def _embedder(model_name: str = EMBED_MODEL):
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(model_name)


def _collection(root: Path, create: bool = False):
    from chromadb import PersistentClient

    client = PersistentClient(path=str(root / INDEX_DIR))
    if create:
        try:
            client.delete_collection(COLLECTION_NAME)
        except Exception:
            pass
        return client.create_collection(COLLECTION_NAME, metadata={"hnsw:space": "cosine"})
    return client.get_collection(COLLECTION_NAME)


def build_index(root: Path, model_name: str = EMBED_MODEL, batch_size: int = 32) -> int:
    records = read_jsonl(root / KB_PATH)
    model = _embedder(model_name)
    collection = _collection(root, create=True)
    for start in range(0, len(records), batch_size):
        batch = records[start : start + batch_size]
        embeddings = model.encode(
            [record["text"] for record in batch], normalize_embeddings=True
        )
        collection.add(
            ids=[record["id"] for record in batch],
            embeddings=[list(map(float, embedding)) for embedding in embeddings],
            documents=[record["text"] for record in batch],
            metadatas=[
                {
                    "kind": record["kind"],
                    "poem_ids": ",".join(record.get("poem_ids", [])),
                    "canonical_work_id": record.get("canonical_work_id", ""),
                    "rights": record.get("rights", ""),
                    "trainable": bool(record.get("trainable")),
                    "uncertainty": bool(record.get("uncertainty")),
                }
                for record in batch
            ],
        )
    manifest = {"embed_model": model_name, "records": len(records)}
    (root / INDEX_DIR / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    return len(records)


def retrieve(root: Path, query: str, k: int = 8) -> list[dict[str, Any]]:
    manifest_path = root / INDEX_DIR / "manifest.json"
    model_name = EMBED_MODEL
    if manifest_path.exists():
        model_name = json.loads(manifest_path.read_text(encoding="utf-8")).get(
            "embed_model", EMBED_MODEL
        )
    model = _embedder(model_name)
    collection = _collection(root)
    embedding = model.encode([query], normalize_embeddings=True)
    result = collection.query(
        query_embeddings=[list(map(float, embedding[0]))],
        n_results=k,
        include=["documents", "metadatas", "distances"],
    )
    hits: list[dict[str, Any]] = []
    for kb_id, document, metadata, distance in zip(
        result["ids"][0], result["documents"][0], result["metadatas"][0], result["distances"][0]
    ):
        hits.append(
            {
                "id": kb_id,
                "text": document,
                "metadata": metadata,
                "score": round(1.0 - float(distance), 4),
            }
        )
    return hits


def compose_prompt(question: str, hits: list[dict[str, Any]]) -> str:
    blocks = []
    for index, hit in enumerate(hits, start=1):
        uncertainty = " [carries uncertainty qualifiers]" if hit["metadata"].get("uncertainty") else ""
        blocks.append(
            f"Record {index} — id {hit['id']} (kind: {hit['metadata'].get('kind')}, "
            f"score {hit['score']}){uncertainty}:\n{hit['text']}"
        )
    records_text = "\n\n".join(blocks)
    return f"Question: {question}\n\nRecords:\n\n{records_text}"


def validate_citations(answer: str, hits: list[dict[str, Any]]) -> list[str]:
    """Return cited kb ids that were NOT among the retrieved records."""
    retrieved = {hit["id"] for hit in hits}
    return sorted({cited for cited in CITATION_RE.findall(answer) if cited not in retrieved})


def ask(
    root: Path,
    question: str,
    model: str = "qwen3:8b",
    k: int = 8,
    min_score: float = DEFAULT_MIN_SCORE,
    retrieve_only: bool = False,
) -> dict[str, Any]:
    hits = retrieve(root, question, k=k)
    best = hits[0]["score"] if hits else 0.0
    if retrieve_only:
        return {"question": question, "hits": hits, "answer": None, "declined": False, "invalid_citations": []}
    if not hits or best < min_score:
        return {
            "question": question,
            "hits": hits,
            "answer": (
                "The archive does not currently contain material matching this question "
                f"(best retrieval score {best} < threshold {min_score})."
            ),
            "declined": True,
            "invalid_citations": [],
        }
    answer = run_ollama_chat(model, SYSTEM_PROMPT, compose_prompt(question, hits))
    # qwen3 emits <think>…</think> reasoning blocks; only the final answer counts.
    answer = re.sub(r"<think>.*?</think>", "", answer, flags=re.S).strip()
    return {
        "question": question,
        "hits": hits,
        "answer": answer,
        "declined": False,
        "invalid_citations": validate_citations(answer, hits),
    }
