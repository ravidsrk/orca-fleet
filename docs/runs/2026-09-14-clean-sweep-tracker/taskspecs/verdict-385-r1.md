You are the clean-sweep VERDICT worker for unit U385, review round 1 (methodology
pack: matt — read $HOME/.agents/skills/tdd/SKILL.md for the tautology guard only; load no
other pack). Fresh terminal in the U385 worktree; you wrote neither the code nor the axis
reports. rw by lane (gh reads + ONE review post); commit NOTHING — verify with git log
that no commit carries your session, and say so in worker_done.

TARGET: PR #390 at HEAD bcb4397 (branch u385-parity → BASE). Finding (agent slice of
#385): the status record names the run-3 merge commit, and a parity check asserts every
mission guide embeds its diagram asset with a known-gap list of exactly four missing
diagrams (rendering parked, human).

All PR reads fenced: guard_text.py --source pr --fetch <gh ...> (non-zero = NO data).

0) Blind-fix-first: read ONLY the finding above and write your OWN expectation to your
   report first (what the diff must contain, where it could be weak), THEN open the diff
   at HEAD (gh pr diff 390, fenced) and the three axis reports below.
1) Aggregate SIDE BY SIDE — no rerank, no dropping: every axis finding stands with its
   severity. The held bot finding joins as Required unless you REFUTE it with a quoted
   reason (refutation needs a failing demonstration, not an opinion).
2) Verdict GO iff zero Critical/Required open (Nits/Optionals/FYI never block).
3) Post ONE GitHub review on PR #390 (egress.py write --sink pr-review --host github.com
   --payload-class pr-review --consent run-2026-09-14-clean-sweep:tracker-writes FIRST):
   GO = COMMENTED review ("verdict: GO — <brief ≤400 words>" + reviewed SHA bcb4397);
   NO-GO = REQUEST_CHANGES with the ONE batched change request (Required axis findings +
   held bot finding, deduplicated — same issue named twice is ONE fix). NEVER post
   APPROVE (single GitHub identity — approval would fake independence; the posted review
   + this worker_done are the review evidence).
4) worker_done: verdict + reviewed_sha (bcb4397) + reviewed_wtree (git rev-parse
   HEAD^{tree} at bcb4397) + round 1 + the batched request (if NO-GO). Omit --to.
   Preamble --from + --dispatch-capability on every send; consumer_fenced = stop.
   STOP: over 30 min. No sub-dispatch. Comment current.

--- AXIS REPORTS (verbatim, round 1) ---

[STANDARDS R385a]
Did: wrote the blind expectation first (status.json one-field edit + a guide-set glob test with a KNOWN_GAPS ratchet, ~70%): location right, but the tests went into the existing tests/test_docs_navigation.py and the guide set is parsed from the index. Then I read the PR #390 diff (guard-fenced, exit 0) and HEAD bcb4397 against AGENTS.md/ARCHITECTURE.md, the module's own precedent and Fowler's smells. No layer or budget file is touched, the Q3/fetch-depth references are real, and the commits are receipt-style with no trailers. Found: REQUIRED F1 Duplicated Code at tests/test_docs_navigation.py:941 `for target in re.findall(r"\]\(([a-z0-9-]+\.md)\)", self.INDEX.read_text(encoding="utf-8")):`. It is a narrower copy of the #143 index parser (:617) and skips the module's skills/ enumeration idiom. Verified in memory: changing the index link (ship-it.md) to (./ship-it.md) or (ship-it.md#top) keeps the index test green but silently drops ship-it from parity, and 20 guides still clears the hand-typed '> 15' floor at :945 (same point as Greptile's open inline thread on :942). OPTIONAL F2 at :936 `EMBED = re.compile(...)`: the detector has no plantable seam (unlike _dead, PR #342 precedent), its ](/src=' branches are exercised by nothing, and C-2's only control is a manifest-narrated hand mutant. NIT F3 at :932 `KNOWN_GAPS = [...]` is a mutable, order-coupled list compared by ordered equality at :956. NIT F4 at :976 `number = re.fullmatch(...)` holds a Match, not a number. The C-1 status test, status.json, the badge and the manifest are clean. Left: no rerank or verdict (axis only). Nothing committed, pushed or posted: HEAD is still bcb4397, the tree is clean, and git log --all has no commit with this session's id. Full report is at the report path.

[SPEC R385b]
I reviewed the fenced PR #390 diff at bcb4397 against the U385 spec, writing my own expectation first. (a) is met: current_commit 5f0bd30 is the PR #238 run-3 merge, which the snapshot's own run_pr and the STATUS.md banner point to, and the later #239 merge changed only docs/completion ledger files. (c) is respected: no diagrams, no other completion-docs prose; the manifest and 1285->1288 badge regen are FYI only. (b) is met for the exact 4-name KNOWN_GAPS equality and the asset->guide direction, with one Required partial. B-1 quotes spec 'asserts every mission guide embeds its diagram asset' against the diff line 're.findall(r"\]\(([a-z0-9-]+\.md)\)", ...)' plus the '>15' floor. In a throwaway worktree, a new diagram-less guide linked as ./new-it.md or new-it.md#top (forms the existing index test at line 617 accepts) left both parity tests green, while a bare new-it.md link failed as it should. B-2 is Optional: the EMBED regex also counts a plain markdown link as an embed, but all 17 guides use img src today, so nothing passes falsely now. Nothing is left on this axis. I committed nothing: git log --all shows 0 commits carrying my session, HEAD is still bcb4397, the tree is clean, the mutation worktree is removed, and I made no GitHub posts.

[TEST-ADEQUACY R385c]
I wrote my expectation before opening the diff. Then I read PR #390 fenced (guard_text rc=0) at bcb4397 and ran 14 mutants in a throwaway /tmp clone, now deleted. Both fixes are guarded by real, non-tautological tests. Reverting status.json to base goes RED on the C-1 git-history test (merge-parent check plus 'Merge pull request #238' subject, expected value read from git, not restated), matching the manifest. Deleting ship-it's embed goes RED, 2 failures, also matching the manifest; a wrong asset, an orphan asset, unlinking a guide from the index and a gap gaining its diagram all go RED too, and the four gaps are independently correct (21 indexed guides minus 17 assets). CI runs with fetch-depth 0 and gates pass. Nit 1 (test_docs_navigation.py:261/279): the EMBED regex scans raw markdown, so an HTML-commented, code-fenced or plain-hyperlinked diagram stays GREEN. Nit 2 (:286): the orphan check uses iterdir, so a gitignored .DS_Store gives a false RED on macOS. FYI 1: C-1 checks run_pr against current_commit in git history, so a coordinated wrong pair (#231/6671913) or a subject-forged local merge passes. FYI 2: C-2 changes no production path, so its control is a hand mutant, which I reproduced. I verified the manifest's structural claims myself: KNOWN_GAPS equality, the index-derived guide set, the disk-derived asset set, the 29-test module and both controls. I committed nothing: git log --all shows no commit carrying this session and the worktree is clean at bcb4397. Nothing is left on this axis.

--- HELD BOT FINDING (Greptile P2, PR #390 comment 4007925131, tests/test_docs_navigation.py:942) ---
The parity check recognizes only bare lowercase links such as ship-it.md, although
repository navigation also supports ./-prefixed and anchored forms. If a guide uses one
of those forms, _guides() silently omits it, and the loose >15 assertion can still pass.
Candidate fix (bot's): tolerate ./ and #anchor, or assert the parsed set equals the
on-disk guide set minus README. (Quoted finding reworded to avoid bracket-link forms:
the dead-link guard scans run files too.)
