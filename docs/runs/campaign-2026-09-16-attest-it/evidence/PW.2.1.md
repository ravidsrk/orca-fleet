# PW.2.1 — Review the Software Design to Verify Compliance with Security Requirements and Risk Information

- Obligation (frozen NIST-SP-800-218@1.0.0): "Have 1) a qualified person (or people) who were not involved with the design and/or 2) automated processes instantiated in the toolchain review the software design to confirm and enforce that it meets all of the security requirements and satisfactorily addresses the identified risk information."
- Verdict: VERIFIED
- Target: orca-fleet @ 6390743815f8f435181fa410cce374587128b30a
- Basis: the automated leg (2) — every change is reviewed by toolchain gates on each PR; the human leg (1) is the documented build-blind review process.
- Evidence (verbatim at HEAD):
  - `.github/workflows/validate.yml:4`: "  pull_request:"
  - `playbooks/acceptance-review.md:3`: "Recipe: Matt `code-review` two-axis (isolated) + gstack review-army dispatch mechanics. Always-on for"
  - `playbooks/acceptance-review.md:61`: "Pinned fixed point (non-empty `git diff <fp>...HEAD`), ALL THREE axes reported with no cross-rerank,"
  - `docs/completion/ISSUES.md:1`: "# ISSUES — S5-C filing ledger (run 3, 2026-09-09)"
- Re-derive: quotes exist at HEAD (rederive.py); automated review (validator, contract suite, secret scan, soundness gate) runs on every PR per validate.yml; human build-blind review with recorded reviewed_sha is the documented process and findings land in the tracker.
- Residuals: solo maintainer, so the human leg is usually same-person review plus automation — the independence bar rests on the automated gates and occasional external reviews.
