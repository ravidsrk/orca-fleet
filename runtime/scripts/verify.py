#!/usr/bin/env python3
"""verify.py — independent, separate-process re-derivation of an evidence manifest.

The completion oracle runs OUTSIDE the producing session and TRUSTS NOTHING IN THE WORKER'S MANIFEST
that it can instead check against authoritative state. The manifest is a *claim*; the authorities are:
  - the COORDINATOR's frozen contract — the criterion denominator materialized at dispatch and passed
    in as --contract-source/--contract-digest, NOT read from the worker's manifest;
  - GIT — commit existence and ancestry;
  - GITHUB — whether a review actually happened at the reviewed SHA (a manifest-set reviewed_sha
    proves nothing);
  - the NEGATIVE-CONTROL artifact; --execute-nc is fail-closed until a replay exists.

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
     proof; --execute-nc fail-closes (evidence-manifest §2's re-execution sample is the sound form).
  5. ancestry (best-effort) · 6. symbol-on-base (best-effort).

Usage:
    verify.py --manifest <m.json> --contract-source <path@ref> --contract-digest <sha256:…>
              [--repo owner/name] [--unit-class mutation|report-only|planning] [--execute-nc]
              [--base <branch>] [--symbol <tok>]
    # exit 0 = all REQUIRED checks pass · 1 = usage/dependency · 2 = a REQUIRED invariant FAILED
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import importlib.util
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
REVIEWER_MODES = {"cross-vendor", "same-vendor-fresh", "instructed-isolation"}
LIGHTING_VALUES = {"lit", "dark-eligible"}
# Criterion ids in a frozen source: hyphenated (AC-1, SC-12, REQ-3) or compact (AC1, SC12). A JSON
# source may instead declare an explicit criterion_ids array, which is unambiguous and preferred.
# Over-counting is fail-safe (the manifest must address MORE); under-counting would let scope shrink.
CRIT_ID_RE = re.compile(r"\b[A-Z][A-Z0-9]*-\d+\b|\b[A-Z]{2,}\d+\b")
HEX40_RE = re.compile(r"^[0-9a-f]{40}$")
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


def _resolve(path):
    """Resolve a repo-relative path against the git toplevel; absolute paths pass through."""
    p = Path(path)
    if p.is_absolute():
        return p
    code, top = _git(["rev-parse", "--show-toplevel"])
    return (Path(top) / path) if code == 0 else p


def read_source(source):
    """Read a source: `path@gitref` reads the immutable git blob at a real commit; a bare/absolute
    path reads the file. Returns (raw_bytes, err). Bytes are NOT stripped or newline-translated —
    the digest must see exactly what the coordinator's `shasum -a 256` saw (#180)."""
    if not source:
        return None, "missing"
    path, sep, ref = source.partition("@")
    if sep and ref:
        if path.startswith("-") or ref.startswith("-"):
            return None, "refusing option-like ref/path (leading '-') — see git-option-injection guard"
        code, out, err = _run_bytes(["git", "show", f"{ref}:{path}"])
        return (out, None) if code == 0 else (None, (err.strip() or "git ref not found"))
    try:
        return _resolve(path).read_bytes(), None
    except OSError as err:
        return None, str(err)


def sha256_of(content):
    """Digest of RAW BYTES, matching `shasum -a 256` (coordinators compute digests over bytes)."""
    return "sha256:" + hashlib.sha256(content).hexdigest()


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
    authoritative = extract_criterion_ids(content.decode("utf-8"))
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
    """A reviewed_sha, if claimed, must equal head_sha (a rebase/bot-push after review voids it).
    Independent proof that the review HAPPENED is check_review (mutation units)."""
    reviewed = (m.get("pr") or {}).get("reviewed_sha")
    head = m.get("head_sha")
    if reviewed and reviewed != head:
        return [f"stale review: reviewed_sha '{reviewed}' != head_sha '{head}'"]
    return []


def review_ok(reviews, head_sha, author=None):
    """Pure: the LATEST review by some INDEPENDENT reviewer (not the PR author) is APPROVED at
    head_sha. A later COMMENTED/DISMISSED by the same reviewer supersedes an earlier APPROVED."""
    latest = {}
    for r in reviews or []:
        latest[(r.get("user") or {}).get("login")] = r  # chronological: last per reviewer wins
    for who, r in latest.items():
        if author is not None and who == author:
            continue
        if r.get("state") == "APPROVED" and r.get("commit_id") == head_sha:
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


def check_review(m, repo, is_mutation, no_gh=False, corroborated=False, dispatch_lighting=None):
    """3. A mutation unit needs an INDEPENDENT review at head_sha. Default: an APPROVED GitHub review
    looked up on GitHub (a worker-set reviewed_sha is not evidence). Fail-closed. A dark-eligible unit
    (a COORDINATOR dispatch decision, gate-classification.md) lands without a build-blind human review;
    its oracle is the negative control + tests (checked separately). In the sanctioned no-gh / offline
    lane (dispatch --no-gh; merge-serialization.md) the local reviewer artifact is trusted only when an
    out-of-band coordinator contract corroborates the run — otherwise it is worker-forgeable."""
    if not is_mutation:
        return []
    if dispatch_lighting == "dark-eligible":
        if not corroborated:
            return ["dark-eligible mutation: review is waived, so the negative-control oracle must be "
                    "unfakeable — but without an out-of-band coordinator contract (--contract-source + "
                    "--contract-digest) the worker-produced artifact is forgeable; fail-closed "
                    "(gate-classification.md)"]
        return ["NOTE: independent review waived — dark-eligible unit (gate-classification.md); the "
                "corroborated negative control + tests are the oracle, not a human review"]
    head = m.get("head_sha")
    if no_gh:
        art = (m.get("review") or {}).get("artifact")
        if not art:
            return ["no-gh mutation unit: missing review.artifact (a local reviewer record at head_sha)"]
        content, err = read_source(art)
        if err:
            return [f"no-gh mutation unit: review.artifact unreadable ({art}): {err}"]
        if head and head not in content.decode("utf-8"):
            return ["no-gh mutation unit: review.artifact does not reference head_sha"]
        if not corroborated:
            return ["no-gh mutation unit: review.artifact is worker-forgeable without an out-of-band "
                    "coordinator contract (--contract-source + --contract-digest) — fail-closed "
                    "(sign the dispatch record; merge-serialization.md)"]
        return ["NOTE: no-gh review is coordinator-attested via the frozen out-of-band contract (local "
                "reviewer artifact at head_sha), not GitHub-verified — the weaker guarantee "
                "(merge-serialization.md)"]
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
    if not review_ok(reviews, head, author):
        return [f"mutation unit: no INDEPENDENT APPROVED review at head_sha on {repo}#{number} "
                f"(the PR author's own approval and superseded reviews do not count)"]
    return []


def check_negative_control(m, is_mutation, execute=False):
    """4. Structured NC AND the artifact must corroborate the pinned mutant being killed. Reading the
    artifact resolves the mutant + verdict; it is corroboration, not proof (a fabricated artifact can
    still be read). --execute-nc is fail-closed until a replay exists — evidence-manifest §2's
    re-execution sample is the sound form."""
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
    content = content.decode("utf-8")
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
    if execute:
        # replay is not implemented in the reference verifier; a caller that ASKED for it must not
        # get a false pass — fail closed (evidence-manifest §2's re-execution sample is the sound form).
        errs.append("--execute-nc replay is not implemented here; run evidence-manifest §2's "
                    "re-execution sample and record it, or drop --execute-nc")
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
           dispatch_record=None, dispatch_pubkey=None):
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
    checks = (
        lambda: check_scope(m, contract_source, contract_digest),
        lambda: check_shas_present(m),
        lambda: check_real_commits(m, is_mut),
        lambda: check_freshness(m),
        lambda: check_review(m, repo, is_mut, no_gh, corroborated, lighting),
        lambda: check_negative_control(m, is_mut, execute_nc),
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
    ap.add_argument("--execute-nc", action="store_true",
                    help="request NC replay (currently fail-closed; not implemented)")
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
                           args.dispatch_record, args.dispatch_pubkey)
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
