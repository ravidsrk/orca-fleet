# Playbook — land  (merge the integrated work to BASE)

Recipe: merge-serialization.md as the mechanism. LAND is the first of the three release states —
distinct from RELEASE (version/publish) and OBSERVE (canary). Landing means the work is on the
integration BASE, verified by ancestry; it does NOT mean shipped.

## Steps

1. All units for the wave are `merge_ready` (reviewed-SHA fresh, ancestry-verifiable).
2. The conductor drains the queue in arrival order, hot-file chains serialized, `--force-with-lease`
   only, rebase voids review (re-board).
3. VERIFY each: `git merge-base --is-ancestor <mergeCommit> origin/<BASE>` AND state=MERGED AND
   baseRefName==BASE AND a symbol from the unit is greppable on BASE.
4. Ledger the merge SHA per unit; `WT_CLEAN` after teardown (never remove an active/unmerged/dirty
   worktree).

## Terminal state

`BUILT` — everything merged to BASE and verified. The BASE→default promotion is a SEPARATE one-way
human gate (gate-classification.md); landing on BASE is never promotion.
