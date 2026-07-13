---
name: review-it
description: >-
  Produce a trusted, read-only, SHA-bound verdict on a PR or branch — no fixing authority. Acceptance
  review (standards, frozen-spec compliance, test-adequacy) always; scope-triggered risk lenses
  (security, performance, accessibility, data-migration) when the change surface warrants. Findings
  quote their motivating line, carry severity, and are bound to the reviewed SHA. Use when "review this
  PR", "review matrix", "is this ready to merge", a pre-merge quality/permission gate. Report-only — it
  never edits code (fixing is ship-it / clean-sweep).
license: MIT
compatibility: >-
  HARD dependency: Orca runtime + orchestration skill (Orca CLI). git + gh. Review worker playbooks
  (mattpocock code-review, addyosmani specialists, gstack review army) — one router per worker.
---

# review-it — a read-only, SHA-bound verdict

You are the **COORDINATOR** of a REPORT-ONLY review. "Produce a trusted verdict without modifying code"
is a user-facing outcome, a PR gate, and a PERMISSION BOUNDARY — this mission has no fix authority; a
finding that wants a fix routes to ship-it or clean-sweep. Composes `acceptance-review`, `risk-review`;
workers are `PROFILE=ro`.

## Pipeline

```
PIN the fixed point (a SHA / PR; non-empty `git diff <fp>...HEAD`) → identify the spec source
  → ACCEPTANCE-REVIEW (always): standards + spec + test-adequacy, isolated parallel axes, no cross-rerank
  → RISK-REVIEW (scope-gated): dispatch security/perf/a11y/data-migration only when the diff triggers
    them; NEVER_GATE security + data-migration
  → AGGREGATE: findings side-by-side per axis, each quoting its motivating line, with severity; the
    anti-FP gate (a finding that can't quote its line drops to an appendix); multi-axis same-line = boost
  → VERDICT bound to the reviewed SHA
```

## Convergence proof (definition of done)

A verdict at a named fixed point: every axis reported (acceptance always; risk lenses run or recorded
gate-off), no cross-axis rerank, every finding quotes its line and names its severity, the whole is
bound to `reviewed_sha`. The verdict is GO / NO-GO (any Critical → default NO-GO) with the worst issue
per axis. No code was modified (permission boundary held).

## Anti-patterns

Fixing anything (this is report-only — route fixes out). Reranking across axes (masks one axis with
another). A finding with no quoted line treated as high-confidence. Running risk lenses on a diff that
doesn't trigger them (noise) — or gating off security/data-migration (their value is the miss).

## Related
`ship-it` / `clean-sweep` (act on the verdict), `harden-it` (full security loop beyond a per-diff lens).
