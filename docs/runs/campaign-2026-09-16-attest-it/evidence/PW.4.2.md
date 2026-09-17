# PW.4.2 — Reuse Existing, Well-Secured Software When Feasible Instead of Duplicating Functionality

- Obligation (frozen NIST-SP-800-218@1.0.0): "Create and maintain well-secured software components in-house following SDLC processes to meet common internal software development needs that cannot be better met by third-party software components."
- Verdict: VERIFIED
- Target: orca-fleet @ 6390743815f8f435181fa410cce374587128b30a
- Evidence (verbatim at HEAD):
  - `CONTRIBUTING.md:99`: "## Changing runtime policies or scripts"
  - `CONTRIBUTING.md:107`: "`runtime/scripts/` is shared tooling: shell/Python, stdlib only, no secrets (env vars only),"
  - `.github/workflows/validate.yml:22`: "        run: python3 scripts/validate.py"
  - `.github/workflows/validate.yml:23`: "      - name: Run the contract test suite without Gitleaks"
- Re-derive: quotes exist at HEAD (rederive.py); in-house components (runtime/scripts/*, scripts/*) are created and maintained under the repo SDLC: documented practices, validator gates, and the contract suite on every PR; the git repo itself is the component repository with full version history.
- Residuals: none statement-level.
