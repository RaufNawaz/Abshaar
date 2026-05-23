# AGENTS.md

## Purpose

This file contains standing instructions for Codex or any AI coding, writing, research, or project assistant working in this repository.

The main purpose of this file is to prevent context loss.

After every substantive task, the assistant must create or update a detailed project offloading document named:

```text
OFFLOADING.md
```

The `OFFLOADING.md` file must allow the user to pause the project and restart it later in a new chat, Codex session, coding environment, or AI tool without needing to re-explain the full project history, context, decisions, current state, or next steps.

Project continuity is a required part of the work.

---

# Core Rule

After every substantive task, update `OFFLOADING.md`.

A substantive task includes, but is not limited to:

- Writing code.
- Editing code.
- Debugging.
- Refactoring.
- Creating files.
- Modifying files.
- Reviewing a codebase.
- Creating documentation.
- Editing documentation.
- Creating prompts, templates, workflows, or scripts.
- Running analysis.
- Making architectural decisions.
- Making project structure decisions.
- Researching information that affects the project.
- Changing the project direction.
- Producing any output that affects the project’s state, logic, files, or future work.

If the task is extremely small and does not affect project state, an offloading update may be unnecessary. In that case, explicitly say why.

When uncertain, update `OFFLOADING.md`.

---

# Required Offloading Document

The assistant must create or update:

```text
OFFLOADING.md
```

The document must be detailed enough that another AI assistant, Codex session, developer, researcher, or future version of the user can continue the project immediately.

Do not write vague summaries.

Do not omit small details that would help a future assistant continue the project.

Do not invent facts.

If information is missing, unclear, or unverified, write:

```text
Unknown
```

or:

```text
Needs verification
```

---

# Required Method: CRAFT

The `OFFLOADING.md` document must use the CRAFT method:

- C: Context
- R: Role
- A: Action
- F: Format
- T: Tone

Use this structure to preserve the full project state in a practical and restartable way.

---

# C: Context

When updating `OFFLOADING.md`, summarize the full project context so far.

Include:

- What the project is trying to accomplish.
- The broader purpose or end goal.
- The user’s role, preferences, constraints, and priorities.
- Important background information from the conversation.
- Relevant files.
- Relevant folders.
- Codebase structure.
- Datasets.
- Documents.
- Links.
- Tools used.
- Commands run.
- Environment details.
- Operating system details.
- Package managers.
- Frameworks.
- Programming languages.
- Assumptions made so far.
- Terminology, naming conventions, or project-specific meanings.
- Current blockers.
- Current risks.
- Current open questions.
- Any decisions already made.

The goal is not just to describe what exists. The goal is to explain why it exists, how it connects, and what should happen next.

---

# R: Role

Write `OFFLOADING.md` as if you are a senior project handoff assistant preparing another capable AI agent, Codex session, developer, researcher, or future ChatGPT conversation to continue immediately.

The next assistant should be able to understand:

- What the project is.
- Why the project matters.
- What has already happened.
- What files matter.
- What has changed.
- What the current state is.
- What the user wants.
- What the user prefers.
- What decisions have been made.
- What risks or uncertainties remain.
- What needs to happen next.
- What mistakes to avoid.

Be practical, precise, and implementation-focused.

Do not include generic filler.

Do not include irrelevant conversation history.

Do not include hidden reasoning or private chain-of-thought.

---

# A: Action

Create or update `OFFLOADING.md` using the exact section structure below.

Preserve useful prior content.

Update old content when the project changes.

Remove or revise obsolete information only when it is clearly outdated, incorrect, or replaced by better information.

Do not delete important history unless it is no longer useful.

---

## 1. Project Overview

Include:

- One-paragraph project summary.
- Main objective.
- Broader purpose.
- Current project stage.
- Current working direction.

Required format:

```md
## 1. Project Overview

[One detailed paragraph explaining the project, its purpose, the user’s goal, and the current stage.]

### Main Objective

- [Main objective]

### Current Stage

- [Current stage]

### Current Working Direction

- [What should happen next]
```

---

## 2. What Has Been Done

List completed steps in chronological or logical order.

Include:

- User requests already handled.
- Files created.
- Files modified.
- Scripts written.
- Prompts created.
- Documentation written.
- Commands run.
- Tools used.
- Research completed.
- Bugs fixed.
- Errors encountered.
- Outputs generated.
- Decisions made.
- Attempted approaches that did not work.
- Anything that changed the project state.

Required format:

```md
## 2. What Has Been Done

- [Completed step 1]
  - Details:
  - Why it matters:
  - Files affected:

- [Completed step 2]
  - Details:
  - Why it matters:
  - Files affected:
```

Be specific. Do not write vague lines such as “Updated files” or “Improved project.”

Instead, write which files changed, what changed, and why.

---

## 3. Current State

Explain exactly where the project stands right now.

Include:

- Latest version of important files.
- Current file paths.
- Current scripts.
- Current commands.
- Current project structure.
- Current working setup.
- Current errors.
- Current blockers.
- Current open questions.
- Current assumptions.
- Any files that need to be checked before continuing.

Use a table when useful.

Required format:

```md
## 3. Current State

| Item | Current Status | Notes |
|---|---|---|
| [File, feature, script, or task] | [Status] | [Important details] |
```

Also include:

```md
### Current Known Working Commands

- [Command 1]
- [Command 2]

### Current Blockers

- [Blocker or “None known.”]

### Current Open Questions

- [Question or “None known.”]
```

---

## 4. Key Decisions and Rationale

Record major decisions and explain why they were made.

Include:

- Decision.
- Rationale.
- Alternatives considered.
- Why alternatives were rejected, if relevant.
- Effect on future work.

Required format:

```md
## 4. Key Decisions and Rationale

| Decision | Rationale | Alternatives Considered | Effect on Future Work |
|---|---|---|---|
| [Decision] | [Reason] | [Alternatives] | [Effect] |
```

If no major decisions have been made, write:

```text
No major decisions recorded yet.
```

---

## 5. User Preferences and Instructions

Capture all user preferences that affect future work.

Include:

- Formatting preferences.
- Tone preferences.
- Workflow preferences.
- Coding preferences.
- Documentation preferences.
- Citation preferences.
- Output format preferences.
- Operating system constraints.
- Terminal or shell constraints.
- “Do not do this” instructions.
- Any recurring instructions that should persist across sessions.

Known preferences for this user and project:

- The user wants detailed offloading documents after substantive project work.
- The user wants to avoid context loss when moving to a new chat, Codex session, coding environment, or AI tool.
- The user prefers practical, precise, implementation-focused writing.
- The user wants the CRAFT method used when helpful.
- The user wants clear markdown headings, bullet points, checklists, and tables.
- The user does not want vague summaries.
- The user does not want invented facts.
- Unknown or unverified information should be clearly marked.
- The user is on Windows.
- Prefer PowerShell-compatible commands.
- Do not assume Bash is available.
- When terminal instructions are needed, use PowerShell unless the user explicitly asks for Bash, WSL, Git Bash, Linux, or macOS instructions.
- Preserve operational details such as filenames, paths, commands, decisions, errors, and next steps.

If new preferences appear, add them to this section.

Required format:

```md
## 5. User Preferences and Instructions

### Persistent Preferences

- [Preference]

### Project-Specific Instructions

- [Instruction]

### Things to Avoid

- [Thing to avoid]
```

---

## 6. Important Context a New Chat Must Know

Summarize anything that would be hard to infer from the files alone.

Include:

- Why the project exists.
- What problem the user is trying to solve.
- Any hidden assumptions.
- Any dependencies between files.
- Any workflow expectations.
- Any relevant conversation history.
- Any important user frustrations.
- Any priorities.
- How the project pieces connect.
- What the next assistant should understand before making changes.

Required format:

```md
## 6. Important Context a New Chat Must Know

- [Important context item]
- [Important context item]
- [Important context item]
```

This section should prevent the next assistant from asking the user to repeat context.

---

## 7. Next Steps

Provide a prioritized checklist.

Separate urgent next actions from optional improvements.

Each item must be specific and actionable.

Required format:

```md
## 7. Next Steps

### Urgent

- [ ] [Specific next action]
- [ ] [Specific next action]

### Soon

- [ ] [Specific next action]
- [ ] [Specific next action]

### Optional Improvements

- [ ] [Optional improvement]
- [ ] [Optional improvement]
```

Avoid vague tasks such as “continue working.”

Instead, write exactly what should be done next.

---

## 8. Restart Prompt

Write a ready-to-copy prompt that the user can paste into a new chat, Codex session, coding environment, or AI tool.

The restart prompt must tell the next assistant:

- What the project is.
- Where the project stands.
- Which files matter.
- What has already been done.
- What to do next.
- What preferences to follow.
- What to avoid.
- That `AGENTS.md` and `OFFLOADING.md` should be read first.
- That `OFFLOADING.md` must be updated after substantive work.

Required format:

```md
## 8. Restart Prompt

Copy and paste this into a new chat or Codex session:

> I am continuing a project with an `AGENTS.md` file and an `OFFLOADING.md` handoff document.
>
> First, read `AGENTS.md` and `OFFLOADING.md`.
>
> The purpose of this project is: [project purpose].
>
> Current state: [current state].
>
> Important files: [important files].
>
> What has already been done: [summary].
>
> Next steps: [next steps].
>
> Follow these preferences:
> - Use precise, practical markdown.
> - Preserve context.
> - Do not invent facts.
> - Mark unknowns as “Unknown” or “Needs verification.”
> - Prefer PowerShell commands because I am on Windows.
> - Update `OFFLOADING.md` after substantive work.
```

The restart prompt must be updated as the project evolves.

---

## 9. Risks, Gaps, and Things to Verify

Identify anything uncertain, incomplete, risky, or dependent on external conditions.

Include:

- Unknown project state.
- Missing files.
- Untested commands.
- Environment assumptions.
- Dependency issues.
- Tool limitations.
- Possible user clarification needed.
- Anything that could break.
- Anything that could confuse the next assistant.
- Anything that must be verified before continuing.

Required format:

```md
## 9. Risks, Gaps, and Things to Verify

| Risk, Gap, or Unknown | Why It Matters | How to Verify or Resolve |
|---|---|---|
| [Issue] | [Reason] | [Action] |
```

If there are no known risks, write:

```text
None known.
```

---

## 10. Compact Version

End with a shorter version of the handoff that can be pasted quickly into another chat.

Include:

- Project purpose.
- Current state.
- Key files.
- User preferences.
- Immediate next steps.

Required format:

```md
## 10. Compact Version

[Short but useful summary of the project, current state, key files, preferences, and next steps.]
```

The compact version should be detailed enough to help, but short enough to paste quickly.

---

# F: Format

Use markdown.

Use:

- Clear headings.
- Bullet points.
- Numbered lists.
- Checklists.
- Tables where useful.
- Code blocks for commands, paths, prompts, and file contents.

Avoid vague wording.

Do not write:

- “Some changes were made.”
- “The project was improved.”
- “Various files were edited.”
- “Updated the code.”
- “Fixed things.”

Instead, write:

- Which files changed.
- What changed.
- Why the change matters.
- What remains to be done.
- What commands were run.
- What errors appeared.
- What decisions were made.

Keep the document detailed but organized.

Do not include irrelevant conversation filler.

Do not include private chain-of-thought.

Do not invent information.

If information is missing, write:

```text
Unknown
```

or:

```text
Needs verification
```

---

# T: Tone

Use a professional, precise, practical tone.

Write like a careful project manager handing work to a capable successor.

Prioritize:

- Continuity.
- Clarity.
- Usefulness.
- Specificity.
- Implementation detail.
- Accuracy.
- Restartability.

Avoid:

- Vague summaries.
- Overly casual language.
- Unverified claims.
- Irrelevant detail.
- Repeating unnecessary conversation history.

---

# Required Workflow for Every Substantive Task

For every substantive task, follow this workflow:

1. Understand the user’s request.
2. Inspect relevant files before editing when possible.
3. Identify the current project state.
4. Make the requested changes or produce the requested output.
5. Verify the result where practical.
6. Update `OFFLOADING.md`.
7. In the final response, briefly state:
   - What was done.
   - Which files were changed.
   - Whether `OFFLOADING.md` was updated.
   - Any remaining issues or next steps.

If a task fails, still update `OFFLOADING.md` with:

- What was attempted.
- What failed.
- Error messages.
- Current project state.
- Recommended next steps.

---

# Required Quality Checklist for OFFLOADING.md

Before finishing any substantive task, check whether `OFFLOADING.md` answers these questions:

- Can a new assistant understand the project without reading the old chat?
- Does it explain the project goal?
- Does it explain the current stage?
- Does it list what has already been done?
- Does it identify the latest important files?
- Does it include user preferences?
- Does it include decisions and rationale?
- Does it include risks and unknowns?
- Does it include specific next steps?
- Does it include a ready-to-copy restart prompt?
- Does it include a compact version?
- Are unknowns clearly marked?
- Are filenames, commands, paths, and outputs included where relevant?
- Are errors, blockers, and unresolved issues documented?
- Is the document detailed but organized?

If the answer to any of these is no, improve `OFFLOADING.md` before finishing.

---

# Windows-Specific Instruction

The user is on Windows.

Prefer Windows-compatible instructions.

When providing terminal commands, prefer PowerShell.

Do not assume Bash is available.

Use PowerShell syntax unless the user explicitly asks for Bash, WSL, Git Bash, Linux, or macOS instructions.

For example, prefer:

```powershell
Get-ChildItem
```

instead of:

```bash
ls
```

Prefer:

```powershell
Set-Content
```

instead of:

```bash
cat > file
```

---

# Command and Script Guidance

When creating commands or scripts:

- Prefer PowerShell for Windows.
- Make commands copy-paste friendly.
- Avoid assuming Unix tools are installed.
- Explain where the command should be run.
- Mention whether the command should be run from the project root.
- Avoid destructive commands unless the user explicitly asks for them.
- If a command modifies files, say which files it is expected to modify.
- If a command depends on a tool such as Node.js, npm, Python, Git, or Codex CLI, mention that dependency.

---

# File Editing Rules

When editing project files:

- Inspect existing files first when possible.
- Preserve useful existing content.
- Avoid overwriting important files without need.
- Do not delete user work unless explicitly requested.
- Prefer small, clear changes.
- Keep filenames and paths explicit.
- Document changes in `OFFLOADING.md`.
- If creating a new file, explain why it exists.
- If modifying a script, explain what behavior changed.

---

# Verification Rules

When practical, verify work before finishing.

Verification may include:

- Running tests.
- Running a script.
- Checking file contents.
- Checking formatting.
- Checking command output.
- Reviewing changed files.
- Confirming that expected files exist.

If verification was not possible, write that clearly in both the final response and `OFFLOADING.md`.

Use this format:

```text
Verification: Not run because [reason].
```

or:

```text
Verification: Completed using [command or method].
```

---

# Final Response Requirement

At the end of a substantive task, respond briefly with this structure:

```text
Done. I completed [brief summary of work].

Changed files:
- [file 1]
- [file 2]

Offloading document:
- Updated `OFFLOADING.md`.

Verification:
- [What was checked, or “Not run because...”]

Remaining issues:
- [Issue or “None known.”]
```

If no `OFFLOADING.md` update was necessary, say:

```text
No `OFFLOADING.md` update was necessary because [specific reason].
```

Do not claim that `OFFLOADING.md` was updated unless it was actually updated.

---

# Default Behavior

Unless the user gives different instructions:

- Be precise.
- Be practical.
- Preserve context.
- Use markdown.
- Prefer PowerShell.
- Update `OFFLOADING.md` after substantive work.
- Do not invent facts.
- Mark unknowns clearly.
- Keep the project restartable.