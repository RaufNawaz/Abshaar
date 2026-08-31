<#
.SYNOPSIS
  Collect everything worth keeping into <Root>\outbox and checksum it.

.DESCRIPTION
  This workstation deletes all data at sign-out. Anything not copied off
  before then is gone -- including the GPU-hours. This step gathers the
  adapter, the training summary, the environment report, the generations
  and the logs, writes SHA256SUMS.txt, zips the small artefacts into one
  file you can email or upload, and prints what still has to be moved by
  hand (the GGUF is too large to email).
#>
[CmdletBinding()]
param(
    [string]$Root,
    [string]$Model = 'Qwen/Qwen3-8B'
)

. "$PSScriptRoot\common.ps1"
$Root = Resolve-WorkRoot $Root
Initialize-AbshaarEnv -Root $Root

$runName = ($Model -replace '[\\/:]', '_')
$runDir = Join-Path (Join-Path $Root 'runs') $runName
$outbox = Join-Path $Root 'outbox'
$adapterOut = Join-Path $outbox ('adapter\' + $runName)

Write-Head "Packing results"

if (Test-Path -LiteralPath (Join-Path $runDir 'adapter')) {
    New-Item -ItemType Directory -Force -Path $adapterOut | Out-Null
    Copy-Item -Path (Join-Path $runDir 'adapter\*') -Destination $adapterOut -Recurse -Force
    Write-Good "adapter -> $adapterOut"
} else {
    Write-Warn "No adapter found in $runDir - nothing trained?"
}

foreach ($file in @('train_summary.json')) {
    $src = Join-Path $runDir $file
    if (Test-Path -LiteralPath $src) { Copy-Item -LiteralPath $src -Destination $outbox -Force }
}
$logs = Join-Path $Root 'logs'
if (Test-Path -LiteralPath $logs) {
    $logOut = Join-Path $outbox 'logs'
    New-Item -ItemType Directory -Force -Path $logOut | Out-Null
    Copy-Item -Path (Join-Path $logs '*') -Destination $logOut -Recurse -Force
}

# Checksums over everything in the outbox.
$sums = Join-Path $outbox 'SHA256SUMS.txt'
if (Test-Path -LiteralPath $sums) { Remove-Item -LiteralPath $sums -Force }
$lines = @()
Get-ChildItem -LiteralPath $outbox -Recurse -File | Where-Object { $_.Name -ne 'SHA256SUMS.txt' } | ForEach-Object {
    $relative = $_.FullName.Substring($outbox.Length).TrimStart('\')
    $lines += ((Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash.ToLower() + '  ' + $relative)
}
$lines | Set-Content -LiteralPath $sums -Encoding ASCII
Write-Good "SHA256SUMS.txt ($($lines.Count) files)"

# One small zip: adapter + summaries + generations + logs. Excludes the GGUF.
$zip = Join-Path $Root 'abshaar_results_small.zip'
if (Test-Path -LiteralPath $zip) { Remove-Item -LiteralPath $zip -Force }
$staging = Join-Path $Root 'cache\zip-staging'
if (Test-Path -LiteralPath $staging) { Remove-Item -LiteralPath $staging -Recurse -Force }
New-Item -ItemType Directory -Force -Path $staging | Out-Null
Get-ChildItem -LiteralPath $outbox -Force | Where-Object { $_.Name -ne 'model' } | ForEach-Object {
    Copy-Item -LiteralPath $_.FullName -Destination $staging -Recurse -Force
}
$zipMb = 0
if (Get-ChildItem -LiteralPath $staging -Force) {
    Compress-Archive -Path (Join-Path $staging '*') -DestinationPath $zip -Force
    $zipMb = [math]::Round((Get-Item -LiteralPath $zip).Length / 1MB, 1)
    Write-Good "$zip ($zipMb MB)"
} else {
    Write-Warn "Nothing to zip - the outbox holds no small artefacts."
}
Remove-Item -LiteralPath $staging -Recurse -Force

Write-Head "BEFORE YOU SIGN OUT - this machine wipes itself"
Write-Host ""
Write-Host "  1. Copy this ZIP off the machine (upload, USB, or email if it fits):" -ForegroundColor Yellow
Write-Host "       $zip  ($zipMb MB)" -ForegroundColor Yellow
$modelDir = Join-Path $outbox 'model'
if (Test-Path -LiteralPath $modelDir) {
    Get-ChildItem -LiteralPath $modelDir -File | ForEach-Object {
        Write-Host ("  2. Copy the servable model by hand ({0:N1} GB - too big to email):" -f ($_.Length / 1GB)) -ForegroundColor Yellow
        Write-Host "       $($_.FullName)" -ForegroundColor Yellow
    }
} else {
    Write-Host "  2. No GGUF was produced. The adapter in the ZIP is enough to redo the" -ForegroundColor Yellow
    Write-Host "     merge later, but that means re-downloading the 16 GB base model." -ForegroundColor Yellow
}
Write-Host ""
Write-Host "  3. Verify the copy landed: compare against outbox\SHA256SUMS.txt." -ForegroundColor Yellow
Write-Host "  4. Only then sign out." -ForegroundColor Yellow
Write-Host ""
