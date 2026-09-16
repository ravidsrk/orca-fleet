# Research brief — SSDF obligation-catalog source

- Question (verbatim): "What is the authoritative, version-pinned, machine-readable source for the NIST Secure Software Development Framework (SP 800-218) obligation set, and what is its exact task enumeration?"
- Decision waiting on it: freeze the attest-it denominator (`standard@version` + SOURCE digest) for the orca-fleet self-attestation run.
- Read date: 2026-09-16. Worker profile: ro (fetch + read only; no tree mutation for research itself).

## Answer

Freeze **NIST-SP-800-218@1.0.0** with SOURCE = NIST's own OSCAL catalog JSON
`nist.gov/SP800-218/ver1/json/NIST_SP800-218_ver1_catalog.json` from the
`usnistgov/oscal-content` repo (NIST's official OSCAL representation of its publications).
It enumerates **42 tasks** in 4 groups (PO 13, PS 4, PW 16, RV 9). The bytes are frozen
in this run dir at `catalog/NIST_SP800-218_ver1_catalog.json`.

## Claims and owning sources

- NIST maintains `usnistgov/oscal-content` as the official OSCAL representation of its
  publications, including the SP 800-218 v1 catalog in JSON/XML/YAML — owner: NIST CSRC
  OSCAL FAQ + usnistgov/oscal repo README, read 2026-09-16 via
  `https://Csrc.nist.gov/Projects/open-security-controls-assessment-language/faqs` and
  `https://github.com/usnistgov/oscal`.
- The catalog file lives at `nist.gov/SP800-218/ver1/json/NIST_SP800-218_ver1_catalog.json`
  (253878 bytes, git blob `94f85f214557d4f52faddbf0b2e83de55d11db5d`) — owner: GitHub API
  listing of `usnistgov/oscal-content` path `nist.gov/SP800-218/ver1/json`, ref `main`,
  read 2026-09-16.
- The file's last upstream change is commit `78650f02ad9321bb7b817846f8fbd4f2bcd620de`
  ("Publishing auto-converted artifacts", 2026-05-13, oscalbuilder bot) — owner: GitHub
  API commits for that path, read 2026-09-16.
- Downloaded bytes sha256 `b01634a5fdb382e7a12660c379a4d0bc3a2b8e29abccf2861834880005137117`;
  `git hash-object` of the bytes equals the advertised blob sha above — owner: local
  computation on fetched bytes, 2026-09-16 (see Verification leg).
- Catalog metadata title "Electronic (OSCAL) Version of Secure Software Development
  Framework (SSDF)", version `1.0.0` — owner: the file's own `catalog.metadata`, read
  2026-09-16.
- Task shape: groups → practices (`controls`) → tasks (`controls` with `class: task`),
  each task carrying a `statement` part plus `example` parts; count = 42 — owner: the
  file's own structure, parsed 2026-09-16.
- SSDF v1.1 exists (Feb 2022, clarifications over v1.0) but the official OSCAL repo
  exposes only `ver1`; no `ver1.1` directory exists under `nist.gov/SP800-218` — owner:
  GitHub API listing of `nist.gov/SP800-218` (single entry `ver1`), read 2026-09-16.
  Hence the frozen version is exactly 1.0.0 — declared upfront, not shrunk.

## What was searched and NOT found

- `nist.gov/SP800-218/ver1.1` or `v1.1` in oscal-content: absent (only `ver1`).
- A v1.1 machine-readable enumeration from NIST: not found; the v1.1 PDF on nvlpubs
  was not used because PDF prose is not a digest-stable machine enumeration.
- SOC 2 / EU AI Act were considered and rejected as the denominator: SOC 2 criteria
  are paywalled (no digest-stable primary source fetchable); EU AI Act Art-12/50
  targets deployed high-risk AI systems, which a source repo is not. SSDF targets
  software development itself, so it genuinely applies to orca-fleet.

## Open residue

- None blocking the freeze. V1.0-vs-v1.1 task drift is bounded: v1.1 made no
  task-ID changes (would need the v1.1 PDF to re-confirm; not needed since the
  frozen denominator is exactly v1.0.0).

## Verification leg

Method: deterministic re-check of every fetchable claim (byte identity + independent
parse). Limitation recorded honestly: gather and verify ran in one CLI session
(`reviewer_mode: instructed-isolation`) — there is no second Orca worker identity
on this host run; the mechanical checks below are the oracle, not narration.

- Sample: all 7 fetchable claims (100 %, not a sample).
- `git hash-object` of frozen bytes = `94f85f21...` = blob sha advertised by the
  GitHub API for that path: PASS (binds bytes to the upstream repo independently
  of the download channel).
- Re-parse with an independent snippet (groups → controls → controls, count
  `class == task`): 42 tasks, IDs PO.1.1..RV.3.4 with no PW.3 (reserved in v1.0):
  PASS, matches the frozen extraction.
- Failures: 0 struck, 0 demoted. Brief status: CITABLE (with the
  instructed-isolation caveat above).
