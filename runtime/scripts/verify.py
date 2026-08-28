#!/usr/bin/env python3
"""verify.py — independent, separate-process re-derivation of an evidence manifest.

The completion oracle runs OUTSIDE the producing session and TRUSTS NOTHING IN THE WORKER'S MANIFEST
that it can instead check against authoritative state. The manifest is a *claim*; the authorities are:
  - the COORDINATOR's frozen contract — the criterion denominator materialized at dispatch and passed
    in as --contract-source/--contract-digest, NOT read from the worker's manifest;
  - GIT — commit existence and ancestry;
  - GITHUB — whether a review actually happened at the reviewed SHA (a manifest-set reviewed_sha
    proves nothing);
  - the NEGATIVE-CONTROL artifact, and with --execute-nc a replay.

Checks (evidence-manifest.md section 2), scope FIRST:
  1. scope: re-derive the criterion set from the COORDINATOR-supplied authoritative contract
     (--contract-source read at --contract-digest) — never from the manifest. Confirm the manifest's
     criteria / criterion_ids cover it and that its own declared digest matches (swap detection).
     FAIL-CLOSED without an authoritative contract: a manifest cannot certify its own denominator.
  2. base_sha / head_sha are real commits (git cat-file -e).
  3. review: a mutation unit needs an INDEPENDENT APPROVED review whose commit == head_sha, looked
     up on GitHub (gh api). FAIL-CLOSED — a manifest-set reviewed_sha is not evidence a review happened.
  4. negative control: structured (known tool, KILLED/RED verdict, pinned mutant, artifact) AND the
     artifact must corroborate (name the mutant, show it killed). Static reading is corroboration, not
     proof; --execute-nc replays it (evidence-manifest §2's re-execution sample is the sound form).
  5. ancestry (best-effort) · 6. symbol-on-base (best-effort).

Usage:
    verify.py --manifest <m.json> --contract-source <path@ref> --contract-digest <sha256:…>
              [--repo owner/name] [--unit-class mutation|report-only|planning] [--execute-nc]
              [--base <branch>] [--symbol <tok>]
    # exit 0 = all REQUIRED checks pass · 1 = usage/dependency · 2 = a REQUIRED invariant FAILED
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

# The coordinator classifies each unit at dispatch (a --unit-class flag / ORCA_UNIT_CLASS), NEVER the
# worker's manifest. Mutation units land code and need the review + negative-control authorities;
# report-only / planning units bind evidence differently (evidence-manifest.md section 3). A missing
# or unknown class defaults to mutation (fail-safe): the strict authorities run.
UNIT_CLASSES = ("mutation", "report-only", "planning")
NC_TOOLS = {"mutmut", "cosmic-ray", "stryker", "pitest", "cargo-mutants", "go-mutesting", "revert"}
# Criterion ids in a frozen source (AC-1, SC-12, REQ-3, …). A JSON source may instead declare an
# explicit criterion_ids array, which is unambiguous and preferred.
CRIT_ID_RE = re.compile(r"\b[A-Z][A-Z0-9]*-\d+\b")


def _run(args, timeout=20):
    """Run a command; return (code, stdout, stderr). Never raises."""
    try:
        p = subprocess.run(args, capture_output=True, text=True, timeout=timeout, check=False)
        return p.returncode, p.stdout, p.stderr
    except (subprocess.TimeoutExpired, OSError) as err:
        return 1, "", str(err)


def _git(args, timeout=10):
    code, out, _ = _run(["git", *args], timeout=timeout)
    return code, out.strip()


def infer_repo():
    code, url = _git(["remote", "get-url", "origin"])
    if code != 0:
        return None
    m = re.search(r"[:/]([^/]+/[^/]+?)(?:\.git)?$", url.strip())
    return m.group(1) if m else None


def load_manifest(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh), None
    except (OSError, json.JSONDecodeError) as err:
        return None, f"unreadable/invalid manifest: {err}"


def _resolve(path):
    """Resolve a repo-relative path against the git toplevel; absolute paths pass through."""
    p = Path(path)
    if p.is_absolute():
        return p
    code, top = _git(["rev-parse", "--show-toplevel"])
    return (Path(top) / path) if code == 0 else p


def read_source(source):
    """Read a source: `path@gitref` reads the immutable git blob at a real commit; a bare/absolute
    path reads the file. Returns (content, err). Bytes are NOT stripped (the digest must see them)."""
    if not source:
        return None, "missing"
    path, sep, ref = source.partition("@")
    if sep and ref:
        if path.startswith("-") or ref.startswith("-"):
            return None, "refusing option-like ref/path (leading '-') — see git-option-injection guard"
        code, out, err = _run(["git", "show", f"{ref}:{path}"])
        return (out, None) if code == 0 else (None, (err.strip() or "git ref not found"))
    try:
        return _resolve(path).read_text(encoding="utf-8"), None
    except OSError as err:
        return None, str(err)


def sha256_of(content):
    return "sha256:" + hashlib.sha256(content.encode("utf-8")).hexdigest()


def _norm_digest(d):
    return d if d.startswith("sha256:") else "sha256:" + d


def extract_criterion_ids(content):
    """The authoritative criterion set, re-derived FROM the frozen source. A JSON source may declare
    `criterion_ids`; otherwise the ids are the AC-1/SC-2/… tokens in the text."""
    try:
        data = json.loads(content)
        if isinstance(data, dict) and isinstance(data.get("criterion_ids"), list):
            return set(data["criterion_ids"])
    except (json.JSONDecodeError, ValueError):
        pass
    return set(CRIT_ID_RE.findall(content))


def _is_mutation(unit_class):
    """True unless the coordinator explicitly classed the unit report-only/planning. Missing or
    unknown => mutation (fail-safe), so the review + negative-control authorities run."""
    return unit_class not in ("report-only", "planning")


def check_scope(m, auth_source, auth_digest):
    """1. The denominator is the COORDINATOR's frozen contract (auth_source @ auth_digest), NOT the
    worker's manifest. A worker that drops a criterion — from criterion_ids, criteria, or by pointing
    its own contract at a shrunken source — is caught, because the authoritative content still carries
    it and only the coordinator's digest is trusted. Fail-closed without an authoritative contract."""
    if not auth_source or not auth_digest:
        return ["scope: no authoritative contract (--contract-source/--contract-digest from the "
                "dispatch record) — a worker manifest cannot certify its own denominator"]
    content, err = read_source(auth_source)
    if err:
        return [f"scope: authoritative contract unreadable ({auth_source}): {err}"]
    want = _norm_digest(auth_digest)
    got = sha256_of(content)
    if got != want:
        return [f"scope: authoritative source does not match --contract-digest ({got} != {want})"]
    authoritative = extract_criterion_ids(content)
    if not authoritative:
        return ["scope: no criterion ids in the authoritative contract"]
    contract = m.get("contract") or {}
    errs = []
    mdigest = contract.get("digest")
    if mdigest and _norm_digest(mdigest) != want:
        errs.append("scope: manifest contract.digest != authoritative digest (denominator swap)")
    addressed = {c.get("id") for c in (m.get("criteria") or []) if c.get("addressed") is True}
    declared = set(contract.get("criterion_ids") or [])
    unaddressed = sorted(authoritative - addressed)
    if unaddressed:
        errs.append(f"scope: authoritative criteria not addressed in criteria[] "
                    f"(absent, or addressed != true): {unaddressed}")
    undeclared = sorted(authoritative - declared)
    if undeclared:
        errs.append(f"scope shrunk: contract.criterion_ids drops authoritative ids: {undeclared}")
    return errs


def check_shas_present(m):
    return [f"missing required '{f}'" for f in ("base_sha", "head_sha") if not m.get(f)]


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
    """A reviewed_sha, if claimed, must equal head_sha (a rebase/bot-push after review voids it).
    Independent proof that the review HAPPENED is check_review (mutation units)."""
    reviewed = (m.get("pr") or {}).get("reviewed_sha")
    head = m.get("head_sha")
    if reviewed and reviewed != head:
        return [f"stale review: reviewed_sha '{reviewed}' != head_sha '{head}'"]
    return []


def review_ok(reviews, head_sha):
    """Pure: an APPROVED review exists whose commit == head_sha."""
    return any(r.get("state") == "APPROVED" and r.get("commit_id") == head_sha for r in reviews)


def fetch_reviews(repo, pr_number):
    if shutil.which("gh") is None:
        return None, "gh not on PATH"
    code, out, err = _run(["gh", "api", f"repos/{repo}/pulls/{pr_number}/reviews"])
    if code != 0:
        return None, (err.strip() or "gh api failed")
    try:
        return json.loads(out), None
    except (json.JSONDecodeError, ValueError) as err:
        return None, str(err)


def check_review(m, repo, is_mutation):
    """3. A mutation unit needs an INDEPENDENT APPROVED review at head_sha — looked up on GitHub, not
    read from the manifest (a worker-set reviewed_sha is not evidence a review occurred). Fail-closed."""
    if not is_mutation:
        return []
    head = m.get("head_sha")
    number = (m.get("pr") or {}).get("number")
    if not number:
        return ["mutation unit: no pr.number to look up an independent review — unreviewed"]
    if not repo:
        return ["mutation unit: --repo not resolvable — cannot verify the review independently"]
    reviews, err = fetch_reviews(repo, number)
    if err:
        return [f"mutation unit: cannot fetch reviews for {repo}#{number} ({err}) — fail-closed"]
    if not review_ok(reviews, head):
        return [f"mutation unit: no APPROVED review at head_sha on {repo}#{number}"]
    return []


def check_negative_control(m, is_mutation, execute=False):
    """4. Structured NC AND the artifact must corroborate the pinned mutant being killed. Reading the
    artifact resolves the mutant + verdict; it is corroboration, not proof (a fabricated artifact can
    still be read). --execute-nc replays the control — evidence-manifest §2's re-execution sample is
    the sound form."""
    if not is_mutation:
        return []
    nc = m.get("negative_control") or {}
    errs = []
    tool = nc.get("tool")
    if tool not in NC_TOOLS:
        errs.append(f"negative_control.tool must be one of {sorted(NC_TOOLS)}, got {tool!r}")
    if not re.search(r"(?i)\b(killed|red)\b", nc.get("result") or ""):
        errs.append("negative_control.result must record the mutant KILLED / the proof going RED")
    mutant = nc.get("mutant")
    if tool and tool != "revert" and not mutant:
        errs.append("negative_control.mutant (a pinned mutant id) is required for a mutation tool")
    artifact = nc.get("artifact")
    if not artifact:
        errs.append("negative_control.artifact (an evidence path) is required")
        return errs
    content, err = read_source(artifact)
    if err:
        errs.append(f"negative_control.artifact unreadable ({artifact}): {err}")
        return errs
    if not re.search(r"(?i)\b(killed|red|fail)\b", content):
        errs.append("negative_control.artifact does not evidence a killed/RED outcome")
    if mutant and mutant not in content:
        errs.append("negative_control.artifact does not reference the pinned mutant")
    if execute:
        errs.append("NOTE: --execute-nc replay is not implemented in the reference verifier — run "
                    "evidence-manifest §2's re-execution sample for the sound proof")
    return errs


def check_ancestry(m, base):
    """5. Best-effort: head_sha is an ancestor of origin/<base> (post-merge)."""
    if not base:
        return ["NOTE: --base not given — ancestry check skipped (pre-merge/offline)"]
    ref = f"origin/{base}"
    if _git(["rev-parse", "--verify", ref])[0] != 0:
        return [f"NOTE: {ref} not found — ancestry check skipped"]
    if _git(["merge-base", "--is-ancestor", m.get("head_sha", ""), ref])[0] != 0:
        return [f"head_sha is not an ancestor of {ref} (not merged / wrong base)"]
    return []


def check_symbol_on_base(symbol, base):
    """6. Best-effort: a unit symbol is greppable on origin/<base> (change is real on base)."""
    if not symbol or not base:
        return []
    code, out, _ = _run(["git", "grep", "-l", "-e", symbol, f"origin/{base}"])
    if code != 0 or not out.strip():
        return [f"symbol '{symbol}' not found on origin/{base} (change may not be on base)"]
    return []


def verify(manifest_path, contract_source=None, contract_digest=None, repo=None,
           base=None, symbol=None, execute_nc=False, unit_class=None):
    """Return (fatal_errors, notes). fatal_errors non-empty => exit 2."""
    m, err = load_manifest(manifest_path)
    if err:
        return None, err
    is_mut = _is_mutation(unit_class)
    fatal, notes = [], []
    for result in (
        check_scope(m, contract_source, contract_digest),
        check_shas_present(m), check_real_commits(m),
        check_freshness(m), check_review(m, repo, is_mut),
        check_negative_control(m, is_mut, execute_nc),
        check_ancestry(m, base), check_symbol_on_base(symbol, base),
    ):
        for line in result:
            (notes if line.startswith("NOTE:") else fatal).append(line)
    return (fatal, notes), None


def main(argv=None):
    ap = argparse.ArgumentParser(description="Independent evidence-manifest verifier.")
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--contract-source", default=None,
                    help="AUTHORITATIVE frozen contract (path@ref), from the dispatch record — not the manifest")
    ap.add_argument("--contract-digest", default=None, help="AUTHORITATIVE sha256 of the frozen contract")
    ap.add_argument("--repo", default=None, help="owner/name for the review lookup (default: infer from origin)")
    ap.add_argument("--execute-nc", action="store_true", help="replay the negative control (heavier)")
    ap.add_argument("--base", default=None, help="integration base branch (for ancestry)")
    ap.add_argument("--symbol", default=None, help="a unit symbol to grep on the base")
    ap.add_argument("--unit-class", default=None, choices=UNIT_CLASSES,
                    help="unit class from the dispatch record (mutation|report-only|planning); "
                         "missing => mutation (fail-safe)")
    args = ap.parse_args(argv)

    if shutil.which("git") is None:
        print("dependency: git not on PATH", file=sys.stderr)
        return 1
    out, load_err = verify(args.manifest, args.contract_source, args.contract_digest,
                           args.repo or infer_repo(), args.base, args.symbol, args.execute_nc,
                           args.unit_class)
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
