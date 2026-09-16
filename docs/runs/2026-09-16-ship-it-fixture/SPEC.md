# FROZEN SPEC (candidate — awaiting human gate #1) — fixture target `demo/target-app/`

Run: ship-it fixture build · branch `ship/fixture-target-app` · fork point `c46d4b3f`.
Grill: round 1 answered 2026-09-16 (domain tracker / flaws documented / telemetry full);
premises 1–3 unopposed.

## Objective

A small-but-real target app inside this repo that future mission runs (self-tests,
campaigns, external-run bids) can execute against honestly: every mission that
parked `missing-target` in the 2026-09-16 campaign gets a true target, and
finding-missions get documented true signal instead of fabricated runs.

## Capabilities + acceptance criteria (each testable)

### C1 — Issue tracker API + store
- AC1.1: FastAPI JSON API: create/get/list/update issues (title, body, status
  open|closed, priority 1–3), add/list comments per issue; OpenAPI at `/docs`.
- AC1.2: SQLite file DB; **real Alembic** migrations `0001` (issues) and `0002`
  (comments); `alembic upgrade head` from empty + `downgrade -1` round-trip green.
- AC1.3: pytest suite (≥20 tests, API via TestClient) green via `uv run pytest`.

### C2 — Server-rendered UI
- AC2.1: Jinja pages: issue list, issue detail (+comments), new/edit forms;
  reachable at `/` with no JS build step.
- AC2.2: UI covered by smoke tests (status codes + key content markers).

### C3 — Telemetry + staging (compose)
- AC3.1: Structured JSON logs (structlog) + Prometheus `/metrics` (request
  latency histogram, issue-count gauge).
- AC3.2: `docker compose up` serves app :8000, staging :8001 (own DB file),
  Prometheus :9090, Grafana :3000 (one provisioned dashboard), Loki + Promtail,
  Alertmanager → app `/hooks/alerts` with last-receipt visible at
  `/hooks/alerts/last` (observable test-fire destination).
- AC3.3: `teardown` (compose down -v) leaves no containers/volumes; CI runs the
  smoke (build + `/healthz` + one PromQL query + one Loki query).

### C4 — Documented imperfection set (frozen; `FLAWS.md` in the fixture)
- AC4.1: F1 slow endpoint: issue-list N+1, measurable >500ms at 1k-row seed
  (seed script provided; oracle = timing harness, speed-it signal).
- AC4.2: F2 a11y nit: priority `<select>` missing an associated label
  (oracle = axe-core rule `label`, access-it signal).
- AC4.3: F3 pending migration `0003` (adds index) generated but NOT applied at
  freeze (migrate-it signal; applying it is a mission run, not this build).
- AC4.4: F4 doc drift: README claims PostgreSQL support; only SQLite is wired
  (clean-sweep doc-claim signal).
- AC4.5: Each flaw states its oracle + "fix only inside a mission run" rule.

### C5 — Catalog hygiene
- AC5.1: Repo gates green: `validate.py`, ruff, contract tests, no new
  `SKILL.md` outside `skills/` (fixture docs are plain Markdown).
- AC5.2: README documents run/test/teardown; fixture CI is its own workflow
  file, not coupled to catalog gates.

## Boundaries (NOT in scope)

Auth/users; real PostgreSQL; mobile/emulator packaging (BROWSER tier only);
production deploy; real pager routing; perf budgets as CI gates (budgets are
mission inputs in SCOPE.md — a 30s guard at today's ~250s suite would red main);
fixing F1–F4 (that is future mission work).

## Test strategy + seams (decided before the spec)

Seams (3, highest available): HTTP (TestClient in unit, live compose in smoke),
SQLite file assertions, PromQL/LogQL queries. No lower seam; no browser driver
in fixture CI (axe/Playwright arrive with access-it runs).

## Slices (decompose preview; DAG in decompose phase)

S0 foundation (serial): scaffold pyproject/alembic/compose/CI/pytest harness.
S1 API+store (AC1). S2 UI (AC2). S3 seed+F1+telemetry+staging (AC3, AC4.1).
S4 docs+FLAWS+SCOPE+CI wiring (AC4.2–4.5, AC5).
