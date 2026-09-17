# DETECT — orca-fleet stack reading + measured current values

Measured at FORK_POINT `c46d4b3f3371e41408aed19e54476fa194c20b42` (origin/main tip, PR #445),
clean tree. Every row below is a repo-own counter run via `runtime/scripts/evidence-run.py`;
transcripts live in `transcripts/` and the content-bound ledger is `manifest.json` (`commands[]`).

## Stack (read from the tree, not recalled)

- Shape: Markdown + Python catalog (21 missions in `skills/`, 28 playbooks, `runtime/` policies +
  `runtime/scripts/`, `scripts/` repo tooling, `tests/` contract suite, `bench/vf-bench/`,
  `demo/negative-control/`). No `pyproject.toml` / `package.json` / lockfile at root; Python 3.13,
  stdlib `unittest`, no third-party runtime deps.
- CI (`.github/workflows/`): `validate.yml` jobs `gates` + `vfbench`; `bind-check.yml`;
  `install.yml` (from-scratch install); `negative-control.yml` (pinned-demo); `alert-on-failure.yml`.
- Existing gates (all currently GREEN at the fork point — see transcripts):
  `scripts/validate.py` (three-layer separation, instruction budgets, frontmatter, identity,
  references), `unittest discover -s tests`, routing eval (`--threshold 1.0`),
  `proof_status.py --check`, `run_report.py`, `bundle.py --check`, `agentskills validate` (CI-only,
  not installed locally), pinned gitleaks `detect`, `ruff check` (E9,F63,F7,F82), vf-bench gate.
- No CONSTRAINTS.md exists (floor-it installs it). `docs/DECISIONS.md` exists (waiver surface for
  the future guard). `runtime/scripts/floor_guard.py` exists in-catalog (mission vendors it into
  the target's CI at GUARD; here target == catalog, so the wire step is CI wiring, not authoring).
- No coverage runner, no coverage config, no coverage CI gate. No repo-wide perf harness or perf
  budget (vf-bench measures verifier soundness, not product latency). No web/UI surface (a11y has
  no target). No lockfile/dependency surface (`pip install` only in CI from `.github/ci-tools.lock`).

## Measured values (command + number per candidate dimension)

| # | Candidate dimension | Command (repo's own counter) | Exit | Measured value | Transcript |
|---|---|---|---|---|---|
| 1 | suite-green | `python3 -m unittest discover -s tests` | 0 | 1490 tests, OK, 281s | transcripts/unittests.txt |
| 2 | catalog-valid (arch boundaries + budgets + refs) | `python3 scripts/validate.py` | 0 | 21/21 missions ok; separation holds; evals valid | transcripts/validate.txt |
| 3 | lint-clean | `ruff check scripts runtime/scripts tests bench demo` | 0 | All checks passed (0 findings) | transcripts/ruff.txt |
| 4 | secrets-clean | `gitleaks detect --redact --no-banner --source .` | 0 | 994 commits, ~20.92MB, no leaks | transcripts/gitleaks.txt |
| 5 | routing-eval | `python3 scripts/eval.py run --suite routing` | 0 | 94/94 correct (100%) | transcripts/routing.txt |
| 6 | proof-honesty | `python3 runtime/scripts/proof_status.py` | 0 | 19 doctrine-only / 2 self-run | transcripts/proof-status.txt |
| 7 | report-binding | `python3 runtime/scripts/run_report.py` | 0 | 2 reports bound | transcripts/run-report.txt |
| 8 | bundle-self-contained | `python3 scripts/bundle.py --check` | 0 | 21/21 self-contained | transcripts/bundle.txt |
| 9 | verifier-soundness | `python3 bench/vf-bench/gate.py` | 0 | false-done 0/20, valid 3/3, skipped 0 | transcripts/vfbench.txt |
| 10 | coverage | `python3 -m coverage --version` | 1 | ABSENT — no runner, no config, no gate | transcripts/coverage-absent.txt |
| 11 | perf-budget | — (no harness exists to run) | n/a | ABSENT — no repo-wide perf surface/harness | — (stack reading above) |
| 12 | a11y | — (no UI surface exists) | n/a | N/A — markdown+python catalog, no render target | — (stack reading above) |
| 13 | ref-validator | `which agentskills` | 1 | CI-ONLY — not installed locally | transcripts/agentskills-absent.txt |

Orca substrate: `orca status --json` → `runtime.reachable: true`, appVersion 1.4.203
(transcripts/orca-status.txt). `run-create` refused with `no_active_sender_terminal` — this shell
is not an Orca-managed terminal, so no Run namespace; zero dispatches, coordinator-only run.

## Draft dimension set for the freeze (proposal — NOT frozen)

Enforceable today (tool exists, RED/GREEN demonstrated in CI history only — PROVE-FIRES still owed
per dimension after the human freezes): 1–9 above. Coverage (#10) has no measurable tool: the
freeze either charters a WIRE unit to install one (threshold TBD by the human) or PARKS it as
untoolable with a human gate. Perf (#11) and a11y (#12) have no target of their kind in this repo:
proposed PARK as not-applicable (never a vacuous check). See FREEZE-PROPOSAL.md.
