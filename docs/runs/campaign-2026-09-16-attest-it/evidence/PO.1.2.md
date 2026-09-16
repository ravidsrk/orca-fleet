# PO.1.2 — Define Security Requirements for Software Development

- Obligation (frozen NIST-SP-800-218@1.0.0): "Identify and document all security requirements for organization-developed software to meet, and maintain the requirements over time."
- Verdict: VERIFIED
- Target: orca-fleet @ 6390743815f8f435181fa410cce374587128b30a
- Evidence (verbatim at HEAD):
  - `AGENTS.md:130`: "- **Never:** grade completion on a trace — bind it to a SHA and verify against authoritative state."
  - `SECURITY.md:19`: "In scope: `runtime/scripts/` (especially `verify.py`, `verify-gate.sh`,"
  - `runtime/evidence-manifest.md:146`: "## 3. Standing definition-of-done floor (every mission, on top of its own contract)"
  - `.github/workflows/validate.yml:4`: "  pull_request:"
- Re-derive: quotes exist at HEAD (rederive.py); compliance is verified at SDLC gates on every PR (validate.yml `on: pull_request` + `push: main`).
- Residuals: no end-of-life/support notification policy and no stated archive-retention period (example-level gaps); requirements live across AGENTS.md/CONTRIBUTING.md/SECURITY.md/runtime policies rather than one page.
