# Runtime policy — merge serialization (the merge queue)

Parallel workers open PRs onto one integration BASE. Two failure modes bite: merge RACES (PRs
rebasing over each other) and STALE evidence (merging a SHA the reviewer never saw). One conductor,
strict order, evidence-fresh.

## Signal

Workers/integrators emit `send --to <conductor-handle> --subject "merge_ready <unit>" --type
merge_ready --payload '{"unit":"<id>","pr":123,"branch":"<head>","reviewed_sha":"<sha>","reviewed_wtree":"<tree sha of the reviewed content>","base":"<BASE>"}'`
(`--subject` is mandatory; `--payload` must be real JSON, not shorthand). `merge_ready` is a
first-class Orca message type with NO built-in behavior — the runtime delivers it and stops, so the
fleet owns the queue semantics.

Two corrections against v1.4.199, both of which make this rule the FLEET's, not the runtime's:

- **`--to` is optional** from an active Dispatch — an omitted recipient defaults to the owning Run
  mailbox, which is the coordinator inbox and the address upstream prefers (`orchestration.ts:76`).
  Naming the conductor handle explicitly stays correct and stays this fleet's convention, because a
  merge queue has exactly one owner and the handle says so.
- **A `merge_ready` to a group is NOT rejected.** The runtime refuses group addresses for
  `worker_done` and `heartbeat` only (`message-send-handler.ts:51-58`); a `merge_ready --to @all`
  would fan out to every worker and put N writers on one BASE. Nothing below the fleet stops that,
  so the rule stands on our discipline alone: **never address a `merge_ready` to a group.**

## Conductor loop (ONE terminal owns all merges to BASE)

1. BOARD: `check --wait --types merge_ready,worker_done,escalation` → append in ARRIVAL ORDER.
   `--types` is the WAKE condition only: the Delivery that comes back is the whole FIFO batch, every
   type in it (orca-dag-semantics.md). Process the ENTIRE Delivery — settle the `worker_done`s, reply
   to the `question`s, board the `merge_ready`s — and only then `--ack <delivery_id>`. Acking after
   handling just the filtered type discards the rest unread.
2. FRESH? head of queue: `gh pr view <n> --json headRefOid,baseRefName,state` —
   state OPEN · `baseRefName == BASE` (never merge a PR aimed at default) ·
   `headRefOid == reviewed_sha` (reviewed-sha-freshness.md). Pin this accepted head as
   `reviewed_sha` for the merge command. Mismatch → compare TREES before
   bouncing (`git rev-parse <head>^{tree}` vs the payload's `reviewed_wtree`): equal trees (a
   content-identical rebase) keep the review and pin the newly accepted head; different trees →
   bounce to re-review, requeue.
3. MERGE (one at a time, commits preserved): conflicts/behind → rebase onto origin/BASE as a UNION
   preserving both intents, re-run gates, push with `--force-with-lease` (never bare force). A
   content-CHANGING rebase VOIDS the review — the PR leaves the train and re-boards on a new
   merge_ready; a content-identical one keeps it (the tree test above). Clean →
   `gh pr merge <n> --merge --delete-branch --match-head-commit <reviewed_sha>`.
   A concurrent head change refuses the merge: requeue for fresh review, then repeat FRESH;
   never retry without the expected-head guard. `--admin` only under a recorded once-per-run human
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
be restored, the unit has no PR, so the conductor works from the `merge_ready` payload's `branch`
and `reviewed_sha` (`pr` is null) and swaps every `gh` step in the loop above for a git equivalent:

- FRESH? (step 2): `git rev-parse <branch>` == `reviewed_sha` (freshness holds identically — a
  rebase still voids the review), and `git merge-base --is-ancestor origin/<BASE> <branch>`-style
  check that the branch forks from BASE (the local stand-in for `baseRefName == BASE`). Mismatch →
  bounce to re-review, requeue. Never skip this step just because there is no PR to `view`.
- MERGE (step 3): `test "$(git rev-parse <branch>)" = "<reviewed_sha>" && git merge --no-ff <reviewed_sha>`
  into BASE (commits preserved, never squash). A changed branch refuses: requeue for fresh review.
  The pinned commit also prevents a later branch move from substituting unreviewed content.
  Conflicts return to the worker for resolution and fresh review; then requeue before merging.
  Delete the branch only if it still names the merged head; retain a moved branch for re-review.
- VERIFY (step 4): unchanged — it was already pure git ancestry.

Record `no-gh: local-merge` in the ledger AND a local reviewer record — `review.artifact` at
head_sha (declared in evidence-manifest.md §1) — which verify.py's `--no-gh` review path checks
(coordinator-attested, the weaker guarantee). Because the local artifact is worker-forgeable on the
native in-session hook, verify.py accepts it ONLY when an out-of-band coordinator contract
corroborates the run (`--contract-source` `--contract-digest`, from the dispatch record — not the
manifest); without it the `--no-gh` review fails closed. The BASE→default promotion still needs a
human and a real PR, so a no-gh run stops at BASE and surfaces that the promotion PR is owed.

The same lane applies when a run STARTS offline, not just when gh dies mid-run: Phase 0
preflights with `preflight.py --offline --base <BASE> --default <branch>` — gh checks are
skipped, every git-based BASE invariant still runs — and the conductor works PR-less from
`merge_ready` payloads from unit one, with the same `no-gh: local-merge` ledger record.

## Rules

- ONE conductor per BASE. Two trains on one base is a race, not redundancy.
- Arrival order only; no priority lanes without a human gate.
- Merge to the DEFAULT branch is out of scope here — that promotion is a one-way human gate.
