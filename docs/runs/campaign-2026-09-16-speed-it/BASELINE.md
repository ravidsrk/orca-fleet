# J1 baseline (to metric contract) — 2026-09-16

Conditions: host ravindra-mbp, macOS, python 3.13.15, HEAD `c46d4b3f`,
harness `bin/baseline.sh`, 5 sequential runs, `assets/` restored between runs.
Raw logs: `baseline.log`, `baseline-validate-N.txt`, `baseline-tests-N.txt`,
`baseline-proof-N.txt` (N=1..5).

## Per-run wall seconds (all stages exit 0; suite OK, 1490 tests each run)

| Run | validate | tests | proof_status | J1 total |
|-----|----------|-------|--------------|----------|
| 1 | 0.96 | 286.25 | 0.04 | 287.25 |
| 2 | 0.99 | 306.04 | 0.04 | 307.07 |
| 3 | 0.96 | 272.43 | 0.04 | 273.43 |
| 4 | 1.02 | 271.35 | 0.04 | 272.41 |
| 5 | 0.99 | 272.90 | 0.04 | 273.93 |

## Medians (the contract's confirmation statistic)

- validate: **0.99 s**
- tests: **272.90 s**
- proof_status: **0.04 s**
- **J1 median: 273.93 s** vs budget **≤ 30 s** → BREACH, gap ≈ 244 s (9.1×)

## Spread / noise band

- J1 range 272.41–307.07 s (spread 34.66 s; run 2 is +33 s over median, machine noise).
- Noise band for KEEP-OR-REVERT: a candidate median must beat 273.93 s by more
  than the observed run-to-run spread to count as IMPROVEMENT; inside the band =
  NEUTRAL = REVERT.

## Breach ranking (gap × traffic — single journey)

1. J1 catalog-gates: gap 244 s. Stage split shows the breach lives in `tests/`
   (272.90 of 273.93 s); validate + proof_status are jointly ~1 s. Diagnose the
   tests-stage bottleneck next (per-file profile).
