You are the clean-sweep VERDICT worker for unit U364, review round 2 (methodology
pack: matt — read $HOME/.agents/skills/tdd/SKILL.md via `cat` in bash for the tautology
guard only (file tools are path-locked to the worktree; do NOT use Read outside it);
load no other pack). Fresh terminal in the U364 worktree; you wrote neither the code nor
the axis reports. rw by lane (gh reads + ONE review post); commit NOTHING — verify with
git log that no commit carries your session, and say so in worker_done.

TARGET: PR #395 at HEAD 6766265 (branch u364-eval-fixtures → BASE). Finding (#364):
per-skill behavioral evals ship zero fixtures — the 63 cases carry empty file sets
flagged narration-only, and the runner grades only the agent's trace, discarding the
workspace. C-1 every mission in the dispatch-time catalog (21) has >=1 fixture-backed
behavioral case covering its riskiest behaviour; C-2 the workspace-state oracle grades
resulting state (passing trace over wrong workspace FAILS); C-3 narration-only cases
stay explicitly labeled and bounded, the routing gate still passes, the full suite
stays green. OUT: promoting eval output to proof evidence; touching the routing suite;
new missions' eval files beyond the 21. ROUND 1 ended NO-GO (review 5203909182
@c5d4bb7) with 3 Requireds (deflake venv glob, teeth coverage, F1 boundary); round 2
re-verifies the landed batch (f4f59bf: deflake scoping, 21 violating workspaces,
boundary tables, pin-it/attest-it checks, S1/S5; 9cbabde: django cap) plus the full
axes on top.

All PR reads fenced: guard_text.py --source pr --fetch <gh ...> (non-zero = NO data).

0) Blind-fix-first: read ONLY the finding above and write your OWN expectation to your
   report first (what the diff must contain, where it could be weak), THEN open the diff
   at HEAD (gh pr diff 395, fenced) and the three axis reports below.
1) Aggregate SIDE BY SIDE — no rerank, no dropping: every axis finding stands with its
   severity. Bot status: F1 fixed with in-thread fix reply; F2 withdrawn by Greptile;
   the contradictory-pins P1 (comment 4010263920) was REFUTED WITH REASON by the
   coordinator and UPHELD by the round-1 SPEC axis (stays out — note only); the django
   P1 (comment 4010681990) was FIXED in 9cbabde with in-thread fix reply; the
   attest-glob P1 (comment 4010681983) was REFUTED WITH REASON by the coordinator
   (in-thread reply 4010718894) and does NOT auto-join — but the round-2 SPEC axis was
   asked to judge the call: if SPEC sustains it as Required, aggregate it as Required
   (it becomes the batched request). Greptile posted no APPROVED — note that, do not
   treat it as a finding.
2) Verdict GO iff zero Critical/Required open (Nits/Optionals/FYI never block).
3) Post ONE GitHub review on PR #395 (egress.py write --sink pr-review --host github.com
   --payload-class pr-review --consent run-2026-09-14-clean-sweep:tracker-writes FIRST):
   GO = COMMENTED review ("verdict: GO — <brief ≤400 words>" + reviewed SHA 6766265);
   NO-GO = COMMENTED review ("verdict: NO-GO — <brief>" + reviewed SHA 6766265) with
   the ONE batched change request (Required axis findings, deduplicated — same issue
   named twice is ONE fix — plus directly-adjacent cheap items in the touched checks;
   EXCLUDE with a recorded reason: conductor-side record items, accepted optionals,
   pre-existing issues filed separately). COMMENTED for both outcomes — GitHub 422s
   REQUEST_CHANGES on an own-PR (proven this run). NEVER post APPROVE (single GitHub
   identity — approval would fake independence; the posted review + this worker_done
   are the review evidence).
4) worker_done: verdict + reviewed_sha (6766265) + reviewed_wtree (git rev-parse
   HEAD^{tree} at 6766265) + round 2 + the batched request (if NO-GO). Omit --to.
   Preamble --from + --dispatch-capability on every send; consumer_fenced = stop.
   STOP: over 30 min. No sub-dispatch. Comment current.

--- AXIS REPORTS (verbatim, round 2 — PASTED AT DISPATCH) ---

[SPEC R364r2]
I reviewed PR #395 at 6766265 on the SPEC axis. I wrote my expectation before opening the diff, read the diff through the fence, and ran the full suite (1337 OK), validate.py, ruff and the routing gate (94/94) plus real-oracle probes; C-1 (21/21 fixture-backed id-4 cases with faithful riskiest-behaviour picks), C-2 (state failures fail the verdict, 25 violating rows plus 2 passing rows cover all 21 cases, no tautology) and C-3 (frozen 63-case narration list, routing suite untouched) are met, and the out-of-scope limits are respected. Findings: F-1 Required — harden-it's skip-ban glob **/*.py fails untouched fixtures once a real .venv with pytest is installed (4 _pytest files match, e.g. _pytest/unittest.py:185), the same class as round-1 R-1, which was scoped only for deflake-it; F-2 Nit — the held Greptile P1 4010681983 refutation HOLDS (any access-review record in the eval workspace is agent-authored, so fabricated), but the glob is name-based both ways (it fails a GAP handoff ticket named gaps/OB-2-access-review-request.md and passes ACCESS-REVIEW-2026Q2.md); F-3/F-4 Nits on the prove-it argument-order dodge and modernize-it false-fails on valid pins (hashed pin, >2.32.3, cap-first django); F-5/F-6 FYIs on oncall-it and deflake-it regex reach; FYI-7: an untouched workspace passes state in 16/21 cases, by design. Nothing is left for this axis; 0 commits carry this session (git log --all checked) and I made no GitHub posts.

[TEST-ADEQUACY R364r2]
Reviewed PR #395 at 6766265 on the test-adequacy axis only. I verified the claims myself: NC reproduced exactly (eval.py reverted to 506a059 = 23F+89E exit 1, clean 96 OK); C-1 is RED 21/21 at base; the C-2 flip and the frozen list each catch a targeted mutation; round-1 R1 is CLOSED (violating-row coverage 21/21, set equality both ways); the requests table pins both directions. Required: (R-A) three single-regex mutations to the django cap survive the 10-row DJANGO_ROWS table: dropping the (?![\d.]) lookahead passes >=5.2,<6.1 / <6.0.1 (6.x admitted, G1's class), dropping the <= branch fails <=5.2.9, and dropping the (?:\.0+)* suffix fails <6.0; (R-B) 24/55 single checks can be gutted to vacuous with tests.test_evals still OK (13 regex bans/requirements Required, 11 input-unchanged Optional); (R-C) the field-test-it FIELD-REPORT.md and oss-contribute docs/DECISIONS.md positive checks can be made unmatchable with the suite OK (no committed row shows either passes); plus Optional/Nit: AGENT_MUST_EDIT growth isn't test-guarded, no requests pre-release row, duplicate check labels. Left: axis-only report with no rerank or verdict; I committed NOTHING (HEAD 6766265, porcelain empty, 0 commits in any ref name this session), made no GitHub posts, and deleted the /tmp mutation clone.

[STANDARDS R364r2]
I wrote my expectation before opening the diff, then reviewed PR #395 at 6766265 on the STANDARDS axis only (AGENTS.md + ARCHITECTURE.md + Fowler smells per hunk, tautology guard from matt tdd), fencing every PR read through guard_text. All repo gates pass on a clean tree: three-layer separation and eval validity (validate.py and eval.py validate exit 0), routing 94/94 and untouched, 1337 tests OK, badges and ruff clean. The references check out: the Greptile comment and review IDs exist, the pip/CPython 3.13.15 venv excerpts are verbatim, the ledger labels resolve, and the manifest tree 1a2a21cf and negctrl sha256 match. There are no Critical or Required findings. The Nits are N1, duplicated materialize+originals setup in tests (test_evals.py:245, :263 vs _state_after); N2, predicate lookup computed twice (eval.py:957/:991); N3, the deflake ban regex copied three times (deflake-it evals.json:68/73/78) with the venv test reading only the first copy; O1 is a fifth refusal branch in run_behavioral_eval; F1-F5 are FYI (failure-string parsing in _labels, private-helper calls with precedent, review-round label comments, eval.py:24 docstring slightly narrow, first JSON data file under tests/), and Appendix A holds commit receipts at low confidence because no written repo rule exists. Nothing is left on this axis; I committed nothing (git log --all shows 0 commits carrying this session, HEAD 6766265, tree clean) and posted nothing to GitHub.
