# PO.3.2 — Implement Supporting Toolchains

- Obligation (frozen NIST-SP-800-218@1.0.0): "Follow recommended security practices to deploy, operate, and maintain tools and toolchains."
- Verdict: VERIFIED
- Target: orca-fleet @ 6390743815f8f435181fa410cce374587128b30a
- Evidence (verbatim at HEAD):
  - `.github/ci-tools.lock:1`: "# CI tool pins, by HASH (#301)."
  - `.github/workflows/validate.yml:83`: "          echo "${GITLEAKS_SHA256}  gitleaks.tar.gz" | sha256sum --check --strict -"
  - `.github/workflows/validate.yml:15`: "      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1 (Node 24; Node 20 left runners 2026-09-23, #367)"
  - `runtime/pins.json:7`: "    "witnessed": "2026-09-16","
- Re-derive: quotes exist at HEAD (rederive.py); practices evidenced: hash-pinned installs (--require-hashes against ci-tools.lock), checksum-verified tool download before execution, commit-SHA-pinned Actions, pipeline-as-code, and re-witnessed upstream pins (2026-09-16).
- Residuals: none statement-level.
