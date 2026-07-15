# Addy Osmani orchestration articles × orca-fleet — gap analysis & adoption map

**Status:** MAPPED — D1–D4 implemented on `cursor/addy-orchestration-gap-analysis-62a1` (D5–D6 parked; D7–D8 rejected / deferred)  
**Date:** 2026-07-15  
**Mission shape:** map-it → ship-it (adoption slices F1–S3)  
**Destination:** Adopt Addy orchestration concepts that fit orca-fleet; reject peer-messaging and LLM outer orchestrators.

## Sources researched

| # | Article | Core thesis |
|---|---------|-------------|
| 1 | [The future of agentic coding](https://addyosmani.com/blog/future-agentic-coding/) | Conductor (1 sync agent) → Orchestrator (async fleet); specialist AI team; verification stays human |
| 2 | [Lesson 19: orchestrators](https://addyosmani.com/agents/18-orchestrators/) | Control-flow patterns: Sequential / Parallel / Loop / Routing / Hierarchical / Group Chat; hybrid deterministic+LLM |
| 3 | [The Orchestration Tax](https://addyosmani.com/blog/orchestration-tax/) | Human attention is the serial bottleneck (Amdahl/GIL); scale fleet to review rate, not UI limits |
| 4 | [The Code Agent Orchestra](https://addyosmani.com/blog/code-agent-orchestra/) | Subagents → Agent Teams → tiered tools; quality gates; Ralph Loop; compound learning; factory line |
| 5 | [The Factory Model](https://addyosmani.com/blog/factory-model/) | Build the factory that builds software; spec is leverage; TDD mandatory; verification > generation |

---

## Verdict (one line)

orca-fleet already implements the **orchestrator / factory / verification** core of these articles — often more rigorously than the articles prescribe (SHA-bound evidence, independent verifier, reviewed-SHA freshness). The remaining gaps are mostly **attention architecture** (WIP vs review rate), **compound learning** (structured retro into target-repo context), and a few **reliability knobs** (reflection-before-retry, optional model routing) — not a missing multi-agent substrate.

---

## Coverage matrix

Legend: **✓** fully embodied · **◐** partial / weaker · **✗** absent · **⊘** deliberate non-goal

### A. Topology & roles (articles 1, 4, 5)

| Concept | Articles | Fleet status | Where |
|---------|----------|--------------|-------|
| Conductor → Orchestrator shift | 1, 4 | ✓ | Coordinator + disposable workers (`docs/concepts.md`) |
| Async agents → PRs / git trail | 1, 4 | ✓ | PR-per-unit, worktrees, merge train |
| Specialist roles (plan / build / test / review / deploy) | 1, 4 | ✓ | Missions + playbooks; builder / build-blind reviewer / conductor / risk lenses |
| Docs agent as peer specialist | 1 | ◐ | Noticed-but-not-touched → backlog; no dedicated docs worker |
| Hierarchical coordinator-worker | 2, 4 | ✓ | Core topology; unit subtree ≤3–4 deep |
| Nested feature-lead subagents | 4 | ◐ | Coordinator → unit worktree → review/fix/integrator; no recursive "feature lead" layer beyond that |
| Peer-to-peer teammate messaging | 4 | ⊘ | Workers message the coordinator only — intentional for verification independence |
| Shared self-claiming task board | 4 (Agent Teams) | ⊘ | Orca DAG assigns tasks; self-claim would bypass ledger/evidence contracts |
| Group-chat / roundtable | 2 | ⊘ | Avoided (token-expensive); parallel isolated axes instead (`acceptance-review`) |
| Substrate swap (Conductor / Claude Squad / Jules) | 1, 4 | ⊘ | Orca is the substrate; recipes come from packs |

### B. Orchestration patterns (article 2)

| Pattern | Fleet status | Where |
|---------|--------------|-------|
| Deterministic outer workflow | ✓ | Mission pipelines are fixed state machines |
| LLM flexibility inside steps | ✓ | Workers reason freely within playbooks |
| Hybrid (recommended) | ✓ | Exactly the production choice article 2 endorses |
| Sequential | ✓ | Mission phases; mission-chaining |
| Parallel fan-out/gather | ✓ | Foundation serializes; slices parallelize |
| Loop / generator-critic | ✓ | Review rounds; harden-it re-attack; clean-sweep re-enumerate; prove-it re-map |
| Routing / specialist dispatch | ✓ | Intent→mission map; risk-review lenses; PoC routing |
| Hierarchical | ✓ | Coordinator-worker |
| Validate between steps | ✓ | Evidence verification before advance |
| Iteration limits | ✓ | 3 review rounds; 3 doctor attempts; circuit_broken |
| Start simple / anti overkill | ✓ | Mission-identity test; instruction budgets; proof honesty |
| Multi-model cost routing | ◐ | Cross-vendor reviewer preferred; spawn defaults `xhigh`; no `MODEL_ROUTING` table |
| Observability (latency/tokens/success per step) | ◐ | Ledger + provenance + worktree comments; no token/cost telemetry policy |
| Context compaction between agents | ✓ | Fresh context per worker; ledger as durable memory |

### C. Factory / verification (articles 4, 5)

| Concept | Fleet status | Where |
|---------|--------------|-------|
| Spec is the leverage | ✓ | `decide-and-freeze`; map-it → frozen map |
| Plan → Spawn → Monitor → Verify → Integrate | ✓ | ship-it pipeline + liveness + merge train |
| Retro / compound learning | ◐ | ship-it REFLECT writes readiness/backlog; **no** systematic target-repo `AGENTS.md` update |
| Red/green TDD + tautology guard | ✓ | `build-change` |
| Negative control / mutation proof | ✓ | `evidence-manifest` (stronger than article "run tests") |
| Independent verification ≠ author claim | ✓ | Fresh verifier session; `reviewer_mode` recorded |
| Plan approval before risky code | ◐ | Mission freeze + irreversibility stop-list; **no** per-unit plan→approve→build gate for risky slices |
| Lifecycle hooks (idle/complete must pass tests) | ◐ | Manifest requires commands+exit; not automated TeammateIdle-style hooks |
| Ralph Loop (stateless overnight drain) | ◐ | Closest: `mission-scheduling` + `clean-sweep`; not pick→implement→validate→commit→reset |
| Beads / queryable institutional memory | ◐ | Ledger + Orca provenance; not cross-run SQL decision beads |
| Human-curated AGENTS.md only | ✓ (this repo) | ETH Zurich finding cited in art. 4 — agents must not auto-write project rules |
| WIP: one file / one owner | ✓ | Hot-file merge chains; PR sizing seam |
| Kill criteria (stuck 3+ same error) | ◐ | Doctor attempts + circuit break; **no** forced reflection-before-retry prompt |

### D. Orchestration tax / attention (article 3)

| Concept | Fleet status | Where |
|---------|--------------|-------|
| Human as serial bottleneck | ✓ (governance) | One-way gates always human; never fake approval |
| Scale fleet to review rate (backpressure) | ◐ | Merge train serializes merges; **no** explicit max-parallel-by-review-capacity policy |
| Sort piles: isolated vs judgment-heavy | ◐ | Embodied as different missions; not documented as attention architecture |
| Batch human reviews | ✗ | No batching guidance for promotion/one-way gates |
| Spend lock only on judgment; machine verifies 80% | ✓ | Mechanical/taste auto; evidence + negative control for boring proof |
| Busy ≠ productive | ✓ (culturally) | Proof status honesty; degraded terminals stop chains |
| Protect serial thinking time | ✗ | Process guidance for humans, not a fleet policy |

---

## What we already do *better* than the articles

These are load-bearing and must not be diluted by adopting softer article patterns:

1. **SHA-bound evidence + independent verifier** — articles say "run tests / review PRs"; the fleet re-derives facts from git ancestry, clean-env runs, negative controls, and `reviewed_sha == head_sha`.
2. **Outcome missions, not ingredient skills** — avoids the co-mounted router wars the articles' tool zoo quietly invites.
3. **Deterministic mission state machines** — article 2's hybrid recommendation; we refuse LLM outer routing for the whole SDLC.
4. **Wrong-base / reviewed-SHA / anti-inflation** — operational specifics the articles gesture at as "quality gates" but do not specify.
5. **Proof honesty + instruction budgets** — doctrine cannot outrun evidence (predecessor failure mode).

---

## Decision tickets (sharp questions for human freeze)

Fog-of-war rule: only tickets that can be phrased sharply now. Answer these to authorize a ship-it adoption DAG.

### D1 — WIP / orchestration-tax policy *(taste → possibly one-way if it changes autonomy defaults)*

**Question:** Should we add a runtime policy that caps concurrent builder/reviewer dispatches to an explicit **verification-capacity WIP limit** (recommended default: low single-digit builders + matching reviewer ratio), rather than only serializing at the merge train?

**Recommendation:** Yes — adopt as `runtime` policy (attention backpressure). Merge serialization is consumer-side; WIP is producer-side. Article 3's strongest actionable insight.

**If yes, layer:** `runtime/` (new short policy or section in `dispatch-lifecycle` / `mission-scheduling`) + one paragraph in `docs/concepts.md`. Not a new mission.

### D2 — Compound-learning / retro playbook *(taste)*

**Question:** After a mission REFLECT, should workers propose **human-approved** appends to the *target repo's* `AGENTS.md` / gotchas file (lead must approve every line; never auto-merge LLM prose)?

**Recommendation:** Yes — new playbook `compound-learn` composed by ship-it / clean-sweep / harden-it REFLECT. Hard rule: human-curated only (article 4 / ETH Zurich). Keep proposals in `docs/reports/<run>/REFLECTION.md`; merge to AGENTS.md is a taste/one-way gate depending on repo norms.

**If yes, layer:** `playbooks/compound-learn.md` + compose clauses. Not a mission (no new convergence proof).

### D3 — Reflection-before-retry on stuck workers *(mechanical)*

**Question:** On WATCH respawn / doctor retry, require a structured reflection line in the evidence (what failed, what changes, am I repeating?) before the next attempt, and kill+reassign after N identical-error retries?

**Recommendation:** Yes — fold into `liveness-resume.md` (fits iteration-limit best practice; low surface area).

### D4 — Per-unit plan gate for risky / irreversible slices *(one-way-adjacent)*

**Question:** For slices that touch the irreversibility stop-list (auth, destructive migration, payments, secrets), require a written plan artifact + coordinator/human approve *before* `build-change` may start coding — not only escalate mid-build?

**Recommendation:** Yes — strengthen `build-change` entry + `gate-classification` Lane B/0. Aligns with article 4 plan-approval quality gate.

### D5 — Multi-model routing table *(taste)*

**Question:** Publish an optional `MODEL_ROUTING` convention (plan/decompose → cheaper; implement → strong; review → cross-vendor; classify → fast) referenced from sandbox/spawn docs?

**Recommendation:** Optional / later. Cross-vendor review already preferred; spawn defaults `xhigh`. Cost routing helps at scale but is not a correctness gap. Park unless D1–D4 land first.

### D6 — Ralph-style overnight drain *(taste; mission-identity check)*

**Question:** Is a stateless pick→implement→validate→commit→reset loop a **new mission**, an enhancement of `mission-scheduling`+`clean-sweep`, or out of scope?

**Recommendation:** Enhancement of scheduling + clean-sweep / prove-it — **not** a new mission (same unit/state machine/proof as backlog drain). Only if overnight unattended drain is a real operator need. Otherwise ⊘.

### D7 — Peer messaging / Agent Teams primitives *(one-way architectural)*

**Question:** Should workers exchange contracts peer-to-peer (bypassing the coordinator)?

**Recommendation:** **No.** Coordinator mediation is how evidence stays independent and the ledger stays authoritative. Peer messaging optimizes the wrong bottleneck for this fleet (verification, not coordination chatter).

### D8 — Beads / cross-run queryable memory *(taste)*

**Question:** Invest in structured cross-run decision beads beyond ledger + provenance?

**Recommendation:** Not yet. Resume + anti-inflation already re-read prior run reports. Revisit only if operators show they cannot find past decisions.

### Open "not yet specified"

- Exact default WIP numbers per mission class (needs operator measurement of review rate).
- Whether compound-learn writes to `AGENTS.md` vs `docs/GOTCHAS.md` vs repo-local convention.
- Whether Orca runtime will grow native lifecycle hooks (fleet can only approximate today).

---

## Adoption plan (prepared for ship-it — not dispatched)

Authorize only after D1–D4 (and optionally D5–D6) are human-resolved. Sequence assumes D1–D4 = yes, D5–D6 = later/no, D7–D8 = no.

```
FOUNDATION (serial)
  F1  Add orchestration-tax / WIP backpressure section to runtime
      (dispatch-lifecycle or new attention-budget.md ≤160 lines)
  F2  Docs: concepts.md paragraph + getting-started mention of review-rate scaling

PARALLEL behind F1
  S1  liveness-resume: reflection-before-retry + identical-error kill criteria
  S2  build-change + gate-classification: pre-build plan gate for irreversibility list
  S3  playbooks/compound-learn.md + compose from ship-it / clean-sweep / harden-it REFLECT
      + docs/missions notes; human-approve-only rule

VERIFY
  V1  validate.py + contract tests green; instruction budgets hold
  V2  No new mission; no peer-messaging; proof: fields unchanged unless a self-run lands later

PARKED (explicit)
  P1  MODEL_ROUTING (D5)
  P2  Ralph overnight enhancement (D6)
  P3  Beads (D8)
```

**Handoff checklist (map-it → ship-it):**

| Item | Value |
|------|-------|
| Destination | Adopt D1–D4 orchestration-tax + reliability + compound-learn; reject D7; park D5/D6/D8 |
| Frozen plan path | `docs/research/2026-07-15-addy-orchestration-gap-analysis.md` (this file) |
| Prepared DAG | Logical slices F1–F2, S1–S3, V1–V2 above — **not** materialized in Orca until human freeze of D1–D4 |
| Blocked tickets | D1, D2, D3, D4 (need human answers) |
| Terminal | **MAPPED** — D1–D4 shipped in the same PR as this research; D5/D6 parked; D7 rejected; D8 deferred |

---

## Concept → mission cheat sheet (for operators)

| If an article makes you want… | Use / extend |
|-------------------------------|--------------|
| "Run a fleet that ships a feature" | `ship-it` (+ `map-it` if foggy) |
| "Drain the backlog overnight" | `mission-scheduling` + `clean-sweep` (Ralph = optional later enhancement) |
| "Specialist security / perf / tests" | `harden-it` / `speed-it` / `prove-it` — not co-mounted routers |
| "Review many PRs" | `review-it` (read-only; scales to review rate) |
| "Plan then build" | `map-it` → freeze → `ship-it` adopts DAG |
| "Chain harden then prove then ship" | `mission-chaining` |
| "Trust but verify" | Already mandatory: `evidence-manifest` |

---

## Anti-adoption list (do not "improve" the fleet this way)

1. Co-mount matt + addy + gstack routers in one worker TASK.
2. Replace deterministic mission pipelines with an LLM outer orchestrator.
3. Add peer-to-peer worker chat as a substitute for the ledger.
4. Let agents auto-write `AGENTS.md` without human approval.
5. Grade done on traces / dashboards of "busy agents."
6. Spawn to UI max instead of verification capacity.
7. Name a new mission `orchestrate-it` / `factory-it` / `ralph-it` — those are ingredients or modes, not outcomes.

---

## Evidence of research

- Full text of all five URLs fetched and read 2026-07-15.
- Cross-walked against: `ARCHITECTURE.md`, all 10 `skills/*/SKILL.md`, all 10 playbooks, all runtime policies (esp. `evidence-manifest`, `dispatch-lifecycle`, `liveness-resume`, `merge-serialization`, `gate-classification`, `mission-chaining`, `mission-scheduling`), `docs/concepts.md`, `README.md`, `TODOS.md`.
- No production code changed in this map-it pass.
