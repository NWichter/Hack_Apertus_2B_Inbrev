#!/usr/bin/env bash
# Prompt p2 vs p3 on the four test sets with Apertus 8B (3 samples, 3 parallel requests).
#   DATA_DIR=path/with/gold-set bash scripts/run_prompt_comparison.sh [OUT]
set -uo pipefail
cd "$(dirname "$0")/.."
OUT="${1:-runs/p3}"
mkdir -p "$OUT"
declare -A SETS=(
  [gold]="$DATA_DIR/gold-set/merged.v0.jsonl"
  [swiss]="data/ood/swiss_practice_inbox.jsonl"
  [nemotron]="$DATA_DIR/gold-set/nemotron.jsonl"
  [grascco]="data/grascco/messages.jsonl"
)
echo "start $(date -u +%FT%TZ) git $(git rev-parse --short HEAD)"
for s in gold swiss nemotron grascco; do
  for v in p3 p2; do
    echo "--- $s $v $(date -u +%T)"
    INBREV_PROMPT=$v INBREV_CONCURRENCY=3 python -m inbrev triage "${SETS[$s]}" --out "$OUT/$s-$v-8b.jsonl" 2>&1 | tail -1
  done
done
echo "done $(date -u +%FT%TZ)"
