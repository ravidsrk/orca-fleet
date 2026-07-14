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

## Lifecycle state ≠ blocking effect

A gate's recorded status (pending / resolved / unanswered) is not the same as "the fleet is
blocked." An unanswered `ask` proves only that no answer was retained — it is a **current**
blocker only while its named task is `blocked` (or you parked it as a one-way human hold). Do
not stall the whole run waiting on historical unanswered asks after the unit completed. Full
DAG context: orca-dag-semantics.md.

## Classification (before reading the recommended option)

| Class | Test | Resolver |
|-------|------|----------|
| **Mechanical** | one defensible answer (tooling with a repo precedent, naming, retry-on-transient) | coordinator auto-resolves, AUDITED (a ledger line: gate · mechanical · answer · why) |
| **Taste** | reasonable disagreement, reversible (API shape, copy, structure within spec) | coordinator picks the recommendation, BATCHES to one decision-ready brief; work continues; human can veto |
| **One-way** | hard/impossible to reverse or out-of-authority: merge to default, deploy, rollback, deletion, spend, scope change, secret rotation | HUMAN ONLY. Never auto-resolved. Never defaulted on timeout. |

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
