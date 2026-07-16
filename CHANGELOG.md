# Changelog

All notable changes to orca-fleet are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); the version source of
truth is `.claude-plugin/plugin.json`.

## [Unreleased]

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
- Verifier checks for reviewer independence (byte-identity rejection,
  `reviewer_mode` recorded) and a run-close sha256 integrity inventory.
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
