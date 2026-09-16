# DECISIONS — ship-it fixture run (`ts · gate-or-ask-id · class · answer · why`)

2026-09-16 · fixture-placement · taste · human: in-repo demo/target-app/ (recommended) · versioned with missions, CI runs it, campaigns reference by path ·
2026-09-16 · fixture-stack · taste · human: Python FastAPI + SQLite (recommended) · matches repo toolchain (uv, ruff, pytest); server-rendered DOM covers access-it + field-test-it browser tier ·
2026-09-16 · fixture-scope · taste · human: full fixture UI+API+DB+telemetry+staging+CI (recommended) · unlocks all six parked missions at once ·
2026-09-16 · fixture-domain · taste · human: tiny issue tracker (recommended) · richest CRUD/state/UI surface for missions to bite ·
2026-09-16 · fixture-flaws · taste · human: documented imperfection set F1–F4 (recommended) · finding-missions need true signal; the list is frozen in the spec, fixes are future mission work ·
2026-09-16 · fixture-telemetry · taste · human: compose Prom+Grafana+Loki+Alertmanager (recommended) · oncall-it compatibility demands queryable backend + observable alert destination ·
2026-09-16 · migration-runner · taste · coordinator: real Alembic (not hand-rolled) · migrate-it compatibility needs the project's own migration runner; real tool, honest target ·
2026-09-16 · alert-catcher · taste · coordinator: Alertmanager → app /hooks/alerts with /hooks/alerts/last receipt · avoids an extra service; observable test-fire destination per oncall-it ·
2026-09-16 · perf-guard-lane · mechanical · coordinator: budgets as SCOPE.md mission inputs, not CI gates · a 30s guard at today's ~250s suite would red main (speed-it J1 evidence) ·
