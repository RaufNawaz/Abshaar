---
name: project-mac-migration
description: Abshaar project was Windows/PowerShell-only; now has parallel macOS support
metadata: 
  node_type: memory
  type: project
  originSessionId: c5e768b6-d63c-406c-9d06-0cd64134297b
---

As of 2026-07-04, the user is migrating their dev environment for the Abshaar
project (D:\Harvard\Poetry Model Project, GitHub RaufNawaz/Abshaar, branch
`draft`) from Windows to a Mac. The repo previously hard-assumed Windows +
PowerShell everywhere (AGENTS.md, START_HERE.md, docs/05_local_setup.md,
scripts/*.ps1).

**Why:** the Python core (`src/abshaar/`) was always OS-agnostic (pathlib-based);
only the automation wrapper scripts and docs assumed PowerShell.

**What changed:** added `scripts/abshaar.sh` and `scripts/build_all.sh` as
bash equivalents of the `.ps1` wrappers (same args/behavior), a `.gitattributes`
forcing LF line endings on `*.sh` (and CRLF on `*.ps1`/`*.cmd`) so scripts stay
executable across OSes regardless of a checkout machine's `core.autocrlf`,
macOS setup steps in `docs/05_local_setup.md`, and cross-platform notes in
`AGENTS.md`, `START_HERE.md`, `README.md`, and `docs/09`/`docs/10`.

**Scope note:** the Codex-handoff automation (`scripts/cxh-run.ps1`,
`install_cxh.ps1`, `codex_with_handoff.py`) was deliberately left Windows-only
per the user's choice — it exists solely to work around a Windows PowerShell
execution-policy bug with npm's `codex.ps1` wrapper that doesn't exist on
macOS, so there's nothing to port there.

**How to apply:** when working in this repo, match terminal commands to
whichever OS the session is actually on (infer from path style: `D:\...` vs
`/Users/...`) rather than defaulting to Windows/PowerShell out of habit. If
adding new automation to `scripts/`, add both a `.ps1` and a `.sh` version.
