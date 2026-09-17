# PO.4.1 — Define and Use Criteria for Software Security Checks

- Obligation (frozen NIST-SP-800-218@1.0.0): "Define criteria for software security checks and track throughout the SDLC."
- Verdict: VERIFIED
- Target: orca-fleet @ 6390743815f8f435181fa410cce374587128b30a
- Evidence (verbatim at HEAD):
  - `.github/workflows/validate.yml:36`: "        run: python3 scripts/eval.py run --suite routing --threshold 1.0"
  - `.github/workflows/validate.yml:143`: "      - name: VF-Bench soundness gate (verify.py false-done must be 0)"
  - `.github/workflows/validate.yml:4`: "  pull_request:"
  - `docs/completion/ISSUES.md:1`: "# ISSUES — S5-C filing ledger (run 3, 2026-09-09)"
- Re-derive: quotes exist at HEAD (rederive.py); criteria (routing threshold 1.0, 0% false-done, validator + proof gates) are enforced by CI on every PR and on main, with findings tracked in the issue tracker (sev:S2/S3 labels per ISSUES.md).
- Residuals: none statement-level.
