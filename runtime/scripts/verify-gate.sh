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
# Inputs (env). CRITICAL: these are trustworthy only when they originate OFF the graded worker.
# On the native Stop/TaskCompleted hook the gate runs IN the worker's session, so the worker can set
# them — there the gate is ADVISORY (defense-in-depth), not a soundness boundary. The SOUND guarantee
# holds on CI / MCP-Task / SDK-subprocess surfaces where the coordinator, not the worker, sets the env.
# Set ORCA_PROVENANCE=ci|mcp|sdk|dispatch on those surfaces to assert off-worker origin (else a NOTE
# is emitted). See docs/verify-gate.md#trust-boundary. (Signed/out-of-band binding is tracked separately.)
#   ORCA_MANIFEST         path to the unit's evidence manifest JSON (required)
#   ORCA_CONTRACT_SOURCE  authoritative frozen contract `path@ref` (required for scope soundness)
#   ORCA_CONTRACT_DIGEST  authoritative sha256 of that contract (required for scope soundness)
#   ORCA_REPO             owner/name for the independent review lookup (optional; inferred from origin)
#   ORCA_BASE             integration base branch, for the ancestry check (optional)
#   ORCA_SYMBOL           a unit symbol to grep on the base (optional)
#   ORCA_UNIT_CLASS       mutation | report-only | planning, from dispatch (optional; missing => mutation)
#   ORCA_PROVENANCE       ci|mcp|sdk|dispatch — asserts the env came from OFF the worker (optional)
#   ORCA_EXECUTE_NC       set to replay the negative control (heavier)
# Without ORCA_CONTRACT_SOURCE/DIGEST the verifier fail-closes on scope (a manifest cannot certify
# its own denominator), so the gate blocks — as it should.
#
# Exit: 0 = verified (allow) · 2 = a required invariant failed OR nothing to verify (BLOCK).
# Enterprise note: `allowManagedHooksOnly` can disable plugin hooks — see docs/verify-gate.md
# for the MCP-Task / CI / SDK-subprocess fallbacks that run the SAME verify.py.
set -eu

HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
EVENT=""
if [ "${1:-}" = "--event" ]; then EVENT="${2:-}"; shift 2; fi
MANIFEST="${ORCA_MANIFEST:-${1:-}}"
CONTRACT_SOURCE="${ORCA_CONTRACT_SOURCE:-}"
CONTRACT_DIGEST="${ORCA_CONTRACT_DIGEST:-}"
REPO="${ORCA_REPO:-}"
BASE="${ORCA_BASE:-}"
SYMBOL="${ORCA_SYMBOL:-}"
UNIT_CLASS="${ORCA_UNIT_CLASS:-}"
NO_GH="${ORCA_NO_GH:-}"
LIGHTING="${ORCA_LIGHTING:-}"
RECORD="${ORCA_DISPATCH_RECORD:-}"
PUBKEY="${ORCA_DISPATCH_PUBKEY:-}"
# Signed-dispatch enforcement (#135) is opt-in: if the repo COMMITS .orca/dispatch-pubkey, pin it from
# the immutable git blob at HEAD (a working-tree copy is worker-writable; the committed blob is not
# without a reviewed commit). verify.py's read_source resolves `path@ref` to that blob.
if [ -z "$PUBKEY" ] && git -C "$HERE/../.." cat-file -e "HEAD:.orca/dispatch-pubkey" 2>/dev/null; then
  PUBKEY=".orca/dispatch-pubkey@HEAD"
fi

if [ -z "$MANIFEST" ]; then
  # Stop fires on EVERY turn end; a turn with no unit in progress (manifest unset) has nothing to
  # verify — allow it. TaskCompleted with no manifest is a mis-dispatch — fail closed.
  if [ "$EVENT" = "stop" ]; then
    echo "verify-gate: Stop with no unit in progress (ORCA_MANIFEST unset) — nothing to verify, allowing" >&2
    exit 0
  fi
  echo "verify-gate: no evidence manifest (ORCA_MANIFEST unset) — BLOCKING (fail-closed)" >&2
  exit 2
elif [ ! -f "$MANIFEST" ]; then
  # A NAMED manifest that does not exist means an active unit's evidence is missing (deleted, mistyped,
  # or unavailable) — never allow the turn to end on it, even on Stop.
  echo "verify-gate: evidence manifest named but missing: $MANIFEST — BLOCKING (fail-closed)" >&2
  exit 2
fi

set -- --manifest "$MANIFEST"
[ -n "$CONTRACT_SOURCE" ] && set -- "$@" --contract-source "$CONTRACT_SOURCE"
[ -n "$CONTRACT_DIGEST" ] && set -- "$@" --contract-digest "$CONTRACT_DIGEST"
[ -n "$REPO" ] && set -- "$@" --repo "$REPO"
[ -n "$BASE" ] && set -- "$@" --base "$BASE"
[ -n "$SYMBOL" ] && set -- "$@" --symbol "$SYMBOL"
[ -n "$UNIT_CLASS" ] && set -- "$@" --unit-class "$UNIT_CLASS"
[ -n "$NO_GH" ] && set -- "$@" --no-gh
[ -n "$LIGHTING" ] && set -- "$@" --lighting "$LIGHTING"
[ -n "$RECORD" ] && set -- "$@" --dispatch-record "$RECORD"
[ -n "$PUBKEY" ] && set -- "$@" --dispatch-pubkey "$PUBKEY"
[ -n "${ORCA_EXECUTE_NC:-}" ] && set -- "$@" --execute-nc

# Trust boundary (#112, #135): the contract digest + unit class are only as sound as their provenance.
if [ -n "$PUBKEY" ] && [ -n "$RECORD" ]; then
  : # a coordinator-signed dispatch record is present — verify.py verifies it against the pinned
    # pubkey, so the NATIVE in-session path is SOUND for this unit (#135).
else
  case "${ORCA_PROVENANCE:-}" in
    ci|mcp|sdk|dispatch) : ;;  # env originates off the graded worker — the sound guarantee holds
    *) echo "verify-gate: NOTE — contract/unit-class provenance unverified (ORCA_PROVENANCE unset," \
            "no signed dispatch record); on the native in-session hook path this gate is ADVISORY," \
            "not a soundness boundary. Sign the dispatch record (dispatch-sign.py) or run under" \
            "CI/MCP/SDK for the sound guarantee — docs/verify-gate.md#trust-boundary." >&2 ;;
  esac
fi

# Any nonzero from verify.py (2 = invariant failed, 1 = usage/dep) is a BLOCK: an un-runnable or
# failing verifier is never a green light. Capture the REAL exit in the else branch — `$?` after a
# bare `fi` is the if-statement's status (0 when the condition fails with no else), not verify.py's.
if python3 "$HERE/verify.py" "$@"; then
  rc=0
else
  rc=$?
fi
[ "$rc" -eq 0 ] && exit 0
echo "verify-gate: verifier returned $rc — BLOCKING completion" >&2
exit 2
