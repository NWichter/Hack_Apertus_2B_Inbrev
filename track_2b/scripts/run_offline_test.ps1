# Runs the unit tests and the non-LLM baselines in the Docker image with
# --network none. No model is called, so this is not an air-gapped triage run;
# that needs local GGUF weights (make run-local).
param([string]$Log = "")
$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
if (-not $Log) { $Log = Join-Path $root "runs/offline-tests.log" }
New-Item -ItemType Directory -Force -Path (Split-Path -Parent $Log) | Out-Null
$image = if ($env:IMAGE) { $env:IMAGE } else { "inbrev:latest" }
$mounts = @("-v", "${root}/src:/app/src", "-v", "${root}/tests:/app/tests", "-v", "${root}/data:/app/data")
$lines = [System.Collections.Generic.List[string]]::new()
function Say([string]$t) { Write-Host $t; $lines.Add($t) }
function Run([string[]]$cmd) {
    $out = & docker run --rm --network none @mounts $image @cmd 2>&1 | ForEach-Object { "$_" }
    $out | ForEach-Object { Say $_ }
}

Say "Inbrev: tests and baselines without network"
Say ("date: " + (Get-Date).ToUniversalTime().ToString("yyyy-MM-dd HH:mm:ss 'UTC'"))
Say ("git: " + (git -C $root rev-parse --short HEAD))
Say ("docker: " + (docker --version))
Say "scope: pytest + baselines (majority, keywords, TF-IDF); no language model is called"
Say ""
docker image inspect $image *> $null
if ($LASTEXITCODE -ne 0) { docker build -t $image $root }
Say "--- network check inside the container ---"
Run @("python", "-c", "import socket; socket.setdefaulttimeout(3)`ntry:`n    socket.create_connection(('1.1.1.1', 443)); print('network: reachable')`nexcept OSError as e:`n    print('network: unreachable (' + type(e).__name__ + ')')")
Say "--- pytest ---"
Run @("python", "-m", "pytest", "-q")
Say "--- baselines, seed set (n = 12) ---"
Run @("python", "-m", "inbrev", "eval", "data/seed/messages.seed.jsonl", "--baselines")
Say "--- baselines, synthetic Swiss practice set (n = 30) ---"
Run @("python", "-m", "inbrev", "eval", "data/ood/swiss_practice_inbox.jsonl", "--baselines")

[System.IO.File]::WriteAllLines($Log, $lines, [System.Text.UTF8Encoding]::new($false))
Write-Host "log: $Log"
