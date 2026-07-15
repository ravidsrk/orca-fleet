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

Record in the ledger header: `WIP: builders=<n> reviewers=<n>`. Exceeding the cap → hold the
next dispatch until a unit leaves `dispatched` (verify or park), never silently raise the cap.

## Sort the work (do not parallelize judgment)

- **Isolated / machine-verifiable** → background workers (clean-sweep findings, slice builds with
  clear ACs, characterization tests).
- **Judgment-heavy** → serial on the coordinator or a dedicated interactive session (architecture
  forks, foggy diagnosis, one-way product calls). Parallelizing these thrashing the lock.

## Spend the lock only on judgment

Mechanical proof (tests, negative controls, ancestry, reviewed-SHA) is machine-checked via
`evidence-manifest.md`. Batch one-way human gates when several park at once — context-switch cost
dominates. Never spawn more agents to feel busy; throughput equals review+verify throughput.

## Completion

Every dispatch wave respects the recorded WIP; judgment-heavy units are not fanned; the run
report names any WIP override and why.
