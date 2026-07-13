# Runtime policy — reviewed-SHA freshness

A build-blind review is only valid for the exact SHA it reviewed. The single most common way a
fleet ships unreviewed code is merging a branch whose head moved after review.

## The invariant

`worker_done.pr.reviewed_sha` MUST equal the branch head at merge time. If they differ, the review
is VOID and the PR must be re-reviewed for the new head before it can merge.

## What moves a head after review (all void it)

- A conductor/integrator **rebase** to resolve conflicts or union-merge onto BASE — necessarily
  changes the head SHA. The PR leaves the merge queue and re-boards only with a fresh review.
- A **bot autofix** commit (Cursor BugBot Autofix and similar) landing after the reviewer's PASS.
  See dispatch-lifecycle.md "bot non-convergence".
- Any late push by the builder.

## Enforcement

- The reviewer records the SHA it reviewed in the evidence manifest.
- The merge step (merge-serialization.md) checks `gh pr view <n> --json headRefOid` against
  `reviewed_sha` and refuses to merge on mismatch — bounce to re-review, requeue at the back.
- "Re-run gates green" is NOT a review. Only a fresh build-blind review of the new head restores
  freshness.
