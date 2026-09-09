#!/bin/bash
# Run-3 baseline re-freeze cold start (R4) — executed 2026-09-09 by the completion driver.
# Produces the P0-r3-coldstart-*.txt evidence files beside this script.
set -u
EV=/Users/ravindra/projects/orca-fleet/docs/completion/evidence
SCRATCH=/Users/ravindra/projects/orca-fleet-r3-coldstart
TS=$(date -u +%FT%TZ)
test ! -e "$SCRATCH" || { echo "scratch exists, refusing"; exit 1; }
{
  echo "# $TS run-3 toolchain (R1) — maintainer Mac /Users/ravindra/projects/orca-fleet"
  for c in "git --version" "python3 --version" "ruff --version" "greptile --version" "gh --version" "uv --version" "mise --version" "just --version"; do
    echo "\$ $c"; $c 2>&1 | head -2; echo
  done
} > "$EV/P0-r3-coldstart-tools.txt" 2>&1
git clone --branch main file:///Users/ravindra/projects/orca-fleet "$SCRATCH" >/dev/null 2>&1 || { echo "CLONE FAILED"; exit 1; }
cd "$SCRATCH"
HEADSHA=$(git rev-parse HEAD)
echo "scratch HEAD: $HEADSHA"
FAILURES=0
run() {
  local name=$1; shift
  { echo "# $TS fresh clone (backup-to-restore per A-09) - HEAD $HEADSHA"; echo "\$ $*"; "$@" 2>&1; echo "exit=$?"; } > "$EV/$name"
  # fail closed (greptile P2): the recorded exit is the command's; propagate nonzero to the script
  grep -q "^exit=0$" "$EV/$name" || { echo "FAILED: $name"; FAILURES=$((FAILURES+1)); }
}
run P0-r3-coldstart-validate.txt python3 scripts/validate.py
run P0-r3-coldstart-proof-status.txt python3 runtime/scripts/proof_status.py --check
run P0-r3-coldstart-tests-run1.txt python3 -m unittest discover -s tests
run P0-r3-coldstart-tests-run2.txt python3 -m unittest discover -s tests
run P0-r3-coldstart-demo.txt sh demo/negative-control/run.sh
run P0-r3-coldstart-vfbench.txt python3 bench/vf-bench/vfbench.py
{ echo "# $TS - HEAD $HEADSHA"
  echo "\$ python3 scripts/eval.py (no args = usage; exit is eval.py's own, no pipe)"
  python3 scripts/eval.py 2>&1 | head -6
  echo "exit=${PIPESTATUS[0]}"; echo
  echo "\$ python3 scripts/eval.py validate"
  python3 scripts/eval.py validate 2>&1; echo "exit=$?"
} > "$EV/P0-r3-coldstart-eval.txt"
grep -q "All evals valid" "$EV/P0-r3-coldstart-eval.txt" || { echo "FAILED: eval"; FAILURES=$((FAILURES+1)); }
run P0-r3-coldstart-badges.txt python3 scripts/gen-badges.py --check
run P0-r3-coldstart-ruff.txt ruff check .
[ "$FAILURES" -eq 0 ] && echo "COLDSTART DONE" || { echo "COLDSTART FAILED ($FAILURES)"; exit 1; }
