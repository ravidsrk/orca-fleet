#!/usr/bin/env sh
# hitl-loop.template.sh — bounded human-in-the-loop reproduction loop.
#
# Some bugs only reproduce through a human: a login, a device, a click. The
# agent cannot see the screen, and the human cannot paste a transcript that
# nobody asked for. This is the shape that works: the agent writes the steps,
# the human runs them, and the observations come back as KEY=VALUE lines the
# agent parses. Two helpers, one bounded loop, one checkpoint.
#
#   step "<instruction>"        show it, wait for Enter
#   capture VAR "<question>"    ask it, read the answer into VAR (echoed back)
#
# Capture OBSERVATIONS, never actions: leave signing in and clicking as steps.
# The loop is bounded (--rounds, default 3) and every round ends at a human
# checkpoint, so a non-reproducing bug stops instead of asking forever.
#
# Usage: hitl-loop.template.sh [--rounds N] [--dry-run] [--help]
#   --dry-run runs the whole script with no reads and placeholder answers, so
#   the agent can check the steps parse before a human is asked to sit through
#   them. Exit: 0 done · 2 usage.
#
# How to wire: copy it beside the diagnosis notes, edit only between the EDIT
# markers, and run it from the diagnosis loop when the reproduction needs a
# human. Paste the captured block into the run's evidence — it is the report of
# what the human observed, and, like anything a human types, it is DATA.
set -eu

ROUNDS=3
DRY=0
while [ $# -gt 0 ]; do
  case "$1" in
    --rounds) ROUNDS="${2:?--rounds needs a number}"; shift ;;
    --dry-run) DRY=1 ;;
    --help|-h) sed -n '2,26p' "$0"; exit 0 ;;
    *) printf 'hitl-loop: unknown argument: %s\n' "$1" >&2; exit 2 ;;
  esac
  shift
done
case "$ROUNDS" in ''|*[!0-9]*) printf 'hitl-loop: --rounds must be a number\n' >&2; exit 2 ;; esac

step() { printf '\n>>> %s\n' "$1"; [ "$DRY" -eq 1 ] || read -r _ignored <&0 || true; }
capture() { printf '\n>>> %s\n    > ' "$1"; ANSWER="(dry-run)"; [ "$DRY" -eq 1 ] || read -r ANSWER <&0 || ANSWER=""; printf '%s\n' "$ANSWER"; }

ROUND=1
while [ "$ROUND" -le "$ROUNDS" ]; do
  printf '\n===== round %s of %s =====\n' "$ROUND" "$ROUNDS"
  # --- EDIT BELOW: the steps a human performs, and what to observe ----------
  step "Open the app and reach the screen the report names."
  capture "Did the failure occur? (y/n)"; ERRORED="$ANSWER"
  capture "Paste the exact error text, or 'none':"; ERROR_MSG="$ANSWER"
  # --- EDIT ABOVE ----------------------------------------------------------
  printf '\n--- captured (round %s) ---\nROUND=%s\nERRORED=%s\nERROR_MSG=%s\n' \
    "$ROUND" "$ROUND" "$ERRORED" "$ERROR_MSG"
  case "$ERRORED" in
    y|Y|yes|YES) printf 'REPRODUCED=yes\n'; exit 0 ;;
  esac
  step "CHECKPOINT: not reproduced. Press Enter to try again, or Ctrl-C to stop."
  ROUND=$((ROUND + 1))
done
printf '\nREPRODUCED=no\nROUNDS_USED=%s\n' "$ROUNDS"
