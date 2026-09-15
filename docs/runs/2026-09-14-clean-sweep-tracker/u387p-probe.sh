#!/bin/sh
# U387P negative-control proof (build-387-process.md C-1..C-4): one probe per criterion.
# Run from the repo root. Reads the WORKING TREE, so a revert control that restores
# negative_control.paths from base_sha turns it RED. Exit 0 only when all four hold.
R=docs/runs/2026-09-14-clean-sweep-tracker
failed=0
fail() { echo "FAIL: $1"; failed=$((failed + 1)); }
ok() { echo "ok: $1"; }

# C-1: every T-row park cell (column 12) is empty or '<class>: ...' with <class> parsed from
# the '## Park classes' table of runtime/ledger-contract.md; T1/T2/T3 carry the run ref, T3
# points at gate-batch.md G3 (which must exist) and cites T6 GO 5205447863; T1-T4 columns
# 1-11 equal their cells at base_sha 9a115f7. A missing ledger, contract or gate file fails.
if python3 - "$R.md" runtime/ledger-contract.md "$R/gate-batch.md" <<'EOF'
import re, subprocess, sys
ledger, contract, gates = sys.argv[1:4]
BASE = "9a115f7579232f50b913ce84515e3964f8b68b33"  # u387p-manifest.json base_sha
RUN = "run_0607bdc681e6"
errs = []

def read(path):
    try:
        return open(path, encoding="utf-8").read()
    except OSError:
        errs.append(f"[{path} missing]")
        return None

def t_rows(text):
    rows = {}
    for line in text.splitlines():
        if re.match(r"^\| T[0-9]+ \|", line):
            cells = [c.strip() for c in line.split("|")[1:-1]]
            rows[cells[0]] = cells
    return rows

led, con, gat = read(ledger), read(contract), read(gates)
classes = set()
if con is not None:
    sec = con.split("## Park classes", 1)[-1].split("\n## ", 1)[0] if "## Park classes" in con else ""
    for line in sec.splitlines():
        if line.startswith("|"):
            classes.update(re.findall(r"`([^`]+)`", line.split("|")[1]))
    if not classes:
        errs.append("[no park classes parsed from ledger-contract.md]")
if led is not None and classes:
    rows = t_rows(led)
    for tid, cells in rows.items():
        if len(cells) != 13:
            errs.append(f"[{tid} has {len(cells)} cells, header has 13]")
            continue
        park = cells[11]
        cls = park.split(":", 1)[0] if ":" in park else None
        if park not in ("", "—") and cls not in classes:
            errs.append(f"[{tid} park class {cls or park!r} not in ledger-contract]")
    for tid in ("T1", "T2", "T3", "T4"):
        if tid not in rows or len(rows[tid]) != 13:
            errs.append(f"[{tid} row missing]")
    for tid in ("T1", "T2", "T3"):
        if tid in rows and len(rows[tid]) == 13 and RUN not in rows[tid][11]:
            errs.append(f"[{tid} park lacks run ref {RUN}]")
    t3 = rows.get("T3", [])
    if len(t3) == 13:
        if "gate-batch.md G3" not in t3[11]:
            errs.append("[T3 park does not point at gate-batch.md G3]")
        if "T6 GO 5205447863" not in t3[12]:
            errs.append("[T3 evidence lacks T6 GO 5205447863]")
    if gat is not None and not re.search(r"(?m)^## G3 ", gat):
        errs.append("[gate-batch.md has no '## G3' entry]")
    base = subprocess.run(["git", "show", f"{BASE}:{ledger}"], capture_output=True, text=True)
    if base.returncode != 0:
        errs.append(f"[cannot read {ledger} at base {BASE[:7]}]")
    else:
        brows = t_rows(base.stdout)
        for tid in ("T1", "T2", "T3", "T4"):
            if tid in rows and rows[tid][:11] != brows.get(tid, [])[:11]:
                errs.append(f"[{tid} columns 1-11 differ from base {BASE[:7]}]")
print(" ".join(errs))
sys.exit(1 if errs else 0)
EOF
then ok "C-1 T-row parks in ledger-contract classes; T1-T3 run ref; T3 G3 ref + T6 GO; T1-T4 flags = base"
else fail "C-1 ledger park/ref/flag check (errors above)"; fi

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

# C-3: review template has a correct TARGET checkout line whose reattach note names the
# conductor-close.md rule, and an explicit worker_done contract: the five flags are grepped
# inside the WORKER_DONE CONTRACT block only (header line to the next blank line).
T=$R/taskspecs/review-template.md
c3=""
if [ ! -f "$T" ]; then c3=" [$T missing]"
else
  grep -Eq 'fetch origin \+|as usual' "$T" && c3="$c3 [malformed separator or 'as usual' present]"
  grep -q 'git fetch origin && git checkout' "$T" || c3="$c3 [no TARGET fetch && checkout line]"
  tgt=$(awk '/^TARGET/{f=1} f&&/^$/{exit} f' "$T" | tr '\n' ' ')
  case "$tgt" in *conductor-close.md*reattach*) ;; *) c3="$c3 [TARGET reattach note does not name conductor-close.md reattach]";; esac
  blk=$(awk '/^WORKER_DONE CONTRACT/{f=1} f&&/^$/{exit} f' "$T")
  [ -n "$blk" ] || c3="$c3 [no WORKER_DONE CONTRACT block]"
  for flag in '--outcome succeeded|failed' '--report-path' '--files-modified' \
              '--from' '--dispatch-capability'; do
    printf '%s\n' "$blk" | grep -qF -- "$flag" || c3="$c3 [worker_done contract lacks $flag]"
  done
fi
if [ -z "$c3" ]; then ok "C-3 review template TARGET line + reattach ref + explicit worker_done contract"
else fail "C-3$c3"; fi

# C-4: conductor-close.md documents each CLOSE step and each rule BODY. Anchors are a step
# number or rule name plus its key sentences, matched on the whitespace-collapsed file (so a
# re-wrap stays green); deleting or gutting any step or rule turns it RED.
C=$R/taskspecs/conductor-close.md
if [ ! -f "$C" ]; then fail "C-4 $C does not exist"
else
  norm=$(tr '\n' ' ' < "$C" | tr -s ' ')
  c4=""
  for a in \
    '1) Resolve the tip: T := git rev-parse M^2' \
    "Assert T == the verdict's reviewed_sha" \
    'ledger-contract MERGED = merge-commit (not squash)' \
    'A squash, rebase or fast-forward merge has no M^2' \
    'STOP and raise a human gate' \
    'never derive T another way' \
    '2) Re-run in a clean worktree at the merge tip' \
    'git status --porcelain empty' \
    '3) Append coordinator records' \
    'Builder records at older trees STAY as true history' \
    '4) Re-bind head/head_tree' \
    'RECOMPUTED from git, never copied from a note' \
    '5) pr fill' \
    'pr.reviewed_sha := T' \
    '6) verify.py' \
    'A RED leg is RECORDED, never hidden' \
    '7) Commit: ONE chore(run) commit on BASE' \
    '- option-A (self-reference). A commit cannot name its own SHA' \
    'at BUILD the worker sets head_sha = its last CONTENT commit' \
    'At CLOSE the conductor re-binds head_sha to the reviewed tip' \
    '- union-invalidates. A merge of BASE into the unit branch (a union) changes the tree under every earlier binding' \
    'they are STALE until re-run at the post-union tip' \
    'never count as fresh' \
    '- out-of-process-merge. A merge made outside this pipeline' \
    'is disclosed, not normalised' \
    "re-verify from step 1 at that merge's tip" \
    '- reattach. Review workers check out the reviewed SHA' \
    'they leave it detached, commit nothing, and say so in worker_done' \
    'reattaches BEFORE the first commit' \
    'git rev-parse HEAD == the expected tip' \
    'never commit on a detached HEAD'; do
    printf '%s' "$norm" | grep -qF -- "$a" || c4="$c4 [$a]"
  done
  if [ -z "$c4" ]; then ok "C-4 conductor-close.md CLOSE steps 1-7 + option-A, union, out-of-process, reattach bodies"
  else fail "C-4 conductor-close.md missing:$c4"; fi
fi

echo "u387p probes: $failed failed of 4"
[ "$failed" -eq 0 ]
