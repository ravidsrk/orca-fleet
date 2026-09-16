# fixture target app
A small issue-tracker fixture for orca-fleet mission runs.
Run: `uv run uvicorn app.main:app` from `demo/target-app/`.
Test: `uv run pytest`. Migrate: `uv run alembic upgrade head`.
Spec: run dir `SPEC.md`; flaws land in `FLAWS.md` (S4).
