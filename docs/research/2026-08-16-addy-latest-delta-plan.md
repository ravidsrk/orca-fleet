# Addy latest × orca-fleet — 2026-08-16 delta, implementations, suggestions

**Status:** MAPPED (research complete; implementation tickets classified; no production code in this pass)  
**Date:** 2026-08-16  
**Base:** `main` @ `9c784b6` (PR #67 clean-sweep learnings)  
**Predecessor:** [2026-07-15 gap analysis](2026-07-15-addy-orchestration-gap-analysis.md) (D1–D4 shipped in #21)  
**Destination:** A frozen adopt / suggest / reject map that ship-it can consume without re-researching the July–August delta.

## What this pass did

1. Pulled latest `origin/main` (already at HEAD; no divergence).
2. Re-read the five original articles plus the **newer** Addy posts that landed after the July 15 snapshot.
3. Re-scored the fleet against current runtime, playbooks, missions, and the 2026-07-17 tracker self-run.

## What landed on the fleet since 2026-07-15

The July 15 plan is no longer the live gap. D1–D4 shipped, then the catalog hardened them in the field.

| Wave | What | Evidence |
|------|------|----------|
| #21 | D1 attention-budget, D2 compound-learn, D3 reflection-before-retry, D4 irreversibility plan gate | merged |
| #20/#22 | `oss-contribute` + `upstream-contribution` (new outcome; external-run on chimely) | 0.4.0 |
| #23/#54 | `WIP:` is a **required** ledger-header field | contract tests |
| #51/#62 | WIP-curve protocol (throughput, verify latency, rework, freshness) — **ASSERTED**, first measured row still owed | parked #51 |
| #50 | Criterion↔test binding audit on the verifier | `evidence-manifest` §2 |
| #30/#63 | Per-unit flag `BUILT` → `BUILD_DONE` (wave-state still `BUILT`) | ledger-contract |
| #64 | spawn_worker effort keyset + collision-safe scratch | spawn hardening |
| 2026-07-16 | oss-contribute external-run | `docs/runs/` |
| 2026-07-17 | clean-sweep tracker self-run: DRY-WITH-PARKED, WIP 3/1, identical-error-kill used, dual-writer lesson | `docs/runs/` |
| #67 | Two learnings encoded: wave-plan must cover every frozen id; broken-test routing seam | clean-sweep SKILL |

**Field verdict on D1–D4:** they worked. The 07-17 sweep ran the attention budget, hit identical-error-kill on `.claude/settings.json` hangs, and the re-enumeration caught two dropped findings. Remaining debt from that run is operational (WIP-curve first data point), not missing policy text.

---

## Newer articles (not in the July 15 set)

| Date | Article | Thesis that could change the fleet |
|------|---------|------------------------------------|
| 2026-07-20 | [Software Factories, Light and Dark](https://addyosmani.com/blog/software-factories/) | Loop → harness → factory. A loop may run **dark** only if the check is cheap, frequent, and unfakeable. Lights stay on for expensive judgment. Deterministic **graph** around LLM-inside-the-node. |
| 2026-07-15 | [Own the Outer Loop](https://addyosmani.com/blog/own-the-outer-loop/) | Agents run the inner loop; humans own Quality → Verdict → Answerability. Back-pressure is how you grant autonomy. Accountability contract on every accepted change. |
| 2026-07-02 | [Agentic Autonomy Levels](https://addyosmani.com/blog/agentic-autonomy-levels/) | Two axes: agency × orchestration. Levels 0–5. Autonomy follows verification, not status. Per-run contract: goal, scope, non-goals, tools, stop, evidence, escalation, budget. Four anti-patterns. |
| 2026-06-16 | [Agentic Code Review](https://addyosmani.com/blog/agentic-code-review/) | Review is the bottleneck (4× code / ~12% value). Capture discarded agent *intent* on the PR. Human moves **on** the loop (sample, audit, high-blast gates), not every line. |
| 2026-06-07 | [Loop Engineering](https://addyosmani.com/blog/loop-engineering/) | Design the system that prompts agents. Five primitives + disk memory. Maker ≠ checker, including the *stop condition*. |
| 2026-06-05 | [The Intent Debt](https://addyosmani.com/blog/intent-debt/) | Technical / cognitive / intent. Agents cannot pay intent debt; they fabricate why. Externalize load-bearing rationale. |
| 2026-05-24 | Orchestration Tax *(already adopted)* | Human attention is the GIL. |
| 2026-03-26 / 02-25 | Orchestra / Factory Model *(already adopted)* | Verification > generation. |

Related but not re-opened as tickets: Cognitive Surrender, Don't Outsource the Learning, Comprehension Debt, Long-running Agents, Agent Harness Engineering, Stop Using /init for AGENTS.md, Your parallel Agent limit. They reinforce existing doctrine (human-curated AGENTS.md, ledger-as-memory, don't grade busy).

---

## Re-score of the July 15 matrix

Legend: **✓** embodied · **◐** partial · **✗** absent · **⊘** non-goal

| July ticket | July status | August 16 status |
|-------------|-------------|------------------|
| D1 WIP / review-rate | planned | **✓** policy + required header + pane-count + WIP-curve (still ASSERTED) |
| D2 compound-learn | planned | **◐** playbook exists; composed only by ship-it / clean-sweep / harden-it; no REFLECTION.md from the 07-17 run on disk |
| D3 reflection-before-retry | planned | **✓** policy + used in the 07-17 hang |
| D4 irreversibility plan gate | planned | **✓** build-change entry + gate-classification |
| D5 MODEL_ROUTING | parked | still parked (spawn still defaults `xhigh`) |
| D6 Ralph overnight | parked | still not a new mission; `mission-scheduling` + clean-sweep is the loop. Product `/goal`/`/loop` are substrate, not catalog. |
| D7 peer messaging | reject | **still reject** (maker/checker independence) |
| D8 beads | deferred | still deferred; **intent packet on the PR** is the cheaper cousin (E2) |

July rows that flipped from ◐/✗ without a named ticket:

| Concept | Now |
|---------|-----|
| Scale to review rate | ✓ attention-budget + merge train |
| Sort isolated vs judgment | ✓ attention-budget |
| Batch one-way gates | ✓ "Spend the lock only on judgment" |
| Kill + reflection | ✓ |
| Plan-before-risky-code | ✓ |
| Observability of WIP | ◐ protocol exists; **zero measured rows** |

---

## New coverage (July–August articles)

| Concept | Source | Fleet now | Gap |
|---------|--------|-----------|-----|
| Inner loop vs outer loop | Outer Loop / Light-Dark | ✓ coordinator never codes; one-way gates; evidence crosses the boundary | Name the split in concepts (docs) |
| Quality → Verdict → Answerability | Outer Loop | ✓ evidence + promotion PR + named terminals | No named **accountable human** on the promotion artifact |
| Light vs dark loops | Light-Dark | ◐ irreversible = lit (plan gate); scheduled review-it/clean-sweep ≈ dark-capable | No explicit per-unit light/dark bit; operators cannot audit which loops ran unread |
| Graph around the loop | Light-Dark | ✓ mission state machines are the graph; LLM only inside the node | Already the production choice; do not add an LLM outer router |
| Autonomy level 0–5 | Autonomy Levels | ◐ fleet is L4/L5-shaped; no per-unit level or budget | Task spec lacks goal/stop/budget/escalation block |
| Autonomy anti-patterns | Autonomy Levels | ✓ (status, permission laundering, summary substitution, fleet cosplay) already refused in doctrine | Could name them in anti-patterns |
| Intent captured on the PR | Code Review / Intent Debt | ◐ DECISIONS.md + claim field; claim is explicitly **not** the oracle | No required rationale / ruled-out / load-bearing-why on the manifest |
| Human *on* the loop (sample) | Code Review | ◐ 10% negative-control sample; every mutation unit still gets a build-blind reviewer | Do **not** drop per-unit review. Sampling is for *human* reading of already-reviewed diffs, if volume forces it |
| Maker ≠ checker on *done* | Loop Engineering | ✓ independent verifier; `/goal`-style stop is the coordinator+verifier, not the builder | Document the analogue; no new worker |
| Compound-learn coverage | Intent Debt / Orchestra | ◐ three missions only | Remaining mutating missions omit it |
| WIP-curve first measured row | attention-budget / #51 | ✗ owed | Next self-run must emit the row |

The fleet is already a **lit factory** with a deterministic outer graph. The remaining work is making light/dark, intent, and autonomy **legible per unit**, and closing the measurement loop on WIP.

---

## Decision tickets (sharp now)

### E1 — Light / dark classification *(taste)*

**Question:** Should every dispatched unit declare `lighting: lit | dark-eligible` in the ledger/manifest, with dark-eligible only when the stop condition is a cheap, frequent, unfakeable oracle (types/tests/binding audit) **and** blast radius is Lane A reversible?

**Recommendation:** **Adopt.** Maps Light-Dark onto gates we already have. Default **lit**. Dark-eligible is opt-in per unit class (e.g. lint-only, characterization-only), never for auth/payments/secrets (already the plan gate). Scheduled `review-it` stays report-only (no ship), so it is not "dark merge."

**Layer:** `gate-classification.md` (one short section) + one field on the ledger row / manifest. Not a mission.

### E2 — Intent packet on the unit *(mechanical)*

**Question:** Require the worker to attach a short intent packet (goal in one sentence · what was ruled out · load-bearing why) on the evidence manifest / PR body, distinct from `claim` (still non-oracle)?

**Recommendation:** **Adopt.** Agentic Code Review + Intent Debt. Cheap; kills "first human to see this code has to reconstruct why." Verifier checks the packet is present and non-empty, not that it is wise.

**Layer:** `evidence-manifest.md` + `build-change.md` Evidence section.

### E3 — Autonomy contract on the TASK *(taste)*

**Question:** Add a compact autonomy block to every mutating TASK spec: goal, scope, non-goals, stop condition, evidence, escalation, budget (doctor attempts already; optional token/time)?

**Recommendation:** **Adopt a short template**, not a routing table. Most fields already exist in slice specs; the hole is naming stop + escalation + budget in one place. Do **not** publish MODEL_ROUTING (D5 stays parked).

**Layer:** `dispatch-lifecycle.md` (TASK preamble) or a 10-line block in `decompose-dag` / `remediate-finding`.

### E4 — WIP-curve first measured row *(mechanical / operational)*

**Question:** Is the next mutating self-run required to emit the WIP-curve table row (setting, throughput, verify latency, rework, freshness)?

**Recommendation:** **Yes — operational, not a code change.** #51 is already `CODE_CLOSED` + `VERIFY_AT_SCALE`. The next `clean-sweep` or `ship-it` self-run closes it. Add a one-line reminder to `docs/runs/README.md`.

### E5 — compound-learn on the rest of the mutating catalog *(mechanical)*

**Question:** Compose `compound-learn` (and ride `attention-budget` where missing) from `oss-contribute`, `prove-it`, `speed-it`, `modernize-it`, `deflake-it`?

**Recommendation:** **Adopt.** Same playbook, same human-approve rule. `oss-contribute` REFLECT writes proposals for the *upstream* context file only if maintainers welcome it; otherwise fleet-side backlog only.

### E6 — Named accountable human on promotion *(taste)*

**Question:** Require the promotion PR / run report to name the human who owns the Verdict (Outer Loop answerability)?

**Recommendation:** **Suggest, do not block.** Interactive runs already have a human at gate #2. Unattended runs park one-way gates. A `accountable:` line on the promotion PR is enough if adopted.

### E7 — Sample human reading of already-reviewed diffs *(one-way)*

**Question:** Allow a human to sample (not read every) build-blind-reviewed units before BASE merge?

**Recommendation:** **Reject for now.** Volume has not broken this fleet's review gate; Faros' "unread merge" is the failure mode we exist to prevent. Keep per-unit build-blind review. Revisit only with WIP-curve data showing review latency is the constraint.

### Still parked / rejected

| ID | Disposition |
|----|-------------|
| D5 MODEL_ROUTING | Park. Cost, not correctness. |
| D6 Ralph / `/goal` overnight | Park. `mission-scheduling` + clean-sweep is the loop. |
| D7 Peer messaging | Reject. |
| D8 Beads | Defer. E2 is the incremental step. |
| Token/cost telemetry | Park until an operator asks. |
| New mission (`factory-it`, `loop-it`, `ralph-it`) | Reject — mission-identity test fails. |
| LLM outer orchestrator | Reject — Light-Dark's graph point is already our design. |
| Dark factory as default | Reject. |

### Open "not yet specified"

- Exact dark-eligible unit classes beyond "Lane A + unfakeable oracle."
- Whether E2's intent packet is a new JSON field or a required PR section.
- Whether E3's budget includes tokens or only doctor-attempts + wall-clock.
- Which mutating mission is the next self-run (E4's vehicle).

---

## Implementation plan (prepared for ship-it — not dispatched)

Authorize E1–E5. E6 optional. E7 rejected. Sequence:

```
FOUNDATION (serial)
  F1  evidence-manifest: required intent packet (E2)
      + verifier check "present and non-empty"
  F2  gate-classification: lighting lit | dark-eligible (E1)
      + ledger/manifest field; default lit

PARALLEL behind F1
  S1  TASK autonomy contract block (E3) in dispatch-lifecycle
      or decompose-dag / remediate-finding
  S2  Compose `compound-learn` + ride `attention-budget`
      from remaining mutating missions (E5)
  S3  docs/runs/README.md: next self-run MUST include WIP-curve row (E4)

OPTIONAL
  O1  promotion PR `accountable: <human>` line (E6)

VERIFY
  V1  validate.py + unittest green; instruction budgets hold
  V2  No new mission; no peer-messaging; no unread-merge sampling

PARKED
  P1  D5 MODEL_ROUTING
  P2  D6 Ralph / product /goal
  P3  D8 beads
  P4  token telemetry
```

**Handoff checklist**

| Item | Value |
|------|-------|
| Destination | Close the July–August Addy delta: lighting + intent packet + autonomy contract + compound-learn coverage + WIP-curve reminder |
| Frozen plan | this file |
| Prepared DAG | F1–F2, S1–S3, V1–V2 — materialize in Orca only after human freeze of E1–E3 (E4–E5 are mechanical) |
| Blocked | E1, E3 (taste); E2/E4/E5 may proceed as mechanical if the human so classifies |
| Terminal | **MAPPED-WITH-BLOCKED** until E1 and E3 are answered; E2/E4/E5 are ready to ship |

---

## Suggestions (do not implement unless asked)

These are operator / product posture, not catalog work:

1. **Stay a lit factory.** The 07-17 run already showed what "management by exception" looks like when env hangs force coordinator authorship — document the degradation, don't hide it. Do not chase Level 5 as a badge (Autonomy Levels anti-pattern #1).
2. **Treat `#51` as the next proof, not more policy.** The WIP-curve without a row is doctrine again. One measured wave is worth another policy paragraph.
3. **Use compound-learn on the next close.** The 07-17 run did not leave a `REFLECTION.md` in-repo. The playbook is idle until a run writes the proposal.
4. **Do not add a docs-specialist worker.** Noticed-but-not-touched → backlog is enough; a docs agent is an ingredient, not an outcome.
5. **Validator P2s in TODOS.md** (unreadable SKILL.md, shared reference grammar) are still open and unrelated to Addy — fine as a separate clean-sweep slice.
6. **Read Dex Horthy / HumanLayer "Harness Engineering is not Enough"** if a later pass wants the factory-failure case studies Light-Dark cites; not required to freeze E1–E5.

---

## Anti-adoption (unchanged, plus one)

1. Co-mount two routers in one worker.
2. LLM outer orchestrator / throw away the mission graph.
3. Peer-to-peer worker chat as a ledger substitute.
4. Auto-write `AGENTS.md`.
5. Grade done on traces or "agents busy."
6. Spawn to UI max.
7. Name a mission for a technique.
8. **New:** drop per-unit review because an article said "human on the loop." That article's own Faros number is unread merge. Our gate stays.

---

## Evidence of research

- `git fetch` + `main` @ `9c784b6`; commit list since 2026-07-15; files added; CHANGELOG 0.4.0 + Unreleased.
- Re-read: attention-budget (WIP-curve), liveness-resume, evidence-manifest §2 binding audit, build-change plan gate, compound-learn, clean-sweep SKILL (wave-plan guard), oss-contribute SKILL, 2026-07-17 run report, concepts, ARCHITECTURE.
- Fetched and read: original five URLs plus Software Factories Light and Dark, Own the Outer Loop, Agentic Autonomy Levels, Agentic Code Review, Loop Engineering, The Intent Debt.
- No production code in this map-it pass.
