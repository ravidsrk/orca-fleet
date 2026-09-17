RUN: local-single-operator-no-orca-run · COORDINATOR: workflow-child-session-46f15971 · BASE: - · FORK_POINT: - · T0: 2026-09-16T13:01:16Z · SOURCE: symptom=issue-#440-ENOTEMPTY-teardown + fixed-point-SHA=c46d4b3f3371e41408aed19e54476fa194c20b42 · WIP: builders=0 reviewers=0
PHASE: ORIENT → RUN → DONE (planning/report-only chain; current: RUN)
WORKER-PACK-ROUTER: matt (diagnosing-bugs, feedback-loop-first) — single router for all investigation work; addy NOT co-mounted.
ORCA-ADAPTATION: single-operator run; no Orca Run id (no dispatch performed — investigation executed directly by this worker). Ledger/evidence/manifest discipline kept; WATCH/RESUME N/A.

# Unit ledger (root-cause unit = one falsifiable hypothesis about one bug)

Symptom: `test_verify.FreshnessCheck.test_wtree_equivalence_relaxes_a_content_identical_head_move`
ERRORs with `OSError: [Errno 39] Directory not empty: '/tmp/.../.git'` in
`TemporaryDirectory.__exit__ → cleanup → _rmtree → shutil.rmtree → os.rmdir('.git')`.
CI: run 35074600535, job `gates`, step `Secret scan (gitleaks, pinned)` =
`PATH="$RUNNER_TEMP/gitleaks:$PATH" python3 -m unittest discover -s tests -p test_verify.py`
(gitleaks 8.30.1 ON PATH), 243 tests, 102.831s. Assertions all passed; teardown raised.

| hypothesis_id | hypothesis | status | falsification_artifact |
|---|---|---|---|
| H1 | Runner-environment external writer (GH-ubuntu-specific daemon/FS/gitconfig creates entries in fresh scratch .gits during teardown) | SURVIVOR-UNDER-TEST (CI-only; E5/E6 in handoff) | - |
| H2 | Predecessor-leaker in the full-suite process (an earlier test leaks execution that writes via process-global cwd into a later test's tmpdir) | TESTING in decisive round F-A | - |
| H3 | Git-version-specific background writer on CI's git | TESTING in decisive round F-B (calibration: git-2.50.1 replica 0/1000 weighs against) | transcripts/linux-git250-replica-1000.txt |
| H4 | Load/timing-amplified rare window (writer exists everywhere, fires only under CI-like load) | TESTING in decisive round F-C | - |
| H5 | Gitleaks as (co-)writer | FALSIFIED (necessary-cause form) | receipts/incident-2-no-gitleaks-step.txt + import-closure audit in run-report |

Already falsified during Phase-1 calibration (loop-building, pre-freeze):
- H0a rmtree self-race/readdir-hole: FALSIFIED — `_rmtree_safe_fd` is two-phase
  (`entries = list(scandir_it)`, closed before first unlink); single-threaded =>
  scandir complete. Lemma CONFIRMED: external post-scandir creation REQUIRED.
- H0b git gc --auto from the test's own commits: FALSIFIED — 4 loose objects vs
  6700 gate; no gc.log/gc.pid; no lingering git (gc-gate probe).
- H0c git maintenance --auto: FALSIFIED — requires repo registration; fresh
  mkdtemp repos are unregistered and maintenance.repo cannot cover random paths.
- H0d in-test_verify threads/lingering processes: FALSIFIED — import-closure
  audit: stdlib-only, no threading/multiprocessing/Popen/os.spawn/os.fork;
  all spawns via blocking subprocess.run; evidence-run.py's Popen is `with`-awaited.

Method note (honest): hypotheses crystallized during loop-building; the ranked
set above was FROZEN here before the decisive falsification round (F-A/F-B/F-C)
was executed. Phase-1 calibration outputs (replica/positive-control/strip
baselines, gc-gate, audits) are loop infrastructure, not hypothesis tests.

Phase gates:
- [x] STOP-THE-LINE: fixed point c46d4b3f; CI logs captured via fence (3 incidents); prior art read (#340, 6ab0c632, RepoCase/test_run_report/test_bind_check flags)
- [x] Phase 1: red-capable loop built (phase1-harness.py: replica + catcher + flag-strip + gc-gate + positive control); signature reproduced on demand; natural rate 0 after honest elevation (macOS + Linux + git-2.50.1 + load)
- [x] Phase 2: 5 ranked falsifiable hypotheses FROZEN in-ledger before the decisive round (H1-H5; H0a-d pre-falsified in calibration, disclosed)
- [x] Phase 3: falsified one variable at a time (F-A/F-B/F-C) to a single undemonstrated survivor (H1); see ledger-falsification-close.md
- [x] Phase 4: DEMONSTRATION PARKED honestly — survivor undemonstrated, no natural repro; terminal INCONCLUSIVE per SKILL.md (never DIAGNOSED); rivals carry falsification evidence; next experiments specified (E5/E6 in fix-handoff-brief.md B1)
- [x] Manifest + fix-handoff brief (agent-brief shape, path/line-number clean) + run report; committed on campaign/root-cause-selftest (no push, no PR, no merge)

TERMINAL: INCONCLUSIVE (degraded) — every falsified hypothesis named above;
next experiments listed in fix-handoff-brief.md B1. Claim: none beyond the
falsification table + the surviving-but-undemonstrated H1.

DECISIONS-log: none yet (no mechanical/taste/one-way gates hit; fix handoff is separately authorized — this mission does not mutate).
