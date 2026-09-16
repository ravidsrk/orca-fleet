# Slice S3 — seed + F1 + telemetry + staging (needs S1; parallel with S2)

- goal: Seed script (1k rows, F1 N+1 present), structlog JSON logs,
  Prometheus `/metrics`, `/hooks/alerts` + `/hooks/alerts/last`, full compose
  stack (app, staging w/ own DB, prometheus, grafana + 1 dashboard, loki +
  promtail, alertmanager), teardown cleanliness.
- scope: `app/{telemetry,seed}.py`, `app/routers/hooks.py`, `compose.yaml`
  (fill in), `observability/{prometheus.yml,alertmanager.yml,dashboards/*.json,loki-config.yml,promtail-config.yml}`,
  `tests/test_telemetry_*.py`.
- non-goals: No UI changes, no new API resources, no `0003`, no CI edits, no
  fixing F1 (document its oracle: seed + timing command).
- stop: AC3.1–3.3 + AC4.1 green at pushed head; manifest + intent packet.
- evidence: `s3-manifest.json`; compose smoke transcript (build, /healthz,
  one PromQL + one LogQL query, teardown `docker ps -q` empty).
- budget: 80 tool calls; escalate if images won't pull.
- acceptance check: (1) fixture pytest green; (2) compose smoke transcript at
  head; (3) F1 measurable: seeded list endpoint >500ms documented with command;
  (4) ruff clean. Append-only to `app/main.py` (own `# S3` region).
- files it may create: in-scope paths + `s3-manifest.json`.
- hot-files it must NOT touch: CI workflow, `alembic/versions/*`,
  `app/templates/*`, catalog paths.
- lighting: lit. worker pack: addy (sole router).

## Criteria (machine-readable denominator; worker manifest MUST use these ids)

- S3-AC1: fixture pytest green.
- S3-AC2: compose smoke transcript at head (build, /healthz, PromQL, LogQL, teardown).
- S3-AC3: F1 measurable — seeded list endpoint >500ms documented with command.
- S3-AC4: ruff clean.
