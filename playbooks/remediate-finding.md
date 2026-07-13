# Playbook — remediate-finding  (the per-finding fix loop; shared by clean-sweep + campaigns)

The unit is ONE confirmed finding. Same loop whether the finding came from an audit, a tracker issue,
a security lens, a perf breach, or a flaky test — the mission supplies the finding SOURCE and the
"clean" contract; this playbook supplies the closure pipeline.

## Per-finding pipeline (PR-per-finding)

1. **Verify the finding is real BEFORE spending fix effort** (Matt triage): reproduce the bug /
   check out the PR and confirm it does what it claims. Two codebase checks first — REDUNDANCY (search
   by domain concept: already implemented → wontfix) and PRIOR-REJECTION (an out-of-scope KB). An
   unreproducible finding is REFUTED with attempts logged, or needs-human if it implies private state.
2. **Fix** via `build-change` (failing test first / red repro, smallest change, negative control).
3. **Open PR against BASE** (integrator, never the builder; assert `baseRefName==BASE`) + reconcile
   any review bot (dispatch-lifecycle.md bot non-convergence).
4. **Build-blind REVIEW** (acceptance-review, + risk-review lens if the finding is a risk class);
   record reviewed_sha.
5. **merge_ready → the conductor** (merge-serialization.md): reviewed-SHA-fresh, ancestry-verified.
6. **Close with evidence:** the merge SHA + a completion note. A fix-backed close needs no extra human
   gate — the evidence chain is the authorization. A refutation/duplicate close is a one-way batch gate.

## Rules

- Close ONLY off a verified merge, never off worker memory.
- One finding = one branch = one PR = one merge commit; same-file findings form a merge chain.
- The mission owns "how do I know the whole set is clean" (its convergence proof); this owns "how do I
  close one finding correctly".
