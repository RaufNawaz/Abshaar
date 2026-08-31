<#
.SYNOPSIS
  Base vs tuned answers on the held-out eval set and the honesty probes.

.DESCRIPTION
  Evidence captured while the GPU is still available -- not the project's
  acceptance evaluation, which is `abshaar run-eval` on the Mac with a judge
  model and RAG. Two answer files per model land in outbox\generations\, so
  the scored comparison later has raw text to point at, and so an obviously
  broken tune is caught before the machine is wiped.
#>
[CmdletBinding()]
param(
    [string]$Root,
    [string]$Model = 'Qwen/Qwen3-8B',
    [int]$MaxNewTokens = 512,
    [int]$BatchSize = 8,
    [switch]$SkipBase
)

. "$PSScriptRoot\common.ps1"
$Root = Resolve-WorkRoot $Root
Initialize-AbshaarEnv -Root $Root
$python = Assert-VenvPython $Root

$runName = ($Model -replace '[\\/:]', '_')
$adapter = Join-Path (Join-Path (Join-Path $Root 'runs') $runName) 'adapter'
if (-not (Test-Path -LiteralPath $adapter)) { throw "No adapter at $adapter - run 01_train.ps1 first." }

$outDir = Join-Path $Root 'outbox\generations'
$dataDir = Join-Path $PSScriptRoot 'dataset'
$script = Join-Path $PSScriptRoot 'generate_outputs.py'

if (-not $SkipBase) {
    Write-Head "Generating BASE answers (untuned $Model)"
    Invoke-Checked 'base generation' $python @(
        $script, '--model', $Model, '--data-dir', $dataDir, '--out-dir', $outDir,
        '--tag', 'base', '--max-new-tokens', $MaxNewTokens, '--batch-size', $BatchSize
    )
}

Write-Head "Generating TUNED answers (adapter applied)"
Invoke-Checked 'tuned generation' $python @(
    $script, '--model', $Model, '--adapter', $adapter, '--data-dir', $dataDir, '--out-dir', $outDir,
    '--tag', 'tuned', '--max-new-tokens', $MaxNewTokens, '--batch-size', $BatchSize
)

Write-Head "Generations written"
Get-ChildItem -LiteralPath $outDir -Filter '*.jsonl' | ForEach-Object {
    Write-Good ("{0}  ({1:N0} KB)" -f $_.Name, ($_.Length / 1KB))
}
Write-Note "These are unscored. Scoring happens on the Mac with the project's rubric."
Write-Note "Next: .\04_pack_outbox.ps1 -Root `"$Root`""
