# Slice S4 — docs + flaws + CI + pending 0003 (needs S2, S3)

- goal: README, `FLAWS.md` (F1–F4 frozen entries), `SCOPE.md` (journeys +
  budgets as mission inputs), fixture CI workflow (pytest, ruff, migration
  round-trip, compose smoke), Alembic `0003` generated but UNAPPLIED.
- scope: `demo/target-app/{README,FLAWS,SCOPE}.md`,
  `.github/workflows/fixture-target-app.yml` (fill in), `alembic/versions/0003_*.py`.
- non-goals: No app-code changes except `0003` version file; no applying `0003`;
  no touching catalog workflows; no fixing F1–F4 (F4 = the README's PostgreSQL
  claim, planted deliberately per spec).
- stop: AC4.2–4.5 + AC5 green at pushed head; manifest + intent packet.
- evidence: `s4-manifest.json`; proof `0003` is pending (`alembic history` shows
  it down from head... more precisely: `alembic upgrade head` applies 0001+0002
  only — 0003 must be a down-revision side branch OR documented unapplied: use
  a single-head chain where CI asserts `alembic current` == 0002 after upgrade
  head... NO — simplest honest shape: 0003 exists on disk, heads show 0003, but
  fixture boot pins `alembic upgrade 0002`. State the exact mechanism in FLAWS.md).
- budget: 60 tool calls.
- acceptance check: (1) fixture pytest green; (2) README run/test/teardown
  commands verified by execution; (3) CI workflow YAML valid (`actionlint` if
  present, else `python -c yaml.safe_load`); (4) catalog `validate.py` green;
  (5) ruff clean both trees.
- files it may create: in-scope paths + `s4-manifest.json`.
- hot-files it must NOT touch: `app/*`, `compose.yaml`, `observability/*`,
  catalog paths outside the run dir + the one CI workflow file.
- lighting: lit. worker pack: addy (sole router).
