verdict: NO-GO — round 2

Zero Critical; ten Required axis entries (overlaps retained), plus two VALID held bots. Each axis keeps its own severity; no cross-rerank.

| Axis | Open stickers and findings |
| --- | --- |
| Spec — 1 Required | **SPEC-R2-1 / BOT-4:** `origin/<default>` lacks a refresh obligation; a stale ref can strand a legitimately resumable chain. |
| Standards — 3 Required | **S-R2-1 / BOT-4:** `origin/<default>` is cached evidence. **S-R2-2 / BOT-5:** `BASE = Path("base-policy.md").read_text()` requires an unpublished fixture. **S-R2-3:** `sys.exit(1 if surv else 0)` reports success despite failed controls or import errors. |
| Test adequacy — 6 Required | **R2-TA-441:** `must(park, r"(?i)ancestor of the DEFAULT branch",` permits six resume-condition regressions. **R2-TA-443:** `for field in (r"carry id", r"input status"):` leaves three schema/missing-log regressions unprotected. **R2-TA-444:** `must(local, r"(?i)reproduces every cited commit",` misses three ancestry/retrieval/integrity regressions. **BOT-4:** stale `origin/<default>`; **BOT-5:** missing `BASE = Path("base-policy.md").read_text()` fixture; **R2-HARNESS:** `sys.exit(1 if surv else 0)` accepts invalid mutation evidence. |
| Held bots | **BOT-4 — P1, VALID:** stale `origin/<default>` blocks resume. **BOT-5 — P2, VALID:** `BASE = Path("base-policy.md").read_text()` fails in a clean checkout. Both remain held; bot priorities are preserved. |

The original doctrine corrections and F-4/F-5/F-6 are closed on the submitted reviews; F-3 remains partial. The historical 13/13 battery reproduces after fixture recovery, but twelve narrower mutants survive. BOT-3's residuals are covered by R2-TA-441/R2-TA-443. Fix all listed Required findings and held defects, then re-review.

Reviewed SHA: `302d43e9e028f93d0698bccaa93f308f1fdbdb63`; reviewed tree: `f66caa068a07d574be260054e51118413468cfbf`. Inputs: `review-spec-r2.txt`, `review-standards-r2.txt`, `review-tests-r2.txt`, and `integrate-r2.json` under `docs/reports/U-CHAIN/`. The axes reviewed `0dbc669e`; its only successor change is the integration report, inspected for this aggregation. The forthcoming report-only evidence commit is code-identical but changes the full Git tree; this verdict remains bound to the SHA above.
