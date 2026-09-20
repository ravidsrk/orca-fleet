"""Round-2 mutation battery for the chain contract test — REPLAYABLE.

Round 2 found this harness unreplayable (BOT-5: it read an untracked `base-policy.md`
and exited before any mutant ran) and unsound (R2-HARNESS: it called any nonzero exit a
kill and reported success with failed controls). Both fixes live in `mutants_core`; the
mutant list below is unchanged, so the round-2 13/13 claim replays exactly as recorded.

Run from the repository root, in a DISPOSABLE checkout — it rewrites
runtime/mission-chaining.md between cases and restores it after each.

    python3 docs/reports/U-CHAIN/run_mutants-r2.py

The round-3 battery, which adds the twelve survivors round 2 executed, is
`run_mutants-r3.py`.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mutants_core import baseline, drop_bullet, main, repl_bullet, sub  # noqa: E402

BASE = baseline()

PACE = "**Chains are human-paced"
PARK = "**The wait has a name"
CARRY = "**The carry has ONE shape"
LOCAL = "**Local-only targets must ship"

M = {}
M["base-policy"] = ("RED", "revert every doc addition, keep head test", lambda t: BASE)
M["drop-pacing"] = ("RED", "delete only the human-pacing bullet", lambda t: drop_bullet(t, PACE))
M["drop-park"] = ("RED", "delete only the named park / resume bullet", lambda t: drop_bullet(t, PARK))
M["drop-carry"] = ("RED", "delete only the handoff-shape bullet", lambda t: drop_bullet(t, CARRY))
M["drop-local"] = ("RED", "delete only the local reconstruction bullet", lambda t: drop_bullet(t, LOCAL))

M["pacing-first-boundary-only"] = (
    "RED",
    "weaken every-link human pacing to the first boundary only",
    lambda t: repl_bullet(t, PACE,
        "- **Chains are human-paced at the first link boundary only.** Subsequent boundaries\n"
        "  may proceed automatically once the preceding mission reaches a clean terminal.\n"))

M["park-no-resume-precondition"] = (
    "RED",
    "retain named terminal and fact vocabulary, remove the mandatory resume procedure",
    lambda t: repl_bullet(t, PARK,
        "- **The wait has a name: `PARKED-AT-PROMOTION`.** It is a CHAIN state.\n"
        "  A **landed promotion SHA** or **BASE-carry grant** may be logged for convenience;\n"
        "  neither is a precondition for resuming the parked chain.\n"))

M["park-no-procedure-defined"] = (
    "RED",
    "SPEC-2 mutant: reserve both resume terms, define no resume procedure",
    lambda t: repl_bullet(t, PARK,
        "- **The wait has a name: `PARKED-AT-PROMOTION`.** It is a CHAIN state, recorded in the\n"
        "  ledger header beside the link it stopped at. The terms **landed promotion SHA** and\n"
        "  **BASE-carry grant** are reserved; no procedure for resuming the park is defined.\n"))

M["carry-sections-optional"] = (
    "RED",
    "make the two carry sections optional without changing their vocabulary or fields",
    lambda t: sub(t, "Two sections, both required:",
                     "Two optional examples (consumers may omit both):"))

M["carry-schema-deleted"] = (
    "RED",
    "retain per-chain artifact and section names but remove every field declaration",
    lambda t: repl_bullet(t, CARRY,
        "- **The carry has ONE shape: the handoff log.** One Markdown file per chain, `handoff-log`.\n"
        "  Its two sections are a **carry table** and a **gate record**; their contents are\n"
        "  unspecified.\n"))

M["local-artifacts-optional"] = (
    "RED",
    "replace the local reconstruction requirement with explicitly optional artifacts",
    lambda t: repl_bullet(t, LOCAL,
        "- **Local-only targets may cite SHAs alone.** When a target has no remote, a\n"
        "  **pushed mirror** or embedded **reconstruction artifacts** are optional conveniences;\n"
        "  a leg is complete without either and need not publish reconstruction bytes.\n"))

M["local-seed-diff-optional"] = (
    "RED",
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
    "RED",
    "SPEC-2 mutant: reverse the publication requirement in place",
    lambda t: sub(sub(t, "Such a leg is complete only once", "Such a leg is complete even if"),
                  "the chain publishes one of two things, named in the report, and is INCOMPLETE without one:",
                  "the chain publishes neither of these optional things:"))

main(M)
