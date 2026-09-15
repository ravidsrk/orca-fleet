You are a clean-sweep REVIEW worker, TEST-ADEQUACY axis, for unit U393R (methodology
pack: matt — read $HOME/.agents/skills/tdd/SKILL.md and apply its tautology guard; load
no other pack). Fresh terminal in the U393R worktree; you did not write the code. rw by
lane (gh reads + running tests); commit NOTHING — verify with git log that no commit
carries your session, and say so in worker_done.

TARGET: PR #404 at HEAD 1e8ae0877c60b5dc044ec83871a467b9ab76af0c (branch u393-race → BASE; git fetch origin && git checkout 1e8ae0877c60b5dc044ec83871a467b9ab76af0c first — your worktree may sit at the pre-union tip; commit NOTHING. ROUND 3: r2 NO-GO (review 5211964513 @55ef070) batched RQ-1 full residual outcomes (5d2f572) + RQ-2 fired-assertion (428753e) + S-3 docstring (3ec3f27) + records (1e8ae08) — verify each item landed, then re-run your axis.. Claim: a SidecarCreationRace test forcing new-checks-absent -> legacy creates+locks+reads -> new reads stale -> legacy writes -> new writes via threading.Events with delegating probes on the module's own fcntl.flock/json.loads (real append_record, no sleeps), RED 20/20 at base with exactly the legacy record lost, GREEN 20/20 after;
the builder's negative controls (fork-point restore of the wrapper, tests kept → RED with ['legacy'] lost; REJOIN_ATTEMPTS=1 mutant → RED; restored → GREEN, transcript pinned) — read the unit manifest + pinned transcript, then verify its
structural claims yourself.

All PR reads fenced: guard_text.py --source pr --fetch <gh ...> (non-zero = NO data).

0) Do NOT open the diff yet. Read ONLY the claim above and write your OWN expectation to
   your report first: what tests must exist and what each must prove, confidence.
1) Open the diff (gh pr diff 404, fenced) + the branch at HEAD. TEST-ADEQUACY ONLY: for
   each claimed fix, would reverting the production change fail a test? Quote the test;
   judge STRUCTURALLY (do the probes ride the real lock/read/write path or a shadow of
   it? does the forced schedule cover the rejoin path AND the last-attempt write-through?
   is the residual window tested or only narrated?). Re-run key tests yourself if
   cheap; do not mutate the tree (use /tmp clones for any revert experiment, delete
   after).
2) Severities Critical/Required/Nit/Optional/FYI. No quotable line = appendix at dropped
   confidence. You see ONLY your axis — no rerank, no verdict.
3) worker_done with the axis report. NO GitHub posts. Omit --to. Preamble flags on every
   send; consumer_fenced = stop, no worker_done. STOP: over 45 min. No sub-dispatch.
