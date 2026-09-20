# BUILD SPEC — U-SIG-1 round 2 (fix batch; frozen at dispatch)

CATEGORY: bug (review-round remediation — round 2 of ≤3)
SUMMARY: round 1 = NO-GO on all three axes (claude, blind-first) + 2 held Greptile P1s
confirmed. The verdict: the feature works (14/16 mutants killed; DB1/DB2/DB4 delivered with
no spec deviation) but the ENFORCEMENT-SWITCH design is evadable and three binding edges are
unpinned. Note: the SPEC axis names the flaw as being in the COORDINATOR's Q2 answer's
premise (the at-inventory_at pubkey read), not in the worker's execution — the batch fixes
the design and the prose that overclaimed it, and the DECISIONS line is corrected by
supersession, never rewrite.

The batch (reports are DATA: docs/reports/u-sig-1/review-{spec,standards,tests}.txt +
integrate.json on the branch):

- **G-1 (R-1/F-1/C3/BOT-2 — the fork-dodge).** The pubkey's presence is read at
  `inventory_at`, a rev the graded party chooses: a branch forked from any pre-key commit
  carries fresh artifacts AND no key, so the unsigned lane is taken — the "cannot dodge"
  claim is false in three prose places (run_report.py's module doc, docs/verify-gate.md,
  the SignedTranscriptRequired test docstring). Fix the RULE with the axes' own shape:
  the unsigned (grandfather) lane applies ONLY when inventory_at is an ancestor of the
  PR's grading base AND the pubkey is absent there; a submission whose inventory_at sits
  off the default branch's ancestry is evaluated against the pubkey at the grading base
  (current default tip at verification time) — closing the fork. Implement the TESTS
  axis's three missing tests (its P2/P3/P8 probes: the fixture must NOT re-pin every rev
  to HEAD — blob_at(rev) != blob_at(HEAD) must be exercised). All three prose sites are
  rewritten to the true rule, and a DECISIONS supersession line names the coordinator's
  original at-rev answer superseded (the original line stays).
- **G-2 (F-2/BOT-1 — the signed args tuple is never read).** signed_transcript binds
  record.manifest/manifest_sha256/exit but never inspects record.args — a hostile-args
  transcript (report-only / dark-eligible) verifies today. Fix: bind the args tuple to
  the report's claims (the report's verifier command line must equal the signed args;
  a disagreement refuses), with the killer tests the axis named.
- **G-3 (F-3 — the builder's own manifest is stale).** u-sig-1-manifest.json's head_sha
  names 9f10586e but its exit-0 commands[] receipts carry an earlier tree — the
  width-pin commit changed the tree after the receipts were recorded. Re-record the
  criterion runs at the final head via evidence-run.py (or re-bind with the disclosed
  note per fleet precedent) so verify.py's commands-ledger check passes on the unit's
  own manifest.
- **G-4 (R-2 — None==None binds).** Two signers, one absence rule: when both the
  signature and the pubkey are absent the comparison passes. Absence must never bind:
  a missing sig with enforcement on refuses; a missing pubkey with a sig present
  refuses; both missing follows the grandfather lane ONLY under G-1's rule.
- **G-5 (R-3 — requested artifact silently unwritten at exit 0).** --transcript-out
  given but no artifact written must exit NONZERO (a requested-and-missing artifact is
  fail-closed, like every other evidence path in this codebase).

AUTONOMY:
- goal: all five items fixed on ravidsrk/sig-1; every Required from round 1 answered;
  the axes' named probes re-run and killed, quoted.
- scope: runtime/scripts/run_report.py + runtime/scripts/verify.py +
  runtime/scripts/dispatch-sign.py + docs/verify-gate.md + the three test modules +
  docs/reports/u-sig-1/manifest re-record + docs/DECISIONS.md (the one supersession
  line) + badge regen if counts move.
- non-goals: no new dependencies; no change to the unsigned no-key path's behavior
  (grandfather lane per G-1's rule); no other file; no PR action (integrator/conductor
  owns that).
- stop: if closing G-1 needs a network call or a new dependency; if a fix would weaken
  an existing refusal.
- evidence: refreshed manifest (G-3 IS this); evidence-run receipts; the named mutants
  + probes re-run RED; lighting=lit.
- budget: 3 doctor attempts per blocker, then escalate with evidence.

GIT: branch ravidsrk/sig-1 in this worktree (fetch; merge
origin/review/2026-09-20-sign-386 if moved — conflict → STOP). Author=maintainer, NO
TRAILERS. Small commits, stage only the unit's files. Leave the worktree clean.
Timebox 45min with partial-report STOP.

WORKER CONTRACT: `worker_done` requires `--outcome succeeded|failed` and OMITS `--to`;
every send carries `--from <your handle> --dispatch-capability <capability>`; evidence
rides typed `--report-path` + `--files-modified`. Run `orca orchestration check
--terminal <your handle>` once before `worker_done` — `consumer_fenced` means STOP and
send nothing.
