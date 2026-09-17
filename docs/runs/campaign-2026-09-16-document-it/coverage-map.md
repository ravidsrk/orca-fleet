# Coverage map (judged) — document-it self-test vs orca-fleet

BASE `6390743815f8f435181fa410cce374587128b30a` · surface digest
`sha256:058e51cdf0384da8e4f1d958f115a5beac080c453fc796c1849921a00022993a`
(21 skills + 29 CLIs + 7 configs = 57 entities).
Raw grep hits: [evidence/map-raw.txt](evidence/map-raw.txt). A raw hit is candidate
evidence only; the verdict below applies the quadrant definitions (reference = what it
is + options/types/defaults; how-to = accomplish task X; tutorial = zero→working
example; explanation = why / what was traded). Quadrant homes are user-facing docs
only — runs/reports/reviews/research/completion are evidence and history, not coverage.

## Sub-surface A — published skills (21/21 fully covered, zero gaps)

Every skill scores identically: reference via the README catalog row + the full
`docs/missions/<name>.md` guide; how-to via the guide's `## Invoke it`; tutorial via
the guide's `## A worked example` (review-it/ship-it additionally in getting-started's
worked missions); explanation via `## When to reach for it` (+ `## Failure modes`).
Spot-verified guides: ship-it, pin-it, absorb-it, document-it (all carry all four
sections; worked examples are genuine narratives, not stubs).

| entity | reference | how-to | tutorial | explanation |
|---|---|---|---|---|
| skill:absorb-it | ✅ docs/missions/absorb-it.md:1 + README.md:188 | ✅ docs/missions/absorb-it.md:24 | ✅ docs/missions/absorb-it.md:130 | ✅ docs/missions/absorb-it.md:58 |
| skill:access-it | ✅ docs/missions/access-it.md:1 + README.md:181 | ✅ docs/missions/access-it.md:24 | ✅ docs/missions/access-it.md:99 | ✅ ARCHITECTURE.md:60 + docs/missions/access-it.md:47 |
| skill:attest-it | ✅ docs/missions/attest-it.md:1 + README.md:180 | ✅ docs/missions/attest-it.md:24 | ✅ docs/missions/attest-it.md:94 | ✅ docs/missions/attest-it.md:45 |
| skill:clean-sweep | ✅ docs/missions/clean-sweep.md:1 + README.md:170 | ✅ docs/missions/clean-sweep.md:27 | ✅ docs/missions/clean-sweep.md:186 | ✅ ARCHITECTURE.md:50 + docs/missions/clean-sweep.md:69 |
| skill:deflake-it | ✅ docs/missions/deflake-it.md:1 + README.md:175 | ✅ docs/missions/deflake-it.md:23 | ✅ docs/missions/deflake-it.md:147 | ✅ docs/missions/deflake-it.md:51 |
| skill:document-it | ✅ docs/missions/document-it.md:1 + README.md:189 | ✅ docs/missions/document-it.md:23 | ✅ docs/missions/document-it.md:113 | ✅ docs/missions/document-it.md:46 |
| skill:field-test-it | ✅ docs/missions/field-test-it.md:1 + README.md:185 | ✅ docs/missions/field-test-it.md:23 | ✅ docs/missions/field-test-it.md:110 | ✅ ARCHITECTURE.md:66 + docs/missions/field-test-it.md:48 |
| skill:floor-it | ✅ docs/missions/floor-it.md:1 + README.md:183 | ✅ docs/missions/floor-it.md:24 | ✅ docs/missions/floor-it.md:111 | ✅ docs/missions/floor-it.md:50 |
| skill:harden-it | ✅ docs/missions/harden-it.md:1 + README.md:171 | ✅ docs/missions/harden-it.md:24 | ✅ docs/missions/harden-it.md:152 | ✅ docs/missions/harden-it.md:52 |
| skill:map-it | ✅ docs/missions/map-it.md:1 + README.md:177 | ✅ docs/missions/map-it.md:24 | ✅ docs/missions/map-it.md:161 | ✅ docs/missions/map-it.md:48 |
| skill:migrate-it | ✅ docs/missions/migrate-it.md:1 + README.md:186 | ✅ docs/missions/migrate-it.md:24 | ✅ docs/missions/migrate-it.md:196 | ✅ docs/missions/migrate-it.md:46 |
| skill:modernize-it | ✅ docs/missions/modernize-it.md:1 + README.md:173 | ✅ docs/missions/modernize-it.md:23 | ✅ docs/missions/modernize-it.md:166 | ✅ docs/missions/modernize-it.md:60 |
| skill:oncall-it | ✅ docs/missions/oncall-it.md:1 + README.md:187 | ✅ docs/missions/oncall-it.md:24 | ✅ docs/missions/oncall-it.md:113 | ✅ docs/missions/oncall-it.md:46 |
| skill:oss-contribute | ✅ docs/missions/oss-contribute.md:1 + README.md:179 | ✅ docs/missions/oss-contribute.md:26 | ✅ docs/missions/oss-contribute.md:174 | ✅ ARCHITECTURE.md:176 + docs/missions/oss-contribute.md:53 |
| skill:pin-it | ✅ docs/missions/pin-it.md:1 + README.md:182 | ✅ docs/missions/pin-it.md:24 | ✅ docs/missions/pin-it.md:111 | ✅ ARCHITECTURE.md:73 + docs/missions/pin-it.md:50 |
| skill:prove-it | ✅ docs/missions/prove-it.md:1 + README.md:174 | ✅ docs/missions/prove-it.md:24 | ✅ docs/missions/prove-it.md:153 | ✅ docs/missions/prove-it.md:52 |
| skill:reshape-it | ✅ docs/missions/reshape-it.md:1 + README.md:184 | ✅ docs/missions/reshape-it.md:23 | ✅ docs/missions/reshape-it.md:103 | ✅ docs/missions/reshape-it.md:46 |
| skill:review-it | ✅ docs/missions/review-it.md:1 + README.md:176 | ✅ docs/getting-started.md:94 + docs/missions/review-it.md:25 | ✅ docs/getting-started.md:11 + docs/missions/review-it.md:152 | ✅ docs/missions/review-it.md:48 |
| skill:root-cause | ✅ docs/missions/root-cause.md:1 + README.md:178 | ✅ docs/missions/root-cause.md:25 | ✅ docs/missions/root-cause.md:151 | ✅ docs/missions/root-cause.md:47 |
| skill:ship-it | ✅ docs/missions/ship-it.md:1 + README.md:169 | ✅ docs/missions/ship-it.md:25 | ✅ docs/missions/ship-it.md:174 + docs/getting-started.md:12 | ✅ docs/missions/ship-it.md:54 |
| skill:speed-it | ✅ docs/missions/speed-it.md:1 + README.md:172 | ✅ docs/missions/speed-it.md:23 | ✅ docs/missions/speed-it.md:143 | ✅ docs/missions/speed-it.md:55 |

Note: raw getting-started prerequisite-table one-liners (e.g. `:58`-`:67`) were judged
NOT tutorial/how-to content — only review-it/ship-it have worked missions there. The
in-guide worked examples carry the tutorial verdict instead.

## Sub-surface B — script CLIs

| entity | reference | how-to | tutorial | explanation | verdict |
|---|---|---|---|---|---|
| cli:runtime/scripts/decisions.py | ❌ | ❌ | ❌ | ❌ | CRITICAL |
| cli:runtime/scripts/deny-hook.sh | ❌ (README.md:528 is a what-only sentence; `--settings` undocumented) | ❌ | ❌ | ❌ | CRITICAL |
| cli:runtime/scripts/diff_scope.py | ❌ | ❌ | ❌ | ❌ | CRITICAL |
| cli:runtime/scripts/dispatch-sign.py | ✅ docs/verify-gate.md:241-245 | ✅ docs/verify-gate.md:241-245 + docs/ops.md:193 | n/a (bounded out) | ✅ docs/verify-gate.md:196-237 | covered |
| cli:runtime/scripts/ed25519.py | ❌ (docs/verify-gate.md:263 is a one-clause mention, no API/usage) | ❌ | ❌ | ❌ | CRITICAL |
| cli:runtime/scripts/egress.py | ❌ | ❌ | ❌ | ❌ | CRITICAL |
| cli:runtime/scripts/evidence-run.py | ✅ docs/verify-gate.md:94 + docs/run-submission-guide.md:73 | ✅ docs/run-submission-guide.md:73 | n/a (bounded out) | n/a (bounded out — common-gap explanation deferred) | covered |
| cli:runtime/scripts/floor_guard.py | ❌ | ❌ | ❌ | ❌ | CRITICAL |
| cli:runtime/scripts/gate-batch.py | ❌ | ❌ | ❌ | ❌ | CRITICAL |
| cli:runtime/scripts/guard_text.py | ❌ | ❌ | ❌ | ❌ | CRITICAL |
| cli:runtime/scripts/hitl-loop.template.sh | ❌ | ❌ | ❌ | ❌ | CRITICAL |
| cli:runtime/scripts/inventory.py | ✅ docs/run-submission-guide.md:87-88 | ✅ docs/run-submission-guide.md:87-88 | n/a (bounded out) | n/a (bounded out) | covered |
| cli:runtime/scripts/pm.py | ❌ | ❌ | ❌ | ❌ | CRITICAL |
| cli:runtime/scripts/preflight.py | ✅ README.md:525 + docs/missions/review-it.md:132 | ✅ docs/getting-started.md:181 | n/a (bounded out) | ✅ README.md:522-530 (doctrine + gap, honestly stated) | covered |
| cli:runtime/scripts/proof_status.py | ✅ docs/ops.md:176 | ✅ docs/ops.md:176 | n/a (bounded out) | n/a (bounded out) | covered |
| cli:runtime/scripts/run_report.py | ✅ AGENTS.md:103 | ✅ docs/run-submission-guide.md:126 | n/a (bounded out) | ✅ docs/concepts.md:436 | covered |
| cli:runtime/scripts/sandbox_doctor.py | ❌ | ❌ | ❌ | ❌ | CRITICAL |
| cli:runtime/scripts/spawn_worker.sh | ❌ | ❌ | ❌ | ❌ | CRITICAL |
| cli:runtime/scripts/verify-gate.sh | ✅ docs/verify-gate.md:36 | ✅ docs/getting-started.md:111 | ✅ docs/getting-started.md:109-113 (worked wiring) | ✅ docs/verify-gate.md:44 | covered |
| cli:runtime/scripts/verify.py | ✅ README.md:504 | ✅ docs/verify-gate.md:139 | n/a (bounded out) | ✅ ARCHITECTURE.md:251-259 | covered |
| cli:runtime/scripts/watchdog.py | ❌ | ❌ | ❌ | ❌ | CRITICAL |
| cli:runtime/scripts/wtree.sh | ❌ | ❌ | ❌ | ❌ | CRITICAL |
| cli:scripts/bind_check.py | ✅ docs/run-submission-guide.md:95 | ✅ docs/run-submission-guide.md:95 | n/a (bounded out) | n/a (bounded out) | covered |
| cli:scripts/bundle.py | ✅ docs/install.md:83-84 | ✅ docs/install.md:83-84 | n/a (bounded out) | n/a (bounded out) | covered |
| cli:scripts/eval.py | ✅ README.md:465 + CONTRIBUTING.md:65 | ✅ CONTRIBUTING.md:65 | n/a (bounded out) | n/a (bounded out) | covered |
| cli:scripts/gen-badges.py | ✅ ARCHITECTURE.md:180-191 | ✅ docs/ops.md:202 | n/a (bounded out) | ✅ ARCHITECTURE.md:191 | covered |
| cli:scripts/install.sh | ✅ docs/install.md:18 + README.md:31 | ✅ docs/install.md:18 | n/a (bounded out) | ✅ docs/distribution.md:37-59 | covered |
| cli:scripts/validate.py | ✅ README.md:462 | ✅ docs/ops.md:76 | n/a (bounded out) | ✅ ARCHITECTURE.md:139-163 | covered |
| cli:hooks/print-settings-snippet.sh | ✅ README.md:144 | ✅ docs/getting-started.md:109 | ✅ getting-started.md:109-113 | n/a (bounded out) | covered |

## Sub-surface C — config keys / env

| entity | reference | how-to | tutorial | explanation | verdict |
|---|---|---|---|---|---|
| config:hooks/hooks.json | ✅ README.md:151 + docs/verify-gate.md:34-36 | ✅ docs/getting-started.md:82 | ✅ getting-started.md:82-113 | ✅ README.md:151 | covered |
| config:hooks/settings-snippet.json | ✅ docs/verify-gate.md:29 | ✅ docs/getting-started.md:109-113 (via snippet-merge flow) | n/a (bounded out) | n/a (bounded out) | covered |
| config:runtime/one-way-doors.json | ❌ | ❌ | ❌ | ❌ | CRITICAL |
| config:runtime/pins.json | ✅ README.md:117 + docs/distribution.md:53 | ✅ docs/run-submission-guide.md:16 | n/a (bounded out) | ✅ docs/distribution.md:53 | covered |
| config:runtime/watchdog.json | ❌ | ❌ | ❌ | ❌ | CRITICAL |
| config:.env.example | ✅ docs/verify-gate.md:65-120 (all 15 ORCA_* vars; filename grep missed, judgment corrects) | ✅ docs/verify-gate.md:99-145 | n/a (bounded out) | ✅ docs/verify-gate.md:soundness-condition | covered |
| config:ruff.toml | ✅ CONTRIBUTING.md:133 (effective rule set stated) | ✅ CONTRIBUTING.md:133 | n/a (bounded out) | n/a (bounded out) | covered |

## Gap counts

- Critical (zero coverage anywhere): **16** — 14 CLIs (decisions, deny-hook, diff_scope,
  ed25519, egress, floor_guard, gate-batch, guard_text, hitl-loop.template, pm,
  sandbox_doctor, spawn_worker, watchdog, wtree) + 2 configs (one-way-doors.json,
  watchdog.json).
- Common (reference-only or partial): 0 frozen — covered entities' missing
  tutorial/explanation cells are bounded out at the freeze gate (below), not frozen.
- Diagrams: 18 skill tokens across README + mission-guide mermaid blocks, zero orphans
  ([evidence/diagram-entities.txt](evidence/diagram-entities.txt)). JPG architecture
  diagrams are not machine-readable — noted, not scored.

## Frozen gap list (human gate — spawned auto-resolve, see DECISIONS.md)

- FROZEN-FILL (16 reference cells): one per critical entity, reference-first from code
  archaeology, landing in `docs/runtime-scripts.md` (new page, repo-flat-docs
  convention) + README one-hop link.
- FROZEN-ATTEMPT (16 explanation cells): same entities; fill where the design rationale
  is in-tree, else park `explanation-needs-author` (an invented "why" is worse than a
  blank). Thin utilities with no why beyond purpose are bounded out at write time with
  the reason recorded per cell — bounding out is the gate's call, not a silent drop.
- BOUNDED OUT (never frozen): every tutorial cell for B/C entities (per-script
  tutorials are the mission's named anti-pattern; getting-started is the catalog
  tutorial); explanation cells for already-covered B/C entities (common-gap
  explanations deferred to a next run — backlog, §Backlog).
- The frozen list does not grow mid-run. New entities surface → next run.

## Backlog (noticed, not frozen)

- Common-gap explanation cells for evidence-run, inventory, proof_status, bind_check,
  bundle, eval, hooks.json, settings-snippet.json, ruff.toml, print-settings-snippet.
- JPG architecture diagrams are not machine-extractable; a future run could OCR or
  sidecar the entity list.
