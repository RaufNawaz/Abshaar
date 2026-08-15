"""Phase 2 gate: grounded-answering smoke test over the live index.

Run from the repo root with the project venv:
    .venv/bin/python scripts/rag_smoke_test.py [--model qwen3:8b]

Requires: build-kb + build-index done, Ollama serving the chosen model.
Exits non-zero if any check fails. Checks per the plan (docs/15 §3 Phase 2):
- 10 in-corpus questions retrieve their expected records,
- the birthplace answer preserves the dispute qualifier,
- 2 out-of-corpus questions are declined (or answered as not-in-archive),
- no answer cites a kb id that was not retrieved.

This is a Python script (cross-platform by itself); no .sh/.ps1 pair needed.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from abshaar.rag import ask  # noqa: E402


IN_CORPUS = [
    ("What does the letter Alif teach in Bulleh Shah's kafi 'A for Allah'?", "bulleh_shah_0002"),
    ("Where was Bulleh Shah born?", "bio_claim"),
    ("Who was Bulleh Shah's murshid or spiritual guide?", "bio_claim"),
    ("What is the refrain of the kafi 'Ranjha Ranjha kardi'?", "bulleh_shah_0001"),
    ("Which poem of Bulleh Shah mocks scholars and book-learning?", "bulleh_shah_0035"),
    ("What does the term nuqta mean in Bulleh Shah's poetry?", "term_nuqta"),
    ("What happens in Bulleh Shah's spinning-wheel poems?", "bulleh_shah_00"),
    ("When did Bulleh Shah die?", "bio_claim"),
    ("In which poems does Bulleh Shah speak as Heer or about Ranjha?", "bulleh_shah_00"),
    ("What themes about the ego and its annihilation appear in Bulleh Shah's poetry?", "theme_"),
]

OUT_OF_CORPUS = [
    "What did Bulleh Shah write about railway trains?",
    "What is the capital of France?",
]

DECLINE_RE = re.compile(
    r"does not currently contain|not in the (archive|corpus)|no (record|material|information)",
    re.I,
)
DISPUTE_RE = re.compile(r"disput|uncertain|conventional|later sources|not definitive|debated", re.I)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="qwen3:8b")
    parser.add_argument("--k", type=int, default=8)
    args = parser.parse_args()

    failures: list[str] = []

    for index, (question, expected_fragment) in enumerate(IN_CORPUS, start=1):
        result = ask(REPO_ROOT, question, model=args.model, k=args.k)
        hit_ids = " ".join(hit["id"] for hit in result["hits"])
        print(f"[{index:02d}] {question}")
        print(f"     best={result['hits'][0]['score'] if result['hits'] else 0} "
              f"declined={result['declined']} invalid_citations={result['invalid_citations']}")
        if expected_fragment not in hit_ids:
            failures.append(f"Q{index}: expected a record containing `{expected_fragment}` among hits")
        if result["declined"]:
            failures.append(f"Q{index}: declined an in-corpus question")
        if result["invalid_citations"]:
            failures.append(f"Q{index}: invented citations {result['invalid_citations']}")
        if index == 2 and result["answer"] and not DISPUTE_RE.search(result["answer"]):
            failures.append("Q2: birthplace answer lost the dispute qualifier")

    for offset, question in enumerate(OUT_OF_CORPUS, start=len(IN_CORPUS) + 1):
        result = ask(REPO_ROOT, question, model=args.model, k=args.k)
        declined = result["declined"] or bool(result["answer"] and DECLINE_RE.search(result["answer"]))
        print(f"[{offset:02d}] {question}")
        print(f"     declined={declined}")
        if not declined:
            failures.append(f"Q{offset}: out-of-corpus question was answered instead of declined")
        if result["invalid_citations"]:
            failures.append(f"Q{offset}: invented citations {result['invalid_citations']}")

    if failures:
        print("\nSMOKE TEST FAILED:")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    print("\nSMOKE TEST PASSED: 12/12 checks clean.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
