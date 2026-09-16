RUN: solo-no-dispatch (run-create refused: no live Orca terminal on this host) · COORDINATOR: cli-session-a4a0c8e3 · BASE: - · FORK_POINT: - · T0: 2026-09-16T10:00:15Z · SOURCE: NIST-SP-800-218@1.0.0 catalog/NIST_SP800-218_ver1_catalog.json sha256:b01634a5fdb382e7a12660c379a4d0bc3a2b8e29abccf2861834880005137117 · WIP: builders=1 reviewers=1

PHASE: DONE (report-only mission). Terminal: CONFORMANT-WITH-GAPS (34 VERIFIED, 8 GAP). Worker methodology: matt (single pack; never co-mounted). Target: orca-fleet @ 6390743815f8f435181fa410cce374587128b30a (origin/main tip).

| obligation | task | GATHERED | REDERIVED | verdict | evidence |
|---|---|---|---|---|---|
| PO.1.1 | attest-po-1-1 | t | t | VERIFIED | evidence/PO.1.1.md |
| PO.1.2 | attest-po-1-2 | t | t | VERIFIED | evidence/PO.1.2.md |
| PO.1.3 | attest-po-1-3 | t | t | VERIFIED | evidence/PO.1.3.md |
| PO.2.1 | attest-po-2-1 | t | t | GAP | evidence/PO.2.1.md |
| PO.2.2 | attest-po-2-2 | t | t | GAP | evidence/PO.2.2.md |
| PO.2.3 | attest-po-2-3 | t | t | GAP | evidence/PO.2.3.md |
| PO.3.1 | attest-po-3-1 | t | t | VERIFIED | evidence/PO.3.1.md |
| PO.3.2 | attest-po-3-2 | t | t | VERIFIED | evidence/PO.3.2.md |
| PO.3.3 | attest-po-3-3 | t | t | VERIFIED | evidence/PO.3.3.md |
| PO.4.1 | attest-po-4-1 | t | t | VERIFIED | evidence/PO.4.1.md |
| PO.4.2 | attest-po-4-2 | t | t | VERIFIED | evidence/PO.4.2.md |
| PO.5.1 | attest-po-5-1 | t | t | GAP | evidence/PO.5.1.md |
| PO.5.2 | attest-po-5-2 | t | t | GAP | evidence/PO.5.2.md |
| PS.1.1 | attest-ps-1-1 | t | t | VERIFIED | evidence/PS.1.1.md |
| PS.2.1 | attest-ps-2-1 | t | t | VERIFIED | evidence/PS.2.1.md |
| PS.3.1 | attest-ps-3-1 | t | t | VERIFIED | evidence/PS.3.1.md |
| PS.3.2 | attest-ps-3-2 | t | t | GAP | evidence/PS.3.2.md |
| PW.1.1 | attest-pw-1-1 | t | t | VERIFIED | evidence/PW.1.1.md |
| PW.1.2 | attest-pw-1-2 | t | t | VERIFIED | evidence/PW.1.2.md |
| PW.1.3 | attest-pw-1-3 | t | t | VERIFIED | evidence/PW.1.3.md |
| PW.2.1 | attest-pw-2-1 | t | t | VERIFIED | evidence/PW.2.1.md |
| PW.4.1 | attest-pw-4-1 | t | t | VERIFIED | evidence/PW.4.1.md |
| PW.4.2 | attest-pw-4-2 | t | t | VERIFIED | evidence/PW.4.2.md |
| PW.4.4 | attest-pw-4-4 | t | t | GAP | evidence/PW.4.4.md |
| PW.5.1 | attest-pw-5-1 | t | t | VERIFIED | evidence/PW.5.1.md |
| PW.6.1 | attest-pw-6-1 | t | t | VERIFIED | evidence/PW.6.1.md |
| PW.6.2 | attest-pw-6-2 | t | t | GAP | evidence/PW.6.2.md |
| PW.7.1 | attest-pw-7-1 | t | t | VERIFIED | evidence/PW.7.1.md |
| PW.7.2 | attest-pw-7-2 | t | t | VERIFIED | evidence/PW.7.2.md |
| PW.8.1 | attest-pw-8-1 | t | t | VERIFIED | evidence/PW.8.1.md |
| PW.8.2 | attest-pw-8-2 | t | t | VERIFIED | evidence/PW.8.2.md |
| PW.9.1 | attest-pw-9-1 | t | t | VERIFIED | evidence/PW.9.1.md |
| PW.9.2 | attest-pw-9-2 | t | t | VERIFIED | evidence/PW.9.2.md |
| RV.1.1 | attest-rv-1-1 | t | t | VERIFIED | evidence/RV.1.1.md |
| RV.1.2 | attest-rv-1-2 | t | t | VERIFIED | evidence/RV.1.2.md |
| RV.1.3 | attest-rv-1-3 | t | t | VERIFIED | evidence/RV.1.3.md |
| RV.2.1 | attest-rv-2-1 | t | t | VERIFIED | evidence/RV.2.1.md |
| RV.2.2 | attest-rv-2-2 | t | t | VERIFIED | evidence/RV.2.2.md |
| RV.3.1 | attest-rv-3-1 | t | t | VERIFIED | evidence/RV.3.1.md |
| RV.3.2 | attest-rv-3-2 | t | t | VERIFIED | evidence/RV.3.2.md |
| RV.3.3 | attest-rv-3-3 | t | t | VERIFIED | evidence/RV.3.3.md |
| RV.3.4 | attest-rv-3-4 | t | t | VERIFIED | evidence/RV.3.4.md |

Verdict values: VERIFIED | GAP. No obligation is silently dropped; the set is frozen at 42.

## Close-out
RESUME scope (header + 42 rows) satisfied: every obligation GATHERED=t REDERIVED=t with a verdict; rederive.py 664/664 green (rederive/rederive.log RESULT=PASS); verify.py matrix in receipts/verify-matrix.log (sole per-manifest finding: solo-shape class-downgrade; GAP manifests add the correct unaddressed-criterion finding).
