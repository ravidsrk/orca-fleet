# Playbook — decompose-dag  (the DECOMPOSE phase)

Recipe: Matt `to-tickets` (tracer-bullet slices) → Orca `spec-decompose` (materialize the DAG).

## Cut tracer-bullet vertical slices

Each slice = a narrow but COMPLETE path through every layer it touches (schema→API→UI→tests),
demoable alone, sized to fit ONE fresh context window (if you can't state its acceptance check in
two sentences, cut smaller), declaring its BLOCKING edges. Name the FOUNDATION set (scaffold, data
layer, seams, test harness) — it serializes; slices parallelize behind it.

Wide mechanical refactors do NOT slice vertically: sequence expand → migrate-in-batches → contract,
each batch a slice keeping CI green. Prefactor first: make the change easy, then make the easy change.

## Materialize the Orca DAG

Per slice in topological order (blockers first, deps must name REAL returned task ids):
`orca orchestration task-create --spec "<slice: goal · exact acceptance check · files it may create ·
hot-files it must NOT touch · worker_done requires an evidence manifest>" --deps '[...]'`.
Record every returned id in the ledger (id ↔ slice table = the run scope liveness-resume needs).

Hot mount-point files (route registry, DI wiring, migrations, barrels) → mark each a merge-chain
(merge-serialization.md): slices touching one share a dependency chain, never run in parallel.

## Verify the DAG before dispatching anything

`task-list --json`: every task present · deps resolve to real ids (the stuck-pending trap —
liveness-resume.md) · no cycles · foundation has no deps on slices · every hot-file chain is a path
not a fan. Five minutes here saves a fleet-wide debugging session.

## Plan skeptic (a fresh worker stresses the decomposition, before commit)

The check above is mechanical (the DAG is well-formed). This one is semantic: a FRESH build-blind
worker stresses the slices against the frozen spec's acceptance criteria and answers four
questions, updating the plan inline before it commits:

- **Orphan criterion** — every acceptance criterion maps to at least one slice? An uncovered
  criterion is a silent scope drop.
- **Gold-plating** — every slice traces to a criterion? A slice no criterion needs is invented
  scope; cut it or surface it as a backlog item.
- **Order** — nothing depends on unbuilt foundation; the build order is dependency-correct.
- **Stub-slices** — each slice is a genuine vertical path, not a stub masquerading as a slice.

This is the plan-time analogue of clean-sweep's skeptic-triage: it catches a bad denominator
before a fleet builds against it.

## Completion

The slice↔task-id table is in the ledger; the DAG's frontier is exactly the foundation; the loop
(runtime coordinator vs manual wave) is declared.

A decomposition is COMMITTED in one of two ways, and which one is the caller's:
- **build mission** (`ship-it`, `clean-sweep`): committed by DISPATCH — the foundation frontier is
  dispatched and the mission drives it to merge. A materialized-but-never-dispatched DAG here is
  just a proposal.
- **prepare-only handoff** (`map-it`): committed by FREEZE — the DAG is materialized, verified
  (the section above), and frozen as the planning mission's terminal artifact for a later build
  mission to dispatch unchanged. Dispatching is explicitly NOT this caller's job; a verified frozen
  DAG is done. A DAG that is neither dispatched nor frozen-for-handoff is the only real "just a
  proposal".
