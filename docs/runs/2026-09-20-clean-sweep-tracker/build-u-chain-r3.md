# BUILD SPEC — U-CHAIN round 3, FINAL (fix batch; frozen at dispatch)

CATEGORY: bug (review-round remediation — round 3 of 3; a round-3 NO-GO parks the unit)
SUMMARY: round 2 = NO-GO on all three axes. The doctrine text is now right; the fight is
(a) one real freshness hole in the resume check, and (b) the contract test + mutation harness
still accepting reversed, missing, or stillborn evidence. One batch on ravidsrk/u-chain.

The batch (reports are DATA: docs/reports/U-CHAIN/review-{spec,standards,tests}-r2.txt):

- **G-1 freshness of the default ref (BOT-4, all axes).** The resume check's ancestry test
  names `origin/<default>` with no freshness obligation — a cached ref parks a promoted
  chain. Add to the clause, following the repo's own pattern (`runtime/scripts/preflight.py`'s
  default-resolution contract): for a REMOTE target the check first refreshes the default ref
  (fetch), and a ref whose freshness cannot be established makes the promotion UNPROVEN,
  never landed; the LOCAL (offline) branch stays explicitly local. Update the contract test
  to bind both sentences.
- **G-2 harness publishes its baseline (BOT-5 / S-R2-2).**
  `docs/reports/U-CHAIN/run_mutants-r2.py` reads `base-policy.md`, which is neither tracked
  nor created — a clean-checkout replay exits 1 with zero mutants run. Fix: the harness
  DERIVES the baseline itself (`git show <unit-base-sha>:runtime/mission-chaining.md`, the sha
  pinned in the file) or the fixture is tracked; a clean exact-checkout invocation must run
  all mutants.
- **G-3 stillborn evidence is not a kill (S-R2-3 / R2-HARNESS).** The harness calls any
  nonzero mutant exit "KILLED (RED)" and reports success when controls fail. Fix: a mutant
  run is a KILL only when the output carries an ASSERTION failure (ImportError / collection
  error / no-tests-ran = STILLBORN, harness exits nonzero); both positive controls
  (fixed-head, head-restored) MUST be green or the harness exits nonzero.
- **G-4 resume alternatives bound (R2-TA-441).** The park test must fail when either resume
  alternative loses its condition: bind, within EACH numbered alternative, its full
  obligation set (alternative 1: BASE tip + ancestor-of-DEFAULT + the ref rule incl. G-1's
  freshness; alternative 2: named human + explicit decision + unpromoted BASE tip + granted
  SHA written down), plus the "exactly one of two facts / nothing else is sufficient"
  framing. Re-run the reviewers' executed survivors and record them RED.
- **G-5 carry schema + missing-log bound (R2-TA-443).** Bind the carry table's FULL field set
  (carry id · from · content · input status incl. the OWED rule) and the gate record's
  (which gate · state · owning human · what resumes it) plus "a MISSING handoff log is an
  unfinished chain, never an empty one". Kill the three named survivors.
- **G-6 reconstruction obligations bound (R2-TA-444).** Bind "reproduces every cited commit
  AND ITS ANCESTRY", the mirror's "remote and pushed refs written down", seed+diff as
  "SUPPLEMENTAL and never sufficient", and the integrity-inventory hash obligation. Kill the
  three named survivors.

AUTONOMY:
- goal: all six items fixed; every round-2 Required answered; harness replay green from a
  clean checkout with all mutants KILLED-for-the-right-reason.
- scope: runtime/mission-chaining.md (≤160 lines), tests/test_architecture.py,
  docs/reports/U-CHAIN/* (harness + manifest + receipts), badge if the count moves, BASE
  merge if BASE moved.
- non-goals: everything else; no PR action; do not weaken any existing assertion to make a
  survivor pass — the answer to a survivor is a stronger bind or a policy clause that really
  carries the obligation, never a deleted probe.
- stop: if closing a survivor would require the policy to assert something false or outside
  the three findings' scope, STOP and ask — that is a round-3 parking conversation, not a fix.
- evidence: refreshed manifest — new head_sha, evidence-run.py receipts (contract test,
  validate, full suite exit 0, NC re-run), the reviewers' named survivors re-run RED with
  assertion failures, harness replay transcript; lighting=lit.
- budget: 3 doctor attempts per blocker, then escalate with evidence.

GIT: branch ravidsrk/u-chain in this worktree (fetch; merge origin/review/2026-09-20-tracker-sweep
if moved — conflict → STOP). Author=maintainer, no trailers, small commits, stage only the
unit's files. Leave the worktree clean. Timebox 45min with partial-report STOP.

WORKER CONTRACT: `worker_done` requires `--outcome succeeded|failed` and OMITS `--to`; every
send carries `--from <your handle> --dispatch-capability <capability>`; evidence rides typed
`--report-path` + `--files-modified`. Run `orca orchestration check --terminal <your handle>`
once before `worker_done` — `consumer_fenced` means STOP and send nothing.
