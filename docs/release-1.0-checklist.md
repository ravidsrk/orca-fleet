# Release 1.0 checklist

The bar for orca-fleet 1.0, resolved to commands a second person can run. This
file DEFINES the release; it does not perform it (#414). Every gate below is a
command with its expected output — prose approvals do not count. Run top to
bottom; a gate that fails stops the release, it does not get waived in chat.

Sources: roadmap epic [#407](https://github.com/ravidsrk/orca-fleet/issues/407)
Definition of Done (gates 1–6), [ops.md](ops.md) release mechanics.

## Gate 0 — tree and catalog gates green

```bash
git status --porcelain                       # empty
git rev-parse HEAD                            # record the SHA; every gate below runs at it
python3 scripts/validate.py                   # all missions valid
python3 -m unittest discover -s tests         # full suite green
gh run list --workflow validate --branch main --limit 1 --json conclusion -q '.[0].conclusion'
# SUCCESS
```

## Gate 1 — Phase 0 at zero (epic DoD 1)

G1–G4 are answered in the
[gate-batch](runs/2026-09-14-clean-sweep-tracker/gate-batch.md) file, one
`Status: ANSWERED <date> <decider>: <decision>` line per item:

```bash
grep -c '^Status: ANSWERED' docs/runs/2026-09-14-clean-sweep-tracker/gate-batch.md
# 4
gh issue view 408 --json state -q .state    # CLOSED (runway settled)
gh issue view 386 --json state -q .state    # CLOSED (signing decision recorded; implementation is its own issue)
gh issue view 235 --json state -q .state    # CLOSED (marketplace submissions filed by the maintainer)
gh pr view 406 --json state -q .state       # MERGED (docs re-check)
```

## Gate 2 — flagships proven (epic DoD 2)

```bash
python3 - <<'PY'
import re
for name, want in (("harden-it", "external-run"),
                   ("prove-it", "self-run"),
                   ("clean-sweep", "self-run")):
    fm = open(f"skills/{name}/SKILL.md").read().split("---")[1]
    have = re.search(r"^\s+proof:\s*(\S+)", fm, re.M).group(1)
    assert have == want, (name, have)
    print(name, have, "OK")
PY
python3 runtime/scripts/run_report.py         # every claimed tier binds to artifacts
python3 runtime/scripts/proof_status.py --check
```

## Gate 3 — verifier moat held by CI (epic DoD 3)

```bash
python3 bench/vf-bench/vfbench.py --json | python3 -c \
  'import json,sys; g=json.load(sys.stdin)["gates"]["orca-fleet verify.py (sound)"]; assert (g["false_done"], g["red_total"]) == (0, 20), g; print("verify.py false-done 0/20 OK")'
sh demo/negative-control/run.sh | tail -1    # PASS: self-scorer GREEN ... RED (exit 0 overall)
grep -rl 'vfbench\.py' .github/workflows/    # non-empty: #412 landed
grep -rl 'negative-control' .github/workflows/  # non-empty: #413 landed
```

## Gate 4 — install is one command (epic DoD 4)

```bash
grep -c 'sh scripts/install.sh' README.md docs/distribution.md
# README.md: >=1, docs/distribution.md: >=1 (same command in both)
gh run list --workflow install --branch main --limit 1 --json conclusion -q '.[0].conclusion'
# SUCCESS
test -f docs/release-1.0-checklist.md && echo "this file exists"
```

## Gate 5 — runtime re-pinned, chaining exercised (epic DoD 5)

The pin must be a *fresh live* witness, not the 2026-09-13 one #416 replaces:

```bash
gh issue view 416 --json state -q .state    # CLOSED (re-pin run)
python3 -c 'import json; e=json.load(open("runtime/pins.json"))["orca"]; assert e["witness"]=="live" and e["witnessed"]>="2026-09-16", e; print("orca", e["version"], e["witnessed"], "live OK")'
gh issue view 417 --json state -q .state    # CLOSED (chaining exercise)
ls docs/runs/ | grep -i chain                # the published chaining report (non-empty)
grep -ci 'chain' docs/runs/README.md         # >=1: the run-archive index links it
```

## Gate 6 — mechanization merged and used (epic DoD 6)

```bash
gh issue view 418 --json state -q .state    # CLOSED (liveness watchdog)
gh issue view 419 --json state -q .state    # CLOSED (gate-batch tooling)
git log --oneline --grep='#418' --format='%H %s'  # the landing merge (non-empty)
git log --oneline --grep='#419' --format='%H %s'  # the landing merge (non-empty)
```

"Used" binds to the first run that consumes each tool. When those runs land,
their reports name the tool; bind RUN to that report directory and run:

```bash
test -d "docs/runs/$RUN" && grep -rq 'watchdog' "docs/runs/$RUN" && grep -rq 'gate-batch' "docs/runs/$RUN" \
  && echo "run $RUN consumes both tools"
```

## Release mechanics — 1.0.0

All six gates green? Cut exactly like any release ([ops.md](ops.md#release-cut)):
the prepare/cut/tag/record blocks with `RELEASE_VERSION=1.0.0`. The maintainer
authorizes the cut SHA before tagging; green checks never authorize publication.

```bash
export RELEASE_VERSION=1.0.0 RELEASE_DATE=<today YYYY-MM-DD>
# run the four <!-- release:... --> blocks in docs/ops.md in order, then:
python3 -c 'import json; d=json.load(open("docs/releases.json")); assert d["preparing"] is None and d["releases"][-1]["version"]=="1.0.0", d; print("row recorded OK")'
git cat-file -t refs/tags/v1.0.0              # tag (annotated, not lightweight)
git rev-parse 'v1.0.0^{commit}'               # equals the releases.json 1.0.0 commit
git push origin v1.0.0                        # publish the single approved tag
```

Marketplace updates ride #235 (already CLOSED per gate 1): confirm the live
listings lead with the `proof:` framing + run-archive link, not the stale
catalog-count blurb, and that `docs/about.md` is the applied About text.

## Rollback — a bad 1.0

Tags and published rows are immutable ([ops.md](ops.md#release-cut) recovery):
a bad 1.0 is corrected forward, never rewritten.

```bash
git rev-parse 'v1.0.0^{commit}'               # record; this SHA must never change
git revert -m 1 <merge-sha-of-the-bad-change> # land the revert on main via a normal PR
export RELEASE_VERSION=1.0.1 RELEASE_DATE=<today YYYY-MM-DD>
# re-run all six gates above at the revert tip, then the four ops.md blocks
git tag --list 'v1.0.*'                       # v1.0.0 still present, v1.0.1 beside it
```

Plugin consumers pick up the fix by reinstalling (`/plugin install orca-fleet`
re-copies the repo at the new tip); symlink consumers `git pull` and re-run
`sh scripts/install.sh --check`. If the bad 1.0 was a *release-process* failure
(wrong cut, lightweight tag) rather than a code failure, stop after recording:
do not amend the cut, recreate the tag, or reset the published mapping —
investigate with the maintainer per ops.md recovery.
