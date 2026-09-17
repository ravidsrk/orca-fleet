#!/bin/bash
# STREAK-module: PROVE streak, fixed module, serial fresh processes at ONE head SHA.
# Logs go to /tmp during the streak (zero test-visible drift), moved to the run dir after.
# Usage: STREAK-module.sh <n> <tmp-log>
set -u
TOP="$(git rev-parse --show-toplevel)" && cd "$TOP" || exit 2
N="${1:-30}"; LOG="${2:-/tmp/streak-module.log}"
HEAD_SHA="$(git rev-parse HEAD)"; HEAD_TREE="$(git rev-parse HEAD^{tree})"
pass=0; fail=0
: > "$LOG"
echo "STREAK-module start $(date -u +%FT%TZ) N=$N HEAD=$HEAD_SHA TREE=$HEAD_TREE host=$(uname -srm)" | tee -a "$LOG"
for i in $(seq 1 "$N"); do
  now="$(git rev-parse HEAD)"
  if [ "$now" != "$HEAD_SHA" ]; then echo "STREAK ABORTED: HEAD moved $HEAD_SHA -> $now at iter $i" | tee -a "$LOG"; exit 3; fi
  if python3 -m unittest discover -s tests -p test_verify.py >> "$LOG" 2>&1; then pass=$((pass+1)); else fail=$((fail+1)); echo "ITER $i FAILED — STREAK RESET" | tee -a "$LOG"; fi
done
echo "STREAK-module end $(date -u +%FT%TZ) HEAD=$HEAD_SHA pass=$pass fail=$fail consecutive_green=$([ "$fail" -eq 0 ] && echo "$N" || echo 0)" | tee -a "$LOG"
