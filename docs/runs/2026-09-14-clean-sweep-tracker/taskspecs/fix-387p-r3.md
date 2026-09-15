You are the clean-sweep FIX worker for unit U387P, review round 3 (methodology pack:
matt — read $HOME/.agents/skills/tdd/SKILL.md and follow it; load no other pack). Fresh
terminal in the U387P worktree on branch ravidsrk/u387p-process (must be at the r2
tip 7f52bf6 — verify with git log AND git status; if HEAD is detached (reviewers
checkout the SHA), reattach with `git checkout ravidsrk/u387p-process` first and verify
the tip is 7f52bf6; refuse a dirty baseline).

VERDICT (round 2, NO-GO, reviewed 7f52bf6, review 5206777406): 1 Required open
(TEST TA-R1, reproduced by the verdict worker). Everything else stands at its
severity and does NOT block: SPEC 1 Nit + 1 Optional + 5 FYI, TEST 6 Nits + 1
Optional, STANDARDS 6 Nits + 1 Optional + 4 FYI (incl. the stale DECISIONS FYI —
the ruling IS on BASE, do not touch); Greptile APPROVED 5206614322, no new
findings. The 2 held bot P2 threads are auto-resolved with zero replies — the
in-thread answers are OWED FROM THE COORDINATOR LANE, not you: post NO replies,
make NO GitHub posts at all.

THE ONE BATCHED REQUEST (fix exactly this, nothing else):
1) TA-R1 (Required): the C-1 probe accepts ANY ledger-contract class on T1-T3, so
   relabelling T1's park to 'refuted:' stays GREEN though spec C-1 requires
   needs-human. Pin the T1-T3 park class to needs-human AND require the ask text
   in the C-1 probe; the relabel mutant (T1 park → 'refuted:') must go RED and be
   recorded in the negctrl transcript.
2) Adjacent cheap items in the touched checks: (a) repoint T1/T2 park refs from
   the loop log to gate-batch.md G3 and extend the G3-ref assertion to T1-T3;
   (b) assert the G3 body ASK text, not just the heading; (c) scope
   conductor-close's 'A merged unit cannot park' so it does not contradict step
   6 / the T1-T3 needs-human rows; (d) correct the manifest's not_witnessed_note
   '2 hand mutants' to the true C-4 mutant count (9).

SCOPE: the run ledger + gate-batch.md refs + conductor-close.md + u387p-probe.sh
+ the unit manifest + the negctrl transcript ONLY. Do not touch frozen specs,
other flags, code, evals, or any other file. No badge regen (a shell probe moves
no test count). Never `git add -A`. The non-batched Nits/Optionals/FYI are NOT
in this batch; touch them only if your Required fix cannot land without it, and
say so in the commit message.

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
2) Red FIRST: the relabel mutant (T1 park → 'refuted:') fails pre-fix (show the RED),
   passes post-fix; same red-first for 2a/2b probe assertions.
3) Implement 1)+2) above, smallest change.
4) Recorder run of the NC-COMMAND (probe) + validate.py + FULL suite, all green.
   gitleaks detect clean.
5) Re-run the round-1+2 negative controls (record the revert RED transcript) at the
   new tip. Update the unit manifest
   (docs/runs/2026-09-14-clean-sweep-tracker/u387p-manifest.json): new head_sha (:=
   the CODE tip — option-A: a manifest cannot name the SHA of the commit containing
   it, so the manifest-commit tip is named in worker_done and the coordinator
   re-binds at close; see DECISIONS.md fix-step5-headsha / ruling msg_b92468884470 —
   this supersedes the r1/r2 specs' 'INCLUDING the manifest commit' line), new
   commands block (artifact null everywhere, never a /tmp path), extended NC
   transcript, same contract/criteria/intent/lighting. Commit fix + manifest
   (bisectable, maintainer author, no trailers, named staging, receipt-style
   messages).
6) Push the BARE branch (egress.py write --sink git-push --host github.com
   --payload-class branch-tip --consent run-2026-09-14-clean-sweep:base-writes FIRST):
   `git push origin ravidsrk/u387p-process:u387p-process`. PR #403 exists — do NOT
   open another; your push updates it. No merge, no rebase past step 1. After your
   push Greptile re-reviews: report any NEW findings in worker_done, do not chase them
   (they need a new spec).
7) worker_done with new head SHA + gates + NC transcript. Omit --to. Preamble flags on
   every send; consumer_fenced = stop. STOP: unexplained red; out-of-scope rot; over 60
   min. ESCALATION: blocking ask. No sub-dispatch. Comment current.
