# TRACEABILITY — frozen SPEC criteria → slices → passing tests @ BASE head

BASE head verified: `b43641f2` (Merge PR #450). Union of slice contracts equals
the frozen 15-criterion set: zero unassigned, zero unmet, zero waived.

| SPEC AC | Slice criterion | Proof at BASE head |
|---|---|---|
| AC1.1 CRUD API + OpenAPI | S1-AC1 | 24 API tests green; live `/docs` 200 |
| AC1.2 Alembic 0001/0002 + round-trip | S1-AC2 | round-trip re-executed; CI migrate job green |
| AC1.3 pytest ≥20 | S1-AC1 | 51 passed (28+13+10) |
| AC2.1 Jinja pages | S2-AC2 | 13 UI smoke tests; live `/` 200 |
| AC2.2 smoke tests | S2-AC1/AC2 | same 13; full suite green |
| AC3.1 logs + /metrics | S3-AC1 | 10 telemetry tests; live /metrics 55 series |
| AC3.2 compose stack | S3-AC2 | worker 8/8 smoke; CI smoke job green |
| AC3.3 teardown + CI smoke | S3-AC2 + S4-AC3 | transcript + CI smoke green (43s) |
| AC4.1 F1 measurable | S3-AC3 | re-measured 0.91–0.93s @ BASE + shape test |
| AC4.2 F2 planted | S2 plant + S4 entry | verified: select unlabeled, siblings labelled |
| AC4.3 F3 pending 0003 | S4-AC2 (round-trip leg) | boot DB @ 0002, heads @ 0003, verified |
| AC4.4 F4 drift | S4-AC2 | README claim + FLAWS refutation verified |
| AC4.5 flaw oracles + rule | S4 | FLAWS.md verified (oracles + fix-only-in-missions) |
| AC5.1 repo gates | S4-AC4/5/6 | validate green; 1490 contract tests OK @ head |
| AC5.2 README + decoupled CI | S4-AC2/3 | README executed; fixture workflow standalone |

Integrated whole (runtime-prove Part B @ b43641f2): fixture 51 passed,
catalog 1490 OK, validate green, live drive (healthz/UI/docs/metrics),
F1–F4 spot-verified. Per-slice green was never taken as done alone.
