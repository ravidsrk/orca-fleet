# Leg 1 — clean-sweep ledger

`RUN · COORDINATOR=subagent-01a0a9a5 · BASE=chain417/leg1-cleansweep-base · FORK_POINT=892eae208b01780a426deecdf9e81380753b30cc · T0=2026-09-16T09:56Z · SOURCE=audit:issue-417-declaration-7-findings · WIP=1`

Target: `/Users/ravindra/projects/chaining-target-417` (scratch, no remote — no-gh lane).
Suite: `uv run --with pytest pytest -q` in target root. Baseline @FORK_POINT: 4 passed.

## Triage + freeze (2026-09-16)

| task_id | id | title | CLASS | BUILD_DONE | PR_OPEN | BOT | REVIEWED | MERGED | WT_CLEAN | lighting | park | evidence |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| L1F1 | F1 | hardcoded admin token | real (security) | — | — | — | — | — | — | lit | out-of-scope → leg-2 carry H1 | code read notes.py:16; mission must not own secrets |
| L1F2 | F2 | SQL string interpolation | real (security) | — | — | — | — | — | — | lit | out-of-scope → leg-2 carry H2 | code read notes.py:30-33; exploit proof is harden-it's unit |
| L1F3 | F3 | None-token deletes | real-bug | t | t(no-gh branch) | n/a | self-GO / indep-PENDING | t `eec6505` | t | lit | — | head `b68a7be`; test RED→GREEN; NC exit 1/0; wtree-bound |
| L1F4 | F4 | export crash on empty | refuted | n/a | n/a | n/a | n/a | t `c5e807c` (comment closeout) | t | lit | refuted (mechanical: repro exit 0, `[]`) | triage+reenumeration transcripts; G-REFUTE |
| L1F5 | F5 | MD5 content hash | real-bug-small | t | t(no-gh branch) | n/a | self-GO / indep-PENDING | t `873724d` | t | lit | — | head `690b79d`; test RED→GREEN; NC exit 1/0; wtree-bound |
| L1F6 | F6 | false AES-256 claim | doc-claim | t | t(no-gh branch) | n/a | self-GO / indep-PENDING | t `4c5c946` | t | lit | — | head `0ee5a79`; NC grep exit 0/1; suite 4 passed |
| L1F7 | F7 | delete-requires-token claim | doc-claim | t | n/a (BASE closeout) | n/a | n/a | t `3a40662` | t | lit | — | TRUE post-F3 (CLI denied/deleted); stale-marker dropped |

Wave plan → frozen-id coverage: {F1..F7} each map to exactly one row above. No
finding omitted at dispatch (anti-pattern guard asserted).

## Landings (conductor, serial, --no-ff)

- `eec6505` F3 ← `b68a7be` (parents `892eae2 b68a7be`); suite 5 passed.
- `873724d` F5 ← `690b79d` (conductor-resolved test-append conflict, both kept);
  suite 6 passed.
- `4c5c946` F6 ← `0ee5a79`; suite 6 passed.
- `3a40662` F7 closeout (stale-marker drop; claim verified true via CLI:
  no-token → `denied`, token → `deleted`); suite 6 passed, wtree-bound.
- `c5e807c` F4 closeout (stale-crash-comment drop); suite 6 passed, wtree-bound
  (`7f03245…`). FINAL BASE tip.

Re-enumeration @ `c5e807c` (pasted): export-empty → exit 0 `[]` (F4 stays
refuted); `delete 1` no-token → `denied` (F3 fixed, F7 true); `AES-256` only in
F6's historical note; `SEED-1`/`SEED-2` intact (parked); full diff
`892eae2..c5e807c` re-read — no new findings. Denominator: 4 CLOSED (F3 F5 F6,
F7-via-F3) + 1 refuted (F4) + 2 parked-clean out-of-scope (F1 F2). Zero degraded.

## Gate record

- G-REFUTE (refuted close F4): ruled MECHANICAL per gate-classification
  (deterministic executed repro, re-derivable) — auto-resolved, recorded here.
  Batch human gate NOT opened; disclosed as mission-level observation O1.
- G-REVIEW (deviation D1, FINAL): independent build-blind review UNAVAILABLE.
  Fresh-session spawn rejected 7× (fleet capacity 8/8), then accepted 2× but
  both children died in ~10ms on infra config fatal (`unknown tool work_stop`,
  deterministic — not retried further). Orca-TUI-worker path ASSESSED AND
  DECLINED: 5–8 unfamiliar setup round-trips on the shared runtime for an
  outcome that cannot change the chain's stopped state (G-PROMO-1 waits behind
  this gate regardless) — forcing a DRY through exotic paths would be routing
  around a stop. Merges rode on recorded NON-gating author self-checks.
  CONSEQUENCE: DRY is NOT declared; leg-1 terminal is NOT-DRY (exhausted,
  review-owed). RESUME: the PR reviewer (human, second person) reads
  `full-diff.txt` (77 lines) + re-derives from the SHAs below — that verdict
  lifts G-REVIEW to DRY (if GO) or fix-forwards (if findings).
- G-PROMO-1 (HUMAN QUEUE): BASE→default promotion owed. BASE
  `chain417/leg1-cleansweep-base` @ `c5e807c` stops here per clean-sweep
  ("open the promotion PR, stop") + merge-serialization no-gh ("stops at BASE")
  + gate-classification (promotion one-way, recorded human grant always).
  Coordinator-executed promotion (D2) was CONSIDERED AND REFUSED — reclassifying
  by "it's just scratch" is the exact rewording decisions.py refuses. This hold
  sits BEHIND G-REVIEW (the run stopped at the leg-1 gate first): even with
  G-REVIEW lifted to DRY, leg 2 cannot fork a BASE without either a landed
  promotion or a human BASE-carry decision (mission-chaining: carry-over is
  explicit-human, never default) — certain by doctrine analysis, three policies
  agreeing. Chain PARKED. No human answer faked; no agent message labeled
  approval.
