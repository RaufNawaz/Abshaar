# common.ps1 - shared helpers for the Abshaar workstation bundle.
# Windows PowerShell 5.1 compatible (no PowerShell 7-only syntax).
# Dot-source it:  . "$PSScriptRoot\common.ps1"

$ErrorActionPreference = 'Stop'
$ProgressPreference    = 'SilentlyContinue'   # Invoke-WebRequest is ~10x faster without the progress bar
try { [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12 } catch { }

function Write-Head {
    param([string]$Text)
    Write-Host ''
    Write-Host ('=' * 74) -ForegroundColor Cyan
    Write-Host $Text -ForegroundColor Cyan
    Write-Host ('=' * 74) -ForegroundColor Cyan
}

function Write-Note { param([string]$Text) Write-Host "  $Text" -ForegroundColor DarkGray }
function Write-Good { param([string]$Text) Write-Host "  $Text" -ForegroundColor Green }
function Write-Warn { param([string]$Text) Write-Host "  WARNING: $Text" -ForegroundColor Yellow }

# The work root holds EVERYTHING: venv, model cache, checkpoints, outbox.
# Nothing is written to the user profile, so one folder is the whole session.
function Resolve-WorkRoot {
    param([string]$Root)
    if (-not $Root) { $Root = $env:ABSHAAR_ROOT }
    if (-not $Root) { $Root = $PSScriptRoot }
    if (-not (Test-Path -LiteralPath $Root)) { New-Item -ItemType Directory -Force -Path $Root | Out-Null }
    return (Resolve-Path -LiteralPath $Root).Path
}

function Initialize-AbshaarEnv {
    param([Parameter(Mandatory = $true)][string]$Root)
    $env:ABSHAAR_ROOT     = $Root
    $env:HF_HOME          = Join-Path $Root 'cache\huggingface'
    $env:PIP_CACHE_DIR    = Join-Path $Root 'cache\pip'
    $env:TORCH_HOME       = Join-Path $Root 'cache\torch'
    $env:PYTHONUTF8       = '1'
    $env:PYTHONIOENCODING = 'utf-8'
    # Urdu/Shahmukhi text in the console breaks on the legacy code page.
    try { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8 } catch { }
    foreach ($d in @('cache', 'logs', 'outbox', 'downloads', '.stages')) {
        $p = Join-Path $Root $d
        if (-not (Test-Path -LiteralPath $p)) { New-Item -ItemType Directory -Force -Path $p | Out-Null }
    }
}

function Get-StagePath { param([string]$Root, [string]$Name) return (Join-Path (Join-Path $Root '.stages') $Name) }
function Test-Stage    { param([string]$Root, [string]$Name) return (Test-Path -LiteralPath (Get-StagePath $Root $Name)) }
function Set-Stage     { param([string]$Root, [string]$Name) Set-Content -LiteralPath (Get-StagePath $Root $Name) -Value (Get-Date -Format 'o') }

# Never gate on a piped command: the pipe swallows the exit code.
function Invoke-Checked {
    param([string]$What, [string]$Exe, [string[]]$Arguments)
    Write-Host "> $Exe $($Arguments -join ' ')" -ForegroundColor DarkGray
    & $Exe @Arguments
    if ($LASTEXITCODE -ne 0) { throw "$What failed (exit code $LASTEXITCODE)" }
}

function Get-VenvPython { param([string]$Root) return (Join-Path $Root 'venv\Scripts\python.exe') }

function Assert-VenvPython {
    param([string]$Root)
    $py = Get-VenvPython $Root
    if (-not (Test-Path -LiteralPath $py)) {
        throw "No venv at $py - run 00_bootstrap.ps1 first."
    }
    return $py
}

function Get-FreeGB {
    param([string]$Path)
    $qualifier = (Split-Path -Qualifier (Resolve-Path -LiteralPath $Path).Path)
    $drive = Get-PSDrive -Name $qualifier.TrimEnd(':') -ErrorAction SilentlyContinue
    if ($drive -and $drive.Free) { return [math]::Round($drive.Free / 1GB, 1) }
    return -1
}

function Get-DirSizeGB {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) { return 0 }
    $bytes = (Get-ChildItem -LiteralPath $Path -Recurse -File -ErrorAction SilentlyContinue |
        Measure-Object -Property Length -Sum).Sum
    if (-not $bytes) { return 0 }
    return [math]::Round($bytes / 1GB, 2)
}
