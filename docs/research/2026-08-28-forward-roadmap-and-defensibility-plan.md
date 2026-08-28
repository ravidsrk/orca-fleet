# Forward roadmap & defensibility plan — orca-fleet — 2026-08-28

> **Dated snapshot (2026-08-28).** Round-2 forward-looking research: platform trajectory, the
> reproducible-proof path, threat durability, and demand/catalog/GTM — turned into a prioritized
> roadmap. A point-in-time plan, not a live coverage matrix; see [ARCHITECTURE.md](../../ARCHITECTURE.md)
> for current catalog state. Builds on the same-day competitive scan
> ([2026-08-28 differentiation snapshot](2026-08-28-competitive-landscape-differentiation.md)).
> Forward claims are tagged SHIPPED / ANNOUNCED / SPECULATED with a horizon (now / <6mo / 6–18mo);
> unverifiable figures are flagged, not made load-bearing.

**Status:** MAPPED — 4 forward clusters synthesized into a prioritized action set filed as GitHub issues
**Date:** 2026-08-28
**Base:** `main` @ `32050a0`
**Method:** 4 parallel research agents (platform trajectory · proof path · threat trajectory · demand/catalog/GTM), primary sources, plus a primary-source verification pass on the #1 threat (claude-flow → Ruflo).
**Destination:** A frozen roadmap the catalog can execute against without re-researching the Aug-2026 forward picture. Each action below is filed as an issue (labels `research` + `enhancement`/`documentation`).

## Executive summary — the plan in five sentences

1. The moat is the **verification axis (B)** — specifically its two near-zero-prior-art primitives, a **mandatory negative control** (revert/mutate → the proof goes red) and an **independent-second-session re-derivation from a frozen contract** — bundled with the **ops-hardening suite (D)**.
2. Generic "verification-first / independent reviewer / evidence ledger" framing is **commoditizing right now**; the two specific primitives remain **ownable for ~6–18 months and closing**.
3. The single highest-leverage move is to **turn the moat into a public, third-party-checkable artifact** — a negative-control head-to-head where a self-scoring gate stays green while orca-fleet's goes red — before the #1 threat (**Ruflo/claude-flow**) closes the gap and claims priority through its own dossier machinery.
4. **Topology (C) and worker isolation are now Anthropic platform primitives** (agent teams, `isolation: worktree`, hooks) — **ride them**; keep B + the rest of D as the differentiated layer attached via a headless verifier session and native completion hooks.
5. Two adjacent moves compound the moat: **re-message on "verified, not asserted" / own-the-outer-loop**, and **extend the evidence manifest into an EU AI Act Art-12 provenance record**, which unlocks a compliance-conformance mission (`attest-it`).

## Strategic thesis: a finite, defensible window

Round-1 established that no competitor ships orca-fleet's B+C+D combination. Round-2 asks *how durable* that is:

- **Commoditizing NOW (tailwind that is also the erosion clock).** "Own the Outer Loop" (Addy Osmani, Jul 2026) mainstreamed the vocabulary — *"prefer deterministic verifiers over asking the same model to grade its own output," "split implementers and reviewers," "autonomy follows verification."* arXiv **2607.05391** ("LLM-as-a-Verifier", Jul 2026) declares verification a scaling axis; arXiv **2608.13867** (Aug 2026, 314-page monograph) codifies the evidence-ledger + reliability-protocol discipline. Leading with a *generic* "we verify" will soon differentiate nothing.
- **Still ownable (6–18 months).** A **mandatory negative control**, an **independent-session git re-derivation from a frozen `contract@digest`**, and a **frozen criterion↔test denominator** have zero/near-zero shipping prior art. The move is to *define the vocabulary + the benchmark* before convergence.
- **The market just learned to distrust self-reported green.** The flagship self-consistent oracle, **SWE-bench Verified**, collapsed under contamination in 2026 (agents gamed `conftest.py`; a large share of "passing" PRs would not merge; OpenAI reportedly stopped reporting it — *magnitudes SECONDARY/UNVERIFIED, direction corroborated*). This is the exact failure orca-fleet's negative control + independent re-derivation is built to catch, and the most persuasive public narrative for the moat.

## Threat map — who closes the gap, and how fast

Verified against primary sources on 2026-08-28.

| Competitor | SHA/sig-binding | Independent 2nd session | Negative control | Frozen denominator | Full-axis-B ETA | Why |
|---|:-:|:-:|:-:|:-:|---|---|
| **Ruflo (claude-flow)** | ✅ Witness Verification (ADR-103) signed artifact manifest + `verify rollback --to-commit` | ◐ PAIR "navigator" fresh-context verify (same-run, LLM-graded) | ✗ | ◐ scope check vs the agent's *own plan* | **<6mo** | rebranded Ruflo v3.10.1, ~69.6k★, weekly alpha, public "Prior Art Dossier" (2026-06-13) |
| **gstack + Octomind** | ◐ content-fingerprint FRESH/STALE ledger | ✗ (same-session; provenance bit) | ✗ | ◐ Octomind 0.44.2 checklist-from-request | **6–18mo** | huge reach + YC megaphone; Octomind ships fast |
| **Factory.ai** | ◐ git audit/OTEL, scoped tokens | ◐ distinct validator models (same-run) | ✗ | ✗ self-set milestone criteria | **6–18mo** | well-funded, but aimed at *security* not *completion* |
| **ccswarm** | ✗ | ◐ Sangha independent vote (LLM) | ◐ `mutation-test` skill (advisory) | ✗ | **12–18mo+** | owns the closest ideas, lowest velocity |

**#1 threat — Ruflo, verified with a correction.** Primary source (`github.com/ruvnet/claude-flow`, now `ruvnet/ruflo`) confirms the rebrand, v3.10.1, ~69.6k★, and that **Witness Verification (ADR-103) is real**. Crucially, the README frames ADR-103 as a **signed manifest of artifacts** where `ruflo verify` "confirms the installed version matches the audited baseline" — i.e. **supply-chain / install integrity**, *not* a per-task completion gate. The stronger "manifest of fixes that finds the regression-introducing commit" characterization traces to Ruflo's own **Prior Art Dossier** (self-promotional), so it is recorded here as *Ruflo's claim*, not established fact. Net: Ruflo ships SHA/signature-bound integrity + a fresh-context navigator + rollback + a self-scored truth score, and is one negative control + one navigator-hardening away from the full completion axis — at weekly cadence, a **<6-month copy**, and it is already building priority-claim machinery. **This is the clock the roadmap runs against.**

## Platform trajectory — ride vs. commoditize

The substrate is absorbing topology and isolation; it ships no completion oracle, so B stays defensible.

| Platform surface | State (2026-08-28) | Implication for orca-fleet |
|---|---|---|
| Claude Code **agent teams** (lead + teammates, shared task list w/ deps + file-lock claim, plan-first) | SHIPPED experimental, flag-gated, iterating weekly (v2.1.250); GA <6–18mo (SPECULATED) | **Claim C is a native primitive — ride it.** Coordinator = lead; workers = subagent-defs. |
| **Subagents** + `isolation: worktree` (enforced) + read-only Explore/Plan + managed-agents orchestration | SHIPPED now | Build-blind reviewer + worktree isolation are **free**; keep coordinator-never-writes + single-conductor as discipline. |
| **Hooks** (`Stop`, `TaskCompleted` exit-2 = block completion, `TeammateIdle`) | SHIPPED now | **Native attach point for the gate.** `TaskCompleted` exit-2 = "cannot mark done until verified." Risk: `allowManagedHooksOnly` can lock out plugin hooks in enterprise → need a fallback. |
| **Claude Agent SDK** (headless `-p`; teammates do NOT spawn in `-p`) | SHIPPED now | A headless run is naturally a **lone, separate session** — the substrate for the independent verifier. |
| **agentskills.io** spec | SHIPPED, capability-only; no verification vocab | B stays invisible-to-format; `proof:` rides free-form `metadata`; zero lock-in. Watch for an outcome/eval vocabulary (SPECULATED). |
| **MCP** roadmap: Tasks (async), ETag/content-versioning, agent-identity/delegation | ANNOUNCED 6–12mo | Ride for: verifier-as-Task, content-bound evidence freshness, per-worker scoped credentials + attesting the verifier as a distinct principal. |

**Absorption-risk register** (full detail in the platform brief): agent-teams GA absorbs C (SPEC); read-only subagents+worktrees already absorb build-blind+isolation (SHIPPED); Stop/TaskCompleted make gates a generic surface — only B's *content* is defensible (SHIPPED); `allowManagedHooksOnly` lockout needs an MCP/CI/SDK fallback (SHIPPED); MCP ETag/Tasks commoditize evidence ledgers (ANNOUNCED). The ledger was never the moat; the negative control + independent re-derivation are.

## The proof plan — make the moat un-fakeable and public

The load-bearing insight: **every existing benchmark measures agent capability; none measures verifier soundness** — "what fraction of *gamed* solutions did the completion gate wrongly accept?" (false-done rate). That axis is uncontested whitespace: **benchmark the gate, not the agent.**

- **VF-Bench** — a corpus of *gaming traps* (inline-demo/dead-library, tautological test, wrong-SHA/stale-env, scope-shrink, rebase-after-review, fabricated finding, lucky-single-run), each engineered so a naive self-scoring gate goes GREEN on a wrong solution while orca-fleet's independent + negative-control + frozen-denominator gate goes RED. Metric = **false-done rate**. Substrate exists today: **inspect-ai** (`Task = Dataset + Solver + Scorer`, Docker sandbox, runs external agents — so Ruflo's `verify` and orca-fleet's verifier drop in side-by-side). Contamination hygiene copied from **Terminal-Bench** (private tests, canary GUID, versioning) and **SWE-bench-Live** (held-out/temporal refresh).
- **The negative control is off-the-shelf and deterministic:** mutation testing (mutmut/Stryker/PIT/cargo-mutants). A criterion-violating mutant that **survives** is a tautological suite; a competitor cannot argue with a surviving-mutant report. Action: replace the hand-wavy "mutate the boundary" in `evidence-manifest.md` with a named tool + a pinned mutant id + a killed/survived verdict.
- **Two proof runs that advance a mission tier AND seed VF-Bench:** (1, P0) **prove-it self-run** against this repo (freeze a contract on an under-tested `scripts/validate.py` rule, TDD a criterion-bound test, `mutmut`-kill the criterion-violating mutant, independent verifier re-derives + clean-env re-runs at `head_sha`) → advances `doctrine-only → self-run` and yields the reference negative-control artifact; (2, P1) **harden-it external-run** (plant a secret → `gitleaks` RED → remove → GREEN) → the cheapest unfakeable external proof. Both double as VF-Bench trap seeds — shared artifacts, no duplicated effort. Companion to the flagship ship-it proof already tracked in #49.

## Positioning, autonomy, and the compliance wedge

- **Reposition on "verified, not asserted" and align with "own the outer loop."** "Outcomes" is commoditized (Factory/Devin/Copilot/Jules are all plan-first), and — per round-1 — the "ingredients, not outcomes" claim overstates the delta vs gstack/addyosmani. Scope the change to *external positioning* (README/AGENTS.md competitive framing); the internal layer-decision rule ("a fleet is an outcome, not an ingredient") stays. Feeds the doc that #52 asked for.
- **Speak the autonomy ladder (L0–L5).** Buyers reason in Osmani's levels ("the level you can safely reach is exactly the level you can cheaply prove"). Position orca-fleet as the L4–L5 layer whose independent verifier is the *cheap verification* that unlocks high autonomy; add an `autonomy:` frontmatter tag (sibling to `proof:`).
- **Turn the evidence manifest into an EU AI Act Art-12 provenance record.** Articles 12/50 enforceable **2 Aug 2026** expect per-change provenance (governing spec/policy version, model lineage, reviewer identity + timestamp, test outcomes, security-scan results, tamper-evident retention) — **structurally the orca-fleet manifest**. This is the strongest enterprise wedge surfaced this round and the prerequisite for `attest-it`.

## Catalog expansion — two new missions pass the identity test

Run against the five-part mission-identity test (unit of work · state machine · convergence proof · ordering/isolation · parking/failure):

- **`attest-it` (PASS, strongest).** Prove a codebase/change-set conforms to a standard (EU AI Act Art-12/50, SOC 2, NIST SSDF) with auditor-grade, independently-re-derived evidence, or name the gaps. Unit = one obligation from a *frozen standard catalog* (`standard@version`, not a discovered finding); state machine `UNAUDITED → EVIDENCED → VERIFIED / GAP`; convergence = every obligation evidence-bound + re-derived; parking = `CONFORMANT-WITH-GAPS` to a human/legal owner. Rides the moat directly; timed to the enforcement wave. Depends on the Art-12 manifest extension.
- **`access-it` (PASS).** WCAG 2.2 AA (EAA/ADA/508) conformance over a *frozen surface*. Deterministic oracle (axe-core/Lighthouse) + mandatory negative control (revert → violation returns) + a hard **30–40% automation ceiling** that forces screen-reader/cognitive criteria into a first-class human-AT park — a distinct convergence + parking semantics. (Caveat: without the standard-frozen denominator + ceiling-parking it degenerates into a clean-sweep variant — those are what keep it distinct.)
- **Rejected (documented to prevent scope-creep):** `stabilize-it`/incident-response (telemetry substrate, not git; prod-revert negative control unsafe — belongs to SRE agents; `root-cause` owns the repo-scoped slice); `docs-drift`, `upgrade-it`, `api-compat` (modes of `clean-sweep`/`modernize-it`/`review-it`); `patch-it` (fold into `harden-it` with an SCA-frozen denominator); `localize-it` (translation correctness isn't git-verifiable — poor axis-B fit).

## Prioritized roadmap (filed as issues)

Priority/effort/horizon are analyst estimates from the briefs. `filed as` links the GitHub issue.

| # | Action | Effort | Priority | Horizon | filed as |
|---|---|---|---|---|---|
| 1 | Ship a reproducible negative-control head-to-head vs a self-scoring gate (Ruflo) + a dated priority record | M | P0 | now | [#73](https://github.com/ravidsrk/orca-fleet/issues/73) |
| 2 | prove-it self-run with a mutation negative control (→ self-run tier) | M | P0 | now | [#74](https://github.com/ravidsrk/orca-fleet/issues/74) |
| 3 | Reposition on "verified, not asserted" / own-the-outer-loop; qualify "outcomes, not ingredients" | S–M | P0 | now | [#75](https://github.com/ravidsrk/orca-fleet/issues/75) |
| 4 | Harden the independent verifier: separate-process, deterministic git re-derivation | M | P1 | <6mo | [#76](https://github.com/ravidsrk/orca-fleet/issues/76) |
| 5 | Package the verifier + gate as native Stop/TaskCompleted hooks, with an MCP/CI/SDK fallback | M | P1 | <6mo | [#77](https://github.com/ravidsrk/orca-fleet/issues/77) |
| 6 | Bind the evidence-manifest negative control to a named mutation tool + pinned mutant | S | P1 | now | [#78](https://github.com/ravidsrk/orca-fleet/issues/78) |
| 7 | Publish VF-Bench: a verifier-soundness (false-done-rate) benchmark | L | P1 | <6mo→6–18mo | [#79](https://github.com/ravidsrk/orca-fleet/issues/79) |
| 8 | Extend the evidence manifest to EU AI Act Art-12 provenance fields | M | P1 | <6mo | [#80](https://github.com/ravidsrk/orca-fleet/issues/80) |
| 9 | Document the platform-ride architecture + absorption-risk register (+ signals watch-list) | S–M | P1 | now | [#81](https://github.com/ravidsrk/orca-fleet/issues/81) |
| 10 | Map each mission to an autonomy level via an `autonomy:` frontmatter tag | S | P1 | now | [#82](https://github.com/ravidsrk/orca-fleet/issues/82) |
| 11 | harden-it external-run with a plant-secret negative control (→ external-run tier) | M | P2 | <6mo | [#83](https://github.com/ravidsrk/orca-fleet/issues/83) |
| 12 | Propose `attest-it`: standards/regulatory conformance mission (identity-test argued) | L | P1 | 6–18mo | [#84](https://github.com/ravidsrk/orca-fleet/issues/84) |
| 13 | Propose `access-it`: WCAG 2.2 conformance mission (identity-test argued) | L | P2 | 6–18mo | [#85](https://github.com/ravidsrk/orca-fleet/issues/85) |
| 14 | Publish to community marketplaces + skills indexers; lead with the machine-checked `proof:` badge | S | P2 | now | [#86](https://github.com/ravidsrk/orca-fleet/issues/86) |

Sequencing: **1–3 first** (they are the finite-window plays); 4–6 harden and sharpen the moat's core; 7 makes it a standing artifact; 8→12 opens the enterprise/compliance line; the rest compound. Related open issues: **#49** (ship-it proof — companion to 2/11), **#51** (attention-budget curve — complements the `TeammateIdle` hook in 5/9), **#52** (positioning doc — 3 supplies its reframe; the round-1 snapshot supplies its comparison).

## Sources (accessed 2026-08-28)

Full per-cluster citations live in the four research briefs behind this synthesis. Load-bearing sources:

**Platform** — agent teams <https://code.claude.com/docs/en/agent-teams> · subagents/worktree isolation <https://code.claude.com/docs/en/sub-agents> · hooks (Stop/TaskCompleted/TeammateIdle, `allowManagedHooksOnly`) <https://code.claude.com/docs/en/hooks> · Agent SDK <https://code.claude.com/docs/en/agent-sdk/overview> · agentskills spec <https://agentskills.io/specification.md> · MCP roadmap <https://modelcontextprotocol.io/development/roadmap>.

**Proof** — SWE-bench Verified <https://openai.com/index/introducing-swe-bench-verified/> · SWE-bench-Live <https://huggingface.co/datasets/SWE-bench-Live/SWE-bench-Live> · Terminal-Bench <https://www.tbench.ai/> · inspect-ai <https://inspect.aisi.org.uk/> · mutation testing <https://github.com/boxed/mutmut>, <https://stryker-mutator.io/>, <https://github.com/sourcefrog/cargo-mutants> · contamination reckoning (SECONDARY) <https://www.openhands.dev/blog/ai-coding-benchmarks-explained>.

**Threat** — Ruflo/claude-flow <https://github.com/ruvnet/claude-flow> (renders as `ruvnet/ruflo`, README + wiki confirm ADR-103 Witness Verification) · Truth Verification System <https://github.com/ruvnet/claude-flow/wiki/Truth-Verification-System> · Prior Art Dossier (self-promotional) <https://gist.github.com/ruvnet/1a88c9fc7b7eaa99b4ea2f0dd0891c49> · Octomind 0.44.2 <https://octomind.run/blog/octomind-0-44-2-release> · Factory security review <https://factory.ai/news/automated-security-review> · Osmani "Own the Outer Loop" <https://addyosmani.com/blog/own-the-outer-loop/> · arXiv <https://arxiv.org/abs/2607.05391>, <https://arxiv.org/abs/2608.13867>.

**Demand/GTM** — EU AI Act transparency guidance <https://digital-strategy.ec.europa.eu/en/library/guidelines-transparency-obligations-providers-and-deployers-ai-systems> + 2 Aug 2026 <https://commission.europa.eu/news-and-media/news/safer-and-more-transparent-ai-2026-08-02_en> · autonomy levels <https://x.com/addyosmani/article/2072885435312042327> · accessibility automation ceiling <https://stigstack.com/comparisons/ai-accessibility-tools/> · marketplace scale <https://skillworks.kynth.studio/>.

### UNVERIFIED / caveats

- **Ruflo ADR-103 is confirmed as a signed *artifact/install-integrity* manifest** (`ruflo verify` = installed tree matches audited baseline); the "manifest of *fixes* that finds the regression-introducing commit / completion axis-B" framing is **Ruflo's own dossier claim**, not corroborated as a per-task completion gate. Treat the threat as "adjacent and fast," not "already shipped."
- SWE-bench contamination magnitudes (59% flawed tests, ~33% leakage, "half of PRs wouldn't merge", OpenAI deprecation) are **secondary/aggregator-sourced** — direction corroborated, exact numbers not load-bearing.
- arXiv IDs (2606.28430, 2608.04066, 2607.05391, 2608.13867, 2604.04604) are carried from the briefs; treat provenance as reported, not independently re-fetched here.
- Star/commit/install counts and vendor pricing are self-reported or comparison-site figures — directional only.
- Time-to-copy ETAs and mission-identity verdicts are analyst judgments, not vendor commitments; new missions still require the full PR contract (SKILL.md + guide + README/AGENTS.md + `EXPECTED_MISSIONS`) and must argue the identity test at PR time.
