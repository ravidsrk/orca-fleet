#!/usr/bin/env python3
"""verify.py — independent, separate-process re-derivation of an evidence manifest.

The completion oracle runs OUTSIDE the producing session — a headless subprocess (this
script, or `claude -p` / an MCP Task), NEVER a teammate. Teammate / cross-session messages
are in-band and self-certifying: exactly the trace-as-oracle failure the evidence protocol
rejects (evidence-manifest.md, reviewed-sha-freshness.md). This re-derives the
git-authoritative facts DETERMINISTICALLY, before any LLM judgment, and fails closed.

Checks (evidence-manifest.md section 2), scope FIRST because passing tests on a shrunken
denominator is the most dangerous false "done":
    1. scope not shrunk: RE-DERIVE the criterion set from the frozen contract.source (a git blob at
       `path@ref`, or the working-tree file), verify contract.digest, and confirm criteria[] and
       criterion_ids cover it — never a comparison of two manifest-controlled fields. Fail-closed
       when the source cannot be re-read.
    2. base_sha / head_sha are present and real commits (git cat-file -e).
    3. freshness: mutation units REQUIRE pr.reviewed_sha, and it must equal head_sha.
    4. negative control: mutation units carry a STRUCTURED control (known tool, KILLED/RED verdict,
       a pinned mutant unless a plain revert, and an evidence artifact).
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
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

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

NC_TOOLS = {"mutmut", "cosmic-ray", "stryker", "pitest", "cargo-mutants", "go-mutesting", "revert"}
# Criterion ids in a frozen source (AC-1, SC-12, REQ-3, …). JSON sources may instead declare an
# explicit criterion_ids array, which is preferred and unambiguous.
CRIT_ID_RE = re.compile(r"\b[A-Z][A-Z0-9]*-\d+\b")


def _git_show(ref, path):
    """Read a file's content from git at a ref — authoritative: a blob at a real commit cannot be
    forged by the worker. Returns (content, err); does NOT strip (digest must see exact bytes)."""
    try:
        p = subprocess.run(["git", "show", f"{ref}:{path}"],
                           capture_output=True, text=True, timeout=10, check=False)
        return (p.stdout, None) if p.returncode == 0 else (None, p.stderr.strip() or "not found")
    except (subprocess.TimeoutExpired, OSError) as err:
        return None, str(err)


def read_frozen_source(source):
    """Read the FROZEN contract source. `source` is `path` or `path@gitref`.

    `path@gitref` is read from git (sound — the blob is anchored to a real commit). A bare path is
    read from the working tree (resolved against the repo toplevel) — weaker, because the worker can
    write it, so it returns a note recommending `path@ref`. Returns (content, note, err)."""
    if not source:
        return None, None, "contract.source missing"
    path, sep, ref = source.partition("@")
    if sep and ref:
        content, err = _git_show(ref, path)
        if err is not None:
            return None, None, f"git show {ref}:{path}: {err}"
        return content, None, None
    p = Path(path)
    if not p.is_absolute():
        code, top = _git(["rev-parse", "--show-toplevel"])
        if code == 0:
            p = Path(top) / path
    try:
        return p.read_text(encoding="utf-8"), \
            "source read from working tree (not git-anchored — use path@ref for a sound denominator)", None
    except OSError as err:
        return None, None, str(err)


def extract_criterion_ids(content):
    """The authoritative criterion set, re-derived FROM the frozen source (not the manifest). A JSON
    source may declare `criterion_ids`; otherwise ids are the AC-1/SC-2/… tokens in the text."""
    try:
        data = json.loads(content)
        if isinstance(data, dict) and isinstance(data.get("criterion_ids"), list):
            return set(data["criterion_ids"])
    except (json.JSONDecodeError, ValueError):
        pass
    return set(CRIT_ID_RE.findall(content))


def load_manifest(path):
    """Return (manifest, error). Never raises."""
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh), None
    except (OSError, json.JSONDecodeError) as err:
        return None, f"unreadable/invalid manifest: {err}"


def check_scope(m):
    """1. Re-derive the frozen denominator FROM contract.source (authoritative) and confirm the
    manifest addressed it — NOT a comparison of two manifest-controlled fields. A worker that drops a
    criterion from its own criterion_ids AND criteria is still caught, because the frozen source
    carries it. Fail-closed when the source cannot be re-read (no source ⇒ not verifiable)."""
    contract = m.get("contract") or {}
    content, note, err = read_frozen_source(contract.get("source"))
    if err:
        return [f"scope: cannot re-derive the frozen denominator — {err}"]
    digest = contract.get("digest")
    if digest:
        got = "sha256:" + hashlib.sha256(content.encode("utf-8")).hexdigest()
        want = digest if digest.startswith("sha256:") else "sha256:" + digest
        if got != want:
            return [f"scope: contract.digest mismatch — frozen source hashes to {got}, manifest claims {want}"]
    authoritative = extract_criterion_ids(content)
    if not authoritative:
        return ["scope: no criterion ids found in the frozen contract.source"]
    addressed = {c.get("id") for c in (m.get("criteria") or [])}
    declared = set(contract.get("criterion_ids") or [])
    errs = []
    unaddressed = sorted(authoritative - addressed)
    if unaddressed:
        errs.append(f"scope shrunk: frozen-source criteria not in criteria[]: {unaddressed}")
    undeclared = sorted(authoritative - declared)
    if undeclared:
        errs.append(f"scope shrunk: contract.criterion_ids drops frozen-source ids: {undeclared}")
    if note:
        errs.append("NOTE: " + note)
    return errs


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
    """3. reviewed_sha must equal head_sha (a rebase/bot-push after review voids it). For a mutation
    unit the review is REQUIRED — a missing/empty reviewed_sha is unreviewed code, which cannot
    complete."""
    is_mutation = m.get("unit_class") == "mutation" or m.get("unit") in MUTATING_MISSIONS
    reviewed = (m.get("pr") or {}).get("reviewed_sha")
    head = m.get("head_sha")
    if is_mutation and not reviewed:
        return ["mutation unit missing pr.reviewed_sha — unreviewed code cannot complete"]
    if reviewed and reviewed != head:
        return [f"stale review: reviewed_sha '{reviewed}' != head_sha '{head}'"]
    return []


def check_negative_control(m):
    """4. Mutation units must carry a STRUCTURED negative control: a known tool, a KILLED/RED
    verdict, a pinned mutant (unless the tool is a plain revert), and an evidence artifact. This does
    not prove the control was executed (that is §2's ≥10% re-execution sample) but it rejects the
    arbitrary-string evidence a truthiness check would wave through."""
    is_mutation = m.get("unit_class") == "mutation" or m.get("unit") in MUTATING_MISSIONS
    if not is_mutation:
        return []
    nc = m.get("negative_control") or {}
    errs = []
    tool = nc.get("tool")
    if tool not in NC_TOOLS:
        errs.append(f"negative_control.tool must be one of {sorted(NC_TOOLS)}, got {tool!r}")
    if not re.search(r"(?i)\b(killed|red)\b", nc.get("result") or ""):
        errs.append("negative_control.result must record the mutant KILLED / the proof going RED")
    if tool and tool != "revert" and not nc.get("mutant"):
        errs.append("negative_control.mutant (a pinned mutant id) is required for a mutation tool")
    if not nc.get("artifact"):
        errs.append("negative_control.artifact (an evidence path) is required")
    return errs


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
