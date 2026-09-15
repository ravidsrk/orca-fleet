You are the clean-sweep FIX worker for unit U387W, review round 5 (methodology pack:
matt — read $HOME/.agents/skills/tdd/SKILL.md and follow it; load no other pack). Fresh
terminal in the U387W worktree on branch ravidsrk/u387w-wipsection (must be at the
r4 tip f8a0d87 — verify with git log AND git status; if HEAD is detached (reviewers
checkout the SHA), reattach with `git checkout ravidsrk/u387w-wipsection` first and
verify the tip is f8a0d87; refuse a dirty baseline).

VERDICT (round 4, NO-GO, reviewed f8a0d87, review 5208015370): 3 Required open
(STANDARDS S-1/S-2, TEST R-1), each reproduced. Greptile P1 4013782318 is
FALSE-POSITIVE (all three axes agree, oracle-confirmed). Everything else stands
at its severity and does NOT block: SPEC S4-1 is IN this batch (adjacent);
S-3/S-5/FYIs accepted; nnt[2] pre-existing. Do NOT post thread replies (the
coordinator answers all four threads at the fix close — name your pushed tip
clearly in worker_done).

THE ONE BATCHED REQUEST (fix exactly this, nothing else):
1) S-1 (Required): STALE PR BODY — ALREADY DONE BY THE COORDINATOR (gh pr edit
   401, receipted, Greptile block preserved; body now describes f8a0d87: the
   `WIP-curve protocol row` rule, per-round history, 81/validate/1376 gates,
   35-control NC table). Do NOT touch the PR body. No code ships for this item.
2) S-2 (Required, cross-axis SPEC C-2): NEW fail-open — an indented-code line
   arms a setext close (:554 `para = ...` then :535): rows 1-2, then '    note'
   / '---', then an incomplete wave=2 binds [] at HEAD, while base refuses it
   with 2 errors. This is NOT the pre-existing indented-code FYI (nnt[2]) —
   that one only HIDES rows (fail-closed); this one BINDS []. Indented-code
   lines must never arm a setext close. Committed test with the exact repro
   (rows 1-2 + indented note + --- + incomplete wave=2 refused naming wave 2).
3) R-1 (Required): the :551 line is unwitnessed — the mutant 'items[:], para =
   opened, None' (dropping the list items, the P1's described mechanism)
   survives all 81 tests and binds [] on an incomplete duplicate. Add the
   witness test the verdict names: '- a'/'  - b'/'  ***'/'  para'/'---' plus
   the incomplete wave=2 — it must kill the mutant (RED on mutant, GREEN on
   true code). This test also locks in the P1's FALSE-POSITIVE reasoning.
4) Adjacent cheap items: (a) S4-1 (SPEC Nit): an empty list item plus a blank
   line should close the item (pre-existing, same class as r3 F-1 — fix with
   a committed test); (b) MX11 (4-space marker-gap boundary, fails open) +
   MX15 (rows before any heading) witness subtests, red-first; (c) finish
   the truncated S-4 comment at :493.

SCOPE: runtime/scripts/run_report.py + tests/test_run_report.py + the unit
manifest + the negctrl transcript ONLY. Do not touch the prose (your check
changes must keep matching what attention-budget.md:60 names — if a rule change
drifts from the prose, adjust the WORDING minimally and say so), caps,
graduation, other checks, the PR body, or any other file. Badge regen only if
YOUR new tests move the count (same mechanical-commit rule). Never `git add -A`.
The non-batched Nits/Optionals/FYI are NOT in this batch; touch them only if
your Required fix cannot land without it, and say so in the commit message.

CONTRACT (unchanged): contract.source =
docs/runs/2026-09-14-clean-sweep-tracker/taskspecs/build-387-wip-section.md@719d997be28476c382660f3f37d829e597130ce9.
contract.digest =
sha256:d7b4e72c070e589df86aca9d57fd667d1227ca9cd72414edbaa6bc6a9f2d317d.
criterion_ids = [C-1, C-2, C-3, C-4] (unchanged). NC-COMMAND unchanged: python3 -m
unittest tests.test_run_report.

STEPS:
1) Union first: merge origin/review/2026-09-14-holistic-fixes into the branch; if ONLY
   badge files conflict, re-regen + continue (mechanical); any other conflict = STOP.
2) Red FIRST: the S-2 repro + R-1 witness + S4-1/MX11/MX15 subtests fail pre-fix
   (show all), pass post-fix. Oracle: markdown-it-py CommonMark for disputed
   shapes (match it, don't argue it).
3) Implement 2)+4) above, smallest change. (Item 1 needs no code.)
4) Recorder run of the nc-command + validate.py + FULL suite, all green. ruff on the
   touched modules. gitleaks detect clean. Capture the full-suite summary line
   (tee the log AND grep Ran/OK).
5) Re-run the round-1+2+3+4 negative controls (record the revert RED transcript)
   at the new tip. Update the unit manifest
   (docs/runs/2026-09-14-clean-sweep-tracker/u387w-manifest.json): new head_sha (:=
   the CODE tip — option-A: a manifest cannot name the SHA of the commit containing
   it, so the manifest-commit tip is named in worker_done and the coordinator
   re-binds at close; see DECISIONS.md fix-step5-headsha / ruling msg_b92468884470),
   new commands block (artifact null everywhere, never a /tmp path), extended NC
   transcript, same contract/criteria/intent/lighting. Commit fix + manifest
   (bisectable, maintainer author, no trailers, named staging, receipt-style
   messages).
6) Push the BARE branch (egress.py write --sink git-push --host github.com
   --payload-class branch-tip --consent run-2026-09-14-clean-sweep:base-writes FIRST):
   `git push origin ravidsrk/u387w-wipsection:u387w-wipsection`. PR #401 exists — do
   NOT open another; your push updates it. No merge, no rebase past step 1. After your
   push Greptile re-reviews: report any NEW findings in worker_done, do not chase them
   (they need a new spec).
7) worker_done with new head SHA + gates + NC transcript. Omit --to. Preamble flags on
   every send; consumer_fenced = stop. STOP: unexplained red; out-of-scope rot; over 60
   min. ESCALATION: blocking ask. No sub-dispatch. Comment current.
