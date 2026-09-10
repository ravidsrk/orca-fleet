#!/usr/bin/env sh
# deny-hook.sh — PreToolUse guard for read-write workers (Bash, Edit, Write).
#
# The Never list and the worktree boundary are doctrine (runtime/sandbox-policy.md,
# playbooks/risk-review.md). Doctrine sits above the model; this sits below it.
# A read-write worker runs with the host's permission prompts turned down, so the
# only thing between an improvised `rm -rf ~` and the disk is a hook.
#
# Reads the PreToolUse event JSON on stdin and writes ONE decision object on
# stdout in the shape the host honors:
#
#   {"hookSpecificOutput":{"hookEventName":"PreToolUse",
#     "permissionDecision":"deny|ask","permissionDecisionReason":"…"}}
#
# The nesting is load-bearing: a top-level permissionDecision is ignored, which
# is how a deny silently becomes an allow. Every field is JSON-encoded by
# python3 — never printf-interpolated, since a path carrying a quote produces
# malformed JSON and a malformed decision is no decision at all.
#
# POLARITY IS FAIL-CLOSED. Unparseable stdin, absent stdin, or no JSON parser on
# PATH all DENY. A boundary that fails open is not a boundary. Allow is the only
# decision this hook makes silently (exit 0, no output).
#
# HIGH tier (deny, never ask) for Bash — simple commands only, since string
# matching cannot resolve what `cd X && git push --force` does; a compound
# command falls through to the Never-list ask:
#   1. recursive delete whose every target is /, ~, $HOME or /*, or any
#      recursive delete carrying --no-preserve-root
#   2. force-push to the default branch, including the +main refspec form that
#      needs no flag at all
#   3. `git push --force` / `-f` without --force-with-lease, on any target: the
#      lease is what makes a force-push recoverable, and a worker that has not
#      earned the lease has not earned the push
#   4. `orca orchestration reset` — one command that discards a whole fleet's
#      dispatch state
# --force-with-lease is deliberately NOT matched anywhere in the HIGH tier.
#
# Never list (ask, per runtime/sandbox-policy.md): live-prod mutation, credential
# provisioning, destructive database or infrastructure teardown, unpinned remote
# code execution, publishing, and history-discarding local git. These are "ask"
# rather than "deny" because each has a legitimate form the human can authorize
# in the moment; the HIGH tier has none.
#
# Edit/Write: when ORCA_UNIT_WORKTREE is set, a target path outside it is DENIED.
# Symlinks are resolved through the final component first, so an in-boundary
# symlink pointing out of the boundary is judged by its target. A payload that
# parses but names no file_path (a non-file tool) is allowed. When the variable
# is unset the boundary is not enforced — an unset boundary is a configuration
# choice, and this hook says so rather than guessing one.
#
# Exit codes: always 0. The DECISION is the output, not the status — a non-zero
# exit from a hook is a hook error, which the host treats differently from a deny.
#
# How to wire — and what does NOT wire it. Nothing in this repository registers
# this hook, and this header used to say the dispatcher did (PR #277 review, P2).
# It cannot, on either lane spawn_worker.sh has: the supervised `worker-start`
# lane takes its launch args from the HOST's agentDefaultArgs, not from any
# command this repo builds, and an env var exported here does not cross the Orca
# daemon into the worker's process. A hook nobody registers is doctrine wearing a
# script's file extension, which is the thing this catalog exists to refuse.
#
# So you wire it, per host, and `deny-hook.sh --settings <worktree>` prints the
# exact block: a PreToolUse matcher over Bash|Edit|Write|NotebookEdit|MultiEdit
# plus ORCA_UNIT_WORKTREE=<the unit's own worktree>, which gives the freeze
# boundary for free. Merge it into the settings file the worker's agent reads.
#
# State the boundary honestly when you do: this runs INSIDE the worker's session,
# so it is defense-in-depth against an improvised command, the same advisory
# status the completion gate carries — not a soundness boundary against a worker
# that sets out to defeat it. The soundness boundary is the disposable sandbox
# for the danger lane.
set -eu

usage() {
  cat <<'USAGE'
deny-hook.sh — PreToolUse deny/ask guard for read-write workers.

Usage: deny-hook.sh [--help] [--settings <worktree>]
  Reads a PreToolUse event JSON object on stdin; writes a decision object on
  stdout when the action is denied or must be asked, nothing when it is allowed.
  --settings <worktree> prints the settings.json block that registers this hook
  for one worker, with the boundary path resolved. Nothing registers it for you.

Environment:
  ORCA_UNIT_WORKTREE  when set, Edit/Write outside this directory is denied.

Exit: always 0 (the decision is the output). Fail-closed: unparseable input denies.
USAGE
}

if [ "${1:-}" = "--help" ] || [ "${1:-}" = "-h" ]; then usage; exit 0; fi

# --settings <worktree>: print the registration block, boundary resolved. This is
# the whole answer to "how do I turn this on" — there is no dispatcher step that
# does it for you, and saying so in a --help is cheaper than a doc nobody reads.
if [ "${1:-}" = "--settings" ]; then
  if [ -z "${2:-}" ]; then
    echo "deny-hook.sh --settings needs the worker's worktree path" >&2
    exit 2
  fi
  _wt=$(cd "$2" 2>/dev/null && pwd -P) || {
    echo "deny-hook.sh --settings: '$2' is not a directory" >&2
    exit 2
  }
  _self=$(cd "$(dirname -- "$0")" && pwd -P)/$(basename -- "$0")
  printf '%s\n' '{'
  printf '  "env": {"ORCA_UNIT_WORKTREE": "%s"},\n' "$_wt"
  printf '%s\n' '  "hooks": {'
  printf '%s\n' '    "PreToolUse": ['
  printf '%s\n' '      {'
  printf '%s\n' '        "matcher": "Bash|Edit|Write|NotebookEdit|MultiEdit",'
  printf '%s\n' '        "hooks": ['
  printf '          {"type": "command", "command": "%s"}\n' "$_self"
  printf '%s\n' '        ]'
  printf '%s\n' '      }'
  printf '%s\n' '    ]'
  printf '%s\n' '  }'
  printf '%s\n' '}'
  exit 0
fi
if [ $# -gt 0 ]; then
  printf 'deny-hook.sh: unexpected argument: %s\n' "$1" >&2
  usage >&2
  exit 2
fi

# One decision object, with the reason JSON-encoded via argv (never interpolated).
decide() {
  python3 -c 'import json,sys; print(json.dumps({"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":sys.argv[1],"permissionDecisionReason":sys.argv[2]}}))' "$1" "$2" 2>/dev/null && return 0
  # No parser: emit a decision with a fixed, quote-free reason so the deny still
  # lands as valid JSON.
  printf '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"%s","permissionDecisionReason":"denied by policy"}}\n' "$1"
}

PAYLOAD=$(cat 2>/dev/null || true)

# Extract tool_name, tool_input.command and tool_input.file_path as three lines.
# A parse failure (or no python3) exits non-zero here and DENIES below.
FIELDS=$(printf '%s' "$PAYLOAD" | python3 -c 'import json,sys
d = json.loads(sys.stdin.read())
if not isinstance(d, dict):
    raise SystemExit(1)
ti = d.get("tool_input") or {}
if not isinstance(ti, dict):
    ti = {}
def s(v):
    return v.replace("\n", " ") if isinstance(v, str) else ""
print(s(d.get("tool_name")))
print(s(ti.get("command")))
print(s(ti.get("file_path")))' 2>/dev/null) || {
  decide deny "deny-hook: the tool payload could not be parsed. Fail-closed: an unreadable payload is refused, never allowed."
  exit 0
}

# --- path resolution ---------------------------------------------------------
# The boundary check is a string prefix, so the path it compares has to be a
# REAL absolute path. It previously was not: when a write named a parent that
# did not exist yet, the fallback pasted the raw (un-normalized) parent onto
# $PWD, so `../outside/new/file` became `/worktree/../outside/new` — which
# prefix-matches `/worktree/` and was ALLOWED while the write landed outside
# (PR #277 review, P2).
#
# lexical_abs collapses `.` and `..` with no filesystem access, so it is safe on
# a tail that does not exist yet. resolve_dir resolves the deepest EXISTING
# ancestor physically first (that is what catches symlinks, which a lexical pass
# cannot), then collapses the remaining tail against it — components that do not
# exist cannot be symlinks, so collapsing them lexically is sound.
lexical_abs() {
  _p=$1
  case "$_p" in /*) : ;; *) _p="$(pwd -P)/$_p" ;; esac
  _out=""
  _oldifs=$IFS
  IFS='/'
  for _seg in $_p; do
    case "$_seg" in
      ''|.) : ;;
      ..) _out=${_out%/*} ;;
      *) _out="$_out/$_seg" ;;
    esac
  done
  IFS=$_oldifs
  printf '%s' "${_out:-/}"
}

resolve_dir() {
  _d=$1
  [ -n "$_d" ] || return 0
  case "$_d" in /*) : ;; *) _d="$(pwd -P)/$_d" ;; esac
  _tail=""
  while [ ! -d "$_d" ]; do
    _parent=$(dirname -- "$_d")
    [ "$_parent" = "$_d" ] && break
    _tail="$(basename -- "$_d")${_tail:+/}$_tail"
    _d=$_parent
  done
  _real=$(cd "$_d" 2>/dev/null && pwd -P) || _real=$_d
  [ -n "$_tail" ] && _real="$_real/$_tail"
  lexical_abs "$_real"
}

TOOL=$(printf '%s\n' "$FIELDS" | sed -n '1p')
CMD=$(printf '%s\n' "$FIELDS" | sed -n '2p')
FILE=$(printf '%s\n' "$FIELDS" | sed -n '3p')

case "$TOOL" in
  Edit|Write|NotebookEdit|MultiEdit)
    [ -n "$FILE" ] || exit 0
    [ -n "${ORCA_UNIT_WORKTREE:-}" ] || exit 0
    BOUND=$(cd "$ORCA_UNIT_WORKTREE" 2>/dev/null && pwd -P) || BOUND=""
    if [ -z "$BOUND" ]; then
      decide deny "deny-hook: ORCA_UNIT_WORKTREE is set but does not resolve to a directory. Fail-closed."
      exit 0
    fi
    # Resolve the final component's symlink, then its directory, so a symlink
    # inside the boundary is judged by where it actually points.
    DIR=$(dirname -- "$FILE")
    BASE=$(basename -- "$FILE")
    REAL=$(resolve_dir "$DIR")
    if [ -n "$REAL" ] && [ -L "$REAL/$BASE" ]; then
      TARGET=$(readlink "$REAL/$BASE" 2>/dev/null || printf '')
      case "$TARGET" in
        "") : ;;
        /*) REAL=$(resolve_dir "$(dirname -- "$TARGET")") ;;
        *) REAL=$(resolve_dir "$REAL/$(dirname -- "$TARGET")") ;;
      esac
    fi
    if [ -z "$REAL" ]; then
      decide deny "deny-hook: the write target could not be resolved to an absolute path. Fail-closed."
      exit 0
    fi
    case "$REAL/" in
      "$BOUND"/*) exit 0 ;;
      *) decide deny "deny-hook: this worker may only write inside its own worktree. The target resolves outside the unit boundary."
         exit 0 ;;
    esac
    ;;
  Bash) : ;;
  *) exit 0 ;;
esac

[ -n "$CMD" ] || exit 0

# --- HIGH tier (deny) --------------------------------------------------------
# Simple commands only: a compound command's effective target is unknowable by
# string matching, so it falls through to the Never-list ask below.
IS_SIMPLE=1
case "$CMD" in
  *';'*|*'&&'*|*'||'*|*'|'*) IS_SIMPLE=0 ;;
esac

has() { printf '%s' "$CMD" | grep -qE "$1" 2>/dev/null; }

if [ "$IS_SIMPLE" -eq 1 ]; then
  # 1. Recursive delete of a root-class target, or --no-preserve-root anywhere.
  if has '^[[:space:]]*(sudo[[:space:]]+)?rm[[:space:]]' \
    && has '(^|[[:space:]])(-[a-zA-Z]*[rR][a-zA-Z]*|--recursive)([[:space:]]|$)'; then
    if has '(^|[[:space:]])--no-preserve-root([[:space:]]|$)'; then
      decide deny "deny-hook[HIGH]: rm --no-preserve-root is refused. No task authorizes disabling the root guard."
      exit 0
    fi
    ROOTY=0; SAFE=0
    set -f
    for TOK in $CMD; do
      TOK=${TOK#\"}; TOK=${TOK%\"}; TOK=${TOK#\'}; TOK=${TOK%\'}
      case "$TOK" in
        sudo|rm|-*|--|[0-9]'>'*|'>'*|'<'*|'&') continue ;;
        '/'|'//'|'/*'|'~'|'~/'|'$HOME'|'$HOME/'|'${HOME}'|'${HOME}/') ROOTY=1 ;;
        *) SAFE=1 ;;
      esac
    done
    set +f
    if [ "$ROOTY" -eq 1 ] && [ "$SAFE" -eq 0 ]; then
      decide deny "deny-hook[HIGH]: recursive delete of / or the home directory is refused. Delete a named path inside the unit worktree instead."
      exit 0
    fi
  fi

  # 2/3. Force-push. A lease makes a force-push recoverable; without one it is
  # refused outright, and with one it is never HIGH even against the default branch.
  if has '^[[:space:]]*(sudo[[:space:]]+)?git[[:space:]]+push([[:space:]]|$)' \
    && ! has '(^|[[:space:]])--force-with-lease'; then
    HAS_FORCE=0
    has '(^|[[:space:]])(-f|--force)($|[[:space:]])' && HAS_FORCE=1
    has '(^|[[:space:]])\+[^[:space:]]' && HAS_FORCE=1
    if [ "$HAS_FORCE" -eq 1 ]; then
      DEFAULT_BRANCH=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's|^refs/remotes/origin/||' || true)
      if [ -z "$DEFAULT_BRANCH" ]; then
        if git show-ref --verify -q refs/remotes/origin/main 2>/dev/null; then DEFAULT_BRANCH="main"
        elif git show-ref --verify -q refs/remotes/origin/master 2>/dev/null; then DEFAULT_BRANCH="master"
        fi
      fi
      TARGETS_DEFAULT=0
      if [ -n "$DEFAULT_BRANCH" ]; then
        set -f
        for TOK in $CMD; do
          TOK=${TOK#\"}; TOK=${TOK%\"}; TOK=${TOK#\'}; TOK=${TOK%\'}
          case "$TOK" in git|push|sudo|-*) continue ;; esac
          REF=${TOK#+}; REF=${REF##*:}
          [ "$REF" = "$DEFAULT_BRANCH" ] && TARGETS_DEFAULT=1 && break
        done
        set +f
      fi
      if [ "$TARGETS_DEFAULT" -eq 1 ]; then
        decide deny "deny-hook[HIGH]: force-push to the default branch is refused. It rewrites the history everyone else builds on."
      else
        decide deny "deny-hook[HIGH]: git push --force without --force-with-lease is refused. Use --force-with-lease so a concurrent push cannot be silently discarded."
      fi
      exit 0
    fi
  fi

  # 4. Fleet-wide orchestration reset.
  if has '^[[:space:]]*(sudo[[:space:]]+)?orca[[:space:]]+orchestration[[:space:]]+reset([[:space:]]|$)'; then
    decide deny "deny-hook[HIGH]: 'orca orchestration reset' discards the whole fleet's dispatch state. A worker never resets the orchestration it runs inside."
    exit 0
  fi
fi

# --- Never list (ask) --------------------------------------------------------
ask() { decide ask "deny-hook[NEVER-LIST]: $1 Per runtime/sandbox-policy.md this needs a recorded human grant before it runs."; exit 0; }

has '(^|[[:space:]])rm[[:space:]]+(-[a-zA-Z]*[rR][a-zA-Z]*|--recursive)' && ask "Recursive delete."
has '(DROP|TRUNCATE)[[:space:]]+(TABLE|DATABASE|SCHEMA)' && ask "Destructive database statement."
has '(^|[[:space:]])(kubectl|helm)[[:space:]]+(delete|uninstall)' && ask "Cluster resource teardown."
has '(^|[[:space:]])terraform[[:space:]]+(destroy|apply)' && ask "Infrastructure mutation."
has '(^|[[:space:]])(aws|gcloud|az)[[:space:]]+[a-z0-9-]+[[:space:]]+(delete|rm|destroy|terminate)' && ask "Cloud resource deletion."
has '(^|[[:space:]])docker[[:space:]]+(system[[:space:]]+prune|rm[[:space:]]+-f|volume[[:space:]]+rm)' && ask "Container or volume destruction."
has 'curl[^|]*\|[[:space:]]*(ba|z|d|k)?sh' && ask "Piping a remote script into a shell."
has '(^|[[:space:]])(npm|pnpm|yarn|cargo|gem|twine)[[:space:]]+publish' && ask "Publishing a package."
has '(^|[[:space:]])git[[:space:]]+reset[[:space:]]+--hard' && ask "Discarding uncommitted work."
has '(^|[[:space:]])git[[:space:]]+(checkout|restore)[[:space:]]+\.' && ask "Discarding every local change."
has '(^|[[:space:]])gh[[:space:]]+secret[[:space:]]+(set|delete)' && ask "Writing or removing a repository secret."
has '(^|[[:space:]])(aws[[:space:]]+iam|gcloud[[:space:]]+iam)[[:space:]]+.*(create|add)' && ask "Provisioning a credential or identity."
has '(^|[[:space:]])git[[:space:]]+push[^|;]*(prod|production|release)' && ask "Pushing to a production ref."

exit 0
