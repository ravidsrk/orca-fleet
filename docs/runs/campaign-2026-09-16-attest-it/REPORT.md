# attest-it self-run — orca-fleet vs NIST-SP-800-218@1.0.0

RUN: solo-no-dispatch · COORDINATOR: cli-session-a4a0c8e3 · BASE: - · T0: 2026-09-16T10:00:15Z · TARGET: orca-fleet @ 6390743815f8f435181fa410cce374587128b30a (origin/main tip) · SOURCE: NIST-SP-800-218@1.0.0 catalog/NIST_SP800-218_ver1_catalog.json sha256:b01634a5fdb382e7a12660c379a4d0bc3a2b8e29abccf2861834880005137117 · VERDICT: CONFORMANT-WITH-GAPS (34 VERIFIED, 8 GAP)

## What was attested

Target: the orca-fleet repository itself at its main tip (6390743, verified equal
to origin/main at T0). Denominator: all 42 tasks of NIST SP 800-218 v1.0.0,
enumerated from NIST's official OSCAL catalog bytes (frozen in catalog/, blob
sha cross-checked against the GitHub API). Unit: one SSDF task. Worker
methodology: matt (single pack; nothing co-mounted). No Orca dispatch was
possible (no live terminal on this host), so gather + re-derive ran solo with a
deterministic script as the re-derivation oracle; independence limits are stated
below, not hidden.

## Verdict: CONFORMANT-WITH-GAPS

34 obligations VERIFIED with evidence bound to TARGET and re-derived; 8 are GAPs,
each with missing evidence stated, a named owner, and a handoff artifact.

| Obligation | Verdict | Obligation | Verdict | Obligation | Verdict |
|---|---|---|---|---|---|
| PO.1.1 | VERIFIED | PS.1.1 | VERIFIED | PW.8.1 | VERIFIED |
| PO.1.2 | VERIFIED | PS.2.1 | VERIFIED | PW.8.2 | VERIFIED |
| PO.1.3 | VERIFIED | PS.3.1 | VERIFIED | PW.9.1 | VERIFIED |
| PO.2.1 | GAP | PS.3.2 | GAP | PW.9.2 | VERIFIED |
| PO.2.2 | GAP | PW.1.1 | VERIFIED | RV.1.1 | VERIFIED |
| PO.2.3 | GAP | PW.1.2 | VERIFIED | RV.1.2 | VERIFIED |
| PO.3.1 | VERIFIED | PW.1.3 | VERIFIED | RV.1.3 | VERIFIED |
| PO.3.2 | VERIFIED | PW.2.1 | VERIFIED | RV.2.1 | VERIFIED |
| PO.3.3 | VERIFIED | PW.4.1 | VERIFIED | RV.2.2 | VERIFIED |
| PO.4.1 | VERIFIED | PW.4.2 | VERIFIED | RV.3.1 | VERIFIED |
| PO.4.2 | VERIFIED | PW.4.4 | GAP | RV.3.2 | VERIFIED |
| PO.5.1 | GAP | PW.5.1 | VERIFIED | RV.3.3 | VERIFIED |
| PO.5.2 | GAP | PW.6.1 | VERIFIED | RV.3.4 | VERIFIED |
| | | PW.6.2 | GAP | | |
| | | PW.7.1 | VERIFIED | | |
| | | PW.7.2 | VERIFIED | | |

## Gap register (all owned by Ravindra Kumar, Maintainer)

| Gap | Missing evidence | Handoff |
|---|---|---|
| PO.2.1 | SDLC roles/responsibilities record | gaps/PO.2.1.md |
| PO.2.2 | role-based training plan | gaps/PO.2.2.md |
| PO.2.3 | recorded authorizing-official commitment | gaps/PO.2.3.md |
| PO.5.1 | dev-environment separation/protection record | gaps/PO.5.1.md |
| PO.5.2 | endpoint hardening baseline | gaps/PO.5.2.md |
| PS.3.2 | per-release component provenance (SBOM or equivalent) | gaps/PS.3.2.md |
| PW.4.4 | recurring component-vulnerability verification | gaps/PW.4.4.md |
| PW.6.2 | approved interpreter security-feature configuration | gaps/PW.6.2.md |

Each handoff carries ARTIFACT + RECIPIENT + a VERIFY-COMPLETE observation a fresh
worker can check. No GAP was closed on narration; no obligation was dropped (the
denominator stayed 42 from freeze to verdict).

## How to re-derive (deterministic)

1. `python3 docs/runs/campaign-2026-09-16-attest-it/rederive/rederive.py` — must
   exit 0 (664/664: every quoted line at TARGET, every absence/no-match claim,
   every manifest digest + provenance.spec_version == frozen, all 9
   release↔tag bindings, suite receipt). Current transcript:
   rederive/rederive.log (`RESULT=PASS`, sha256 pinned in all 42 manifests).
2. `runtime/scripts/verify.py --manifest manifests/<ID>.json --unit-class
   report-only --contract-source taskspecs/<ID>.json --contract-digest <sha>
   --lighting lit` per manifest — full matrix in receipts/verify-matrix.log.
   Expected: exactly one finding per manifest (solo-shape class-downgrade,
   base==head with no signed dispatch — the documented solo limitation,
   corroborated by receipts/worktree-clean.log showing target code untouched);
   GAP manifests add the correct unaddressed-criterion finding (parked, not done).
   Zero redaction hits, zero digest mismatches, zero provenance failures.
3. Suite receipt: receipts/suite-2026-09-16.log (1490 tests, OK, exit 0) at TARGET.
4. Integrity inventory: inventory.json (sha256 of every run file).

## Limitations (read before citing)

- Solo run: gather and re-derive share one session (`reviewer_mode:
  instructed-isolation`, the weakest guarantee, named in all 42 manifests). The
  mechanical oracles above — not the session's word — are what a citation rests on.
- No self-signed dispatch theater: a solo signature cannot create supervision, so
  verify.py's class check stays honestly RED (see §2) instead of being laundered.
- Residuals inside VERIFIED verdicts (unsigned commit third, unsigned tags, no
  SBOM-standard format, qualitative risk scoring, etc.) are recorded per
  obligation in evidence/*.md — a VERIFIED here means "statement satisfied with
  stated residuals", and the residuals are part of the verdict.
- External-state items (GitHub write-access enforcement, runner internals) are
  GAPs or residuals, never assumed passes.
