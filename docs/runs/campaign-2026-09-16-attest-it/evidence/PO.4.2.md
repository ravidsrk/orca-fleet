# PO.4.2 — Define and Use Criteria for Software Security Checks

- Obligation (frozen NIST-SP-800-218@1.0.0): "Implement processes, mechanisms, etc. to gather and safeguard the necessary information in support of the criteria."
- Verdict: VERIFIED
- Target: orca-fleet @ 6390743815f8f435181fa410cce374587128b30a
- Evidence (verbatim at HEAD):
  - `runtime/evidence-manifest.md:106`: "  always passes through) that appends the record above, fingerprinting the tree with `wtree.sh` BEFORE the run. That"
  - `runtime/evidence-manifest.md:144`: "later audit reject an artifact whose hash no longer matches."
  - `runtime/evidence-manifest.md:30`: "    {"label": "tests", "cmd": "pnpm test src/pay", "cmd_sha256": "<sha256 of that exact command line>", "exit": 0,"
- Re-derive: quotes exist at HEAD (rederive.py); mechanism: evidence-run.py auto-gathers command records with tree fingerprints into SHA-bound manifests; safeguarding is git immutability plus per-artifact sha256 inventories that later audits re-hash.
- Residuals: the gathered information is public (open repo), so "authorized-only access" does not apply; integrity (not confidentiality) is the safeguard.
