# PS.2.1 — Provide a Mechanism for Verifying Software Release Integrity

- Obligation (frozen NIST-SP-800-218@1.0.0): "Make software integrity verification information available to software acquirers."
- Verdict: VERIFIED
- Target: orca-fleet @ 6390743815f8f435181fa410cce374587128b30a
- Evidence (verbatim at HEAD):
  - `docs/releases.json:7`: "      "tag": "v0.1.0","
  - `docs/releases.json:8`: "      "commit": "fc0d08c4276ae25e5e3ac48caa11976ec331e304","
  - `docs/ops.md:105`: "git tag -a "v$RELEASE_VERSION" "$cut_sha" -m "orca-fleet $RELEASE_VERSION""
  - `docs/ops.md:143`: "python3 -m unittest tests.test_docs_navigation.TestDocsNavigation tests.test_docs_navigation.EveryReleaseHasTheTagItDescribes"
- Re-derive: quotes exist at HEAD (rederive.py); all 9 releases.json rows resolve: each `commit` exists and each annotated tag peels to that commit (rederive.py checks all 9); acquirers verify with `git rev-parse <tag>^{commit}` against the published row.
- Residuals: tags are annotated, not cryptographically signed (`git verify-tag` finds no signature); no CA-backed code signing.
