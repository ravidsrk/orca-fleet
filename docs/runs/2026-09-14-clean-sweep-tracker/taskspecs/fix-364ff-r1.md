You are the clean-sweep FIX worker for unit U364-FF, contract-amendment micro-fix
(methodology pack: matt — read $HOME/.agents/skills/tdd/SKILL.md via `cat` in bash
(file tools are path-locked to the worktree; do NOT use Read outside it); load no other
pack). Fresh terminal in the U364-FF worktree on branch u364ff-venv-globs (currently at
7ceaf5b — verify with git log; refuse a dirty baseline).

CONTEXT (verified by the coordinator): the builder shipped 717083c (scoped bans) +
eeeb38b (badge 1341) + 7ceaf5b (manifest + NC transcript), all gates green. But the
frozen contract's criterion ids C-FF1..C-FF3 do not match verify.py's CRIT_ID_RE, so
the scope leg fails and NC replay is blocked. The coordinator AMENDED the contract on
BASE (C-1..C-3). Your job: re-bind the manifest to the amended contract, nothing else.

AMENDED BINDING (copy these EXACT values):
contract.source = docs/runs/2026-09-14-clean-sweep-tracker/taskspecs/build-364ff.md@8adf609df57f0a9fa74c090b928120e9b8aa6900
contract.digest = sha256:f69003a2ecc516cac81eeaa3f3419c96286fefe2c53cf6b382b7ad3e3893299c
criterion_ids = [C-1, C-2, C-3]

THE ONE BATCHED FIX (fix exactly this, nothing else):
1) In docs/runs/2026-09-14-clean-sweep-tracker/u364ff-manifest.json ONLY: set
   contract.source/contract.digest/criterion_ids to the amended binding above;
   rename every criteria[] id C-FF1→C-1, C-FF2→C-2, C-FF3→C-3 (labels and witnesses
   unchanged); record the amendment in the manifest's deviations/notes with the
   reason (CRIT_ID_RE shape). Touch NO other file (no code, no tests, no badges).
2) Union first: merge origin/review/2026-09-14-holistic-fixes into the branch; if
   ONLY badge files conflict, re-regen + continue (mechanical); any other
   conflict = STOP.
3) Re-run verify.py over the manifest with the amended --contract-source/
   --contract-digest, --unit-class mutation, --lighting lit, the manifest's
   NC-COMMAND and --execute-nc: the scope leg MUST go green and NC replay MUST
   run (only the pre-review review leg may still fail). Paste the verify tail in
   worker_done. If any other leg fails = STOP + report.
4) Commit manifest-only (bisectable, maintainer author, no trailers, named
   staging, receipt-style message). Push (egress.py write --sink git-push FIRST,
   consent run-2026-09-14-clean-sweep:base-writes). No PR (integrator opens it).
   No merge/rebase past step 2.
5) worker_done with new head SHA + verify tail. Omit --to. Preamble flags on every
   send; consumer_fenced = stop. STOP: any red beyond the pre-review review leg;
   over 30 min. ESCALATION: blocking ask. No sub-dispatch. Comment current.
