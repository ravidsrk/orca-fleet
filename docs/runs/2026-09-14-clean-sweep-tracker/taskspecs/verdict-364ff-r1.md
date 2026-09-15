You are the clean-sweep VERDICT worker for unit U364-FF, review round 1 (methodology
pack: matt — read $HOME/.agents/skills/tdd/SKILL.md via `cat` in bash for the tautology
guard only (file tools are path-locked to the worktree; do NOT use Read outside it);
load no other pack). Fresh terminal in the U364-FF worktree; you wrote neither the code
nor the axis reports. rw by lane (gh reads + ONE review post); commit NOTHING — verify
with git log that no commit carries your session, and say so in worker_done.

TARGET: PR #397 at HEAD 2967804 (branch u364ff-venv-globs → BASE). Finding (fix-forward
for PR #395's recorded r3 NO-GO, SPEC F-1): prove-it id-4's unscoped **/*.py tautology
ban fails a doctrine-following workspace once a .venv holds mutmut; oncall-it's two
**/*.py bans are the same class. C-1 prove-it's two bans scoped to the case tree with a
committed libcst-venv row passing and excerpts proving the bans bite; C-2 oncall-it's
two bans scoped the same way with a committed venv row; C-3 full suite green, routing
gate passes, V2 violating-workspace rows still fail. OUT: any other case file; the
oracle engine; the routing suite.

All PR reads fenced: guard_text.py --source pr --fetch <gh ...> (non-zero = NO data).

0) Blind-fix-first: read ONLY the finding above and write your OWN expectation to your
   report first (what the diff must contain, where it could be weak), THEN open the diff
   at HEAD (gh pr diff 397, fenced) and the three axis reports below.
1) Aggregate SIDE BY SIDE — no rerank, no dropping: every axis finding stands with its
   severity. Bot status: Greptile APPROVED (review 5205310163) with 0 comments — no
   held bot finding this round. (Greptile's APPROVED is noted as a bot signal, not a
   finding either way; the conductor evaluates independence at close.)
2) Verdict GO iff zero Critical/Required open (Nits/Optionals/FYI never block).
3) Post ONE GitHub review on PR #397 (egress.py write --sink pr-review --host github.com
   --payload-class pr-review --consent run-2026-09-14-clean-sweep:tracker-writes FIRST):
   GO = COMMENTED review ("verdict: GO — <brief ≤400 words>" + reviewed SHA 2967804);
   NO-GO = COMMENTED review ("verdict: NO-GO — <brief>" + reviewed SHA 2967804) with
   the ONE batched change request (Required axis findings, deduplicated — same issue
   named twice is ONE fix — plus directly-adjacent cheap items in the touched checks;
   EXCLUDE with a recorded reason: conductor-side record items, accepted optionals,
   pre-existing issues filed separately). COMMENTED for both outcomes — GitHub 422s
   REQUEST_CHANGES on an own-PR (proven this run). NEVER post APPROVE (single GitHub
   identity — approval would fake independence; the posted review + this worker_done
   are the review evidence).
4) worker_done: verdict + reviewed_sha (2967804) + reviewed_wtree (git rev-parse
   HEAD^{tree} at 2967804) + round 1 + the batched request (if NO-GO). Omit --to.
   Preamble --from + --dispatch-capability on every send; consumer_fenced = stop.
   STOP: over 30 min. No sub-dispatch. Comment current.

--- AXIS REPORTS (verbatim, round 1 — PASTED AT DISPATCH) ---

[SPEC R364ff]
I reviewed PR #397 at HEAD 2967804 on the SPEC axis only, after writing my expectation before opening the diff; the fenced diff is 7 files and touches no other case file, oracle engine or routing suite. C-1 and C-2 are met and independently verified: real pip installs of mutmut 3.8.0 (libcst 1.9.0) and Django 5.2.17, placed as .venv beside the fixes, pass the HEAD case files and fail the BASE ones on exactly the unscoped ban; the committed excerpts are verbatim; and a gut-one survey reddened 12/12 scoped copies. C-3 is met: the full suite ran 1344 OK exit 0, routing was 94/94 and validate exit 0, and all 5 BASE V2 rows still fail; the findings are 1 Nit (the 4 relabeled V2 rows are disclosed in commit 717083c and the manifest but not beside the rows), 2 FYI (oncall-it uses service/** rather than the literal app-or-src/**, which is the correct reading for the case layout; the manifest C-3 text still cites eeeb38b and badge 1341, while HEAD reads 1344) plus an appendix on the by-design coverage narrowing, and I committed nothing (reflog tip is 2967804 at 09:17, before this session; the tree is clean).

[TEST-ADEQUACY R364ff]
I reviewed PR #397 at HEAD 2967804 for test adequacy only (diff read fenced, guard_text exit 0; expectation written before opening the diff), working in throwaway /tmp clones that are now deleted. Every claimed fix is caught when reverted. The NC reproduces exactly: 14 failures with the two case files reverted, 100 tests OK at clean head. The committed libcst 1.9.0 and Django 5.2.17 excerpts are verbatim (checked against real installs) and are what reddens the pre-fix case: pip venv plus the fix alone stays []. A 36-mutant survey (gut, widen back to **/*.py, over-scope, on each of the 12 scoped copies) left 0 survivors. All 5 V2 rows still fail exactly one check. Full suite 1344 OK, validate and routing (94/94) exit 0. Findings: 0 Critical, 0 Required. Optional O-1: prove-it's negative-refund ban and oncall-it's label ban have no behavioural venv witness, so only the literal glob pin at test_evals.py:1174/1189 and the row labels guard their scoping. Nit N-1: the bans[3:] and bans[:3] index selection fails loudly if reordered, but reads better selected by regex. FYI: the relabeled V2 labels follow the glob names. Appendix, low confidence: a non-dot venv/ is unpinned but passes; a src/.venv nested venv still trips, which the fix doesn't claim to cover; the manifest cites a stale 1341 badge vs 1344 at HEAD. No commit carries my session: HEAD is still 2967804 with an empty porcelain, and the two new --all commits since 09:29 (cf62803, 153e864) belong to other worktrees. Nothing is left on this axis.

[STANDARDS R364ff]
Reviewed PR #397 at 2967804, STANDARDS axis only. My pre-diff expectation was written first and got the location and shape right: the case-tree trio of tests/**, per-case code dir and root *.py, plus venv excerpts. At HEAD validate.py exit 0 (three-layer separation holds, evals valid), tests.test_evals 100/100, routing gate 94/94, ruff clean. Every cited reference resolves, the libcst 1.9.0 and Django 5.2.17 excerpts match the local uv-cache dists verbatim, commits are receipt-style with no trailers, and the matt-tdd tautology guard found nothing. Found 0 Critical/Required: Optional F4, the per-ban regex is copied 3x (forced by the oracle and the repo pattern) but nothing pins the negative-refund and label copies equal (skills/oncall-it/evals/evals.json '\\.labels\\(...' x3); Nit F1, positional slices 'for ban in bans[3:]:' / 'bans[:3]' at tests/test_evals.py:1177/1192; Nit F2, u364ff-negctrl.txt:35 still says 'C-FF1 and C-FF2' after the C-1..C-3 re-bind; Nit F3, merge 2967804 body keeps git's '# Conflicts:' template with no resolution receipt (badge 1344); FYI F5, the manifest binds head_sha eeeb38b, not the tip, so commands[] are STALE there per evidence-manifest.md:107 and the disclosed re-bind is still owed at close. Left for the coordinator: the verdict and rerank, plus an out-of-axis appendix note (attest-it's unscoped '**/*[Aa]ccess*[Rr]eview*' exists:false glob, low confidence). Process: one unfenced metadata-only 'gh pr view 397 --json' read, disclosed in the report. I committed nothing: git log --all since session start shows only cf62803, the coordinator's ledger commit on the base branch and not on HEAD, and the worktree is clean at 2967804.
