#!/usr/bin/env bash
# Runs the unit tests and the non-LLM baselines in the Docker image with
# --network none. No model is called, so this is not an air-gapped triage run;
# that needs local GGUF weights (make run-local).
set -euo pipefail
export LC_ALL=C.UTF-8

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG="${1:-${ROOT}/runs/offline-tests.log}"
mkdir -p "$(dirname "${LOG}")"
IMAGE="${IMAGE:-inbrev:latest}"
RUN=(docker run --rm --network none -v "${ROOT}/src:/app/src" -v "${ROOT}/tests:/app/tests" -v "${ROOT}/data:/app/data" "${IMAGE}")

{
  echo "Inbrev: tests and baselines without network"
  echo "date: $(date -u +'%Y-%m-%d %H:%M:%S UTC')"
  echo "git: $(git -C "${ROOT}" rev-parse --short HEAD 2>/dev/null || echo unknown)"
  echo "docker: $(docker --version)"
  echo "scope: pytest + baselines (majority, keywords, TF-IDF); no language model is called"
  echo
  docker image inspect "${IMAGE}" >/dev/null 2>&1 || docker build -t "${IMAGE}" "${ROOT}"
  echo "--- network check inside the container ---"
  "${RUN[@]}" python -c "import socket; socket.setdefaulttimeout(3)
try:
    socket.create_connection(('1.1.1.1', 443)); print('network: reachable')
except OSError as e:
    print('network: unreachable (' + type(e).__name__ + ')')"
  echo "--- pytest ---"
  "${RUN[@]}" python -m pytest -q
  echo "--- baselines, seed set (n = 12) ---"
  "${RUN[@]}" python -m inbrev eval data/seed/messages.seed.jsonl --baselines
  echo "--- baselines, synthetic Swiss practice set (n = 30) ---"
  "${RUN[@]}" python -m inbrev eval data/ood/swiss_practice_inbox.jsonl --baselines
} 2>&1 | tee "${LOG}"
echo "log: ${LOG}"
