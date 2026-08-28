#!/usr/bin/env sh
# run.sh — reproducible head-to-head: a self-scoring gate vs orca-fleet's independent verifier,
# on the SAME gamed solution (a scope-shrink trap: the worker froze a 2-criterion contract but
# reported only 1). A self-scorer grades the self-reported list and goes GREEN; orca-fleet's
# verify.py re-derives the FROZEN denominator and goes RED. Anyone can re-run this.
#
# Reproduce against a real self-scorer too: point step [1] at that gate instead of selfscore.py,
# e.g. `ruflo verify` (Truth Verification System) — it self-scores and has no frozen denominator,
# so it exhibits the same GREEN on this trap.
set -u
HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
ROOT=$(CDPATH= cd -- "$HERE/../.." && pwd)
M="$HERE/gamed-manifest.json"
# The AUTHORITATIVE frozen contract is supplied by the coordinator (here: this script), NOT read
# from the worker's manifest — that is what makes the denominator un-swappable.
SRC="demo/negative-control/frozen-spec.md"
DIGEST="sha256:$(shasum -a 256 "$ROOT/$SRC" | awk '{print $1}')"

echo "### negative-control head-to-head (scope-shrink trap) — $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "### trap: frozen contract = [AC-1, AC-2]; worker self-reported only [AC-1]"
echo

echo "== [1] SELF-SCORING gate (grades the self-reported criteria) =="
python3 "$HERE/selfscore.py" --manifest "$M"; ss=$?
echo "self-scorer exit: $ss"
echo

echo "== [2] orca-fleet INDEPENDENT verifier (re-derives the frozen denominator) =="
python3 "$ROOT/runtime/scripts/verify.py" --manifest "$M" --contract-source "$SRC" --contract-digest "$DIGEST" --unit-class report-only; vf=$?
echo "verify.py exit: $vf"
echo

echo "== verdict =="
if [ "$ss" -eq 0 ] && [ "$vf" -ne 0 ]; then
  echo "PASS: self-scorer GREEN (exit $ss) while orca-fleet caught the dropped criterion RED (exit $vf)."
  echo "The moat is the frozen denominator + independent re-derivation, not the gate mechanism."
  exit 0
fi
echo "UNEXPECTED: ss=$ss vf=$vf"
exit 1
