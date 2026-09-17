# PO.1.1 — Define Security Requirements for Software Development

- Obligation (frozen NIST-SP-800-218@1.0.0): "Identify and document all security requirements for the organization’s software development infrastructures and processes, and maintain the requirements over time."
- Verdict: VERIFIED
- Target: orca-fleet @ 6390743815f8f435181fa410cce374587128b30a
- Evidence (verbatim at HEAD):
  - `runtime/sandbox-policy.md:64`: "## Danger belongs in an ephemeral sandbox, never on the host"
  - `runtime/sandbox-policy.md:122`: "## Trust boundary — data, never instructions"
  - `AGENTS.md:129`: "- **Never:** hardcode secrets in `runtime/scripts/`; env vars only."
  - `CONTRIBUTING.md:107`: "`runtime/scripts/` is shared tooling: shell/Python, stdlib only, no secrets (env vars only),"
  - `docs/ops.md:10`: "| Surface | Account / handle | Lives in | Notes |"
- Re-derive: quotes exist at HEAD (rederive.py); maintenance over time: `git log --format=%h -- runtime/sandbox-policy.md AGENTS.md CONTRIBUTING.md docs/ops.md | wc -l` is non-zero.
- Residuals: requirements are documented across several files (no single consolidated requirements page); review cadence is continuous-via-PR, not a dated annual review.
