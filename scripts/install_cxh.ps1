$ErrorActionPreference = "Stop"

$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$Bin = Join-Path $env:USERPROFILE "codex-handoff-bin"
$RunSource = Join-Path $RepoRoot "scripts\cxh-run.ps1"
$CmdSource = Join-Path $RepoRoot "scripts\cxh.cmd"
$RunTarget = Join-Path $Bin "cxh-run.ps1"
$CmdTarget = Join-Path $Bin "cxh.cmd"
$OldPs1 = Join-Path $Bin "cxh.ps1"

New-Item -ItemType Directory -Force -Path $Bin | Out-Null

if (Test-Path $OldPs1) {
    $Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $Backup = Join-Path $Bin "cxh.ps1.bak_$Timestamp"
    Move-Item -LiteralPath $OldPs1 -Destination $Backup -Force
    Write-Host "Moved old cxh.ps1 to $Backup"
}

Copy-Item -LiteralPath $RunSource -Destination $RunTarget -Force
Copy-Item -LiteralPath $CmdSource -Destination $CmdTarget -Force

$OldPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($OldPath -notlike "*$Bin*") {
    [Environment]::SetEnvironmentVariable("Path", "$OldPath;$Bin", "User")
    Write-Host "Added $Bin to the user PATH."
}

if ($env:Path -notlike "*$Bin*") {
    $env:Path = "$env:Path;$Bin"
}

Write-Host ""
Write-Host "Installed cxh launcher."
Write-Host "Command resolution now available in new PowerShell windows:"
Write-Host ""
Get-Command cxh -All | Select-Object CommandType,Name,Source | Format-Table
Write-Host ""
Write-Host "Try:"
Write-Host "  cxh --dry-run --skip-task `"Test handoff prompt`""
