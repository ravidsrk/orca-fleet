# RV.2.2 — Assess, Prioritize, and Remediate Vulnerabilities

- Obligation (frozen NIST-SP-800-218@1.0.0): "Plan and implement risk responses for vulnerabilities."
- Verdict: VERIFIED
- Target: orca-fleet @ 6390743815f8f435181fa410cce374587128b30a
- Evidence (verbatim at HEAD):
  - `playbooks/remediate-finding.md:13`: "2. **Fix** via `build-change` (failing test first / red repro, smallest change, negative control)."
  - `playbooks/remediate-finding.md:18`: "4. **Build-blind REVIEW** (acceptance-review, + risk-review lens if the finding is a risk class);"
  - `docs/ops.md:195`: "4. Rollback = `git revert -m 1 <merge-sha>` on a branch, then a PR"
  - `CHANGELOG.md:20`: "What the #308 round changed about the verifier is worth naming, because each was a way a unit"
- Re-derive: quotes exist at HEAD (rederive.py); risk responses are planned per finding (verify → fix → review → merge → close with evidence), temporary mitigations ship as CODE_CLOSED+VERIFY_AT_SCALE when acceptance needs unreachable state, rollback is rehearsed, and remediations reach acquirers through tagged releases with changelog entries.
- Residuals: none statement-level.
