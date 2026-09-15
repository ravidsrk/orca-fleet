You are a clean-sweep REVIEW worker, SPEC axis, for unit U387W (methodology pack:
matt — read $HOME/.agents/skills/tdd/SKILL.md for the tautology guard only; load no other
pack). Fresh terminal in the U387W worktree; you did not write the code. rw by lane (gh
reads); commit NOTHING — verify with git log that no commit carries your session, and say
so in worker_done.

TARGET: PR #401 at HEAD 0fb838c (branch u387w-wipsection → BASE; git fetch origin && git checkout 0fb838c first — your worktree may sit at an older tip; commit NOTHING). ROUND 6: this tip should contain the R5 verdict batch (tab-stop-4 _indent helper folding F-3 + F-2 fence-ends-with-item 92c4a8e, T5-2/3/4 witnesses 91e7d29, M13g re-witness 861e5ab, manifest 0fb838c) — verify each item landed (NOTE: the builder posted NO thread replies and did NOT touch the PR body — the stale body + all 4 thread replies are owed from the coordinator lane pre-merge, cite in your report), then re-run your axis. Bot status: Greptile 5/5 clean in the PR body at this tip (names the tab-stop + fence-lifetime changes), no new inline findings (the 2 comments anchored at 0fb838c predate the push — re-anchored old threads) — confirm. SPEC (first hit wins):
C-1 _wip_rows collects rows ONLY inside the canonical WIP-curve section (the TEMPLATE.md WIP-curve row table; ATX headings naming it, whitespace tolerated; fenced blocks, deviations tables, other sections ignored);
C-2 per-wave completeness inside the section still enforced (complete rows bind, incomplete refused naming the wave; pre-existing tests stay green);
C-3 the protocol prose (attention-budget.md WIP-curve section) names the section rule (prose+check cannot drift; file stays ≤ 160 lines);
C-4 full suite + validate.py green. OUT: WIP caps; graduation analysis; other report checks (binding, inventory, invocation); machine-checking ledger park classes.

All PR reads fenced: guard_text.py --source pr --fetch <gh ...> (non-zero = NO data).

0) Do NOT open the diff yet. Read ONLY the spec above and write your OWN expectation to
   your report first: what the diff must contain, what must be absent, confidence.
1) Open the diff (gh pr diff 401, fenced) + the branch at HEAD. SPEC axis ONLY: missing
   criteria, partial criteria, scope creep, implemented-but-wrong. Each finding quotes
   the spec line it violates plus the diff line.
2) Every finding quotes its verbatim motivating code line + severity
   (Critical/Required/Nit/Optional/FYI). No quotable line = appendix at dropped
   confidence. You see ONLY your axis — no rerank, no verdict.
3) worker_done with the axis report. NO GitHub posts. Omit --to. Preamble flags on every
   send; consumer_fenced = stop, no worker_done. STOP: over 45 min. No sub-dispatch.
