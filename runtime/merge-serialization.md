# Runtime policy — merge serialization (the merge queue)

Parallel workers open PRs onto one integration BASE. Two failure modes bite: merge RACES (PRs
rebasing over each other) and STALE evidence (merging a SHA the reviewer never saw). One conductor,
strict order, evidence-fresh.

## Signal

Workers/integrators emit `send --to <conductor-handle> --subject "merge_ready <unit>" --type
merge_ready --payload '{"unit":"<id>","pr":123,"branch":"<head>","reviewed_sha":"<sha>","base":"<BASE>"}'`
(`--to` and `--subject` are mandatory; `--payload` must be real JSON, not shorthand). `merge_ready` is a first-class Orca message type with NO built-in behavior — the runtime
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

## First-merge spot-check (the pipeline inherits it)

The FIRST merge of a run gets an extra dispatched verification before the second unit merges: a
fresh worker confirms it landed as a merge commit (commits preserved, not squashed), every commit
is authored by the maintainer with no trailers, the branch is deleted, and the worktree is
retired. Whatever shape the first merge takes, the rest of the train copies — so a squashed or
mis-authored first merge silently sets the pattern for every unit after it. Catch it once, at unit
one, not at run close.

## No-gh fallback (offline / unauthenticated)

`gh` is the default path (`gh pr create` / `gh pr merge`). When `gh auth status` fails and cannot
be restored, the conductor degrades to LOCAL merge commits into BASE — `git merge --no-ff` (commits
preserved, never squash), conflicts resolved locally the same union way, branch deleted, maintainer
authorship — and records `no-gh: local-merge` in the ledger. The BASE→default promotion still needs
a human and a real PR, so a no-gh run stops at BASE and surfaces that the promotion PR is owed.

## Rules

- ONE conductor per BASE. Two trains on one base is a race, not redundancy.
- Arrival order only; no priority lanes without a human gate.
- Merge to the DEFAULT branch is out of scope here — that promotion is a one-way human gate.
