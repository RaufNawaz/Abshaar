from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

from abshaar.export import export_site_data
from abshaar.jsonl import write_jsonl
from abshaar.markdown_entry import entry_to_poem_record, parse_markdown_entry
from abshaar.ollama_client import check_ollama, draft_poem
from abshaar.paths import resolve_root
from abshaar.prompts import save_prompt_pack
from abshaar.status import format_project_status, next_poem_id, project_status
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

    prompt_pack = subparsers.add_parser("prompt-pack", help="Build a model prompt pack for one poem.")
    prompt_pack.add_argument("--poem-id", default=None)
    prompt_pack.add_argument("--all", action="store_true", help="Build prompt packs for all poems.")

    subparsers.add_parser("ai-check", help="Check whether Ollama is available locally.")

    draft = subparsers.add_parser("draft", help="Generate a model draft through local Ollama.")
    draft.add_argument("--poem-id", required=True)
    draft.add_argument("--model", default="qwen3:8b")

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
    if args.command == "prompt-pack":
        return command_prompt_pack(root, args.poem_id, args.all)
    if args.command == "ai-check":
        return command_ai_check()
    if args.command == "draft":
        return command_draft(root, args.poem_id, args.model)

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


if __name__ == "__main__":
    raise SystemExit(main())
