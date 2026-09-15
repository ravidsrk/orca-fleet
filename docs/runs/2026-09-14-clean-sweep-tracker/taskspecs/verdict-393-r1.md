You are the clean-sweep VERDICT worker for unit U393, review round 1 (methodology
pack: matt — read $HOME/.agents/skills/tdd/SKILL.md via `cat` in bash for the tautology
guard only (file tools are path-locked to the worktree; do NOT use Read outside it);
load no other pack). Fresh terminal in the U393 worktree; you wrote neither the code
nor the axis reports. rw by lane (gh reads + ONE review post); commit NOTHING — verify
with git log that no commit carries your session, and say so in worker_done.

TARGET: PR #400 at HEAD 7630815 (branch u393-sidecar-lock → BASE). Finding (#393):
during a mixed-version rollout, an old (sidecar-discipline) wrapper and the new
(inode-lock) wrapper share no lock and can lose records; the fix joins a PRE-EXISTING
sibling sidecar (never creates one) before the inode lock, under one documented lock
order, plus a mixed-version concurrency test. C-1 pre-existing sidecar LOCK_EX (no
O_CREAT, absent=skip) then inode lock, one order; C-2 no run creates a sidecar; C-3
N+M mixed-version appends all land (stable, no bare sleeps); C-4 full suite + validate
green. OUT: lock-free peers; rollout docs; runbooks.

All PR reads fenced: guard_text.py --source pr --fetch <gh ...> (non-zero = NO data).

0) Blind-fix-first: read ONLY the finding above and write your OWN expectation to your
   report first (what the diff must contain, where it could be weak), THEN open the diff
   at HEAD (gh pr diff 400, fenced) and the three axis reports below.
1) Aggregate SIDE BY SIDE — no rerank, no dropping: every axis finding stands with its
   severity. Bot status (integrator-ingested, held VALID): [1] P1 thread 4012297723
   (u393-manifest.json:6-7): head_sha/commands[] bind tree 451cac2c (a74139b) not
   union-tip tree e53e0e4f — VALID as a fail-closed tree check will reject them;
   a74139b..7630815 is 6 docs/ledger paths, 0 under runtime/tests/scripts/assets;
   the rebind + re-recorded run is the close step the manifest's head_sha_role assigns
   to the coordinator. [2] P2 thread 4012297731 (evidence-run.py:134): a FIFO at
   <manifest>.lock blocks the O_RDONLY sidecar open — VALID, reproduced by the
   integrator (open(fifo,'rb') with no writer blocked >3s); low severity (needs a
   non-regular file at the sidecar path); sits beside manifest noticed_not_touched #2
   (non-openable sidecar not treated as absent).
2) Verdict GO iff zero Critical/Required open (Nits/Optionals/FYI never block).
3) Post ONE GitHub review on PR #400 (egress.py write --sink pr-review --host github.com
   --payload-class pr-review --consent run-2026-09-14-clean-sweep:tracker-writes FIRST):
   GO = COMMENTED review ("verdict: GO — <brief ≤400 words>" + reviewed SHA 7630815);
   NO-GO = COMMENTED review ("verdict: NO-GO — <brief>" + reviewed SHA 7630815) with
   the ONE batched change request (Required axis findings, deduplicated — same issue
   named twice is ONE fix — plus directly-adjacent cheap items in the touched checks;
   EXCLUDE with a recorded reason: conductor-side record items, accepted optionals,
   pre-existing issues filed separately). COMMENTED for both outcomes — GitHub 422s
   REQUEST_CHANGES on an own-PR (proven this run). NEVER post APPROVE (single GitHub
   identity — approval would fake independence; the posted review + this worker_done
   are the review evidence).
4) worker_done: verdict + reviewed_sha (7630815) + reviewed_wtree (git rev-parse
   HEAD^{tree} at 7630815) + round 1 + the batched request (if NO-GO). Omit --to.
   Preamble --from + --dispatch-capability on every send; consumer_fenced = stop.
   STOP: over 30 min. No sub-dispatch. Comment current.

--- AXIS REPORTS (verbatim, round 1 — PASTED AT DISPATCH) ---

[SPEC R393]
I wrote my expectation down before opening the diff, then reviewed PR #400 at 7630815 (fenced gh reads, exit 0) on the SPEC axis only against the pre-#388 writer e04b0c2, and reran it at HEAD myself: validate.py exit 0, full suite Ran 1351 OK exit 0, MixedVersionRollout+NoLedgerLitter 10/10 green. C-1 through C-3 are met at source: the sidecar is opened rb (no O_CREAT) and FileNotFoundError skips it, then flock sidecar, then flock inode, in one with-statement under a documented order; the path and flock primitive match e04b0c2, and the only other flock is egress.py on its own ledger. The C-2 test checks the sidecar path is absent on disk; C-3 runs 8 real-CLI appends plus 4x60 sidecar-only appends against a pre-touched sidecar and asserts a literal label set, with condition polls only and no bare sleeps; there is no scope creep and none of the OUT items. Findings: F1 Required, C-4 evidence bound to the wrong tree: the manifest line '"head_sha": "a74139bc28e871f08d88a7eeb0f59f67163d7e3e",' and all three command records bind tree 451cac2c, but PR head 7630815's tree is e53e0e4f, so C-4 is met in fact (my rerun) but its manifest witness must be rebound at close (coordinator-owned, as the manifest says). Also F2-F4, F6 FYI (order enforced by construction and not test-pinned; only FileNotFoundError counts as absent; a sidecar created after the absence check isn't joined; child polls have no deadline of their own) and F5 Nit (assertEqual(len(expected), 248) is a fixture self-check). This session made no commits: HEAD and the branch tip are still 7630815, the last reflog entry (11:00:35) predates my 11:14 start, and the tree was clean at start and end; nothing was posted to GitHub.

[TEST-ADEQUACY R393]
I wrote my expectation before opening the diff, then read the fenced PR #400 diff (head 7630815), the manifest and the negctrl transcript. I re-ran tests.test_evidence_run at HEAD (28 OK) and 51 mutation runs in scratchpad git-archive copies: NC-1 (fork-point wrapper) was RED 10/10 and NC-2 (O_CREAT) RED with exactly the 3 named failures, both reproduced; my own mutants were also RED 10/10 (sidecar released before the read-modify-write; sidecar unlinked after use), while HEAD was GREEN 10/10 with new-* records interleaved at ledger indices 21-74 of 248. The mixed-version test is not tautological: its old writer is an independent copy of e04b0c2 append_record, the expected set is built from literals (248 asserted) and compared as an exact multiset, and the no-creation guard checks the real sidecar path on disk. Findings: 0 Critical, 0 Required, 0 Nit; Optional O-1: the base RED depends on timing and nothing asserts the interleaving happened (tests/test_evidence_run.py:373-381), so a host where the old writers finish first would give a vacuous GREEN. FYI: the lock order is not pinned by any test (reversed-order mutant GREEN 10/10, harmless for this writer set); the narrow FileNotFoundError catch (EACCES or directory sidecar drops the record) is untested and disclosed; the C-2 guard is subsumed in sensitivity by the pre-existing #388 test. Left: I did not re-run the full 1351-test suite; I committed nothing (HEAD still 7630815, tree clean, reflog shows no move this session, scratch copies deleted) and made no GitHub posts.

[STANDARDS R393]
Reviewed PR #400 at 7630815 on the STANDARDS axis only. I wrote a pre-diff expectation, then read AGENTS/ARCHITECTURE/CONTRIBUTING, the fenced diff, the wrapper and tests at HEAD, and ran one probe. No Critical or Required findings: never-raises holds (every new raise site sits inside append_record's existing handler), three-layer separation and commit conventions hold (no trailers), and every checked reference resolves (e04b0c2 old-writer shape, taskspec digest, negctrl sha256). The Nit/Optional items are: S1 yield inside 'except FileNotFoundError' (probe confirmed misleading exception chaining), S2 a docstring line saying 'Not a sibling lockfile' beside the new sidecar lock, S3 a blocking FIFO open that could hang the transparency contract (duplicates Greptile), S4 no test for the unopenable-sidecar branch, S5 test literals that duplicate class constants plus a tautological len==248 check, S7 stale manifest refs ('pending' sha, 'nothing pushed', a local-only branch name), S8 the name 'peer'; FYI: S6 test overlap, S9 absolute builder paths (precedent exists), and off-axis, BASE moved to a41608e and is not contained in 7630815. I committed nothing: HEAD is still 7630815, the tree is clean, and no commit carries my session (newer commits under --all come from other worktrees sharing .git); I made no GitHub posts.
