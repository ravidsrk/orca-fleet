#!/usr/bin/env python3
"""Bind a proof-tier advance to artifacts instead of a filename (issue #259).

Before this, `proof: self-run` in a mission's frontmatter needed only a file
under ``docs/runs/`` whose name and body mentioned the mission. A three-line
report with the right filename passed `scripts/validate.py`, `proof_status.py
--check`, and the whole suite — which made "the honesty is machine-checked"
false for the one claim it was written to protect.

What a tier advance has to survive here instead:

* a single ``RUN:`` header line whose fields parse;
* ``mission=`` matching the mission that claims the tier, and ``tier=`` matching
  the tier it claims — so a report cannot be re-pointed at another mission;
* ``inventory_at=`` resolving to a real commit **in this repository**;
* ``manifest=`` existing at that commit — the evidence manifest the run was
  graded against, not a path invented afterwards;
* ``verifier=`` recording the verifier's outcome, with the body carrying the
  ``verify.py`` invocation it came from (a RED is a legitimate recorded outcome:
  a solo run cannot manufacture an independent approver, and saying so is the
  point of the field);
* the run-close integrity inventory re-deriving **at that commit**: at least one
  path verified and zero mismatched.

The inventory is the load-bearing half. Hashing at the recorded commit is what a
fabricated report cannot fake — the bytes have to have existed at a commit that
exists, and the working tree moving on afterwards (which it always does) neither
weakens nor breaks the check. The graded manifest must itself be one of the hashed
paths, and none of this run's OWN artifacts may be absent there: pinning a
neighbouring file while the document the verdict rests on floats free would bind
nothing that matters.

What a tier COSTS, since #286: an actual command execution. The graded manifest's
own ``commands[]`` ledger must carry a record of `verify.py` running against that
manifest, with a ``cmd_sha256`` that hashes its own command line and a ``wtree``
that resolves to a real object here. Prose is free -- a fabricated report cleared
the earlier gate in fifteen minutes by writing a command line -- so the body's
invocation is no longer the only evidence a run happened.

What this does NOT do, said plainly: it does not re-run `verify.py` and re-derive
the verdict, and the ledger above is still written ON the worker, so the floor it
raises is "ran a command and recorded it against real content", not "could not
have been typed". Closing that needs a coordinator-signed verifier transcript
checked against a committed key (#281). That run's authorities are not reproducible after the fact — the
coordinator's out-of-band contract, a GitHub review lookup, the live worktree — so
a "re-derivation" here would be a different, weaker check wearing the same name.
What is checked is that the recorded outcome is attributable to a real invocation
and that every artifact behind it still hashes true at the recorded commit.

A report whose artifacts were never retained in this repository cannot pass, and
that is the intended answer, not a gap: it stays in ``docs/runs/`` as recorded
history while the mission's frontmatter says ``doctrine-only``. History and a
machine-checkable claim are different things.

Exit codes
    0  every checked report binds
    1  at least one report does not
    2  could not run (no skills/, unreadable input)
"""
import argparse
import hashlib
import importlib.util
import json
import re
import shlex
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
RUNS_DIR = ROOT / "docs" / "runs"

_spec = importlib.util.spec_from_file_location("inventory", HERE / "inventory.py")
inventory = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(inventory)

RUN_HEADER_RE = re.compile(r"^RUN:\s*(.+?)\s*$", re.M)


def _invocation_re(manifest):
    r"""`verify.py … --manifest <THIS report's manifest>` — the transcript, not the word.

    Two tightenings, both learned the hard way. "the body contains 'verify.py'" was
    satisfied by any prose mentioning it. Replacing that with `--manifest \S+` was
    then satisfied by this very module's explanatory prose, which writes
    `verify.py … --manifest <path>` — `<path>` is a perfectly good `\S+`. So the
    argument has to be the actual manifest the RUN: header names: a sentence about
    verification cannot accidentally contain it, and a run that really happened has
    it for free.
    """
    return re.compile(r"verify\.py[^\n]*--manifest\s+" + re.escape(manifest) + r"(\s|$)")
FIELD_RE = re.compile(r"([a-z_]+)=(\S+)")
REQUIRED_FIELDS = ("mission", "tier", "inventory_at", "manifest", "verifier")
VERIFIER_OUTCOMES = {"GREEN", "RED"}
# Tiers a RUN: header may DECLARE. `doctrine-only` is legal here and advances nothing: it is how a
# report says "this run happened and is recorded, and it supports no tier claim". Without it a
# demoted report had to keep asserting the tier its own Evidence-binding section retracted, and
# nothing checked the contradiction — check_report only runs for missions claiming a tier ABOVE
# doctrine-only, so the stale header was unreachable (PR #308 review).
TIERS = {"doctrine-only", "self-run", "external-run"}
# ...but only these two are a tier ADVANCE that needs evidence behind it.
ADVANCING_TIERS = {"self-run", "external-run"}


def parse_run_header(text):
    """({field: value}, error). Exactly one RUN: line, every required field present."""
    headers = RUN_HEADER_RE.findall(text)
    if not headers:
        return None, (
            "no 'RUN:' header — a tier advance needs one line naming the mission, the "
            "tier, the commit its inventory was computed at, its manifest, and the "
            "verifier outcome"
        )
    if len(headers) > 1:
        return None, f"{len(headers)} 'RUN:' headers — exactly one is the report's identity"
    fields = dict(FIELD_RE.findall(headers[0]))
    missing = [f for f in REQUIRED_FIELDS if not fields.get(f)]
    if missing:
        return None, f"RUN: header is missing {missing} (want {list(REQUIRED_FIELDS)})"
    return fields, None


def path_exists_at(rev, path_text, root):
    return subprocess.run(
        ["git", "cat-file", "-e", f"{rev}:{path_text}"],
        cwd=str(root), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    ).returncode == 0


_ENV_ASSIGN_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")
# THE verifier, by path — not by basename. `/tmp/verify.py` is a script the worker wrote
# (PR #308 review); only this repository's own verifier counts.
VERIFIER_PATH_PARTS = ("runtime", "scripts", "verify.py")


def _is_repo_verifier(token, root):
    """True when `token` names THIS repository's verify.py."""
    path = Path(token)
    parts = tuple(part for part in path.parts if part != ".")
    if ".." in parts:
        return False  # an escape hatch out of the repo, wherever it currently points
    if tuple(parts[-3:]) != VERIFIER_PATH_PARTS:
        return False  # includes a bare `verify.py`, which resolves against cwd or PATH
    try:
        root = Path(root).resolve()
        return (root / path).resolve() == root.joinpath(*VERIFIER_PATH_PARTS)
    except (ValueError, OSError, RuntimeError):
        return False


def _valid_python_xoption(option):
    """Known CPython 3.13 startup value constraints (using/cmdline.html#cmdoption-X).

    This is argv validation, not authentication of the executable or its environment. In
    particular gil=0 needs a free-threaded build; future/build-specific options are not modeled.
    CPython permits arbitrary additional keys in sys._xoptions, so they are preserved.
    """
    name, sep, value = option.partition("=")
    if name == "utf8":
        return not sep or value in {"0", "1"}
    if name == "gil":  # introduced in 3.13; build availability is a separate concern
        return value in {"0", "1"}
    if name == "frozen_modules":
        return value in {"", "on", "off"}
    if name not in {"int_max_str_digits", "cpu_count", "tracemalloc"}:
        return True
    if not sep:
        return name == "tracemalloc"
    if name == "cpu_count" and value == "default":  # introduced in 3.13
        return True
    # initconfig.c uses wcstol plus an INT_MAX bound, not Python's int grammar (underscores).
    if value and not re.fullmatch(r"[ \t\r\n\f\v]*[+-]?[0-9]+", value):
        return False
    try:
        number = int(value or "0")
    except ValueError:
        return False
    if not 0 <= number <= 2147483647:
        return False
    if name == "int_max_str_digits":
        return number == 0 or number >= 640
    if name == "cpu_count":
        return number >= 1
    return number <= 65535  # tracemalloc's maximum traceback depth


def _python_script_index(argv, i):
    """Locate a script after Python options; reject non-script modes and unknown syntax.

    Short options can cluster; -W/-X consume the rest of their token or the NEXT token.
    Skipping all dash-prefixed tokens admits -cpass, -uV and --help without running a script.
    """
    xoptions = {}
    while i < len(argv) and argv[i].startswith("-"):
        token = argv[i]
        if token == "--":
            i += 1
            break
        if token == "--check-hash-based-pycs":
            if i + 1 >= len(argv) or argv[i + 1] not in {"always", "default", "never"}:
                return len(argv)
            i += 2
            continue
        if token == "-" or token.startswith("--"):
            return len(argv)
        for offset, flag in enumerate(token[1:], start=1):
            if flag in "WX":
                value = token[offset + 1:]
                if offset == len(token) - 1:
                    i += 1  # consume the separate option argument, never mistake it for a script
                    if i >= len(argv):
                        return len(argv)
                    value = argv[i]
                if flag == "X":
                    # CPython initializes from the FIRST occurrence of a key, not the last.
                    xoptions.setdefault(value.partition("=")[0], value)
                break
            if flag not in "bBdEiIOPqRsSuvx":
                return len(argv)  # includes c/m modes and h/?/V exits, even inside clusters
        i += 1
    return i if all(_valid_python_xoption(value) for value in xoptions.values()) else len(argv)


class _SilentParser(argparse.ArgumentParser):
    """argparse that raises instead of printing usage and calling sys.exit."""

    def error(self, message):
        raise ValueError(message)

    def exit(self, status=0, message=None):
        raise ValueError(message or f"exit {status}")


def _parsed_manifest(rest):
    """The `--manifest` value argparse would see in `rest`, or None if it would refuse the line.

    Hand-reading this argv diverged from argparse three times in review, three different ways: the
    first occurrence was taken where argparse keeps the last, and a dangling trailing `--manifest`
    read as the earlier value where argparse rejects the whole command line. The lesson is not "be
    more careful with the next hand-rolled scan" — it is that the only reliable model of a parser
    is that parser. So the recorded argv is PARSED, not scanned.

    `parse_known_args` because a recorded command legitimately carries flags this function does not
    model (--contract-source, --lighting, --execute-nc): an unrecognised flag is no reason to
    disbelieve the run, while a malformed one is.
    """
    parser = _SilentParser(add_help=False)
    parser.add_argument("--manifest")
    try:
        known, _unknown = parser.parse_known_args(list(rest))
    except (ValueError, SystemExit):
        return None
    return known.manifest


def executes_verifier(cmd, manifest_path, root=None):
    r"""True when `cmd` RUNS this repo's verify.py against `manifest_path` — parsed as argv.

    A regex over the command line is the wrong instrument here, and this module already has the
    scar tissue to prove it: `_invocation_re` was tightened twice, first because "the body
    contains verify.py" matched any prose, then because `--manifest \S+` matched this module's own
    docstring. Applied to a ledger RECORD it failed again — `echo verify.py --manifest <m>` hashes
    true, names a real tree, and invokes nothing. The regex is still right for the report BODY,
    which is prose; a recorded command is argv and is read as argv.

    Two further evasions review found in the argv reading itself, both fixed here. A basename test
    accepted `/tmp/verify.py`, a script the worker wrote; the path must be this repository's own
    verifier. And taking the FIRST `--manifest` disagreed with argparse, which takes the LAST — so
    `--manifest <graded> --manifest other.json` read as graded here while the real verifier read
    the other file.
    """
    if not isinstance(cmd, str):
        return False
    try:
        argv = shlex.split(cmd, comments=True)
    except ValueError:
        return False
    i = 0
    while i < len(argv) and (argv[i] == "env" or _ENV_ASSIGN_RE.match(argv[i])):
        i += 1
    if i >= len(argv):
        return False
    if Path(argv[i]).name.startswith("python"):
        i = _python_script_index(argv, i + 1)
        if i >= len(argv):
            return False
    if not _is_repo_verifier(argv[i], root or ROOT):
        return False
    return _parsed_manifest(argv[i + 1:]) == manifest_path


def blob_at(rev, path_text, root):
    """The bytes of `path_text` as of `rev`, or None. Reading the manifest AT the pinned commit,
    never from the working tree, is the whole point: the tree has moved on since the run."""
    proc = subprocess.run(
        ["git", "show", f"{rev}:{path_text}"],
        cwd=str(root), stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
    )
    return proc.stdout if proc.returncode == 0 else None


def tree_of(rev, root):
    """`rev`'s tree sha, or None."""
    proc = subprocess.run(
        ["git", "rev-parse", f"{rev}^{{tree}}"],
        cwd=str(root), stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True,
    )
    out = proc.stdout.strip()
    return out if proc.returncode == 0 and out else None


def verifier_ran(manifest_path, rev, root):
    """Errors that stop this report proving the verifier was RUN. [] means a run is recorded.

    Until #286 the only evidence a tier had that `verify.py` ever executed was PROSE: the report
    body had to contain a command line naming its own manifest. Prose is free. A fabricated
    `map-it` self-run — seven files, 32 lines, one commit — cleared the whole gate in under fifteen
    minutes because writing a command line costs nothing.

    So the tier now costs a command EXECUTION: the graded manifest's own `commands[]` ledger must
    carry a record of the verifier running, with a `wtree` that resolves to the tree of a commit
    the report pins. `evidence-run.py` writes those records; a hand-written one has to name a tree
    that really exists in this repository and hash its own command line.

    Said plainly, because it bounds what this buys: the ledger is still written on the worker, so
    this raises the floor from "wrote a sentence" to "ran a command and recorded it against real
    content". It is not yet a leg the worker cannot type — that needs a coordinator-signed verifier
    transcript checked against a committed key (#281).
    """
    raw = blob_at(rev, manifest_path, root)
    if raw is None:
        return [f"the graded manifest {manifest_path} cannot be read at {rev}"]
    try:
        manifest = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, ValueError) as err:
        return [f"the graded manifest {manifest_path} at {rev} is not readable JSON ({err})"]
    if not isinstance(manifest, dict):
        return [f"the graded manifest {manifest_path} at {rev} is not a JSON object"]

    records = [c for c in (manifest.get("commands") or []) if isinstance(c, dict)]
    verifier = [c for c in records if executes_verifier(c.get("cmd"), manifest_path, root)]
    if not verifier:
        seen = ", ".join(repr(c.get("cmd")) for c in records) or "nothing"
        return [f"the graded manifest {manifest_path} records no commands[] entry running "
                f"verify.py against itself — a tier costs a RUN, not a sentence about one. Wrap the "
                f"verifier in evidence-run.py so the ledger carries it (#286). Recorded there: {seen}"]

    # Every candidate must bind to content, or the record describes nothing.
    problems = []
    for rec in verifier:
        line = rec["cmd"]
        digest, wtree = rec.get("cmd_sha256"), rec.get("wtree")
        actual = hashlib.sha256(line.encode("utf-8")).hexdigest()
        if digest != actual:
            problems.append(f"its cmd_sha256 {digest} does not hash its own command line ({actual})")
            continue
        if not (isinstance(wtree, str) and wtree):
            problems.append("it carries no wtree, so it is bound to no content at all")
            continue
        if not inventory.rev_exists(wtree, root) and tree_of(wtree, root) is None:
            problems.append(f"its wtree {wtree[:12]}… is not an object in this repository")
            continue
        return []  # one sound record is enough
    return [f"the graded manifest {manifest_path} records a verify.py run that binds to nothing: "
            + "; ".join(problems)]


def check_report(report_path, mission, tier, root=None):
    """Errors that stop `mission` claiming `tier` on this report. [] means bound."""
    root = root or ROOT
    report = Path(report_path)
    if not report.is_absolute():
        report = root / report
    errors = []
    if not report.is_file():
        return [f"proof_evidence {report_path} does not exist"]
    try:
        text = report.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as err:
        return [f"proof_evidence {report_path} is unreadable: {err}"]

    fields, err = parse_run_header(text)
    if err:
        return [f"{report_path}: {err}"]

    if fields["mission"] != mission:
        errors.append(
            f"{report_path}: RUN: mission={fields['mission']} but {mission} claims it "
            "— a run report belongs to the mission that ran"
        )
    if fields["tier"] != tier:
        errors.append(
            f"{report_path}: RUN: tier={fields['tier']} but the frontmatter claims {tier}"
        )
    if fields["verifier"] not in VERIFIER_OUTCOMES:
        errors.append(
            f"{report_path}: RUN: verifier={fields['verifier']} — want one of "
            f"{sorted(VERIFIER_OUTCOMES)} (a recorded RED is honest; an unrecorded one is not)"
        )
    elif not _invocation_re(fields["manifest"]).search(text):
        # "the body contains the string verify.py" was satisfied by any prose that
        # mentioned it (PR #277 review, P1). The body must show the actual command,
        # run against the manifest this report is graded on.
        errors.append(
            f"{report_path}: RUN: verifier={fields['verifier']} but the body shows no "
            f"verify.py invocation against {fields['manifest']} that the outcome could "
            "have come from — record the command and its exit code, not a description of them"
        )

    rev = fields["inventory_at"]
    if not inventory.rev_exists(rev, root):
        errors.append(
            f"{report_path}: RUN: inventory_at={rev} is not a commit in this repository "
            "— an unresolvable pin verifies nothing"
        )
        return errors

    manifest = fields["manifest"]
    if not path_exists_at(rev, manifest, root):
        errors.append(f"{report_path}: RUN: manifest={manifest} does not exist at {rev}")
    run_dir = run_directory(report, mission, root)
    if run_dir is None:
        errors.append(
            f"{report_path}: filename must be docs/runs/<YYYY-MM-DD>-{mission}-<tier>.md "
            "— the run directory is derived from it"
        )
    elif not manifest.startswith(run_dir + "/"):
        errors.append(
            f"{report_path}: RUN: manifest={manifest} is outside this run's own directory "
            f"{run_dir}/ — a run is graded against its own manifest, not another run's"
        )

    # #286: the tier must cost a command execution, not a sentence describing one.
    for problem in verifier_ran(manifest, rev, root):
        errors.append(f"{report_path}: {problem}")

    try:
        _report, _lines, entries = inventory.load(report)
    except inventory.InventoryError as exc:
        errors.append(f"{report_path}: integrity inventory: {exc}")
        return errors
    matched, mismatched, missing = inventory.check_entries(entries, report, root, at=rev)
    if mismatched:
        for path_text, recorded, actual in mismatched:
            errors.append(
                f"{report_path}: inventory {path_text} at {rev}: recorded {recorded[:12]}…, "
                f"actual {actual[:12]}…"
            )
    if not matched:
        errors.append(
            f"{report_path}: inventory verified nothing at {rev} "
            f"({len(missing)} listed path(s) absent there) — the tier is not artifact-bound"
        )
    elif run_dir is not None and not any(p.startswith(run_dir + "/") for p in matched):
        errors.append(
            f"{report_path}: no verified inventory path lives in this run's own directory "
            f"{run_dir}/ — borrowing another run's artifacts is not evidence of this one"
        )
    # The manifest the run was GRADED against has to be one of the hashed artifacts.
    # Without this, the inventory could hash one trivial file while the manifest — the
    # document the whole verdict rests on — went unpinned and could be edited freely
    # afterwards (PR #277 review, P1).
    if manifest not in matched:
        where = "hashes differently" if any(p == manifest for p, _r, _a in mismatched) else (
            "is not in the inventory at all" if manifest not in missing else
            "is listed but absent at that commit")
        errors.append(
            f"{report_path}: the graded manifest {manifest} {where} — the inventory must pin the "
            "document the verdict rests on, not only its neighbours"
        )
    # A run's own artifacts are the ones it is responsible for retaining. A path
    # elsewhere may legitimately have moved since (inventory.py treats MISSING as a
    # snapshot, not a mismatch); one inside this run's directory going absent means
    # the evidence was not kept.
    if run_dir is not None:
        gone = sorted(p for p in missing if p.startswith(run_dir + "/"))
        if gone:
            errors.append(
                f"{report_path}: this run's own artifact(s) {gone} are absent at {rev} — a run "
                "must retain the evidence it claims, even when other listed paths have moved on"
            )
    return errors


def run_directory(report, mission, root=None):
    """`docs/runs/<date>-<mission>…` — the directory a run's own artifacts live in.

    Derived from the report filename, never from the RUN: header, so a report
    cannot nominate someone else's directory. Both `…-ship-it-self-run.md` and
    its `…-ship-it-selfrun/` artifact directory share the date and the mission,
    which is what is matched: same date prefix, mission name present.
    """
    m = re.match(r"^(\d{4}-\d{2}-\d{2})-", report.stem)
    if not m or mission not in report.stem:
        return None
    date = m.group(1)
    flat = mission.replace("-", "")
    runs_dir = ((root or ROOT) / "docs" / "runs") if root is not None else RUNS_DIR
    for candidate in sorted(runs_dir.glob(f"{date}-*")):
        if not candidate.is_dir():
            continue
        stem = candidate.name
        if stem.startswith(date + "-") and (mission in stem or flat in stem.replace("-", "")):
            return f"docs/runs/{stem}"
    return f"docs/runs/{report.stem}"


def _missions(root):
    """[(mission, tier, proof_evidence)] for every mission above doctrine-only."""
    spec = importlib.util.spec_from_file_location("proof_status", HERE / "proof_status.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    out = []
    for rec in mod.collect(root / "skills", root):
        if rec["proof"] in ADVANCING_TIERS:
            out.append((rec["name"] or rec["dir"], rec["proof"], rec["proof_evidence"]))
    return out


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="run_report.py",
        description="Check that a proof-tier advance is bound to artifacts, not a filename.",
        epilog="exit 0 bound / 1 not bound / 2 could-not-run",
    )
    parser.add_argument("report", nargs="?", help="one report to check (default: every claim)")
    parser.add_argument("--mission", help="mission the report is claimed by (with `report`)")
    parser.add_argument("--tier", help="tier claimed (with `report`)")
    args = parser.parse_args(argv)

    if args.report:
        if not (args.mission and args.tier):
            parser.error("--mission and --tier are required with an explicit report")
        claims = [(args.mission, args.tier, args.report)]
    else:
        if not (ROOT / "skills").is_dir():
            print(f"skills/ not found at {ROOT / 'skills'}", file=sys.stderr)
            return 2
        claims = _missions(ROOT)

    failed = False
    seen = {}
    for mission, tier, evidence in claims:
        if evidence and evidence in seen:
            print(
                f"FAIL {mission} ({tier}) — proof_evidence {evidence} is already claimed by "
                f"{seen[evidence]}; one run report proves one mission's tier"
            )
            failed = True
            continue
        if evidence:
            seen[evidence] = mission
        if not evidence:
            print(f"FAIL {mission} ({tier}) — no proof_evidence")
            failed = True
            continue
        errors = check_report(evidence, mission, tier)
        if errors:
            failed = True
            print(f"FAIL {mission} ({tier})")
            for error in errors:
                print(f"   - {error}")
        else:
            print(f"bound {mission} ({tier}) — {evidence}")
    if not claims:
        print("no mission claims a tier above doctrine-only")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
