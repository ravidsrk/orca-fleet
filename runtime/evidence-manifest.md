# Runtime policy — the evidence manifest (the definition of done)

This is how a fleet knows a unit of work is actually DONE. It replaces trace-grading, which is
not enforceable for a coordinator (it does not hold its workers' traces, and a trace proves an
action was attempted, not that the resulting state is correct — an agent can run the right-looking
commands against the wrong SHA or a stale environment).

Completion is a two-part protocol: the worker emits a **SHA-bound evidence manifest**, and an
**independent verifier** checks its claims against **authoritative state** (git, the test runner
in a clean env, the runtime, the deploy target). A unit advances only when verification passes.

## 1. The manifest (every worker emits this in `worker_done`)

The worker writes it to `reportPath` and names that path in the `worker_done` payload. Shape
(JSON; a mission may add fields but never drops these):

```json
{
  "unit": "<task-id / finding-id / slice-id>",
  "base_sha": "<the SHA the work started from>",
  "head_sha": "<the SHA the work produced>",
  "base_branch": "<the integration BASE the PR targets>",
  "criteria": [
    {"id": "AC-1", "text": "<the exact acceptance criterion>", "addressed": true}
  ],
  "commands": [
    {"cmd": "pnpm test src/pay", "exit": 0, "artifact": "docs/reports/<unit>/test.txt"}
  ],
  "negative_control": {
    "did": "reverted the production change / mutated the boundary",
    "result": "the targeted test went RED",
    "artifact": "docs/reports/<unit>/revert.txt"
  },
  "artifacts": ["docs/reports/<unit>/…"],
  "pr": {"number": 0, "url": "", "reviewed_sha": "<SHA the reviewer approved>"},
  "toolchain": "<node 24 / python 3.12 / …>",
  "parked": [{"item": "<what>", "reason": "<one-way / no-safe-sandbox / needs-human>", "gate": "<gate id>"}],
  "claim": "<the worker's own summary — informational only, NEVER the completion oracle>"
}
```

Rules:
- `base_sha` and `head_sha` are REQUIRED and must be real commits. "It works" with no SHA is not
  a manifest.
- `criteria` lists the ACTUAL acceptance criteria from the task spec, each marked addressed or not.
  A criterion with no addressing evidence is unmet work, not a waiver.
- `negative_control` is REQUIRED for any unit that claims a fix or a test: show the proof FAILS
  when the change is reverted/mutated (a green test over reverted code proves nothing). The
  specific control differs per mission (a bug fix reverts the production line; a coverage test
  applies a semantics-preserving mutation; a perf fix compares before/after to the metric contract).
- `commands` pastes real invocations + exit codes with artifact paths. Never a summary.
- `pr.reviewed_sha` is the SHA the build-blind reviewer actually reviewed (see
  reviewed-sha-freshness.md). It gates the merge.
- `claim` is the worker's narration. The verifier ignores it except as a hint.

## 2. Independent verification (the coordinator, or a fresh verifier worker)

A DIFFERENT session than the one that produced the work checks the manifest against authoritative
state. The manifest is a claim; these are facts:

| Check | How (authoritative source) |
|-------|----------------------------|
| The commit exists on the intended base | `git merge-base --is-ancestor <head_sha> origin/<base_branch>` after the merge; before merge, `git cat-file -e <head_sha>` and the PR's `baseRefName == base_branch` |
| Tests pass at that exact SHA in a clean env | check out `head_sha` in a fresh worktree, run the suite, confirm green — do NOT trust the pasted output alone for the critical path |
| The negative control really fails | on a sample (≥10%), a fresh worker reverts/mutates and confirms the proof goes RED |
| The review is fresh | `pr.reviewed_sha == head_sha` (a rebase after review voids it — reviewed-sha-freshness.md) |
| The change is real on base | after merge, a file/symbol from the unit is greppable on `origin/<base_branch>` |
| Deployed == reviewed (ship only) | the deployed revision equals the reviewed/merged SHA |
| The metric contract is met (measurement units) | the benchmark/coverage/streak satisfies its PRE-DECLARED statistical contract, not a lucky single run |

Verification failing on any required check → the unit is NOT done; it returns to its state
machine (re-dispatch, or SUSPECT if provenance says done but git disagrees).

## 3. Standing definition-of-done floor (every mission, on top of its own contract)

A unit is done only when its own acceptance criteria AND this floor both hold:

- **Runtime-verified, not just compiled/typechecked** — the change behaves as intended when the
  real path is exercised, not merely that it builds.
- **No new red** — the suite (and CI where the mission touches it) is green at the unit's head SHA.
- **Evidence exists** — the manifest is present, SHA-bound, with a passing negative control.
- **Parked is named** — anything not done is PARKED with a reason and a gate, never silently dropped.

## Why this and not trace-grading

Traces live in separate terminals, get truncated/compacted, and are gameable. The manifest binds
every claim to a SHA and an artifact; the verifier re-derives the facts from git and a clean run.
This is exactly what made `clean-sweep`/`spec-to-ship` reliable ("verify, never trust"): a
`worker_done` that says "merged" is a claim to check, not a fact to record.
