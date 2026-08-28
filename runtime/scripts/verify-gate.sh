#!/usr/bin/env sh
# verify-gate.sh — the completion-gate entrypoint for Claude Code Stop / TaskCompleted hooks.
#
# Wires the independent verifier (verify.py) to the native hook surface so a unit CANNOT be
# marked done until its evidence manifest passes. `TaskCompleted` exit 2 blocks completion and
# returns feedback; `Stop` exit 2 refuses the turn end. This is the plugin-hook packaging of
# evidence-manifest.md section 2 — the gate mechanism is native, its CONTENT (independent
# re-derivation + negative control + frozen denominator) is the differentiator.
#
# FAIL CLOSED: if no manifest is named, the unit is NOT verifiable, so the gate blocks (exit 2),
# never passes by default. Same for a verifier that errors.
#
# Inputs (env, set by the coordinator/dispatch):
#   ORCA_MANIFEST  path to the unit's evidence manifest JSON (required)
#   ORCA_BASE      integration base branch, for the ancestry check (optional)
#   ORCA_SYMBOL    a unit symbol to grep on the base (optional)
# Or: verify-gate.sh <manifest.json> [base] [symbol]
#
# Exit: 0 = verified (allow) · 2 = a required invariant failed OR nothing to verify (BLOCK).
# Enterprise note: `allowManagedHooksOnly` can disable plugin hooks — see docs/verify-gate.md
# for the MCP-Task / CI / SDK-subprocess fallbacks that run the SAME verify.py.
set -eu

HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
MANIFEST="${ORCA_MANIFEST:-${1:-}}"
BASE="${ORCA_BASE:-${2:-}}"
SYMBOL="${ORCA_SYMBOL:-${3:-}}"

if [ -z "$MANIFEST" ] || [ ! -f "$MANIFEST" ]; then
  echo "verify-gate: no evidence manifest (ORCA_MANIFEST unset or missing) — BLOCKING (fail-closed)" >&2
  exit 2
fi

set -- --manifest "$MANIFEST"
[ -n "$BASE" ] && set -- "$@" --base "$BASE"
[ -n "$SYMBOL" ] && set -- "$@" --symbol "$SYMBOL"

# Any nonzero from verify.py (2 = invariant failed, 1 = usage/dep) is a BLOCK: an un-runnable or
# failing verifier is never a green light. The `if` keeps `set -e` from exiting before we remap.
if python3 "$HERE/verify.py" "$@"; then
  exit 0
fi
rc=$?
echo "verify-gate: verifier returned $rc — BLOCKING completion" >&2
exit 2
