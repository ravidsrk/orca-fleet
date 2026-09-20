verdict: NO-GO — round 1

PR #484 · reviewed_sha `5328cc866d3b213c444687b9c7d9cb2d1d45d853` · reviewed_wtree `f6dd754d53cd329e4406ccd7bfa1f79f18693a99`.

Zero Critical, nine Required axis findings, and three unresolved VALID held bot findings. Findings retain their axis order and severity; bot P1/P2 priorities are unchanged. S3 is Optional. Every blocker below remains open.

| Spec | Standards | Test adequacy | Held bots (VALID) |
|---|---|---|---|
| **SPEC-1 — Required:** Wrong promotion boundary; `integration BASE` cannot prove BASE→default promotion. | **S1 — Required:** Promotion contradicts doctrine: `integration BASE — is a one-way human gate`. | **TA-441 — Required:** Human-gate mutants survive `r"human-paced", r"link boundary"`. | **BOT-1 — P1:** Wrong base: `origin/<base>` proves integration, not promotion. |
| **SPEC-2 — Required:** AC-1 misses obligations; `r"reconstruction artifacts"` survives optional-publication mutants. | **S2 — Required:** `seed sources plus the leg's full diff` cannot preserve cited commits/ancestry. | **TA-443 — Required:** Optional/deleted schema survives `r"carry table", r"gate record"`. | **BOT-2 — P2:** `Worked exemplar:` still describes a proposed, unspecified format. |
| **SPEC-3 — Required:** AC-3 remains unmet: `"addressed": false`; five baseline failures persist. | **S3 — Optional:** Optional wrapping brittleness: `out.append("\n".join(cur))`. | **TA-444 — Required:** No-bytes/SHA-only mutants survive `r"reconstruction artifacts"`. | **BOT-3 — P2:** Semantic regressions survive `re.search(p, b, re.I)`. |
| **SPEC-4 — Required:** AC-4 lacks archived `evidence-run.py` receipt; submitted command is `python3 -m unittest`. | — | — | — |

Source reports: `docs/reports/U-CHAIN/{review-spec.txt,review-standards.txt,review-tests.txt,integrate.json}`; full locations, verbatim motivating lines, and source hashes are retained in `verdict.json`.

Fix the blocking policy/test/evidence findings and reconcile the baseline suite failures before a fresh SHA-bound review. This COMMENTED review records a completed NO-GO assessment. The subsequent evidence commit changes reports only; reviewed_sha remains the pre-evidence code head.
