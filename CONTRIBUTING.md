# Contributing to orca-fleet

Contributions are welcome — and this repo is unusually opinionated about what goes where. Read
this page before opening a PR; it will save us both a review round.

## The one rule that decides everything else

**A fleet is an outcome, not an ingredient.** Before adding anything, decide which layer it
belongs to:

| You are adding…                                        | It belongs in     | It is a…                       |
|--------------------------------------------------------|-------------------|--------------------------------|
| a new *outcome* with its own definition of done        | `skills/<name>/`  | mission (discoverable skill)   |
| reusable *phase logic* two or more missions could run  | `playbooks/`      | callable protocol, not a skill |
| dispatch/merge/liveness/sandbox *mechanics*            | `runtime/`        | policy, invisible to users     |
| human-facing explanation                                | `docs/`           | documentation                  |

Only `skills/` may contain a `SKILL.md`. Publishing a playbook or runtime policy as a
discoverable skill recreates the routing collisions this repo exists to remove — the validator
fails the build if you try.

## Adding a mission

New missions must clear the **mission-identity test** (see
[ARCHITECTURE.md](ARCHITECTURE.md)): your workflow is a new mission only if it differs from every
existing mission in at least one of — unit of work, per-unit state machine, convergence proof,
ordering/isolation constraints, parking/failure semantics, the oracle its proof binds to. If it shares all six with an existing
mission, it is a *source* or an *adaptation* of that mission, not a new one. Argue the test
explicitly in your PR description.

A mission PR must include:

1. `skills/<name>/SKILL.md` with:
   - `name:` equal to the folder name (lowercase, hyphens);
   - `description:` 1–1024 chars including a "Use when…" trigger *and* a "Not for…" pointer to
     the neighboring missions it will be confused with;
   - `compatibility:` ≤ 500 chars declaring the Orca dependency and tooling;
   - a **Composes/rides clause** naming, in backticks, every playbook and runtime policy it
     uses (bare names — `` `decide-and-freeze` `` — never paths). At least one backticked name
     is mandatory; the validator rejects a clause it cannot machine-check.
   - a `## Convergence proof` (or definition of done) section and a `## Anti-patterns` section —
     contract tests require both.
   - a `metadata:` block. Top level is the
     [agentskills.io](https://agentskills.io/specification) allowlist and nothing else — every
     repo claim lives under `metadata:`, which is the spec's extension point. `uvx --from
     skills-ref agentskills validate skills/<name>` must say "Valid skill"; CI runs it. A
     top-level extra fails both it and `scripts/validate.py`.
   - `metadata.proof: doctrine-only` — every mission starts there. It advances to `self-run` or
     `external-run` only with a run report that BINDS: a `RUN:` header, a manifest inside the
     run's own `docs/runs/<date>-<mission>…/` directory, and an integrity inventory that
     re-hashes at the commit the header names (`runtime/scripts/run_report.py`) — and, for a
     mutating mission, `waves=<n>` in that header with one measured WIP-curve row per dispatch
     wave (`runtime/attention-budget.md`; the checker refuses a missing, partial or doubled row).
     A report whose artifacts were not retained here is history, not a tier. Do not argue a
     mission is proven in prose; bind the run.
   - `metadata.autonomy:` — the Osmani L0–L5 level.
   - the six identity points — `unit`, `state_machine`, `convergence`, `ordering`, `parking`,
     `oracle`. This is ARCHITECTURE.md's "what makes a mission a mission" test in machine-readable
     form: `scripts/validate.py` fails the build when two missions declare the same six — or merely
     restate them, since comparison is stemmed and a pair with no genuinely divergent point is one
     mission twice — and warns when they differ on only one. If you cannot fill all six, you are describing a mode of an
     existing mission, not a new one.
   - within the instruction budget: mission BODY ≤ 110 lines and frontmatter ≤ 34 (playbooks ≤ 90,
     runtime ≤ 160). If your mission needs more body, the overflow is probably a playbook.
2. `skills/<name>/evals/evals.json` — `scripts/eval.py validate` checks its schema, and
   `tests/test_evals.py` requires at least one **fixture-backed** case: `files[]` that
   materialize a small repo plus a `workspace_state[]` naming the end state the agent's workspace
   must reach (`exists`, `unchanged`, `matches`, `not_matches` on one `path` or `glob`), read
   straight off the files with no model in between; a `glob` never reads dependency directories
   such as `venv` or `node_modules`, and a regex over an empty match set fails rather than holding
   vacuously. A case with no fixtures must be labeled
   `"narration_only": true`, is graded on its trace alone, and the set of those is frozen in the
   same test. Nothing in `evals/` is proof evidence; it asks whether the mission's *text* steers an
   agent, and only a run report moves `metadata.proof`.
3. An entry in the README mission table and in [AGENTS.md](AGENTS.md)'s intent → mission mapping.
4. A guide at `docs/missions/<name>.md` following the structure of
   [docs/missions/ship-it.md](docs/missions/ship-it.md). The guide embeds the mission's contract
   card from `assets/diagrams/missions/<name>.jpg` (dark) and `<name>-light.jpg`, rendered from a
   spec in `assets/diagrams/generator/specs_missions.py` — a test holds guides and assets to parity
   in both directions.
5. An updated `EXPECTED_MISSIONS` set in `tests/test_architecture.py` AND `tests/test_evals.py` —
   the mission set is locked on purpose; changing it is a deliberate act.

Naming: outcome verbs (`ship-it`, `clean-sweep`), never vendors or techniques. The contract
tests reject mission names containing vendor tokens.

## Adding or changing a playbook

- Plain Markdown, **no frontmatter**, never a `SKILL.md`.
- Write it as a versioned, executable protocol with a checkable completion section — not an
  attribution essay. Name the upstream recipe it adapts in one line at the top.
- Every playbook must be composed by at least one mission, by explicit reference:
  a backticked `` `name` `` inside a Composes/rides clause, or a bare `name.md`
  token. A Related-section backtick is not composition — the orphan test and the
  validator share `explicit_protocol_refs` so they cannot drift.
- If your change alters a completion contract, update every mission that composes it in the
  same PR.

## Changing runtime policies or scripts

Runtime files encode operational lessons that were paid for in broken runs — wrong-base
detection, reviewed-SHA freshness, bot-autofix non-convergence, the stuck-pending watchdog.
Simplifying one because it "seems verbose" is how the lesson gets re-learned. If you can show a
mechanism is genuinely obsolete, remove it *with the story of why it existed* in the commit
message.

`runtime/scripts/` is shared tooling: shell/Python, stdlib only, no secrets (env vars only),
fail-closed exits documented in the header comment.

## Documentation

- `docs/missions/<name>.md` pages follow the ship-it template: an invoke-it line and a Needs
  line copied verbatim from the skill's `compatibility` field (a test keeps them equal), what it
  does, when (and when NOT) to reach for it, a mermaid pipeline, a `## Terminal states` table
  (State · Meaning · Who acts on it, degraded terminals annotated as such), human gates,
  convergence proof, a worked example, failure modes, composes, related. The `## Composes`
  section must name every playbook and runtime policy the SKILL's compose/rides clause declares
  and nothing the SKILL neither declares nor names as a phase-cued read; deferred reads are
  listed separately — contract tests reject drift in both directions.
- Cross-references between catalog files use bare protocol names — the validator flags
  path-prefixed or case-typo'd `<name>.md` references anywhere in `skills/`, `playbooks/`, or
  `runtime/`.
- `README.md` and `docs/` speak to humans; `AGENTS.md`, `SKILL.md`s, playbooks, and runtime
  policies speak to agents. Keep the registers distinct — agent files stay terse and
  imperative.

## Before you open the PR

```bash
python3 scripts/validate.py                # must end: "three-layer separation holds; evals valid."
python3 -m unittest discover -s tests -v   # all contract + validator fixture tests green
# optional: ruff check scripts runtime/scripts tests bench demo
# (CI runs ruff 0.16.5 on E9/F63/F7/F82 only — see ruff.toml)
```

The validator finishes in under a second; the suite takes a few minutes because it builds real
git repositories. Neither is optional. PRs that fail either
will be asked to fix before review. ruff is CI-only (not required locally). If you add validator behavior, add the negative-path fixture that proves
the new failure branch fires — the suite's standard is that every guard must be demonstrably
capable of failing.

## Commit and PR conventions

- Semantic prefixes (`feat:`, `fix:`, `docs:`, `test:`, `chore:`), small logical commits, each
  building alone.
- No `Co-authored-by` or tool-attribution trailers.
- PR bodies: state the problem, then the solution. If you changed a mission's contract, show
  the before/after of its convergence proof.

## Maintainer ops

Account inventory and the 2 a.m. incident process live in
[docs/ops.md](docs/ops.md). Contributors do not need that page to open a PR.

## License

By contributing you agree your contributions are licensed under the [MIT License](LICENSE).
