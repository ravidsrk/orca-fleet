# BUILD SPEC — U-442 round 3, FINAL (fix batch; frozen at dispatch)

CATEGORY: bug (review-round remediation — round 3 of 3; a round-3 NO-GO parks the unit)
SUMMARY: round 2 = NO-GO (STANDARDS GO; SPEC 3 Required; TESTS 3 Required). The split is
functionally right (both Greptile P1s resolved, bot clean); what remains is evidence
discipline, one real compatibility regression, and four coverage gaps the axes pinned.

The batch (reports are DATA: docs/reports/u-442/review-{spec,standards,tests}-r2.txt):

- **H-1 pin the F-4 fixtures (S2-R1).** The new symlink-escape manifests reference
  `escape-link/nc.txt` / `up-link/<nc>` in `negative_control.artifact` but their `artifacts[]`
  pins still name the default fixture path. Pin each manifest's artifacts[] to the artifact it
  actually names, so the refusal cases prove the pin path too.
- **H-2 refreshed r2 manifest + runner receipts (S2-R2).** The unit manifest still names
  head_sha 1ef8bd79 (round 1) with exit-1 suite and AC-3 false. Re-emit the SHA-bound manifest
  at the NEW head: evidence-run.py receipts for the r2 regression set, the full test_verify
  module, and the full suite (exit 0), new head_sha, criteria all addressed, refreshed intent,
  artifact inventory including round2 files. This is the closure artifact the verifier reads.
- **H-3 legacy symbol timeout restored (S2-R3).** The F-2 fix routed `--symbol` through
  `_git`, whose default timeout is 10s; the legacy `_run` path was 20s — a no-flag behavior
  change, reproduced by the reviewer. Pass the legacy timeout explicitly (20s) on that leg so
  the no-flag path is byte-identical in timing contract as well as output. Add the reviewer's
  repro as a regression assertion where feasible (or document why timing isn't assertable and
  pin the constant by test instead).
- **H-4 one-flag collisions (R2-T1).** `--git-dir` alone and `--evidence-root` alone are both
  SPLIT invocations for authority purposes (the defaulted other root differs). Add the
  reviewer's two collision probes as regression tests: invoked from A with only --git-dir B,
  and from B with only --evidence-root A — a colliding tracked blob with NO artifacts[] pin
  must be REFUSED in both (the `and`→`or` mutant in `_roots_are_split` dies).
- **H-5 pinned symlink escape, really (R2-T2, completes H-1).** Add the specified fixture:
  BOTH the ordinary artifact pin AND a pin for the escaping path supplied, otherwise valid
  evidence → REFUSED; and prove an inventory pin can NEVER override confinement (the N5
  mutant dies). The nested-root fixture gets its selected-root contract and ordinary command
  artifact restored.
- **H-6 symbol selection pins origin/<base>, not HEAD (R2-T3).** Add both asymmetric
  fixtures: a symbol present ONLY on local HEAD (absent from origin/<base>) must NOT satisfy
  the check; a symbol present on origin/<base> but deleted in a later local HEAD MUST still
  be found (the grep-ref→HEAD mutant dies).
- **H-7 guard hold: the pragma and the two quotations (CI guard RED on PR #485).** The
  floor guard flags `pragma: no cover` at runtime/scripts/verify.py:209 (the OSError branch
  in `_roots_are_split`) plus two review-report files that QUOTE pragmas
  (docs/reports/u-442/verdict-r2.json, verdict-review-r2.md). Fix the code, don't waive it:
  cover the branch (mock `Path.resolve` to raise OSError; assert fail-closed True) and DELETE
  the pragma. For the two report files the coordinator records DECISIONS floor-waivers
  (archival-quotation class, 2026-09-17 precedent) — the worker only verifies
  `python3 runtime/scripts/floor_guard.py` (or the repo's guard command) is green after the
  code fix + waivers.

AUTONOMY:
- goal: all items fixed on u-442; every round-2 Required answered.
- scope: runtime/scripts/verify.py (the one timeout line), tests/test_verify.py (fixture
  pins + timeout regression), docs/reports/u-442/* (manifest + receipts), badge if the count
  moves, BASE merge if BASE moved.
- non-goals: no behavior change beyond H-3's restoration; no new flags; no PR action.
- stop: if H-3's restoration conflicts with the split's root-aware timing, STOP and ask.
- evidence: refreshed manifest per H-2; mutants re-run where the test surface moved;
  lighting=lit.
- budget: 3 doctor attempts per blocker, then escalate with evidence.

GIT: branch u-442 in this worktree (fetch; merge origin/review/2026-09-20-tracker-sweep if
moved — conflict → STOP). Author=maintainer, NO TRAILERS OF ANY KIND (twice bitten — the
conductor strips them and the re-review notes it). Small commits, stage only the unit's
files. Leave the worktree clean. Timebox 35min with partial-report STOP.

WORKER CONTRACT: `worker_done` requires `--outcome succeeded|failed` and OMITS `--to`; every
send carries `--from <your handle> --dispatch-capability <capability>`; evidence rides typed
`--report-path` + `--files-modified`. Run `orca orchestration check --terminal <your handle>`
once before `worker_done` — `consumer_fenced` means STOP and send nothing.
