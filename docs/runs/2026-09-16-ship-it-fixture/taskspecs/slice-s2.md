# Slice S2 — server-rendered UI + F2 (needs S1)

- goal: Jinja pages (list/detail/new/edit) + smoke tests; plant documented
  flaw F2 exactly as specified.
- scope: `app/routers/pages.py`, `app/templates/*.html`, `tests/test_ui_*.py`;
  F2: priority `<select>` with NO associated `<label>` on the new/edit form.
- non-goals: No API changes, no telemetry, no seed, no JS build, no fixing F2
  (it is the documented flaw; note its location in the manifest).
- stop: AC2.1–2.2 green at pushed head; manifest + intent packet; worker_done.
- evidence: `s2-manifest.json`; smoke transcripts; F2 location + axe-rule note.
- budget: 60 tool calls.
- acceptance check: (1) full fixture pytest green; (2) `/`, `/issues/new`,
  one `/issues/{id}` return 200 with key markers via TestClient; (3) ruff clean.
- files it may create: in-scope paths + `s2-manifest.json`. Append-only to
  `app/main.py` (own region marked `# S2`; never touch `# S1`/`# S3` regions).
- hot-files it must NOT touch: `compose.yaml`, CI workflow, `alembic/versions/*`,
  `app/telemetry.py`, `app/seed.py`, catalog paths.
- lighting: lit. worker pack: matt (sole router; tdd).

## Criteria (machine-readable denominator; worker manifest MUST use these ids)

- S2-AC1: full fixture pytest green.
- S2-AC2: `/`, `/issues/new`, one `/issues/{id}` return 200 with key markers.
- S2-AC3: ruff clean.
