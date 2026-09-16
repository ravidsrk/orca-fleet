# Triage — candidates → findings (`triage-findings`)

## 1. Mode

**Gated** (declared at T0 in `pin.md`, never moved). Bar: high confidence —
a concrete instance of a real pattern. Below the bar: not reported.

## 2. Candidate disposition

| candidate | disposition | reason |
|---|---|---|
| S-N1 inconsistent JSON formatting | REPORTED (Nit) | directly observed, high confidence; severity Nit (cosmetic, both shapes parse) |
| S-FYI1 inventory `#` warnings | REPORTED (FYI) | observed; standard practice, exit 0 |
| SP-FYI1 human-verdict half owed | REPORTED (FYI) | report's own resume path; not a defect |
| SP-FYI2 merge-precondition check | REPORTED (FYI, clear) | checked against merge record; precondition met |
| TA-FYI1 F6 NC transcript absent | REPORTED (FYI) | claim re-verified; transcript would be nicer |
| SEC-FYI1 quoted seed token | REPORTED (FYI, accepted) | scratch PoC material, variant-confined, gitleaks-clean |
| PRI-FYI1 operator username in tmp paths | REPORTED (FYI, dropped) | maintainer's own public handle |
| seed vulnerable patterns (SQLi/MD5/token) | DISCARDED | hard exclusion: test fixture imported by no production code (import grep clean) |
| prose report files as vuln candidates | DISCARDED | hard exclusion: prose documentation file (no executable-agent-instruction content) |
| AUTH/PERF keyword flags as lens triggers | ADJUDICATED | AUTH: security lens ran bounded (NEVER_GATE), CLEAN. PERF: ran bounded, CLEAN; triggers cited as keyword noise |

Zero candidates UNVERIFIED, zero TENTATIVE (gated mode admits none).

## 3. Anti-FP gate

Every reported item quotes its verbatim motivating line (see axis/lens
files). Nothing dropped to an appendix — nothing lacked a line.

## 4. Active verification

All by tracing/reads (git plumbing against a `/tmp` bundle clone, hash
re-computation, API reads through `guard_text.py`). No live system touched;
no target code executed. See `axis-test-adequacy.md` rows 1–12.

## 5. Independent verifiers — RECORDED DEGRADATION

No separate fresh-context verifier was dispatched per candidate: this is a
solo workflow-child run and the execution contract forbids recursive agent
dispatch. Every finding therefore carries **"self-verified — no independent
verifier"** (triage §5: a scanner agreeing with itself is one opinion, never
a silent equivalence). Authorship independence holds (the reviewer wrote none
of PR #445); session independence does not.

## 6. Variant analysis

- `admin-secret-12345`: repo-wide grep → 3 files, all in the new report dir;
  absent at the fixed point. Complete.
- Single-line-JSON inconsistency: the 3 unit manifests are the full variant
  set within the diff; no other JSON added. Complete.
- `pytest-of-ravindra` tmp paths: confined to the two NC transcripts. Complete.
