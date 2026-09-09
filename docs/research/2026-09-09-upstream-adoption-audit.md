# Upstream adoption audit — orca-fleet vs its four skill sources

**Date:** 2026-09-09 · **Method:** cloned all four upstreams at current HEAD; four parallel deep
audits (one per source), every claim anchored to `file:line` on both sides; adoption points in
orca-fleet traced from README:469-471, playbooks, runtime policies, and mission frontmatter.

**Sources audited (commit-pinned; local clone paths are for this machine only — follow the links):**

| Source | Pinned revision | Upstream movement since orca-fleet started (2026-07-13) |
|---|---|---|
| mattpocock/skills | [`3cca18b`](https://github.com/mattpocock/skills/tree/3cca18b368ae95cdbdebbff572ccafa662551015) | grilling rewrite, redaction, planning-stack rename, new in-progress skills (169 commits) |
| garrytan/gstack | [`c8f0c4e`](https://github.com/garrytan/gstack/tree/c8f0c4e368fd59ec316c0eb0d1f4ebfa896c2d16) (v1.84) | content-bound evidence ledger, dispatch-recovery machinery, doc-sync step, 2 new lenses (65 commits, v1.60.1 → v1.84) |
| addyosmani/agent-skills | [`6ca0cd7`](https://github.com/addyosmani/agent-skills/tree/6ca0cd7db39b41b1c37e26d335c507ee92382c6d) (plugin v0.6.9) | destructive-path validation, perf keep-or-revert, constraint-driven-development, privacy rules |
| stablyai/orca (runtime) | [`65631e4`](https://github.com/stablyai/orca/tree/65631e449af36bba24b6a2d6c331a3c184e7a3e2) | **two rebuilds of the orchestration model**: #9925 Runs+worker-start+Delivery (07-27) · #16904 durable control plane (09-06→09-09) (~4,850 commits) |

> Note: `~/projects/agent-skills` on this machine is **ravidsrk/agent-skills** (our own
> capability-skills repo — cloudflare-dns, deep-research, terminal-poster…), not addyosmani's
> pack. The clone collided on the directory name; addyosmani's was cloned to
> `~/projects/addyosmani-agent-skills`. All upstream `file:line` anchors below resolve at the
> pinned revisions above.

---

## 1. Headline findings

1. **Our policy layer is two generations behind the Orca runtime it rides.** `runtime/*.md` and
   `runtime/scripts/spawn_worker.sh` were written 2026-07-13/14 against the pre-#9925 model:
   manual `terminal create` → `wait tui-idle` → `dispatch --inject` → blind-Enter → heartbeat
   folklore, one-message-per-`check`, machine-global scoping. Upstream replaced all of it
   (`worker-start` supervised path with typed refusals, 50-message Delivery batches replayed until
   `--ack`, Runs as the durable scope primitive, `worker-list` liveness projection, idempotent
   `--retry-request`, schema v40). **Today's own field run proves the drift, not the adoption** —
   it created a Run and *attempted* `worker-start`/`--retry-of`, but every `worker-start` failed on
   local substrate (claude trust dialog, expired OAuth, codex usage limit) and the completing
   workers ran as bare-shell tracked dispatches with manual prompt sends
   (`docs/completion/evidence/CF-05-r3-dispatch-record.txt`). The runtime accepted both generations
   of calls; our policy docs describe neither accurately.
2. **gstack moved onto our evidence-discipline turf — and in one place is now *more* precise than
   us.** Its `gstack-wtree` working-tree content fingerprint keeps a review CURRENT across a
   content-identical rebase where our `runtime/reviewed-sha-freshness.md:13-15` voids it (every
   conductor rebase currently forces full re-review of content the reviewer already read).
3. **Matt and Addy adoptions are mostly healthy.** Two stale Addy lenses (security, perf) and a
   handful of high-value, low-cost gaps (redaction in diagnosis evidence, grilling round format,
   destructive-path target validation, perf keep-or-revert + attempt ledger).
4. **The meta-gap is drift mechanics.** Every stale row traces to us hardcoding CLI mechanics in
   prose while upstream's explicit anti-drift design is `orca skills get <name>` — version-matched
   guides served by the binary itself. We adopted the content, not the anti-drift mechanism.

## 2. Per-source detail

### 2.1 stablyai/orca — ADOPTED-STALE (highest-value gap)

Runtime policies written pre-#9925 and never updated. Confirmed stale rows (anchors in audit):
- **Spawn path**: `spawn_worker.sh:283-311` folklore vs `worker-start` composing placement +
  readiness (settles on observed `turn_started`, not write-acceptance) + ownership. `dispatch
  --inject` is now explicitly the **unsupervised** lane — our workers are invisible to
  `worker-list` completion accounting.
- **Inbox**: "one message per `check`" (`dispatch-lifecycle.md:119-121`) is wrong since 07-27 —
  a consuming `check` returns a ≤50-message Delivery replayed until `--ack`.
- **Scoping**: our hand-rolled "coordinator handle + task ids" resume scope re-implements what
  `run-create`/`run-use`/`worker-list --run` give natively; `coordinator_runs` (which
  `orca-dag-semantics.md` analyzes) no longer exists.
- **Ask timeout**: `gate-classification.md:9` says re-ask under a new id; upstream says resume the
  SAME message id, never duplicate.
- **sandbox-policy citation**: `DEFAULT_TUI_AGENT_ARGS` no longer exists in
  `tui-agent-permissions.ts`; droid gained a yolo flag (`--auto high`) our spawn script denies.
- **Not adopted at all**: supervised lifecycle (`worker-show/stop/abandon/release/retain`,
  `projection.liveness/attention/nextAction`), legacy-contract takeover (covers "Orca updated
  mid-run"), `--retry-request` idempotency, nested-worker-depth enforcement (matters: a reviewer
  worker that spawns its own axis workers now fails with `nested_worker_depth_exceeded`).

### 2.2 garrytan/gstack — mostly current, two stale, one precision inversion

- `release.md` classifier + `land-and-deploy` + `canary` + anti-FP gate + User-Challenge: **current**.
- **ADOPTED-STALE:** (a) upstream mechanized the fresh-evidence rule into an IRON LAW gate
  (`gstack-evidence check` binds FRESH to the exact command string + wtree fingerprint,
  `ship/SKILL.md:909-939`); we have the prose rule only (`release.md:26-27`). (b) review-army lens
  list: upstream added **api-contract** and **simplification** lenses (v1.75).
- **NOT-ADOPTED:** the wtree content fingerprint (see headline 2); dispatched-subagent scope
  guards + reconcile-against-pre-dispatch-HEAD on deadline (v1.79); `/document-release` doc-sync
  as a first-class release step (we fix doc drift only reactively via clean-sweep);
  `gstack-egress-receipt` (worker network egress is currently unrecorded in our `rw`/`danger`
  lanes — slots directly into the evidence manifest's artifact set).

### 2.3 addyosmani/agent-skills — mostly current, two stale lenses

- **Security lens STALE**, missing three post-July additions: destructive-path target validation
  (allowlisted root post-symlink-resolution · depth floor · ownership evidence — `45fd4a0`),
  shared-store rate-limit red flag (`1458305`), Data Privacy & Compliance operating rules
  (`bb53a78`).
- **Perf lens STALE**: missing Step 4 "neutral is a revert, not a keep" + the strict decision
  table + the **attempt ledger** (a reverted idea is never re-tried next quarter) — our own
  evidence philosophy applied to perf, currently absent from `skills/speed-it/`.
- **Current/ahead:** a11y (we're on WCAG 2.2 AA, upstream still 2.1), data-migration, incremental
  implementation, doubt-driven verification (upstream untouched since May/June).
- **NOT-ADOPTED:** constraint-driven-development (whole skill — written, numbered, tool-enforced
  quality bar with a floor-guard that watches for bar-lowering diffs); runbook doctrine (every
  alert symptom-based, runbook-linked, test-fired once); Tier-3 behavioral evals with pressure
  cases (our `eval.py` is routing/structural only).

### 2.4 mattpocock/skills — healthiest adoption

- `code-review` two-axis, wayfinder structure, TDD seams, domain-modeling: **current**.
- **Gaps:** (1) `diagnosing-bugs` gained a **Redact** section (secrets as `<REDACTED>` before
  artifacts) — our diagnosis evidence is pasted command output bound into SHA-pinned manifests,
  the single most likely place a credential gets immortalized; (2) **grilling** was rewritten to
  round-by-round frontier batches with a recommended answer per question — exactly what our
  "spawned → auto-pick the recommendation" doctrine needs to be well-defined
  (`playbooks/decide-and-freeze.md` still serializes one-question-at-a-time); (3) map-it never
  adopted the **Prototype** and **Task** ticket types (both pre-fork upstream — a partial
  adoption, not drift); (4) `retro`'s environment-improvement categories for `compound-learn`.

## 3. Quick wins (not missions — direct edits, ranked)

1. **Redact rule** in `playbooks/diagnose.md` + reference from `skills/root-cause/` convergence
   proof. Two files; closes a secrets-in-evidence-manifests hole.
2. **Grilling rounds** in `playbooks/decide-and-freeze.md` (batch the frontier, recommended
   answer per question, non-blocking fact dispatch) — makes spawned auto-pick well-defined.
3. **Destructive-path target validation** in the `risk-review.md` security lens + a
   `sandbox-policy.md` Never-row cross-ref (fleet-scale lights-out risk).
4. **Perf keep-or-revert + attempt ledger** in `skills/speed-it/` pipeline + one line in the
   `risk-review.md` perf lens.
5. **`api-contract` + `simplification` lenses** in `risk-review.md`; one sentence naming the
   channel the session-kind signal may arrive on (`gate-classification.md`, injection guard).
6. **Ask-resume-same-id** fix (`gate-classification.md:9`); **nested-worker-depth** note
   (`dispatch-lifecycle.md` / `acceptance-review.md` — who dispatches the axes).
7. **Prototype + Task ticket types** in `map-it`; **retro categories** in `compound-learn.md`.
8. **Doc-sync unit** in `playbooks/release.md` (PROMOTION_READY→RELEASED) so drift stops
   accumulating into clean-sweeps.
9. **Dead citation + droid flag** in `sandbox-policy.md` / `spawn_worker.sh`.

## 4. Mission proposals (each passed through the mission-identity test)

Four candidates emerged from the audits; two more were proposed and rejected during analysis
(doc-sync mission = clean-sweep/doc-claims already; standing monitoring = no finite denominator).

### 4.1 `pin-it` — *the fleet's runtime contract matches the Orca binary it runs on* (RECOMMENDED FIRST)
- **Outcome:** after any Orca upgrade, the runtime doctrine is re-witnessed and re-pinned.
  Today's trigger is the anecdote: our field run *attempted* `worker-start` (the current
  supervised path), fell back to bare-shell tracked dispatch after three substrate failures, and
  its failure-recovery (`agent_prompt_stalled`, `--retry-of`, abandoned dispatches) has no
  coverage in the policy docs at all — policy teaches the pre-#9925 folklore throughout.
- **Unit of work:** one mechanics *claim* in `runtime/*.md` / `runtime/scripts/` / mission
  preambles (a command shape, receipt field, lifecycle rule).
- **State machine:** ENUMERATE (extract every claim + load version-matched guides via
  `orca skills get`) → RE-WITNESS (replay each claim against the live runtime, capture the
  receipt) → CLASSIFY (current / stale / superseded) → PATCH → PROVE → PINNED /
  PINNED-WITH-PARKED.
- **Convergence proof:** every surviving claim quotes a receipt from the installed binary at a
  recorded CLI version; every *removed* claim is demonstrated failing against the live binary
  (refutation receipts archived like run evidence). Denominator = the claim inventory.
- **Why not an existing mission:** clean-sweep's oracle is the repo suite (test-goes-red);
  modernize-it's unit is a dependency group with build/test oracles. pin-it's unit (a doctrine
  claim), oracle (receipts from an external live control plane), and archive of refutations are
  all distinct. **First run has its work already cut out: section 2.1 of this document.**

### 4.2 `floor-it` — *the repo has a written, numbered, tool-enforced quality bar*
- **Outcome:** "set the bar and make it enforceable" — a `CONSTRAINTS.md` with numbered
  thresholds, one tool per dimension, and a guard that watches for bar-lowering diffs.
- **Unit of work:** one constraint dimension (coverage · security scanning · perf budget ·
  a11y · architecture boundary).
- **State machine:** DETECT → FREEZE (interview w/ defaults; headless floor) → WIRE (tool per
  dimension) → PROVE-FIRES (inject a violation per dimension, gate must go RED) → ENFORCE in CI →
  GUARD (diff-watch for new suppressions / skipped tests / edited thresholds) → REFLECT.
- **Convergence proof:** demonstrated-RED negative control per frozen dimension at the merged SHA;
  the artifact is committed; CI blocks. This is the substrate our "unfakeable oracle" (lighting)
  and attest-it currently lack — the bar becomes machine-checkable instead of prose.
- **Why not existing:** prove-it owns test debt (one dimension); ship-it consumes the bar;
  attest-it proves *external* frameworks; harden-it is threat-model-scoped.

### 4.3 `reshape-it` — *shallowness-audited, behavior-preserving deepening of hot modules*
- **Outcome:** confirmed high-churn modules sit behind smaller, testable interfaces with behavior
  demonstrably unchanged (Matt's `improve-codebase-architecture` + `codebase-design` vocabulary,
  entirely unadopted).
- **Unit of work:** one module-deepening (one interface shrink at one seam).
- **State machine:** SCAN (churn-weighted shallowness inventory) → CONFIRM-SURFACE →
  CHARACTERIZE (mutation-audited net at existing seams BEFORE restructure) → DEEPEN → REVIEW →
  LAND → RE-SCAN. Terminal: RESHAPED / RESHAPED-WITH-PARKED (API-break decisions gated).
- **Convergence proof:** before/after interface-surface measurement + characterization net green
  at both SHAs + build-blind review + the deletion test. Named for the outcome, not the
  technique ("deepen-it" would be vendor-vocabulary).
- **Why not existing:** modernize-it = dependencies; clean-sweep = enumerable findings;
  prove-it = test gaps. Architectural erosion in lived-in code has no owner today.

### 4.4 `field-test-it` — *verified on a real device* (CONDITIONAL)
- **Outcome:** on-device repro → fix → re-verify on hardware, with an on-device negative control
  (revert reintroduces the observed failure). The device oracle is unfakeable in principle.
- Passes the identity test cleanly (distinct unit: device-observed defect; distinct state machine:
  pair/baseline/reverify on hardware). **But:** gstack sustains five iOS skills + three companion
  CLIs for this — it is a large surface, and orca-fleet's users may not ship mobile apps.
  Propose building only if device targets are in scope. (Orca ships `orca-emulator` /
  `orca-emulator-android` skills today, which lowers the substrate cost considerably.)

### Recommended sequencing
1. **Quick wins** (section 3) — hours, close real holes (redaction first).
2. **`pin-it`** — and run it immediately against section 2.1; it re-pins the runtime layer and
   institutionalizes the anti-drift mechanism (`orca skills get`) so this audit never has to be
   repeated manually. Its first run (against this repo) would produce a self-run report — the
   honest first step past doctrine-only.
3. **`floor-it`** — makes every other mission's gates machine-checkable.
4. **`reshape-it`** when a lived-in codebase needs it. **`field-test-it`** only with device demand.

## 5. What we deliberately did NOT adopt (and why)

- gstack `gstack-verify-gate` Stop hook — name collision only; ours is fail-closed with an
  independent `verify.py` re-derivation, strictly stronger than upstream's fail-open trust store.
- gstack iOS/browser cluster, `benchmark*`, gbrain memory — outside doctrine scope (today).
- Addy eval Tier-3 as a *mission* — it's catalog tooling (`scripts/eval.py`), not a user outcome.
- Matt `triage` state machine, `handoff`, `implement-spec` — subsumed by clean-sweep's
  skeptic-triage, liveness-resume CONTEXT HANDOFF, and Orca dispatch respectively.
- Remote/federated worker placement (`--on`) — no demonstrated demand; sandbox lanes pair via
  `orca serve` today.

## 6. Caveats

- Snapshots: upstream HEADs as of 2026-09-09; the Addy security skill alone moved three times in
  the last ten days. Treat stale rows as a snapshot, not a steady state — which is precisely the
  argument for `pin-it` + the `orca skills get` load step.
- The stablyai audit covered the orchestration surface orca-fleet consumes, not the whole Orca
  app (editor, browser, automations beyond `mission-scheduling`'s flags).
