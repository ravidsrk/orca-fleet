# harden-it — secret-scan negative-control demonstration (2026-08-28)

**Scope (honest):** a **scoped negative-control demonstration** of harden-it's unfakeable secret-scan
oracle, not a full external-run. It proves the plant→RED→fix→GREEN mechanism with a real tool on a
throwaway fixture. It **does not advance `harden-it` past `doctrine-only`**: a tier bump to
`external-run` requires the full mission run against a real external repo (audit → exploit → fix →
re-attack → clean re-audit), which needs an external target and the orchestration runtime. Presenting
this as an external-run would violate the repo's "never more proven than its evidence" rule.

## The negative control

The cheapest unfakeable harden-it control: the scanner's exit code is the oracle.

| Step | State | gitleaks |
|------|-------|----------|
| 1 | fake, non-functional secret planted in an out-of-repo fixture | **exit 1 — leaks found (RED)** |
| 2 | secret removed (the fix) | — |
| 3 | re-scan | **exit 0 — no leaks (GREEN)** |

Tool: `gitleaks 8.30.1` (`gitleaks dir <fixture> --redact`). The planted key was a fake,
non-functional AWS-style credential in `/tmp` (**never committed**); `--redact` keeps the raw secret
out of this evidence. Full transcript: [`negctrl.txt`](negctrl.txt).

> Note: AWS's *public documentation* example key (`AKIAIOSFODNN7EXAMPLE`) is allowlisted by gitleaks
> by design, so a credible control must plant a non-allowlisted fake — captured here.

## Integrity inventory (sha256)

| Artifact | sha256 | producer |
|----------|--------|----------|
| `negctrl.txt` | `d6dd9d58de05f969932d29346f115114e40b254216e665ba3752680362654a0b` | `gitleaks 8.30.1` (2026-08-28) |

## Follow-up to reach `external-run`

A full `harden-it` run against a small **external** repo — audit → exploit a real finding → fix →
**re-attack the fix** → clean re-audit finds zero unrefuted P0/P1 — recorded in `docs/runs/` with the
scan negative control above as one unit. That report advances the tier. This demonstration also seeds
a VF-Bench "planted-vuln" trap (#79).
