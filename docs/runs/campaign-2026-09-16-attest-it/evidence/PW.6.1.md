# PW.6.1 — Configure the Compilation, Interpreter, and Build Processes to Improve Executable Security

- Obligation (frozen NIST-SP-800-218@1.0.0): "Use compiler, interpreter, and build tools that offer features to improve executable security."
- Verdict: VERIFIED
- Target: orca-fleet @ 6390743815f8f435181fa410cce374587128b30a
- Evidence (verbatim at HEAD):
  - `.github/workflows/validate.yml:20`: "          python-version: "3.13"  # pin: CI 3.x was a moving target (G-03)"
  - `.github/ci-tools.lock:1`: "# CI tool pins, by HASH (#301)."
  - `.github/workflows/validate.yml:83`: "          echo "${GITLEAKS_SHA256}  gitleaks.tar.gz" | sha256sum --check --strict -"
  - `runtime/pins.json:6`: "    "version": "v1.4.203","
- Re-derive: quotes exist at HEAD (rederive.py); the interpreter (CPython 3.13, current) and build/analysis tools are used up-to-date, pinned, and integrity-validated (hashes, checksums, SHA-pinned actions) with changes flowing through PR review.
- Residuals: which interpreter security features are enabled is not a documented determination — that is the PW.6.2 gap.
