#!/usr/bin/env python3
"""Resumable build-index.

`abshaar build-index` embeds all 1,306 knowledge-base records in one pass and
writes `manifest.json` only at the end, so an interrupted run leaves a partial
Chroma collection that cannot be re-added to (duplicate ids) and has to be
thrown away. On this M4 Air that is ~45 minutes of BGE-M3 encoding to lose.

This does the same work, but asks the collection which ids it already holds and
embeds only the remainder. Killing it costs at most one batch.

    ./.venv/bin/python scripts/build_index_resumable.py [--batch-size 32]

Same embedding model, same normalisation, same metadata and same manifest as
`src/abshaar/rag.py`, so the two are interchangeable -- this one can finish a
run the other one started.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from abshaar.rag import COLLECTION_NAME, EMBED_MODEL, INDEX_DIR, _embedder  # noqa: E402
from abshaar.knowledge_base import KB_PATH  # noqa: E402
from abshaar.jsonl import read_jsonl  # noqa: E402


def get_or_create(root: Path):
    """Open the collection WITHOUT destroying it.

    rag.py's `_collection(create=True)` calls `delete_collection` first, which
    is correct for a clean rebuild and fatal for a resume -- it would drop the
    very embeddings this script exists to keep.
    """
    from chromadb import PersistentClient

    client = PersistentClient(path=str(root / INDEX_DIR))
    return client.get_or_create_collection(
        COLLECTION_NAME, metadata={"hnsw:space": "cosine"}
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch-size", type=int, default=32)
    ap.add_argument("--model", default=EMBED_MODEL)
    args = ap.parse_args()

    records = read_jsonl(ROOT / KB_PATH)
    collection = get_or_create(ROOT)

    existing = set(collection.get(include=[])["ids"])
    todo = [r for r in records if r["id"] not in existing]
    print(f"knowledge base: {len(records)} records")
    print(f"already embedded: {len(existing)}")
    print(f"to do: {len(todo)}", flush=True)

    if todo:
        model = _embedder(args.model)
        for start in range(0, len(todo), args.batch_size):
            batch = todo[start : start + args.batch_size]
            embeddings = model.encode(
                [r["text"] for r in batch], normalize_embeddings=True
            )
            collection.add(
                ids=[r["id"] for r in batch],
                embeddings=[list(map(float, e)) for e in embeddings],
                documents=[r["text"] for r in batch],
                metadatas=[
                    {
                        "kind": r["kind"],
                        "poem_ids": ",".join(r.get("poem_ids", [])),
                        "canonical_work_id": r.get("canonical_work_id", ""),
                        "rights": r.get("rights", ""),
                        "trainable": bool(r.get("trainable")),
                        "uncertainty": bool(r.get("uncertainty")),
                    }
                    for r in batch
                ],
            )
            done = len(existing) + start + len(batch)
            print(f"  {done}/{len(records)}", flush=True)

    final = len(collection.get(include=[])["ids"])
    if final != len(records):
        print(f"REFUSING to write manifest: {final} embedded, {len(records)} expected", file=sys.stderr)
        return 1

    (ROOT / INDEX_DIR / "manifest.json").write_text(
        json.dumps({"embed_model": args.model, "records": len(records)}, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"manifest written: {final} records")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
