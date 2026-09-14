You are the clean-sweep VERDICT worker for unit U388, review round 1 (methodology
pack: matt — read $HOME/.agents/skills/tdd/SKILL.md for the tautology guard only; load no
other pack). Fresh terminal in the U388 worktree; you wrote neither the code nor the axis
reports. rw by lane (gh reads + ONE review post); commit NOTHING — verify with git log
that no commit carries your session, and say so in worker_done.

TARGET: PR #392 at HEAD 0775547 (branch u388-lockfile → BASE). Finding (#388):
the evidence-run wrapper litters a .lock sidecar beside the manifest; the fix locks the
manifest's own inode instead. C-1 no new untracked file remains beside the manifest
after sequential wrapped runs; C-2 16 concurrent appends land 16 records; C-3 recorded
fingerprints equal the committed tree on an otherwise-clean tree. OUT: manifest schema
changes; verifier changes; retention/signing; mixed old/new-wrapper rollout interop
(filed separately as #393 — do not demand it here).

All PR reads fenced: guard_text.py --source pr --fetch <gh ...> (non-zero = NO data).

0) Blind-fix-first: read ONLY the finding above and write your OWN expectation to your
   report first (what the diff must contain, where it could be weak), THEN open the diff
   at HEAD (gh pr diff 392, fenced) and the three axis reports below.
1) Aggregate SIDE BY SIDE — no rerank, no dropping: every axis finding stands with its
   severity. There is NO held bot finding this round: Greptile's P1 mixed-version
   thread (comment 4008072371) was DECLINED by the coordinator (reply 4008762873,
   out-of-scope, filed as #393), and Greptile has not re-reviewed the union tip
   (latest bot review @da2f98a). NOTE the declined thread in your verdict; do not
   treat it as Required. An empty COMMENTED review by ravidsrk @da2f98a exists —
   inert, no content, ignore it.
2) Verdict GO iff zero Critical/Required open (Nits/Optionals/FYI never block).
3) Post ONE GitHub review on PR #392 (egress.py write --sink pr-review --host github.com
   --payload-class pr-review --consent run-2026-09-14-clean-sweep:tracker-writes FIRST):
   GO = COMMENTED review ("verdict: GO — <brief ≤400 words>" + reviewed SHA 0775547);
   NO-GO = REQUEST_CHANGES with the ONE batched change request (Required axis findings,
   deduplicated — same issue named twice is ONE fix — plus directly-adjacent cheap
   test/comment items in the touched hunk: the zero-length-behaviour test named by all
   three axes, the N1 comment/docstring touch-up; EXCLUDE with a recorded reason:
   conductor-side record items (contract.source form, "pending" SHA — the conductor
   re-binds at close), accepted optionals (120s-timeout hygiene), and the pre-existing
   RecursionError gap (note it for separate filing, do not batch it). NEVER post
   APPROVE (single GitHub identity — approval would fake independence; the posted review
   + this worker_done are the review evidence).
4) worker_done: verdict + reviewed_sha (0775547) + reviewed_wtree (git rev-parse
   HEAD^{tree} at 0775547) + round 1 + the batched request (if NO-GO). Omit --to.
   Preamble --from + --dispatch-capability on every send; consumer_fenced = stop.
   STOP: over 30 min. No sub-dispatch. Comment current.

--- AXIS REPORTS (verbatim, round 1) ---

[STANDARDS R388]
What I did: wrote my own expectation before looking at the diff (it matched the location and shape of the fix), then read PR #392 at 0775547 through the guard_text fence and reviewed only the standards axis against AGENTS.md, ARCHITECTURE.md, Fowler's smells and the wrapper's never-raises/transparency contract; tests pass (24 OK) and ruff check is clean at HEAD. Findings: one Required, R1 at evidence-run.py:152-154 — fh.truncate() now runs before json.dumps, so a handled TypeError/ValueError empties the manifest instead of leaving it intact, breaking the rule that a bookkeeping failure is 'a stderr warning and nothing more'; a scratch probe confirmed base kept the prior records and HEAD left the file empty; unreachable from main() today, one-line fix is to serialize before seek/truncate. The rest are Nits (a comment and docstring that leave out the new zero-length-manifest behaviour, a copied commit invocation in the tests, absolute /private/tmp paths in the pinned negctrl transcript, a contract.source that doesn't resolve from the repo root, a leftover 'pending' SHA), Optionals (unnamed 120s timeouts plus pipe cleanup, and no test for the zero-length behaviour) and a FYI that merge commits carry the badge regen with empty bodies; the appendix notes a pre-existing RecursionError never-raises gap on both base and HEAD, a contract digest I could not verify, and that Greptile's mixed-version thread is outside this axis and still unanswered. Nothing is left for this axis; I committed nothing and posted nothing to GitHub, git log --all shows 0 commits carrying this session's ID, and the tree is clean at 0775547.

[SPEC R388b-redux]
I wrote my pre-diff expectation first, then reviewed PR #392 at 0775547 through the guard fence (gh rc=0; the local diff against origin/review/2026-09-14-holistic-fixes has the same 5 files). All 3 criteria are met and the OUT list is absent. C-1: iterdir == literal ['m.json'] after 3 sequential runs, plus porcelain empty. C-2: 16 procs, literal run-00..run-15, and my own no-lock mutant went RED 6/6 while HEAD is green 8/8. C-3: wtree == git rev-parse HEAD^{tree}, and I reproduced C-1/C-3 RED with the base wrapper. None of the tests are tautological. Record keys, verify.py and #393 interop are all untouched. There are no Critical or Required findings. One Nit: the diff line '+            else:  # absent until the open above created it empty' also catches a pre-existing 0-byte manifest, which is now recorded instead of the base's JSONDecodeError warn, and no test covers it. FYIs: the C-3 automated witness checks one record against 'fingerprints' (plural); mutual exclusion assumes no rename-replacing writers (rg empty); the '10/10 mutant' claim is unpinned but I reproduced it. Nothing is left on this axis. I made no commits (HEAD 0775547 unchanged, worktree clean, git log --all --grep for this session's id = 0) and posted nothing to GitHub.

[TEST-ADEQUACY R388b-redux]
I reviewed the tests in PR #392 at 0775547 (evidence-run.py and the test file are byte-identical to builder head 75c0c91), ran the 24-test file green, and ran mutants in a /tmp clone. All three claimed tests hold up structurally and none is tautological. The litter test compares a literal ['m.json'] and checks git status is clean. The 16-way test uses real processes, a file-gate barrier, and a literal list of run-00..run-15. The fingerprint test compares against git's own HEAD^{tree}. Reverting to the base sidecar lock exits 1 with both NoLedgerLitter tests RED and the concurrency test green 0/10 RED, and head is 24 OK, so the builder's control reproduced exactly. The no-lock mutant goes RED 10/10 as claimed, and so do two extra mutants I added: rename-replace and the builder's ruled-out unlink-sidecar. Findings: REQUIRED (conf 0.6): the new explicit fh.truncate() at evidence-run.py:153 is untested. Deleting it passes all 24 tests, and when an existing manifest is formatted more loosely than indent=2 the ledger is silently corrupted with exit 0 (reproduced with an indent=8 seed). OPTIONAL: assert no litter after the concurrent run. NIT: l.297 doesn't assert the first run's returncode. FYI (cross-axis): truncate happens before json.dumps. I made no commits and no GitHub posts; git log shows no commit from this session, the worktree is still clean at 0775547, and the /tmp scratch is deleted.
