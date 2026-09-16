#!/bin/bash
# Baseline harness: 5 sequential runs of the J1 catalog-gates journey.
# Each run: scripts/validate.py + unittest discover -s tests + proof_status --check
# Appends one line per stage per run to baseline.log; keeps full tails.
set -u
cd "$(dirname "$0")/../../.." || exit 1
# cd to repo root (script lives in docs/runs/campaign-2026-09-16-speed-it/bin/)
if [ ! -f scripts/validate.py ]; then cd "$(git rev-parse --show-toplevel)" || exit 1; fi
RUNDIR="docs/runs/campaign-2026-09-16-speed-it"
LOG="$RUNDIR/rebench.log"
{
echo "REBENCH-START $(date -u +%FT%TZ) host=$(hostname) python=$(python3 -c 'import sys;print(sys.version.split()[0])') head=$(git rev-parse HEAD)"
for i in 1 2 3 4 5; do
  echo "== RUN $i validate $(date -u +%FT%TZ)"
  s=$(python3 -c 'import time;print(time.time())')
  python3 scripts/validate.py > "$RUNDIR/rebench-validate-$i.txt" 2>&1; ev=$?
  e=$(python3 -c 'import time;print(time.time())')
  echo "RUN=$i STAGE=validate exit=$ev wall_s=$(python3 -c "print(round($e - $s, 2))")"
  echo "== RUN $i tests $(date -u +%FT%TZ)"
  s=$(python3 -c 'import time;print(time.time())')
  python3 -m unittest discover -s tests > "$RUNDIR/rebench-tests-$i.txt" 2>&1; et=$?
  e=$(python3 -c 'import time;print(time.time())')
  echo "RUN=$i STAGE=tests exit=$et wall_s=$(python3 -c "print(round($e - $s, 2))")"
  tail -3 "$RUNDIR/rebench-tests-$i.txt"
  git checkout -- assets/ 2>/dev/null
  echo "== RUN $i proof_status $(date -u +%FT%TZ)"
  s=$(python3 -c 'import time;print(time.time())')
  python3 runtime/scripts/proof_status.py --check > "$RUNDIR/rebench-proof-$i.txt" 2>&1; ep=$?
  e=$(python3 -c 'import time;print(time.time())')
  echo "RUN=$i STAGE=proof_status exit=$ep wall_s=$(python3 -c "print(round($e - $s, 2))")"
done
echo "REBENCH-END $(date -u +%FT%TZ)"
} 2>&1 | tee -a "$LOG"
