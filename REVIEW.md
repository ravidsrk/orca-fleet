# REVIEW.md — deep review of ravidsrk/orca-fleet

Reviewed SHA: `af8ea8975cdc5e9d0911a1d251cb02afd4f7a5dd` (main, 2026-09-10, merge of #254).
Every `file:line` below is at that SHA. Read-only engagement; nothing in the repo was changed.
Scratch clones were used for every injection. Research sources are listed in §9.

Sections 1–9 are the review as delivered and are not edited after the fact. **§10 is a later,
dated re-measurement** at `9afefc6` — the same attacks and the same routing matrix, re-run against
the branch that addressed the backlog, including what the fixes cost and what is still not true.

## 1. Verdict

**NO-GO for "verified, not asserted" as stated at this SHA.**

What is machine-verified: the frozen denominator (scope), commit existence, reviewed-SHA freshness
(tree-bound), and an APPROVED GitHub review looked up outside the manifest. Those four legs are
real mechanism and hold under attack.

What is not: the negative control, which the README names as the moat. No script in the repo
executes, replays, or re-derives a negative control. `verify.py` reads the worker's own artifact
for the words "killed" or "RED". In both lanes where the GitHub review is waived
(`dark-eligible`, `--no-gh`), a worker-written text file is sufficient for a GREEN verdict on a
mutation unit. Six of ten manifest-gaming attacks landed. The claim that holds is narrower:
"scope-frozen, review-checked on GitHub, fail-closed where the coordinator owns the environment."

## 2. Executive summary — top five findings

1. **The negative control is never executed by any mechanism.** `verify.py:370-397` pattern-matches
   the artifact text; `--execute-nc` is a documented stub. A fabricated `negctrl.txt` passes.
   With `--lighting dark-eligible` or `--no-gh` the review leg is also waived, so a mutation unit
   goes GREEN on forged text alone (bypass log A1, A2, A4, A6, A9, A10).
2. **Proof-status honesty is a filename-and-substring check.** A three-line fake run report
   naming the mission passes `validate.py`, `proof_status.py --check`, and 339 of 340 tests
   (bypass B2; `scripts/validate.py:371`). The mechanism checks that a file exists, not that a run
   happened.
3. **The routing eval measures a hand-written keyword table, not routing.** `scripts/eval.py:27`
   is a dictionary the repo maintains; the 43 curated prompts score 100%, 36 realistic prompts
   score 53%. Sixteen realistic asks route nowhere; "coverage" sends floor-it work to prove-it.
   CI's routing step cannot fail (`.github/workflows/validate.yml:38`); only the 0.95 unit-test
   floor gates it.
4. **The recommended install path ships no completion gate, and the frontmatter is not
   spec-legal.** `hooks/hooks.json:10` resolves only under `${CLAUDE_PLUGIN_ROOT}`; the
   README's recommended symlink install (`README.md:79`, `:313`) never wires `verify-gate.sh`.
   The three custom fields (`proof`, `autonomy`, `proof_evidence`) fail the agentskills.io
   reference validator and Claude Code's packaging/upload path. One mission loads ~29.5K tokens
   (88% of the doctrine tree), so progressive disclosure is nominal.
5. **The autonomy ladder assignments do not follow their source.** Osmani's L4 is "parallel
   delegation" (many agents on isolated slices); L3 is a single agent looping to a measurable
   stop. Every mission here is a coordinator plus parallel isolated workers, including
   review-it's three to four axis workers, so all 17 sit at L4 by the source definition. The
   repo's L3/L4 split (`README.md:122-123`) uses a "does it mutate" axis the source does not
   define, and the quotation attributed to Osmani at `README.md:117` could not be located in his
   published ladder text.

## 3. Rubric and scores

Weights sum to 100. Pass bar per criterion is stated; score is 0–10.

| # | Criterion (grounded in) | Weight | Pass bar | Score | Evidence |
|---|---|---|---|---|---|
| 1 | Evidence legs are mechanism, not prose (verify.py, hooks, CI) | 15 | Every README guarantee maps to a machine check that fails RED on the gaming trap | 5 | §3.1 table: 7 of 20 guarantees are mechanism |
| 2 | Negative-control soundness (mutation-testing literature: pseudo-tested methods, coupled fix+test) | 12 | The verifier re-executes or replays at least a sample of NCs; a forged artifact is RED | 1 | A1/A4/A9/A10 LANDED; `--execute-nc` stub |
| 3 | Verifier independence (Knight–Leveson, self-preference bias, AI-control) | 8 | Cross-model or execution-based verifier by default; same-model fresh session named as weak | 5 | `reviewer_mode` is recorded and named honestly; default in the only ship-it run was `instructed-isolation` |
| 4 | Proof-status honesty is machine-checked | 8 | An unearned tier cannot pass CI without a real run artifact | 3 | B1 CAUGHT, B2 LANDED |
| 5 | Run-report integrity (SHAs, PRs, hashes resolve) | 6 | Every referenced SHA and hash resolves on a full clone | 8 | All 21 SHAs and the ship-it inventory hashes resolve; demo hash stale |
| 6 | Catalog identity test enforced | 8 | The five-point test is asserted by a test, and every mission passes it | 4 | `tests/test_architecture.py:97` checks only a regex; three merge candidates |
| 7 | Routing clarity (no sibling collision) | 8 | ≥90% on realistic prompts including ambiguous ones | 3 | 53% on 36 realistic prompts |
| 8 | agentskills.io conformance | 6 | Reference validator passes; custom data under `metadata` | 3 | Three top-level extras fail `skills-ref validate` and Claude packaging |
| 9 | Portability / self-containment | 7 | A mission survives `npx skills add` and a copy | 3 | `../../` refs break every copy installer; documented caveat only |
| 10 | Instruction budget / progressive disclosure | 5 | One mission loads ≤5K tokens per spec guidance; references on demand | 3 | ship-it ≈29.5K tokens end to end |
| 11 | Supply-chain drift (Orca, packs, actions) | 6 | Every hard dep pinned; drift detected by a check, not a mission | 4 | Actions SHA-pinned; Orca and packs unpinned; Orca v1.4.199 shipped the same day as the re-pin |
| 12 | Security / injection surface | 6 | Untrusted text is fenced by mechanism; `danger` requires a sandbox by check | 5 | `pm.py` escapes control chars; everything else is doctrine; `danger` checks an env var only |
| 13 | Doc truthfulness (clean-sweep pass) | 5 | Zero false factual claims | 6 | Five false or misleading claims found (§7.4) |
| | **Weighted total** | 100 | | **40 / 100** | |

### 3.1 Mechanism vs doctrine — every README guarantee

Mechanism = a script, hook, or CI step fails RED when the guarantee is violated. Doctrine = prose
an agent under context pressure can skip. Advisory = mechanism exists but the graded worker
controls its inputs.

| README guarantee (line) | Where it lives | Class | Notes |
|---|---|---|---|
| Frozen denominator; worker cannot shrink scope (`README.md:285`) | `verify.py:164` check_scope | Mechanism | Sound when the coordinator supplies `--contract-source@ref`; A8 shows a bare working-tree path is accepted |
| SHA-bound manifest; commits are real (`README.md:285`) | `verify.py:203` check_real_commits | Mechanism | 40-hex required on mutation units |
| Reviewed-SHA freshness, tree-bound (`README.md:234`) | `verify.py:222`, `_wtree_bound` | Mechanism | A5 forged wtree CAUGHT |
| Independent APPROVED review at head (`README.md:454`) | `verify.py:316` check_review | Mechanism | Fail-closed without `gh`; waived by `dark-eligible` and `--no-gh` |
| Negative control mandatory for every fix and test (`README.md:286`) | `verify.py:370` | Advisory | Field presence plus regex on worker text; never executed |
| Negative control re-executed on a ≥10% sample (`runtime/evidence-manifest.md:119`) | prose only | Doctrine | No script, no ledger field, no test |
| Tests re-run at head_sha in a clean env (`README.md:454`) | `runtime/evidence-manifest.md:117` | Doctrine | "coordinator-run — not verify.py" |
| Deployed revision == reviewed SHA (`README.md:454` FAQ) | `playbooks/release.md` | Doctrine | No script |
| Integrity inventory makes evidence tamper-evident (`evidence-manifest.md:131`) | prose; `test_docs_navigation.py:103` checks a heading exists | Doctrine | No hash re-check; demo inventory is already stale |
| Wrong-base detection, BASE ≠ default (`README.md:231`) | `preflight.py` | Mechanism if invoked | Invocation is doctrine in each SKILL.md; nothing forces it |
| One merge train, arrival order (`README.md:236`) | `runtime/merge-serialization.md` | Doctrine | |
| Attention budget ≤3 builders (`README.md:238`) | `runtime/attention-budget.md`; header test | Doctrine | The test checks the header template mentions WIP |
| Liveness / resume re-verifies against git (`README.md:248`) | `runtime/liveness-resume.md` | Doctrine | |
| One-way doors are human, never defaulted (`README.md:244`) | `runtime/gate-classification.md` | Doctrine | |
| Least-privilege workers; `danger` only in a sandbox (`README.md:248`) | `spawn_worker.sh:152-159` | Advisory | Env-var opt-in is checked; sandbox existence is not |
| Only `skills/` holds a SKILL.md (`README.md:306`) | `validate.py:486` | Mechanism | D1 a/b/c CAUGHT |
| Proof tier needs a run report on disk (`README.md:127`) | `validate.py:347-376`, `proof_status.py` | Mechanism (weak) | Existence and naming only; B2 LANDED |
| Instruction-budget caps (`README.md:421`) | `validate.py:96-104` | Mechanism | Line and byte caps hold |
| Autonomy level validator-enforced (`README.md:116`) | `validate.py:382` | Mechanism (value legality only) | Any of L0–L5 passes |
| Verifier is a different session (`README.md:270`) | `hooks/hooks.json`; `docs/verify-gate.md:98` | Advisory | Native hook runs inside the graded worker; sound only on CI/MCP/SDK surfaces the repo does not ship |

Seven of twenty are mechanism. The four the README leads with (negative control, clean-env
re-run, sample replay, tamper evidence) are doctrine or advisory.

## 4. Bypass log

Method: scratch clone of the repo at the reviewed SHA, a two-criterion frozen contract committed
as `contract.md@<sha>`, a real head commit, `verify.py` invoked as the coordinator would. Full
commands were run, not reasoned about.

| ID | Attack | Lane / flags | Outcome | Anchor |
|---|---|---|---|---|
| A1 | Fabricated `negctrl.txt` ("mutmut#7 killed") never run; contract corroborated | `--unit-class mutation --lighting dark-eligible` | **LANDED** exit 0 | `verify.py:331`, `:397` |
| A2 | Worker-written `review.artifact` containing head_sha, plus forged NC | `--no-gh` with contract | **LANDED** exit 0 (NOTE only) | `verify.py:347` |
| A3 | Report-only manifest: every criterion `addressed: true`, no commands, no artifacts | `--unit-class report-only` | **LANDED** exit 0 | source-binding of quoted lines is doctrine (`evidence-manifest.md` §3) |
| A4 | `tool: hand` with an invented unified diff and "killed" line | dark-eligible | **LANDED** exit 0 | `verify.py:409-415` |
| A5 | Stale review at an older commit with `reviewed_wtree` forged to the head tree | mutation | **CAUGHT** exit 2 | `verify.py:241` recomputes both trees |
| A6 | Amend after review (same tree), dark-eligible | mutation | **LANDED** exit 0 | By design; flags that freshness plus waived review is GREEN with no review anywhere |
| A7 | Contract source with zero criterion ids | report-only | **CAUGHT** exit 2 | `verify.py:181` |
| A8 | Bare working-tree path as `--contract-source`, edited to drop AC-2 | report-only | **LANDED** exit 0 | `verify.py:119-131` accepts non-ref paths; only matters where the worker sets env (native hook) |
| A9 | Pinned mutant killed, sibling mutant survived ("killed: 1 survived: 1") | dark-eligible | **LANDED** exit 0 | Survival is scoped to the pinned id (`verify.py:62`, `:403`); a one-mutant "audit" is accepted |
| A10 | NC artifact at an absolute path outside the repo, untracked, unhashed | dark-eligible | **LANDED** exit 0 | `verify.py:110` `_resolve` passes absolute paths through |
| A11 | Realistic contract text with `SHA-256`, `PR-12`, `RFC-7519`, `ISO-8601` | any | **FALSE RED** (usability) | `verify.py:57` CRIT_ID_RE treats them as criteria |
| B1 | `proof: self-run` with no evidence file | validate + proof_status | **CAUGHT** both exit 1 | `validate.py:347` |
| B2 | `proof: self-run` plus a 3-line fabricated `docs/runs/2026-09-10-map-it-self-run.md` with an "integrity inventory" heading | validate + proof_status + unittest | **LANDED** validate 0, proof_status 0; 1 of 340 tests red (`test_distribution_proof_mix_matches_reality`, a prose-consistency check fixable by editing one sentence) | `validate.py:371-376` |
| D1a | Tracked `playbooks/x/SKILL.md` | validate | **CAUGHT** | `validate.py:486` |
| D1b | Untracked `docs/SKILL.md` | validate | **CAUGHT** (git-tracked scan falls back to filesystem) | |
| D1c | Nested `skills/ship-it/sub/SKILL.md` | validate | **CAUGHT** | |
| E1 | Stop hook with `ORCA_MANIFEST` unset | native hook | **LANDED by design** (`verify-gate.sh:70`) | A worker that never names a manifest ends every turn |
| E2 | Worker sets `ORCA_CONTRACT_SOURCE`/`ORCA_UNIT_CLASS` in-session | native hook | **LANDED, documented** (`docs/verify-gate.md:98`) | The only sound surfaces (CI/MCP/SDK) are not shipped in this repo |
| U1 | Clean-env test re-run at head_sha | — | **UNTESTABLE** | No script; no ledger field the verifier reads |
| U2 | ≥10% fresh-worker revert sample | — | **UNTESTABLE** | No script, no record in any run report |
| U3 | Integrity inventory re-check on RESUME | — | **UNTESTABLE** | No checker; `demo/negative-control/README.md:50` hash already differs from the committed transcript (`70d42150…` vs `f40e3f86…`) |
| U4 | Deployed == reviewed | — | **UNTESTABLE** | No deploy surface, no script |
| U5 | Verifier independence (different session) | — | **UNTESTABLE** without Orca | The shipped hook runs in the worker session |

Tally: 9 LANDED, 1 false RED, 6 CAUGHT, 2 landed-by-design, 5 UNTESTABLE.

### 4.1 What "independent" buys, against the literature

The verifier is deterministic Python, which is the right choice: execution-based checks are the
mitigation the reward-hacking literature converges on (METR 2025, Baker et al. 2025, AI-Control
2024). But the deterministic part stops at scope, SHA, freshness, and review existence. The
judgment-shaped legs (was the NC real, is the test tautological, did the binding audit happen)
are pushed to "the coordinator" — an LLM in the same model family as the worker, reading the
worker's artifacts. That is the shared-blind-spot configuration Knight–Leveson and the 2025–2026
judge-bias results warn about (correlated errors rise with capability; same-family judges favor
same-family output). The repo names this honestly in `reviewer_mode` and prefers cross-vendor in
`playbooks/acceptance-review.md:13`, but the only recorded ship-it run used the weakest mode, and
nothing prevents `same-vendor-fresh` from being the default forever. The one structural
mitigation the design does have is the GitHub-review lookup, which requires a second identity;
that leg is exactly the one both waiver lanes remove.

### 4.2 `demo/negative-control` and `bench/vf-bench`

Both run and report what they claim, with two caveats. The demo's only trap is scope-shrink on
a `report-only` unit, so it demonstrates the frozen denominator, not the negative control the
README leads with. VF-Bench's single positive control (`traps/valid-control.json:6`) is also
`report-only`; no mutation-class manifest has ever passed `verify.py` GREEN inside this repo (the
ship-it self-run went RED on review). "The sound gate is not trivially always-RED"
(`bench/vf-bench/README.md:26`) is therefore proven only for the class where review and NC are
skipped. The `review-fetch-fail-closed` trap silently skips on a shallow clone (this session's
first clone was depth-1 and the suite reported `skipped=1`).

## 5. Collision matrix and eval results

`python3 scripts/eval.py run --suite all` at HEAD: routing 43/43 (100%), 51 per-skill evals.
The router under test is `classify_prompt` (`scripts/eval.py:279`), a substring/word-trigger
scorer over `MISSION_TRIGGERS` (`:27`) with a specialist override (`:271`). It is not the
description-based router any agent host actually uses, so the score measures agreement between
two hand-written artifacts in the same repo.

36 realistic prompts, analyst-predicted routing vs heuristic:

| Prompt | Predicted | Heuristic | Result |
|---|---|---|---|
| the README lies | clean-sweep | clean-sweep | ok |
| why is this flaky | root-cause / deflake-it | root-cause | ok |
| make CI strict | floor-it | none | FN |
| this breaks on mobile | field-test-it | field-test-it | ok |
| our tests are flaky and I want to know why | deflake-it | deflake-it | ok |
| the login page is slow on mobile | speed-it | speed-it | ok |
| review this PR for accessibility problems | review-it | review-it | ok |
| harden the CI pipeline | floor-it / harden-it | harden-it | ok |
| update the README to match the code | clean-sweep | none | FN |
| upgrade React and fix what breaks | modernize-it | modernize-it | ok |
| refactor the payments module safely | reshape-it | none | FN |
| add tests before we refactor payments | prove-it | none | FN |
| we need SOC 2 evidence for our CI security gates | attest-it | attest-it | ok |
| make the checkout accessible and fast | access-it / speed-it | none | FN |
| close the open issues about performance | clean-sweep / speed-it | speed-it | ok |
| diagnose why the deploy failed last night | root-cause | root-cause | ok |
| ship the feature and make sure it works on a real phone | ship-it / field-test-it | none | FN |
| our Orca docs are out of date | pin-it / clean-sweep | none | FN |
| plan the migration to the new auth provider | map-it | none | FN |
| is this branch safe to merge | review-it | none | FN |
| remove the god object in the API layer | reshape-it | reshape-it | ok |
| find and fix all secrets in the repo | harden-it | harden-it | ok |
| the dependency audit has 40 findings, fix them all | clean-sweep / modernize-it | modernize-it | ok |
| cover the untested payment paths and fix the bugs you find | prove-it | none | FN |
| why does the build fail only in CI | root-cause / deflake-it | none | FN |
| set a coverage floor and enforce it | floor-it | prove-it | **FP** (specialist override on "coverage", `eval.py:61`) |
| prove our app meets WCAG for the audit | access-it / attest-it | access-it | ok |
| submit fixes to the upstream library we depend on | oss-contribute | none | FN |
| make this production-ready | chain | none | FN (expected; no chain route) |
| this test passes locally but fails in CI | deflake-it / root-cause | none | FN |
| the API contract drifted from the docs | clean-sweep | none | FN |
| kill the retry wrappers and make the suite deterministic | deflake-it | none | FN |
| chart a plan for the mobile rewrite | map-it | map-it | ok |
| our quality bar keeps slipping — fix the bugs it let through | floor-it / clean-sweep | floor-it | ok |
| Orca updated and the emulator QA flow broke on device | pin-it / field-test-it | field-test-it | ok |
| red team the checkout on a real device | harden-it / field-test-it | harden-it | ok |

19/36 correct (53%). 16 false negatives, 1 false positive. Sibling collisions the heuristic
cannot see because it returns `None`: review-it vs ship-it on "safe to merge", prove-it vs
reshape-it on "add tests before we refactor", clean-sweep vs pin-it on "docs out of date",
access-it vs speed-it on compound asks. The one measured collision (floor-it → prove-it) is a
direct consequence of `SPECIALIST_MISSIONS` containing both missions while only prove-it owns
the word "coverage".

CI: `.github/workflows/validate.yml:38` runs the routing eval inside an `if: always()` summary
step with `|| echo`, so it can never fail the build. The only gate is
`tests/test_evals.py:43` (`ROUTING_MIN_SCORE = 0.95`) over the curated set.

## 6. Catalog verdict — 17 under the five-point test

The test (`ARCHITECTURE.md:37-41`) is not enforced anywhere: `tests/test_architecture.py:97`
asserts only that a "convergence proof" heading and an "Anti-patterns" section exist. Applying
the test by hand, using the repo's own precedent that audit findings, tracker issues, and false
doc-claims are one mission "even though each source materializes the denominator differently":

| Mission | Unit | State machine | Convergence proof | Ordering | Parking | Verdict |
|---|---|---|---|---|---|---|
| ship-it | slice | build→review→prove→land→release | traceability table on BASE head | foundation serial, slices parallel | WITH-PARKED | stands |
| clean-sweep | finding | remediate-finding | full re-enumeration dry | hot-file chains | DRY-WITH-PARKED classes | stands (the reference shape) |
| harden-it | P0/P1 | audit→PoC→fix→re-attack→re-audit | fresh full re-audit zero unrefuted | PoC routing gate | OPEN-ITEMS | stands (re-attack + quorum refute are unique states) |
| speed-it | hotspot | baseline→profile→fix→re-benchmark | metric contract with confidence | per-journey | OPTIMIZED-WITH-PARKED | stands |
| modernize-it | dep group | expand→migrate→contract | every major current or pinned | compatibility graph | WITH-PINNED | stands |
| prove-it | critical path | characterize→mutate→review→land | mutation-sensitive set | none | COVERED-WITH-PARKED | stands |
| deflake-it | flake | detect→diagnose→fix→ratchet→streak | consecutive streak local and CI at one SHA | streak resets on commit | QUARANTINE | stands |
| review-it | diff at a SHA | pin→axes→aggregate→verdict | every axis reported, lines quoted | none | NO-GO | stands |
| map-it | decision ticket | chart→clear frontier→freeze | verified frozen DAG | HITL per decision | — | stands |
| root-cause | hypothesis | repro→rank→falsify→demonstrate | one survivor with falsification table | serial | INCONCLUSIVE | stands |
| oss-contribute | upstream issue | triage (incl. open PRs)→build→PR-open→follow-up | actionable set dry at PR-open | maintainer-gated alternatives | awaiting-maintainer-merge | stands (terminal differs from clean-sweep) |
| attest-it | obligation | enumerate→evidence→re-derive→VERIFIED/GAP | every obligation dispositioned | none | WITH-GAPS | stands |
| **access-it** | one violation instance | remediate-finding | oracle clean on frozen surface, re-enumerated | structural items serial (a hot-file rule) | human-AT park (a park class) | **merge → clean-sweep source=axe**. All five points match clean-sweep; the only novelty is a park class and an oracle, and "oracle" is not one of the five points |
| **field-test-it** | one device-observed defect | baseline→reproduce→fix→re-verify | on-device revert NC, re-verified at head | none | FIELD-PROVEN-WITH-PARKED | **merge → clean-sweep source=device**. Same argument; the device is the oracle, the pipeline is remediate-finding |
| **pin-it** | one doctrine claim | enumerate→re-witness→classify→patch→prove | every claim receipted or refuted | none | PINNED-WITH-PARKED | **merge → clean-sweep source=doc-claims scoped to runtime/**. The 2026-09-09 audit (`docs/research/…-upstream-adoption-audit.md` §4.1) argues distinctness on "oracle" and "archive of refutations"; neither is one of the five points, and refutation receipts are clean-sweep's `refuted` class |
| floor-it | constraint dimension | detect→freeze→wire→prove-fires→enforce→guard | gate RED on injection, canary PR RED, guard landed | cheapest-first | WITH-PARKED | stands, but the routing collision with prove-it on "coverage" is real |
| reshape-it | module seam | CHARACTERIZE (prove-it's protocol verbatim) → DEEPEN | interface measurement smaller plus pinned mutant still killed | CHARACTERIZE before DEEPEN | WITH-PARKED | stands as a mission; **split its CHARACTERIZE phase into a chain link to prove-it** (`skills/reshape-it/SKILL.md` restates prove-it's protocol and is the second-longest mission) |

Verdict: **14 stand, 3 merge.** If the maintainer wants to keep access-it, field-test-it, and
pin-it, the identity test must gain a sixth point ("the oracle") and ARCHITECTURE.md must
re-argue clean-sweep's three sources under it, because they also differ by oracle. Either the
test is wrong or the catalog is. All three merge candidates are `doctrine-only`, so the merge
costs no evidence.

Splits: none required. ship-it's release state machine is large but the "stop at the highest
authorized state" rule keeps it one mission.

## 7. Competitive position after Phase 1

### 7.1 What is still a moat

Nothing in the shipped landscape combines all four of: a fail-closed gate, a verdict produced by
a session the worker did not spawn, a mandatory negative control, and evidence bound to a
coordinator-frozen contract digest. The closest public analogue (boshu2/agentops) has distinct
author/validator context IDs and content-addressed verdicts but no negative control.
obra/superpowers has an in-session revert-must-fail rule. gstack (v1.84.1, 2026-09-09) now has a
content-hash evidence ledger, a working-tree fingerprint for freshness, fresh-subagent plan
audits, a cross-model Codex pass, and a Stop-hook verify gate that "fails open" — all inside the
producing run. The README's "self-certified within the run that produced them"
(`README.md:31`) is still accurate for gstack and addyosmani, but it understates gstack: it is
now cross-model and hash-bound, and its freshness binding is stronger than this repo's was until
`reviewed_wtree` landed in #251.

### 7.2 What is commoditized

"Independent verification" as a phrase: Claude Code `/verify` and `/code-review` fork context by
default; Codex Auto-review is a separate reviewer agent; Osmani's own L5 text names "separate
implementers and reviewers, separate test runners and QA" as table stakes. The Stop/TaskCompleted
gate mechanism is a public primitive. Hash-bound evidence is arriving (gstack, agentops,
compound-engineering's `verified_merge_sha`).

The uncomfortable conclusion: the one ingredient that is not commoditized — the negative control
— is the one this repo mandates in prose and does not execute in code. The moat exists on paper.

### 7.3 Orca and the packs

Orca is at v1.4.199 (tagged 2026-09-09), near-daily releases. v1.4.199 shipped "make multi-agent
workflows durable", "keep worker lineage across app restart", and "skills: rewrite and trim the
seven non-orchestration guides" — the same day this repo's runtime re-pin (#251) merged.
`runtime/dispatch-lifecycle.md:32` still says receipted sends "exist only in upstream's
unreleased source". pin-it is needed now, and it is `doctrine-only` with no recorded run. None of
the three packs is version-pinned anywhere a validator reads; the adoption audit pins commits in
a research doc only.

### 7.4 Doc truthfulness (clean-sweep phase-one enumeration)

| Claim | Where | Reality |
|---|---|---|
| `head-to-head.txt` sha256 `f40e3f86…` | `demo/negative-control/README.md:50` | Committed file hashes `70d42150…` |
| `attention-budget.md` "is the measured exemplar" | `ARCHITECTURE.md:106` | `runtime/attention-budget.md:27`: "Evidence level: **ASSERTED**" |
| "both are verified to preserve them" (symlink and plugin) | `README.md:365` | Evidence exists for symlink only (`docs/completion/evidence/CF-02-*`); no plugin-install transcript |
| Osmani quote "the level you can safely reach is exactly the level you can cheaply prove" | `README.md:117` | Not found in the cited L0–L5 source; attribution unverified |
| Nine versions in CHANGELOG (0.1.0 → 0.6.1) | `CHANGELOG.md` | Zero git tags; `git tag` is empty |
| "verified, not asserted" | `README.md:32` | §4 |

TODOS.md lists two completed items and no open work while `docs/completion/GAPS.md` carries
DEFER rows (G-09, G-19) and the field-proof plan lists 13 missions to run — TODOS.md is a stale
surface, not a backlog. CHANGELOG `[Unreleased]` is correctly dated (all four new missions
landed after the 0.6.1 cut).

## 8. Prioritized backlog

Each item is scoped for one agent, one PR.

### P0 — the claim is false until these land

1. **Execute the negative control.** Implement `--execute-nc` for `tool: revert`: in a fresh
   worktree at `head_sha`, `git revert --no-commit` the unit's commits (or apply the quoted `hand`
   diff), run the manifest's `commands[]` that carry the bound test, require a non-zero exit, then
   restore and require zero. Fail closed on any tool other than `revert`/`hand` until per-tool
   replay exists. Anchor: `runtime/scripts/verify.py:370`.
2. **Close the waiver lanes to forged text.** A `dark-eligible` or `--no-gh` mutation unit must
   require an executed NC (item 1) — not a corroborated contract — before GREEN. Anchor:
   `verify.py:325-348`.
3. **Add a mutation-class positive control to VF-Bench** that passes only with a real executed
   revert, so "not always-RED" is proven for the class that matters. Anchor:
   `bench/vf-bench/traps/valid-control.json`.
4. **Reword the README.** Replace "verified, not asserted" with the claim the mechanism supports
   today, and move the negative-control sentence at `README.md:286` to "required and read, not
   yet executed" until item 1 ships. Fix the four false claims in §7.4.

### P1 — the honesty and routing mechanisms are hollow

5. **Bind proof tiers to artifacts, not filenames.** Require a run report to carry a manifest
   path plus a `verify.py` transcript whose exit code CI re-derives, or a signed dispatch record.
   Anchor: `scripts/validate.py:347-376`.
6. **Replace the keyword router in the eval with a description-based judge** (headless
   `claude -p` or the agentskills reference scorer) and add the 36 prompts in §5 as fixtures. Gate
   CI on it, not on a summary step. Anchors: `scripts/eval.py:27`, `.github/workflows/validate.yml:38`.
7. **Fix the coverage collision**: give floor-it the "coverage floor / threshold" triggers and
   remove bare "coverage" from prove-it. Anchor: `scripts/eval.py:61`.
8. **Ship the gate on the symlink path.** Either document that symlink installs have no
   completion gate, or add a `settings.json` hook snippet that resolves the repo path. Anchor:
   `hooks/hooks.json:10`, `README.md:313`.
9. **Move `proof`, `autonomy`, `proof_evidence` under `metadata:`** and teach `validate.py` to
   read them there; the current stance (`CONTRIBUTING.md:49`) blocks Claude Code packaging and
   upload and fails `skills-ref validate`. Anchor: `scripts/validate.py:67-80`.
10. **Re-derive the autonomy levels from the source.** Either all 17 are L4 (parallel delegation)
    with scheduled runs at L5, or the README must define its own axis and stop citing Osmani for
    it. Anchor: `README.md:114-123`, every `autonomy:` line.
11. **Enforce the five-point test.** Add a test that requires each SKILL.md to declare
    `unit:`, `state-machine:`, `convergence:`, `ordering:`, `parking:` in a machine-readable block
    and fails on two missions with identical tuples. Then merge access-it, field-test-it, and
    pin-it into clean-sweep sources, or add the oracle as point six and re-argue. Anchor:
    `tests/test_architecture.py:91`.
12. **Run pin-it against Orca v1.4.199** and record the report; `dispatch-lifecycle.md:32` is
    already suspect.

### P2 — hardening and hygiene

13. Reject absolute and out-of-repo artifact paths in `verify.py:110`; require artifacts to be
    tracked at `head_sha` or listed in the integrity inventory, and add an inventory re-check
    script that RESUME and CI run.
14. Tighten `CRIT_ID_RE` (`verify.py:57`) or require JSON `criterion_ids` in every frozen
    contract; `SHA-256`, `PR-12`, `RFC-7519` currently become criteria.
15. `spawn_worker.sh` `danger` profile: require evidence of an ephemeral sandbox (a recipe id or
    hostname check), not only `ORCA_COORD_ALLOW_DANGER=1`. Anchor: `spawn_worker.sh:156`.
16. Add `gitleaks` to `validate.yml`; today it is doctrine in `dispatch-lifecycle.md` only.
17. Pin the three upstream packs and Orca by commit in a machine-read file that a test compares
    against `compatibility:`; the adoption audit's pins live in prose.
18. Add a build step or vendoring so `npx skills add` and copy installs work (inline the composed
    playbooks into `skills/<name>/references/`), then delete the README caveat at `README.md:344`.
19. Split reshape-it's CHARACTERIZE into a `mission-chaining` link to prove-it; the mission is
    124 lines because it restates another mission.
20. Tag releases; nine CHANGELOG versions have no git tags.
21. Replace TODOS.md with a pointer to `docs/completion/GAPS.md` or delete it.
22. Add `fetch-depth: 0` guidance to the vf-bench README; the review-leg trap silently skips on
    a shallow clone.
23. Measure and publish the per-mission load (SKILL.md plus composed docs) in `validate.py`;
    ship-it is ~29.5K tokens against a 5K-token spec recommendation.

## 9. Sources

Repository state: `git rev-list --count origin/main` = 501; 442 commits by the maintainer, 50 by
`ravidsrk`, 9 by Cursor agents. Local gate at HEAD: `validate.py` OK, `eval.py --suite all`
43/43, `unittest` 340 OK (1 skipped on shallow clones), `ruff` clean.

External (fetched 2026-09-10):
- agentskills.io specification and `skills-ref` validator (`ALLOWED_FIELDS` hard error on extras);
  Claude Code skills/plugins docs (packaging rejects unknown keys; plugin cache copies the plugin
  root only); vercel-labs/skills `src/installer.ts` (copies the skill directory alone).
- garrytan/gstack v1.84.1 (`bin/gstack-evidence`, `bin/gstack-wtree`, `bin/gstack-verify-gate`,
  `ship/SKILL.md`); mattpocock/skills v1.2.3; addyosmani/agent-skills 0.6.9; anthropics/skills;
  obra/superpowers 6.3.0; EveryInc/compound-engineering-plugin 3.24.0; boshu2/agentops 3.6.0;
  Claude Code `/verify`; OpenAI Codex Auto-review; critique.sh.
- Addy Osmani, "Agentic Autonomy Levels", addyo.substack.com, 2026-07-03 (L0–L5 verbatim).
- stablyai/orca tags through v1.4.199 (2026-09-09); `skill-guides/orchestration.md`.
- Verification literature: Papadakis et al. 2018 (mutation survey); Just et al. 2014 and
  Papadakis et al. 2018 (mutants vs real faults); Niedermayr et al. 2016 and Vera-Pérez et al.
  2018 (pseudo-tested methods); Knight & Leveson 1986; Ron, Baudry, Monperrus 2026 (N-version
  with agents); Goel et al. 2025 (correlated errors); Panickssery et al. 2024 and Li et al. 2026
  (self-preference, preference leakage); METR 2025, Baker et al. 2025, MacDiarmid et al. 2025
  (reward hacking); Greenblatt et al. 2024 (AI control); Lipsitch et al. 2010 (negative
  controls); Ye et al. 2021 and Le et al. 2018 (patch overfitting); GitHub stale-review dismissal,
  Gerrit patchset votes, in-toto/SLSA subject binding.

## 10. Status at `9afefc667322c43e289051a1fc2b22ae66fb6bbf` (2026-09-10)

The verdict in §1 stands as written, bound to `af8ea89`. This section is a later, dated
re-measurement on branch `claude/orca-fleet-deep-review-nksvxh` — the same instruments, re-run.
Nothing above was rewritten; a review that edits its own findings after the fixes is not a review.

### The two instruments, re-run

**Manifest-gaming attacks (§4).** Same harness, same scratch-clone method. Five attacks that
LANDED at `af8ea89` are now RED:

| ID | At `af8ea89` | Now | What refuses it |
|---|---|---|---|
| A1 fabricated NC, dark-eligible | LANDED | **CAUGHT** exit 2 | the waived-review lane requires an EXECUTED control (`--execute-nc`), plus a commands ledger |
| A2 `--no-gh` forged review + forged NC | LANDED | **CAUGHT** exit 2 | `review.artifact` must reference `head_sha`; commands ledger required |
| A4 `tool: hand`, invented diff | LANDED | **CAUGHT** exit 2 | same executed-control requirement |
| A9 pinned mutant killed, sibling survived | LANDED | **CAUGHT** exit 2 | same |
| A10 artifact outside the repo | LANDED | **CAUGHT** exit 2 | absolute evidence paths refused |
| A11 realistic contract prose ids | GREEN | **GREEN** | unchanged — the tightened id regex is not a false-positive machine |
| positive control: real executed revert | — | **GREEN** exit 0 | the gate is not always-RED |

**Routing (§5).** The 36 realistic prompts: **36/36** (was 19/36 = 53% with the keyword table).
The full fixture suite is 86/86, and the CI floor is ratcheted to 1.0 — a description collision
now reds the build rather than being counted and shrugged at.

**A new bypass, found and closed during the fix.** The first artifact-binding checker accepted a
fabricated `map-it` report that pointed at `ship-it`'s real manifest and inventory: everything
hashed, because the artifacts were real — just someone else's. A run's manifest must now live in
that run's own `docs/runs/<date>-<mission>…/` directory, and one report may prove one mission.

### Backlog disposition

P0 — 1 executed negative control · 2 waiver lanes closed · 3 mutation-class positive control in
VF-Bench · 4 README reworded: **all four landed.**

P1 — 5 proof tiers bound to artifacts · 6 description-based router with the §5 prompts as CI-gated
fixtures · 7 coverage collision · 8 gate on the symlink path · 9 `metadata:` migration · 10
autonomy re-derived · 11 identity test enforced: **all landed.** 12 (pin-it run against Orca
v1.4.199): doctrine re-pinned against the v1.4.199 source, **no bound run report** — so pin-it
stays `doctrine-only`, which is the point of item 5.

P2 — 13 artifact paths + inventory re-check · 14 `CRIT_ID_RE` · 15 danger-profile sandbox evidence
· 16 gitleaks · 17 upstream pins in a machine-read file · 18 bundle for copy installers · 20 tags
· 21 TODOS · 22 vf-bench `fetch-depth` · 23 per-mission load measured, published and capped:
**landed.** 19 (split reshape-it's CHARACTERIZE into a chain link to prove-it): **refuted** —
CHARACTERIZE already delegates to prove-it's protocol by reference rather than restating it, and
reshape-it's declared oracle is the net being live at its own `head_sha`, which a separate chained
run would sever.

### What the fixes cost, said plainly

- **Every proof tier was removed, not gained.** `clean-sweep`, `review-it` and `oss-contribute`
  ran for real, but their artifacts were retained outside this repository, so no gate here can
  re-derive them. `ship-it` kept its artifacts — all five hashes still re-derive at `748b328` —
  but never wrote down the verifier's command line, which its own template asked for verbatim, so
  its recorded outcome is the coordinator's word. The catalog now reads **21 `doctrine-only` / 0 /
  0**. Binding tiers to artifacts did not make the number smaller once; it made it zero, and the
  last one fell to a reviewer's finding on the PR that shipped the binding (§10.1).
- **Activation load grew before it shrank.** The fixes added playbooks and runtime doctrine, and
  `ship-it` reached ~39,600 tokens against §2's measured ~29,500. Deferring phase-scoped reads
  brought the three heaviest to 31,400 / 33,000 / 33,600 and the cap is ratcheted to 34,000 — still
  roughly 7× the spec's per-skill recommendation, and unrestructured everywhere else.
- **The catalog grew from 17 missions to 21**, which is the direction §6 warned about. The
  discipline against it is now mechanical rather than editorial: six declared identity points per
  mission and a build failure when two match.

### 10.1 What the PR's own review found

Seven findings from an automated reviewer on PR #277, all of them accepted. Three are worth
recording here because they are the same class this review was written about — a mechanism that
reads as sound and is not:

- **The executed negative control ran a command the worker chose.** `--execute-nc` (§8 P0-1, the
  fix at the centre of this branch) took `negative_control.command` from the worker-written
  manifest and executed it. A worker could nominate any command that fails under the control and
  passes clean — the gate goes green, the criterion is never run. Now the command must already be
  in the manifest's content-bound `commands[]` ledger (exit 0 at `head_sha`'s tree, `cmd_sha256`
  hashing its own `cmd`), or be supplied out of band as `--nc-command`, which the manifest must
  agree with. **A1's fix had A1's shape.**
- **The proof-tier gate accepted "the body contains the string `verify.py`".** Any prose mentioning
  the verifier satisfied it. Tightened to require the actual invocation against the report's own
  manifest — and the first replacement, `--manifest \S+`, was itself satisfied by the module's
  explanatory prose, which writes `--manifest <path>`. That is what took `ship-it`'s tier: no
  transcript was ever recorded for it.
- **The deny hook claimed a registration nothing performed.** Its header said the dispatcher
  registers it as a `PreToolUse` hook; nothing in the repo does, and on the supervised lane nothing
  can — Orca takes launch args from the host's `agentDefaultArgs` and env does not cross the
  daemon. The claim is gone, `deny-hook.sh --settings <worktree>` prints the registration a host
  pastes, and a test fails if the claim returns while no registrar exists.

The other four: a path-traversal hole in that hook's boundary check (a missing parent plus `..`
prefix-matched the worktree and was allowed), `privacy` declared NEVER_GATE in the playbook but
absent from the executable tuple (it would have auto-gated off after ten quiet reviews), the
agentskills validator installed unpinned in CI, and the secret-scan fixtures already handled by the
baseline. Each fix carries its own negative control; each is tested against the pre-fix version.

### What is still not true

`verify.py`'s soundness still depends on the coordinator owning the environment: on the native
`Stop`/`TaskCompleted` hook the gate runs inside the graded worker, so it is defense-in-depth
there, not a boundary (`docs/verify-gate.md` says so). A8 — a bare working-tree path as
`--contract-source` — is still accepted where the worker sets the env. And one bound self-run is
one; the mechanism is now real, the evidence base behind it is thin.
