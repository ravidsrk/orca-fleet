# Falsification round complete — terminal: INCONCLUSIVE (degraded, honest park)

F-A (H2 predecessor-leaker): SUITE-STRIP-ALL on Linux, full tree (1482 tests),
all ignore_cleanup_errors forced OFF, no gitleaks (Sept-13 step replica):
0 ENOTEMPTY across 1482 tests => H2 FALSIFIED (no suite-resident leaker;
agrees with the no-thread-primitives audit of every test file).
Artifact: transcripts/linux-FA-fulltree-strip.txt

F-B (H3 git-version writer): test_verify strip (243 tests) on git 2.50.1
(newer than CI) WITH gitleaks 8.30.1: 0 errors, 0 ENOTEMPTY => H3 FALSIFIED.
Artifact: transcripts/linux-FB-git250-strip.txt

F-C (H4 load-amplified window): replica x500 on Linux under CPU churn +
parallel git churn on /tmp, gitleaks on PATH: 0 failures => H4 FALSIFIED
(as a locally-testable conjunction; a wider window with no writer still
never fails).
Artifact: transcripts/linux-FC-loaded-500.txt

Survivor: H1 (runner-environment external writer) — UNDEMONSTRATED from here.
CI-only next experiments E5 (runner env dump) + E6 (leftover-catcher in CI)
are specified in the handoff brief. Terminal per SKILL.md: INCONCLUSIVE.
Never reported as DIAGNOSED.

Totals: ~7950 test-executions / ~5-6k scratch-git teardowns locally + Linux,
0 natural reproductions. Expected at the CI-measured rate (~1e-5/teardown):
~0.1 hits — consistent.
