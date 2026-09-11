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
# HIGH tier (deny, never ask) for Bash. Every segment of a compound command is
# judged on its own, with env/VAR= prefixes stripped first, so a refused shape
# is refused wherever it sits rather than only in first position (#297). Still
# string matching: a segment whose target comes from a variable or a subshell is
# beyond it, and the Never list is the net for those. The refused shapes:
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
# Worktree boundary: when ORCA_UNIT_WORKTREE is set, a write outside it is DENIED.
# It covers the Edit/Write/NotebookEdit/MultiEdit file_path, and — since a worker
# that can run a shell can spell the same write as `echo pwned > /etc/cron.d/x`
# — a Bash redirect or `tee` destination naming an ABSOLUTE path (#297). Both go
# through one resolver, which follows the whole symlink chain, so an in-boundary
# name pointing out is judged by where it ends up however many links that takes.
#
# What the Bash half does NOT cover, and says so at the block itself: a relative
# target (the hook is not told the worker's cwd, and the segment before it may
# have been a `cd`, so judging one would be guessing), a `cp`/`mv`/`dd of=`
# destination, a path built from a variable, and an interpreter writing through
# its own API. The disposable sandbox is the boundary for those. The process's
# own standard streams and /dev/null are allowed by name — not by a /dev/ prefix,
# which would waive `> /dev/sda` along with them.
#
# A payload that parses but names no file_path (a non-file tool) is allowed. When
# the variable is unset the boundary is not enforced — an unset boundary is a
# configuration choice, and this hook says so rather than guessing one.
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
  ORCA_UNIT_WORKTREE  when set, a write outside this directory is denied: the
                      Edit/Write file_path, and a Bash redirect or tee
                      destination naming an absolute path.

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
  # Serialized, never interpolated: a POSIX path may legally contain a quote, a
  # backslash or a control character, and pasting one into a hand-built JSON
  # string yields either invalid JSON or a DIFFERENT path — a boundary silently
  # set somewhere else is worse than no boundary (PR #277 review, P2). Same
  # json.dumps the decision path below already uses.
  python3 -c 'import json,sys; print(json.dumps({
      "env": {"ORCA_UNIT_WORKTREE": sys.argv[1]},
      "hooks": {"PreToolUse": [{
          "matcher": "Bash|Edit|Write|NotebookEdit|MultiEdit",
          "hooks": [{"type": "command", "command": sys.argv[2]}],
      }]},
  }, indent=2))' "$_wt" "$_self" || {
    echo "deny-hook.sh --settings: python3 is required to emit valid JSON" >&2
    exit 2
  }
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
def c(v):
    # The three-line protocol below cannot carry an embedded newline, but in a
    # shell a newline SEPARATES two commands exactly as `;` does. Flattening it
    # to a space glued them into one nonsense segment that matched nothing, so a
    # two-line payload walked straight past the HIGH tier (#297). Map it to the
    # separator it actually is and let the splitter do its job.
    return v.replace("\r", "\n").replace("\n", " ; ") if isinstance(v, str) else ""
print(s(d.get("tool_name")))
print(c(ti.get("command")))
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

# resolve_target sets RESOLVED to the physical directory the final component of
# $1 actually lives in, following the WHOLE symlink chain. Resolving a single hop
# denied `wt/link -> /outside/f` and allowed `wt/a -> wt/b -> /outside/f` — the
# same escape with one more link in it, and the attacker picks the number of
# links (#297). Bounded, so a cycle cannot spin here; exhausting the bound is a
# refusal, not a pass. It sets a global rather than printing one because a
# command substitution would run the refusal below in a subshell, where `exit`
# exits the substitution and the hook carries on to allow.
resolve_target() {
  _base=$(basename -- "$1")
  RESOLVED=$(resolve_dir "$(dirname -- "$1")")
  _hops=0
  while [ -n "$RESOLVED" ] && [ -L "$RESOLVED/$_base" ]; do
    _hops=$((_hops + 1))
    if [ "$_hops" -gt 32 ]; then
      decide deny "deny-hook: the write target is a symlink chain over 32 links deep, or a cycle. Fail-closed."
      exit 0
    fi
    _tgt=$(readlink "$RESOLVED/$_base" 2>/dev/null || printf '')
    [ -n "$_tgt" ] || break
    case "$_tgt" in
      /*) RESOLVED=$(resolve_dir "$(dirname -- "$_tgt")") ;;
      *)  RESOLVED=$(resolve_dir "$RESOLVED/$(dirname -- "$_tgt")") ;;
    esac
    _base=$(basename -- "$_tgt")
  done
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
    # Judged by where the final component actually points, not by its own name.
    resolve_target "$FILE"
    REAL=$RESOLVED
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
# Each SEGMENT of the command line is judged on its own. This block used to run only when the
# command contained no ';', '&&', '||' or '|', and the header claimed a compound command "falls
# through to the Never-list ask". It did not — it was ALLOWED, silently. `cd /x && rm
# --no-preserve-root -rf /` and `env FOO=1 rm --no-preserve-root -rf /` both passed, so putting
# anything at all in front of a refused command defeated the entire tier (#297).
#
# This is still string matching and still cannot resolve what a command DOES: a segment whose
# target comes from a variable or a subshell is beyond it, and the Never list below is the net for
# those. What it buys is that the refused shapes are refused wherever they sit.
#
# The split does not parse quoting, so a separator inside a quoted string splits too: `git commit
# -m "oops; rm -rf /"` is refused for a string it would only ever have written down. That is the
# direction the error has to point. Splitting can only ever produce MORE segments, and every
# segment is judged, so a dangerous command cannot be hidden inside quotes from a splitter that
# ignores them — `rm -rf "/;x"` still lands as a segment whose only target is `/`.
FULL_CMD=$CMD
has() { printf '%s' "$CMD" | grep -qE "$1" 2>/dev/null; }

# Drop env/sudo-style prefixes so a refused command cannot be laundered by putting something
# harmless in front of it. `sudo` is deliberately NOT stripped — the patterns match it themselves.
strip_prefix() {
  _c=$1
  while : ; do
    case "$_c" in
      # A quoted value holds spaces. Stripping to the first space left `b" rm --no-preserve-root
      # -rf /`, which begins with neither `rm` nor anything else the tier knows (PR #308 review,
      # P1). Strip to the closing quote instead. A value containing an ESCAPED quote is beyond
      # string matching and stays beyond it; it cannot hide a command, only mangle a prefix.
      [A-Za-z_]*=\"*) _rest=${_c#*=\"}; _c=${_rest#*\" } ;;
      [A-Za-z_]*=\'*) _rest=${_c#*=\'}; _c=${_rest#*\' } ;;
      [A-Za-z_]*=*[!\ ]*\ *) _c=${_c#* } ;;
      env\ *)     _c=${_c#env } ;;
      nohup\ *)   _c=${_c#nohup } ;;
      time\ *)    _c=${_c#time } ;;
      command\ *) _c=${_c#command } ;;
      builtin\ *) _c=${_c#builtin } ;;
      \ *)        _c=${_c# } ;;
      *) break ;;
    esac
  done
  printf '%s' "$_c"
}

# Split on ; && || | & into positional parameters — POSIX, and no subshell, so a `decide deny`
# inside the loop still exits the script.
#
# A bare `&` separates two commands exactly as `;` does, and leaving it out let `true & rm
# --no-preserve-root -rf /` through (PR #308 review, P1). Two operators that merely CONTAIN one of
# these characters are protected first, or splitting would shred them: `>|` is the noclobber
# redirect, not a pipe, and `>&` is a redirect whose `&` would leave the `>` dangling in one segment
# and its target alone in the next. `&>` needs no protection — splitting at its `&` leaves `>
# target` whole in the following segment, which reads identically. That is measured, not assumed:
# protecting it survived every mutant, which is how this hook learns a line of it is inert.
_SEP=$(printf '\001')
_P1=$(printf '\002'); _P3=$(printf '\004')
_SPLIT=$(printf '%s' "$FULL_CMD" \
  | sed -e "s/>|/$_P1/g" -e "s/&&/$_SEP/g" -e "s/>&/$_P3/g" \
        -e "s/||/$_SEP/g" -e "s/|/$_SEP/g" -e "s/;/$_SEP/g" -e "s/&/$_SEP/g" \
        -e "s/$_P1/>|/g" -e "s/$_P3/>\&/g")
_OLDIFS=$IFS
IFS=$_SEP
set -f
# shellcheck disable=SC2086
set -- $_SPLIT
set +f
IFS=$_OLDIFS

for _SEG in "$@"; do
  CMD=$(strip_prefix "$_SEG")
  [ -n "$(printf '%s' "$CMD" | tr -d '[:space:]')" ] || continue
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
  if has '^[[:space:]]*(sudo[[:space:]]+)?orca(-ide)?[[:space:]]+orchestration[[:space:]]+reset([[:space:]]|$)'; then
    decide deny "deny-hook[HIGH]: 'orca orchestration reset' discards the whole fleet's dispatch state. A worker never resets the orchestration it runs inside."
    exit 0
  fi
done

# --- worktree boundary for Bash writes ---------------------------------------
# The boundary used to be applied only to an Edit/Write payload, so a bounded
# worker could write anywhere it liked by spelling the write as a shell line:
# `echo pwned > /etc/cron.d/x` was ALLOWED (#297). A redirect and a `tee`
# destination are the two file writes in a shell line that can be read off the
# text without knowing what the command does, so those are the two this covers.
#
# ABSOLUTE targets only. A relative target resolves against a working directory
# this hook cannot know — the host does not hand it the worker's cwd, and the
# segment before it may have been a `cd` — so judging one would be guessing, and
# a boundary that guesses at half its cases is worse than one that says what it
# covers. Deliberately NOT covered: `cp`/`mv`/`install` destinations, `dd of=`,
# an interpreter writing through its own API, a path built from a variable, and
# every relative path. The disposable sandbox is the boundary for those; this is
# defense in depth, the same advisory status the rest of this hook carries.
if [ -n "${ORCA_UNIT_WORKTREE:-}" ]; then
  BOUND=$(cd "$ORCA_UNIT_WORKTREE" 2>/dev/null && pwd -P) || BOUND=""
  if [ -z "$BOUND" ]; then
    decide deny "deny-hook: ORCA_UNIT_WORKTREE is set but does not resolve to a directory. Fail-closed."
    exit 0
  fi

  bounded_write() {
    _t=$1
    _t=${_t#\"}; _t=${_t%\"}; _t=${_t#\'}; _t=${_t%\'}
    case "$_t" in /*) : ;; *) return 0 ;; esac
    # The process's own standard streams and the bit bucket. `make > /dev/null`
    # is the most common redirect there is and writes nothing anyone can read;
    # refusing it would make the boundary a thing workers route around. Named
    # one by one, not as a /dev/ prefix — `> /dev/sda` IS an escape.
    case "$_t" in
      /dev/null|/dev/zero|/dev/full|/dev/tty|/dev/stdout|/dev/stderr|/dev/stdin|/dev/fd/*)
        return 0 ;;
    esac
    resolve_target "$_t"
    [ -n "$RESOLVED" ] || return 0
    case "$RESOLVED/" in "$BOUND"/*) return 0 ;; esac
    decide deny "deny-hook: this worker may only write inside its own worktree. A shell redirect or tee destination names an absolute path outside the unit boundary."
    exit 0
  }

  for _SEG in "$@"; do
    # `tee` counts only as the segment's own command — `grep tee /etc/passwd`
    # reads a file, and refusing a read here would be a boundary inventing work.
    _TEE=0
    case "$(strip_prefix "$_SEG")" in tee|tee\ *) _TEE=1 ;; esac
    _PENDING=0
    set -f
    # shellcheck disable=SC2086
    for TOK in $_SEG; do
      if [ "$_PENDING" -eq 1 ]; then
        _PENDING=0
        bounded_write "$TOK"
        continue
      fi
      case "$TOK" in
        '>'|'>>'|'>|'|'>&'|[0-9]'>'|[0-9]'>>'|[0-9]'>|') _PENDING=1 ;;
        # `>&file` is bash's both-streams redirect and writes a file; `>&1` and
        # `>&2` duplicate a descriptor. A bare digit is relative, so both reach
        # bounded_write and only the path is ever judged — no arm of its own.
        # (`&>file` never arrives here: the splitter above cuts at its `&`, and
        # the `> file` half lands in the next segment.)
        '>&'*)      bounded_write "${TOK#'>&'}" ;;
        [0-9]'>>'*) bounded_write "${TOK#?'>>'}" ;;
        [0-9]'>|'*) bounded_write "${TOK#?'>|'}" ;;
        [0-9]'>'*)  bounded_write "${TOK#?'>'}" ;;
        '>>'*)      bounded_write "${TOK#'>>'}" ;;
        '>|'*)      bounded_write "${TOK#'>|'}" ;;
        '>'*)       bounded_write "${TOK#'>'}" ;;
        -*) : ;;
        *) if [ "$_TEE" -eq 1 ]; then bounded_write "$TOK"; fi ;;
      esac
    done
    set +f
  done
fi
CMD=$FULL_CMD

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
