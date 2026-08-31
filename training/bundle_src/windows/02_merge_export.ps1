<#
.SYNOPSIS
  Merge the LoRA adapter into the base model and export a GGUF for Ollama.

.DESCRIPTION
  The merge and the quantisation both happen here because this machine has
  the base weights, the RAM and the disk -- and because it is about to be
  wiped. What travels home is a ~5 GB Q4_K_M GGUF that `ollama create` can
  serve directly, plus the ~100 MB adapter as the reproducible artefact.

  The GGUF step is best-effort: it pulls llama.cpp from GitHub. If that
  fails the adapter is still yours and the script says so instead of
  pretending the export happened.
#>
[CmdletBinding()]
param(
    [string]$Root,
    [string]$Model = 'Qwen/Qwen3-8B',
    [string]$Quant = 'Q4_K_M',
    [switch]$SkipGguf,
    [string]$LlamaCppZip = 'https://github.com/ggml-org/llama.cpp/archive/refs/heads/master.zip'
)

. "$PSScriptRoot\common.ps1"
$Root = Resolve-WorkRoot $Root
Initialize-AbshaarEnv -Root $Root
$python = Assert-VenvPython $Root

$runName = ($Model -replace '[\\/:]', '_')
$runDir = Join-Path (Join-Path $Root 'runs') $runName
$adapter = Join-Path $runDir 'adapter'
if (-not (Test-Path -LiteralPath $adapter)) { throw "No adapter at $adapter - run 01_train.ps1 first." }

Write-Head "Merging adapter into base weights"
$merged = Join-Path $runDir 'merged'
Invoke-Checked 'merge' $python @(
    (Join-Path $PSScriptRoot 'merge_adapter.py'),
    '--base', $Model, '--adapter', $adapter, '--out', $merged, '--device', 'cpu'
)
Write-Good ("Merged model: $merged (" + (Get-DirSizeGB $merged) + " GB)")

if ($SkipGguf) {
    Write-Note "-SkipGguf set; stopping after the merge."
    return
}

Write-Head "GGUF export ($Quant)"
$tools = Join-Path $Root 'tools'
New-Item -ItemType Directory -Force -Path $tools | Out-Null

# 1. llama.cpp source, for convert_hf_to_gguf.py
$srcDir = Join-Path $tools 'llama.cpp-master'
if (-not (Test-Path -LiteralPath $srcDir)) {
    $zip = Join-Path $Root 'downloads\llama.cpp-master.zip'
    Write-Note "Downloading llama.cpp source ..."
    Invoke-WebRequest -Uri $LlamaCppZip -OutFile $zip
    Expand-Archive -LiteralPath $zip -DestinationPath $tools -Force
}
$convert = Get-ChildItem -LiteralPath $tools -Recurse -Filter 'convert_hf_to_gguf.py' -ErrorAction SilentlyContinue |
    Select-Object -First 1
if (-not $convert) { throw "convert_hf_to_gguf.py not found under $tools" }

# 2. Prebuilt llama-quantize.exe. If it is unavailable we convert straight to
#    q8_0 instead (bigger, but the convert script can produce it unaided).
$quantizeExe = $null
$existing = Get-ChildItem -LiteralPath $tools -Recurse -Filter 'llama-quantize.exe' -ErrorAction SilentlyContinue |
    Select-Object -First 1
if ($existing) {
    $quantizeExe = $existing.FullName
} else {
    try {
        Write-Note "Looking for a prebuilt llama.cpp Windows binary ..."
        $release = Invoke-RestMethod -Uri 'https://api.github.com/repos/ggml-org/llama.cpp/releases/latest' -Headers @{ 'User-Agent' = 'abshaar-bundle' }
        $asset = $null
        foreach ($pattern in @('*bin-win-cpu-x64.zip', '*bin-win-avx2-x64.zip', '*bin-win-avx-x64.zip')) {
            $asset = $release.assets | Where-Object { $_.name -like $pattern } | Select-Object -First 1
            if ($asset) { break }
        }
        if ($asset) {
            $binZip = Join-Path $Root ('downloads\' + $asset.name)
            Invoke-WebRequest -Uri $asset.browser_download_url -OutFile $binZip
            Expand-Archive -LiteralPath $binZip -DestinationPath (Join-Path $tools 'llama-bin') -Force
            $found = Get-ChildItem -LiteralPath (Join-Path $tools 'llama-bin') -Recurse -Filter 'llama-quantize.exe' |
                Select-Object -First 1
            if ($found) { $quantizeExe = $found.FullName }
        }
    } catch {
        Write-Warn "Could not fetch a llama.cpp binary: $($_.Exception.Message)"
    }
}

$outDir = Join-Path $Root 'outbox\model'
New-Item -ItemType Directory -Force -Path $outDir | Out-Null
$safeName = 'abshaar-bulleh-' + $runName.ToLower()

try {
    if ($quantizeExe) {
        $f16 = Join-Path $outDir "$safeName.f16.gguf"
        if (-not (Test-Path -LiteralPath $f16)) {
            Invoke-Checked 'gguf convert (f16)' $python @($convert.FullName, $merged, '--outfile', $f16, '--outtype', 'f16')
        }
        $quantized = Join-Path $outDir "$safeName.$($Quant.ToLower()).gguf"
        Invoke-Checked "quantize $Quant" $quantizeExe @($f16, $quantized, $Quant)
        Remove-Item -LiteralPath $f16 -Force     # 16 GB intermediate; the quantised file is what travels
        Write-Good "GGUF: $quantized"
    } else {
        Write-Warn "No llama-quantize.exe available - converting straight to q8_0 (~8.5 GB) instead of $Quant."
        $q8 = Join-Path $outDir "$safeName.q8_0.gguf"
        Invoke-Checked 'gguf convert (q8_0)' $python @($convert.FullName, $merged, '--outfile', $q8, '--outtype', 'q8_0')
        Write-Good "GGUF: $q8"
    }

    $modelfile = Join-Path $outDir 'Modelfile.abshaar-bulleh'
    $gguf = Get-ChildItem -LiteralPath $outDir -Filter '*.gguf' | Select-Object -First 1
    $lines = @(
        "# Ollama Modelfile for the tuned Bulleh Shah model.",
        "# On the Mac, from the folder holding this file and the .gguf:",
        "#   ollama create abshaar-bulleh -f Modelfile.abshaar-bulleh",
        "FROM ./$($gguf.Name)",
        'PARAMETER temperature 0.6',
        'PARAMETER top_p 0.95',
        'SYSTEM """You are Abshaar, a scholarly assistant on the Punjabi Sufi poet Bulleh Shah. Answer from your studied corpus. Preserve uncertainty and dispute qualifiers exactly; when the corpus does not contain an answer, say so plainly instead of guessing."""'
    )
    # Not Set-Content -Encoding UTF8: Windows PowerShell 5.1 writes a BOM there,
    # and Ollama's Modelfile parser can choke on it.
    [System.IO.File]::WriteAllLines($modelfile, $lines)
    Write-Good "Modelfile: $modelfile"
} catch {
    Write-Warn "GGUF export failed: $($_.Exception.Message)"
    Write-Warn "The adapter in $adapter is unaffected - carry it home and convert later."
}

Write-Note "Next: .\03_generate.ps1 -Root `"$Root`" -Model $Model"
