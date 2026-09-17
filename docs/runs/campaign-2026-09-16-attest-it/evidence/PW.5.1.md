# PW.5.1 — Create Source Code by Adhering to Secure Coding Practices

- Obligation (frozen NIST-SP-800-218@1.0.0): "Follow all secure coding practices that are appropriate to the development languages and environment to meet the organization’s requirements."
- Verdict: VERIFIED
- Target: orca-fleet @ 6390743815f8f435181fa410cce374587128b30a
- Evidence (verbatim at HEAD):
  - `AGENTS.md:129`: "- **Never:** hardcode secrets in `runtime/scripts/`; env vars only."
  - `runtime/sandbox-policy.md:135`: "## Scripts: argv, never interpolation"
  - `CONTRIBUTING.md:107`: "`runtime/scripts/` is shared tooling: shell/Python, stdlib only, no secrets (env vars only),"
  - `ruff.toml:7`: "select = ["E9", "F63", "F7", "F82"]"
  - `ruff.toml:4`: "target-version = "py313""
- Re-derive: quotes exist at HEAD (rederive.py); language-appropriate practices are documented (no hardcoded secrets, argv-never-interpolation, stdlib-only, fail-closed exits) and enforced by the ruff gate plus secret scanning on every PR.
- Residuals: ruff covers syntax/undefined-names only, not a security ruleset (see PW.6.2 gap); input-validation/error-handling discipline is per-script convention, not a linted rule.
