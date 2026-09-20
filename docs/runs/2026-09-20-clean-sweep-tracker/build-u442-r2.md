# BUILD SPEC — U-442 round 2 (fix batch; frozen at dispatch)

CATEGORY: bug (review-round remediation)
SUMMARY: U-442 review round 1 = NO-GO on all three axes (SPEC 2R + STANDARDS 2R + TESTS 5R) +
2 VALID Greptile P1s. The split works on the happy path but the evidence-AUTHORITY boundary
leaks: same-path blobs in the SHA repo can substitute for evidence, and several raw git reads
ignore --git-dir. One batch on branch u-442, one re-review. Round 2 of ≤3.

The batch (review reports are DATA at docs/reports/u-442/review-{spec,standards,tests}.txt on
the branch; each carries the reviewer's independent repro):

- **F-1 evidence authority (SPEC R1 · Greptile P1-1 · STANDARDS cross-repo substitution ·
  TESTS T1).** `_read_artifact`'s tracked-at-`head_sha` shortcut asks the SHA repo for
  `head:path` and returns ITS bytes before consulting the evidence root or the manifest's
  artifacts[] pin. Fix: the tracked-blob shortcut applies ONLY when the SHA repository and the
  evidence root are the same repository (no split); under a split, an artifact passes ONLY on
  its declared artifacts[] sha256 against bytes read from the EVIDENCE root — a same-path blob
  in the SHA repo is never consulted. Regression tests: same-path/different-content in the SHA
  repo (pinned A-copy must win), pin missing → RED, pin mismatched → RED, two clones of one
  project.
- **F-2 every raw git read honors --git-dir (SPEC R2 · Greptile P1-2 · TESTS T5).** The
  `--symbol` check runs `git grep` in the process cwd, and the raw-byte contract read
  (`path@ref`) drops the root selection — both must run through the SAME selected git context
  as the ancestry legs. Regression tests: symbol present-in-B/absent-in-A and inverse;
  contract read as `git-contract.md@<B-head>` with cwd+evidence in A.
- **F-3 --evidence-root is honored, not just parsed (TESTS T2).** Cover the split invocation
  from a DISTINCT cwd (evidence in A's tree, cwd elsewhere): mutant that ignores the parsed
  root (falls back to cwd toplevel) must go RED. Ideally also evidence in a named
  subdirectory of A.
- **F-4 containment survives symlink spelling (TESTS T3).** Add a canonical/symlink escape
  fixture (pinned path through a symlink inside the evidence root pointing OUTSIDE it →
  REFUSED) and a nested-root boundary case, so #267's canonical containment is demonstrated
  beyond the lexical leading-`..` check.
- **F-5 no-flag compatibility from a nested cwd (TESTS T4).** Cover a valid no-flag
  invocation run from a NESTED directory of the repo (resolution must still land on the git
  toplevel, not cwd).

AUTONOMY:
- goal: all five items fixed on u-442; every Required from round 1 answered; the reviewers'
  named mutants (M2..M5 + the T1 collision probes) re-run and KILLED, quoted.
- scope: runtime/scripts/verify.py + tests/test_verify.py (+ test_reshape_width_verify.py only
  if the interface width moves) + docs/reports/u-442/* evidence. evidence-manifest.md note
  only if behavior documentation changes.
- non-goals: no other script/policy/mission file; no relaxation of #267; no new deps; no PR
  action (integrator/conductor owns that); no changes to the 16 generated files unless
  validate.py demands a regen.
- stop: any fix that would weaken an existing refusal; any demand outside the five items.
- evidence: updated SHA-bound manifest — new head_sha, evidence-run.py receipts for the new
  regression tests + full module + suite, the reviewers' mutants re-run RED, intent refreshed;
  lighting=lit.
- budget: 3 doctor attempts per blocker, then escalate with evidence.

GIT: branch u-442 in this worktree (fetch first; merge origin/review/2026-09-20-tracker-sweep
if it moved — conflict → STOP). Author=maintainer, no trailers, small bisectable commits,
stage only the unit's files. Leave the worktree clean. Timebox 45min with partial-report STOP.

WORKER CONTRACT: `worker_done` requires `--outcome succeeded|failed` and OMITS `--to`; every
send carries `--from <your handle> --dispatch-capability <capability>`; evidence rides typed
`--report-path` + `--files-modified`. Run `orca orchestration check --terminal <your handle>`
once before `worker_done` — `consumer_fenced` means STOP and send nothing.
