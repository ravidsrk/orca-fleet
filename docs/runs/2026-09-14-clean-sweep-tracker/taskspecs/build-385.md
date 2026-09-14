You are a clean-sweep BUILD worker for unit U385 (methodology pack: matt — read
$HOME/.agents/skills/tdd/SKILL.md and follow it; load no other pack).

GOAL · SCOPE · NON-GOALS · STOP · EVIDENCE · ESCALATION · BUDGET: build-change.
Work on branch u385-parity in THIS worktree (forked from origin/BASE
review/2026-09-14-holistic-fixes @ e04b0c2 — verify with git log; refuse a dirty baseline
or wrong base). If the branch is not u385-parity, create it from
origin/review/2026-09-14-holistic-fixes first.

FINDING (agent-brief, agent slice of split #385 — verified at triage; diagrams are a
parked human item, NOT this unit):
CATEGORY: bug (documentation). Most polish already landed on the branch. Two gaps remain:
the machine-readable completion status record still names a snapshot commit predating
the fixes it describes, and no automated check enforces that every mission guide embeds
its diagram asset (sixteen guides do; four have no asset at all).
DESIRED: the status record names the commit the snapshot actually describes; an automated
parity check asserts every mission guide embeds its diagram asset, with an explicit
known-gap list naming the four missing diagrams until they exist.
OUT OF SCOPE: rendering the four missing diagrams (parked human item — do not invent,
copy, or reference assets that do not exist); any other completion-docs prose.
NOTICED-BUT-NOT-TOUCHED otherwise.

HOT FILES (re-derived at dispatch from e04b0c2): the completion status record, the
docs-navigation test module. Touch nothing else. Never `git add -A`.

CONTRACT (coordinator-issued — copy EXACTLY):
contract.source = triage/brief-385-slice.md@e04b0c2 + issue #385 (agent slice).
contract.digest = sha256:__DIGEST_385__ (of THIS task spec file).
criterion_ids = [C-1, C-2].
C-1: the status commit field matches the tree the snapshot describes.
C-2: the parity test fails if any listed guide loses its diagram, with a known-gap list
naming exactly the four missing diagrams.
NC-COMMAND: python3 -m unittest tests.test_docs_navigation

STEPS:
1) Red FIRST: the parity test must FAIL on the branch today (four guides without assets
   and no enforcement). Write it against the guides index + assets directory with the
   known-gap list as an explicit constant (gaps named, not silently skipped). Expected
   values from the on-disk state (independent source), never from the implementation.
2) Smallest change: status commit field to the commit the snapshot describes (derive it
   from the snapshot's own contents — the run-3 merge it claims to include — and show the
   derivation in the commit message); parity test + known-gap list of exactly four.
3) Recorder run of the nc-command + validate.py + FULL suite green. ruff on touched files.
4) NEGATIVE CONTROL: tool=revert on BOTH touched paths (record + test module together —
   reverting only the test kills the oracle, so the control reverts the pair and requires
   the nc-command NONZERO; additionally demonstrate the test alone goes RED when one
   listed guide reference is removed in a throwaway worktree, then discard it). Transcript.
5) gitleaks detect clean before pushing.
6) Commit on u385-parity (bisectable, maintainer author, no trailers, named staging).
   Push (egress.py write --sink git-push --host github.com --payload-class branch-tip
   --consent run-2026-09-14-clean-sweep:base-writes FIRST). No PR. No merge/rebase.
7) Manifest at docs/runs/2026-09-14-clean-sweep-tracker/u385-manifest.json (commit on
   branch): unit U385, base/head SHAs, contract above, C-1..C-2 with witnesses, commands,
   negative_control (revert, both paths, NC-COMMAND verbatim, RED), intent non-empty,
   lighting lit, reviewer_mode same-vendor-fresh. Leave pr EMPTY.

STOP: unexplained red; out-of-scope rot (note, do not touch); over 90 minutes.
ESCALATION: blocking ask. No sub-dispatch.

WORKER CONTRACT: preamble --from + --dispatch-capability on every send. check
--terminal <handle> + pre-worker_done; consumer_fenced = stop, no worker_done.
--report-path + --files-modified. worker_done --outcome, omit --to. Comment current.
