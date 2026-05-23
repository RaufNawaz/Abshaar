$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$env:PYTHONPATH = Join-Path $repoRoot "src"

$pythonLauncher = Get-Command py -ErrorAction SilentlyContinue

if ($pythonLauncher) {
    py -m abshaar --root $repoRoot @args
} else {
    python -m abshaar --root $repoRoot @args
}

exit $LASTEXITCODE
