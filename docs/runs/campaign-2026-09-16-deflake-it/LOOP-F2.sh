#!/bin/bash
# LOOP-F2: natural-rate measurement — full test_verify module, serial, fresh process each.
# Usage: LOOP-F2.sh <iterations> <out-log>
set -u
TOP="$(git rev-parse --show-toplevel)" && cd "$TOP" || exit 2
N="${1:-30}"; LOG="${2:-loop-f2.log}"
case "$LOG" in /*) : ;; *) LOG="$TOP/docs/runs/campaign-2026-09-16-deflake-it/$LOG";; esac
pass=0; fail=0
: > "$LOG"
echo "LOOP-F2 start $(date -u +%FT%TZ) N=$N host=$(uname -srm) python=$(python3 --version 2>&1) gitleaks=$(command -v gitleaks || echo absent)" | tee -a "$LOG"
for i in $(seq 1 "$N"); do
  if python3 -m unittest discover -s tests -p test_verify.py >> "$LOG" 2>&1; then pass=$((pass+1)); else fail=$((fail+1)); echo "ITER $i FAILED" | tee -a "$LOG"; fi
done
echo "LOOP-F2 end $(date -u +%FT%TZ) pass=$pass fail=$fail rate=$(python3 -c "print($fail/$N)")" | tee -a "$LOG"
