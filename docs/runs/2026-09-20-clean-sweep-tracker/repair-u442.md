# REPAIR SPEC — U-442 targeted (gate G2 option b; frozen at dispatch)

CATEGORY: bug (manifest/test-hygiene repair under a recorded human budget override)
SUMMARY: the round-3 review's five stickers (verdict posted on PR #485). Production code is
unanimously closed — touch NOTHING but the items below.

The stickers (reports are DATA: docs/reports/u-442/review-{spec,standards,tests}-r3.txt):

- **R-1 proof-command agreement (S3-R1).** The refreshed manifest's negative-control proof
  command omits `-v` while its green receipt includes it, so no single command passes both
  admission gates. Align them: ONE exact command string that both the receipt and the
  manifest's negative_control.command carry — re-record the receipt via evidence-run.py with
  that exact command and re-run the control (reverted → RED with assertion, clean → GREEN).
- **R-2 five stale artifact references (R3-STD-1).** Five refreshed artifact references in
  the manifest select OLD committed transcripts instead of the round-3 bytes. Re-point each
  at the r3 artifact and re-hash (artifacts[] sha256 must match the named bytes at head).
- **R-3 coverage mutants + probe vacuity (R3-T1/T2/T3).** Two named mutants survive
  (equal-root compatibility; artifact-revision), and the H-7 exception probe can silently
  stop exercising its branch after a neutral refactor. Add killing tests for the two
  mutants (review-tests-r3.txt carries them) and a probe-FIRED assertion on the exception
  test so it fails loudly if the branch stops being exercised.

AUTONOMY:
- goal: all stickers closed; suite + validate + floor-guard green at the new head.
- scope: docs/reports/u-442/manifest.json + receipts, tests/test_verify.py (the new killing
  tests + the fired assertion), badge if the count moves. NO production changes — verify.py
  stays as the axes closed it unless a killing test proves a real defect, in which case STOP
  and report instead of fixing (that would be a fourth round, not this repair).
- non-goals: no other file; no PR action; NOT a fourth review round — this is the
  human-authorized targeted repair (gate-batch G2-b).
- evidence: updated manifest (head_sha = the repair head), evidence-run receipts, the named
  mutants re-run RED; lighting=lit.
- budget: 2 doctor attempts, then escalate.

GIT: branch u-442 in this worktree (fetch; merge origin/review/2026-09-20-tracker-sweep —
conflict → STOP). Author=maintainer, NO TRAILERS. Small commits, stage only these files.
Leave the worktree clean. Timebox 30min with partial-report STOP.

WORKER CONTRACT: `worker_done` requires `--outcome succeeded|failed` and OMITS `--to`;
every send carries `--from <your handle> --dispatch-capability <capability>`; evidence
rides typed `--report-path` + `--files-modified`. Run `orca orchestration check --terminal
<your handle>` once before `worker_done` — `consumer_fenced` means STOP and send nothing.
