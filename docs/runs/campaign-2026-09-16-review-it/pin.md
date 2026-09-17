# PIN — fixed point, spec source, scope (review-it self-test 2026-09-16)

## Fixed point

| field | value |
|---|---|
| target | `ravidsrk/orca-fleet` PR #445, "docs(#417): mission-chaining exercise report (stopped chain, published)" |
| fixed point (fp) | `6390743815f8f435181fa410cce374587128b30a` (first parent = merge-base of the PR merge) |
| reviewed_sha | `c46d4b3f3371e41408aed19e54476fa194c20b42` (= `origin/main` tip at run time; PR merge commit) |
| reviewed_wtree | `3d39ff3709a3e95c1ba7b535d6f2dc6858ed3055` |
| diff | `git diff <fp>...HEAD` = 28 files changed, 828 insertions(+), 0 deletions |
| PR state | MERGED 2026-09-16T10:39:18Z; base `main`, head `2aa73d10`; reviews: greptile COMMENTED + APPROVED, ravidsrk COMMENTED |
| freshness | reviewed_sha == main tip; post-merge review — the verdict is a quality record (and G-REVIEW re-derivation input), not a merge gate |

Transcript: `transcripts/pin.txt`.

## Spec source (first hit wins, named)

No frozen unit spec exists for this docs report. First hit: **originating
issue #417 "Acceptance Criteria" (AC-1..AC-5)**, frozen verbatim in
`criteria.md`. PR #445 body corroborates (report contents, resume path,
follow-ups). No STOP: a real requirement source was found.

## Triage mode (declared at T0, does not move)

**Gated** (default): only high-confidence candidates reported; below the bar
is not reported. Recorded in `triage.md`.

## Worker-playbook routers (one per worker, never co-mounted)

- Acceptance axes (standards / spec / test-adequacy): **matt** (code-review
  recipe per `acceptance-review`).
- Risk lenses (security / privacy / data-migration / perf): **addy**
  (specialist skills per `risk-review`).
- Solo run: sequential same-session passes, isolated by phase (each axis file
  written from its own read pass; aggregation only in `verdict.md`). Recorded
  degradation: no fresh-context workers, no independent verifiers —
  `reviewer_mode=instructed-isolation`, every finding self-verified.

## Scope signals (`diff_scope.py --json --strict`, exit 0, no unmatched)

Transcript: `transcripts/diff-scope.json`.

| flag | value | reading |
|---|---|---|
| BACKEND | true | two `.py` seed fixtures under `docs/reports/.../leg1/` |
| DOCS | true | report prose (25 files) + transcripts |
| AUTH | true | keyword hits in prose ("session", "author", "credential", "permissions") — no auth surface change |
| PERF | true | keyword hits: embedded `index <sha>` lines in quoted transcripts — no render/query/bundle-code surface |
| FRONTEND/PROMPTS/TESTS/CONFIG/MIGRATIONS/API/SECURITY/A11Y | false | — |

Lens dispatch (see `lens-risk.md`): security + privacy + data-migration ran
(NEVER_GATE); perf ran bounded (script-flagged, inspected as keyword noise);
api-contract + a11y recorded gate-off (no trigger); simplification considered
(advisory, none). Lens-tally check: `docs/DECISIONS.md` carries zero
`lens-tally:` lines — no auto-gate streak for any lens; tally for this run
recorded in `lens-tally.md` (DECISIONS.md itself untouched: report-only
boundary).

## Blind-fix expectation (written from the criteria before line-level review)

Expected: a new `docs/reports/chaining-<date>/` dir with per-leg manifests,
a handoff log, a terminal-state table, named follow-up issues, and
SHA-cited re-derivation material. Rough shape: markdown + JSON + transcripts.
Confidence: high that structure exists (PR merged); the review's job is
whether every criterion binds to evidence, not whether files exist.
Divergence after opening the diff: none material — the report exceeds the
expectation (embedded git bundle + RESTORE.md answering re-derivability).
