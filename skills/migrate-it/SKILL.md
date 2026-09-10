---
name: migrate-it
description: >-
  Land a stateful schema or data change across deploys with old and new code valid at every step:
  expand → dual-write → backfill → switch reads → zero-readers → contract, each phase its own
  deployed and baked change, each with a down path that was written AND run, dual-validity proven
  in both directions, and a parity probe (row counts + sampled hashes) GREEN before the old shape
  is dropped. The unit is one migration PHASE of one table or shape. Use when "migrate the
  database", "rename this column safely", "expand/contract migration", "backfill this table",
  "split this table without downtime", "we cannot take downtime for this schema change". Not for
  building a feature slice through one release (ship-it), dependency or framework currency
  (modernize-it), restructuring code behind unchanged behaviour (reshape-it), or a backlog of
  findings (clean-sweep) — those pass the release machine once and revert with a deploy; data does
  not.
license: MIT
compatibility: >-
  HARD dependency: Orca runtime + the orchestration skill (Orca CLI). git + gh. The project's own
  migration runner and a database the fleet can migrate and dump (a schema-dump command is the
  down-path oracle), plus a deploy path per phase and read/write telemetry for the zero-reader
  window. One worker playbook pack per worker (matt or addy) — never two routers in one worker.
metadata:
  proof: doctrine-only
  autonomy: L4
  unit: one migration phase of one table or shape
  state_machine: expand → dual-write → throttled resumable backfill → switch reads → contract
  convergence: data parity holds and zero readers of the old shape remain, across deploys
  ordering: strictly phased — a phase never starts before its predecessor is proven in production
  parking: MIGRATED-WITH-PARKED, or ABANDONED with the expand rolled back
  oracle: data parity between the two shapes plus a zero-old-shape-reader query, never the repo suite
---

# migrate-it — a stateful shape change landed across deploys, nothing ever invalid

You are the **COORDINATOR** of a migration run. The outcome is a schema or data shape moved with
**old and new code valid against the schema at every step**, proven — not a migration file merged.
Thin loop-holder: you plan the phases, dispatch one phase at a time, verify against authoritative
state (the dumped schema, the parity probe, the deploy record), and keep the ledger FILE (your
memory is compacted; the ledger survives). You never write migrations, review, or merge.

Read [ARCHITECTURE.md](../../ARCHITECTURE.md) once. Composes `data-migration` (the phase
contract), `remediate-finding` (each phase is built and closed as one unit), `acceptance-review`
(build-blind review per phase), `completion-audit` (bake and zero-reader criteria are classified by
verification mode, never waved through), `compound-learn`; rides `evidence-manifest` (per phase:
base → head SHA, the down round-trip diff, the parity probe, both dual-validity runs),
`merge-serialization` (the migrations directory is a merge chain), `reviewed-sha-freshness`,
`dispatch-lifecycle`, `liveness-resume`, `ledger-contract`, `attention-budget`,
`gate-classification` (CONTRACT is one-way). Worker TASK pack: one of matt | addy — never
co-mount. The release states each phase passes through are release.md's; this mission runs that
machine once per phase, never once per run.

## Three terminal outcomes

- **MIGRATED** — parity 100% on the frozen table set, old-shape readers zero over the declared
  window with pasted telemetry, the contract PR merged, every phase's down path exercised.
- **MIGRATED-WITH-PARKED** (degraded) — the ladder is complete up to a phase whose bake or
  zero-reader evidence the fleet cannot reach: `CODE_CLOSED` + `VERIFY_AT_SCALE` naming the query
  and the window, or a `needs-human` one-way gate. Never reported as MIGRATED.
- **ABANDONED** — the migration is rolled back down the ladder using the exercised down paths,
  with the state it was returned to receipted. A migration left half-expanded is not a terminal.

## Pipeline

```
SELF-ORIENT → PLAN: freeze the TABLE SET and the phase list per table (one row per phase, with its
  down path), from the surface the code actually reads — a table nobody reads is not in the set,
  and the set never grows mid-run (a new table is the NEXT run).
→ BOOTSTRAP integration BASE (runtime/scripts/preflight.py --base <BASE> --fork-point <sha>;
  BASE ≠ default — dispatch-lifecycle.md).
→ PER PHASE, strictly serial per table (data-migration.md):
    EXPAND[deploy + bake] → DUAL-WRITE[deploy + bake] → BACKFILL (batched, throttled, resumable;
    parity probe) → SWITCH-READS[deploy + bake] → ZERO-READERS window → CONTRACT[separate deploy]
  each phase: build (one unit, one PR against BASE) → down written and RUN (schema dump diff
  empty) → dual-validity both directions → build-blind REVIEW → LAND → deploy → BAKE, then the
  next phase is dispatched. Never two phases of one table in flight.
→ PARITY: re-probe after the last backfill batch and at SWITCH-READS; any mismatch resumes the
  backfill from its cursor and re-probes — it does not restart, and it does not advance.
→ ZERO-READERS: the declared window of telemetry showing no reader of the old shape, pasted.
→ CONTRACT: its own deploy, its own PR, a one-way human gate. Only then is the old shape dropped.
→ VERDICT + `compound-learn`: MIGRATED / MIGRATED-WITH-PARKED / ABANDONED.
```

## Convergence proof (definition of done)

Per phase: the down path was written **and run** — the negative control is up + down followed by a
schema dump whose diff against the pre-up dump is EMPTY, command and diff pasted; old-code-vs-new-
schema and new-code-vs-old-schema both GREEN at the phase head; the parity probe (row counts equal
plus seeded sampled hashes matching) GREEN on the frozen table set; the phase deployed and baked
for its declared window. Terminal: parity 100% on the frozen set, old-shape readers = 0 over the
declared window (telemetry pasted, not summarized), the contract PR merged and the drop verified
against the dumped schema. A phase whose evidence is a worker's assurance is not done: the verifier
re-runs the parity probe at the merged SHA and re-derives the schema diff — it never re-applies a
landed migration.

## Ledger + supervision

Header at T0 per liveness-resume.md: `RUN · COORDINATOR · BASE · FORK_POINT · T0 · SOURCE · WIP`
(SOURCE = the frozen table set + phase count; `WIP: builders=<n> reviewers=<n>` sized to
attention-budget.md — a migration's real WIP is one phase per table, so the cap is usually the
table count, not the builder count). One row per PHASE:

`| task_id | table | phase | DOWN_RUN | DUAL_OK | BUILD_DONE | PR_OPEN | REVIEWED | MERGED | DEPLOYED | BAKED | PARITY | WT_CLEAN | park | evidence |`

Stalls → liveness-resume.md WATCH; a dead coordinator RESUMES from the ledger and the dumped
schema, never from narration — the schema on disk says which phase actually landed.

## Gates

CONTRACT (the drop) is a one-way human gate, always, per gate-classification.md — as is any
irreversible phase declared in its PR body. BASE→default promotion stays out of scope: open the
promotion PR and stop. A bake window the fleet cannot observe is `CODE_CLOSED` + `VERIFY_AT_SCALE`
with the exact query, never an assumed pass.

## Anti-patterns

Renaming or dropping a shape in place ("it's one line") — during the rollout old and new code run
together and one queries a shape that is gone. Merging a phase whose down path exists but was never
run. Shipping the additive step and the code that depends on it in one deploy. A single `UPDATE`
across millions of rows (it locks the table; batch, throttle, resume). Restarting a failed backfill
instead of resuming from its cursor. Declaring parity from row counts alone (equal counts with
wrong values is exactly what the sampled hash exists to catch). Dropping the old shape because
"nothing should read it" without the zero-reader window's telemetry. Two migrations on one table in
flight. Treating a deploy revert as a data revert. Letting the frozen table set grow mid-run.

## Related

`ship-it` (a feature slice through the release machine once — a schema slice inside a wave uses the
same phase contract but keeps ship-it's unit), `modernize-it` (dependency currency; it hands a
data-shape change here explicitly), `reshape-it` (code restructured behind unchanged behaviour —
no data at risk), `clean-sweep` (a findings backlog), `root-cause` (why the data is wrong; this
mission moves it, it does not diagnose it).
