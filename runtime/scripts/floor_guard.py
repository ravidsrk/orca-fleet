#!/usr/bin/env python3
"""Diff-scoped floor guard: the cheap road to green, caught mechanically.

Five moves lower the bar without touching a stated requirement: a silenced
checker, a test made easier, unfinished work left as a stub, an assertion
deleted from a test that stayed, and a threshold walked down in the constraints
file (or a new exception row admitted beside it). Each is invisible to a green
build and obvious in a diff. This guard reads the diff.

Scope is the merge base against ``--base`` plus the working tree plus untracked
files -- a guard that reads only ``git diff`` misses the new file. Tightening is
silent; loosening is loud: only moves that lower the bar are reported.

Rules (rule ids are stable; a waiver names one):

===================  ============================================================
rule id              what trips it (added lines unless stated)
===================  ============================================================
silenced-checker     ``# noqa``, ``eslint-disable``, ``@ts-ignore``, ``@ts-nocheck``,
                     ``# type: ignore``, ``pragma: no cover``, ``biome-ignore``,
                     ``istanbul ignore``, ``nosemgrep``, ``gitleaks:allow``,
                     ``#[allow(``, ``nolint``, ``Stryker disable``, ``prettier-ignore``
test-made-easier     ``@skip``, ``.skip(``, ``.only(``, ``.todo(``, ``xit(``,
                     ``xdescribe(``, ``pytest.mark.skip``, ``pytest.mark.xfail``,
                     ``unittest.skip``, ``t.Skip(``, ``@Ignore``, ``return  # stub``
unfinished-work      ``TODO``/``FIXME``/``XXX``, ``NotImplementedError``,
                     ``not implemented``, an empty ``catch``/``except: pass``,
                     a ``TODO``-return (``return None  # TODO``)
assertion-removed    a REMOVED line carrying ``assert``, ``expect(``, ``should``,
                     ``self.assert``, ``t.Error`` in a path that looks like a test
                     and still exists at HEAD (a deleted file is not this rule)
threshold-lowered    a number in the constraints file that went DOWN, matched by
                     the row/bullet key left of the first ``|`` or ``:``
new-exception        an added constraints row shaped ``| W123 |`` / ``| E45 |``, or
                     an added line under an ``## Exceptions`` heading
===================  ============================================================

Exemptions come from the DECISIONS log, never from an ignore file. A waiver line
must carry the ``floor-waiver`` marker, the rule id as a whole token, and the
path either named exactly or covered by an explicit ``dir/**`` glob -- a bare
directory is not a waiver, and neither is ``**``. That keeps a waiver
reviewable, attributable and dated (runtime/ledger-contract.md DECISIONS log)
instead of a silent glob, and keeps it a DECLARATION rather than two substrings
a sentence happens to contain (#313).

Reporting is redaction-first: rule id, ``file:line`` and a short pattern name --
never the matched text, which may be the credential someone tried to suppress.

Exit codes
    0  clean
    1  at least one un-waived finding (block the change)
    2  the guard could not run -- not a git repo, no merge base, unreadable
       waiver file. Never let a 2 read as a 0.

How to wire
    Run it OFF the worker, never inside the builder loop: a guard the builder can
    see is a guard the builder edits. Two consumers. (1) A GUARD unit in the
    floor-it mission runs it against the unit's base and treats exit 1 as the
    unit's failing oracle -- the script IS the reviewed CI unit. (2) An
    independent verifier runs it over a mutation unit's diff before any
    judgement-based review: a diff that trips ``test-made-easier`` or
    ``assertion-removed`` fails the negative-control leg deterministically, so a
    disabled test cannot hide behind a hand-written negative-control note. Exit 2
    parks the unit (a shallow CI checkout must not present as a clean floor).
    It is regex-shallow by design: a floor under review, never a replacement for it.

    Example: ``floor_guard.py --base origin/main --constraints CONSTRAINTS.md``
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

EXIT_CLEAN = 0
EXIT_FINDINGS = 1
EXIT_CANNOT_RUN = 2

# (pattern name, compiled regex). The name is what gets reported; the matched
# text never is.
SUPPRESSIONS = [
    ("noqa", re.compile(r"#\s*noqa")),
    ("type-ignore", re.compile(r"#\s*type:\s*ignore")),
    ("pragma-no-cover", re.compile(r"pragma:\s*no\s*cover")),
    ("eslint-disable", re.compile(r"eslint-disable")),
    ("ts-ignore", re.compile(r"@ts-(ignore|nocheck|expect-error)")),
    ("biome-ignore", re.compile(r"biome-ignore")),
    ("istanbul-ignore", re.compile(r"istanbul\s+ignore")),
    ("nosemgrep", re.compile(r"nosemgrep")),
    ("gitleaks-allow", re.compile(r"gitleaks:allow")),
    ("rust-allow", re.compile(r"#\[allow\(")),
    ("golangci-nolint", re.compile(r"//\s*nolint")),
    ("stryker-disable", re.compile(r"Stryker\s+disable")),
    ("prettier-ignore", re.compile(r"prettier-ignore")),
    ("phpstan-ignore", re.compile(r"@phpstan-ignore")),
]

SKIPS = [
    ("pytest-skip", re.compile(r"@?pytest\.mark\.(skip|skipif|xfail)")),
    ("unittest-skip", re.compile(r"@?unittest\.(skip|expectedFailure)")),
    ("decorator-skip", re.compile(r"^\s*@(skip|Skip|Ignore|Disabled)\b")),
    ("dot-skip", re.compile(r"\.(skip|only|todo|failing)\s*\(")),
    ("xit", re.compile(r"\bx(it|describe|test|context)\s*\(")),
    ("go-skip", re.compile(r"\bt\.Skip(Now)?\s*\(")),
    ("rust-ignore", re.compile(r"#\[ignore")),
    ("junit-ignore", re.compile(r"@(Ignore|Disabled)\b")),
]

STUBS = [
    ("todo-marker", re.compile(r"\b(TODO|FIXME|XXX|HACK)\b")),
    ("not-implemented", re.compile(r"(NotImplementedError|not\s+implemented|unimplemented!)")),
    ("empty-catch", re.compile(r"catch\s*(\([^)]*\))?\s*\{\s*\}")),
    ("swallowed-except", re.compile(r"except[^:]*:\s*pass\b")),
    ("stub-return", re.compile(r"return\s+(None|null|nil|\{\}|\[\]|\"\"|'')\s*(#|//)\s*(TODO|stub)")),
    ("pass-stub", re.compile(r"\bpass\s*(#|//)\s*stub")),
]

ASSERTIONS = re.compile(r"(\bassert\b|\bexpect\s*\(|\bshould\b|self\.assert|\bt\.Error)")
TEST_PATH = re.compile(r"(^|/)(tests?|spec|__tests__)/|\.(test|spec)\.|_test\.|(^|/)test_[^/]*$")
EXCEPTION_ROW = re.compile(r"^\s*\|\s*[WE]\d+\s*\|")
EXCEPTIONS_HEADING = re.compile(r"^\s*#{1,6}\s+.*\bexceptions?\b", re.IGNORECASE)
NUMBER = re.compile(r"\d+(?:\.\d+)?")
HUNK = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")

DEFAULT_BASES = ("origin/main", "origin/master", "main", "master")


class GuardError(Exception):
    """Raised for every could-not-run condition; the caller maps it to exit 2."""


def git(repo, *args):
    """Run git with argv only. Returns stdout, or None when git exits non-zero."""
    try:
        r = subprocess.run(
            ["git", "-C", str(repo), *args],
            capture_output=True, text=True, timeout=60,
        )
    except (OSError, subprocess.SubprocessError) as err:
        raise GuardError(f"git {' '.join(args)} failed to run: {err}") from err
    return r.stdout if r.returncode == 0 else None


def repo_root(start):
    top = git(start, "rev-parse", "--show-toplevel")
    if not top or not top.strip():
        raise GuardError(f"{start} is not inside a git work tree")
    return Path(top.strip())


def resolve_base(repo, base):
    """Pick a base ref. An explicit --base that does not resolve is an error, not
    a fallback: silently guarding against the wrong base is a false clean."""
    if base:
        if git(repo, "rev-parse", "--verify", "-q", base + "^{commit}") is None:
            raise GuardError(f"base ref {base!r} is not resolvable (shallow clone or missing fetch)")
        return base
    head = git(repo, "symbolic-ref", "refs/remotes/origin/HEAD")
    if head and head.strip():
        candidate = head.strip().replace("refs/remotes/", "", 1)
        if git(repo, "rev-parse", "--verify", "-q", candidate + "^{commit}") is not None:
            return candidate
    for candidate in DEFAULT_BASES:
        if git(repo, "rev-parse", "--verify", "-q", candidate + "^{commit}") is not None:
            return candidate
    raise GuardError("no base ref could be resolved (tried origin/HEAD, origin/main, main, master)")


def merge_base(repo, base):
    mb = git(repo, "merge-base", base, "HEAD")
    if not mb or not mb.strip():
        raise GuardError(f"no merge base between {base} and HEAD")
    return mb.strip()


def collect_diff(repo, mb):
    """Unified-0 diff against the merge base, plus every untracked file rendered
    as an all-added diff. Returns the concatenated diff text."""
    tracked = git(repo, "diff", "--unified=0", mb, "--") or ""
    others = git(repo, "ls-files", "--others", "--exclude-standard") or ""
    chunks = [tracked]
    for name in others.splitlines():
        if not name.strip():
            continue
        # --no-index exits 1 when the files differ; that is the normal case, so
        # go through subprocess directly rather than git() (which returns None).
        try:
            r = subprocess.run(
                ["git", "-C", str(repo), "diff", "--no-index", "--unified=0", "--", "/dev/null", name],
                capture_output=True, text=True, timeout=60,
            )
        except (OSError, subprocess.SubprocessError):
            continue
        chunks.append(r.stdout)
    return "\n".join(chunks)


def parse_diff(diff_text):
    """Split a unified diff into (added, removed) lists of (path, lineno, text)."""
    added, removed = [], []
    new_path = old_path = ""
    new_no = old_no = 0
    for line in diff_text.split("\n"):
        if line.startswith("--- "):
            old_path = strip_prefix(line[4:])
            continue
        if line.startswith("+++ "):
            new_path = strip_prefix(line[4:])
            continue
        m = HUNK.match(line)
        if m:
            old_no = int(m.group(1))
            new_no = int(m.group(3))
            continue
        if line.startswith("+"):
            added.append((new_path or old_path, new_no, line[1:]))
            new_no += 1
        elif line.startswith("-"):
            removed.append((old_path or new_path, old_no, line[1:]))
            old_no += 1
        elif line.startswith(" "):
            new_no += 1
            old_no += 1
    return added, removed


def strip_prefix(path):
    path = path.strip()
    if path.startswith(("a/", "b/")):
        return path[2:]
    if path == "/dev/null":
        return ""
    return path


def is_constraints(path, constraints_name):
    return bool(path) and Path(path).name == Path(constraints_name).name


def numbers(text):
    return [float(n) for n in NUMBER.findall(text)]


def row_key(text):
    """Identify a constraints row so its before/after pair can be matched.

    The key is the first NON-EMPTY cell: a markdown table row starts with the
    delimiter, so splitting naively yields an empty first field and every row
    keys the same, which silently disables the comparison.
    """
    for token in re.split(r"[|:]", text.strip()):
        cleaned = token.strip().strip("-*# ").lower()
        if cleaned:
            return cleaned
    return ""


def scan(added, removed, constraints_name, repo):
    """Return findings as dicts: rule, path, line, detail (never matched text)."""
    findings = []

    def flag(rule, path, line, detail):
        findings.append({"rule": rule, "path": path or "(unknown)", "line": line, "detail": detail})

    in_exceptions = {}
    for path, line, text in added:
        if is_constraints(path, constraints_name) and EXCEPTIONS_HEADING.match(text):
            in_exceptions[path] = True
        for name, pat in SUPPRESSIONS:
            if pat.search(text):
                flag("silenced-checker", path, line, name)
                break
        for name, pat in SKIPS:
            if pat.search(text):
                flag("test-made-easier", path, line, name)
                break
        for name, pat in STUBS:
            if pat.search(text):
                flag("unfinished-work", path, line, name)
                break
        if is_constraints(path, constraints_name):
            if EXCEPTION_ROW.match(text):
                flag("new-exception", path, line, "exception-row")
            elif in_exceptions.get(path) and text.strip().startswith(("-", "*")):
                flag("new-exception", path, line, "exceptions-bullet")

    for path, line, text in removed:
        if not TEST_PATH.search(path or ""):
            continue
        if not ASSERTIONS.search(text):
            continue
        # A wholly deleted test FILE is a different move (and a visible one);
        # this rule is about a file that stayed and lost an assertion.
        if git(repo, "cat-file", "-e", f"HEAD:{path}") is None and not (repo / path).exists():
            continue
        flag("assertion-removed", path, line, "assertion")

    old_rows = [(p, n, t) for p, n, t in removed if is_constraints(p, constraints_name)]
    new_rows = [(p, n, t) for p, n, t in added if is_constraints(p, constraints_name)]
    for path, line, text in old_rows:
        key = row_key(text)
        if not key:
            continue
        match = next((t for p, _, t in new_rows if p == path and row_key(t) == key), None)
        if match is None:
            continue
        before, after = numbers(text), numbers(match)
        for i, value in enumerate(after):
            if i < len(before) and value < before[i]:
                flag("threshold-lowered", path, line, f"{before[i]:g} -> {value:g}")
                break
    return findings


def load_waivers(path):
    """A waiver line names a rule id and a path. Missing file = no waivers (that
    is a clean state, not a could-not-run); an unreadable one IS a 2."""
    p = Path(path)
    if not p.exists():
        return []
    try:
        return [ln for ln in p.read_text(encoding="utf-8", errors="replace").splitlines() if ln.strip()]
    except OSError as err:
        raise GuardError(f"waiver file {path} is unreadable: {err}") from err


_WAIVER_MARKER = "floor-waiver"
# Tokens of a waiver line: path/rule shaped runs. `-` and `.` are in the class so `test-made-easier`
# and `src/new.py` each read as ONE token, which is the whole point — substring matching is what
# made `silenced-checkers` waive `silenced-checker`.
_WAIVER_TOKEN_RE = re.compile(r"[A-Za-z0-9_./*-]+")


def _path_waived_by(token, path):
    """True when `token` names `path` exactly, or is a `dir/**` glob whose segments prefix it.

    Segment-wise, never substring: `src/new.pyc` must not cover `src/new.py`, and `src` must not
    cover `srcinternal/x`. A bare `**` is a blanket, not a waiver — it names nothing, so a reviewer
    reading the line learns nothing about the blast radius."""
    if token == path:
        return True
    if not token.endswith("/**"):
        return False
    prefix = [p for p in token[:-3].split("/") if p]
    if not prefix:
        return False
    return path.split("/")[:len(prefix)] == prefix


def is_waived(finding, waivers):
    """A waiver is a DECLARATION the line makes, not two substrings it happens to contain (#313).

    The old test was `rule in line and path in line`, over every line of the DECISIONS file. That
    let a superstring stand in for either field (`silenced-checkers`, `src/new.pyc`), and — because
    any line at all was scanned — a line recording that the team DECLINED to waive a finding
    granted it, as did a sentence that merely mentioned both. So: the line must carry the
    `floor-waiver` marker, the rule id must appear as a whole token, and the path must be named
    exactly or covered by an explicit `dir/**` glob."""
    path = finding.get("path")
    if not path:
        return False
    for line in waivers:
        tokens = _WAIVER_TOKEN_RE.findall(line)
        if _WAIVER_MARKER not in tokens or finding["rule"] not in tokens:
            continue
        if any(_path_waived_by(t, path) for t in tokens):
            return True
    return False


def build_parser():
    p = argparse.ArgumentParser(
        prog="floor_guard.py",
        description="Diff-scoped detection of the five moves that lower the bar.",
        epilog="exit 0 clean / 1 findings / 2 could-not-run (never let a 2 read as a 0)",
    )
    p.add_argument("--base", default=None, help="base ref (default: origin/HEAD, then origin/main, main, master)")
    p.add_argument("--constraints", default="CONSTRAINTS.md", help="constraints file whose numbers may not go down")
    p.add_argument("--waivers", default="docs/DECISIONS.md", help="DECISIONS log; a line naming a rule id and a path waives it")
    p.add_argument("--repo", default=".", help="repository to guard (default: cwd)")
    p.add_argument("--quiet", action="store_true", help="print findings only, no clean banner")
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        repo = repo_root(args.repo)
        base = resolve_base(repo, args.base)
        mb = merge_base(repo, base)
        added, removed = parse_diff(collect_diff(repo, mb))
        findings = scan(added, removed, args.constraints, repo)
        waiver_path = args.waivers if Path(args.waivers).is_absolute() else repo / args.waivers
        waivers = load_waivers(waiver_path)
    except GuardError as err:
        print(f"floor-guard: could not run: {err}", file=sys.stderr)
        return EXIT_CANNOT_RUN

    live = [f for f in findings if not is_waived(f, waivers)]
    if not live:
        if not args.quiet:
            waived = len(findings)
            note = f" ({waived} waived)" if waived else ""
            print(f"floor-guard: clean{note}")
        return EXIT_CLEAN
    print(f"floor-guard: {len(live)} floor violation(s):", file=sys.stderr)
    for f in live:
        print(f"  [{f['rule']}] {f['path']}:{f['line']} ({f['detail']})", file=sys.stderr)
    print(
        "\nEach lowers the bar. Fix the code, or record a DECISIONS waiver line carrying "
        "`floor-waiver`, the rule id, and the path exactly (or `dir/**`).",
        file=sys.stderr,
    )
    return EXIT_FINDINGS


if __name__ == "__main__":
    sys.exit(main())
