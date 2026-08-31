"""Training-data factory: chat-format instruction examples from the corpus.

Core principle: the corpus already contains every answer (translations,
tashreeh, terms, claims), so the base dataset is TEMPLATED mechanically and
deterministically — no LLM in the loop, nothing invented, every example
traceable to kb record ids. An optional LLM paraphrase pass can diversify
question phrasings later; it must re-run the same gates.

Gates (all fatal):
1. No example shares an 8-gram with a copyrighted reference translation.
2. Dedup on normalized user text.
3. Examples built from uncertain records must hedge in the answer.
4. Train/eval split is by canonical work cluster; zero overlap.
"""

from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from abshaar.clusters import cluster_map
from abshaar.jsonl import read_jsonl, write_jsonl
from abshaar.knowledge_base import KB_PATH
from abshaar.training_export import (
    UNCERTAINTY_RE,
    build_reference_index,
    find_leaks,
    normalize_words,
)


@dataclass(frozen=True)
class GenerationPolicy:
    """What the generator is allowed to draw on.

    Defaults reproduce the original conservative behaviour exactly, so
    nothing changes for a caller that does not ask. Each flag opens one
    specific gate and is documented where it is enforced.
    """

    # Emit Taufiq Rafat's reference translations and skip the leak scan whose
    # purpose is to catch them. Rauf stated on 2026-08-31 that he holds
    # explicit permission. Publishing is unaffected: export.py still strips
    # them from the public site export.
    include_reference_translations: bool = False

    # Build examples from the Sufinama witness records. They are already in
    # the knowledge base and marked trainable; until now nothing consumed
    # them. Their crosswalk classifications are an AI first pass carrying
    # human_confirmed: false -- accepted deliberately, not overlooked.
    include_witnesses: bool = False

    # Cross-view pairs per witness text. 79 texts carry 3+ aligned views, so
    # the ceiling is 516 ordered pairs; taking all of them would make script
    # conversion roughly half the dataset. 0 means no cap.
    witness_pairs_per_text: int = 2

    # Keep the eval split. Setting this False trains on every example and
    # leaves eval.jsonl empty -- only for a final production run AFTER the
    # recipe has been validated, since it destroys the ability to measure.
    holdout: bool = True

    @classmethod
    def unrestricted(cls, witness_pairs_per_text: int = 2, holdout: bool = True) -> "GenerationPolicy":
        return cls(
            include_reference_translations=True,
            include_witnesses=True,
            witness_pairs_per_text=witness_pairs_per_text,
            holdout=holdout,
        )

    def describe(self) -> list[str]:
        return [
            f"- Reference (Rafat) translations: {'INCLUDED' if self.include_reference_translations else 'excluded (leak-scanned)'}",
            f"- Sufinama witnesses: {'INCLUDED' if self.include_witnesses else 'excluded'}"
            + (f", up to {self.witness_pairs_per_text or 'all'} cross-view pair(s) per text" if self.include_witnesses else ""),
            f"- Eval holdout: {'kept (cluster-disjoint)' if self.holdout else 'DISABLED — every example is in train; eval.jsonl is empty'}",
        ]


WITNESS_VIEW_LABELS = {
    "roman_plain": "plain Roman transliteration",
    "roman_diacritic": "diacritic Roman transliteration",
    "urdu": "Urdu script",
    "devanagari": "Devanagari script",
}

TRAINING_DIR = "data/processed/training"
EVAL_WORK_MODULUS = 10  # every Nth poem-bearing cluster (sorted) is held out
HEDGE_NOTE = "Note: parts of the underlying record carry uncertain readings flagged for review."

SYSTEM_PROMPT = (
    "You are Abshaar, a scholarly assistant on the Punjabi Sufi poet Bulleh Shah. "
    "Answer from your studied corpus. Preserve uncertainty and dispute qualifiers "
    "exactly; when the corpus does not contain an answer, say so plainly instead of guessing."
)

# Full-line italic notes are editorial attributions, not poem content.
_ATTRIBUTION_LINE_RE = re.compile(r"(?:\n|^)_[^_\n]+_\s*$")

FALSE_PREMISE_TOPICS = [
    "railway trains",
    "the telephone",
    "the city of Islamabad",
    "cricket matches",
    "the British Raj",
    "airplanes",
    "the printing press in Lahore",
    "coffee houses",
    "photography",
    "the partition of 1947",
    "electricity",
    "newspapers",
    "the telegraph",
    "steamships",
    "banks and paper currency",
    "the East India Company",
    "bicycles",
    "modern universities",
    "the radio",
    "motor cars",
    "factories and mills",
    "postage stamps",
    "the canal colonies",
    "vaccination",
    "the game of chess between empires",
]

FAKE_TITLES = [
    "The Nightingale of Kasur",
    "Ode to the Ravi Bridge",
    "The Merchant's Lament",
    "Song of the Forty Saints",
    "The Golden Spinning Top",
    "Elegy for the Emperor",
    "The Boatman of Panjnad",
    "Forty Days in the Desert",
    "The Weaver's Last Thread",
    "Hymn to the Morning Star",
]

MISATTRIBUTED_WORKS = [
    "the romance Heer Ranjha as a complete epic",
    "the Japji Sahib",
    "the qawwali 'Dama Dam Mast Qalandar' as his own composition",
    "the Shahnameh",
    "the Masnavi of Rumi",
    "the Sassi Punnun epic",
]

OUT_OF_SCOPE_QUESTIONS = [
    "What is the capital of France?",
    "How do I fix a Python import error?",
    "Who won the last cricket world cup?",
    "What is the boiling point of water at altitude?",
    "Recommend a good restaurant in Boston.",
    "Write me a marketing plan for a coffee shop.",
    "What are the side effects of aspirin?",
    "Summarize the plot of Hamlet.",
    "How far is the moon from the earth?",
    "Translate 'good morning' into Japanese.",
    "What's the best laptop to buy this year?",
    "Explain how a car engine works.",
]


def strip_attribution_notes(text: str) -> str:
    previous = None
    while previous != text:
        previous = text
        text = _ATTRIBUTION_LINE_RE.sub("", text).rstrip()
    return text.strip()


def _pick(templates: list[str], index: int) -> str:
    return templates[index % len(templates)]


def _first_line(text: str) -> str:
    for line in text.splitlines():
        if line.strip():
            return line.strip()
    return ""


def _hedged(answer: str, uncertain: bool) -> str:
    if uncertain and not UNCERTAINTY_RE.search(answer) and "uncertain" not in answer.lower():
        return f"{answer}\n\n{HEDGE_NOTE}"
    return answer


def build_examples(root: Path, policy: GenerationPolicy | None = None) -> list[dict[str, Any]]:
    policy = policy or GenerationPolicy()
    kb = {record["id"]: record for record in read_jsonl(root / KB_PATH)}
    poems = read_jsonl(root / "data" / "processed" / "poems.jsonl")
    works = cluster_map(root)
    titles = {str(p["id"]): str(p.get("title", "")) for p in poems}
    examples: list[dict[str, Any]] = []

    def add(
        family: str,
        question: str,
        answer: str,
        kb_ids: list[str],
        poem_ids: list[str],
        uncertain: bool,
        work_id: str | None = None,
    ) -> None:
        if not question.strip() or not answer.strip():
            return
        anchor = poem_ids[0] if poem_ids else ""
        examples.append(
            {
                "id": f"ex_{family}_{len(examples):05d}",
                "task_family": family,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": question.strip()},
                    {"role": "assistant", "content": _hedged(answer.strip(), uncertain)},
                ],
                "kb_ids": kb_ids,
                "poem_ids": poem_ids,
                "canonical_work_id": work_id or works.get(anchor, ""),
                "generator": "template_v1",
                "uncertainty": uncertain,
            }
        )

    for index, poem in enumerate(sorted(poems, key=lambda p: str(p["id"]))):
        poem_id = str(poem["id"])
        title = titles[poem_id]
        original = poem.get("original", {}).get("text", "")
        transliteration = poem.get("transliteration", {}).get("text", "")

        translations = {
            t.get("kind"): strip_attribution_notes(t.get("text", ""))
            for t in poem.get("translations", [])
            if isinstance(t, dict) and t.get("trainable") is True
        }
        tashreeh_items = [
            strip_attribution_notes(t.get("text", ""))
            for t in poem.get("tashreeh", [])
            if isinstance(t, dict) and t.get("trainable") is True
        ]
        uncertain = bool(UNCERTAINTY_RE.search(original)) or any(
            UNCERTAINTY_RE.search(text) for text in [transliteration, *translations.values(), *tashreeh_items]
        )

        best_translation = translations.get("literary_translation") or translations.get("ai_translation") or ""

        # Rafat's rendering is a *published human* translation of the same
        # poem, so it gets its own family and its own question wording rather
        # than competing with the drafted translation for the same prompt --
        # two different answers to one question would be contradictory
        # training signal, and would trip the dedup gate besides.
        reference_translation = ""
        if policy.include_reference_translations:
            for translation in poem.get("translations", []):
                if isinstance(translation, dict) and translation.get("kind") == "reference_translation":
                    reference_translation = strip_attribution_notes(translation.get("text", ""))
                    break
        if original and reference_translation:
            add(
                "reference_translation",
                _pick(
                    [
                        f"Give the published English reference translation of these lines by Bulleh Shah:\n\n{original}",
                        f"How has this kafi of Bulleh Shah been rendered in published English translation?\n\n{original}",
                    ],
                    index,
                ),
                reference_translation,
                [f"kb:{poem_id}:original"],
                [poem_id],
                uncertain,
            )
        if original and best_translation:
            question = _pick(
                [
                    f"Translate this Bulleh Shah original into English:\n\n{original}",
                    f"Render the following kafi of Bulleh Shah in English:\n\n{original}",
                    f"Give an English translation of these lines by Bulleh Shah:\n\n{original}",
                ],
                index,
            )
            add("translation", question, best_translation, [f"kb:{poem_id}:original"], [poem_id], uncertain)

        if original and transliteration:
            add(
                "transliteration",
                _pick(
                    [
                        f"Transliterate this Shahmukhi text into Latin script:\n\n{original}",
                        f"Provide a Roman transliteration of these lines:\n\n{original}",
                    ],
                    index,
                ),
                transliteration,
                [f"kb:{poem_id}:original", f"kb:{poem_id}:transliteration"],
                [poem_id],
                uncertain,
            )
            add(
                "transliteration",
                f"Write the following transliterated Punjabi lines in Shahmukhi script:\n\n{transliteration}",
                original,
                [f"kb:{poem_id}:original", f"kb:{poem_id}:transliteration"],
                [poem_id],
                uncertain,
            )

        for tashreeh in tashreeh_items:
            add(
                "tashreeh",
                _pick(
                    [
                        f'Give a tashreeh (interpretive explanation) of Bulleh Shah\'s "{title}".',
                        f'Explain the meaning and context of the kafi "{title}" by Bulleh Shah.',
                        f'What is Bulleh Shah saying in "{title}"? Explain in depth.',
                    ],
                    index,
                ),
                tashreeh,
                [f"tash_{poem_id}_beginner"],
                [poem_id],
                uncertain,
            )

        first_roman = _first_line(transliteration)
        if first_roman and title:
            add(
                "identification",
                f"Which work of Bulleh Shah opens with the line: \"{first_roman}\"?",
                f'That is the opening of "{title}" ({poem_id} in the Abshaar archive).',
                [f"kb:{poem_id}:transliteration"],
                [poem_id],
                False,
            )
            add(
                "identification",
                f'What is the opening line of Bulleh Shah\'s "{title}"?',
                f'It opens: "{first_roman}".',
                [f"kb:{poem_id}:transliteration"],
                [poem_id],
                False,
            )

    for index, (kb_id, record) in enumerate(sorted(kb.items())):
        kind = record["kind"]
        if kind == "term":
            headword = record["text"].split(".", 1)[0].removeprefix("Term:").strip()
            add(
                "term",
                _pick(
                    [
                        f"What does the term \"{headword}\" mean in Bulleh Shah's poetry?",
                        f"Explain Bulleh Shah's use of \"{headword}\".",
                        f"How should \"{headword}\" be understood (and not be flattened) in Bulleh Shah?",
                    ],
                    index,
                ),
                record["text"],
                [kb_id],
                record.get("poem_ids", []),
                bool(record.get("uncertainty")),
            )
        elif kind == "theme":
            label = record["text"].split(".", 1)[0].removeprefix("Theme:").strip()
            poem_list = ", ".join(
                f'"{titles.get(p, p)}" ({p})' for p in record.get("poem_ids", [])
            )
            if poem_list:
                add(
                    "theme",
                    f"Which poems of Bulleh Shah express the theme of {label.lower()}?",
                    f"In the Abshaar archive, the theme \"{label}\" appears in: {poem_list}.",
                    [kb_id],
                    record.get("poem_ids", []),
                    False,
                )
        elif kind == "biographical_claim":
            claim_body = record["text"].split("): ", 1)[-1].split(".")[0].strip()
            add(
                "biography",
                _pick(
                    [
                        f"What does the historical record say about this aspect of Bulleh Shah's life: {claim_body}?",
                        f"What is known — and how securely — about this point in Bulleh Shah's biography: {claim_body}?",
                    ],
                    index,
                ),
                record["text"],
                [kb_id],
                [],
                True,
            )
        elif kind == "event":
            event_body = record["text"].split("): ", 1)[-1].split(".")[0].strip()
            add(
                "biography",
                f"What does the archive record about this event in Bulleh Shah's history: {event_body}?",
                record["text"],
                [kb_id],
                [],
                bool(record.get("uncertainty")),
            )
        elif kind == "cluster_relation":
            member_list = record["text"].split("): ", 1)[-1].rstrip(".")
            add(
                "variant_awareness",
                f"Are these records the same work of Bulleh Shah or different works: {member_list}?",
                record["text"],
                [kb_id],
                record.get("poem_ids", []),
                bool(record.get("uncertainty")),
            )

    if policy.include_witnesses:
        by_stem: dict[str, dict[str, tuple[str, dict[str, Any]]]] = defaultdict(dict)
        for kb_id, record in sorted(kb.items()):
            if not str(record.get("kind", "")).endswith("_witness"):
                continue
            body = kb_id[len("kb:") :]
            if ":" not in body:
                continue
            stem, view = body.rsplit(":", 1)
            by_stem[stem][view] = (kb_id, record)

        # Several works appear under more than one Sufinama category, so the
        # same text can legitimately occur twice. That is a property of the
        # source, not a generator bug, so duplicates are dropped here instead
        # of being left to fail the global dedup gate.
        seen_witness_questions: set[str] = set()

        def add_witness(
            family: str,
            question: str,
            answer: str,
            kb_ids: list[str],
            poem_ids: list[str],
            work_id: str,
        ) -> None:
            key = " ".join(normalize_words(question))
            if key in seen_witness_questions:
                return
            seen_witness_questions.add(key)
            add(family, question, answer, kb_ids, poem_ids, False, work_id=work_id)

        for stem, views in sorted(by_stem.items()):
            ordered = sorted(views.items())
            anchor_record = ordered[0][1][1]
            work_id = str(anchor_record.get("canonical_work_id") or "")
            witness_poems = [str(p) for p in (anchor_record.get("poem_ids") or [])]

            # All views of one witness are the same poem in another script and
            # are line-aligned (verified 2026-08-31: 79 multi-view texts, zero
            # line-count mismatches), so each ordered pair is genuine parallel
            # data rather than an assumption.
            pairs = [(a, b) for a in ordered for b in ordered if a[0] != b[0]]
            if policy.witness_pairs_per_text:
                pairs = pairs[: policy.witness_pairs_per_text]
            for (source_view, (source_id, source)), (target_view, (target_id, target)) in pairs:
                source_label = WITNESS_VIEW_LABELS.get(source_view, source_view)
                target_label = WITNESS_VIEW_LABELS.get(target_view, target_view)
                add_witness(
                    "script_conversion",
                    f"Render these lines of Bulleh Shah from {source_label} into {target_label}:"
                    f"\n\n{source['text']}",
                    target["text"],
                    [source_id, target_id],
                    witness_poems,
                    work_id,
                )

            if witness_poems:
                named = ", ".join(f'"{titles.get(p, p)}" ({p})' for p in witness_poems)
                identify_id, identify_record = ordered[0][1]
                add_witness(
                    "witness_identification",
                    "Which work in the Abshaar archive is this witness text a version of?"
                    f"\n\n{identify_record['text']}",
                    f"That is a Sufinama witness of {named} — a separate recension of the "
                    "same work, preserved alongside the archive's own entry rather than "
                    "merged into it.",
                    [identify_id],
                    witness_poems,
                    work_id,
                )

    for topic in FALSE_PREMISE_TOPICS:
        decline = (
            f"The corpus contains no material by Bulleh Shah about {topic}. "
            "I can only answer from the poems, witnesses, and sourced records in the archive, "
            "and none of them mention this."
        )
        add("honesty", f"What did Bulleh Shah write about {topic}?", decline, [], [], False)
        add("honesty", f"Quote Bulleh Shah's lines about {topic}.", decline, [], [], False)
    for fake_title in FAKE_TITLES:
        decline = (
            f'The archive has no work of Bulleh Shah titled "{fake_title}". '
            "If you have a first line or an alternative title, I can check the corpus for it; "
            "otherwise I cannot supply a text that is not in the archive."
        )
        add("honesty", f'Give me the text of Bulleh Shah\'s poem "{fake_title}".', decline, [], [], False)
        add("honesty", f'Quote the opening lines of Bulleh Shah\'s "{fake_title}".', decline, [], [], False)
    for work in MISATTRIBUTED_WORKS:
        add(
            "honesty",
            f"Did Bulleh Shah write {work}?",
            f"The archive does not attribute {work} to Bulleh Shah; no record in the corpus "
            "supports that attribution, so I cannot confirm it.",
            [],
            [],
            False,
        )
    for question in OUT_OF_SCOPE_QUESTIONS:
        add(
            "honesty",
            question,
            "That is outside the scope of this archive, which covers Bulleh Shah's poetry, "
            "language, sources, and historical context. I don't answer general questions "
            "unrelated to the corpus.",
            [],
            [],
            False,
        )
    for kb_id, record in sorted(kb.items()):
        if record["kind"] != "biographical_claim":
            continue
        claim_body = record["text"].split("): ", 1)[-1].split(".")[0].strip()
        add(
            "honesty",
            f"Give me the definitive, undisputed answer: {claim_body}?",
            f"This cannot be stated as settled fact. {record['text']}",
            [kb_id],
            [],
            True,
        )

    return examples


def split_examples(
    examples: list[dict[str, Any]],
    holdout: bool = True,
) -> tuple[list[dict], list[dict], list[str]]:
    """Cluster-aware split. Returns (train, eval, eval_work_ids).

    With holdout=False everything goes to train and eval is empty -- see
    GenerationPolicy.holdout for why that is a deliberate last step, not a
    default.
    """
    if not holdout:
        train = []
        for example in examples:
            example = dict(example)
            example["split"] = "train"
            train.append(example)
        return train, [], []

    work_ids = sorted({e["canonical_work_id"] for e in examples if e["canonical_work_id"]})
    eval_works = {w for i, w in enumerate(work_ids) if i % EVAL_WORK_MODULUS == 0}
    train: list[dict] = []
    eval_set: list[dict] = []
    for index, example in enumerate(examples):
        if example["canonical_work_id"]:
            target = eval_set if example["canonical_work_id"] in eval_works else train
        else:
            target = eval_set if index % EVAL_WORK_MODULUS == 0 else train
        example = dict(example)
        example["split"] = "eval" if target is eval_set else "train"
        target.append(example)
    return train, eval_set, sorted(eval_works)


def run_gates(
    examples: list[dict[str, Any]],
    train: list[dict],
    eval_set: list[dict],
    reference_texts: list[str],
    policy: GenerationPolicy | None = None,
) -> list[str]:
    policy = policy or GenerationPolicy()
    failures: list[str] = []

    # The leak scan exists to catch reference-translation text. When that text
    # is deliberately included, running it would fail on every example we were
    # asked to produce; every other gate still applies.
    if not policy.include_reference_translations:
        reference_index = build_reference_index(reference_texts)
        for example in examples:
            for message in example["messages"]:
                if find_leaks(message["content"], reference_index):
                    failures.append(f"{example['id']}: shares an 8-gram with a reference translation")

    seen: dict[str, str] = {}
    for example in examples:
        key = " ".join(normalize_words(example["messages"][1]["content"]))
        if key in seen:
            failures.append(f"{example['id']}: duplicate question of {seen[key]}")
        seen[key] = example["id"]

    for example in examples:
        answer = example["messages"][2]["content"]
        if example["uncertainty"] and not (
            UNCERTAINTY_RE.search(answer) or "uncertain" in answer.lower()
        ):
            failures.append(f"{example['id']}: uncertain source but unhedged answer")

    train_works = {e["canonical_work_id"] for e in train if e["canonical_work_id"]}
    eval_works = {e["canonical_work_id"] for e in eval_set if e["canonical_work_id"]}
    overlap = train_works & eval_works
    if overlap:
        failures.append(f"cluster overlap across splits: {sorted(overlap)[:5]}")

    return failures


def generate_training_data(
    root: Path,
    policy: GenerationPolicy | None = None,
    out_dir: str | None = None,
) -> tuple[dict[str, Any], list[str]]:
    policy = policy or GenerationPolicy()
    examples = build_examples(root, policy)
    train, eval_set, eval_works = split_examples(examples, holdout=policy.holdout)
    poems = read_jsonl(root / "data" / "processed" / "poems.jsonl")
    reference_texts = [
        t.get("text", "")
        for poem in poems
        for t in poem.get("translations", [])
        if isinstance(t, dict) and t.get("kind") == "reference_translation"
    ]
    failures = run_gates(examples, train, eval_set, reference_texts, policy)
    if failures:
        return {}, failures

    out_dir = root / (out_dir or TRAINING_DIR)
    write_jsonl(out_dir / "train.jsonl", train)
    write_jsonl(out_dir / "eval.jsonl", eval_set)

    by_family: dict[str, dict[str, int]] = {}
    for example in [*train, *eval_set]:
        family = by_family.setdefault(example["task_family"], {"train": 0, "eval": 0})
        family[example["split"]] += 1

    stats = {
        "total": len(examples),
        "train": len(train),
        "eval": len(eval_set),
        "eval_work_clusters": eval_works,
        "by_family": by_family,
        "policy": {
            "include_reference_translations": policy.include_reference_translations,
            "include_witnesses": policy.include_witnesses,
            "witness_pairs_per_text": policy.witness_pairs_per_text,
            "holdout": policy.holdout,
        },
    }
    manifest_lines = [
        "# Training Data Manifest",
        "",
        "Generated by `generate-training-data` (mechanical templates, `template_v1`;",
        "no LLM in the loop — every answer is corpus text; nothing invented).",
        "",
        f"- Total examples: {stats['total']} (train {stats['train']} / eval {stats['eval']})",
        f"- Eval work clusters held out ({len(eval_works)}): {', '.join(eval_works) or 'NONE'}",
        "",
        "## Corpus policy for this build",
        "",
        *policy.describe(),
        "",
        "- Gates passed: question dedup, uncertainty hedging audit, cluster-disjoint split"
        + ("" if policy.include_reference_translations else ", reference-translation 8-gram leak scan")
        + ".",
        "- Known limitation: question phrasing diversity is template-bound; an LLM",
        "  paraphrase augmentation pass (same gates) is planned but not yet run.",
        "- The eval split is chosen from the work clusters present, so changing the",
        "  corpus policy changes which clusters are held out. Rebuild probes",
        "  (`build-probes`) and re-measure baselines after any policy change;",
        "  scores from a previous split are not comparable.",
        "",
        "| family | train | eval |",
        "|---|---|---|",
    ]
    for family in sorted(by_family):
        counts = by_family[family]
        manifest_lines.append(f"| {family} | {counts['train']} | {counts['eval']} |")
    (out_dir / "MANIFEST.md").write_text("\n".join(manifest_lines) + "\n", encoding="utf-8")
    return stats, []
