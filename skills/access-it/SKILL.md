---
name: access-it
description: >-
  Drive a FROZEN page/flow/component set to WCAG 2.2 AA (EAA / ADA / Section 508) conformance: a
  deterministic axe-core oracle clean on the surface plus a mandatory negative control (revert the fix,
  the violation returns), with the hard ~30-40% automation ceiling forcing screen-reader and cognitive
  criteria into a first-class human-AT park. The unit is one success-criterion violation instance on the
  frozen surface. Use when "accessibility", "a11y", "WCAG", "screen reader", "keyboard", "ARIA",
  "axe-core", "Section 508 accessibility", "color contrast". Not for a security exploit loop (harden-it),
  a PR merge verdict (review-it), a discovered backlog (clean-sweep), or standards attestation (attest-it).
license: MIT
proof: doctrine-only
autonomy: L4
compatibility: >-
  HARD dependency: Orca runtime + orchestration skill (Orca CLI). git + gh; a deterministic a11y oracle
  (axe-core / Lighthouse) and a runnable surface. A fix worker playbook (addyosmani, mattpocock, gstack)
  — one router per worker.
---

# access-it — WCAG 2.2 conformance over a frozen surface

You are the **COORDINATOR** of an accessibility conformance run. "Make this surface WCAG 2.2 AA, or name
what only a human can" is a user-facing outcome with a hard automation ceiling: the deterministic
oracle proves what it can, and the ~30-40% it cannot (screen-reader semantics, cognitive load) is a
first-class **human-AT park**, never a silent pass. Composes `decompose-dag` (enumerate violations
into a DAG over the frozen surface), `remediate-finding` (fix each), `acceptance-review` (build-blind
review of each fix), `compound-learn` (retro); rides `evidence-manifest` (each fix carries the axe
result + a revert-to-violation negative control), `sandbox-policy` (`PROFILE=rw`),
`merge-serialization`, `reviewed-sha-freshness`, `dispatch-lifecycle`, `liveness-resume`,
`ledger-contract`, `attention-budget`. Worker TASK pack: one of matt | addy | gstack — never co-mount.

## Terminal outcomes

- **CONFORMANT** — *near-unreachable*: only when the frozen surface has NO success criteria past the
  ~30-40% automation ceiling (rare — most surfaces have screen-reader/cognitive criteria). The oracle
  is clean across the surface, every criterion is covered, and each fix's negative control holds.
- **CONFORMANT-WITH-MANUAL-PARKED** — the automatable criteria are clean, and the criteria past the
  automation ceiling (screen-reader / keyboard-trap / cognitive) are PARKED to a human + assistive-tech
  reviewer, each named with the criterion and why the oracle cannot decide it.

## Pipeline

```
FREEZE the surface: the page/flow/component set × the WCAG 2.2 AA criteria — the denominator, digest-locked.
  → DETECT: run the deterministic oracle (axe-core/Lighthouse); enumerate violations into a DAG.
  → FIX (rw workers, remediate-finding): each violation fixed at its instance; structural items
    (landmarks, heading order) serialized as they are global.
  → RE-VERIFY: the oracle goes clean on the frozen surface AND the mandatory negative control holds —
    revert the fix and the violation returns (evidence-manifest). A fix with no revert-to-red is not proven.
  → PARK: criteria past the automation ceiling routed to a human + assistive-tech reviewer, named.
  → VERDICT: CONFORMANT, or CONFORMANT-WITH-MANUAL-PARKED with the human-AT park register.
```

## Convergence proof (definition of done)

Every success criterion in the frozen (surface × WCAG 2.2 AA) denominator is accounted for: the
deterministic oracle is clean across the surface, each automatable criterion is covered with a fix whose
negative control (revert → violation returns) holds, and each criterion past the automation ceiling is
PARKED to a named human-AT reviewer with the reason the oracle cannot decide it. The verdict is
CONFORMANT or CONFORMANT-WITH-MANUAL-PARKED; the denominator was never shrunk to only the automatable
criteria, and no violation is silently dropped.

## Ledger + supervision

Ledger header at T0 (`ledger-contract.md`) with `WIP: builders=<n> reviewers=<n>` sized to
`attention-budget.md` (fix workers are a mutation wave: ≤3 builders, 1 reviewer per 3 builders, with
at least 1 reviewer). Stalls → `liveness-resume.md` WATCH; death → RESUME, while compaction → write
`CONTEXT HANDOFF` then RESUME (ledger-scoped, git-verified). Fixes land via `merge-serialization` with
`reviewed-sha-freshness`.

## Anti-patterns

Declaring CONFORMANT off a green axe run alone (the ~30-40% ceiling means the oracle's silence is not
proof — the un-automatable criteria must be parked, not assumed passing). Shrinking the denominator to
only what axe checks (the frozen surface × WCAG set is the denominator). A fix with no revert-to-violation
negative control (a green oracle over reverted markup proves nothing). Confusing access-it with the
per-diff accessibility lens in `review-it`, or with `attest-it` (a standard's obligation set, not a
surface's rendered violations).

## Related

`review-it` (a bounded per-diff a11y lens, not a surface sweep), `attest-it` (standard-obligation
conformance, not rendered violations), `clean-sweep` (a discovered code backlog); `sandbox-policy`
(rw fix workers), `evidence-manifest` (the revert-to-violation negative control each fix carries).
