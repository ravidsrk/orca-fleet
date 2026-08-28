#!/usr/bin/env python3
"""verify.py — independent, separate-process re-derivation of an evidence manifest.

The completion oracle runs OUTSIDE the producing session — a headless subprocess (this
script, or `claude -p` / an MCP Task), NEVER a teammate. Teammate / cross-session messages
are in-band and self-certifying: exactly the trace-as-oracle failure the evidence protocol
rejects (evidence-manifest.md, reviewed-sha-freshness.md). This re-derives the
git-authoritative facts DETERMINISTICALLY, before any LLM judgment, and fails closed.

Checks (evidence-manifest.md section 2), scope FIRST because passing tests on a shrunken
denominator is the most dangerous false "done":
    1. scope not shrunk: every contract.criterion_ids entry has a criteria[] entry (exact).
    2. base_sha / head_sha are present and real commits (git cat-file -e).
    3. freshness: pr.reviewed_sha == head_sha (a rebase after review voids it).
    4. negative control: mutation units carry negative_control.tool + .result.
    5. ancestry (best-effort): head_sha is an ancestor of origin/<base_branch> — reported,
       not fatal pre-merge (the coordinator's PR baseRef check is the pre-merge twin).
    6. change real on base (best-effort): --symbol is greppable on origin/<base_branch>.

Checks 1-4 are DETERMINISTIC and machine-local (no network); 5-6 need the base ref and are
skipped-with-note when it is absent (pre-merge / offline), never silently passed.

Usage:
    verify.py --manifest <path.json> [--base <branch>] [--symbol <token>]
    # exit 0 = all REQUIRED checks pass
    # exit 1 = usage / dependency (git missing, manifest unreadable/invalid)
    # exit 2 = a REQUIRED invariant FAILED — the unit is NOT done
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys

# Mutation missions land code and must carry the revert/mutate negative control; report-only
# and planning units bind evidence differently (evidence-manifest.md section 3).
MUTATING_MISSIONS = {
    "ship-it", "clean-sweep", "harden-it", "speed-it",
    "modernize-it", "prove-it", "deflake-it",
}


def _git(args, timeout=10):
    """Run a git command; return (exit_code, stdout). Never raises on git failure."""
    try:
        p = subprocess.run(
            ["git", *args], capture_output=True, text=True, timeout=timeout, check=False
        )
        return p.returncode, p.stdout.strip()
    except (subprocess.TimeoutExpired, OSError) as err:
        return 1, f"<git error: {err}>"


def load_manifest(path):
    """Return (manifest, error). Never raises."""
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh), None
    except (OSError, json.JSONDecodeError) as err:
        return None, f"unreadable/invalid manifest: {err}"


def check_scope(m):
    """1. The worker cannot shrink its own denominator: every declared criterion id must
    have a criteria[] entry. Pure — no git, no network."""
    declared = set((m.get("contract") or {}).get("criterion_ids") or [])
    addressed = {c.get("id") for c in (m.get("criteria") or [])}
    missing = sorted(declared - addressed)
    if missing:
        return [f"scope shrunk: criterion_ids missing a criteria[] entry: {missing}"]
    if not declared:
        return ["scope undefined: contract.criterion_ids is empty"]
    return []


def check_shas_present(m):
    errs = []
    for field in ("base_sha", "head_sha"):
        if not m.get(field):
            errs.append(f"missing required '{field}'")
    return errs


def check_real_commits(m):
    """2. base_sha / head_sha must be real commits (skipped-with-note outside a git repo)."""
    if _git(["rev-parse", "--is-inside-work-tree"])[0] != 0:
        return ["NOTE: not inside a git repo — commit-existence check skipped"]
    errs = []
    for field in ("base_sha", "head_sha"):
        sha = m.get(field)
        if sha and _git(["cat-file", "-e", f"{sha}^{{commit}}"])[0] != 0:
            errs.append(f"{field} '{sha}' is not a real commit")
    return errs


def check_freshness(m):
    """3. reviewed_sha must equal head_sha (a rebase/bot-push after review voids it)."""
    pr = m.get("pr") or {}
    reviewed = pr.get("reviewed_sha")
    if reviewed and reviewed != m.get("head_sha"):
        return [f"stale review: reviewed_sha '{reviewed}' != head_sha '{m.get('head_sha')}'"]
    return []


def check_negative_control(m):
    """4. Mutation units must carry a negative control (tool + result)."""
    is_mutation = m.get("unit_class") == "mutation" or m.get("unit") in MUTATING_MISSIONS
    if not is_mutation:
        return []
    nc = m.get("negative_control") or {}
    if not nc.get("tool") or not nc.get("result"):
        return ["mutation unit missing negative_control.tool / .result"]
    return []


def check_ancestry(m, base):
    """5. Best-effort: head_sha is an ancestor of origin/<base> (post-merge)."""
    if not base:
        return ["NOTE: --base not given — ancestry check skipped (pre-merge/offline)"]
    ref = f"origin/{base}"
    if _git(["rev-parse", "--verify", ref])[0] != 0:
        return [f"NOTE: {ref} not found — ancestry check skipped"]
    code, _ = _git(["merge-base", "--is-ancestor", m.get("head_sha", ""), ref])
    if code != 0:
        return [f"head_sha is not an ancestor of {ref} (not merged / wrong base)"]
    return []


def check_symbol_on_base(symbol, base):
    """6. Best-effort: a unit symbol is greppable on origin/<base> (change is real on base)."""
    if not symbol or not base:
        return []
    ref = f"origin/{base}"
    code, out = _git(["grep", "-l", "-e", symbol, ref])
    if code != 0 or not out:
        return [f"symbol '{symbol}' not found on {ref} (change may not be on base)"]
    return []


def verify(manifest_path, base=None, symbol=None):
    """Return (fatal_errors, notes). fatal_errors non-empty => exit 2."""
    m, err = load_manifest(manifest_path)
    if err:
        return None, err
    fatal, notes = [], []
    for result in (
        check_scope(m), check_shas_present(m), check_real_commits(m),
        check_freshness(m), check_negative_control(m),
        check_ancestry(m, base), check_symbol_on_base(symbol, base),
    ):
        for line in result:
            (notes if line.startswith("NOTE:") else fatal).append(line)
    return (fatal, notes), None


def main(argv=None):
    ap = argparse.ArgumentParser(description="Independent evidence-manifest verifier.")
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--base", default=None, help="integration base branch (for ancestry)")
    ap.add_argument("--symbol", default=None, help="a unit symbol to grep on the base")
    args = ap.parse_args(argv)

    if shutil.which("git") is None:
        print("dependency: git not on PATH", file=sys.stderr)
        return 1
    out, load_err = verify(args.manifest, args.base, args.symbol)
    if load_err:
        print(load_err, file=sys.stderr)
        return 1
    fatal, notes = out
    for n in notes:
        print(n)
    if fatal:
        for f in fatal:
            print(f"FAIL: {f}", file=sys.stderr)
        print(f"verify: {len(fatal)} invariant(s) failed — unit is NOT done", file=sys.stderr)
        return 2
    print("verify: OK — all required checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
