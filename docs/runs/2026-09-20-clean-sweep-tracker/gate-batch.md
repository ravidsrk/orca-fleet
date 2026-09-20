# Gate batch — run_bec47e54b673 (clean-sweep 2026-09-20)

One-way human decisions owed by this run. Precedent: docs/runs/2026-09-14-clean-sweep-tracker/gate-batch.md.

## G1 — U-CHAIN review-round budget exhausted (PARK)

**Unit:** U-CHAIN (#441/#443/#444), PR #484 vs review/2026-09-20-tracker-sweep, head d75b23b1.
**State:** THREE failed review rounds (acceptance-review budget). SPEC axis r3 = GO — the
doctrine text is correct and complete; Greptile APPROVED d75b23b1; suite 1707 OK; harness
28/28 kills replay from a clean checkout.

**Sticking findings (all evidence-layer, none doctrinal):**
1. Harness accepts SKIPPED positive controls as success (`OK (skipped=1)` matches `^OK`) —
   S-R3-1 + r3 TESTS same finding.
2. Manifest head_sha names 5bd2eb07, a commit the CONDUCTOR's trailer-strip rewrite replaced
   with 1635b27f (content-identical tree) — S-R3-2. Coordinator-caused; the rebind is a
   one-line evidence correction with the mapping documented in the r3 SPEC report.
3. Contract test still lets two narrow mutants survive: reversed ancestry operands and an
   optionalized OWED rule — r3 TESTS.

**Options:**
- (a) ACCEPT PARK: #441/#443/#444 stay OPEN; branch ravidsrk/u-chain retained at d75b23b1;
  the run closes DRY-WITH-PARKED naming this gate.
- (b) AUTHORIZE exceptional conductor-led repair of the three narrow stickers (harness
  skip-guard, manifest rebind, two test binds) + a TARGETED re-review of just those fixes —
  a recorded budget override, human-named.
- (c) MERGE ANYWAY with accept-with-reason (Greptile APPROVED + SPEC GO + the stickers are
  evidence-layer) — recorded as a human override of the round budget.

**Default if unanswered:** (a). A fleet never fakes a human answer.
