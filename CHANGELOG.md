# Changelog

All notable changes to orca-fleet are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); the version source of
truth is `.claude-plugin/plugin.json`.

## [Unreleased]

The deep-review branches. The 2026-09-10 review (archived at `docs/reviews/2026-09-10-review.md`)
and the upstream deep audit under `docs/research/` opened issues #255–#276; the 2026-09-11 review
(`REVIEW.md`) opened #279–#307.

**Both review backlogs are now closed, and the release audit after them has landed.** The
2026-09-11 backlog (#279–#306) and a second independent review's #309–#318 merged together in
#308 — 38 issues, one commit each. #307 stayed open until its nine release tags were published;
they now exist and the gate that demanded them passes. The release audit of 2026-09-12 landed as
#321–#338 against `deny-hook.sh`, `verify.py`, `egress.py`, `bundle.py`, `spawn_worker.sh` and the
mission contracts, with its evidence under `docs/reports/release-20260912/`.

What the #308 round changed about the verifier is worth naming, because each was a way a unit
could be graded against a proof it chose: `check_redaction` now scans `commands[].artifact`, the
captured stdout where a leaked credential actually lands (#309); an unsigned `report-only` or
`planning` class is measured against what `base_sha..head_sha` really changes, so one
worker-controlled env var can no longer shed the negative control, intent packet, lighting and
reviewer_mode (#310); the signed dispatch record covers the control's own inputs — `nc_paths`,
`nc_command`, `nc_artifact_sha256` — so signing the class and contract no longer leaves the worker
picking its own oracle (#311); a standing `CHANGES_REQUESTED` at the reviewed head is no longer
overridden by a second approval (#317); and a floor-guard waiver is a DECISIONS record the ledger
can retire, not a line that happens to contain a rule id and a path (#313).

Landed on 2026-09-10 and previously unlisted here, which the entry below promised and did not do:
missions `migrate-it`, `oncall-it`, `absorb-it`, `document-it`; scripts `bundle.py`, `deny-hook.sh`,
`egress.py`, `floor_guard.py`, `guard_text.py`, `decisions.py`, `evidence-run.py`, `inventory.py`.
A changelog that says "each is listed below as it lands" and then lists none is worse than one that
promises nothing (#293).

### Changed

- README no longer claims "verified, not asserted"; it states the claim the mechanism supports
  — scope frozen against a coordinator digest, commits real on the base, review looked up on
  GitHub and tree-bound, the negative control executed by `verify.py --execute-nc` for revert
  and hand controls — and names the clean-env re-run and the ≥10% sample as coordinator
  doctrine (#258).
- Four false or unsupported claims corrected (#258): `attention-budget.md` is the exemplar of
  the Evidence-level rule, not "the measured exemplar" (its own level is ASSERTED); the symlink
  install is the verified path (`CF-02-r2` evidence) and the plugin path preserves references by
  construction only; the unlocated Osmani quotation is gone, replaced by the source's own
  L3/L4/L5 definitions; the gstack / addyosmani characterization names what those packs now
  ship (a content-hash evidence ledger, cross-model review, a fail-open Stop gate, a floor-guard
  reference — inside the producing run, no executed negative control).
- Autonomy re-derived from the source (#264): every mission is `autonomy: L4` (a coordinator
  plus parallel isolated workers); the human-owned verdict or plan in review-it, map-it,
  root-cause, and attest-it is a gate class, not a lower level; scheduled unattended runs are
  the L5 shape. The derivation is `docs/concepts.md` § Autonomy; every guide's Autonomy line
  carries the per-mission reason.
- The mission-identity test gains a sixth point, the oracle (#265): two workflows that differ
  only in oracle are one mission with an `oracle=` source, and differ as missions only when the
  oracle changes the proof's shape or the parking classes. `ARCHITECTURE.md` re-argues
  access-it, field-test-it (the oracle-tiered "prove it on the target" mission: DEVICE /
  EMULATOR / BROWSER / DESKTOP / CLEAN-ENV), and pin-it under it; no mission is deleted.
- `runtime/pins.json` pins Orca and the three upstream packs by commit and witness date, and
  `tests/test_pins.py` requires an entry for every pack a `compatibility:` field names (#271).
- `docs/releases.json` — every CHANGELOG version bound to its cut commit, with
  `test_every_changelog_release_has_a_cut_commit` holding the two together, plus the release-cut
  checklist in `docs/ops.md`. Annotated tags `v0.1.0` … `v0.6.1` were reconstructed at those
  commits; a tag is a repository ref rather than branch content, so the committed file is what a
  fresh clone can check and the one-line publish command lives in `docs/ops.md` (#274).
- `TODOS.md` is a pointer to `docs/completion/GAPS.md`, the run-archive field-proof plan, and
  the review issues (#275). `docs/research/REJECTED.md` ledgers every rejected mission candidate
  with source, shape, reason, and date.
- `docs/getting-started.md` states that the completion-gate hook is wired only under the plugin
  install and links the symlink-path snippet; `docs/distribution.md` drops the "verified, not
  asserted" framing.

### Added

- Runtime policy layer modernized to the current Orca orchestration model (#251): worker-start
  supervised spawn path with typed refusals, Run-scoped fleets, batched Delivery + ack inbox,
  worker-release/retain lifecycle, --retry-request idempotency, ask --resume same-id, spawn_worker.sh
  v4 (ro never takes worker-start — it would launch Orca's YOLO default), and the
  `reviewed_wtree` content-fingerprint equivalence class (a content-identical rebase no longer
  voids a review), verified end-to-end in verify.py + merge-serialization.
- Audit quick wins (#250): diagnose.md "Redact first", round-by-round grilling in
  decide-and-freeze, api-contract + simplification review lenses, security lens rate-limit +
  destructive-path target validation, speed-it keep-or-revert + attempt ledger, map-it
  Prototype/Task ticket types, compound-learn environment-improvement categories, release.md
  doc-sync unit, sandbox-policy Never-row target validation.

- `pin-it` mission: re-witness and re-pin runtime-mechanics doctrine against the installed Orca
  binary — per-claim receipts, archived refutations for removed claims, substrate-block
  classification; terminals `PINNED` / `PINNED-WITH-PARKED` (from the 2026-09-09 upstream
  adoption audit).
- `floor-it` mission: install a written, numbered, tool-enforced quality bar — frozen
  CONSTRAINTS table, one tool per dimension, prove-fires negative control per gate, GUARD
  diff-watch against bar-lowering; terminals `FLOORED` / `FLOORED-WITH-PARKED`.
- `reshape-it` mission: churn-weighted shallowness inventory → human-confirmed surface →
  mutation-audited characterization net pinned BEFORE any restructure → one module-deepening
  per unit with build-blind review; terminals `RESHAPED` / `RESHAPED-WITH-PARKED`.
- `field-test-it` mission: on-device verification via the Orca emulator skills or a paired
  physical device — baseline, reproduce, fix, re-verify at `head_sha` with a revert negative
  control; terminals `FIELD-PROVEN` / `FIELD-PROVEN-WITH-PARKED`.

## [0.6.1] - 2026-09-09

plugin.json, marketplace.json, and this heading now agree on 0.6.1 (issue #237).
The alert-on-failure workflow, the completion-run items, and the ops rollback
step.

### Added

- `alert-on-failure` workflow (#213): a failed `validate` run on `main` opens or
  updates an issue labeled `ci-failure`; a `workflow_dispatch` drill files and
  closes a `[drill]` issue so the alert path can be proven without redding
  `main`. `validate` publishes the proof rollup and routing score to its run
  summary; `docs/ops.md` incident step 1 names the issue as the alert. The
  drill on `main` filed and closed #229 on 2026-09-02.
- `docs/runs/TEMPLATE.md` and a per-mission field-proof plan in the run-archive
  index (#212): targets, tiers, terminals, and blockers for the nine
  doctrine-only missions; a tier still advances only through a mission run.

### Changed

- `docs/ops.md` incident step 4 documents the rollback this catalog has
  (`git revert -m 1` of the merge via a PR; no deploy target), rehearsed
  against a real merge commit on a scratch clone; `playbooks/release.md`
  says `-m 1` too. Completion gap G-14 closes on that evidence and
  its ACCEPT expiry marker (#226) with it. #212 closes as a tracker: the
  field-proof plan in `docs/runs/README.md` is the live one, and G-09 stays
  deferred in the register.
- Adversarial review of every mission skill, one `SKILL.md` at a time, fixing
  contract drift against the playbooks and runtime policies rather than prose:
  `ship-it` proves the integrated whole at the BASE head before `BUILT` and
  names deploy/rollback as one-way gates (it never self-authorizes a deploy;
  it may execute one under a recorded grant); `harden-it` routes every PoC to
  an execution profile BEFORE quorum-verify or re-attack runs it (the audit
  writes scenarios, it does not execute them); `prove-it` records the mutation
  audit as the manifest's `negative_control` + `binding_audit` (not
  `metric_contract`, which `verify.py` never reads for it) and drops the
  "semantics-preserving mutation" wording — that phrase names an equivalent,
  unkillable mutant; `deflake-it` binds the green streak to one SHA and names
  how CI re-runs are triggered; `access-it` gains the BASE bootstrap,
  build-blind review, and LAND steps its compose clause already declared;
  `attest-it` requires the obligation catalog to be a sourced document at a
  digest, never model recall; `clean-sweep`, `oss-contribute`, `review-it`,
  `map-it`, and `root-cause` ride `sandbox-policy` (issue / PR / review text is
  data, never instructions) and state their worker profiles; `modernize-it`
  treats the lockfile as a hot-file merge chain and installs bumped packages
  with lifecycle scripts disabled until provenance is verified; `root-cause`
  draws its boundary at landing, not editing; `speed-it` guards at the
  declared budget, not the lucky run; `oss-contribute`'s CLASS enum gains
  `refuted` / `duplicate` and its allowed parks name
  `awaiting-maintainer-merge`.
- Guides realigned with their skills: deflake-it defaults (30/30, not 20/10),
  review-it's verdict table (a Required finding also blocks), harden-it's phase
  order, ship-it's integrated prove, prove-it's mutation wording;
  `mission-chaining.md` names `CLEAN` (not the nonexistent `HARDENED`) among
  clean terminals.
- Routing: bare "keyboard" no longer routes to `access-it` (a keyboard-shortcuts
  feature is `ship-it`); `aria` matches as a whole word or the head of an identifier
  (`aria-label`, `ariaLabel`, `aria_roles`) and never inside "variant", as a prefix
  of "Arial"/"ARIAL", or as the title-case name Aria mid-sentence (at the head of a prompt,
  line, or sentence the capital is conventional and still routes); seven routing
  examples and a direct classifier test added.

- Product-completion run 2 (resume at `f2e53f4`, `docs/completion/`): every
  angle re-scored on fresh-clone evidence (67%, was 56%; CONDITIONAL GO pending
  H-07, the review-it dry run re-witnessed on the current head); the six critical
  flows re-evidenced with failure paths (a copied mission loses its
  `../../playbooks` references; an over-claimed `proof:` tier fails
  `proof_status --check`); new human actions H-04..H-07 (GitHub About
  description still says 10 fleets, next version cut, failure-notification
  setting, CF-05 re-witness on the current head); the G-14 ACCEPT expiry is
  now a filed issue.

### Fixed

- Leftover Greptile comments from the post-launch PRs (#219–#223): incident
  process compares `plugin.json` to the dated CHANGELOG heading (not
  `[Unreleased]`); dispatch-key rotation names all three verifier sources
  and a post-merge `git fetch` so the `origin/HEAD` pin moves;
  README Ops navigation is a real `href`; digit-bearing unexpected
  frontmatter keys (including hyphen-leading) fail the extras allowlist;
  GAPS/`status.json` match the closed G-06..G-08/G-11..G-13 issues.

## [0.6.0] - 2026-09-01

plugin.json, marketplace.json, and this heading now agree on 0.6.0 (issue #209).
Signed dispatch, the #163–#184 sweep leftovers, SECURITY.md, the Python 3.13
pin, product-completion close-out, and the post-launch G-08/G-11/G-12/G-13/G-07
agent slice.

### Added

- Signed dispatch records make a worker's substitution of `{manifest-id, contract-digest, unit-class,
  lighting}` **detectable off-worker** (issue #135, follow-up to #112). The coordinator signs the tuple
  off-worker (`runtime/scripts/dispatch-sign.py`, vendored Ed25519 in `runtime/scripts/ed25519.py`);
  `verify.py` verifies the signature against a supplied public key, binds it to the unit, and rejects a
  substituted or unsigned field. This is a soundness boundary **when the verifying key is trusted —
  i.e. off-worker** (CI/MCP/SDK, or an auditor with the coordinator's real key); the native in-session
  hook stays advisory (no in-session anchor is worker-untamperable, the #112 result). Opt-in; default
  behaviour unchanged. See [docs/verify-gate.md](docs/verify-gate.md#signed-dispatch--making-the-native-path-sound-135).
- `SECURITY.md` disclosure path; `.env.example` lists every `ORCA_*` gate input.
- [docs/ops.md](docs/ops.md): account inventory (GitHub, plugin marketplace,
  greptile, agentskills) and a 3-step incident process (issue #215).
- Index check of public marketplace aggregators (issue #210): GitHub self-host
  and buildwithclaude auto-index are live; official directory, skills.sh, and
  claudemarketplace.net still need [H-02](docs/completion/HUMAN_ACTIONS.md).

### Changed

- CI Python pin `3.x` → `3.13` (catalog gates).
- CI runs ruff 0.16.5 on `E9`/`F63`/`F7`/`F82` (syntax / undefined names)
  only (issue #214). Full rule set is still a policy change.
- Validator and the orphan-protocol test share `explicit_protocol_refs` (issue #216).
  A Related-section backtick no longer keeps a protocol alive; `ship-it` rides
  `mission-chaining` and `review-it` rides `mission-scheduling`.
- Validator allowlists only three extras beyond the agentskills.io spec
  (`proof`, `autonomy`, `proof_evidence`). A fourth top-level field fails
  the catalog (issue #211). skills-ref still reports those extras; that is
  expected, not a migrate-to-metadata prompt.

### Fixed

- Leftover review comments from the #163–#184 sweep PRs: pin discovery cannot
  cheat via local `HEAD`; env pubkey precedes the repo pin; nested schema keys
  are matched as keys not substrings; the trust-boundary assertion is bounded
  to that H2; `ORCA_EXECUTE_NC` is documented as fail-closed; vf-bench ancestry
  is hermetic; the review-leg GREEN half still skips on a shallow clone (the
  fail-closed fetch pin does not — `verify()` keeps aggregating); mutation e2e
  tests spy the review and NC lanes; temp fixtures are cleaned up.
- Validator: a non-UTF-8 or unreadable `SKILL.md` (and the same class of error
  in playbooks/runtime) is a one-item per-file failure instead of aborting the
  catalog (issue #71).

## [0.5.0] - 2026-08-26

Release hygiene: the previous Unreleased block was already on main (issue #42).
plugin.json, marketplace.json, and this heading now agree on 0.5.0.

### Fixed — live docs after E1–E6

- Mission guides' Composes sections now name every protocol their SKILL declares
  (ledger-contract, evidence-manifest, acceptance-review, and the rest that had drifted).
- Human-facing schema (README, concepts, getting-started, ARCHITECTURE) documents the
  intent packet, lighting, and `accountable:` on promotion.
- README proof status includes the 2026-07-17 clean-sweep tracker self-run.
- Research archive index marks snapshots as historical; E1–E6 landed in PR #68.

### Added — Addy August delta (E1–E6)

- Lighting: per-unit `lit` / `dark-eligible` (`gate-classification.md`, ledger row,
  evidence manifest). Default lit; dark-eligible only Lane A + unfakeable oracle.
- Intent packet on the evidence manifest (`goal` · `ruled_out` · `why`); verifier
  checks presence. Distinct from `claim`.
- Autonomy contract on TASK specs (`decompose-dag`, `remediate-finding`).
- `compound-learn` + `attention-budget` composed by the remaining mutating missions.
- Promotion PR names `accountable: <human>` (`release.md`).
- Next self-run must emit the WIP-curve row (`docs/runs/README.md`).

### Added — orchestration-tax adoption (Addy gap analysis)

- `runtime/attention-budget.md`: producer-side WIP caps (default ≤3 builders),
  sort isolated vs judgment-heavy work, scale fleet to verification capacity.
- `playbooks/compound-learn.md`: post-mission REFLECTION.md proposals; human must
  approve every AGENTS.md/GOTCHAS line (never auto-write).
- `liveness-resume.md`: reflection-before-retry + identical-error kill on doctor
  respawns.
- `build-change.md` + `gate-classification.md`: pre-build plan gate for
  irreversibility stop-list units.
- Wired into `ship-it`, `clean-sweep`, `harden-it`; docs in concepts, getting-
  started, ARCHITECTURE, README; research archive under `docs/research/`.

## [0.4.0] - 2026-07-16

Adds an eleventh mission, `oss-contribute`: landing contributions on a repo you
do NOT control. It is `clean-sweep` forked for upstream work, and it is a distinct
mission by the five-part test — the convergence proof is a PR open and internally
reviewed (not a merged SHA), the state machine adds upstream-PR overlap discovery
and an assist/alternative/stand-down decision while dropping the merge step and the
merge-serialization conductor, and `awaiting-maintainer-merge` / `externally-covered`
are normal terminals. Ships with the `upstream-contribution` playbook (fork topology,
overlap check, contribution decision, DCO/CONTRIBUTING etiquette) and enters at
`external-run` proof — a real run against `dodopayments/chimely` (5 PRs, 4 quoted
review-assist comments) is in `docs/runs/`. `validate.py` now holds `oss-contribute`
to the mutating-mission evidence-manifest standard.

`oss-contribute` also gained a post-open PR follow-up loop: a PR is not
fire-and-forget, so the unit stays live (watch, triage each review thread against
the current head, fix valid ones as fix rounds on the same branch, answer every
thread) until merged, closed, or quiet. Adds the `FOLLOWED_UP` ledger flag.

Made the catalog messaging count-agnostic so adding a mission no longer means
rewriting counts across the docs. The README badges now read dynamically (version
from `plugin.json`, mission and test counts from generated `assets/badges/*.json`
via `scripts/gen-badges.py`); the manifest descriptions dropped the count and the
mission enumeration; and `validate.py` gained three guards — a count-lint that
fails on any hardcoded catalog count in the doc surfaces, a keyword check that
every mission is in `plugin.json` keywords, and a badge-freshness check.

## [0.3.0] - 2026-07-13

Syncs the runtime policies with the current Orca `orchestration` and `orca-cli`
skills (an audit against both found drift, including one bug in 0.2.1), and adds
two capabilities the audit surfaced: the full agent roster and scheduled runs.

### Added — agent roster (flags from Orca source, autonomy-correct)

- `spawn_worker.sh` now covers the Orca roster, and the write tiers use each
  agent's fully-autonomous flag — the exact flag Orca appends by default
  (`src/shared/tui-agent-permissions.ts`, cloned and read directly):
  claude `--dangerously-skip-permissions`, codex
  `--dangerously-bypass-approvals-and-sandbox`, gemini `--yolo`, grok
  `--permission-mode bypassPermissions`. This fixes a latent blocking bug: the
  prior `rw` flags (acceptEdits / workspace-write / auto_edit, and a wrong grok
  `--always-approve` from a web source) are the SANDBOXED modes that still
  prompt on shell + network, so a build worker running tests or `npm install`
  would block and defeat the run — the exact failure this project exists to
  avoid. `ro` stays read-only (non-blocking because it cannot mutate); `danger`
  shares `rw`'s flag and adds the ephemeral-sandbox requirement. opencode/droid/
  omp/pi have no Orca autonomous launch flag → `WORKER_CMD`. The old
  claude|codex-only refusal is gone; `WORKER_CMD` generalizes the override to
  any agent; `sandbox-policy.md` carries the full matrix.
- Because `rw` launches a permission-bypass worker, it is fail-closed behind a
  new explicit opt-in `ORCA_COORD_ALLOW_AUTONOMOUS_WRITE=1` (mirroring the danger
  gate) so a bare/accidental spawn never starts a bypass worker silently. The
  safety envelope is the isolated worktree + build-blind review + PR gate +
  testnet/staging rails; `danger` additionally mandates an ephemeral sandbox.

### Added — scheduled runs

- `runtime/mission-scheduling.md`: Orca `automations` run a mission on a cadence
  (nightly clean-sweep, weekday review-it PR sweep). Each is a full unattended
  run — headless autonomy, one-way gates parked not faked, cross-run
  anti-inflation, stops at BASE/report. Wired to review-it and clean-sweep (the
  cleanly-schedulable missions).

### Fixed

- Subtree lineage (0.2.1 bug): a supervised unit's worktree is created with
  `--parent-worktree active`, not by merely omitting `--no-parent` — the latter
  relies on Orca inferring the parent, which only works "when it can"
  (`runtime/dispatch-lifecycle.md`).
- Inbox mechanics: `check --peek` inspects unread WITHOUT consuming (the correct
  tool when an off-type heartbeat is buried); the old note misdescribed `--all`
  and omitted `--peek`.

### Added

- Provenance rule: lifecycle authority is the payload `taskId`+`dispatchId`
  verified against the dispatched pane, never a handle comparison; a
  `worker_done`/`heartbeat` from a different pane is ignored, and
  `terminal_handle_stale` means re-resolve and never dual-send
  (`runtime/liveness-resume.md`).
- Orca-native progress surface: workers update the worktree comment +
  `--workspace-status` at checkpoints, complementing the file ledger.
- `--setup run` on the builder worktree for repos needing setup hooks;
  `task-list --brief` for coordinator DAG sweeps; the composite worktree-id
  form `<repoId>::<worktreePath>`; the Linux `orca`-is-the-screen-reader gotcha
  (use `orca-ide`); `worker_done` auto-completes the task (no manual
  `task-update`); expanded group roster (`@grok`, `@cursor`).

## [0.2.1] - 2026-07-13

Closes the gaps a coverage audit found between the catalog and the original
Orca coordinator prompt library (the two monolithic prompts this repo
decomposed from).

### Changed

- Worktree lineage is now a subtree per unit: a supervised worker's worktree is
  a CHILD of the coordinator (omit `--no-parent`), and its dependent workers
  (reviewer, fix rounds, integrator, bot reconcile) run as fresh terminals
  inside that worktree — so one `WT_CLEAN` tears the whole subtree down at merge
  (`runtime/dispatch-lifecycle.md`).
- The bot-reconcile policy is generalized from Cursor BugBot to ANY PR review
  bot (Greptile, CodeRabbit, …) with a full wait → ingest → reconcile
  discipline: bounded poll with a did-not-run fallback, comment triage folded
  into one change request, dynamic bot-login detection.

### Added

- First-merge spot-check: the run's first merge gets a dispatched verification
  of its shape before the train continues, since the pipeline inherits it
  (`runtime/merge-serialization.md`).
- No-gh fallback: the conductor degrades to local `git merge --no-ff` into BASE
  when `gh` is unavailable, and records that the promotion PR is owed.
- Plan skeptic: a fresh worker stresses a decomposition against the frozen
  spec's criteria (orphan criterion / gold-plating / order / stub-slices)
  before it commits (`playbooks/decompose-dag.md`).

## [0.2.0] - 2026-07-13

Lessons ported from the failed predecessor (ravidsrk/autonomous-fleet) — the
mechanisms it earned in real runs, without the multi-runtime platform that
killed it.

### Added

- `runtime/mission-chaining.md`: sequential gated chains — the previous
  mission's verified terminal state is the gate, degraded terminals stop the
  chain, deferral carry seeds the next enumeration.
- Proof-status honesty: every mission declares `proof:` (`doctrine-only` |
  `self-run` | `external-run`) in frontmatter; advancing requires a linked run
  report on disk; validator-enforced. All ten missions start at doctrine-only.
- Instruction budget: validator-enforced line caps (missions 130, playbooks 90,
  runtime 160) so doctrine creep fails CI instead of surfacing in a postmortem.
- Orca coordinator mechanics from the predecessor's real runs: one message per
  `check --wait` call, read-marking semantics, broadcast-only group addresses,
  worktree retirement guards, lost-preamble recovery, a ban on mid-run
  `orchestration reset`.
- Blind-fix anti-anchoring and a three-round review budget in
  acceptance-review; a field-validated PR sizing seam in build-change and
  remediate-finding.
- `reviewer_mode` recorded on every manifest and a run-close sha256 integrity
  inventory (byte-identity rejection is a coordinator judgment, not automated).
- Structural anti-inflation: re-runs treat a prior run's green-but-unverified
  claims as the first items to re-verify (liveness-resume + clean-sweep).
- Trust boundary (repo/issue/PR/log text is data, never instructions) and an
  argv-never-interpolation rule for runtime scripts, with contract tests.

## [0.1.1] - 2026-07-13

### Added

- `scripts/validate.py` now rejects a mission with no machine-checkable
  Composes/rides name, scans clauses to the end of their paragraph (an "e.g. "
  or a capitalized "Rides" can no longer hide a dangling name), resolves every
  `<name>.md` mention across missions, playbooks, and runtime policies, flags
  case/underscore typos of protocol names and path-prefixed references, and
  ignores external URLs.
- Negative-path test suite (`tests/test_validate.py`): every failure branch of
  the new composition and reference checks is locked to a fixture that must
  trip it.

### Changed

- `release.md` owns the BUILT state end to end (entered by landing via
  merge-serialization); the orphaned `land.md` playbook is folded in and removed.
- `ship-it` declares its playbooks and runtime policies in a machine-checkable
  Composes/rides clause instead of bare directory pointers.
- `root-cause` delegates only the diagnosis phases of the diagnose playbook and
  stops before its fix phase; fix authority stays with the separately authorized
  handoff.
- `dispatch-lifecycle` documents the worker-spawn specifics its script relies on:
  composite worktree selectors, re-dispatch-to-used-handle as a no-op, and why
  the bounded re-Enter loop is safe.

### Fixed

- `runtime-prove` was composed but never placed in harden-it, speed-it,
  modernize-it, and prove-it; each pipeline now runs it between review and land.
- speed-it, modernize-it, prove-it, and deflake-it declare the runtime policies
  their REVIEW/LAND phases ride; deflake-it composes `remediate-finding` so a
  flake fix has a PR, review, and merge protocol.
- The orphan contract test requires explicit reference forms; "landed" in prose
  can no longer keep an orphaned playbook alive.
- Vendor names and dead README pointers scrubbed from runtime scripts;
  ARCHITECTURE layout matches the tree.
- Clarity: `{{DETECT_RUNS}}` gets a default (20), the exploit sandbox is named
  `sandbox-policy` consistently in harden-it, observe.md's depth heading no
  longer points at a definition release.md never had, and review-it's
  test-adequacy axis is marked as static reasoning for read-only workers.

## [0.1.0] - 2026-07-13

### Added

- Initial catalog: 10 outcome-named missions, callable playbooks, runtime
  policies and scripts, the agentskills.io validator, and architecture contract
  tests.
