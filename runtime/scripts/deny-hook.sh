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
#      needs no flag at all — and deleting it outright, which carries no flag
#      either: `:main`, `git push -d`, `git push --delete` (#297)
#   3. effective `git push --force` / `-f`, on any target: explicit global
#      force disables --force-with-lease checks, even when a lease is supplied
#   4. `orca orchestration reset` — one command that discards a whole fleet's
#      dispatch state
# Git global options between `git` and the subcommand (-C, -c, --git-dir and
# kin) are stripped before any of this is judged — `git -C /x push --force` is
# the push it names (#297). A deletion that spares the default branch asks
# rather than denies: re-pushing the ref recovers it, and recovery is a human
# call — except under a redirected repository (-C, --git-dir, GIT_DIR=), where
# the default is resolved in the hook's own cwd and the ref cannot be shown
# recoverable, so any remote-ref deletion denies (#321 review).
# --force-with-lease is deliberately NOT matched as a force-push — but a
# lease does not pardon a deletion (judged first) or an effective explicit
# global force, which Git documents as disabling the lease checks.
#
# Never list (ask, per runtime/sandbox-policy.md): live-prod mutation, credential
# provisioning, destructive database or infrastructure teardown, unpinned remote
# code execution, publishing, and history-discarding local git. These are "ask"
# rather than "deny" because each has a legitimate form the human can authorize
# in the moment; the HIGH tier has none.
#
# Worktree boundary: when ORCA_UNIT_WORKTREE is set, a write outside it is DENIED.
# It covers the Edit/Write/MultiEdit file_path and NotebookEdit's notebook_path
# — the one write tool that spells the field differently (#297) — and, since a
# worker that can run a shell can spell the same write as `echo pwned >
# /etc/cron.d/x`, a Bash redirect or `tee` destination naming an ABSOLUTE path. Both go
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
                      Edit/Write/MultiEdit file_path or NotebookEdit
                      notebook_path, and a Bash redirect or tee destination
                      naming an absolute path.

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
FIELDS=$(printf '%s' "$PAYLOAD" | python3 -c 'import json,re,shlex,sys
d = json.loads(sys.stdin.read())
if not isinstance(d, dict):
    raise SystemExit(1)
ti = d.get("tool_input") or {}
if not isinstance(ti, dict):
    ti = {}
def s(v):
    return v.replace("\n", " ") if isinstance(v, str) else ""
def r(v):
    # The command as the shell sees it, newlines intact. `segments` needs them:
    # a newline separates two commands, and it is also the only thing that ENDS
    # a # comment. Pre-mapping it to `;` erased that boundary, so a comment had
    # no end to find (PR #325 review, P1).
    return v.replace("\r", "\n") if isinstance(v, str) else ""
def c(v):
    # The as-written Never-list pass reads this off a single line of the field
    # protocol, which cannot carry an embedded newline. In a shell a newline
    # SEPARATES two commands exactly as `;` does; flattening it to a space glued
    # them into one nonsense segment that matched nothing, so a two-line payload
    # walked straight past the HIGH tier (#297). Map it to the separator it
    # actually is. The splitter reads `r` instead and needs no such compromise.
    return r(v).replace("\n", " ; ")


# NOTE: this whole program is the argument of a single-quoted sh string, so it may not contain
# an apostrophe anywhere — not in code, not in a comment. SQ/DQ are how a quote character is
# named here. A stray one ends the sh string and the payload reader dies, which fails closed and
# refuses every tool call.
SQ = chr(39)
DQ = chr(34)
# What a shell splits words on. NOT str.isspace(): Python calls NBSP and friends
# whitespace, a shell does not, and a word boundary the shell never saw is one this
# parser must not invent either (PR #325 review, P1).
BLANKS = chr(32) + chr(9)


def segments(cmd):
    """Split a shell line into command segments, QUOTE-AWARE.

    This was a sed pass over the raw text, and a separator inside a quoted string split there
    too. The header called that safe, reasoning that splitting only ever makes MORE segments and
    every segment is judged. That reasoning was wrong: the split leaves the rest of the quoted
    value glued to the FRONT of the next segment, and every HIGH-tier rule is anchored at ^.
    X=<dq>a&b<dq> git push --force origin main became `b<dq> git push --force origin main`, which
    begins with neither git nor anything else the tier knows, and was allowed (PR #308 review,
    P1). Same for ; and | inside a value.

    Quoting is parsed here rather than in sh because a POSIX shell cannot do it without eval, and
    python3 is already load-bearing above: no parser, no decision, and this whole script denies.
    Redirect operators are consumed whole so their | and & are never read as separators.

    A # that OPENS A WORD opens a comment, which runs to the end of its line. Nothing recognized
    them, so `git status # dont modify anything` was tokenized as shell: the apostrophe in the
    comment opened a quote that never closed, shlex raised, and the payload reader hard-DENIED a
    read-only command (PR #325 review, P1). Word position is what decides it, exactly as in a
    shell: after a redirect operator `>#f` names a file, and un-seeing that word would lose a
    write target, which is the one direction this parser must never fail in.
    """
    segs, cur = [], []
    i, n, quote = 0, len(cmd), ""
    word_start = True
    while i < n:
        ch = cmd[i]
        # A backslash-newline is a line continuation. The shell REMOVES it -- inside double
        # quotes as well as outside -- and the text on either side is one word. Keeping it opened
        # two holes (PR #325 review, P1): the newline rode into a word and broke the one-line
        # record protocol below, forging a C record that reset tee enforcement so the write
        # target after it went unchecked; and counting it as a word boundary made
        # echo a\<newline>#b a comment, swallowing the command after it. Removing it here leaves
        # word_start untouched, which is the point: a continuation neither opens nor closes a
        # word. Single quotes take no escapes, so it is literal there.
        if ch == "\\" and quote != SQ and i + 1 < n and cmd[i + 1] == "\n":
            i += 2
            continue
        if quote:
            # A literal newline inside a quoted word is data, not a boundary. It cannot travel on
            # the one-line record protocol below, so it rides as a space: a value, still one word.
            cur.append(" " if ch == "\n" else ch)
            if ch == "\\" and quote == DQ and i + 1 < n:
                cur.append(cmd[i + 1])
                i += 2
                continue
            if ch == quote:
                quote = ""
            word_start = False
            i += 1
            continue
        if ch == SQ or ch == DQ:
            quote = ch
            cur.append(ch)
            word_start = False
            i += 1
            continue
        if ch == "\\" and i + 1 < n:
            cur.append(ch)
            cur.append(cmd[i + 1])
            word_start = False   # an escaped character is a word character
            i += 2
            continue
        if ch == "#" and word_start:
            while i < n and cmd[i] != "\n":
                i += 1
            continue   # the newline itself falls through to the separator case below
        if ch in "<>" or (ch == "&" and i + 1 < n and cmd[i + 1] == ">"):
            j = i + 1
            while j < n and cmd[j] in "<>|&":
                j += 1
            cur.append(cmd[i:j])
            word_start = False
            i = j
            continue
        # && and || need no case of their own: the second character lands on a separator too, and
        # the empty segment between them is dropped below. Measured, not assumed — a mutant
        # removing a special case for them changed no decision, so there is no special case.
        # A newline is a separator too, and the one that ends a comment.
        if ch in ";|&\n":
            segs.append("".join(cur))
            cur = []
            word_start = True
            i += 1
            continue
        cur.append(ch)
        word_start = ch in BLANKS
        i += 1
    segs.append("".join(cur))
    return [seg for seg in segs if seg.strip()]


def policy_word(word):
    # This is an internal comparison word, NEVER shell code. Encode whitespace,
    # quotes and escapes so shell word splitting cannot turn one operand into
    # flags/refspecs. Literal command/option words lose their shell quoting.
    return "".join("\\%03o" % ord(ch) if ch.isspace() or ch in (SQ, DQ, "\\")
                   else ch for ch in word) or "\\000"


def shell_tokens(seg):
    # Keep operator identity BEFORE quote removal: quoted/escaped > is data.
    # A descriptor is optional and may have several digits. After an operator,
    # however, the next word is its target: in 10>&1>file, 1 is not another fd.
    ops = r"(?:&>>|&>|>>|>\||>&|<>|<<<|<<-|<<|<&|>|<)"
    i, target = 0, False
    while i < len(seg):
        if seg[i].isspace():
            i += 1
            continue
        op = re.match(ops if target else r"[0-9]*" + ops, seg[i:])
        if op:
            yield "redirect", op[0].lstrip("0123456789")
            i += len(op[0])
            target = True
            continue
        start, quote = i, ""
        while i < len(seg):
            ch = seg[i]
            if ch == "\\" and quote != SQ:
                i += 2
                continue
            if quote:
                if ch == quote:
                    quote = ""
            elif ch in (SQ, DQ):
                quote = ch
            elif ch.isspace() or ch in "<>&":
                break
            i += 1
        if i == start:
            raise ValueError("unexpected operator")
        yield "word", shlex.split(seg[start:i])[0]
        target = False


def record(kind, value):
    # One record, one line. A value carrying a newline forges the NEXT record, and a forged
    # C line resets tee enforcement so the write target after it is never checked (PR #325
    # review, P1). segments() makes this unreachable -- an unquoted newline separates, a
    # quoted one rides as a space, a continuation is removed -- so anything arriving here
    # means that reasoning is wrong somewhere, and dying is the fail-closed answer.
    if "\n" in value or "\r" in value:
        raise ValueError("a record value cannot contain a newline")
    print(kind + " " + value)


raw_command = r(ti.get("command"))
command = c(raw_command)
print(s(d.get("tool_name")))
print(command)
# NotebookEdit names its target notebook_path, not file_path — reading only
# file_path left the one write tool that spells the field differently free of
# the boundary entirely (#297).
print(s(ti.get("file_path") or ti.get("notebook_path")))
# Line 4 onward: C = comparison command, W = write target, A = literal argument.
# Paths stay decoded on their own lines; comparison words cannot split operands.
for seg in segments(raw_command):
    args, writes, pending = [], [], None
    for kind, value in shell_tokens(seg):
        if kind == "redirect":
            pending = value
        elif pending:
            if pending in (">", ">>", ">|", ">&", "&>", "&>>", "<>"):
                writes.append(value)
            pending = None
        else:
            args.append(value)
    record("C", " ".join(policy_word(word) for word in args))
    for path in writes:
        record("W", path)
    for word in args:
        record("A", word)' 2>/dev/null) || {
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
# The split IS quote-aware (see `segments` in the payload reader), so `git commit -m "oops; rm -rf
# /"` is one segment naming `git commit`, and `rm -rf "/;x"` is one segment whose only target is a
# file literally called `/;x`. An earlier cut split on the raw text and argued that was safe
# because splitting only ever makes MORE segments. It is not: the split leaves the rest of the
# quoted value glued to the FRONT of the next segment, and every rule here is anchored at `^`.
FULL_CMD=$CMD
has() { printf '%s' "$CMD" | grep -qE "$1" 2>/dev/null; }

# Drop env/sudo-style prefixes so a refused command cannot be laundered by putting something
# harmless in front of it. `sudo` is peeled but REATTACHED — the rules below match `sudo`
# themselves — because an assignment under it (`sudo GIT_DIR=x git push -d`) otherwise hid
# the whole command from every anchored pattern (PR #321 review).
strip_prefix() {
  _c=$1
  _pre=""
  case "$_c" in sudo\ *) _pre="sudo "; _c=${_c#sudo } ;; esac
  while : ; do
    case "$_c" in
      env\ *)     _c=${_c#env } ;;
      nohup\ *)   _c=${_c#nohup } ;;
      time\ *)    _c=${_c#time } ;;
      command\ *) _c=${_c#command } ;;
      builtin\ *) _c=${_c#builtin } ;;
      \ *)        _c=${_c# } ;;
      # A NAME=value prefix only IS a prefix when the `=` lives in the FIRST
      # token — a glob cannot confine it there (`*` crosses spaces), so the
      # inner case re-checks the first token alone. An `=` further right is an
      # option operand — `git -c a=b push -f`, `git --git-dir=/x push` — and
      # letting this arm fire there ate `git ` and freed the options after it
      # (#297). A quoted value cuts at its closing quote, not the first space
      # (PR #308 review, P1); an ESCAPED quote inside stays beyond it.
      [A-Za-z_]*=*[!\ ]*\ *)
        case "${_c%% *}" in
          [A-Za-z_]*=*) _c=$(skip_tok "$_c") ;;
          *) break ;;
        esac ;;
      *) break ;;
    esac
  done
  printf '%s%s' "$_pre" "$_c"
}

# git's global options sit between `git` and the subcommand, and every rule here
# anchors the subcommand to the word `git`: `git -C /x push --force`,
# `git -c a=b push -f`, `git --git-dir=/x push --force` all named refused pushes
# and were ALLOWED (#297). Strip the leading option run — an option that takes
# a separate operand drops the operand too, and a quoted operand is cut at its
# closing quote, not the next space. Glued forms need no arm: git rejects
# `-C/x` and `-ca=b` itself. An option this does not know ends the run and the
# segment is judged as written — a future global option still evades, which is
# the same string-matching limit the tier already states above.
strip_git_opts() {
  case "$1" in
    git\ *)       _pre="";      _rest=${1#git } ;;
    sudo\ git\ *) _pre="sudo "; _rest=${1#sudo git } ;;
    *)            printf '%s' "$1"; return ;;
  esac
  while : ; do
    case "$_rest" in
      # Options taking a separate operand: drop the option, then the operand.
      -C\ *|-c\ *|--git-dir\ *|--work-tree\ *|--namespace\ *|--config-env\ *)
        _rest=${_rest#* }
        _rest=$(skip_tok "$_rest") ;;
      # Immediate-exit options print and stop — `git --html-path push --force`
      # never pushes at all, and stripping the option would judge tokens git
      # ignores (PR #321 review). Empty the rest so the segment normalizes to a
      # bare `git`. `--exec-path` is here, not in the operand arm: git's own
      # `[=path]` is optional-and-inline, so a separate token after it is just
      # more ignored text.
      --html-path|--html-path\ *|--man-path|--man-path\ *|--info-path|--info-path\ *|\
      --exec-path|--exec-path\ *|--version|--version\ *|--help|--help\ *|-h|-h\ *)
        _rest=""; break ;;
      # Inline `--opt=value`: drop `name=` then the whole word — the value may
      # quote only its middle (`=/srv/dir" one"`), so it goes through skip_tok
      # like any other operand (PR #321 review, P1).
      --git-dir=*|--work-tree=*|--namespace=*|--exec-path=*|--config-env=*)
        _rest=${_rest#*=}
        _rest=$(skip_tok "$_rest") ;;
      # Valueless flags drop one token each.
      -p\ *|-P\ *|--paginate\ *|--no-pager\ *|--bare\ *|--no-replace-objects\ *|--no-advice\ *|\
      --literal-pathspecs\ *|--glob-pathspecs\ *|--noglob-pathspecs\ *|--icase-pathspecs\ *|\
      --no-optional-locks\ *)
        _rest=${_rest#* } ;;
      *) break ;;
    esac
  done
  printf '%sgit %s' "$_pre" "$_rest"
}

# Collapse every whitespace run to one space and trim the ends. The prefix and
# option arms match single literal spaces, so `git -C␣␣/x` or a tab after `-C`
# left the options in place and the refused push unmatched (PR #321 review).
# Collapsing a quoted value's interior is harmless — rules never inspect a
# value, only the command around it.
norm_ws() {
  _n=$(printf '%s' "$1" | tr -s '[:space:]' ' ')
  _n=${_n# }; _n=${_n% }
  printf '%s' "$_n"
}

# Remove the first shell WORD from $1 and print what follows. A word may quote
# only part of itself — `--git-dir=/srv/dir" one"` is one word — and a `\x`
# escape binds anywhere, including `\ ` for a space (#321 review) — so scanning
# must skip quoted spans and escaped chars wherever they sit. An unclosed
# quote eats to end: that mangles the line, it cannot free a refused command.
skip_tok() {
  _w=$1
  while : ; do
    _p=$_w
    case "$_w" in
      \"*)
        _w=${_w#\"}
        while : ; do
          _i=$_w
          _q=${_w%%[\\\"]*}
          _w=${_w#"$_q"}
          case "$_w" in
            \"*) _w=${_w#\"}; break ;;
            \\*) _w=${_w#\\?} ;;
            *)   break ;;
          esac
          [ "$_w" = "$_i" ] && break
        done ;;
      \'*)    _w=${_w#\'}; _w=${_w#*\'} ;;
      *)      _h=${_w%%[\\\'\" ]*}; _w=${_w#"$_h"}
              case "$_w" in \\*) _w=${_w#\\?} ;; esac ;;
    esac
    [ "$_w" = "$_p" ] && break
    case "$_w" in \ *) break ;; esac
  done
  printf '%s' "${_w# }"
}

# `-C`, `--git-dir`, `--work-tree`, and GIT_DIR=/GIT_WORK_TREE= point a command
# at a DIFFERENT repository, but DEFAULT_BRANCH below is resolved in the hook's
# own working directory — so under a redirect nothing here can prove which ref
# the target repo calls its default (#321 review). Detected on the raw segment,
# before the options were stripped away. An env var only redirects when it sits
# in the leading assignment run — `feature/GIT_DIR=config` is a ref name, not
# a redirect (#321 review) — and the option run ends at `git` itself.
git_redirected() {
  _r=$1
  while : ; do
    case "$_r" in
      \ *)          _r=${_r# } ;;
      env\ *)       _r=${_r#env } ;;
      sudo\ *)      _r=${_r#sudo } ;;
      command\ *)   _r=${_r#command } ;;
      builtin\ *)   _r=${_r#builtin } ;;
      nohup\ *)     _r=${_r#nohup } ;;
      time\ *)      _r=${_r#time } ;;
      GIT_DIR=*|GIT_WORK_TREE=*) return 0 ;;
      # Any other assignment advances past its token — but only when the `=`
      # lives in the FIRST token, as in strip_prefix: `git --git-dir=/x` also
      # contains `=`+space and letting this arm fire there ate `git ` (#321
      # review). A trailing token with no space after fails the arm outright,
      # so the loop cannot spin on it; a quoted value cuts at its closing
      # quote, not the first space inside.
      [A-Za-z_]*=*\ *)
        case "${_r%% *}" in
          [A-Za-z_]*=*) _r=$(skip_tok "$_r") ;;
          *) break ;;
        esac ;;
      *) break ;;
    esac
  done
  case "$_r" in git\ *) _r=${_r#git } ;; *) return 1 ;; esac
  # Only git's LEADING global-option run can redirect — a `-C` sitting inside a
  # `-c` operand value is text, not an option, so the run is walked and every
  # operand skipped rather than substring-matched (#321 review).
  while : ; do
    case "$_r" in
      -C\ *|-C|--git-dir\ *|--git-dir|--work-tree\ *|--work-tree|\
      --git-dir=*|--git-dir=*\ *|--work-tree=*|--work-tree=*\ *)
        return 0 ;;
      -c\ *|-c|--namespace\ *|--namespace|--config-env\ *|--config-env)
        _r=${_r#* }
        _r=$(skip_tok "$_r") ;;
      --namespace=*|--config-env=*|--exec-path=*)
        _r=${_r#*=}
        _r=$(skip_tok "$_r") ;;
      -p|-p\ *|-P|-P\ *|--paginate|--paginate\ *|--no-pager|--no-pager\ *|\
      --bare|--bare\ *|--no-replace-objects|--no-replace-objects\ *|\
      --no-advice|--no-advice\ *|--literal-pathspecs|--literal-pathspecs\ *|\
      --glob-pathspecs|--glob-pathspecs\ *|--noglob-pathspecs|--noglob-pathspecs\ *|\
      --icase-pathspecs|--icase-pathspecs\ *|--no-optional-locks|--no-optional-locks\ *)
        _r=${_r#* } ;;
      *) return 1 ;;
    esac
  done
}

# Normalize push options only after the command/global-option run was resolved.
# Operand-taking options consume the rest of a short cluster or the next word;
# `-vof` carries push-option `f`, whereas `-vf` forces. Operand text must never
# supply a force flag, a lease, or a deleted ref to the HIGH tier.
push_policy() {
  python3 -c 'import sys
words = sys.argv[1].split()
out, skip, options = [], False, True
lease, force = False, False
for word in words:
    if skip:
        skip = False
        continue
    if word == "--":
        options = False
    elif options and word in ("-o", "--push-option", "--receive-pack", "--exec", "--repo"):
        skip = True
        continue
    elif word in ("--force", "--no-force", "-f"):
        if options:
            force = word != "--no-force"
        continue
    elif word == "--no-force-with-lease":
        if options:
            lease = False
        continue
    elif word == "--force-with-lease" or word.startswith("--force-with-lease="):
        if options:
            lease = True
        continue
    elif options and word.startswith("-") and not word.startswith("--"):
        cluster = word[1:]
        for i, flag in enumerate(cluster):
            if flag == "o":
                skip = i == len(cluster) - 1
                break
            if flag not in "vqnfdu46":
                out.append(word)
                break
            if flag == "f":
                force = True
                continue
            out.append("-" + flag)
        continue
    out.append(word)
# Emit only the effective lease; canceled leases and operands after -- cannot
# grant the HIGH-tier exemption. Explicit global force disables lease checks
# (git-push 2.55); --no-force clears that flag in command-line order.
if force:
    out.append("--force")
elif lease:
    out.append("--force-with-lease")
print(" ".join(out))' "$1"
}

# The C records carry PRE-SPLIT, word-normalized commands from the payload reader above. They
# are split there because splitting is quote-aware and a POSIX shell cannot parse quoting without
# eval: a separator inside a quoted value used to split too, leaving the rest of the value glued
# to the FRONT of the next segment, and every rule below is anchored at `^`. `X="a&b" git push
# --force origin main` became `b" git push --force origin main` and was allowed (PR #308 review,
# P1). Selecting only C records keeps literal path/argument records out of the HIGH tier.
# Loading the commands into positional parameters keeps the loop out of a subshell, so a
# `decide deny` inside it still exits the script.
_SEGS=$(printf '%s\n' "$FIELDS" | sed -n '4,$s/^C //p')
_OLDIFS=$IFS
IFS='
'
set -f
# shellcheck disable=SC2086
set -- $_SEGS
set +f
IFS=$_OLDIFS

for _SEG in "$@"; do
  _SEG_N=$(norm_ws "$_SEG")
  CMD=$(strip_git_opts "$(strip_prefix "$_SEG_N")")
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

  # 2/3. Force-push and deletion. An effective lease guards concurrent updates; a
  # deletion recovers nothing, so it is judged FIRST and no lease pardons it:
  # `git push origin :main`, `-d` and `--delete` carry no force flag at all and
  # sailed under both force rules (#297).
  if has '^[[:space:]]*(sudo[[:space:]]+)?git[[:space:]]+push([[:space:]]|$)'; then
    CMD=$(push_policy "$CMD")
    DEFAULT_BRANCH=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's|^refs/remotes/origin/||' || true)
    if [ -z "$DEFAULT_BRANCH" ]; then
      if git show-ref --verify -q refs/remotes/origin/main 2>/dev/null; then DEFAULT_BRANCH="main"
      elif git show-ref --verify -q refs/remotes/origin/master 2>/dev/null; then DEFAULT_BRANCH="master"
      fi
    fi

    # `-d`/`--delete` take their refs positionally; a `:dst` or `+:dst` refspec
    # names the deleted ref in the token itself. A bare `:` or `+:` is the
    # matching-branches push — an empty dst is not a deletion. `refs/heads/` is
    # stripped before comparing: `git push origin :refs/heads/main` deletes the
    # same ref `:main` does (#321 review).
    _DEL=0; _DEL_FLAG=0; _DEL_DEFAULT=0; _SKIP=0
    set -f
    for TOK in $CMD; do
      TOK=${TOK#\"}; TOK=${TOK%\"}; TOK=${TOK#\'}; TOK=${TOK%\'}
      # `-o`/`--push-option`, `--receive-pack`, `--repo` consume the next token —
      # its content is an option string, never a refspec: `-o :x` is not a
      # deletion of x (#321 review).
      [ "$_SKIP" -eq 1 ] && _SKIP=0 && continue
      case "$TOK" in
        -o|--push-option|--receive-pack|--exec|--repo) _SKIP=1 ;;
        -d|--delete) _DEL=1; _DEL_FLAG=1 ;;
        +:*|:*) _dst=${TOK#+}; _dst=${_dst#:}; _dst=${_dst#refs/heads/}
                [ -n "$_dst" ] || continue
                _DEL=1
                [ -n "$DEFAULT_BRANCH" ] && [ "$_dst" = "$DEFAULT_BRANCH" ] && _DEL_DEFAULT=1 ;;
      esac
    done
    set +f
    if [ "$_DEL" -eq 1 ] && git_redirected "$_SEG_N"; then
      # The push targets another repository while DEFAULT_BRANCH was resolved
      # in this one's cwd — the deleted ref cannot be shown recoverable, and
      # ask is the wrong answer for maybe-the-default. Deny.
      decide deny "deny-hook[HIGH]: deleting a remote ref under a redirected repository (-C/--git-dir/GIT_DIR) is refused — the hook cannot verify the target repo's default branch."
      exit 0
    fi
    if [ "$_DEL_FLAG" -eq 1 ] && [ -n "$DEFAULT_BRANCH" ]; then
      # The flag form names its refs among the positionals: a bare token equal
      # to the default branch — qualified or not (`--delete origin
      # refs/heads/main` is the same delete, #321 review) — is the ref being
      # deleted. A remote literally named after it earns a deny rather than a
      # silent delete — that is the error to err toward.
      _SKIP=0
      set -f
      for TOK in $CMD; do
        TOK=${TOK#\"}; TOK=${TOK%\"}; TOK=${TOK#\'}; TOK=${TOK%\'}
        [ "$_SKIP" -eq 1 ] && _SKIP=0 && continue
        case "$TOK" in
          -o|--push-option|--receive-pack|--exec|--repo) _SKIP=1; continue ;;
          git|push|sudo|-*) continue ;;
        esac
        TOK=${TOK#refs/heads/}
        [ "$TOK" = "$DEFAULT_BRANCH" ] && _DEL_DEFAULT=1 && break
      done
      set +f
    fi
    if [ "$_DEL_DEFAULT" -eq 1 ]; then
      decide deny "deny-hook[HIGH]: deleting the default branch is refused. The ref everyone else builds on is not a worker's to remove."
      exit 0
    fi
    if [ "$_DEL" -eq 1 ]; then
      decide ask "deny-hook[NEVER-LIST]: Deleting a remote ref. Per runtime/sandbox-policy.md this needs a recorded human grant before it runs."
      exit 0
    fi

    if ! has '(^|[[:space:]])--force-with-lease($|[[:space:]])'; then
      HAS_FORCE=0
      has '(^|[[:space:]])(-f|--force)($|[[:space:]])' && HAS_FORCE=1
      has '(^|[[:space:]])\+[^[:space:]]' && HAS_FORCE=1
      if [ "$HAS_FORCE" -eq 1 ]; then
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
          decide deny "deny-hook[HIGH]: unleased or explicit global force is refused. Use --force-with-lease without -f/--force so a concurrent push cannot be silently discarded."
        fi
        exit 0
      fi
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

  # Consume typed records without splitting paths on whitespace. The here-doc
  # keeps this loop in the main shell so a refusal exits the entire hook.
  _TEE=0
  while IFS= read -r _RECORD; do
    case "$_RECORD" in
      'C '*) _TEE=0
             case "$(strip_prefix "${_RECORD#C }")" in tee|tee\ *) _TEE=1 ;; esac ;;
      'W '*) bounded_write "${_RECORD#W }" ;;
      'A '*) if [ "$_TEE" -eq 1 ]; then bounded_write "${_RECORD#A }"; fi ;;
    esac
  done <<EOF
$(printf '%s\n' "$FIELDS" | sed -n '4,$p')
EOF
fi
# --- Never list (ask) --------------------------------------------------------
ask() { decide ask "deny-hook[NEVER-LIST]: $1 Per runtime/sandbox-policy.md this needs a recorded human grant before it runs."; exit 0; }

never_list() {
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
  # Every rule above is `has && ask` — when nothing matches the function's
  # status is the last has's failure, and set -e reads a failing CALL as a
  # failing command. Returning 0 keeps "nothing to ask" from exiting nonzero.
  :
}

# The list judges the line twice. As WRITTEN first, because rules like curl|sh
# match on the `|` that sits BETWEEN segments — a normalized join replaces the
# separators with `;` and would unsee the shape the rule exists to catch. Then
# over the same normalized segments the HIGH tier judged — prefixes and git
# global options stripped — so `git -C /x reset --hard` asks what `git reset
# --hard` asks (#297). A line the split somehow emptied falls back to raw.
CMD=$FULL_CMD
never_list
CMD=
for _SEG in "$@"; do
  _n=$(strip_git_opts "$(strip_prefix "$(norm_ws "$_SEG")")")
  CMD=${CMD:+$CMD ; }$_n
done
[ -z "$CMD" ] || never_list

exit 0
