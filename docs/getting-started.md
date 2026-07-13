# Getting started with orca-fleet

This guide takes you from a fresh clone to your first completed mission, explains what you will
see on screen while a fleet runs, and covers the failure modes new users hit most. It assumes you
have used Claude Code before but never run a multi-agent fleet.

## Contents

- [Prerequisites](#prerequisites)
- [Install the catalog](#install-the-catalog)
- [Your first mission: a review-it dry run](#your-first-mission-a-review-it-dry-run)
- [Your second mission: ship-it end to end](#your-second-mission-ship-it-end-to-end)
- [What you will see while a fleet runs](#what-you-will-see-while-a-fleet-runs)
- [Where the evidence lands](#where-the-evidence-lands)
- [Your side of the human gates](#your-side-of-the-human-gates)
- [Troubleshooting](#troubleshooting)

## Prerequisites

Two hard requirements, without which no mission will start:

1. **The Orca runtime and its `orchestration` skill** (shipped with the Orca CLI, not with this
   repo). Missions are coordinators for Orca fleets: they create worktrees, spawn worker
   terminals, dispatch tasks, and read `worker_done` messages through Orca. Verify with:

   ```bash
   orca status --json
   ```

2. **`git` and `gh`**, authenticated. Fleets open PRs per unit of work and verify merges by
   ancestry; `gh auth status` must succeed. Repos on a tracker other than GitHub issues can use
   `orca linear` where a mission supports it.

Per-mission tooling on top of that — each mission declares its own in `SKILL.md` frontmatter:

| If you plan to run | Also install                                                        |
|--------------------|----------------------------------------------------------------------|
| harden-it          | `gitleaks`, plus an ephemeral per-workspace sandbox for exploit PoCs |
| speed-it           | Lighthouse/DevTools access, or a load/profiler harness                |
| modernize-it       | nothing extra — but CI must be green at baseline                     |
| prove-it           | a coverage tool your suite already supports                          |
| deflake-it         | nothing extra — CI history is read via `gh run list`                 |
| ship-it            | your deploy tooling, if you want the states past `RELEASED`          |

## Install the catalog

**Symlink (recommended while evaluating).** Missions reference `../../playbooks/` and
`../../runtime/` relative to their own directory. A symlink preserves those references; a copy
severs them — this is the single most common broken-install cause.

```bash
git clone https://github.com/ravidsrk/orca-fleet.git
cd orca-fleet
ln -s "$(pwd)/skills/ship-it"   ~/.claude/skills/ship-it
ln -s "$(pwd)/skills/review-it" ~/.claude/skills/review-it
```

**Plugin (whole catalog).** The manifest at `.claude-plugin/plugin.json` installs all ten
missions at once; the relative references resolve inside the copied plugin directory:

```
/plugin marketplace add ravidsrk/orca-fleet
/plugin install orca-fleet
```

Confirm the install by asking your agent "which missions are available?" — the ten
outcome-named skills should list. If a mission is visible but errors on start about missing
playbooks, you copied instead of linking.

## Your first mission: a review-it dry run

Start with [`review-it`](missions/review-it.md), because it has **no fix authority** — the worst
it can do is be wrong in a report. In a repo with an open PR or a feature branch:

```
review this PR: is it ready to merge?
```

What happens, in order:

1. The coordinator pins the fixed point — a SHA or PR with a non-empty diff — and identifies
   the spec source (the PR description, the linked issue, a spec file).
2. Read-only workers (`PROFILE=ro`) run the acceptance axes in parallel isolation: repo
   standards, spec fidelity, test adequacy. Risk lenses (security, performance, accessibility,
   data migration) dispatch only if the diff triggers them.
3. Findings that cannot quote the exact line that motivated them drop to an appendix — that one
   rule removes most of the false positives you have seen from single-agent reviews.
4. You get a GO / NO-GO verdict bound to the reviewed SHA. Any Critical finding defaults the
   verdict to NO-GO.

Total cost: a few worker sessions, no writes, and you have now seen the coordinator/worker shape
without risking a single line of code.

## Your second mission: ship-it end to end

Pick something real but small — a feature you could build by hand in an afternoon.

```
ship this: add a /healthz endpoint that reports version and DB connectivity,
with tests, and stop at the promotion PR
```

The run in phases (the full tour is in [the ship-it guide](missions/ship-it.md)):

**Phase 0 — preflight.** The coordinator checks `orca status`, verifies the integration BASE is
not your default branch (`runtime/scripts/preflight.py`), and confirms the suite is green at
baseline. A red baseline stops the run — otherwise the fleet cannot tell its regressions from
your pre-existing ones.

**Phase 1 — the grill (your part).** Since you gave intent, not a spec, the coordinator
interviews you: one question at a time, each with a recommended answer. Facts it can look up in
the codebase it does not ask about. When the decision tree is resolved it publishes a spec —
objectives, acceptance criteria, explicit non-goals, test seams — and asks you to **freeze** it.
This is human gate #1. After the freeze, scope does not silently reopen.

**Phase 2 — decompose and build.** The spec is cut into tracer-bullet slices; each slice gets a
fresh worker in its own worktree and terminal. Workers write the failing test first and touch
only what their slice requires. You can watch, but nothing needs you.

**Phase 3 — review and prove.** Fresh sessions that did not write the code review each slice;
then the integrated whole is driven through its real entry point — for the example above,
an actual HTTP request to `/healthz` asserting the persisted response, plus a negative control
(revert the change, watch the test go red, restore).

**Phase 4 — land and stop.** A single conductor merges each reviewed slice into the integration
BASE, verifying ancestry and reviewed-SHA freshness. The fleet opens the BASE → default
**promotion PR** with a traceability table mapping every frozen criterion to a passing test, and
stops. Merging that PR is human gate #2 — always yours.

## What you will see while a fleet runs

A fleet is not one scrolling transcript. Expect:

- **The coordinator terminal** — where you started. It narrates phases, dispatches, and
  verification results, and it is where gates surface.
- **Worker terminals** — one per active slice/finding, each in its own git worktree. They open,
  work, emit a manifest, and are torn down. You never need to type into one.
- **The ledger** — a file the coordinator keeps (its memory gets compacted; the ledger
  survives). One row per unit: id, state, PR, reviewed SHA, merge SHA, evidence pointer. If you
  want to know where the run is, read the ledger, not the scrollback.
- **PRs on your repo** — one per unit of work, each targeting the integration BASE (never your
  default branch), each merged only by the conductor after verification.

## Where the evidence lands

Every unit of work produces a SHA-bound **evidence manifest** — the JSON contract described in
[concepts](concepts.md#the-evidence-manifest) and specified in
[`runtime/evidence-manifest.md`](../runtime/evidence-manifest.md). The parts worth reading as a
human:

- `base_sha` → `head_sha` — exactly what moved.
- `criteria[]` — every acceptance criterion from the frozen source, each marked addressed or
  not. The verifier re-derives this list; a worker cannot shrink it.
- `negative_control` — what was reverted or mutated, and proof the test went red.
- `commands[]` — real invocations with exit codes and artifact paths, not summaries.
- `claim` — the worker's own narration. Informational only; never the completion oracle.

When a coordinator says a unit is done, it means an independent verifier has already checked the
manifest against git and a clean test run — not that a worker said so.

## Your side of the human gates

Fleets classify every decision as **mechanical** (auto-resolved, audited), **taste**
(recommendation picked, batched for your veto, work continues), or **one-way** (yours, always).
You will be interrupted only for:

| Gate                             | When                       | What a good answer looks like |
|----------------------------------|----------------------------|-------------------------------|
| Freeze the spec                  | ship-it/map-it, intent entry | Read the acceptance criteria, not the prose. If a criterion is untestable, say so now — it is cheap here and expensive later. |
| Promotion to the default branch  | end of ship-it / clean-sweep | Review the traceability table on the PR, then merge it yourself. |
| Refuted/duplicate closes (batch) | clean-sweep                | Skim the refutation evidence; approve as a batch or pull items out. |
| One-way remediations             | harden-it (e.g. secret rotation) | Do the action, then confirm — the mission counts it done only when *verified*, not when acknowledged. |

An unattended run never fakes your answer: unanswerable one-way questions get parked with the
run continuing elsewhere, or the run winds down and tells you what it was blocked on.

## Troubleshooting

**"BASE is the default branch" and the run refuses to start.** Working as intended — fixes must
not land straight on production. Let the mission create its integration branch, or pass one that
forks from your default's history.

**A mission starts but workers never pick up tasks.** Check `orca status` and that the
`orchestration` skill is available in the worker context. The most common cause is running in a
repo where Orca is not initialized.

**Broken references to `../../playbooks/...`.** You copied a mission directory instead of
symlinking it, or installed a single skill with a tool that copies. Re-install per
[Install the catalog](#install-the-catalog).

**The suite was red before the fleet started.** Fleets refuse to build on a red baseline.
Run [`deflake-it`](missions/deflake-it.md) (if the red is intermittent) or fix the deterministic
failures first — [`clean-sweep`](missions/clean-sweep.md) can drain them as findings.

**A worker died mid-run / the coordinator crashed.** Nothing is lost: liveness is watched, dead
workers are respawned in fresh terminals with bounded attempts, and a dead coordinator resumes
from the ledger + Orca provenance, re-verifying every completed unit against git before trusting
it. See [`runtime/liveness-resume.md`](../runtime/liveness-resume.md).

**You want to know why a decision was made.** Mechanical decisions are audited in the ledger
with their reasoning; taste decisions arrive batched in a brief you can veto. If a fleet made a
one-way decision without you, that is a bug — file it.

---

Next: [Concepts](concepts.md) for the mental model behind fleets, or pick a
[mission guide](missions/) and go deep.
