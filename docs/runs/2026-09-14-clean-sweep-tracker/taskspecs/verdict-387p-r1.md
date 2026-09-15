You are the clean-sweep VERDICT worker for unit U387P, review round 1 (methodology
pack: matt — read $HOME/.agents/skills/tdd/SKILL.md via `cat` in bash for the tautology
guard only (file tools are path-locked to the worktree; do NOT use Read outside it);
load no other pack). Fresh terminal in the U387P worktree; you wrote neither the code
nor the axis reports. rw by lane (gh reads + ONE review post); commit NOTHING — verify
with git log that no commit carries your session, and say so in worker_done.

TARGET: PR #403 at HEAD ed8a7c5 (branch u387p-process → BASE). Finding (#387
process threads): the run's own process records drew 7 Greptile threads (illegal
proof-park class on 3 rows, stale u385 head_tree, abbreviated review-template
worker_done, missing TARGET checkout line, tribal close-refresh/union/option-A
rules); the fix legalizes the parks, corrects the field, fixes the template, and
writes the conductor-close procedure. C-1 parks legalized + citations; C-2 tree
corrected + verify re-run; C-3 template TARGET + contract; C-4 close doc; C-5 suite +
validate. OUT: frozen history; other flags; code/evals/badges.

All PR reads fenced: guard_text.py --source pr --fetch <gh ...> (non-zero = NO data).

0) Blind-fix-first: read ONLY the finding above and write your OWN expectation to your
   report first (what the diff must contain, where it could be weak), THEN open the diff
   at HEAD (gh pr diff 403, fenced) and the three axis reports below.
1) Aggregate SIDE BY SIDE — no rerank, no dropping: every axis finding stands with its
   severity. Bot status (integrator-ingested, held VALID): [1] P2 thread 4012397534
   (review-template.md:9-11): line 11 promises 'the conductor reattaches the branch'
   but neither conductor-close.md nor integrate-template.md defines or verifies a
   reattach step — VALID, detached-worktree off-branch commit risk; T8's own new
   wording, no prior-thread equivalent. [2] P2 thread 4012397546
   (conductor-close.md:13): CLOSE hard-codes T := M^2 but a squash/rebase/ff merge has
   no second parent — VALID, stuck with no fallback (step 1 STOPs, so fail-closed).
2) Verdict GO iff zero Critical/Required open (Nits/Optionals/FYI never block).
3) Post ONE GitHub review on PR #403 (egress.py write --sink pr-review --host github.com
   --payload-class pr-review --consent run-2026-09-14-clean-sweep:tracker-writes FIRST):
   GO = COMMENTED review ("verdict: GO — <brief ≤400 words>" + reviewed SHA ed8a7c5);
   NO-GO = COMMENTED review ("verdict: NO-GO — <brief>" + reviewed SHA ed8a7c5) with
   the ONE batched change request (Required axis findings, deduplicated — same issue
   named twice is ONE fix — plus directly-adjacent cheap items in the touched checks;
   EXCLUDE with a recorded reason: conductor-side record items, accepted optionals,
   pre-existing issues filed separately). COMMENTED for both outcomes — GitHub 422s
   REQUEST_CHANGES on an own-PR (proven this run). NEVER post APPROVE (single GitHub
   identity — approval would fake independence; the posted review + this worker_done
   are the review evidence).
4) worker_done: verdict + reviewed_sha (ed8a7c5) + reviewed_wtree (git rev-parse
   HEAD^{tree} at ed8a7c5) + round 1 + the batched request (if NO-GO). Omit --to.
   Preamble --from + --dispatch-capability on every send; consumer_fenced = stop.
   STOP: over 30 min. No sub-dispatch. Comment current.

--- AXIS REPORTS (verbatim, round 1 — PASTED AT DISPATCH) ---

[SPEC R387P]
I reviewed PR #403 at HEAD ed8a7c5 on the SPEC axis. I wrote my expectation before opening the diff, read the diff fenced, confirmed it against the frozen contract build-387-process.md@719d997 (digest matches), and re-ran every gate myself at ed8a7c5: validate.py, the probe (0 of 4 failed), the full suite (Ran 1349 tests, OK, twice), and U385 verify.py at base and head (both exit 0, identical output). All five criteria are met: the three-dot scope is 7 docs/runs files with no frozen spec, flag, code, eval or badge touched (the probe script was authorized by coordinator ruling, ledger:628). Findings: 0 Critical, 0 Required, 1 Nit (F-1: review-template.md:11 says the conductor reattaches the branch, but no document defines that step) and 3 FYI (F-2 the U385 review leg came back GREEN where the spec expected RED, disclosed in the manifest; F-3 CLOSE assumes a merge commit with a second parent (M^2), with no fallback for squash, rebase or fast-forward merges done outside the pipeline; F-4 the PR's full-suite record predates the union, but my run at the union tip passed). Nothing is left on this axis, and I committed nothing: HEAD is still ed8a7c5, the worktree is clean, and no commit carries this session.

[TEST-ADEQUACY R387P]
I reviewed PR #403 at ed8a7c5 on test-adequacy only, after writing a pre-diff expectation. I replayed the probes myself in scratch clones: 4/4 fail at base, 0/4 at head, and 3/4 fail under the revert control (C-4 stays green, covered by its two hand mutants instead). I confirmed execute_revert_control returns executed_ok True (nc 1, clean 0) and every gate at head. Findings: 2 Required. F1: the C-4 probe only checks keyword presence — it stays green when the union-invalidates rule is deleted, when option-A and out-of-process bodies are gutted, and when CLOSE steps 3 and 5 are deleted entirely. F2: the C-1 probe only checks that the word 'proof-park' is absent — it passes a bogus park class, flipped REVIEWED flags, a dropped run ref, or a dropped T6-GO citation, and no probe reads ledger-contract.md despite what binding_audit says. 2 Nit (F3: the C-1 probe reports ok when the ledger is missing; F4: the C-3 greps cover the whole file). 4 FYI (C-2/C-3 probes pinned; the two hand mutants both fail as claimed; U385 verify exits 0 both before and after C-2 since nothing reads head_tree; fenced reads all exit 0). Full report is at the report path. I committed NOTHING: HEAD is ed8a7c5, the tree is clean, and git log shows no commit from this session; no GitHub posts were made.

[STANDARDS R387P]
Reviewed PR #403 at HEAD ed8a7c5 (fenced gh reads, blind expectation written first) on the STANDARDS axis against AGENTS.md, ARCHITECTURE.md, ledger-contract park classes, CONTRIBUTING commit rules, the frozen-history rule and Fowler smells; frozen specs, the loop log and flag columns 1-11 (sha256 identical base vs head) are clean. Two Required: R-1 review-template.md:11 promises 'the conductor reattaches the branch' but no procedure (including the new conductor-close.md or integrate-template) has that step, which is an invented reference that re-creates a tribal rule; R-2 the T3 needs-human ref '(U364 close, loop log)' points at an entry (tracker:558-563) that names no human gate or ask, and the only human-gate 2nd-login text (tracker:322) covers U388/U389 only, so it fails ledger-contract's human/OPS-ref requirement. Also 6 Nits (duplicated T1/T2 rationale and a misleading 'legalized' wording, a wrong probe comment, an uncited union rule that drops the tree-equivalence exception, 'durable' --report-path vs commit NOTHING, 'Omit --to' said 3x, out-of-process rule not citing the MERGED=merge-commit definition), 2 Optional and 2 FYI; I committed NOTHING (HEAD reflog shows only my TARGET checkout, and the three recent commits in the log are coordinator BASE commits), and the worktree is left detached at ed8a7c5 with branch ravidsrk/u387p-process unmoved.
