You are a clean-sweep BUILD worker for unit U389 (methodology pack: matt — read
$HOME/.agents/skills/tdd/SKILL.md and follow it; load no other pack).

GOAL · SCOPE · NON-GOALS · STOP · EVIDENCE · ESCALATION · BUDGET: build-change.
Work on branch u389-wip-schema in THIS worktree (forked from origin/BASE
review/2026-09-14-holistic-fixes @ e04b0c2 — verify with git log before starting; refuse a
dirty baseline or a wrong base). If the worktree branch is not u389-wip-schema, create it
from origin/review/2026-09-14-holistic-fixes first.

FINDING (agent-brief, verified by triage + coordinator differential repro):
CATEGORY: bug. The run-report checker's WIP-curve validation passes any mutating run
report containing at least one table row naming builder and reviewer counts. A
settings-only row passes; a multi-wave report with a single row passes; an unrelated
row carrying the two settings passes. The doctrine protocol requires one complete row per
dispatch wave carrying the WIP setting plus every metric the protocol table names
(builder throughput, verification latency as median and max, rework rate, freshness
violations).
DESIRED: a defined per-wave row schema (wave identity + WIP setting + all protocol
metrics); the checker requires one complete row per recorded wave; the protocol prose
names the schema so text and check cannot drift; tests blessing incomplete rows are
updated; no live tier claim breaks (none above doctrine-only).
OUT OF SCOPE: changing WIP caps; the multi-run graduation analysis; other report checks
(manifest binding, inventory, invocation). NOTICED-BUT-NOT-TOUCHED otherwise.

HOT FILES (re-derived at dispatch from e04b0c2): the run-report checker script, the
attention-budget protocol doc, the run-report test module. Touch nothing else. Never
`git add -A`.

CONTRACT (coordinator-issued — copy EXACTLY into the manifest):
contract.source = triage/brief-389.md@e04b0c2 + issue #389.
contract.digest = sha256:__DIGEST_389__ (of THIS task spec file).
criterion_ids = [C-1, C-2, C-3].
C-1: a settings-only row is refused.
C-2: a multi-wave report with partial or missing wave rows is refused.
C-3: complete per-wave rows bind, and the protocol prose names the enforced schema.
NC-COMMAND: python3 -m unittest tests.test_run_report

STEPS:
1) Red FIRST: failing tests proving a settings-only row binds today (it must bind pre-fix
   — that is the bug) and is refused post-fix; same for partial multi-wave rows. Expected
   values from the protocol text (independent source), never recomputed the checker's way.
   NOTE: one existing test blesses an incomplete row — it encodes the bug; update it to
   the schema and say so plainly in the commit message.
2) Smallest change: define the row schema (wave identity + setting + all metrics), enforce
   one complete row per recorded wave. "Recorded waves" = the waves the report itself
   records — define precisely and document the definition where the protocol names the
   schema. Keep the no-row refusal message shape (a cap recorded nowhere was never a cap).
3) Recorder run of the nc-command + validate.py + FULL suite green. ruff on touched files.
4) NEGATIVE CONTROL: tool=revert on the checker path; nc-command NONZERO reverted, ZERO
   clean. Transcript recorded.
5) gitleaks detect clean before pushing.
6) Commit on u389-wip-schema (bisectable, maintainer author, no trailers, named staging).
   Push (egress.py write --sink git-push --host github.com --payload-class branch-tip
   --consent run-2026-09-14-clean-sweep:base-writes FIRST). No PR (integrator opens it).
   No merge/rebase onto BASE.
7) Manifest at docs/runs/2026-09-14-clean-sweep-tracker/u389-manifest.json (commit on
   branch): unit U389, base/head SHAs, contract above, C-1..C-3 with witnesses, commands,
   negative_control (revert, checker path, NC-COMMAND verbatim, RED), intent non-empty,
   lighting lit, reviewer_mode same-vendor-fresh. Leave pr EMPTY.

STOP: unexplained red; out-of-scope rot (note, do not touch); over 90 minutes.
ESCALATION: blocking ask. No sub-dispatch.

WORKER CONTRACT: preamble --from + --dispatch-capability on every send. check
--terminal <handle> at checkpoints + pre-worker_done; consumer_fenced = stop, no
worker_done. --report-path + --files-modified. worker_done --outcome, omit --to.
Worktree comment current.
