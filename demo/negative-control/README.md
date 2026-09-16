# Negative-control head-to-head — a self-scoring gate vs orca-fleet's verifier

A **reproducible, third-party-checkable** demonstration of orca-fleet's moat: on the *same* gamed
solution, a self-scoring completion gate returns **GREEN** while orca-fleet's independent verifier
returns **RED**. Run it yourself:

```sh
sh demo/negative-control/run.sh
```

## The trap (scope-shrink)

`gamed-manifest.json` points at a frozen source (`frozen-spec.md`, criteria `AC-1` + `AC-2`), but the
worker quietly **reported only `AC-1`** in its manifest. This is one of round-2's documented gaming vectors.

| Gate | What it does | Verdict on the trap |
|---|---|---|
| [`selfscore.py`](selfscore.py) — a faithful **self-scoring** stand-in | grades the worker's OWN self-reported criteria (no frozen denominator, no independent session, no negative control) | **GREEN** (exit 0) — it never sees the dropped `AC-2` |
| [`verify.py`](../../runtime/scripts/verify.py) — orca-fleet's **independent** verifier | re-derives the criterion set from the frozen source (`frozen-spec.md`) and checks the reported `criteria` cover it | **RED** (exit 2) — `scope: authoritative criteria not addressed in criteria[] … ['AC-2']` (the transcript also records the #310 empty-range refusal, which fires on the same manifest) |

Recorded run: [`head-to-head.txt`](head-to-head.txt). The delta is not the gate *mechanism* (anyone
can ship a gate) — it is the **frozen denominator + independent re-derivation**, which a self-scorer
cannot have by construction.

## CI-pinned

This demo is CI-pinned: every PR re-runs `run.sh` and diffs fresh output against
`head-to-head.txt` (`.github/workflows/negative-control.yml`, #413). To change expected output,
change the demo AND explain why — a drifted transcript means either the demo rotted (fix the demo)
or the verifier changed behavior (fix the expectations and file a follow-up on the behavior change),
never a silent re-baseline.

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
2. **Independent re-derivation from a coordinator-anchored denominator** — a *different process*
   re-derives the criterion set from the **authoritative frozen contract supplied by the coordinator**
   (`--contract-source`/`--contract-digest` from the dispatch record — never the worker's manifest),
   before any LLM judgment (`runtime/scripts/verify.py`), demonstrated RED-vs-GREEN here.

## Integrity inventory (sha256)

| Artifact | sha256 |
|----------|--------|
| `head-to-head.txt` | `055e8725df76853ec97dc369557ee1f7d52e0c6fb21a192c818a1908a1a11c0e` |

(Re-running `run.sh` re-stamps the timestamp line, so a fresh transcript hashes differently; the value
above pins the committed snapshot and is re-derived from it, not carried forward — the 2026-09-10 deep
review found this row stale against the file it names, which is exactly the failure an integrity
inventory exists to prevent. `tests/test_negative_control.py` now re-checks it. The transcript
records two FAIL lines — the scope-shrink this demo is about, and the #310 empty-range guard that
also fires on this manifest; `run.sh`'s PASS requires the AC-2 line, so a broken `check_scope`
cannot print PASS on the strength of the structural refusal alone (#370).)
