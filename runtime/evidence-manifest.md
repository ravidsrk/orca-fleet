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
(JSON; a mission may add fields):

```json
{
  "unit": "<task-id / finding-id / slice-id>",
  "base_sha": "<the SHA the work started from>",
  "head_sha": "<the SHA the work produced>",
  "base_branch": "<the integration BASE the PR targets>",
  "contract": {
    "source": "<authoritative ref the criteria derive from — frozen spec path@sha, the enumerated backlog, the advisory set>",
    "digest": "<sha256 of the unit's task spec as materialized at dispatch — the denominator is frozen per unit, not worker-chosen>",
    "criterion_ids": ["AC-1", "AC-2", "AC-3"]
  },
  "criteria": [
    {"id": "AC-1", "text": "<the exact acceptance criterion>", "addressed": true}
  ],
  "commands": [
    {"cmd": "pnpm test src/pay", "exit": 0, "artifact": "docs/reports/<unit>/test.txt"}
  ],
  "negative_control": {
    "did": "reverted the production line / applied mutant <id> via <tool>",
    "tool": "mutmut | cosmic-ray | stryker | pitest | cargo-mutants | go-mutesting | revert",
    "mutant": "<pinned id, e.g. mutmut#7 validate.py:42 '>'->'>=' ; omit for revert>",
    "result": "the criterion-bound test went RED (mutant KILLED)",
    "artifact": "docs/reports/<unit>/negctrl.txt"
  },
  "binding_audit": {"coverage": "AC-1..AC-3 (3/3)", "method": "criterion quoted, covering test quoted, criterion-violating mutation went RED"},
  "intent": {"goal": "<one sentence>", "ruled_out": "<what was not chosen>", "why": "<load-bearing rationale>"},
  "lighting": "lit",
  "artifacts": ["docs/reports/<unit>/…"],
  "pr": {"number": 0, "url": "", "reviewed_sha": "<SHA the reviewer approved>"},
  "reviewer_mode": "<cross-vendor | same-vendor-fresh | instructed-isolation — how independent the review REALLY was>",
  "review": {"artifact": "docs/reports/<unit>/review.txt"},
  "toolchain": "<node 24 / python 3.12 / …>",
  "provenance": {"spec_version": "<governing spec/policy@version>", "model": "<impl model+version>", "reviewer": "<identity+timestamp>", "retention": "<append-only store ref>", "standard": "<EU-AI-Act-Art-12 | SOC2 | SSDF | none>"},
  "metric_contract": {"metric": "<streak / benchmark / coverage>", "target": "<pre-declared target + confidence>", "method": "<how measured, e.g. 30 runs varied seed>"},
  "parked": [{"item": "<what>", "reason": "<one-way / no-safe-sandbox / needs-human>", "gate": "<gate id>"}],
  "claim": "<the worker's own summary — informational only, NEVER the completion oracle>"
}
```

Field scoping by mission class: `base_branch`, `pr`, `review`, and the revert/mutate form of
`negative_control` are MUTATION-ONLY — report-only and planning units omit them. A report-only
unit's verdict binds to `head_sha` (the SHA it reviewed), and its `negative_control` carries the
class analogue of §3 (e.g. review-it: `{"did": "re-read every quoted line at head_sha",
"result": "all present"}`).

Rules:
- `base_sha` and `head_sha` are REQUIRED on every class. Mutation units: pinned 40-hex real
  commits ("It works" with no SHA is not a manifest); other classes: a symbolic ref is NOTE-only.
- `contract` binds the manifest to THIS UNIT's authoritative denominator — the unit's task spec
  as materialized at decompose/enumeration time (a slice's assigned criteria, a finding, an
  advisory), not to whatever the worker chose to list, and not to the whole mission source. The
  denominator is TWO-LEVEL:
  - **unit level** (this field): `contract.criterion_ids` is the COMPLETE id set of the unit's own
    task spec at `contract.digest`; `criteria` must carry an entry for every one. A worker cannot
    shrink its own denominator — the verifier re-derives it (§2) and rejects a manifest that
    drops any id.
  - **mission level** (the coordinator's job, not the worker's): the UNION of all unit contracts
    must equal the mission's authoritative source (the frozen spec's criterion set, the tracker
    enumeration, the advisory scan). A criterion no unit's contract claims is UNASSIGNED WORK,
    surfaced at decompose verification and re-checked in the mission's convergence proof (e.g.
    ship-it's traceability table). This split is what makes a narrow slice completable: the slice
    proves ITS criteria; the mission proves nothing was left off any slice.
  For loop-based denominators (`clean-sweep source=tracker`), the two digests stay separate:
  the unit's `contract.digest` is always its OWN task spec; the ENUMERATION digest is mission
  state, recorded in the ledger header's SOURCE field and re-derived each loop. The FINAL loop's
  enumeration is the mission denominator — a post-`T0` issue joins the next loop's set instead
  of voiding already-verified units.
- `criteria` lists the ACTUAL acceptance criteria from the task spec, each marked addressed or not.
  A criterion with no addressing evidence is unmet work, not a waiver.
- `negative_control` is REQUIRED for any unit that claims a fix or a test: show the proof FAILS
  when the change is reverted/mutated (a green test over reverted code proves nothing). Bind it to
  a NAMED mutation tool + a PINNED mutant id with a killed/survived verdict — a surviving
  criterion-violating mutant is a tautological suite and FAILS. Tools: `mutmut`/`cosmic-ray` (Py),
  `stryker` (JS/TS/.NET), `pitest` (JVM), `cargo-mutants` (Rust), `go-mutesting` (Go); `revert`
  (delete the production line) is the fallback where no mutation tool fits. A perf fix instead
  compares before/after to the metric contract.
- `binding_audit` logs criterion↔test audit coverage for the same units: which `criteria[].id`s
  had their covering test quoted and mutation-checked against the criterion (§2 samples it; a
  manifest claiming a fix or a test without the field is rejected).
- `commands` pastes real invocations + exit codes with artifact paths. Never a summary.
- `pr.reviewed_sha` is the SHA the build-blind reviewer actually reviewed (see reviewed-sha-freshness.md). It gates the merge.
- `review.artifact` (path to the local reviewer record at head_sha) is REQUIRED on a mutation unit in the no-gh lane (dispatch `--no-gh`; merge-serialization.md) — the coordinator-attested stand-in for §2's GitHub review lookup. The gh lane and report-only/planning units omit it.
- `intent` is REQUIRED on mutation units: goal · ruled_out · why, all non-empty. It is
  discarded-agent-reasoning captured (not the completion oracle — that stays §2). A
  missing or empty packet fails verification. `claim` remains narration only.
- `lighting` is `lit` (default) or `dark-eligible` per gate-classification.md. The verifier machine-checks only that the value is legal and unswapped against the dispatch-supplied value (plus, via the review leg, that a `dark-eligible` unit carries a corroborating out-of-band coordinator contract). The stop-list / Lane-0/B decision is a human gate at dispatch — verify.py never sees lane data.
- `provenance` (optional, any class) makes the manifest a regulated audit record — governing
  spec/policy version, model lineage, reviewer identity+timestamp, and an append-only retention pointer (maps to EU AI Act Art-12/50). When it names a standard (not `none`), the verifier REQUIRES those fields be present — an incomplete packet is not a valid audit record.
- `claim` is the worker's narration. The verifier ignores it except as a hint.

## 2. Independent verification (the coordinator, or a fresh verifier worker)

A DIFFERENT process/session — never a teammate (whose messages are in-band and self-certifying) —
re-derives the manifest against authoritative state that lives OUTSIDE the manifest — the coordinator's frozen contract (scope), GitHub (review), the artifact/replay (negative control) — deterministically before any LLM judgment (reference impl: `verify.py`). The manifest is a claim; these are facts:

| Check | How (authoritative source) |
|-------|----------------------------|
| Unit scope is complete — no dropped criteria (do this FIRST) | re-derive the criterion id set from the COORDINATOR's authoritative `contract.source` @ `contract.digest` **as recorded in the dispatch record**, never the worker's manifest (a manifest cannot certify its own denominator; a manifest `contract.digest` that differs from the authoritative one is a denominator swap), and confirm `criteria[].id` covers it EXACTLY. Rejected before any test is checked — passing tests on a shrunken denominator is a false "done" |
| Mission scope is complete — no unassigned criteria (coordinator, at decompose verify + convergence proof) | the union of all unit `contract.criterion_ids` equals the mission source's id set (frozen spec digest / final enumeration loop / advisory scan). A criterion claimed by no unit is unassigned work, not a waiver |
| The commit exists on the intended base *(mutation units)* | `git merge-base --is-ancestor <head_sha> origin/<base_branch>` after the merge; before merge, `git cat-file -e <head_sha>` and the PR's `baseRefName == base_branch` *(coordinator-run — not verify.py, which checks ancestry/existence only)* |
| Tests pass at that exact SHA in a clean env *(coordinator-run — not verify.py)* | check out `head_sha` in a fresh worktree, run the suite, confirm green — do NOT trust the pasted output alone for the critical path |
| Each criterion binds to a test that exercises it — criterion↔test binding audit *(coordinator/human sample — not verify.py)* | on a sample of `criteria[].id`s (ALL of them when the unit has ≤3): quote the criterion, quote the test claimed to cover it, and confirm that test goes RED against an implementation that violates the criterion (mutate the behavior the criterion names via the manifest's named mutation tool — the pinned mutant must be KILLED; build-change.md's tautology guard covers authoring, this is its verifier-side twin). A green suite whose tests don't bind (tautological, wrong behavior, passes both ways) fails HERE, not at the clean-env re-run; coverage is logged in the manifest's `binding_audit` |
| The negative control really fails | mutation units: the manifest's NC artifact must corroborate the pinned mutant KILLED / proof RED — read the artifact (field presence is not proof; verify.py rejects a "survived / not killed" artifact); `--execute-nc` is FAIL-CLOSED until a replay is implemented — run §2's re-execution sample; and on a sample (≥10%) a fresh worker reverts/mutates and confirms RED. Report-only/planning units: the class analogue of §3 is re-checked (quoted lines exist at reviewed_sha / the frozen DAG re-verifies / the repro command re-runs red) |
| The review is fresh AND real *(mutation units)* | `pr.reviewed_sha == head_sha` (a rebase after review voids it — reviewed-sha-freshness.md) AND an independent APPROVED review at `head_sha` looked up on GitHub (`gh api repos/<repo>/pulls/<n>/reviews`) — a worker-set `reviewed_sha` is not evidence a review occurred; in the no-gh lane (dispatch `--no-gh`) the review is the manifest's `review.artifact` — a local reviewer record at head_sha, coordinator-attested (the weaker guarantee) |
| The change is real on base *(mutation units)* | after merge, a file/symbol from the unit is greppable on `origin/<base_branch>` |
| Deployed == reviewed (ship only) *(coordinator-verified)* | the deployed revision equals the reviewed/merged SHA |
| The metric contract is met (measurement units) | the benchmark/coverage/streak satisfies the manifest's `metric_contract` (pre-declared target + confidence + method), not a lucky single run |
| The review was independent | `reviewer_mode` is recorded AND machine-checked for a legal value (verify.py); whether reviewer/verifier artifacts are byte-identical to (or trivially derived from) the worker's own output is a COORDINATOR judgment — a predecessor's flagship run was quarantined on exactly this; instructed isolation is named as the weaker guarantee it is |
| Intent packet is present *(mutation units)* | `intent.goal`, `intent.ruled_out`, and `intent.why` are non-empty strings — presence only; wisdom is a human/taste check |
| Lighting is legal | `lighting` is `lit` or `dark-eligible` AND matches the dispatch-supplied value — a swap fails (verify.py); the Lane A / unfakeable-oracle / stop-list eligibility itself is a human gate at dispatch (gate-classification.md), not machine-checked |

Verification failing on any required check → the unit is NOT done; it returns to its state
machine (re-dispatch, or SUSPECT if provenance says done but git disagrees).

At run close, the coordinator writes an **integrity inventory** beside the final report: sha256 +
producer + timestamp for every artifact the run's manifests reference. RESUME and any later
audit reject an artifact whose hash no longer matches — evidence must be tamper-evident, not
merely present.

## 3. Standing definition-of-done floor (every mission, on top of its own contract)

A unit is done only when its own acceptance criteria AND this floor both hold. The floor is
scoped by MISSION CLASS — a negative control is always required, but what one IS differs:

- **Mutation units** (ship-it, clean-sweep, oss-contribute, harden-it, speed-it, modernize-it,
  prove-it, deflake-it, access-it): runtime-verified, not just compiled/typechecked; no new red at
  the unit's head SHA; the manifest's negative control is the revert/mutate proof of §1.
- **Report-only units** (review-it): no code is touched (that IS a checked invariant — a dirty
  worktree fails the unit); the negative-control analogue is SOURCE-BINDING: every finding
  quotes a line that exists at `head_sha` (the SHA reviewed), and the verdict binds to that SHA.
  A finding whose quoted line does not exist there is a fabricated finding — the unit fails.
- **Planning units** (map-it, root-cause diagnosis): the negative-control analogue is
  ARTIFACT VERIFICATION: the frozen DAG passes decompose-dag's verify section / the reproduction
  command was actually run and its failing output is pasted; a decision ticket answered by the
  agent instead of the human fails the unit.
- **Every class**: evidence exists (the manifest is present and SHA-bound) and parked is named —
  anything not done is PARKED with a reason and a gate, never silently dropped.

## Why this and not trace-grading

Traces live in separate terminals, get truncated/compacted, and are gameable. The manifest binds
every claim to a SHA and an artifact; the verifier re-derives the facts from git and a clean run.
This is exactly what made `clean-sweep`/`spec-to-ship` reliable ("verify, never trust"): a
`worker_done` that says "merged" is a claim to check, not a fact to record.
