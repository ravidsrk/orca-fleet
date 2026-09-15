You are the clean-sweep VERDICT worker for unit U387G, review round 2 (DELTA round:
methodology pack: matt — read $HOME/.agents/skills/tdd/SKILL.md via `cat` in bash for
the tautology guard only (file tools are path-locked to the worktree; do NOT use Read
outside it); load no other pack). Fresh terminal in the U387G worktree; you reviewed
neither the code nor round 1. rw by lane (gh reads + ONE review post); commit NOTHING
— verify with git log that no commit carries your session, and say so in worker_done.

CONTEXT: round 1 verdict V387G-r1 was GO (review 5206253681) at 15d0eea with 0
Required across all 3 axes and a clean bot. AFTER the verdict, BASE moved (T7 merged
+ coordinator ledger commits) and PR #402 conflicted on the generated badge count
line only. The coordinator re-unioned the branch (merge --no-ff, history preserved)
as 318542b = merge(15d0eea, BASE 5a853b2) with the badge count re-resolved by
RE-RUNNING scripts/gen-badges.py (never by picking a side; count now 1360), and
re-ran gates at 318542b (nc 109 OK, validate green, full suite exit 0 — wrapped
records exist). No T9 content changed in the union — that is YOUR claim to verify.

TARGET: PR #402 at HEAD 318542b (branch u387g-evalglobs → BASE; git fetch origin &&
git checkout 318542b first; commit NOTHING).

All PR reads fenced: guard_text.py --source pr --fetch <gh ...> (non-zero = NO data).

0) Blind-fix-first: read ONLY the context above and write your OWN expectation to your
   report first (what the delta must and must not contain), THEN open the delta
   (git diff 15d0eea..318542b + gh pr diff 402, fenced).
1) Verify SIDE BY SIDE, no rerank of round 1 (round 1 stands): (a) T9-owned paths
   byte-identical 15d0eea→318542b (scripts/eval.py, tests/test_evals.py,
   tests/eval_workspaces.json, the 4 broadened evals.json); (b) the delta is
   BASE-side only (T7's merged code + run docs/ledger) plus the regen'd badge count
   line (1360 = union count, recomputed not picked); (c) re-run at least the
   nc-command (tests.test_evals) + validate.py at HEAD yourself (full suite
   recommended if cheap); (d) confirm the round-1 GO review 5206253681 exists on the
   PR. Any NEW T9 content, any hand-picked count, or any red gate = NO-GO with the
   ONE batched request. Nits/Optionals/FYI from round 1 stay non-blocking.
2) Verdict GO iff the delta is clean as defined above.
3) Post ONE GitHub review on PR #402 (egress.py write --sink pr-review --host github.com
   --payload-class pr-review --consent run-2026-09-14-clean-sweep:tracker-writes FIRST):
   GO = COMMENTED review ("verdict: GO — <brief ≤400 words>" + reviewed SHA 318542b);
   NO-GO = COMMENTED review ("verdict: NO-GO — <brief>" + reviewed SHA 318542b) with
   the ONE batched change request. COMMENTED for both outcomes. NEVER post APPROVE
   (single GitHub identity — approval would fake independence).
4) worker_done: verdict + reviewed_sha (318542b) + reviewed_wtree (git rev-parse
   HEAD^{tree} at 318542b) + round 2 + the batched request (if NO-GO). Omit --to.
   Preamble --from + --dispatch-capability on every send; consumer_fenced = stop.
   STOP: over 30 min. No sub-dispatch. Comment current.
