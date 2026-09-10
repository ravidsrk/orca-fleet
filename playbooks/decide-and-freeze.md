# Playbook — decide-and-freeze  (the SPEC phase)

Recipe: Matt `grilling` + `to-spec` + `domain-modeling`. Turn intent into a FROZEN spec that is the
canonical fixed point for every downstream ticket, review, and acceptance test.

## Entry contract (two shapes, then one pipeline)

- **Input already frozen** (docs/spec handed in): VALIDATE it — load-bearing external deps are real
  and installable (research, don't assume), acceptance criteria are testable, boundaries explicit —
  then skip to `decompose-dag`. No grill.
- **Input is intent/draft**: run the grill below, then freeze.

## The grill (interactive; HITL leak if fanned to a worker)

On the coordinator terminal, run `grilling` + `domain-modeling` — **round by round**, not
question-by-question: ask the WHOLE frontier in one round, one bold-titled question + a
RECOMMENDED answer each (upstream format: ❓ question, ➡️ recommendation), so a taste-class run can
auto-pick per `gate-classification.md` and a human answers in one pass. After each round, resolve
what the answers sharpened and ask the next frontier; facts that live in the codebase are
dispatched to a non-blocking fact-finder between rounds — never asked, never blocking the round.
**The join rule:** a question whose answer depends on an outstanding fact-finder stays OPEN until
that dispatch returns, and the freeze never happens with fact dispatches outstanding — independent
facts run concurrently, dependent decisions join on them.
- Sharpen overloaded terms against a `CONTEXT.md` glossary (account = Customer or User?); an ADR only
  when hard-to-reverse ∧ surprising ∧ a real trade-off.
- Every DECISION goes to the human. Never answer the human's side.

## Seam-first spec

Before writing the spec, sketch the TEST SEAMS — prefer existing seams, the highest seam, the fewest
possible (ideal = 1). The test surface is decided before the spec, not after.

## Freeze (human gate #1)

Publish the spec: objectives, acceptance criteria per capability, boundaries (explicit NOT-in-scope),
test strategy, seam list. The human confirms → FROZEN. No re-open of frozen scope without a backlog
entry.

## Completion (checkable + exhaustive)

Every intent has an objective; every capability has ≥1 testable acceptance criterion; the seam list
is confirmed; boundaries name what is out; the human freeze is recorded. A spec with a capability
lacking a testable criterion is NOT frozen.
