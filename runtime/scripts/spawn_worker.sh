#!/usr/bin/env bash
# spawn_worker.sh — fail-closed Orca worker dispatch for fleet coordinators. (v5)
#
# v5 contract (2026-09-10 upstream re-pin). Every mechanism below is source-witnessed at the TAG
#   v1.4.199 — the shipped binary — not at upstream HEAD, which has already moved past it:
#   - supervised lane = `worker-start` (compose: worktree + agent terminal + readiness + dispatch).
#     READINESS SEMANTIC: at v1.4.199 `ready` means the preamble WRITE WAS ACCEPTED, not that the
#     agent started a turn (`local-worker-start.ts:263` marks the dispatch ready straight after the
#     accepted write). The next release flips this to a positive `turn_started`, returning
#     `state: outcome_unknown` otherwise — which is why exit 4 exists below, before that upgrade
#     lands. Readiness per agent is source-witnessed at v1.4.199
#     (`local-worker-start.ts:243-263`); live probe owed — pin-it.
#   - typed refusals: branch on `error.code`, NEVER on stderr text, and print `error.data.nextSteps`
#     verbatim — that array is the runtime's own recovery text
#     (`orchestration-dispatch-refusal-contract.ts:8`,
#     `orchestration/recovery-and-cleanup:96-108`).
#   - `state: outcome_unknown` is NOT a failure: it is an unproven outcome. Exit 4, print the
#     receipt's `nextCommands`, and INSPECT — never respawn (respawning beside a live pane is the
#     dual-writer class) (`worker-start-receipt.ts:48,60-68`).
#   - custom-argv lane = `terminal create` + `dispatch --inject`. The inject ALREADY SUBMITS the
#     preamble (`dispatch-methods.ts:155-165` calls `sendTerminalAgentPrompt`) and `--json` returns
#     `result.prompt{requestId, stages}`, stages drawn from `input_accepted | turn_started`
#     (`runtime-terminal-contracts.ts:221-225`). v4's blind re-Enter/heartbeat loop is DELETED:
#     the guide's rule is "never resend on silence"
#     (`orchestration/recovery-and-cleanup:92-94`). When `turn_started` is absent we replay the
#     receipt ONCE with
#     `terminal send --retry-request <requestId> --wait-submit <secs>` — a replay, never a resend
#     ("timeout returns the queued/input-accepted receipt and never resends",
#     `terminal-send.ts:19-22`). At v1.4.199 that flag pair also REQUIRES `--text` with `--enter`
#     (`terminal-send.ts:17-24` handler), so the exact preamble is recovered first via
#     `dispatch-show --task <id> --preamble` (`dispatch-methods.ts:196-213`); if it cannot be
#     recovered, or the host refuses the replay, the lane reports UNPROVEN rather than resending.
#     Whether the regenerated preamble byte-matches the injected payload the requestId is bound to
#     is source-witnessed only (`dispatch-methods.ts:199-212` omits dispatchCapability);
#     live probe owed — pin-it.
#   - `terminal wait` result is READ: `wait.satisfied:false` is an unsatisfied condition. The CLI
#     also sets exit 1 for it (`terminal.ts:126-130`), so v4 failed closed BY ACCIDENT; v5 reads
#     the field, so a host that sets only one of the two still fails closed.
#   - PROFILE=ro NEVER takes worker-start: launch args come from the host's `agentDefaultArgs`
#     profile setting, whose migrated default IS the YOLO map (`tui-agent-launch-defaults.ts:10`
#     re-exports `YOLO_TUI_AGENT_ARGS` as `DEFAULT_TUI_AGENT_ARGS`), so a default host would
#     silently upgrade a read-only reviewer to a bypass one. A host set to manual mode has `''`
#     instead — the rationale is host-dependent, not universal. `agentDefaultArgs` is
#     source-witnessed at v1.4.199 (`tui-agent-launch-defaults.ts:10`); live probe owed — pin-it.
#   - `launch.effective` from the worker-start receipt is printed when present: never claim a model,
#     effort, or permission flag from the REQUESTED arguments alone
#     (`orchestration/coordinator-loop:23-36`).
#   - fail-closed: any failed step exits nonzero with a SPAWN=FAILED diagnostic line on stderr
#   - respects the task DAG: never forces `ready`; `--mark-ready` is an explicit opt-in and
#     only applies when every declared dep is already completed
#   - least-privilege launch profiles: PROFILE=ro|rw|danger; danger requires ORCA_COORD_ALLOW_DANGER=1
#   - distinct exit codes so coordinators can react:
#       0  dispatched — supervised: state=ready; custom-argv: `turn_started` observed
#       1  a spawn/dispatch step failed (includes the refusal code `runtime_error`)
#       2  usage or policy refusal (bad args, task not ready, unmet deps, danger without opt-in,
#          and EVERY typed refusal code: task_not_found, task_not_startable, inject_rejected,
#          nested_worker_depth_exceeded, consumer_fenced, dispatch_inactive)
#       3  (custom-argv lane only) preamble accepted but the turn is UNPROVEN — `input_accepted`
#          with no `turn_started`. Inspect with `orca terminal read --terminal <h> --screen`;
#          NEVER respawn on this, and never send another Enter.
#       4  supervised state=outcome_unknown — the start neither proved nor disproved the worker.
#          Run the receipt's nextCommands (worker-show / worker-abandon); inspect, never respawn.
#
# Usage:
#   SP=<dir> [PROFILE=rw] spawn_worker.sh [--mark-ready] <task_id> <worktree_selector> <title> [agent] [effort]
#   agent ∈ claude|codex|cursor|gemini|grok|droid|opencode|omp|pi (default claude)
# Prints:  supervised: HANDLE=<h> READY=<state>, DISPATCH=<id>, and LAUNCH_EFFECTIVE=<json> when the
#          receipt carries it.  custom-argv lane: HANDLE=<h> STAGES=<csv>
#
# Agent × profile coverage (flags are Orca's own autonomous "yolo" args from
# `tui-agent-permissions.ts:6-33`, so workers never block on a prompt; anything else fails closed
# and needs WORKER_CMD):
#   claude/codex/gemini → ro + rw + danger
#   cursor              → rw + danger (`tui-agent-permissions.ts:21` maps cursor to `--yolo`; Orca
#                         has no read-only mode for it) — also one of the three agents that
#                         `--model`/`--effort` can target
#   grok                → rw + danger (Orca has no read-only mode for grok)
#   droid               → rw + danger (Orca appends `--auto high`); ro → WORKER_CMD
#   opencode/omp/pi     → WORKER_CMD. opencode AND kilo are actively STRIPPED of
#                         `--dangerously-skip-permissions` (`tui-agent-launch-defaults.ts:5-8`);
#                         kilo stays off this roster for the same reason opencode fails closed.
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
#   SETTLE_SECS / SUBMIT_SECS  timing knobs (defaults 20 / 8) — custom-argv lane. SUBMIT_SECS is
#                             the `--wait-submit` observation window, in SECONDS.
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
# cursor and grok have a verified WRITE flag (rw/danger) but no read-only mode in Orca's map;
# opencode/droid/omp/pi have no Orca autonomous launch flag at all. Any (agent, profile)
# without a verified flag fails CLOSED and must be supplied via WORKER_CMD (below).
# `kilo` is deliberately ABSENT for the same reason opencode fails closed: Orca STRIPS
# `--dangerously-skip-permissions` from both (`tui-agent-launch-defaults.ts:5-8` at v1.4.199).
case "$agent" in
  claude|codex|cursor|gemini|grok|droid|opencode|omp|pi) : ;;
  *)
    echo "SPAWN=REFUSED task=${task} unknown agent '${agent}' (want claude|codex|cursor|gemini|grok|droid|opencode|omp|pi)" >&2
    exit 2
    ;;
esac
SP="${SP:-$(pwd)}"
PROFILE="${PROFILE:-rw}"
SETTLE_SECS="${SETTLE_SECS:-20}"
SUBMIT_SECS="${SUBMIT_SECS:-8}"
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
  cursor:rw|cursor:danger)   cmd_default="cursor --yolo" ;;
  grok:rw|grok:danger)       cmd_default="grok --permission-mode bypassPermissions" ;;
  droid:rw|droid:danger)     cmd_default="droid --auto high" ;;
  # No Orca-verified non-blocking flag → WORKER_CMD required:
  #   cursor:ro, grok:ro, droid:ro (no read-only modes in Orca's map)
  #   opencode:*, kilo:* (Orca STRIPS --dangerously-skip-permissions from both;
  #                       opencode autonomy is config-driven)
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
#   PROFILE=ro                            → custom-argv lane with the profile's ro command. A
#                                           worker-start launch takes its args from the host's
#                                           `agentDefaultArgs` setting, whose migrated default IS
#                                           the YOLO map, so on a default host it would silently
#                                           turn a read-only reviewer into a permission-bypass one.
#                                           ro NEVER takes worker-start. (Host-dependent: a
#                                           manual-mode host has `''` — probe owed, pin-it.)
#   PROFILE=rw|danger, no override        → supervised worker-start lane
step=spawn
ws="$SP/ws-$safe_title.json"
if [ -z "$override" ] && [ "$PROFILE" != "ro" ]; then
  # The supervised path: one call composes worktree + agent terminal + readiness + dispatch.
  # Creation flags (--name et al.) are REJECTED for current/existing worktrees — pass --name only
  # when the selector asks for a new worktree.
  name_args=()
  case "$sel" in
    new-child|new-top-level) name_args=(--name "$safe_title") ;;
  esac
  # The call's own exit status is NOT the verdict: a typed refusal, a hard failure, and an
  # UNPROVEN outcome (state: outcome_unknown) all exit nonzero. The receipt is the verdict.
  ws_rc=0
  orca orchestration worker-start --task "$task" --worktree "$sel" ${name_args[@]+"${name_args[@]}"} --agent "$agent" --json > "$ws" 2>&1 || ws_rc=$?

  step=read-start-receipt
  # Line 1 is the machine verdict; the remaining stdout lines are the caller-facing receipt
  # fields. nextSteps / nextCommands go to stderr verbatim — they are the runtime's own
  # recovery text, not ours to paraphrase.
  ws_out=$(python3 - "$ws" <<'PY'
import json, sys

# Every typed preflight refusal is a POLICY/usage answer, not a transport failure: the
# coordinator must branch, not retry. runtime_error is the documented catch-all and is the
# one code that stays a failure ("do not retry unchanged").
POLICY_CODES = {
    "task_not_found", "task_not_startable", "inject_rejected",
    "nested_worker_depth_exceeded", "consumer_fenced", "dispatch_inactive",
}
try:
    d = json.load(open(sys.argv[1]))
except Exception:
    d = {}
if not isinstance(d, dict):
    d = {}
r = d.get("result")
if not isinstance(r, dict):
    r = d
err = d.get("error") or r.get("error") or {}
if not isinstance(err, dict):
    err = {}
code = err.get("code") or ""
data = err.get("data") if isinstance(err.get("data"), dict) else {}
# Older hosts may omit `data` entirely — treat every field as optional.
for s in data.get("nextSteps") or []:
    print(f"nextStep: {s}", file=sys.stderr)
if code in POLICY_CODES:
    print(f"VERDICT=refused CODE={code}")
    raise SystemExit(0)
if code:
    print(f"VERDICT=failed CODE={code}")
    raise SystemExit(0)

state = r.get("state") or (r.get("worker") or {}).get("state")
did = r.get("dispatchId") or r.get("dispatch_id") or ""
# The agent terminal is the effects[] entry kind=terminal role=agent; agentTerminalHandle is a
# worker-list/worker-show field, kept as a harmless fallback.
h = r.get("agentTerminalHandle") or ""
if not h:
    for e in r.get("effects") or []:
        if isinstance(e, dict) and e.get("kind") == "terminal" and e.get("role") == "agent":
            h = e.get("id") or ""
            break

if state == "outcome_unknown":
    # NOT a failure: the start neither proved nor disproved the worker. The receipt names the
    # exact inspection commands; a respawn here is the dual-writer class.
    for c in r.get("nextCommands") or []:
        print(f"nextCommand: {c}", file=sys.stderr)
    print(f"VERDICT=unknown STATE={state}")
    print(f"HANDLE={h} READY={state}")
    print(f"DISPATCH={did}")
    raise SystemExit(0)
if state is not None and state != "ready":
    print(f"VERDICT=failed STATE={state}")
    raise SystemExit(0)

print(f"VERDICT=ready STATE={state or 'exit0'}")
print(f"HANDLE={h} READY={state or 'exit0'}")
print(f"DISPATCH={did}")
launch = r.get("launch") if isinstance(r.get("launch"), dict) else {}
if "effective" in launch:
    eff = launch["effective"]
    print("LAUNCH_EFFECTIVE=" + (eff if isinstance(eff, str) else json.dumps(eff, sort_keys=True)))
PY
)
  verdict_line=$(printf '%s\n' "$ws_out" | head -n 1)
  verdict=${verdict_line#VERDICT=}
  verdict=${verdict%% *}
  payload=$(printf '%s\n' "$ws_out" | tail -n +2)
  # Fail CLOSED on a nonzero call whose receipt named neither a code nor a state: a missing
  # binary, a truncated write, or a host that answered in some shape we do not parse must never
  # read as READY just because the parser found nothing to object to.
  if [ "$verdict" = "ready" ] && [ "$ws_rc" != "0" ]; then
    verdict=failed
    verdict_line="VERDICT=failed UNPARSEABLE_RECEIPT rc=${ws_rc}"
  fi

  step=verify-ready
  case "$verdict" in
    ready)
      printf '%s\n' "$payload"
      ;;
    refused)
      echo "SPAWN=REFUSED task=${task} worker-start refused: ${verdict_line#VERDICT=refused } (policy/usage — nextSteps above; receipt in $ws)" >&2
      exit 2
      ;;
    unknown)
      printf '%s\n' "$payload"
      echo "SPAWN=OUTCOME_UNKNOWN task=${task} — the start neither proved nor disproved the worker. Run the nextCommands above (worker-show, then an explicit worker-stop or worker-abandon): INSPECT, NEVER RESPAWN — a second worker beside a live pane is the dual-writer class (liveness-resume.md). Receipt in $ws" >&2
      exit 4
      ;;
    *)
      echo "SPAWN=FAILED task=${task} step=${step} rc=${ws_rc} — worker-start failed: ${verdict_line#VERDICT=failed } (receipt in $ws)" >&2
      exit 1
      ;;
  esac
else
  # --- custom-argv lane (overrides + PROFILE=ro): terminal create + dispatch --inject ----------
  # Deliberately UNSUPERVISED — no worker-lifecycle row, so worker-stop/worker-release never touch
  # this process. It IS still enumerated: `worker-list` lists it as `unsupervised` with terminal
  # state `retained` (`orchestration-worker-specs.ts:124` at v1.4.199). Record the trade in the
  # ledger (dispatch-lifecycle.md).
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
  # READ the result. A timed-out wait prints a normal result carrying `wait.satisfied:false` AND
  # sets exit 1; relying on the exit code alone (v4) was failing closed by accident. An absent
  # field is an older host, not a false — do not invent a verdict from absence.
  tw="$SP/tw-$safe_title.json"
  wait_rc=0
  orca terminal wait --terminal "$h" --for tui-idle --timeout-ms 90000 --json > "$tw" 2>&1 || wait_rc=$?
  satisfied=$(python3 - "$tw" <<'PY'
import json, sys
try:
    d = json.load(open(sys.argv[1]))
except Exception:
    print("unreadable")
    raise SystemExit(0)
r = d.get("result", d) if isinstance(d, dict) else {}
if isinstance(r, dict) and isinstance(r.get("result"), dict):
    r = r["result"]
w = r.get("wait") if isinstance(r, dict) else None
s = w.get("satisfied") if isinstance(w, dict) else None
print("true" if s is True else "false" if s is False else "absent")
PY
)
  if [ "$satisfied" = "false" ] || [ "$wait_rc" != "0" ]; then
    echo "SPAWN=FAILED task=${task} step=${step} rc=1 — terminal wait unsatisfied (wait.satisfied=${satisfied}, cli_rc=${wait_rc}); the TUI never went idle, so an injected preamble would land in a booting pane. Inspect: orca terminal read --terminal ${h} --screen" >&2
    exit 1
  fi
  sleep "$SETTLE_SECS"  # let the TUI settle so it can receive the paste

  step=dispatch-inject
  # --inject SUBMITS the preamble; it does not merely paste it. The --json receipt carries
  # result.prompt{requestId, stages}. There is no Enter to send after this.
  dj="$SP/dispatch-$safe_title.json"
  orca_json "$dj" orchestration dispatch --task "$task" --to "$h" --inject

  step=read-inject-receipt
  read_stages() {
    python3 - "$1" <<'PY'
import json, sys
try:
    d = json.load(open(sys.argv[1]))
except Exception:
    print("STAGES= REQUEST=")
    raise SystemExit(0)
r = d.get("result", d) if isinstance(d, dict) else {}
if isinstance(r, dict) and isinstance(r.get("result"), dict):
    r = r["result"]
# dispatch --inject returns result.prompt; terminal send returns result.send.prompt.
p = r.get("prompt") if isinstance(r, dict) else None
if not isinstance(p, dict):
    send = r.get("send") if isinstance(r, dict) else None
    p = send.get("prompt") if isinstance(send, dict) else None
if not isinstance(p, dict):
    p = {}
stages = p.get("stages")
stages = [s for s in stages if isinstance(s, str)] if isinstance(stages, list) else []
req = p.get("requestId")
print("STAGES=" + ",".join(stages) + " REQUEST=" + (req if isinstance(req, str) else ""))
PY
  }
  rcpt=$(read_stages "$dj")
  stages=${rcpt#STAGES=}
  stages=${stages%% *}
  request=${rcpt#* REQUEST=}

  case ",$stages," in
    *,turn_started,*) : ;;
    *)
      # No observed turn start. Replay the receipt ONCE — never resend, never a bare Enter.
      # --retry-request/--wait-submit require --text with --enter at v1.4.199, and the requestId
      # is bound to the prompt payload, so recover the exact preamble first.
      step=recover-preamble
      pj="$SP/preamble-$safe_title.json"
      pre_rc=0
      orca orchestration dispatch-show --task "$task" --preamble --json > "$pj" 2>&1 || pre_rc=$?
      preamble=$(python3 - "$pj" <<'PY'
import json, sys
try:
    d = json.load(open(sys.argv[1]))
except Exception:
    raise SystemExit(0)
r = d.get("result", d) if isinstance(d, dict) else {}
if isinstance(r, dict) and isinstance(r.get("result"), dict):
    r = r["result"]
p = r.get("preamble") if isinstance(r, dict) else None
if isinstance(p, str):
    sys.stdout.write(p)
PY
)
      if [ "$pre_rc" = "0" ] && [ -n "$request" ] && [ -n "$preamble" ]; then
        step=replay-receipt
        ts="$SP/ts-$safe_title.json"
        # ONE replay. On timeout the runtime returns the queued/input-accepted receipt and
        # never resends; a failure here leaves the lane UNPROVEN rather than duplicating input.
        if orca terminal send --terminal "$h" --text "$preamble" --enter \
             --retry-request "$request" --wait-submit "$SUBMIT_SECS" --json > "$ts" 2>&1; then
          replay=$(read_stages "$ts")
          replay_stages=${replay#STAGES=}
          replay_stages=${replay_stages%% *}
          if [ -n "$replay_stages" ]; then stages="$replay_stages"; fi
        else
          echo "SPAWN=REPLAY_REFUSED task=${task} handle=${h} — the host refused the receipt replay (see $ts); NOT resending" >&2
        fi
      else
        echo "SPAWN=REPLAY_SKIPPED task=${task} handle=${h} — no requestId or no recoverable preamble, so the receipt cannot be replayed; NOT resending" >&2
      fi
      ;;
  esac

  echo "HANDLE=$h STAGES=$stages"
  case ",$stages," in
    *,turn_started,*) : ;;
    *)
      echo "SPAWN=UNPROVEN task=${task} handle=${h} stages=${stages:-none} — the input was accepted but no turn start was observed. accepted proves input acceptance, NOT a started turn. Inspect with: orca terminal read --terminal ${h} --screen — never resend on silence, and never respawn beside this pane (dispatch-lifecycle.md)" >&2
      exit 3
      ;;
  esac
fi
