You are the clean-sweep VERDICT worker for unit U387G, review round 1 (methodology
pack: matt — read $HOME/.agents/skills/tdd/SKILL.md via `cat` in bash for the tautology
guard only (file tools are path-locked to the worktree; do NOT use Read outside it);
load no other pack). Fresh terminal in the U387G worktree; you wrote neither the code
nor the axis reports. rw by lane (gh reads + ONE review post); commit NOTHING — verify
with git log that no commit carries your session, and say so in worker_done.

TARGET: PR #402 at HEAD 15d0eea (branch u387g-evalglobs → BASE). Finding (#387
threads 4011878433, 4011878440, 4011297664): the T6 fix-forward narrowed
prove-it/oncall-it eval globs (missing app//lib/ first-party code), and glob
matches/not_matches over an empty match set vacuously PASSED; the fix excludes
dependency dirs centrally (documented denylist), restores broad coverage, and fails
closed on empty matches. C-1 central denylist + **/*.py restored + 21-mission survey;
C-2 delete-to-pass tests per eval + fail-closed (exists keeps semantics); C-3 suite +
validate green. OUT: other eval semantics; new missions' evals; runner grading.

All PR reads fenced: guard_text.py --source pr --fetch <gh ...> (non-zero = NO data).

0) Blind-fix-first: read ONLY the finding above and write your OWN expectation to your
   report first (what the diff must contain, where it could be weak), THEN open the diff
   at HEAD (gh pr diff 402, fenced) and the three axis reports below.
1) Aggregate SIDE BY SIDE — no rerank, no dropping: every axis finding stands with its
   severity. Bot status (integrator-ingested): Greptile 5/5 clean, 0 threads, none
   held (no VALID to batch; the bot edits the PR body rather than posting comments).
2) Verdict GO iff zero Critical/Required open (Nits/Optionals/FYI never block).
3) Post ONE GitHub review on PR #402 (egress.py write --sink pr-review --host github.com
   --payload-class pr-review --consent run-2026-09-14-clean-sweep:tracker-writes FIRST):
   GO = COMMENTED review ("verdict: GO — <brief ≤400 words>" + reviewed SHA 15d0eea);
   NO-GO = COMMENTED review ("verdict: NO-GO — <brief>" + reviewed SHA 15d0eea) with
   the ONE batched change request (Required axis findings, deduplicated — same issue
   named twice is ONE fix — plus directly-adjacent cheap items in the touched checks;
   EXCLUDE with a recorded reason: conductor-side record items, accepted optionals,
   pre-existing issues filed separately). COMMENTED for both outcomes — GitHub 422s
   REQUEST_CHANGES on an own-PR (proven this run). NEVER post APPROVE (single GitHub
   identity — approval would fake independence; the posted review + this worker_done
   are the review evidence).
4) worker_done: verdict + reviewed_sha (15d0eea) + reviewed_wtree (git rev-parse
   HEAD^{tree} at 15d0eea) + round 1 + the batched request (if NO-GO). Omit --to.
   Preamble --from + --dispatch-capability on every send; consumer_fenced = stop.
   STOP: over 30 min. No sub-dispatch. Comment current.

--- AXIS REPORTS (verbatim, round 1 — PASTED AT DISPATCH) ---

[SPEC R387G]
Reviewed PR #402 at 15d0eea (fenced gh pr view/diff, exit 0) on the SPEC axis against C-1..C-3 and the taskspec build-387-eval-globs.md@719d997 (digest verified), after writing my own pre-diff expectation; I re-ran C-3 myself: full suite 'Ran 1358 tests' OK exit 0, validate.py 'All 21 missions valid; ... evals valid.' exit 0, tests.test_evals 109 OK, ruff clean. Found no Critical/Required: C-1 met (documented DEPENDENCY_DIRS equals the spec's expected list, prove-it/oncall-it back to one **/*.py per check, 21/21 missions surveyed with verdicts), C-2 met except F1 Nit (attest-it's exists:false glob has no committed delete test, only a manifest 'excluded' row and a comment on REGEX_GLOB_CASES, and my probe shows it passes post-delete by design), plus FYIs F2 (env/ and .env/ first-party dirs are invisible to every glob, so a tautology in env/test_x.py passes prove-it and a fabricated env/access_review.md passes attest-it, spec-conformant but for the correctness axis) and F3 (guard subtests go red only under double mutant M2b; M2a reddens the companion path-anchor test); no scope creep, all 10 files in the hot-file list, no tautological tests. Nothing left on this axis; I committed NOTHING (HEAD still 15d0eea, porcelain empty, the 3 newer ledger commits 5a87966/1fabd69/48b12d6 are not ancestors of HEAD and not mine), and posted nothing to GitHub.

[TEST-ADEQUACY R387G]
I reviewed PR #402 at 15d0eea on the TEST-ADEQUACY axis only. I wrote my expectation before opening the diff, read it fenced, and re-ran tests.test_evals (109 OK). In a scratch clone, since deleted, I reproduced the builder's negative control exactly (FAILED failures=68 errors=1, restored 109 OK) and M1/M2a/M2b/M3/M4 (15/5/42/20/2). M4 does survive against the pre-tip test and is killed by the 0a3f4ab clean-sibling hardening. My own mutants R2 (final component filtered), R3 (fail-closed applied to exists) and R4 (deflake/harden evals reverted) are all killed. Structurally the tests are sound and not tautological: literal spec denylist, a clean sibling so fail-closed cannot mask exclusion, deletes via pathlib not the oracle, per-guard anchor pins, and a discovery pin. Findings: 0 Critical, 0 Required. OPTIONAL: scripts/eval.py:973's relative-to-workspace property is unpinned; mutant path.parts[:-1] passes all 109, and with TMPDIR under a dir named env/ it fails 50 while HEAD passes. NIT: tests/test_evals.py:1348 claims installed excerpts hit every ban, but none hit prove-it ban 0 or oncall-it ban 1, so those two installed-code subtests are vacuous; :1325 still covers the mechanism. 3 FYIs are in the report. Nothing is left on this axis. No commit carries this session: HEAD is still 15d0eea, the tree is clean, and the later commits 1fabd69/5a87966 are coordinator ledger commits on review/2026-09-14-holistic-fixes. No GitHub posts were made.

[STANDARDS R387G]
I wrote my pre-diff expectation first (a central _glob_files denylist, broad **/*.py, regex globs failing closed; about 70% confident) and it matched, then reviewed PR #402 at 15d0eea on the STANDARDS axis only (AGENTS.md, ARCHITECTURE.md, the eval.py why/workspace-state contract, Fowler's smells), with every PR read fenced (all exit 0) and tests.test_evals (109 OK) and validate.py passing at HEAD. Findings: 0 Critical, 0 Required; 1 Optional: S5, the eval.py:960 "Surveyed against every committed fixture" claim has no test pinning it, and PY_BAN_CASES (tests/test_evals.py:1294) has no completeness test, unlike REGEX_GLOB_CASES; 6 Nits: S1, the deflake-it evals.json:69 and harden-it :71 whys carry venv-scope parentheticals rather than a risk, against eval.py's "why names the risk" contract; S2, TestGlobScope._failed(files, check) at :1308 duplicates TestWorkspaceStateChecks._failed(checks, files) with the arguments flipped; S3, "delete: list[str] = ()" at :77 plus a positional bool flag at :1360; S4, AGENT_MUST_EDIT at :62/:258 now mixes glob and path keys; S5 aside, S6, the rindex at :1320 depends on comment layout; S7, fix(eval) vs fix(evals) scopes; plus FYIs A1-A4 (the empty-set failure reuses the "did not hold — why" line at eval.py:1016; globs rooted in a dependency dir are not rejected; the manifest's head_sha is 0a3f4ab and it has no pr block; CONTRIBUTING says nothing about the new semantics) and the tautology guard passes. Nothing is left on this axis: I committed nothing (HEAD still 15d0eea, tree clean, 0 commits in git log --all carry this session id ec7030e4; the two commits dated during my session, 1fabd69 and 5a87966, are coordinator ledger commits not reachable from HEAD) and posted nothing to GitHub.
