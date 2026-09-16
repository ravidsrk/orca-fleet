# PS.3.1 — Archive and Protect Each Software Release

- Obligation (frozen NIST-SP-800-218@1.0.0): "Securely archive the necessary files and supporting data (e.g., integrity verification information, provenance data) to be retained for each software release."
- Verdict: VERIFIED
- Target: orca-fleet @ 6390743815f8f435181fa410cce374587128b30a
- Evidence (verbatim at HEAD):
  - `docs/releases.json:8`: "      "commit": "fc0d08c4276ae25e5e3ac48caa11976ec331e304","
  - `docs/ops.md:160`: "investigation. Preserve published rows and refs; correct a bad release with a new"
  - `docs/ops.md:143`: "python3 -m unittest tests.test_docs_navigation.TestDocsNavigation tests.test_docs_navigation.EveryReleaseHasTheTagItDescribes"
- Re-derive: quotes exist at HEAD (rederive.py); the archive is the git object store (content-addressed, immutable history — no force-push per ops.md:196) holding every release cut, tag, CHANGELOG entry, and releases.json row; the tag↔row binding is machine-checked by the cited test on every suite run.
- Residuals: no stated retention period; "read-only access by necessary personnel" is satisfied trivially (public read, maintainer write) rather than by an access policy.
