verdict: NO-GO — round 1

Reviewed SHA: `a5f84978548a00a97cfcc11614aa6bdfd71683e6`; reviewed tree: `8a39ac3e3576dc1eafdb3e7ddfb60734b1408184`.

All three axes are NO-GO. Counts and severity remain separate; overlapping findings are not deduplicated or reranked.

| Axis | Counts | Sticking findings |
| --- | --- | --- |
| Spec | 0 Critical, 2 Required | **R1:** Same-path SHA-repository blobs replace evidence-root artifacts and bypass their inventory pins (`runtime/scripts/verify.py:276`: `code, out, gerr = _git_bytes(["show", f"{head}:{path}"])`). **R2:** Symbol lookup bypasses the selected Git root (`:1720`: `code, out, _ = _run(["git", "grep", "-l", "-e", symbol, f"origin/{base}"])`). |
| Standards | 0 Critical, 2 Required | **STD-1:** Wrong-repository artifact substitution violates authoritative, fail-closed evidence (`verify.py:276`: `code, out, gerr = _git_bytes(["show", f"{head}:{path}"])`). **STD-2:** Symbol-on-base can approve the evidence repository's symbol (`:1720`: `code, out, _ = _run(["git", "grep", "-l", "-e", symbol, f"origin/{base}"])`). |
| Test adequacy | 0 Critical, 5 Required | **T1:** Same-path collisions and absent pins are uncovered (`verify.py:276`: `code, out, gerr = _git_bytes(["show", f"{head}:{path}"])`). **T2:** Ignoring the evidence-root flag survives (`test_verify.py:3132`: `Repo A (this case's repo, and the cwd) holds the manifest, the contract and the artifacts.`). **T3:** Removing canonical containment survives (`verify.py:208`: `if full != root and root not in full.parents:`). **T4:** Nested-cwd legacy compatibility is uncovered (`:200`: `top = out.strip() if code == 0 else None`). **T5:** Raw Git reads can ignore the SHA root (`:143`: `return _run_bytes(["git", *(["-C", _ROOTS["git"]] if _ROOTS["git"] else []), *args],`). |
| Held Greptile findings | 2 VALID P1, unfixed | **4056474414:** Artifact pinning can be bypassed; motivating line quoted under R1. **4056474416:** Symbol check uses wrong repository; motivating line quoted under R2. |

The three reports record 1,714 passing tests, but four behavioral mutants survive the 255 verifier tests. Both production defects were reproduced at the reviewed SHA. Fix every sticking finding, then re-review.

Details: `docs/reports/u-442/review-{spec,standards,tests}.txt` and `integrate.json`. A code-identical, reports-only evidence commit follows; the reviewed SHA/tree remain the pre-evidence binding, and the full tree changes when reports are committed.
