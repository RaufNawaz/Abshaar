#!/usr/bin/env python3

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


OFFLOADING_FILE = "OFFLOADING.md"
REPO_ROOT = Path(__file__).resolve().parent


def find_codex_command():
    """Prefer codex.cmd on Windows to avoid PowerShell execution-policy errors."""
    for candidate in ("codex.cmd", "codex.exe", "codex"):
        resolved = shutil.which(candidate)
        if resolved:
            return resolved
    return None


def run_command(command, input_text=None):
    command_name = command[0] if command else "command"
    try:
        result = subprocess.run(
            command,
            input=input_text,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            cwd=REPO_ROOT,
        )
        return result.returncode, result.stdout, result.stderr
    except FileNotFoundError:
        print(f"Error: {command_name} was not found.")
        sys.exit(1)


def collect_repo_context():
    commands = {
        "git_status": ["git", "status", "--short"],
        "recent_commits": ["git", "log", "--oneline", "-10"],
        "tracked_files": ["git", "ls-files"],
    }

    context_parts = []

    for label, command in commands.items():
        code, out, err = run_command(command)
        if code == 0:
            context_parts.append(f"## {label}\n\n{out.strip() or 'No output.'}")
        else:
            context_parts.append(f"## {label}\n\nUnavailable.\n\nError:\n{err.strip()}")

    offloading_path = REPO_ROOT / OFFLOADING_FILE
    if offloading_path.exists():
        context_parts.append(
            f"## Existing {OFFLOADING_FILE}\n\n{offloading_path.read_text(encoding='utf-8')}"
        )
    else:
        context_parts.append(f"## Existing {OFFLOADING_FILE}\n\nNo existing offloading document found.")

    return "\n\n".join(context_parts)


def main():
    parser = argparse.ArgumentParser(
        description="Run a Codex task and then automatically update OFFLOADING.md."
    )
    parser.add_argument(
        "task",
        nargs="+",
        help="The task prompt to send to Codex.",
    )
    parser.add_argument(
        "--skip-task",
        action="store_true",
        help="Only update OFFLOADING.md without running a task first.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the Codex commands and write the handoff prompt without running Codex.",
    )
    args = parser.parse_args()

    task_prompt = " ".join(args.task)
    codex_command = find_codex_command()

    if codex_command is None:
        print("Error: Codex CLI was not found.")
        print("Install it first with: npm i -g @openai/codex")
        sys.exit(1)

    print(f"Using Codex executable: {codex_command}")

    if not args.skip_task:
        print("\nRunning Codex task...\n")
        task_command = [
            codex_command,
            "exec",
            "--sandbox",
            "workspace-write",
            "--cd",
            str(REPO_ROOT),
            task_prompt,
        ]

        if args.dry_run:
            print("Dry run: would run task command:")
            print(" ".join(task_command))
        else:
            code, out, err = run_command(task_command)

            if out.strip():
                print(out)

            if err.strip():
                print(err, file=sys.stderr)

            if code != 0:
                print("\nCodex task failed. I will still try to update the offloading document.\n")

    repo_context = collect_repo_context()

    handoff_prompt = f"""
You are updating a project offloading document.

Create or update `{OFFLOADING_FILE}` so this project can be resumed in a new chat, Codex session, or AI tool without context loss.

Use the CRAFT method:

C: Context
Summarize the project purpose, goals, constraints, files, tools, assumptions, user preferences, and relevant history.

R: Role
Write as a senior project handoff assistant preparing another AI agent or developer to continue immediately.

A: Action
Update `{OFFLOADING_FILE}` with these sections:
1. Project Overview
2. What Has Been Done
3. Current State
4. Key Decisions and Rationale
5. User Preferences and Instructions
6. Important Context a New Chat Must Know
7. Next Steps
8. Restart Prompt
9. Risks, Gaps, and Things to Verify
10. Compact Version

F: Format
Use clear markdown headings, bullets, checklists, and tables where useful.
Include filenames, paths, commands, errors, decisions, and unresolved issues.
Do not invent facts. Mark unknowns as "Unknown" or "Needs verification."

T: Tone
Professional, precise, practical, and continuity-focused.

The latest user task was:

{task_prompt}

Repository context:

{repo_context}

Now update `{OFFLOADING_FILE}` directly.
"""

    print("\nUpdating OFFLOADING.md...\n")

    handoff_command = [
        codex_command,
        "exec",
        "--sandbox",
        "workspace-write",
        "--cd",
        str(REPO_ROOT),
        "-",
    ]

    if args.dry_run:
        prompt_path = REPO_ROOT / "data" / "cache" / "codex_handoff_prompt.md"
        prompt_path.parent.mkdir(parents=True, exist_ok=True)
        prompt_path.write_text(handoff_prompt, encoding="utf-8", newline="\n")
        print("Dry run: would run handoff command:")
        print(" ".join(handoff_command))
        print(f"Dry run: wrote handoff prompt to {prompt_path}")
        return

    code, out, err = run_command(handoff_command, input_text=handoff_prompt)

    if out.strip():
        print(out)

    if err.strip():
        print(err, file=sys.stderr)

    if code == 0:
        print(f"\nDone. `{OFFLOADING_FILE}` should now be updated.")
    else:
        print(f"\nFailed to update `{OFFLOADING_FILE}`.")
        sys.exit(code)


if __name__ == "__main__":
    main()
