# document-it self-test · ledger

RUN: solo-no-orca-run · COORDINATOR: workflow-child-a4a0bde3 · BASE: campaign/document-it-selftest · FORK_POINT: 6390743815f8f435181fa410cce374587128b30a · T0: 2026-09-16T10:06:08Z · SOURCE: extractor `python3 docs/runs/campaign-2026-09-16-document-it/extractor/extract.py` digest sha256:058e51cdf0384da8e4f1d958f115a5beac080c453fc796c1849921a00022993a (57 entities) · WIP: builders=1 reviewers=1

PHASE: BUILDING

Worker pack router: matt (sole router for every cell worker; addy never co-mounted).
No-gh lane: local-merge chain on BASE, one commit per cell, `no-gh: local-merge`.
Review mode: instructed-isolation self-review (D3 — no second identity exists in this
solo self-test; the mechanical oracle is the claim check + rename control + re-derived map).

| task_id | entity | quadrant | GAP | BUILD_DONE | CLAIMS_OK | NC_RED | PR_OPEN | BOT | REVIEWED | MERGED | REACHABLE | WT_CLEAN | lighting | park | evidence |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| doc-r01 | cli:runtime/scripts/decisions.py | reference | critical | t | t | t | n/a | n/a | t | t | f | n/a | lit | | cells/doc-r01.md @107df88 |
| doc-r02 | cli:runtime/scripts/deny-hook.sh | reference | critical | t | t | t | n/a | n/a | t | t | f | n/a | lit | | cells/doc-r02.md @1aa143a |
| doc-r03 | cli:runtime/scripts/diff_scope.py | reference | critical | t | t | t | n/a | n/a | t | f | f | n/a | lit | | cells/doc-r03.md |
| doc-r04 | cli:runtime/scripts/ed25519.py | reference | critical | f | f | f | n/a | n/a | f | f | f | n/a | lit | | |
| doc-r05 | cli:runtime/scripts/egress.py | reference | critical | f | f | f | n/a | n/a | f | f | f | n/a | lit | | |
| doc-r06 | cli:runtime/scripts/floor_guard.py | reference | critical | f | f | f | n/a | n/a | f | f | f | n/a | lit | | |
| doc-r07 | cli:runtime/scripts/gate-batch.py | reference | critical | f | f | f | n/a | n/a | f | f | f | n/a | lit | | |
| doc-r08 | cli:runtime/scripts/guard_text.py | reference | critical | f | f | f | n/a | n/a | f | f | f | n/a | lit | | |
| doc-r09 | cli:runtime/scripts/hitl-loop.template.sh | reference | critical | f | f | f | n/a | n/a | f | f | f | n/a | lit | | |
| doc-r10 | cli:runtime/scripts/pm.py | reference | critical | f | f | f | n/a | n/a | f | f | f | n/a | lit | | |
| doc-r11 | cli:runtime/scripts/sandbox_doctor.py | reference | critical | f | f | f | n/a | n/a | f | f | f | n/a | lit | | |
| doc-r12 | cli:runtime/scripts/spawn_worker.sh | reference | critical | f | f | f | n/a | n/a | f | f | f | n/a | lit | | |
| doc-r13 | cli:runtime/scripts/watchdog.py | reference | critical | f | f | f | n/a | n/a | f | f | f | n/a | lit | | |
| doc-r14 | cli:runtime/scripts/wtree.sh | reference | critical | f | f | f | n/a | n/a | f | f | f | n/a | lit | | |
| doc-r15 | config:runtime/one-way-doors.json | reference | critical | f | f | f | n/a | n/a | f | f | f | n/a | lit | | |
| doc-r16 | config:runtime/watchdog.json | reference | critical | f | f | f | n/a | n/a | f | f | f | n/a | lit | | |
| doc-x01 | cli:runtime/scripts/decisions.py | explanation | critical | f | f | f | n/a | n/a | f | f | f | n/a | lit | | |
| doc-x02 | cli:runtime/scripts/deny-hook.sh | explanation | critical | f | f | f | n/a | n/a | f | f | f | n/a | lit | | |
| doc-x03 | cli:runtime/scripts/diff_scope.py | explanation | critical | f | f | f | n/a | n/a | f | f | f | n/a | lit | | |
| doc-x04 | cli:runtime/scripts/ed25519.py | explanation | critical | f | f | f | n/a | n/a | f | f | f | n/a | lit | | |
| doc-x05 | cli:runtime/scripts/egress.py | explanation | critical | f | f | f | n/a | n/a | f | f | f | n/a | lit | | |
| doc-x06 | cli:runtime/scripts/floor_guard.py | explanation | critical | f | f | f | n/a | n/a | f | f | f | n/a | lit | | |
| doc-x07 | cli:runtime/scripts/gate-batch.py | explanation | critical | f | f | f | n/a | n/a | f | f | f | n/a | lit | | |
| doc-x08 | cli:runtime/scripts/guard_text.py | explanation | critical | f | f | f | n/a | n/a | f | f | f | n/a | lit | | |
| doc-x09 | cli:runtime/scripts/hitl-loop.template.sh | explanation | critical | f | f | f | n/a | n/a | f | f | f | n/a | lit | | |
| doc-x10 | cli:runtime/scripts/pm.py | explanation | critical | f | f | f | n/a | n/a | f | f | f | n/a | lit | | |
| doc-x11 | cli:runtime/scripts/sandbox_doctor.py | explanation | critical | f | f | f | n/a | n/a | f | f | f | n/a | lit | | |
| doc-x12 | cli:runtime/scripts/spawn_worker.sh | explanation | critical | f | f | f | n/a | n/a | f | f | f | n/a | lit | | |
| doc-x13 | cli:runtime/scripts/watchdog.py | explanation | critical | f | f | f | n/a | n/a | f | f | f | n/a | lit | | |
| doc-x14 | cli:runtime/scripts/wtree.sh | explanation | critical | f | f | f | n/a | n/a | f | f | f | n/a | lit | | |
| doc-x15 | config:runtime/one-way-doors.json | explanation | critical | f | f | f | n/a | n/a | f | f | f | n/a | lit | | |
| doc-x16 | config:runtime/watchdog.json | explanation | critical | f | f | f | n/a | n/a | f | f | f | n/a | lit | | |

Flag semantics: BUILD_DONE = section written on BASE from code archaeology;
CLAIMS_OK = claim check passes for the cell's anchors; NC_RED = rename control for the
cell's anchor went RED on a throwaway branch; REVIEWED = instructed-isolation self-review
recorded (D3); MERGED = cell commit exists on BASE; REACHABLE = section reachable in one
hop (README → docs/runtime-scripts.md); WT_CLEAN n/a (no unit worktrees in solo run).

## Deviations (numbered, carried into the run report)

- D1 no-orca-run: no Orca Run namespace; no dispatches, no DAG. Solo self-test acts as
  coordinator+builder+reviewer. Liveness/resume/dispatch mechanics unexercised.
- D2 no-gh: no PRs opened, no merges to any shared branch (workflow constraint). Cells
  land as a serialized commit chain on local BASE; PR_OPEN/BOT n/a; MERGED =
  ancestry on BASE; promotion PR owed and out of scope.
- D3 review-not-independent: no second identity; build-blind review impossible. Each
  cell carries an instructed-isolation self-review (blind-fix expectation written
  before re-reading the section, three axes) explicitly labeled as the weaker
  guarantee. The terminal rests on the mechanical oracle (claim check + rename RED +
  re-derived map + reachability grep), never on the review.
- D4 freeze-gate auto-resolve: spawned session → recommended options picked per
  gate-classification, each logged in DECISIONS.md. No one-way door crossed: nothing
  pushed, merged to default, or deployed.
