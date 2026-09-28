#!/usr/bin/env python3
"""release_check.py — the 1.0 release checklist as a runnable gate (#414).

docs/release-1.0-checklist.md DEFINES the release: every gate is a command a
second person can run, with its expected output. This script RUNS those
commands from the repo root, one line per check, and exits with a code a
release branch can be gated on. The document stays the definition, this file
is its executable form, and the two must agree: the checklist opens with the
command that runs this file, and tests/test_release_check.py runs it against
this repository and holds the doc's commands to the script's checks.

Usage:
  python3 scripts/release_check.py                 # every gate, full suite (~8 min)
  python3 scripts/release_check.py --fast          # skip the unittest suite: SKIP(--fast)
  python3 scripts/release_check.py --skip-github   # skip the gh-backed checks: SKIP(--skip-github)
  python3 scripts/release_check.py --json          # one JSON object on stdout instead of lines
  python3 scripts/release_check.py --repo PATH     # gate another checkout (tests point it at a fixture)

Output, text mode: a header per gate, then one line per check —
  PASS  <gate>/<check>: <detail>
  FAIL  <gate>/<check>: <detail>
  SKIP(<reason>)  <gate>/<check>
  INFO  <gate>/<check>: <detail>        a fact the release does not gate on (#235)
— and a final `summary:` line with the counts and the exit code.

Exit contract (fail-closed):
  0  every check PASS (INFO lines are allowed; the summary counts them)
  1  any check FAIL
  2  could not run: --repo is not a directory, or a gate raised
  3  incomplete: no FAIL, but at least one SKIP — the run proved less than the
     release needs (--fast, --skip-github, or a machine without gh, network,
     git or sh). A 3 is not a release verdict; only a 0 is (PR #509 review).

SKIP rules: a check that needs something this MACHINE does not have — `gh` not
on PATH (SKIP(no gh)), `gh auth status` failing (SKIP(gh unauthenticated)), no
route to GitHub (SKIP(no network)), git or sh absent — prints SKIP with the
reason and never PASS. A SKIP is not a FAIL, but it is counted, printed, and
turns exit 0 into exit 3, so a run carrying one cannot be mistaken for a full
run by a script reading only the exit code: re-run it where the tool exists. The gh-backed checks carry `gh-` in their name. Something the
CHECKOUT lacks (no scripts/validate.py, no gate-batch store, a missing report)
is a FAIL, not a SKIP: that is the release's state, not the machine's.

Stdlib only. Subprocesses take argv lists, never shell text; the checkout's
Python tools run under this interpreter (sys.executable), so an empty PATH
cannot swap it for another.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import traceback
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_REPO = HERE.parent

PASS, FAIL, SKIP, INFO = "PASS", "FAIL", "SKIP", "INFO"
STATUSES = (PASS, FAIL, SKIP, INFO)

# Gate 1 reads this run's gate batch: #408 settled it, #419 typed it (gate-batch.json).
GATE_BATCH_RUN = "2026-09-14-clean-sweep-tracker"
# Gate 2: the flagships, and the bar as #407 re-scoped it (#409 took harden-it
# from external-run to self-run). A BOUND tier is the bar; the tier is not.
FLAGSHIPS = ("harden-it", "prove-it", "clean-sweep")
PROOF_BAR = ("self-run", "external-run")
# Gate 4: the one install command, in both places it is documented.
INSTALL_CMD = "sh scripts/install.sh"
# Gate 5: the pin must be a fresh live witness, not the 2026-09-13 one #416 replaced,
# and the chaining report must be named by a doc a reader navigates.
PIN_MIN_WITNESSED = "2026-09-16"
CHAINING_NEEDLE = "docs/reports/chaining-"
CHAINING_INDEXES = ("runtime/mission-chaining.md", "docs/runs/README.md")
# Gate 6: each mechanized tool with the contract test module that holds it.
MECHANIZED = (("runtime/scripts/watchdog.py", "tests/test_watchdog.py"),
              ("runtime/scripts/gate-batch.py", "tests/test_gate_batch.py"))

TIMEOUT_TOOL = 600      # validate, proof_status, run_report, the vf-bench gate, the demo
TIMEOUT_SUITE = 3600    # the full unittest suite (~8 min)
TIMEOUT_GH = 120

OWED_LINE = re.compile(r"^(G\d+) \[owed\]")
LIST_LINE = re.compile(r"^(G\d+) \[(\w+)\]")

# gh's own wording when the machine, not GitHub, is the problem.
_OFFLINE_MARKERS = ("could not resolve", "no such host", "dial tcp", "connection refused",
                    "connection reset", "network is unreachable", "i/o timeout", "timed out",
                    "tls handshake", "error connecting to", "failed to connect",
                    "temporary failure in name resolution", "proxyconnect")
_UNAUTHENTICATED_MARKERS = ("not logged in", "gh auth login", "authentication", "http 401",
                            "bad credentials", "no oauth token", "gh_token")


class Result:
    """What a subprocess left behind, including the two ways it never ran."""
    __slots__ = ("returncode", "stdout", "stderr", "missing", "timeout")

    def __init__(self, returncode, stdout="", stderr="", missing=False, timeout=False):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr
        self.missing = missing
        self.timeout = timeout

    @property
    def ok(self):
        return self.returncode == 0


_UNPROBED = object()


class Context:
    """The checkout under test, the flags, a memo of commands already run
    (run_report.py is a Gate 0 and a Gate 2 check; it runs once) and the
    one-time gh probe. `on_check` streams each check as it lands."""

    def __init__(self, repo=DEFAULT_REPO, fast=False, skip_github=False, on_check=None):
        self.repo = Path(repo).resolve()
        self.fast = fast
        self.skip_github = skip_github
        self.on_check = on_check
        self._memo = {}
        self._gh = _UNPROBED

    def run(self, argv, timeout=TIMEOUT_TOOL, memo=True):
        """Run argv from the repo root, capturing text. Never raises for the
        executable being absent or slow: callers branch on the Result."""
        argv = [str(a) for a in argv]
        key = tuple(argv)
        if memo and key in self._memo:
            return self._memo[key]
        try:
            proc = subprocess.run(argv, cwd=str(self.repo), capture_output=True,
                                  encoding="utf-8", errors="replace", timeout=timeout)
            result = Result(proc.returncode, proc.stdout, proc.stderr)
        except FileNotFoundError:
            result = Result(None, "", f"{argv[0]}: not found on PATH", missing=True)
        except subprocess.TimeoutExpired:
            result = Result(None, "", f"timed out after {timeout}s", timeout=True)
        except OSError as e:
            result = Result(None, "", f"{argv[0]}: {e}", missing=True)
        if memo:
            self._memo[key] = result
        return result

    def py(self, tool, *args, timeout=TIMEOUT_TOOL):
        """Run one of the checkout's Python tools under this interpreter."""
        script = self.repo / tool
        if not script.is_file():
            return Result(None, "", f"{tool}: not in this checkout", missing=True)
        return self.run([sys.executable, str(script), *args], timeout=timeout)

    def read(self, rel):
        """Text of a checkout file, or None when it is not there."""
        try:
            return (self.repo / rel).read_text(encoding="utf-8", errors="replace")
        except OSError:
            return None

    def rel(self, path):
        try:
            return str(Path(path).resolve().relative_to(self.repo))
        except ValueError:
            return str(path)

    def record(self, checks, check):
        checks.append(check)
        if self.on_check is not None:
            self.on_check(check)
        return check


def tail(text, lines=2, width=240):
    """The last non-empty lines of a stream, on one line, for a detail field."""
    kept = [ln.strip() for ln in (text or "").splitlines() if ln.strip()]
    out = " | ".join(kept[-lines:]) if kept else "(no output)"
    return out if len(out) <= width else out[:width - 1] + "…"


def git_head(ctx):
    r = ctx.run(["git", "rev-parse", "HEAD"])
    return r.stdout.strip() if r.ok else None


# ---------------------------------------------------------------------------
# gh: the machine's fault is a SKIP, GitHub's answer is a verdict.
# ---------------------------------------------------------------------------

def _offline(text):
    low = text.lower()
    return any(marker in low for marker in _OFFLINE_MARKERS)


def _unauthenticated(text):
    low = text.lower()
    return any(marker in low for marker in _UNAUTHENTICATED_MARKERS)


def gh_unavailable(ctx):
    """None when gh can answer; otherwise the SKIP reason. Probed once per run."""
    if ctx.skip_github:
        return "--skip-github"
    if ctx._gh is not _UNPROBED:
        return ctx._gh
    if shutil.which("gh") is None:
        ctx._gh = "no gh"
        return ctx._gh
    r = ctx.run(["gh", "auth", "status"], timeout=TIMEOUT_GH, memo=False)
    text = r.stderr + r.stdout
    if r.missing:
        ctx._gh = "no gh"
    elif r.timeout:
        ctx._gh = "no network: gh auth status " + r.stderr
    elif r.ok:
        ctx._gh = None
    elif _offline(text):
        ctx._gh = "no network: " + tail(text, 1, 120)
    else:
        ctx._gh = "gh unauthenticated"
    return ctx._gh


def gh_json(ctx, argv):
    """(data, None) from a gh command that prints JSON, else (None, (status, detail)):
    SKIP when the machine is at fault, FAIL when GitHub answered and it was no."""
    reason = gh_unavailable(ctx)
    if reason:
        return None, (SKIP, reason)
    r = ctx.run(["gh", *argv], timeout=TIMEOUT_GH)
    if r.missing:
        return None, (SKIP, "no gh")
    if r.timeout:
        return None, (SKIP, "no network: gh " + r.stderr)
    label = "gh " + " ".join(argv)
    if not r.ok:
        text = r.stderr + r.stdout
        if _offline(text):
            return None, (SKIP, "no network: " + tail(text, 1, 120))
        if _unauthenticated(text):
            return None, (SKIP, "gh unauthenticated")
        return None, (FAIL, f"{label}: exit {r.returncode}: {tail(text)}")
    try:
        return json.loads(r.stdout), None
    except ValueError:
        return None, (FAIL, f"{label} printed no JSON: {tail(r.stdout)}")


def check_issue_closed(ctx, gate, number, why):
    name = f"{gate}/gh-issue-{number}-closed"
    data, err = gh_json(ctx, ["issue", "view", str(number), "--json", "state"])
    if err:
        return (name, err[0], err[1])
    state = str((data or {}).get("state", "")).upper()
    if state == "CLOSED":
        return (name, PASS, f"#{number} CLOSED ({why})")
    return (name, FAIL, f"#{number} is {state or 'in an unknown state'}; the gate needs CLOSED ({why})")


def check_pr_merged(ctx, gate, number, why):
    name = f"{gate}/gh-pr-{number}-merged"
    data, err = gh_json(ctx, ["pr", "view", str(number), "--json", "state"])
    if err:
        return (name, err[0], err[1])
    state = str((data or {}).get("state", "")).upper()
    if state == "MERGED":
        return (name, PASS, f"PR #{number} MERGED ({why})")
    return (name, FAIL, f"PR #{number} is {state or 'in an unknown state'}; the gate needs MERGED ({why})")


def check_workflow_green_at_head(ctx, gate, workflow):
    """The latest `<workflow>` run on main must be a success AT this HEAD —
    a stale green from another SHA does not count."""
    name = f"{gate}/gh-{workflow}-run-green-at-head"
    data, err = gh_json(ctx, ["run", "list", "--workflow", workflow, "--branch", "main",
                              "--limit", "1", "--json", "conclusion,headSha"])
    if err:
        return (name, err[0], err[1])
    head_probe = ctx.run(["git", "rev-parse", "HEAD"])
    if head_probe.missing:
        return (name, SKIP, "no git")
    if not head_probe.ok:
        return (name, FAIL, f"git rev-parse HEAD: {tail(head_probe.stderr, 1)}")
    head = head_probe.stdout.strip()
    if not isinstance(data, list) or not data:
        return (name, FAIL, f"no `{workflow}` workflow run recorded on main")
    run = data[0] if isinstance(data[0], dict) else {}
    conclusion, sha = run.get("conclusion"), run.get("headSha")
    if conclusion == "success" and sha == head:
        return (name, PASS, f"`{workflow}` bound GREEN at {sha}")
    return (name, FAIL, f"latest `{workflow}` run on main is {conclusion or 'unfinished'} at "
                        f"{sha}; HEAD is {head} — a stale green from another SHA does not count")


# ---------------------------------------------------------------------------
# Gate 0 — tree and catalog gates green
# ---------------------------------------------------------------------------

def check_tree_clean(ctx):
    name = "gate0/tree-clean"
    r = ctx.run(["git", "status", "--porcelain"])
    if r.missing:
        return (name, SKIP, "no git")
    if not r.ok:
        return (name, FAIL, f"git status --porcelain: exit {r.returncode}: {tail(r.stderr)}")
    dirty = [ln.strip() for ln in r.stdout.splitlines() if ln.strip()]
    if dirty:
        shown = ", ".join(dirty[:5]) + (" …" if len(dirty) > 5 else "")
        return (name, FAIL, f"{len(dirty)} uncommitted path(s): {shown}")
    return (name, PASS, f"working tree clean at {git_head(ctx) or 'HEAD'}")


def check_tool_exit0(ctx, name, tool, *args, timeout=TIMEOUT_TOOL):
    """PASS iff `python3 <tool> <args>` exits 0. A tool the checkout lacks FAILs."""
    label = " ".join((tool, *args))
    r = ctx.py(tool, *args, timeout=timeout)
    if r.missing:
        return (name, FAIL, r.stderr)
    if r.timeout:
        return (name, FAIL, f"{label}: {r.stderr}")
    if r.ok:
        return (name, PASS, f"{label}: exit 0 — {tail(r.stdout or r.stderr, 1)}")
    return (name, FAIL, f"{label}: exit {r.returncode}: {tail(r.stderr or r.stdout)}")


def check_suite(ctx):
    name = "gate0/unittest"
    label = "python3 -m unittest discover -s tests"
    if not (ctx.repo / "tests").is_dir():
        return (name, FAIL, "no tests/ directory in this checkout")
    r = ctx.run([sys.executable, "-m", "unittest", "discover", "-s", "tests"],
                timeout=TIMEOUT_SUITE)
    if r.timeout:
        return (name, FAIL, f"{label}: {r.stderr}")
    if r.ok:
        return (name, PASS, f"{label}: {tail(r.stderr, 2)}")
    return (name, FAIL, f"{label}: exit {r.returncode}: {tail(r.stderr, 3)}")


def gate0(ctx):
    """Gate 0 — tree and catalog gates green."""
    checks = []

    def add(check):
        return ctx.record(checks, check)

    add(check_tree_clean(ctx))
    add(check_tool_exit0(ctx, "gate0/validate", "scripts/validate.py"))
    if ctx.fast:
        add(("gate0/unittest", SKIP, "--fast"))
    else:
        add(check_suite(ctx))
    add(check_tool_exit0(ctx, "gate0/proof-status", "runtime/scripts/proof_status.py", "--check"))
    add(check_tool_exit0(ctx, "gate0/run-report", "runtime/scripts/run_report.py"))
    add(check_workflow_green_at_head(ctx, "gate0", "validate"))
    return checks


# ---------------------------------------------------------------------------
# Gate 1 — Phase 0 at zero (epic DoD 1)
# ---------------------------------------------------------------------------

def check_gate_batch_owed(ctx):
    """The store is gate-batch.json (#419), read through its own CLI — never a
    grep over the rendered .md, which is a view of the store, not the store."""
    name = "gate1/gate-batch-owed"
    tool = "runtime/scripts/gate-batch.py"
    label = f"gate-batch.py --run {GATE_BATCH_RUN} list --status owed"
    r = ctx.py(tool, "--run", GATE_BATCH_RUN, "list", "--status", "owed")
    if r.missing:
        return (name, FAIL, r.stderr)
    if r.timeout:
        return (name, FAIL, f"{label}: {r.stderr}")
    if not r.ok:
        return (name, FAIL, f"{label}: exit {r.returncode}: {tail(r.stderr)}")
    owed = [m.group(1) for m in (OWED_LINE.match(ln) for ln in r.stdout.splitlines()) if m]
    if owed:
        return (name, FAIL, f"{len(owed)} owed gate(s) in {GATE_BATCH_RUN}: {', '.join(owed)}")
    listing = ctx.py(tool, "--run", GATE_BATCH_RUN, "list")
    states = [f"{m.group(1)} {m.group(2)}"
              for m in (LIST_LINE.match(ln) for ln in listing.stdout.splitlines()) if m]
    detail = f"no owed gates in {GATE_BATCH_RUN}"
    if states:
        detail += ": " + ", ".join(states)
    return (name, PASS, detail)


def info_issue_235(ctx):
    """#235 (marketplace submissions) is needs-human and its own body says it
    does not gate launch: recorded for the reader, never graded."""
    name = "gate1/issue-235-marketplace"
    base = "#235 marketplace submissions: needs-human, does not gate"
    reason = gh_unavailable(ctx)
    if reason:
        return (name, INFO, f"{base} (state not queried: {reason})")
    data, err = gh_json(ctx, ["issue", "view", "235", "--json", "state"])
    if err:
        return (name, INFO, f"{base} (state not queried: {err[1]})")
    state = (data or {}).get("state", "unknown")
    return (name, INFO, f"{base} (state {state}; stays tracked)")


def gate1(ctx):
    """Gate 1 — Phase 0 at zero (epic DoD 1)."""
    checks = []

    def add(check):
        return ctx.record(checks, check)

    add(check_gate_batch_owed(ctx))
    add(check_issue_closed(ctx, "gate1", 408, "runway settled"))
    add(check_issue_closed(ctx, "gate1", 386, "signing decision recorded and implemented"))
    add(check_pr_merged(ctx, "gate1", 406, "docs re-check"))
    add(info_issue_235(ctx))
    return checks


# ---------------------------------------------------------------------------
# Gate 2 — flagships proven (epic DoD 2)
# ---------------------------------------------------------------------------

def frontmatter_proof(text):
    """`metadata.proof` from a SKILL.md, read the way the checklist reads it:
    the block between the first `---` pair, the indented `proof:` key."""
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end == -1:
        return None
    m = re.search(r"^\s+proof:\s*(\S+)\s*$", text[3:end], re.M)
    return m.group(1).strip("\"'") if m else None


def gate2(ctx):
    """Gate 2 — flagships proven (epic DoD 2)."""
    checks = []

    def add(check):
        return ctx.record(checks, check)

    bar = " or ".join(PROOF_BAR)
    for mission in FLAGSHIPS:
        name = f"gate2/proof-{mission}"
        path = f"skills/{mission}/SKILL.md"
        text = ctx.read(path)
        if text is None:
            add((name, FAIL, f"{path} missing"))
            continue
        proof = frontmatter_proof(text)
        if proof is None:
            add((name, FAIL, f"{path}: no metadata.proof in the frontmatter"))
        elif proof in PROOF_BAR:
            add((name, PASS, f"{path}: proof: {proof} (bar: {bar})"))
        else:
            add((name, FAIL, f"{path}: proof: {proof}; the bar is {bar}"))
    add(check_tool_exit0(ctx, "gate2/run-report", "runtime/scripts/run_report.py"))
    return checks


# ---------------------------------------------------------------------------
# Gate 3 — verifier moat held by CI (epic DoD 3)
# ---------------------------------------------------------------------------

def check_negative_control_demo(ctx):
    name = "gate3/negative-control-demo"
    script = "demo/negative-control/run.sh"
    if not (ctx.repo / script).is_file():
        return (name, FAIL, f"{script} missing")
    sh = shutil.which("sh") or ("/bin/sh" if os.path.exists("/bin/sh") else None)
    if sh is None:
        return (name, SKIP, "no sh")
    r = ctx.run([sh, str(ctx.repo / script)], timeout=TIMEOUT_TOOL)
    if r.missing:
        return (name, SKIP, "no sh")
    if r.timeout:
        return (name, FAIL, f"sh {script}: {r.stderr}")
    if r.ok:
        verdict = next((ln.strip() for ln in r.stdout.splitlines() if ln.startswith("PASS:")),
                       None) or tail(r.stdout, 1)
        return (name, PASS, f"sh {script}: exit 0 — {verdict}")
    return (name, FAIL, f"sh {script}: exit {r.returncode}: {tail(r.stdout + r.stderr, 2)}")


def check_workflows_mention(ctx, name, patterns, landed):
    wf_dir = ctx.repo / ".github" / "workflows"
    files = sorted(p for p in wf_dir.iterdir() if p.is_file()) if wf_dir.is_dir() else []
    hits = []
    for path in files:
        text = path.read_text(encoding="utf-8", errors="replace")
        if any(re.search(pat, text) for pat in patterns):
            hits.append(path.name)
    what = " or ".join(patterns)
    if hits:
        return (name, PASS, f".github/workflows/{{{', '.join(hits)}}} mention {what} ({landed} landed)")
    return (name, FAIL, f"no file under .github/workflows/ mentions {what} ({landed} has not landed)")


def gate3(ctx):
    """Gate 3 — verifier moat held by CI (epic DoD 3)."""
    checks = []

    def add(check):
        return ctx.record(checks, check)

    add(check_tool_exit0(ctx, "gate3/vf-bench-gate", "bench/vf-bench/gate.py"))
    add(check_negative_control_demo(ctx))
    add(check_workflows_mention(ctx, "gate3/ci-runs-vf-bench",
                                (r"vfbench\.py", r"vf-bench/gate\.py"), "#412"))
    add(check_workflows_mention(ctx, "gate3/ci-runs-negative-control",
                                (r"negative-control",), "#413"))
    return checks


# ---------------------------------------------------------------------------
# Gate 4 — install is one command (epic DoD 4)
# ---------------------------------------------------------------------------

def check_file_exists(ctx, name, rel):
    if (ctx.repo / rel).is_file():
        return (name, PASS, f"{rel} exists")
    return (name, FAIL, f"{rel} missing")


def gate4(ctx):
    """Gate 4 — install is one command (epic DoD 4)."""
    checks = []

    def add(check):
        return ctx.record(checks, check)

    for doc in ("README.md", "docs/distribution.md"):
        name = f"gate4/install-command-in-{Path(doc).stem.lower()}"
        text = ctx.read(doc)
        if text is None:
            add((name, FAIL, f"{doc} missing"))
            continue
        count = text.count(INSTALL_CMD)
        if count:
            add((name, PASS, f"{doc}: {count} mention(s) of `{INSTALL_CMD}`"))
        else:
            add((name, FAIL, f"{doc}: `{INSTALL_CMD}` not mentioned"))
    add(check_file_exists(ctx, "gate4/checklist-exists", "docs/release-1.0-checklist.md"))
    add(check_workflow_green_at_head(ctx, "gate4", "install"))
    return checks


# ---------------------------------------------------------------------------
# Gate 5 — runtime re-pinned, chaining exercised (epic DoD 5)
# ---------------------------------------------------------------------------

def check_orca_pin(ctx):
    name = "gate5/orca-pin-live"
    text = ctx.read("runtime/pins.json")
    if text is None:
        return (name, FAIL, "runtime/pins.json missing")
    try:
        orca = json.loads(text)["orca"]
        witness = orca.get("witness")
        witnessed = str(orca.get("witnessed", ""))
        version = orca.get("version")
    except (ValueError, KeyError, TypeError, AttributeError) as e:
        return (name, FAIL, f"runtime/pins.json: no readable orca entry ({type(e).__name__}: {e})")
    if witness == "live" and witnessed >= PIN_MIN_WITNESSED:
        return (name, PASS, f"orca {version} witnessed {witnessed} live (fresh: >= {PIN_MIN_WITNESSED})")
    return (name, FAIL, f"orca {version}: witness={witness!r} witnessed={witnessed!r}; the gate "
                        f"needs witness 'live' and witnessed >= {PIN_MIN_WITNESSED}")


def check_chaining_report_published(ctx):
    name = "gate5/chaining-report-published"
    reports_dir = ctx.repo / "docs" / "reports"
    reports = sorted(p for p in reports_dir.glob("chaining-*") if p.is_dir()) \
        if reports_dir.is_dir() else []
    if reports:
        return (name, PASS, ", ".join(ctx.rel(p) + "/" for p in reports))
    return (name, FAIL, "no docs/reports/chaining-*/ directory — the chaining exercise's report "
                        "is not published")


def check_chaining_report_indexed(ctx):
    """A report nobody links is not published: the protocol under test
    (runtime/mission-chaining.md) or the run-archive index must name it."""
    name = "gate5/chaining-report-indexed"
    naming = [doc for doc in CHAINING_INDEXES if CHAINING_NEEDLE in (ctx.read(doc) or "")]
    if naming:
        return (name, PASS, f"{', '.join(naming)} name(s) {CHAINING_NEEDLE}*")
    return (name, FAIL, f"neither {' nor '.join(CHAINING_INDEXES)} names {CHAINING_NEEDLE}*")


def gate5(ctx):
    """Gate 5 — runtime re-pinned, chaining exercised (epic DoD 5)."""
    checks = []

    def add(check):
        return ctx.record(checks, check)

    add(check_orca_pin(ctx))
    add(check_chaining_report_published(ctx))
    add(check_chaining_report_indexed(ctx))
    add(check_issue_closed(ctx, "gate5", 416, "re-pin run"))
    add(check_issue_closed(ctx, "gate5", 417, "chaining exercise"))
    return checks


# ---------------------------------------------------------------------------
# Gate 6 — mechanization merged and used (epic DoD 6)
# ---------------------------------------------------------------------------

def check_tool_merged(ctx, tool, test):
    name = f"gate6/{Path(tool).stem}-merged"
    if not (ctx.repo / tool).is_file():
        return (name, FAIL, f"{tool} missing")
    if (ctx.repo / test).is_file():
        return (name, PASS, f"{tool} in tree, contract-tested by {test}")
    return (name, FAIL, f"{tool} in tree but {test} missing — merged without its contract test")


def check_gate_batch_used(ctx):
    name = "gate6/gate-batch-used"
    runs = ctx.repo / "docs" / "runs"
    stores = sorted(runs.glob("*/gate-batch.json")) if runs.is_dir() else []
    if stores:
        shown = ", ".join(ctx.rel(p) for p in stores[:3]) + (" …" if len(stores) > 3 else "")
        return (name, PASS, f"{len(stores)} run(s) carry a gate-batch.json store: {shown}")
    return (name, FAIL, "no docs/runs/*/gate-batch.json — no run has consumed gate-batch.py")


def check_watchdog_used(ctx):
    name = "gate6/watchdog-used"
    runs = ctx.repo / "docs" / "runs"
    needle = b"watchdog.py"
    hits = []
    if runs.is_dir():
        for path in sorted(runs.rglob("*")):
            if not path.is_file():
                continue
            try:
                if needle in path.read_bytes():
                    hits.append(ctx.rel(path))
            except OSError:
                continue
    if hits:
        shown = ", ".join(hits[:3]) + (f" … ({len(hits)} files)" if len(hits) > 3 else "")
        return (name, PASS, f"run artifacts name watchdog.py: {shown}")
    return (name, FAIL, "no file under docs/runs/ names watchdog.py — no run has consumed the watchdog")


def gate6(ctx):
    """Gate 6 — mechanization merged and used (epic DoD 6)."""
    checks = []

    def add(check):
        return ctx.record(checks, check)

    for tool, test in MECHANIZED:
        add(check_tool_merged(ctx, tool, test))
    add(check_gate_batch_used(ctx))
    add(check_watchdog_used(ctx))
    add(check_issue_closed(ctx, "gate6", 418, "liveness watchdog"))
    add(check_issue_closed(ctx, "gate6", 419, "gate-batch tooling"))
    return checks


# ---------------------------------------------------------------------------
# The run
# ---------------------------------------------------------------------------

GATES = (
    ("gate0", "Gate 0 — tree and catalog gates green", gate0),
    ("gate1", "Gate 1 — Phase 0 at zero (epic DoD 1)", gate1),
    ("gate2", "Gate 2 — flagships proven (epic DoD 2)", gate2),
    ("gate3", "Gate 3 — verifier moat held by CI (epic DoD 3)", gate3),
    ("gate4", "Gate 4 — install is one command (epic DoD 4)", gate4),
    ("gate5", "Gate 5 — runtime re-pinned, chaining exercised (epic DoD 5)", gate5),
    ("gate6", "Gate 6 — mechanization merged and used (epic DoD 6)", gate6),
)


def format_check(check):
    name, status, detail = check
    if status == SKIP:
        return f"SKIP({detail})  {name}"
    return f"{status}  {name}: {detail}"


def run_gates(ctx):
    """Every gate in checklist order -> [(gate_id, title, checks)]."""
    return [(gid, title, fn(ctx)) for gid, title, fn in GATES]


def summarize(results):
    counts = {status.lower(): 0 for status in STATUSES}
    for _, _, checks in results:
        for _, status, _ in checks:
            counts[status.lower()] += 1
    return counts


EXIT_INCOMPLETE = 3


def exit_code(counts):
    """1 on any FAIL; else 3 when a SKIP stands (the run proved less than the release
    needs, so a gate reading only the code cannot cut on it); else 0."""
    if counts["fail"]:
        return 1
    if counts["skip"]:
        return EXIT_INCOMPLETE
    return 0


def to_json(ctx, results, counts):
    return {
        "repo": str(ctx.repo),
        "head": git_head(ctx),
        "fast": ctx.fast,
        "skip_github": ctx.skip_github,
        "gates": [{"gate": gid, "title": title,
                   "checks": [{"name": n, "status": s, "detail": d} for n, s, d in checks]}
                  for gid, title, checks in results],
        "summary": counts,
        "exit": exit_code(counts),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="release_check.py",
        description="Run docs/release-1.0-checklist.md as commands: one PASS / FAIL / "
                    "SKIP(<reason>) line per check, then a summary.",
        epilog="exit 0: every check PASS · 1: any FAIL · 2: could not run. A SKIP never "
               "counts as a PASS; the summary counts it.")
    parser.add_argument("--repo", default=str(DEFAULT_REPO),
                        help="the checkout to gate (default: the repo this script lives in)")
    parser.add_argument("--fast", action="store_true",
                        help="skip the full unittest suite (~8 min); it reports SKIP(--fast)")
    parser.add_argument("--skip-github", action="store_true",
                        help="skip the gh-backed checks; they report SKIP(--skip-github)")
    parser.add_argument("--json", action="store_true",
                        help="print one JSON object instead of lines")
    args = parser.parse_args(argv)

    repo = Path(args.repo)
    if not repo.is_dir():
        print(f"release_check.py: --repo {args.repo}: not a directory", file=sys.stderr)
        return 2
    text_mode = not args.json
    if text_mode and hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")

    def stream(check):
        if text_mode:
            print("  " + format_check(check), flush=True)

    ctx = Context(repo, fast=args.fast, skip_github=args.skip_github, on_check=stream)
    results = []
    try:
        if text_mode:
            print(f"release check: {ctx.repo} @ {git_head(ctx) or 'HEAD unknown'}", flush=True)
        for gid, title, fn in GATES:
            if text_mode:
                print(f"\n{title}", flush=True)
            results.append((gid, title, fn(ctx)))
    except Exception:  # a gate raised: not a verdict, a broken run
        traceback.print_exc()
        print("release_check.py: could not run (a gate raised; see the traceback)",
              file=sys.stderr)
        return 2
    counts = summarize(results)
    code = exit_code(counts)
    if args.json:
        print(json.dumps(to_json(ctx, results, counts), indent=2))
    else:
        print(f"\nsummary: {counts['pass']} PASS, {counts['fail']} FAIL, {counts['skip']} SKIP, "
              f"{counts['info']} INFO -> exit {code}")
        skipped = [n for _, _, checks in results for n, s, _ in checks if s == SKIP]
        if skipped:
            print("skipped, so not a full run: " + ", ".join(skipped))
    return code


if __name__ == "__main__":
    sys.exit(main())
