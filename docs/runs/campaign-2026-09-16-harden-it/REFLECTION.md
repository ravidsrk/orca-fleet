# REFLECTION — harden-it self-run, campaign-2026-09-16

## Surprises

- The repo's own verifier rejected the run's first evidence round (JSON evidence
  counted as code; raw gitleaks JSON pinned credential-shaped bytes). The gate
  worked as designed against its own operator — the remediation (prose-only
  evidence, `--redact` captures) is now the pattern to copy.
- `deny-hook.sh` survived 27 adversarial probes with zero bypasses; the hook's
  review history (quoted in its own comments) predicted every probe I tried.
- The `.env.example` NC-fallback comment documents a fallback `#279` removed —
  fail-safe direction, but the exact kind of drift `pin-it` exists to catch.

## Proposed AGENTS.md / GOTCHAS appends (HUMAN MUST APPROVE EACH LINE)

- GOTCHAS: report-only evidence must be prose extensions (`.md`/`.txt`) only —
  a `.json` artifact flips the unit to mutation-strict under `#310`.
- GOTCHAS: capture gitleaks evidence with `--redact`; raw findings JSON pins
  credential-shaped bytes and fails `check_redaction`.
- GOTCHAS: a solo harden-it run cannot manufacture independent verification —
  record `self-verified` on every disposition and keep the mission at
  `doctrine-only` unless a second context re-derives the audit.
- STYLE: keep the round-1 RED verifier transcript beside the green one
  (`verifier-round1-red.txt`) — the loop is the evidence.
- TEST_STRATEGY: probe `deny-hook.sh` with valid-JSON payloads via a Python
  driver; shell-`printf` payloads with inner quotes test the JSON parser, not
  the hook.

## Prompt / playbook tweaks (fleet-side, optional)

- harden-it SKILL: name the solo-run evidence shape (report-only manifest over
  a prose-only range, head = evidence commit) so the next solo run does not
  rediscover the round-1 RED.
