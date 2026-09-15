CONDUCTOR-CLOSE procedure — post-merge evidence closure, once per unit. ACTOR: the
COORDINATOR (conductor) itself, never a dispatched worker: the unit's workers are released
by the time it runs, and every record it writes is labelled "coordinator". Methodology:
none (mechanical record-keeping). Commits exactly ONE chore(run) commit on BASE per close.

WHEN: after the unit PR is MERGED into BASE and its verdict review is posted. Not before:
every rule below binds evidence to the merged, reviewed tip, which does not exist earlier.

INPUTS: the unit manifest; PR number; merge commit M; verdict review id; the dispatch
record's contract source + digest; the coordinator-named nc-command; the unit class.

CLOSE (in order; any mismatch is a STOP, logged, never patched over):
1) Resolve the tip: T := git rev-parse M^2 (the merged PR head). Assert T == the verdict's
   reviewed_sha and git merge-base --is-ancestor T BASE. T != reviewed_sha means the
   review is stale (see union-invalidates). M must be a merge commit: ledger-contract
   MERGED = merge-commit (not squash) (runtime/ledger-contract.md, unit-row flags), so
   unit PRs merge with gh pr merge --merge only. A squash, rebase or fast-forward merge
   has no M^2 (git rev-parse M^2 fails): the merge is non-conforming, so STOP and raise a
   human gate naming M and its merge method. Fail closed: never derive T another way
   (not M, M^1, the PR's headRefOid or a guessed commit).
2) Re-run in a clean worktree at the merge tip: git worktree add --detach
   <scratch>/close-<unit> T; git status --porcelain empty; then the nc-command,
   python3 scripts/validate.py and python3 -m unittest discover -s tests, each wrapped by
   runtime/scripts/evidence-run.py into a manifest OUTSIDE the worktree (the tree stays
   clean). All exit 0. git worktree remove --force the scratch worktree after.
3) Append coordinator records: the three records go into commands[] labelled
   "coordinator <gate> at head", commit = T, wtree = git rev-parse T^{tree}, with an
   artifact_note quoting the runner's summary line. Builder records at older trees STAY as
   true history; they are not edited or deleted.
4) Re-bind head/head_tree: head_sha := T and head_tree := git rev-parse T^{tree}, both
   RECOMPUTED from git, never copied from a note (U385 slip: head_sha re-bound, head_tree
   left at the builder tree 022dc9a; fixed by U387P). Prepend a "CONDUCTOR CLOSE <iso-ts>"
   sentence to head_sha_role naming the old and new values and the T-vs-builder-head delta
   (git diff --stat, normally manifest + negctrl only).
5) pr fill: pr.number, pr.url, pr.reviewed_sha := T, pr.reviewed_wtree := T^{tree}.
   Replace every "pending" SHA in commits[] with the real one from git log. If the worker
   wrote contract.source in brief form, correct it to the frozen spec file@dispatch-commit
   and check git show <ref>:<path> | shasum -a 256 == contract.digest; say so in a
   conductor_note.
6) verify.py: python3 runtime/scripts/verify.py --manifest <m> --contract-source <src>
   --contract-digest <digest> --nc-command '<nc>' --execute-nc --base <BASE>
   --unit-class <class>. Record the per-leg outcome in the ledger row evidence. A RED leg
   is RECORDED, never hidden: the review leg RED (no independent APPROVED) parks the row
   needs-human with the ask and a run ref — the ledger contract allows no other class for it.
7) Commit: ONE chore(run) commit on BASE with the manifest edits, the ledger row
   (MERGED/WT_CLEAN flips, park, evidence) and a loop-log line, subject
   "chore(run): U<nnn> evidence closure (...)". Push with its egress receipt, then retire
   the unit worktree (dispatch-lifecycle guards).

RULES:
- option-A (self-reference). A commit cannot name its own SHA, and a commands[] record
  cannot bind the tree of a commit that contains the record. So at BUILD the worker sets
  head_sha = its last CONTENT commit (the code tip: every commands[] wtree == that
  commit's tree) and names the pushed manifest-commit tip separately in worker_done.
  Never write "head := pushed tip incl. manifest": it cannot be implemented. At CLOSE the
  conductor re-binds head_sha to the reviewed tip (step 4), the first point where the
  manifest commit is already history. Precedent: U388/U389 (asks msg_e020b050c175,
  msg_a7efb8e1b918).
- union-invalidates. A merge of BASE into the unit branch (a union) changes the tree under
  every earlier binding. commands[] records, NC replays and verdicts made before the union
  bind a tree that is no longer the tip, so they are STALE until re-run at the post-union
  tip: the integrator re-runs the gates on the union, reviewers review the union tip, and
  step 2 re-runs at the merge tip regardless. Stale records stay in commands[] as history
  and never count as fresh (verify.py check_commands binds wtree to head_sha^{tree}).
- out-of-process-merge. A merge made outside this pipeline (a human merging on GitHub while
  a review is in flight, another agent's PR landing on BASE) is disclosed, not normalised:
  record the actor (gh pr view --json mergedBy), the merge commit and what was in flight,
  in the loop log and in the manifest; then re-verify from step 1 at that merge's tip. A
  merged unit cannot park, so an open review round posts as a record and a sticking finding
  goes to a fix-forward unit. Precedent: T6 (PR #397 merged ~7 min before its GO verdict,
  disclosed; verify 6/6) and U364 (PR #395 merged mid-r3; fix-forward by T6).
- reattach. Review workers check out the reviewed SHA (review-template.md TARGET), which
  leaves the unit worktree on a detached HEAD; they leave it detached, commit nothing, and
  say so in worker_done. Whoever commits next in a review-touched worktree (the fix
  builder, or the conductor or integrator making a union) reattaches BEFORE the first
  commit: git status --porcelain empty; git checkout <unit-branch>; assert
  git branch --show-current == <unit-branch> and git rev-parse HEAD == the expected tip
  (the reviewed_sha, or the tip the dispatch names). A dirty tree, a failed checkout or a
  tip mismatch is a STOP: never commit on a detached HEAD (the commit sits on no branch
  and the push leaves it behind).
