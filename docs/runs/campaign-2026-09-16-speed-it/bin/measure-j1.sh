#!/bin/bash
# J1 journey measurement + budget guard (single run; medians come from repeated runs).
# Usage: bin/measure-j1.sh [--budget SECONDS] [--label NAME]
# Exit 0 when J1 total <= budget; exit 2 on breach; exit 1 on stage failure.
# PARKED from CI wiring until J1 is within budget (see DIAGNOSE.md) — landing a
# hard 30 s guard while J1 runs ~250 s would red main. Wire into validate.yml
# when the journey reaches WITHIN-BUDGET; the budget here stays the DECLARED 30 s.
set -u
BUDGET=30
LABEL="j1"
while [ $# -gt 0 ]; do
  case "$1" in
    --budget) BUDGET="$2"; shift 2 ;;
    --label) LABEL="$2"; shift 2 ;;
    *) echo "unknown arg: $1" >&2; exit 1 ;;
  esac
done
cd "$(git rev-parse --show-toplevel)" || exit 1
now() { python3 -c 'import time;print(time.time())'); }
s=$(now); python3 scripts/validate.py >/dev/null 2>&1; ev=$?; e=$(now)
v=$(python3 -c "print(round($e - $s, 2))")
s=$(now); python3 -m unittest discover -s tests >/dev/null 2>&1; et=$?; e=$(now)
t=$(python3 -c "print(round($e - $s, 2))")
git checkout -- assets/ 2>/dev/null
s=$(now); python3 runtime/scripts/proof_status.py --check >/dev/null 2>&1; ep=$?; e=$(now)
p=$(python3 -c "print(round($e - $s, 2))")
total=$(python3 -c "print(round($v + $t + $p, 2))")
echo "LABEL=$LABEL validate=$v tests=$t proof_status=$p J1=$total budget=$BUDGET exits=$ev/$et/$ep"
if [ "$ev" != "0" ] || [ "$et" != "0" ] || [ "$ep" != "0" ]; then
  echo "J1 stage failure (a fast red run is not a win)"; exit 1
fi
if python3 -c "import sys; sys.exit(0 if float('$total') <= float('$BUDGET') else 1)"; then
  echo "J1 WITHIN budget"; exit 0
else
  echo "J1 OVER budget"; exit 2
fi
