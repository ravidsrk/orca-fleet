#!/bin/sh
# U387P negative-control proof (build-387-process.md C-1..C-4): one probe per criterion.
# Run from the repo root. Reads the WORKING TREE, so a revert control that restores
# negative_control.paths from base_sha turns it RED. Exit 0 only when all four hold.
R=docs/runs/2026-09-14-clean-sweep-tracker
failed=0
fail() { echo "FAIL: $1"; failed=$((failed + 1)); }
ok() { echo "ok: $1"; }

# C-1: no unit row parks as proof-park (runtime/ledger-contract.md allows no such class).
# Scoped to the park cell (column 12) of T-rows: the word also appears in T8's own title
# and in the frozen loop log, neither of which is a park.
n=$(grep -E '^\| T[0-9]+ \|' "$R.md" | cut -d'|' -f13 | grep -c 'proof-park')
if [ "$n" -eq 0 ]; then ok "C-1 no T-row park cell is proof-park"
else fail "C-1 $n T-row park cell(s) still read proof-park"; fi

# C-2: u385-manifest.json head_tree is the tree of its own head_sha.
if python3 - "$R/u385-manifest.json" <<'EOF'
import json, subprocess, sys
m = json.load(open(sys.argv[1], encoding="utf-8"))
tree = subprocess.run(["git", "rev-parse", m["head_sha"] + "^{tree}"],
                      capture_output=True, text=True, check=True).stdout.strip()
ok = m["head_tree"] == tree == m["pr"]["reviewed_wtree"]
print(f"head_sha={m['head_sha'][:7]} head_tree={m['head_tree'][:7]} "
      f"rev-parse={tree[:7]} reviewed_wtree={m['pr']['reviewed_wtree'][:7]}")
sys.exit(0 if ok else 1)
EOF
then ok "C-2 u385 head_tree == git rev-parse head_sha^{tree}"
else fail "C-2 u385 head_tree does not match git rev-parse head_sha^{tree}"; fi

# C-3: review template has a correct TARGET checkout line and an explicit worker_done contract.
T=$R/taskspecs/review-template.md
c3=""
grep -Eq 'fetch origin \+|as usual' "$T" && c3="$c3 [malformed separator or 'as usual' present]"
grep -q 'git fetch origin && git checkout' "$T" || c3="$c3 [no TARGET fetch && checkout line]"
for flag in '--outcome succeeded|failed' '--report-path' '--files-modified' \
            '--from' '--dispatch-capability'; do
  grep -qF -- "$flag" "$T" || c3="$c3 [worker_done contract lacks $flag]"
done
if [ -z "$c3" ]; then ok "C-3 review template TARGET line + explicit worker_done contract"
else fail "C-3$c3"; fi

# C-4: conductor-close.md documents CLOSE and the three rules.
C=$R/taskspecs/conductor-close.md
if [ ! -f "$C" ]; then fail "C-4 $C does not exist"
else
  c4=""
  for term in 'option-A' 'union-invalidates' 'out-of-process-merge' 'clean worktree' \
              'head_tree' 'verify.py' 'chore(run)'; do
    grep -qF -- "$term" "$C" || c4="$c4 [$term]"
  done
  if [ -z "$c4" ]; then ok "C-4 conductor-close.md documents CLOSE + option-A + union + out-of-process"
  else fail "C-4 conductor-close.md missing:$c4"; fi
fi

echo "u387p probes: $failed failed of 4"
[ "$failed" -eq 0 ]
