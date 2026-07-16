# Playbook — compound-learn  (REFLECT: capture gotchas for the next session)

Recipe: Orchestra / Factory "Retro" + ETH Zurich finding (LLM-written AGENTS.md hurts; human-
curated helps). After a mission reaches a terminal state, propose durable learnings — never
auto-merge them into the target repo's agent context.

## When (mission REFLECT / final report)

Run once per mission close (ship-it REFLECT, clean-sweep final report, harden-it after CLEAN /
HARDENED-WITH-OPEN-ITEMS). Skip if the run produced zero merged units and zero parked learnings.

## Produce a proposal, not a merge

Write `docs/reports/<run-id>/REFLECTION.md` (or the target repo's equivalent under its docs/):

```
## Surprises
- <what the fleet learned the hard way this run>

## Proposed AGENTS.md / GOTCHAS appends (HUMAN MUST APPROVE EACH LINE)
- STYLE: …
- GOTCHAS: …
- ARCH_DECISIONS: …
- TEST_STRATEGY: …

## Prompt / playbook tweaks (fleet-side, optional)
- <one improvement to a TASK preamble — file a backlog item, do not edit orca-fleet from here>
```

Rules:
- Prefer the target's existing context file (`AGENTS.md`, `CLAUDE.md`, `docs/GOTCHAS.md`) —
  never invent a second competing file if one exists.
- Keep proposals short (≤ 8 bullets total). Vague "be careful" lines are noise — drop them.
- **NEVER** let a worker `git add` / commit / push into `AGENTS.md` (or equivalent) without a
  recorded human approve of the exact lines. Auto-written agent rules are a known negative.
- Taste-class merges of approved lines may proceed after the human says yes; one-way if the
  repo treats agent-context as protected.

## Completion

REFLECTION.md exists beside the run report; every proposed line is either human-approved and
landed, explicitly rejected, or listed in the human-owed queue. No silent AGENTS.md mutation.
