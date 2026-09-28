# Release 1.0 checklist

Run it: `python3 scripts/release_check.py` (add `--fast` to skip the suite).

The bar for orca-fleet 1.0, resolved to commands a second person can run. This
file DEFINES the release; [`scripts/release_check.py`](../scripts/release_check.py)
RUNS it (#414). Every gate below is a command with its expected output — prose
approvals do not count — and the script runs those same commands from the repo
root, printing one `PASS` / `FAIL` / `SKIP(<reason>)` line per check and a
summary: exit 0 when every check passes, 1 on any FAIL, 2 when it could not run.
A check that needs something the machine lacks (`gh` absent or unauthenticated,
no network) prints `SKIP(<reason>)` and never `PASS`; the summary counts it, so a
run carrying a SKIP is visibly not a full run. `--skip-github` skips the
`gh`-backed checks on purpose, `--json` is the machine form, `--repo PATH` gates
another checkout. Run top to bottom; a gate that fails stops the release, it does
not get waived in chat. A command changed here changes in the script in the same
PR: `tests/test_release_check.py` runs the script against this repository and
holds the doc's commands to the script's checks.

Sources: roadmap epic [#407](https://github.com/ravidsrk/orca-fleet/issues/407)
Definition of Done (gates 1–6), [ops.md](ops.md) release mechanics.

## Gate 0 — tree and catalog gates green

```bash
git status --porcelain                       # empty
git rev-parse HEAD                            # record the SHA; every gate below runs at it
python3 scripts/validate.py                   # all missions valid
python3 -m unittest discover -s tests         # full suite green (~8 min; `--fast` reports it as SKIP(--fast))
python3 runtime/scripts/proof_status.py --check   # every proof_evidence resolves
python3 runtime/scripts/run_report.py         # every claimed tier binds to artifacts
RELEASE_SHA=$(git rev-parse HEAD) gh run list --workflow validate --branch main --limit 1 --json conclusion,headSha \
  -q '.[0] | select(.conclusion=="success" and .headSha==env.RELEASE_SHA) | "bound GREEN at \(.headSha)"'
# bound GREEN at <the recorded SHA> — empty output fails the gate: a stale green from another SHA does not count
```

## Gate 1 — Phase 0 at zero (epic DoD 1)

G1–G4 are typed records in the run's
[gate-batch store](runs/2026-09-14-clean-sweep-tracker/gate-batch.json) (#419);
the [`.md`](runs/2026-09-14-clean-sweep-tracker/gate-batch.md) beside it is the
rendered view, so the gate reads the store through its own CLI, never a grep
over prose. The gate is that nothing is owed:

```bash
python3 runtime/scripts/gate-batch.py --run 2026-09-14-clean-sweep-tracker list --status owed
# no output: nothing owed. `list` without --status shows the record — G1 answered, G2 answered, G3 waived, G4 overtaken
gh issue view 408 --json state -q .state    # CLOSED (runway settled)
gh issue view 386 --json state -q .state    # CLOSED (signing decision recorded and implemented)
gh pr view 406 --json state -q .state       # MERGED (docs re-check)
gh issue view 235 --json state -q .state    # informational: needs-human, does not gate
```

#235 (marketplace submissions) does not gate 1.0: its own body says it does not
gate launch, so the script records its state as an `INFO` line and the issue
stays tracked as the needs-human item it is.

## Gate 2 — flagships proven (epic DoD 2)

The bar is a BOUND tier — `self-run` or `external-run` — for each flagship.
harden-it's bar is `self-run`: #407 re-scoped its promotion (#409) from
external-run to self-run, bound by
[2026-09-21-harden-it-self-run.md](runs/2026-09-21-harden-it-self-run.md), and
`external-run` stays the Tier C aspiration — a bound user run filed through the
intake (#415) — not a 1.0 gate.

```bash
python3 - <<'PY'
import re
BAR = ("self-run", "external-run")
for name in ("harden-it", "prove-it", "clean-sweep"):
    fm = open(f"skills/{name}/SKILL.md").read().split("---")[1]
    have = re.search(r"^\s+proof:\s*(\S+)", fm, re.M).group(1)
    assert have in BAR, (name, have)
    print(name, have, "OK")
PY
python3 runtime/scripts/run_report.py         # every claimed tier binds to artifacts
```

## Gate 3 — verifier moat held by CI (epic DoD 3)

```bash
python3 bench/vf-bench/gate.py               # exit 0: corpus pinned, no trap skipped, verify.py false-done 0/20, controls green
sh demo/negative-control/run.sh | tail -2    # PASS: self-scorer GREEN ... RED (exit 0 overall)
grep -rlE 'vfbench\.py|vf-bench/gate\.py' .github/workflows/   # non-empty: #412 landed
grep -rl 'negative-control' .github/workflows/                 # non-empty: #413 landed
```

## Gate 4 — install is one command (epic DoD 4)

```bash
grep -c 'sh scripts/install.sh' README.md docs/distribution.md
# README.md: >=1, docs/distribution.md: >=1 (same command in both)
test -f docs/release-1.0-checklist.md && echo "this file exists"
RELEASE_SHA=$(git rev-parse HEAD) gh run list --workflow install --branch main --limit 1 --json conclusion,headSha \
  -q '.[0] | select(.conclusion=="success" and .headSha==env.RELEASE_SHA) | "bound GREEN at \(.headSha)"'
# bound GREEN at <the recorded SHA> — empty output fails the gate: a stale green from another SHA does not count
```

## Gate 5 — runtime re-pinned, chaining exercised (epic DoD 5)

The pin must be a *fresh live* witness, not the 2026-09-13 one #416 replaced,
and the chaining exercise's report must be published where a reader is sent to
it: the protocol under test names it (the run-archive index may too).

```bash
python3 -c 'import json; e=json.load(open("runtime/pins.json"))["orca"]; assert e["witness"]=="live" and e["witnessed"]>="2026-09-16", e; print("orca", e["version"], e["witnessed"], "live OK")'
ls -d docs/reports/chaining-*                # the published chaining report (non-empty)
grep -l 'docs/reports/chaining-' runtime/mission-chaining.md docs/runs/README.md   # non-empty: a navigable doc names it
gh issue view 416 --json state -q .state    # CLOSED (re-pin run)
gh issue view 417 --json state -q .state    # CLOSED (chaining exercise)
```

## Gate 6 — mechanization merged and used (epic DoD 6)

"Merged" is the tool in the tree with its contract test beside it. "Used" has a
checkable form: a `gate-batch.json` store under a run directory (the CLI is its
only writer) and a run artifact that names `watchdog.py`.

```bash
test -f runtime/scripts/watchdog.py   && test -f tests/test_watchdog.py   && echo "watchdog merged"
test -f runtime/scripts/gate-batch.py && test -f tests/test_gate_batch.py && echo "gate-batch merged"
ls docs/runs/*/gate-batch.json               # non-empty: a run consumed gate-batch.py (2026-09-14-clean-sweep-tracker)
grep -rl 'watchdog\.py' docs/runs/           # non-empty: a run's artifacts name the watchdog
gh issue view 418 --json state -q .state    # CLOSED (liveness watchdog)
gh issue view 419 --json state -q .state    # CLOSED (gate-batch tooling)
```

## Release mechanics — 1.0.0

All six gates green — `python3 scripts/release_check.py` exits 0 with no SKIP in
its summary? Cut exactly like any release ([ops.md](ops.md#release-cut)): the
prepare/cut/tag/record blocks with `RELEASE_VERSION=1.0.0`. The maintainer
authorizes the cut SHA before tagging; green checks never authorize publication.

```bash
export RELEASE_VERSION=1.0.0 RELEASE_DATE=<today YYYY-MM-DD>
# run the four <!-- release:... --> blocks in docs/ops.md in order, then:
python3 -c 'import json; d=json.load(open("docs/releases.json")); assert d["preparing"] is None and d["releases"][-1]["version"]=="1.0.0", d; print("row recorded OK")'
git cat-file -t refs/tags/v1.0.0              # tag (annotated, not lightweight)
git rev-parse 'v1.0.0^{commit}'               # equals the releases.json 1.0.0 commit
git push origin v1.0.0                        # publish the single approved tag
```

Marketplace updates ride #235 (needs-human, not a gate — see gate 1): when the
maintainer files them, confirm the live listings lead with the `proof:` framing
+ run-archive link, not the stale catalog-count blurb, and that `docs/about.md`
is the applied About text.

## Rollback — a bad 1.0

Tags and published rows are immutable ([ops.md](ops.md#release-cut) recovery):
a bad 1.0 is corrected forward, never rewritten.

```bash
git rev-parse 'v1.0.0^{commit}'               # record; this SHA must never change
git revert -m 1 <merge-sha-of-the-bad-change> # land the revert on main via a normal PR
export RELEASE_VERSION=1.0.1 RELEASE_DATE=<today YYYY-MM-DD>
python3 scripts/release_check.py              # all six gates again, at the revert tip; then the four ops.md blocks
git tag --list 'v1.0.*'                       # v1.0.0 still present, v1.0.1 beside it
```

Plugin consumers pick up the fix by reinstalling (`/plugin install orca-fleet`
re-copies the repo at the new tip); symlink consumers `git pull` and re-run
`sh scripts/install.sh --check`. If the bad 1.0 was a *release-process* failure
(wrong cut, lightweight tag) rather than a code failure, stop after recording:
do not amend the cut, recreate the tag, or reset the published mapping —
investigate with the maintainer per ops.md recovery.
