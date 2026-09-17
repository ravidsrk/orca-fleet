# REFLECTION — floor-it self-test (compound-learn proposal; HUMAN MUST APPROVE EACH LINE)

## Surprises

- The repo is already a near-floor: 8 of 11 candidate dimensions have wired CI gates GREEN at the
  fork point. floor-it's value here is the freeze + prove-fires + guard, not new tooling — except
  coverage, which has no runner at all.
- `run-create` refusal (`no_active_sender_terminal`) is the honest boundary for coordinator-only
  runs: borrowing a live foreign terminal as `--from` would impersonate another run's sender.
- The full suite (1490 tests, 281s) is side-effect-clean (badge files rewrite identical bytes) —
  safe to run pre-commit without tree restoration.

## Proposed AGENTS.md / GOTCHAS appends (HUMAN MUST APPROVE EACH LINE)

- GOTCHAS: coordinator-only runs record `RUN:-` with the witnessed refusal; never `--from` a
  terminal owned by another run.
- TEST_STRATEGY: `python3 -m unittest discover -s tests` (~5 min, 1490 tests) is side-effect-clean;
  run it, don't fear it.
- STYLE: campaign self-test reports live in `docs/runs/campaign-<date>-<mission>/` with
  `tier=doctrine-only` RUN headers — bind_check skips them; they advance no tier.

## Prompt / playbook tweaks (fleet-side, optional)

- floor-it SKILL: name the coordinator-only ledger shape (`RUN:-`, `WIP: builders=0 reviewers=0`,
  `waves=0`) so headless freeze-parks don't improvise header semantics per run — file a backlog item.
