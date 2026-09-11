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
    # exits 0 after reporting; a broken verifier (a non-0/2 verify.py exit) raises instead of scoring.
    # tests/test_vfbench.py asserts the soundness property.
"""
import argparse
import hashlib
import json
import os
import shutil
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


def _commit_present(sha):
    return subprocess.run(["git", "cat-file", "-e", f"{sha}^{{commit}}"],
                          capture_output=True, cwd=ROOT).returncode == 0


def skip_reason(trap):
    """#257: a trap that pins a real commit CANNOT be scored on a shallow clone — the commit is
    simply not there, so every leg that reads it degrades and the verdict measures the checkout,
    not the gate. Say so by name instead of scoring ambient state (docs/reviews/2026-09-10-review.md P2 item 22: the
    review-leg trap used to skip silently). `fetch-depth: 0` fixes it in CI."""
    for sha in trap.get("requires_commits", []):
        if not _commit_present(sha):
            return f"shallow clone: pinned commit {sha[:12]} is not in this checkout"
    return None


def naive_gate(trap):
    """Self-scoring: GREEN iff every self-reported criterion is addressed (no frozen denominator)."""
    crit = trap["manifest"].get("criteria", [])
    return bool(crit) and all(c.get("addressed") for c in crit)


FIXTURE_MOD_BASE = "def add(a, b):\n    return a - b  # the defect AC-1 names\n"
FIXTURE_MOD_HEAD = "def add(a, b):\n    return a + b  # the fix\n"
FIXTURE_TEST = (
    "import unittest\n\nimport mod\n\n\n"
    "class T(unittest.TestCase):\n"
    "    def test_add(self):  # the test AC-1 binds to\n"
    "        self.assertEqual(mod.add(2, 2), 4)\n"
)
FIXTURE_CONTRACT = "# Frozen contract (vf-bench mutation fixture)\n\n- AC-1: add(a, b) returns a + b\n"
FIXTURE_NC = (
    "revert negative control, EXECUTED\n\n"
    "mod.py restored from base_sha in a throwaway worktree at head_sha; `python -m unittest`\n"
    "went RED (mutant KILLED). Re-running at clean head_sha is green.\n"
)
# The stillborn trap's artifact (#306). A `hand` control must QUOTE its diff in the artifact —
# putting it in a `negative_control.diff` field gets the manifest refused as malformed, which
# would refuse the trap for the wrong reason and measure nothing about stillborn detection.
# The diff below is a real one against mod.py's changed line, and it breaks the parse, so the
# executed run dies on a SyntaxError before any assertion is evaluated.
FIXTURE_NC_STILLBORN = (
    "hand negative control, EXECUTED\n\n"
    "```diff\n"
    "--- a/mod.py\n"
    "+++ b/mod.py\n"
    "@@ -1,2 +1,2 @@\n"
    " def add(a, b):\n"
    "-    return a + b  # the fix\n"
    "+    return a +  # the fix\n"
    "```\n\n"
    "`python -m unittest` exited non-zero (mutant KILLED).\n"
)


def _fixture_git(repo, *args):
    subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True)


def _fixture_rev(repo, rev):
    return subprocess.run(["git", "-C", str(repo), "rev-parse", rev],
                          check=True, capture_output=True, text=True).stdout.strip()


def build_mutation_fixture(repo):
    """#257: a REAL mutation unit, built at run time, hermetic.

    A module with a defect at `base_sha`, the fix at `head_sha`, and a criterion-bound test that
    goes RED when the fix is reverted. Nothing here is narrated: the commits, the tree, the control
    and the proof command are all real, so a gate can only pass this trap by EXECUTING the control.
    A committed corpus could not carry that — the revert has to happen against live commits."""
    repo.mkdir(parents=True)
    _fixture_git(repo, "init", "-q", "-b", "main")
    (repo / "mod.py").write_text(FIXTURE_MOD_BASE, encoding="utf-8")
    (repo / "test_mod.py").write_text(FIXTURE_TEST, encoding="utf-8")
    (repo / "contract.md").write_text(FIXTURE_CONTRACT, encoding="utf-8")
    _fixture_git(repo, "add", "-A")
    _fixture_git(repo, "-c", "user.name=vf", "-c", "user.email=vf@vf", "commit", "-qm", "base")
    base = _fixture_rev(repo, "HEAD")
    (repo / "mod.py").write_text(FIXTURE_MOD_HEAD, encoding="utf-8")
    _fixture_git(repo, "-c", "user.name=vf", "-c", "user.email=vf@vf", "commit", "-qam", "the fix")
    head = _fixture_rev(repo, "HEAD")
    # Evidence written AFTER the head commit (a reviewer record must name the head SHA), so it is
    # untracked — which is exactly the case #267's artifacts[] sha256 inventory exists for.
    evidence = repo / "docs" / "reports" / "vf"
    evidence.mkdir(parents=True)
    (evidence / "nc.txt").write_text(FIXTURE_NC, encoding="utf-8")
    (evidence / "nc-stillborn.txt").write_text(FIXTURE_NC_STILLBORN, encoding="utf-8")
    (evidence / "review.txt").write_text(
        f"build-blind review of {head}\nAPPROVED by vf-reviewer (local lane record)\n",
        encoding="utf-8")

    def sha256(rel):
        return hashlib.sha256((repo / rel).read_bytes()).hexdigest()

    return {
        "base_sha": base, "head_sha": head, "head_tree": _fixture_rev(repo, "HEAD^{tree}"),
        "contract_digest": "sha256:" + sha256("contract.md"),
        "nc_sha256": sha256("docs/reports/vf/nc.txt"),
        "nc_stillborn_sha256": sha256("docs/reports/vf/nc-stillborn.txt"),
        "review_sha256": sha256("docs/reports/vf/review.txt"),
        # The SAME command line the negative control replays and the ledger records —
        # one token, so the trap cannot drift into proving nothing. sys.executable in
        # full, not its basename: the manifest's control names the interpreter it will
        # actually run, and --execute-nc requires the two to be the same string.
        "proof_cmd": (_proof := f"{sys.executable} -m unittest test_mod"),
        # The ledger's own digest of that command line, exactly as evidence-run.py
        # writes it. --execute-nc will only replay a command the ledger already
        # recorded green at head_sha's tree, so the trap has to carry a real one
        # (PR #277 review, P1) — a placeholder here would make this control pass
        # for the wrong reason.
        "proof_cmd_sha256": hashlib.sha256(_proof.encode("utf-8")).hexdigest(),
        "python": sys.executable,
    }


def _gh_stub(bindir, head, state="APPROVED"):
    """A `gh` on PATH that serves ONE independent review at head_sha by a login that is not the PR
    author. The review authority is external to the manifest by design, so the only honest way to
    exercise the GREEN half offline is to stand a real one up."""
    bindir.mkdir(parents=True, exist_ok=True)
    stub = bindir / "gh"
    stub.write_text(
        "#!/usr/bin/env python3\n"
        "import json, sys\n"
        "endpoint = sys.argv[-1]\n"
        "if endpoint.endswith('/reviews'):\n"
        f"    print(json.dumps([{{'user': {{'login': 'vf-reviewer'}}, 'state': {state!r},\n"
        f"                        'commit_id': {head!r}}}]))\n"
        "elif '/pulls/' in endpoint:\n"
        "    print(json.dumps({'user': {'login': 'vf-author'}}))\n"
        "else:\n"
        "    sys.exit(1)\n", encoding="utf-8")
    stub.chmod(0o755)
    return str(bindir)


def _render(obj, facts):
    """Substitute {{token}} placeholders in a trap's manifest template with the fixture's real
    values — a manifest cannot be committed with SHAs that do not exist yet."""
    if isinstance(obj, str):
        for key, value in facts.items():
            obj = obj.replace("{{" + key + "}}", str(value))
        return obj
    if isinstance(obj, list):
        return [_render(x, facts) for x in obj]
    if isinstance(obj, dict):
        return {k: _render(v, facts) for k, v in obj.items()}
    return obj


def fixture_gate(trap):
    """Run verify.py against a trap whose unit is built at run time (see build_mutation_fixture).
    Returns True when the gate returned GREEN."""
    holder = Path(tempfile.mkdtemp(prefix="vfbench-fixture-"))
    try:
        repo = holder / "repo"
        facts = build_mutation_fixture(repo)
        manifest = _render(trap["manifest"], facts)
        mpath = repo / "vf-manifest.json"
        mpath.write_text(json.dumps(manifest), encoding="utf-8")
        cmd = [sys.executable, str(VERIFY), "--manifest", str(mpath),
               "--contract-source", "contract.md",
               "--contract-digest", facts["contract_digest"],
               "--unit-class", trap.get("unit_class", "mutation")]
        if trap.get("lighting"):
            cmd += ["--lighting", trap["lighting"]]
        if trap.get("no_gh"):
            cmd.append("--no-gh")
        if trap.get("execute_nc"):
            cmd.append("--execute-nc")
            # #279: the criterion-bound command comes from the COORDINATOR, out of band, exactly as
            # the contract does. The bench plays that role here; a trap that omits it is modelling a
            # coordinator who named no command, and verify.py refuses the run.
            if trap.get("nc_command"):
                cmd += ["--nc-command", _render(trap["nc_command"], facts)]
        if trap.get("repo"):
            cmd += ["--repo", trap["repo"]]
        env = dict(os.environ)
        if trap.get("gh_stub"):
            env["PATH"] = _gh_stub(holder / "bin", facts["head_sha"]) + os.pathsep + env["PATH"]
        r = subprocess.run(cmd, capture_output=True, text=True, cwd=repo, env=env)
        if r.returncode not in (0, 2):
            raise RuntimeError(f"verify.py exited {r.returncode} on fixture trap {trap['id']} "
                               f"(not a 0/2 verdict): {r.stderr.strip()[:400]}")
        if r.returncode != 0 and trap.get("sound_expected") == "GREEN":
            # A positive control going RED is a broken control, not a measurement:
            # it would quietly stop proving "not always-RED". Say why, loudly.
            raise RuntimeError(
                f"positive control {trap['id']} went RED — the control is broken, not the gate: "
                f"{r.stderr.strip()[:600]}")
        return r.returncode == 0
    finally:
        shutil.rmtree(holder, ignore_errors=True)


def sound_gate(trap):
    """orca-fleet's verifier, run as a separate process, given the trap's AUTHORITATIVE contract
    (the coordinator role) — never the manifest's own contract fields."""
    if trap.get("fixture") == "mutation-revert":
        return fixture_gate(trap)
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
        json.dump(trap["manifest"], fh)
        path = fh.name
    try:
        cmd = [sys.executable, str(VERIFY), "--manifest", path]
        if trap.get("contract_source"):
            cmd += ["--contract-source", trap["contract_source"]]
        if trap.get("contract_digest"):
            cmd += ["--contract-digest", trap["contract_digest"]]
        # unit_class is a DISPATCH fact the coordinator supplies OUT OF BAND — verify.py never reads it
        # from the manifest. The trap carries it at TOP LEVEL; a trap with no `unit_class` models the
        # coordinator not classifying (verify.py fail-safes to mutation). The manifest's own unit_class
        # is ignored — that is what makes the downgraded-class / unclassified-mutation vectors fail.
        if trap.get("unit_class"):
            cmd += ["--unit-class", trap["unit_class"]]
        if trap.get("base"):
            cmd += ["--base", trap["base"]]
        if trap.get("repo"):
            cmd += ["--repo", trap["repo"]]
        if trap.get("execute_nc"):
            cmd.append("--execute-nc")
            if trap.get("nc_command"):  # coordinator-supplied, as in fixture_gate (#279)
                cmd += ["--nc-command", trap["nc_command"]]
        r = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)
        # verify.py returns 0 (GREEN/allow) or 2 (RED/invariant failed). Any other code (1 = usage /
        # dependency error) is a BROKEN run, not a verdict — fail loud so it cannot inflate soundness
        # by scoring an execution failure as a caught trap.
        if r.returncode not in (0, 2):
            raise RuntimeError(f"verify.py exited {r.returncode} (not a 0/2 verdict) — broken "
                               f"verifier/env, not a RED verdict: {r.stderr.strip()[:200]}")
        return r.returncode == 0  # True = gate returned GREEN (allow)
    finally:
        Path(path).unlink(missing_ok=True)


GATES = {
    "self-scoring (naive)": naive_gate,
    "orca-fleet verify.py (sound)": sound_gate,
}


def run():
    traps = load_traps()
    skipped = [{"id": t["id"], "class": t["class"], "reason": r}
               for t in traps for r in [skip_reason(t)] if r]
    skipped_ids = {s["id"] for s in skipped}
    scored = [t for t in traps if t["id"] not in skipped_ids]
    red_total = sum(1 for t in scored if t["sound_expected"] == "RED")
    results = {}
    for name, gate in GATES.items():
        false_done, rows = 0, []
        for t in scored:
            passed = gate(t)
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
            "skipped": skipped,
        }
    return results


def main(argv):
    ap = argparse.ArgumentParser(description="VF-Bench v0 — verifier soundness / false-done rate")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    res = run()
    skipped = next(iter(res.values()))["skipped"] if res else []
    if args.json:
        print(json.dumps(
            {"version": VERSION,
             "skipped": skipped,
             "gates": {k: {"false_done": v["false_done"], "red_total": v["red_total"],
                           "rate": v["rate"]} for k, v in res.items()}},
            indent=2))
        return 0
    print(f"VF-Bench {VERSION} — false-done rate (fraction of gamed traps a gate wrongly accepted)")
    # #257: never let a skip hide. A skipped trap is scored by nobody and named by everybody.
    for s in skipped:
        print(f"  [SKIP ] {s['id']:24} {s['class']:26}  <- NOT SCORED: {s['reason']}")
    if skipped:
        print(f"  {len(skipped)} trap(s) skipped — this run does not measure them. "
              "Use a full clone (CI: actions/checkout with fetch-depth: 0).")
    for name, r in res.items():
        print(f"\n== {name} ==  false-done {r['false_done']}/{r['red_total']} = {r['rate']:.0%}")
        for row in r["rows"]:
            flag = "  <- FALSE-DONE" if row["false_done"] else ""
            print(f"  [{row['verdict']:5}] {row['id']:24} {row['class']:26}{flag}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
