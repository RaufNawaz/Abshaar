"""LLM paraphrase augmentation for the templated training set (plan Phase 3).

Only QUESTIONS are paraphrased; answers stay verbatim corpus text, so the
generator cannot inject facts. A separate verifier model must confirm each
paraphrase asks the same thing; rejects are dropped and counted. Augmented
examples then pass the same gates as the base set (leak scan, dedup against
originals + each other, hedging audit) before being appended to train.jsonl.
Eval.jsonl is never augmented.

The chat function is injected so tests can stub it; the CLI wires local
Ollama. Do not run this against live models without explicit user go-ahead.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Callable

from abshaar.dataset_gen import TRAINING_DIR, run_gates
from abshaar.jsonl import read_jsonl, write_jsonl


ChatFn = Callable[[str, str, str], str]

THINK_RE = re.compile(r"<think>.*?</think>", re.S)

GENERATOR_SYSTEM = (
    "You rewrite questions. Reply with ONLY the rewritten question, nothing else."
)
GENERATOR_PROMPT = (
    "Rewrite this question in different words. Keep the meaning EXACTLY the same, "
    "including any quoted text, names, and script samples (copy those verbatim).\n\n{question}"
)
VERIFIER_SYSTEM = "You compare two questions. Reply with only YES or NO."
VERIFIER_PROMPT = (
    "Do these two questions ask for exactly the same information?\n\n"
    "Question A: {original}\n\nQuestion B: {paraphrase}\n\nReply YES or NO."
)

# Families whose questions embed source-script text are excluded: a paraphrase
# that mangles the embedded original would corrupt the pair.
AUGMENTABLE_FAMILIES = {"tashreeh", "term", "theme", "biography", "honesty", "identification"}


def _clean(reply: str) -> str:
    return THINK_RE.sub("", reply).strip().strip('"')


def augment_training_data(
    root: Path,
    chat: ChatFn,
    generator_model: str,
    verifier_model: str,
    per_family_limit: int = 30,
) -> tuple[dict[str, Any], list[str]]:
    train_path = root / TRAINING_DIR / "train.jsonl"
    train = read_jsonl(train_path)
    eval_set = read_jsonl(root / TRAINING_DIR / "eval.jsonl")

    picked: dict[str, int] = {}
    augmented: list[dict[str, Any]] = []
    rejected = 0

    for example in train:
        family = example["task_family"]
        if family not in AUGMENTABLE_FAMILIES or picked.get(family, 0) >= per_family_limit:
            continue
        picked[family] = picked.get(family, 0) + 1
        original_question = example["messages"][1]["content"]

        paraphrase = _clean(
            chat(generator_model, GENERATOR_SYSTEM, GENERATOR_PROMPT.format(question=original_question))
        )
        if not paraphrase or paraphrase == original_question:
            rejected += 1
            continue
        verdict = _clean(
            chat(
                verifier_model,
                VERIFIER_SYSTEM,
                VERIFIER_PROMPT.format(original=original_question, paraphrase=paraphrase),
            )
        )
        if not verdict.upper().startswith("YES"):
            rejected += 1
            continue

        augmented.append(
            {
                **example,
                "id": f"ex_aug_{family}_{len(augmented):05d}",
                "messages": [
                    example["messages"][0],
                    {"role": "user", "content": paraphrase},
                    example["messages"][2],
                ],
                "generator": f"paraphrase:{generator_model}|verify:{verifier_model}",
            }
        )

    if not augmented:
        return {"attempted": sum(picked.values()), "kept": 0, "rejected": rejected}, []

    combined_train = [*train, *augmented]
    poems = read_jsonl(root / "data" / "processed" / "poems.jsonl")
    reference_texts = [
        t.get("text", "")
        for poem in poems
        for t in poem.get("translations", [])
        if isinstance(t, dict) and t.get("kind") == "reference_translation"
    ]
    failures = run_gates([*combined_train, *eval_set], combined_train, eval_set, reference_texts)
    if failures:
        return {}, failures

    write_jsonl(train_path, combined_train)
    attempted = sum(picked.values())
    rejection_rate = rejected / attempted if attempted else 0.0
    stats = {
        "attempted": attempted,
        "kept": len(augmented),
        "rejected": rejected,
        "rejection_rate": round(rejection_rate, 3),
        "train_total": len(combined_train),
    }
    if rejection_rate > 0.30:
        stats["warning"] = (
            "rejection rate above 30% — stop and inspect generator prompts before scaling up"
        )
    return stats, []
