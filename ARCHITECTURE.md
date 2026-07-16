# orca-fleet architecture

A fleet is an **outcome**, not an ingredient. Missions are named for what they achieve
("ship it", "close every issue", "find the root cause"), never for the pack whose technique
a worker happens to run. This repo has no `matt-*` or `gstack-*` skills. The upstream packs
(mattpocock/skills, garrytan/gstack, addyosmani/agent-skills) are sources of *recipes* that
missions compose; the Orca runtime is the substrate every mission rides.

## Three layers, strictly separated

```
MISSIONS   (skills/, discoverable)     ← the only user-facing skills. One outcome each.
   │  compose, by reference, →
PLAYBOOKS  (playbooks/, callable)       ← reusable phase protocols. NOT auto-triggering skills.
   │  run on, →
RUNTIME    (runtime/, invisible)        ← Orca primitives + policies. Called, not discovered.
```

> Missions are discoverable. Playbooks are callable. Runtime mechanisms are invisible unless
> directly administered.

Publishing playbooks or runtime mechanisms as auto-triggering skills would recreate the exact
routing collisions and ingredient-shaped entry points this repo exists to remove. So:

- **Missions** are `skills/<name>/SKILL.md` — the discoverable catalog. Each is one outcome
  with a distinct state machine and an evidence-based definition of done.
- **Playbooks** are `playbooks/<name>.md` — plain protocol docs a mission references by bare
  name (never a path) and injects into worker task specs. They are versioned, executable
  protocols with checkable completion criteria, never attribution summaries of "best of X + Y".
- **Runtime** is `runtime/*.md` policies + `runtime/scripts/` shared tooling — the Orca
  dispatch/gate/merge/liveness/sandbox mechanics. Missions call these; users don't invoke them.

## What makes a mission a mission (not a mode of another)

Two workflows are the **same mission** only if they share ALL five:

1. the same unit of work,
2. the same per-unit state machine,
3. the same convergence proof (definition of done),
4. the same ordering and isolation constraints,
5. the same parking / failure semantics.

"Inventory → fix → repeat" is not enough — almost every maintenance process paraphrases that
way. By this test, closing audit findings, tracker issues, and false doc-claims are one mission
(`clean-sweep`), but security hardening, perf budgeting, dependency modernization, test-debt
proving, and flake eradication are NOT — their denominators and convergence proofs differ, so
each is its own mission.

## The definition of done is an evidence protocol, not trace-grading

A coordinator does not hold its workers' terminal traces, and a trace proves an action was
*attempted*, not that the resulting state is *correct* (an agent can run the right-looking
commands against the wrong SHA). So completion is never graded on narration or trace.

Every unit of work emits a **SHA-bound evidence manifest** (see
[`runtime/evidence-manifest.md`](runtime/evidence-manifest.md)): base SHA → head SHA, the exact
acceptance criteria addressed, commands run with exit codes, artifact paths (logs, reports,
screenshots, benchmarks), the negative-control result, PR + reviewed SHA, and any parked items.
An **independent verifier** then checks facts against authoritative state: does the commit exist
on the intended base, do tests pass at that exact SHA in a clean environment, does mutating the
fix break the proof, does the deployed revision equal the reviewed revision. The Orca provenance
DB records the lifecycle and evidence references; traces are for forensic audit, never the
completion oracle.

## The operational details ARE the product

`clean-sweep` and `spec-to-ship` worked because of their ugly operational specifics, not despite
them. These are preserved as runtime policies, not abstracted away:

- Orca DAG semantics for CLI fleets (global DB, handle-scoped runs, deps-not-parent_id, real vs
  fictional message types, gate lifecycle ≠ blocking) — `runtime/orca-dag-semantics.md`
- Ledger boolean gates, `CODE_CLOSED`/`VERIFY_AT_SCALE`, DECISIONS.md, CONTEXT HANDOFF —
  `runtime/ledger-contract.md`
- wrong-base detection (BASE ≠ default, canonical-ref comparison) — `runtime/dispatch-lifecycle.md`
- coordinator inbox mechanics + worktree retirement (one message per `check`, read-marking,
  broadcast-only groups, verified teardown) — `runtime/dispatch-lifecycle.md`
- reviewed-SHA freshness (a rebase voids the review) — `runtime/reviewed-sha-freshness.md`
- ledger recovery / crash-resume from provenance, cross-run anti-inflation — `runtime/liveness-resume.md`
- bot-autofix non-convergence (Cursor BugBot Autofix loops) — `runtime/dispatch-lifecycle.md`
- bounded review loops, hot-file ownership, merge serialization — `runtime/merge-serialization.md`
- attention budget / orchestration tax (scale to review rate, not spawn UI) —
  `runtime/attention-budget.md`
- promotion semantics (human gate; merge ≠ deploy) — `runtime/gate-classification.md`
- gated sequential chains (an audit gates, it never always-flows) — `runtime/mission-chaining.md`

## Proof over doctrine

This repo's predecessor (ravidsrk/autonomous-fleet) died of doctrine outrunning evidence: twelve
missions with two proven, a portable substrate with zero field hours, and ~42K tokens of mandatory
instruction surface. Two structural guards inherit that lesson:

- **Proof status.** Every mission's frontmatter carries `proof:` — `doctrine-only`, `self-run`,
  or `external-run`. Advancing past doctrine-only requires `proof_evidence:` pointing at a run
  report that exists on disk; `scripts/validate.py` enforces both. A mission is never presented
  as more proven than its evidence.
- **Instruction budget.** Missions ≤ 130 lines, playbooks ≤ 90, runtime policies ≤ 160, enforced
  by the validator. Raising a cap is a deliberate, reasoned edit — never drift.

## Governance is uniform and below the model

- Every decision is classified **mechanical / taste / one-way** and resolved per
  `runtime/gate-classification.md`. One-way doors always override any auto-decide preference.
- Autonomy tracks the session kind: spawned → auto-pick recommended; headless → block on the
  unanswerable; interactive → prose brief. A fleet never fakes a human answer.
- One router per worker: a worker TASK loads exactly one upstream pack's playbooks (they fight
  when co-mounted). Missions compose across packs at the mission level, one pack per worker.

## Layout

```
skills/       missions (discoverable, one dir each)
playbooks/    callable protocols
runtime/      policies + runtime/scripts/ (spawn_worker, preflight, pm) — shared, not vendored
docs/         human documentation: getting started, concepts, per-mission guides
assets/       banners and images
scripts/      validate.py
tests/        contract tests
```
