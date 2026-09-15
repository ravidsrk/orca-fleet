You are the clean-sweep VERDICT worker for unit U387W, review round 1 (methodology
pack: matt — read $HOME/.agents/skills/tdd/SKILL.md via `cat` in bash for the tautology
guard only (file tools are path-locked to the worktree; do NOT use Read outside it);
load no other pack). Fresh terminal in the U387W worktree; you wrote neither the code
nor the axis reports. rw by lane (gh reads + ONE review post); commit NOTHING — verify
with git log that no commit carries your session, and say so in worker_done.

TARGET: PR #401 at HEAD d94c6c1 (branch u387w-wipsection → BASE). Finding (#387
thread 4009895678): the run-report checker's WIP-curve validation bound
complete-looking wave= rows from anywhere in the report; the fix scopes collection
to the canonical WIP-curve section and names the rule in the protocol prose. C-1
rows only inside the canonical section (fences/deviations/other sections ignored);
C-2 per-wave completeness inside enforced; C-3 prose names the rule (≤160 lines);
C-4 suite + validate green. OUT: caps; graduation; other checks; park-class checks.

All PR reads fenced: guard_text.py --source pr --fetch <gh ...> (non-zero = NO data).

0) Blind-fix-first: read ONLY the finding above and write your OWN expectation to your
   report first (what the diff must contain, where it could be weak), THEN open the diff
   at HEAD (gh pr diff 401, fenced) and the three axis reports below.
1) Aggregate SIDE BY SIDE — no rerank, no dropping: every axis finding stands with its
   severity. Bot status (integrator-ingested, held VALID): P2 thread 4012319774
   (run_report.py:499, 'Invalid fences hide rows'): _FENCE_RE opens a backtick fence
   without CommonMark's no-backtick-in-info-string rule — VALID, reproduced read-only
   by the integrator on d94c6c1 (a line '```text`example``' in the section makes a
   canonical wave=1 row drop to rows=[], a fail-closed false missing-evidence; control
   and a valid fence still bind wave=1).
2) Verdict GO iff zero Critical/Required open (Nits/Optionals/FYI never block).
3) Post ONE GitHub review on PR #401 (egress.py write --sink pr-review --host github.com
   --payload-class pr-review --consent run-2026-09-14-clean-sweep:tracker-writes FIRST):
   GO = COMMENTED review ("verdict: GO — <brief ≤400 words>" + reviewed SHA d94c6c1);
   NO-GO = COMMENTED review ("verdict: NO-GO — <brief>" + reviewed SHA d94c6c1) with
   the ONE batched change request (Required axis findings, deduplicated — same issue
   named twice is ONE fix — plus directly-adjacent cheap items in the touched checks;
   EXCLUDE with a recorded reason: conductor-side record items, accepted optionals,
   pre-existing issues filed separately). COMMENTED for both outcomes — GitHub 422s
   REQUEST_CHANGES on an own-PR (proven this run). NEVER post APPROVE (single GitHub
   identity — approval would fake independence; the posted review + this worker_done
   are the review evidence).
4) worker_done: verdict + reviewed_sha (d94c6c1) + reviewed_wtree (git rev-parse
   HEAD^{tree} at d94c6c1) + round 1 + the batched request (if NO-GO). Omit --to.
   Preamble --from + --dispatch-capability on every send; consumer_fenced = stop.
   STOP: over 30 min. No sub-dispatch. Comment current.

--- AXIS REPORTS (verbatim, round 1 — PASTED AT DISPATCH) ---

[SPEC R387W]
I reviewed PR #401 at d94c6c1 on the SPEC axis only, writing my pre-diff expectation first, then reading the diff through guard_text (exit 0), probing the checker, and re-running validate.py (exit 0) and the full suite ('Ran 1353 tests' / OK, exit 0). C-2 and C-4 are met and C-3's sentence is present with attention-budget.md at 78 lines, but F-1 (Required) finds C-1 partial: run_report.py:482 '_WIP_SECTION_RE = re.compile(r" {0,3}#{1,6}[ \t]+WIP(?:-|[ \t]+)curve\b", re.I)' opens the section on any heading beginning 'WIP curve', so '## WIP-curve example (from another run)' with complete rows and no canonical section binds [] (the #387 false pass returns); F-2 (Nit) is prose/check drift, since attention-budget.md:60 names only '## WIP-curve protocol row' while the check reads broader headings and closes the section at any subheading; F-3 and F-4 are FYI (sanctioned gen-badges outputs; one pre-existing test body edited because C-1 requires it). No tautological tests were found, no GitHub posts were made, and I committed nothing: HEAD is still d94c6c1 with a clean tree, and git log shows no commit from this session; full axis report with quotes and probe results is at the report path.

[TEST-ADEQUACY R387W]
I reviewed PR #401 at d94c6c1 on the test-adequacy axis only: I wrote my expectation before opening the diff, reproduced NC-1 (9 failures, same names; restored 69 OK) and NC-2 (1 failure, 'unexpectedly None'; restored OK), confirmed 65->69 tests with only the heading-less fixture call removed, and ran 18 targeted mutants plus probes in /tmp clones that are now deleted. The core claims are structurally witnessed: out-of-section rows (deviations table, backtick/tilde fences inside the section, heading quoted in a fence) are refused with a literal 'none found', complete in-section rows bind and an incomplete one is refused with exactly one error, and the extended protocol fixture takes its heading from the prose and TEMPLATE.md, never from the checker, so it is not tautological. 9 of 18 mutants survive: Required R1, a heading-contains-'WIP-curve' opener (run_report.py:502, the manifest's own ruled_out alternative) lets '## Deviations — WIP-curve cap raised' rows bind; Required R2, the CommonMark fence-close clause (:494-497) can be replaced by 'any fence line closes' with 69 OK, and , -inside-~~~ rows then bind (all executed); Nit: the ###-subsection closer (M2) and the no-space '#387' heading (M15); Optional: re.I, fence indent, and the message wording coupled into the behaviour assertion. Full report with quotes and probes is at the report path; this session made no commits (HEAD d94c6c1, clean status, reflog's last entry 11:08 predates the 11:19 session start) and posted nothing to GitHub.

[STANDARDS R387W]
I wrote my pre-diff expectation first (it matched the location and shape of the fix), then reviewed PR #401 at d94c6c1 on the STANDARDS axis only, reading the PR through guard_text.py; validate.py passes and the tautology guard found no tautological tests. Findings, each quoting its code line: Optional S1, Duplicated Code: run_report.py adds a second heading/fence scanner (_HEADING_RE/_FENCE_RE) beside inventory.py's NEXT_HEADING/FENCE, which it already loads, and the two apply different Markdown rules to the same report (a heading inside a fence closes an inventory block but not the WIP section). Nit S2: attention-budget.md:60 says rows are read 'only under' the '## WIP-curve protocol row' heading, but _WIP_SECTION_RE accepts any heading at any level that begins 'WIP curve'. Nit S3: the public WIP_SECTION holds only message text, and the heading is now spelled in 4 places. Nit S4: manifest commit 6ae6cf0 has an empty body. FYI S5: the prose line grew 331->557 bytes to keep 'File stays at 78 lines', and clean-sweep is at 33,803/34,000 tokens. Nothing is left on this axis; the report has an appendix and the full evidence, no GitHub posts were made, and git log/reflog confirm no commit from this session (HEAD d94c6c1, clean tree, newest reflog entry 11:08 predates the session).
