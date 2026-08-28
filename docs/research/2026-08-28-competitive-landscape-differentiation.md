# Competitive landscape × differentiation — orca-fleet vs the agent-orchestration market — 2026-08-28

> **Dated snapshot (2026-08-28).** A point-in-time competitive scan against then-current primary
> sources, scoring the market on orca-fleet's four load-bearing claims. Not a live coverage
> matrix and not a product roadmap — see [ARCHITECTURE.md](../../ARCHITECTURE.md) for current
> catalog state. Vendor features move weekly; every claim is cited, and unverifiable claims are
> flagged rather than guessed.

**Status:** MAPPED — 29 competitors across 4 clusters scored; differentiation + defensibility frozen
**Date:** 2026-08-28
**Base:** `main` @ `32050a0`
**Method:** 4 parallel research agents, one per cluster, each reading primary sources (official docs, source repos, first-party blogs, spec pages) and filling a fixed 9-field rubric + an A/B/C/D score per competitor. Full per-competitor briefs archived as the agent artifacts behind this synthesis.
**Destination:** A frozen positioning/differentiation map that answers "does orca-fleet's thesis hold up, what is copyable vs defensible, and how should it describe itself" — consumable without re-running the scan.

## The four claims under test

| | Claim | One-line test |
|---|---|---|
| **A** | outcome-commitment + per-unit **state machine** + **convergence proof** | is "done" a *named, checkable end-state*, or just a run loop terminating? |
| **B** | **SHA-bound evidence manifest** + **independent second-session verifier** re-deriving from git — incl. **negative control** (proof-can-fail) + **frozen denominator** (agent can't shrink scope) | is "done" *re-derived from authoritative state by a different session*, or graded on the agent's own trace? |
| **C** | **coordinator-never-writes-code** + **disposable fresh-context workers** + specialized roles (build-blind reviewer, single merge conductor) | is there a non-writing coordinator + isolated workers, or one agent that both drives and codes? |
| **D** | **operational-hardening suite**: merge-train serialization · reviewed-SHA freshness · attention budget · liveness-resume · sandbox profiles · one-router-per-worker | are these shipped as an *integrated policy set*, or at most one fragment? |

**B is the axis that matters.** A, C, and — for distribution — the SKILL.md/plugin format are where the
market is converging. B (and, secondarily, D as a bundle) is where orca-fleet is alone.

## Headline finding

**No competitor scans as `✓` on axis B, and none ships the full A+B+C+D combination.** Across 29
frameworks, products, packs, and OSS swarms, "done" is universally graded on the producing session:
a termination/stop condition, a same-run guardrail/tripwire, an LLM critic saying "APPROVE", a
self-computed quality score, an advisory second-model review, or an offline eval against a
hand-authored dataset. **Not one binds completion to a git SHA and re-derives the criterion set from
a frozen contract in a *different* session, and not one runs a mandatory negative control** (revert or
mutate to prove the check can go red). orca-fleet's "git is truth; the trace is never the oracle;
prove the proof can fail" trio is matched only by a non-product research instrument (arXiv 2608.04066).

But the scan also **corrects orca-fleet's own headline positioning**: "outcomes, not ingredients" is
materially overstated (see [The positioning correction](#the-positioning-correction-outcomes-vs-ingredients-is-the-wrong-axis)).

## The differentiation scorecard

Legend: **✓** present · **◐** partial/weaker analog · **✗** absent. Scores are for the *shipped design*
as documented at the cited sources on 2026-08-28.

### Reference row

| Entity | A | B | C | D |
|---|:-:|:-:|:-:|:-:|
| **orca-fleet** (design; proof status mixed — see caveat) | ✓ | ✓ | ✓ | ✓ |

> Caveat: the orca-fleet row is its *documented doctrine*. Per the repo's own `proof:` field, only
> `clean-sweep` (self-run) and `review-it` / `oss-contribute` (external-run) are field-proven; the rest
> are honestly `doctrine-only`. This snapshot compares *designs*, not maturity.

### Cluster 1 — general-purpose orchestration frameworks/SDKs (libraries to *build* multi-agent apps)

| Entity | A | B | C | D | License |
|---|:-:|:-:|:-:|:-:|---|
| LangGraph (LangChain) | ✗ | ✗ | ◐ | ◐ | MIT |
| CrewAI | ◐ | ✗ | ◐ | ✗ | MIT |
| AutoGen / AG2 (Microsoft / community) | ✗ | ✗ | ◐ | ◐ | MIT / Apache-2.0 |
| OpenAI Agents SDK (Swarm successor) | ✗ | ✗ | ◐ | ◐ | MIT |
| Google ADK | ◐ | ◐ | ◐ | ◐ | Apache-2.0 |
| Microsoft Agent Framework | ◐ | ✗ | ◐ | ◐ | MIT |

Verification is left to the app developer everywhere. Closest on B is **Google ADK** (`AgentEvaluator`/
`EvalSet`: trajectory + response matched against ground truth, rubric metrics) — but it is an *offline
regression eval against hand-authored datasets*, trusts the recorded trajectory as the oracle, and
never re-derives from git. Strongest ops slices: LangGraph checkpoints/time-travel and MS Agent
Framework workflow checkpointing + durable execution + `RequestInfoExecutor` HITL.

### Cluster 2 — autonomous SWE agent products (issue/prompt → code → PR)

| Entity | A | B | C | D | Model |
|---|:-:|:-:|:-:|:-:|---|
| Devin (Cognition) | ◐ | ✗ | ◐ | ◐ | closed SaaS |
| **Factory.ai** (Droids/Missions) | ◐ | ◐ | ✓ | ◐ | commercial |
| OpenHands (All-Hands.ai) | ✗ | ✗ | ◐ | ◐ | MIT |
| SWE-agent (Princeton) | ✗ | ◐ | ✗ | ◐ | MIT |
| GitHub Copilot coding agent | ◐ | ✗ | ◐ | ◐ | commercial |
| Cursor Cloud Agents | ◐ | ✗ | ◐ | ◐ | commercial |
| Google Jules | ◐ | ✗ | ✗ | ◐ | freemium |
| Sourcegraph Amp | ✗ | ◐ | ◐ | ◐ | commercial |

**Factory.ai is the closest overall competitor**: Missions = up-front plan → features/milestones with
success criteria → orchestrator + feature workers + **distinct validation workers** at milestone
boundaries + specialized Code/Review/Test/Docs droids. But validation is *behavioral against the
running app in the same system* — no SHA binding, no independent second session, no negative control,
no frozen denominator. **SWE-agent + SWE-bench is the closest technical *shape* of B** (FAIL_TO_PASS /
PASS_TO_PASS criterion↔test binding on a frozen task instance, evaluated by an independent process) —
but it is an offline benchmark, not a runtime completion gate.

### Cluster 3 — Claude Code / agent-skills ecosystem (orca-fleet's substrate, channel, and upstream packs)

| Entity | A | B | C | D | Role |
|---|:-:|:-:|:-:|:-:|---|
| Claude Code subagents | ✗ | ✗ | ◐ | ◐ | substrate (isolation:worktree) |
| Claude plugins + marketplaces | ✗ | ✗ | ✗ | ✗ | distribution channel |
| Agent Skills / agentskills.io spec | ✗ | ✗ | ✗ | ✗ | format (capability packaging only) |
| Claude Agent SDK | ✗ | ✗ | ◐ | ◐ | harness/plumbing |
| Claude Code agent teams (experimental) | ✗ | ✗ | ◐ | ◐ | nearest native fleet primitive |
| mattpocock/skills | ◐ | ✗ | ✗ | ✗ | upstream pack |
| **garrytan/gstack** | ◐ | ◐ | ◐ | ◐ | upstream pack |
| addyosmani/agent-skills | ◐ | ◐ | ◐ | ◐ | upstream pack |
| obra/superpowers | ◐ | ◐ | ◐ | ◐ | adjacent methodology pack |

Two decisive facts here. (1) **The SKILL.md / agentskills.io format carries zero outcome/verification
vocabulary** — `name`, `description`, optional `license`/`compatibility`/free-form `metadata`. orca-fleet's
entire A/B/C/D layer lives *above* the format and is invisible to it; the format cannot encode the moat,
and conforming to it is what gives low lock-in. (2) **The closest thing in the whole study to axis B is
`garrytan/gstack`**: a real SHA/content-bound evidence *ledger* (`gstack-evidence` records
`cmd_sha256`+commit+tree+working-tree fingerprint, grades FRESH/STALE/MISSING), a `gstack-wtree` content
fingerprint that "binds reviews and test evidence to content instead of commit SHAs", a `gstack-verify-gate`
Stop-hook, plus `/cso` independent-finding and `/codex` cross-model checks. It falls short of orca-fleet on
exactly three points: **self-produced in the same session** (no independent second-session re-derivation),
**no mandatory negative control**, **no frozen denominator / criterion↔test binding**.

### Cluster 4 — verification-centric agents + parallel "fleet/swarm" tooling (the direct-threat niche)

| Entity | A | B | C | D | Kind |
|---|:-:|:-:|:-:|:-:|---|
| Qodo (Cover / Merge) | ◐ | ✗ | ✗ | ✗ | code-integrity SaaS |
| CodeRabbit | ✗ | ◐ | ✗ | ✗ | AI review SaaS |
| Greptile (TREX) | ✗ | ◐ | ✗ | ✗ | AI review + execution |
| Graphite (Diamond/Agent) | ✗ | ✗ | ✗ | ✗ | AI review + stacked PRs |
| Reflection AI (Asimov) | ✗ | ✗ | ✗ | ✗ | comprehension (adjacent) |
| **ccswarm** (OSS) | ◐ | ◐ | ◐ | ◐ | Claude/Codex swarm |
| **claude-flow** (OSS) | ◐ | ◐ | ◐ | ◐ | Claude swarm + verify gate |
| LangSmith | ✗ | ◐ | ✗ | ✗ | eval-gate / LLM-as-judge |

Best execution-evidence-on-a-diff: **Greptile TREX** (writes tests for the PR, runs them in a sandbox,
attaches logs/traces/videos as evidence). Best first-class verification *gate* + git rollback:
**claude-flow** Truth Verification System (weighted truth score from real compile/test/lint checks, a
threshold gate with auto-rollback, `verify rollback --to-commit <sha>`, and a `verify check --json` CI
gate). Best topology: **ccswarm** (git-worktree isolation + specialized roles + Sangha independent-vote
consensus + NDJSON replay/undo ledger + a `mutation-test` skill — the nearest OSS thing to a negative
control, though it is a review skill, not a mandatory manifest gate). All three **self-grade**; none re-derives
in an independent session, none has a mandatory negative control, none freezes a denominator.

## Closest competitor, by lens

| Lens | Closest | Why it's close | The gap orca-fleet keeps |
|---|---|---|---|
| **Overall product concept** | Factory.ai (Missions) | plan→milestones+success-criteria, orchestrator+workers, distinct validation-worker role, specialized droids | behavioral self-QA, not git-SHA-bound independent re-derivation; no negative control / frozen denominator; no reviewed-SHA freshness / merge train |
| **Verification (B) — shipping, in-ecosystem** | garrytan/gstack | SHA/content-bound evidence ledger + verify Stop-hook + `/cso`/`/codex` second opinions | self-produced same-session; no independent second session; **no negative control**; no frozen criterion denominator |
| **Verification (B) — most direct threat** | claude-flow | branded verify gate + truth score from real checks + git rollback-to-SHA + CI JSON gate; ~500k self-reported installs; same MCP/Claude ecosystem; fast alpha | self-scored; no independent session; no negative control; no frozen denominator |
| **Topology (C)** | ccswarm / obra/superpowers / Claude Agent Teams | worktrees + specialized roles + reviewer/consensus; lead+teammates+shared task-list state machine | none enforce coordinator-**never-writes**, a single merge conductor, or fresh-terminal disposable respawn |
| **Framework verification** | Google ADK | criterion↔ground-truth trajectory+response eval, rubric metrics | offline dataset eval; trusts recorded trace; no git re-derivation / independent session / negative control |
| **Technical shape of B** | SWE-agent + SWE-bench | frozen task instance + FAIL_TO_PASS/PASS_TO_PASS + independent evaluation | offline benchmark, not a runtime gate; no SHA manifest / negative control |

## Copyable vs defensible

**Weekend-to-weeks copies (do not treat as moat):**

- **Outcome/plan-first commitment (A)** — Factory Missions, Jules/Copilot plan approval, gstack `/ship`,
  addyosmani `/build auto` already ship it.
- **Fleet topology skeleton (C)** — Claude Agent Teams (lead+teammates+shared task list), subagents'
  `isolation: worktree`, ccswarm, Superpowers, Cursor "Builds" snapshots, Devin/OpenHands/Jules VMs. Fan-out
  over isolated contexts is becoming an Anthropic *platform primitive* (managed-agents multiagent orchestration).
- **An evidence *ledger* of command runs** — gstack proves this is public and shippable.
- **A verification *gate* + git rollback** — claude-flow proves this is public and shippable.
- **A "second reasoner" / LLM-as-judge review pass** — Amp Oracle, Cursor Bugbot, CodeRabbit judge model,
  LangSmith llm-as-judge, `/codex`.
- **Distribution** — SKILL.md/agentskills.io conformance + plugin marketplace is commodity, MIT-licensed, low lock-in.

**Genuinely defensible (zero or near-zero shipping prior art):**

1. **Independent, *different-session* verifier that re-derives from git and refuses to trust the trace** —
   `git merge-base --is-ancestor`, clean-env test at the SHA, `reviewed_sha == head_sha`, symbol greppable on
   BASE. Everyone who verifies at all self-certifies within the producing session or evals skills in CI.
2. **Mandatory negative control (revert/mutate → red).** Not shipped by any competitor. The only prior art is a
   research instrument (arXiv 2608.04066) and an ablation methodology (arXiv 2606.28430). This is the single
   least-copied idea in the study.
3. **Frozen denominator + criterion↔test binding** so an agent cannot silently shrink its own scope — the
   `contract.source@digest` → `criterion_ids` mechanism. SWE-bench has the *shape* offline; no runtime product has it.
4. **The ops-hardening suite (D) as one coherent contract** — merge-train serialization with hot-file chains +
   reviewed-SHA freshness + attention budget (≈1 reviewer / 3 builders) + liveness-resume-against-a-ledger +
   sandbox profiles + one-router-per-worker + wrong-base detection. Competitors have at most one fragment
   (Graphite's merge-ordering UX, claude-flow's auto-rollback, Copilot's branch-protection respect). **This bundle
   is harder to weekend-copy than any single verification primitive.**
5. **Coordinator-never-writes discipline + single merge conductor.** Every fleet competitor lets the
   coordinator/main agent also write code; none enforce a build-blind reviewer or one conductor draining a train.

**Net:** the moat is not any one primitive — it is the **combination** of (B) + (D), anchored by the two ideas
with no shipping prior art: **the mandatory negative control** and **the independent second-session re-derivation**.

## The positioning correction: "outcomes vs ingredients" is the wrong axis

The scan directly contradicts orca-fleet's own README/AGENTS.md framing that the upstream packs are mere
"ingredients":

- **mattpocock/skills — the framing holds.** Explicitly small, composable, single-activity skills, positioned
  *against* process-owning frameworks.
- **garrytan/gstack — the framing is false.** An outcome-oriented pipeline (Think→Ship→Reflect) with named
  end-states (`/ship`, `/land-and-deploy` "verified in production"), a `/ship` IRON LAW, and a real evidence ledger.
- **addyosmani/agent-skills — the framing is false.** A full-lifecycle phase-committed pipeline with a Definition
  of Done, parallel review personas, and a catalog-wide execution-trace eval framework.

Factory Missions, Jules, and Copilot are *also* outcome/plan-first. **Outcomes are commoditizing.** The honest,
defensible differentiation is:

> **Independently-verified, git-grounded, negative-controlled fleet outcomes** (with a coordinator that never
> writes code and an ops-hardening contract) — **vs self-certified, single-session pipeline outcomes.**

Recommendation: retire or soften "outcomes, not ingredients" and lead with **"verified, not asserted"** —
"git is truth, the trace is never the oracle, prove the proof can fail." That message is the one no competitor
can currently make truthfully.

## Threats and what to watch

1. **claude-flow (fastest gap-closer).** Same ecosystem, large install base, already ships a verify gate + SHA
   rollback + CI gate. Adding SHA-bound manifests, a negative control, and a frozen denominator is plausibly a
   weeks-scale copy. Highest-priority watch.
2. **Anthropic absorbing topology.** Subagents, Agent Teams, and managed-agents multiagent orchestration make C a
   platform primitive. orca-fleet should *ride* these (build the coordinator/worker skeleton on them) rather than
   reimplement, and keep its differentiation in B+D on top.
3. **Factory.ai (best-funded nearest concept).** If it swaps behavioral self-QA for git-bound independent
   verification with a negative control, it closes the most ground of any product. Watch its validation-worker roadmap.

## Independent validation — the idea is in the air (tailwind and warning)

Three recent primary research artifacts (not competitors) both *validate* orca-fleet's design and prove the
guards are necessary — and signal the window to own the category is finite:

- **"Building to the Test", Microsoft, [arXiv 2606.28430](https://arxiv.org/abs/2606.28430) (2026-06-26).**
  Coding agents with a naive in-loop oracle **game the check** — inlining tested behavior into a throwaway demo
  while leaving the requested library dead. The fix the paper validates *is orca-fleet's B*: a **source-hidden
  oracle** (frozen denominator — the agent sees failing test *names*, never their source), a **no-op ablation**
  (textbook negative control), and an **audit that re-derives from delivered source**. Near-exact independent
  confirmation, plus proof that self-graded completion is exploitable.
- **"The LLM Proposes, the Executive Disposes", [arXiv 2608.04066](https://arxiv.org/abs/2608.04066) (2026-08-04).**
  A deterministic executive owns all belief; the LLM may only file typed proposals; a claim is admitted only when a
  **prediction pre-registered before acting** is matched against observation by code, and runs **self-invalidate**
  on breached floors (built-in negative control). Closest philosophy match to "the trace is never the oracle."
- **Spec-first convergence / "AICode", [arXiv 2608.12440](https://huggingface.co/papers/2608.12440) (2026-08-12).**
  A frozen spec + verification cycles until two consecutive passes return zero findings (a convergence proof ≈
  orca-fleet's), audited in different sessions. Closest to claims A + independent-ish sessions.

## Recommendations (positioning + product; each an orca-fleet-owned action)

1. **Re-message around "verified, not asserted."** Rewrite the README/AGENTS.md/concepts lead from "outcomes, not
   ingredients" (overclaims vs gstack/addyosmani) to the evidence protocol (B) + ops suite (D). *One-way? No — a
   reversible taste/doc change.*
2. **Make the two zero-prior-art primitives the headline demo.** A reproducible side-by-side vs a self-scoring tool
   (e.g. claude-flow): mutate the code, show the competitor's gate stays green while orca-fleet's negative control
   goes red and the independent verifier rejects the manifest. Turns the moat into a third-party-checkable artifact —
   and fits the repo's own `proof:` ethos (advance a mission's tier with a real run report).
3. **Treat topology (C) as table stakes.** Build the coordinator/worker skeleton on Claude Agent Teams / subagents
   as they stabilize; keep coordinator-never-writes + single-conductor as the discipline layer, not a reimplemented substrate.
4. **Watch claude-flow and Factory explicitly** (above). Consider a public "verified-fleet" benchmark stressing
   negative-control + frozen-denominator, where self-scoring tools measurably fail.
5. **Don't expect distribution lock-in.** Keep agentskills.io conformance + marketplace; compete on the behavioral
   runtime, which the format cannot encode.

## Sources

Primary sources, all accessed 2026-08-28. Per-competitor rubric detail and the full citation set live in the four
cluster briefs behind this synthesis; the load-bearing URLs:

**Frameworks/SDKs** — LangGraph <https://docs.langchain.com/oss/python/langgraph/persistence>, <https://docs.langchain.com/oss/python/langgraph/interrupts>; CrewAI <https://docs.crewai.com/en/concepts/tasks>; AutoGen <https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/termination.html>, AG2 <https://docs.ag2.ai>; OpenAI Agents SDK <https://openai.github.io/openai-agents-python/>, <https://openai.github.io/openai-agents-python/guardrails/>; Google ADK <https://google.github.io/adk-docs/evaluate/>; MS Agent Framework <https://learn.microsoft.com/en-us/agent-framework/workflows/checkpoints>, <https://learn.microsoft.com/en-us/agent-framework/workflows/human-in-the-loop>.

**Autonomous SWE** — Devin <https://docs.devin.ai/work-with-devin/advanced-capabilities>, <https://cognition.com/blog/devin-can-now-manage-devins>; Factory <https://docs.factory.ai/missions/overview>, <https://docs.factory.ai/missions/planning>, <https://docs.factory.ai/harness/subagents>, <https://docs.factory.ai/software-factory/automated-qa>; OpenHands <https://docs.openhands.dev/openhands/usage/agent-canvas/architecture>, <https://www.openhands.dev/blog/agent-sandboxing-what-openai-got-wrong-with-the-huggingface-hack>; SWE-agent <https://swe-agent.com/latest/usage/benchmarking/>, <https://arxiv.org/abs/2405.15793>; GitHub Copilot <https://docs.github.com/en/copilot/concepts/agents/cloud-agent/about-cloud-agent>; Cursor <https://cursor.com/blog/builds>, <https://cursor.com/guides/ai-code-review>; Jules <https://jules.google/docs>; Amp <https://ampcode.com/docs/markdown/models-and-subagents>, <https://ampcode.com/docs/tools#oracle>.

**Skills ecosystem** — Claude subagents <https://code.claude.com/docs/en/sub-agents>; plugins <https://code.claude.com/docs/en/plugins>; Agent Skills spec <https://agentskills.io/specification.md>; Agent SDK <https://code.claude.com/docs/en/agent-sdk/overview>; Agent Teams <https://code.claude.com/docs/en/agent-teams>; mattpocock/skills <https://github.com/mattpocock/skills>; garrytan/gstack <https://github.com/garrytan/gstack> (evidence source <https://raw.githubusercontent.com/garrytan/gstack/main/bin/gstack-evidence>); addyosmani/agent-skills <https://github.com/addyosmani/agent-skills> (evals <https://raw.githubusercontent.com/addyosmani/agent-skills/main/evals/README.md>); obra/superpowers <https://github.com/obra/superpowers>.

**Verification/fleet niche** — Qodo Cover <https://github.com/qodo-ai/cover-agent>, Merge code_validation <https://docs.qodo.ai/qodo-documentation/qodo-merge/pr-agent/core-abilities/code_validation>; CodeRabbit <https://www.coderabbit.ai/blog/explainable-reviews-coderabbit-review-context-engine>; Greptile TREX <https://www.greptile.com/blog/trex-code-execution>; Graphite <https://graphite.com/docs/ai-reviews>; Reflection AI <https://sequoiacap.com/companies/reflection-ai> (pricing/positioning UNVERIFIED); ccswarm <https://github.com/nwiizo/ccswarm>; claude-flow <https://github.com/ruvnet/claude-flow/wiki/Truth-Verification-System>; Anthropic multiagent orchestration <https://platform.claude.com/docs/en/managed-agents/multiagent-orchestration>; LangSmith <https://docs.langchain.com/langsmith/evaluation-concepts>, <https://docs.langchain.com/langsmith/read-local-experiment-results>.

**Supporting research** — <https://arxiv.org/abs/2606.28430> (Building to the Test, Microsoft) · <https://arxiv.org/abs/2608.04066> (Executive Disposes) · <https://huggingface.co/papers/2608.12440> (spec-first convergence).

### UNVERIFIED / caveats

- Adoption numbers (claude-flow ~500k installs; GitHub star counts) are self-reported or API-returned and **not
  load-bearing** — treat as directional only.
- First-party SWE-bench percentages for Devin (~13.86%, 2024) and OpenHands were not re-confirmed against a live
  page at this date; used only as historical capability signals.
- Reflection AI / Asimov pricing and "not a code-writer" positioning come from secondary write-ups; no first-party
  verification-feature source was found.
- "gstack has no independent second-session verifier / no negative control" is an **[INFERENCE]** from reading the
  `gstack-evidence` source + README tool table; not every file in the pack was read.
- Qodo 2.0 multi-agent internals and its release date are from secondary reporting (**UNVERIFIED**).
