#!/usr/bin/env python3
"""search_sessions.py — orca search with an --index-status precheck (S19).

Upstream argv (pinned specs/search.ts, handlers/search.ts,
shared/ai-vault-search-contract.ts):

* ``search --index-status`` answers ``{enabled, phase, filesIndexed, filesDue,
  filesFailed, …}`` with phase ∈ idle|indexing|current|degraded|closed. This
  wrapper runs it FIRST: enabled=false or phase ∈ {degraded, closed} refuses
  (exit 2) before the query fires — searching an index the host reports broken
  proves nothing. current/idle/indexing proceed (--fresh asks the host to
  reconcile first, then searches anyway).
* ``search <query>|--query … [--scope conversation|all] [--fresh] [--limit 1-100]
  [--cursor …] [--agent …]* [--path …]* [--since <iso>] [--sort relevance|newest]
  [--debug]``. The query rides positionally or as --query, never both (upstream
  reads unquoted words as command names). --limit caps at 100; --since must be
  ISO 8601 with an offset.

Results answers print HITS=/NEXT_CURSOR=; stale-cursor, malformed-cursor, and
unavailable are failures (exit 1), never empty results. --precheck-only runs
just the verdict. Live index behavior is PARKED (needs-human: run against a
host mid-indexing and confirm phase gating).

Exit: 0 ok · 1 runtime/refusal/receipt failure · 2 usage/precheck refusal.
"""
import argparse
import datetime
import json
import subprocess
import sys

EXIT_OK = 0
EXIT_FAILED = 1
EXIT_REFUSED = 2

GOOD_PHASES = ("current", "idle", "indexing")
SCOPES = ("conversation", "all")
SORTS = ("relevance", "newest")


class Refused(Exception):
    """Usage/validation/precheck refusal: exit 2, the query never fired."""


class Failed(Exception):
    """The runtime refused or the receipt is unreadable: exit 1."""


def _nonempty(value, flag):
    if value is None:
        return None
    if not isinstance(value, str) or not value:
        raise Refused(f"{flag} needs a non-empty value")
    return value


def _limit(raw):
    if not isinstance(raw, str) or not raw.isdigit():
        raise Refused(f"--limit must be 1-100, got {raw!r}")
    value = int(raw)
    if value < 1 or value > 100:
        raise Refused(f"--limit must be 1-100, got {raw!r}")
    return raw


def _since(raw):
    try:
        stamp = raw.replace("Z", "+00:00") if isinstance(raw, str) else raw
        parsed = datetime.datetime.fromisoformat(stamp)
    except (ValueError, TypeError):
        raise Refused(f"--since must be ISO 8601 with an offset, e.g. "
                      f"2026-08-01T00:00:00Z — got {raw!r}")
    if parsed.tzinfo is None:
        raise Refused(f"--since must carry an offset, got {raw!r}")
    return raw


def parse_args(argv):
    parser = argparse.ArgumentParser(
        prog="search_sessions.py",
        description="Orca session search with an index precheck.")
    parser.add_argument("query", nargs="?", default=None)
    parser.add_argument("--query", dest="query_flag", default=None)
    parser.add_argument("--scope", default=None)
    parser.add_argument("--fresh", action="store_true")
    parser.add_argument("--limit", default=None)
    parser.add_argument("--cursor", default=None)
    parser.add_argument("--agent", action="append", default=[])
    parser.add_argument("--path", action="append", default=[])
    parser.add_argument("--since", default=None)
    parser.add_argument("--sort", default=None)
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--environment", default=None)
    parser.add_argument("--pairing-code", default=None)
    parser.add_argument("--precheck-only", action="store_true")
    return parser.parse_args(argv)


def build_search_argv(ns):
    if (ns.query is None) == (ns.query_flag is None):
        raise Refused("pass the query positionally or as --query, not both "
                      "and not neither")
    query = ns.query if ns.query is not None else ns.query_flag
    if not query:
        raise Refused("the query must be non-empty")
    if ns.query is not None:
        argv = ["search", ns.query]
    else:
        argv = ["search", "--query", ns.query_flag]
    if ns.scope is not None:
        if ns.scope not in SCOPES:
            raise Refused(f"--scope must be one of {','.join(SCOPES)}, "
                          f"got {ns.scope!r}")
        argv += ["--scope", ns.scope]
    if ns.fresh:
        argv += ["--fresh"]
    if ns.limit is not None:
        argv += ["--limit", _limit(ns.limit)]
    if _nonempty(ns.cursor, "--cursor") is not None:
        argv += ["--cursor", ns.cursor]
    for agent in ns.agent:
        argv += ["--agent", _nonempty(agent, "--agent")]
    for path in ns.path:
        argv += ["--path", _nonempty(path, "--path")]
    if ns.since is not None:
        argv += ["--since", _since(ns.since)]
    if ns.sort is not None:
        if ns.sort not in SORTS:
            raise Refused(f"--sort must be one of {','.join(SORTS)}, "
                          f"got {ns.sort!r}")
        argv += ["--sort", ns.sort]
    if ns.debug:
        argv += ["--debug"]
    if _nonempty(ns.environment, "--environment") is not None:
        argv += ["--environment", ns.environment]
    if _nonempty(ns.pairing_code, "--pairing-code") is not None:
        argv += ["--pairing-code", ns.pairing_code]
    return argv


def check_index(status):
    """Precheck verdict: return the phase or raise Refused."""
    if not isinstance(status, dict):
        raise Refused("index precheck: the status receipt is not an object")
    if status.get("enabled") is not True:
        raise Refused("index precheck: the host reports enabled=false — the "
                      "index is off, so a search would prove nothing")
    phase = status.get("phase")
    if phase not in GOOD_PHASES:
        raise Refused(f"index precheck: phase={phase or 'absent'} — searching "
                      f"a degraded/closed index proves nothing")
    return phase


def format_results(result):
    if not isinstance(result, dict):
        raise Failed("search receipt is not an object")
    kind = result.get("kind")
    if kind != "results":
        detail = result.get("reason") or ""
        raise Failed(f"search answered {kind or 'unknown'}"
                     f"{' (' + detail + ')' if detail else ''} — not results")
    hits = result.get("hits")
    if not isinstance(hits, list):
        raise Failed("search results answer names no hits")
    page = result.get("page") if isinstance(result.get("page"), dict) else {}
    return [f"HITS={len(hits)}",
            f"NEXT_CURSOR={page.get('cursor') or 'none'}"]


def run_orca(argv):
    try:
        proc = subprocess.run(["orca", *argv, "--json"],
                              capture_output=True, text=True, timeout=180)
    except (OSError, subprocess.SubprocessError) as exc:
        raise Failed(f"could not run orca: {exc}")
    try:
        doc = json.loads(proc.stdout)
    except json.JSONDecodeError:
        raise Failed(f"orca returned unreadable JSON (exit {proc.returncode})")
    if not isinstance(doc, dict):
        raise Failed("orca returned a non-object envelope")
    result = doc.get("result") if isinstance(doc.get("result"), dict) else {}
    err = doc.get("error") or result.get("error")
    if err:
        code = err.get("code") if isinstance(err, dict) else err
        raise Failed(f"orca refused: {code}")
    if proc.returncode != 0:
        raise Failed(f"orca exited {proc.returncode} with no error envelope")
    return result


def main(argv=None):
    try:
        ns = parse_args(sys.argv[1:] if argv is None else argv)
    except SystemExit as exc:
        return exc.code
    try:
        if ns.precheck_only:
            phase = check_index(run_orca(["search", "--index-status"]))
            print(f"PRECHECK=ok phase={phase}")
            return EXIT_OK
        search_argv = build_search_argv(ns)
        phase = check_index(run_orca(["search", "--index-status"]))
        lines = [f"PRECHECK=ok phase={phase}"]
        lines += format_results(run_orca(search_argv))
        print("\n".join(lines))
        return EXIT_OK
    except Refused as exc:
        print(f"search_sessions: REFUSED: {exc}", file=sys.stderr)
        return EXIT_REFUSED
    except Failed as exc:
        print(f"search_sessions: FAILED: {exc}", file=sys.stderr)
        return EXIT_FAILED


if __name__ == "__main__":
    sys.exit(main())
