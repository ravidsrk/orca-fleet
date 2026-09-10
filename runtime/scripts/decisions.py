#!/usr/bin/env python3
"""Writer, reader and validator for the DECISIONS log.

``docs/DECISIONS.md`` was a parser without a writer: the scope-gated review
playbook reads it mechanically to decide whether a lens has earned its
auto-gate-off, but every line was hand-typed, so two coordinators could disagree
about the same log. This is the writer, and the same rules run as a check over a
file somebody else wrote.

Line format (runtime/ledger-contract.md, "DECISIONS log")::

    ts · gate-or-ask-id · class · answer · why · task_id?

``·`` (U+00B7) separates fields; the trailing ``task_id`` is optional. ``class``
is one of ``mechanical`` (one defensible answer), ``taste`` (reasonable
disagreement, reversible) or ``one-way`` (hard to reverse or out of authority).

What ``append`` refuses to write, and why each refusal exists:

* an unknown class, an empty id, an empty answer, or an empty ``why`` -- a
  decision nobody can reconstruct is not a record, and "why" is the field that
  makes the log re-readable by a fresh coordinator;
* a field containing ``·`` or a newline -- one record, one line;
* anything shaped like a credential (see ``SECRET_SHAPES``) -- the log is
  committed and permanent, so a pasted token in a "why" is permanent too. The
  refusal names the shape, never the value;
* a line whose text matches the one-way keyword net in
  ``runtime/one-way-doors.json`` but whose class is NOT ``one-way`` -- an agent
  must not be able to reclassify its own gate by choosing a milder word;
* a ``one-way`` line with no human source -- one-way doors are human-only, so
  the line must carry ``source=human:<name>`` (written into the ``why`` field,
  which keeps the format at six fields). ``--source`` supplies it.

Subcommands
    append   validate and append one line
    active   list the non-superseded lines (the newest line for an id wins; an
             answer of exactly ``superseded`` retires the id entirely)
    tally    ``--lens <name>``: read ``lens-tally:<lens>`` lines newest-first and
             report the streak of consecutive zero-finding dispatches, plus
             whether that lens may auto-gate off (10+ zeros, and the lens is not
             one of the never-gate lenses)
    check    run every append-time rule over an existing file

Exit codes
    0  ok
    1  a validation failure (refused append, or ``check`` found a violation)
    2  could not run -- unreadable file, missing/invalid door registry, usage

How to wire
    The coordinator appends one line per mechanical or taste auto-resolve and one
    per human-answered one-way gate, so the log is the durable record RESUME
    re-reads before re-asking a question a previous coordinator already settled.
    The scope-gated review playbook appends ``lens-tally:<lens>`` with the
    dispatch's finding count as the answer, and calls ``tally --lens`` BEFORE
    dispatching: the gate verdict then comes from committed state that survives a
    crashed run, not from one coordinator's memory. An independent verifier runs
    ``check`` over the file: a line that trips the one-way net without the class
    and the human source fails the run, which is the machine form of "one-way is
    never auto-resolved".

    Example: ``decisions.py append --id lens-tally:security --class mechanical
    --answer 0 --why "diff touched no auth surface" --task t-14``
"""
import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

EXIT_OK = 0
EXIT_VIOLATION = 1
EXIT_CANNOT_RUN = 2

SEP = " · "
SEP_CHAR = "·"
CLASSES = ("mechanical", "taste", "one-way")
DEFAULT_LOG = "docs/DECISIONS.md"
DEFAULT_DOORS = Path(__file__).resolve().parent.parent / "one-way-doors.json"

# Lenses whose value IS the miss they would catch: they never auto-gate off, however
# long their zero streak runs. This tuple is the EXECUTABLE form of the sentence in
# playbooks/risk-review.md; `tests/test_decisions.py` parses that sentence and requires
# the two to agree, because a policy naming three lenses and a gate enforcing two is how
# privacy silently switched itself off after ten quiet reviews (PR #277 review, P1).
NEVER_GATE = ("security", "privacy", "data-migration")
GATE_OFF_STREAK = 10

HUMAN_SOURCE = re.compile(r"source=human:\S+")
TS_PREFIX = re.compile(r"^\d{4}-\d{2}-\d{2}")

# Shapes, not values. A match is reported by NAME; the matched text is never echoed.
SECRET_SHAPES = [
    ("aws-access-key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("github-token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}")),
    ("slack-token", re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}")),
    ("private-key-block", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("bearer-literal", re.compile(r"\b(Bearer|Authorization:)\s+[A-Za-z0-9._\-]{20,}")),
    ("provider-secret-key", re.compile(r"\bsk-[A-Za-z0-9]{20,}")),
    ("assigned-secret", re.compile(
        r"\b(password|passwd|secret|token|api[_-]?key|access[_-]?key)\b\s*[=:]\s*[\"']?[A-Za-z0-9/+._\-]{12,}")),
]


class DecisionsError(Exception):
    """Could-not-run: unreadable log, missing or invalid door registry."""


def load_doors(path=None):
    p = Path(path) if path else DEFAULT_DOORS
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError) as err:
        raise DecisionsError(f"one-way door registry {p} is unusable: {err}") from err
    doors = data.get("doors")
    if not isinstance(doors, list) or not doors:
        raise DecisionsError(f"one-way door registry {p} declares no doors")
    net = []
    for door in doors:
        did = door.get("id")
        keywords = door.get("keywords") or []
        if not did or not isinstance(keywords, list) or not keywords:
            raise DecisionsError(f"one-way door registry {p}: door {did!r} has no keyword net")
        for kw in keywords:
            net.append((did, str(kw).lower()))
    return net


def fold(text):
    return re.sub(r"\s+", " ", text).strip().lower()


def door_hits(text, net):
    probe = fold(text)
    return sorted({door_id for door_id, kw in net if kw in probe})


def secret_hits(text):
    return sorted({name for name, pattern in SECRET_SHAPES if pattern.search(text)})


def format_line(ts, ident, klass, answer, why, task_id=None):
    fields = [ts, ident, klass, answer, why]
    if task_id:
        fields.append(task_id)
    return SEP.join(fields)


def parse_line(line):
    """Return a dict for a DECISIONS record line, or None when the line is prose.

    A record is identified by its FIRST field being an ISO date. Without that
    test the file's own format legend (``ts · gate-or-ask-id · class · …``)
    parses as a record and fails its own check.
    """
    if SEP_CHAR not in line:
        return None
    parts = [p.strip() for p in line.strip().lstrip("-*# ").split(SEP_CHAR)]
    if len(parts) < 5:
        return None
    if not TS_PREFIX.match(parts[0].strip("`")):
        return None
    parts[0] = parts[0].strip("`")
    record = {
        "ts": parts[0], "id": parts[1], "class": parts[2],
        "answer": parts[3], "why": SEP_CHAR.join(parts[4:5]),
        "task_id": parts[5] if len(parts) > 5 else "",
        "raw": line.rstrip("\n"),
    }
    if len(parts) > 6:
        record["why"] = SEP_CHAR.join(parts[4:-1])
        record["task_id"] = parts[-1]
    return record


def validate(record, net):
    """Return a list of violation strings for one parsed record."""
    problems = []
    if not record["id"]:
        problems.append("empty gate-or-ask id")
    if record["class"] not in CLASSES:
        problems.append(f"class {record['class']!r} is not one of {', '.join(CLASSES)}")
    if not record["answer"]:
        problems.append("empty answer")
    if not record["why"]:
        problems.append("empty why (a decision nobody can reconstruct is not a record)")
    shapes = secret_hits(record["raw"])
    if shapes:
        problems.append(f"credential-shaped text ({', '.join(shapes)}) — the log is permanent")
    hits = door_hits(record["raw"], net)
    if hits and record["class"] != "one-way":
        problems.append(
            f"matches the one-way net ({', '.join(hits)}) but is classed {record['class']!r} — "
            "one-way doors are human-only and are never auto-resolved"
        )
    if record["class"] == "one-way" and not HUMAN_SOURCE.search(record["raw"]):
        problems.append("class one-way with no human source — needs source=human:<name>")
    return problems


def read_lines(path):
    p = Path(path)
    if not p.exists():
        return []
    try:
        text = p.read_text(encoding="utf-8")
    except OSError as err:
        raise DecisionsError(f"{path} is unreadable: {err}") from err
    out = []
    for i, line in enumerate(text.splitlines(), 1):
        record = parse_line(line)
        if record:
            record["lineno"] = i
            out.append(record)
    return out


def active(records):
    """Newest line per id wins; an answer of exactly 'superseded' retires the id."""
    latest = {}
    for record in records:
        latest[record["id"]] = record
    return [r for r in latest.values() if r["answer"].strip().lower() != "superseded"]


def tally(records, lens):
    """Consecutive zero-finding dispatches for a lens, newest-first."""
    ident = f"lens-tally:{lens}"
    rows = [r for r in records if r["id"] == ident]
    streak = 0
    for record in reversed(rows):
        if re.fullmatch(r"0+", record["answer"].strip()):
            streak += 1
        else:
            break
    never = lens in NEVER_GATE
    return {
        "lens": lens,
        "dispatches": len(rows),
        "zero_streak": streak,
        "never_gate": never,
        "may_gate_off": (not never) and streak >= GATE_OFF_STREAK,
    }


def cmd_append(args, net):
    ts = args.ts or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    why = args.why
    if args.source:
        if not re.fullmatch(r"human:\S+", args.source):
            print("decisions: --source must be shaped human:<name>", file=sys.stderr)
            return EXIT_VIOLATION
        if f"source={args.source}" not in why:
            why = f"{why} [source={args.source}]"
    for name, value in (("id", args.id), ("answer", args.answer), ("why", why),
                        ("task", args.task or "")):
        if SEP_CHAR in value or "\n" in value:
            print(f"decisions: {name} may not contain '{SEP_CHAR}' or a newline "
                  "(one record, one line)", file=sys.stderr)
            return EXIT_VIOLATION
    line = format_line(ts, args.id.strip(), args.klass, args.answer.strip(), why.strip(),
                       (args.task or "").strip())
    record = parse_line(line)
    if record is None:
        print("decisions: refusing to write an unparseable line", file=sys.stderr)
        return EXIT_VIOLATION
    record["lineno"] = 0
    problems = validate(record, net)
    if problems:
        print("decisions: refused:", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        return EXIT_VIOLATION
    path = Path(args.file)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        exists = path.exists()
        with path.open("a", encoding="utf-8") as fh:
            if not exists:
                fh.write("# DECISIONS\n\n"
                         "`ts · gate-or-ask-id · class · answer · why · task_id?`\n\n")
            fh.write(line + "\n")
    except OSError as err:
        raise DecisionsError(f"{path} could not be appended: {err}") from err
    print(line)
    return EXIT_OK


def cmd_active(args, _net):
    records = read_lines(args.file)
    rows = active(records)
    if args.json:
        print(json.dumps([{k: r[k] for k in ("ts", "id", "class", "answer", "why", "task_id")}
                          for r in rows], indent=2))
    else:
        for r in rows:
            print(r["raw"])
    return EXIT_OK


def cmd_tally(args, _net):
    records = read_lines(args.file)
    result = tally(records, args.lens)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        gate = "may auto-gate off" if result["may_gate_off"] else (
            "NEVER_GATE" if result["never_gate"] else "stays on")
        print(f"lens={result['lens']} dispatches={result['dispatches']} "
              f"zero_streak={result['zero_streak']} → {gate}")
    return EXIT_OK


def cmd_check(args, net):
    records = read_lines(args.file)
    failures = []
    for record in records:
        for problem in validate(record, net):
            failures.append(f"{args.file}:{record['lineno']}: {problem}")
    if failures:
        for f in failures:
            print(f, file=sys.stderr)
        return EXIT_VIOLATION
    print(f"decisions: {len(records)} record(s) valid in {args.file}")
    return EXIT_OK


def build_parser():
    p = argparse.ArgumentParser(
        prog="decisions.py",
        description="Append to, read and validate the DECISIONS log.",
        epilog="exit 0 ok / 1 validation failure / 2 could-not-run",
    )
    p.add_argument("--file", default=DEFAULT_LOG, help=f"DECISIONS log path (default {DEFAULT_LOG})")
    p.add_argument("--doors", default=None, help="one-way door registry (default runtime/one-way-doors.json)")
    sub = p.add_subparsers(dest="command", required=True)

    a = sub.add_parser("append", help="validate and append one decision line")
    a.add_argument("--id", required=True, help="gate or ask id, e.g. lens-tally:security")
    a.add_argument("--class", dest="klass", required=True, choices=CLASSES, help="decision class")
    a.add_argument("--answer", required=True, help="what was decided (a finding count, for a lens tally)")
    a.add_argument("--why", required=True, help="why — never empty")
    a.add_argument("--task", default=None, help="optional task id")
    a.add_argument("--source", default=None, help="human:<name> — required for class one-way")
    a.add_argument("--ts", default=None, help="ISO timestamp (default: now, UTC)")

    sub.add_parser("active", help="list non-superseded decisions").add_argument(
        "--json", action="store_true", help="emit JSON")

    t = sub.add_parser("tally", help="zero-finding dispatch streak for a lens")
    t.add_argument("--lens", required=True, help="lens name, e.g. security")
    t.add_argument("--json", action="store_true", help="emit JSON")

    sub.add_parser("check", help="validate an existing log")
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    handlers = {"append": cmd_append, "active": cmd_active, "tally": cmd_tally, "check": cmd_check}
    try:
        net = load_doors(args.doors)
        return handlers[args.command](args, net)
    except DecisionsError as err:
        print(f"decisions: could not run: {err}", file=sys.stderr)
        return EXIT_CANNOT_RUN


if __name__ == "__main__":
    sys.exit(main())
