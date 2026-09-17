#!/bin/bash
# LOOP-F1: tight independent-process repetition of the CI-failing test.
# Each iteration is a fresh `python3 -m unittest <single test>` process (independent runs).
# Usage: LOOP-F1.sh <iterations> <out-log>
set -u
TOP="$(git rev-parse --show-toplevel)" && cd "$TOP" || exit 2
N="${1:-500}"; LOG="${2:-loop-f1.log}"
case "$LOG" in /*) : ;; *) LOG="$TOP/docs/runs/campaign-2026-09-16-deflake-it/$LOG";; esac
TEST="tests.test_verify.FreshnessCheck.test_wtree_equivalence_relaxes_a_content_identical_head_move"
pass=0; fail=0
: > "$LOG"
echo "LOOP-F1 start $(date -u +%FT%TZ) N=$N host=$(uname -srm) python=$(python3 --version 2>&1)" | tee -a "$LOG"
for i in $(seq 1 "$N"); do
  if python3 -m unittest "$TEST" >> "$LOG" 2>&1; then pass=$((pass+1)); else fail=$((fail+1)); echo "ITER $i FAILED" | tee -a "$LOG"; fi
done
echo "LOOP-F1 end $(date -u +%FT%TZ) pass=$pass fail=$fail rate=$(python3 -c "print($fail/$N)")" | tee -a "$LOG"
