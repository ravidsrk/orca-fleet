# REFLECTION — clean-sweep 2026-09-20 (run_bec47e54b673)

Terminal: DRY-WITH-PARKED (2 units parked at the review-round budget, gates G1/G2).

## Surprises

- The test-adequacy axis is an arms race with no floor: every round produced NARROWER
  surviving mutants (6 → 12 → 2-3 per unit). The doctrine/code was right by round 2; the
  budget parked both units on evidence-layer stickers. The round budget did exactly its
  job — without it this loop runs forever.
- Claude workers appended `Co-Authored-By` trailers TWICE despite an explicit "no trailers"
  spec line — caught only at harvest. The third wave's explicit "twice bitten" warning
  worked (0 trailers). A check at BUILD time beats a rewrite after: the trailer strip
  invalidated a manifest's recorded SHA, which itself became a review finding (S-R3-2).
- My own STABILIZE commits broke 5 pre-existing tests (index row + generator-string fixed
  point) — the run's first red was self-inflicted, and the run-archive integrity test reads
  the LEDGER for a line I dropped at freeze time.
- `worker-stop` settles its task to `blocked` with NO gate row — recovery is a manual
  `task-update --status ready`, not `gate-resolve` (gate-list is empty).
- `check --ack` returned the NEXT delivery in the same envelope once; and an ack envelope
  once read `ok:false` while the ack had in fact landed — trust the delivery-id progression,
  not the envelope's ok bit alone.

## Proposed AGENTS.md / GOTCHAS appends (HUMAN MUST APPROVE EACH LINE)

- GOTCHAS (worker preambles): put "no Co-Authored-By / agent trailers" in the WORKER
  CONTRACT block of every build spec, and have the BUILDER self-check
  `git log --format='%(trailers)'` before worker_done — harvest-side stripping rewrites
  SHAs the manifest already recorded.
- AUTOMATED CHECK: a `git log --format='%(trailers)' <base>..HEAD` assert belongs in the
  integrator's pre-push gate (and possibly floor_guard) — catches trailers before they
  reach origin, not after.
- TOOL ECONOMY: `spawn_worker.sh`'s custom-argv lane needs ORCA_TERMINAL_HANDLE exported
  (unscoped task-list silently returns 0 tasks otherwise → misleading
  `SPAWN=FAILED step=verify-task-ready`). A preflight line in the script would save a
  debugging loop.
- NO-OP STEERING: "One pack only: matt" appeared in every build TASK this run but no worker
  referenced a pack doc — either wire the pack into the spec meaningfully or delete the
  line (instruction budget is finite).

## Prompt / playbook tweaks (fleet-side, optional)

- File a backlog item: review-round budget counts EVIDENCE-layer stickers identically to
  doctrine/code findings — both units parked with green code. A per-axis distinction
  (production-Required vs evidence-Required) with evidence-only repairs allowed past the
  cap under a named coordinator deviation is worth a doctrine discussion — NOT a decision
  this run makes unilaterally (gate-classification: user-challenge class).
- File a backlog item: the reviewer-cap breach at wave 3 was invisible until the final
  report — `worker-list --run` shows review fans; a coordinator habit of checking
  review-units-in-flight BEFORE each verdict-wave dispatch would have caught it.
