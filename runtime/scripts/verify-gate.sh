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
# Inputs (env, set by the coordinator/dispatch — NOT by the worker):
#   ORCA_MANIFEST         path to the unit's evidence manifest JSON (required)
#   ORCA_CONTRACT_SOURCE  authoritative frozen contract `path@ref` (required for scope soundness)
#   ORCA_CONTRACT_DIGEST  authoritative sha256 of that contract (required for scope soundness)
#   ORCA_REPO             owner/name for the independent review lookup (optional; inferred from origin)
#   ORCA_BASE             integration base branch, for the ancestry check (optional)
#   ORCA_SYMBOL           a unit symbol to grep on the base (optional)
#   ORCA_EXECUTE_NC       set to replay the negative control (heavier)
# Without ORCA_CONTRACT_SOURCE/DIGEST the verifier fail-closes on scope (a manifest cannot certify
# its own denominator), so the gate blocks — as it should.
#
# Exit: 0 = verified (allow) · 2 = a required invariant failed OR nothing to verify (BLOCK).
# Enterprise note: `allowManagedHooksOnly` can disable plugin hooks — see docs/verify-gate.md
# for the MCP-Task / CI / SDK-subprocess fallbacks that run the SAME verify.py.
set -eu

HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
MANIFEST="${ORCA_MANIFEST:-${1:-}}"
CONTRACT_SOURCE="${ORCA_CONTRACT_SOURCE:-}"
CONTRACT_DIGEST="${ORCA_CONTRACT_DIGEST:-}"
REPO="${ORCA_REPO:-}"
BASE="${ORCA_BASE:-}"
SYMBOL="${ORCA_SYMBOL:-}"

if [ -z "$MANIFEST" ] || [ ! -f "$MANIFEST" ]; then
  echo "verify-gate: no evidence manifest (ORCA_MANIFEST unset or missing) — BLOCKING (fail-closed)" >&2
  exit 2
fi

set -- --manifest "$MANIFEST"
[ -n "$CONTRACT_SOURCE" ] && set -- "$@" --contract-source "$CONTRACT_SOURCE"
[ -n "$CONTRACT_DIGEST" ] && set -- "$@" --contract-digest "$CONTRACT_DIGEST"
[ -n "$REPO" ] && set -- "$@" --repo "$REPO"
[ -n "$BASE" ] && set -- "$@" --base "$BASE"
[ -n "$SYMBOL" ] && set -- "$@" --symbol "$SYMBOL"
[ -n "${ORCA_EXECUTE_NC:-}" ] && set -- "$@" --execute-nc

# Any nonzero from verify.py (2 = invariant failed, 1 = usage/dep) is a BLOCK: an un-runnable or
# failing verifier is never a green light. The `if` keeps `set -e` from exiting before we remap.
if python3 "$HERE/verify.py" "$@"; then
  exit 0
fi
rc=$?
echo "verify-gate: verifier returned $rc — BLOCKING completion" >&2
exit 2
