# RATCHET — red-by-revert for F1 (negative control)

Unit F1: OSError-39 teardown race on temp git repos in `tests/test_verify.py` (gitleaks-PATH CI leg).
Fix: `_temp_repo()` helper (`ignore_cleanup_errors=True`, the #340 mitigation) + 4 call-site swaps
+ pinning regression test `FreshnessCheck.test_throwaway_repo_teardown_tolerates_a_late_writer`.

Control (tool `hand`, surgical flag flip — the fix line only, test kept):

Pinned mutant: hand m-F1 _temp_repo: True->False (diff quoted in RATCHET.md)

```diff
diff --git a/tests/test_verify.py b/tests/test_verify.py
index abaaf37..96e9963 100755
--- a/tests/test_verify.py
+++ b/tests/test_verify.py
@@ -53,7 +53,7 @@ def _temp_repo(suffix=None, prefix=None, dir=None):  # noqa: ANN001, ANN202 - te
     on Linux CI a late writer in the gitleaks-PATH leg can leave .git/ non-empty while rmtree runs
     (OSError 39; CI run 35074600535 hit a bare site after b726431 covered RepoCase only)."""
     return tempfile.TemporaryDirectory(suffix=suffix, prefix=prefix, dir=dir,
-                                       ignore_cleanup_errors=True)
+                                       ignore_cleanup_errors=False)
 
 
 class RepoCase(unittest.TestCase):
```

Bound command (ONE string; coordinator-supplied):

```
python3 -m unittest tests.test_verify.FreshnessCheck.test_throwaway_repo_teardown_tolerates_a_late_writer
```

## Arms (2026-09-16, macOS arm64, Python 3.13.15, this worktree)

| Arm | Result | Transcript sample |
|---|---|---|
| Fixed (`True`) x1 | OK (0.130s) | `ratchet-green-sample.log` |
| Reverted (`False`) x20 | pass=0 fail=20, rate 1.0 — RED via `AssertionError: Lists differ: ['OSError errno=66', ...] != []` (errno 66 macOS = errno 39 Linux = ENOTEMPTY; 10/10 raced trials raised per run) | `ratchet-red-sample.log` |
| Restored (`True`) x20 | pass=20 fail=0, rate 0.0 — mini-streak green | `ratchet-green-sample.log` |

Restore verified byte-identical (`cmp` clean) against the pre-revert file; `git diff --stat` unchanged
after restore. The reverted arm's RED is assertion-shaped (`AssertionError` from `assertEqual`), not a
loader/import error: the oracle (test collected, trials ran, teardown raised) is intact.

## Why revert-the-file would be the wrong control here

`git checkout <base> -- tests/test_verify.py` would remove the pinning test along with the fix, so the
bound command would go red via a loader error (test not found) — a stillborn-shaped RED that proves
nothing about the fix line. The surgical flag flip keeps the oracle and binds the RED to the change.
