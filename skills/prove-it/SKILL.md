---
name: prove-it
description: >-
  Give every critical path a test that dies under a semantics-preserving mutation. Map the untested
  critical surface (coverage × call-graph of the money/auth/data paths), write characterization tests
  that assert real behavior, prove each earns its keep by failing at its assertion under a mutation
  (harness still runnable — a compile break is not proof), and route surfaced bugs to a fix or backlog,
  looping until every confirmed critical path is mutation-audited. Use when "close the test gap",
  "cover the critical paths", "test debt", characterization/mutation testing. Not for flake
  eradication (deflake-it) or building features with tests from the start (ship-it).
license: MIT
proof: doctrine-only
compatibility: >-
  HARD dependency: Orca runtime + orchestration skill (Orca CLI). git + gh; a runnable suite +
  coverage tool. A TDD worker playbook (addyosmani or mattpocock) — one router per worker.
---

# prove-it — a mutation-audited test on every critical path

You are the **COORDINATOR**. Here the work CREATES PROOF where no defect finding necessarily exists;
the denominator is a FINITE CRITICAL SURFACE, done is MUTATION-SENSITIVE coverage of it, and bugs
surfaced during characterization spawn a NESTED remediation loop. Composes `build-change`,
`remediate-finding` (for surfaced bugs), `acceptance-review`, `runtime-prove`; rides
`merge-serialization`, `reviewed-sha-freshness`, `dispatch-lifecycle`, `liveness-resume`,
`evidence-manifest`, `ledger-contract`. Worker TASK pack: one of matt | addy — never co-mount.

## Two terminal outcomes

- **COVERED** — every path on the confirmed critical surface has a merged, mutation-audited test; every
  surfaced bug fixed-with-test.
- **COVERED-WITH-PARKED** (degraded) — all writable paths mutation-audited, ≥1 surfaced bug parked as
  needs-human (load-bearing quirk / behavior-change decision) or a path can't be tested without a human
  decision. Never reported as COVERED.

## Pipeline

```
MAP critical surface (coverage gaps × call-graph of money/auth/data/external-contract entry points;
  uncovered trivial getters are NOT the mission) → HUMAN scope confirm (bounds the mission)
  → BOOTSTRAP integration BASE (runtime/scripts/preflight.py --base <BASE> --fork-point <sha
    recorded in the ledger header at BASE creation>; BASE ≠ default — dispatch-lifecycle.md)
  → CHARACTERIZE waves (build-change): assert REAL expected behavior. Two outcomes:
    · code correct, untested → the test passes; PROVE it with a semantics-preserving MUTATION (flip a
      boundary, negate a condition, zero a return — code still COMPILES, harness still RUNS) that fails
      the targeted assertion. A revert that breaks compile/imports proves source-SHAPE dependence, not
      behavior — does not count. Record each audit in the unit manifest's `metric_contract`
      (mutation, target assertion, harness still runnable — see `evidence-manifest.md` for schema).
    · test reveals a BUG → SURFACED-BUG sub-loop (remediate-finding). Route small clear fixes in-PR;
      route ambiguous / behavior-changing bugs to PARK needs-human or hand to clean-sweep. Never assert
      the buggy behavior as correct.
  → build-blind REVIEW (acceptance-review) → RUNTIME-PROVE (characterization asserts behavior the
    real entry point actually exhibits, not harness-only fiction) → LAND
  → RE-MAP coverage → loop → outcome
```

## Convergence proof

Every critical-surface path: a merged test that fails at its assertion under a semantics-preserving
mutation, harness runnable (mutation-audit recorded in `metric_contract`; spot-audited on a sample).
Every surfaced bug: fixed-with-test, or parked with a reason, or handed to clean-sweep. No assertion
weakened to pass (diff-audit). Coverage before/after pasted — but the pass criterion is the
mutation-audit set, not the percent. Manifest names COVERED or COVERED-WITH-PARKED.

## Ledger + supervision

Header per liveness-resume.md: `RUN · COORDINATOR · BASE · FORK_POINT · T0 · SOURCE · WIP` (`-` if N/A;
SOURCE = critical-surface digest). Rows include Orca task id + path fields (test · mutation · PR ·
disposition). Stalls → WATCH; death → RESUME scoped to header coordinator + ledger task ids,
git-verified.

## Anti-patterns

Chasing coverage percent (100% with tautological asserts proves nothing). A green test whose mutation
passes (insensitive to the behavior — worse than no test). Accepting a compile break as the mutation
proof. Silently asserting a surfaced bug's wrong behavior as correct. Unbounded surface (needs the
confirmed critical list).

## Related
`deflake-it` (test stability), `clean-sweep` (surfaced bugs go there), `ship-it` (build tests into new work).
