# PW.4.1 — Reuse Existing, Well-Secured Software When Feasible Instead of Duplicating Functionality

- Obligation (frozen NIST-SP-800-218@1.0.0): "Acquire and maintain well-secured software components (e.g., software libraries, modules, middleware, frameworks) from commercial, open-source, and other third-party developers for use by the organization’s software."
- Verdict: VERIFIED
- Target: orca-fleet @ 6390743815f8f435181fa410cce374587128b30a
- Evidence (verbatim at HEAD):
  - `runtime/pins.json:6`: "    "version": "v1.4.203","
  - `runtime/pins.json:7`: "    "witnessed": "2026-09-16","
  - `.github/ci-tools.lock:1`: "# CI tool pins, by HASH (#301)."
  - `CONTRIBUTING.md:107`: "`runtime/scripts/` is shared tooling: shell/Python, stdlib only, no secrets (env vars only),"
  - `docs/research/2026-09-10-upstream-audit/orca.md:3`: "# Orca substrate adoption audit — orca-fleet vs stablyai/orca"
- Re-derive: quotes exist at HEAD (rederive.py); components are acquired pinned (commit + hash), evaluated by dated upstream audits, re-witnessed on cadence (pin-it runs), and minimized (stdlib-only runtime); secure configurations ship as config-as-code (ruff.toml, .gitleaks.toml, spawn_worker.sh).
- Residuals: ongoing vulnerability monitoring of these components is the PW.4.4 gap, not repeated here.
