# root-cause self-test — run report: the ENOTEMPTY teardown flake (issue #440)

Terminal: **INCONCLUSIVE** (degraded, honest park). Fixed point: `c46d4b3f`.
Mission: `root-cause` at its doctrine-only self-test; worker router: matt
(feedback-loop-first) only — addy not co-mounted. Single-operator adaptation
(no Orca dispatch; ledger/evidence/manifest discipline kept).

## 1. Symptom (STOP-THE-LINE)

`test_verify.FreshnessCheck.test_wtree_equivalence_relaxes_a_content_identical_head_move`
ERRORs — never FAILs — with `OSError: [Errno 39] Directory not empty` on the
scratch repo's `.git`, raised from `TemporaryDirectory.__exit__` AFTER every
assertion in the body passed. Incident: CI run 35074600535, job `gates`, step
`Secret scan (gitleaks, pinned)` = the contract suite for the verifier module
run with gitleaks 8.30.1 on PATH (243 tests, 102.8s). Receipt:
`receipts/incident-440-ci-error.txt`.

This is the mission's exact target class: a hard intermittent bug (flaky
teardown failure) with no frozen spec and no enumerable backlog, a single-bug
unit (not a suite-wide flake rate — `deflake-it` does not apply).

## 2. Prior art (same seam)

- #340 (Sept 13): same OSError 39 on `.git/objects` in the gitleaks step;
  attributed to gitleaks without a demonstrated mechanism; fixed by scanner-cwd
  isolation + `ignore_cleanup_errors` on the shared temp-repo fixture.
- Sept-13 second incident (commit 6ab0c632): same OSError 39 on `.git/objects`
  in the **no-gitleaks** step (verified from the step log this run —
  `receipts/incident-2-no-gitleaks-step.txt`); writer explicitly unidentified;
  suppressed with the same flag.
- A third suite has since taken the same flag. Three suppressions, zero
  identified causes: per the mission's prior-art rule, this seam needed a
  diagnosis, not a fourth suppression. This run is that diagnosis attempt.

## 3. Phase 1 — red-capable loop (built before theory)

`phase1-harness.py` (new evidence file; the tests under diagnosis were never
edited): exact-method replica with a leftover-catcher (on ENOTEMPTY the tmpdir
survives, so the harness lists leftover entries + process snapshot), a
flag-strip mode (forces `ignore_cleanup_errors` OFF suite-wide to unmask a
common writer), a gc-gate probe, and a positive control.

- Positive control: a deliberate concurrent writer into `.git` during teardown
  reproduces the EXACT CI signature (`Directory not empty: '.../.git'`).
  The diagnostic chain is validated; the signature mechanism (post-scandir
  creation) is proven. `transcripts/positive-control.txt`.
- Natural-rate baselines (all green): 300 + 300 macOS replicas (plain and
  gitleaks-on-PATH), 243-test strip on macOS, 2000 + 1000 Linux replicas
  (Python 3.13.15 = CI's exact version; git 2.39.5 and source-built 2.50.1;
  gitleaks 8.30.1 on PATH), 243-test strips x2 + intact run on Linux
  (95.5s vs CI's 102.8s — faithful timing replica).
- Lemma CONFIRMED from CPython 3.13 source (local == CI line numbers 658/707/
  763): `_rmtree_safe_fd` is two-phase (`entries = list(scandir_it)`, closed
  before the first unlink of that directory). Single-threaded + two-phase =>
  a missed entry is impossible; a concurrent creator between scandir and rmdir
  is REQUIRED on a sane local filesystem. The leftover in #440 is a DIRECT
  child of `.git` (every subdir removed OK); in the two priors it sat in
  `.git/objects`.

## 4. Frozen hypotheses (ranked, shown before the decisive round)

| id | hypothesis | verdict |
|----|-----------|---------|
| H1 | Runner-environment external writer (GH-ubuntu-specific daemon / FS behavior / gitconfig-driven git background task) | SURVIVES, undemonstrated (CI-only) |
| H2 | Predecessor-leaker in the full-suite process (earlier test leaks execution writing via process-global cwd) | FALSIFIED (F-A) |
| H3 | Git-version-specific background writer on CI's git | FALSIFIED (F-B + calibration) |
| H4 | Load/timing-amplified ubiquitous writer | FALSIFIED (F-C, no support) |
| H5 | Gitleaks as (co-)writer | FALSIFIED as necessary cause (incident #2 step log) |
| H0a | rmtree self-race / readdir hole | FALSIFIED in calibration (two-phase source proof) |
| H0b | git gc --auto from the test's own commits | FALSIFIED (4 objects vs 6700 gate; gc-gate probe) |
| H0c | git maintenance --auto | FALSIFIED (registration gate; random mkdtemp paths uncoverable) |
| H0d | In-suite threads / lingering processes | FALSIFIED (import-closure audit: stdlib-only, no threading/multiprocessing/Popen/os.spawn/os.fork across every test module; all spawns blocking; the one shipped Popen is `with`-awaited; no tests/__init__.py side effects) |

Decisive round: F-A full-suite global strip on Linux, full tree, no gitleaks
(1482 tests, 0 ENOTEMPTY); F-B verifier-module strip on git 2.50.1 with
gitleaks (243 tests, 0 errors, 0 ENOTEMPTY); F-C loaded replica x500
(0 failures). Transcripts under `transcripts/`.

## 5. Why INCONCLUSIVE, and what would change it

Every rival of H1 is falsified with evidence, but H1 itself is not
demonstrated: no writer was caught, no natural repro was produced in ~7950
test-executions (~5-6k scratch-git teardowns) across macOS and Linux. The
CI-measured rate (~1e-5 per scratch-git teardown; workings in
`receipts/run-volume.txt`) predicts ~0.1 hits at that volume — the
non-reproduction is consistent, not evidence of absence. A "cause" with no
run reproduction is not a diagnosis, so this run parks INCONCLUSIVE per the
mission's degraded terminal, with the next experiments specified as a
durable handoff (`fix-handoff-brief.md`, briefs B1-diagnostic and
B2-hardening, separately authorized — this mission mutated nothing).

The single most valuable next datum is the LEFTOVER ENTRY'S NAME on the next
CI incident (an `index.lock` says git-with-cwd-here; `gc.log`/`gc.pid` says
background gc; `tmp_obj_*` says object write; anything else narrows
similarly). Brief B1 specifies exactly that catcher plus a one-time runner
environment dump (`df -T /tmp`, system+global gitconfig with origins,
git version, kernel, process list).

## 6. Findings that stand regardless

1. Gitleaks is REFUTED as a necessary cause (incident #2 step verification).
   The #340 comment attributing the writer to gitleaks is unproven and at
   least sometimes wrong; the handoff brief asks that it be softened when the
   writer is caught.
2. The in-process space is CLOSED by audit: no thread/linger/daemonize
   primitive exists in any test module or shipped script on the failing paths.
3. The failure physics is pinned: post-scandir creation by an external party
   is required; the teardown window is milliseconds wide (whole-tree unlink
   between scandir and rmdir of `.git`), which is why the flake is rare but
   not impossible.
4. Rate bound: order 1e-5 per scratch-git teardown at current CI volume.

## 7. Evidence map

- `ledger.md` + `ledger-falsification-close.md`: header, phase gates, frozen
  hypotheses, falsification close-out.
- `phase1-harness.py`: the red-capable loop + catcher (runnable).
- `transcripts/`: 11 observed outputs (replicas, strips, gc-gate,
  positive control, F-A/F-B/F-C).
- `receipts/`: 5 CI-log excerpts via the text fence + run-volume Fermi.
- `fix-handoff-brief.md`: B1 (diagnostic experiment) + B2 (hardening) briefs.
- `evidence-manifest.json` + `inventory.txt`: SHA-bound manifest (planning
  class; demonstration parked) + integrity inventory.
