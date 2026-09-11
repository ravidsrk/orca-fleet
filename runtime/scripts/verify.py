#!/usr/bin/env python3
"""verify.py — independent, separate-process re-derivation of an evidence manifest.

The completion oracle runs OUTSIDE the producing session and TRUSTS NOTHING IN THE WORKER'S MANIFEST
that it can instead check against authoritative state. The manifest is a *claim*; the authorities are:
  - the COORDINATOR's frozen contract — the criterion denominator materialized at dispatch and passed
    in as --contract-source/--contract-digest, NOT read from the worker's manifest;
  - GIT — commit existence and ancestry;
  - GITHUB — whether a review actually happened at the reviewed SHA (a manifest-set reviewed_sha
    proves nothing);
  - the NEGATIVE-CONTROL, EXECUTED (--execute-nc) in throwaway worktrees against the command the
    COORDINATOR names (--nc-command) — the artifact alone is corroboration, never proof, and a
    command the worker names proves only what the worker chose to prove (#279).

Checks (evidence-manifest.md section 2), scope FIRST:
  1. scope: re-derive the criterion set from the COORDINATOR-supplied authoritative contract
     (--contract-source read at --contract-digest) — never from the manifest. Confirm the manifest's
     criteria / criterion_ids cover it and that its own declared digest matches (swap detection).
     FAIL-CLOSED without an authoritative contract: a manifest cannot certify its own denominator.
  2. base_sha / head_sha are real commits (git cat-file -e).
  3. review: a mutation unit needs an INDEPENDENT APPROVED review whose commit == head_sha, looked
     up on GitHub (gh api). FAIL-CLOSED — a manifest-set reviewed_sha is not evidence a review happened.
     The two lanes that WAIVE that review (--lighting dark-eligible, --no-gh) pass ONLY with an
     EXECUTED negative control: there the control is the whole oracle, so it cannot be text (#256).
  4. negative control: structured (known tool, KILLED/RED verdict, pinned mutant, artifact) AND the
     artifact must corroborate. With --execute-nc the control is APPLIED in a throwaway worktree at
     head_sha and the command --nc-command names must go NON-ZERO under it and ZERO at clean
     head_sha (#255, #279).
  5. commands: a mutation unit needs ≥1 recorded exit-0 command whose `wtree` is head_sha's tree,
     written by evidence-run.py — the clean-env re-run as a machine check (#3 of the audit ledger).
  6. redaction: the manifest and every named artifact are scanned for credential shapes (#14).
  7. ancestry (best-effort) · 8. symbol-on-base (best-effort).

Every evidence path is repo-relative and bounded by the git toplevel; a manifest-named artifact is
PINNED — tracked at head_sha, or hashed in the manifest's `artifacts[]` inventory (#267).

Usage:
    verify.py --manifest <m.json> --contract-source <path@ref> --contract-digest <sha256:…>
              [--repo owner/name] [--unit-class mutation|report-only|planning]
              [--execute-nc --nc-command <cmd>] [--base <branch>] [--symbol <tok>]
    # exit 0 = all REQUIRED checks pass · 1 = usage/dependency · 2 = a REQUIRED invariant FAILED
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import importlib.util
import json
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# The coordinator classifies each unit at dispatch (a --unit-class flag / ORCA_UNIT_CLASS), NEVER the
# worker's manifest. Mutation units land code and need the review + negative-control authorities;
# report-only / planning units bind evidence differently (evidence-manifest.md section 3). A missing
# or unknown class defaults to mutation (fail-safe): the strict authorities run.
UNIT_CLASSES = ("mutation", "report-only", "planning")
NC_TOOLS = {"mutmut", "cosmic-ray", "stryker", "pitest", "cargo-mutants", "go-mutesting", "revert",
            "hand"}  # hand = a hand-written mutant (boundary flip / negated condition / zeroed return, compile-preserving; the diff is quoted in the artifact)
REVIEWER_MODES = {"cross-vendor", "same-vendor-fresh", "instructed-isolation"}
LIGHTING_VALUES = {"lit", "dark-eligible"}
# The two negative-control tools verify.py can REPLAY itself (#255). Any other tool under
# --execute-nc is fail-closed: an unreplayable control is not an executed one.
EXECUTABLE_NC_TOOLS = ("revert", "hand")
# Criterion ids in a frozen source: hyphenated (AC-1, SC-12, REQ-3) or compact (AC1, SC12). A JSON
# source may instead declare an explicit criterion_ids array, which is unambiguous and PREFERRED —
# write frozen contracts as JSON where you can.
# #268: in a TEXT source an id counts only where it BEGINS a list item or a line and is followed by
# a separator — `- AC-1: …`, `2. SC-3)`, `REQ-4.`. Prose tokens of the same shape (`SHA-256`,
# `PR-12`, `RFC-7519`, `ISO-8601`) are NOT criteria; counting them is a FALSE RED that makes the
# gate unusable on realistic contracts (docs/reviews/2026-09-10-review.md A11). The anchor is the one place a contract
# author declares a criterion, so under-counting (which would let scope shrink) stays unlikely.
CRIT_ID_RE = re.compile(
    r"(?m)^[ \t]*(?:[-*]|\d+\.)?[ \t]*((?:[A-Z][A-Z0-9]*-\d+)|(?:[A-Z]{2,}\d+))[ \t]*[:.)]")
HEX40_RE = re.compile(r"^[0-9a-f]{40}$")
# #14: a SHA-pinned manifest is permanent, so a credential that reaches one is permanent too.
# gitleaks is preferred when installed; these shapes are the fail-closed built-in floor.
REDACTION_PATTERNS = (
    ("aws-access-key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("github-token", re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{20,}\b")),
    ("github-pat", re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b")),
    ("private-key-block", re.compile(r"-----BEGIN (?:[A-Z]+ )?PRIVATE KEY-----")),
    ("slack-token", re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}\b")),
    ("inline-credential", re.compile(
        r"(?i)\b(?:password|passwd|secret)\s*=\s*[\"']?[^\s\"';,)}<]{6,}")),
)
# A run where NOTHING was killed (the pinned mutant among them) — the sound-fail signal. Aggregate
# survivor counts of OTHER mutants are NOT here: a multi-mutant run where the pinned mutant WAS killed
# is valid, so survival is scoped to the pinned mutant id in check_negative_control.
_NC_ZERO_KILL_RE = re.compile(
    r"(?i)(not\s+killed|not\s+red|\bno\s+mutants?\s+killed\b|killed\s*[:=]\s*0\b"
    r"|\b0(?:\.0+)?\s*%\s+killed\b|\b0\s+mutants?\s+killed\b|\b0\s+killed\b)")


def _run(args, timeout=20):
    """Run a command; return (code, stdout, stderr). Never raises."""
    try:
        p = subprocess.run(args, capture_output=True, text=True, timeout=timeout, check=False)
        return p.returncode, p.stdout, p.stderr
    except (subprocess.TimeoutExpired, OSError) as err:
        return 1, "", str(err)


def _run_bytes(args, timeout=20):
    """Run a command; return (code, stdout_bytes, stderr). stdout is RAW bytes — no newline
    translation (#180) — stderr stays text for error messages. Never raises."""
    try:
        p = subprocess.run(args, capture_output=True, timeout=timeout, check=False)
        return p.returncode, p.stdout, p.stderr.decode("utf-8", "replace")
    except (subprocess.TimeoutExpired, OSError) as err:
        return 1, b"", str(err)


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
            obj = json.load(fh)
    except (OSError, json.JSONDecodeError, UnicodeDecodeError) as err:
        return None, f"unreadable/invalid manifest: {err}"
    if not isinstance(obj, dict):
        return None, f"manifest must be a JSON object, got {type(obj).__name__}"
    return obj, None


def _toplevel():
    code, top = _git(["rev-parse", "--show-toplevel"])
    return top if code == 0 else None


def _resolve(path):
    """Resolve a repo-relative path against the git toplevel. Returns (Path|None, err).

    #267: an ABSOLUTE path, or one that escapes the toplevel, is REFUSED. Evidence outside the
    clone is evidence no auditor can re-derive — docs/reviews/2026-09-10-review.md A10 walked a negative-control artifact
    out to a temp dir, untracked and unhashed, and the gate read it happily. There is no permissive
    fallback: outside a git repo there is no toplevel to bound against, so the read fails closed
    rather than silently widening."""
    p = Path(path)
    if p.is_absolute():
        return None, f"absolute evidence path refused — must be repo-relative (#267): {path}"
    if p.parts and p.parts[0] == "..":
        return None, f"evidence path escapes the repo toplevel (#267): {path}"
    top = _toplevel()
    if top is None:
        return None, "not inside a git repo — no toplevel to bound the evidence path against (#267)"
    root = Path(top).resolve()
    try:
        full = (root / p).resolve()
    except OSError as err:  # pragma: no cover — resolve() rarely raises on POSIX
        return None, str(err)
    if full != root and root not in full.parents:
        return None, f"evidence path escapes the repo toplevel (#267): {path}"
    return full, None


def read_source(source):
    """Read a source: `path@gitref` reads the immutable blob at a real commit; a bare path is read
    from the working tree, bounded by _resolve. Returns (raw_bytes, err). Bytes are NOT stripped or
    newline-translated — the digest must see exactly what `shasum -a 256` saw (#180)."""
    if not source:
        return None, "missing"
    path, sep, ref = source.partition("@")
    if sep and ref:
        if path.startswith("-") or ref.startswith("-"):
            return None, "refusing option-like ref/path (leading '-') — see git-option-injection guard"
        if Path(path).is_absolute():
            return None, f"absolute path refused in a path@ref source (#267): {path}"
        code, out, err = _run_bytes(["git", "show", f"{ref}:{path}"])
        return (out, None) if code == 0 else (None, (err.strip() or "git ref not found"))
    resolved, err = _resolve(path)
    if err:
        return None, err
    try:
        return resolved.read_bytes(), None
    except OSError as oserr:
        return None, str(oserr)


def artifact_inventory(m):
    """The manifest's `artifacts[]` integrity inventory as {path: sha256-hex}. Entries may be bare
    strings (named, but NOT pinned) or `{"path": …, "sha256": …}` objects; only the latter pin a
    working-tree file."""
    out = {}
    for entry in (m.get("artifacts") or []):
        if isinstance(entry, dict):
            path, digest = entry.get("path"), entry.get("sha256")
            if isinstance(path, str) and isinstance(digest, str):
                out[path] = digest.strip().lower().replace("sha256:", "", 1)
    return out


def read_artifact(m, path):
    """Read a MANIFEST-NAMED artifact. Returns (raw_bytes, err).

    #267: two conditions, both required.
      1. the path is repo-relative and inside the toplevel (_resolve);
      2. the BYTES are pinned — either the path is TRACKED at `head_sha`
         (`git cat-file -e <head_sha>:<path>`; the blob at that commit is what gets read), or the
         working-tree file's sha256 matches an entry in the manifest's `artifacts[]` inventory.
    An untracked, unhashed file is a claim ABOUT a file, not evidence: it can be rewritten between
    the run and the audit and nothing notices."""
    if not path:
        return None, "missing"
    if "@" in path:
        return None, "artifact must be a repo-relative path, not a path@ref (#267)"
    resolved, err = _resolve(path)
    if err:
        return None, err
    head = m.get("head_sha")
    if head and HEX40_RE.match(str(head)) and _git(["cat-file", "-e", f"{head}:{path}"])[0] == 0:
        code, out, gerr = _run_bytes(["git", "show", f"{head}:{path}"])
        if code == 0:
            return out, None
        return None, (gerr.strip() or "cannot read the tracked artifact at head_sha")
    try:
        raw = resolved.read_bytes()
    except OSError as oserr:
        return None, str(oserr)
    want = artifact_inventory(m).get(path)
    if not want:
        return None, (f"artifact '{path}' is neither tracked at head_sha nor pinned by a sha256 in "
                      "the manifest's artifacts[] integrity inventory — unpinned evidence (#267)")
    got = hashlib.sha256(raw).hexdigest()
    if got != want:
        return None, (f"artifact '{path}' hashes {got} but artifacts[] pins {want} — the evidence "
                      "changed after it was inventoried (#267)")
    return raw, None


def sha256_of(content):
    """Digest of RAW BYTES, matching `shasum -a 256` (coordinators compute digests over bytes)."""
    return "sha256:" + hashlib.sha256(content).hexdigest()


def _norm_digest(d):
    return d if d.startswith("sha256:") else "sha256:" + d


# Any token SHAPED like a criterion id, wherever it sits. CRIT_ID_RE only matches the ones that
# BEGIN a list item or line, which is what keeps `see RFC-7519` out of the denominator (#268).
CRIT_SHAPED_RE = re.compile(r"\b((?:[A-Z][A-Z0-9]*-\d+)|(?:[A-Z]{2,}\d+))\b")


def _criterion_family(token):
    """The family prefix of a criterion id, in either supported shape: AC-1 -> AC, SC12 -> SC.

    Both shapes are counted by CRIT_ID_RE, so both need a family. Reading the family off the hyphen
    alone skipped every compact id, and A16 then worked verbatim by dropping one character: a
    contract counting `- SC12:` while hiding `| SC13 |` in a table row was not flagged, though the
    hyphenated spelling of the same attack was (PR #308 review, P1).
    """
    head, sep, _ = token.rpartition("-")
    return head if sep else token.rstrip("0123456789")


def hidden_criterion_ids(content, counted):
    """Criterion ids the contract carries in a form the extractor does not count (A16; #296).

    The denominator is the whole scope guarantee: coverage is measured against it, so a contract
    that hides criteria from the extractor shrinks the thing the unit is graded on while still
    reading as a full specification to a human. Attack A16 wrote them as table rows and em-dash
    lines — `| AC-2 | … |`, `AC-3 — …` — and a three-criterion contract graded as one.

    Refusing every uncounted `AAA-9` token would refuse prose: `see RFC-7519`, `ISO-8601`,
    `SHA-256`. What distinguishes a hidden criterion is that it shares its PREFIX with one the
    contract does count — a contract's criteria are numbered in one family by construction, so
    `AC-2` beside a counted `AC-1` is a criterion in the wrong shape, while `RFC-7519` is not.
    A contract that hides ALL of them extracts nothing and is already refused upstream.
    """
    prefixes = {_criterion_family(cid) for cid in counted}
    hidden = {}
    for i, line in enumerate(content.splitlines(), 1):
        for token in CRIT_SHAPED_RE.findall(line):
            if token in counted:
                continue
            if _criterion_family(token) in prefixes:
                hidden.setdefault(token, i)
    return hidden


def json_contract(content):
    """The parsed contract if it is JSON declaring an explicit criterion_ids array, else None.

    That array IS the denominator — declared, machine-readable, unambiguous. Nothing is being
    scraped out of prose, so there is no prose to be fooled by, and the text heuristic below must
    not run on it (PR #308 review, P1): a valid contract whose descriptive fields mention an old
    `AC-9` beside an explicit `["AC-1"]` was refused, and the refusal told the author to use the
    very JSON array they had used.
    """
    try:
        data = json.loads(content)
    except (json.JSONDecodeError, ValueError):
        return None
    if isinstance(data, dict) and isinstance(data.get("criterion_ids"), list):
        return data
    return None


def extract_criterion_ids(content):
    """The authoritative criterion set, re-derived FROM the frozen source. A JSON source may declare
    `criterion_ids` — unambiguous, and PREFERRED. Otherwise the ids are the tokens that BEGIN a list
    item or line in the text (CRIT_ID_RE): `- AC-1: …` is a criterion, `see RFC-7519` is prose
    (#268)."""
    doc = json_contract(content)
    if doc is not None:
        return set(doc["criterion_ids"])
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
    text = content.decode("utf-8")
    authoritative = extract_criterion_ids(text)
    if not authoritative:
        return ["scope: no criterion ids in the authoritative contract"]
    doc = json_contract(text)
    if doc is not None:
        # A declared array needs no heuristic — but it can still under-declare. A16 in JSON form is
        # a `criteria` list a human reads as the spec beside a shorter `criterion_ids`, so check it
        # structurally, against the document's own ids, rather than by scanning its text.
        listed = {c.get("id") for c in (doc.get("criteria") or [])
                  if isinstance(c, dict) and isinstance(c.get("id"), str)}
        undeclared = sorted(listed - authoritative)
        if undeclared:
            return [f"scope: the authoritative contract lists {undeclared} in its criteria[] but "
                    f"leaves them out of criterion_ids, so the denominator would be "
                    f"{sorted(authoritative)} — smaller than the contract a human reads, which is "
                    "the whole scope guarantee. Declare every criterion in criterion_ids (#296)"]
    else:
        hidden = hidden_criterion_ids(text, authoritative)
        if hidden:
            where = ", ".join(f"{tok} (line {ln})" for tok, ln in sorted(hidden.items()))
            return [f"scope: the authoritative contract carries {where} in a form the extractor "
                    "does not count, beside criteria it does. The denominator would be "
                    f"{sorted(authoritative)} — smaller than the contract a human reads, which is "
                    "the whole scope guarantee. Write every criterion as a list item "
                    "(`- AC-2: …`), or use a JSON contract with an explicit criterion_ids array "
                    "(#296)"]
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


def check_real_commits(m, is_mutation=False):
    """2. base_sha / head_sha must be real, immutable commits. A symbolic ref like 'HEAD' resolves
    but is not a pinned commit — fatal for a mutation unit, advisory otherwise. Existence check is
    skipped outside a git repo."""
    errs = []
    for field in ("base_sha", "head_sha"):
        sha = m.get(field)
        if sha and not HEX40_RE.match(sha):
            msg = f"{field} '{sha}' is not a pinned 40-hex commit SHA (a symbolic ref is not immutable)"
            errs.append(msg if is_mutation else f"NOTE: {msg}")
    if _git(["rev-parse", "--is-inside-work-tree"])[0] != 0:
        return errs + ["NOTE: not inside a git repo — commit-existence check skipped"]
    for field in ("base_sha", "head_sha"):
        sha = m.get(field)
        if sha and _git(["cat-file", "-e", f"{sha}^{{commit}}"])[0] != 0:
            errs.append(f"{field} '{sha}' is not a real commit")
    return errs


def check_freshness(m):
    """A reviewed_sha, if claimed, must equal head_sha (a rebase/bot-push after review voids it) —
    UNLESS `pr.reviewed_wtree` is bound to BOTH trees: tree(reviewed_sha) == reviewed_wtree ==
    tree(head_sha), all recomputed locally (a worker-chosen 40-hex string that only matches the
    head is a forgery, not freshness). A content-identical rebase/amend does not void the review;
    any content change does (reviewed-sha-freshness.md). The SHA remains the GitHub-lookup key.
    Independent proof that the review HAPPENED is check_review (mutation units)."""
    reviewed = (m.get("pr") or {}).get("reviewed_sha")
    head = m.get("head_sha")
    if reviewed and reviewed != head and not _wtree_bound(m):
        return [f"stale review: reviewed_sha '{reviewed}' != head_sha '{head}'"]
    return []


def _tree(sha):
    code, out = _git(["rev-parse", f"{sha}^{{tree}}"])
    return out if code == 0 else None


def _wtree_bound(m):
    """True only when pr.reviewed_wtree is a 40-hex tree SHA bound to BOTH the reviewed commit's
    tree and the head's tree (a content-identical head move). Fail-closed on anything missing,
    non-hex, outside a git repo, or unresolvable."""
    pr = m.get("pr") or {}
    reviewed, head, wtree = pr.get("reviewed_sha"), m.get("head_sha"), pr.get("reviewed_wtree")
    if not (reviewed and head and wtree):
        return False
    if not all(HEX40_RE.match(str(v)) for v in (reviewed, head, wtree)):
        return False
    if _git(["rev-parse", "--is-inside-work-tree"])[0] != 0:
        return False
    rt, ht = _tree(reviewed), _tree(head)
    return rt is not None and ht is not None and rt == wtree == ht


def review_ok(reviews, head_sha, author=None, also_sha=None):
    """Pure: the LATEST review by some INDEPENDENT reviewer (not the PR author) is APPROVED at
    head_sha. A later COMMENTED/DISMISSED by the same reviewer supersedes an earlier APPROVED.
    also_sha (a content-identical earlier head, tree-bound by _wtree_bound) is accepted too —
    the reviewer approved exactly this content."""
    latest = {}
    for r in reviews or []:
        latest[(r.get("user") or {}).get("login")] = r  # chronological: last per reviewer wins
    ok_shas = {head_sha} | ({also_sha} if also_sha else set())
    for who, r in latest.items():
        if author is not None and who == author:
            continue
        if r.get("state") == "APPROVED" and r.get("commit_id") in ok_shas:
            return True
    return False


def parse_review_pages(out):
    """`gh api --paginate` concatenates one JSON array per page; merge them into a single list.
    Fail-closed on malformed output or a non-array page."""
    dec = json.JSONDecoder()
    items, i = [], 0
    while True:
        while i < len(out) and out[i] in " \t\r\n":
            i += 1
        if i >= len(out):
            return items, None
        try:
            obj, i = dec.raw_decode(out, i)
        except (json.JSONDecodeError, ValueError) as err:
            return None, str(err)
        if not isinstance(obj, list):
            return None, "unexpected non-array page in gh output"
        items.extend(obj)


def fetch_reviews(repo, pr_number):
    if shutil.which("gh") is None:
        return None, "gh not on PATH"
    # --paginate: without it GitHub returns the first 30 reviews only, and review_ok would
    # compute "latest per reviewer" over a stale window (#167). One HTTP round-trip per page,
    # so allow a longer timeout than the single-call default.
    code, out, err = _run(["gh", "api", "--paginate", f"repos/{repo}/pulls/{pr_number}/reviews"],
                          timeout=60)
    if code != 0:
        return None, (err.strip() or "gh api failed")
    return parse_review_pages(out)


def fetch_pr_author(repo, pr_number):
    code, out, _ = _run(["gh", "api", f"repos/{repo}/pulls/{pr_number}"])
    if code != 0:
        return None
    try:
        return (json.loads(out).get("user") or {}).get("login")
    except (json.JSONDecodeError, ValueError):
        return None


_WAIVER_NEEDS_EXECUTED_NC = (
    "{lane}: the independent review is WAIVED in this lane, so the negative control is the ONLY "
    "oracle left — and a control that was merely READ is a text file the worker wrote. It must be "
    "EXECUTED (--execute-nc / ORCA_EXECUTE_NC) and go RED. Fail-closed (#256; docs/reviews/2026-09-10-review.md A1/A2/A4/"
    "A6/A9 all landed on exactly this)")


def check_review(m, repo, is_mutation, no_gh=False, corroborated=False, dispatch_lighting=None,
                 nc_executed=False):
    """3. A mutation unit needs an INDEPENDENT review at head_sha. Default: an APPROVED GitHub review
    looked up on GitHub (a worker-set reviewed_sha is not evidence). Fail-closed.

    #256 — the two WAIVER lanes. A dark-eligible unit (a COORDINATOR dispatch decision,
    gate-classification.md) lands without a build-blind human review, and the sanctioned no-gh /
    offline lane (dispatch --no-gh; merge-serialization.md) replaces GitHub with a local reviewer
    artifact. In BOTH the negative control becomes the entire oracle, so both now require an
    EXECUTED control (`nc_executed`, from check_negative_control under --execute-nc) on top of the
    out-of-band coordinator contract. Static corroboration is necessary and NOT sufficient: the
    artifact is worker-written either way."""
    if not is_mutation:
        return []
    if dispatch_lighting == "dark-eligible":
        if not corroborated:
            return ["dark-eligible mutation: review is waived, so the negative-control oracle must be "
                    "unfakeable — but without an out-of-band coordinator contract (--contract-source + "
                    "--contract-digest) the worker-produced artifact is forgeable; fail-closed "
                    "(gate-classification.md)"]
        if not nc_executed:
            return [_WAIVER_NEEDS_EXECUTED_NC.format(lane="dark-eligible mutation")]
        return ["NOTE: independent review waived — dark-eligible unit (gate-classification.md); the "
                "EXECUTED negative control + tests are the oracle, not a human review"]
    head = m.get("head_sha")
    if no_gh:
        art = (m.get("review") or {}).get("artifact")
        if not art:
            return ["no-gh mutation unit: missing review.artifact (a local reviewer record at head_sha)"]
        content, err = read_artifact(m, art)
        if err:
            return [f"no-gh mutation unit: review.artifact unreadable ({art}): {err}"]
        if head and head not in content.decode("utf-8", "replace"):
            return ["no-gh mutation unit: review.artifact does not reference head_sha"]
        if not corroborated:
            return ["no-gh mutation unit: review.artifact is worker-forgeable without an out-of-band "
                    "coordinator contract (--contract-source + --contract-digest) — fail-closed "
                    "(sign the dispatch record; merge-serialization.md)"]
        if not nc_executed:
            return [_WAIVER_NEEDS_EXECUTED_NC.format(lane="no-gh mutation unit")]
        return ["NOTE: no-gh review is coordinator-attested via the frozen out-of-band contract (local "
                "reviewer artifact at head_sha) plus an EXECUTED negative control, not GitHub-verified "
                "— the weaker guarantee (merge-serialization.md)"]
    number = (m.get("pr") or {}).get("number")
    if not number:
        return ["mutation unit: no pr.number to look up an independent review — unreviewed"]
    if not repo:
        return ["mutation unit: --repo not resolvable — cannot verify the review independently"]
    reviews, err = fetch_reviews(repo, number)
    if err:
        return [f"mutation unit: cannot fetch reviews for {repo}#{number} ({err}) — fail-closed"]
    author = fetch_pr_author(repo, number)
    if author is None:
        return [f"mutation unit: cannot resolve PR author for {repo}#{number} — cannot exclude the "
                "author's self-review, fail-closed"]
    if not review_ok(reviews, head, author) and not (
            _wtree_bound(m) and review_ok(reviews, (m.get("pr") or {}).get("reviewed_sha"), author)):
        return [f"mutation unit: no INDEPENDENT APPROVED review at head_sha on {repo}#{number} "
                f"(the PR author's own approval and superseded reviews do not count; a review at "
                f"reviewed_sha only counts when reviewed_wtree binds its tree to the head's)"]
    return []


NC_TIMEOUT_S = 600


def _run_at(cwd, args, timeout=20, stdin_bytes=None):
    """Run a command in `cwd` with an optional stdin payload. argv only — never shell=True, so a
    manifest string can never become a shell command. Returns (code, stdout, stderr)."""
    try:
        p = subprocess.run(args, cwd=cwd, capture_output=True, timeout=timeout, check=False,
                           input=stdin_bytes)
        return (p.returncode, p.stdout.decode("utf-8", "replace"),
                p.stderr.decode("utf-8", "replace"))
    except (subprocess.TimeoutExpired, OSError) as err:
        return 124, "", str(err)


def _nc_command(nc, override):
    """The criterion-bound command the control must turn RED. Returns (argv, err).

    The command is NOT taken on the worker's word — and not on the ledger's either. Both are
    documents the graded worker writes: `negative_control.command` directly, and the `commands[]`
    records that once justified it via `evidence-run.py`, which runs on the worker and records
    what the worker hands it. Binding the one to the other is circular. A worker that writes both
    can nominate `grep -q FIXED calc.py` as its "criterion-bound proof", record it green at
    head_sha's tree, and clear the executed-control gate without ever running a test
    (docs/reviews/2026-09-11 §4 A12/A15; #279).

    So the only admissible source is `override`: the coordinator's `--nc-command`, supplied out of
    band the way `--contract-source` is. The manifest must still name a command, and it must AGREE
    with the coordinator's, so a worker cannot quietly swap the proof command underneath a
    coordinator who named one.
    """
    raw = nc.get("command")
    if not (isinstance(raw, str) and raw.strip()):
        return None, ("negative_control.command (the criterion-bound proof command, as a string) is "
                      "REQUIRED to execute the control — without it there is nothing to turn RED")
    try:
        argv = shlex.split(raw)
    except ValueError as err:
        return None, f"negative_control.command is not parseable as a command line ({err})"
    if not argv:
        return None, "negative_control.command is empty after parsing"
    line = shlex.join(argv)

    if override is None:
        return None, (
            "--execute-nc requires --nc-command: the criterion-bound proof command must come from "
            "the coordinator, out of band, exactly as --contract-source does. The manifest nominates "
            f"{line!r} — and the manifest is written by the graded worker, as is the `commands[]` "
            "ledger, so neither can authorise the other; fail-closed (#279)")
    try:
        want = shlex.split(override)
    except ValueError as err:
        return None, f"--nc-command is not parseable as a command line ({err})"
    if not want:
        return None, "--nc-command is empty after parsing"
    if shlex.join(want) != line:
        return None, (f"negative_control.command {line!r} is not the command the coordinator "
                      f"supplied out of band ({shlex.join(want)!r}) — a unit does not get to "
                      "choose what proves it; fail-closed")
    return want, None


def _fresh_command_records(m):
    """`commands[]` records with exit 0 whose wtree is head_sha's tree. Returns (records, err).

    Same freshness rule as `check_commands`; kept in one place so the ledger the NC
    replay binds to and the ledger the gate checks can never drift apart.
    """
    head = m.get("head_sha")
    if not head:
        return [], "commands ledger: head_sha is missing, so no record can be bound to content"
    code, want = _git(["rev-parse", f"{head}^{{tree}}"])
    if code != 0 or not want:
        return [], ("commands ledger: cannot resolve the tree of head_sha — the recorded run cannot "
                    "be bound to content; fail-closed")
    records = [c for c in (m.get("commands") or []) if isinstance(c, dict)]
    return [c for c in records if c.get("exit") == 0 and c.get("wtree") == want], None


def _load_diff_scope():
    """diff_scope.py, loaded the way _load_ed25519 loads its sibling. It owns the repo's one
    definition of what a test path is (SCOPE_TESTS), and the control-binding checks below need
    exactly that definition — a second copy here would drift from the lens gate's copy."""
    spec = importlib.util.spec_from_file_location(
        "diff_scope", Path(__file__).resolve().parent / "diff_scope.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _is_test_path(path):
    """True when diff_scope classifies `path` as SCOPE_TESTS on its path alone. Content rules are
    deliberately not consulted: the file may not exist at the tree we are asking about."""
    try:
        ds = _load_diff_scope()
    except Exception:  # noqa: BLE001 - a missing/unloadable sibling must not open the gate
        return None
    low = str(path).lower()
    for flag, pattern in ds.PATH_RULES:
        if flag == "TESTS" and pattern.search(low):
            return True
    return False


def _changed_paths(base, head):
    """Paths changed in base..head, split into (production, tests, err).

    This is the denominator the control must live inside. `negative_control.paths` naming anything
    outside it is a DECOY: the control reverts a file the unit never touched, the bound command goes
    RED for a reason unrelated to the change, and the gate reads that as a kill. Lipsitch et al.
    2010 call this a violation of U-comparability — the control differs from head in more than the
    causal variable under test (docs/reviews/2026-09-11 §4 A13; #280)."""
    if not (base and head and HEX40_RE.match(str(base)) and HEX40_RE.match(str(head))):
        return None, None, ("the control cannot be bound to the change without pinned 40-hex "
                            "base_sha and head_sha")
    code, out = _git(["diff", "--name-only", f"{base}..{head}"])
    if code != 0:
        return None, None, ("cannot diff base_sha..head_sha to bind the control to the change; "
                            "fail-closed")
    changed = [ln.strip() for ln in out.splitlines() if ln.strip()]
    prod, tests = [], []
    for path in changed:
        verdict = _is_test_path(path)
        if verdict is None:
            return None, None, ("diff_scope.py could not be loaded, so a test path cannot be told "
                                "from a production one; fail-closed")
        (tests if verdict else prod).append(path)
    return prod, tests, None


def _bind_paths_to_change(paths, m, what):
    """Every path the control touches must be a PRODUCTION path this unit actually changed.
    Returns an error string or None."""
    prod, _tests, err = _changed_paths(m.get("base_sha"), m.get("head_sha"))
    if err:
        return err
    prod_set = set(prod)
    for path in paths:
        norm = path.lstrip("./")
        if norm in prod_set:
            continue
        verdict = _is_test_path(norm)
        if verdict:
            return (f"{what} names {path!r}, which is a TEST path. Reverting the test that encodes "
                    "the criterion makes the proof go RED because the oracle is gone, not because "
                    "the behaviour came back — the control must revert the BEHAVIOUR (#280)")
        return (f"{what} names {path!r}, which base_sha..head_sha does not change. A control that "
                "reverts a file this unit never touched is a decoy: its RED says nothing about the "
                f"change being proved. Production paths changed here: {sorted(prod_set) or 'none'} "
                "(#280)")
    return None


def _diff_target_paths(diff):
    """Repo-relative paths a unified diff writes to, read from its `+++ b/...` headers."""
    paths = []
    for line in diff.splitlines():
        if not line.startswith("+++ "):
            continue
        target = line[4:].strip().split("\t")[0]
        if target == "/dev/null":
            continue
        if target.startswith(("a/", "b/")):
            target = target[2:]
        if target:
            paths.append(target)
    return paths


# A control run that dies before the oracle ever executes is a STILLBORN MUTANT, not a kill: the
# non-zero exit is the module failing to load, so it would be non-zero for any command at all.
# Vera-Pérez et al. 2018 and Niedermayr et al. 2016 are explicit that only a mutant the test suite
# actually EXERCISES says anything about that suite (docs/reviews/2026-09-11 §4 A14; #280).
STILLBORN_MARKERS = (
    "importerror", "modulenotfounderror", "syntaxerror", "indentationerror",
    "cannot import name", "error collecting", "collection error", "unable to import",
    "no module named", "failed to load", "conftest.py", "attributeerror: module",
)
# What a real oracle failing looks like, across the runners the catalog's missions actually drive.
ASSERTION_MARKERS = (
    "assertionerror", "assert", "failed", "fail:", "failures=", "expected", "not ok",
    "panicked at", "✗", "test failed", "e   ", "✕",
)
# Evidence an assertion was actually EVALUATED and FAILED, as opposed to a runner summarising that
# something went wrong, or a traceback merely QUOTING a line of source. Only these override a
# stillborn marker, and each is anchored to the start of a line for that reason: a collection
# traceback echoes the source it was reading ("    assert helper() == 1") while the assertion
# never ran, so an unanchored "assert " let a stillborn mutant through (PR #308 review, round 3).
# `AssertionError` at the head of a line is an exception that was RAISED; a failed import cannot
# produce one. pytest prefixes the failing assertion with `E`, and never the source it quotes.
STRONG_ASSERTION_RE = re.compile(
    r"^[ \t]*(?:e[ \t]+)?assertionerror\b"      # AssertionError raised (pytest prefixes E)
    r"|^[ \t]*e[ \t]+assert\b"                   # pytest's failing assertion line
    r"|^[ \t]*thread .*panicked at"               # Rust
    r"|✗|✕",
    re.M,
)
# unittest and pytest both distinguish an ERROR (an exception escaped) from a FAILURE (an assertion
# was evaluated and was false). Only the second exercises the oracle. `FAILED (errors=1)` is an
# import blowing up, and it says "FAILED" — which is why the assertion markers alone cannot be
# trusted to mean an assertion ran (PR #308 review).
_ERRORS_RE = re.compile(r"\berrors?\s*[=:]\s*(\d+)|\b(\d+)\s+errors?\b")
_FAILURES_RE = re.compile(r"\bfailures?\s*[=:]\s*(\d+)|\b(\d+)\s+failed\b")


def _counted(pattern, text):
    """Sum of every count `pattern` reports in a runner's summary line. None when it reports none."""
    total, seen = 0, False
    for match in pattern.finditer(text):
        for group in match.groups():
            if group is not None:
                total += int(group)
                seen = True
    return total if seen else None


def _failure_signature(out, err):
    """Read the control run's output. Returns (ok, reason).

    A non-zero exit is not a kill on its own — `grep` exits 1 on no-match, an unimportable module
    exits 1 before a single assertion runs, and both look identical to a gate that only reads the
    return code. The RED must LOOK like an oracle failing.

    Three layers, in this order, because two review rounds on #308 showed either one alone is
    wrong. The RUNNER'S OWN SUMMARY is the best evidence there is: unittest and pytest already
    separate errors from failures, so `FAILED (errors=1)` is a stillborn mutant no matter what
    words surround it. Only when no summary exists — a plain script, say — does the substring scan
    matter, and even then explicit assertion evidence outranks it: a test asserting that a
    `ModuleNotFoundError` is raised prints that name while its oracle runs perfectly well. That
    evidence is line-anchored, because a collection traceback QUOTES the source it was reading —
    an `assert` in echoed source is not an assertion that ran."""
    text = f"{out}\n{err}".lower()
    if not text.strip():
        return False, ("the control run produced NO output at all. A silent non-zero exit is not a "
                       "failing test — it is what `grep` does when it finds nothing; fail-closed "
                       "(#280)")
    errors = _counted(_ERRORS_RE, text)
    failures = _counted(_FAILURES_RE, text)
    if errors and not failures:
        return False, (f"the runner reports {errors} error(s) and no assertion failure — an error is "
                       "an exception escaping, not an oracle evaluating to false, so it does not "
                       "show the criterion-bound assertion ran at all; fail-closed (#280)")
    if not failures:
        # No runner summary to trust, so read the text. A stillborn mutant refuses unless the
        # output carries evidence an assertion was really evaluated.
        stillborn = [mark for mark in STILLBORN_MARKERS if mark in text]
        if stillborn and not STRONG_ASSERTION_RE.search(text):
            return False, (f"the control run did not get as far as an oracle ({stillborn[0]!r} in "
                           "its output, and nothing showing an assertion was evaluated) — that is "
                           "a STILLBORN MUTANT, not a kill. The non-zero exit is the module failing "
                           "to load, which would happen for any command; the control must leave the "
                           "code runnable and fail an ASSERTION (#280)")
    if not any(mark in text for mark in ASSERTION_MARKERS):
        return False, ("the control run exited non-zero but its output names no assertion failure, "
                       "so nothing shows the criterion-bound oracle actually ran and failed; "
                       "fail-closed (#280)")
    return True, None


def _hunk_lines(text, side):
    """{path: head-side line numbers the diff's hunks touch}, reading `side` ('-' or '+').

    For a mutant applied AT head_sha the `-` side carries head's own line numbers — the lines the
    mutant replaces. For `git diff base..head` the `+` side carries them. Both land in head
    coordinates, which is what makes the two comparable."""
    want = re.compile(r"@@\s*-(\d+)(?:,(\d+))?\s+\+(\d+)(?:,(\d+))?\s*@@")
    out, current = {}, None
    for line in text.splitlines():
        if line.startswith("+++ "):
            target = line[4:].strip().split("\t")[0]
            if target == "/dev/null":
                current = None
                continue
            if target.startswith(("a/", "b/")):
                target = target[2:]
            current = target or None
            if current:
                out.setdefault(current, set())
        elif line.startswith("@@") and current:
            match = want.search(line)
            if not match:
                continue
            groups = match.groups()
            start, count = (groups[0], groups[1]) if side == "-" else (groups[2], groups[3])
            start = int(start)
            count = 1 if count is None else int(count)
            # A pure insertion/deletion spans no lines on its own side; bind it to the seam it
            # sits at, so it still has to land where the unit worked.
            out[current].update(range(start, start + count) if count else (start, start + 1))
    return out


def _bind_hunks_to_change(diff, m):
    """A `hand` mutant must touch the lines this unit changed, not merely the same FILE.

    Binding by path alone left a decoy one level down: a production file can carry the criterion
    change AND an unrelated change, and a mutant that only touches the unrelated hunk still goes
    RED under a broad test command while the criterion behaviour stands untouched (PR #308 review).
    """
    base, head = m.get("base_sha"), m.get("head_sha")
    if not (base and head and HEX40_RE.match(str(base)) and HEX40_RE.match(str(head))):
        return "the hand mutant cannot be bound to the change without pinned base_sha and head_sha"
    for path, lines in _hunk_lines(diff, "-").items():
        code, out = _git(["diff", "-U0", f"{base}..{head}", "--", path])
        if code != 0:
            return (f"cannot diff {path} over base_sha..head_sha to bind the hand mutant to the "
                    "change; fail-closed")
        changed = set().union(*_hunk_lines(f"+++ {path}\n{out}", "+").values() or [set()])
        if not lines:
            return (f"the hand mutant's diff names {path} but carries no hunk for it, so nothing "
                    "says which behaviour it mutates (#280)")
        if not lines & changed:
            return (f"the hand mutant touches {path} at line(s) {sorted(lines)[:6]}, and "
                    f"base_sha..head_sha changes line(s) {sorted(changed)[:6] or 'none'} there — "
                    "they do not overlap. Mutating an untouched hunk of a changed file is the same "
                    "decoy as mutating an untouched file: the RED comes from behaviour this unit "
                    "did not introduce (#280)")
    return None


def _nc_paths(nc):
    """`negative_control.paths` — the production paths the revert control restores to base_sha.
    Repo-relative, inside the toplevel, never option-like. Returns (paths, err)."""
    raw = nc.get("paths")
    if raw is None:
        return None, None
    if not (isinstance(raw, list) and raw and all(isinstance(x, str) and x for x in raw)):
        return None, "negative_control.paths must be a non-empty list of repo-relative path strings"
    for path in raw:
        if path.startswith("-"):
            return None, f"refusing option-like path in negative_control.paths: {path}"
        _, err = _resolve(path)
        if err:
            return None, f"negative_control.paths: {err}"
    return raw, None


def _extract_diff(text):
    """Pull the unified diff out of a `hand` NC artifact. The diff runs from the first `diff --git`
    or `--- ` header through the last line that still looks like diff body; trailing prose (the
    test output that shows the RED) is dropped."""
    lines = text.splitlines()
    start = next((i for i, ln in enumerate(lines)
                  if ln.startswith("diff --git ") or ln.startswith("--- ")), None)
    if start is None:
        return None
    end = start
    for i in range(start, len(lines)):
        ln = lines[i]
        if (ln.startswith(("diff --git ", "index ", "--- ", "+++ ", "@@", "+", "-", " ",
                           "new file mode", "deleted file mode", "similarity index",
                           "rename from", "rename to", "old mode", "new mode"))
                or ln == ""):
            end = i
        else:
            break
    body = "\n".join(lines[start:end + 1]).rstrip("\n")
    return (body + "\n") if body.strip() else None


def _apply_control(wt, m, nc, tool):
    """Apply the negative control inside the throwaway worktree `wt`. Returns an error string or
    None. Fail-closed on every git error: a control that did not apply is not a control."""
    if tool == "revert":
        base = m.get("base_sha")
        paths, err = _nc_paths(nc)
        if err:
            return err
        if paths:
            if not (base and HEX40_RE.match(str(base))):
                return ("negative_control.paths needs a pinned 40-hex base_sha to restore the "
                        "pre-fix content from")
            bind_err = _bind_paths_to_change(paths, m, "negative_control.paths")
            if bind_err:
                return bind_err
            code, _, gerr = _run_at(wt, ["git", "checkout", str(base), "--", *paths])
            if code != 0:
                return f"could not restore {paths} from base_sha in the control worktree: {gerr.strip()}"
            return None
        # No paths: the ONLY sound fallback is reverting the whole linear base..head range.
        head = m.get("head_sha")
        if not (base and head and HEX40_RE.match(str(base)) and HEX40_RE.match(str(head))):
            return ("negative_control.paths is required for tool 'revert' (the range fallback needs "
                    "pinned base_sha and head_sha)")
        if _run_at(wt, ["git", "merge-base", "--is-ancestor", str(base), str(head)])[0] != 0:
            return ("negative_control.paths is required: base_sha..head_sha is not linear "
                    "(base is not an ancestor of head), so a range revert is not well-defined")
        code, merges, _ = _run_at(wt, ["git", "rev-list", "--merges", f"{base}..{head}"])
        if code != 0 or merges.strip():
            return ("negative_control.paths is required: base_sha..head_sha contains merge commits, "
                    "so a range revert is not well-defined")
        # A range revert takes the TESTS with it. When the unit adds a test module, reverting the
        # range deletes it, and the bound command then fails because the test file is gone — a
        # missing oracle reads as a kill. Refuse, and make the unit name its production paths
        # (docs/reviews/2026-09-11 §4 A14b/A21; #280).
        _prod, tests, bind_err = _changed_paths(base, head)
        if bind_err:
            return bind_err
        if tests:
            return ("negative_control.paths is REQUIRED here: base_sha..head_sha changes test "
                    f"paths ({sorted(tests)}), and a range revert would remove them along with the "
                    "fix. The bound command would then go RED because its oracle is gone, not "
                    "because the behaviour came back. Name the production paths the control should "
                    "restore (#280)")
        code, _, gerr = _run_at(wt, ["git", "revert", "--no-commit", f"{base}..{head}"], timeout=60)
        if code != 0:
            return f"git revert of base_sha..head_sha failed in the control worktree: {gerr.strip()}"
        return None
    # tool == "hand": the mutant IS the diff quoted in the artifact — apply exactly that.
    raw, err = read_artifact(m, nc.get("artifact"))
    if err:
        return f"negative_control.artifact unreadable, so the hand mutant cannot be applied: {err}"
    diff = _extract_diff(raw.decode("utf-8", "replace"))
    if not diff:
        return "negative_control.artifact for tool 'hand' quotes no applicable unified diff"
    targets = _diff_target_paths(diff)
    if not targets:
        return ("negative_control.artifact for tool 'hand' quotes a diff with no `+++` target — "
                "nothing identifies which file the mutant touches, so it cannot be bound to the "
                "change (#280)")
    bind_err = _bind_paths_to_change(targets, m, "the hand mutant's diff")
    if bind_err:
        return bind_err
    bind_err = _bind_hunks_to_change(diff, m)
    if bind_err:
        return bind_err
    code, _, gerr = _run_at(wt, ["git", "apply", "--whitespace=nowarn", "-"],
                            stdin_bytes=diff.encode("utf-8"))
    if code != 0:
        return ("the hand mutant quoted in negative_control.artifact does not apply at head_sha "
                f"({gerr.strip()}) — the quoted diff is not the diff that was run")
    return None


def execute_negative_control(m, nc_command=None):
    """#255 — EXECUTE the negative control. Returns (executed_ok, messages).

    The proof, not the paperwork: in a throwaway worktree detached at `head_sha` the control is
    APPLIED (`revert`: restore `negative_control.paths` from base_sha — or, only when no paths are
    given and the range is linear, `git revert --no-commit base..head`; `hand`: `git apply` the
    unified diff quoted in the artifact) and `negative_control.command` must exit NON-ZERO. Then
    the SAME command must exit ZERO in a second, clean worktree at `head_sha`. Both halves are
    required: a command that fails under the control but also fails clean proves nothing, and a
    command that passes under the control is a TAUTOLOGY — the proof does not go RED.

    Fail-closed everywhere: an unknown tool, a missing command/paths, a git error, a worktree that
    cannot be made, or a control that applies no change at all."""
    nc = m.get("negative_control") or {}
    tool = nc.get("tool")
    if tool not in EXECUTABLE_NC_TOOLS:
        return False, [f"--execute-nc: no replay is implemented for negative_control.tool {tool!r} "
                       f"— only {list(EXECUTABLE_NC_TOOLS)} can be re-executed here; fail-closed "
                       "(#255)"]
    head = m.get("head_sha")
    if not (head and HEX40_RE.match(str(head))):
        return False, ["--execute-nc: head_sha must be a pinned 40-hex commit to check out a "
                       "control worktree"]
    top = _toplevel()
    if top is None:
        return False, ["--execute-nc: not inside a git repo — cannot create a control worktree"]
    if _git(["cat-file", "-e", f"{head}^{{commit}}"])[0] != 0:
        return False, [f"--execute-nc: head_sha '{head}' is not a real commit here"]
    argv, err = _nc_command(nc, nc_command)
    if err:
        return False, [f"--execute-nc: {err}"]
    msgs = []
    for phase in ("control", "clean"):
        holder = tempfile.mkdtemp(prefix="orca-nc-")
        wt = str(Path(holder) / "wt")
        code, _, gerr = _run(["git", "-C", top, "worktree", "add", "--detach", wt, str(head)],
                             timeout=120)
        try:
            if code != 0:
                return False, [f"--execute-nc: could not create the {phase} worktree at head_sha: "
                               f"{gerr.strip()}"]
            if phase == "control":
                apply_err = _apply_control(wt, m, nc, tool)
                if apply_err:
                    return False, [f"--execute-nc: {apply_err}"]
                if not _run_at(wt, ["git", "status", "--porcelain"])[1].strip():
                    return False, ["--execute-nc: the negative control changed NOTHING at head_sha "
                                   "— a no-op mutant cannot make any proof go RED (#255)"]
            rc, out, errout = _run_at(wt, argv, timeout=NC_TIMEOUT_S)
            tail = (errout.strip() or out.strip())[-300:]
            if phase == "control":
                sig_ok, sig_err = _failure_signature(out, errout)
        finally:
            _run(["git", "-C", top, "worktree", "remove", "--force", wt], timeout=60)
            shutil.rmtree(holder, ignore_errors=True)
        if phase == "control":
            if rc == 124:
                return False, [f"--execute-nc: the bound command did not complete under the control "
                               f"({NC_TIMEOUT_S}s timeout / exec error): {tail}"]
            if rc == 0:
                return False, ["--execute-nc: TAUTOLOGICAL — the proof does NOT go RED. The control "
                               f"was applied at head_sha and `{shlex.join(argv)}` still exited 0, so "
                               "the command does not bind to the change it claims to prove (#255)"]
            if not sig_ok:
                return False, [f"--execute-nc: {sig_err} Output was: {tail}"]
            msgs.append(f"NOTE: negative control EXECUTED — with the {tool} control applied at "
                        f"head_sha the bound command exited {rc} on an assertion failure (RED, as "
                        "required)")
        else:
            if rc != 0:
                return False, [f"--execute-nc: the bound command exits {rc} at CLEAN head_sha too, "
                               "so its RED under the control is not evidence of anything: "
                               f"{tail}"]
            msgs.append("NOTE: the same command exits 0 at clean head_sha — the RED above is the "
                        "control's doing, not a broken suite")
    return True, msgs


def check_negative_control(m, is_mutation, execute=False, nc_command=None):
    """4. Structured NC AND the artifact must corroborate the pinned mutant being killed. Reading the
    artifact resolves the mutant + verdict; it is corroboration, not proof (a fabricated artifact can
    still be read). Under `execute` the control is additionally RE-EXECUTED (execute_negative_control)
    — that is the only leg that turns the manifest's claim into a fact.

    Returns (errs, executed_ok). `executed_ok` is what the review-waiver lanes require (#256)."""
    if not is_mutation:
        return [], False
    nc = m.get("negative_control") or {}
    errs = []
    tool = nc.get("tool")
    if tool not in NC_TOOLS:
        errs.append(f"negative_control.tool must be one of {sorted(NC_TOOLS)}, got {tool!r}")
    if not re.search(r"(?i)\b(killed|red)\b", nc.get("result") or ""):
        errs.append("negative_control.result must record the mutant KILLED / the proof going RED")
    mutant = nc.get("mutant")
    if tool and tool not in ("revert", "hand") and not mutant:
        errs.append("negative_control.mutant (a pinned mutant id) is required for a mutation tool")
    artifact = nc.get("artifact")
    if not artifact:
        errs.append("negative_control.artifact (an evidence path) is required")
        return errs, False
    content, err = read_artifact(m, artifact)
    if err:
        errs.append(f"negative_control.artifact unreadable ({artifact}): {err}")
        return errs, False
    content = content.decode("utf-8", "replace")
    if not re.search(r"(?i)\b(killed|red|fail)\b", content):
        errs.append("negative_control.artifact does not evidence a killed/RED outcome")
    if _NC_ZERO_KILL_RE.search(content):
        errs.append("negative_control.artifact indicates no mutant was killed (0 killed / 0% killed)")
    # the pinned mutant must not be reported as surviving — scoped to the mutant id and tolerant of
    # delimiters (`m7: Survived: 1`, `m7 - survived - 0`), but a zero count is a KILL. The lookahead
    # excludes `<>` so a comparison like `survived > 0` is NOT read as a zero count (it is a survivor).
    surv = r"survived\b(?![\s:=-]*0\b)"
    if re.search(rf"(?i)\bmutant\s+{surv}", content) or (
            mutant and re.search(rf"(?i)\b{re.escape(mutant)}\b[\s:=<>-]*(?:has\s+|was\s+)?{surv}", content)):
        errs.append("negative_control.artifact reports the pinned mutant SURVIVED / was not killed")
    if mutant and mutant not in content:
        errs.append("negative_control.artifact does not reference the pinned mutant")
    if tool == "hand":
        # `hand` is exempt from a pinned mutant id, so the diff it applied is the ONLY thing binding
        # the RED to a mutation — the artifact must quote it (evidence-manifest §1).
        has_diff = re.search(r"(?m)^(diff --git|@@ )", content) or (
            re.search(r"(?m)^-[^-]", content) and re.search(r"(?m)^\+[^+]", content))
        if not has_diff:
            errs.append("negative_control.artifact for tool 'hand' must quote the hand-written diff")
    # Binding the control's paths to the change is a STATIC check — the declared paths against
    # base_sha..head_sha — so it belongs here, on every mutation unit, not only on the executed
    # leg. It lived solely in _apply_control, which meant a NARRATED manifest could nominate a
    # decoy path, or revert the test that encodes the criterion, and nothing looked (#306).
    #
    # Executed, those two are caught anyway: reverting a file the change never touched is a no-op
    # and #255 refuses it. That is why the gap survived #280 — the executed lane covered for the
    # narrated one, and no trap sampled the narrated lane until now.
    if tool == "revert":
        declared, perr = _nc_paths(nc)
        if perr:
            errs.append(perr)
        elif declared:
            bind_err = _bind_paths_to_change(declared, m, "negative_control.paths")
            if bind_err:
                errs.append(bind_err)
    executed_ok = False
    if execute:
        executed_ok, msgs = execute_negative_control(m, nc_command)
        errs.extend(msgs)
    return errs, executed_ok


def check_commands(m, is_mutation):
    """5. The CONTENT-BOUND evidence ledger (audit §3 item 3; gstack `bin/gstack-evidence`).

    "Tests pass at that exact SHA in a clean env" was doctrine — a sentence in evidence-manifest §2
    addressed to the coordinator, with no field any verifier read. `evidence-run.py` records
    `{cmd, cmd_sha256, exit, duration_s, commit, wtree, artifact}` for every command it wraps, and
    this check requires at least ONE record with `exit == 0` whose `wtree` equals
    `git rev-parse <head_sha>^{tree}` — the content actually committed at the head. A record made on
    other content (an earlier tree, a dirty tree with extra files) is STALE and does not count.

    FAIL-CLOSED, unlike upstream's advisory `check`: no record means nothing proved the suite ran on
    this content. The NOTE says what the pass does NOT mean — the coordinator's clean-env re-run is
    still the stronger authority, because this record was written by the worker's own runner."""
    if not is_mutation:
        return []
    head = m.get("head_sha")
    if not head:
        return []  # check_shas_present already fails this manifest
    code, want = _git(["rev-parse", f"{head}^{{tree}}"])
    if code != 0 or not want:
        return ["commands ledger: cannot resolve the tree of head_sha (not a real commit here, or "
                "not inside a git repo) — the recorded run cannot be bound to content; fail-closed"]
    records = [c for c in (m.get("commands") or []) if isinstance(c, dict)]
    if not records:
        return ["commands ledger: no recorded command (mutation unit). Wrap the criterion-bound "
                "run in `runtime/scripts/evidence-run.py --label <L> --manifest <m.json> -- <cmd>` "
                "so the manifest carries an exit code bound to a content fingerprint; fail-closed"]
    # A record whose cmd_sha256 does not hash its own cmd describes nothing, so it binds nothing:
    # a decorative digest would let the line be edited after the run. Checked here rather than at
    # the point of use, because since #279 the replay no longer draws its command from this ledger
    # and the integrity of the ledger is still worth asserting.
    for rec in records:
        line = rec.get("cmd")
        digest = rec.get("cmd_sha256")
        if not (isinstance(line, str) and isinstance(digest, str)):
            continue
        actual = hashlib.sha256(line.encode("utf-8")).hexdigest()
        if digest != actual:
            return [f"commands ledger: record for {line!r} carries cmd_sha256 {digest} but the "
                    f"command line hashes to {actual} — the record does not describe its own "
                    "command, so it binds nothing; fail-closed"]
    fresh, _ = _fresh_command_records(m)
    if not fresh:
        seen = sorted({str(c.get("wtree")) for c in records if c.get("exit") == 0})
        return [f"commands ledger: no recorded command with exit 0 whose wtree is head_sha's tree "
                f"{want} (exit-0 records carry {seen or 'no wtree at all'}) — the recorded run was "
                "made on other content, so it is STALE evidence for this head; fail-closed"]
    return [f"NOTE: commands ledger FRESH — {len(fresh)} exit-0 record(s) bound to head_sha's tree "
            f"{want[:12]}. This is the worker's own runner, so the coordinator's clean-env re-run at "
            "head_sha still stands as the stronger authority (evidence-manifest.md §2)"]


def _gitleaks_scan(path):
    """Scan one file with gitleaks when it is installed. Returns True (hit) / False (clean) / None
    (gitleaks unusable — the caller falls back to the built-in patterns)."""
    if shutil.which("gitleaks") is None:
        return None
    code, _, _ = _run(["gitleaks", "detect", "--no-git", "--no-banner", "--redact",
                       "--source", str(path)], timeout=120)
    if code == 0:
        return False
    if code == 1:
        return True
    return None


def _scan_text(text):
    return sorted({name for name, rx in REDACTION_PATTERNS if rx.search(text)})


def check_redaction(m, manifest_path):
    """6. Redaction (audit §3 item 14). A manifest is SHA-pinned and permanent, and so is anything
    quoted into it or into an artifact it names. Scan the manifest JSON and every named artifact
    (the negative control's, the reviewer record, and the `artifacts[]` inventory) for credential
    shapes. gitleaks decides when it is on PATH; otherwise REDACTION_PATTERNS is the floor. A hit
    FAILS the unit — rotate the credential, scrub the evidence, re-emit."""
    errs = []
    targets = []
    if manifest_path:
        targets.append(("manifest", Path(manifest_path)))
    named = []
    for path in ((m.get("negative_control") or {}).get("artifact"),
                 (m.get("review") or {}).get("artifact")):
        if isinstance(path, str) and path:
            named.append(path)
    for entry in (m.get("artifacts") or []):
        path = entry.get("path") if isinstance(entry, dict) else entry
        if isinstance(path, str) and path:
            named.append(path)
    for path in dict.fromkeys(named):
        resolved, err = _resolve(path) if "@" not in path else (None, "path@ref")
        if err is None and resolved is not None and resolved.is_file():
            targets.append((f"artifact {path}", resolved))
    for label, path in targets:
        hit = _gitleaks_scan(path)
        if hit is False:
            continue
        try:
            kinds = _scan_text(path.read_text(encoding="utf-8", errors="replace"))
        except OSError:
            continue
        if hit is True and not kinds:
            kinds = ["gitleaks-rule"]
        if kinds:
            errs.append(f"redaction: credential shape(s) {kinds} found in {label} — evidence is "
                        "SHA-pinned and permanent; rotate the credential and re-emit the unit")
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


def check_intent(m, is_mutation):
    """7. Mutation units carry a non-empty intent packet (goal · ruled_out · why) — presence only;
    wisdom is a human/taste check (evidence-manifest.md §1)."""
    if not is_mutation:
        return []
    intent = m.get("intent")
    if not isinstance(intent, dict):
        intent = {}
    missing = [k for k in ("goal", "ruled_out", "why")
               if not (isinstance(intent.get(k), str) and intent.get(k).strip())]
    return [f"intent packet incomplete — non-empty {missing} required (mutation unit)"] if missing else []


def check_lighting(m, is_mutation, dispatch_lighting=None):
    """8. Lighting is a legal value when present; omission defaults to lit — "Recording nothing
    means lit" (gate-classification.md). dark-eligibility's stop-list is a human gate; verify.py
    machine-checks that the value is legal and, when the dispatch supplied a lighting, that the
    worker's manifest did not swap it (the dispatch value is authoritative for the review waiver
    in check_review). Omission being lit means a dark-eligible dispatch + omitted manifest
    lighting is a swap."""
    if not is_mutation:
        return []
    lighting = m.get("lighting", "lit")  # omission means lit (gate-classification.md); an
    # explicit null is a present value, not omission, and fails the legality check below
    if not (isinstance(lighting, str) and lighting in LIGHTING_VALUES):
        return [f"lighting must be one of {sorted(LIGHTING_VALUES)}, got {lighting!r}"]
    if dispatch_lighting is not None and lighting != dispatch_lighting:
        return [f"lighting swap: manifest says {lighting!r} but dispatch classed the unit "
                f"{dispatch_lighting!r} (the dispatch value is authoritative)"]
    return []


def check_reviewer_mode(m, is_mutation):
    """9. reviewer_mode is recorded and legal — how independent the review was. The strongest
    independence signal is the APPROVED GitHub review (check_review); this records the qualifier."""
    if not is_mutation:
        return []
    mode = m.get("reviewer_mode")
    if not (isinstance(mode, str) and mode in REVIEWER_MODES):
        return [f"reviewer_mode must be one of {sorted(REVIEWER_MODES)}, got {mode!r}"]
    return []


def check_provenance(m):
    """10. EU AI Act Art-12/50: a manifest that CLAIMS a regulated standard must carry the provenance
    fields that make it an audit record. Presence-only (not deep validation), but an incomplete packet
    claiming a standard is not a valid audit record — fail it rather than accept incomplete evidence."""
    prov = m.get("provenance")
    if not isinstance(prov, dict):
        return []
    standard = prov.get("standard")
    if not (isinstance(standard, str) and standard.strip() and standard.strip().lower() != "none"):
        return []
    missing = [k for k in ("spec_version", "model", "reviewer", "retention")
               if not (isinstance(prov.get(k), str) and prov.get(k).strip())]
    return [f"provenance claims standard {standard!r} but is missing audit fields {missing} "
            "(EU AI Act Art-12/50 record incomplete)"] if missing else []


_DISPATCH_FIELDS = ("manifest_id", "contract_digest", "unit_class", "lighting")


def _load_ed25519():
    spec = importlib.util.spec_from_file_location("ed25519", Path(__file__).resolve().parent / "ed25519.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _canonical_dispatch(record):
    """Must match dispatch-sign.py.canonical_record byte-for-byte (a cross-tool test guards this)."""
    subset = {k: record[k] for k in _DISPATCH_FIELDS if record.get(k) is not None}
    return json.dumps(subset, sort_keys=True, separators=(",", ":")).encode("utf-8")


def check_dispatch_provenance(m, contract_digest, unit_class, lighting, record_ref, pubkey_ref):
    """11. #135: verify a coordinator-signed dispatch record so a run's contract_digest / unit_class /
    lighting can be checked against what the coordinator actually authorized. This is a SOUNDNESS
    boundary only when the *verifying key* is trusted — i.e. supplied by an OFF-WORKER context
    (CI/MCP/SDK, or an auditor re-running verify.py with the coordinator's real public key). In the
    native in-session hook the worker controls the key source, so there it is defense-in-depth, not a
    boundary (verify-gate.sh keeps that lane ADVISORY; the durable value is off-worker detection).
      - neither record nor pubkey -> [] (nothing to check).
      - only one of them -> fail-closed (cannot verify).
      - bad signature, an id that names another unit, or a used field the record did not sign / signed
        differently -> fatal (substitution / replay caught).
      - all good -> NOTE (signature verified against the SUPPLIED key)."""
    if not record_ref and not pubkey_ref:
        return []
    if bool(record_ref) != bool(pubkey_ref):
        missing = "--dispatch-record" if pubkey_ref else "--dispatch-pubkey"
        return [f"dispatch provenance half-configured (missing {missing}) — cannot verify; fail-closed (#135)"]
    try:
        ed = _load_ed25519()
    except Exception as exc:
        return [f"dispatch provenance requested but the Ed25519 verifier is unavailable ({exc}) — fail-closed"]
    rec_text, err = read_source(record_ref)
    if err:
        return [f"dispatch record unreadable ({record_ref}): {err}"]
    pub_text, err = read_source(pubkey_ref)
    if err:
        return [f"dispatch pubkey unreadable ({pubkey_ref}): {err}"]
    try:
        envelope = json.loads(rec_text.decode("utf-8"))
        record = envelope["record"]
        sig = base64.b64decode(envelope["sig_b64"])
        pub = bytes.fromhex(pub_text.decode("utf-8").strip())
    except (ValueError, KeyError, TypeError) as exc:
        return [f"dispatch record / pubkey malformed ({exc})"]
    if not ed.checkvalid(sig, _canonical_dispatch(record), pub):
        return ["dispatch record signature INVALID for the supplied pubkey — not signed by that key "
                "(forged or wrong key); fail-closed (#135)"]
    signed_id = record.get("manifest_id")
    manifest_id = m.get("unit")
    if not signed_id or not manifest_id or signed_id != manifest_id:
        return [f"dispatch record identity {signed_id!r} does not bind this manifest {manifest_id!r} "
                "— a record must name the unit it authorizes, else another unit's record replays (#135)"]
    # Every value the run actually used must be signed AND match — an UNSIGNED field is unbound, so a
    # worker could set it freely; treat that as fail-closed, not a pass.
    for field, used in (("contract_digest", contract_digest), ("unit_class", unit_class),
                        ("lighting", lighting)):
        if used is None:
            continue
        signed = record.get(field)
        if signed is None:
            return [f"dispatch record did not sign {field} but the run uses it — unbound value, "
                    "fail-closed (the coordinator must sign every field the gate enforces) (#135)"]
        if signed != used:
            return [f"dispatch substitution: the run used {field}={used!r} but the coordinator signed "
                    f"{signed!r} — the value was tampered (#135)"]
    return ["NOTE: dispatch record signature verified against the supplied key (#135) — a soundness "
            "boundary only if that key is trusted (off-worker: CI/MCP/SDK or an auditor)"]


def verify(manifest_path, contract_source=None, contract_digest=None, repo=None,
           base=None, symbol=None, execute_nc=False, unit_class=None, no_gh=False, lighting=None,
           dispatch_record=None, dispatch_pubkey=None, nc_command=None):
    """Return (fatal_errors, notes). fatal_errors non-empty => exit 2."""
    m, err = load_manifest(manifest_path)
    if err:
        return None, err
    is_mut = _is_mutation(unit_class)
    corroborated = bool(contract_source and contract_digest)
    fatal, notes = [], []
    if unit_class is not None and unit_class not in UNIT_CLASSES:
        # An unknown class (a typo, or a class this script predates) must not wedge on a usage
        # error: _is_mutation already fails safe to mutation — say so loudly (#178).
        notes.append(f"NOTE: unknown unit class {unit_class!r} — expected one of "
                     f"{sorted(UNIT_CLASSES)}; failing safe to mutation-strict checks (#178)")
    # The negative control runs FIRST of the mutation legs because its EXECUTED verdict is an input
    # to the review check: the dark-eligible / no-gh waiver lanes pass only on an executed control
    # (#256). A malformed manifest must fail closed here too, never crash the gate.
    try:
        nc_errs, nc_executed = check_negative_control(m, is_mut, execute_nc, nc_command)
    except Exception as exc:
        nc_errs, nc_executed = ([f"malformed manifest: {type(exc).__name__} in the negative-control "
                                 f"check ({exc})"], False)
    checks = (
        lambda: check_scope(m, contract_source, contract_digest),
        lambda: check_shas_present(m),
        lambda: check_real_commits(m, is_mut),
        lambda: check_freshness(m),
        lambda: check_review(m, repo, is_mut, no_gh, corroborated, lighting, nc_executed),
        lambda: nc_errs,
        lambda: check_commands(m, is_mut),
        lambda: check_redaction(m, manifest_path),
        lambda: check_intent(m, is_mut),
        lambda: check_lighting(m, is_mut, lighting),
        lambda: check_reviewer_mode(m, is_mut),
        lambda: check_provenance(m),
        lambda: check_dispatch_provenance(m, contract_digest, unit_class, lighting,
                                          dispatch_record, dispatch_pubkey),
        lambda: check_ancestry(m, base),
        lambda: check_symbol_on_base(symbol, base),
    )
    for run_check in checks:
        try:
            result = run_check()
        except Exception as exc:  # a malformed manifest must fail closed, never crash the gate
            result = [f"malformed manifest: {type(exc).__name__} in a verifier check ({exc})"]
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
    ap.add_argument("--nc-command", default=None,
                    help="AUTHORITATIVE criterion-bound command for --execute-nc, supplied out of "
                         "band by the coordinator. REQUIRED by --execute-nc (#279): the manifest "
                         "and the commands ledger are both worker-written, so neither can "
                         "authorise the other. The manifest must agree with this or the run is "
                         "RED. A unit never chooses what proves it.")
    ap.add_argument("--execute-nc", action="store_true",
                    help="EXECUTE the negative control (#255): apply it in a throwaway worktree at "
                         "head_sha, require the bound command to exit non-zero there and 0 at "
                         "clean head_sha. Requires --nc-command (#279). REQUIRED by the "
                         "review-waiver lanes (--lighting dark-eligible / --no-gh), which have no "
                         "other oracle (#256)")
    ap.add_argument("--base", default=None, help="integration base branch (for ancestry)")
    ap.add_argument("--symbol", default=None, help="a unit symbol to grep on the base")
    ap.add_argument("--unit-class", default=None,
                    help="unit class from the dispatch record (mutation|report-only|planning); "
                         "missing/unknown => mutation (fail-safe, with a NOTE) — validated in "
                         "code, not by argparse, so an unknown value cannot wedge the gate (#178)")
    ap.add_argument("--no-gh", action="store_true",
                    help="offline/no-gh lane (merge-serialization.md): review is a local reviewer "
                         "artifact at head_sha, coordinator-attested — set by the coordinator, not the worker")
    ap.add_argument("--lighting", default=None, choices=sorted(LIGHTING_VALUES),
                    help="unit lighting from the dispatch record (lit|dark-eligible); dark-eligible "
                         "waives the independent-review requirement — set by the coordinator, not the worker")
    ap.add_argument("--dispatch-record", default=None,
                    help="coordinator-signed dispatch record (path or path@ref) binding "
                         "contract-digest/unit-class/lighting — makes the native hook path sound (#135)")
    ap.add_argument("--dispatch-pubkey", default=None,
                    help="repo-pinned coordinator public key (path or path@ref) that verifies "
                         "--dispatch-record; a committed pubkey is one the worker cannot swap")
    args = ap.parse_args(argv)

    if shutil.which("git") is None:
        print("dependency: git not on PATH", file=sys.stderr)
        return 1
    out, load_err = verify(args.manifest, args.contract_source, args.contract_digest,
                           args.repo or infer_repo(), args.base, args.symbol, args.execute_nc,
                           args.unit_class, args.no_gh, args.lighting,
                           args.dispatch_record, args.dispatch_pubkey, args.nc_command)
    if load_err:
        print(f"FAIL: {load_err}", file=sys.stderr)
        print("verify: evidence manifest malformed/unreadable — unit is NOT done", file=sys.stderr)
        return 2
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
