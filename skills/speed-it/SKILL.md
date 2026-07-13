---
name: speed-it
description: >-
  Bring declared user journeys within pre-declared performance budgets, proven by measurement.
  Controlled baseline (measure to a metric contract, not once) → profile the real bottleneck → fix
  PR-per-hotspot with a mandatory before/after → re-benchmark to the metric's statistical contract →
  add CI regression guards, looping until every journey is within budget or parked. Use when "the app
  is slow", "perf sweep", "Core Web Vitals", "get under budget", or an unattended perf-hardening run.
license: MIT
proof: doctrine-only
compatibility: >-
  HARD dependency: Orca runtime + orchestration skill (Orca CLI). git + gh. A real MEASUREMENT path
  (Lighthouse/DevTools for web CWV, or a load/profiler harness). A perf worker playbook (addyosmani
  performance-optimization or gstack benchmark) — one router per worker.
---

# speed-it — every journey within budget, proven by a number

You are the **COORDINATOR**. Unlike a findings mission, here BASELINE MEASUREMENT PRECEDES inventory,
fixes interact systemically, measurements are noisy, and DONE is a STATISTICALLY-DEFINED BUDGET over
journeys — not closure of a finding list. Composes `risk-review` (perf lens), `remediate-finding`,
`runtime-prove`; rides `merge-serialization`, `reviewed-sha-freshness`, `dispatch-lifecycle`,
`liveness-resume`.

## Two terminal outcomes

- **WITHIN-BUDGET** — every critical journey meets its budget on its metric contract's confirmation.
- **OPTIMIZED-WITH-PARKED** (degraded) — all fixable hotspots fixed, ≥1 journey over budget needs an
  infra/architecture change beyond scope or is an inherent-cost tradeoff; parked with a human ref.
  Never reported as WITHIN-BUDGET.

## The measurement contract (declare per metric BEFORE baselining)

Two runs is a smoke minimum, not proof. Field CWV = the metric's percentile (p75) over a window +
sample count. Lab CWV = median of ≥5 runs (report spread) at a pinned throttle/cache/device. Server
p95/p99 = the percentile over ≥N requests at stated concurrency, two independent load runs agree.
Baseline and candidate MUST share source, sample size, and pinned conditions — a lab-vs-field or
warm-vs-cold comparison is not a delta. A number you can't measure to its contract is `unmeasured`
(human-flagged), never a downgraded proxy; never fabricate a metric.

## Pipeline

```
declare metric contracts → BASELINE every journey (to contract) → rank breaches by gap×traffic
  → DIAGNOSE the bottleneck (profile; symptom→cause tree; name the one dominant cause)
  → BOOTSTRAP integration BASE (runtime/scripts/preflight.py --base <BASE>; BASE ≠ default —
    dispatch-lifecycle.md)
  → FIX PR-per-hotspot (before→after mandatory; GUARD: add a CI budget) → build-blind REVIEW
  → RUNTIME-PROVE (runtime-prove: drive the journey at its real entry point — fast but behaviorally
    wrong is a bug, not a win) → LAND
  → RE-BENCHMARK to the contract (a lucky single run is not confirmation) → loop → outcome
```

## Convergence proof

Every journey: within budget confirmed to its metric contract (source, sample, conditions, pasted
numbers) OR parked with a reason. Every fix PR: a measured before→after to its contract, a fresh worker
re-measures a sample. No fabricated metrics (spot-checked). CI budgets added so wins don't rot. A fix
that changes behavior is a bug the review must catch.

## Anti-patterns

Optimizing without a baseline (can't prove a win). One fast run = "fixed" (perf is noisy). Confirming
below the metric's contract. Scattershot micro-opts instead of the profiled bottleneck.

## Related
`clean-sweep` (general findings), `review-it` (per-diff perf lens), `observe` (post-deploy perf watch).
