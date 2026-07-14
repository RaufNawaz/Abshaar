# Claude Project Instructions

The canonical repository instructions are in `AGENTS.md`. Read that file in
full and follow it, including the required CRAFT-format `OFFLOADING.md` update
after every substantive task.

This project is shared with Codex. Before changing anything:

1. Read `AGENTS.md`, `OFFLOADING.md`, and any task-specific log such as
   `Bulleh Shah/CORPUS_BUILD_LOG.md`.
2. Run `git status --short --branch` and inspect existing diffs for the files in
   scope.
3. Preserve all pre-existing modified and untracked work. Do not revert, delete,
   overwrite, stage, or commit another assistant's changes unless Rauf asks.
4. Re-read each target file immediately before editing because Codex may have
   changed it during the session.

After substantive work:

1. Update the canonical docs, schemas, templates, tests, and task logs affected
   by the work.
2. Update `OFFLOADING.md` with exact files, commands, outputs, errors, decisions,
   current state, and next steps.
3. Run proportionate verification and re-check `git status` plus relevant diffs.
4. Report what changed, what was verified, and what remains.

Important current safety notes are maintained in `OFFLOADING.md`; do not rely on
this file for corpus counts or project stage. Do not run broad staging commands
such as `git add .`, and do not remove `.git/index.lock` without first verifying
that no active Git process owns it.
