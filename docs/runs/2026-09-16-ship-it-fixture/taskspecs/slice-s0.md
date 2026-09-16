# Slice S0 — foundation scaffold (SERIAL, frontier)

- goal: Scaffold `demo/target-app/` so slices build on green: project layout,
  FastAPI skeleton with `/healthz`, Alembic env, compose skeleton, pytest
  harness, fixture CI workflow skeleton.
- scope: `demo/target-app/{pyproject.toml,.python-version,app/__init__.py,app/main.py,app/deps.py,tests/__init__.py,tests/test_health.py,alembic.ini,alembic/}`, `compose.yaml` skeleton (app service only),
  `.github/workflows/fixture-target-app.yml` skeleton (pytest + ruff jobs).
- non-goals: No domain code, no UI, no telemetry, no seed, no docs beyond a
  5-line README stub. No migrations versions yet (S1/S4 own `versions/`).
- stop: Acceptance check green; push branch; emit evidence manifest + intent
  packet; worker_done. Do NOT open the slice PR (coordinator owns PRs/merges).
- evidence: manifest JSON at `docs/runs/2026-09-16-ship-it-fixture/s0-manifest.json`
  (base/head SHA, criteria S0-AC1..3, commands+exits, tests log, NC record).
- budget: 60 tool calls; escalate on uv/alembic install failure.
- acceptance check: (1) `uv run pytest` ≥1 green in `demo/target-app`;
  (2) `alembic heads` resolves; (3) `ruff check` clean; (4) `docker compose
  config` valid. All at the pushed head SHA.
- files it may create: paths under `demo/target-app/` listed in scope +
  `.github/workflows/fixture-target-app.yml` + its manifest JSON.
- hot-files it must NOT touch: `alembic/versions/*`, `skills/*`, `playbooks/*`,
  `runtime/*`, `scripts/*`, `tests/*` (catalog), any `docs/` outside the run dir.
- lighting: lit. worker pack: addy (sole router).
- worker_done contract: outcome + manifest path + head SHA; no approval actions.
