#!/usr/bin/env bash
# nc-run.sh <cell-id> <section> <source-file> <old> <new>
# Rename-control: on a throwaway branch, rename ONE anchored fact in SOURCE,
# run the claim check for that cell (must go RED), then delete the branch.
# Transcript -> evidence/nc-<cell-id>.txt. Worktree left clean on BASE.
set -u
CELL="$1"; SECTION="$2"; SRC="$3"; OLD="$4"; NEW="$5"
RUN="docs/runs/campaign-2026-09-16-document-it"
OUT="$RUN/evidence/nc-$CELL.txt"
BR="nc-throwaway-$CELL"
BASE="$(git rev-parse --abbrev-ref HEAD)"
{
echo "NC $CELL: rename '$OLD' -> '$NEW' in $SRC; expect claimcheck --cell $SECTION RED"
git checkout -q -b "$BR"
python3 - "$SRC" "$OLD" "$NEW" <<'PY'
import sys
p, old, new = sys.argv[1], sys.argv[2], sys.argv[3]
t = open(p).read()
assert t.count(old) >= 1, f"anchor {old!r} not found"
open(p, "w").write(t.replace(old, new))
print(f"renamed {t.count(old)} occurrence(s)")
PY
echo "--- claimcheck (expect FAIL) ---"
python3 "$RUN/extractor/claimcheck.py" --cell "$SECTION"; echo "claimcheck exit=$?"
echo "--- restore ---"
git checkout -q -- "$SRC"
git checkout -q "$BASE"
git branch -q -D "$BR"
echo "renamed file restored: $(git diff --quiet -- "$SRC" && echo yes || echo NO)"
} 2>&1 | tee "$OUT"
