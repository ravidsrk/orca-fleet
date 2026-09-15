# T11 FIX round 3 — U393R: honest residual + unfragile F-1 (verdict r2 NO-GO)

## Context
V393R-r2 (review 5211964513, COMMENTED, reviewed 55ef070) is NO-GO on two
Requireds, both reproduced by the verdict worker on scratch copies of 55ef070.
The M1/M2/M3 killers stand (all kill); this round is one doc correction + one
test-hardening. No production behavior change is asked for or expected.

## Batched request (all required)
- RQ-1 (SPEC residual doc): the residual-window docs (append_record docstring,
  manifest noticed_not_touched[0], manifest decisions) name only "a dropped
  record". Reproduce the SPEC r2 demo first (forced schedule, real
  append_record: legacy reads after the look, writes between truncate and
  flush): it leaves the manifest CORRUPT JSON ("Extra data"), the tearing
  append prints no WARNING, and every later append warns and records nothing.
  Then correct all three texts to name the FULL outcome set (drop vs corrupt
  vs poisoned-ledger, with the mechanism for each) and name the last-attempt
  write-through with an unjoined sidecar as the second loss path (SPEC FYI-1,
  adjacent). Keep it tight: outcomes + mechanism, no redesign prose.
- RQ-2 (S-1+N-1 merged, S-3 adjacent): the F-1 killer's module-level `open`
  stand-in goes vacuous under a behavior-neutral refactor (os.fdopen(os.open)
  for the sidecar open): F-1 stays green and M1 then survives 31/31. Harden
  the test so the vacuity is impossible-or-loud: assert the stand-in FIRED
  with a literal expected count (a refactor that bypasses it must RED, not
  pass silently). Correct the manifest's 'neither passes silently' line to
  match what is now pinned, and have the SidecarRejoin docstring name its
  stand-ins (S-3). Reproduce X8b/S-1 (os.fdopen refactor + M1) RED before and
  GREEN-theory after: the hardened test must FAIL on (refactor+M1) and PASS
  on the fix — quote both.
- Records: transcripts for the RQ-1 demo + RQ-2 vacuity kill (both directions)
  appended to u393r-negctrl.txt ROUND 3; badge regen only if the count moves
  (its own commit); C-3 gates re-recorded at the new head. Full suite +
  validate green at the code tip.

## Red-first
RQ-2's hardened assertion lands and FAILS on (refactor+M1) before any other
change (paste the failing output in the manifest notes). RQ-1 is docs: quote
the reproduced corrupt-manifest output in the negctrl.

## Worker protocol (run conventions)
- Worktree /Users/ravindra/orca/workspaces/orca-fleet/u393-race. REATTACH
  FIRST (reviewers leave it detached; one axis reattached but assert anyway):
  `git status --porcelain` empty; `git checkout ravidsrk/u393-race`; assert
  branch + `git rev-parse HEAD` == 55ef0704d0498a16c4d3034f537ab3ddffdffdab.
  Anything else = STOP.
- Ownership: ONLY `tests/test_evidence_run.py`,
  `runtime/scripts/evidence-run.py` (comments/docstrings only — any behavior
  delta is a STOP, say why),
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
  gate outputs quoted, RQ-1/RQ-2 evidence quoted, files modified, report path
  = the manifest.
