# Playbook — acceptance-review  (REVIEW: does it do the right thing, right?)

Recipe: Matt `code-review` two-axis (isolated) + gstack review-army dispatch mechanics. Always-on for
any non-trivial diff. Build-blind: the reviewer is a FRESH session that did not write the code.

## The two axes (isolated parallel sub-agents, no cross-rerank)

- **Standards:** repo-documented standards (paste the files) + the Fowler 12-smell baseline, judged
  per hunk. Repo standard overrides the baseline; smells are judgement calls; skip what tooling
  enforces.
- **Spec:** does the diff faithfully implement the frozen spec / originating issue — missing/partial
  criteria, scope creep, implemented-but-wrong. Each finding quotes the spec line.
- **Test-adequacy:** for each claimed fix, would reverting the production change fail a test?

Run the axes as separate fresh-context workers so they can't pollute each other; aggregate side by
side; do NOT rerank across axes (code can pass one and fail the other — that's the point).

## Anti-false-positive gate (gstack)

A finding MUST quote its verbatim motivating code line; if it can't, confidence drops and it goes to
an appendix. Kills the "field doesn't exist on the model" FP class. Multiple axes flagging the same
`path:line` → confirmed, boost confidence.

## Output + the reviewed SHA

Findings side by side per axis with severity (Critical/Required/Nit/Optional/FYI), each with the
quoted line. Record the exact `reviewed_sha` in the evidence manifest (reviewed-sha-freshness.md) —
the merge depends on it.

## Completion

Pinned fixed point (non-empty `git diff <fp>...HEAD`), both axes reported with no cross-rerank, every
finding quotes its line, reviewed_sha recorded. This axis checks conformance; refusal-under-attack is
`risk-review` / `harden-it`.
