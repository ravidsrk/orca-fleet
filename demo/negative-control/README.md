# Negative-control head-to-head — a self-scoring gate vs orca-fleet's verifier

A **reproducible, third-party-checkable** demonstration of orca-fleet's moat: on the *same* gamed
solution, a self-scoring completion gate returns **GREEN** while orca-fleet's independent verifier
returns **RED**. Run it yourself:

```sh
sh demo/negative-control/run.sh
```

## The trap (scope-shrink)

`gamed-manifest.json` froze a 2-criterion contract (`AC-1`, `AC-2`) at dispatch, but the worker
quietly **reported only `AC-1`** as done. This is one of round-2's documented gaming vectors.

| Gate | What it does | Verdict on the trap |
|---|---|---|
| [`selfscore.py`](selfscore.py) — a faithful **self-scoring** stand-in | grades the worker's OWN self-reported criteria (no frozen denominator, no independent session, no negative control) | **GREEN** (exit 0) — it never sees the dropped `AC-2` |
| [`verify.py`](../../runtime/scripts/verify.py) — orca-fleet's **independent** verifier | re-derives the FROZEN `contract.criterion_ids` and checks the reported `criteria` cover it exactly | **RED** (exit 2) — "scope shrunk: `AC-2` missing" |

Recorded run: [`head-to-head.txt`](head-to-head.txt). The delta is not the gate *mechanism* (anyone
can ship a gate) — it is the **frozen denominator + independent re-derivation**, which a self-scorer
cannot have by construction.

## Reproduce against a real self-scorer

`selfscore.py` is an honest stand-in, but the trap is gate-agnostic. Point step [1] of `run.sh` at a
shipping self-scoring gate — e.g. **`ruflo verify`** (claude-flow's Truth Verification System, which
self-scores and has no frozen denominator) — and it exhibits the same GREEN, because closing the gap
requires implementing the moat (a second session that re-derives the frozen contract), at which point
it stops being a self-scorer. That is why the property, not the branding, is what the demo measures.

## Dated priority record (2026-08-28)

orca-fleet's two near-zero-prior-art verification primitives, dated and SHA-stamped here so the record
predates convergence (round-2 threat brief: competitors run public priority dossiers):

1. **A mandatory negative control** — a criterion-violating mutation/revert must make the proof go RED
   (`runtime/evidence-manifest.md` §1, bound to a named mutation tool; demonstrated live in
   `docs/reports/prove-it-selfrun/` and `docs/reports/harden-it-externalrun/`).
2. **Independent-session re-derivation from a frozen denominator** — a *different process* re-derives
   the frozen `contract.criterion_ids` from authoritative state before any LLM judgment
   (`runtime/scripts/verify.py`), demonstrated RED-vs-GREEN here.

## Integrity inventory (sha256)

| Artifact | sha256 |
|----------|--------|
| `head-to-head.txt` | `45c4222b3ad5987af486e274a9e3c027861e5443314598fb5de8911d3a8797d6` |

(Re-running `run.sh` re-stamps the timestamp line, so a fresh transcript hashes differently; the value
above pins the committed snapshot.)
