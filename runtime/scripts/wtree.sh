#!/usr/bin/env sh
# wtree.sh — print a working-tree CONTENT fingerprint (a git tree hash).
#
# Ported from gstack `bin/gstack-wtree` (MIT, garrytan/gstack v1.84.1) — the mechanism is theirs,
# the POSIX-sh spelling and the fail-closed exit are ours. See
# docs/research/2026-09-10-upstream-audit/gstack.md §4.2.
#
# Builds a TEMP index, stages the full working tree into it (`git add -A`, so .gitignore'd scratch
# stays out and UNTRACKED source is included), and prints `git write-tree` of that index. Why this
# and not `git rev-parse HEAD^{tree}`:
#
#   - committing identical content does NOT change the fingerprint, so a record made on a dirty
#     tree stays valid once that exact content is committed;
#   - an untracked new source file DOES change it, so "tests passed" cannot stay fresh after a new
#     file appears;
#   - rebase / amend / squash that preserve content do not change it.
#
# The REAL repo index is never touched. Seeding the temp index by COPYING the real one preserves the
# stat cache, so `git add -A` only re-hashes files whose stat changed. gstack's #2687 hardening is
# kept verbatim in spirit: `cp` stamps the copy "now", which defeats git's racy-index protection and
# can hide a same-second rewrite, so `touch -r` restores the original mtime — and if that touch
# FAILS we fall through to the slower `read-tree HEAD` seed rather than trusting a stale stat cache.
#
# Staged blobs land in the object store as unreachable objects and are gc'd like stash churn (so the
# CONTENT of untracked, non-ignored files enters .git/objects until gc — the same property
# `git stash -u` has).
#
# Usage: wtree.sh [repo-dir]        # default: the current directory
# Exit 1 outside a git repo, or in a repo with no commits and no usable index — callers MUST treat
# a non-zero exit as "no fingerprint" and fail closed, never as an empty one.
set -eu

TARGET="${1:-.}"
TOP=$(git -C "$TARGET" rev-parse --show-toplevel 2>/dev/null) || exit 1

# Resolve the REAL index path BEFORE exporting GIT_INDEX_FILE: with the variable set,
# `rev-parse --git-path index` returns the temp index itself and the stat-cache seed self-copies.
REAL_INDEX=$(git -C "$TOP" rev-parse --git-path index 2>/dev/null || true)
case "$REAL_INDEX" in
  ""|/*) ;;
  *) REAL_INDEX="$TOP/$REAL_INDEX" ;;
esac

TMPIDX=$(mktemp "${TMPDIR:-/tmp}/orca-wtree-XXXXXX") || exit 1
trap 'rm -f "$TMPIDX"' EXIT INT TERM
GIT_INDEX_FILE="$TMPIDX"
export GIT_INDEX_FILE

seed_from_head() {
  rm -f "$TMPIDX" 2>/dev/null || true
  git -C "$TOP" read-tree HEAD 2>/dev/null || return 1
}

if [ -n "$REAL_INDEX" ] && [ -f "$REAL_INDEX" ] && cp "$REAL_INDEX" "$TMPIDX" 2>/dev/null; then
  if ! touch -r "$REAL_INDEX" "$TMPIDX" 2>/dev/null; then
    seed_from_head || exit 1
  fi
else
  seed_from_head || exit 1
fi

git -C "$TOP" add -A 2>/dev/null || exit 1
git -C "$TOP" write-tree 2>/dev/null || exit 1
