# OFFLOADING.md

Last updated: 2026-05-23

## 1. Project Overview

This repository is located at `D:\Harvard\Poetry Model Project`. The project appears, from the repository name and user-provided file/status context, to concern a poetry model project with data templates, documentation, implementation guidance, automation/handoff workflows, and likely source/tests infrastructure. The full substantive purpose, model design, data workflow, and runtime behavior still need verification from repository files because direct PowerShell inspection failed during this update with `windows sandbox: spawn setup refresh`. The current immediate objective is to maintain a detailed, restartable `OFFLOADING.md` handoff document as required by `AGENTS.md`, so the user can pause and resume the project in a new chat, Codex session, coding environment, or AI tool without losing operational context.

### Main Objective

- Maintain a detailed, restartable project handoff document for `D:\Harvard\Poetry Model Project` so future AI assistants, Codex sessions, developers, researchers, or the user can continue work without context loss.

### Current Stage

- Handoff-document update stage. The repository has a prior initial `OFFLOADING.md`, user-provided current git status, and multiple modified/untracked files that need direct verification once shell access works.

### Current Working Direction

- Continue by reading `AGENTS.md` and `OFFLOADING.md`, then inspect the repository contents directly, verify the user-provided git status, identify the project architecture and commands, and update this handoff with concrete file-level details after any substantive work.

## 2. What Has Been Done

- Created the required initial `OFFLOADING.md` handoff document in a prior task.
  - Details: The prior handoff was created from the user-provided `AGENTS.md` instructions and environment context after PowerShell workspace inspection failed with `windows sandbox: spawn setup refresh`.
  - Why it matters: The repository has the required CRAFT-based handoff location for preserving project continuity after substantive work.
  - Files affected: `OFFLOADING.md`

- Captured standing project-continuity rules from `AGENTS.md`.
  - Details: The handoff records that every substantive task must create or update `OFFLOADING.md`, use the CRAFT method when updating it, preserve useful prior content, avoid invented facts, mark unknowns clearly, prefer PowerShell-compatible commands on Windows, and document failures as well as successes.
  - Why it matters: These rules are the controlling workflow for future AI or developer work in this repository.
  - Files affected: `OFFLOADING.md`

- Attempted repository inspection during the prior offloading task.
  - Details: PowerShell commands to list files and read `AGENTS.md`/`OFFLOADING.md` failed before output could be returned.
  - Why it matters: The earlier handoff intentionally marked project implementation details as `Unknown` or `Needs verification`.
  - Files affected: None directly from the failed inspection attempts.

- Updated this handoff from user-provided repository status and existing handoff text.
  - Details: The user supplied the repository root, current `git status --short` output, recent commits, tracked files, and the existing `OFFLOADING.md` content. This update incorporates those details while clearly marking direct disk verification as blocked.
  - Why it matters: The handoff now contains more actionable state than the initial version, including known modified/untracked paths and the current verification blocker.
  - Files affected: `OFFLOADING.md`

- Attempted direct workspace inspection again during this update.
  - Details: The following PowerShell commands were attempted from `D:\Harvard\Poetry Model Project`, but each failed with `windows sandbox: spawn setup refresh`:

    ```powershell
    Get-ChildItem -Force
    Get-Content -Raw -LiteralPath AGENTS.md
    if (Test-Path -LiteralPath OFFLOADING.md) { Get-Content -Raw -LiteralPath OFFLOADING.md } else { '<missing>' }
    git status --short
    ```

  - Why it matters: The current update could not independently verify files on disk. It is based on explicit user-provided repository context and must be rechecked once shell execution works.
  - Files affected: `OFFLOADING.md`

- Added a Windows sandbox workaround to the `cxh` launcher.
  - Details: The nested Codex CLI can fail with `windows sandbox: spawn setup refresh` when it tries to use the Windows shell sandbox. The repo-controlled `scripts/cxh-run.ps1` now accepts `--no-sandbox` and `--danger-full-access`, which switch the nested Codex call from `--sandbox workspace-write` to `--sandbox danger-full-access`. The updated launcher was installed with `powershell -ExecutionPolicy Bypass -File .\scripts\install_cxh.ps1`.
  - Why it matters: The `cxh` command itself can work, but nested Codex shell access may fail under the Windows sandbox. The new flag gives a practical local workaround for trusted projects.
  - Files affected: `scripts/cxh-run.ps1`, `docs/11_codex_handoff_automation.md`, `OFFLOADING.md`

- Made plain `cxh "task"` use the Windows sandbox workaround by default.
  - Details: Updated `scripts/cxh-run.ps1` so `$NoSandbox` defaults to `true`. This means `cxh "task"` now calls Codex with `--sandbox danger-full-access` unless the user explicitly passes `--safe-sandbox` or `--workspace-write`. Reinstalled the global launcher with `powershell -ExecutionPolicy Bypass -File .\scripts\install_cxh.ps1`.
  - Why it matters: The user asked to type only `cxh "task"` without extra flags. The default now avoids the known `windows sandbox: spawn setup refresh` failure.
  - Files affected: `scripts/cxh-run.ps1`, `docs/11_codex_handoff_automation.md`, `OFFLOADING.md`

## 3. Current State

| Item | Current Status | Notes |
|---|---|---|
| Repository path | User-provided | `D:\Harvard\Poetry Model Project` |
| Operating system | Known from user/developer context | Windows. Prefer PowerShell commands. |
| Current date | Known from environment | 2026-05-23. |
| `AGENTS.md` | User-provided as untracked; direct file read blocked | The user pasted its instructions into the chat. On-disk contents still need verification. |
| `OFFLOADING.md` | Being updated directly | The user provided the existing content. This update replaces/refreshes it with the latest known status and the repeated shell blocker. |
| Shell inspection | Blocked | PowerShell execution failed with `windows sandbox: spawn setup refresh` during this update and the prior update. |
| Git status | User-provided, needs direct verification | See the detailed modified/untracked file list below. |
| Recent commits | User-provided, needs direct verification | `d7fe895 Roadmap`; `2af0a49 Initialization`. |
| Project purpose | Partially inferred, needs verification | Repository name and docs suggest a poetry model/data/documentation project, but the specific objective must be verified from `README.md` and docs. |
| Package manager | User-provided as likely Python, needs verification | `pyproject.toml` is untracked according to user-provided status. Its contents could not be read. |
| Programming languages/frameworks | Needs verification | Presence of `pyproject.toml`, `src/`, `scripts/`, and `tests/` suggests Python infrastructure may exist, but this is not verified. |
| Data folders | User-provided/tracked list | Tracked templates and placeholder data folders exist; `data/working/` is untracked. Contents need verification. |
| Documentation | User-provided/tracked list | Existing docs include roadmap, model strategy, annotation guide, website architecture, setup, governance, and implementation guide. Additional docs `08` through `11` are untracked. |
| Tests or validation commands | Unknown | No working test or validation command has been verified. |
| `cxh --no-sandbox` | Added and dry-run verified | Use only for trusted local projects when nested Codex reports `windows sandbox: spawn setup refresh`. |
| Plain `cxh "task"` | Updated | Now defaults to `--sandbox danger-full-access`; use `--safe-sandbox` to opt into `workspace-write`. |

### User-Provided Git Status

The user provided this repository status for the current update. It needs direct verification once shell access works:

```text
 M .gitignore
 M README.md
 M data/README.md
 M docs/05_local_setup.md
 M docs/07_step_by_step_implementation_guide.pdf
 M docs/07_step_by_step_implementation_guide.tex
?? .github/
?? AGENTS.md
?? OFFLOADING.md
?? codex_with_handoff.py
?? data/working/
?? docs/08_text_entry_transliteration_workflow.md
?? docs/09_automation_infrastructure.md
?? docs/10_plain_english_automation_guide.md
?? docs/11_codex_handoff_automation.md
?? pyproject.toml
?? scripts/
?? src/
?? tests/
```

### User-Provided Tracked Files

The user provided the following tracked file list. It needs direct verification once shell access works:

```text
.gitignore
CONTENT_LICENSE.md
CONTRIBUTING.md
LICENSE
README.md
data/README.md
data/annotations/.gitkeep
data/context/.gitkeep
data/lexicon/.gitkeep
data/processed/.gitkeep
data/raw/public/.gitkeep
data/templates/events.template.jsonl
data/templates/model_outputs.template.jsonl
data/templates/people.template.jsonl
data/templates/poems.template.jsonl
data/templates/qa_pairs.template.jsonl
data/templates/reviews.template.jsonl
data/templates/sources.template.jsonl
data/templates/terms.template.jsonl
data/templates/themes.template.jsonl
docs/01_project_roadmap.md
docs/02_model_strategy.md
docs/03_data_and_annotation_guide.md
docs/04_website_architecture.md
docs/05_local_setup.md
docs/06_open_source_governance.md
docs/07_step_by_step_implementation_guide.fdb_latexmk
docs/07_step_by_step_implementation_guide.fls
docs/07_step_by_step_implementation_guide.pdf
docs/07_step_by_step_implementation_guide.tex
```

### Current Known Working Commands

- `cxh --dry-run --skip-task "Test normal sandbox prompt"`
- `cxh --dry-run --no-sandbox --skip-task "Test no sandbox prompt"`
- `cxh --dry-run --skip-task "Test simple cxh default"`
- `cxh --dry-run --safe-sandbox --skip-task "Test safe sandbox opt-in"`
- `cxh --help`
- `powershell -ExecutionPolicy Bypass -File .\scripts\install_cxh.ps1`
- `powershell -ExecutionPolicy Bypass -File .\scripts\abshaar.ps1 validate`

### Current Blockers

- PowerShell command execution failed with `windows sandbox: spawn setup refresh`, preventing direct inspection of repository files, git status, and test commands.
- Plain `cxh "task"` now uses the no-sandbox workaround by default. Only use it in trusted local project folders.

### Current Open Questions

- What is the full purpose and current implementation state of the Poetry Model Project?
- Do the on-disk `AGENTS.md` contents exactly match the instructions provided in the user message?
- What changed in `.gitignore`, `README.md`, `data/README.md`, `docs/05_local_setup.md`, and `docs/07_step_by_step_implementation_guide.tex/pdf`?
- What is contained in untracked `.github/`, `codex_with_handoff.py`, `data/working/`, `pyproject.toml`, `scripts/`, `src/`, and `tests/`?
- What setup, test, lint, build, data-processing, or documentation commands should be used?

## 4. Key Decisions and Rationale

| Decision | Rationale | Alternatives Considered | Effect on Future Work |
|---|---|---|---|
| Use the required CRAFT-based `OFFLOADING.md` structure | The user-provided `AGENTS.md` instructions explicitly require this structure after substantive work. | Free-form handoff summary | Future updates should preserve these ten sections and keep them specific. |
| Update `OFFLOADING.md` directly from user-provided repository context | Direct shell inspection failed again, but the user explicitly asked to update the file and supplied current repository state plus existing handoff content. | Stop without editing until shell access works | The handoff is now more useful, but future assistants must verify the file system before making project-specific claims. |
| Mark unverified repository details as `Needs verification` | The instructions prohibit inventing facts, and command execution is blocked. | Treating user-provided status as independently verified | Future work should re-run inspection and correct this document if the user-provided status differs from disk. |
| Prefer PowerShell-compatible workflow notes | The user is on Windows and explicitly prefers PowerShell unless another shell is requested. | Bash/Linux-style instructions | Future commands should be Windows-friendly and copy-pasteable from the project root. |
| Preserve prior failure history in the handoff | Repeated shell failure affects how the next session should proceed. | Omitting transient tool errors | Future assistants can recognize the blocker and know which verification steps still need to be performed. |

## 5. User Preferences and Instructions

### Persistent Preferences

- The user wants detailed offloading documents after substantive project work.
- The user wants to avoid context loss when moving to a new chat, Codex session, coding environment, or AI tool.
- The user prefers practical, precise, implementation-focused writing.
- The user wants the CRAFT method used when helpful and specifically for `OFFLOADING.md`.
- The user wants clear markdown headings, bullet points, checklists, and tables.
- The user does not want vague summaries.
- The user does not want invented facts.
- Unknown or unverified information should be clearly marked as `Unknown` or `Needs verification`.
- The user is on Windows.
- Prefer PowerShell-compatible commands.
- Do not assume Bash is available.
- Preserve operational details such as filenames, paths, commands, decisions, errors, and next steps.

### Project-Specific Instructions

- Read `AGENTS.md` and `OFFLOADING.md` first when continuing the project.
- Update `OFFLOADING.md` after every substantive task.
- A substantive task includes writing code, editing code, debugging, refactoring, creating or modifying files, reviewing the codebase, creating or editing documentation, creating prompts/templates/workflows/scripts, running analysis, making architectural or structural decisions, researching information that affects the project, changing project direction, or producing output that affects project state or future work.
- Preserve useful prior `OFFLOADING.md` content when updating it.
- Remove or revise obsolete information only when it is clearly outdated, incorrect, or replaced by better verified information.
- If a task fails, still update `OFFLOADING.md` with what was attempted, what failed, error messages, current state, and recommended next steps.
- Before finishing a substantive task, verify whether `OFFLOADING.md` answers the required continuity questions in `AGENTS.md`.

### Things to Avoid

- Do not write vague lines such as "Updated files", "Improved project", "Various files were edited", or "Fixed things."
- Do not invent project details that have not been verified.
- Do not assume Unix tools or Bash are available.
- Do not overwrite important files without inspecting them when inspection is available.
- Do not omit errors, blockers, unresolved issues, commands, paths, or decisions that would help future work.
- Do not claim verification was completed when shell execution or file inspection was blocked.

## 6. Important Context a New Chat Must Know

- The user explicitly requires an `OFFLOADING.md` document for continuity in `D:\Harvard\Poetry Model Project`.
- The required offloading method is CRAFT: Context, Role, Action, Format, Tone.
- The offloading document must be detailed, practical, and restartable.
- The latest user task was: "Update the offload document."
- Direct shell inspection failed during this update with `windows sandbox: spawn setup refresh`, so repository contents could not be independently verified.
- The user supplied repository status showing several modified tracked files and many untracked files/folders, including `AGENTS.md`, `OFFLOADING.md`, `codex_with_handoff.py`, `pyproject.toml`, `scripts/`, `src/`, and `tests/`.
- The repository already tracks documentation and data template files, including docs for roadmap, model strategy, data/annotation, website architecture, local setup, governance, and a step-by-step implementation guide.
- The repository also has untracked documentation related to text entry/transliteration, automation infrastructure, plain-English automation guidance, and Codex handoff automation.
- Future assistants should inspect the workspace before making implementation claims, then revise this document with concrete file contents, setup commands, test commands, dependencies, datasets, scripts, and current blockers.
- The user prefers Windows and PowerShell-compatible instructions.

## 7. Next Steps

### Urgent

- [ ] Re-run workspace inspection from `D:\Harvard\Poetry Model Project` once shell access works.
- [ ] Use plain `cxh "task"` for the simple path. Use `cxh --safe-sandbox "task"` only if the Windows sandbox starts working again and you want the original workspace-write mode.
- [ ] Verify that `AGENTS.md` exists on disk and matches the instructions provided in the user message.
- [ ] Verify the current `git status --short` output and reconcile it against the user-provided status above.
- [ ] Read `README.md`, `docs/01_project_roadmap.md`, `docs/02_model_strategy.md`, and `docs/03_data_and_annotation_guide.md` to confirm the project purpose and current technical direction.
- [ ] Inspect untracked `pyproject.toml`, `src/`, `scripts/`, and `tests/` to identify setup, runtime, and test commands.
- [ ] Update this `OFFLOADING.md` with verified project-specific context after inspection.

### Soon

- [ ] Review modified tracked files and summarize what changed in `.gitignore`, `README.md`, `data/README.md`, `docs/05_local_setup.md`, and `docs/07_step_by_step_implementation_guide.tex/pdf`.
- [ ] Inspect untracked `codex_with_handoff.py` and docs `08` through `11` to understand the handoff/automation workflow.
- [ ] Identify whether the project uses Python packaging, pytest, linting, type checking, LaTeX build tooling, or documentation generation.
- [ ] Record any existing errors, blockers, or incomplete work discovered in the repository.

### Optional Improvements

- [ ] Add a concise repository file map after direct inspection succeeds.
- [ ] Add a command reference table for common project workflows.
- [ ] Add a short chronology of major project decisions after reviewing prior materials and commit history.
- [ ] Add a verification matrix for data templates, scripts, tests, documentation, and generated PDFs.

## 8. Restart Prompt

Copy and paste this into a new chat or Codex session:

> I am continuing a project with an `AGENTS.md` file and an `OFFLOADING.md` handoff document.
>
> First, read `AGENTS.md` and `OFFLOADING.md`.
>
> The purpose of this project is: continue work in `D:\Harvard\Poetry Model Project` without context loss. The project appears to involve a poetry model, data templates, documentation, setup/governance guidance, and automation/handoff workflows, but the full project-specific purpose needs verification from repository files.
>
> Current state: `OFFLOADING.md` has been updated from user-provided repository status because direct PowerShell inspection failed with `windows sandbox: spawn setup refresh`. User-provided status shows modified tracked files `.gitignore`, `README.md`, `data/README.md`, `docs/05_local_setup.md`, `docs/07_step_by_step_implementation_guide.pdf`, and `docs/07_step_by_step_implementation_guide.tex`; it also shows untracked `.github/`, `AGENTS.md`, `OFFLOADING.md`, `codex_with_handoff.py`, `data/working/`, docs `08` through `11`, `pyproject.toml`, `scripts/`, `src/`, and `tests/`.
>
> Important files: `AGENTS.md`, `OFFLOADING.md`, `README.md`, `data/README.md`, `docs/01_project_roadmap.md`, `docs/02_model_strategy.md`, `docs/03_data_and_annotation_guide.md`, `docs/04_website_architecture.md`, `docs/05_local_setup.md`, `docs/06_open_source_governance.md`, `docs/07_step_by_step_implementation_guide.tex`, `docs/07_step_by_step_implementation_guide.pdf`, `pyproject.toml`, `codex_with_handoff.py`, `scripts/`, `src/`, `tests/`, and `data/templates/*.template.jsonl`.
>
> What has already been done: The offloading document structure was created using the required CRAFT sections; user preferences and project continuity rules were recorded; current user-provided repository status was added; direct inspection attempts and the `windows sandbox: spawn setup refresh` failure were documented.
>
> Next steps: inspect the repository from `D:\Harvard\Poetry Model Project`, verify `AGENTS.md`, verify git status, read the README and core docs, inspect untracked Python/source/test/automation files, identify working commands, then update `OFFLOADING.md` with concrete verified details.
>
> Follow these preferences:
> - Use precise, practical markdown.
> - Preserve context.
> - Do not invent facts.
> - Mark unknowns as "Unknown" or "Needs verification."
> - Prefer PowerShell commands because I am on Windows.
> - Update `OFFLOADING.md` after substantive work.

## 9. Risks, Gaps, and Things to Verify

| Risk, Gap, or Unknown | Why It Matters | How to Verify or Resolve |
|---|---|---|
| Repository contents could not be independently inspected | The current handoff relies on user-provided status rather than direct file reads. | Run `Get-ChildItem -Force` from `D:\Harvard\Poetry Model Project` once shell access works. |
| `AGENTS.md` file on disk was not verified | The user provided instructions, but the file itself may differ or may not exist on disk. | Read `AGENTS.md` directly and reconcile differences. |
| Current `OFFLOADING.md` state before editing was not independently verified | The user pasted the existing content, but direct read failed. | Inspect the file directly once shell access works and confirm this update is present. |
| Modified tracked files have unknown changes | Future work could accidentally overwrite or misunderstand user changes. | Run `git diff -- .gitignore README.md data/README.md docs/05_local_setup.md docs/07_step_by_step_implementation_guide.tex` and inspect the PDF generation context. |
| Untracked source, scripts, tests, and package config are unverified | These likely define current implementation behavior and commands. | Inspect `pyproject.toml`, `src/`, `scripts/`, and `tests/`; then document commands and behavior here. |
| Project purpose and implementation details are only partially inferred | Future assistants need concrete project context to continue actual work. | Read `README.md`, core docs, data templates, and relevant scripts. |
| No test or validation command is known | Future changes cannot be safely verified without project commands. | Identify and document setup/test/run commands after inspecting dependency files. |
| Shell tooling failure may recur | It prevents direct verification and normal development workflow. | Retry shell commands in a fresh session or fix the local sandbox issue before doing implementation-heavy work. |

## 10. Compact Version

This repository is `D:\Harvard\Poetry Model Project`. The user requires a detailed `OFFLOADING.md` handoff after every substantive task, using CRAFT and preserving enough context for a new assistant or coding session to continue without the old chat. The project appears to involve a poetry model with documentation, data templates, possible Python source/tests, and automation/handoff workflows, but the exact implementation purpose needs verification from files. This update incorporated user-provided repository status: modified tracked files include `.gitignore`, `README.md`, `data/README.md`, `docs/05_local_setup.md`, and `docs/07_step_by_step_implementation_guide.tex/pdf`; untracked files/folders include `.github/`, `AGENTS.md`, `OFFLOADING.md`, `codex_with_handoff.py`, `data/working/`, docs `08` through `11`, `pyproject.toml`, `scripts/`, `src/`, and `tests/`. Direct PowerShell inspection failed again with `windows sandbox: spawn setup refresh`, so all disk-specific claims must be verified later. Future work should first inspect the repository, verify `AGENTS.md`, verify git status, read the README/core docs, identify setup/test/run commands, and then update `OFFLOADING.md` again. The user is on Windows, prefers PowerShell-compatible commands, precise markdown, no invented facts, and explicit `Unknown` or `Needs verification` labels for unverified information.
