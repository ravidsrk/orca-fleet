You are the clean-sweep FIX worker for unit U387P, review round 2 (methodology pack:
matt — read $HOME/.agents/skills/tdd/SKILL.md and follow it; load no other pack). Fresh
terminal in the U387P worktree on branch ravidsrk/u387p-process (must be at the union
tip ed8a7c5 — verify with git log AND git status; if HEAD is detached (reviewers
checkout the SHA), reattach with `git checkout ravidsrk/u387p-process` first and verify
the tip is ed8a7c5; refuse a dirty baseline).

VERDICT (round 1, NO-GO, reviewed ed8a7c5, review 5206282948): SPEC met C-1..C-5 with
0 Required, but 4 Required findings are open (TEST F1/F2, STANDARDS R-1/R-2) plus 2
VALID bot P2s. Everything else stands at its severity and does NOT block: SPEC Nit +
3 FYI, TEST 2 Nits + 4 FYI, STANDARDS 6 Nits + 2 Optional + 2 FYI; the U364 ask line,
SPEC F-4 and the pending manifest SHA are conductor-side; SPEC F-2 is disclosed;
#235/head_tree are pre-existing.

THE ONE BATCHED REQUEST (fix exactly this, nothing else):
1) Reattach (R-1 = SPEC F-1 = bot 4012397534): review-template.md:11 promises 'the
   conductor reattaches the branch' with no procedure. DEFINE the reattach step in
   conductor-close.md ( whoever commits next in a review-touched worktree — fix
   builder or conductor union — checks branch state first and reattaches to the unit
   branch, verifying the expected tip, before committing; reviewers leave HEAD
   detached and say so) and keep the template's reference accurate (or drop the
   promise if you can justify deletion over definition — definition recommended).
2) M^2 fallback (conductor-close.md:13; bot 4012397546 = SPEC F-3): CLOSE hard-codes
   T := M^2 but squash/rebase/ff merges have no second parent. Document the fallback:
   merges MUST be --merge (ledger-contract MERGED = merge-commit, cite it); a merge
   with no M^2 is non-conforming → STOP + human gate (fail closed, never improvise T).
3) C-4 probe (TEST F1): the probe checks keyword presence only. Make it check RULE
   BODIES + CLOSE steps: pin the union-invalidates sentence, the option-A sentence,
   the out-of-process sentence, and each CLOSE step (stable anchors — step numbers +
   key verbs — not full-text equality). Deleting any rule or step must go RED.
4) C-1 probe (TEST F2): the probe is a one-word denylist. Make it validate each T-row
   park cell against ledger-contract's allowed classes (parse the contract or pin+cite
   its lines — either way binding_audit must say what the probe TRULY does, no
   overclaim), plus the run ref present, the T6 GO citation present on T3, and flags
   1-11 unchanged. Adjacent Nits in the same probes: F3 (missing ledger file → FAIL,
   not ok) and F4 (scope the C-3 greps to the worker_done contract block).
5) T3 ref (R-2): repoint the T3 needs-human ref from '(U364 close, loop log)' to the
   conductor-written ask at docs/runs/2026-09-14-clean-sweep-tracker/gate-batch.md G3
   (committed on BASE; your step-1 union brings it — verify it exists before
   referencing it).

SCOPE: the run ledger + u385-manifest.json + review-template.md + conductor-close.md +
u387p-probe.sh + the unit manifest + the negctrl transcript ONLY. Do not touch frozen
specs, other flags, code, evals, or any other file. No badge regen (a shell probe
moves no test count). Never `git add -A`. The non-batched Nits/Optionals/FYI are NOT
in this batch; touch them only if your Required fix cannot land without it, and say so
in the commit message.

CONTRACT (unchanged): contract.source =
docs/runs/2026-09-14-clean-sweep-tracker/taskspecs/build-387-process.md@719d997be28476c382660f3f37d829e597130ce9.
contract.digest =
sha256:d2b868060256e8ff541121e8eb1897d9f94b7d3e0eccf45f02e068313414331f.
criterion_ids = [C-1, C-2, C-3, C-4, C-5] (unchanged). NC-COMMAND unchanged: sh
docs/runs/2026-09-14-clean-sweep-tracker/u387p-probe.sh.

STEPS:
1) Union first: merge origin/review/2026-09-14-holistic-fixes into the branch. LEDGER
   WARNING: the branch edits T1/T2/T3/T4 rows — the union MUST keep both the branch's
   fixes AND BASE's newer rows/bullets; take-both-sides only, else STOP (escalate).
   If ONLY badge files conflict, re-regen + continue (mechanical); any other conflict
   = STOP.
2) Red FIRST: each strengthened probe assertion fails pre-fix (show the RED: delete a
   rule body, use a bogus park class, drop the T6 cite, remove the ledger — each must
   fail), passes post-fix.
3) Implement 1)+5) above, smallest change.
4) Recorder run of the NC-COMMAND (probe) + validate.py + FULL suite, all green.
   gitleaks detect clean.
5) Re-run the round-1 negative controls (record the revert RED transcript) at the new
   tip. Update the unit manifest
   (docs/runs/2026-09-14-clean-sweep-tracker/u387p-manifest.json): new head_sha (:= the
   tip you push, INCLUDING the manifest commit — name the pushed tip, not its parent),
   new commands block (artifact null everywhere, never a /tmp path), extended NC
   transcript, CORRECTED binding_audit (describe what the probes truly check), same
   contract/criteria/intent/lighting. Commit fix + manifest (bisectable, maintainer
   author, no trailers, named staging, receipt-style messages).
6) Push the BARE branch (egress.py write --sink git-push --host github.com
   --payload-class branch-tip --consent run-2026-09-14-clean-sweep:base-writes FIRST):
   `git push origin ravidsrk/u387p-process:u387p-process`. PR #403 exists — do NOT
   open another; your push updates it. No merge, no rebase past step 1. After your
   push Greptile re-reviews: report any NEW findings in worker_done, do not chase them
   (they need a new spec).
7) worker_done with new head SHA + gates + NC transcript. Omit --to. Preamble flags on
   every send; consumer_fenced = stop. STOP: unexplained red; out-of-scope rot; over 60
   min. ESCALATION: blocking ask. No sub-dispatch. Comment current.
