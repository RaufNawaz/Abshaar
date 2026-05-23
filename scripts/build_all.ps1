$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$env:PYTHONPATH = Join-Path $repoRoot "src"
$pythonLauncher = Get-Command py -ErrorAction SilentlyContinue

function Invoke-Abshaar {
    param([Parameter(ValueFromRemainingArguments = $true)] [string[]] $CliArgs)

    if ($pythonLauncher) {
        py -m abshaar --root $repoRoot @CliArgs
    } else {
        python -m abshaar --root $repoRoot @CliArgs
    }

    if ($LASTEXITCODE -ne 0) {
        exit $LASTEXITCODE
    }
}

Invoke-Abshaar init
Invoke-Abshaar validate
Invoke-Abshaar build-data
Invoke-Abshaar validate
Invoke-Abshaar export-site
Invoke-Abshaar status

Write-Host "Abshaar automation build completed."
