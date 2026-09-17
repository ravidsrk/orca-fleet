# PO.3.3 — Implement Supporting Toolchains

- Obligation (frozen NIST-SP-800-218@1.0.0): "Configure tools to generate artifacts of their support of secure software development practices as defined by the organization."
- Verdict: VERIFIED
- Target: orca-fleet @ 6390743815f8f435181fa410cce374587128b30a
- Evidence (verbatim at HEAD):
  - `.github/workflows/validate.yml:121`: "      - name: Publish the gate summary (proof rollup + routing score)"
  - `.github/workflows/validate.yml:133`: "          } >> "$GITHUB_STEP_SUMMARY""
  - `runtime/evidence-manifest.md:144`: "later audit reject an artifact whose hash no longer matches."
  - `docs/ops.md:172`: "1. A red `validate` or `negative-control-demo` run on `main` files (or updates) an issue labeled"
- Re-derive: quotes exist at HEAD (rederive.py); artifacts generated: per-run gate summaries, SHA-bound evidence manifests, integrity inventories, and filed ci-failure issues.
- Residuals: artifact retention policy (how long summaries/inventories are kept) is not stated (example-level).
