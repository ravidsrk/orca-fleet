#!/usr/bin/env bash
# spawn_worker.sh — fail-closed Orca worker dispatch for fleet coordinators. (v2)
#
# v2 contract (Codex review B1/D3 remediation):
#   - fail-closed: any failed step exits nonzero with a SPAWN=FAILED diagnostic line on stderr
#   - respects the task DAG: never forces `ready`; `--mark-ready` is an explicit opt-in and
#     only applies when every declared dep is already completed
#   - least-privilege launch profiles: PROFILE=ro|rw|danger; danger requires ORCA_COORD_ALLOW_DANGER=1
#   - distinct exit codes so coordinators can react:
#       0  dispatched and heartbeat observed
#       1  a spawn/dispatch step failed
#       2  usage or policy refusal (bad args, task not ready, unmet deps, danger without opt-in)
#       3  dispatched but NO heartbeat after retries — respawn in a FRESH terminal
#          (re-dispatch to the same handle is a no-op; see the README.md beside this script)
#
# Still works around: `dispatch --inject` pastes the prompt into a claude worker but does not
# SUBMIT it (codex auto-submits). Flow: create terminal -> wait tui-idle -> settle -> verify task
# ready -> dispatch --inject -> Enter -> verify heartbeat, re-Enter up to 3x.
#
# Usage:
#   SP=<dir> [PROFILE=rw] spawn_worker.sh [--mark-ready] <task_id> <worktree_selector> <title> [agent: claude|codex] [effort]
# Prints:  HANDLE=<h> HB=<ts|None>
#
# NOTE: <worktree_selector> is a RAW orca selector. Orca worktree IDs are composite `uuid::path` —
#   pass `path:/abs/worktree/path` (unambiguous) or the full composite id.
#   See the README.md beside this script ("Learnings"; canonical: scripts/orca-coord/README.md).
#
# Env:
#   SP                        scratchpad dir for JSON artifacts (default: cwd)
#   PROFILE                   ro | rw (default) | danger — worker permission profile
#   ORCA_COORD_ALLOW_DANGER   must be 1 for PROFILE=danger
#   CLAUDE_CMD / CODEX_CMD    full override of the worker launch command (wins over PROFILE)
#   SETTLE_SECS / SUBMIT_SECS / HB_POLL_SECS   timing knobs (defaults 20 / 8 / 40)
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
case "$agent" in
  claude|codex) : ;;
  *)
    echo "SPAWN=REFUSED task=${task} unknown agent '${agent}' (want claude|codex)" >&2
    exit 2
    ;;
esac
SP="${SP:-$(pwd)}"
PROFILE="${PROFILE:-rw}"
SETTLE_SECS="${SETTLE_SECS:-20}"
SUBMIT_SECS="${SUBMIT_SECS:-8}"
HB_POLL_SECS="${HB_POLL_SECS:-40}"
safe_title=$(printf '%s' "$title" | tr -c 'A-Za-z0-9._-' '-')

step=resolve-profile
case "$PROFILE" in
  ro)
    codex_default="codex --sandbox read-only -c model_reasoning_effort=\"$effort\""
    claude_default="claude --permission-mode plan"
    ;;
  rw)
    codex_default="codex --sandbox workspace-write -c model_reasoning_effort=\"$effort\""
    claude_default="claude --permission-mode acceptEdits"
    ;;
  danger)
    if [ "${ORCA_COORD_ALLOW_DANGER:-0}" != "1" ]; then
      echo "SPAWN=REFUSED task=${task} PROFILE=danger requires ORCA_COORD_ALLOW_DANGER=1 (least-privilege guard)" >&2
      exit 2
    fi
    codex_default="codex --dangerously-bypass-approvals-and-sandbox -c model_reasoning_effort=\"$effort\""
    claude_default="claude --dangerously-skip-permissions"
    ;;
  *)
    echo "SPAWN=REFUSED task=${task} unknown PROFILE='$PROFILE' (want ro|rw|danger)" >&2
    exit 2
    ;;
esac
CODEX_CMD="${CODEX_CMD:-$codex_default}"
CLAUDE_CMD="${CLAUDE_CMD:-$claude_default}"
if [ "$agent" = "codex" ]; then cmd="$CODEX_CMD"; else cmd="$CLAUDE_CMD"; fi

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

# --- create worker terminal ---------------------------------------------------
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

# --- dispatch + submit --------------------------------------------------------
step=dispatch-inject
dj="$SP/dispatch-$safe_title.json"
orca_json "$dj" orchestration dispatch --task "$task" --to "$h" --inject

sleep "$SUBMIT_SECS"
step=submit-enter
orca_json "$SP/ts-$safe_title.json" terminal send --terminal "$h" --enter  # SUBMIT the pasted prompt

# --- verify a heartbeat; re-Enter up to 3x -------------------------------------
# The bounded re-Enter loop is the documented claude paste-without-submit workaround
# (README Learnings L1): an extra Enter on an already-submitted claude prompt is an
# empty submit (no-op), the terminal is fresh with only our injected prompt in it, and
# the loop is bounded at 3. Retry sends are best-effort nudges — the authoritative
# verdict is the heartbeat check below (exit 3 on failure), never the send itself.
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
  echo "SPAWN=NO_HEARTBEAT task=${task} handle=${h} — respawn in a FRESH terminal; re-dispatch to the same handle is a no-op (see README.md beside this script)" >&2
  exit 3
fi
