# Slice S1 — issues API + store (needs S0)

- goal: CRUD issues API + comments + SQLite + Alembic `0001`/`0002`, TDD.
- scope: `app/{models,schemas,routers/issues,routers/comments}.py`,
  `alembic/versions/0001_*.py`, `0002_*.py`, `tests/test_api_*.py`
  (≥20 tests via TestClient); OpenAPI at `/docs`.
- non-goals: No UI templates, no telemetry, no seed, no `0003` (S4 owns it),
  no compose/CI edits, no query optimization in the list endpoint (S3 owns the
  N+1 query shape for F1 — write it straightforwardly, do not preempt it).
- stop: AC1.1–1.3 green at pushed head; manifest + intent packet; worker_done.
- evidence: `s1-manifest.json` (same dir); RED-first transcripts per TDD.
- budget: 80 tool calls; escalate on migration round-trip failure.
- acceptance check: (1) full fixture pytest green; (2) `alembic upgrade head`
  from empty + `downgrade -1` + `upgrade head` round-trips with data smoke
  (insert issue+comment, read back); (3) ruff clean.
- files it may create: in-scope paths + `s1-manifest.json`. Append-only to
  `app/main.py` router includes (own region marked `# S1`).
- hot-files it must NOT touch: `compose.yaml`, CI workflow, `app/templates/*`,
  `app/telemetry.py`, catalog paths (skills/playbooks/runtime/scripts/tests).
- lighting: lit. worker pack: matt (sole router; tdd).
