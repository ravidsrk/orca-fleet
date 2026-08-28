#!/usr/bin/env python3
"""vfbench.py — VF-Bench v0: a benchmark of VERIFIER SOUNDNESS, not agent capability.

Every existing code-agent benchmark asks "what fraction did the agent solve?". VF-Bench asks the
uncontested question: **"what fraction of GAMED solutions did the completion gate wrongly accept?"**
— the gate's **false-done rate**. It runs each gate over a corpus of gaming traps
(`bench/vf-bench/traps/*.json`), each a frozen contract + a planted defect whose SOUND verdict is
RED. A sound gate scores 0% false-done; a self-scoring gate scores high.

Gates measured:
  - self-scoring (naive): grades the worker's OWN self-reported criteria (the trace-as-oracle pattern).
  - orca-fleet verify.py (sound): re-derives the frozen denominator + checks git, in a separate process.

Drop in another gate by adding it to GATES (e.g. a subprocess wrapper around `ruflo verify`).

    vfbench.py            # human table
    vfbench.py --json     # machine summary
    # exit 0 always — it reports; tests/test_vfbench.py asserts the soundness property.
"""
import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
TRAPS = HERE / "traps"
VERIFY = ROOT / "runtime" / "scripts" / "verify.py"
VERSION = (HERE / "VERSION").read_text(encoding="utf-8").strip() if (HERE / "VERSION").exists() else "vf-bench@?"


def load_traps():
    return [json.loads(f.read_text(encoding="utf-8")) for f in sorted(TRAPS.glob("*.json"))]


def naive_gate(manifest):
    """Self-scoring: GREEN iff every self-reported criterion is addressed (no frozen denominator)."""
    crit = manifest.get("criteria", [])
    return bool(crit) and all(c.get("addressed") for c in crit)


def sound_gate(manifest):
    """orca-fleet's independent verifier (verify.py), run as a separate process from the repo root."""
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
        json.dump(manifest, fh)
        path = fh.name
    r = subprocess.run(
        [sys.executable, str(VERIFY), "--manifest", path],
        capture_output=True, text=True, cwd=ROOT,
    )
    return r.returncode == 0  # True = gate returned GREEN (allow)


GATES = {
    "self-scoring (naive)": naive_gate,
    "orca-fleet verify.py (sound)": sound_gate,
}


def run():
    traps = load_traps()
    red_total = sum(1 for t in traps if t["sound_expected"] == "RED")
    results = {}
    for name, gate in GATES.items():
        false_done, rows = 0, []
        for t in traps:
            passed = gate(t["manifest"])
            fooled = t["sound_expected"] == "RED" and passed
            false_done += 1 if fooled else 0
            rows.append({
                "id": t["id"], "class": t["class"],
                "verdict": "GREEN" if passed else "RED",
                "false_done": fooled,
            })
        results[name] = {
            "false_done": false_done, "red_total": red_total,
            "rate": (false_done / red_total) if red_total else 0.0, "rows": rows,
        }
    return results


def main(argv):
    ap = argparse.ArgumentParser(description="VF-Bench v0 — verifier soundness / false-done rate")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    res = run()
    if args.json:
        print(json.dumps(
            {"version": VERSION, "gates": {k: {"false_done": v["false_done"],
             "red_total": v["red_total"], "rate": v["rate"]} for k, v in res.items()}},
            indent=2))
        return 0
    print(f"VF-Bench {VERSION} — false-done rate (fraction of gamed traps a gate wrongly accepted)")
    for name, r in res.items():
        print(f"\n== {name} ==  false-done {r['false_done']}/{r['red_total']} = {r['rate']:.0%}")
        for row in r["rows"]:
            flag = "  <- FALSE-DONE" if row["false_done"] else ""
            print(f"  [{row['verdict']:5}] {row['id']:24} {row['class']:26}{flag}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
