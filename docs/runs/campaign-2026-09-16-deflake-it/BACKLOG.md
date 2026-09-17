# BACKLOG — noticed-but-not-touched (campaign-2026-09-16-deflake-it)

- **Identify the exact late-writer process.** The #340 diagnosis ("gitleaks-on-PATH can leave a file in
  `.git/objects`") was never nailed to a specific process, and the ec917f50 recurrence happened WITH the
  gitleaks cwd isolation in place — a residual writer path exists. Teardown tolerance terminalizes the
  distribution (the throwaway repo cannot fail the suite), so this is follow-up, not an open flake.
  Suggested: strace/fs-usage capture of `.git/` writers during the gitleaks-PATH leg on Linux.
- **Unify the teardown seam.** `RepoCase.setUp` (line ~69) carries its own inline
  `ignore_cleanup_errors=True`; the four fixed sites now use `_temp_repo()`. A future third occurrence
  should route one helper through both (reshape-it tripwire per REFLECTION.md) — not done here to keep
  the fix minimal and the diff reviewable.
- **`ReviewPagination.setUp` bare tmpdir (line ~705).** Holds JSON + a fake `gh`, no git repo — outside
  the observed mechanism. Left bare deliberately; revisit only if the signature ever appears there.
- **11 deterministic `validate.py` PR-branch failures in CI history** (distinct SHAs, `attempt=1`).
  Content-gate failures, not flakes — clean-sweep territory, out of scope for deflake-it.
- **OPS owed: CI-leg verification of the F1 fix.** The task forbade push/PR/merge, so no CI ran the
  fixed SHA. The promotion PR carrying `c8abd8c` must show the `validate` workflow green (both the
  plain suite leg and the gitleaks-PATH `test_verify.py` leg) before the mission terminal STABLE can
  be honestly claimed. Local streaks are recorded in REPORT.md.
