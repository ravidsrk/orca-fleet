#!/usr/bin/env python3
"""Regenerate and re-check the integrity inventory embedded in a report.

A run report closes with an inventory of the artifacts it produced and their
sha256. Written by hand it is a claim; re-derived it is a check. This script is
both halves: ``write`` regenerates the block from the files on disk, ``check``
re-hashes every listed path and reports the drift.

Two block shapes are recognised, because both are already in use. Under a
heading matching ``## ... integrity inventory (sha256)`` (any depth, any leading
words, case-insensitive):

* a fenced block of ``<sha256>  <path>`` lines -- the ``sha256sum`` format; and
* a markdown table of ``| `path` | `hash` |`` rows, with a ``| --- |``
  separator row skipped.

Paths resolve against the repo root first, then against the report's own
directory -- a run report lists repo-relative paths, a per-directory README
lists its own siblings, and both are correct.

An inventory that names a path which no longer exists is NOT a mismatch. A
report is a dated snapshot: it may pin artifacts from a slice tip that has since
moved, or files that were deliberately retired. Those are reported as MISSING
and do not fail ``check``; a path that exists and hashes differently does.

Exit codes
    0  every path that exists matches its recorded hash
    1  at least one existing path hashes differently (``check``), or a path to
       be written does not exist (``write``)
    2  could not run -- no inventory block found, an unreadable report, or
       (``check``) not one listed path exists, so nothing was actually verified.
       A verification that examined nothing must not report success.

How to wire
    ``write`` runs at run close, after the last artifact is final: the block it
    emits is the thing a reader can re-derive. ``check`` runs in the same gate
    that reads the report -- the inventory is what makes a manifest's SHA pins
    meaningful, since a pin nobody re-computes is a comment. Exit 2 is the one
    that matters most: an inventory whose paths have all moved verified nothing,
    and must park rather than pass. Re-derive a historical report's hashes at
    the commit it names, not at HEAD.

    Example: ``inventory.py check docs/runs/2026-08-28-ship-it-self-run.md``
"""
import argparse
import hashlib
import re
import subprocess
import sys
from pathlib import Path

EXIT_OK = 0
EXIT_MISMATCH = 1
EXIT_CANNOT_RUN = 2

HEADING = re.compile(r"^\s{0,3}#{1,6}\s+.*\bintegrity inventory\s*\(sha256\)", re.IGNORECASE)
NEXT_HEADING = re.compile(r"^\s{0,3}#{1,6}\s+")
FENCE = re.compile(r"^\s*(```+|~~~+)")
SHA_LINE = re.compile(r"^([0-9a-fA-F]{64})\s+(\S.*)$")
TABLE_ROW = re.compile(r"^\s*\|(.+)\|\s*$")
SHA256 = re.compile(r"^[0-9a-fA-F]{64}$")


class InventoryError(Exception):
    """Could-not-run: no block, unreadable report, nothing verifiable."""


def sha256_file(path):
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def repo_root(start):
    try:
        r = subprocess.run(["git", "-C", str(start), "rev-parse", "--show-toplevel"],
                           capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None
    if r.returncode != 0 or not r.stdout.strip():
        return None
    return Path(r.stdout.strip())


def find_blocks(lines):
    """[(start, end)] for EVERY inventory block body, exclusive of the heading. Each block runs to
    the next heading of any depth or EOF.

    Every, not the first (#315). Reading only the first left a second block in the same document
    unhashed and uncompared, so a report could carry one inventory a tool checks and another a
    human reads. A document's integrity claim is all of the claims it makes."""
    blocks = []
    for i, line in enumerate(lines):
        if not HEADING.match(line):
            continue
        end = len(lines)
        for j in range(i + 1, len(lines)):
            if NEXT_HEADING.match(lines[j]):
                end = j
                break
        blocks.append((i, end))
    if not blocks:
        raise InventoryError("no '## … integrity inventory (sha256)' heading found")
    return blocks


def parse_entries(lines, start, end):
    """[(lineno, path, recorded_hash, shape)] for one inventory block."""
    entries = []
    in_fence = False
    for idx in range(start + 1, end):
        line = lines[idx]
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        m = SHA_LINE.match(line.strip())
        if m:
            entries.append((idx, m.group(2).strip(), m.group(1).lower(), "fenced"))
            continue
        t = TABLE_ROW.match(line)
        if t:
            cells = [c.strip().strip("`").strip() for c in t.group(1).split("|")]
            if len(cells) < 2 or set("".join(cells)) <= set("-: "):
                continue
            path_cell, hash_cell = cells[0], cells[1]
            if SHA256.match(hash_cell):
                entries.append((idx, path_cell, hash_cell.lower(), "table"))
            elif SHA256.match(path_cell):
                entries.append((idx, hash_cell, path_cell.lower(), "table"))
    if not entries:
        raise InventoryError("the inventory block lists no <sha256> <path> entries")
    return entries


def resolve(path_text, report, root):
    """Repo root first, then the report's own directory. Returns a Path or None."""
    candidates = []
    if root is not None:
        candidates.append(root / path_text)
    candidates.append(report.parent / path_text)
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return None


def sha256_at(rev, path_text, cwd):
    """sha256 of `path_text` as it was at git revision `rev`, or None if absent.

    A dated report pins artifacts at the tip it closed on; HEAD has moved since.
    Hashing the blob at that revision is what makes the pin re-derivable years
    later, and it is the only form of the check a fabricated report cannot pass:
    the bytes have to have existed at a commit that exists.
    """
    proc = subprocess.run(
        ["git", "cat-file", "blob", f"{rev}:{path_text}"],
        cwd=str(cwd), stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
    )
    if proc.returncode != 0:
        return None
    return hashlib.sha256(proc.stdout).hexdigest()


def rev_exists(rev, cwd):
    """True iff `rev` names a real commit in the repo at `cwd`."""
    return subprocess.run(
        ["git", "rev-parse", "--verify", "--quiet", f"{rev}^{{commit}}"],
        cwd=str(cwd), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    ).returncode == 0


def load(report_path):
    report = Path(report_path)
    try:
        text = report.read_text(encoding="utf-8")
    except OSError as err:
        raise InventoryError(f"{report_path} is unreadable: {err}") from err
    lines = text.splitlines()
    entries = []
    for start, end in find_blocks(lines):
        entries.extend(parse_entries(lines, start, end))
    return report, lines, entries


def check_entries(entries, report, root, at=None):
    """(matched, mismatched, missing) for one inventory, in the tree or at a rev."""
    matched, mismatched, missing = [], [], []
    for _idx, path_text, recorded, _shape in entries:
        if at:
            actual = sha256_at(at, path_text, root or report.parent)
            if actual is None:
                missing.append(path_text)
                continue
        else:
            resolved = resolve(path_text, report, root)
            if resolved is None:
                missing.append(path_text)
                continue
            try:
                actual = sha256_file(resolved)
            except OSError as err:
                raise InventoryError(f"{path_text} could not be hashed: {err}") from err
        if actual == recorded:
            matched.append(path_text)
        else:
            mismatched.append((path_text, recorded, actual))
    return matched, mismatched, missing


def cmd_check(args):
    report, _lines, entries = load(args.report)
    root = repo_root(report.parent if report.parent.exists() else Path("."))
    at = getattr(args, "at", None)
    if at and not rev_exists(at, root or report.parent):
        raise InventoryError(f"--at {at} is not a commit in this repo")
    matched, mismatched, missing = check_entries(entries, report, root, at)
    if not matched and not mismatched:
        raise InventoryError(
            f"none of the {len(entries)} listed path(s) exist" + (f" at {at}" if at else "")
            + " — nothing was verified; "
            "re-derive the hashes at the commit the report names")
    for path_text, recorded, actual in mismatched:
        print(f"MISMATCH {path_text}\n  recorded {recorded}\n  actual   {actual}", file=sys.stderr)
    where = f"the tree at {at}" if at else "the tree"
    for path_text in missing:
        print(f"MISSING  {path_text} (not present in {where} — not a mismatch)")
    print(f"inventory: {len(matched)} verified, {len(mismatched)} mismatched, "
          f"{len(missing)} missing, in {args.report}" + (f" at {at}" if at else ""))
    return EXIT_MISMATCH if mismatched else EXIT_OK


def cmd_write(args):
    report, lines, entries = load(args.report)
    root = repo_root(report.parent if report.parent.exists() else Path("."))
    updated, absent = 0, []
    for idx, path_text, recorded, _shape in entries:
        resolved = resolve(path_text, report, root)
        if resolved is None:
            absent.append(path_text)
            continue
        actual = sha256_file(resolved)
        if actual == recorded:
            continue
        # Exactly one 64-hex token per entry line; replace it in place so the
        # surrounding formatting (fence or table cell) survives untouched.
        lines[idx] = re.sub(r"[0-9a-fA-F]{64}", actual, lines[idx], count=1)
        updated += 1
    if absent:
        for path_text in absent:
            print(f"inventory: cannot hash {path_text} — it does not exist", file=sys.stderr)
        return EXIT_MISMATCH
    if args.dry_run:
        print(f"inventory: would update {updated} hash(es) in {args.report}")
        return EXIT_OK
    try:
        report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    except OSError as err:
        raise InventoryError(f"{args.report} could not be written: {err}") from err
    print(f"inventory: updated {updated} hash(es) in {args.report}")
    return EXIT_OK


def build_parser():
    p = argparse.ArgumentParser(
        prog="inventory.py",
        description="Regenerate or re-check the sha256 integrity inventory embedded in a report.",
        epilog="exit 0 verified / 1 mismatch / 2 could-not-run (no block, or nothing verifiable)",
    )
    sub = p.add_subparsers(dest="command", required=True)
    w = sub.add_parser("write", help="re-hash every listed path and rewrite the block in place")
    w.add_argument("report", help="markdown report carrying the inventory block")
    w.add_argument("--dry-run", action="store_true", help="report what would change, write nothing")
    c = sub.add_parser("check", help="re-hash every listed path that exists")
    c.add_argument("report", help="markdown report carrying the inventory block")
    c.add_argument(
        "--at",
        metavar="REV",
        help="hash each path as it was at this git revision instead of in the working "
             "tree — the form a dated report's pins stay re-derivable in",
    )
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    handlers = {"write": cmd_write, "check": cmd_check}
    try:
        return handlers[args.command](args)
    except InventoryError as err:
        print(f"inventory: could not run: {err}", file=sys.stderr)
        return EXIT_CANNOT_RUN


if __name__ == "__main__":
    sys.exit(main())
