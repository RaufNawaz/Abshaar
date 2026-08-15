$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$env:PYTHONPATH = Join-Path $repoRoot "src"

# Prefer the project venv so AI-stack commands (build-index, ask) find their
# dependencies; the stdlib-only commands run identically either way.
$venvPython = Join-Path $repoRoot ".venv\Scripts\python.exe"
$pythonLauncher = Get-Command py -ErrorAction SilentlyContinue

if (Test-Path $venvPython) {
    & $venvPython -m abshaar --root $repoRoot @args
} elseif ($pythonLauncher) {
    py -m abshaar --root $repoRoot @args
} else {
    python -m abshaar --root $repoRoot @args
}

exit $LASTEXITCODE
