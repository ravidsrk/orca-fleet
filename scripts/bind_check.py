#!/usr/bin/env python3
"""Per-PR intake check for submitted run bundles (issue #415).

The `validate` workflow's bare `run_report.py` only checks missions that
ALREADY claim a tier above doctrine-only — a submission PR (bundle first,
promotion later) is invisible to it. This check closes that gap: on PRs
touching `docs/runs/` or `docs/reports/` it routes every added or modified
candidate report to the binder and enforces the bundle format from
`docs/run-submission-guide.md` (envelope + bindable core).

Routing only — every substantive verdict comes from
`run_report.check_report`, and failures print the binder's own output so a
contributor learns the bar from the bot, not from a review round.

Exit 0: every candidate binds (or nothing to check). 1: at least one
failure. 2: could not run (unresolvable base, no skills/).
"""
import argparse
import importlib.util
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

_spec = importlib.util.spec_from_file_location(
    "run_report", ROOT / "runtime" / "scripts" / "run_report.py"
)
run_report = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(run_report)

_ps_spec = importlib.util.spec_from_file_location(
    "proof_status", ROOT / "runtime" / "scripts" / "proof_status.py"
)
proof_status = importlib.util.module_from_spec(_ps_spec)
_ps_spec.loader.exec_module(proof_status)

# The exact frontmatter spelling a RUN: header must use. A run-together
# `tier=selfrun` would route fine here and then fail the promotion gate,
# where validate.py compares it against `proof: self-run` — so the bot
# teaches the hyphenated spelling at submission time, not at promotion.
ADVANCING_TIERS = ("self-run", "external-run")
# Envelope dirnames accept both spellings: the on-disk Phase-1 envelopes
# are run-together (`harden-it-externalrun`), TEMPLATE.md is hyphenated.
TIER_NORMALIZED = {"selfrun", "externalrun"}
CANONICAL_TIER = {"selfrun": "self-run", "externalrun": "external-run"}
NON_REPORT_BASENAMES = {"README.md", "TEMPLATE.md"}
DATE_PREFIX_RE = re.compile(r"^\d{4}-\d{2}-\d{2}-")


def known_missions(root):
    """Mission names from the catalog's own frontmatter (never hardcoded)."""
    return {
        rec["name"] or rec["dir"]
        for rec in proof_status.collect(root / "skills", root)
        if rec["name"] or rec["dir"]
    }


def normalize_tier(tier):
    return tier.strip().lower().replace("-", "")


def changed_entries(root, base):
    """[(status, path)] for added/modified/renamed paths in this branch.

    `base` is the merge-base ref (CI passes origin/<base_ref>); the diff is
    merge-base..HEAD, i.e. exactly what the PR adds. Raises ValueError when
    the base does not resolve.
    """
    mb = subprocess.run(
        ["git", "merge-base", "HEAD", base],
        cwd=str(root), stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True,
    )
    if mb.returncode != 0 or not mb.stdout.strip():
        raise ValueError(f"base ref {base!r} does not resolve to a merge-base with HEAD")
    proc = subprocess.run(
        ["git", "diff", "--name-status", "--diff-filter=AMR",
         mb.stdout.strip(), "HEAD", "--", "docs/runs", "docs/reports"],
        cwd=str(root), stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True,
    )
    if proc.returncode != 0:
        raise ValueError("git diff of the PR range failed")
    entries = []
    for line in proc.stdout.splitlines():
        parts = line.split("\t")
        if parts[0].startswith("R"):
            entries.append(("A", parts[-1]))  # a rename is new content at its new path
        elif len(parts) == 2:
            entries.append((parts[0], parts[1]))
    return entries


def is_core_path(path_text):
    """A file that could be a bindable report: any docs/runs/*.md except the
    archive's own README and TEMPLATE (whose RUN: line is a placeholder)."""
    p = Path(path_text)
    return (
        len(p.parts) >= 3
        and p.parts[0] == "docs"
        and p.parts[1] == "runs"
        and p.suffix == ".md"
        and p.name not in NON_REPORT_BASENAMES
    )


def envelope_claim(path_text, missions):
    """(mission, tier-token) if `path_text` is a submission envelope's README.

    `docs/reports/<mission>-<tier>/README.md`, longest mission-prefix match
    so `harden-it-externalrun` is mission `harden-it`, not `harden`. Anything
    else under docs/reports/ (release snapshots, future non-submission dirs)
    is not an envelope and is ignored.
    """
    p = Path(path_text)
    if len(p.parts) != 4 or p.parts[0] != "docs" or p.parts[1] != "reports":
        return None
    if p.name != "README.md":
        return None
    dirname = p.parts[2]
    for mission in sorted(missions, key=len, reverse=True):
        if dirname == mission or dirname.startswith(mission + "-"):
            rest = dirname[len(mission):].lstrip("-")
            if rest and normalize_tier(rest) in TIER_NORMALIZED:
                return mission, rest
            continue
    return None


def envelope_present(root, mission, tier_norm):
    """The complete envelope (README.md + negctrl.txt) for (mission, tier)
    in either spelling, or None. README-only is not an envelope: the bundle
    format requires both files, and so does this script's failure message."""
    spellings = {"selfrun": ("selfrun", "self-run"),
                 "externalrun": ("externalrun", "external-run")}[tier_norm]
    for spelling in spellings:
        candidate = root / "docs" / "reports" / f"{mission}-{spelling}" / "README.md"
        if candidate.is_file() and (candidate.parent / "negctrl.txt").is_file():
            return candidate.relative_to(root).as_posix()
    return None


def submission_shape(path_text, missions):
    """(mission, tier) if the basename is the documented submission path.

    `docs/runs/<YYYY-MM-DD>-<mission>-<tier>.md`, longest mission-prefix
    match, either tier spelling. A file at this path is a submission
    attempt even when its RUN: header is missing or misspelled — that is
    the route that fails those closed instead of skipping them as notes.
    """
    p = Path(path_text)
    if (
        len(p.parts) != 3
        or p.parts[0] != "docs"
        or p.parts[1] != "runs"
        or p.suffix != ".md"
        or p.name in NON_REPORT_BASENAMES
    ):
        return None
    dated = DATE_PREFIX_RE.match(p.name)
    if not dated:
        return None
    rest = p.name[dated.end(): -len(".md")]
    for mission in sorted(missions, key=len, reverse=True):
        if rest == mission or rest.startswith(mission + "-"):
            token = rest[len(mission):].lstrip("-")
            if token and normalize_tier(token) in TIER_NORMALIZED:
                return mission, CANONICAL_TIER[normalize_tier(token)]
            continue
    return None


def fail_shaped(root, path_text, shape):
    """Route a malformed submission-shaped report to the binder and fail.

    The claim is the path's own (mission, tier): a missing RUN: header
    fails on the binder's first leg, a misspelled mission= on its
    mission-mismatch leg. Returns the failure count (always 1 — the
    mismatch is structural, so the binder cannot come back clean).
    """
    mission, tier = shape
    errors = run_report.check_report(path_text, mission, tier, root=root)
    print(f"FAIL {mission} ({tier}) — {path_text}")
    for error in errors:
        print(f"   - {error}")
    return 1


def header_of(root, path_text):
    try:
        text = (root / path_text).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None, f"{path_text} is unreadable"
    fields, err = run_report.parse_run_header(text)
    if err is not None:
        if run_report.RUN_HEADER_RE.search(text):
            return None, f"{path_text}: {err}"
        return None, None  # no RUN: line at all — a tracker or note, not a candidate
    return fields, None


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="bind_check.py",
        description="Bind-check the run reports a PR adds or modifies (issue #415).",
        epilog="exit 0 bound-or-nothing-to-check / 1 failure / 2 could-not-run",
    )
    parser.add_argument("--base", default="origin/main",
                        help="merge-base ref for the PR range (default: origin/main)")
    parser.add_argument("--root", default=None, help="repo root (default: inferred)")
    args = parser.parse_args(argv)
    root = Path(args.root).resolve() if args.root else ROOT

    if not (root / "skills").is_dir():
        print(f"skills/ not found at {root / 'skills'}", file=sys.stderr)
        return 2
    try:
        entries = changed_entries(root, args.base)
    except ValueError as err:
        print(f"bind-check: {err}", file=sys.stderr)
        return 2

    missions = known_missions(root)
    failures = 0
    candidates = []  # (path, mission, tier) routed to the binder
    cores = []  # (mission, tier_norm, path) for envelope cross-checks

    # Two passes: the diff sorts docs/reports/ before docs/runs/, so an
    # envelope is always seen before its core — collect every core first.
    for _status, path_text in entries:
        if not is_core_path(path_text):
            continue
        fields, err = header_of(root, path_text)
        if err is not None:
            print(f"FAIL {path_text}")
            print(f"   - {err}")
            print("   - a bindable report carries exactly one RUN: header "
                  "(docs/run-submission-guide.md, bundle format)")
            failures += 1
            continue
        if fields is None:
            # No RUN: line — a tracker or note, unless the filename is the
            # documented submission path, which fails closed through the
            # binder instead of skipping to a no-candidates success.
            shape = submission_shape(path_text, missions)
            if shape is None:
                continue
            failures += fail_shaped(root, path_text, shape)
            continue
        mission, tier = fields["mission"], fields["tier"]
        if mission not in missions:
            shape = submission_shape(path_text, missions)
            if shape is None:
                print(f"skip {path_text} — RUN: mission={mission} names no catalog mission")
                continue
            failures += fail_shaped(root, path_text, shape)
            continue
        if tier == "doctrine-only":
            # Recorded history, explicitly allowed: the binder's own default
            # mode only checks advancing tiers, and so does this route.
            print(f"skip {path_text} — tier=doctrine-only advances nothing")
            continue
        if tier not in ADVANCING_TIERS:
            print(f"FAIL {mission} ({tier}) — {path_text}")
            print(f"   - RUN: tier={tier} — want exactly "
                  f"{' | '.join(ADVANCING_TIERS)} (the frontmatter spelling; "
                  "a run-together tier fails the promotion gate)")
            failures += 1
            continue
        candidates.append((path_text, mission, tier))
        cores.append((mission, normalize_tier(tier), path_text))

    for status, path_text in entries:
        if status != "A":
            continue
        claim = envelope_claim(path_text, missions)
        if claim is None:
            continue
        mission, token = claim
        want = normalize_tier(token)
        match = next(
            (p for m, t, p in cores if m == mission and t == want), None,
        )
        if match is None:
            print(f"FAIL envelope {Path(path_text).parent.as_posix()}")
            print(f"   - a submission envelope needs its bindable core in the same PR: "
                  f"docs/runs/<YYYY-MM-DD>-{mission}-*.md with "
                  f"RUN: mission={mission} tier=<{token}> — the envelope alone "
                  "cannot BIND or promote (docs/run-submission-guide.md, bundle format)")
            failures += 1
        else:
            print(f"envelope {Path(path_text).parent.as_posix()} — core {match}")

    for path_text, mission, tier in candidates:
        errors = run_report.check_report(path_text, mission, tier, root=root)
        if errors:
            failures += 1
            print(f"FAIL {mission} ({tier}) — {path_text}")
            for error in errors:
                print(f"   - {error}")
            continue
        print(f"bound {mission} ({tier}) — {path_text}")
        env = envelope_present(root, mission, normalize_tier(tier))
        if env is None:
            failures += 1
            print(f"FAIL {mission} ({tier}) — {path_text}")
            print(f"   - the report binds, but the bundle is missing its envelope: add "
                  f"docs/reports/{mission}-{tier}/ (README.md + negctrl.txt), the stable "
                  "mission-addressed summary future runners copy "
                  "(docs/run-submission-guide.md, bundle format)")

    if not candidates and failures == 0:
        print("no candidate run reports changed in this PR")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
