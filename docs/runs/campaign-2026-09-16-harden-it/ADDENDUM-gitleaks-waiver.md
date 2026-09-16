# ADDENDUM — gitleaks waiver for the round-1 capture (2026-09-16)

## What happened

The run's first gitleaks capture (`--no-git`, unredacted) was committed as
`receipts/gitleaks-audit.json` in `f0c83cb`. Its `Secret`/`Match` fields echo
the three known fake fixtures from `tests/test_decisions.py`, producing 5
finding rows at new fingerprints. The file was replaced by a `--redact`
capture one commit later — but git-mode `detect` reads history, so the dead
revision kept flagging: the run-close scan reported `leaks found: 5`, all in
`f0c83cb:.../gitleaks-audit.json` (rules `aws-access-token` ×4 rows,
`generic-api-key` ×1).

## Why waiver, not rotation

The bytes are copies of the two known fake fixtures from
`tests/test_decisions.py` — the AWS-documented example access key and the
24-char alphanumeric test string assigned to `api_key` there (quoted
literals omitted: this file must not reintroduce detectable shapes) —
confirmed by reading the blob at `f0c83cb` (`git show f0c83cb:<path>`).
Nothing live, nothing to rotate.
The repo's sanctioned mechanism for fake credentials in history is a
fingerprint waiver in `.gitleaksignore` (precedent: the `test_decisions.py`
fixtures, same file), so the 5 fingerprints were appended there with a
rationale comment. No history rewrite (forbidden), no silent deletion (the
tree already carries the redacted capture; the waiver covers dead history).

## Verification

- `gitleaks detect --redact --no-banner --source .` → `no leaks found`, exit 0
  (post-waiver, this branch).
- Canary negative control (validate.yml shape, throwaway clone): plant a
  real-shaped key in `tests/test_decisions.py`, commit, scan → must go red.
  Observed: `leaks found: 1` (the planted key only), exit 1. The waiver is
  tight: it suppresses exactly the 5 listed fingerprints.
