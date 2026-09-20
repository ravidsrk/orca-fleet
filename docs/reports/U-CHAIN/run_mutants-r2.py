import re, subprocess, sys, shutil
from pathlib import Path

POLICY = Path("runtime/mission-chaining.md")
ORIG = POLICY.read_text()
BASE = Path("base-policy.md").read_text()
CMD = [sys.executable, "-B", "-m", "unittest",
       "tests.test_architecture.TestArchitecture.test_chain_link_boundary_is_specified", "-v"]

def bullet(text, start):
    """The whole top-level bullet whose first line starts with `start`."""
    m = re.search(r"(?ms)^- " + re.escape(start) + r".*?(?=^- \*\*)", text)
    assert m, start
    return m.group(0)

def repl_bullet(text, start, new):
    return text.replace(bullet(text, start), new)

def drop_bullet(text, start):
    return text.replace(bullet(text, start), "")

def sub(text, old, new):
    assert old in text, old[:60]
    return text.replace(old, new, 1)

PACE = "**Chains are human-paced"
PARK = "**The wait has a name"
CARRY = "**The carry has ONE shape"
LOCAL = "**Local-only targets must ship"

M = {}
M["base-policy"] = ("revert every doc addition, keep head test", lambda t: BASE)
M["drop-pacing"] = ("delete only the human-pacing bullet", lambda t: drop_bullet(t, PACE))
M["drop-park"] = ("delete only the named park / resume bullet", lambda t: drop_bullet(t, PARK))
M["drop-carry"] = ("delete only the handoff-shape bullet", lambda t: drop_bullet(t, CARRY))
M["drop-local"] = ("delete only the local reconstruction bullet", lambda t: drop_bullet(t, LOCAL))

M["pacing-first-boundary-only"] = (
    "weaken every-link human pacing to the first boundary only",
    lambda t: repl_bullet(t, PACE,
        "- **Chains are human-paced at the first link boundary only.** Subsequent boundaries\n"
        "  may proceed automatically once the preceding mission reaches a clean terminal.\n"))

M["park-no-resume-precondition"] = (
    "retain named terminal and fact vocabulary, remove the mandatory resume procedure",
    lambda t: repl_bullet(t, PARK,
        "- **The wait has a name: `PARKED-AT-PROMOTION`.** It is a CHAIN state.\n"
        "  A **landed promotion SHA** or **BASE-carry grant** may be logged for convenience;\n"
        "  neither is a precondition for resuming the parked chain.\n"))

M["park-no-procedure-defined"] = (
    "SPEC-2 mutant: reserve both resume terms, define no resume procedure",
    lambda t: repl_bullet(t, PARK,
        "- **The wait has a name: `PARKED-AT-PROMOTION`.** It is a CHAIN state, recorded in the\n"
        "  ledger header beside the link it stopped at. The terms **landed promotion SHA** and\n"
        "  **BASE-carry grant** are reserved; no procedure for resuming the park is defined.\n"))

M["carry-sections-optional"] = (
    "make the two carry sections optional without changing their vocabulary or fields",
    lambda t: sub(t, "Two sections, both required:",
                     "Two optional examples (consumers may omit both):"))

M["carry-schema-deleted"] = (
    "retain per-chain artifact and section names but remove every field declaration",
    lambda t: repl_bullet(t, CARRY,
        "- **The carry has ONE shape: the handoff log.** One Markdown file per chain, `handoff-log`.\n"
        "  Its two sections are a **carry table** and a **gate record**; their contents are\n"
        "  unspecified.\n"))

M["local-artifacts-optional"] = (
    "replace the local reconstruction requirement with explicitly optional artifacts",
    lambda t: repl_bullet(t, LOCAL,
        "- **Local-only targets may cite SHAs alone.** When a target has no remote, a\n"
        "  **pushed mirror** or embedded **reconstruction artifacts** are optional conveniences;\n"
        "  a leg is complete without either and need not publish reconstruction bytes.\n"))

M["local-seed-diff-optional"] = (
    "weaken the reconstruction payload while retaining the artifact label and mandatory publish",
    lambda t: sub(t,
        "embedded **reconstruction artifacts** committed beside the chain report that are\n"
        "  COMMIT-PRESERVING — a self-contained `git bundle` of the leg's refs, or an equivalent that\n"
        "  demonstrably reproduces every cited commit and its ancestry. Seed sources plus the leg's full\n"
        "  diff recover file bytes only, never the commit objects, so they are SUPPLEMENTAL and never\n"
        "  sufficient on their own — the exemplar's own\n"
        "  docs/reports/chaining-2026-09-16/leg1/RESTORE.md draws exactly that line.",
        "embedded **reconstruction artifacts** committed beside the chain report — a list of\n"
        "  commit SHAs is sufficient; source bytes are optional."))

M["local-publishes-neither"] = (
    "SPEC-2 mutant: reverse the publication requirement in place",
    lambda t: sub(sub(t, "Such a leg is complete only once", "Such a leg is complete even if"),
                  "the chain publishes one of two things, named in the report, and is INCOMPLETE without one:",
                  "the chain publishes neither of these optional things:"))

def run(label, why, fn):
    POLICY.write_text(fn(ORIG))
    p = subprocess.run(CMD, capture_output=True, text=True)
    POLICY.write_text(ORIG)
    out = (p.stdout + p.stderr).strip()
    first = next((l for l in out.splitlines() if "AssertionError" in l), "")
    verdict = "KILLED (RED)" if p.returncode != 0 else "SURVIVOR (GREEN)"
    print(f"{label}: exit={p.returncode}; {verdict} — {why}")
    if first:
        print(f"    {first.strip()}")
    return p.returncode

print("== POSITIVE CONTROL ==")
p = subprocess.run(CMD, capture_output=True, text=True)
print(f"fixed-head: exit={p.returncode}; {'GREEN' if p.returncode==0 else 'RED'} — unmutated head")
print("\n== MUTANTS ==")
surv = [k for k, (w, f) in M.items() if run(k, w, f) == 0]
print(f"\n{len(M)} mutants run; {len(M)-len(surv)} KILLED, {len(surv)} SURVIVORS: {surv or 'none'}")
p = subprocess.run(CMD, capture_output=True, text=True)
print(f"head-restored: exit={p.returncode}")
sys.exit(1 if surv else 0)
