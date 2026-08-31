<#
.SYNOPSIS
  LoRA fine-tune of the base model on the gated Bulleh Shah dataset.

.DESCRIPTION
  Resumable: checkpoints are written every -SaveSteps optimizer steps into
  <Root>\runs\<model>\checkpoints, and re-running with -Resume continues from
  the newest one. On a 48 GB Ada / 96 GB Blackwell card an 8B bf16 LoRA over
  ~1,000 examples is minutes, not hours.

.EXAMPLE
  .\01_train.ps1 -Root D:\abshaar-work
#>
[CmdletBinding()]
param(
    [string]$Root,
    [string]$Model = 'Qwen/Qwen3-8B',
    [double]$Epochs = 3,
    [int]$BatchSize = 4,
    [int]$GradAccum = 4,
    [int]$MaxSeqLen = 4096,
    [int]$SaveSteps = 50,
    [switch]$Resume
)

. "$PSScriptRoot\common.ps1"
$Root = Resolve-WorkRoot $Root
Initialize-AbshaarEnv -Root $Root
$python = Assert-VenvPython $Root

$runName = ($Model -replace '[\\/:]', '_')
$runDir = Join-Path (Join-Path $Root 'runs') $runName
$dataDir = Join-Path $PSScriptRoot 'dataset'

Write-Head "Training LoRA on $Model"
Write-Note "data:  $dataDir"
Write-Note "run:   $runDir"

$arguments = @(
    (Join-Path $PSScriptRoot 'train_lora_cuda.py'),
    '--model', $Model,
    '--data-dir', $dataDir,
    '--out-dir', $runDir,
    '--epochs', $Epochs.ToString([System.Globalization.CultureInfo]::InvariantCulture),
    '--batch-size', $BatchSize,
    '--grad-accum', $GradAccum,
    '--max-seq-len', $MaxSeqLen,
    '--save-steps', $SaveSteps
)
if ($Resume) { $arguments += '--resume' }

Invoke-Checked 'training' $python $arguments
Set-Stage $Root ("train_" + $runName)

Write-Head "Training done"
Write-Good "Adapter:  $runDir\adapter"
Write-Good "Summary:  $runDir\train_summary.json"
Write-Note "Next: .\02_merge_export.ps1 -Root `"$Root`" -Model $Model"
