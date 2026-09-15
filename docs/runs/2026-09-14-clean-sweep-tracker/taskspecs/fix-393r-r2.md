# T11 FIX round 2 — U393R: pin the rejoin (verdict r1 NO-GO)

## Context
V393R-r1 (review 5211486225, COMMENTED, reviewed abaf175) is NO-GO on two
TEST-ADEQUACY Requireds, both re-verified by the verdict worker on scratch
copies of abaf175 (each mutant passes 29/29). The production fix itself stands
(SPEC: C-1/C-2/C-3 met, no scope creep); this round is test-hardening plus
touched-file text fixes. Greptile P1 4015794383 was ACCEPTED with reason by the
verdict (the disclosed residual, unclosable under #388) — do NOT chase it.

## Batched request (all required)
- F-1 (TEST R-1): pin the last-attempt write-through. Killer: M1 drops the
  `attempt < REJOIN_ATTEMPTS` guard at evidence-run.py:212 — today that mutant
  passes all 29 tests while silently writing nothing on a sidecar-present final
  attempt. Add a test that FAILS on M1 and passes on the fix.
- F-2 (TEST R-2): pin the pre-truncate re-check POSITION. Killer: M2 moves the
  look to right after the manifest flock — today that passes all 29 tests while
  a sidecar created after the read loses ['new']. Add a forced-schedule test
  with the sidecar created AFTER the read and BEFORE the truncate, asserting
  all records land ([seed,legacy,new]); it must FAIL on M2 and pass on the fix.
- F-3 (coordinator-verified data, same mechanism): pin the BLOCKING join, not
  just the re-read. Killer: M3 replaces the attempt>1 sidecar_lock with
  `contextlib.nullcontext(True)` — the coordinator reproduced this mutant
  SURVIVING 20/20 race-test runs and the full 29-test module (3.9s, OK) at
  abaf175, because the forced schedule pins the re-read but nothing forces the
  rejoin to block on the sidecar. Add a test (or extend F-2's choreography)
  that FAILS on M3 and passes on the fix. If pinning the block is impossible
  without production changes, say so with the mechanism argument and propose
  the minimal production touch — do NOT silently skip.
- F-4 (text fixes, touched files only): the manifest's C-2 `exists()`/OSError
  witness (false on py3.13 — PermissionError raises; conclusion holds via the
  outer except), the residual "one write" wording (understates the buffered
  write-to-close gap), the :138 sidecar_lock docstring (describes its caller),
  the :211 comment (lost referent). One fix each, no essays.
- F-5 (records): RED/GREEN + M1/M2/M3-kill transcripts in u393r-negctrl.txt
  (both directions observed and quoted), badge regen if the count moves (its
  own commit), C-3 gates re-recorded at the new head. Full suite + validate
  green at the code tip.

## Red-first
Each killer lands and FAILS on its mutant before any production touch (paste
the failing output in the manifest notes). Production changes are expected to
be ZERO — if F-3 forces one, it gets its own red-first commit and a decisions
entry.

## Worker protocol (run conventions)
- Worktree /Users/ravindra/orca/workspaces/orca-fleet/u393-race. REATTACH
  FIRST (conductor-close.md reattach rule — reviewers left it detached):
  `git status --porcelain` empty; `git checkout ravidsrk/u393-race`; assert
  branch + `git rev-parse HEAD` == abaf17502a25f16dbd4cfaf28fafba1e211ab40a.
  Anything else = STOP.
- Ownership: ONLY `tests/test_evidence_run.py`,
  `runtime/scripts/evidence-run.py` (F-3-conditional; prefer zero),
  `assets/badges/tests.json` (badge regen only),
  `docs/runs/2026-09-14-clean-sweep-tracker/u393r-manifest.json`,
  `docs/runs/2026-09-14-clean-sweep-tracker/u393r-negctrl.txt`. Nothing else.
- The manifest commit follows head_sha (option A); the conductor re-binds at
  close. Contract source for new records: this spec file@dispatch-commit
  (given in your TASK preamble) + its sha256 (given).
- Gates before worker_done: `python3 -m unittest discover -s tests` green,
  `python3 scripts/validate.py` green.
- Do NOT push. Do NOT merge. Do NOT touch BASE. Commit locally only, one
  concern each.
- worker_done: three-sentence summary + explicit --outcome, the code-tip SHA,
  gate outputs quoted, per-killer RED/GREEN evidence quoted, files modified,
  report path = the manifest.
