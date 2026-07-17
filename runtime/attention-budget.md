# Runtime policy — attention budget (orchestration tax)

Starting agents is cheap; closing the loop is not. Human judgment is the serial bottleneck
(Amdahl / GIL of the fleet). Scale the fleet to **verification capacity**, not the UI's spawn
limit. Merge serialization (`merge-serialization.md`) is consumer-side backpressure; this policy
is producer-side.

## WIP caps (defaults — override in the ledger header if measured)

| Class | Concurrent builders | Concurrent build-blind reviewers | Notes |
|-------|---------------------|----------------------------------|-------|
| Mutation wave (ship / sweep / harden / …) | ≤ 3 | ≤ 1 per 3 builders (min 1) | Match the human or conductor review rate |
| Report-only (review-it axes) | n/a | ≤ 4 axis workers | Axes stay isolated; cap total terminals |
| Planning (map-it research) | ≤ 3 research workers | n/a | Decision tickets stay one-at-a-time HITL |

`WIP: builders=<n> reviewers=<n>` is a required ledger-header field, written at T0 with the
wave plan sized to it (liveness-resume.md) — a cap recorded nowhere was never a cap. Exceeding
it → hold the next dispatch until a unit leaves `dispatched` (verify or park), never silently
raise it.

The cap counts live PANES, not tasks: a doctor respawn's original pane counts against the cap
until its closure is verified by pane read. Heartbeat false negatives spawn dual writers — the
2026-07-15 chimely run planned a 4-builder wave and peaked at 5 builder panes this way.

Evidence level: ASSERTED. These defaults come from one field run (2026-07-15 chimely) and its
dual-writer post-mortem, not a measured curve — no published methodology for sizing fleet
concurrency to verification capacity exists anywhere yet. They are the convention until the
WIP-curve protocol below replaces them with cited run data.

## Sort the work (do not parallelize judgment)

- **Isolated / machine-verifiable** → background workers (clean-sweep findings, slice builds with
  clear ACs, characterization tests).
- **Judgment-heavy** → serial on the coordinator or a dedicated interactive session (architecture
  forks, foggy diagnosis, one-way product calls). Parallelizing these thrashing the lock.

## Spend the lock only on judgment

Mechanical proof (tests, negative controls, ancestry, reviewed-SHA) is machine-checked via
`evidence-manifest.md`. Batch one-way human gates when several park at once — context-switch cost
dominates. Never spawn more agents to feel busy; throughput equals review+verify throughput.

## The WIP-curve protocol (how a cap graduates from asserted to measured)

Every fleet run records, per dispatch wave, one row in its run report under `docs/runs/`:

| Metric | Definition |
|----------------------|--------------------------------------------------------------------|
| WIP setting          | the ledger-header `WIP: builders=<n> reviewers=<n>` the wave ran at |
| Builder throughput   | units reaching verified CLOSED per hour of wave wall-clock          |
| Verification latency | median and max `worker_done` → verified-or-parked, per unit         |
| Rework rate          | share of units bounced by evidence-manifest.md §2 (re-dispatch / SUSPECT) |
| Freshness violations | reviews voided by `reviewed_sha != head_sha` (reviewed-sha-freshness.md) |

After ≥3 runs at differing WIP settings, plot throughput and rework against WIP and revise the
caps table citing the run reports. Negative data counts — "cap 4 broke review freshness twice"
is a publishable point. A cap revised without a cited report is still ASSERTED.

## Completion

Every dispatch wave respects the recorded WIP; judgment-heavy units are not fanned; the run
report names any WIP override and why, and carries the WIP-curve protocol's per-wave row.
