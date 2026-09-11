#!/usr/bin/env python3
"""Content-free, hash-chained receipts for everything the fleet sends off-repo.

The run-close integrity inventory hashes what the fleet PRODUCED. Nothing
records what it SENT. This ledger is the second half: one line per off-repo
write the fleet performs -- opening a PR, posting a comment, closing an issue,
triggering a deploy, creating a schedule -- appended BEFORE the send.

Status, stated first because it bounds what this is worth today: this ledger
has no caller (#284). No mission or playbook invokes it, so the receipts it
describes are not being written. It is a working library waiting to be wired
into the fleet's own sinks, not a guarantee in force -- read every sentence
below as what it WILL record once called, not what is recorded now.

Threat model, stated because it bounds what this is worth even then: the
ledger is forensic observability, not an exfiltration control. It records ATTEMPTED
egress so an accident is auditable afterwards. Anything with a shell can send
without a receipt; the point is that the fleet's own sinks cannot do so
silently.

Record (one JSON object per line, ``.orca/egress.jsonl``, mode 0600)::

    {"id", "ts", "sink", "host", "payload_class", "bytes",
     "payload_sha256", "consent", "prev"}

* **Content-free.** Never the payload text: a sha256 of the exact bytes sent
  and a byte count, and a ``payload_class`` that describes the KIND of thing
  sent ("pr-body", "issue-comment"). ``payload_sha256`` is null when a
  subprocess owns the bytes and the fleet never saw them.
* **Tamper-evident.** ``prev`` is the sha256 of the previous raw line (``""``
  on line 1), so any edit to an earlier line breaks every later one. ``id`` is
  the sha256 of this record's own fields including ``prev`` -- it names the
  line and its position in the chain at once.
* **Fail-closed on write.** A sink that cannot write its receipt must not
  send. ``write`` exits 3 in that case, so the caller's ``&&`` stops.
* **Consent is a field, not a vibe.** Every receipt names the standing grant
  that authorizes the send; ``grants`` lists them so a human can see what the
  fleet believes it is allowed to do.

Subcommands
    write    append one receipt, print its id
    verify   recompute the whole chain
    grants   list the distinct consents, with sink/host and use counts

Exit codes
    0  ok (``verify``: the chain is intact)
    2  usage -- a missing or malformed argument
    3  fail-closed: the receipt could not be written, or ``verify`` found a
       broken/unparseable line. Never treat a 3 as permission to send.

How to wire
    Every off-repo write the coordinator itself performs is preceded by
    ``egress.py write ... && <the send>`` -- the ``&&`` is the fail-closed
    coupling, since exit 3 stops the send. ``--payload-file`` hashes the exact
    bytes about to go out (a PR body written to a file first), so a later
    dispute compares hashes rather than memories. Per-worker network egress is
    NOT covered here and cannot be without a proxy: that stays a sandbox-policy
    requirement for the disposable lane, stated rather than claimed. At run
    close, ``verify`` runs beside the integrity inventory and the two together
    answer "what did this run produce, and what left the machine".

    Example: ``egress.py write --sink pr-open --host github.com
    --payload-class pr-body --payload-file /tmp/body.md --consent
    grant:pr-open-on-base && gh pr create --body-file /tmp/body.md``
"""
import argparse
import hashlib
import json
import os
import stat
import sys
from datetime import datetime, timezone
from pathlib import Path

EXIT_OK = 0
EXIT_USAGE = 2
EXIT_FAIL_CLOSED = 3

DEFAULT_LEDGER = ".orca/egress.jsonl"
LEDGER_ENV = "ORCA_EGRESS_LEDGER"
# Field order is fixed so `id` is reproducible byte-for-byte on re-verification.
FIELDS = ("ts", "sink", "host", "payload_class", "bytes", "payload_sha256", "consent", "prev")
MAX_FIELD_BYTES = 512


class EgressError(Exception):
    """Fail-closed condition: the receipt could not be written."""


def sha256_hex(data):
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def ledger_path(explicit=None):
    if explicit:
        return Path(explicit)
    env = os.environ.get(LEDGER_ENV)
    if env:
        return Path(env)
    return Path(DEFAULT_LEDGER)


def record_id(record):
    """sha256 over the record's fields in fixed order, chain position included."""
    payload = "\n".join(f"{k}={json_scalar(record.get(k))}" for k in FIELDS)
    return sha256_hex(payload)


def json_scalar(value):
    return "" if value is None else str(value)


def last_raw_line(path):
    try:
        with path.open("rb") as fh:
            lines = [ln for ln in fh.read().split(b"\n") if ln]
    except FileNotFoundError:
        return None
    except OSError as err:
        raise EgressError(f"{path} is unreadable: {err}") from err
    if not lines:
        return None
    return lines[-1].decode("utf-8", errors="replace")


def require_field(value, name):
    if not value or not str(value).strip():
        raise EgressError(f"receipt requires a non-empty {name}")
    text = str(value)
    if len(text.encode("utf-8")) > MAX_FIELD_BYTES:
        raise EgressError(f"receipt {name} exceeds {MAX_FIELD_BYTES} bytes")
    if "\n" in text or "\r" in text:
        raise EgressError(f"receipt {name} may not contain a newline (one receipt, one line)")
    return text


def write_receipt(path, sink, host, payload_class, consent, nbytes=0, payload_sha256=None, ts=None):
    """Append one chained receipt. Raises EgressError on any failure (fail closed)."""
    record = {
        "ts": ts or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "sink": require_field(sink, "sink"),
        "host": require_field(host, "host"),
        "payload_class": require_field(payload_class, "payload_class"),
        "bytes": int(nbytes),
        "payload_sha256": payload_sha256,
        "consent": require_field(consent, "consent"),
    }
    if record["bytes"] < 0:
        raise EgressError("receipt bytes must be a non-negative integer")
    if payload_sha256 is not None and not _is_sha256(payload_sha256):
        raise EgressError("payload_sha256 must be 64 lowercase hex characters or absent")
    try:
        if not path.parent.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            os.chmod(path.parent, stat.S_IRWXU)  # 0700: the ledger dir is private
        previous = last_raw_line(path)
        record["prev"] = "" if previous is None else sha256_hex(previous)
        record["id"] = record_id(record)
        line = json.dumps({"id": record["id"], **{k: record[k] for k in FIELDS}},
                          separators=(",", ":"), sort_keys=False)
        existed = path.exists()
        with path.open("a", encoding="utf-8") as fh:
            fh.write(line + "\n")
        if not existed:
            os.chmod(path, stat.S_IRUSR | stat.S_IWUSR)
    except EgressError:
        raise
    except OSError as err:
        raise EgressError(f"receipt could not be written to {path}: {err}") from err
    return record


def _is_sha256(value):
    return isinstance(value, str) and len(value) == 64 and all(
        c in "0123456789abcdef" for c in value)


def read_ledger(path):
    """[(lineno, raw, record-or-None)]. A missing ledger is an empty chain."""
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return []
    except OSError as err:
        raise EgressError(f"{path} is unreadable: {err}") from err
    out = []
    for i, raw in enumerate([ln for ln in text.split("\n") if ln], 1):
        try:
            parsed = json.loads(raw)
            record = parsed if isinstance(parsed, dict) else None
        except ValueError:
            record = None
        out.append((i, raw, record))
    return out


def verify_ledger(path):
    """Recompute the chain. Returns (ok, count, broken_line, reason)."""
    lines = read_ledger(path)
    previous_raw = None
    for lineno, raw, record in lines:
        if record is None or not isinstance(record.get("prev"), str):
            return False, len(lines), lineno, "unparseable line or missing prev"
        expected_prev = "" if previous_raw is None else sha256_hex(previous_raw)
        if record["prev"] != expected_prev:
            return False, len(lines), lineno, "prev does not match the previous raw line"
        if record.get("id") != record_id(record):
            return False, len(lines), lineno, "id does not match the record's own fields"
        previous_raw = raw
    return True, len(lines), None, None


def cmd_write(args):
    path = ledger_path(args.ledger)
    payload_sha = args.payload_sha256
    nbytes = args.bytes
    if args.payload_file:
        try:
            data = Path(args.payload_file).read_bytes()
        except OSError as err:
            print(f"egress: payload file unreadable: {err}", file=sys.stderr)
            return EXIT_USAGE
        payload_sha = sha256_hex(data)
        if nbytes is None:
            nbytes = len(data)
    record = write_receipt(
        path, args.sink, args.host, args.payload_class, args.consent,
        nbytes=nbytes or 0, payload_sha256=payload_sha, ts=args.ts,
    )
    print(record["id"])
    return EXIT_OK


def cmd_verify(args):
    path = ledger_path(args.ledger)
    ok, count, broken, reason = verify_ledger(path)
    if ok:
        print(f"egress: chain intact, {count} receipt(s) in {path}")
        return EXIT_OK
    print(f"egress: TAMPER at {path}:{broken} — {reason} ({count} line(s) read)", file=sys.stderr)
    return EXIT_FAIL_CLOSED


def cmd_grants(args):
    path = ledger_path(args.ledger)
    grants = {}
    for _lineno, _raw, record in read_ledger(path):
        if not record:
            continue
        key = record.get("consent", "(none)")
        entry = grants.setdefault(key, {"consent": key, "uses": 0, "sinks": set(), "hosts": set()})
        entry["uses"] += 1
        entry["sinks"].add(record.get("sink", ""))
        entry["hosts"].add(record.get("host", ""))
    rows = [
        {"consent": g["consent"], "uses": g["uses"],
         "sinks": sorted(s for s in g["sinks"] if s),
         "hosts": sorted(h for h in g["hosts"] if h)}
        for g in sorted(grants.values(), key=lambda g: g["consent"])
    ]
    if args.json:
        print(json.dumps(rows, indent=2))
    else:
        if not rows:
            print(f"egress: no consents recorded in {path}")
        for row in rows:
            print(f"{row['consent']}  uses={row['uses']}  sinks={','.join(row['sinks'])}  "
                  f"hosts={','.join(row['hosts'])}")
    return EXIT_OK


def build_parser():
    p = argparse.ArgumentParser(
        prog="egress.py",
        description="Content-free hash-chained receipts for off-repo sends.",
        epilog="exit 0 ok / 2 usage / 3 fail-closed (receipt unwritable, or chain tampered)",
    )
    p.add_argument("--ledger", default=None,
                   help=f"ledger path (default ${LEDGER_ENV} or {DEFAULT_LEDGER})")
    sub = p.add_subparsers(dest="command", required=True)

    w = sub.add_parser("write", help="append one receipt BEFORE the send")
    w.add_argument("--sink", required=True, help="which fleet component is sending, e.g. pr-open")
    w.add_argument("--host", required=True, help="destination host[:port]")
    w.add_argument("--payload-class", required=True, dest="payload_class",
                   help="content-free description of the payload kind, e.g. pr-body")
    w.add_argument("--consent", required=True, help="the standing grant that authorizes this send")
    w.add_argument("--bytes", type=int, default=None, help="exact byte count (default 0, or the payload file's size)")
    w.add_argument("--payload-file", default=None, help="file whose exact bytes are being sent; hashed, never stored")
    w.add_argument("--payload-sha256", default=None, dest="payload_sha256",
                   help="sha256 of the bytes, when a subprocess owns them")
    w.add_argument("--ts", default=None, help="ISO timestamp (default: now, UTC)")

    v = sub.add_parser("verify", help="recompute the hash chain")
    v.add_argument("--json", action="store_true", help=argparse.SUPPRESS)

    g = sub.add_parser("grants", help="list the standing consents the ledger records")
    g.add_argument("--json", action="store_true", help="emit JSON")
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    handlers = {"write": cmd_write, "verify": cmd_verify, "grants": cmd_grants}
    try:
        return handlers[args.command](args)
    except EgressError as err:
        print(f"egress: EGRESS_RECEIPT_FAILED: {err}", file=sys.stderr)
        return EXIT_FAIL_CLOSED


if __name__ == "__main__":
    sys.exit(main())
