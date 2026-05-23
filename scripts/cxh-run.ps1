param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$TaskParts
)

$ErrorActionPreference = "Stop"

function Show-Usage {
    Write-Host "Usage:"
    Write-Host "  cxh `"your Codex task`""
    Write-Host "  cxh --skip-task `"Update OFFLOADING.md after recent work`""
    Write-Host "  cxh --dry-run --skip-task `"Preview handoff update`""
    Write-Host "  cxh --safe-sandbox `"Use Codex workspace-write sandbox instead of the Windows workaround`""
}

function Find-Codex {
    $candidates = @("codex.cmd", "codex.exe", "codex")
    foreach ($candidate in $candidates) {
        $command = Get-Command $candidate -ErrorAction SilentlyContinue
        if ($command) {
            return $command.Source
        }
    }
    return $null
}

function Find-RepoRoot {
    param([string]$StartPath)

    $current = Resolve-Path $StartPath
    while ($current) {
        $agentsPath = Join-Path $current "AGENTS.md"
        $gitPath = Join-Path $current ".git"
        if ((Test-Path $agentsPath) -or (Test-Path $gitPath)) {
            return $current.Path
        }

        $parent = Split-Path $current -Parent
        if (-not $parent -or $parent -eq $current.Path) {
            break
        }
        $current = Resolve-Path $parent
    }

    return $null
}

function Ensure-AgentsFile {
    if (Test-Path "AGENTS.md") {
        return
    }

@"
# Project Working Instructions

## Mandatory offloading document

After every substantive task, update `OFFLOADING.md` so the project can be moved to a new chat, Codex session, or AI tool without losing context.

Use the CRAFT method.

### C: Context
Preserve the project purpose, user goals, constraints, relevant files, tools, assumptions, and background information.

### R: Role
Write as a senior project handoff assistant preparing another AI agent, developer, researcher, or future version of ChatGPT/Codex to continue immediately.

### A: Action
Maintain these sections in `OFFLOADING.md`:

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

### F: Format
Use markdown headings, bullets, checklists, and tables where useful.
Include filenames, paths, commands, errors, decisions, unresolved issues, and next actions.
Do not invent missing facts. Mark unknowns as "Unknown" or "Needs verification."

### T: Tone
Professional, precise, practical, and continuity-focused.

At the end of every substantive task:
- update `OFFLOADING.md`, or
- explain clearly why no offloading update was necessary.
"@ | Set-Content -Encoding UTF8 "AGENTS.md"

    Write-Host "Created AGENTS.md"
}

$SkipTask = $false
$DryRun = $false
$NoSandbox = $true
$Help = $false
$Remaining = New-Object System.Collections.Generic.List[string]

foreach ($part in $TaskParts) {
    switch ($part) {
        "--skip-task" { $SkipTask = $true; continue }
        "--dry-run" { $DryRun = $true; continue }
        "--no-sandbox" { $NoSandbox = $true; continue }
        "--danger-full-access" { $NoSandbox = $true; continue }
        "--safe-sandbox" { $NoSandbox = $false; continue }
        "--workspace-write" { $NoSandbox = $false; continue }
        "--help" { $Help = $true; continue }
        "-h" { $Help = $true; continue }
        default { $Remaining.Add($part) }
    }
}

if ($Help) {
    Show-Usage
    exit 0
}

if ($Remaining.Count -eq 0) {
    Show-Usage
    exit 1
}

$Task = $Remaining -join " "
$OffloadingFile = "OFFLOADING.md"
$LaunchDir = (Get-Location).Path
$RepoRoot = Find-RepoRoot $LaunchDir

if (-not $RepoRoot) {
    Write-Host "Could not find a repository root."
    Write-Host "Run cxh from inside a project folder that contains AGENTS.md or .git."
    exit 1
}

Set-Location $RepoRoot
$Codex = Find-Codex

if (-not $Codex) {
    Write-Host "Codex CLI not found."
    Write-Host "Install it with:"
    Write-Host "  npm i -g @openai/codex"
    exit 1
}

Ensure-AgentsFile

Write-Host "Using Codex executable: $Codex"

$SandboxArgs = if ($NoSandbox) {
    @("--sandbox", "danger-full-access")
} else {
    @("--sandbox", "workspace-write")
}

if ($NoSandbox) {
    Write-Host "Codex sandbox mode: danger-full-access"
    Write-Host "Use this only for trusted local projects when the Windows sandbox fails."
} else {
    Write-Host "Codex sandbox mode: workspace-write"
}

if (-not $SkipTask) {
    Write-Host ""
    Write-Host "Running Codex task..."
    Write-Host ""

    if ($DryRun) {
        Write-Host "Dry run: would run:"
        Write-Host "$Codex exec $($SandboxArgs -join ' ') --cd `"$RepoRoot`" `"$Task`""
    } else {
        & $Codex exec @SandboxArgs --cd $RepoRoot $Task
        if ($LASTEXITCODE -ne 0) {
            Write-Host ""
            Write-Host "Codex task failed. I will still try to update the offloading document."
            Write-Host ""
        }
    }
}

Write-Host ""
Write-Host "Updating $OffloadingFile..."
Write-Host ""

$PromptDir = if (Test-Path "data") { Join-Path $RepoRoot "data\cache" } else { $env:TEMP }
New-Item -ItemType Directory -Force -Path $PromptDir | Out-Null
$PromptPath = Join-Path $PromptDir ("codex_handoff_prompt_" + [guid]::NewGuid().ToString() + ".md")

$GitStatus = git status --short 2>$null
if (-not $GitStatus) { $GitStatus = "No git status available." }

$RecentCommits = git log --oneline -10 2>$null
if (-not $RecentCommits) { $RecentCommits = "No git log available." }

$TrackedFiles = git ls-files 2>$null
if (-not $TrackedFiles) {
    $TrackedFiles = "No tracked files available."
}

$WorkspaceFiles = Get-ChildItem -Recurse -File -Depth 3 |
    Where-Object {
        $_.FullName -notmatch "\\.git\\" -and
        $_.FullName -notmatch "\\data\\cache\\" -and
        $_.FullName -notmatch "\\__pycache__\\"
    } |
    ForEach-Object {
        $_.FullName.Substring($RepoRoot.Length).TrimStart("\")
    }

if (-not $WorkspaceFiles) {
    $WorkspaceFiles = "No workspace file list available."
}

$ExistingOffloading = if (Test-Path $OffloadingFile) {
    Get-Content $OffloadingFile -Raw
} else {
    "No existing OFFLOADING.md found."
}

$Prompt = @"
You are updating the project offloading document.

Create or update `OFFLOADING.md` so this project can be resumed in a new chat, Codex session, or AI tool without context loss.

Important file-editing instructions:
- The wrapper has already inspected the repository from PowerShell and included the relevant context below.
- If your own shell commands fail, use the repository context in this prompt instead of replacing known information with generic Unknowns.
- If `OFFLOADING.md` exists in the "Existing OFFLOADING.md" section below, update it. Do not attempt to create it with an "Add File" patch.
- Do not overwrite detailed existing handoff content with a generic placeholder just because shell inspection is unavailable.
- If you truly cannot edit the file, explain the blocker in your final response instead of making a blind non-destructive creation attempt.

Use the CRAFT method:

C: Context
Summarize the project purpose, goals, constraints, files, tools, assumptions, user preferences, and relevant history.

R: Role
Write as a senior project handoff assistant preparing another AI agent or developer to continue immediately.

A: Action
Update `OFFLOADING.md` with these sections:
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

Latest user task:
$Task

Launch directory:
$LaunchDir

Repository root:
$RepoRoot

Repository status:
$GitStatus

Recent commits:
$RecentCommits

Tracked files:
$TrackedFiles

Workspace files, depth 3:
$WorkspaceFiles

Existing OFFLOADING.md:
$ExistingOffloading

Now update `OFFLOADING.md` directly.
"@

$Prompt | Set-Content -Encoding UTF8 $PromptPath

if ($DryRun) {
    Write-Host "Dry run: would run:"
    Write-Host "Get-Content `"$PromptPath`" -Raw | $Codex exec $($SandboxArgs -join ' ') --cd `"$RepoRoot`" -"
    Write-Host "Dry run: wrote handoff prompt to $PromptPath"
    exit 0
}

Get-Content $PromptPath -Raw | & $Codex exec @SandboxArgs --cd $RepoRoot -
$ExitCode = $LASTEXITCODE
Remove-Item $PromptPath -Force -ErrorAction SilentlyContinue

if ($ExitCode -ne 0) {
    Write-Host ""
    Write-Host "Failed to update $OffloadingFile."
    exit $ExitCode
}

Write-Host ""
Write-Host "Done. Your project handoff is in $OffloadingFile"
