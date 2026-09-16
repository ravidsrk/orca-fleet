# PO.3.1 — Implement Supporting Toolchains

- Obligation (frozen NIST-SP-800-218@1.0.0): "Specify which tools or tool types must or should be included in each toolchain to mitigate identified risks, as well as how the toolchain components are to be integrated with each other."
- Verdict: VERIFIED
- Target: orca-fleet @ 6390743815f8f435181fa410cce374587128b30a
- Evidence (verbatim at HEAD):
  - `.github/workflows/validate.yml:15`: "      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1 (Node 24; Node 20 left runners 2026-09-23, #367)"
  - `.github/workflows/validate.yml:20`: "          python-version: "3.13"  # pin: CI 3.x was a moving target (G-03)"
  - `.github/workflows/validate.yml:36`: "        run: python3 scripts/eval.py run --suite routing --threshold 1.0"
  - `runtime/pins.json:5`: "    "commit": "54eaa14756bf80a6deb0b9cb5349fbe8ac3449ec","
  - `runtime/pins.json:7`: "    "witnessed": "2026-09-16","
- Re-derive: quotes exist at HEAD (rederive.py); the toolchain is specified as pipeline-as-code (validate.yml jobs/steps with pinned tools) plus the upstream pin record (pins.json) and the contributor gate list (CONTRIBUTING.md "Before you open the PR").
- Residuals: none statement-level.
