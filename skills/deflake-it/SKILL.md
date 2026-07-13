---
name: deflake-it
description: >-
  Eliminate intermittent test failures to a declared confidence contract. Detect flakes by repeat-run
  + CI retry history, diagnose each with a loop that RAISES the failure rate (never a theory), fix the
  root cause and ratchet it red-by-revert, then re-run the whole suite for a consecutive green streak —
  local AND in CI — looping until the streak holds. Retry-wrappers as fixes are banned and grep-checked.
  Use when "kill the flaky tests", "deflake the CI", "flake zero", a flaky/intermittent suite.
license: MIT
compatibility: >-
  HARD dependency: Orca runtime + orchestration skill (Orca CLI). git + gh; a runnable suite. A
  feedback-loop-first debugging playbook (mattpocock diagnosing-bugs or addyosmani debug) — one router
  per worker.
---

# deflake-it — green N times in a row, local and CI

You are the **COORDINATOR**. The unit is an INTERMITTENT FAILURE DISTRIBUTION, not a defect: detection
and proof require REPEATED observations, environment correlation, and a consecutive-green / statistical
contract. Rerun behavior IS the mission, not verification-after-a-fix. Composes `diagnose`, `build-change`,
`remediate-finding` (the finding is a flake; the red-by-revert ratchet is its negative control);
rides `merge-serialization`, `reviewed-sha-freshness`, `dispatch-lifecycle`, `liveness-resume`.

## Two terminal outcomes

- **STABLE** — the full suite passes `{{GREEN_STREAK}}` consecutive runs (default 10), local AND CI,
  with zero flakes and zero retry-wrappers.
- **STABLE-WITH-QUARANTINE** (degraded) — ≥1 flake survives diagnosis with no root cause and is
  quarantined with a human-approved tracking ticket. Never reported as STABLE.

## Pipeline

```
DETECT: run the suite `{{DETECT_RUNS}}` times (parallel, varied seed/order) → per-test flake RATE;
  mine CI retry history (pass-on-retry tests flake in an env local runs don't reproduce — capture even
  at local rate 0). Deterministic N/N failures are BUGS → route to clean-sweep, out of scope.
  → DIAGNOSE (diagnose playbook, adapted): build a loop that RAISES the failure rate (tight loop, under
    load, clock skew, shuffled order, shared-state siblings); classify the taxonomy (order-dependence /
    shared mutable state / real time-or-tz / network / unseeded RNG / resource leak / too-tight timeout
    / async race) → the class dictates the fix.
  → FIX root cause + RATCHET red-by-revert (revert only the fix, show the flake returns at its measured
    rate; restore, show it's gone across a mini-streak) — never `retry(3)` a flake into hiding.
  → close per remediate-finding: PR-per-flake against BASE → build-blind REVIEW → conductor LAND
  → PROVE: full suite `{{GREEN_STREAK}}` consecutive runs, local AND verified in CI (gh run list). ANY
    flake resets the streak to zero and re-enters detection. → loop → outcome
```

## Convergence proof

Every detected flake (local AND CI-only) reaches a terminal state: root-caused + fixed + merged (with a
red-by-revert ratchet) OR quarantined with a human-approved ticket — no "documented and left flaky"
exit. CI-only flakes: the local streak does NOT disprove them; each fixed-and-verified-in-CI (green
across `{{GREEN_STREAK}}` triggers, gh run list pasted) or quarantined. The streak (timestamps +
seeds/orders per run) pasted, local AND CI. Zero retry/rerun wrappers added (grep the diff).

## Anti-patterns

Theorizing before a loop that reproduces at elevated rate. `retry(n)` / `--rerun-failures` as the fix
(hides flakes, poisons the signal). One green run = done. Treating an N/N deterministic failure as a
flake (it's a bug — clean-sweep). Widening a timeout that masks a real race.

## Related
`root-cause` (a single hard intermittent bug), `prove-it` (coverage), `clean-sweep` (deterministic bugs).
