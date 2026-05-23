# Codex Handoff Automation

This file explains how to finish the `OFFLOADING.md` automation and what errors
were found.

## What the Automation Is Supposed to Do

The script:

```text
codex_with_handoff.py
```

is meant to do two jobs:

1. Run a normal Codex task.
2. After the task, ask Codex to update `OFFLOADING.md` so the project can be
   restarted later without losing context.

This supports the rule in `AGENTS.md`: after every substantive task,
`OFFLOADING.md` should be created or updated.

## Main Error Found

On this Windows machine, running:

```powershell
codex --help
```

failed with:

```text
codex.ps1 cannot be loaded because running scripts is disabled on this system.
```

Why this happens:

- npm installed a PowerShell wrapper named `codex.ps1`;
- PowerShell blocks local `.ps1` scripts unless execution policy allows them;
- so `codex` resolves to `codex.ps1` and fails before Codex can run.

A second related issue was found with the custom `cxh` wrapper:

- the setup created both `cxh.ps1` and `cxh.cmd` in
  `C:\Users\raufn\codex-handoff-bin`;
- PowerShell resolved `cxh` to `cxh.ps1` before `cxh.cmd`;
- that meant typing `cxh ...` failed before the `.cmd` bypass wrapper could run.

## Fix Applied

`codex_with_handoff.py` now prefers:

```text
codex.cmd
```

instead of:

```text
codex.ps1
```

This avoids the PowerShell execution-policy problem.

The script now searches in this order:

1. `codex.cmd`
2. `codex.exe`
3. `codex`

It also passes:

```text
--cd D:\Harvard\Poetry Model Project
```

to Codex so Codex works inside this repository even if the script is launched
from another folder.

The `cxh` launcher was also fixed:

- added `scripts/cxh-run.ps1`;
- added `scripts/cxh.cmd`;
- added `scripts/install_cxh.ps1`;
- installed the fixed launcher to `C:\Users\raufn\codex-handoff-bin`;
- moved the old blocked `cxh.ps1` to a timestamped backup;
- verified that `Get-Command cxh -All` now resolves `cxh` to `cxh.cmd`.

The important pattern is:

```text
cxh
  -> C:\Users\raufn\codex-handoff-bin\cxh.cmd
  -> powershell -ExecutionPolicy Bypass -File cxh-run.ps1
  -> codex.cmd exec ...
```

## Dry Run Mode

A new dry-run mode was added:

```powershell
py -3.14 .\codex_with_handoff.py --dry-run --skip-task "Update the offloading document"
```

Dry run does not call Codex. It only:

- confirms which Codex executable will be used;
- prints the command that would run;
- writes the generated handoff prompt to:

```text
data/cache/codex_handoff_prompt.md
```

This is useful for debugging without spending model calls or changing files.

## Normal Usage

Preferred global command after installing the fixed launcher:

```powershell
cxh --dry-run --skip-task "Test handoff prompt"
cxh --skip-task "Update OFFLOADING.md after recent work"
cxh "Do this Codex task, then update OFFLOADING.md"
```

As of the latest launcher update, plain `cxh "task"` uses the Windows sandbox
workaround by default. Internally, it calls Codex with:

```text
--sandbox danger-full-access
```

This is intentional because the normal Windows sandbox has been failing with
`windows sandbox: spawn setup refresh`.

If Codex prints this Windows sandbox error:

```text
windows sandbox: spawn setup refresh
```

the default `cxh "task"` path should already avoid it. You can still be explicit:

```powershell
cxh --dry-run --no-sandbox --skip-task "Test handoff prompt"
cxh --no-sandbox --skip-task "Update OFFLOADING.md after recent work"
```

Use `cxh` only for trusted local projects. To opt back into the original
`workspace-write` sandbox, run:

```powershell
cxh --safe-sandbox "Do this task using workspace-write sandbox"
```

If the global launcher ever breaks, reinstall it from this repo:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\install_cxh.ps1
```

You can still call the Python version directly:

Run a Codex task and then update `OFFLOADING.md`:

```powershell
py -3.14 .\codex_with_handoff.py "Add a new validation command to the automation CLI"
```

Only update `OFFLOADING.md` after manual work:

```powershell
py -3.14 .\codex_with_handoff.py --skip-task "Manual work was completed; update OFFLOADING.md"
```

Preview what would happen:

```powershell
py -3.14 .\codex_with_handoff.py --dry-run --skip-task "Preview handoff update"
```

## Things That Must Be True Before It Works

Run these checks:

```powershell
codex.cmd --help
codex.cmd doctor
```

If `codex.cmd doctor` reports login/auth problems, run:

```powershell
codex.cmd login
```

The script cannot update `OFFLOADING.md` unless the Codex CLI is installed,
working, and authenticated.

## Why This Still Needs Care

This script launches Codex from inside a Codex-related project. That means it is
possible for one agent to call another agent. This is useful, but it can be
confusing.

Use `--dry-run` first when debugging.

Use `--skip-task` when you have already done the actual project work and only
want the handoff updated.

## Recommended Completion Path

1. Run:

   ```powershell
   codex.cmd doctor
   ```

2. Fix any Codex login/auth/config issue it reports.

3. Run:

   ```powershell
   py -3.14 .\codex_with_handoff.py --dry-run --skip-task "Test handoff prompt"
   ```

4. Confirm it writes:

   ```text
   data/cache/codex_handoff_prompt.md
   ```

5. Run:

   ```powershell
   py -3.14 .\codex_with_handoff.py --skip-task "Create initial OFFLOADING.md for current project state"
   ```

6. Check that `OFFLOADING.md` exists and follows the CRAFT structure required by
   `AGENTS.md`.

7. After future substantive tasks, either:

   ```powershell
   py -3.14 .\codex_with_handoff.py --skip-task "Update OFFLOADING.md after recent work"
   ```

   or run the whole task through the wrapper:

   ```powershell
   py -3.14 .\codex_with_handoff.py "Do the task and update OFFLOADING.md"
   ```

## Verification Performed

The patched script was checked with:

```powershell
py -3.14 -m py_compile codex_with_handoff.py
py -3.14 .\codex_with_handoff.py --dry-run --skip-task "Test handoff prompt"
codex.cmd doctor
```

Results:

- Python syntax check passed.
- Dry run succeeded.
- Dry run wrote the generated handoff prompt to `data/cache/codex_handoff_prompt.md`.
- `codex.cmd doctor` confirmed that the Codex CLI is installed.
- `codex.cmd doctor` also reported missing Codex credentials in this sandboxed
  environment.
- `codex.cmd doctor` reported provider reachability failures from this sandboxed
  environment.
- `powershell -ExecutionPolicy Bypass -File .\scripts\install_cxh.ps1` installed
  the fixed global `cxh` launcher.
- `Get-Command cxh -All` now reports `cxh.cmd`, not `cxh.ps1`.
- `cxh --dry-run --skip-task "Test handoff prompt"` succeeded and wrote a prompt
  file to `data/cache/`.
- `cxh --dry-run --no-sandbox --skip-task "Test no sandbox prompt"` succeeded
  and showed that the wrapper would call Codex with `--sandbox
  danger-full-access`.
- `cxh --dry-run --skip-task "Test simple cxh default"` succeeded and showed that
  the default plain `cxh` path now calls Codex with `--sandbox
  danger-full-access`.
- `cxh --dry-run --safe-sandbox --skip-task "Test safe sandbox opt-in"`
  succeeded and showed that `--safe-sandbox` calls Codex with `--sandbox
  workspace-write`.

What this means:

The script logic is now usable, but the fully automated Codex-to-Codex handoff
will not work until the Codex CLI is authenticated and has network/provider
reachability in the environment where the user runs it.

## Remaining Risks

| Risk | Why It Matters | Fix |
|---|---|---|
| Codex CLI not logged in | The script cannot call Codex | Run `codex.cmd doctor`, then `codex.cmd login` if needed |
| Codex task fails | The handoff update may still run, but the task output may be incomplete | Read terminal output carefully |
| Prompt becomes too long | Very large `OFFLOADING.md` or repo context could exceed model context | Later add context trimming |
| The AI forgets to edit the file | Codex is asked to update `OFFLOADING.md`, but this depends on agent behavior | Check `OFFLOADING.md` after every run |
| Running nested Codex sessions can be confusing | One automation launches another agent | Use `--dry-run` and `--skip-task` when unsure |
