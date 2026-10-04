#!/usr/bin/env bash
# Full triage with local Apertus GGUF weights on an internal Docker network
# (internal: true, no route to the internet). Writes log, docker inspect,
# predictions, report and memory samples to OUT.
#   GOLD=path/to/messages.jsonl OUT=evidence/offline/run bash scripts/run_offline_eval.sh
set -euo pipefail
export LC_ALL=C.UTF-8 MSYS_NO_PATHCONV=1

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT}"
hostpath() { (cd "$1" && (pwd -W 2>/dev/null || pwd)); }
GOLD="${GOLD:-data/seed/messages.seed.jsonl}"
GOLD_DIR="$(hostpath "$(dirname "${GOLD}")")"
GOLD_FILE="$(basename "${GOLD}")"
OUT="${OUT:-${ROOT}/runs/offline/$(date -u +%Y%m%dT%H%MZ)}"
mkdir -p "${OUT}"
OUT_M="$(hostpath "${OUT}")"
GGUF_FILE="${GGUF_FILE:-apertus-v1.5-8b-text-Q4_K_M.gguf}"
export GGUF_FILE
P=(docker compose -p inbrev-offline --profile local)
RUN="inbrev-offline-run"
LOG="${OUT}/offline-eval.log"

docker image inspect inbrev:latest >/dev/null 2>&1 || docker build -t inbrev:latest "${ROOT}"

{
  echo "Inbrev offline evaluation: Apertus GGUF in llama.cpp, internal Docker network"
  echo "date: $(date -u +'%Y-%m-%d %H:%M:%S UTC')"
  echo "git: $(git rev-parse --short HEAD 2>/dev/null || echo unknown)$(git diff --quiet 2>/dev/null || echo ' (dirty)')"
  echo "docker: $(docker --version)"
  echo "host: $(docker info --format '{{.OperatingSystem}}, {{.NCPU}} CPUs, {{.MemTotal}} bytes RAM for Docker')"
  echo "input: ${GOLD} ($(wc -l < "${GOLD}") messages)"
  echo "samples per message: ${INBREV_SAMPLES:-3}"
  echo "weights: ${GGUF_FILE} from ${MODELS_SRC:-./models}"
  echo

  echo "--- 1. start llama.cpp (network: practice, internal) ---"
  "${P[@]}" up -d llm
  echo "--- 2. sha256 of the weights the server loads ---"
  "${P[@]}" exec -T llm sh -c "sha256sum /models/${GGUF_FILE}"
  echo "--- 3. start the Inbrev run container (network: practice only) ---"
  docker rm -f "${RUN}" >/dev/null 2>&1 || true
  "${P[@]}" run -d --no-deps --name "${RUN}" -u 0 -v "${GOLD_DIR}:/gold:ro" -v "${OUT_M}:/out" app-local sleep infinity >/dev/null
  docker inspect "${RUN}" "$("${P[@]}" ps -q llm)" > "${OUT}/docker-inspect.json"
  docker network inspect inbrev-offline_practice > "${OUT}/docker-network-practice.json"
  echo "network inbrev-offline_practice internal: $(docker network inspect -f '{{.Internal}}' inbrev-offline_practice)"
  echo "run container networks: $(docker inspect -f '{{range $k, $v := .NetworkSettings.Networks}}{{$k}} {{end}}' "${RUN}")"
  echo "llm container networks: $(docker inspect -f '{{range $k, $v := .NetworkSettings.Networks}}{{$k}} {{end}}' "$("${P[@]}" ps -q llm)")"
  echo "--- 4. egress test from the run container (must fail) ---"
  docker exec "${RUN}" python /app/scripts/egress_check.py
  echo "--- 5. control: same test on the default bridge network (should succeed) ---"
  docker run --rm --network bridge inbrev:latest python /app/scripts/egress_check.py --expect-open || true
  echo "--- 6. wait until the model is loaded ---"
  t0=$(date +%s)
  docker exec "${RUN}" python -c "
import time, urllib.request
for _ in range(720):
    try:
        if urllib.request.urlopen('http://llm:8080/health', timeout=5).status == 200: break
    except Exception: pass
    time.sleep(5)
print(urllib.request.urlopen('http://llm:8080/v1/models', timeout=5).read().decode()[:600])"
  echo "model ready after $(( $(date +%s) - t0 )) s"
  echo "--- 7. triage (${INBREV_SAMPLES:-3} sample(s) per message, one request per sample; llama.cpp rejects n > 1) ---"
  ( while docker inspect "${RUN}" >/dev/null 2>&1; do
      docker stats --no-stream --format '{{.Name}} {{.CPUPerc}} {{.MemUsage}}' >> "${OUT}/docker-stats.txt" 2>/dev/null
      echo "--- $(date -u +%H:%M:%S)" >> "${OUT}/docker-stats.txt"; sleep 15; done ) &
  STATS=$!
  t1=$(date +%s)
  docker exec "${RUN}" python -m inbrev triage "/gold/${GOLD_FILE}" --out /out/predictions.jsonl
  echo "triage wall time: $(( $(date +%s) - t1 )) s"
  echo "--- 8. evaluation ---"
  docker exec "${RUN}" python -m inbrev eval "/gold/${GOLD_FILE}" /out/predictions.jsonl --baselines --report /out/report.md
  kill "${STATS}" 2>/dev/null || true
  echo "--- 9. peak memory (docker stats, every 15 s) ---"
  awk '/inbrev-offline/ { v=$3; u=v; sub(/[0-9.]+/,"",u); sub(/[A-Za-z]+/,"",v); f=(u=="GiB")?1024:(u=="MiB")?1:(u=="KiB")?1/1024:1; m=v*f; if (m>max[$1]) max[$1]=m } END { for (k in max) printf "%s peak %.0f MiB\n", k, max[k] }' "${OUT}/docker-stats.txt"
  docker rm -f "${RUN}" >/dev/null
  "${P[@]}" stop llm >/dev/null
} 2>&1 | tee "${LOG}"
echo "log: ${LOG}"
