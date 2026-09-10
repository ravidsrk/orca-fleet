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
weakens nor breaks the check.

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
import importlib.util
import re
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
FIELD_RE = re.compile(r"([a-z_]+)=(\S+)")
REQUIRED_FIELDS = ("mission", "tier", "inventory_at", "manifest", "verifier")
VERIFIER_OUTCOMES = {"GREEN", "RED"}
TIERS = {"self-run", "external-run"}


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
    elif "verify.py" not in text:
        errors.append(
            f"{report_path}: RUN: verifier={fields['verifier']} but the body never shows the "
            "verify.py invocation it came from"
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
        if rec["proof"] in TIERS:
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
