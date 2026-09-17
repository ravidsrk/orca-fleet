# DECISIONS — pin-it selftest campaign (mechanical auto-resolves)

2026-09-16T13:02:36Z · base-selection · mechanical · BASE=campaign/pin-it-selftest (the campaign branch itself, forked at origin/main tip c46d4b3f) — a separate -BASE branch would add a merge hop for a run that produced no doctrine patch · task_id=n/a
2026-09-16T13:05:00Z · inventory-granularity · mechanical · 32 claim-families + 10 parks (prior pin's drift-table method: 13 policies + scripts + preamble spot-checks) — a per-sentence enumeration (≈373+ children) at an unchanged build would re-prove identical bytes claim-by-claim without new information · task_id=FREEZE
2026-09-16T13:05:00Z · scope-cut · mechanical · fleet-only files (ledger/attention/chaining/reviewed-sha + 16 fleet-only scripts + 2 new fleet-only scripts) excluded per SKILL SCOPE CUT; `--report-path` cite kept as C24 · task_id=FREEZE
2026-09-16T13:06:00Z · source-anchors · mechanical · held by build-identity (installed commit == pinned commit 54eaa147) instead of re-reading 34 files — identical commit ⇒ identical bytes; re-reading would be theater · task_id=CLASSIFY
2026-09-16T13:10:00Z · no-patch · mechanical · zero STALE/SUPERSEDED ⇒ PATCH/REVIEW/LAND vacuous per remediate-finding/acceptance-review/merge-serialization (no finding ⇒ no loop; no diff ⇒ no review surface; no PR ⇒ no train) · task_id=PATCH
2026-09-16T13:10:00Z · pin-record · mechanical · orca-pin.md + pins.json NOT rewritten — same build + zero drift ⇒ rewrite would be a no-op date bump; the official rewrite lane is issue #427 (2026-12-16), not a campaign branch · task_id=CLOSE
2026-09-16T13:10:00Z · redaction · mechanical · worker-list receipts redacted to counts+scope+page+shape-row-1 per the morning pin's convention (rows name unrelated workspaces/paths/handles) · task_id=REPLAY

No taste calls, no one-way gates, no Lane B forks. No human grant needed or faked.
