# ISSUES — S5-C filing ledger (run 3, 2026-09-09)

Dedup pass: fetched **96** issues (`gh issue list --state all --limit 100` — open + closed; 0 open at fetch time). No `pcd:` machine markers existed (runs 1–2 predate the marker convention). Matching: marker → normalised title → shared paths/symbols → same flow+angle.

| candidate | action | url | dedup note |
|---|---|---|---|
| G-19 (S2, ops.md rollback step precision) | **created** | https://github.com/ravidsrk/orca-fleet/issues/232 | no match (no prior ops-step issue) |
| G-20 (S2, `-m 1` unbound by tests) | **created** | https://github.com/ravidsrk/orca-fleet/issues/233 | nearest #174 (vf-bench test gaps, closed) — different surface |
| G-21 (S3, ledger hygiene + PR-body lesson) | **created** | https://github.com/ravidsrk/orca-fleet/issues/234 | nearest #163 (hygiene tail 20260829, closed) — different content |
| H-02 (marketplace submits, human) | **created** | https://github.com/ravidsrk/orca-fleet/issues/235 | nearest #210 (G-07 agent slice, closed 2026-09-01) and #86 (closed 2026-08-28) — register splits H-02 from G-07; dedup comment added to #235 |
| H-04 (About description 10→13, human) | **created** | https://github.com/ravidsrk/orca-fleet/issues/236 | nearest #33 (stale "ten missions" count-lint, closed 2026-07-17) — repo-content counts, not the About field |
| H-05 (cut 0.6.1, human) | **created** | https://github.com/ravidsrk/orca-fleet/issues/237 | nearest #209 (G-06 cut 0.6.0, closed) — previous instance of the same shape; body references the pattern |
| G-09 (DEFER, doctrine-only field-proof) | **skipped-dup** | (was #212, closed) | A-27: tracker closed at the maintainer's request; live tracker is the field-proof plan in `docs/runs/README.md`; G-09 stays DEFER/open in the register and is never counted complete |
| G-15 / G-17 | covered by H-04 / H-05 | #236 / #237 | gap and its human action share one issue (the action is the fix) |
| G-16 (closed this run, T-13) | not filed | — | closed gaps are not filed |

Verification (2026-09-09): `gh search issues "pcd:<id>" --repo ravidsrk/orca-fleet` returns exactly one issue per id (6/6); `gh search issues "pcd"` returns exactly these 6 — zero duplicates. created 6 · updated 0 · reopened 0 · dedup-skipped 1 · existing_fetched 96.

Labels: existing repo taxonomy used (A-31): `sev:S2` / `sev:S3` for severity, `needs-human` for human-action, `post-launch` for DEFER. No item filed here gates launch, so no `launch-gating` label was needed.
