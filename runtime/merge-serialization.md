# Runtime policy — merge serialization (the merge queue)

Parallel workers open PRs onto one integration BASE. Two failure modes bite: merge RACES (PRs
rebasing over each other) and STALE evidence (merging a SHA the reviewer never saw). One conductor,
strict order, evidence-fresh.

## Signal

Workers/integrators emit `send --to <conductor-handle> --subject "merge_ready <unit>" --type
merge_ready --payload '{unit, pr, branch, reviewed_sha, base}'` (`--to` and `--subject` are
mandatory flags). `merge_ready` is a first-class Orca message type with NO built-in behavior — the runtime
delivers it and stops, so the fleet owns the queue semantics. (merge_ready to a group is rejected;
send to the conductor handle.)

## Conductor loop (ONE terminal owns all merges to BASE)

1. BOARD: `check --wait --types merge_ready,worker_done,escalation` → append in ARRIVAL ORDER.
2. FRESH? head of queue: `gh pr view <n> --json headRefOid,baseRefName,state` —
   state OPEN · `baseRefName == BASE` (never merge a PR aimed at default) ·
   `headRefOid == reviewed_sha` (reviewed-sha-freshness.md). Mismatch → bounce to re-review, requeue.
3. MERGE (one at a time, commits preserved): conflicts/behind → rebase onto origin/BASE as a UNION
   preserving both intents, re-run gates, push with `--force-with-lease` (never bare force) — but a
   rebase VOIDS the review, so the PR leaves the train and re-boards on a new merge_ready. Clean →
   `gh pr merge <n> --merge --delete-branch`. `--admin` only under a recorded once-per-run human
   grant when a merge-trap check hangs (gate-classification.md), never routinely.
4. VERIFY by ancestry, not grep: `git merge-base --is-ancestor <mergeCommit> origin/<BASE>` AND
   `state=MERGED` AND `baseRefName==BASE`. Then ledger the merge SHA + reply on the thread.
5. Hot-file ownership: PRs touching the same mount-point file (route registry, DI wiring,
   migrations, barrels) form a merge CHAIN — build parallel, merge one-at-a-time as a union.

## Rules

- ONE conductor per BASE. Two trains on one base is a race, not redundancy.
- Arrival order only; no priority lanes without a human gate.
- Merge to the DEFAULT branch is out of scope here — that promotion is a one-way human gate.
