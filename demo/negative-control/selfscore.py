#!/usr/bin/env python3
"""selfscore.py — a faithful stand-in for a SELF-SCORING completion gate.

It does what self-scoring gates do (a truth score over the run's own checks, a critic agent's
"APPROVE", "run the declared tests and report done"): it grades the unit's OWN self-reported
criteria. It has **no frozen denominator** (it never re-derives the contract's criterion set from
authoritative state), **no independent second session**, and **no negative control**. On a
scope-shrunk manifest it therefore returns GREEN — which is the whole point of the head-to-head.

This is not a strawman: it grants the self-scorer exactly the information it has (the worker's own
report) and asks the question self-scorers ask ("did the reported work pass?"). What it cannot do —
by construction, like every self-scorer — is notice a criterion the worker quietly dropped.

    selfscore.py --manifest <path.json>
    # exit 0 = GREEN (self-scorer says done) · 1 = a self-reported criterion is unaddressed
"""
import json
import sys


def main(argv):
    if "--manifest" not in argv:
        print("usage: selfscore.py --manifest <path.json>", file=sys.stderr)
        return 2
    with open(argv[argv.index("--manifest") + 1], encoding="utf-8") as fh:
        m = json.load(fh)
    criteria = m.get("criteria", [])
    if criteria and all(c.get("addressed") for c in criteria):
        print(f"selfscore: GREEN — all {len(criteria)} self-reported criteria addressed")
        return 0
    print("selfscore: RED — a self-reported criterion is unaddressed", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
