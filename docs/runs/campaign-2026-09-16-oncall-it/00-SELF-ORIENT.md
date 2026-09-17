# oncall-it self-test — SELF-ORIENT (coordinator)

Campaign: campaign-2026-09-16-oncall-it · Target: orca-fleet itself @ `origin/main` tip.

```
RUN · COORDINATOR · BASE origin/main · FORK_POINT c46d4b3f3371e41408aed19e54476fa194c20b42 · T0 2026-09-16 · SOURCE (frozen path set: EMPTY — see 01-FREEZE-ASSESSMENT.md) · WIP 0
```

## Mission read (full)

- `skills/oncall-it/SKILL.md` (131 lines, frontmatter + body) — read in full.
- `AGENTS.md` — read in full. `ARCHITECTURE.md` — read in full.
- Composed playbooks read: `instrument` (full), `human-handoff` (full),
  `compound-learn` (full). `remediate-finding` / `acceptance-review` not
  activated: zero paths froze, so no per-path unit was ever dispatched; per the
  pipeline they run inside PER PATH, which never started.
- Runtime ridden as applicable to a pre-FREEZE park: `gate-classification`
  (FREEZE is a human gate; a fleet never fakes a human answer),
  `ledger-contract` (ledger below), `sandbox-policy` (read-only probes only).

## HARD dependency check (SKILL.md `compatibility`)

The mission requires ALL of: the target's own logging/metrics/tracing
libraries AND a backend that can be queried AND a staging environment whose
failures can be induced AND an alert destination the fleet can observe
receiving a test fire.

| Requirement | Probe | Result |
|---|---|---|
| logging/metrics/tracing libraries in target code | `grep -rliE 'prometheus\|opentelemetry\|otel\|statsd\|grafana\|loki' --include='*.py' --include='*.md' --include='*.yml' --include='*.toml'` | hits ONLY in `docs/research/*` (upstream audits) and old pin-it run guides — zero in any shipped code or config |
| runnable service (endpoint/job/dependency) | no `Dockerfile*`/`compose*`/`k8s*`/`helm*`; no `main.py`/`app.py`/`server.*`; no `pyproject.toml`/`package.json`; no `listen(`/Flask/FastAPI/HTTP-server code; top level is `skills/ playbooks/ runtime/ scripts/ tests/ docs/` | NONE — the repo is a doctrine + CLI-tools catalog |
| staging environment | `find` for `*staging*/terraform/infra*/deploy*` dirs; `docs/ops.md` l195-200: "There is no hosted service, staging, or deploy target"; l210: "If a deploy target ever appears…" | NONE, self-declared |
| queryable telemetry backend | same grep as above; no otel/prom/datadog/sentry config anywhere | NONE |
| observable alert destination | only alert path is `.github/workflows/alert-on-failure.yml` → files a `ci-failure` issue; `docs/completion/evidence/T-11-alert-drill.txt` l30-37: notification delivery "was NOT observed" and a real failure induction "would red `main` (R9), so it stays unobserved by design" | NOT observable by the fleet |

Repo's own ops page (`docs/ops.md` l18-19): "No other cloud accounts,
registries, or production hosts. 'Deploy' is merge to `main`."

## Worker pack

No worker dispatched (zero paths). No pack mounted; the one-router rule is
vacuously satisfied.
