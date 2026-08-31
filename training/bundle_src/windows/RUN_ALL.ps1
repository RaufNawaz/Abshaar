<#
.SYNOPSIS
  Bootstrap, train, merge, export, evaluate and pack - one command.

.DESCRIPTION
  Each stage records a marker under <Root>\.stages and is skipped if it is
  already done, so re-running after an interruption picks up where it
  stopped. Everything is transcribed to <Root>\logs.

.EXAMPLE
  .\RUN_ALL.ps1 -Root D:\abshaar-work
#>
[CmdletBinding()]
param(
    [string]$Root,
    [string]$Model = 'Qwen/Qwen3-8B',
    [double]$Epochs = 3,
    [switch]$SkipGguf,
    [switch]$SkipGenerate,
    [switch]$Resume
)

. "$PSScriptRoot\common.ps1"
$Root = Resolve-WorkRoot $Root
Initialize-AbshaarEnv -Root $Root

$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$transcript = Join-Path $Root "logs\run-$stamp.log"
Start-Transcript -Path $transcript | Out-Null
$started = Get-Date

try {
    Write-Head "Abshaar - Bulleh Shah expert model, full run"
    Write-Note "root:  $Root"
    Write-Note "model: $Model"
    Write-Note "log:   $transcript"
    Write-Note "Rough timings on an RTX 6000-class card: bootstrap 15-40 min"
    Write-Note "(dominated by ~20 GB of downloads), training 10-40 min,"
    Write-Note "merge + GGUF 15-30 min, generations 10-25 min."

    # Each child script dot-sources common.ps1 and throws on failure, so a
    # failure anywhere lands in the catch below; do not gate on $LASTEXITCODE,
    # which belongs to the last *native* command, not to the script.
    & "$PSScriptRoot\00_bootstrap.ps1" -Root $Root -Model $Model

    $runName = ($Model -replace '[\\/:]', '_')
    if ((Test-Stage $Root ("train_" + $runName)) -and -not $Resume) {
        Write-Note "Training already completed for $Model; skipping (delete .stages\train_$runName to redo)."
    } else {
        & "$PSScriptRoot\01_train.ps1" -Root $Root -Model $Model -Epochs $Epochs -Resume:$Resume
    }

    & "$PSScriptRoot\02_merge_export.ps1" -Root $Root -Model $Model -SkipGguf:$SkipGguf

    if (-not $SkipGenerate) {
        & "$PSScriptRoot\03_generate.ps1" -Root $Root -Model $Model
    }

    & "$PSScriptRoot\04_pack_outbox.ps1" -Root $Root -Model $Model

    $minutes = [math]::Round(((Get-Date) - $started).TotalMinutes, 1)
    Write-Head "Full run finished in $minutes minutes"
} catch {
    Write-Host ""
    Write-Host "RUN FAILED: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "The transcript is at $transcript - re-run this script to resume." -ForegroundColor Red
    Stop-Transcript | Out-Null
    exit 1
}
Stop-Transcript | Out-Null
