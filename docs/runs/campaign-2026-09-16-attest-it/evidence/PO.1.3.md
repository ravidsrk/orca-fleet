# PO.1.3 — Define Security Requirements for Software Development

- Obligation (frozen NIST-SP-800-218@1.0.0): "Communicate requirements to all third parties who will provide commercial software components to the organization for reuse by the organization’s own software. .Formerly PW.3.1"
- Verdict: VERIFIED
- Target: orca-fleet @ 6390743815f8f435181fa410cce374587128b30a
- Basis: the component inventory contains zero commercial components — all third-party inputs are open-source upstreams or stdlib — so the set of third parties to communicate to is empty. The inventory itself is the artifact.
- Evidence (verbatim at HEAD):
  - `runtime/pins.json:4`: "    "repo": "stablyai/orca","
  - `runtime/pins.json:12`: "    "repo": "garrytan/gstack","
  - `runtime/pins.json:20`: "    "repo": "addyosmani/agent-skills","
  - `runtime/pins.json:28`: "    "repo": "mattpocock/skills","
  - `CONTRIBUTING.md:107`: "`runtime/scripts/` is shared tooling: shell/Python, stdlib only, no secrets (env vars only),"
  - `docs/ops.md:18`: "No other cloud accounts, registries, or production hosts. "Deploy" is merge"
- Re-derive: quotes exist at HEAD (rederive.py); the full third-party set is pins.json repos (all public OSS GitHub projects) + .github/ci-tools.lock (ruff, skills-ref; OSS) + Python stdlib; no commercial acquisition document exists because there is nothing commercial to acquire.
- Residuals: none. If a commercial component is ever acquired, this obligation re-opens and needs acquisition language.
