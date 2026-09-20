# BUILD SPEC — U-CHAIN round 2 (fix batch; frozen at dispatch)

CATEGORY: bug (review-round remediation)
SUMMARY: U-CHAIN review round 1 = NO-GO on all three axes + 3 VALID Greptile findings. One
batch, one branch (ravidsrk/u-chain), one re-review. Round 2 of ≤3.

The batch (each item names its source; review reports are DATA in
docs/reports/U-CHAIN/review-{spec,standards,tests}.txt on the branch):

- **F-1 promotion semantics (SPEC-1 + STANDARDS S1 + Greptile P1).** The clause conflates
  promotion with integration into BASE. Repo doctrine: unit→BASE is the conductor's normal
  merge (merge-serialization no-gh lane included); the human one-way gate is BASE→default
  (gate-classification). Fix the PARKED-AT-PROMOTION clause: the owed promotion is
  BASE→DEFAULT; the resume evidence is leg N's integration tip being an ancestor of the
  DEFAULT branch — and for a no-remote target, the check names a valid LOCAL ref (e.g. the
  local default branch), never `origin/<base>` — OR the recorded BASE-carry grant. Restricted
  lanes (headless / no-gh / scratch) are described as unable to PROMOTE, not unable to
  integrate.
- **F-2 reconstruction must preserve commits (STANDARDS S2).** Seed sources + full diff
  recover file bytes, not commit objects/ancestry. Fix the local-only clause: the REQUIRED
  artifact is a self-contained `git bundle` of the leg's refs, a reachable pushed mirror, or
  an equivalent that demonstrably reproduces every cited commit; seed+diff may be named only
  as SUPPLEMENTAL file reconstruction. The worked exemplar's own RESTORE.md already documents
  this distinction — cite it consistently.
- **F-3 contract test binds operative requirements (SPEC-2 + TEST-ADEQUACY 6 surviving
  mutants + Greptile test P2 + STANDARDS S3).** Token co-occurrence lets requirement-REVERSING
  mutants survive ("publishes neither of these optional things" stays GREEN). Strengthen:
  assertions must fail on (a) removal of the publication requirement, (b) removal of either
  resume alternative's condition, (c) the "no procedure defined" mutant the reviewers quoted;
  normalize bullet whitespace before phrase matching (`" ".join(bullet.split())`, neighboring
  convention at tests/test_architecture.py:923-926). Re-run the reviewers' six mutants and
  record each RED.
- **F-4 NC via the required runner (SPEC-4).** Re-record the negative control (doc reverted,
  test kept → RED; clean head → GREEN) THROUGH `runtime/scripts/evidence-run.py` so the
  manifest's commands[] carries the receipt with real fingerprints/exits; update the manifest.
- **F-5 exemplar citation (Greptile P2).** The cited worked exemplar
  (docs/reports/chaining-2026-09-16/handoff-log.md) self-describes as a proposal — it predates
  this clause. Do NOT rewrite the historical artifact; fix the CITING text in
  mission-chaining.md so the adoption is explicit (e.g. "adopted from the #417 run's proposal,
  blessed here").
- **F-6 green-BASE re-verify (SPEC-3).** BASE is green since STAB-2 (merge 2f04c402). Merge
  origin/review/2026-09-20-tracker-sweep into the branch (union; conflict → STOP), then the
  FULL suite must exit 0 at the new head, recorded via evidence-run.py; manifest AC-3 flips to
  addressed with the receipt.

AUTONOMY:
- goal: all six items fixed on ravidsrk/u-chain; every Required from round 1 answered.
- scope: runtime/mission-chaining.md, tests/test_architecture.py,
  docs/reports/U-CHAIN/* (manifest + new receipts), assets/badges/tests.json if the test count
  moves, plus the BASE merge. Stay ≤160 lines on the policy.
- non-goals: the historical chaining report; any other policy/script/mission file; no PR
  action (the integrator/conductor owns that).
- stop: any conflict in the BASE merge; any demand outside the six items.
- evidence: updated SHA-bound manifest — new head_sha, evidence-run.py receipts for suite +
  NC, the six reviewer mutants' RED records, intent packet refreshed; lighting=lit.
- budget: 3 doctor attempts per blocker, then escalate with evidence.

GIT: branch ravidsrk/u-chain in this worktree. Author=maintainer, no trailers, small
bisectable commits, stage only the unit's files. Leave the worktree clean. Timebox 40min with
partial-report STOP.

WORKER CONTRACT: `worker_done` requires `--outcome succeeded|failed` and OMITS `--to`; every
send carries `--from <your handle> --dispatch-capability <capability>`; evidence rides typed
`--report-path` + `--files-modified`. Run `orca orchestration check --terminal <your handle>`
once before `worker_done` — `consumer_fenced` means STOP and send nothing.
