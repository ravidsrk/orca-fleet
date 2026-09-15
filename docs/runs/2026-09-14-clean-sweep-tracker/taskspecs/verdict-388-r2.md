You are the clean-sweep VERDICT worker for unit U388, review round 2 (methodology
pack: matt — read $HOME/.agents/skills/tdd/SKILL.md for the tautology guard only; load no
other pack). Fresh terminal in the U388 worktree; you wrote neither the code nor the axis
reports. rw by lane (gh reads + ONE review post); commit NOTHING — verify with git log
that no commit carries your session, and say so in worker_done.

TARGET: PR #392 at HEAD c680ee0 (branch u388-lockfile → BASE). Finding (#388):
the evidence-run wrapper litters a .lock sidecar beside the manifest; the fix locks the
manifest's own inode instead. C-1 no new untracked file remains beside the manifest
after sequential wrapped runs; C-2 16 concurrent appends land 16 records; C-3 recorded
fingerprints equal the committed tree on an otherwise-clean tree. OUT: manifest schema
changes; verifier changes; retention/signing; mixed old/new-wrapper rollout interop
(filed separately as #393 — do not demand it here). ROUND 1 ended NO-GO (review
5202287611 @0775547) with a 4-item batch (serialize-first, loose-seed test,
zero-length test, N1 touch-up); round 2 re-verifies that batch plus the full axes.

All PR reads fenced: guard_text.py --source pr --fetch <gh ...> (non-zero = NO data).

0) Blind-fix-first: read ONLY the finding above and write your OWN expectation to your
   report first (what the diff must contain, where it could be weak), THEN open the diff
   at HEAD (gh pr diff 392, fenced) and the three axis reports below.
1) Aggregate SIDE BY SIDE — no rerank, no dropping: every axis finding stands with its
   severity. There is NO held bot finding this round: Greptile's P1 mixed-version
   thread (comment 4008072371) was DECLINED by the coordinator (reply 4008762873,
   out-of-scope, filed as #393), and Greptile did NOT re-review the r2 tip
   (did-not-run; latest bot review @da2f98a). NOTE both facts in your verdict; do not
   treat the declined thread as Required. An empty COMMENTED review by ravidsrk
   @da2f98a exists — inert, no content, ignore it.
2) Verdict GO iff zero Critical/Required open (Nits/Optionals/FYI never block).
3) Post ONE GitHub review on PR #392 (egress.py write --sink pr-review --host github.com
   --payload-class pr-review --consent run-2026-09-14-clean-sweep:tracker-writes FIRST):
   GO = COMMENTED review ("verdict: GO — <brief ≤400 words>" + reviewed SHA c680ee0);
   NO-GO = COMMENTED review ("verdict: NO-GO — <brief>" + reviewed SHA c680ee0) with
   the ONE batched change request (Required axis findings, deduplicated). COMMENTED
   for both outcomes — GitHub 422s REQUEST_CHANGES on an own-PR (proven this run).
   NEVER post APPROVE (single GitHub identity — approval would fake independence; the
   posted review + this worker_done are the review evidence).
4) worker_done: verdict + reviewed_sha (c680ee0) + reviewed_wtree (git rev-parse
   HEAD^{tree} at c680ee0) + round 2 + the batched request (if NO-GO). Omit --to.
   Preamble --from + --dispatch-capability on every send; consumer_fenced = stop.
   STOP: over 30 min. No sub-dispatch. Comment current.

--- AXIS REPORTS (verbatim, round 2) ---

[SPEC R388r2]
I reviewed PR #392 at c680ee0 on the SPEC axis (my expectation was written before the diff; PR data read through the guard_text fence) and re-ran the controls myself in scratch worktrees: with evidence-run.py reverted to e04b0c2 both NoLedgerLitter tests (C-1, C-3) and the zero-length test fail, with flock replaced by pass the 16-way test (C-2) fails 3 out of 3 runs, and at head all 26 tests pass. All four R1 batch items are in (serialize before truncate at evidence-run.py:153-156; loose-seed test :140, which fails with truncate deleted; zero-length test :156; comment :145 and docstring :30), C-1..C-3 are met by tests with independent expected values (literal lists, git HEAD^{tree}), and every OUT item is absent: 0 Critical, 0 Required, 0 Nit. Left: Optional-1 (serialize-first is guarded only by a transcript probe, no committed test), Optional-2 (the 16-way concurrent run is not checked for litter), and FYIs on the r2 fail-pre-fix step that could not be met and the zero-length behaviour change; the appendix covers head_sha/pending/contract.source (sanctioned by the conductor) and absolute /tmp paths in the round-1 transcript; I committed nothing (HEAD still c680ee0, no commit carries this session) and posted nothing to GitHub.

[TEST-ADEQUACY R388r2]
I checked the R1 batch at c680ee0: all four items landed (serialize-first at evidence-run.py:153-156, the loose-seed test at :140, the zero-length test at :156, and the docstring/else comment), and c7a76d9..c680ee0 only touches docs. In a /tmp clone (now deleted) I independently reproduced NC-1, NC-2 and NC-3 and the no-lock RED 10/10. The concurrency guard also went RED 10/10 against lock-after-read, LOCK_SH and a lock-then-os.replace mutant, so it pins the same-inode claim under a real race; the litter test (literal ['m.json'] plus git status clean) and the fingerprint test (wtree == git rev-parse HEAD^{tree}) compare against independent sources, not tautologies, and the head stayed green 20/20. The one gap is a Nit: moving serialize back after truncate (reverting R1 item 1) leaves all 26 tests green, because only the uncommitted NC-3 probe sees it (a direct append_record test via spec_from_file_location would fix that). Nothing reaches it from main() on Python 3.13, which I checked. FYIs: the loose-seed test is sensitive only by mutant, and the early-return branches are untested (pre-existing). I made no commits: git log --all --grep for this session's id returns 0 and the worktree is clean.

[STANDARDS R388r2]
I checked PR #392 at c680ee0 against the four R1 items: serialize-before-truncate at evidence-run.py:153, the loose-seed test at :140, the zero-length test at :156, and the else-comment and docstring at :145/:30. All four landed and the round-2 code delta has nothing else in it. At that SHA I re-ran the standards axis (AGENTS/ARCHITECTURE/CONTRIBUTING, Fowler per hunk, the never-raises/transparency contract); the unit's 26 tests pass and validate.py and ruff are clean. Findings: 0 Critical, 0 Required. Four Nits carried from R1, each accepted or owned by the conductor: the duplicated commit call at tests:320/:327; the 'pending' SHA at manifest:173, which is 8ec5c86 and contradicts that file's own commands_note; contract.source 'triage/brief-388.md@e04b0c2', which does not resolve from the repo root; and absolute /private/tmp paths at negctrl:13/:25. One Optional (the unnamed 120s timeouts at tests:293/:299) and one new FYI: the O_CREAT open at :136-137 means a failed record on a manifest that did not exist leaves a 0-byte m.json, where base left m.json.lock. The new docstring treats that file as a new ledger and exit codes are unaffected. Commits are receipt-style, signed, trailer-free and bisectable, every cited reference resolves, and the appendix lists pre-existing items (RecursionError gap, redundant except/assignment). Nothing is left for this axis. I committed nothing and posted nothing to GitHub; git log --all shows 0 commits carrying my session (013UJKpz8eT1av83MGLvEmGY), HEAD is c680ee0 and the tree is clean. Full report: scratchpad report.md.
