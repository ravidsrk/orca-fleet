---
name: modernize-it
description: >-
  Bring a dependency / framework / platform surface current, safely — CI green at every merge.
  Inventory outdated + advisories with reachability triage → order by a compatibility graph → upgrade
  one dep or coherent group per PR, adapting call sites (code-level expand/migrate/contract) to get off
  old majors while keeping CI green → re-inventory until every major is current or pinned-with-a-reason.
  Use when "update the dependencies", "upgrade everything", "framework migration", "get off the old
  major", or an unattended dependency-currency run. Not for stateful DB schema/data migration across
  deploys (hand that to ship-it) or advisory exploit proof (harden-it).
license: MIT
proof: doctrine-only
compatibility: >-
  HARD dependency: Orca runtime + orchestration skill (Orca CLI). git + gh; the package manager + a
  green CI baseline. addyosmani deprecation-and-migration playbook — one router per worker.
---

# modernize-it — every major current or parked, CI green the whole way

You are the **COORDINATOR**. The unit is a COMPATIBILITY GRAPH node, not a finding: ordering,
ecosystem grouping, lockfile contention, code-level adaptation, and rollback constraints dominate —
PR-per-outdated-package is often actively WRONG. Composes `remediate-finding`, `acceptance-review`,
`risk-review` (data-migration lens as a REVIEW SIGNAL, not an execution engine), `runtime-prove`;
rides `merge-serialization`, `reviewed-sha-freshness`, `dispatch-lifecycle`, `liveness-resume`,
`evidence-manifest`, `ledger-contract`. Worker TASK pack: addy — never co-mount a second router.

Scope boundary: this mission owns DEPENDENCY/FRAMEWORK CURRENCY (bump → adapt call sites → CI green).
STATEFUL DB schema/data migration across deploys is a different unit, state machine, and proof — hand
a brief to a SEQUENCE of ship-it runs, one release each: (1) expand, (2) dependent upgrade +
migrate-in-batches, (3) contract. The upgrade is stage (2), never after contract. Never run a
cross-deploy data migration inside a currency loop. Details: docs/missions/modernize-it.md.

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
  → BOOTSTRAP integration BASE (runtime/scripts/preflight.py --base <BASE> --fork-point <sha
    recorded in the ledger header at BASE creation>; BASE ≠ default — dispatch-lifecycle.md)
  → order: security-critical-reachable → patch/minor (batch coherent groups) → majors (one per PR)
  → UPGRADE waves (one dep/coherent-group per PR: bump → adapt call sites, adding code-level
    deprecation shims / dual-run APIs where a major needs them → CI GREEN is the gate; lockfile
    regenerated not hand-edited; verify provenance on registry/maintainer change)
  → FORCED-MIGRATION CHECK (risk-review data-migration lens): if an upgrade forces a stateful DB
    schema/data change, do NOT run it here — open a staged ship-it handoff brief:
    (1) expand release, (2) this dep upgrade + migrate-in-batches, (3) contract only after (2) is
    deployed and stable. Parking the upgrade "behind the whole sequence" is wrong (would contract
    first).
  → build-blind REVIEW (acceptance-review) → RUNTIME-PROVE (drive real entry points — green CI misses
    lazy imports and env-dependent init) → LAND
  → RE-INVENTORY → loop → outcome
```

## Convergence proof

Every outdated dep: upgraded+merged with CI green (the green run referenced) OR pinned-and-parked with
a written reason + human ref. Every merge kept CI green (check the merge commits' checks — a red
pipeline never landed). Every upgrade that FORCED a stateful DB migration is handed off to ship-it with
a brief and its dependent upgrade parked behind that handoff — never silently run inside this loop.
Advisory scan re-run clean (or each remaining one parked with reachability rationale). Final inventory
pasted. Manifest names CURRENT or CURRENT-WITH-PINNED.

## Ledger + supervision

Header per liveness-resume.md: `RUN · COORDINATOR · BASE · FORK_POINT · T0 · SOURCE` (`-` if N/A;
SOURCE = inventory digest). Rows include Orca task id + dep/group fields (target · PR · CI · pin/
handoff). Stalls → WATCH; death → RESUME scoped to header coordinator + ledger task ids, git-verified.

## Anti-patterns

`audit fix --force` / mass-bump. Running a cross-deploy DB schema/data migration inside a currency loop
(no deploy states here — hand it to ship-it). Rename-in-place code migrations (breaks dual-running
deploys). Landing a red CI "to fix next PR". Bumping a major without its changelog. Dropping a compat
shim without a gate.

## Related
`ship-it` (owns the deploy states a forced stateful DB migration needs), `clean-sweep`, `harden-it`
(advisory exploit proof), `review-it` (data-migration lens as a per-diff review).
