# Upstream deep audit — adoption gaps and new-mission proposals

> **Dated snapshot (2026-09-10).** Pinned: orca-fleet `70964b8` (main `af8ea89` + REVIEW.md);
> stablyai/orca HEAD `f2d5711b2d` / tag `v1.4.199`; garrytan/gstack `71f6048e` (v1.84.1.0);
> addyosmani/agent-skills `6ca0cd7` (0.6.9); mattpocock/skills `3cca18b` (v1.2.3+9). Full-history
> clones; every claim anchored to `file:line` on both sides. Extends the 2026-09-09 audit; corrects it
> where it was wrong. The four per-source reports with the complete matrices are in
> [`2026-09-10-upstream-audit/`](2026-09-10-upstream-audit/).

**Question asked:** orca-fleet was built from these four sources; they have moved since 2026-07-13.
Has orca-fleet adopted what it should have, and do the sources now imply missions the catalog lacks?

**Short answer:** upstream barely moved since the 2026-09-09 pins (gstack +1 commit, Orca +27 with no
orchestration change, the other two at the pinned commit). The gap is not *this week's* drift; it is
that the 2026-09-09 audit covered the headline items only. Skill by skill, orca-fleet has adopted the
*methodology* from all four sources well and the *mechanisms* from none of them. Of the machine
mechanisms upstream ships (evidence ledgers, trust envelopes, deny hooks, floor guards, description-based
routing evals, receipted sends, fleet-liveness projections), orca-fleet has zero as code. That is the
same finding REVIEW.md reached from the inside: the doctrine layer is complete and the mechanism layer is
thin. Four mission candidates survive the five-point test with a denominator no existing mission owns
and an oracle a worker cannot narrate: `migrate-it`, `oncall-it`, `absorb-it`, `document-it`. Twelve
others were considered and are recorded as rejected or as playbooks.

## 1. Headline findings

1. **The 2026-09-09 audit's quick wins landed (15 of 20), and its runtime section is already wrong.**
   `#250`/`#251` shipped redaction, grilling rounds, destructive-path validation, the two review lenses,
   keep-or-revert, ask-resume, nested depth, retro categories, doc-sync, `reviewed_wtree`, and the droid
   flag. Not landed: Addy's privacy operating rules, gstack egress receipts, gstack dispatch-recovery
   scope guards, Addy runbook doctrine, Tier-3 behavioral evals. Worse: the audit pinned Orca at
   `65631e4`, which is **not an ancestor of `v1.4.199`** (merge-base `6108ce6`). The shipped binary
   lacks `3a801d213d` (readiness on observed turn start), so the readiness semantic the audit described
   is main-only. (`2026-09-10-upstream-audit/orca.md` §2.2, §2.4)
2. **`runtime/dispatch-lifecycle.md:32` is false and `spawn_worker.sh` is now contrary to the guide.**
   Receipted sends (`terminal send --wait-submit`, `input_accepted → turn_started`) are released in
   v1.4.199 (`06a607a1d7`, 2026-09-06). The script's blind re-Enter loop (`spawn_worker.sh:369-386`)
   re-submits a prompt that `dispatch --inject` already submitted; the guide says "never resend on
   silence". The worker contract's `worker_done --outcome succeeded|failed` and `--dispatch-capability`
   appear in zero orca-fleet files. Three runtime doctrine claims are WRONG, eight STALE, four PARTIAL
   against the shipped source (§7).
3. **Every source ships a machine mechanism orca-fleet has only as prose.** gstack: content-bound
   evidence ledger, tracker trust envelope, fail-loud diff scope, PreToolUse deny hooks, one-way-door
   registry, completion-audit classifier. Addy: floor guard reference implementation, TF-IDF routing eval
   over real descriptions with owner-pairwise negatives and collision detection, headless behavioral
   evals. Orca: `worker-list` liveness/attention/`nextAction` projections, typed refusals with
   `nextSteps`, automations `--precheck`. Matt: the promised `hitl-loop.template.sh`. Ranked in §3.
4. **Three previously "current" adoptions are stale in ways that matter.** map-it's Prototype ticket
   encodes the pre-2026-07-10 disposal semantics (upstream: capture on a throwaway branch, shareable HTML);
   `compound-learn.md` carries 4 of 7 retro categories (missing the three steering-hygiene ones);
   `risk-review.md`'s security lens has the destructive-path rule but not its two stated limits, and no
   privacy lens at all (`security-and-hardening/SKILL.md:378-397`, merged 2026-08-14).
5. **The catalog has a consistent hole: stateful data migration.** `modernize-it` refuses it
   (`SKILL.md:29-33` "Not for stateful DB schema/data migration across deploys"); no other mission takes
   it; three sources converge on the same expand/dual-write/backfill/switch/contract protocol
   (`deprecation-and-migration:164-190`, gstack `review/specialists/data-migration.md`, matt `to-tickets:40`).
   It is the strongest new-mission candidate (§4.1).
6. **The oracle question REVIEW.md raised is now load-bearing.** Five of the nineteen candidates
   (`drive-it`, `screen-prove-it`, `onboard-it`, `polish-it`, `triage-it`) are "remediate-finding with a
   different oracle" — the same shape REVIEW.md found in access-it, field-test-it, and pin-it. The catalog
   must decide once whether the oracle is the sixth identity point. §4.3 recommends the decision.

## 2. What moved, per source

| Source | Window 2026-07-13 → pin | Since the 2026-09-09 pin | Adoption scorecard at HEAD |
|---|---|---|---|
| **stablyai/orca** | v1.4.152 → v1.4.199: Runs + `worker-start` (#9925, 07-27), legacy takeover (07-30), `worker-release` (08-05), `--model/--effort` (08-07), `terminal read --screen` + `agentWait` + unsupervised lanes (08-21), nested depth enforced (08-29), typed refusals (09-08), durable workflows + receipted sends + fleet projections + native-chat workers + guide rewrite (09-09) | 27 commits, **0** orchestration-surface; but the *release* branch diverged from the pin (§1.1) | 12 runtime claims CURRENT, 8 STALE, 3 WRONG, 4 PARTIAL, 3 UNVERIFIABLE; 5 of 8 Orca skills unridden or prose-only (`computer-use`, `orca-linear`, `orca-per-workspace-env`, automations beyond one verb, artifacts) |
| **garrytan/gstack** | 52 commits, v1.60 → v1.84.1: egress receipts (08-13), content binding `wtree` + evidence ledger + tracker trust envelope + fail-closed hooks (08-16), token-load carve (08-27), simplification lens + shortcut debt ledger (08-29), spawned-session contract (08-30/09-01), dispatch recovery (09-01), Aside-first browsing (09-06), impeccable pre-pass (09-08) | 1 commit (model defaults) | Of 61 skills: 19 ADOPTED-CURRENT, 5 ADOPTED-STALE (`ship` evidence gate, `land-and-deploy` cleanup, `document-release` method, doc-sync recovery), 8 NOT-ADOPTED (`qa`/`qa-only`, `devex-review`, `document-generate`, `health`, plan lenses, `cso` triage protocol), 6 DELIBERATELY-EXCLUDED, rest N/A. Of 86 `bin/` tools: **0 mechanisms adopted as code** |
| **addyosmani/agent-skills** | 0.6.4 → 0.6.9: constraint-driven-development + `/constraints` (08-08), privacy rules (08-14), floor-guard reference impl (08-28), plan-clobber guard (08-28), perf backend depth (08-27), rate-limit + destructive-path + entry-point attribution (08-31/09-04) | 0 commits | Of 25 skills: 13 ADOPTED-CURRENT, 4 ADOPTED-STALE (api idempotency, perf backend, privacy, two destructive-path caveats), 4 NOT-ADOPTED (`observability-and-instrumentation`, `interview-me`, `source-driven-development`, ADR protocol), 4 EXCLUDED. Evals: Tier 1 ahead, Tier 2 behind in design, Tier 3 absent. Hooks: 0 adopted |
| **mattpocock/skills** | 156 commits (not 169): grilling rounds (07-16), prototype capture (07-10), writing-for-agents (07-28), phase-boundary tree + six skills removed (08-05), Redact (08-06), skills stop calling user-invoked skills (08-15), `implement-spec` + `retro` in-progress (08-21/24) | 0 commits | Of 37 skills: 13 adopted in some form, 3 stale (`prototype`, `retro` 4/7, `resolving-merge-conflicts` outcome-only), 14 NOT-ADOPTED (incl. `wizard`, `to-questionnaire`, `setup-matt-pocock-skills` tracker indirection, triage state machine details, `hitl-loop.template.sh` promised at `diagnose.md:21` and absent) |

### 2.1 Corrections to the 2026-09-09 audit

| It said | Fact |
|---|---|
| Orca pinned at `65631e4` describes the current contract | `65631e4` and `v1.4.199` are sibling branches; the readiness semantic it documents is unreleased |
| "receipted sends exist only in upstream's unreleased source" (`dispatch-lifecycle.md:32`) | Released in v1.4.199 (`06a607a1d7`) |
| `DEFAULT_TUI_AGENT_ARGS` "no longer exists" | Moved to `src/shared/tui-agent-launch-defaults.ts:10`; still exists |
| mattpocock "169 commits", "planning-stack rename" post-fork | 156 commits; the rename landed 2026-07-02, pre-fork |
| "Matt and Addy adoptions are mostly healthy" | Matt: 13/37 adopted, 14 untouched; Addy: observability entirely unadopted, privacy rule still missing after #250 |
| `gstack-verify-gate` excluded as "name collision only" | Also fails open on every absence and allows after three re-entries (`bin/gstack-verify-gate:8-9`, `:195-206`) — the vacuous-gate class floor-it forbids |

## 3. Mechanism gaps, ranked

Machine parts upstream ships that orca-fleet states in prose. Ranked by how much of REVIEW.md's
"verified, not asserted" gap each closes, then by effort. Each is one agent, one PR.

| # | Mechanism | Source anchor | orca-fleet today | Adopting takes | Closes |
|---|---|---|---|---|---|
| 1 | **Tracker trust envelope** — the only sanctioned path for issue/PR/CI text into context; NFKC + zero-width detection; fetch failure = non-zero with no envelope; CI scanner fails raw reads | gstack `bin/gstack-issue-guard:3-19`, `lib/tracker-guard.ts` | `sandbox-policy.md:84` doctrine, restated in four missions; nothing fences anything | `runtime/scripts/guard_text.py --source issue\|pr\|ci\|web`; enumeration commands route through it; contract test greps for raw `gh issue view` | REVIEW.md criterion 12 (injection surface) |
| 2 | **Floor guard** — diff-scoped detection of suppressions, stubs, skips, removed assertions, lowered thresholds; exit 0/1/2 | Addy `references/floor-guard.md` (2026-08-28) | `floor-it/SKILL.md:78` "land `check_constraints`-style validation" — no script | `runtime/scripts/floor_guard.py` (stdlib, ~120 lines); run in `verify.py` off-worker, not in the builder loop | Partially REVIEW.md #255/#256: a `.skip` cannot hide behind a forged `negctrl.txt` |
| 3 | **Content-bound evidence ledger** — a runner records `{cmd, cmd_sha256, exit, wtree, commit}`; a check grades FRESH/STALE/MISSING | gstack `bin/gstack-evidence:3-35`, `bin/gstack-wtree` (62 lines, MIT) | `evidence-manifest.md:117` "tests pass at that exact SHA — coordinator-run, not verify.py" | `runtime/scripts/evidence-run.py` + `wtree.sh`; `verify.py check_commands` requires ≥1 exit-0 record whose `wtree` equals `head_sha^{tree}`; **fail-closed**, unlike upstream's advisory check | Turns the clean-env re-run from doctrine into a machine check |
| 4 | **Description-based routing eval** — TF-IDF over real frontmatter, owner-pairwise negatives, description-collision detection ≥0.75, `--min-rank1 95` gating CI | Addy `evals/run-evals.js:60-384` | `scripts/eval.py:27` keyword dictionary; CI step cannot fail | ~120 lines stdlib; pass `--threshold 0.95` in `validate.yml` | REVIEW.md #260 |
| 5 | **Fleet-liveness projections** — `worker-list` `projection.liveness` / `attention.requiresAction` / literal `nextAction.argv` | Orca `worker-list-method.ts:271-290`, `orchestration-fleet-projection.ts:51-118` | `liveness-resume.md:22-26` teaches the inverted authority (`worker-show` as truth) + pane-reading folklore | Rewrite WATCH: after 3 empty waits → `worker-list --run --json` → execute `nextAction.argv`; `--terminal-state reclaimable` as the end-of-run gate | Removes the dual-writer class the 2026-07-15 run hit |
| 6 | **Receipted sends** — `dispatch --inject --json` already returns `prompt.stages`; `terminal send --retry-request --wait-submit` replays | Orca `terminal-send.ts:8,19-22`, `orca-cli.md:176-180` | `spawn_worker.sh:369-386` blind Enter loop | Delete the loop; read `prompt.stages`; `outcome_unknown` branch (inspect, never respawn) | Correctness against v1.4.199 and the next release |
| 7 | **Typed refusals + `nextSteps`** | Orca `orchestration-dispatch-refusal-contract.ts:8` | `spawn_worker.sh:309` whitelists four codes; `task_not_found`/`inject_rejected`/`runtime_error` fall to "spawn failed" and get retried | Branch on `error.code`, surface `data.nextSteps` | Same |
| 8 | **One-way-door registry** — the one-way list as data + a keyword net; unregistered destructive phrasing can never be auto-decided | gstack `scripts/question-registry.ts`, `bin/gstack-question-preference --check` | `gate-classification.md:36` one sentence | `runtime/one-way-doors.json`; `verify.py` fails a DECISIONS line whose class is not `one-way` but whose text matches the net | Mis-classified gates |
| 9 | **Fail-loud diff scope** — SCOPE_* flags; exit 2 `SCOPE_ERROR=unmatched\|no_base` so "could not look" is never a clean gate-off | gstack `bin/gstack-diff-scope:6-24` | `risk-review.md:15-17` prose; a shallow clone dispatches no lens and records a legitimate-looking zero | `runtime/scripts/diff_scope.py`; `SCOPE_ERROR` parks the review | Scheduled review-it sweeps |
| 10 | **PreToolUse deny hooks** for `rw` workers — the Never list + a worktree boundary, with a test proving the deny is honored | gstack `careful/SKILL.md:43-79`, `freeze/SKILL.md:77-96`; their own "deny meant allow" history (`CHANGELOG.md:1763`) | `hooks/hooks.json` wires Stop/TaskCompleted only; `rw` runs with the bypass flag and nothing below the model | `runtime/scripts/deny-hook.sh` registered by `spawn_worker.sh` per profile; advisory, stated | REVIEW.md #269 partially |
| 11 | **Automations `--precheck`** + `runs` history + `--host runtime:<env>` | Orca `automations.ts:44-63,101-115` | `mission-scheduling.md` names one `create` shape | Policy edit: precheck = "is the denominator non-empty?"; `runs --id` = cross-run anti-inflation input | Scheduled runs on empty backlogs |
| 12 | **Session-kind export** — `ORCA_SESSION_KIND=spawned` set by the dispatcher, recorded in the ledger header, checked on DECISIONS lines | gstack `bin/gstack-session-kind` (only the echoed STATUS line arms auto-choose) | `gate-classification.md:87-90` rule, no component sets or checks it | `spawn_worker.sh` export; `preflight.py` writes `KIND:`; RESUME rejects a taste auto-resolve under `KIND: interactive` | Auto-pick under the wrong session kind |
| 13 | **Completion-audit classifier** — every criterion tagged DIFF-VERIFIABLE / EXTERNAL-STATE / CROSS-REPO / CONTENT-SHAPE; UNVERIFIABLE handled per item | gstack `ship/sections/plan-completion.md:70-106` | `CODE_CLOSED`+`VERIFY_AT_SCALE` exists but only if a worker notices | `verification_mode` on each frozen criterion; `verify.py` treats `external-state` as by-construction parked, never green; do **not** adopt upstream's free-text "Y" as evidence | Silent external-state criteria |
| 14 | **Manifest redaction check** — scan the manifest and every `artifacts[]` path for credential shapes; HIGH fails the unit | gstack `lib/redact-engine.ts`; Addy `diagnose` Redact | `diagnose.md:5-14` doctrine; `verify.py` never scans | `verify.py check_redaction` via gitleaks (already a dependency) | SHA-pinned manifests are permanent |
| 15 | **Decisions writer** — `decisions.py append\|active\|tally` validating class/id/why | gstack `lib/gstack-decision.ts` | DECISIONS.md is read mechanically by `risk-review.md:22-28` (a parser without a writer) | ~80 lines | Deterministic adaptive lens gate |
| 16 | **Egress receipts** (coordinator-side) — content-free hash-chained record before every off-repo write | gstack `lib/egress-receipt.ts` | none; integrity inventory hashes artifacts only | `runtime/scripts/egress.py write\|verify` before PR open/comment/issue close/deploy | attest-it's "what left the machine" |
| 17 | **Ownership marker before delete** — a worktree may be retired only if it carries a marker the fleet minted | gstack `lib/staging-guard.ts:1-30` | `dispatch-lifecycle.md:155-160` guards in prose | one line in `spawn_worker.sh` + one check | WT_CLEAN safety |
| 18 | **`hitl-loop.template.sh`** | matt `diagnosing-bugs/scripts/` (44 lines) | promised at `diagnose.md:21`, absent | copy + test | A promise the repo makes and does not keep |
| 19 | **Plan-clobber guard** | Addy `planning-and-task-breakdown:150-155` | `liveness-resume.md:103` guards RESUME only | ≤4 lines in `ledger-contract.md`: a ledger with unmet flags and a different SOURCE digest is another run's state | Overwriting a live ledger |
| 20 | **Headless behavioral evals** (catalog tooling, never `proof:` evidence) | Addy `run-evals.js:386-560`; pressure fixtures | 17 `evals.json` files with `assertions[]` nobody executes | `eval.py --behavioral <mission>` via `claude -p` in a fixture repo | REVIEW.md #260 |

## 4. New-mission proposals

Nineteen candidates surfaced across the four audits. Each was run through the five-point test
(`ARCHITECTURE.md:37-41`: unit of work · per-unit state machine · convergence proof · ordering/isolation
· parking) against the nearest of the 17, with the same standard REVIEW.md §6 applied to the existing
catalog. The result splits three ways.

### 4.1 Recommended — four missions with a denominator no mission owns and an oracle a worker cannot narrate

#### `migrate-it` — a stateful schema/data change landed across deploys, old and new code valid at every step

| Point | Definition |
|---|---|
| Outcome | expand → dual-write → backfill → switch reads → contract, each phase deployed and baked; data parity proven; the old shape has zero readers before it is dropped |
| Unit | one migration *phase* of one table/shape (a deploy-gated step), not a slice |
| State machine | PLAN (phase list; `down` per phase) → EXPAND[deploy+bake] → DUAL-WRITE[deploy+bake] → BACKFILL (batched, throttled, resumable; parity probe) → SWITCH-READS[deploy+bake] → ZERO-READERS window → CONTRACT[separate deploy, one-way human] → MIGRATED |
| Convergence proof | per phase: `down` written **and run** (negative control: `up`+`down` → schema identical to base, `git diff` empty on the dumped schema); parity probe (row counts + sampled hashes) GREEN; old-code-vs-new-schema and new-code-vs-old-schema both green. Terminal: parity 100% on the frozen table set, old-shape readers = 0 over the declared window (pasted telemetry), contract PR merged |
| Ordering / isolation | strictly serial phases; never two migrations on one table in flight; the migrations directory is a merge chain; each phase reuses `release.md`'s states |
| Parking | bake / zero-reader windows needing prod telemetry → `CODE_CLOSED` + `VERIFY_AT_SCALE`; CONTRACT is one-way human; a failed backfill batch resumes, never restarts |
| Terminals | `MIGRATED` · `MIGRATED-WITH-PARKED` · `ABANDONED` (down path exercised) |
| Why not one of the 17 | ship-it's unit is a slice with a test oracle and one pass through the release machine; here the oracle is parity + zero readers, the release machine runs ≥3 times, and a deploy revert does not revert data. modernize-it hands it off explicitly. Fails points 1, 3, 5 against both |
| Worker recipe | Addy `deprecation-and-migration:164-190`; gstack `review/specialists/data-migration.md` as the review lens (already `NEVER_GATE` in `risk-review.md`); matt `to-tickets:40` expand–contract slicing |
| Reasons to reject | a chained ship-it can express the phases today; the missing piece is the parity/zero-reader oracle, which could be a playbook first; bake windows make it a multi-day mission with mostly-parked terminals (the shape that killed the predecessor's campaign engine); no run has yet hit modernize-it's handoff |
| Verdict | **Build**, but ship the `data-migration` playbook first (§5) and promote to a mission when a chained run shows the phases need their own ledger |

#### `oncall-it` — the surface is operable: on-call can see, alert on, and act without reading the source

| Point | Definition |
|---|---|
| Outcome | every production path in a frozen set answers its on-call questions from telemetry alone; every alert is symptom-based, runbook-linked, and has been fired |
| Unit | one production path (endpoint / job / external dependency) × its 2–4 on-call questions |
| State machine | FREEZE path set + questions (human gate; the questions are the denominator) → INSTRUMENT (structured events, correlation ID, entry-point field; RED/USE with bounded labels; spans) → ALERT (symptom-based, two severities, justified threshold) → RUNBOOK (three-line minimum at the repo's convention) → TEST-FIRE → INDUCE (a staging failure; a fresh worker with **no source access** must name the failing component from telemetry only) → OPERABLE |
| Convergence proof | each question maps to a quoted signal; alert receipt; runbook at the linked path; the source-blind worker's manifest names the failing component; negative control: remove the instrumentation on a throwaway branch → the blind worker cannot locate it (RED); no PII in sampled logs |
| Ordering / isolation | instrument → alert → runbook → induce per path; paths parallel; shared logger/exporter config serialized |
| Parking | no staging or alert channel → `CODE_CLOSED` + `VERIFY_AT_SCALE`; cardinality-cost decisions → `needs-human` |
| Terminals | `OPERABLE` · `OPERABLE-WITH-PARKED` |
| Why not one of the 17 | ship-it's `observe` is a post-deploy canary that adds no instrumentation and whose oracle is change-vs-baseline; speed-it's oracle is a budget; harden-it's an exploit; root-cause consumes telemetry. Fails 1, 3, 4 |
| Worker recipe | Addy `observability-and-instrumentation` (+ `observability-checklist.md:82-90` pre-launch gate); gstack `canary` for the post-deploy loop |
| Reasons to reject | the blind-diagnosis oracle costs a second worker per path and a drivable staging env; half the value is one `release.md` line ("≥1 symptom alert with runbook, test-fired") plus the `instrument` playbook; without SLOs every threshold is a human gate |
| Verdict | **Build after the playbook.** ship-it can reach `DEPLOYED_AND_VERIFIED` today with zero instrumentation on the new path; the playbook closes that first, the mission owns brownfield "make it operable" asks |

#### `absorb-it` — every inbound contribution is landed with authorship, refuted with receipts, or parked with a named ask

| Point | Definition |
|---|---|
| Outcome | a maintainer's open inbound-PR queue is drained: absorbed (cherry-picked with `Author:` preserved, amended where review finds a gap, regression test proven RED on the pre-absorption base), superseded-by-main (closed citing the commit), duplicate (closed citing the winner), or parked awaiting the contributor |
| Unit | one inbound PR (its diff + linked issue) — someone else's diff, not a finding |
| State machine | ENUMERATE (open PRs, paginated; linked issues; T0) → CLASSIFY {absorbable · superseded · duplicate · needs-contributor · out-of-scope} with a reproduction of the claimed defect on current main → ABSORB (apply preserving authorship; wave amendment as a separate fleet commit; DCO/CLA checked) → RECEIPT (the PR's regression test, or one the fleet writes, RED on a scratch worktree of the pre-absorption base, GREEN on the absorbed head) → build-blind REVIEW → LAND (one PR per absorbed contribution against BASE) → CLOSE (inbound PR closed with landing SHA + credit line; linked issues closed with the same receipt) → re-ENUMERATE until dry |
| Convergence proof | re-enumeration finds zero PRs outside a terminal class; every absorbed PR has preserved authorship on the landed commit (`git log --format=%an` asserted), a RED-on-base / GREEN-on-head receipt with SHAs, a merged SHA on BASE, and the inbound PR closed linking both |
| Ordering / isolation | overlapping inbound PRs (the same bug fixed twice by different contributors — gstack's tracker shows this weekly) form an absorption chain: the first lands, the rest re-classify against the new main, never merge blind; hot-file chains as in `merge-serialization.md` |
| Parking | `needs-contributor` (CLA/DCO, unanswered question — one follow-up round then park), `design-disagreement` (maintainer one-way), `cannot-reproduce` (refuted only after the batch gate) |
| Terminals | `ABSORBED` · `ABSORBED-WITH-PARKED` |
| Why not one of the 17 | clean-sweep's unit is a finding you fix from scratch; oss-contribute is the outsider with no merge rights. absorb-it differs on unit, state machine (absorb + amend + credit), convergence (queue dry **and** authorship + receipt per landing), ordering (overlap chains between inbound diffs), and parking (`needs-contributor`) — four of five |
| Worker recipe | gstack's own weekly practice (`CHANGELOG.md:275`, `:335`, `:896-898`: "absorbed with authorship preserved", "closed with receipts", "regression test proven red on a scratch worktree of the prior release"); matt `code-review` for the build-blind review; `upstream-contribution.md` etiquette inverted for maintainer-side replies |
| Reasons to reject | authorship preservation conflicts with `dispatch-lifecycle.md:105` "author = the maintainer, no trailers" — needs an explicit carve-out and per-repo squash policy; value concentrates in high-volume repos; a reasonable person could file it as `clean-sweep source=inbound-prs` if "absorb" counts as a fix strategy |
| Verdict | **Build.** It is the one candidate with demand evidence from a source's own release process, and this repo (155 merge commits, Cursor-agent PRs, Greptile threads) is a self-run target |

#### `document-it` — every public-surface entity is documented in the quadrants it needs, and every claim is true

| Point | Definition |
|---|---|
| Outcome | the public surface (commands, flags, config keys, endpoints, exported modules, skills) has a Diataxis coverage map with zero critical gaps; every generated or updated doc's claims are verified against the tree; diagrams reference only entities that exist |
| Unit | one (public-surface entity × quadrant) cell of the coverage map |
| State machine | EXTRACT the surface at BASE head (a script, not a reading) → MAP coverage per quadrant by grep-able evidence → FREEZE the gap list (critical = zero coverage; the human bounds which entities merit tutorial/explanation) → WRITE (one cell per unit; reference first, from code archaeology) → CLAIM-VERIFY (every factual claim bound to `file:symbol` or a run — the clean-sweep doc-claims oracle) → build-blind REVIEW (voice, reachability from README) → LAND → RE-MAP → VERDICT |
| Convergence proof | the map re-derived at the final head shows zero critical gaps and every frozen cell filled; every claim in a landed doc has a verified anchor (negative control: rename the anchored flag → the claim check goes RED); diagram entities cross-reference clean; every doc reachable from README/AGENTS.md |
| Ordering / isolation | reference cells before how-to/tutorial cells for the same entity; docs touching one file form a chain |
| Parking | `explanation-needs-author` (the "why" is not in the tree), `tutorial-not-warranted` (human-declined), `diagram-needs-human` |
| Terminals | `DOCUMENTED` · `DOCUMENTED-WITH-PARKED` |
| Why not one of the 17 | `clean-sweep source=doc-claims` removes false claims and says "Generating NEW docs is not this mission" (`SKILL.md:56-58`); ship-it's doc-sync unit covers the wave's diff only. Unit (a coverage cell vs a false claim), convergence (zero gaps vs zero false claims), parking (author-knowledge) differ |
| Worker recipe | gstack `document-generate:467-700` (Diataxis partition, reference-first), `document-release:545-606` (coverage map, diagram drift, CHANGELOG/VERSION rules); Addy `documentation-and-adrs:36-100` (match the repo's ADR convention, never delete, supersede); matt `domain-modeling` for glossary |
| Reasons to reject | "documented" quality is taste; the machine-checkable part (cell filled, claims anchored, discoverable) may be thin enough for a `floor-it` dimension plus a clean-sweep source; agent-written tutorials are the "LLM-written context hurts" class `compound-learn.md:3-5` cites; public-surface extraction is per-language and is the hard part |
| Verdict | **Playbook first (`doc-coverage`, §5), mission on demand.** The coverage map and claim verification are unfakeable; the writing is not |

### 4.2 Folded — five candidates that are a different oracle on an existing shape

| Candidate | Source | Shape it shares | Fold into |
|---|---|---|---|
| `drive-it` (web journeys driven in a real browser; gstack `qa`/`qa-only`) | gstack | field-test-it: baseline → reproduce → fix → re-verify at head with a revert control; differs only in oracle (driven browser vs device) and lane parallelism | field-test-it oracle tier `BROWSER` + the `browser-drive` playbook (§5) |
| `screen-prove-it` (desktop app through `orca computer`, `verified`/`unverified` action tiers) | Orca | same as above with the OS accessibility tree as oracle | field-test-it oracle tier `DESKTOP` |
| `onboard-it` (documented getting-started executed on a clean environment per persona, TTHW budget; gstack `devex-review`, Addy docs) | gstack, Addy | same shape; oracle = fresh sandbox execution | field-test-it oracle tier `CLEAN-ENV`, budget from speed-it's metric contract; needs the `sandbox` lane (§3 #10, Orca per-workspace recipes) |
| `polish-it` (design-rule catalog + impeccable deterministic pre-pass; gstack `design-review`) | gstack | access-it: deterministic rule oracle on a frozen surface, taste parked to a human | access-it `oracle=` slot (design catalog beside axe) |
| `triage-it` (tracker tickets classified and stated without fixing; matt `triage`, Orca `orca-linear`) | matt, Orca | clean-sweep source=tracker, report-only; differs on two of five (no code, no PRs) — the review-it/ship-it margin | clean-sweep `--report-only` lane + `triage-state` and `linear-enumeration` playbooks |

### 4.3 The decision the catalog must make once

REVIEW.md §6 found access-it, field-test-it, and pin-it to be clean-sweep with a different oracle. §4.2
adds five more of the same shape. The catalog can go one of two ways, and the choice decides the size
of the catalog for good:

- **Oracle is not an identity point** (the five-point test as written). Then access-it, field-test-it,
  pin-it merge into clean-sweep as sources (`axe`, `device`, `runtime-doctrine`), and drive-it,
  screen-prove-it, onboard-it, polish-it, triage-it are sources or lanes too. Catalog: 14 + the four in
  §4.1 = **18**, every one with a distinct unit *and* proof shape.
- **Oracle is the sixth point** (`ARCHITECTURE.md` amended). Then the three stand and field-test-it
  becomes the oracle-tiered "prove it on the target" mission (`DEVICE` / `EMULATOR` / `BROWSER` /
  `DESKTOP` / `CLEAN-ENV`), access-it gains `oracle=`, and clean-sweep's own three sources must be
  re-argued under the new point (they also differ by oracle). Catalog: 17 + 4 = **21**, three of which
  are oracle families.

Recommendation: the first. It is what the README already argues for clean-sweep ("one mission even
though each source materializes the denominator differently"), it keeps the identity test enforceable
as a tuple comparison (REVIEW.md #265), and it turns the oracle into a typed field (`oracle:` in the
manifest, with `verified`/`unverified` tiers as Orca's computer-use already models) instead of a reason
to fork a mission. Either way, `ARCHITECTURE.md` must say which.

### 4.4 Rejected — recorded so they are not re-proposed

| Candidate | Source | Rejected as | Reason |
|---|---|---|---|
| `retire-it` (deprecate → migrate consumers → zero usage → remove) | Addy | mission-shaped but telemetry-bound | every proof depends on production usage counters; `-WITH-PARKED` is the normal terminal; single-surface sunsets are a clean-sweep finding; keep as a `migrate-it` tail |
| `erase-it` (personal-data inventory, purpose, retention, export/delete proven) | Addy | attest-it with a GDPR catalog + clean-sweep via deferral carry | needs prod-like data plumbing and a legal owner per run; the privacy lens (§3) is the cheaper first move |
| `sandbox-it` (danger lanes provably created, used, harvested, destroyed) | Orca | runtime policy + script, not a user outcome | "destroy what you created" is hygiene; becomes `runtime/scripts/sandbox_lane.py` (doctor → create → pair → place `--on` → harvest → destroy with receipts) under `sandbox-policy.md`; REVIEW.md #269 |
| `hand-off-it` (fault injection against the fleet: kill the coordinator, adopt the Run, zero re-done work) | Orca | `bench/`/`tests/` territory | tests orca-fleet, not the user's repo; its value is a `proof:` tier for `liveness-resume.md`, which a pin-it run's probes can deliver |
| `verify-on-target` (one change proven on N hosts via `--on`) | Orca | CI matrix does it cheaper | value only where a host cannot be a CI runner; federation is the youngest Orca surface (three mail-filing fixes in the 48 h before the tag) |
| `name-it` (one name per concept; glossary + rename reconcile + avoid-list lint) | matt | floor-it lint dimension + decide-and-freeze ADR rule | nearly all HITL; a cosmetic oracle drives rename churn |
| `orient-it` (a stranger can navigate: probe suite of cold `ro` sessions, no-op test per steering line) | matt | compound-learn + re-probe | the oracle is an LLM run and never `dark-eligible`; the ETH finding says WRITE is where damage happens |
| `unblock-it` (the human-owed queue packaged as wizards/questionnaires and verified complete) | matt | `human-handoff` playbook (§5) | mostly an artifact generator; verification half is item-specific; pointless unattended |
| `automate-it` (recurring loop specified, installed via `orca automations`, first-fire observed) | matt, Orca | `mission-scheduling.md` edit | most loops are missions already; collapses to one CLI line plus `--precheck` |
| `record-it` (ADR currency) | matt, Addy | `record-decision` playbook | the "why" lives in human memory; DETECT has no oracle |
| `contract-it` (public-interface contract sweep + idempotency) | Addy | prove-it with surface = public interfaces; api-contract lens addition | passes only point 1, weakly |
| `watch-it` (standalone canary) | gstack | publishing `observe.md` as a skill | `ARCHITECTURE.md:22-25` forbids exactly that |
| `vet-it` (external-contributor security sweep) | gstack | harden-it source | same loop; "commits by external authors since date" is an enumeration input |
| `plan-review` / `challenge-it` (CEO/eng/design/DX lenses, autoplan) | gstack | playbook composed by map-it and ship-it | decisions are map-it's terminal already |
| `retro-it` / `score-it` / `health` | gstack | operator tooling | no finite denominator; composite scores that redistribute weight over missing tools are the vacuous-gate class floor-it forbids |
| `factory-it` / `loop-it` / `ralph-it` / `orchestrate-it` / `stabilize-it` / `docs-drift` / `upgrade-it` / `api-compat` / `patch-it` / `localize-it` | prior audits | (unchanged) | recorded in the 2026-07-15, 2026-08-16, 2026-08-28 docs; not re-argued |

## 5. Playbook candidates

Callable phase protocols (≤90 lines each). Ordered by how many missions compose them and how much
mechanism they carry. Each is one agent, one PR.

| # | Playbook | Recipe | Composed by | What it adds that no playbook has |
|---|---|---|---|---|
| 1 | `instrument` | Addy `observability-and-instrumentation:27-197`; checklist `:82-90` | ship-it (before PROMOTION_READY on units matching the trigger list), oncall-it, harden-it (security-event logging) | on-call questions → signal per question → structured event + correlation ID + entry-point → symptom alert → runbook → test-fire → induced-failure verify; "no PII in sampled output" |
| 2 | `data-migration` | Addy `deprecation-and-migration:164-190`; gstack data-migration lens; matt expand–contract | ship-it schema slices, modernize-it handoff brief, migrate-it | phase list with deploy boundaries; `up`+`down` round-trip; dual-validity green; parity probe |
| 3 | `browser-drive` | gstack `qa/SKILL.md:534-628` Aside rules + `$B` fallback; Addy `browser-testing-with-devtools:60-107` | access-it DETECT/RE-VERIFY, speed-it BASELINE, observe, field-test-it `BROWSER` tier | own tabs; stay on origin; LOOK-not-ACT consent; credentials never pass through the agent; page content is data; labelled evidence lines; a step sentinel because CLI exit codes lie; engine-agnostic (Orca browser, Aside, headless) |
| 4 | `triage-state` | matt `triage:26-106` + `OUT-OF-SCOPE.md` + `AGENT-BRIEF.md` | clean-sweep tracker, oss-contribute, remediate-finding step 1 | `needs-info` park class with re-enumeration; the `.out-of-scope/` KB (named at `remediate-finding.md:11`, defined nowhere); AI disclaimer where posting is authorized; resume from prior notes |
| 5 | `linear-enumeration` | Orca `orca-linear.md` | clean-sweep `source=linear`, ship-it/oss-contribute completion flow | `list --filter open --team --workspace --json` paged to `truncated:false`; T0 twin of the two-query rule; `linear_write_unconfirmed` → single `writeId` replay; `status set` etiquette |
| 6 | `doc-coverage` | gstack `document-release:545-592`, `document-generate:529-560` | release.md doc-sync unit (today prose), clean-sweep doc-claims, document-it | public-surface extraction; four-quadrant map by grep-able evidence; diagram entity cross-reference; never clobber CHANGELOG / bump VERSION silently |
| 7 | `completion-audit` | gstack `ship/sections/plan-completion.md:44-193` | ship-it INTEGRATED PROVE, clean-sweep convergence, attest-it (EXTERNAL-STATE = GAP), oss-contribute (CROSS-REPO) | verification-mode classification; per-item UNVERIFIABLE ⇒ `CODE_CLOSED`+`VERIFY_AT_SCALE` with a named command, never a human "Y" |
| 8 | `triage-findings` | gstack `cso/SKILL.md:613-702`; `review-army.md:27-67` | harden-it VERIFY (quorum), risk-review security lens, review-it | confidence gate; hard-exclusion and precedent lists; parallel independent verifiers that receive `file:line` only (anti-anchoring); VERIFIED/UNVERIFIED/TENTATIVE; variant analysis |
| 9 | `human-handoff` | matt `wizard` + `to-questionnaire` + wayfinder Task ticket + `AGENT-BRIEF.md` | every PARK (harden-it, floor-it, attest-it, map-it, field-test-it, ship-it Lane 0, OPS queue) | artifact + recipient + VERIFY-COMPLETE observation for each human-owed item |
| 10 | `research-brief` | matt `research` + wayfinder research tickets + a verification leg | map-it, decide-and-freeze VALIDATE, modernize-it INVENTORY, attest-it, pin-it LOAD | output contract, `ro` profile, "primary source" rule (0 hits in orca-fleet today), citation spot-check upstream lacks |
| 11 | `resolve-conflict` | matt `resolving-merge-conflicts:6-14` | merge-serialization step 3, modernize-it lockfile chains, oss-contribute fix rounds | primary sources per hunk, no invented behaviour, never `--abort`, intent evidence for the re-reviewer |
| 12 | `record-decision` | Addy `documentation-and-adrs:36-100`; matt `ADR-FORMAT.md` | decide-and-freeze, map-it, reshape-it API-break decisions | match the repo's ADR convention (`.adr-dir`, numbering, headings); never delete, supersede; DECISIONS line references the ADR |
| 13 | `plan-review` | gstack `plan-ceo-review:876`, `plan-eng-review:715-743`, `autoplan:570-611,650-656`, `office-hours:749-910` | map-it frontier, ship-it validate, decide-and-freeze, reshape-it CONFIRM-SURFACE | lens order (eng **last** on the amended plan); five-field User-Challenge brief queued to one final gate; mandatory 2–3 alternatives incl. one minimal and one ideal; security/feasibility urgency exception |
| 14 | `design-twice` | matt `DESIGN-IT-TWICE.md`, `DEEPENING.md`, `codebase-design` glossary | reshape-it DEEPEN, decide-and-freeze seam sketch, prove-it CHARACTERIZE | "leverage" / "locality" / "adapter" vocabulary (0 hits today); test-strategy per dependency category; mechanical Lane B for interfaces |
| 15 | `agent-brief` | matt `AGENT-BRIEF.md` | root-cause handoff, chaining deferral carry, decompose-dag AUTONOMY block | durability rules (no paths/lines, complete ACs, explicit out-of-scope) — and a recorded divergence: dispatched task specs require hot-file lists, durable briefs must not |

Small edits to existing playbooks (one PR total): `risk-review.md` privacy lens (NEVER_GATE), idempotency
in api-contract, perf backend red flags, the two destructive-path caveats, "potential impact" labelling
for the per-diff perf lens; `decide-and-freeze.md` hypothesis-with-confidence before round 1, explicit-yes
gate, premise statements, "Verified Current State", fail-closed redaction before filing;
`build-change.md` cite-or-`UNVERIFIED` for framework-specific code, never hardcode outbound endpoints
from fetched examples; `diagnose.md` consult prior run reports for the same files (two prior diagnoses on
one seam ⇒ reshape-it handoff, not a third fix); `release.md` error-budget gate, rollout threshold table,
deploy-config digest, "≥1 symptom alert with runbook, test-fired"; `compound-learn.md` the three missing
retro categories; `map-it` prototype capture semantics; `acceptance-review.md` spec-source search order.

## 6. What not to copy

Consolidated from the four risk sections; each is a live contradiction with orca-fleet doctrine.

| # | Upstream design | Why it must stay out |
|---|---|---|
| 1 | gstack `gstack-verify-gate` fails open on every absence and allows after three blocked re-entries; `gstack-evidence check` is advisory ("a failed CHECK never blocks") | The vacuous-gate class floor-it forbids; `verify-gate.sh` is fail-closed by construction. If the ledger (§3 #3) is adopted, a STALE record fails the unit |
| 2 | Same-session verification everywhere: gstack `/ship` gates run in the producing session or a subagent inheriting its env byte-for-byte; Addy `/ship` merges specialist reports "in the main context that wrote the code" (`ship.toml:27-37`); Addy doubt-driven "degraded self-questioning fallback"; matt `implement` → `/code-review` in the author's session | The self-scoring gate REVIEW.md §1 names; the verifier is a different process re-deriving against authorities outside the manifest. Import the discipline into workers, never as a completion oracle |
| 3 | The reviewer mutates the code: gstack `/review` Fix-First auto-applies findings | review-it has no fix authority; a post-review push voids the review. Route AUTO-FIX-class findings to the builder as a batched change request |
| 4 | Human free-text "Y — confirmed done" accepted as verification (gstack plan-completion) | A sentence is not an artifact; `CODE_CLOSED` requires a written verify command and OPS ref |
| 5 | Scope expansion by principle (autoplan "auto-approve expansions <1 day", "bias toward action"; ETHOS "boil the ocean") | The denominator is frozen; growth is scope creep. Keep only their carve-out (User Challenges never auto-decided, destructive options never auto-chosen), which orca-fleet already has |
| 6 | Composite scores as verdicts (`quality_score` = 10.0 when specialists were skipped; `/health` redistributes weight over missing tools; "CLEARED by ≥1 clean review within 7 days") | A number that looks complete when part of the check did not run |
| 7 | Review freshness by commit count ("0–3 commits since review → CURRENT") | orca-fleet voids on any content change; the content-identical class is already adopted |
| 8 | Autonomous merge of the promotion (`/land-and-deploy` "DO IT") | BASE→default is a one-way human gate |
| 9 | `Co-Authored-By` trailers and WIP auto-commits (gstack ship / checkpoint mode) | Author = maintainer, bisectable, no trailers |
| 10 | Learnings auto-applied with self-assigned confidence (gstack `learn`); SessionStart injecting a 193-line router (Addy); worker self-compaction at 75% (Addy `context-engineering`) | `compound-learn.md:40-41` (human approves each line); instruction budget; workers are disposable — CONTEXT HANDOFF then respawn, never self-summary |
| 11 | `simplify-ignore.sh` rewrites source files on disk with placeholders during a session (Addy hook) | Under build-blind review and SHA-bound manifests this is evidence tampering by construction; a crashed Stop leaves a dirty worktree `WT_CLEAN` refuses |
| 12 | Reviewer must "always include at least one positive observation" (Addy personas) | Praise-instructed reviewers anchor toward approval; orca-fleet writes the expectation before the diff |
| 13 | Refactor inside the TDD loop (Addy) vs refactor in review (matt); `DEEPENING.md` "delete old tests" | The documented router conflict — pack per worker, never harmonize; deleting old tests removes the oracle reshape-it pins |
| 14 | matt `prototype/<name>` and `research/<name>` standing branches; `claude --bg` handoffs; `git-guardrails` regex that blocks `--force-with-lease` | Branches a fleet never retires; unsupervised processes outside `worker-list`; blocks a mandated flag |
| 15 | Host-specific recovery (`run_in_background: false` census) imported as doctrine | Orca dispatches through `worker-start`; import the shape (deadline → stop → reconcile orphaned commits → explicit failure record) and the census idea, not the flag |
| 16 | Tier-3 behavioral evals grade the execution trace | Fine as catalog tooling; never `proof:` evidence — completion is never graded on a trace |
| 17 | gstack skill preambles of 430 shared lines; 900–1,900 lines per skill | Any playbook in §5 is written from the mechanism, not transcribed; the 90-line cap holds |

## 7. pin-it pre-cut backlog (run it now)

The Orca report's drift matrix is the claim inventory a pin-it run needs; the full table with every
`file:line` on both sides is in `2026-09-10-upstream-audit/orca.md` §3. Summary of what a run against
an installed v1.4.199 must re-witness, in order (items 1–6 are each one receipt away and need no
remote host):

| # | Claim | Verdict vs source | Probe |
|---|---|---|---|
| 1 | `worker-start` exits 0 only when ready (`dispatch-lifecycle.md:18`) | CURRENT at v1.4.199 (ready = write accepted); **flips next release** to `outcome_unknown` on unobserved turn start (`3a801d213d`) | `worker-start` per roster agent; record `state`, `turnStart`, `stage`; add an `outcome_unknown` branch to `spawn_worker.sh` (inspect via `nextCommands`, never respawn) |
| 2 | `dispatch --inject` needs a submit Enter + heartbeat loop (`spawn_worker.sh:369-386`) | **WRONG** — inject submits; `--json` returns `prompt.stages`; "never resend on silence" | Read the receipt; delete the loop; `terminal send --retry-request --wait-submit` for replay |
| 3 | Worker contract: `worker_done` requires `--outcome`; sends carry `--from`/`--dispatch-capability`; `--report-path` typed flag; `worker_done` omits `--to` | **WRONG by omission** — 0 hits in `runtime/`, `skills/`, `playbooks/` | Add to every mission's dispatch preamble and `evidence-manifest.md:14` |
| 4 | `check --types` filters the Delivery (`orca-dag-semantics.md:46-49`); `merge_ready` to a group is rejected (`merge-serialization.md:12-13`) | **WRONG** — `--types` is the wake condition only; only `worker_done`/`heartbeat` reject groups | Mixed-batch probe; scratch-Run `send --to @all --type merge_ready`; rewrite the conductor loop to process the whole batch before `--ack` |
| 5 | `worker-show` is the per-worker truth (`liveness-resume.md:22-26`) | **WRONG** — `worker-list projection.liveness` is the fleet verdict; `worker-show` is PTY-only; states `outcome_unknown` and `unverifiable` missing | Rewrite WATCH around projections (§3 #5) |
| 6 | Refusal codes `task_not_startable\|nested_worker_depth_exceeded\|consumer_fenced\|dispatch_inactive` (`spawn_worker.sh:309`) | PARTIAL — also `task_not_found`, `inject_rejected`, `runtime_error`, all with `data.nextSteps` | Branch on `error.code`; surface `nextSteps` |
| 7 | `task-create` does not validate `--deps` (`liveness-resume.md:63-65`) | **WRONG** since #9925: throws `Dependency task <id> must belong to run <run>`; the failed-dep strand half is CURRENT | `task-create --deps '["bogus"]'` → archive the refutation |
| 8 | `gate-resolve` injects the resolution into the next dispatch preamble (`gate-classification.md:14-15`) | STALE — injection exists only in the retired scheduler path | `gate-create` → `gate-resolve` → `dispatch-show --preamble`; if absent, the coordinator carries the resolution into the task spec by hand |
| 9 | `ro` avoids `worker-start` because it "would append the YOLO flag" (`spawn_worker.sh:281-283`) | PARTIAL — depends on the host's `agentDefaultArgs` profile; a manual-mode host launches prompting workers | Read `launch.effective` and the pane argv per agent; record the host permission mode in the ledger header |
| 10 | `mission-scheduling.md` create shape | CURRENT; `--precheck`, `--timezone`, `--missed-run-grace-minutes`, `--reuse-session`, `--host runtime:<env>`, `runs` unadopted | Policy edit |
| 11 | `pm.py:73` keys on `_heartbeat` | CURRENT by accident (deprecated alias) | Key on `_keepalive` |
| 12 | Roster excludes `cursor` (`spawn_worker.sh:31,115`); `terminal wait` result never read (`:362`) | STALE; the script fails closed on `wait.satisfied:false` only because the CLI also sets exit 1 | Add cursor; read `satisfied` |

Also: pin-it's LOAD step (`skills/pin-it/SKILL.md:64-65`) must enumerate `--references` and load each
`--reference` — the compact guide is a kernel; the seven references are where the worker contract,
recovery, and legacy-migration rules live.

## 8. Sequenced plan

Priorities follow REVIEW.md's: P0 closes a false claim, P1 closes a mechanism gap, P2 is hygiene or a
new outcome. Effort is one agent-day unless stated.

**P0 — false doctrine and the promises already broken**
1. Fix `dispatch-lifecycle.md:32`, `liveness-resume.md:22-26,44-46,63-65`, `orca-dag-semantics.md:46-49`,
   `merge-serialization.md:12-13`; delete `spawn_worker.sh`'s re-Enter loop; add `--outcome`/
   `--dispatch-capability`/`--report-path` to every dispatch preamble (§7 items 2–5, 7). This is a pin-it
   self-run: file it under `docs/runs/` and advance pin-it's tier honestly.
2. Privacy lens in `risk-review.md` (the #250 miss); the three missing retro categories; map-it prototype
   capture semantics; `hitl-loop.template.sh` (promised, absent).

**P1 — mechanisms (§3 #1–#10)**
3. `guard_text.py` tracker trust envelope + contract test.
4. `floor_guard.py`, wired into floor-it GUARD and `verify.py`.
5. `evidence-run.py` + `wtree.sh` + `verify.py check_commands` (fail-closed).
6. `eval.py` re-based on frontmatter descriptions; CI gates on it (REVIEW.md #260).
7. WATCH rewritten around `worker-list` projections; `outcome_unknown` branch; typed refusals.
8. `one-way-doors.json` + keyword net; `diff_scope.py`; `deny-hook.sh` for `rw` workers with a
   proves-it-denies test; `ORCA_SESSION_KIND` export.

**P1 — playbooks that missions already need (§5 #1–#6)**
9. `instrument` + one `release.md` line; `data-migration`; `browser-drive`; `triage-state`;
   `linear-enumeration`; `doc-coverage`. Then the small-edit PR.

**P2 — catalog**
10. Decide §4.3 in `ARCHITECTURE.md` and enforce the identity test as a tuple (REVIEW.md #265).
11. `absorb-it` (self-run target: this repo's inbound queue). `migrate-it` after one chained run.
    `oncall-it` on the first brownfield ask. `document-it` if `doc-coverage` shows the gap list is
    large enough to need a ledger.
12. Remaining §3 items (#11–#20); `docs/research/REJECTED.md` seeded from §4.4 so the next audit does
    not re-argue them; `runtime/pins.json` for Orca and the three packs (REVIEW.md #271).

## 9. Sources

Clones (full history): `stablyai/orca` `f2d5711b2d` (tags through `v1.4.199`), `garrytan/gstack`
`71f6048e`, `addyosmani/agent-skills` `6ca0cd7`, `mattpocock/skills` `3cca18b`. Per-source reports with
complete inventories, timelines, adoption matrices, mechanism analyses, candidate arguments, and risk
tables: [`2026-09-10-upstream-audit/orca.md`](2026-09-10-upstream-audit/orca.md),
[`gstack.md`](2026-09-10-upstream-audit/gstack.md), [`addyosmani.md`](2026-09-10-upstream-audit/addyosmani.md),
[`mattpocock.md`](2026-09-10-upstream-audit/mattpocock.md). Prior orca-fleet research consulted:
`2026-09-09-upstream-adoption-audit.md`, `2026-08-28-forward-roadmap-and-defensibility-plan.md`
(rejected candidates), `2026-08-16-addy-latest-delta-plan.md`, `2026-07-15-addy-orchestration-gap-analysis.md`,
`REVIEW.md` at `70964b8`. GitHub issues for `stablyai/orca` and `garrytan/gstack` were not reachable
from this session; demand signals come from CHANGELOGs, TODOS, and design docs in the clones.
