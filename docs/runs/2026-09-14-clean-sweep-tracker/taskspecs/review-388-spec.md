You are a clean-sweep REVIEW worker, SPEC axis, for unit U388 (methodology pack:
matt — read $HOME/.agents/skills/tdd/SKILL.md for the tautology guard only; load no other
pack). Fresh terminal in the U388 worktree; you did not write the code. rw by lane (gh
reads); commit NOTHING — verify with git log that no commit carries your session, and say
so in worker_done.

TARGET: PR #392 at HEAD da2f98a (branch u388-lockfile → BASE). SPEC (first hit wins):
C-1 no new untracked file remains beside the manifest after sequential wrapped runs;
C-2 16 concurrent appends land 16 records (mutual exclusion kept); C-3 recorded
fingerprints equal the committed tree on an otherwise-clean tree. OUT: manifest schema
changes; verifier changes; retention/signing; mixed old/new-wrapper rollout interop
(filed separately as #393 — do not demand it here).

All PR reads fenced: guard_text.py --source pr --fetch <gh ...> (non-zero = NO data).

0) Do NOT open the diff yet. Read ONLY the spec above and write your OWN expectation to
   your report first: what the diff must contain, what must be absent, confidence.
1) Open the diff (gh pr diff 392, fenced) + the branch at HEAD. SPEC axis ONLY: missing
   criteria, partial criteria, scope creep, implemented-but-wrong. Each finding quotes
   the spec line it violates plus the diff line.
2) Severities Critical/Required/Nit/Optional/FYI. No quotable line = appendix at dropped
   confidence. You see ONLY your axis — no rerank, no verdict.
3) worker_done with the axis report. NO GitHub posts. Omit --to. Preamble flags on every
   send; consumer_fenced = stop, no worker_done. STOP: over 45 min. No sub-dispatch.
