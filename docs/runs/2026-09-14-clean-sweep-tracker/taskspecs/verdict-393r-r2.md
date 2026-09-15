You are the clean-sweep VERDICT worker for unit U393R, review round 2 (methodology
pack: matt — read $HOME/.agents/skills/tdd/SKILL.md via `cat` in bash for the tautology
guard only (file tools are path-locked to the worktree; do NOT use Read outside it);
load no other pack). Fresh terminal in the U393R worktree; you wrote neither the code
nor the axis reports. rw by lane (gh reads + ONE review post); commit NOTHING — verify
with git log that no commit carries your session, and say so in worker_done.

TARGET: PR #404 at HEAD 55ef0704d0498a16c4d3034f537ab3ddffdffdab (branch u393-race → BASE).
Finding (#387 thread 4012510839): the #393 sidecar join is check-then-act — a legacy
wrapper can create and lock <manifest>.lock after the absence check and overlap the new
append under the other lock, silently losing a record; the fix re-checks before the
truncate and, if one appeared, releases the manifest lock, joins the sidecar (blocking)
and re-reads, bounded, under the one documented lock order, never creating a sidecar
(#388 kept). C-1 deterministic forced-schedule regression test (RED-then-GREEN, no bare
sleeps, real module paths); C-2 the fix preserving #388 + order + never-raises +
steady-state, residual documented; C-3 full suite + validate green. OUT: lock-free
peers; changing #388; the steady-state protocol.
ROUND 2: r1 NO-GO (review 5211486225 @abaf175) batched M1/M2 killer tests + text fixes;
this tip adds the F-1/F-2+F-3 killers, F-4 text, badge 1381, records (6 commits,
zero production behavior change). Re-verify the batch landed; judge only what is
still open.

All PR reads fenced: guard_text.py --source pr --fetch <gh ...> (non-zero = NO data).

0) Blind-fix-first: read ONLY the finding above and write your OWN expectation to your
   report first (what the diff must contain, where it could be weak), THEN open the diff
   at HEAD (gh pr diff 404, fenced) and the three axis reports below.
1) Aggregate SIDE BY SIDE — no rerank, no dropping: every axis finding stands with its
   severity. DEDUPLICATE same-root findings into ONE fix (record the merge — e.g. the
   F-1 stand-in fragility named by both TEST N-1 and STANDARDS S-1 is one item).
   Bot status: r1 Greptile P1 4015794383 stands ACCEPTED with reason (disclosed
   residual, #388 bars closure). ALSO poll PR #404 for any bot review comments posted
   after review 5211486225 and ingest each as VALID-or-FALSE-POSITIVE with a recorded
   reason (a new VALID joins the batch as Required unless refuted).
2) Verdict GO iff zero Critical/Required open (Nits/Optionals/FYI never block).
3) Post ONE GitHub review on PR #404 (egress.py write --sink pr-review --host github.com
   --payload-class pr-review --consent run-2026-09-14-clean-sweep:tracker-writes FIRST):
   GO = COMMENTED review ("verdict: GO — <brief ≤400 words>" + reviewed SHA 55ef070);
   NO-GO = COMMENTED review ("verdict: NO-GO — <brief>" + reviewed SHA 55ef070) with
   the ONE batched change request (Required axis findings, deduplicated, plus
   directly-adjacent cheap items in the touched checks; EXCLUDE with a recorded reason:
   conductor-side record items, accepted optionals, pre-existing issues filed
   separately). COMMENTED for both outcomes — GitHub 422s REQUEST_CHANGES on an
   own-PR (proven this run). NEVER post APPROVE (single GitHub identity — approval
   would fake independence; the posted review + this worker_done are the review
   evidence).
4) worker_done: verdict + reviewed_sha (55ef070) + reviewed_wtree (git rev-parse
   HEAD^{tree} at 55ef070) + round 2 + the batched request (if NO-GO). Omit --to.
   Preamble --from + --dispatch-capability on every send; consumer_fenced = stop.
   STOP: over 30 min. No sub-dispatch. Comment current.

--- AXIS REPORTS (verbatim, round 2 — PASTED AT DISPATCH) ---

[SPEC R393R-r2]
SPEC-axis review of PR #404 at 55ef0704 (fenced gh reads, exit 0; headRefOid == HEAD). All six round-2 commits landed as claimed, verified by my own runs: M1/M2/M3 re-run in a scratch worktree are each RED on the F-1/F-2 killers; bd6b310 is AST-identical to abaf175 modulo docstrings; gen-badges --check exits 0 at 1381; the negctrl sha256 matches its pin. C-1 is MET: the fork-point file goes 5/5 RED losing exactly [legacy]; Events plus liveness bounds, no sleeps in the new classes; real append_record; the legacy stand-in matches e04b0c2; expected values are literals. C-3 is MET: validate.py exit 0 and the full suite ran 1381 tests OK, exit 0, tree clean. There is no scope creep. C-2 is MET (look before truncate; continue closes the manifest before the blocking sidecar_lock; bound 3; no-create; lock order; except tuple; MixedVersionRollout unchanged and green), with ONE Required finding against spec line [the RESIDUAL window documented honestly in code + manifest]. The docstring line [between the last look and the close that flushes this write can still silently drop one of] and noticed_not_touched[0] name only a dropped record. My forced-schedule demo (real append_record, legacy reads after the look and writes between truncate and write) leaves the manifest CORRUPT (json Extra data): the tearing append prints no WARNING and every later append warns and records nothing, so the outcome set is incomplete. There are 2 FYIs: the last-attempt write-through with an unjoined sidecar is a second loss path named only in the REJOIN_ATTEMPTS comment, and the manifest head_sha is acdf998 with commits[-1].sha pending, per the re-bind protocol. I committed and posted nothing: HEAD and the branch are still 55ef0704 and no commit carries this session. The scratch worktrees are removed; the report is at the report path.

[TEST-ADEQUACY R393R-r2]
Did: verified every r1 batch item landed at 55ef070 (adce115 F-1 killer, 53c4894 F-2/F-3 killer, bd6b310 AST-identical modulo docstrings, badge 1381 == countTestCases 1381, acdf998 docstring, 55ef070 records); ran the 3 new tests 10/10 OK at HEAD; in a deleted git-archive scratch copy I reproduced NC-1, NC-2, M1, M2 and M3 exactly as the transcript says, and killed 4 extra mutants (X3 absent-yields-True, X4 LOCK_NB join, X5 look before parse, X7 warn-instead-of-write). Found: the probes ride the real append_record lock/read/write path, and the forced schedules cover the rejoin, the blocking join and the last-attempt write-through, with literal expected lists (tautology guard passes). But Nit N-1: the F-1 test's module-level open stand-in goes vacuous under a behaviour-neutral Path.open refactor, and with M1 applied all 31 tests pass (X8b), contradicting the manifest's 'neither passes silently'; fix by asserting the stand-in fired. Nit N-2: X6, the look moved before json.dumps, survives. Optional O-1: dropping 'not joined' (X1) survives, costing 3 passes per joined append with no record loss. Optional O-2: the residual window is narrated only, though a scratch probe confirms the docstring (legacy-last loses 'new', legacy-first loses 'legacy', no hang). Left: nothing on this axis; I committed nothing (worktree clean at 55ef070; the only post-start commits 1e30715/7655e7d are coordinator ledger commits on the base branch, not ancestors of HEAD), and I made no GitHub posts.

[STANDARDS R393R-r2]
I checked that all six round-2 items landed at 55ef070 (adce115, 53c4894, bd6b310 changing text only per an ast.dump compare with docstrings stripped, 0de1e87 with gen-badges --check exit 0, acdf998, 55ef070); at HEAD the module ran 31 tests OK and validate.py was green, and I then reviewed the STANDARDS axis against AGENTS/ARCHITECTURE/CONTRIBUTING, Fowler smells and the never-raises contract, all PR reads fenced (exit 0). S-1 Required: the F-1 killer patches the builtin open name (tests/test_evidence_run.py:526), and in a scratch copy a refactor that changes no behaviour (sidecar opened via os.fdopen(os.open(...))) left F-1 green and let the M1 mutant survive all 31 tests, so the manifest line 264 claim 'neither passes silently' is false; S-2 Optional covers duplicated test scaffolding, S-3 Nit the acdf998 subject saying it names both stand-ins when the docstring names none (:495), S-4 Optional append_record nesting (:214), and S-5 Nit round-2 commits with no receipt body; the never-raises contract, transparency, #388 no-create, lock order, three-layer separation, the tautology guard and every cited reference all check out. Nothing is left on this axis: I committed nothing (HEAD 55ef070, clean tree, the reflog shows only my checkout; 1e30715/7655e7d are coordinator ledger commits on BASE), reattached the worktree to ravidsrk/u393-race, and the full report with verbatim quotes and the FYI appendix is at the report path.
