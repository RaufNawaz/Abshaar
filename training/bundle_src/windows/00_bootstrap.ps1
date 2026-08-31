<#
.SYNOPSIS
  Downloads and installs everything the training run needs, into one folder.

.DESCRIPTION
  Assumes nothing is on the machine except a browser and a GPU driver, and
  installs into -Root only: a private Python (if none is usable), a venv,
  CUDA torch, the training libraries, and the base model weights. Nothing
  lands in the user profile, so a wipe-on-sign-out workstation needs exactly
  this one folder and this one script.

  Downloads roughly 20 GB (torch ~3 GB, an 8B base model ~16 GB).

.EXAMPLE
  .\00_bootstrap.ps1 -Root D:\abshaar-work -Model Qwen/Qwen3-8B
#>
[CmdletBinding()]
param(
    [string]$Root,
    [string]$Model = 'Qwen/Qwen3-8B',
    # cu128 wheels cover Ada (RTX 6000 Ada, sm_89) and Blackwell (RTX PRO 6000,
    # sm_120). Older card or driver -> try https://download.pytorch.org/whl/cu124
    [string]$TorchIndex = 'https://download.pytorch.org/whl/cu128',
    [string]$PythonUrl = 'https://www.python.org/ftp/python/3.12.10/python-3.12.10-amd64.exe',
    [switch]$SkipModel
)

. "$PSScriptRoot\common.ps1"

$Root = Resolve-WorkRoot $Root
Initialize-AbshaarEnv -Root $Root

Write-Head "Abshaar bootstrap - work root: $Root"
Write-Note "Everything (venv, model cache, checkpoints, results) lives under this folder."
$free = Get-FreeGB $Root
Write-Note "Free space on that drive: $free GB (want 80+ GB for the 8B path)"
if ($free -ge 0 -and $free -lt 40) {
    Write-Warn "Under 40 GB free. The base model alone is ~16 GB; merge + GGUF need more."
}

Write-Head "1/5  GPU"
$smi = Get-Command nvidia-smi -ErrorAction SilentlyContinue
if ($smi) { & nvidia-smi } else { Write-Warn "nvidia-smi not on PATH - the driver may be missing." }

Write-Head "2/5  Python"
function Find-BasePython {
    $candidates = @()
    $launcher = Get-Command py -ErrorAction SilentlyContinue
    if ($launcher) {
        foreach ($v in @('3.12', '3.11', '3.10')) { $candidates += , @($launcher.Source, @("-$v")) }
    }
    $bare = Get-Command python -ErrorAction SilentlyContinue
    if ($bare) { $candidates += , @($bare.Source, @()) }
    $private = Join-Path $Root 'python312\python.exe'
    if (Test-Path -LiteralPath $private) { $candidates = @(, @($private, @())) + $candidates }

    foreach ($candidate in $candidates) {
        $exe = $candidate[0]; $prefix = $candidate[1]
        $version = & $exe @prefix -c "import sys;print('%d.%d' % sys.version_info[:2])" 2>$null
        if ($LASTEXITCODE -eq 0 -and $version) {
            $parts = $version.Trim().Split('.')
            if ([int]$parts[0] -eq 3 -and [int]$parts[1] -ge 10 -and [int]$parts[1] -le 12) {
                return @{ Exe = $exe; Prefix = $prefix; Version = $version.Trim() }
            }
        }
    }
    return $null
}

$python = Find-BasePython
if (-not $python) {
    Write-Note "No Python 3.10-3.12 found. Installing a private copy under $Root\python312 (no admin rights needed)."
    $installer = Join-Path $Root 'downloads\python-installer.exe'
    if (-not (Test-Path -LiteralPath $installer)) {
        Invoke-WebRequest -Uri $PythonUrl -OutFile $installer
    }
    $target = Join-Path $Root 'python312'
    Start-Process -FilePath $installer -Wait -ArgumentList @(
        '/passive', 'InstallAllUsers=0', ('TargetDir="{0}"' -f $target),
        'PrependPath=0', 'Include_launcher=0', 'Include_test=0', 'Include_pip=1'
    )
    $python = Find-BasePython
    if (-not $python) { throw "Python install failed. Install Python 3.12 manually from python.org and re-run." }
}
Write-Good "Python $($python.Version) at $($python.Exe) $($python.Prefix -join ' ')"

Write-Head "3/5  Virtual environment"
$venvPython = Get-VenvPython $Root
if (-not (Test-Path -LiteralPath $venvPython)) {
    Invoke-Checked 'venv creation' $python.Exe (@($python.Prefix) + @('-m', 'venv', (Join-Path $Root 'venv')))
}
Write-Good "venv python: $venvPython"
Invoke-Checked 'pip upgrade' $venvPython @('-m', 'pip', 'install', '--upgrade', '--quiet', 'pip', 'wheel', 'setuptools')

Write-Head "4/5  PyTorch (CUDA) and training libraries"
if (Test-Stage $Root 'deps') {
    Write-Note "Already installed (delete $Root\.stages\deps to force a reinstall)."
} else {
    Write-Note "Installing torch from $TorchIndex - this is the ~3 GB download."
    # --index-url, not --extra-index-url: on Windows the PyPI default torch
    # wheel is CPU-only and pip would happily prefer it.
    Invoke-Checked 'torch install' $venvPython @('-m', 'pip', 'install', '--index-url', $TorchIndex, 'torch')
    Invoke-Checked 'library install' $venvPython @('-m', 'pip', 'install', '-r', (Join-Path $PSScriptRoot 'requirements-cuda.txt'))
    Set-Stage $Root 'deps'
}

Write-Head "5/5  Environment check"
Invoke-Checked 'environment check' $venvPython @((Join-Path $PSScriptRoot 'check_env.py'))

if ($SkipModel) {
    Write-Note "-SkipModel set; not downloading base weights."
} else {
    Write-Head "Base model: $Model"
    $marker = "model_" + ($Model -replace '[\\/:]', '_')
    if (Test-Stage $Root $marker) {
        Write-Note "Already downloaded (cache: $env:HF_HOME)."
    } else {
        $env:HF_HUB_ENABLE_HF_TRANSFER = '1'
        Invoke-Checked 'model download' $venvPython @((Join-Path $PSScriptRoot 'download_model.py'), '--model', $Model)
        Set-Stage $Root $marker
    }
    Write-Note ("Model cache size: " + (Get-DirSizeGB $env:HF_HOME) + " GB")
}

Write-Head "Bootstrap complete"
Write-Good "Next: .\01_train.ps1 -Root `"$Root`" -Model $Model"
