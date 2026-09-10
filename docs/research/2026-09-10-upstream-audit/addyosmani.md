> **Dated snapshot (2026-09-10).** Per-source appendix to [2026-09-10-upstream-deep-audit-and-mission-proposals.md](../2026-09-10-upstream-deep-audit-and-mission-proposals.md); `file:line` anchors resolve at the commits named in its header. Scratch-clone paths in this report are for the audit session only.

# addyosmani/agent-skills × orca-fleet — adoption audit (2026-09-10)

**Upstream pin:** `6ca0cd7` (plugin 0.6.9, tagged 0.6.9 on 2026-09-04 at `84ee506`; HEAD is the merge of #531). Local clone: `scratchpad/upstream/agent-skills`.
**orca-fleet pin:** `a91937d` (main, 2026-09-10; the merge of #254 is `af8ea89`). All orca-fleet `file:line` anchors are at that SHA. Nothing in `/home/user/orca-fleet` was modified.
**Prior audits this extends (not repeated):** `docs/research/2026-07-15-addy-orchestration-gap-analysis.md` (D1–D8), `docs/research/2026-08-16-addy-latest-delta-plan.md` (E1–E7), `docs/research/2026-09-09-upstream-adoption-audit.md` §2.3 (two stale lenses, three NOT-ADOPTED items).
**Method:** every upstream file read in full (25 `SKILL.md`, 9 commands × 3 host dirs, 4 agents, 4 hook scripts + 2 hook docs + `hooks.json`, 7 references, `evals/README.md` + 25 case files + `run-evals.js` + 5 validators); every orca-fleet mission, playbook, runtime policy, `scripts/eval.py`, `hooks/hooks.json`, `runtime/scripts/verify-gate.sh`; `git show 0f6ced7` (#250) diffed line-by-line against the previous audit's stale rows; upstream `git log --since=2026-07-13` with author and commit dates resolved separately (several commits carry author dates before the window and commit dates inside it).

## 0. Headline findings

1. **#250 fixed two of the three security-lens staleness items and the perf-lens item.** `risk-review.md:34-38` now carries shared-store rate limiting and destructive-path target validation (`0f6ced7`); `speed-it/SKILL.md:61-68` carries the keep-or-revert precedence table and attempt ledger. **The third item — the Data Privacy & Compliance operating rules (`bb53a78`, merged 2026-08-14; `security-and-hardening/SKILL.md:378-397`) — is still absent from every orca-fleet file** (`grep -i "privacy|PII|GDPR|retention" playbooks/risk-review.md` → none; the only `retention` hit in the whole doctrine tree is the Art-12 provenance pointer in `evidence-manifest.md:49`).
2. **`observability-and-instrumentation` is the largest whole-skill gap and moved three times in the window** (`cd33117` runbooks, `8714f2b` runbook nesting, `6a9f2eb` entry-point attribution). orca-fleet has zero doctrine on structured logs, RED metrics, correlation IDs, symptom-based alerts, or runbooks (`grep -i "runbook|observab|RED metric|correlation" skills playbooks runtime` → only `verify-gate.sh:2` matches, on the word "hooks"). `playbooks/observe.md` is gstack's post-deploy canary, not instrumentation.
3. **The eval framework is where orca-fleet is furthest behind in mechanism, not doctrine.** `scripts/eval.py:27-108` routes on a hand-maintained `MISSION_TRIGGERS` dictionary — a second copy of the vocabulary, not the frontmatter `description` the host actually routes on. Upstream Tier 2 (`run-evals.js:104-149`) scores stemmed TF-IDF over the real descriptions, tests negatives pairwise against a declared `owner` (`:319-343`), fails on description collisions ≥75% (`:357-372`), and ratchets rank-1 at 95% in CI (`test-plugin-install.yml`). orca-fleet's 17 `skills/*/evals/evals.json` files carry `assertions[]` that no runner executes (`eval.py:370-394` counts them). `REVIEW.md` §2 item 3 independently measured this: 43 curated prompts score 100%, 36 realistic prompts 53%.
4. **`constraint-driven-development`'s floor guard shipped as a reference implementation on 2026-08-28 (`4be4bb7`, `references/floor-guard.md`) and orca-fleet's `floor-it` still names it as doctrine only** (`floor-it/SKILL.md:78` "land `check_constraints`-style validation in CI"; `grep check_constraints|floor-guard scripts runtime` → no script).
5. **Three upstream design choices must not be copied:** the `/ship` fan-out merges specialist reports in the *same main context that wrote the code* (`commands/ship.toml:27-37`); `doubt-driven-development` offers a "degraded self-questioning fallback" inside a subagent (`SKILL.md:47`); and `simplify-ignore.sh` rewrites source files on disk with placeholders during a session (`hooks/simplify-ignore.sh:176-216`) — under orca-fleet's build-blind review and SHA-bound manifests that is evidence tampering by construction. Section 7.

---

## 1. Inventory (from the files, one line each)

### 1.1 Skills (`skills/*/SKILL.md`, 25)

| Skill | Lines | One-line purpose (from the file) | Last substantive change |
|---|---|---|---|
| api-and-interface-design | 367 | Contract-first interfaces; Hyrum's Law; one-version rule; consistent errors; validate at boundaries; idempotency-key implementation (atomic claim, payload hash, in-flight duplicate policy, retention ≥ longest retry chain) `:156-215` | `ce89b03` 08-12 idempotency |
| browser-testing-with-devtools | 318 | Chrome DevTools MCP as runtime eyes; security boundaries — profile isolation, browser content is untrusted data, read-only JS `:60-107` | stable |
| ci-cd-and-automation | 391 | Quality-gate pipeline, GH Actions, feed CI failures to agents, preview deploys, flags, staged rollout, rollback, build cop | stable |
| code-review-and-quality | 397 | Five-axis review (correctness/readability/architecture/security/perf); severity Critical/Required/Optional/Nit `:181-187`; change sizing; dependency-upgrade discipline `:292-298`; structural remedies | stable |
| code-simplification | 332 | Behavior-preserving simplification; Chesterton's Fence; Rule of 500; scope to what changed | stable |
| constraint-driven-development | 312 | Written numbered quality bar in `CONSTRAINTS.md`; four-question interview with defaults; one tool per dimension; lifecycle placement by cost; guard the bar (five bar-lowering moves `:206-212`); ratchets; escalation levels | **new** `0c960d6` 08-08; floor-guard `4be4bb7` 08-28 |
| constraint-driven-development/references/floor-guard.md | 100 | Diff-scoped reference guard: suppressions, stubs, skips, removed assertions, lowered CONSTRAINTS numbers, new exception rows; exit 0/1/2 | `4be4bb7` 08-28 |
| context-engineering | 338 | Context hierarchy; trust levels for loaded files; **Context Budget Management** (trim at 75%, protect task/error, compress before dropping, recency ordering) `:182-223`; confusion management | `a1c8fa9` 08-02, `cc48b69` 08-09 |
| debugging-and-error-recovery | 301 | Stop-the-line; reproduce→localize(bisect)→reduce→fix root cause→guard→verify; non-reproducible tree; error output is untrusted data `:272-279` | stable |
| deprecation-and-migration | 248 | Code is a liability; deprecation decision; advisory vs compulsory; strangler/adapter/flag; **expand/contract DB migrations** with tested down path `:164-190`; zombie code | desc vocab `1483fc1` 08-31 |
| documentation-and-adrs | 289 | ADRs (match existing convention first `:36-44`), why-not-what comments, API docs, README, changelog, docs for agents | `0d52faf`/`a0eba71` 07-15/16 |
| doubt-driven-development | 244 | Fresh-context adversarial review of non-trivial decisions: CLAIM→EXTRACT→DOUBT→RECONCILE→STOP; artifact+contract never the claim; cross-model in read-only sandbox; 3-cycle bound; doubt-theater signal | stable |
| frontend-ui-engineering | 329 | Composition, state ladder, anti-AI-aesthetic table `:118-131`, WCAG **2.1** AA `:165`, responsive, loading/optimistic | stable |
| git-workflow-and-versioning | 356 | Trunk-based; atomic commits; worktrees for parallel agents; change summaries incl. "THINGS I DIDN'T TOUCH"; pre-commit hygiene; semver/tag/changelog contract `:270-311` | desc vocab `b61213f` 08-22 |
| idea-refine | 179 | Divergent→convergent ideation; one-pager with "Not Doing" list (section-check exempt legacy structure) | stable |
| incremental-implementation | 250 | Thin vertical slices; simplicity first; scope discipline; keep compilable; flags; rollback-friendly; do not rerun unchanged commands | stable |
| interview-me | 226 | One question at a time with a guess; hypothesis + confidence number; want-vs-should-want probe; restate; explicit yes; 95% "predict the next three answers" stop | stable |
| observability-and-instrumentation | 239 | Define on-call questions first; signal per question; structured logs + correlation ID + **entry-point field** `:91-104`; RED/USE metrics, cardinality; OTel tracing; symptom-based alerts, two severities, **runbook per alert** `:172-188`; verify telemetry by inducing failure | `cd33117` 07-21, `8714f2b` 08-09, `6a9f2eb` 09-04 |
| performance-optimization | 497 | MEASURE→IDENTIFY→FIX→VERIFY(keep-or-revert, attempt ledger `:368-401`)→GUARD; backend depth: EXPLAIN ANALYZE, pool exhaustion, cache layer/key/invalidation/stampede `:152-366` | `6119908` 07-14; `0ce0107`/`bfc9e32` 08-27; `6a268d7` 08-28 |
| planning-and-task-breakdown | 258 | Plan mode; dependency graph; vertical slicing; task template; sizing XS–XL; single pluggable task-list target `:157-164`; **never overwrite an incomplete plan** `:150-155` | `f18d2c3` 08-12; `8300e1b` 08-28 |
| security-and-hardening | 525 | Threat model first (STRIDE, "trust follows who wrote a value" `:25`); three-tier boundary; OWASP; SSRF+TOCTOU; **destructive-path targets** `:272-278`; dependency triage + install-script gate; **shared-store rate limiting** `:340-352`; secrets; **Data Privacy & Compliance** `:378-397`; LLM Top 10 | `bb53a78` 08-14 privacy; `1458305` 08-31; `45fd4a0` 09-04 |
| shipping-and-launch | 331 | Pre-launch checklist; flag lifecycle; staged rollout with decision thresholds `:142-160`; monitoring; **error-budget release gate** `:238-249`; rollback plan | `dc469a9`/`f0550d8` 07-19/21 |
| source-driven-development | 217 | DETECT→FETCH→IMPLEMENT→CITE against official docs; retrieval safety (fetched docs are data); outbound-endpoint hygiene `:114`; UNVERIFIED flag | `6681f80` 07-21 |
| spec-driven-development | 246 | Gated SPECIFY→PLAN→TASKS→IMPLEMENT; **Phase 0 capability map** with stable module ids `:34-65`; assumptions surfaced; six-area spec; reframe vague asks as success criteria | `cbf37af` 08-09 |
| test-driven-development | 399 | Discover the stack first; RED→GREEN→REFACTOR; Prove-It for bugs; pyramid + sizes; state not interactions; DAMP; real > fake > stub > mock; subagent writes the repro test | `2e49319` 07-19 |
| using-agent-skills | 193 | Meta-router by lifecycle phase; six core operating behaviors; lifecycle sequence of 16 skills | routes to constraints `217feb2` 08-08 |

### 1.2 Slash commands (`commands/*.toml`; mirrored in `.claude/commands/*.md` and `.gemini/commands/*.toml`; parity enforced by `validate-commands.js`)

| Command | Purpose |
|---|---|
| `/build` (`build.toml`) | One task via RED→GREEN→suite→build→commit; `/build auto` requires a spec at a known path, clean `git status`, one unambiguous approval, per-task commits staging only touched files, stop-conditions for irreversible work `:30-40` |
| `/code-simplify` | Behavior-preserving simplification of recent changes; revert on red |
| `/constraints` | Detect → ≤4 questions → write `CONSTRAINTS.md` → install de-facto tools → place by cost → point AGENTS.md at it → verify; sub-commands `check` / `guard` / `ratchet` `:28-31` (new 08-08) |
| `/plan` (`planning.toml`) | Plan mode → dependency graph → vertical tasks → checkpoints → human review; incomplete-plan clobber guard (`78970d5` 08-29) |
| `/review` | Five-axis review; **labels findings Critical / Important / Suggestion** `:14` — inconsistent with the skill's and persona's Critical/Required/Optional/Nit (upstream's own drift; `7cb7a20` fixed the persona, not the command) |
| `/ship` | Fan-out orchestrator: code-reviewer + security-auditor + test-engineer in one turn, main-context merge, GO/NO-GO + mandatory rollback plan; skip fan-out only for ≤2 files/≤50 lines/no auth-payments-data-config `:65-71` |
| `/spec` | Clarify → capability map if multi-capability → six-area SPEC.md → confirm |
| `/test` | TDD for features; Prove-It for bugs; DevTools for browser issues |
| `/webperf` | Quick (source scan, "potential impact") vs Deep (Lighthouse/CrUX/PSI/trace) mode via the web-performance-auditor persona |

### 1.3 Agents / personas (`agents/*.md`, 4)

| Persona | Purpose | Composition rule (all four) |
|---|---|---|
| code-reviewer | Five-axis review, APPROVE/REQUEST CHANGES, severity Critical/Required/Optional/Nit (`7cb7a20` 08-27), "always include at least one positive observation" `:95` | "Do not invoke from another persona" `:102` |
| security-auditor | Trust boundaries + STRIDE first `:106`; six scopes incl. AI/LLM; severity Critical/High/Medium/Low/Info; PoC required for Critical/High | same |
| test-engineer | Level selection; Prove-It; scenario table (happy/empty/boundary/error/concurrency); coverage-gap report | same |
| web-performance-auditor | Quick vs Deep; **metric-honesty rule** ("never fabricate metrics"; label Field/Lab/Trace) `:41-51`; framework detection before framework advice | not in `/ship` fan-out `:183` |

### 1.4 Hooks (`hooks/`)

| File | Event(s) | What it does |
|---|---|---|
| `hooks.json` | `SessionStart` | Runs `session-start.sh` from plugin root or project `.claude/hooks/`; `|| true` never blocks |
| `session-start.sh` | SessionStart | Injects the whole `using-agent-skills/SKILL.md` as `additionalContext` in the standard envelope (`abfb0b3` 08-08); jq-missing fallback |
| `sdd-cache-pre.sh` / `sdd-cache-post.sh` (opt-in, `SDD-CACHE.md`) | `PreToolUse`/`PostToolUse` on `WebFetch` | URL-keyed cache revalidated by HTTP `ETag`/`Last-Modified`; **hit = exit 2 with body on stderr** (a tool error the agent is told to read as content) `sdd-cache-pre.sh:82-105` |
| `simplify-ignore.sh` (opt-in, `SIMPLIFY-IGNORE.md`) | `PreToolUse Read`, `PostToolUse Edit|Write`, `Stop` | Rewrites files **on disk** replacing `simplify-ignore-start/end` blocks with `BLOCK_<hash>` placeholders; expands on edit; restores on Stop `:176-302` |
| `session-start-test.sh`, `simplify-ignore-test.sh` | — | Bash tests for the two hooks |

### 1.5 References (`references/*.md`, 7; per-skill `references/` for floor-guard)

| File | Lines | Purpose |
|---|---|---|
| accessibility-checklist.md | 160 | WCAG **2.1** AA quick checks (still 2.1 at `:3`) |
| definition-of-done.md | 67 | Standing project-wide DoD vs per-task acceptance criteria; includes "human has reviewed and approved before merge or deploy" `:51` |
| observability-checklist.md | 92 | On-call questions first; logs/metrics/traces/alerts/dashboards; **pre-launch gate** (≥1 symptom alert with runbook, test-fired) `:82-90` |
| orchestration-patterns.md | 370 | Five endorsed patterns (direct, single-persona command, parallel fan-out+merge, user-driven sequential, research isolation); Claude Code mapping (subagents cannot spawn subagents); **Agent Teams competing-hypothesis worked example** `:174-278`; four anti-patterns |
| performance-checklist.md | 236 | CWV targets; TTFB; frontend/backend; **query plans, index strategy, pooling, caching patterns, stampede** (`0ce0107` 08-27) |
| security-checklist.md | 245 | STRIDE start; pre-commit; auth/authz; input incl. **destructive path operations worked example** `:68-105` (`45fd4a0` 09-04); install-script gate matrix per package-manager version `:155-179`; LLM Top 10 |
| testing-patterns.md | 235 | JS/TS-specific Jest/RTL/Supertest/Playwright patterns |

### 1.6 Eval framework (`evals/`, `scripts/run-evals.js`) — three tiers (`evals/README.md:14-22`)

| Tier | What | Runs | Mechanism |
|---|---|---|---|
| 1 Structural | frontmatter, kebab name, description ≤1024 with a `Use when` trigger (negated forms rejected), required sections outside fenced blocks, validator-owned exemption allowlist, dead cross-skill refs, **workflow-step ↔ process-section consistency** (`6a268d7` 08-28) | CI | `validate-skills.js` → `lib/skill-lint.js`; plus `validate-commands.js` (3-dir parity), `validate-artifact-paths.js` (SPEC/plan/todo path drift), `validate-reference-links.js`, `validate-versions.js` (all five manifests == `git describe --tags`) |
| 2 Trigger & routing | every skill has `evals/cases/<skill>.json` with ≥3 positive / ≥2 negative / ≥1 behavioral; positives rank top-k (default 3) by **stemmed TF-IDF over name×2 + description**; negatives must not rank #1 and a declared `owner` must outrank; pairwise description cosine ≥0.75 error / ≥0.50 warn; `--min-rank1 95` ratchet | CI | `run-evals.js:60-384` |
| 3 Behavioral | each `evals[]` runs through headless `claude -p --output-format stream-json --permission-mode acceptEdits --allowedTools …` in a throwaway git repo materialized from `evals/fixtures/` (baseline commit + optional `.eval/working-tree.patch`); a second `claude -p` grades the trace against `expectations[]` (trace fenced as untrusted, passed on stdin); `kind: dialogue` for conversation-shaped skills; **pressure fixtures** (time / sunk-cost / authority) | on demand | `run-evals.js:386-560`; results to gitignored `evals/results/` |

Case-file census at HEAD (computed): 88 positive prompts, 100% rank-1; 25 case files; 3 dialogue-kind skills (constraint-driven ×3, idea-refine, interview-me); pressure fixtures wired into `incremental-implementation` eval 2 (`evals/fixtures/incremental-implementation-pressure/scenario.md`) and present for `shipping-and-launch` (`authority-pressure.md`) and `debugging-and-error-recovery` (`time-pressure.md`). Append-only rejected-change ledger at `evals/skill-impact.md` (`125b1f8` 09-02; CONTRIBUTING pre-flight step 3 points at it).

### 1.7 Governance files worth knowing

`CLAUDE.md` / `AGENTS.md` (repo-scoped, "do not copy into other projects"), `.claude/rules/skills-contributing.md` (path-scoped anti-duplication rule for `skills/**`), `CONTRIBUTING.md#before-proposing-a-new-skill` (catalog search, open-PR check, rejected-ledger check, anatomy fit, justify the gap), `docs/skill-anatomy.md` (SKILL.md ≤500 lines `:125`; supporting file only >100 lines `:103`).

---

## 2. Timeline since 2026-07-13

### 2.1 Releases

| Tag | Date | Substantive content |
|---|---|---|
| 0.6.4 | 07-12 | (baseline before the window) |
| 0.6.5 | 07-24 | perf Step 4 keep-or-revert (`6119908` 07-14); ADR convention-matching (`0d52faf`, `a0eba71`); validator rejects fenced headings and negated triggers (`f25f467`); skill-gap issue form; TDD ecosystem-neutral (`2e49319`); SDD retrieval safety + outbound-endpoint hygiene (`dee22bf`, `6681f80`); catalog-wide ecosystem-neutral commands (`45ccfb6`); shipping SLO/error-budget section (`dc469a9` 07-19, trimmed to a release gate `f0550d8` 07-21); observability runbook guidance (`cd33117`, author 07-21 / committed 08-09) |
| 0.6.6 | 08-03 | context-engineering Context Budget Management (`a1c8fa9` 08-02); shipping ↔ observability cross-refs (`cca4df5`); Command Code provider; plugin `agents` key removed so Claude Code loads the four personas (`366beec`) |
| 0.6.7 | 08-14 | **constraint-driven-development** skill + `/constraints` in all three command dirs (`0c960d6`, `7cfb06d` 08-08); "give each dimension a tool" (`127bd99`); spec Phase 0 capability map (`cbf37af` 08-09); planning single pluggable task-list target (`f18d2c3` 08-12); api idempotency-key guidance (`ce89b03` 08-12); eval grader rejects incomplete results (`c848333`); TDD behavioral case made discriminating (`b8eca04`); `--behavioral` path-traversal guard (`4b3122e`); reference-link CI gate + artifact-path validator (`b293c02`, `ce5e12b`); SessionStart standard envelope (`abfb0b3`); **Data Privacy & Compliance** section (`02ba241` author 06-27, merged `bb53a78` 08-14); observability runbook fixes (`8714f2b`); lost-in-the-middle correction (`cc48b69`) |
| 0.6.8 | 08-28 | **floor-guard reference implementation** (`4be4bb7`); **never overwrite an incomplete plan** (`8300e1b`, #518); perf missing-guard step + workflow-step lint (`6a268d7`); **perf backend/DB depth** (`0ce0107`, `bfc9e32` 08-27); code-reviewer severity aligned to skill (`7cb7a20`); allowed-tools semantics corrected (`485cd8e`); validator `Object.hasOwn` fix (`c59c4b4` 08-21); git-workflow PR vocabulary (`b61213f` 08-22) |
| 0.6.9 | 09-04 | **shared-store rate limiting** (`1458305` 08-31); db-migration + dependency-audit vocabulary in two descriptions (`1483fc1` 08-31); rejected skill-change ledger (`125b1f8` 09-02); **destructive-path targets: allowlist, depth floor, owner check** (`45fd4a0` 09-04); **observability entry-point attribution** (`6a9f2eb` 09-04); incomplete-plan guard mirrored across command dirs (`78970d5` 08-29); antigravity command-wrapper limitation doc (`cd8922b`) |
| post-0.6.9 | 09-05 | lifecycle session handoffs doc (`878d5d4`, #513: artifacts are the handoff; re-run checks proportional to what moved); copilot CLI docs (`f7fe1a4`) |

### 2.2 Detail since 2026-08-28 (what an adopter must re-read)

| Commit | Date | Change | Consequence for orca-fleet |
|---|---|---|---|
| `4be4bb7` | 08-28 | `references/floor-guard.md`: diff-scoped guard over merge-base + untracked files; five moves; exit 0 clean / 1 violation / 2 cannot-run; "never let a 2 read as a 0"; `.constraintsignore`; CONSTRAINTS.md is canonical over package.json scripts; floor-only first run; CI-only option for machine-wide tools | floor-it GUARD (`SKILL.md:78-82`) has no script; see §4.3 |
| `8300e1b` + `78970d5` | 08-28/29 | Never overwrite `tasks/plan.md`/`tasks/todo.md` holding unchecked tasks for different work; stop and ask; never bulk-close another plan's tracker items | No orca analogue for a ledger/DAG belonging to another incomplete run; see §6 item 9 |
| `6a268d7` | 08-28 | perf eval expects a concrete GUARD; skill-lint now errors when a "## The X Workflow" block declares numbered steps without a matching process section | `validate.py` has no pipeline-phase ↔ composed-playbook consistency check; §4.5 |
| `0ce0107` / `bfc9e32` | 08-27 | EXPLAIN ANALYZE before indexing; composite column order; four when-an-index-won't-help cases; one pool per process, proxy for serverless; cache layer table, key includes every response input, one invalidation strategy, stampede coalescing; `references/performance-checklist.md` +83 lines | `risk-review.md:44-47` perf lens is web/CWV-shaped; "cache key omits the viewer" is a correctness/security finding the lens does not name; §3.1 row 18 |
| `7cb7a20` | 08-27 | code-reviewer persona severity = skill's Critical/Required/Optional/Nit; `/review` command still says Critical/Important/Suggestion | orca's `acceptance-review.md:36` taxonomy already matches the skill; no action |
| `1458305` | 08-31 | In-memory rate limiter in front of >1 instance is a finding; Upstash example | **Adopted** `risk-review.md:34-36` (#250) |
| `1483fc1` | 08-31 | Descriptions gain "migrating a database schema in production … expand/contract" and "auditing dependencies … supply-chain risk" | Routing vocabulary only |
| `125b1f8` | 09-02 | `evals/skill-impact.md` append-only ledger of proposals rejected on eval evidence; CONTRIBUTING pre-flight step 3 | orca-fleet has anti-adoption lists scattered across three research docs; no single ledger; §4.7 |
| `45fd4a0` | 09-04 | Destructive-path section + checklist worked example; two stated limits (marker is self-attestation; check/use race) | **Adopted** `risk-review.md:36-41` + `sandbox-policy.md:75-79` (#250) — the two limits (marker self-attestation, TOCTOU on ancestor swap) are not carried; §3.1 row 20 |
| `6a9f2eb` | 09-04 | Stamp `entryPoint` next to the correlation ID when scheduler/replay/CLI write to one log; propagate both; `entryPoint` not `source` (ECS collision) | orca has no observability doctrine to carry it; note it is directly relevant to the fleet's own ledger/DECISIONS lines (which coordinator/worker/entry wrote a row) |
| `878d5d4` | 09-05 | Cross-session handoff: artifacts carry the work; re-run checks proportional to what changed; "treat a recorded 'tests pass' as a claim about a specific baseline" | Weaker restatement of `ledger-contract.md:67-86` CONTEXT HANDOFF + `liveness-resume.md:116-123` anti-inflation; nothing to adopt |

---

## 3. Adoption matrix

Statuses: **ADOPTED-CURRENT** (orca-fleet carries the current upstream content or a stronger equivalent) · **ADOPTED-STALE** (adopted, but upstream moved since) · **NOT-ADOPTED** (relevant, absent) · **DELIBERATELY-EXCLUDED** (a documented decision) · **NOT-APPLICABLE** (ingredient/host-specific; nothing to adopt). Anchors are `file:line` on both sides or "none".

### 3.1 Skills

| # | Upstream skill (anchor) | Status | orca-fleet anchor | Evidence / delta |
|---|---|---|---|---|
| 1 | api-and-interface-design — api-contract lens content `:125-144, 338-350`; idempotency `:156-215, 363-367` | **ADOPTED-STALE** | `playbooks/risk-review.md:53-55` (api-contract lens: breaking-change check, versioning path, consumer-compat evidence) | Lens added by #250 covers Hyrum/additive-only/error-shape drift. Idempotency-key implementation (08-12) — "SELECT then INSERT is a race" `:347`, payload-hash reuse `:349`, retention shorter than longest redelivery path `:350` — is absent from every lens. Quote upstream `:213`: "Every call has three outcomes, not two: success, failure, and _unknown_." No orca line. |
| 2 | browser-testing-with-devtools `:60-107` security boundaries; workflows `:109-182` | **DELIBERATELY-EXCLUDED** (skill) / **NOT-ADOPTED** (browser-worker security rules) | `playbooks/runtime-prove.md:21-25` (drive true entry points); `observe.md:11-16` (screenshots, console); `sandbox-policy.md:84-92` (data never instructions) | The generic trust boundary covers "browser content is data". Not carried: profile isolation ("Default to the dedicated profile or `--isolated`" `:67`), "No credential access … cookies, localStorage tokens" `:88`, "User confirmation for mutations" `:90`. observe.md and field-test-it drive browsers/devices with no such rule. |
| 3 | ci-cd-and-automation | **DELIBERATELY-EXCLUDED** | `skills/floor-it/SKILL.md:75-77` (ENFORCE: CI jobs on BASE, cheapest first, canary PR RED) | Pipeline building is floor-it's ENFORCE unit; bot feedback loop is `dispatch-lifecycle.md:72-97`; staged rollout is `release.md`. "No gate can be skipped" `:54` → floor-it anti-patterns `:113-115`. Nothing pending. |
| 4 | code-review-and-quality `:22-87, 181-187, 292-298` | **ADOPTED-CURRENT** | `playbooks/acceptance-review.md:16-26` (axes), `:36` (Critical/Required/Nit/Optional/FYI), `build-change.md:25-27` (PR sizing seam ≤~400 lines, field-validated), `modernize-it/SKILL.md:51-62` (one dep per PR, changelog, lockfile regenerated) | orca's taxonomy matches the upstream skill and the 08-27 persona fix. Upstream `:126` "Separate refactoring from feature work" = `build-change.md:20-21`. Divergence by design: orca's axes are three fresh workers (standards/spec/test-adequacy) + scope-gated lenses, not five axes in one reviewer. |
| 5 | code-simplification `:30-103, 157-171` | **ADOPTED-CURRENT** (as lens) / **DELIBERATELY-EXCLUDED** (as outcome) | `playbooks/risk-review.md:56-58` (simplification lens, advisory) | "Rule of 500" `:171` and Chesterton's Fence `:107-121` are worker-side ingredients. reshape-it owns structural erosion; a simplification *sweep* fails the identity test (§5.9). |
| 6 | constraint-driven-development `:36-262` | **ADOPTED-CURRENT** (mission) with four **NOT-ADOPTED** parts | `skills/floor-it/SKILL.md:1-130`; `docs/research/2026-09-09…md §4.2` | Adopted and strengthened: PROVE-FIRES injection (`floor-it:63-73`, no upstream analogue), canary PR (`:75-77`), one-way freeze that PARKS headless (`:58-62`) vs upstream `:38` "apply the Floor … and flag the rest". Not adopted: (a) `references/floor-guard.md` as a script (`floor-it:78` names it as doctrine); (b) ratchet table "Measured, not yet enforced … today's value, direction" `:126-131, 226-232` — floor-it DETECT measures (`:51-54`) but the ratchet direction row is not a frozen-table column; (c) "at least one external constraint" `:218-224` — no floor-it line; (d) exceptions with owner + expiry `:133-137, 247` — floor-it uses DECISIONS waivers (`:80-81`) with no expiry. |
| 7 | context-engineering `:182-223` budget; `:98-103` trust levels | **DELIBERATELY-EXCLUDED** (ingredient) / one **NOT-ADOPTED** detail | `runtime/ledger-contract.md:67-86` (CONTEXT HANDOFF), `liveness-resume.md:92-96`; `sandbox-policy.md:84-92` | Fresh context per worker + ledger-as-memory makes the hierarchy moot. Not adopted: a numeric compaction trigger ("Start trimming at 75% capacity" `:186`) — orca fires on "degraded recall, lost handles, uncertainty" (`ledger-contract.md:69`), a symptom, not a threshold; and recency ordering for dispatch preambles ("put the most task-critical content last" `:218`) — `decompose-dag.md:17-21` specifies TASK contents, not order. |
| 8 | debugging-and-error-recovery `:21-170, 272-279` | **ADOPTED-CURRENT** | `playbooks/diagnose.md:3, 16-41`; `skills/root-cause/SKILL.md:44-58`; `deflake-it/SKILL.md:51-54` (non-reproducible taxonomy) | Stop-the-line, bisect, root-cause-not-symptom, error text untrusted all present. "Safe Fallback Patterns" `:214-241` (swallow-and-warn) deliberately not carried — it is exactly the "empty catch" floor-guard flags. |
| 9 | deprecation-and-migration — schema `:164-190`; sunset `:37-118, 192-202` | **ADOPTED-CURRENT** (schema half) / **NOT-ADOPTED** (sunset half) | `risk-review.md:50-52`; `modernize-it/SKILL.md:29-33, 63-67, 90-91`; `decompose-dag.md:12-13` | Expand/contract, tested down path, no rename-in-place, separate deploys: all present. The deprecation decision `:39-56`, advisory vs compulsory `:58-65`, churn rule `:106`, remove-old-system `:108-118`, zombie code `:192-202` have no owner (§5.2). |
| 10 | documentation-and-adrs `:23-100` ADRs incl. convention match `:36-44`; `:200-248` README/changelog | **NOT-ADOPTED** (ADR protocol) / **ADOPTED-CURRENT** (changelog + doc-sync) | `decide-and-freeze.md:24-25` ("an ADR only when hard-to-reverse ∧ surprising ∧ a real trade-off"); `release.md:24-31` (changelog, doc-sync unit) | orca decides *when*; upstream's *how* (inspect `.adr-dir`, continue numbering, reuse headings, never delete/supersede `:93-100`) is absent — a fleet writing ADRs into a repo with an existing convention will create a second scheme. §6 item 4. |
| 11 | doubt-driven-development `:49-191` | **ADOPTED-CURRENT** | `playbooks/runtime-prove.md:7-17` | Artifact+contract not claim `:106` = `runtime-prove:9-11`; 3-cycle bound `:184-191` = `:11`; doubt-theater `:215` = `:13-14`; cross-model read-only sandbox `:143-151` + non-interactive skip-and-announce `:161-164` = `:15-17`. Upstream `:47` degraded self-review fallback correctly not adopted (§7.2). Unchanged upstream since June. |
| 12 | frontend-ui-engineering `:118-131, 165-240` | **ADOPTED-CURRENT / ahead** | `risk-review.md:48-49` (WCAG 2.2 AA + target-size + focus-appearance; anti-AI-aesthetic); `skills/access-it` | Upstream skill `:165` and `references/accessibility-checklist.md:3` are still WCAG 2.1. Component/state/loading patterns are worker-side. |
| 13 | git-workflow-and-versioning `:34-119, 191-209, 270-311` | **ADOPTED-CURRENT** | `dispatch-lifecycle.md:104-108`; `build-change.md:20-27`; `release.md:24-31` | Atomic bisectable commits, "THINGS I DIDN'T TOUCH" = NOTICED-BUT-NOT-TOUCHED, gitleaks before push, semver bump + tag + curated changelog. Worktrees are the Orca substrate. |
| 14 | idea-refine | **DELIBERATELY-EXCLUDED** | `skills/map-it/SKILL.md:43-51` (fog-of-war, Prototype tickets); `decide-and-freeze.md:35-36` (explicit NOT-in-scope) | Divergent/convergent + "Not Doing" are covered by map-it + freeze boundaries. |
| 15 | incremental-implementation `:23-42, 89-181, 199-211` | **ADOPTED-CURRENT** | `build-change.md:3, 13-29, 39-42` | Slices, scope discipline, clean baseline, rollback-friendly commits, ">100 lines before a test run" and "same command twice" red flags all present. |
| 16 | interview-me `:40-138` | **NOT-ADOPTED** (matt grilling is the recipe) | `decide-and-freeze.md:13-26` (round-by-round with recommended answer) | Cheap additions with no orca line: hypothesis + confidence number before the first question `:42-51`; "if you didn't have to justify this to anyone…" probe `:90`; explicit-yes gate rejecting "whatever you think" `:117-122`; the checkable stop "can I predict the next three answers?" `:126-132`. Grilling rounds already conflict with `:64-68` "one at a time, not a batch" — orca chose rounds for auto-pick; keep rounds. |
| 17 | observability-and-instrumentation (all) | **NOT-ADOPTED** | none (`observe.md` is canary; `field-test-it` logs are artifacts) | No structured-log, RED, correlation-ID, symptom-alert, runbook, or test-fire doctrine anywhere. ship-it can reach `DEPLOYED_AND_VERIFIED` with zero instrumentation on the new path. §4.4, §5.3, §6 item 1. |
| 18 | performance-optimization — Step 4 `:368-401`; Step 5 `:403-439`; backend `:152-366` | **ADOPTED-CURRENT** (Step 4/5) / **ADOPTED-STALE** (backend depth) | `skills/speed-it/SKILL.md:37-42, 54, 61-68`; `risk-review.md:44-47` | Keep-or-revert precedence (WORSE→revert, NEUTRAL→revert, IMPROVEMENT→land) and the attempt ledger landed in #250 + `c576804`. GUARD at declared budget = Step 5 synthetic; field p75 monitoring is handed to ship-it observe. Not carried into the perf lens: EXPLAIN-before-index `:154-185`, "cache key omits the viewer → one user's data served to another" `:354, 467`, pool-size-as-fix `:187-202`. |
| 19 | planning-and-task-breakdown `:23-123, 143-164, 213-219`; clobber guard `:150-155` | **ADOPTED-CURRENT** / one **NOT-ADOPTED** | `decompose-dag.md:5-13, 15-25, 36-50, 57-65` | Vertical slices, dependency-first, checkpoints (wave gates), plan skeptic (orca addition). Clobber guard (08-28): orca has `liveness-resume.md:103` "FREEZE-check: no other live coordinator" for *resume*, nothing for *starting a new run over a ledger with unmet flags*. |
| 20 | security-and-hardening `:21-40` threat model; `:272-278` destructive paths; `:340-352` rate limit; `:378-397` privacy; `:399-425` LLM; `:307-318` supply chain | **ADOPTED-CURRENT** (all but privacy) / **ADOPTED-STALE** (privacy rules; two destructive-path limits) | `risk-review.md:32-43`; `harden-it/SKILL.md:45-63`; `modernize-it:57-60`; `sandbox-policy.md:61-82, 84-92` | Previous audit's three stale items: destructive-path → **fixed** (`risk-review:36-41`, extended to DB/cloud targets — an orca addition); rate-limit → **fixed** (`:34-36`); privacy operating rules → **still missing** (classify fields; purpose; TTL + deletion incl. backups/caches/indexes; export/delete rights; consent for third-party/LLM sharing; localized defaults). Also missing from the destructive-path adoption: upstream `:278` "a marker inside the tree is self-attestation" and the check/use race on ancestor swap — orca's text (`:36-41`) stops at "read ownership evidence first". |
| 21 | shipping-and-launch `:77-160` rollout; `:238-249` error budget; `:251-278` rollback | **ADOPTED-CURRENT** (rollout/rollback) / **NOT-ADOPTED** (error-budget gate; monitoring setup) | `release.md:40-47`; `observe.md:9-21` | observe alerts on change-vs-baseline with 2-consecutive confirmation (gstack); upstream's numeric advance/hold/rollback table `:146-151` and burn-rate hold `:249` have no orca line. "Budget exhausted → freeze feature work" `:245` is a release-gate input orca's PROMOTION_READY does not read. |
| 22 | source-driven-development `:27-179` | **NOT-ADOPTED** (protocol) / **ADOPTED-CURRENT** (retrieval safety) | `decide-and-freeze.md:8-9` ("load-bearing external deps are real and installable — research, don't assume"); `map-it/SKILL.md:27-28` (fetched sources are data) | No CITE step, no `UNVERIFIED` flag `:173-177`, no outbound-endpoint surfacing `:114` in `build-change.md`. Cheap: one bullet in build-change's per-unit contract for framework-specific code. |
| 23 | spec-driven-development `:34-65` Phase 0; `:67-163` Specify; `:204-211` living spec | **ADOPTED-CURRENT** | `decide-and-freeze.md:6-43`; `decompose-dag.md:9-13` (FOUNDATION set); `sandbox-policy.md:61-82` (Always/Ask/Never) | Capability map ≈ foundation set + slice↔task-id table with stable ids (`decompose-dag:22`). "Reframe as success criteria" `:150-162` = testable AC per capability (`decide-and-freeze:41-43`). |
| 24 | test-driven-development `:24-34, 40-142, 343-357` | **ADOPTED-CURRENT** (via matt) | `build-change.md:3, 16-19`; `remediate-finding.md:9-13`; `root-cause/SKILL.md:51-55`; `prove-it:47-57` | Prove-It = red repro first; "discover the stack first" = "the repository's own command" in every convergence proof; subagent-writes-the-repro-test ≈ root-cause specifying the regression test for a separately authorized fix. REFACTOR-in-loop is the documented router conflict (`AGENTS.md:78-79`). |
| 25 | using-agent-skills `:14-43` router; `:45-114` behaviors; `:141-162` sequence | **DELIBERATELY-EXCLUDED** (router) / **ADOPTED-CURRENT** (behaviors) | `AGENTS.md:74-82` (one router per worker); `gate-classification.md:74-78` (user-challenge = "push back"); `build-change.md:20-21` (scope discipline); `evidence-manifest.md:1-10` (verify, don't assume) | Injecting it at SessionStart (hook) is not adopted; §4.1. |

### 3.2 Commands

| Command | Status | orca anchor | Note |
|---|---|---|---|
| `/build` incl. `auto` `:26-40` | ADOPTED-CURRENT | `build-change.md:5-11, 13-29` | Spec-required, clean baseline, stage only touched files, stop on irreversible → plan gate. orca's approval is classified (mechanical/taste/one-way), not "one unambiguous affirmative". |
| `/code-simplify` | DELIBERATELY-EXCLUDED | `risk-review.md:56-58` | Lens, not a command. |
| `/constraints` (+ `check`/`guard`/`ratchet`) `:28-31` | ADOPTED-CURRENT (partial) | `floor-it/SKILL.md:51-84` | `check` = PROVE-FIRES/ENFORCE; `guard` = GUARD (doctrine); `ratchet` has no orca operation. |
| `/plan` | ADOPTED-CURRENT / clobber guard NOT-ADOPTED | `decompose-dag.md` | see row 19 |
| `/review` | ADOPTED-CURRENT | `skills/review-it`, `acceptance-review.md` | Upstream command's Critical/Important/Suggestion `:14` is upstream's own inconsistency; do not import. |
| `/ship` fan-out `:8-37` | ADOPTED-CURRENT (topology) / DELIBERATELY-EXCLUDED (same-context merge) | `dispatch-lifecycle.md:51-53` (coordinator dispatches axes, one worker each); `acceptance-review.md:25-26` (aggregate side by side, no cross-rerank) | §7.1. |
| `/spec` | ADOPTED-CURRENT | `decide-and-freeze.md` | — |
| `/test` | ADOPTED-CURRENT | `build-change.md`, `remediate-finding.md` | — |
| `/webperf` quick/deep `:8-16` | ADOPTED-CURRENT (mission) / NOT-ADOPTED (lens labeling) | `speed-it/SKILL.md:37-42` | The per-diff perf lens (`risk-review:44-47`) reviews source without measurement and should label findings "potential impact" per `web-performance-auditor.md:41-51`; it does not. |

### 3.3 Agents

| Persona | Status | orca anchor | Note |
|---|---|---|---|
| code-reviewer | ADOPTED-CURRENT | `acceptance-review.md:16-26, 36` | "Always include at least one positive observation" `:95` not adopted — correct (§7.6). |
| security-auditor | ADOPTED-CURRENT | `risk-review.md:32-43`; `harden-it:45-61` (PoC scenario written, routed, then executed under profile) | Severity Critical/High/Medium/Low/Info vs orca P0/P1 classes — orca's harden-it does not define P2+ handling; upstream's "Fix in current sprint / next sprint" rows have no orca terminal. Minor. |
| test-engineer | ADOPTED-CURRENT | `acceptance-review.md:23` (test-adequacy axis); `prove-it` | — |
| web-performance-auditor | ADOPTED-CURRENT (metric honesty) / NOT-ADOPTED (lens mode labeling) | `speed-it:41-42` "never fabricate a metric"; `risk-review:44-47` | see `/webperf` row |

### 3.4 Hooks

| Hook | Status | orca anchor | Note |
|---|---|---|---|
| `hooks.json` SessionStart → meta-skill injection | NOT-ADOPTED | `hooks/hooks.json:4-25` (TaskCompleted + Stop → `verify-gate.sh`) | Different purpose. §4.1 |
| `sdd-cache-*.sh` | NOT-ADOPTED | none | Relevant only to map-it research workers / a future source-driven step; exit-2-as-content is host-specific. |
| `simplify-ignore.sh` | DELIBERATELY-EXCLUDE (recommended) | none | §7.3 — conflicts with build-blind review and `verify.py` symbol-on-base. |
| `session-start-test.sh`, `simplify-ignore-test.sh` | NOT-APPLICABLE | `tests/test_verify_gate.py` | orca already tests its hook script. |

### 3.5 References

| Reference | Status | orca anchor | Note |
|---|---|---|---|
| accessibility-checklist (2.1) | NOT-APPLICABLE (orca ahead) | `risk-review:48`, `access-it` (2.2) | — |
| definition-of-done | ADOPTED-CURRENT (stronger) | `evidence-manifest.md:136-153` (§3 floor scoped by mission class) | Upstream `:51` "human has reviewed and approved before merge" = orca `lit` default (`gate-classification:48-57`). |
| observability-checklist incl. pre-launch gate `:82-90` | NOT-ADOPTED | none | §6 item 1 |
| orchestration-patterns `:9-115, 282-340` | ADOPTED-CURRENT (five patterns, depth-1) / DELIBERATELY-EXCLUDED (Agent Teams peer debate `:174-278`) | `ARCHITECTURE.md:11-29`; `dispatch-lifecycle.md:51-53`; `docs/research/2026-07-15…md D7` | root-cause's "competing-hypothesis debate" (`root-cause:28-29, 49-50`) is coordinator-mediated (one adversarial worker or two workers with a falsification table) — compatible with D7. Do not import the teammates-message-each-other form. |
| performance-checklist | ADOPTED-STALE | `risk-review:44-47`, `speed-it` | Backend/query-plan/cache checklist (08-27) not carried. |
| security-checklist `:21-28, 66-105, 142-187` | ADOPTED-CURRENT (mostly) | `risk-review:32-43`; `modernize-it:57-60` (install scripts disabled until provenance verified) | The per-manager install-script policy matrix `:166-177` is worker-side reference; orca's rule is manager-neutral. |
| testing-patterns (JS/TS) | NOT-APPLICABLE | — | Worker-side. |

### 3.6 Eval framework and validators

| Upstream | Status | orca anchor | Delta |
|---|---|---|---|
| Tier 1 `validate-skills.js` / `skill-lint.js` | ADOPTED-CURRENT (orca ahead in most rules) / two NOT-ADOPTED rules | `scripts/validate.py:96-104` (budgets), `:394-437` (byte caps), `:486-593`; `tests/test_architecture.py` | orca adds three-layer separation, cross-doc refs, proof status, badge freshness. Missing: workflow-step ↔ section consistency (`skill-lint.js:212-233` — orca has no check that a mission's Pipeline block names only phases whose playbooks are composed) and exemptions-in-validator-not-frontmatter (`:53-60, 179-187`) — orca's `proof:` frontmatter is worker-editable by design but validated against on-disk evidence, a different but equivalent guard. |
| Tier 2 `run-evals.js:196-384` | ADOPTED-STALE (design) | `scripts/eval.py:27-108, 279-316`; `evals/routing.json` (43 cases); `tests/test_evals.py` (0.95 floor) | See §4.2 concrete comparison. |
| Tier 3 `run-evals.js:386-560` + fixtures + pressure cases | NOT-ADOPTED | `skills/*/evals/evals.json` (17 files, `assertions[]` never executed; `eval.py:184-221` schema only) | `docs/research/2026-09-09…md §5` deliberately excluded Tier 3 *as a mission*; as catalog tooling it was never built. |
| `validate-commands.js` | NOT-APPLICABLE | — | Single host (Claude Code plugin); no parallel command dirs. |
| `validate-artifact-paths.js` | ADOPTED-CURRENT (analogue) | `validate.py` cross-doc `<name>.md` resolution (`AGENTS.md:102-108`) | Different artifact class, same guarantee. |
| `validate-reference-links.js` | ADOPTED-CURRENT | same | — |
| `validate-versions.js` (5 manifests == `git describe --tags`) | ADOPTED-CURRENT (partial) | `tests/test_docs_navigation.py:29` (plugin.json == CHANGELOG heading) | No tag check; orca's release process (`release.md:24-26`) classifies version state instead. |
| `evals/skill-impact.md` rejected ledger | NOT-ADOPTED | `docs/research/*` anti-adoption lists (three files) | §4.7 |

### 3.7 Re-check of the previous audit's two stale lenses against HEAD

| Previous-audit row (2026-09-09 §2.3) | #250 commit `0f6ced7` | HEAD state | Verdict |
|---|---|---|---|
| Security lens missing destructive-path target validation (`45fd4a0`) | `risk-review.md` +5 lines (diff hunk `@@ -29,17 +31,28 @@`); `sandbox-policy.md` +3 | `risk-review.md:36-41`; `sandbox-policy.md:75-79` | **Fixed**, extended to DB/cloud targets. Two upstream caveats (marker self-attestation; check/use race) not carried. |
| Security lens missing shared-store rate-limit red flag (`1458305`) | same hunk | `risk-review.md:34-36` | **Fixed** |
| Security lens missing Data Privacy & Compliance rules (`bb53a78`) | **not in the diff** (grep of the commit: no privacy/PII/retention) | none anywhere | **Still stale.** The previous audit listed it; #250's commit message enumerates rate-limit + destructive-path only. |
| Perf lens missing Step 4 neutral-is-revert + attempt ledger | `risk-review.md:44-47` +2 lines; `speed-it/SKILL.md` +4 lines; `c576804` then fixed precedence (WORSE→revert first, land last) | `risk-review.md:46-47`; `speed-it:61-68` | **Fixed** |

---

## 4. Mechanisms (machine parts) — what, orca equivalent, cost to adopt

### 4.1 Hooks

| Upstream part | What it enforces | orca equivalent | Adoption |
|---|---|---|---|
| `hooks.json` SessionStart → `session-start.sh` | Nothing; injects the 193-line meta-router into every session so routing happens before the first turn | `hooks/hooks.json` wires **TaskCompleted** and **Stop** to `runtime/scripts/verify-gate.sh` — a fail-closed completion gate (`verify-gate.sh:10-11, 66-80, 106-116`), no SessionStart | Injecting `AGENTS.md:23-46` (the intent→mission table, ~25 lines) at SessionStart would be cheap and would address REVIEW.md's routing finding at the host level. Cost: one `SessionStart` entry + a 15-line sh emitting the standard envelope (copy `session-start.sh:20-25`). Risk: `ARCHITECTURE.md:79-83` instruction budget — inject the table, never a SKILL.md. Note REVIEW.md item 4: the symlink install path never loads `hooks.json` at all; a SessionStart hook would have the same limitation. |
| `sdd-cache` Pre/PostToolUse WebFetch | Cross-session doc fetches revalidated by ETag; hit returned as a tool *error* (exit 2, stderr) | none | Low value until a source-driven step exists. The exit-2-as-content convention (`SDD-CACHE.md:76`) is fragile across hosts; do not copy the mechanism, copy the freshness rule (never serve without a validator). |
| `simplify-ignore` Read/Edit/Write/Stop | Hides annotated blocks from the model by rewriting files on disk | none | **Do not adopt** (§7.3). |

### 4.2 Eval framework — `scripts/eval.py` vs `run-evals.js`, concretely

| Dimension | `run-evals.js` (upstream) | `scripts/eval.py` (orca) | What adopting takes |
|---|---|---|---|
| What is scored | The frontmatter `description` (+ name ×2) — the exact text the host router sees (`:104-119`) | `MISSION_TRIGGERS` dict (`:27-108`) — a hand-curated second vocabulary; a description edit changes nothing the eval measures | Replace `MISSION_TRIGGERS` with tokenized descriptions read from `skills/*/SKILL.md`; keep `MISSION_WORD_TRIGGERS` (`:120-122`) only if measured to help |
| Scoring | Stemmed TF-IDF cosine over the whole catalog (`:69-149`) | Substring match weighted by trigger word-count (`:287-296`) + a specialist tie-break (`:306-314`) | ~120 lines of stdlib Python (tokenize/stem/tf/idf/cosine) — the JS is dependency-free and ports directly |
| Negatives | Must not rank #1 **and** a declared `owner` must outrank (`:319-343`) — a pairwise test that cannot pass vacuously | `type: negative` with `expected_mission` (`routing.json`), scored as "predicted == expected" (`:348-350`) — a negative is just a positive for the other mission | Add `owner` (already implied by `expected_mission`) and assert owner-outranks-self by score, not just argmax |
| Collisions | Pairwise description cosine ≥0.75 error / ≥0.50 warn (`:357-372`) | none | 15 lines once TF-IDF exists; orca's 17 dense 1024-char descriptions (`AGENTS.md:95`) are the case this catches |
| Coverage | Every skill must have a case file with ≥3/≥2/≥1 (`:212-218, 347-354`) | Every mission needs ≥1 positive (`:254-256`); per-skill `evals.json` optional (`:188-190`) | Raise the minimum; `test_evals.py:66-74` already requires the file |
| CI gate | `--min-rank1 95` fails the workflow (`test-plugin-install.yml`) | `--threshold` defaults 0.0 (`:459-464`); `validate.yml:28-33` cannot fail on routing (REVIEW.md §2 item 3); only `tests/test_evals.py` `ROUTING_MIN_SCORE = 0.95` gates | Pass `--threshold 0.95` in `validate.yml` |
| Tier 3 | Headless `claude -p` in a throwaway repo from fixtures; grader on stdin; `kind: dialogue`; pressure fixtures; results gitignored (`:386-560`) | `assertions[]` in 17 `evals.json` files are strings nobody executes; no fixtures; no runner | A `--behavioral <mission>` sub-command: materialize a fixture repo, run the coordinator prompt headless with the mission SKILL.md appended, grade the stream-json trace against `assertions[]`. **Doctrine conflict to state explicitly:** orca never grades *completion* on a trace (`ARCHITECTURE.md:44-56`); a *catalog eval* grading a trace for "did the coordinator freeze before decomposing" is a different question and is legitimate — but the runner must not be presented as proof status (`proof:` stays run-report-based). Pressure cases (`authority-pressure.md`, `scenario.md`) map directly onto orca gates: "mark the release GO despite the failing e2e" is a one-way-gate test. |

### 4.3 Floor guard (`constraint-driven-development/references/floor-guard.md`)

What it does: reads `git diff --unified=0 <merge-base>` plus untracked files (`:38-43`), flags added suppressions / stubs / skips / new `CONSTRAINTS.md` exception rows, removed `expect|assert|should` lines in test files, and any `CONSTRAINTS.md` number that went down (`:56-86`); exit 0/1/2 with "never let a 2 read as a 0" (`:11`); reports rule + location, never a matched secret (`:12`).
orca equivalent: doctrine only — `floor-it/SKILL.md:78-82` ("any diff that lowers a threshold … or touches a dimension's frozen tool-config surface … fails without a recorded DECISIONS waiver"); `acceptance-review.md:23` test-adequacy axis judges assertion removal by LLM; `prove-it:71` "No assertion weakened to pass (diff-audit)" — also LLM-judged.
Adoption: port to `runtime/scripts/floor_guard.py` (stdlib; ~120 lines + `tests/test_floor_guard.py`), same exit contract, plus orca's DECISIONS-waiver exemption instead of `.constraintsignore`. Three consumers: (1) floor-it GUARD unit (the script *is* the reviewed CI unit); (2) `verify.py` — a mutation manifest whose diff trips `test-made-easier` or `assertion-removed` fails the negative-control leg deterministically before any LLM review (this closes one of REVIEW.md's "worker-written text file is sufficient" bypasses partially: a `.skip` cannot hide behind a forged `negctrl.txt`); (3) acceptance-review's test-adequacy axis gets a mechanical pre-check. Caveat: the guard is "regex-shallow … catches the cheap road to green, not a determined human" (`:99`); it must stay a floor under review, not a replacement.

### 4.4 Runbook / alert doctrine (`observability-and-instrumentation/SKILL.md:154-197`; `references/observability-checklist.md:82-90`)

What it enforces: every alert symptom-based, actionable, threshold justified by SLO/history, two severities, **linked to a runbook** (`docs/runbooks/<alert>.md`, three lines minimum: means / first check / escalate), **test-fired once**, and an induced staging failure diagnosed from telemetry alone.
orca equivalent: none. `release.md:40-47` DEPLOYED_AND_VERIFIED and `observe.md` watch a canary window; nothing requires the new path to be observable or that on-call can act on it.
Adoption: a playbook (§6 item 1) composed by ship-it between LAND and PROMOTION_READY for units that add I/O/retries/queues/external calls (the trigger list at `observability-and-instrumentation:213`), and a `release.md` PROMOTION_READY line: "at least one symptom-based alert with runbook, test-fired" — parking as `CODE_CLOSED` + `VERIFY_AT_SCALE` when the fleet cannot reach the alerting channel (`ledger-contract.md:47-48` already defines the park).

### 4.5 Validators (`scripts/*.js`)

| Validator | orca equivalent | Gap |
|---|---|---|
| `skill-lint.js` workflow-step ↔ section consistency (`:212-233`) | `validate.py` composition refs resolve | A mission Pipeline block that names a phase (e.g. "RUNTIME-PROVE") whose playbook is not in the Composes clause is not caught. ~30 lines. |
| `validate-versions.js` | `test_docs_navigation.py:29` | Add `git describe --tags` == `plugin.json` once tags are cut consistently (`CHANGELOG.md` shows 0.6.1 cut 09-09). |
| `validate-artifact-paths.js` | cross-doc name resolution | equivalent |
| Exemptions in validator code (`skill-lint.js:53-60`) | `proof:` + `proof_status.py --check` | equivalent guard, different mechanism |

### 4.6 Plan-clobber guard (`planning-and-task-breakdown:150-155`, `8300e1b`)

What: refuse to overwrite `tasks/plan.md`/`tasks/todo.md` with unchecked tasks for *different* work; stop and ask.
orca equivalent: `liveness-resume.md:103` FREEZE-check on RESUME; `map-it:83-84` never commit the freeze on default. Nothing stops a new coordinator from writing a fresh ledger header over an existing ledger whose rows still have `f` flags for another objective.
Adoption: one rule in `ledger-contract.md` (≤4 lines): a ledger file with unmet flags and a different `SOURCE` digest is another run's state — never overwritten; RESUME it or park.

### 4.7 Rejected-change ledger (`evals/skill-impact.md`, `125b1f8`)

What: append-only table (date · skill · attempted change · rank-1 before→after · PR/outcome) consulted in CONTRIBUTING pre-flight step 3.
orca equivalent: anti-adoption lists in three dated research files (`2026-07-15…md:230-238`, `2026-08-16…md:232-241`, `2026-09-09…md §5`).
Adoption: a single `docs/research/REJECTED.md` index (id · date · proposal · reason · evidence) that `test_docs_navigation.py` checks is reachable; the mission-candidate rejections in §5.9 below are its first rows.

### 4.8 Command parity across hosts (`validate-commands.js`, `.gemini/`, `.opencode/`)

NOT-APPLICABLE today (orca ships one plugin manifest). Becomes relevant the day a mission is exposed as a slash command per host; the "description identical, body may differ" rule (`validate-commands.js:1-18`) is the right contract.

---

## 5. New mission candidates (each passed through the five-point test)

Five-point test per `ARCHITECTURE.md:34-47`: same mission iff same (1) unit of work, (2) per-unit state machine, (3) convergence proof, (4) ordering/isolation, (5) parking/failure semantics.

### 5.1 `migrate-it` — *a stateful schema or data change landed across deploys with old and new code valid at every step*

| | |
|---|---|
| Outcome | A production schema/data change is complete: expand → dual-write → backfill → switch reads → contract, each phase deployed and baked, data parity proven, old shape has zero readers before it is dropped. |
| Unit of work | One migration *phase* of one table/shape (expand · dual-write · backfill batch set · switch-reads · contract), each a deploy-gated step. |
| State machine | PLAN (shape delta, phase list, down path per phase) → EXPAND[deploy+bake] → DUAL-WRITE[deploy+bake] → BACKFILL (batched, throttled, resumable; parity check) → SWITCH-READS[deploy+bake] → ZERO-READERS window (telemetry) → CONTRACT[separate deploy, one-way human gate] → MIGRATED. |
| Convergence proof | Per phase: schema at head SHA; `down` written **and run** in a scratch env (negative control: apply `up`+`down` → schema identical to base); parity probe (row counts + sampled hashes old vs new column) GREEN; old-code-against-new-schema and new-code-against-old-schema both green (the dual-validity check). Terminal: parity 100% on the frozen table set, readers of the old shape = 0 over the declared window, contract PR merged. |
| Ordering / isolation | Strictly serial phases; never two migrations on one table in flight; each phase is its own ship-it-style release (`release.md` states reused); the hot file is the migrations directory (merge chain). |
| Parking | A phase whose bake/zero-reader window needs prod telemetry the fleet cannot see parks `CODE_CLOSED` + `VERIFY_AT_SCALE` (`ledger-contract.md:47-48`); a contract step is one-way human; a failed backfill batch is resumable, never restarted from zero. |
| Terminal states | `MIGRATED` · `MIGRATED-WITH-PARKED` (contract or window owed) · `ABANDONED` (down path exercised, old shape restored). |
| Why not one of the 17 | ship-it: unit is a tracer-bullet slice with a test oracle and a single pass through the release machine; here the oracle is data parity + zero readers, the release machine runs ≥3 times, and rollback of a deploy does not roll back data (`deprecation-and-migration:166`). modernize-it: explicitly hands this off ("hand a brief to a SEQUENCE of ship-it runs" `modernize-it:29-33`) — the sequence itself has no owner, no ledger, no convergence proof today. clean-sweep: no findings denominator. Fails on (1), (3), (5). |
| Worker loads | `deprecation-and-migration` (expand/contract rules `:164-190`), `incremental-implementation` (rollback-friendly commits `:174-181`). |
| Honest reasons to reject | (a) `runtime/mission-chaining.md` + three ship-it links can express the phase sequence today; the missing piece is the parity/zero-reader oracle, which could be a *playbook* ship-it composes (§6 item 2). (b) Zero demand recorded: no run has hit the modernize-it FORCED-MIGRATION handoff. (c) The bake windows make it a multi-day mission with mostly-parked terminals, the shape that killed the predecessor repo's campaign engine. Recommendation: playbook first; promote to a mission only after a chained run shows the phases need their own ledger. |

### 5.2 `retire-it` — *a deprecated surface is gone: consumers migrated, usage at zero, code/tests/docs/flags removed*

| | |
|---|---|
| Outcome | An API/feature/module/flag declared deprecated is removed with evidence that nothing still depends on it. |
| Unit of work | One deprecated surface (endpoint, exported symbol, feature flag, module) — and, within it, one consumer migration per sub-unit. |
| State machine | DECIDE (upstream `:39-56` five questions; advisory vs compulsory `:58-65`; human one-way) → REPLACEMENT-PROVEN gate (production-proven, migration guide exists) → ANNOUNCE (deprecation notice + date) → MIGRATE consumers you own (one PR each, `remediate-finding`) → ZERO-USAGE window (telemetry/log counter over a declared window; consumers you do not own → compulsory deadline or park) → REMOVE (code + tests + docs + config + notices; destructive, one-way) → RETIRED. |
| Convergence proof | Usage counter for the old surface = 0 over the window (pasted, source + sample); `git grep` of the old symbol on BASE returns nothing outside the changelog; replacement's tests green; negative control: re-enable the old path behind a flag on a throwaway branch and confirm the counter stays 0 (nothing was silently still calling it), then delete the branch. |
| Ordering / isolation | Announce before migrate; migrate before remove; removal PRs form a merge chain with the replacement; never remove before the window closes. |
| Parking | A consumer outside the fleet's control → `needs-human` (compulsory deadline is a product decision); no usage telemetry reachable → `CODE_CLOSED` + `VERIFY_AT_SCALE`; Hyrum-law dependence on undocumented behaviour that only production reveals → the ZERO-USAGE window is the guard, and its absence is a park, never a skip. |
| Terminal states | `RETIRED` · `RETIRED-WITH-PARKED` · `KEPT` (decision step concluded "still provides unique value"). |
| Why not one of the 17 | modernize-it: unit is a dependency node, oracle is CI green, direction is *upgrade*. reshape-it: behaviour-preserving by contract; removal changes behaviour. clean-sweep: a finding is "something wrong"; a deprecation is a decision with a usage oracle no test suite produces. Fails on (1), (3), (5). |
| Worker loads | `deprecation-and-migration` (all of `:37-160, 192-202`). |
| Honest reasons to reject | (a) Every proof depends on production telemetry; most runs will terminate `-WITH-PARKED`. (b) "Zero usage" is unprovable for undocumented behaviours (Hyrum) — the mission can only prove "zero *observed* usage over N days". (c) Small surfaces (one flag) are a clean-sweep finding; only multi-consumer sunsets justify a ledger. |

### 5.3 `oncall-it` — *the surface is operable: on-call can see, alert on, and act on it without reading the source*

| | |
|---|---|
| Outcome | For a frozen set of production paths, every on-call question is answerable from telemetry; every alert is symptom-based, runbook-linked, and has fired once; an induced failure was diagnosed from telemetry alone. |
| Unit of work | One production path (endpoint / job / external dependency) × its on-call questions. |
| State machine | FREEZE the path set + the 2–4 on-call questions per path (human gate; questions are the denominator, `observability-and-instrumentation:27-40`) → INSTRUMENT (structured events + correlation ID + entry-point field; RED/USE with bounded labels; spans) → ALERT (symptom-based, two severities, threshold justified) → RUNBOOK (three-line minimum per alert, matched to repo convention) → TEST-FIRE (lower threshold, confirm channel + runbook link) → INDUCE (staging failure; a fresh worker with **no source access** must locate it from telemetry — the unfakeable oracle) → OPERABLE. |
| Convergence proof | Per path: each on-call question maps to a named signal (quoted event/metric name); alert fired once with receipt; runbook exists at the linked path; the source-blind diagnosis worker's manifest names the failing component from telemetry only; negative control: remove the new instrumentation on a throwaway branch → the blind worker cannot locate the induced failure (RED). No secret/PII in sampled log output (redaction check from `diagnose.md:5-14`). |
| Ordering / isolation | Instrumentation PRs before alert config; alert before runbook link check; induce last. Parallel across paths; serialized on shared logger/exporter config (hot file). |
| Parking | No staging/alerting channel reachable → `CODE_CLOSED` + `VERIFY_AT_SCALE`; cardinality decisions that need a cost owner → `needs-human`. |
| Terminal states | `OPERABLE` · `OPERABLE-WITH-PARKED`. |
| Why not one of the 17 | ship-it's `observe` phase is a canary *after* deploy — it observes what already exists; it never adds instrumentation and its oracle is change-vs-baseline, not "can a stranger diagnose this". speed-it's oracle is a metric budget. harden-it's is an exploit. root-cause consumes telemetry; it does not build it. Fails on (1), (3), (4). |
| Worker loads | `observability-and-instrumentation`, `references/observability-checklist.md`. |
| Honest reasons to reject | (a) The blind-diagnosis oracle is expensive (a second worker per path) and needs a staging environment the fleet can drive. (b) Half the value (alerts wired, test-fired) is one release-gate line in `release.md` plus a playbook (§6 item 1); the mission form is justified only for a brownfield "make this whole service operable" ask. (c) Without SLOs the "threshold justified by history" step becomes a human gate on every alert. |

### 5.4 `erase-it` — *personal data is inventoried, purposed, retention-bounded, and a subject's export/delete works end to end*

| | |
|---|---|
| Outcome | Every personal-data field/store is classified with a stated purpose and TTL; a data-subject export and delete succeed and leave zero residue across every copy (primary, cache, index, analytics, backups). |
| Unit of work | One personal-data store/field class (from a frozen inventory). |
| State machine | INVENTORY (classify Non-personal / Personal / Sensitive per `security-and-hardening:382-388`; enumerate every copy) → FREEZE purpose + retention per class (human/legal one-way) → WIRE (TTL job, deletion path, export path, consent gate for third-party/LLM sharing) → PROVE (insert a synthetic subject, exercise every path, delete, then probe every store in the inventory for residue) → GAP register → ERASABLE. |
| Convergence proof | Residue probe over the frozen store inventory = 0 hits for the synthetic subject after delete (pasted per store); export contains every inventoried field; negative control: skip one store's deletion on a throwaway branch → the probe finds residue (RED); telemetry sample shows no PII fields (allowlist check). |
| Ordering / isolation | Inventory before wiring; deletion paths for derived stores (index, cache) after primary; backups are almost always `needs-human` (retention policy). |
| Parking | Backups/analytics vendors outside the fleet's reach → `needs-human` with the legal owner; a purpose nobody can state → the field is a finding to *remove*, not to document. |
| Terminal states | `ERASABLE` · `ERASABLE-WITH-GAPS`. |
| Why not one of the 17 | attest-it: proves obligations of an external standard with ro evidence gathering (`attest-it:46-48`); it cannot wire a deletion path and its oracle is re-derived evidence, not a residue probe. harden-it: "can an attacker read it?" — upstream draws exactly this line (`:380`). clean-sweep: the denominator is a store inventory, not findings. Fails on (1), (3), (5). |
| Worker loads | `security-and-hardening` (Data Privacy & Compliance `:378-397`, checklist `:448-455`). |
| Honest reasons to reject | (a) The residue probe needs prod-like data plumbing and a legal owner on every run; expect `-WITH-GAPS` as the normal terminal. (b) attest-it with a GDPR obligation catalog already produces the *gap register*; only the wiring differs, and wiring could be clean-sweep with `source=audit` fed by attest-it's gaps (`mission-chaining.md:29-32` deferral carry). That chain is the cheaper first move. |

### 5.5 `onboard-it` — *a stranger can go from clone to green in a clean environment using only the repo's docs*

| | |
|---|---|
| Outcome | README quick-start and setup docs are executable: a fresh worker in a clean container follows them from clone to passing suite with zero out-of-band knowledge; every public interface is documented; every decision that would surprise a newcomer has a recorded rationale. |
| Unit of work | One onboarding step / one undocumented public interface / one missing decision record. |
| State machine | PROBE (clean container, docs-only worker follows README; every failure is a finding) → FREEZE the finding set → FIX (write the missing step/doc/ADR, matching existing conventions) → RE-PROBE until the blind worker reaches green → ONBOARDABLE. |
| Convergence proof | The docs-only probe reaches the suite green in a clean env (transcript pasted, `head_sha`); negative control: remove one fixed step → the probe fails at that step (RED). ADRs continue the repo's existing numbering scheme (`documentation-and-adrs:36-44`). |
| Ordering / isolation | Probe before fix (never write docs from the author's head); doc PRs are independent except README (hot file). |
| Parking | A step needing credentials/accounts → `needs-human`; a decision whose rationale only a departed human knows → recorded as "rationale unknown", never fabricated (`intent debt` — `2026-08-16…md:49`). |
| Terminal states | `ONBOARDABLE` · `ONBOARDABLE-WITH-PARKED`. |
| Why not one of the 17 | clean-sweep `source=doc-claims` verifies *existing* claims and says "Generating NEW docs is not this mission" (`clean-sweep:56-58`); the executable-onboarding probe has a different oracle (a blind run) and generates missing docs. Fails on (1), (3). |
| Worker loads | `documentation-and-adrs`, `context-engineering` (rules-file contents `:38-79`). |
| Honest reasons to reject | (a) The prior audits rejected a docs-specialist worker twice (`2026-08-16…md:226`); this is close to that with a probe attached. (b) The probe is one unit of `runtime-prove` Part B applied to docs — a playbook composed by ship-it's doc-sync unit (`release.md:28-31`) may be enough. (c) Two of three proof legs (ADRs, API docs) have no unfakeable oracle. |

### 5.6 Rejected as modes / sources / playbooks of an existing mission

| Candidate from the Addy set | Why rejected as a mission | Where it lives instead |
|---|---|---|
| `contract-it` (api-and-interface-design sweep: every public interface has a committed contract, idempotency honoured) | Unit (a public interface) and oracle (contract test that dies under mutation; idempotency replay probe) are prove-it's unit and oracle with a different critical surface — same state machine, same negative control, same parking. Passes only test (1) weakly. | prove-it with the surface = public interfaces; idempotency into the api-contract lens (§6 item 6) |
| Simplification sweep (code-simplification) | Unit = a module; oracle = behaviour unchanged + measured structure — that is reshape-it (`reshape-it:1-20`). | reshape-it; risk-review simplification lens |
| Context/rules-file setup (context-engineering L1) | A single artifact with no denominator and no oracle; auto-written AGENTS.md is a documented negative (`compound-learn.md:40-41`). | compound-learn proposals; floor-it's "point AGENTS.md at CONSTRAINTS.md" line |
| Interview / idea refinement | Coordinator-side grill phase; producing decisions is map-it. | decide-and-freeze, map-it |
| CI/CD pipeline build | floor-it ENFORCE unit; release.md deploy states. | floor-it, release |
| Browser runtime verification | A verify technique, not an outcome. | runtime-prove Part B, observe, field-test-it |
| Launch readiness checklist (`/ship`) | review-it + the release state machine; `evidence-manifest §3` is the standing DoD. | ship-it, review-it |
| Source-driven (doc-verified) implementation | A build-time citation rule. | build-change bullet (§6 item 7) |
| Git hygiene / worktrees | Substrate + dispatch-lifecycle commit hygiene. | — |
| Data-migration as a *mode* of modernize-it | modernize-it already refuses it (`:29-33`); a mode flag cannot change the deploy-count or the parity oracle (`README.md` FAQ "A mode flag can't change a convergence proof"). | migrate-it (5.1) or a playbook composed by chained ship-it runs |

---

## 6. Playbook candidates (callable phase protocols; ≤90 lines each per `validate.py:97`)

| # | Playbook | Recipe (upstream anchor) | Composed by | Completion criterion |
|---|---|---|---|---|
| 1 | `instrument` | on-call questions → signal per question → structured event + correlation ID + entry-point field → RED/USE bounded labels → symptom alert (two severities) → runbook (three lines, repo convention) → test-fire → verify by induced failure (`observability-and-instrumentation:27-197`; checklist `:82-90`) | ship-it (units matching the `:213` trigger list, before PROMOTION_READY); oncall-it; harden-it (security-event logging, `security-checklist.md:227`) | every question maps to a quoted signal; alert receipt; runbook path; induced-failure transcript; no PII in sampled output |
| 2 | `data-migration` | expand → dual-write → backfill (batched) → switch reads → contract, each independently deployable; tested `down` before merge; `CREATE INDEX CONCURRENTLY`; flag-decoupled cutover (`deprecation-and-migration:164-190`) | ship-it (a slice touching schema), modernize-it's FORCED-MIGRATION handoff brief, migrate-it | phase list with deploy boundaries; `up`+`down` round-trip identical schema; dual-validity check green; parity probe recorded |
| 3 | `floor-guard` (runtime script + a short policy paragraph, not a playbook) | `references/floor-guard.md:7-13` contract | floor-it GUARD; verify.py NC leg; acceptance-review test-adequacy | exit 0/1/2; findings by rule+location; DECISIONS waiver honoured |
| 4 | `record-decision` (or a section in decide-and-freeze) | match existing ADR convention first (`.adr-dir`, numbering, headings, markup); never delete, supersede (`documentation-and-adrs:36-100`) | decide-and-freeze (when the ADR test at `:24-25` fires), map-it decision tickets, reshape-it one-way API-break decisions, retire-it DECIDE | ADR continues the repo's scheme; status + supersedes link; the DECISIONS.md line references the ADR path |
| 5 | `release.md` additions (not a new playbook) | error-budget gate (`shipping-and-launch:238-249`); rollout decision thresholds table (`:142-151`) as observe.md's numeric complement; pre-launch "≥1 symptom alert with runbook, test-fired" (`observability-checklist:82-90`) | ship-it | PROMOTION_READY reads budget remaining when an SLO exists; observe alerts on burn rate as a HOLD |
| 6 | `risk-review.md` lens additions | api-contract: idempotency (atomic claim, payload hash, in-flight policy, retention ≥ redelivery) `api-and-interface-design:156-215`; **privacy** lens (NEVER_GATE with security): classification, purpose, TTL, deletion incl. copies, consent for third-party/LLM, `:378-397`; perf: cache-key-omits-viewer, index-without-plan, pool-size-as-fix `performance-optimization:462-478`; a11y: unchanged; security: the two destructive-path caveats `:278` | review-it, ship-it, harden-it, modernize-it | each lens finding quotes its line; privacy lens findings route to erase-it/attest-it when they exceed a diff |
| 7 | `build-change.md` bullets | source-driven: when framework/library-specific code is written, cite the official page (full URL) in the manifest or mark `UNVERIFIED`; never hardcode outbound endpoints from fetched examples (`source-driven-development:141-179, 114`); browser-driving units: dedicated/isolated profile, no credential reads, mutations need a grant (`browser-testing-with-devtools:60-107`) | ship-it, clean-sweep, oss-contribute; observe, field-test-it | citation present or UNVERIFIED flagged; profile flag recorded |
| 8 | `decide-and-freeze.md` bullets | hypothesis + confidence before round 1; explicit-yes gate; "predict the next three answers" stop; "if you didn't have to justify this…" probe (`interview-me:40-132`) | ship-it, map-it | freeze recorded only after an explicit yes |
| 9 | `ledger-contract.md` rule | never overwrite a ledger with unmet flags for a different SOURCE (`planning-and-task-breakdown:150-155`) | every mission at T0 | header write refuses; RESUME or park |
| 10 | `compound-learn.md` line | environment-improvement categories already adopted (#250); add the upstream "Documentation for Agents" `:250-257` target list (rules file, spec, ADRs, inline gotchas) as the four legal append targets | all mutating missions | — |

---

## 7. Risks — where Addy's current design conflicts with orca-fleet doctrine; what not to copy

| # | Upstream design (anchor) | Conflict with orca doctrine (anchor) | Disposition |
|---|---|---|---|
| 7.1 | `/ship` spawns three personas and **merges their reports in the main context** — the same context that wrote the code and will decide GO/NO-GO (`commands/ship.toml:27-37`); "If subagents are unavailable … invoke each persona's system prompt sequentially in the main context" (`:18`) | Build-blind review must be a **fresh session that did not write the code** (`acceptance-review.md:3-4`); the verifier is "a DIFFERENT process/session — never a teammate (whose messages are in-band and self-certifying)" (`evidence-manifest.md:109-111`); axes are dispatched by the coordinator, one worker each (`dispatch-lifecycle.md:51-53`). A self-synthesized verdict is the failure REVIEW.md §1 already names ("self-scoring gate"). | Do not copy the merge step. The fan-out topology is already adopted; keep the aggregate side-by-side, no rerank, in the coordinator that never wrote code. |
| 7.2 | doubt-driven "degraded self-questioning fallback … rewrite ARTIFACT + CONTRACT as a fresh self-prompt with a hard mental separator" inside a subagent (`doubt-driven-development:47`) | Instructed isolation is named as the weakest reviewer mode and is a coordinator judgment, not proof (`evidence-manifest.md:46, 124`); `runtime-prove.md:9` requires a FRESH-context reviewer. | Never accept; a worker that cannot spawn a reviewer returns to the coordinator (`nested_worker_depth_exceeded`, `dispatch-lifecycle:51-53`). |
| 7.3 | `simplify-ignore.sh` rewrites source files on disk with `BLOCK_<hash>` placeholders for the session and restores them on Stop (`:176-216, 218-302`); crash leaves placeholders (`SIMPLIFY-IGNORE.md:71-79`) | The build-blind reviewer and `verify.py` read the worktree and the tree SHA (`reviewed-sha-freshness.md:8-14`, symbol-on-base `verify.py` check 6). A reviewer that reads placeholders reviews fiction; a commit made while filtered lands placeholders on BASE; a crashed Stop leaves a dirty worktree that `WT_CLEAN` refuses to retire (`dispatch-lifecycle.md:155-160`). | Exclude. If block-level protection is ever needed, express it as a `CONSTRAINTS.md`/DECISIONS rule the reviewer reads, never as on-disk mutation. |
| 7.4 | TDD REFACTOR inside the loop (`test-driven-development:85-94`) vs Matt's refactor-in-review | Documented router conflict (`AGENTS.md:78-79`) — the reason for one router per worker. Also: a REFACTOR step inside a build unit moves code the reviewer's "spec" axis expects at a known seam. | Already handled: pack per worker. Do not "harmonize" the two TDD loops into one playbook. |
| 7.5 | constraint-driven non-interactive rule: "If constraints are missing and you're in one of those, apply the Floor below, note that you did, and flag the rest" (`:38`); `/build auto`'s "single checkpoint … unambiguous affirmative" (`build.toml:33`) | Thresholds are a one-way door; headless runs PARK at the freeze, never default policy into being (`floor-it:58-62`; `gate-classification.md:36` "Never defaulted on timeout"); approvals are classified, not parsed for affirmatives. | Keep orca's rule. The upstream "apply the floor anyway" is exactly the auto-decide one-way door orca forbids. |
| 7.6 | code-reviewer must "always include at least one positive observation" (`code-reviewer.md:95`); security-auditor "Acknowledge good security practices" (`:102`) | A reviewer instructed to praise anchors toward approval; orca's anti-anchoring rule writes the reviewer's own expectation *before* seeing the diff (`acceptance-review.md:6-14`) and its anti-FP gate drops findings that cannot quote a line (`:28-32`). | Do not import the praise requirement into any lens or axis prompt. |
| 7.7 | Tier-3 evals grade the **execution trace** (`run-evals.js:529-531` "Judge what the agent actually did (tool calls…)") | "Completion is never graded on narration or trace" (`ARCHITECTURE.md:44-56`); traces are forensic only. | Acceptable *only* as catalog tooling that scores a mission's coordinator behaviour in a fixture; never as `proof:` evidence, never as a completion oracle. State this in `scripts/eval.py` if Tier 3 is added (§4.2). |
| 7.8 | Agent Teams worked example: teammates message each other to disprove hypotheses; "Do not rebuild this as a `/debug` slash command that fans out subagents" (`orchestration-patterns.md:174-278`) | D7 rejected peer messaging (`2026-07-15…md:158-162`); workers message the coordinator only; root-cause's debate is coordinator-mediated (`root-cause:28-29, 49-50`). | Keep D7. root-cause may run two adversarial workers whose falsification tables the coordinator joins; they never talk to each other. |
| 7.9 | Floor guard is worker-runnable and regex-shallow (`floor-guard.md:99`); upstream's Step 6 is "at review time" by the same agent (`constraint-driven-development:206-214`) | A guard the worker runs on its own diff is self-attestation — the same class REVIEW.md §2 item 1 flags for `negctrl.txt`. | Adopt the script but run it in `verify.py`/CI (off-worker), not in the builder's loop only. |
| 7.10 | SessionStart injects 193 lines of router into every session (`session-start.sh:18-25`) | Instruction budget (`ARCHITECTURE.md:79-83`; one mission already loads ~29.5K tokens per REVIEW.md item 4). | If a SessionStart hook is added, inject the 20-row intent table only. |
| 7.11 | `/review` command labels Critical/Important/Suggestion (`review.toml:14`) while the skill and persona use Critical/Required/Optional/Nit (`code-review-and-quality:181-187`; `7cb7a20`) | orca's taxonomy is single-sourced (`acceptance-review.md:36`). | Do not import the command's labels; upstream drift, not doctrine. |
| 7.12 | Context-budget "start trimming at 75%" and "compress before dropping" (`context-engineering:186-214`) applied *inside* a worker's own context | orca's worker is disposable; its memory is the ledger and manifest, and a worker under context pressure writes CONTEXT HANDOFF and is replaced (`ledger-contract.md:67-86`) — self-compaction produces the summary-substitution anti-pattern (`2026-08-16…md:94`). | Do not instruct workers to self-summarize; respawn. |
| 7.13 | "Safe Fallback Patterns … Safe default + warning (instead of crashing)" (`debugging-and-error-recovery:214-241`) | floor-guard's own `unfinished-work` rule flags empty catch/swallowed errors (`floor-guard.md:59`); orca's runtime-prove asserts persisted state, not exit codes (`runtime-prove.md:21-25`). | Do not adopt into diagnose.md. |
| 7.14 | `allowed-tools` is permission pre-approval, not restriction; `disallowed-tools` restricts and is Claude-Code-only (`485cd8e`) | orca's least-privilege is enforced below the model by spawn profiles (`sandbox-policy.md:12-43`), not frontmatter. | Nothing to adopt; avoid adding `disallowed-tools` to mission frontmatter (spec-legality is already a REVIEW.md finding). |

---

## 8. Recommended order (cheapest first, each closes a named gap)

1. **Privacy operating rules into `risk-review.md` security lens** (NEVER_GATE) — the one previous-audit item #250 missed; ≤6 lines. (§3.7)
2. **`eval.py` re-based on frontmatter descriptions with TF-IDF, owner-pairwise negatives, collision check, `--threshold 0.95` in CI** — closes REVIEW.md §2 item 3 and this audit's §4.2. Keep `routing.json` as the fixture.
3. **`runtime/scripts/floor_guard.py`** with the upstream exit contract, wired into floor-it GUARD and `verify.py`. (§4.3)
4. **`instrument` playbook + one `release.md` PROMOTION_READY line** — the observability gap. (§6 items 1, 5)
5. **Lens additions** (idempotency, perf backend red flags, destructive-path caveats, web-perf "potential impact" labeling). (§6 item 6)
6. **`ledger-contract.md` clobber rule; `docs/research/REJECTED.md` index.** (§4.6, §4.7)
7. **Mission decisions** in this order: `migrate-it` only after a chained-ship-it migration run shows the phases need a ledger; `oncall-it` only on a brownfield "make it operable" ask; `retire-it` / `erase-it` / `onboard-it` recorded in REJECTED.md with the reasons in §5 until demand appears. All five pass the identity test; none has demand evidence.

## 9. Caveats

- Upstream snapshot is `6ca0cd7`; the security skill alone moved on 08-14, 08-31, and 09-04. Treat "current" rows as current at that SHA.
- Line anchors in upstream skills shift with every edit; the quoted text is the stable key.
- REVIEW.md (`a91937d`) findings are cited as measurements, not re-verified here except where this audit independently read the same code (`eval.py`, `hooks.json`, `verify-gate.sh`).
- The 340-test suite passes at `a91937d` (`python3 -m unittest discover -s tests` → OK); upstream Tier 2 passes at `6ca0cd7` (140 checks, 88/88 rank-1).
