# ♿ access-it — WCAG 2.2 conformance over a frozen surface

> **Autonomy:** L4 (Osmani L0-L5) - high autonomy - the deterministic axe oracle is the cheap verification; you own the residual human-AT park and the promotion.

> Point it at a page/flow/component set and a WCAG target. Come back to a surface a deterministic
> oracle certifies clean, every fix proven by a revert-to-violation negative control — and the
> ~30–40% a machine can't judge (screen-reader semantics, cognitive load) named and parked to a
> human with assistive tech, never silently passed.

**Skill:** [`skills/access-it/SKILL.md`](../../skills/access-it/SKILL.md) · **Layer:** mission (discoverable) · **Fix authority:** yes — `PROFILE=rw` fix workers

---

## What it does

`access-it` is the accessibility-conformance fleet. A **coordinator** freezes the surface (the
page/flow/component set × the WCAG 2.2 AA criteria), runs a deterministic oracle (axe-core / Lighthouse)
to enumerate violations, dispatches fresh `rw` **workers** to fix each, and re-verifies that the oracle
goes clean **and** each fix carries a mandatory negative control — revert the fix and the violation
returns. The criteria past the automation ceiling are parked, not assumed.

The unit of work is **one success-criterion violation instance on the frozen surface**. The hard
**~30–40% automation ceiling** is the defining property: axe-core is deterministic but partial, so the
un-automatable criteria (screen-reader semantics, keyboard traps, cognitive load) are a first-class
**human-AT park**, which is what keeps a green oracle run from masquerading as full conformance.

## When to reach for it

- "Bring the checkout flow to WCAG 2.2 AA."
- "Make this component accessible for screen-reader and keyboard users."
- "Section 508 / EAA / ADA conformance sweep over these pages."

**When NOT to reach for it:**

- A bounded per-diff accessibility check on one PR — that is [`review-it`](review-it.md)'s a11y risk lens.
- Attesting a *standard's obligation set* (SOC 2 / EU AI Act) — that is [`attest-it`](attest-it.md);
  access-it's denominator is a rendered surface's violations, not a document's obligations.
- Closing a discovered code backlog — that is [`clean-sweep`](clean-sweep.md).

## The pipeline

```mermaid
flowchart TD
    A[surface + WCAG 2.2 AA target] --> B[FREEZE surface x criteria<br/>digest-locked denominator]
    B --> C[DETECT<br/>axe-core / Lighthouse · violations to a DAG]
    C --> D[FIX — rw workers<br/>remediate-finding · structural items serialized]
    D --> E[RE-VERIFY<br/>oracle clean + revert-to-violation NC]
    E --> F[PARK ceiling criteria<br/>screen-reader / cognitive → human-AT]
    F --> G{{CONFORMANT}}
    F --> H{{CONFORMANT-WITH-MANUAL-PARKED}}
```

## Terminal outcomes

| Verdict | Meaning | Who acts on it |
|---|---|---|
| `CONFORMANT` | *near-unreachable* — only when the frozen surface has no criteria past the ~30–40% automation ceiling (rare); axe-core clean, every criterion covered with a revert-to-violation NC | a human promotes |
| `CONFORMANT-WITH-MANUAL-PARKED` | automatable criteria clean; ceiling criteria parked to a named human-AT reviewer | the human-AT reviewer closes the parked criteria (a one-way gate) |

## Human gates

The residual **human-AT park** is a one-way door under
[`gate-classification`](../../runtime/gate-classification.md): the fleet never declares a
screen-reader/cognitive criterion passing on the oracle's silence. Fix workers run `PROFILE=rw`
([`sandbox-policy`](../../runtime/sandbox-policy.md)); promotion past a degraded terminal is human.

## Convergence proof

`access-it` is done when every criterion in the frozen (surface × WCAG 2.2 AA) denominator is
accounted for: the deterministic oracle is clean across the surface, each automatable criterion is
covered by a fix whose negative control (revert → violation returns) holds, and each ceiling criterion
is PARKED to a named human-AT reviewer with the reason the oracle cannot decide it. The verdict is
`CONFORMANT` or `CONFORMANT-WITH-MANUAL-PARKED`; the denominator was never shrunk to only the
automatable criteria.

## Composes

Playbooks: [`decompose-dag`](../../playbooks/decompose-dag.md) ·
[`remediate-finding`](../../playbooks/remediate-finding.md) ·
[`acceptance-review`](../../playbooks/acceptance-review.md) ·
[`compound-learn`](../../playbooks/compound-learn.md)

Runtime policies: [`evidence-manifest`](../../runtime/evidence-manifest.md) ·
[`sandbox-policy`](../../runtime/sandbox-policy.md) ·
[`merge-serialization`](../../runtime/merge-serialization.md) ·
[`reviewed-sha-freshness`](../../runtime/reviewed-sha-freshness.md) ·
[`dispatch-lifecycle`](../../runtime/dispatch-lifecycle.md) ·
[`liveness-resume`](../../runtime/liveness-resume.md) ·
[`ledger-contract`](../../runtime/ledger-contract.md) ·
[`attention-budget`](../../runtime/attention-budget.md)

## Related missions

- [`review-it`](review-it.md) — the bounded per-diff a11y lens, not a surface sweep.
- [`attest-it`](attest-it.md) — a standard's obligation set, not a surface's rendered violations.
- [`clean-sweep`](clean-sweep.md) — a discovered code backlog; access-it's denominator is a frozen surface × WCAG.
