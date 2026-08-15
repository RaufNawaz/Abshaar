from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

from abshaar.export import export_site_data
from abshaar.gurmukhi_pdf import extract_gurmukhi_pdf
from abshaar.jsonl import write_jsonl
from abshaar.markdown_entry import entry_to_poem_record, parse_markdown_entry
from abshaar.ollama_client import check_ollama, draft_poem
from abshaar.paths import resolve_root
from abshaar.prompts import save_prompt_pack
from abshaar.status import format_project_status, next_poem_id, project_status
from abshaar.source_matching import match_source_manifest
from abshaar.sufinama import (
    DEFAULT_USER_AGENT,
    acquire_sufinama_corpus,
    acquire_sufinama_texts,
)
from abshaar.validation import iter_working_entries, validate_project


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="abshaar",
        description="Automation CLI for the Abshaar archive and translation workflow.",
    )
    parser.add_argument("--root", default=None, help="Repository root. Defaults to current checkout.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("init", help="Create expected project directories.")
    subparsers.add_parser("status", help="Show a plain-language project status summary.")

    new_entry = subparsers.add_parser("new-entry", help="Create a Markdown poem entry from template.")
    new_entry.add_argument(
        "--id",
        default=None,
        help="Poem ID, for example bulleh_shah_0001. If omitted, the next ID is chosen.",
    )
    new_entry.add_argument("--title", default=None, help="Working title or first line.")
    new_entry.add_argument("--poet-id", default="bulleh_shah", help="Poet ID.")

    build_data = subparsers.add_parser("build-data", help="Convert working Markdown entries to JSONL.")
    build_data.add_argument(
        "--include-placeholders",
        action="store_true",
        help="Also include entries that still contain placeholder text.",
    )

    subparsers.add_parser("validate", help="Validate working entries and JSONL files.")
    subparsers.add_parser("export-site", help="Export website-ready JSON into data/site/.")

    export_training = subparsers.add_parser(
        "export-training-corpus",
        help="Export rights-safe trainable layers; fails on any reference-translation leak.",
    )
    export_training.add_argument(
        "--output",
        default="data/processed/training/trainable_layers.jsonl",
    )

    subparsers.add_parser(
        "extract-lexicon",
        help="Extract Key Terms and Themes from working entries into terms/themes JSONL.",
    )
    subparsers.add_parser(
        "build-clusters",
        help="Build conservative canonical-work clusters from the source crosswalks.",
    )
    subparsers.add_parser(
        "build-kb",
        help="Build the consolidated private knowledge base; fails on any reference leak.",
    )

    build_index = subparsers.add_parser(
        "build-index",
        help="Embed the knowledge base into the local Chroma index (requires the .venv AI stack).",
    )
    build_index.add_argument("--model", default=None, help="Embedding model; defaults to BAAI/bge-m3.")

    ask = subparsers.add_parser(
        "ask",
        help="Ask a grounded question over the knowledge base (retrieval + local Ollama).",
    )
    ask.add_argument("question")
    ask.add_argument("--model", default="qwen3:8b")
    ask.add_argument("--k", type=int, default=8)
    ask.add_argument("--min-score", type=float, default=None)
    ask.add_argument("--retrieve-only", action="store_true", help="Show retrieved records without generation.")

    subparsers.add_parser(
        "generate-training-data",
        help="Build the templated train/eval instruction dataset with all gates.",
    )

    subparsers.add_parser(
        "build-probes",
        help="Build the fixed 50-probe evaluation set (factual/honesty/disputed).",
    )

    subparsers.add_parser(
        "export-mlx-dataset",
        help="Write messages-only train/valid JSONL for mlx_lm.lora into data/processed/training/mlx/.",
    )

    normalize_translit = subparsers.add_parser(
        "normalize-translit",
        help="Normalize entry Transliteration sections to project-latin-v1 (dry-run unless --apply).",
    )
    normalize_translit.add_argument("--apply", action="store_true")

    augment = subparsers.add_parser(
        "augment-training-data",
        help="Paraphrase-augment training questions via local Ollama (answers stay verbatim); re-runs all gates.",
    )
    augment.add_argument("--generator", default="qwen3:8b")
    augment.add_argument("--verifier", default="qwen3:4b")
    augment.add_argument("--limit-per-family", type=int, default=30)

    run_eval = subparsers.add_parser(
        "run-eval",
        help="Evaluate a model over the probe set; appends to eval_baseline.md.",
    )
    run_eval.add_argument("--model", default="qwen3:8b")
    run_eval.add_argument("--rag", action="store_true", help="Answer through retrieval (ask) instead of bare chat.")
    run_eval.add_argument("--judge", default="qwen3:4b")
    run_eval.add_argument("--limit", type=int, default=None)

    prompt_pack = subparsers.add_parser("prompt-pack", help="Build a model prompt pack for one poem.")
    prompt_pack.add_argument("--poem-id", default=None)
    prompt_pack.add_argument("--all", action="store_true", help="Build prompt packs for all poems.")

    subparsers.add_parser("ai-check", help="Check whether Ollama is available locally.")

    draft = subparsers.add_parser("draft", help="Generate a model draft through local Ollama.")
    draft.add_argument("--poem-id", required=True)
    draft.add_argument("--model", default="qwen3:8b")

    source_match = subparsers.add_parser(
        "match-source-manifest",
        help="Match an offline source manifest to existing working poem entries.",
    )
    source_match.add_argument("--manifest", required=True, help="Input JSONL manifest path.")
    source_match.add_argument(
        "--output",
        default="data/context/source_matches.jsonl",
        help="Output JSONL path for reviewable candidate matches.",
    )
    source_match.add_argument("--top", type=int, default=3, help="Candidates per source item.")

    sufinama = subparsers.add_parser(
        "acquire-sufinama",
        help="Acquire and align the authorized Sufinama Bulleh Shah kaafi corpus.",
    )
    sufinama.add_argument(
        "--output",
        default="data/processed/private/sufinama_bulleh_shah_kaafi.jsonl",
    )
    sufinama.add_argument(
        "--catalog-output",
        default="data/context/sufinama_source_items.jsonl",
    )
    sufinama.add_argument(
        "--match-output",
        default="data/context/source_matches.jsonl",
    )
    sufinama.add_argument("--cache-dir", default="data/raw/private/sufinama")
    sufinama.add_argument("--delay", type=float, default=0.75)
    sufinama.add_argument("--workers", type=int, default=3)
    sufinama.add_argument("--limit", type=int, default=None)
    sufinama.add_argument("--refresh", action="store_true")
    sufinama.add_argument("--discover-only", action="store_true")
    sufinama.add_argument(
        "--offline",
        action="store_true",
        help="Rebuild from the saved 76-item catalog and raw cache without network access.",
    )
    sufinama.add_argument("--user-agent", default=DEFAULT_USER_AGENT)
    sufinama.add_argument("--transport", choices=["urllib", "curl"], default="urllib")

    sufinama_texts = subparsers.add_parser(
        "acquire-sufinama-texts",
        help="Acquire the authorized non-kaafi Bulleh Shah textual categories.",
    )
    sufinama_texts.add_argument(
        "--output",
        default="data/processed/private/sufinama_bulleh_shah_other_texts.jsonl",
    )
    sufinama_texts.add_argument(
        "--catalog-output",
        default="data/context/sufinama_text_source_items.jsonl",
    )
    sufinama_texts.add_argument(
        "--match-output",
        default="data/context/sufinama_text_source_matches.jsonl",
    )
    sufinama_texts.add_argument("--cache-dir", default="data/raw/private/sufinama")
    sufinama_texts.add_argument("--delay", type=float, default=0.75)
    sufinama_texts.add_argument("--workers", type=int, default=3)
    sufinama_texts.add_argument("--limit", type=int, default=None)
    sufinama_texts.add_argument("--refresh", action="store_true")
    sufinama_texts.add_argument("--discover-only", action="store_true")
    sufinama_texts.add_argument(
        "--offline",
        action="store_true",
        help="Rebuild from the saved 48-item text catalog and raw cache without network access.",
    )
    sufinama_texts.add_argument("--user-agent", default=DEFAULT_USER_AGENT)
    sufinama_texts.add_argument(
        "--transport", choices=["urllib", "curl"], default="urllib"
    )

    gurmukhi_pdf = subparsers.add_parser(
        "extract-gurmukhi-pdf",
        help="Extract a numbered Gurmukhi PDF as a separate, review-required witness corpus.",
    )
    gurmukhi_pdf.add_argument("--input", required=True, help="Local PDF path.")
    gurmukhi_pdf.add_argument(
        "--output",
        default="data/processed/private/punjab_library_bulleh_shah_kafian.jsonl",
    )
    gurmukhi_pdf.add_argument(
        "--catalog-output",
        default="data/context/punjab_library_source_items.jsonl",
    )
    gurmukhi_pdf.add_argument(
        "--run-output",
        default="data/processed/private/punjab_library_gurmukhi_run.json",
    )
    gurmukhi_pdf.add_argument("--expected-count", type=int, default=160)

    args = parser.parse_args(argv)
    root = resolve_root(args.root)

    if args.command == "init":
        return command_init(root)
    if args.command == "status":
        return command_status(root)
    if args.command == "new-entry":
        return command_new_entry(root, args.id, args.title, args.poet_id)
    if args.command == "build-data":
        return command_build_data(root, args.include_placeholders)
    if args.command == "validate":
        return command_validate(root)
    if args.command == "export-site":
        return command_export_site(root)
    if args.command == "export-training-corpus":
        return command_export_training(root, args.output)
    if args.command == "extract-lexicon":
        return command_extract_lexicon(root)
    if args.command == "build-clusters":
        return command_build_clusters(root)
    if args.command == "build-kb":
        return command_build_kb(root)
    if args.command == "build-index":
        return command_build_index(root, args.model)
    if args.command == "ask":
        return command_ask(root, args)
    if args.command == "generate-training-data":
        return command_generate_training_data(root)
    if args.command == "build-probes":
        return command_build_probes(root)
    if args.command == "export-mlx-dataset":
        return command_export_mlx_dataset(root)
    if args.command == "augment-training-data":
        return command_augment_training_data(root, args)
    if args.command == "normalize-translit":
        return command_normalize_translit(root, args.apply)
    if args.command == "run-eval":
        return command_run_eval(root, args)
    if args.command == "prompt-pack":
        return command_prompt_pack(root, args.poem_id, args.all)
    if args.command == "ai-check":
        return command_ai_check()
    if args.command == "draft":
        return command_draft(root, args.poem_id, args.model)
    if args.command == "match-source-manifest":
        return command_match_source_manifest(root, args.manifest, args.output, args.top)
    if args.command == "acquire-sufinama":
        return command_acquire_sufinama(root, args)
    if args.command == "acquire-sufinama-texts":
        return command_acquire_sufinama_texts(root, args)
    if args.command == "extract-gurmukhi-pdf":
        return command_extract_gurmukhi_pdf(root, args)

    parser.error(f"unknown command {args.command}")
    return 2


def command_init(root: Path) -> int:
    directories = [
        "data/raw/public",
        "data/raw/private",
        "data/processed",
        "data/annotations",
        "data/lexicon",
        "data/context",
        "data/cache",
        "data/working",
        "data/templates",
        "data/site",
        "src/abshaar",
        "scripts",
        "tests",
    ]
    for directory in directories:
        (root / directory).mkdir(parents=True, exist_ok=True)
    print(f"Initialized project directories under {root}")
    return 0


def command_status(root: Path) -> int:
    print(format_project_status(project_status(root)))
    return 0


def command_new_entry(root: Path, poem_id: str | None, title: str | None, poet_id: str) -> int:
    template = root / "data" / "working" / "bulleh_shah_entry_template.md"
    if not template.exists():
        print(f"Template not found: {template}", file=sys.stderr)
        return 1

    selected_poem_id = poem_id or next_poem_id(root, poet_id)
    output = root / "data" / "working" / f"{selected_poem_id}.md"
    if output.exists():
        print(f"Entry already exists: {output}", file=sys.stderr)
        return 1

    text = template.read_text(encoding="utf-8")
    text = text.replace("id: bulleh_shah_0001", f"id: {selected_poem_id}")
    text = text.replace("poet_id: bulleh_shah", f"poet_id: {poet_id}")
    if title:
        text = text.replace('title: "[first line or working title]"', f'title: "{title}"')
    output.write_text(text, encoding="utf-8", newline="\n")
    print(f"Created {output.relative_to(root)}")
    return 0


def command_build_data(root: Path, include_placeholders: bool) -> int:
    from abshaar.text import has_placeholder

    records = []
    skipped = []
    for path in iter_working_entries(root):
        entry = parse_markdown_entry(path)
        record = entry_to_poem_record(entry)
        if has_placeholder(record) and not include_placeholders:
            skipped.append(path)
            continue
        records.append(record)

    output = root / "data" / "processed" / "poems.jsonl"
    write_jsonl(output, records)
    print(f"Wrote {len(records)} poem record(s) to {output.relative_to(root)}")
    if skipped:
        print(f"Skipped {len(skipped)} placeholder entry file(s):")
        for path in skipped:
            print(f"  - {path.relative_to(root)}")
    return 0


def command_generate_training_data(root: Path) -> int:
    from abshaar.dataset_gen import TRAINING_DIR, generate_training_data

    stats, failures = generate_training_data(root)
    if failures:
        print("GATE FAILURE — no dataset written:", file=sys.stderr)
        for failure in failures[:20]:
            print(f"  - {failure}", file=sys.stderr)
        if len(failures) > 20:
            print(f"  ... and {len(failures) - 20} more", file=sys.stderr)
        return 1
    print(
        f"Wrote {stats['train']} train / {stats['eval']} eval example(s) "
        f"({stats['total']} total) to {TRAINING_DIR}/"
    )
    for family in sorted(stats["by_family"]):
        counts = stats["by_family"][family]
        print(f"  - {family}: {counts['train']} train / {counts['eval']} eval")
    return 0


def command_normalize_translit(root: Path, apply: bool) -> int:
    from abshaar.translit import normalize_entries

    report = normalize_entries(root, apply=apply)
    mode = "APPLIED to" if apply else "DRY RUN — would change"
    print(f"{mode} {len(report['changed'])} entr(ies); {len(report['unchanged'])} already conform")
    for stem in report["changed"]:
        print(f"  ~ {stem}")
    if report["residual_lint"]:
        print("Residual style issues after normalization (need manual review):")
        for stem, issues in report["residual_lint"].items():
            print(f"  ! {stem}: {'; '.join(issues)}")
    return 0


def command_augment_training_data(root: Path, args: argparse.Namespace) -> int:
    from abshaar.augment import augment_training_data
    from abshaar.ollama_client import run_ollama_chat

    stats, failures = augment_training_data(
        root,
        run_ollama_chat,
        generator_model=args.generator,
        verifier_model=args.verifier,
        per_family_limit=args.limit_per_family,
    )
    if failures:
        print("GATE FAILURE — augmented set not written:", file=sys.stderr)
        for failure in failures[:20]:
            print(f"  - {failure}", file=sys.stderr)
        return 1
    print(
        f"Augmentation: attempted {stats['attempted']}, kept {stats['kept']}, "
        f"rejected {stats['rejected']}"
        + (f" (train now {stats['train_total']})" if stats.get("train_total") else "")
    )
    if stats.get("warning"):
        print(f"WARNING: {stats['warning']}", file=sys.stderr)
        return 1
    return 0


def command_export_mlx_dataset(root: Path) -> int:
    from abshaar.jsonl import read_jsonl, write_jsonl as _write_jsonl

    training_dir = root / "data" / "processed" / "training"
    out_dir = training_dir / "mlx"
    counts = {}
    for source, target in [("train.jsonl", "train.jsonl"), ("eval.jsonl", "valid.jsonl")]:
        examples = read_jsonl(training_dir / source)
        _write_jsonl(out_dir / target, [{"messages": e["messages"]} for e in examples])
        counts[target] = len(examples)
    print(f"Wrote mlx dataset: train {counts['train.jsonl']} / valid {counts['valid.jsonl']} to {out_dir.relative_to(root)}/")
    return 0


def command_build_probes(root: Path) -> int:
    from abshaar.evaluate import PROBES_PATH, build_probes

    count = build_probes(root)
    print(f"Wrote {count} probe(s) to {PROBES_PATH}")
    return 0


def command_run_eval(root: Path, args: argparse.Namespace) -> int:
    from abshaar.evaluate import run_eval

    summary = run_eval(root, args.model, args.rag, judge_model=args.judge, limit=args.limit)
    print(
        f"{summary['model']}{' + RAG' if summary['rag'] else ''}: "
        f"factual {summary['factual']} | honesty {summary['honesty']} | "
        f"disputed {summary['disputed']} ({summary['probes']} probes)"
    )
    return 0


def command_build_index(root: Path, model: str | None) -> int:
    try:
        from abshaar.rag import EMBED_MODEL, build_index
    except ImportError as exc:
        print(f"AI stack unavailable ({exc}). Run via the .venv python after installing requirements.txt.", file=sys.stderr)
        return 1

    count = build_index(root, model_name=model or EMBED_MODEL)
    print(f"Indexed {count} knowledge-base record(s) into data/cache/chroma/")
    return 0


def command_ask(root: Path, args: argparse.Namespace) -> int:
    try:
        from abshaar.rag import DEFAULT_MIN_SCORE, ask
    except ImportError as exc:
        print(f"AI stack unavailable ({exc}). Run via the .venv python after installing requirements.txt.", file=sys.stderr)
        return 1

    result = ask(
        root,
        args.question,
        model=args.model,
        k=args.k,
        min_score=args.min_score if args.min_score is not None else DEFAULT_MIN_SCORE,
        retrieve_only=args.retrieve_only,
    )
    if args.retrieve_only:
        for hit in result["hits"]:
            print(f"{hit['score']:.4f}  {hit['id']}  ({hit['metadata'].get('kind')})")
        return 0
    print(result["answer"])
    print()
    print("Retrieved records:")
    for hit in result["hits"]:
        print(f"  {hit['score']:.4f}  {hit['id']}")
    if result["invalid_citations"]:
        print("ERROR: answer cites record ids that were not retrieved:", file=sys.stderr)
        for cited in result["invalid_citations"]:
            print(f"  - {cited}", file=sys.stderr)
        return 1
    return 0


def command_extract_lexicon(root: Path) -> int:
    from abshaar.lexicon import extract_lexicon

    report = extract_lexicon(root)
    print(f"Wrote {report['terms']} term(s) to data/lexicon/terms.jsonl")
    print(f"Wrote {report['themes']} theme(s) to data/context/themes.jsonl")
    if report["entries_without_terms"]:
        print("Entries contributing no key terms:")
        for poem_id in report["entries_without_terms"]:
            print(f"  - {poem_id}")
    else:
        print("Every working entry contributed at least one key term.")
    return 0


def command_build_clusters(root: Path) -> int:
    from abshaar.clusters import build_clusters

    counts = build_clusters(root)
    print(
        f"Wrote {counts['clusters']} cluster(s) covering {counts['members']} member(s) "
        f"({counts['auto_merged_witnesses']} witness(es) auto-merged on exact 1.0 matches) "
        "to data/context/canonical_clusters.jsonl"
    )
    return 0


def command_build_kb(root: Path) -> int:
    from abshaar.knowledge_base import KB_PATH, build_kb

    counts, leaks = build_kb(root)
    if leaks:
        print("LEAK DETECTED — reference-translation text in knowledge base; nothing written:", file=sys.stderr)
        for leak in leaks:
            print(f"  - {leak}", file=sys.stderr)
        return 1
    print(f"Wrote {counts['total']} knowledge-base record(s) to {KB_PATH}")
    for kind in sorted(k for k in counts if k != "total"):
        print(f"  - {kind}: {counts[kind]}")
    return 0


def command_export_training(root: Path, output: str) -> int:
    from abshaar.training_export import export_training_corpus

    count, leaks = export_training_corpus(root, root / output)
    if leaks:
        print("LEAK DETECTED — reference-translation text in trainable layers; nothing written:", file=sys.stderr)
        for leak in leaks:
            print(f"  - {leak}", file=sys.stderr)
        return 1
    print(f"Wrote {count} trainable layer record(s) to {output}")
    return 0


def command_validate(root: Path) -> int:
    issues = validate_project(root)
    if not issues:
        print("No validation issues found.")
        return 0

    for issue in issues:
        print(issue.format())
    has_errors = any(issue.level == "error" for issue in issues)
    return 1 if has_errors else 0


def command_export_site(root: Path) -> int:
    summary = export_site_data(root)
    print("Exported website data to data/site/:")
    for key, value in summary.items():
        print(f"  {key}: {value}")
    return 0


def command_prompt_pack(root: Path, poem_id: str | None, all_poems: bool) -> int:
    if all_poems:
        from abshaar.jsonl import read_jsonl

        poems_path = root / "data" / "processed" / "poems.jsonl"
        if not poems_path.exists():
            print("No data/processed/poems.jsonl file exists yet.", file=sys.stderr)
            return 1
        poems = read_jsonl(poems_path)
        for poem in poems:
            if poem.get("id"):
                output_path = save_prompt_pack(root, str(poem["id"]))
                print(f"Wrote {output_path.relative_to(root)}")
        print(f"Built {len(poems)} prompt pack(s).")
        return 0

    if not poem_id:
        print("Provide --poem-id or use --all.", file=sys.stderr)
        return 1

    try:
        output_path = save_prompt_pack(root, poem_id)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(f"Wrote {output_path.relative_to(root)}")
    return 0


def command_ai_check() -> int:
    status = check_ollama()
    print(f"Ollama CLI found: {status['cli_found']}")
    print(f"Ollama version: {status['version'] or 'unknown'}")
    print(f"Ollama API available: {status['api_available']}")
    if status["models"]:
        print("Installed Ollama models:")
        for model in status["models"]:
            print(f"  - {model}")
    else:
        print("Installed Ollama models: none detected")
    print("Optional Python AI packages:")
    for package_name, installed in status["optional_packages"].items():
        print(f"  - {package_name}: {'installed' if installed else 'missing'}")
    return 0 if status["api_available"] else 1


def command_draft(root: Path, poem_id: str, model: str) -> int:
    if shutil.which("ollama") is None:
        print("Ollama CLI was not found. Install Ollama and pull a model first.", file=sys.stderr)
        return 1
    try:
        output_path = draft_poem(root, poem_id, model)
    except Exception as exc:  # noqa: BLE001 - CLI should give a clean failure.
        print(f"Could not generate draft: {exc}", file=sys.stderr)
        return 1
    print(f"Saved model output to {output_path.relative_to(root)}")
    return 0


def command_match_source_manifest(
    root: Path,
    manifest: str,
    output: str,
    top_n: int,
) -> int:
    manifest_path = Path(manifest)
    output_path = Path(output)
    if not manifest_path.is_absolute():
        manifest_path = root / manifest_path
    if not output_path.is_absolute():
        output_path = root / output_path

    try:
        matches = match_source_manifest(root, manifest_path, output_path, top_n=top_n)
    except (OSError, ValueError) as exc:
        print(f"Could not match source manifest: {exc}", file=sys.stderr)
        return 1

    try:
        shown_path = output_path.relative_to(root)
    except ValueError:
        shown_path = output_path
    print(f"Wrote {len(matches)} source match record(s) to {shown_path}")
    print("Review candidate matches before adding source IDs to poem entries.")
    return 0


def command_acquire_sufinama(root: Path, args: argparse.Namespace) -> int:
    def resolve(value: str) -> Path:
        path = Path(value)
        return path if path.is_absolute() else root / path

    try:
        summary = acquire_sufinama_corpus(
            root=root,
            output_path=resolve(args.output),
            catalog_output_path=resolve(args.catalog_output),
            match_output_path=resolve(args.match_output),
            cache_dir=resolve(args.cache_dir),
            delay_seconds=args.delay,
            workers=args.workers,
            limit=args.limit,
            refresh=args.refresh,
            discover_only=args.discover_only,
            user_agent=args.user_agent,
            transport=args.transport,
            offline=args.offline,
        )
    except Exception as exc:  # noqa: BLE001 - CLI should preserve a clean failure.
        print(f"Could not acquire Sufinama corpus: {exc}", file=sys.stderr)
        return 1

    print(f"Discovered paired catalog items: {summary['catalog_items']}")
    print(f"Normalized witness records written: {summary['records']}")
    print(f"View errors: {summary['errors']}")
    print(f"Requested views unavailable at source: {summary.get('unavailable', 0)}")
    audit = summary.get("audit") or {}
    layers = audit.get("layer_record_counts") or {}
    if layers:
        print(
            "Layer coverage: "
            f"Roman plain {layers.get('roman_plain', 0)}, "
            f"Roman diacritic {layers.get('roman_diacritic', 0)}, "
            f"Urdu {layers.get('urdu', 0)}, "
            f"Devanagari {layers.get('devanagari', 0)}"
        )
        print(
            "Roman/Urdu line-ID alignment: "
            f"{audit.get('roman_urdu_line_id_matches', 0)}/"
            f"{audit.get('roman_urdu_pair_records', 0)} paired witnesses"
        )
    return 0 if summary["errors"] == 0 else 1


def command_acquire_sufinama_texts(root: Path, args: argparse.Namespace) -> int:
    def resolve(value: str) -> Path:
        path = Path(value)
        return path if path.is_absolute() else root / path

    try:
        summary = acquire_sufinama_texts(
            root=root,
            output_path=resolve(args.output),
            catalog_output_path=resolve(args.catalog_output),
            match_output_path=resolve(args.match_output),
            cache_dir=resolve(args.cache_dir),
            delay_seconds=args.delay,
            workers=args.workers,
            limit=args.limit,
            refresh=args.refresh,
            discover_only=args.discover_only,
            user_agent=args.user_agent,
            transport=args.transport,
            offline=args.offline,
        )
    except Exception as exc:  # noqa: BLE001 - CLI should preserve a clean failure.
        print(f"Could not acquire Sufinama text categories: {exc}", file=sys.stderr)
        return 1

    print(f"Cataloged non-kaafi text records: {summary['catalog_items']}")
    print(f"Normalized witness records written: {summary['records']}")
    print(f"View errors: {summary['errors']}")
    print(f"Requested views unavailable at source: {summary.get('unavailable', 0)}")
    audit = summary.get("audit") or {}
    categories = audit.get("category_record_counts") or {}
    if categories:
        print(
            "Category coverage: "
            + ", ".join(f"{category} {count}" for category, count in categories.items())
        )
    return 0 if summary["errors"] == 0 else 1


def command_extract_gurmukhi_pdf(root: Path, args: argparse.Namespace) -> int:
    def resolve(value: str) -> Path:
        path = Path(value)
        return path if path.is_absolute() else root / path

    try:
        run = extract_gurmukhi_pdf(
            root=root,
            pdf_path=resolve(args.input),
            output_path=resolve(args.output),
            catalog_output_path=resolve(args.catalog_output),
            run_output_path=resolve(args.run_output),
            expected_count=args.expected_count,
        )
    except Exception as exc:  # noqa: BLE001 - CLI should preserve a clean failure.
        print(f"Could not extract Gurmukhi PDF: {exc}", file=sys.stderr)
        return 1

    audit = run["audit"]
    print(f"Extracted Gurmukhi witness records: {audit['records']}")
    print(f"PDF pages inspected: {run['pdf_pages']}")
    print(f"Missing ordinals: {len(audit['missing_ordinals'])}")
    print(f"Duplicate ordinals: {len(audit['duplicate_ordinals'])}")
    print(f"Empty extracted texts: {audit['empty_texts']}")
    print("All extracted text remains review-required; rendered PDF pages are authoritative.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
