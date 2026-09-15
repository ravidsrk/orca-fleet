# T11 — U393R: sidecar-creation race (#387 thread 4012510839)

## Problem
T7 (U393, merged 6d9e46a) joins a PRE-EXISTING `<manifest>.lock` before the
inode lock. But the absence check is check-then-act: when no sidecar exists,
the new wrapper proceeds on the manifest lock alone, and a legacy
(sidecar-discipline) wrapper can create + lock `<manifest>.lock` AFTER the
check. The legacy writer never takes the manifest lock, so the two read-modify-write
cycles overlap on different locks and one record is silently lost. T7's C-3
test pre-creates the sidecar, so it never covers this shape. The coordinator
reproduced the loss deterministically (forced interleaving, real locking/IO
path: legacy record silently dropped); unforced concurrency trials show 0/60
(the natural window is thin — the test must force the schedule).

## Decision (coordinator-picked, disclosed)
Implement the code fix: shrink the check-then-act window. Declined (for now):
bare accept-with-reason — "rollout is transient" is unevidenced (stale
checkouts run legacy wrappers indefinitely), and silent evidence loss is what
this file exists to prevent. If no safe fix exists under the constraints, say
so with the deadlock argument and the verdict adjudicates fix-vs-accept.

## Scope note (read carefully)
T7's lock-free-peer impossibility still holds. This unit covers
sidecar-discipline peers only. The fix must preserve ALL of: (a) #388 —
the new wrapper never CREATES the sidecar (T7's C-2 test stays green);
(b) the one lock order — sidecar first, inode second, NEVER hold the manifest
lock while acquiring the sidecar lock (a legacy holder waits on nothing the
new code holds, so release-then-rejoin cannot ABBA — argue it in a comment);
(c) `append_record` never raises; (d) the steady-state mixed-version test
stays green.

## Criteria
- C-1: a DETERMINISTIC regression test that forces the interleaving
  (new checks absent -> legacy creates+locks+reads -> new reads stale ->
  legacy writes -> new writes) and FAILS on the current code with exactly
  the lost legacy record, GREEN after the fix. Schedule-forcing via
  barriers/events (no bare sleeps on the correctness path); all locking/IO
  through the real module functions.
- C-2: the fix. Suggested shape (builder may improve): after taking the
  manifest lock, re-check the sidecar; if one appeared, release the manifest
  lock, join the sidecar (blocking), re-take the manifest lock, re-read and
  proceed — bounded retries, then proceed. Document the RESIDUAL window
  honestly in the code comment and in manifest decisions (what interleaving,
  if any, can still lose a record, and why it is acceptable or not).
- C-3: `python3 -m unittest` and `python3 scripts/validate.py` green.

## Negative control
Fork-point pattern (T7-corrected): with the new tests in the tree, restore the
base version `git show <fork>:runtime/scripts/evidence-run.py >
runtime/scripts/evidence-run.py` where `<fork>` is the unit branch's fork
point off BASE (confirm with `git merge-base`): the C-1 test fails with the
lost record. Restore via `git checkout HEAD -- runtime/scripts/evidence-run.py`:
green. Both directions observed and quoted.

## Red-first
C-1 lands and FAILS before the C-2 change (paste the failing output in the
manifest notes); then implement C-2.

## Hot files
- `runtime/scripts/evidence-run.py` (`sidecar_lock`, `append_record`)
- `tests/test_evidence_run.py`

## Out of scope
- Lock-free peers (impossible, see scope note).
- Changing #388 (no-create stays) or the steady-state protocol.
- Anything outside the owned files (below).

## Worker protocol (run conventions)
- Ownership: you may edit ONLY `runtime/scripts/evidence-run.py`,
  `tests/test_evidence_run.py`, `assets/badges/tests.json` (badge regen only),
  `docs/runs/2026-09-14-clean-sweep-tracker/u393r-manifest.json` and
  `docs/runs/2026-09-14-clean-sweep-tracker/u393r-negctrl.txt`. Nothing else.
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
- `u393r-negctrl.txt`: full terminal transcript of the negative control (both
  directions), pinned by sha256 in `artifacts[]`.
- Gates before worker_done: `python3 -m unittest discover -s tests` (full
  suite, ~4 min) green, `python3 scripts/validate.py` green.
- Do NOT push. Do NOT merge. Do NOT touch BASE. Commit locally only.
- worker_done: three-sentence summary + explicit --outcome, the code-tip SHA,
  gate outputs quoted, RED-first evidence quoted, files modified, report path
  = the manifest.
