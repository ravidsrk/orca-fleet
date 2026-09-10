# Playbook — data-migration  (expand → dual-write → backfill → switch → contract, phase by phase)

Recipe: Addy `deprecation-and-migration` expand/contract schema rules + the matt expand–contract
slicing and the gstack data-migration review lens. The unit is ONE phase of ONE table or shape — a
deploy-gated step, not a slice. Data is the one thing a reverted deploy does not roll back, so the
rule is absolute: **never change a shape in place; old and new code must both be valid against the
schema at every step**. `migrate-it` runs a table through the whole ladder; a single-phase schema
slice inside a build wave runs the same phase contract.

## The phase ladder (each phase is its own deploy)

```
EXPAND        add the new column/table/index, nullable, beside the old one   [deploy + bake]
DUAL-WRITE    the app writes BOTH shapes on every insert/update              [deploy + bake]
BACKFILL      copy old → new for existing rows, batched + throttled          [job, resumable]
SWITCH-READS  reads move to the new shape, writes stay dual                  [deploy + bake]
ZERO-READERS  telemetry shows no reader of the old shape over the window     [observation]
CONTRACT      stop writing the old shape, then DROP it in a separate deploy  [one-way, human]
```

Additive first, destructive last and alone. Adds are safe in any deploy; drops and renames get
their own deploy AFTER no code references the old shape. A phase that ships two rungs at once
("add the column and start using it") is the coupling this playbook exists to prevent: during the
rollout window old and new code run together and one of them queries a shape that is not there.

## `down` is written AND run before the phase merges

A migration with no exercised down path is a deploy that cannot be reversed. Per phase, before the
PR is mergeable: run `up`, then `down`, then dump the schema and diff it against the pre-`up` dump
— **the diff must be empty**. Paste the command and the empty diff into the manifest; a `down` that
merely exists in the file is not evidence. A genuinely irreversible phase (data destroyed) is
declared irreversible in the PR body and becomes a one-way human gate, never a silent exception.

## Dual-validity, proven both directions

Per phase, two checks, both green, both pasted:

- **old code vs new schema** — the pre-phase application revision run against the migrated schema.
- **new code vs old schema** — the phase's application revision run against the un-migrated schema
  (what a rollback lands on).

A phase whose new code needs the new shape to boot has failed dual-validity: split it.

## Index and lock rules

Large indexes are built without blocking writes (Postgres `CREATE INDEX CONCURRENTLY`, and its
engine-specific equivalents — name the engine and the mechanism in the ledger). Adds are nullable
with no default rewrite where the engine rewrites the table for one. No `ALTER` that takes an
exclusive lock on a hot table inside a deploy step; that is its own throttled operation with a
stated lock-time budget and an abort rule.

## Backfill: batched, throttled, resumable

The backfill is a job, not a migration file: a single `UPDATE` over millions of rows locks the
table. It processes a bounded batch by an ordered key, records the last committed key as its
resume cursor, sleeps a throttle between batches, and watches replica lag or the equivalent
saturation signal — over the ceiling, it backs off, it does not power through. A failed batch
**resumes from the cursor; it never restarts** — a restart re-does completed work and, on a
non-idempotent copy, corrupts what it already wrote. Every write is idempotent so a re-run of a
batch is a no-op.

## Parity probe (the phase oracle)

Parity is a probe, not an opinion. Its shape, run at the phase head and pasted:

```
rows_old=<n> rows_new=<n>            equal on the frozen table set
sample=<k rows, seeded, ordered>     hash(old_shape) == hash(new_shape) per sampled row
mismatches=<list or empty>           any mismatch = phase RED, backfill resumes
```

The sample is seeded and re-derivable so a verifier can re-run it, and the sampled hash covers the
transformed value, not just presence. Parity is re-probed after the LAST backfill batch and again
at SWITCH-READS.

## Cutover is decoupled from the deploy

Where the read switch is risky, it moves behind a flag so the cutover is a config change, not a
release: flip, watch, flip back. The flag's removal is its own later change. Bake windows and the
zero-reader window need production telemetry the fleet may not have — where it does not, the phase
merges `CODE_CLOSED` with a `VERIFY_AT_SCALE` item naming the exact query and the window, never a
claimed green.

## Completion (per phase)

The phase is one deployable change; `down` was written, run, and produced an empty schema diff;
old-code-vs-new-schema and new-code-vs-old-schema are both green; the backfill (if this phase) ran
to its cursor end with parity GREEN on the frozen table set; index and lock rules are named for the
engine; the ZERO-READERS window has pasted telemetry or is parked; CONTRACT is a separate deploy
behind a human gate. Two phases of the same table are never in flight at once.
