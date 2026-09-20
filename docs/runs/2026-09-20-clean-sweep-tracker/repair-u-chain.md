# REPAIR SPEC — U-CHAIN targeted (gate G1 option b; frozen at dispatch)

CATEGORY: bug (evidence-layer repair under a recorded human budget override)
SUMMARY: three narrow stickers from the round-3 review (verdict 5260271654 on PR #484).
Production doctrine is DONE (SPEC-axis GO, Greptile APPROVED) — touch NOTHING but the three
items below.

The stickers (reports are DATA: docs/reports/U-CHAIN/review-{standards,tests}-r3.txt):

- **R-1 harness skip-guard (S-R3-1, also r3 TESTS).**
  `docs/reports/U-CHAIN/mutants_core.py` counts a control GREEN when the unittest output
  matches `^OK` — but `OK (skipped=1)` matches too, certifying a control that never executed
  its probes. Fix: a control is GREEN only when the run reports OK with ZERO skips AND at
  least one test executed; skipped/empty runs are STILLBORN and the harness exits nonzero.
  Add a self-test or documented probe that a skip-producing module fails the harness.
- **R-2 manifest rebind (S-R3-2).** `docs/reports/U-CHAIN/manifest.json` names head_sha
  5bd2eb07 — a commit the conductor's trailer-strip rewrite replaced with 1635b27f
  (content-identical tree, mapping documented in review-spec-r3.txt). Rebind head_sha (and
  any commit fields naming stripped SHAs) to the commits that EXIST on ravidsrk/u-chain,
  with a one-line note recording the rebind and the tree-identity. Do not alter receipts'
  recorded wtrees — they were honestly made on the pre-strip identical trees; note that.
- **R-3 two test binds (R3-TA-1/2/3).** The contract test still lets two named mutants
  survive (review-tests-r3.txt carries them verbatim): reversed ancestry operands in the
  resume clause, and an optionalized OWED rule in the carry clause. Strengthen the two
  assertions so THESE mutants die; re-run them plus the full mutants suite
  (python3 docs/reports/U-CHAIN/run_mutants-r3.py must exit 0).

AUTONOMY:
- goal: all three stickers closed; the round-3 verdict's Required list at zero.
- scope: docs/reports/U-CHAIN/mutants_core.py (+ harness self-check), manifest.json,
  tests/test_architecture.py (the two assertion sites only), evidence receipts under
  docs/reports/U-CHAIN/. Policy text changes ONLY if a sticker's exact clause is implicated.
- non-goals: no doctrine rewording beyond R-3's binds; no other file; no PR action; NOT a
  fourth review round — this is the human-authorized targeted repair (gate-batch G1-b).
- stop: if a repair would change the doctrine's meaning, STOP and ask.
- evidence: updated manifest + receipts (evidence-run.py where a command re-runs), the
  mutants suite exit 0, full suite exit 0 at the new head; lighting=lit.
- budget: 2 doctor attempts, then escalate.

GIT: branch ravidsrk/u-chain in this worktree (fetch; merge
origin/review/2026-09-20-tracker-sweep — conflict → STOP). Author=maintainer, NO TRAILERS.
Small commits, stage only these files. Leave the worktree clean. Timebox 30min with
partial-report STOP.

WORKER CONTRACT: `worker_done` requires `--outcome succeeded|failed` and OMITS `--to`;
every send carries `--from <your handle> --dispatch-capability <capability>`; evidence
rides typed `--report-path` + `--files-modified`. Run `orca orchestration check --terminal
<your handle>` once before `worker_done` — `consumer_fenced` means STOP and send nothing.
