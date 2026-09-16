#!/bin/bash
# Profile: time each test file individually (single pass, pinned conditions).
set -u
cd "$(git rev-parse --show-toplevel)" || exit 1
RUNDIR="docs/runs/campaign-2026-09-16-speed-it"
{
echo "PROFILE-START $(date -u +%FT%TZ) head=$(git rev-parse HEAD)"
for f in tests/test_*.py; do
  mod="tests.$(basename "$f" .py)"
  s=$(python3 -c 'import time;print(time.time())')
  out=$(python3 -m unittest "$mod" 2>&1); ec=$?
  e=$(python3 -c 'import time;print(time.time())')
  ran=$(echo "$out" | grep -E "^Ran " | head -1)
  verdict=$(echo "$out" | grep -E "^(OK|FAILED)" | head -1)
  echo "FILE=$f exit=$ec wall_s=$(python3 -c "print(round($e - $s, 2))") $ran $verdict"
  git checkout -- assets/ 2>/dev/null
done
echo "PROFILE-END $(date -u +%FT%TZ)"
} 2>&1 | tee "$RUNDIR/profile.log"
