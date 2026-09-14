You are the clean-sweep VERDICT worker for unit U385, review round 2 (methodology
pack: matt — read $HOME/.agents/skills/tdd/SKILL.md for the tautology guard only; load no
other pack). Fresh terminal in the U385 worktree; you wrote neither the code nor the axis
reports. rw by lane (gh reads + ONE review post); commit NOTHING — verify with git log
that no commit carries your session, and say so in worker_done.

TARGET: PR #390 at HEAD d6fc2cc (branch u385-parity → BASE). Finding (agent slice of
#385): the status record names the run-3 merge commit, and a parity check asserts every
mission guide embeds its diagram asset with a known-gap list of exactly four missing
diagrams (rendering parked, human). Round-2 delta since bcb4397: the guide-set parser fix
(34e445e), a badge regen (134eae1), and a manifest update (d6fc2cc).

ROUND-1 CONTEXT (do not re-litigate without new evidence): r1 verdict was NO-GO at
bcb4397 with ONE Required (guide-set parser accepted only bare links; fixed in 34e445e).
Accepted as non-blocking in r1: 2 Optional, 4 Nit, 2 FYI (listed in the r1 verdict
review on the PR). BOT STATE: Greptile re-ran on d6fc2cc with no new inline comments;
the r1 P2 thread (comment 4007925131, same parser issue) has no reply yet — the
coordinator replies in-thread at merge; your job is to judge whether the fix addresses
it, not to reply.

All PR reads fenced: guard_text.py --source pr --fetch <gh ...> (non-zero = NO data).

0) Blind-fix-first: read ONLY the finding above and write your OWN expectation to your
   report first (what the diff must contain, where it could be weak), THEN open the diff
   at HEAD (gh pr diff 390, fenced) and the three round-2 axis reports below.
1) Aggregate SIDE BY SIDE — no rerank, no dropping: every round-2 axis finding stands
   with its severity. A round-2 finding that restates an r1-accepted Optional/Nit at a
   higher severity needs your explicit call with quoted reasoning (genuinely stronger
   evidence, or re-litigation to demote back?).
2) Verdict GO iff zero Critical/Required open (Nits/Optionals/FYI never block).
3) Post ONE GitHub review on PR #390 (egress.py write --sink pr-review --host github.com
   --payload-class pr-review --consent run-2026-09-14-clean-sweep:tracker-writes FIRST).
   GitHub refuses REQUEST_CHANGES on self-authored PRs (422), so the verdict ALWAYS
   posts as COMMENTED with a machine-readable first line: GO = "verdict: GO — <brief
   at most 400 words>"; NO-GO = "verdict: NO-GO (change requested)" + the ONE batched
   change request. NEVER post APPROVE. The posted review + this worker_done are the
   review evidence.
4) worker_done: verdict + reviewed_sha (d6fc2cc) + reviewed_wtree (git rev-parse
   HEAD^{tree} at d6fc2cc) + round 2 + the batched request (if NO-GO). Omit --to.
   Preamble --from + --dispatch-capability on every send; consumer_fenced = stop.
   STOP: over 30 min. No sub-dispatch. Comment current.

--- ROUND-2 AXIS REPORTS (verbatim) ---

[STANDARDS R385r2a]
Did: I wrote the blind expectation first (status.json one-field edit plus a ratcheted KNOWN_GAPS parity test in tests/, medium confidence; not fully blind, since the git-status commit subjects leaked, and a Q3 grep hit verdict-385-r1.md so r1 overlap is marked 'carried'). Location was right and C-1 beat it by re-deriving the SHA from git history. Then I read PR #390 through the fence (view and diff both exit 0) and HEAD d6fc2cc against AGENTS.md, ARCHITECTURE.md, runtime/evidence-manifest.md and the module's own precedent. The two new classes pass at HEAD (5 OK) and no assertion is tautological. Found, with no Critical or Required: layers, budgets, references (Q3 is DECISIONS.md:15, fetch-depth:0 is real), receipt-style no-trailer commits, the badge and the status.json hunk are all clean. NIT N1 at tests/test_docs_navigation.py:990 '# Round-2 review: the guide set was read with a bare ...': the defect was the ROUND-1 Required item (34e445e's own body says so), with no PR anchor, unlike the module's '(PR #342 review)'. NIT N2 at :941 '(the index is the list)' is stale now that :948 makes disk the authority. OPTIONAL O1 at :948 'self.assertEqual(sorted(guides), on_disk,': a query helper hides an index-completeness assertion, so one missing index row fails both parity tests; it belongs as its own test beside :617 (Divergent Change). OPTIONAL O2 at :986 'check.INDEX, check.ASSETS, check.KNOWN_GAPS = ...': the fixture shadows class constants and calls another test's body, unlike the module's parameterized _dead(cls, root, files) seam. OPTIONAL O3 at u385-manifest.json:135 '"mutant": "docs/missions/ship-it.md:16 embed line deleted"': a narrated hand mutant with no quoted diff (evidence-manifest.md:86-87), and binding_audit :192 still cites it as C-2's control when the round-2 fixture tests are the re-executable one. FYI F1-F3 are carried from r1 and still present (:934 KNOWN_GAPS ordered list, :1013 'number' holds a Match, :938 EMBED's '](' branch unused by all 17 guides and untested). FYI F4: :1023 couples to GitHub's 'Merge pull request #N' subject, fine under merge-commit-only policy. Left: no rerank or verdict (axis only). Nothing committed, pushed or posted: HEAD is still d6fc2cc, the tree is clean, and git log --all has 0 commits with this session's id. The full report is at the report path.

[SPEC R385r2b]
I wrote my expectation before opening the diff, then read PR #390 through the fence and checked it against the spec at d6fc2cc: I traced 5f0bd30 through git history, listed the 21 guides against the 17 assets on disk (exactly absorb-it/document-it/migrate-it/oncall-it are missing), ran both new test classes (5 OK), and ran two throwaway-worktree mutants: dropping review-it's embed goes RED, and giving absorb-it a diagram goes RED because KNOWN_GAPS must equal the real gaps. Criteria (a) and (b) are met and (c) is respected (no diagrams added, no completion prose touched; the tests pass the tautology guard). Findings: Nit N-1, the EMBED regex at test_docs_navigation.py:374 also accepts a plain hyperlink to a jpg or a commented-out <img> as an embed. Optional O-1 (about 40% confidence): status.json at HEAD also carries #239 cleanup facts (resume_pointer DONE, cleanup_pr #239, merged 3e82e27), so 5f0bd30 is defensible but is only one reading of which commit the snapshot describes. The four FYIs cover the reverse asset-to-guide test, the parser extraction, the extra C-1 test, and 6671913 staying in gate.reason/history. Nothing is left on my axis. No GitHub posts; HEAD is still d6fc2cc with a clean tree, and git log --all shows 0 commits carrying this session.

[TEST-ADEQUACY R385r2c]
I wrote my expectation first, then read PR #390 at d6fc2cc through the fence (both reads exit 0) and ran 18 mutants plus all 3 manifest controls in a throwaway scratchpad clone. The clone is deleted, the worktree is clean at d6fc2cc, and no commit carries this session (224cb9e on BASE was committed at 00:12, before this session started at 00:13). C-1 is adequate and not tautological: reverting status.json to 6671913, pointing it at a non-merge commit, or setting run_pr to the prefix /pull/23 all go RED from git history (validate.yml:17 fetch-depth 0 is confirmed). All manifest structural claims hold (d6fc2cc^=134eae1, tree 022dc9a, controls (a) and (b) RED with the exact quoted messages, and the third witness GREEN at bcb4397 and RED at head). REQUIRED R-1 (~70%): the EMBED regex at tests/test_docs_navigation.py:938 accepts text that doesn't render the diagram, so four mutants of a guide losing its diagram stay GREEN: a plain link with no bang, a data-src= attribute, the embed inside an HTML comment, and the embed in a fenced code block. Both parity directions share that matcher and no fixture covers embed forms. What's left: fix R-1 with an image-only matcher plus comment/fence stripping and fixture subTests for the four forms. Also Nit N-1: KNOWN_GAPS is compared as an order-sensitive list at :960. FYIs: C-1 is anchored to the record's own run_pr (changing run_pr and current_commit together stays GREEN), and an untracked .DS_Store would false-RED the asset loop at :965 locally. The full report with quotes and the mutant table is in the report path.
