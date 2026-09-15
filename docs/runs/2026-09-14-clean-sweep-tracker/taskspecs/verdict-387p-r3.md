You are the clean-sweep VERDICT worker for unit U387P, review round 3 (methodology
pack: matt — read $HOME/.agents/skills/tdd/SKILL.md via `cat` in bash for the tautology
guard only (file tools are path-locked to the worktree; do NOT use Read outside it);
load no other pack). Fresh terminal in the U387P worktree; you wrote neither the code
nor the axis reports. rw by lane (gh reads + ONE review post); commit NOTHING — verify
with git log that no commit carries your session, and say so in worker_done.

TARGET: PR #403 at HEAD 19be7a1 (branch u387p-process → BASE). Finding (#387
process threads): the run's own process records drew 7 Greptile threads (illegal
proof-park class on 3 rows, stale u385 head_tree, abbreviated review-template
worker_done, missing TARGET checkout line, tribal close-refresh/union/option-A
rules); the fix legalizes the parks, corrects the field, fixes the template, and
writes the conductor-close procedure. C-1 parks legalized + citations; C-2 tree
corrected + verify re-run; C-3 template TARGET + contract; C-4 close doc; C-5 suite +
validate. OUT: frozen history; other flags; code/evals/badges.
ROUND 3: this tip carries the R2 verdict batch (TA-R1 pin, G3 refs+ASK, park
scope, note fix) — the axes below re-verify it.

All PR reads fenced: guard_text.py --source pr --fetch <gh ...> (non-zero = NO data).

0) Blind-fix-first: read ONLY the finding above and write your OWN expectation to your
   report first (what the diff must contain, where it could be weak), THEN open the diff
   at HEAD (gh pr diff 403, fenced) and the three axis reports below.
1) Aggregate SIDE BY SIDE — no rerank, no dropping: every axis finding stands with its
   severity. Bot status at 19be7a1: Greptile APPROVED 5206957088, no new inline
   findings. The 2 held P2 threads (4012397534 reattach-gap → fixed 708b5a8,
   4012397546 no-M^2-fallback → fixed 2c029dd) were AUTO-RESOLVED by greptile-bot
   with zero replies — the in-thread answers are owed from the COORDINATOR lane
   pre-merge (conductor-side record item, NOT a builder fix; exclude with this
   reason — the coordinator posts them before merging).
2) Verdict GO iff zero Critical/Required open (Nits/Optionals/FYI never block).
3) Post ONE GitHub review on PR #403 (egress.py write --sink pr-review --host github.com
   --payload-class pr-review --consent run-2026-09-14-clean-sweep:tracker-writes FIRST):
   GO = COMMENTED review ("verdict: GO — <brief ≤400 words>" + reviewed SHA 19be7a1);
   NO-GO = COMMENTED review ("verdict: NO-GO — <brief>" + reviewed SHA 19be7a1) with
   the ONE batched change request (Required axis findings, deduplicated — same issue
   named twice is ONE fix — plus directly-adjacent cheap items in the touched checks;
   EXCLUDE with a recorded reason: conductor-side record items, accepted optionals,
   pre-existing issues filed separately). COMMENTED for both outcomes — GitHub 422s
   REQUEST_CHANGES on an own-PR (proven this run). NEVER post APPROVE (single GitHub
   identity — approval would fake independence; the posted review + this worker_done
   are the review evidence).
4) worker_done: verdict + reviewed_sha (19be7a1) + reviewed_wtree (git rev-parse
   HEAD^{tree} at 19be7a1) + round 3 + the batched request (if NO-GO). Omit --to.
   Preamble --from + --dispatch-capability on every send; consumer_fenced = stop.
   STOP: over 30 min. No sub-dispatch. Comment current.

--- AXIS REPORTS (verbatim, round 3 — PASTED AT DISPATCH) ---

[SPEC R387P-r3]
I reviewed PR #403 on the SPEC axis at detached HEAD 19be7a1 (blind expectation written first; the fenced gh diff matches the 7 local files vs merge-base 34c05f1). All R2 batch items landed: e221938, 955dda3, b60c5ee, 4142b63, ee988da, and the 9-mutant C-4 note in 19be7a1. C-1 through C-5 and the OUT rules are MET, and I re-ran probe 0/4, validate.py, the full suite and verify.py U385 (all exit 0, tree clean). Greptile APPROVED 5206957088 @19be7a1 with no new inline findings; findings are 0 Critical / 0 Required / 2 Nit (manifest :74-75 C-5 witness still cites round-2 head 708b5a8 and 1351 tests although head_sha is 4142b63 with 1360; manifest :64 C-4 commit list omits ee988da) / 4 FYI (loop-log proof-park at ledger :593 scoped out by ruling; U385 review leg GREEN rather than RED; probe.sh sanctioned by RULING T8). Still open: the coordinator lane owes in-thread replies on the 2 held Greptile P2s before merge (4012397534 -> fixed by 708b5a8, 4012397546 -> fixed by 2c029dd). I committed nothing: HEAD is still 19be7a1, porcelain is empty, my reflog entry is only the checkout, and the commits after 13:10 in git log --all are the coordinator's BASE commits from other worktrees.

[TEST-ADEQUACY R387P-r3]
At PR #403 HEAD 19be7a1 I checked all seven R2-batch items: e221938, 955dda3, b60c5ee, 4142b63, ee988da, the 2->9 mutants note and the 19be7a1 manifest. In a /tmp clone (now deleted) I re-ran the probe: RED 4/4 at base, 3/4 with the 3 NC paths reverted, GREEN at head. check_negative_control(execute=True) returned executed_ok True, the digests re-derive, and Greptile APPROVED 5206957088 is at 19be7a1 with no new inline comments, but the two held bot P2 threads (4012397534, 4012397546) have zero replies and the coordinator lane owes them before merge. Findings: 0 Critical, 0 Required; N-1 Nit: ee988da's cannot-park scoping has no test (reversing it, or deleting the RED-leg-parks sentences, leaves the probe 0/4 GREEN; builder disclosed this); N-2 Nit: C-1 checks the G3 pointer but not that G3 lists the row's head (dropping '#392 U388 c680ee0' stays GREEN); O-1 Optional: the C-3 checkout line is grepped file-wide, not in the TARGET block; 3 FYI plus 1 low-confidence appendix (no committed text mentions the tee file); I made no commit, porcelain is empty, and the worktree is left detached at 19be7a1.

[STANDARDS R387P-r3]
I reviewed PR #403 on the STANDARDS axis at HEAD 19be7a1 (fenced reads; the worktree was already detached at 19be7a1). All six R3 batch items landed: e221938 pins T1-T3 to needs-human with the ask; 955dda3 and b60c5ee put the G3 ref on T1-T3; 4142b63 asserts the G3 ASK body; ee988da scopes 'cannot park' at conductor-close.md:68-71; the 19be7a1 note now says nine mutants, and the '2 hand mutants' grep hits are substrings of '22'. I re-ran the probe (0 of 4 failed) and validate (exit 0), and confirmed Greptile APPROVED 5206957088 at 19be7a1 with no new inline finding. I found 0 Critical, 0 Required, 3 Nits, 1 carried-over Optional and 3 FYI: S3-1, conductor-close.md:70-71's '(T1-T3: needs-human ...)' repeats step 6 and omits T7 and T9; S3-2, step 6 (:43-44) never says to append the head to gate-batch G3 or point the park cell at it, and G3 at the BASE tip still lacks #402 (318542b) with no G3 pointer in the T7/T9 park cells; S3-3, u387p-probe.sh:78 defines g3_ask inline instead of as a constant next to ASK; plus the union-invalidates Nit (missing the tree-identical exception) and the move-to-runtime Optional, both carried from R2. Still owed: the 2 held bot P2 threads were auto-resolved by greptile with ZERO replies, so the coordinator lane owes in-thread answers before merge (4012397534 -> 708b5a8, 4012397546 -> 2c029dd); I committed, stashed and pushed nothing (git log -1 is the builder's 13:04 commit, porcelain is empty, and the 13:11:49 detached checkout in the reflog is not mine).
