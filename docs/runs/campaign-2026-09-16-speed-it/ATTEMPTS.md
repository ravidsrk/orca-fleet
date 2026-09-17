# Attempt ledger (one line per fix attempt, kept or reverted)

| # | Hypothesis | Before → After | Verdict | Why |
|---|-----------|----------------|---------|-----|
| H1 | deny_hook per-test identical repo builds dominate file time; class-sharing + config-fold cuts it | file {46.24,47.97,48.08} → {42.39,42.52,42.79}, 140/140 OK; journey median 273.93 → 252.69, ranges non-overlapping | KEEP | deterministic spawn cut, oracle unchanged; journey delta partly environment (see REBENCH.md) |
| (rejected pre-attempt) | bundle 12.6 s test: drop --help entry-point spawns | — | NOT TRIED | spawns ARE the oracle; removing them weakens the proof (fast-but-wrong) |
| (rejected pre-attempt) | verify RepoCase: share repos across mutating tests | — | NOT TRIED | tests commit per-test; sharing breaks hermeticity |
| (rejected pre-attempt) | parallel runner for the suite | — | NOT TRIED | infra change (new runner + CI contract + assets/badges races); beyond hotspot scope → journey park gate |

KEEP-OR-REVERT decision rule (recorded before rebench completed): KEEP iff the
rebench J1 median beats the baseline median (273.93 s) AND every rebench run
falls below the baseline minimum (272.41 s) — non-overlapping ranges, so a keep
cannot be machine jitter. WORSE or overlapping → REVERT via follow-up commit.
