#!/usr/bin/env bash
# spawn_worker.sh — fail-closed Orca worker dispatch for fleet coordinators. (v4)
#
# v4 contract (2026-09-09 runtime modernization, re-witnessed against the INSTALLED Orca;
#   v3's first pass shipped an unparseable receipt + a ro→YOLO leak — review-caught, fixed here):
#   - the supervised spawn path is `worker-start` (compose: worktree + agent terminal + readiness
#     + dispatch, one call; on installed Orca the call exits 0 only when the worker is READY).
#     Refusals are TYPED codes in the error envelope (task_not_startable carries
#     data.unmetDependencies; nested_worker_depth_exceeded; consumer_fenced) — branch on the code,
#     never on stderr text.
#   - PROFILE=ro NEVER takes worker-start: Orca's default agent launch appends the YOLO flag, which
#     would silently turn a read-only review worker into a permission-bypass one. ro runs the
#     custom-argv lane with the profile's computed ro command (no CMD_OVERRIDE opt-in — it IS the
#     profile, not an override).
#   - WORKER_CMD / legacy CLAUDE_CMD / CODEX_CMD overrides run the custom-argv lane: terminal
#     create + dispatch --inject (deliberately UNSUPERVISED — no worker-lifecycle row; record the
#     trade in the ledger per dispatch-lifecycle.md) + the bounded Enter submit loop.
#   - fail-closed: any failed step exits nonzero with a SPAWN=FAILED diagnostic line on stderr
#   - respects the task DAG: never forces `ready`; `--mark-ready` is an explicit opt-in and
#     only applies when every declared dep is already completed
#   - least-privilege launch profiles: PROFILE=ro|rw|danger; danger requires ORCA_COORD_ALLOW_DANGER=1
#   - distinct exit codes so coordinators can react:
#       0  dispatched and ready observed
#       1  a spawn/dispatch step failed
#       2  usage or policy refusal (bad args, task not ready, unmet deps, danger without opt-in)
#       3  (legacy lane only) dispatched but NO heartbeat after retries — READ THE PANE FIRST:
#          a live TUI is a working worker; respawn beside it only after that check
#
# Usage:
#   SP=<dir> [PROFILE=rw] spawn_worker.sh [--mark-ready] <task_id> <worktree_selector> <title> [agent] [effort]
#   agent ∈ claude|codex|gemini|grok|droid|opencode|omp|pi (default claude)
# Prints:  HANDLE=<h> READY=<ts|bool> — and on the override lane: HANDLE=<h> HB=<ts|None>
#
# Agent × profile coverage (flags are Orca's own autonomous "yolo" args, so workers never block
# on a prompt; anything else fails closed and needs WORKER_CMD):
#   claude/codex/gemini → ro + rw + danger (worker-start appends Orca's flag)
#   grok                → rw + danger (Orca has no read-only mode for grok)
#   droid               → rw + danger (Orca appends `--auto high`); ro → WORKER_CMD
#   opencode/omp/pi     → WORKER_CMD (Orca strips/omits an autonomous launch flag for these)
# rw and danger use the SAME non-blocking flag; danger only adds the ALLOW_DANGER gate + the
# ephemeral-sandbox requirement (sandbox-policy.md). worker-start's `--effort` requires `--model`
# (a provider model id the fleet does not pin) — the validated `effort` arg applies on the
# override lane's launch command; the supervised path takes the agent's configured default.
#
# NOTE: <worktree_selector> is a RAW orca selector. A worktree id is the composite
#   `<repoId>::<worktreePath>` from `worktree create --json` — pass `path:/abs/worktree/path`
#   (unambiguous) or that full id. See runtime/dispatch-lifecycle.md.
#
# Env:
#   SP                        scratchpad dir for JSON artifacts (default: cwd)
#   PROFILE                   ro | rw (default) | danger — worker permission profile
#   ORCA_COORD_ALLOW_AUTONOMOUS_WRITE  must be 1 for PROFILE=rw (accept autonomous bypass workers)
#   ORCA_COORD_ALLOW_DANGER   must be 1 for PROFILE=danger (implies the above + ephemeral sandbox)
#   WORKER_CMD                full launch command for ANY agent (the generic override; its
#                             read-only/write semantics become YOUR assertion). Legacy
#                             CLAUDE_CMD / CODEX_CMD still work for those two. Any override
#                             requires ORCA_COORD_ALLOW_CMD_OVERRIDE=1 (it bypasses the profile).
#   SETTLE_SECS / SUBMIT_SECS / HB_POLL_SECS   timing knobs (defaults 20 / 8 / 40) — override lane
set -Eeuo pipefail  # -E: ERR trap fires inside functions (orca_json) too

step=parse-args
task="?"
trap 'rc=$?; echo "SPAWN=FAILED task=${task} step=${step} rc=${rc}" >&2; exit "${rc}"' ERR

# orca_json <outfile> <orca-args...> — run orca with --json, fail on nonzero exit
# OR on an exit-0 error envelope ({"error": ...}); fail-closed for every step.
orca_json() {
  local out="$1"; shift
  orca "$@" --json > "$out"
  python3 - "$out" <<'PY'
import json, sys
d = json.load(open(sys.argv[1]))
err = None
if isinstance(d, dict):
    err = d.get("error")
    res = d.get("result")
    if not err and isinstance(res, dict):
        err = res.get("error")
if err:
    print(f"orca error envelope: {err}", file=sys.stderr)
    raise SystemExit(1)
PY
}

MARK_READY=0
args=()
for a in "$@"; do
  case "$a" in
    --mark-ready) MARK_READY=1 ;;
    *) args+=("$a") ;;
  esac
done
if [ "${#args[@]}" -lt 3 ] || [ "${#args[@]}" -gt 5 ]; then
  echo "usage: [PROFILE=ro|rw|danger] spawn_worker.sh [--mark-ready] <task_id> <worktree_selector> <title> [agent] [effort]" >&2
  exit 2
fi
task="${args[0]}"; sel="${args[1]}"; title="${args[2]}"; agent="${args[3]:-claude}"; effort="${args[4]:-xhigh}"
# `effort` is interpolated into the codex reasoning-effort flag (below), so an unvalidated
# value would be injected verbatim into the launch command string. Validate it against the
# known reasoning-effort keyset, fail CLOSED like `agent`/`PROFILE` — never interpolate an
# arbitrary string. Non-codex agents ignore effort entirely, so a bad value is only a risk
# on the codex path, but we reject early and uniformly.
case "$effort" in
  minimal|low|medium|high|xhigh) : ;;
  *)
    echo "SPAWN=REFUSED task=${task} invalid effort '${effort}' (want minimal|low|medium|high|xhigh)" >&2
    exit 2
    ;;
esac
# Known Orca roster. claude/codex/gemini have Orca-verified flags for all three profiles;
# grok has a verified WRITE flag (rw/danger) but no read-only mode in Orca's map;
# opencode/droid/omp/pi have no Orca autonomous launch flag at all. Any (agent, profile)
# without a verified flag fails CLOSED and must be supplied via WORKER_CMD (below).
case "$agent" in
  claude|codex|gemini|grok|droid|opencode|omp|pi) : ;;
  *)
    echo "SPAWN=REFUSED task=${task} unknown agent '${agent}' (want claude|codex|gemini|grok|droid|opencode|omp|pi)" >&2
    exit 2
    ;;
esac
SP="${SP:-$(pwd)}"
PROFILE="${PROFILE:-rw}"
SETTLE_SECS="${SETTLE_SECS:-20}"
SUBMIT_SECS="${SUBMIT_SECS:-8}"
HB_POLL_SECS="${HB_POLL_SECS:-40}"
# The scratch-file key must be UNIQUE per spawn. `tr`-squashing alone collides: two titles
# differing only in a squashed character (e.g. "Fix: a/b" vs "Fix: a\b") map to the same
# name, so parallel spawns clobber each other's JSON artifacts. Append a checksum of the RAW
# title so distinct titles never share a key, regardless of what `tr` folds together.
title_hash=$(printf '%s' "$title" | cksum | cut -d' ' -f1)
safe_title="$(printf '%s' "$title" | tr -c 'A-Za-z0-9._-' '-')-${title_hash}"

# Self-test hook: compute the two hardened values and exit before any orchestration side
# effect. Lets the contract test assert effort-validation and scratch-key uniqueness without
# a live runtime. Placed after both computations so it exercises the real code paths.
if [ -n "${SW_SELFTEST:-}" ]; then
  printf 'safe_title=%s\neffort=%s\n' "$safe_title" "$effort"
  exit 0
fi

step=resolve-profile
case "$PROFILE" in ro|rw|danger) : ;; *)
  echo "SPAWN=REFUSED task=${task} unknown PROFILE='$PROFILE' (want ro|rw|danger)" >&2; exit 2 ;;
esac
# rw and danger launch fully-autonomous (permission-bypass) write workers — non-blocking by
# design, but a real capability grant. They are FAIL-CLOSED behind an explicit opt-in so a
# bare/accidental invocation never spawns a bypass worker silently. ro (read-only) needs none.
#   rw     → ORCA_COORD_ALLOW_AUTONOMOUS_WRITE=1  (accept: no per-command prompts; safety is the
#            isolated worktree + build-blind review + PR gate + testnet/staging rails)
#   danger → ORCA_COORD_ALLOW_DANGER=1            (implies the above AND the ephemeral-sandbox
#            requirement — see sandbox-policy.md; use for destructive / exploit work)
if [ "$PROFILE" = "rw" ] && [ "${ORCA_COORD_ALLOW_AUTONOMOUS_WRITE:-0}" != "1" ]; then
  echo "SPAWN=REFUSED task=${task} PROFILE=rw launches an autonomous permission-bypass worker — set ORCA_COORD_ALLOW_AUTONOMOUS_WRITE=1 to accept (worktree + review + PR gate are the safety layer, not per-command prompts)" >&2
  exit 2
fi
if [ "$PROFILE" = "danger" ] && [ "${ORCA_COORD_ALLOW_DANGER:-0}" != "1" ]; then
  echo "SPAWN=REFUSED task=${task} PROFILE=danger requires ORCA_COORD_ALLOW_DANGER=1 AND an ephemeral sandbox (sandbox-policy.md)" >&2
  exit 2
fi

# Per-agent × profile launch command. Autonomy is the WHOLE POINT: a worker that blocks on a
# permission prompt kills the run. So the write tiers use each agent's fully-autonomous
# ("yolo") flag — the exact flag Orca itself appends by DEFAULT (src/shared/tui-agent-
# permissions.ts YOLO_TUI_AGENT_ARGS / YOLO_TUI_AGENT_ENV; re-witness the map after an Orca
# upgrade — pin-it). NOT the sandboxed modes (acceptEdits / workspace-write / auto_edit), which
# still prompt on shell + network and would block a build worker running tests or `npm install`.
#
# ro    = read-only, non-blocking (it cannot mutate, so nothing to approve) — for review/audit.
# rw    = autonomous write, non-blocking — the DEFAULT. Safety is the isolated worktree +
#         build-blind review + PR gate + no-merge-to-default-without-human, NOT per-command
#         prompts (per the coordinator prompt library's "no per-action permission prompts").
# danger= the SAME autonomous flag as rw, but gated (ORCA_COORD_ALLOW_DANGER) and required to run
#         in an ephemeral per-workspace sandbox (sandbox-policy.md) for destructive / exploit work.
# An (agent, tier) with no Orca-verified flag stays empty → fail-closed to WORKER_CMD below.
cmd_default=""
_cx_effort="-c model_reasoning_effort=\"$effort\""
case "$agent:$PROFILE" in
  claude:ro)                 cmd_default="claude --permission-mode plan" ;;
  claude:rw|claude:danger)   cmd_default="claude --dangerously-skip-permissions" ;;
  codex:ro)                  cmd_default="codex --sandbox read-only $_cx_effort" ;;
  codex:rw|codex:danger)     cmd_default="codex --dangerously-bypass-approvals-and-sandbox $_cx_effort" ;;
  gemini:ro)                 cmd_default="gemini --approval-mode plan" ;;
  gemini:rw|gemini:danger)   cmd_default="gemini --yolo" ;;
  grok:rw|grok:danger)       cmd_default="grok --permission-mode bypassPermissions" ;;
  droid:rw|droid:danger)     cmd_default="droid --auto high" ;;
  # No Orca-verified non-blocking flag → WORKER_CMD required:
  #   grok:ro, droid:ro (no read-only modes in Orca's map)
  #   opencode:* (Orca STRIPS --dangerously-skip-permissions; opencode autonomy is config-driven)
  #   omp:*, pi:* (not in Orca's autonomous-arg map)
esac

# Generalized launch override: WORKER_CMD (any agent) or the legacy CLAUDE_CMD/CODEX_CMD.
# An override replaces the profile's command entirely, so an inherited env var with bypass
# flags would silently defeat PROFILE=ro — it needs its own opt-in, mirroring the danger guard.
override=""
case "$agent" in
  claude) override="${CLAUDE_CMD:-${WORKER_CMD:-}}" ;;
  codex)  override="${CODEX_CMD:-${WORKER_CMD:-}}" ;;
  *)      override="${WORKER_CMD:-}" ;;
esac
if [ -n "$override" ]; then
  if [ "${ORCA_COORD_ALLOW_CMD_OVERRIDE:-0}" != "1" ]; then
    echo "SPAWN=REFUSED task=${task} launch override set without ORCA_COORD_ALLOW_CMD_OVERRIDE=1 (it would bypass PROFILE=$PROFILE)" >&2
    exit 2
  fi
  cmd="$override"
elif [ -n "$cmd_default" ]; then
  cmd="$cmd_default"
else
  echo "SPAWN=REFUSED task=${task} agent '${agent}' has no verified PROFILE=$PROFILE launch flag — supply WORKER_CMD='<cmd>' with ORCA_COORD_ALLOW_CMD_OVERRIDE=1 (its read-only/write semantics are then your assertion)" >&2
  exit 2
fi

# --- verify task readiness against the DAG (never force ready) ---------------
step=verify-task-ready
tl="$SP/tl-$safe_title.json"
orca_json "$tl" orchestration task-list
tl_out=$(python3 - "$tl" "$task" <<'PY'
import json, sys
path, tid = sys.argv[1], sys.argv[2]
d = json.load(open(path))
r = d.get("result", d)
tasks = r.get("tasks") if isinstance(r, dict) else r
tasks = tasks or []
by = {t.get("id"): t for t in tasks}
t = by.get(tid)
if not t:
    print("not-found 0")
    raise SystemExit(0)
deps = t.get("deps")
if deps is None:
    deps = []  # absent deps is the ONLY value that legitimately means "no deps"
elif isinstance(deps, str):
    try:
        deps = json.loads(deps)  # "" and garbage both fail here -> refusal below
    except Exception:
        deps = None
if not isinstance(deps, list):
    # Corrupt/unreadable dependency metadata ("", 0, {}, bad JSON) must fail
    # CLOSED, not count as "no deps".
    print(t.get("status", "unknown"), -1)
    raise SystemExit(0)
unmet = sum(1 for dep in deps if (by.get(dep) or {}).get("status") != "completed")
print(t.get("status", "unknown"), unmet)
PY
)
read -r status unmet <<< "$tl_out"

case "$status" in
  ready) : ;;
  pending)
    if [ "$MARK_READY" != "1" ]; then
      echo "SPAWN=REFUSED task=${task} status=pending — pass --mark-ready only for tasks whose deps are complete" >&2
      exit 2
    fi
    if [ "$unmet" = "-1" ]; then
      echo "SPAWN=REFUSED task=${task} deps metadata unreadable — failing closed rather than assuming no deps" >&2
      exit 2
    fi
    if [ "$unmet" != "0" ]; then
      echo "SPAWN=REFUSED task=${task} status=pending unmet_deps=${unmet} — dispatching would bypass the DAG" >&2
      exit 2
    fi
    step=mark-ready
    orca_json "$SP/tu-$safe_title.json" orchestration task-update --id "$task" --status ready
    ;;
  not-found)
    echo "SPAWN=REFUSED task=${task} not found in task-list" >&2
    exit 2
    ;;
  *)
    echo "SPAWN=REFUSED task=${task} status=${status} — only ready (or opt-in pending) tasks can be dispatched" >&2
    exit 2
    ;;
esac

# --- spawn lanes ---------------------------------------------------------------
# Lane selection:
#   override set (WORKER_CMD/legacy)      → custom-argv lane (opt-in checked above)
#   PROFILE=ro                            → custom-argv lane with the profile's ro command —
#                                           worker-start appends Orca's YOLO flag by default, which
#                                           would silently turn a read-only review worker into a
#                                           permission-bypass one. ro NEVER takes worker-start.
#   PROFILE=rw|danger, no override        → supervised worker-start lane
step=spawn
ws="$SP/ws-$safe_title.json"
if [ -z "$override" ] && [ "$PROFILE" != "ro" ]; then
  # The supervised path: one call composes worktree + agent terminal + readiness + dispatch.
  # On installed Orca the call exits 0 only when the worker is READY. Refusals are typed codes in
  # the error envelope. Creation flags (--name et al.) are REJECTED for current/existing
  # worktrees — pass --name only when the selector asks for a new worktree.
  name_args=()
  case "$sel" in
    new-child|new-top-level) name_args=(--name "$safe_title") ;;
  esac
  # worker-start gets its own envelope handling: typed policy refusals (task_not_startable with
  # unmet deps, nested_worker_depth_exceeded, consumer_fenced) are exit 2 (usage/policy), not 1.
  if ! orca orchestration worker-start --task "$task" --worktree "$sel" ${name_args[@]+"${name_args[@]}"} --agent "$agent" --json > "$ws" 2>&1; then
    code=$(python3 - "$ws" <<'PY'
import json, sys
try:
    d = json.load(open(sys.argv[1]))
    print((d.get("error") or {}).get("code") or "")
except Exception:
    print("")
PY
)
    case "$code" in
      task_not_startable|nested_worker_depth_exceeded|consumer_fenced|dispatch_inactive)
        echo "SPAWN=REFUSED task=${task} worker-start refused: ${code} (policy/usage — see the receipt in $ws)" >&2
        exit 2 ;;
      *)
        echo "SPAWN=FAILED task=${task} step=${step} rc=1 — worker-start failed (receipt in $ws)" >&2
        exit 1 ;;
    esac
  fi
  step=verify-ready
  python3 - "$ws" <<'PY'
import json, sys
d = json.load(open(sys.argv[1]))
r = d.get("result", d)
# The receipt is FLAT: taskId, dispatchId, state ("ready"), effects[], residualResources.
state = r.get("state") or (r.get("worker") or {}).get("state")
did = r.get("dispatchId") or r.get("dispatch_id") or ""
h = r.get("agentTerminalHandle") or ""
if not h:
    for e in r.get("effects") or []:
        if e.get("kind") == "terminal" and e.get("role") == "agent":
            h = e.get("id") or ""
            break
if state == "failed" or (state is not None and state != "ready"):
    print(f"worker-start state={state} — inspect stage/effects before retrying", file=sys.stderr)
    raise SystemExit(1)
print(f"HANDLE={h} READY={state or 'exit0'}")
print(f"DISPATCH={did}")
PY
else
  # --- custom-argv lane (overrides + PROFILE=ro): terminal create + dispatch --inject ----------
  # Deliberately UNSUPERVISED: no worker-lifecycle row; worker-list accounting will not see this
  # worker and worker-stop/release never close it — the ledger records the trade
  # (dispatch-lifecycle.md). The bounded Enter loop below is the submit check for this lane
  # (older CLIs ack the send without receipts; the loop stays bounded and safe).
  step=create-terminal
  tj="$SP/sw-$safe_title.json"
  orca_json "$tj" terminal create --worktree "$sel" --title "$title" --command "$cmd"
  h=$(python3 - "$tj" <<'PY'
import json, sys
d = json.load(open(sys.argv[1]))
if d.get("error"):
    print(f"terminal create error: {d['error']}", file=sys.stderr)
    raise SystemExit(1)
r = d.get("result", d)
h = (r.get("terminal") or {}).get("handle") or r.get("handle")
if not h or h == "None":
    print("terminal create returned no handle", file=sys.stderr)
    raise SystemExit(1)
print(h)
PY
)

  step=wait-tui-idle
  orca_json "$SP/tw-$safe_title.json" terminal wait --terminal "$h" --for tui-idle --timeout-ms 90000
  sleep "$SETTLE_SECS"  # let the TUI settle so it can receive the paste

  step=dispatch-inject
  dj="$SP/dispatch-$safe_title.json"
  orca_json "$dj" orchestration dispatch --task "$task" --to "$h" --inject

  sleep "$SUBMIT_SECS"
  step=submit-enter
  orca_json "$SP/ts-$safe_title.json" terminal send --terminal "$h" --enter  # SUBMIT the pasted prompt

  # --- verify a heartbeat; re-Enter up to 3x (legacy CLIs without send receipts) --------------
  # The bounded re-Enter loop is safe: an extra Enter on an already-submitted claude prompt is an
  # empty submit (no-op), the terminal is fresh with only our injected prompt in it, and the loop
  # is bounded at 3. The authoritative verdict is the heartbeat check (exit 3 on failure).
  step=verify-heartbeat
  hb=None
  for _ in 1 2 3; do
    sleep "$HB_POLL_SECS"
    if out=$(orca orchestration dispatch-show --task "$task" --json 2>/dev/null); then
      hb=$(printf '%s' "$out" | python3 -c 'import sys,json;d=json.load(sys.stdin);r=d.get("result",{});x=r.get("dispatch",r);print(x.get("last_heartbeat_at") or "None")' 2>/dev/null || echo None)
    fi
    if [ "$hb" != "None" ]; then break; fi
    orca terminal send --terminal "$h" --enter --json > /dev/null 2>&1 || true
  done

  echo "HANDLE=$h HB=$hb"
  if [ "$hb" = "None" ]; then
    echo "SPAWN=NO_HEARTBEAT task=${task} handle=${h} — READ THE PANE FIRST: a live TUI is a working worker; respawn beside it only after that check (dispatch-lifecycle.md)" >&2
    exit 3
  fi
fi
