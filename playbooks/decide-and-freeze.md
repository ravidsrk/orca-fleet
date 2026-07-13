# Playbook — decide-and-freeze  (the SPEC phase)

Recipe: Matt `grilling` + `to-spec` + `domain-modeling`. Turn intent into a FROZEN spec that is the
canonical fixed point for every downstream ticket, review, and acceptance test.

## Entry contract (two shapes, then one pipeline)

- **Input already frozen** (docs/spec handed in): VALIDATE it — load-bearing external deps are real
  and installable (research, don't assume), acceptance criteria are testable, boundaries explicit —
  then skip to `decompose-dag`. No grill.
- **Input is intent/draft**: run the grill below, then freeze.

## The grill (interactive; HITL leak if fanned to a worker)

On the coordinator terminal, run `grilling` + `domain-modeling`:
- One question at a time; attach a RECOMMENDED answer to each; walk the decision tree resolving
  dependencies one-by-one.
- **Facts vs decisions:** if a fact can be found in the codebase, look it up — do not ask. Every
  DECISION goes to the human. Never answer the human's side.
- Sharpen overloaded terms against a `CONTEXT.md` glossary (account = Customer or User?); an ADR only
  when hard-to-reverse ∧ surprising ∧ a real trade-off.

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
