# Changelog

All notable changes to orca-fleet are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); the version source of
truth is `.claude-plugin/plugin.json`.

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
