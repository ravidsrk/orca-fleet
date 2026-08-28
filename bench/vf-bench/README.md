# VF-Bench — a benchmark of verifier soundness (v0.1)

Every code-agent benchmark (SWE-bench, Terminal-Bench, …) measures **agent capability**: *what
fraction did the agent solve?* VF-Bench measures the **completion gate** instead — the uncontested
axis round-2 identified:

> **What fraction of GAMED solutions did the gate wrongly accept?** — its **false-done rate**.

```sh
python3 bench/vf-bench/vfbench.py         # human table
python3 bench/vf-bench/vfbench.py --json  # machine summary
```

## What it does

The corpus (`traps/*.json`) is a set of **gaming traps** — each a frozen contract + a planted defect
whose SOUND verdict is RED — plus one valid control. `vfbench.py` runs each gate over the corpus and
reports its false-done rate (traps it wrongly passed). A sound gate scores **0%**; a self-scoring gate
scores high. v0 result:

| Gate | false-done | rate |
|---|---|---|
| self-scoring (naive) | 4/4 | **100%** |
| orca-fleet `verify.py` (sound) | 0/4 | **0%** |

The valid control passes both — the sound gate is not trivially always-RED; it passes real work and
rejects only the gamed traps.

## Trap taxonomy (v0)

| Trap | Gamed move | Sound gate catches via |
|---|---|---|
| `scope-shrink` | froze 2 criteria, reported 1 | re-derive the frozen `contract.criterion_ids` |
| `rebase-after-review` | head moved after review | `reviewed_sha == head_sha` |
| `missing-negative-control` | a fix with no revert/mutate proof | mutation-unit negative-control requirement |
| `wrong-sha` | right-looking logs against a phantom SHA | `git cat-file` on `head_sha` |
| `valid-control` | (not a trap — genuinely complete) | passes (proves soundness ≠ always-RED) |

## Add a gate

Drop another gate into `GATES` in `vfbench.py` — e.g. a subprocess wrapper around `ruflo verify`
(claude-flow's Truth Verification System). Because it self-scores (no frozen denominator, no
independent session, no negative control), it will exhibit false-done on these traps; closing the gap
requires implementing the moat, at which point it stops being a self-scorer. **The benchmark measures
the property, not the branding.**

## Contamination hygiene

`CANARY` carries a GUID that must never appear in training corpora (Terminal-Bench pattern);
`VERSION` pins the corpus version so scores stay comparable. **Buildable-now v0**: hand-authored
deterministic traps evaluated by `verify.py`. **Follow-up (research-grade):** held-out / temporal
refresh (SWE-bench-Live pattern), an inspect-ai `Task` wrapper so third parties re-run in a Docker
sandbox, a public leaderboard, and inter-verifier statistics — tracked, not shipped here.

Design rationale: [`docs/research/2026-08-28-forward-roadmap-and-defensibility-plan.md`](../../docs/research/2026-08-28-forward-roadmap-and-defensibility-plan.md).
