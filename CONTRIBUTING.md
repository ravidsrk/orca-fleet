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
ordering/isolation constraints, parking/failure semantics. If it shares all five with an existing
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
   - `proof: doctrine-only` — every mission starts there. It advances to `self-run` or
     `external-run` only with `proof_evidence:` linking a run report in the repo; the validator
     enforces this. Do not argue a mission is proven in prose; link the run.
   - within the instruction budget: missions ≤ 130 lines (playbooks ≤ 90, runtime ≤ 160).
     If your mission needs more, the overflow is probably a playbook.
2. An entry in the README mission table and in AGENTS.md's intent → mission mapping.
3. A guide at `docs/missions/<name>.md` following the structure of
   [docs/missions/ship-it.md](docs/missions/ship-it.md).
4. An updated `EXPECTED_MISSIONS` set in `tests/test_architecture.py` AND `tests/test_evals.py` —
   the mission set is locked on purpose; changing it is a deliberate act.

Naming: outcome verbs (`ship-it`, `clean-sweep`), never vendors or techniques. The contract
tests reject mission names containing vendor tokens.

## Adding or changing a playbook

- Plain Markdown, **no frontmatter**, never a `SKILL.md`.
- Write it as a versioned, executable protocol with a checkable completion section — not an
  attribution essay. Name the upstream recipe it adapts in one line at the top.
- Every playbook must be composed by at least one mission, by explicit reference
  (`` `name` `` backticked or `name.md`) — an orphan protocol fails the contract tests.
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

- `docs/missions/<name>.md` pages follow the ship-it template: what it does, when (and when
  NOT) to reach for it, a mermaid pipeline, terminal states, human gates, convergence proof,
  failure modes, composes, related.
- Cross-references between catalog files use bare protocol names — the validator flags
  path-prefixed or case-typo'd `<name>.md` references anywhere in `skills/`, `playbooks/`, or
  `runtime/`.
- `README.md` and `docs/` speak to humans; `AGENTS.md`, `SKILL.md`s, playbooks, and runtime
  policies speak to agents. Keep the registers distinct — agent files stay terse and
  imperative.

## Before you open the PR

```bash
python3 scripts/validate.py                # must end: "All 11 missions valid; three-layer separation holds."
python3 -m unittest discover -s tests -v   # all contract + validator fixture tests green
```

Both run in under a second; there is no excuse to skip them. PRs that fail either will be asked
to fix before review. If you add validator behavior, add the negative-path fixture that proves
the new failure branch fires — the suite's standard is that every guard must be demonstrably
capable of failing.

## Commit and PR conventions

- Semantic prefixes (`feat:`, `fix:`, `docs:`, `test:`, `chore:`), small logical commits, each
  building alone.
- No `Co-authored-by` or tool-attribution trailers.
- PR bodies: state the problem, then the solution. If you changed a mission's contract, show
  the before/after of its convergence proof.

## License

By contributing you agree your contributions are licensed under the [MIT License](LICENSE).
