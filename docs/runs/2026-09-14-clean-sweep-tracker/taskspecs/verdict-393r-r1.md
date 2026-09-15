You are the clean-sweep VERDICT worker for unit U393R, review round 1 (methodology
pack: matt — read $HOME/.agents/skills/tdd/SKILL.md via `cat` in bash for the tautology
guard only (file tools are path-locked to the worktree; do NOT use Read outside it);
load no other pack). Fresh terminal in the U393R worktree; you wrote neither the code
nor the axis reports. rw by lane (gh reads + ONE review post); commit NOTHING — verify
with git log that no commit carries your session, and say so in worker_done.

TARGET: PR #404 at HEAD abaf17502a25f16dbd4cfaf28fafba1e211ab40a (branch u393-race → BASE).
Finding (#387 thread 4012510839): the #393 sidecar join is check-then-act — a legacy
wrapper can create and lock <manifest>.lock after the absence check and overlap the new
append under the other lock, silently losing a record; the fix re-checks before the
truncate and, if one appeared, releases the manifest lock, joins the sidecar (blocking)
and re-reads, bounded, under the one documented lock order, never creating a sidecar
(#388 kept). C-1 deterministic forced-schedule regression test (RED-then-GREEN, no bare
sleeps, real module paths); C-2 the fix preserving #388 + order + never-raises +
steady-state, residual documented; C-3 full suite + validate green. OUT: lock-free
peers; changing #388; the steady-state protocol.

All PR reads fenced: guard_text.py --source pr --fetch <gh ...> (non-zero = NO data).

0) Blind-fix-first: read ONLY the finding above and write your OWN expectation to your
   report first (what the diff must contain, where it could be weak), THEN open the diff
   at HEAD (gh pr diff 404, fenced) and the three axis reports below.
1) Aggregate SIDE BY SIDE — no rerank, no dropping: every axis finding stands with its
   severity. Bot status (integrator-ingested, held VALID): [1] Greptile P1 thread
   4015794383 (evidence-run.py:212-216, "Race still loses records"): the
   post-exists() interleaving it describes is real, but it is the SAME residual window
   the builder already disclosed in the append_record docstring and the manifest's
   noticed_not_touched[0] (seek+truncate+one write, unclosable under #388); its note
   that the forced C-1 test does not cover that window matches the manifest's scoping.
   Adjudicate: accept-with-reason (disclosed residual, spec C-2 explicitly asks for
   honest documentation, not elimination) or fold into the change request — with a
   recorded reason either way.
2) Verdict GO iff zero Critical/Required open (Nits/Optionals/FYI never block).
3) Post ONE GitHub review on PR #404 (egress.py write --sink pr-review --host github.com
   --payload-class pr-review --consent run-2026-09-14-clean-sweep:tracker-writes FIRST):
   GO = COMMENTED review ("verdict: GO — <brief ≤400 words>" + reviewed SHA abaf175);
   NO-GO = COMMENTED review ("verdict: NO-GO — <brief>" + reviewed SHA abaf175) with
   the ONE batched change request (Required axis findings, deduplicated — same issue
   named twice is ONE fix — plus directly-adjacent cheap items in the touched checks;
   EXCLUDE with a recorded reason: conductor-side record items, accepted optionals,
   pre-existing issues filed separately). COMMENTED for both outcomes — GitHub 422s
   REQUEST_CHANGES on an own-PR (proven this run). NEVER post APPROVE (single GitHub
   identity — approval would fake independence; the posted review + this worker_done
   are the review evidence).
4) worker_done: verdict + reviewed_sha (abaf175) + reviewed_wtree (git rev-parse
   HEAD^{tree} at abaf175) + round 1 + the batched request (if NO-GO). Omit --to.
   Preamble --from + --dispatch-capability on every send; consumer_fenced = stop.
   STOP: over 30 min. No sub-dispatch. Comment current.

--- AXIS REPORTS (verbatim, round 1 — PASTED AT DISPATCH) ---

[SPEC R393R]
I reviewed PR #404 at abaf175 against the frozen C-1..C-3 spec (fenced diff read, pre-diff expectation written first) and re-ran everything myself under timeouts: RED 5/5 with exactly ['legacy'] lost on 62da77c's production file, GREEN at HEAD (29/29 in the target file, race + mixed-version 5/5), validate.py exit 0, full suite 'Ran 1379 tests ... OK'. All three criteria are MET with no scope creep. Findings: F1 Optional, the lock-order clause (never hold manifest while acquiring sidecar) is correct but unguarded, because an ABBA mutant at evidence-run.py:212-213 still passes 29/29; F2 Nit, the manifest's witness 'exists() returns False on OSError' is false on py3.13, though never-raises still holds via the outer except; F3 FYI, the residual 'one write' wording understates the buffered write-to-close gap; F4 FYI, the C-3 records are bound to 076f880, though the code delta to abaf175 is empty. Nothing was left unverified; I committed nothing (git log -1 = abaf175, tree clean), and the only appendix item (A1, the manifest's branch name vs PR head) is at ~40% confidence.

[TEST-ADEQUACY R393R]
I reviewed PR #404 at abaf175 on the test-adequacy axis only, and wrote my own expectation before opening the diff. In a scratch clone (deleted afterwards) I reproduced HEAD GREEN 20/20 and both negative controls RED 20/20 with exactly ['legacy'] lost; C-1 is structurally sound: its probes delegate to the real flock/loads, labels are literals, there are no sleeps, and it covers the rejoin path, since the first read is always stale. Two survivors remain: REQUIRED-1, the last-attempt write-through (evidence-run.py:212, attempt < REJOIN_ATTEMPTS) is unpinned, because dropping that condition passes all 29 tests while silently writing nothing; REQUIRED-2, the pre-truncate re-check position is unpinned, because moving the check to right after the manifest lock passes all 29 tests while a sidecar created after the read loses ['new']; each has a verified scratch killer test, plus Optional notes (residual window only narrated, unopenable mid-append sidecar untested) and a benign Nit (not-joined guard); no commits from this session (worktree clean at abaf175) and no GitHub posts.

[STANDARDS R393R]
I reviewed PR #404 at abaf175 on the STANDARDS axis only. I wrote my pre-diff expectation first, then read every PR text through guard_text.py (exit 0 each time) and checked the diff against AGENTS.md, ARCHITECTURE.md, Fowler's smells and the wrapper's never-raises and transparency contract. Nothing Critical or Required: the contract holds (the new OSError sources land in the unchanged except tuple, and the exit code is still the child's), #388 no-create and the one lock order hold, the three layers stay separate, the tautology guard passes, and every cited reference re-verifies. The one false premise is N1: the manifest at u393r-manifest.json:33 says exists() returns False on OSError, but on py313 I reproduced it raising PermissionError 13, and the conclusion holds anyway; the other two Nits are a sidecar_lock docstring that describes its caller (evidence-run.py:138) and a serialize-before-truncate comment that lost its referent (:211). Optional: O1, the retry loop makes append_record a Long Function (:192); O2, fix commit 305c0c5 has no GREEN receipt, though precedent is mixed and I found no written receipt-style rule. Four FYIs are in the report. I made no commits (HEAD is still abaf175, the tree is clean, git log --all --grep for my session id returns 0) and posted nothing to GitHub; nothing is left on this axis, and no rerank or verdict is given.
