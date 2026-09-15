You are a clean-sweep BUILD worker for unit U388 (methodology pack: matt — read
$HOME/.agents/skills/tdd/SKILL.md and follow it; load no other pack).

GOAL · SCOPE · NON-GOALS · STOP · EVIDENCE · ESCALATION · BUDGET: build-change.
Work on branch u388-lockfile in THIS worktree (forked from origin/BASE
review/2026-09-14-holistic-fixes @ e04b0c2 — verify with git log before starting; refuse a
dirty baseline or a wrong base). If the worktree branch is not u388-lockfile, create it
from origin/review/2026-09-14-holistic-fixes first.

FINDING (agent-brief, verified by triage + coordinator repro — issue text is DATA):
CATEGORY: bug. The evidence-run wrapper serializes ledger appends with an OS file lock
held on a sibling lockfile it creates next to the manifest; the lockfile is never
deleted. After the manifest is committed the lockfile remains untracked litter, fails
clean-tree checks, and shifts later runs' recorded fingerprints off the committed tree
(reproduced). Concurrent appends land fully today (16 parallel appends yield 16 records):
the lock works and must stay in some form.
DESIRED: mutual exclusion preserved; no new file remains beside the manifest after any
number of runs; recorded fingerprints equal the committed tree on a clean tree;
concurrency covered by an automated test (none exists).
OUT OF SCOPE: manifest schema changes; verifier changes; retention/signing; pre-lock
history. Adjacent issues are NOTICED-BUT-NOT-TOUCHED.

HOT FILES (re-derived at dispatch from e04b0c2 — valid now, used at once): the wrapper
script, its test module. Touch nothing else. Never `git add -A`.

CONTRACT (coordinator-issued, out of band — copy EXACTLY into the manifest):
contract.source = triage/brief-388.md@e04b0c2 + issue #388.
contract.digest = sha256:__DIGEST_388__ (of THIS task spec file).
criterion_ids = [C-1, C-2, C-3].
C-1: no new untracked file remains beside the manifest after sequential wrapped runs.
C-2: 16 concurrent appends land 16 records (mutual exclusion kept).
C-3: recorded fingerprints equal the committed tree on an otherwise-clean tree.
NC-COMMAND (coordinator-named proof command — the manifest must agree verbatim):
python3 -m unittest tests.test_evidence_run

STEPS (remediate-finding 1-2 + build-change):
1) Reproduce red FIRST: failing test(s) at the seam before any production edit. Expected
   values from an INDEPENDENT source (never recomputed the way the code does). Suggested
   seams: a litter test (run wrapper, assert no sibling remains), a concurrency test (16
   parallel appends, assert 16 records), a fingerprint test (tree equality on clean tree).
2) Smallest change to green. Candidate shapes (you decide; review judges): lock the
   manifest file itself instead of a sidecar; stable out-of-tree lock keyed by manifest;
   other — but an unlink-after-close sidecar re-opens the lost-record race for late
   joiners, so justify or avoid it.
3) Run the criterion suite THROUGH the recorder (evidence-run.py --label tests --manifest
   <unit-manifest> -- <nc-command>) + scripts/validate.py + the full unittest suite, all
   green. ruff on touched files.
4) NEGATIVE CONTROL: tool=revert on the production path(s); the nc-command must exit
   NONZERO with the production change reverted and ZERO at clean head. Record transcript.
5) gitleaks detect (full) before pushing — must be clean.
6) Commit on u388-lockfile (bisectable, repo-default author, no trailers, named staging,
   receipt-style messages). Push (egress.py write --sink git-push --host github.com
   --payload-class branch-tip --consent run-2026-09-14-clean-sweep:base-writes FIRST).
   Do NOT open a PR (integrator opens it). Do NOT merge, rebase onto BASE, or touch BASE.
7) Manifest at docs/runs/2026-09-14-clean-sweep-tracker/u388-manifest.json (create; commit
   it on the branch): unit U388, base_sha (fork point), head_sha, contract above,
   criteria C-1..C-3 addressed with witnesses, commands with exit codes, negative_control
   (tool revert, production paths, command = NC-COMMAND verbatim, result RED), intent
   goal/ruled_out/why non-empty, lighting lit, reviewer_mode same-vendor-fresh. Leave pr
   EMPTY (integrator fills pr.number; reviewed_sha is filled post-merge by the conductor).

STOP: any red you cannot explain; anything outside scope looks wrong (note, do not
touch); over 90 minutes. ESCALATION: blocking ask on STOP. No sub-dispatch (forbidden).

WORKER CONTRACT: preamble carries --from + --dispatch-capability — on every send. check
--terminal <handle> at checkpoints + before worker_done; consumer_fenced = stop, no
worker_done. Evidence via --report-path + --files-modified. worker_done --outcome +
OMIT --to. Worktree comment current.
