<#
Run Inbrev against a native llama.cpp server (Windows, no Docker) with the same Q4 GGUF and the
same llama.cpp build (b11382) as the Docker offline stack. Measures model speed on the host
without the Docker Desktop VM. It is not the air-gapped proof; that is `make offline-eval`.

Usage (from track_2b/):
  .\scripts\run_native_llamacpp.ps1 -InputFile runs\offline\gold-subset30.jsonl -Out runs\native\gold30-vulkan.jsonl -Backend vulkan
  .\scripts\run_native_llamacpp.ps1 ... -Backend cpu -Threads 8
  .\scripts\run_native_llamacpp.ps1 ... -Backend cuda      # PC with an NVIDIA GPU (downloads the CUDA 12.4 build)

The script downloads the llama.cpp release once into models\ (gitignored), checks the GGUF hash,
starts llama-server on 127.0.0.1 only, runs `inbrev triage` with one sample at temperature 0 and
writes a log with build, device, timings and the hash next to the predictions.
#>
param(
    [Parameter(Mandatory = $true)][string]$InputFile,
    [Parameter(Mandatory = $true)][string]$Out,
    [ValidateSet("cpu", "vulkan", "cuda")][string]$Backend = "vulkan",
    [int]$Threads = 8,
    [int]$Port = 8090,
    [int]$Ctx = 8192,
    [string]$Gguf = "models\apertus-v1.5-8b-text-Q4_K_M.gguf",
    [string]$Build = "b11382"
)
$ErrorActionPreference = "Stop"
$Sha = "a037df8d87ff6caacee794ee85f55342f2152e0d359b7389033300c3bee5f299"
$asset = @{ cpu = "cpu-x64"; vulkan = "vulkan-x64"; cuda = "cuda-12.4-x64" }[$Backend]
$dir = "models\llama.cpp-$Build-$Backend"
if (-not (Test-Path "$dir\llama-server.exe")) {
    $zip = "models\llama-$Build-bin-win-$asset.zip"
    Invoke-WebRequest "https://github.com/ggml-org/llama.cpp/releases/download/$Build/llama-$Build-bin-win-$asset.zip" -OutFile $zip
    Expand-Archive -Force $zip $dir
    if ($Backend -eq "cuda") {
        $rt = "models\cudart-llama-bin-win-cuda-12.4-x64.zip"
        Invoke-WebRequest "https://github.com/ggml-org/llama.cpp/releases/download/$Build/cudart-llama-bin-win-cuda-12.4-x64.zip" -OutFile $rt
        Expand-Archive -Force $rt $dir
    }
}
$hash = (Get-FileHash $Gguf -Algorithm SHA256).Hash.ToLower()
if ($hash -ne $Sha) { throw "GGUF hash $hash does not match $Sha" }

$outDir = Split-Path $Out -Parent
New-Item -ItemType Directory -Force $outDir | Out-Null
$log = [IO.Path]::ChangeExtension($Out, ".log")
$srvLog = [IO.Path]::ChangeExtension($Out, ".server.log")
$srvArgs = @("-m", $Gguf, "-c", "$Ctx", "--parallel", "1", "--jinja", "--host", "127.0.0.1", "--port", "$Port")
if ($Backend -eq "cpu") { $srvArgs += @("-t", "$Threads", "-ngl", "0") } else { $srvArgs += @("-ngl", "99") }

"started   $(Get-Date -Format o)" | Set-Content $log -Encoding utf8
"build     $Build ($Backend)" | Add-Content $log
"gguf      $Gguf sha256 $hash" | Add-Content $log
"server    llama-server $($srvArgs -join ' ')" | Add-Content $log
"host      $((Get-CimInstance Win32_Processor).Name.Trim()), $([math]::Round((Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory / 1GB)) GB RAM" | Add-Content $log
& "$dir\llama-server.exe" --list-devices 2>&1 | Add-Content $log

$srv = Start-Process -FilePath "$dir\llama-server.exe" -ArgumentList $srvArgs -PassThru -NoNewWindow -RedirectStandardError $srvLog
try {
    $t0 = Get-Date
    while ($true) {
        try { if ((Invoke-WebRequest "http://127.0.0.1:$Port/health" -UseBasicParsing -TimeoutSec 5).StatusCode -eq 200) { break } } catch {}
        if ($srv.HasExited) { throw "llama-server exited, see $srvLog" }
        Start-Sleep -Seconds 5
    }
    "loaded    $([int]((Get-Date) - $t0).TotalSeconds) s" | Add-Content $log
    $env:LLM_BASE_URL = "http://127.0.0.1:$Port/v1"
    $env:LLM_API_KEY = "none"
    $env:LLM_NAME = "apertus-v1.5-8b-q4-local"
    $env:INBREV_SAMPLES = "1"
    $env:INBREV_TEMPERATURE = "0"
    $env:INBREV_CONCURRENCY = "1"
    $env:INBREV_TIMEOUT = "1800"
    $before = if (Test-Path $Out) { (Get-Content $Out | Measure-Object -Line).Lines } else { 0 }
    $t1 = Get-Date
    & .venv\Scripts\python -m inbrev triage $InputFile --out $Out --samples 1 --temperature 0 2>&1 | Add-Content $log
    $n = (Get-Content $Out | Measure-Object -Line).Lines - $before
    $sec = ((Get-Date) - $t1).TotalSeconds
    "finished  $(Get-Date -Format o): $n new messages in $([int]$sec) s = $([math]::Round($sec / [math]::Max($n,1), 1)) s per message (wall; rows already in the output are skipped)" | Add-Content $log
}
finally {
    Stop-Process -Id $srv.Id -ErrorAction SilentlyContinue
}
Get-Content $log
