# Self-test campaign 2026-09-16 — rollup

All 21 missions ran against orca-fleet itself on 2026-09-16, one isolated
worktree per mission, base `origin/main` tip (`6390743`/`c46d4b3`, pre-#451).
Each mission kept its full transcript on its own archive branch
(`origin/campaign/<mission>-selftest`); this report is the curated index.
Full per-mission dirs were deliberately NOT merged to `main`: none of the
21 runs bids for a proof-tier advance except through the follow-ups named
below, and their dirs were not built to BIND.

Conventions: terminal names are the missions' own. "Recorded history" means
the run is evidence of honest execution at the mission's current tier, not a
promotion claim.

## Scoreboard

| Mission | Archive HEAD | Terminal | Standing after campaign |
|---|---|---|---|
| absorb-it | `bd79d5a4` | ABSORBED (empty queue = own terminal) | recorded history, doctrine-only |
| access-it | `4b5b3c87` | PARKED — missing target (no UI) | recorded history, doctrine-only |
| attest-it | `b98394a3` | CONFORMANT-WITH-GAPS (34 VERIFIED, 8 GAP, NIST SP 800-218) | recorded history, doctrine-only |
| clean-sweep | `cc57ee66` | DRY-WITH-PARKED (0 closed, 9 parked; U434 needs-human secret) | recorded history; U434 still owes a maintainer secret |
| deflake-it | `86abeef6` | FIXED-LOCAL (F1 fixed at `c8abd8c`; CI leg owed) | promotion PR owed (lever 3) |
| document-it | `0501f476` | DOCUMENTED (32/32 cells terminal) | page at `c064b27` owes a promotion PR (lever 3) |
| field-test-it | `eb5da0e3` | PARKED — no app/device target | recorded history, doctrine-only |
| floor-it | `9e574c0b` | PARKED at FREEZE (human one-way gate) | gate-recorded on main; unpark plan (CONSTRAINTS/WIRE/canaries/GUARD) queued |
| harden-it | `2ca067e0` | CLEAN (zero VERIFIED P0/P1) | recorded history, doctrine-only |
| map-it | `0fee07fd` | MAPPED-WITH-BLOCKED → promoted | **external-run** (promotion #451 merged) |
| migrate-it | `7c44075e` | PARKED — zero tables | recorded history, doctrine-only |
| modernize-it | `e34f11d5` | U1 BUILT + locally merged (ruff 0.16.5→0.16.7 at `d3ee3f5`) | promotion PR owed (lever 3) |
| oncall-it | `2b87883d` | PARKED — no production path | recorded history, doctrine-only |
| oss-contribute | `9fa3edc3` | PARKED — no qualifying upstream | recorded history, doctrine-only |
| pin-it | `23a3a498` | PINNED-WITH-PARKED (substrate-blocked probes) | re-owed to next re-pin (#427) |
| prove-it | `a1296826` | COVERED (PF-3 net) | already self-run, no advance; net owes a promotion PR (lever 3) |
| reshape-it | `e1e2634f` | parked pre-BOOTSTRAP (confirm-surface gate open) | gate-recorded on main; unpark (validate.py + verify.py) queued |
| review-it | `467f4484` | GO on PR #445 | recorded history, doctrine-only |
| root-cause | `94205bfc` | INCONCLUSIVE (H2 falsified; honest park) | recorded history, doctrine-only |
| ship-it | `b0199f15` | PARKED at entry (no input) | recorded history, doctrine-only |
| speed-it | `816a3ce3` | OPTIMIZED-WITH-PARKED (H1 fixed; J1/J3 parked) | H1 owes a promotion PR (lever 3); J1 infra + #440 repro queued |

7 missions reached a mission-named DONE-class terminal; 8 parked on a
genuinely missing target (correct behavior — no run was fabricated); 6 ended
degraded-with-evidence and produced the follow-up queue below.

## What the campaign proved

- The honest-park machinery works: missions with no target parked instead of
  fabricating runs, and missions that hit substrate limits (`no_active_sender_terminal`,
  no live Orca terminal) recorded BLOCKED-BY-SUBSTRATE preconditions rather
  than reclassifying standing.
- The proof ladder held: the only tier advance out of 21 runs is map-it's
  external-run (#451), carried by a binding run report — everything else
  stayed exactly where its evidence puts it.
- Where the repo had real defects, missions found real fixes: the ruff bump
  (U1, built + reviewed + manifest-verified on-branch), the F1 flake fix,
  the H1 hot-path fix, the PF-3 coverage net, and the documentation page.
  None of these were pushed by the campaign harness (push was forbidden);
  promoting them is ordinary lever-3 PR work, below.

## Follow-up queue (all still open at rollup time)

1. Lever-3 promotion PRs: modernize U1 (`d3ee3f5`), deflake F1 (`c8abd8c`),
   document-it page (`c064b27`), speed-it H1, prove-it PF-3 net.
2. Reshape unpark: validate.py + verify.py CHARACTERIZE/DEEPEN.
3. Floor unpark: CONSTRAINTS + WIRE + canaries + GUARD (extends the #452
   verdict-derived check workflow).
4. Verdict-derived required check (#452) — makes branch protection real.
5. Speed-it J1 infra (campaign-Orca probes) + #440 repro; U434 secret (clean-sweep).
6. #386 intake transcript + assess-response signing; pin-it probes re-owed to #427.

## Re-deriving this report

```bash
git ls-remote origin 'campaign/*-selftest'   # all 21 archive branches
git show origin/campaign/<m>-selftest:docs/runs/campaign-2026-09-16-<m>/  # full transcript
```

Archive SHAs above are the branch tips at push time (2026-09-16); the
branches are append-only history and must not be rewritten.
