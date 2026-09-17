# REFLECTION — prove-it campaign self-test 2026-09-16 (compound-learn)

Proposal only — no line below has been merged into any agent-context file, and
none may land without a recorded human approve of the exact lines.

## Surprises

- Traced coverage reads 0% for a module with 32 passing contract tests
  (`guard_text.py`, subprocess-exercised). The mission's `coverage × call-graph`
  intersection is the only thing standing between that artifact and a bogus
  "untested surface" claim — and the `×` needs test-file inspection, not just
  a second coverage number.
- `reviewer_mode` is machine-required even when the review leg is waived
  (dark-eligible): a solo run with no arranged second context cannot go GREEN
  at all, not merely "without a review". The field, not the leg, is the solo
  blocker.
- A two-phase headless review (blind expectation call → judgment call, both
  prompts+replies retained) satisfies blind-fix-first with single-shot CLIs —
  no interactive session needed.

## Proposed AGENTS.md / GOTCHAS appends (HUMAN MUST APPROVE EACH LINE)

- GOTCHAS: coverage.py traces the parent process only — a 0% module exercised
  via subprocess (guard_text.py: 32 tests, 0%) is tested; MAP must intersect
  coverage with test-file inspection before naming a gap.
- GOTCHAS: `reviewer_mode` has no honest solo value — arrange a blind
  headless second context (two-phase: expectation, then judgment; retain both
  prompts+replies) or record RED; never self-certify a mode.
- GOTCHAS: the recorder truncates its artifact at start — a GREEN re-record
  goes to a FRESH artifact file, never over the RED transcript it supersedes.
- GOTCHAS: a test-adding unit trips badge freshness — `gen-badges.py` + a
  separate badge commit (outside the unit pair) before run-close validation.
- TEST_STRATEGY: stash-record-pop stages the binding record's clean tree
  (fingerprint-before-run makes it sound) — no second worktree needed for a
  solo unit.
- NAVIGATION: the oracle-scope tail below the kind gate (`verify.py`
  997/1003/1005/1015/1024 + diff-grammar raises) is the next proving ground —
  one single-criterion wave per gate, PF-3's shape as the template.

## Prompt / playbook tweaks (fleet-side, optional)

- Backlog item (not filed from here — no issue access claimed): consider a
  worked solo-review example in `acceptance-review.md` (two-phase headless
  construction + retention layout), so the next solo run copies a shape
  instead of re-deriving L2.
