# TODOS

This file is a pointer, not a backlog. Open work lives where it is machine-checked or
issue-tracked, so this surface cannot drift into "nothing open" while gaps stand:

- **The 2026-09-28 release-readiness review** —
  [`docs/reviews/2026-09-28-release-readiness-review.md`](docs/reviews/2026-09-28-release-readiness-review.md):
  four P0 findings (the runtime scripts hardcode `orca` where Linux ships `orca-ide`; the
  published version is 1,372 commits behind with no GitHub Releases; five stale hand-typed pin
  and proof sentences; a schema line the 2026-09-28 re-pin missed), eight P1 findings, and a
  three-tier release path (0.7.0 → public beta → 1.0). Its findings are filed as #510–#525
  under label
  [`release-readiness-2026-09-28`](https://github.com/ravidsrk/orca-fleet/issues?q=label%3Arelease-readiness-2026-09-28)
  — that query, not this line, is the live open set. At the 2026-09-30 sweep
  [#511](https://github.com/ravidsrk/orca-fleet/issues/511),
  [#515](https://github.com/ravidsrk/orca-fleet/issues/515) and
  [#518](https://github.com/ravidsrk/orca-fleet/issues/518) were still open; the ordered path
  past the 0.7.0 cut is the road-to-1.0 epic
  [#526](https://github.com/ravidsrk/orca-fleet/issues/526).
- **Standing gaps** — [`docs/completion/GAPS.md`](docs/completion/GAPS.md): every finding
  between HEAD and the completion definition with a FINISH / CUT / DEFER decision. G-09
  (field proof) and G-19 (ops-step precision) are the open DEFER rows. Their tracking ISSUES
  (#212 and the S5-C filings) are closed; the register rows stay open deliberately — a closed
  tracker is not a closed gap, and `docs/runs/README.md`'s field-proof plan is G-09's live
  tracker.
- **Field-proof plan** — [`docs/runs/README.md`](docs/runs/README.md#field-proof-plan-212):
  per-mission targets, tiers, terminals, and blockers for advancing `doctrine-only` missions.
  A tier moves only through a recorded mission run, never a relabel.
- **The 2026-09-11 deep review** — [`REVIEW.md`](REVIEW.md) and issues
  [#279–#307](https://github.com/ravidsrk/orca-fleet/issues?q=label%3Adeep-review-2026-09-11)
  (label `deep-review-2026-09-11`): whether running the negative control proves anything (P0),
  the proof-tier gate, the orphan mechanisms, the routing instrument, the identity test.
  **Closed.** #279–#306 landed in #308, one commit each; #307 closed when its nine release tags
  were published, and the test that demanded them now passes. A second independent review filed
  #309–#318 against the same base and landed in the same PR. `REVIEW.md` is therefore a completed
  review, not open work — it stays at this path as the most recent one. Citations carrying a
  section or attack-id anchor still mean the ARCHIVED 2026-09-10 document and must name that
  dated path, never this one (#295); anchors are numbered per review, so a bare one mis-resolves
  against whichever review holds this path today.
- **The 2026-09-12 release audit** — issues and PRs #321–#338: `deny-hook.sh` word and redirect
  parsing, verifier evidence binding, `egress.py` receipt writes, `bundle.py` vendored protocols,
  `spawn_worker.sh` launch refusals, and the migration/governance mission contracts. Its evidence
  is under [`docs/reports/release-20260912/`](docs/reports/release-20260912/).
- **The 2026-09-10 deep review**, its predecessor, archived at
  [`docs/reviews/2026-09-10-review.md`](docs/reviews/2026-09-10-review.md) and issues
  [#255–#276](https://github.com/ravidsrk/orca-fleet/issues?q=label%3Adeep-review-2026-09-10).
  Code comments and fixtures citing "REVIEW.md §N" mean THAT document, not this one (#295).

Completed items are recorded in [`CHANGELOG.md`](CHANGELOG.md), not here.
