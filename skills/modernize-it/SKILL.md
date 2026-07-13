---
name: modernize-it
description: >-
  Bring a dependency / framework / platform surface current, safely — CI green at every merge.
  Inventory outdated + advisories with reachability triage → order by a compatibility graph → upgrade
  one dep or coherent group per PR, adapting call sites (code-level expand/migrate/contract) to get off
  old majors while keeping CI green → re-inventory until every major is current or pinned-with-a-reason.
  Use when "update the dependencies", "upgrade everything", "framework migration", "get off the old
  major", or an unattended dependency-currency run. Stateful DB schema/data migration across deploys
  (backfills, destructive contracts) is a distinct mission — handed to ship-it, not run here.
license: MIT
proof: doctrine-only
compatibility: >-
  HARD dependency: Orca runtime + orchestration skill (Orca CLI). git + gh; the package manager + a
  green CI baseline. addyosmani deprecation-and-migration playbook — one router per worker.
---

# modernize-it — every major current or parked, CI green the whole way

You are the **COORDINATOR**. Here the unit is a COMPATIBILITY GRAPH node, not a finding: ordering,
ecosystem grouping, lockfile contention, code-level adaptation, downstream-user churn, and rollback
constraints dominate — PR-per-outdated-package is often actively WRONG. Composes `remediate-finding`
(adapted), `risk-review` (data-migration lens as a REVIEW SIGNAL that flags a forced schema change,
not an execution engine for it), `runtime-prove`; rides `merge-serialization`,
`reviewed-sha-freshness`, `dispatch-lifecycle`, `liveness-resume`.

Scope boundary (the mission-identity line): this mission owns DEPENDENCY/FRAMEWORK CURRENCY —
bump → adapt call sites → CI green. STATEFUL DB schema/data migration across deploys (expand/migrate/
contract over the release state machine, backfills, destructive contracts, tested rollback) is a
DIFFERENT mission: a different unit (a data transition, not a package), a different state machine
(temporally-separated deploys, not per-PR merges), and a different proof (deployed compatibility +
completed backfill, which needs the deploy states only `ship-it` owns). When a dependency upgrade
FORCES such a migration, modernize-it flags it and hands the migration to `ship-it`; it never runs a
cross-deploy data migration inside a currency loop.

## Two terminal outcomes

- **CURRENT** — every dep on a current supported version, zero reachable unaddressed advisories.
- **CURRENT-WITH-PINNED** (degraded) — all upgradable deps current, ≥1 pinned-and-parked (breaking
  upstream / dropped platform / unresolved conflict) with a human ref. Never reported as CURRENT.

## "Current supported" authority (record it — registry-latest is NOT the truth)

The target is the version the PROJECT supports, by: an explicit project constraint (engines/peerDeps/
support policy), then the dependency's own published support/EOL policy (LTS/security window), then
registry-latest only when neither exists. A dep on a still-supported older major is CURRENT.

## Pipeline

```
INVENTORY (outdated + advisories; read the CHANGELOG not the version delta; reachability triage —
  dev-only/unreachable transitive is lower priority; never `audit fix --force`)
  → order: security-critical-reachable → patch/minor (batch coherent groups) → majors (one per PR)
  → UPGRADE waves (one dep/coherent-group per PR: bump → adapt call sites, adding code-level
    deprecation shims / dual-run APIs where a major needs them → CI GREEN is the gate; lockfile
    regenerated not hand-edited; verify provenance on registry/maintainer change)
  → FORCED-MIGRATION CHECK (risk-review data-migration lens): if an upgrade forces a stateful DB
    schema/data change, do NOT run it here — open a handoff brief and route the migration to ship-it
    (it owns the deploy states expand/migrate/contract needs); park the dependent upgrade behind it
  → build-blind REVIEW → RUNTIME-PROVE (runtime-prove: drive the app's real entry points — a green
    CI misses runtime-only breakage like lazy imports and env-dependent init) → LAND
  → RE-INVENTORY → loop → outcome
```

## Convergence proof

Every outdated dep: upgraded+merged with CI green (the green run referenced) OR pinned-and-parked with
a written reason + human ref. Every merge kept CI green (check the merge commits' checks — a red
pipeline never landed). Every upgrade that FORCED a stateful DB migration is handed off to ship-it with
a brief and its dependent upgrade parked behind that handoff — never silently run inside this loop.
Advisory scan re-run clean (or each remaining one parked with reachability rationale). Final inventory
pasted.

## Anti-patterns

`audit fix --force` / mass-bump. Running a cross-deploy DB schema/data migration inside a currency loop
(no deploy states here — hand it to ship-it). Rename-in-place code migrations (breaks dual-running
deploys). Landing a red CI "to fix next PR". Bumping a major without its changelog. Dropping a compat
shim without a gate.

## Related
`ship-it` (owns the deploy states a forced stateful DB migration needs), `clean-sweep`, `harden-it`
(advisory exploit proof), `review-it` (data-migration lens as a per-diff review).
