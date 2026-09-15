# T7 — U393: mixed-version rollout lock (#393)

## Problem
#382 moved the wrapper lock from a sibling sidecar to an flock on the manifest
inode; #388 nailed the no-new-sidecar invariant. But during a rollout window an
old (sidecar-discipline) writer and a new (inode-lock) writer do not share one
lock, and concurrent appends can lose records again. Greptile on #387.

## Decision (coordinator-picked, disclosed)
Implement the code fix: the new wrapper opportunistically locks a PRE-EXISTING
sidecar. Declined: bare rollout note (no rollout doc owns it; the code fix
closes the window properly).

## Scope note (read carefully)
A lock-free peer can never be made safe — no lock you take forces others to
lock. This unit covers sidecar-discipline peers only (any writer that flocks
`<manifest>.lock`): new code joins the sidecar lock when the sidecar exists.

## Criteria
- C-1: `append_record` takes LOCK_EX on a pre-existing sibling
  `<manifest>.lock` (open WITHOUT O_CREAT; absent sidecar = skip, no error),
  then the manifest inode lock as today. Lock order everywhere: sidecar first,
  inode second (document it; one order, no ABBA).
- C-2: #388 invariant preserved: no wrapped run CREATES a sidecar. A test
  asserts that after wrapped runs with no pre-existing sidecar, no
  `<manifest>.lock` exists on disk.
- C-3: mixed-version concurrency test: N appends via the new code run
  concurrently with M appends via a sidecar-only-discipline writer (simulating
  the old wrapper: flock sidecar → read → modify → write → release) with a
  pre-existing sidecar, and all N+M records land. Test must be stable
  (barrier-start workers, generous attempts, no bare sleeps).
- C-4: `python3 -m unittest` and `python3 scripts/validate.py` green.

## Negative control
`git show HEAD:runtime/scripts/evidence-run.py > runtime/scripts/evidence-run.py`
(revert ONLY the wrapper, keep the new tests): the C-3 test fails with lost
records. Restore the fix: green. Both directions observed and quoted.

## Red-first
C-3 test lands and FAILS before the C-1 change (paste the failing output in the
manifest notes); then implement C-1/C-2.

## Hot files
- `runtime/scripts/evidence-run.py` (`append_record`)
- `tests/test_evidence_run.py`

## Out of scope
- Lock-free peers (impossible, see scope note).
- Rollout sequencing docs; operator runbooks.
- Anything outside the owned files (below).

## Worker protocol (run conventions)
- Ownership: you may edit ONLY `runtime/scripts/evidence-run.py`,
  `tests/test_evidence_run.py`, `assets/badges/tests.json` (badge regen only),
  `docs/runs/2026-09-14-clean-sweep-tracker/u393-manifest.json` and
  `docs/runs/2026-09-14-clean-sweep-tracker/u393-negctrl.txt`. Nothing else.
- Commits on your unit branch, one concern each: red test(s) first, then the
  fix, then badge regen (`python3 scripts/gen-badges.py` — check the script
  name/flags in-repo; its own commit), then manifest+negctrl.
- Manifest: follow the schema of `u388-manifest.json` in the same directory
  (schema/unit/unit_class/base_sha/head_sha/head_tree/contract/criteria/intent/
  lighting/commands/negative_control/binding_audit/artifacts/files/commits/
  decisions). `contract.source` = this spec file@dispatch-commit (given in your
  TASK preamble), `contract.digest` = its sha256 (given). `head_sha` = your
  code tip (coordinator re-binds at close — do not chase it). commands[] records
  must be written by the WRAPPED runs (evidence-run.py) on a clean tree; keep
  the tree clean while recording (record into manifests outside the tree, then
  concatenate byte-for-byte).
- `u393-negctrl.txt`: full terminal transcript of the negative control (both
  directions), pinned by sha256 in `artifacts[]`.
- Gates before worker_done: `python3 -m unittest discover -s tests` (full
  suite, ~4 min) green, `python3 scripts/validate.py` green.
- Do NOT push. Do NOT merge. Do NOT touch BASE. Commit locally only.
- worker_done: three-sentence summary + explicit --outcome, the code-tip SHA,
  gate outputs quoted, RED-first evidence quoted, files modified, report path
  = the manifest.
