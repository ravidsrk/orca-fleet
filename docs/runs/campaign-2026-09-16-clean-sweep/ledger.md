RUN: solo-no-orca-campaign · COORDINATOR: session-a4a0c7e3 (Muse Spark) · BASE: campaign/clean-sweep-selftest · FORK_POINT: 6390743815f8f435181fa410cce374587128b30a · T0: 2026-09-16T09:59:44Z · SOURCE: tracker q1+q2 agree, 9 open, q1-sha256:1ae6477ec9a54d06a67d2d521aa5dfb8dabd40328a0d50c903c517c19a928526 · WIP: builders=1 reviewers=1
PHASE: FREEZE
TASK-PACK: matt (triage + tdd builder + code-review method) — one pack, never co-mounted.
DEVIATIONS (solo harness): D1 no Orca dispatch (contract forbids recursive/Native-agent control) — coordinator executes phases in-session with phase-separated evidence; D2 harness forbids push/PR/merge and tracker writes — units stop at verified-BUILT locally, no closes posted; D3 review independence is instructed-isolation (no second identity) — executed-control lane where legal, else stop-at-build.

| task_id | id | title | CLASS | BUILD_DONE | PR_OPEN | BOT | REVIEWED | MERGED | WT_CLEAN | lighting | park | evidence |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| T434 | #434 | Regenerate proof-ladder diagrams post-first-promotion | real-bug | f | f | n/a | f | f | n/a | lit | — | triage/verdicts.md; taskspec pending |
| — | #440 | Flaky wtree_equivalence teardown | out-of-scope | — | — | — | — | — | — | — | out-of-scope → deflake-it | triage/verdicts.md + triage/440-determinism-probe.txt |
| — | #427 | Re-pin Orca contract | out-of-scope | — | — | — | — | — | — | — | out-of-scope → pin-it | triage/verdicts.md |
| — | #417 | Mission-chaining exercise | out-of-scope | — | — | — | — | — | — | — | out-of-scope → chaining run | triage/verdicts.md |
| — | #409 | Promote harden-it to self-run | out-of-scope | — | — | — | — | — | — | — | out-of-scope → harden-it | triage/verdicts.md |
| — | #408 | Settle runway G1-G4 | — | — | — | — | — | — | — | — | needs-human (G1/G2/G3 owed) | gate-batch.json re-read 2026-09-16 |
| — | #407 | Roadmap epic 0.6.1→1.0 | out-of-scope | — | — | — | — | — | — | — | out-of-scope → roadmap children | triage/verdicts.md |
| — | #386 | Sign manifest/inventory | — | — | — | — | — | — | — | — | needs-human (G1 owed + owner-deferred) | gate-batch G1; owner comment 2026-09-14 |
| — | #235 | Marketplace submissions | — | — | — | — | — | — | — | — | needs-human (external accounts) | docs/distribution.md boxes `[ ]` |
