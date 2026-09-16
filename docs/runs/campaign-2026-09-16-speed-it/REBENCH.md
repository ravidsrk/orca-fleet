# J1 re-benchmark (to metric contract) — after H1 @ `3383d06`

Same harness (`bin/rebench.sh`), same pinned conditions, 5 sequential runs.
Raw logs: `rebench.log`, `rebench-validate-N.txt`, `rebench-tests-N.txt`,
`rebench-proof-N.txt` (N=1..5).

## Per-run wall seconds (all stages exit 0; suite OK, 1490 tests each run)

| Run | validate | tests | proof_status | J1 total |
|-----|----------|-------|--------------|----------|
| 1 | 0.96 | 254.86 | 0.04 | 255.86 |
| 2 | 0.98 | 250.06 | 0.04 | 251.08 |
| 3 | 0.91 | 251.74 | 0.04 | 252.69 |
| 4 | 0.91 | 250.01 | 0.04 | 250.97 |
| 5 | 0.92 | 254.02 | 0.04 | 254.98 |

## Confirmation vs baseline

- Baseline J1: median 273.93 s, min 272.41 s, max 307.07 s.
- Rebench J1: median **252.69 s**, min 250.97 s, max 255.86 s.
- Ranges **non-overlapping** (255.86 < 272.41) → pre-registered KEEP rule passes.
- Budget ≤ 30 s: still breached by ~223 s → journey PARKED (see REPORT.md).

## KEEP-OR-REVERT verdict: KEEP H1

IMPROVEMENT over baseline to the contract; landed commit `3383d06` stands
(no revert PR needed).

## Attribution honesty

- Hotspot-controlled effect of H1 (file-level, interleaved within one hour,
  tight ranges): {46.24,47.97,48.08} → {42.39,42.52,42.79} ≈ **−5 s**.
- Journey-level delta (medians): −21.2 s. The ~16 s remainder is inter-window
  environment shift between the baseline window (which contained a +33 s outlier
  run) and the rebench window — NOT attributed to H1. A single journey run
  carries ±15 s noise and cannot resolve a 5 s effect; the file-level experiment
  is the binding attribution, the journey rebench confirms direction + no
  regression. Claiming −21 s "from H1" would be fabrication; the kept win is ~5 s.
