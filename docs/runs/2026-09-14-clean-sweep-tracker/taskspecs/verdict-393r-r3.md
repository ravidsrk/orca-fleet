You are the clean-sweep VERDICT worker for unit U393R, review round 3 (methodology
pack: matt — read $HOME/.agents/skills/tdd/SKILL.md via `cat` in bash for the tautology
guard only (file tools are path-locked to the worktree; do NOT use Read outside it);
load no other pack). Fresh terminal in the U393R worktree; you wrote neither the code
nor the axis reports. rw by lane (gh reads + ONE review post); commit NOTHING — verify
with git log that no commit carries your session, and say so in worker_done.

TARGET: PR #404 at HEAD 1e8ae0877c60b5dc044ec83871a467b9ab76af0c (branch u393-race → BASE).
Finding (#387 thread 4012510839): the #393 sidecar join is check-then-act — a legacy
wrapper can create and lock <manifest>.lock after the absence check and overlap the new
append under the other lock, silently losing a record; the fix re-checks before the
truncate and, if one appeared, releases the manifest lock, joins the sidecar (blocking)
and re-reads, bounded, under the one documented lock order, never creating a sidecar
(#388 kept). C-1 deterministic forced-schedule regression test (RED-then-GREEN, no bare
sleeps, real module paths); C-2 the fix preserving #388 + order + never-raises +
steady-state, residual documented; C-3 full suite + validate green. OUT: lock-free
peers; changing #388; the steady-state protocol.
ROUND 3: r2 NO-GO (review 5211964513 @55ef070) batched RQ-1 full residual outcomes +
RQ-2 fired-assertion + S-3 docstring; this tip carries those three plus records (4
commits, zero production behavior change). Re-verify the batch landed; judge only
what is still open.

All PR reads fenced: guard_text.py --source pr --fetch <gh ...> (non-zero = NO data).

0) Blind-fix-first: read ONLY the finding above and write your OWN expectation to your
   report first (what the diff must contain, where it could be weak), THEN open the diff
   at HEAD (gh pr diff 404, fenced) and the three axis reports below.
1) Aggregate SIDE BY SIDE — no rerank, no dropping: every axis finding stands with its
   severity. DEDUPLICATE same-root findings into ONE fix (record the merge).
   Bot status: r1 Greptile P1 4015794383 stands ACCEPTED with reason (disclosed
   residual, #388 bars closure). ALSO poll PR #404 for any bot review comments posted
   after review 5211964513 and ingest each as VALID-or-FALSE-POSITIVE with a recorded
   reason (a new VALID joins the batch as Required unless refuted).
2) Verdict GO iff zero Critical/Required open (Nits/Optionals/FYI never block).
3) Post ONE GitHub review on PR #404 (egress.py write --sink pr-review --host github.com
   --payload-class pr-review --consent run-2026-09-14-clean-sweep:tracker-writes FIRST):
   GO = COMMENTED review ("verdict: GO — <brief ≤400 words>" + reviewed SHA 1e8ae08);
   NO-GO = COMMENTED review ("verdict: NO-GO — <brief>" + reviewed SHA 1e8ae08) with
   the ONE batched change request (Required axis findings, deduplicated, plus
   directly-adjacent cheap items in the touched checks; EXCLUDE with a recorded reason:
   conductor-side record items, accepted optionals, pre-existing issues filed
   separately). COMMENTED for both outcomes — GitHub 422s REQUEST_CHANGES on an
   own-PR (proven this run). NEVER post APPROVE (single GitHub identity — approval
   would fake independence; the posted review + this worker_done are the review
   evidence).
4) worker_done: verdict + reviewed_sha (1e8ae08) + reviewed_wtree (git rev-parse
   HEAD^{tree} at 1e8ae08) + round 3 + the batched request (if NO-GO). Omit --to.
   Preamble --from + --dispatch-capability on every send; consumer_fenced = stop.
   STOP: over 30 min. No sub-dispatch. Comment current.

--- AXIS REPORTS (verbatim, round 3 — PASTED AT DISPATCH) ---

[SPEC R393R-r3]
SPEC-axis review of PR #404 at 1e8ae08, all PR reads fenced (rc=0). I wrote my expectation before opening the diff and the diff matched it. All r2 items landed: RQ-1 (5d2f572, four residual outcomes plus the second loss path, in the docstring and the manifest), RQ-2 (428753e, literal fired-log assert at test:540), S-3 (3ec3f27), and the records (1e8ae08). I checked each criterion myself. C-1 MET: the base production file in a scratch copy goes RED 5/5, each run 'Lists differ: [legacy] != []'; HEAD is GREEN 31/31. C-2 MET: the look at evidence-run.py:229 continues into a blocking rejoin, bounded at REJOIN_ATTEMPTS=3; the sidecar opens rb with no O_CREAT; lock order holds; nothing raises; the steady-state test is untouched (numstat 231/0). C-3 MET: full suite 'Ran 1381 tests in 255.567s / OK' and validate.py green. No scope creep. No Critical or Required findings. Nits: N-1 evidence-run.py:183 (and manifest intent.why:46) says the payload's bytes 'reach the file only as the with closes it', but I measured writes of 9000+ chars landing inside fh.write(), and real manifests here are 42-128 KB; the four outcomes still hold. N-2 evidence-run.py:190 names only the 'legacy rewrite is the longer' tear, not the shorter-or-equal case, which is a silent legacy drop. N-3 manifest:231 'unforced-unreachable in practice (0/60 unforced)' overstates what the evidence supports. FYI: head_sha is 3ec3f27 and commits[-1] is 'pending', awaiting the coordinator's re-bind. Nothing is left on this axis. This session made no commit: newest commit is 1e8ae08 at 21:05:39, before the session started; the only reflog entry since is the prescribed detach checkout; tree clean; nothing posted to GitHub.

[TEST-ADEQUACY R393R-r3]
I checked the three round-3 items at 1e8ae08 and all landed: RQ-1 is text only (AST identical to 55ef070 once docstrings are stripped), the RQ-2 fired-log assertion at tests/test_evidence_run.py:540 fails under REFACTOR, REFACTOR+M1 and M1 alike, and S-3's docstring names every stand-in. I also re-ran the axis in throwaway /tmp clones: HEAD passes 31/31, and SidecarCreationRace goes RED 20/20 with exactly ['legacy'] lost once the fork-point wrapper is restored. REJOIN_ATTEMPTS=1 goes RED on all three race tests, the probes run through the real flock and json.loads calls, a stalled schedule fails instead of passing (FLOCKALIAS RED at 33.8s), and the expected values are literals, so nothing is tautological. Findings: no Critical or Required. One Optional: dropping 'not joined', or pointing the look at the manifest instead of the sidecar, passes 31/31 (perf-only), because nothing pins the one-attempt-when-unraced invariant. Four FYIs: r2 N-2 (look before json.dumps) still survives; the residual window is only described in the docstring and forced by a harness outside the suite; lock order is pinned only incidentally, by F-1's attempt log; and the :540 literal is tied to REJOIN_ATTEMPTS=3. I skipped the full 1381-test suite, made no commits (git log since session start shows only the coordinator's base-branch commits 7776df7, d61b3dc and d706511), made no GitHub posts and deleted the clones.

[STANDARDS R393R-r3]
I verified the r3 batch on PR #404 at 1e8ae08: RQ-1 landed (5d2f572: the docstring at :181-205, noticed_not_touched[0] and the RESIDUAL decision all name the tear and the second loss path), RQ-2 landed (428753e: the literal ×3 fired log at tests:540, and 'neither passes silently' is gone from the manifest), S-3 landed (3ec3f27: the docstring names open, fcntl.flock and json.loads), the records landed (1e8ae08), and every r3 commit carries a receipt body; I ran the STANDARDS axis against AGENTS.md, ARCHITECTURE.md and CONTRIBUTING.md, Fowler's smells and the never-raises contract; tests.test_evidence_run passed 31 OK and validate.py was green at HEAD, and 428753e, 5d2f572 and 3ec3f27 each build alone (git archive, 31 OK, validate green). Findings: N-1 Nit, review-process ids are new in source (zero at base 666d55d): evidence-run.py:170 '(#387 thread 4012510839)', tests:492 '(V393R-r1 R-1, R-2)', and tests:499 '(V393R-r2 RQ-2)', added in r3; the thread resolves, but the V-labels resolve only via the run manifest; N-2 Nit, tests:541 'the open stand-in was bypassed: the last attempt was never reached' names one cause, though a changed REJOIN_ATTEMPTS fails the same assertion; O-3 Optional, carried and possibly overlapping the accepted r2 S-2/S-4: wait/legacy/thread/TIMEOUT/module-load are duplicated across the two forced-schedule tests (tests:434/:560, :454/:582); FYI, the residual prose is in three places, as RQ-1 required; the never-raises and transparency contract holds (the new exists() raises land in the existing except tuple, continue releases the manifest lock before the sidecar, the loop cannot fall through at a bound of 3); the tautology guard passes, the taskspec refs resolve as path@commit on base (checked and dropped), and the appendix holds A-1 (a bound below 1 would record and warn nothing, ~20%) and A-2 (subject length, no rule, ~25%). Nothing is left on this axis: no rerank or verdict per the task, no GitHub posts, full suite not run (SPEC axis; 1e8ae08 records 1381 OK); this session committed nothing (HEAD 1e8ae08, clean tree, git rev-list 1e8ae08..HEAD empty), and the three commits made in my window (7776df7, d61b3dc, d706511) are the coordinator's, on review/2026-09-14-holistic-fixes.
