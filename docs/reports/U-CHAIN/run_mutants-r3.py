"""Round-3 mutation battery for the chain contract test.

Round 2 killed all thirteen of `run_mutants-r2.py`'s mutants and still returned NO-GO:
the reviewers wrote twelve NARROWER mutants that kept every matched noun while the
relationship or condition it governed disappeared, and all twelve survived. This battery
is that set — replayed verbatim in intent against the round-3 policy — plus three mutants
for BOT-4's new freshness rule and three neutral reflows that must stay GREEN.

The soundness and baseline fixes (BOT-5, R2-HARNESS) live in `mutants_core`: a kill is an
ASSERTION failure from the covering test, never merely a nonzero exit, and both controls
must be green or the harness fails.

Run from the repository root, in a DISPOSABLE checkout — it rewrites
runtime/mission-chaining.md between cases and restores it after each.

    python3 docs/reports/U-CHAIN/run_mutants-r3.py
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

# ---------------------------------------------------------------- round-2 battery (13)
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

# ------------------------------------------- round-2's twelve executed survivors (#441)
M["own-promoted-ancestry-inverted"] = (
    "RED",
    "R2-TA-441 survivor: invert the ancestry relationship, keep every noun",
    lambda t: sub(t, "BASE tip is an ancestor of the DEFAULT",
                     "BASE tip is not an ancestor of the DEFAULT"))

M["own-promoted-wrong-commit"] = (
    "RED",
    "R2-TA-441 survivor: substitute the seed commit for the completed BASE tip",
    lambda t: sub(t, "leg N's integration BASE tip is an ancestor of the DEFAULT",
                     "the repository's initial seed commit is an ancestor of the DEFAULT"))

M["own-grant-no-sha"] = (
    "RED",
    "R2-TA-441 survivor: drop the granted SHA from the carry grant",
    lambda t: sub(t, "fork leg N's UNPROMOTED BASE tip, with the granted SHA written down.",
                     "fork leg N's UNPROMOTED BASE tip."))

M["own-grant-no-unpromoted-fork"] = (
    "RED",
    "R2-TA-441 survivor: replace the whole fork/SHA condition with an unconditional resume",
    lambda t: sub(t, "that leg N+1 may fork leg N's UNPROMOTED BASE tip, with the granted SHA written down.",
                     "that leg N+1 may resume without checking a BASE tip or writing down any SHA."))

M["own-grant-promoted-only"] = (
    "RED",
    "R2-TA-441 survivor: flip UNPROMOTED to PROMOTED, collapsing the two alternatives into one",
    lambda t: sub(t, "fork leg N's UNPROMOTED BASE tip", "fork leg N's PROMOTED BASE tip"))

M["own-offline-nonexistent-ref"] = (
    "RED",
    "R2-TA-441 survivor: point an offline target at `origin/<default>`",
    lambda t: sub(t,
        "and a valid LOCAL ref, the local default branch, for an explicitly OFFLINE\n"
        "     target with no remote, never a nonexistent `origin/…`);",
        "and `origin/<default>` for both remote targets and targets with no remote);"))

M["own-carry-source-content-removed"] = (
    "RED",
    "R2-TA-443 survivor: drop `from`/`content`, keep carry id and input status",
    lambda t: sub(t,
        "     · `from` (leg number + source class: parked / backlog / noticed-not-touched) · `content` (the\n"
        "     item, pinned to file:line at that leg's cited SHA) · `input status` for the consuming leg\n",
        "     · `input status` for the consuming leg\n"))

M["own-gate-identity-state-removed"] = (
    "RED",
    "R2-TA-443 survivor: drop gate identity and state, keep owner and resume",
    lambda t: sub(t, "inter-mission gate — which gate, its state, the human who",
                     "inter-mission gate — the human who"))

M["own-missing-handoff-empty"] = (
    "RED",
    "R2-TA-443 survivor: declare a missing handoff log an empty, finished carry",
    lambda t: sub(t, "MISSING handoff log is an unfinished chain, never an empty one.",
                     "MISSING handoff log is an empty carry and counts as a finished chain."))

M["own-reconstruct-ancestry-removed"] = (
    "RED",
    "R2-TA-444 survivor: drop 'and its ancestry' from the equivalent artifact",
    lambda t: sub(t, "demonstrably reproduces every cited commit and its ancestry.",
                     "demonstrably reproduces every cited commit."))

M["own-mirror-ref-fields-removed"] = (
    "RED",
    "R2-TA-444 survivor: drop the mirror's written remote and pushed refs",
    lambda t: sub(t, "**pushed mirror** of the target (the remote and the pushed refs written down), or",
                     "**pushed mirror** of the target, or"))

M["own-artifact-hash-removed"] = (
    "RED",
    "R2-TA-444 survivor: remove the published-byte integrity obligation",
    lambda t: sub(t,
        "Every published\n"
        "  artifact is hashed into the run-close integrity inventory (evidence-manifest.md), so a later\n"
        "  audit can tell the bytes have not moved.",
        "Published artifacts need not be hashed into the run-close integrity inventory."))

# ----------------------------------------------- the new freshness rule itself (BOT-4)
M["own-freshness-refresh-removed"] = (
    "RED",
    "BOT-4: drop the refresh obligation, leaving the cached ref to answer the resume check",
    lambda t: sub(t,
        "`origin/<default>` for a REMOTE target — REFRESHED immediately before the check\n"
        "     (`git fetch origin <default>`), with the resolved default SHA written down, on\n",
        "`origin/<default>` for a REMOTE target — read as cached, with no refresh required, on\n"))

M["own-freshness-unproven-reversed"] = (
    "RED",
    "BOT-4: treat a ref of unestablishable freshness as landed rather than parked",
    lambda t: sub(t,
        "whose freshness cannot be established leaves the promotion UNPROVEN and the chain parked,\n"
        "     never landed",
        "whose freshness cannot be established is accepted as landed anyway"))

M["own-ancestry-subject-unpinned"] = (
    "RED",
    "BOT-4/#441: unpin the ancestry subject so any commit can satisfy the check",
    lambda t: sub(t,
        "the ancestry subject is leg N's own\n     completed BASE tip and no other commit; ",
        ""))

# -------------------------------------------------- neutral reflows that must stay GREEN
M["neutral-soft-wrap-park"] = (
    "GREEN",
    "neutral: reflow the landed-promotion-SHA phrase across a line break",
    lambda t: sub(t,
        "  1. a **landed promotion SHA** — leg N's integration BASE tip is an ancestor of the DEFAULT\n",
        "  1. a **landed\n     promotion SHA** — leg N's integration BASE tip is an ancestor of the DEFAULT\n"))

M["neutral-soft-wrap-publish"] = (
    "GREEN",
    "neutral: reflow the publication requirement across a line break",
    lambda t: sub(t,
        "nothing and the chain report is unverifiable on its own terms. Such a leg is complete only once\n"
        "  the chain publishes one of two things",
        "nothing and the chain report is unverifiable on its own terms. Such a leg is complete only\n"
        "  once the chain\n"
        "  publishes one of two things"))

M["neutral-soft-wrap-freshness"] = (
    "GREEN",
    "neutral: reflow the new freshness clause across a line break",
    lambda t: sub(t,
        "whose freshness cannot be established leaves the promotion UNPROVEN and the chain parked,\n",
        "whose freshness cannot be\n     established leaves the promotion UNPROVEN and the chain parked,\n"))

main(M)
