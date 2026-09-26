"""One developer-contract card per mission: what you give it, what it interrupts you for, what you
get back, where it stops. The pipeline itself stays in each guide's mermaid block."""
from specs import STYLE, D

C = STYLE + """This is a one-screen developer contract card for one mission: large type, few words, no pipeline detail.
Layout: the mission title top-left in white monospace with a muted one-line outcome after it. Below it a 2-by-2 grid of four equal panels, each a rounded box with a small uppercase muted header in its top-left corner and one to three short lines of white monospace text in LARGE type:
top-left panel header: YOU GIVE IT
top-right panel header: IT INTERRUPTS YOU FOR
bottom-left panel header: YOU GET BACK — its first line is the terminal states drawn as small hexagons side by side (the clean one outlined green, the degraded one outlined amber), and its second line names the artifacts in muted text
bottom-right panel header: IT STOPS AT
Along the very bottom a thin strip: the phases as a chain of uppercase words separated by small arrows, in small muted type, no captions.
Every line must stay legible when the image is shown at half size: big primary text, short lines.
The title line is the ONLY text above the grid: the mission name, a dash, and the outcome, all on one line; never repeat the outcome as a second line or subtitle. No arrows, connector lines or brackets between panels or between lines of text inside a panel. No icons or symbols inside a line of text. The four panels are the same size. Draw exactly the hexagons listed under YOU GET BACK and no others — each hexagon contains its state name, and there are no empty or decorative hexagons or shapes. Exactly four panels; the artifacts line lives inside YOU GET BACK, never in a fifth panel or strip. The mission name in the title is lowercase, exactly as written.

"""

def m(id_, outcome, give, gates, states, artifacts, stops, phases):
    hexes = " and ".join(f"a hexagon {name} outlined {colour}" for name, colour in states)
    if len(states) == 1:
        hexes += " — this mission has exactly ONE terminal state, so exactly one hexagon: no amber hexagon, no degraded state, nothing else on that line"
    prompt = C + f"""Title: {id_} — {outcome}
YOU GIVE IT: {give}
IT INTERRUPTS YOU FOR: {gates}
YOU GET BACK: {hexes}; second line: {artifacts}
IT STOPS AT: {stops}
Phase strip: {phases}"""
    return {"id": id_, "out": f"assets/diagrams/missions/{id_}.jpg", **D, "prompt": prompt,
            "contract": {"outcome": outcome, "give": give, "gates": gates,
                         "states": [n for n, _ in states], "artifacts": artifacts,
                         "stops": stops, "phases": phases}}

G, A, R, X = "green", "amber", "red", "grey"

MISSIONS = [
m("ship-it", "build → review → release",
  "an intent, or a frozen spec",
  "gate 1 — confirm the frozen spec · gate 2 — merge the promotion PR",
  [("BUILT", G), ("PROMOTION_READY", G), ("RELEASED", X), ("DEPLOYED_AND_VERIFIED", X)],
  "slice PRs on BASE · a promotion PR with a traceability table · an evidence manifest per unit",
  "the highest release state you authorized, suffixed -WITH-PARKED when units were parked with your approval — it never merges to the default branch itself",
  "FREEZE → DECOMPOSE → BUILD → REVIEW → PROVE → LAND → RELEASE"),

m("clean-sweep", "a backlog exhausted to zero, PR per finding",
  "an audit report, an issue tracker, or docs that lie",
  "batch approval of refuted and duplicate closes · the promotion PR",
  [("DRY", G), ("DRY-WITH-PARKED", A)],
  "one merged PR per finding · a test that failed pre-fix · the final enumeration pasted in the ledger",
  "the promotion PR — every close backed by a merge SHA, never by worker memory",
  "ENUMERATE → TRIAGE → FIX → REVIEW → LAND → CLOSE → RE-ENUMERATE"),

m("harden-it", "a threat model closed, the fix re-attacked",
  "a system and its trust boundaries",
  "one-way remediations you perform yourself, like a secret rotation · the danger-sandbox grant",
  [("CLEAN", G), ("HARDENED-WITH-OPEN-ITEMS", A)],
  "exploit tests · class-wide fixes on BASE · re-attack transcripts · a fresh full audit",
  "parked P0/P1 named per item — no PoC ever runs on your machine",
  "THREAT-MODEL → AUDIT → FIX → LAND → RE-ATTACK → RE-AUDIT"),

m("speed-it", "every journey within budget, on a declared contract",
  "the journeys and their budgets",
  "a metric that cannot be measured to its contract · parking a journey · promotion",
  [("WITHIN-BUDGET", G), ("OPTIMIZED-WITH-PARKED", A)],
  "before → after on every fix PR · CI regression guards · a re-benchmark to the contract",
  "never a weaker proxy metric, never a lucky single run",
  "DECLARE → BASELINE → RANK → DIAGNOSE → FIX → PROVE → RE-BENCHMARK"),

m("modernize-it", "dependency currency, CI green at every merge",
  "a repo with a green CI baseline",
  "pinning a dependency, with a written reason and your reference · a forced stateful migration, handed to migrate-it",
  [("CURRENT", G), ("CURRENT-WITH-PINNED", A)],
  "one PR per dependency or coherent group · CI green at every merge · runtime-prove transcripts",
  "the lockfile regenerated, never hand-edited — and never audit fix --force",
  "INVENTORY → ORDER → UPGRADE → REVIEW → PROVE → LAND → RE-INVENTORY"),

m("prove-it", "a mutation-audited critical surface",
  "a runnable suite and a coverage tool",
  "confirming the critical surface · behaviour calls on bugs the tests surface",
  [("COVERED", G), ("COVERED-WITH-PARKED", A)],
  "merged tests that die under mutation · surfaced bugs fixed, parked, or handed off",
  "never asserting buggy behaviour as correct",
  "MAP → CONFIRM → CHARACTERIZE → MUTATION-AUDIT → REVIEW → LAND → RE-MAP"),

m("deflake-it", "flake zero, proven by a streak",
  "a suite nobody trusts",
  "quarantining a flake — only with a ticket you approve",
  [("STABLE", G), ("STABLE-WITH-QUARANTINE", A)],
  "one PR per flake with a red-by-revert ratchet · a GREEN_STREAK, local and CI, at one SHA",
  "no retry wrappers, ever — the diff is grepped for them",
  "DETECT → DIAGNOSE → FIX → CLOSE → PROVE"),

m("review-it", "a read-only, SHA-bound GO / NO-GO",
  "a PR or branch, and the spec it claims to implement",
  "nothing during the run — acting on the verdict is yours",
  [("GO", G), ("NO-GO", R)],
  "findings per axis, each quoting its motivating line · the verdict bound to reviewed_sha",
  "read-only — PROFILE=ro, not one byte of the tree modified",
  "PIN → STANDARDS · SPEC · TEST-ADEQUACY · RISK → AGGREGATE"),

m("map-it", "a foggy goal charted into a frozen map",
  "a goal too foggy to spec",
  "every decision ticket, one per session · the freeze",
  [("MAPPED", G), ("MAPPED-WITH-BLOCKED", A)],
  "a frozen map + verified Orca DAG that ship-it dispatches unchanged · decision tickets · a frozen spec",
  "no production code — decisions, not deliverables",
  "NAME → CHART → CLEAR THE FRONTIER → FREEZE → PREPARE THE DAG"),

m("root-cause", "a reproduced symptom, one demonstrated cause",
  "a symptom report",
  "authorizing the fix — after the diagnosis, never inside it",
  [("DIAGNOSED", G), ("DIAGNOSED-WITH-HANDOFF", G), ("INCONCLUSIVE", A)],
  "the pasted red-capable loop · ranked hypotheses with their falsifications · a fix handoff brief",
  "diagnosis only — it never merges a fix",
  "STOP-THE-LINE → RED LOOP → LOCALIZE → HYPOTHESES → FALSIFY → DEMONSTRATE"),

m("oss-contribute", "upstream PRs on a repo you cannot merge",
  "issues on an upstream repo you can only fork",
  "refuted and stand-down closes, in a batch · assist vs alternative PR · CLA and DCO signatures",
  [("CONTRIBUTED", G), ("CONTRIBUTED-WITH-PARKED", A)],
  "open, reviewed, etiquette-correct upstream PRs · review-assist comments · every thread answered",
  "the maintainer merges, never the fleet",
  "ENUMERATE → TRIAGE → BUILD ON THE FORK → REVIEW → OPEN PR → FOLLOW UP"),

m("attest-it", "conformance proven, or the gaps named",
  "a standard at a version, and a codebase",
  "the conformance verdict · every accepted gap",
  [("CONFORMANT", G), ("CONFORMANT-WITH-GAPS", A)],
  "evidence per obligation, re-derived in a fresh session · gaps with a named owner",
  "read-only — remediation is a separate ship-it or clean-sweep run",
  "FREEZE → EVIDENCE → RE-DERIVE → ATTEST"),

m("access-it", "WCAG 2.2 AA, oracle-clean, ceiling parked to a human",
  "a page, flow or component set and a WCAG 2.2 AA target",
  "the human-AT park — screen-reader and cognitive criteria · promotion",
  [("CONFORMANT", G), ("CONFORMANT-WITH-MANUAL-PARKED", A)],
  "an axe-core clean report · revert-to-violation controls · parked criteria with reasons",
  "never passing a criterion on the oracle's silence",
  "FREEZE → DETECT → FIX → LAND → RE-VERIFY → PARK"),

m("pin-it", "doctrine re-witnessed against the installed binary",
  "runtime doctrine and the installed Orca binary",
  "probes that are one-way — paid, remote, or human-only",
  [("PINNED", G), ("PINNED-WITH-PARKED", A)],
  "a receipt per claim · an archive of refuted claims · doctrine patched with citations",
  "a substrate failure never rewrites doctrine",
  "FREEZE → RE-WITNESS → CLASSIFY → PATCH → LAND"),

m("floor-it", "a written, numbered bar that CI enforces",
  "a repo whose standards live in people's heads",
  "freezing CONSTRAINTS.md — a one-way gate; headless runs park here",
  [("FLOORED", G), ("FLOORED-WITH-PARKED", A)],
  "CONSTRAINTS.md · one tool per dimension, proven RED · canary PRs · a guard against lowering the bar",
  "violations injected only on throwaway branches, never on BASE",
  "DETECT → FREEZE → WIRE → PROVE-FIRES → ENFORCE → GUARD"),

m("reshape-it", "hot modules deepened, behaviour unchanged",
  "git history and the import graph",
  "confirming the target surface · any public-API break",
  [("RESHAPED", G), ("RESHAPED-WITH-PARKED", A)],
  "a characterization net pinned first · before → after interface measurements · one PR per module",
  "the target list never grows on its own",
  "SCAN → CONFIRM → CHARACTERIZE → DEEPEN → REVIEW → RE-SCAN"),

m("field-test-it", "proven on the device, not on the desktop",
  "a paired device or emulator, and the app",
  "device pairing, permission grants, store and account surfaces",
  [("FIELD-PROVEN", G), ("FIELD-PROVEN-WITH-PARKED", A)],
  "repro recordings · on-device re-verify at the head SHA · a revert-to-red control · before and after baselines",
  "a green desktop run is never device evidence",
  "PAIR → BASELINE → REPRODUCE → FIX → RE-VERIFY → SNAPSHOT"),

m("migrate-it", "a data shape moved one deployable phase at a time",
  "a table set and a phase list, each phase with its down path",
  "CONTRACT — dropping the old shape · bake windows that need production telemetry",
  [("MIGRATED", G), ("MIGRATED-WITH-PARKED", A), ("ABANDONED", X)],
  "one PR per phase · up + down receipts with an empty schema diff · a parity archive · zero-use telemetry",
  "one phase of one table in flight — nothing dropped before the zero-reader window",
  "EXPAND → DUAL-WRITE → BACKFILL → SWITCH-READS → RETIRE-WRITES → CONTRACT"),

m("oncall-it", "operable, proven by a worker who cannot read the source",
  "a path set, with 2–4 on-call questions per path",
  "freezing the questions · cardinality and cost decisions · who gets paged",
  [("OPERABLE", G), ("OPERABLE-WITH-PARKED", A)],
  "instrumentation PRs · test-fired alerts with runbooks · a source-blind worker's manifest and its removal control",
  "a missing staging or alert channel parks — the oracle is never downgraded",
  "FREEZE → INSTRUMENT → ALERT → RUNBOOK → TEST-FIRE → INDUCE"),

m("absorb-it", "an inbound PR queue drained with credit intact",
  "an inbound pull-request queue",
  "closing a contribution without landing it, in a batch · design disagreements",
  [("ABSORBED", G), ("ABSORBED-WITH-PARKED", A)],
  "landed commits with the contributor's authorship · RED-on-base, GREEN-on-head receipts · closing comments with credit",
  "authorship is never rewritten — one follow-up, no nagging",
  "ENUMERATE → CLASSIFY → ABSORB → RECEIPT → REVIEW → LAND → CLOSE"),

m("document-it", "every public-surface cell filled, every claim anchored",
  "a public surface — extracted by a script, not by hand",
  "freezing the gap list · which entities deserve a tutorial or an explanation",
  [("DOCUMENTED", G), ("DOCUMENTED-WITH-PARKED", A)],
  "a page per cell with every claim anchored · rename-control transcripts · the coverage map re-derived at the final head",
  "never inventing a why, never rewriting a diagram",
  "EXTRACT → MAP → FREEZE → WRITE → CLAIM-VERIFY → REVIEW → LAND → RE-MAP"),

m("offload-it", "a recipe that provisions, proven by provisioning",
  "a repo, plus provider and agent accounts",
  "each paid checkpoint · the interactive agent login",
  [("OFFLOADED", G), ("OFFLOADED-WITH-PARKED", A)],
  "a wired recipe · a clear doctor transcript · an enacted provision transcript",
  "money and login stay human — no paid step without an explicit OK",
  "INSPECT → INTERVIEW → SCAFFOLD → SNAPSHOT → WIRE → DOCTOR → PROVISION"),
]
