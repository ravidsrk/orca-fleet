# ADDENDUM — dead-history fixture bytes on this branch (2026-09-16)

## What happened

The run's first gitleaks capture (`--no-git`, unredacted) was committed as
`receipts/gitleaks-audit.json` in `f0c83cb`. Its finding fields echo the known
fake fixtures from `tests/test_decisions.py` (the AWS-documented example access
key and the test `api_key` string — literals omitted here: evidence must not
reintroduce detectable shapes). The file was replaced by a `--redact` capture
one commit later, but git-mode `detect` reads history, so the dead revision
keeps flagging (5 rows). This addendum's own first revision quoted one fixture
literal verbatim and added a sixth dead-history row before being scrubbed.

Current state: `gitleaks detect --source .` on this branch reports 6 rows, all
in dead revisions (`f0c83cb`, `57760b6`), all the same fake bytes. The live
tree is clean.

## Why neither rotation nor waiver was applied

- **Rotation:** nothing live. The bytes are documented test fixtures; there is
  no credential to rotate. (Mission rule: leaks route to rotation — but only
  live secrets qualify, and these provably are not.)
- **Waiver:** attempted, then reverted. Appending the 6 fingerprints to
  `.gitleaksignore` clears the scan (verified) and survives the canary control
  (planted key still caught, exit 1) — but `tests/test_repo_hygiene.py` pins
  the waived set to exactly the known fixtures and fails on any addition,
  demanding per-entry justification. Widening a finding-silencing control is
  a human decision; no human gate is reachable in this solo run, so the
  waiver was reverted rather than forced through against the guard test.

## Parked for the repo owner (OPS, non-security)

NOT a P0/P1 — fake bytes with no exploit path — so the mission terminal is
unaffected. Two owner options:

1. **Justified waiver:** re-apply the 6 fingerprints (listed in the reverted
   revisions `57760b6`/`75915eb9`, `.gitleaksignore` diff) plus the matching
   `WAIVED`-set update in `tests/test_repo_hygiene.py`, with owner review as
   the justification the test demands.
2. **History surgery:** drop/squash the branch's early evidence commits so the
   unredacted capture never enters shared history (only available pre-merge).

VERIFY-COMPLETE (either option): `gitleaks detect --source .` → `no leaks
found`, exit 0, AND `python3 -m unittest discover -s tests` → OK, AND the
canary plant-a-key control still goes red. Until then, this branch must not
merge: merging would carry the dead-history rows into `main`'s scan.
