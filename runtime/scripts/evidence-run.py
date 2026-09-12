#!/usr/bin/env python3
"""evidence-run.py — the content-bound evidence ledger's RUNNER.

"Tests pass at that exact SHA in a clean env" was doctrine: a sentence in evidence-manifest.md §2
addressed to the coordinator, with no field any verifier read (docs/reviews/2026-09-10-review.md §4, U1 — UNTESTABLE).
This wrapper makes it a record, and `verify.py check_commands` makes that record a gate.

    evidence-run.py --label tests --manifest docs/reports/<unit>/manifest.json -- pytest -q
    evidence-run.py --label tests --manifest m.json --artifact docs/reports/u/test.txt -- make test

It is a TRANSPARENT wrapper, and that is load-bearing: the child's stdout/stderr pass through and
the child's exit code is ALWAYS this process's exit code. EVERY bookkeeping failure — an unwritable
manifest, a missing fingerprint, a non-git directory — is a stderr warning and nothing more. A
wrapper that can turn green tests red would be routed around within a week, and then the ledger
records nothing at all.

One record is appended to the manifest's `commands[]`:

    {"label", "ts", "cmd", "cmd_sha256", "exit", "duration_s", "commit", "wtree", "artifact"}

  - `cmd` is the exact command line (shlex.join of argv) and `cmd_sha256` its sha256, with no
    normalization — so a check can demand THIS command and not a similar one;
  - `commit` is HEAD at the time of the run (may be null in a repo with no commits);
  - `wtree` is `wtree.sh`'s working-tree content fingerprint — the freshness key. verify.py
    requires an exit-0 record whose `wtree` equals `git rev-parse <head_sha>^{tree}`, i.e. the run
    happened on exactly the content the head commit carries. A record made on other content is
    STALE and does not certify the head.

The manifest is created (`{"commands": []}`) if absent, so a unit can start recording before it has
anything else to say. Ported in shape from gstack `bin/gstack-evidence` (MIT); see
docs/research/2026-09-10-upstream-audit/gstack.md §4.1. Unlike upstream's advisory `check`, the
downstream gate is FAIL-CLOSED.

Exit: the child's exit code · 1 only when there is no child to run (usage / exec failure).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shlex
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
CHUNK = 65536


def warn(msg):
    """Bookkeeping problems are reported, never fatal — see the transparency invariant above."""
    print(f"evidence-run: WARNING — {msg}", file=sys.stderr)


def git_out(args, cwd):
    try:
        p = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True,
                           timeout=30, check=False)
    except (subprocess.TimeoutExpired, OSError) as err:
        return None, str(err)
    if p.returncode != 0:
        return None, (p.stderr.strip() or f"git {args[0]} exited {p.returncode}")
    return p.stdout.strip(), None


def working_tree_fingerprint(cwd):
    """`wtree.sh` — the content fingerprint the freshness check binds to."""
    script = HERE / "wtree.sh"
    if not script.exists():
        return None, f"{script} is missing"
    try:
        p = subprocess.run(["sh", str(script), str(cwd)], capture_output=True, text=True,
                           timeout=120, check=False)
    except (subprocess.TimeoutExpired, OSError) as err:
        return None, str(err)
    out = p.stdout.strip()
    if p.returncode != 0 or not out:
        return None, (p.stderr.strip() or "no fingerprint (not a git repo, or no commits)")
    return out, None


def run_child(argv, artifact_path, cwd):
    """Run the child transparently. With an artifact, output is TEED — streamed to this process's
    stdout as it arrives AND written to the artifact file, so the evidence file and what a human
    watched are the same bytes."""
    started = time.monotonic()
    if artifact_path is None:
        try:
            code = subprocess.run(argv, cwd=cwd, check=False).returncode
        except OSError as err:
            print(f"evidence-run: cannot execute {argv[0]!r}: {err}", file=sys.stderr)
            return None, time.monotonic() - started
        return code, time.monotonic() - started
    try:
        artifact_path.parent.mkdir(parents=True, exist_ok=True)
        sink = artifact_path.open("wb")
    except OSError as err:
        warn(f"cannot open artifact {artifact_path}: {err} — running without it")
        return run_child(argv, None, cwd)
    try:
        try:
            proc = subprocess.Popen(argv, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        except OSError as err:
            print(f"evidence-run: cannot execute {argv[0]!r}: {err}", file=sys.stderr)
            return None, time.monotonic() - started
        with proc:
            while True:
                chunk = proc.stdout.read(CHUNK) if proc.stdout else b""
                if not chunk:
                    break
                sys.stdout.buffer.write(chunk)
                sys.stdout.buffer.flush()
                sink.write(chunk)
        return proc.returncode, time.monotonic() - started
    finally:
        sink.close()


def append_record(manifest_path, record):
    """Append to `commands[]`, creating the manifest if absent. Never raises."""
    try:
        if manifest_path.exists():
            data = json.loads(manifest_path.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                warn(f"{manifest_path} is not a JSON object — not recording")
                return
        else:
            manifest_path.parent.mkdir(parents=True, exist_ok=True)
            data = {"commands": []}
        commands = data.setdefault("commands", [])
        if not isinstance(commands, list):
            warn(f"{manifest_path} has a non-list 'commands' — not recording")
            return
        commands.append(record)
        data["commands"] = commands
        manifest_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    except (OSError, json.JSONDecodeError, ValueError, TypeError) as err:
        warn(f"could not record into {manifest_path}: {err}")


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Run a command and record a content-bound evidence entry in the manifest.")
    ap.add_argument("--label", required=True, help="what this run proves, e.g. 'tests' / 'lint'")
    ap.add_argument("--manifest", required=True,
                    help="the unit's evidence manifest JSON (relative to --cwd)")
    ap.add_argument("--artifact", default=None,
                    help="path to tee output into (relative to --cwd, recorded on the entry)")
    ap.add_argument("--cwd", default=None, help="directory to run in (default: the current one)")
    ap.add_argument("command", nargs=argparse.REMAINDER,
                    help="-- followed by the command to run (argv, never a shell line)")
    args = ap.parse_args(argv)

    cmd = args.command[1:] if args.command[:1] == ["--"] else args.command
    if not cmd:
        ap.error("no command given — use: evidence-run.py --label L --manifest m.json -- <cmd...>")

    cwd = Path(args.cwd).resolve() if args.cwd else Path.cwd()
    artifact = Path(args.artifact) if args.artifact else None
    artifact_fs = (cwd / artifact) if (artifact and not artifact.is_absolute()) else artifact

    # Fingerprint BEFORE the run: the record must describe the content the command was given, not
    # the content plus whatever the run (and this wrapper's own artifact/manifest writes) left
    # behind. Run from a CLEAN tree at head_sha and this equals `git rev-parse <head_sha>^{tree}`,
    # which is exactly what verify.py's commands check demands.
    wtree, err = working_tree_fingerprint(cwd)
    if err:
        warn(f"no working-tree fingerprint recorded: {err} — verify.py's commands check will treat "
             "this record as STALE")

    code, duration = run_child(cmd, artifact_fs, cwd)
    if code is None:
        return 1

    line = shlex.join(cmd)
    commit, err = git_out(["rev-parse", "HEAD"], cwd)
    if err:
        warn(f"no HEAD commit recorded: {err}")
    append_record(cwd / args.manifest, {
        "label": args.label,
        "ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "cmd": line,
        "cmd_sha256": hashlib.sha256(line.encode("utf-8")).hexdigest(),
        "exit": code,
        "duration_s": round(duration, 3),
        "commit": commit,
        "wtree": wtree,
        "artifact": os.fspath(artifact) if artifact else None,
    })
    return code


if __name__ == "__main__":
    sys.exit(main())
