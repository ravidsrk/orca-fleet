# Runtime policy — decision gates (who answers what)

Every decision a fleet hits is classified before anyone answers. Governance is below the model:
policy is enforced, not requested.

## The two runtime gate kinds (do not conflate)

- **Worker gate:** a worker's blocking `ask` → `decision_gate` **message**. Times out (~10 min),
  re-asks under a NEW id. Answer the CURRENT id with `reply --id <msg_id> --body "<answer>"`.
  On CLI fleets this often writes **no** `decision_gates` table row — reply by message id.
- **DAG gate:** coordinator `gate-create --task <id> --question "<text>"` (both flags required)
  → auto-blocks the task; `gate-resolve`
  injects the resolution into the task's next dispatch preamble.

## Live ask ≠ historical unanswered ≠ DAG `blocked`

- **Live worker `ask`:** the worker CLI blocks until reply/timeout; the task usually stays
  `dispatched` (not `blocked`). An ask with **no thread reply** while the unit is still
  dispatched is **always** current inbox work — reply by message id immediately. Do not wait for
  task status `blocked`. Do not use the unread bit alone (`check` marks read on receive).
- **Historical unanswered ask:** unit already terminal, no waiting worker — retained evidence
  that no answer was stored, **not** a reason to stall the fleet.
- **`gate-create`:** task is `blocked` until resolve — true DAG hold.

Recorded gate lifecycle (pending / resolved / unanswered) is not the same as "the coordinator
must act now." Full DAG context: orca-dag-semantics.md.

## Classification (before reading the recommended option)

| Class | Test | Resolver |
|-------|------|----------|
| **Mechanical** | one defensible answer (tooling with a repo precedent, naming, retry-on-transient) | coordinator auto-resolves; append the DECISIONS log (ledger-contract.md) |
| **Taste** | reasonable disagreement, reversible (API shape, copy, structure within spec) | pick recommendation (or Lane B); log DECISIONS; human may veto |
| **One-way** | hard/impossible to reverse or out-of-authority: merge to default, deploy, rollback, deletion, spend, scope change, secret rotation, real credentials | HUMAN ONLY. Never auto-resolved. Never defaulted on timeout. |

## Three lanes (what a unit is allowed to do)

| Lane | When | Action |
|------|------|--------|
| **A — implement** | Safe to ship on testnet/fixtures; reversible code | Full PR-per-unit pipeline |
| **B — draft-and-gate** | Genuine product/brand/policy fork (two defensible directions) | Draft **both** options fully; stop at a one-way human gate; do not pick silently |
| **0 — refuse-and-surface** | Credential provisioning, live money/prod, engine boundary the fleet must not cross | Do not implement; record OPS/Lane-0 item (`CODE_CLOSED` only if code landed and verify is OPS — ledger-contract.md) |

## Pre-build plan gate (irreversible units)

When `build-change.md`'s irreversibility stop-list applies, classification happens **before**
code: the PLAN artifact is the decision surface. Approving "proceed as planned" on reversible
testnet/fixtures → Lane A (mechanical/taste as usual). Approving a hard-to-reverse path →
one-way human. Rejecting → Lane 0 or rewrite the plan. Coding before the gate resolves is a
protocol breach — park the unit and re-dispatch.

## User-challenge (the never-auto class within one-way)

When the fleet's analysis concludes the USER's stated direction should change, that is never
auto-decided. The user's direction is the default; the fleet must make the case for change, name
its blind spots, and the cost if wrong. This is gstack's User-Challenge, adopted verbatim.

## Escalation is honest (session-kind aware)

`ask` is agent-to-agent (worker→coordinator); a terminal handle is not a human. To reach a human:
- interactive session → put the decision to them in-session; record the answer.
- unattended → PARK: ledger HUMAN-queue line + `gate-create` hold; the run continues elsewhere or
  winds down. NEVER label an agent-to-agent message as human approval.

One-way doors override any never-ask preference. The `--admin` merge and BASE→default promotion are
one-way: they require a recorded human grant, always.
