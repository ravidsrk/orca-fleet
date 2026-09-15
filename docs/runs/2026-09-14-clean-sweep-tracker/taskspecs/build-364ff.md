You are a clean-sweep BUILD worker for unit U364-FF (methodology pack: matt — read
$HOME/.agents/skills/tdd/SKILL.md via `cat` in bash and follow it (file tools are
path-locked to the worktree; do NOT use Read outside it); load no other pack).

GOAL · SCOPE · NON-GOALS · STOP · EVIDENCE · ESCALATION · BUDGET: build-change.
Work on branch u364ff-venv-globs in THIS worktree (forked from origin/BASE
review/2026-09-14-holistic-fixes @ __FORK_364FF__ — verify with git log before starting;
refuse a dirty baseline or a wrong base). If the worktree branch is not
u364ff-venv-globs, create it from origin/review/2026-09-14-holistic-fixes first.

FINDING (frozen from SPEC-r3 F-1 on PR #395, which the unit's own review reproduced;
U364 already merged as 1b64781 — this unit fixes the sticking finding forward):
CATEGORY: real-bug (evals). prove-it id-4's unscoped glob **/*.py tautology ban fails
a doctrine-following workspace once a .venv holds mutmut (its dependency libcst ships
'assert True' in its tests) — the R-1 venv class, previously scoped for deflake-it and
harden-it only. oncall-it's two **/*.py bans are the same class (probed at 0 hits;
scope preemptively on the same pass).
DESIRED: prove-it's two bans and oncall-it's two bans scoped to the case tree
(tests/**, app-or-src/**, root *.py — the deflake/harden pattern), each with a
committed venv row proving a doctrine-following workspace passes, and committed
excerpts proving the bans still hit real violations.
OUT OF SCOPE: any other case file; the oracle engine; the routing suite.
NOTICED-BUT-NOT-TOUCHED otherwise.

HOT FILES: skills/prove-it/evals/evals.json, skills/oncall-it/evals/evals.json,
tests/test_evals.py (+ tests/eval_workspaces.json rows). Touch nothing else.
Never `git add -A`.

CONTRACT (coordinator-issued — copy EXACTLY into the manifest; the dispatch binding
prepended to your TASK resolves both lines — copy the BINDING values, not these
placeholders):
contract.source = docs/runs/2026-09-14-clean-sweep-tracker/taskspecs/build-364ff.md
at the dispatch commit named in your binding.
contract.digest = sha256:__DIGEST_364FF__ (of THIS task spec file).
criterion_ids = [C-FF1, C-FF2, C-FF3].
C-FF1: prove-it's two bans are scoped to the case tree; a committed libcst-venv row
(a .venv holding mutmut/libcst beside the fix) PASSES; committed excerpts assert the
bans still hit real tautologies.
C-FF2: oncall-it's two **/*.py bans are scoped the same way, with a committed venv
row passing beside the fix.
C-FF3: the full suite stays green (1339 in source, plus only YOUR new tests); the
routing gate still passes; the V2 violating-workspace rows for prove-it/oncall-it
still fail (if scoping legitimately changes a V2 row's verdict, update the row and
disclose why — never silently).
NC-COMMAND: python3 -m unittest tests.test_evals

STEPS:
1) Red FIRST: (a) a libcst-venv row for prove-it (mutmut/libcst excerpt in .venv
   beside the fix) FAILS pre-fix on the unscoped glob, passes post-fix; (b) the same
   shape for oncall-it; (c) excerpt rows proving each scoped ban still hits its real
   violation (fail if the ban is gutted). Expected values from the brief above
   (independent source), never recomputed the runner's way.
2) Smallest change: scope the four bans to the case tree (the deflake/harden
   pattern: tests/**, app-or-src/**, root *.py — match each case's own layout).
3) Recorder run of the nc-command + validate.py + FULL suite green (use
   runtime/scripts/evidence-run.py on a clean tree; commands[].artifact null
   everywhere — scratchpad transcripts are inlined summaries, never /tmp paths).
   ruff on touched files.
4) NEGATIVE CONTROL: tool=revert on skills/prove-it/evals/evals.json +
   skills/oncall-it/evals/evals.json (the two case files back to BASE);
   nc-command NONZERO reverted (the new venv rows fail), ZERO clean. Transcript
   recorded.
5) gitleaks detect clean before pushing.
6) Commit on u364ff-venv-globs (bisectable, maintainer author, no trailers, named
   staging). Push (egress.py write --sink git-push --host github.com --payload-class
   branch-tip --consent run-2026-09-14-clean-sweep:base-writes FIRST). No PR
   (integrator opens it). No merge/rebase onto BASE.
7) Manifest at docs/runs/2026-09-14-clean-sweep-tracker/u364ff-manifest.json (commit on
   branch): unit U364-FF, base SHA + head_sha := your last CONTENT commit
   (pre-manifest — a commit cannot name its own SHA; the manifest commit follows
   with a manifest-only delta and you name the pushed tip separately in
   worker_done; the conductor re-binds head_sha to the reviewed tip at close),
   contract above, C-FF1..C-FF3 with witnesses, commands, negative_control (revert,
   the two case files, NC-COMMAND verbatim, RED), intent non-empty, lighting lit,
   reviewer_mode same-vendor-fresh. Leave pr EMPTY. Commit the verbatim NC
   transcript as docs/runs/2026-09-14-clean-sweep-tracker/u364ff-negctrl.txt beside
   the manifest, pinned in artifacts[] (the U388/U364 precedent).

STOP: unexplained red; out-of-scope rot (note, do not touch); over 60 minutes.
ESCALATION: blocking ask. No sub-dispatch.

WORKER CONTRACT: preamble --from + --dispatch-capability on every send. check
--terminal <handle> at checkpoints + pre-worker_done; consumer_fenced = stop, no
worker_done. --report-path + --files-modified. worker_done --outcome, omit --to.
Worktree comment current.
