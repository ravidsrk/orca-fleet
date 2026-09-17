# access-it self-test — PARKED (no target), 2026-09-16

Mission `access-it` run against orca-fleet itself at its main tip, following
`skills/access-it/SKILL.md` and `AGENTS.md`. Verdict: **PARKED — missing target**.
No run was fabricated; the mission parks at FREEZE, before BASE bootstrap.

| Field | Value |
|---|---|
| Mission | `access-it` — mission source revision `6390743` (`skills/access-it/SKILL.md`) |
| Target | orca-fleet itself (self-test), `origin/main` tip `6390743815f8f435181fa410cce374587128b30a` |
| Worktree | isolated copy, updated to `origin/main` tip before the run (`git rev-parse HEAD == origin/main`) |
| Branch | `campaign/access-it-selftest` (this commit; not pushed, no PR, no merge) |
| Coordinator | CLI self-test, no workers dispatched (`waves=0`, no TASK pack mounted — the one-router rule is vacuous with zero workers) |
| Orca | `orca status --json` → `runtime.reachable: true`, `state: ready`, app `1.4.203` (tooling is NOT the blocker) |
| Oracle | axe-core is not installed (`npx --no-install axe-core` → "could not determine executable to run"); moot — there is no surface to scan |

## Pipeline walk (phase by phase)

| Phase | Action | Result | Evidence |
|---|---|---|---|
| FREEZE | Enumerate the surface: page/flow/component set × WCAG 2.2 AA (the denominator) | **EMPTY denominator — PARK** | `surface-enumeration.txt`, `manifest.json` |
| BOOTSTRAP | Not reached (nothing to dispatch against; spawning workers with zero units would be theater) | skipped | — |
| DETECT | Not reached (no rendered surface for the oracle) | skipped | — |
| FIX / REVIEW / LAND | Not reached (zero violations) | skipped | — |
| RE-VERIFY | Not reached (no fix, so no revert-to-violation control is possible) | skipped | — |
| PARK (human-AT) | Not reached as a terminal (that park is for criteria past the automation ceiling on an existing surface; here the surface itself is missing) | n/a | — |
| VERDICT | **PARKED — missing target** | recorded here | this file |

Ledger (T0, `ledger-contract` shape): `WIP: builders=0 reviewers=0`, zero units,
zero dispatches. No `worker_done` was graded; there is nothing to bind to a SHA
beyond the frozen target tip above, which the enumeration transcript re-derives
(`git rev-parse HEAD`, `git ls-files` census).

## Why the mission does not apply

`access-it`'s unit is "one success-criterion violation instance on the frozen
surface" and its oracle is "a deterministic rule engine (axe-core) over a frozen
surface". Both require a runnable rendered surface. At the frozen tip:

- 1114 tracked files: 389 json, 367 md, 160 txt, 91 jpg, 71 py, 10 sh, 7 ts,
  5 yml, 2 toml, rest misc. **Zero** `.html/.css/.tsx/.jsx/.vue/.svelte`,
  no `package.json`, no Dockerfile, no compose file, no docs-site generator
  config (`surface-enumeration.txt`).
- No server code: the only `django/flask/fastapi/express/http.server` hits in
  `*.py` are other missions' eval fixtures in `tests/test_evals.py`; no
  `localhost:<port>` in `runtime/`, `playbooks/`, or `skills/access-it/`.
- The catalog's own field-proof plan (`docs/runs/README.md`) states access-it
  "needs a web UI — an external repo with an axe-core baseline" / external-run.
- The `design-rules` alternative oracle does not help: it still needs the
  target's own component/contrast/target-size rules, and this target has no
  components and no design system.

Per `browser-drive.md`, absence of what a rendered-page phase needs "is a PARK,
never a substitution". The same applies to the surface itself.

## Substitutes considered and rejected

- **Markdown docs as rendered by GitHub**: a third-party origin the run does not
  control; violations could not be fixed "at the instance" nor proven with a
  revert-to-violation control against GitHub's renderer.
- **`assets/*.jpg` diagrams**: static binaries, no DOM to scan.
- **`bench/vf-bench`, `demo/negative-control`, `runtime/scripts/`**: CLI/TUI
  Python and shell, no rendered page.
- **`skills/access-it/evals` `checkout.html` fixture**: a synthetic 6-line
  routing-test fixture, not the repo's surface — scanning it would be a
  fabricated run, which the task explicitly forbids.
- **Vendored `.ts` under `docs/reports/release-20260912/pin/source/`**: Orca CLI
  handler snapshots inside a report, not UI components of this repo.

## Terminal state

`PARKED (missing target)`. `metadata.proof` for `access-it` stays
`doctrine-only`; no `docs/runs/README.md` archive row (this is a parked
self-test, not a proof run). No secrets touched, no deploys, no destructive
commands, nothing pushed.

## Gates at the evidence head

- `python3 scripts/validate.py` → exit 0 (see commit; re-run by reviewer)
- `python3 -m unittest discover -s tests` → exit 0 (see commit; re-run by reviewer)
