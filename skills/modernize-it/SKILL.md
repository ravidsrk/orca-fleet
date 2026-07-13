---
name: modernize-it
description: >-
  Bring a dependency / platform surface current, safely — CI green at every merge. Inventory outdated
  + advisories with reachability triage → order by a compatibility/migration graph → upgrade one dep
  or coherent group per PR keeping CI green → run framework/DB migrations via expand/migrate/contract
  with tested down-paths and human-gated destructive contracts → re-inventory until every major is
  current or pinned-with-a-reason. Use when "update the dependencies", "upgrade everything", "framework
  migration", "get off the old major", or an unattended dependency-currency run.
license: MIT
compatibility: >-
  HARD dependency: Orca runtime + orchestration skill (Orca CLI). git + gh; the package manager + a
  green CI baseline. addyosmani deprecation-and-migration playbook — one router per worker.
---

# modernize-it — every major current or parked, CI green the whole way

You are the **COORDINATOR**. Here the unit is a COMPATIBILITY/MIGRATION GRAPH node, not a finding:
ordering, ecosystem grouping, lockfile contention, expand/migrate/contract, downstream-user churn, and
rollback constraints dominate — PR-per-outdated-package is often actively WRONG. Composes
`remediate-finding` (adapted), `risk-review` (data-migration lens), `runtime-prove`.

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
    → framework/DB migrations (their own lane, expand/migrate/contract)
  → UPGRADE waves (one dep/coherent-group per PR: bump → fix call sites → CI GREEN is the gate;
    lockfile regenerated not hand-edited; verify provenance on registry/maintainer change)
  → MIGRATION lanes (risk-review data-migration: expand → migrate-in-batches → contract in a SEPARATE
    later PR; every migration a tested `down`; destructive contract = one-way human gate)
  → build-blind REVIEW → LAND → RE-INVENTORY → loop → outcome
```

## Convergence proof

Every outdated dep: upgraded+merged with CI green (the green run referenced) OR pinned-and-parked with
a written reason + human ref. Every merge kept CI green (check the merge commits' checks — a red
pipeline never landed). Migration lanes: expand and contract are SEPARATE merged PRs; every DB
migration has a tested down; destructive contracts have their gate ref. Advisory scan re-run clean (or
each remaining one parked with reachability rationale). Final inventory pasted.

## Anti-patterns

`audit fix --force` / mass-bump. Rename-in-place migrations (breaks dual-running deploys). Landing a red
CI "to fix next PR". Bumping a major without its changelog. Dropping a compat shim without a gate.

## Related
`clean-sweep`, `harden-it` (advisory exploit proof), `review-it` (data-migration lens).
