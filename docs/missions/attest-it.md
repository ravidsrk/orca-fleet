# 📋 attest-it — evidence-bound conformance to a frozen standard

> **Autonomy:** L3 (Osmani L0-L5) - conditional autonomy - the human/legal owner disposes of the gaps and the conformance verdict.
> **Proof:** doctrine-only — no recorded run yet; the protocol is mechanism, not yet field-proven.

> Point it at a standard (EU AI Act Art-12/50, SOC 2, NIST SSDF) and a codebase. Come back to an
> auditor-grade verdict: every obligation either satisfied with evidence a fresh session re-derived
> from authoritative state, or named as a GAP parked to a human/legal owner. No control marked
> satisfied on an agent's word.

**Skill:** [`skills/attest-it/SKILL.md`](../../skills/attest-it/SKILL.md) · **Layer:** mission (discoverable) · **Fix authority:** evidence-gathering (`ro`); remediation that lands code routes to `ship-it` / `clean-sweep`

---

## What it does

`attest-it` is the conformance fleet. A **coordinator** freezes a standard at a version, enumerates its
obligations into a DAG, dispatches fresh **workers** to gather the evidence that satisfies each control,
and has an **independent session re-derive** every piece of evidence against authoritative state before
any control is marked satisfied. The output is an audit artifact: `CONFORMANT`, or
`CONFORMANT-WITH-GAPS` with a named gap register.

The unit of work is **one obligation from a frozen `standard@version` catalog** — not a discovered
finding. That is what separates it from [`clean-sweep`](clean-sweep.md) (a discovered backlog),
[`review-it`](review-it.md) (a per-PR verdict), and [`harden-it`](harden-it.md) (an exploit loop). Many
controls need no code change at all — they need evidence, gathered and re-derived.

## When to reach for it

- "Prove SOC 2 compliance with an audit-ready evidence pack."
- "Show EU AI Act Article 12 logging conformance for this high-risk system."
- "Attest NIST SSDF practices across the repo, or tell me the gaps."

**When NOT to reach for it:**

- You want a security exploit → fix → re-attack loop — that is [`harden-it`](harden-it.md).
- You want a merge verdict on one PR — that is [`review-it`](review-it.md).
- You want a discovered backlog closed — that is [`clean-sweep`](clean-sweep.md).

## The pipeline

```mermaid
flowchart TD
    A[standard@version + codebase] --> B[FREEZE the obligation set<br/>enumerate into a DAG · digest-locked]
    B --> C[EVIDENCE per obligation<br/>ro workers · bound to authoritative state]
    C --> D[RE-DERIVE independently<br/>fresh session · deterministic where possible]
    D --> E{Control satisfied?}
    E -->|evidence re-derived| F[VERIFIED]
    E -->|no re-derivable artifact| G[GAP → human/legal owner]
    F --> H{{CONFORMANT}}
    G --> I{{CONFORMANT-WITH-GAPS}}
```

## Terminal outcomes

| Verdict | Meaning | Who acts on it |
|---|---|---|
| `CONFORMANT` | every obligation VERIFIED with independently re-derived evidence | a human/legal owner accepts the attestation |
| `CONFORMANT-WITH-GAPS` | one or more GAPs, each with missing evidence + a named owner | the owner closes the gaps or accepts residual risk (a one-way gate) |

## Human gates

The conformance verdict and any accepted residual gap are **one-way doors** under
[`gate-classification`](../../runtime/gate-classification.md) — a fleet never signs off a standard on a
human/legal owner's behalf. Evidence gathering runs `PROFILE=ro`; remediation that lands code is a
separately authorized `ship-it` / `clean-sweep` run.

## Convergence proof

`attest-it` is done when every obligation in the frozen `standard@version` catalog is accounted for:
the union of unit contracts equals the standard's obligation set (nothing unassigned); each VERIFIED
control carries evidence bound to authoritative state and **independently re-derived** (not the
gatherer's narration); each GAP names its missing evidence and a human/legal owner; and the verdict is
`CONFORMANT` or `CONFORMANT-WITH-GAPS`. No obligation is silently dropped, and the denominator was never
shrunk.

## Composes

Playbooks: [`decompose-dag`](../../playbooks/decompose-dag.md) ·
[`acceptance-review`](../../playbooks/acceptance-review.md)

Runtime policies: [`evidence-manifest`](../../runtime/evidence-manifest.md) ·
[`gate-classification`](../../runtime/gate-classification.md) ·
[`sandbox-policy`](../../runtime/sandbox-policy.md) ·
[`ledger-contract`](../../runtime/ledger-contract.md) ·
[`liveness-resume`](../../runtime/liveness-resume.md)

## Related missions

- [`review-it`](review-it.md) — a per-PR GO/NO-GO verdict, not a standard's obligation set.
- [`harden-it`](harden-it.md) — the security exploit → fix → re-attack loop.
- [`clean-sweep`](clean-sweep.md) — close a discovered backlog; attest-it's denominator is a standard, not a backlog.
- Rides the evidence manifest's [Art-12/50 `provenance` block](../compliance-provenance.md) — the record attest-it attests against.
