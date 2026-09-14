from specs import STYLE, D

M = STYLE + """This is the state-machine diagram of one mission. Phase boxes flow left to right, wrapping onto a second row when needed with a clear connecting arrow. Terminal states are hexagons: the clean terminal outlined in green, the degraded terminal outlined in amber. Human gates are marked with a small amber person icon next to the box. Unless the text below names a loop arrow there are NO dashed or looping arrows anywhere. Draw ONLY the loop arrows the text names, each starting and ending exactly at the boxes named; a loop from row 2 to row 1 is a dashed arrow that leaves the top of its start box, runs along the top margin, and comes down into its end box. Draw a person icon ONLY where the text says "with an amber person icon", nowhere else. Alternative terminals sit side by side and are never chained in sequence. Every phase box carries its uppercase name with a short muted caption beneath it, all captions in the same monospace font. Put the mission title small at the top-left.

"""

def m(id_, prompt):
    return {"id": id_, "out": f"assets/diagrams/missions/{id_}.jpg", **D, "prompt": M + prompt}

MISSIONS = [
m("ship-it", """Title: ship-it — build → review → release
Row 1, left to right:
FREEZE (caption: gate 1 — you confirm the spec) with an amber person icon
→ DECOMPOSE (caption: tracer-bullet slices → Orca DAG)
→ a bracketed group of three parallel boxes stacked vertically: slice w1, slice w2, slice w3 (group caption: BUILD — one worker per slice, failing test first)
→ REVIEW (caption: build-blind, per slice) with a dashed red loop arrow back to the slices labelled: fix rounds, max 3
→ PROVE (caption: drive the real entry point)
→ LAND (caption: one merge train)
→ INTEGRATED PROVE (caption: at the BASE head, traceability table verified)
Row 2, left to right, connected from row 1:
hexagon BUILT (green) → PROMOTION PR (caption: traceability table) → hexagon PROMOTION_READY (green, caption: gate 2 — you merge) with an amber person icon → hexagon RELEASED (drawn dim grey, caption: human merged to default) → hexagon DEPLOYED_AND_VERIFIED (drawn dim grey, caption: deploy + canary window)
Footer, small, centred: stop where your authorization ends — PROMOTION_READY is never reported as RELEASED"""),

m("clean-sweep", """Title: clean-sweep — a backlog exhausted to zero, PR per finding
Far left, three small stacked source boxes feeding the first phase: audit document · tracker at T0 · doc claims
Row 1: ENUMERATE (caption: the full denominator, paginated) → SKEPTIC-TRIAGE (caption: reproduce or refute, per finding; batch gate for refuted / duplicate closes) with an amber person icon → FREEZE (caption: the findings list) → BOOTSTRAP BASE (caption: preflight — BASE ≠ default) → PER-FINDING (caption: verify-real → fix → PR → build-blind review; one finding = one PR)
Row 2: LAND (caption: one merge conductor, one train) → CLOSE (caption: merge SHA + a test that failed pre-fix) → RE-ENUMERATE with a dashed loop arrow back to SKEPTIC-TRIAGE labelled: new or reopened items → VERIFY THE FINAL TIP (caption: validate + test suite green at the final head) → hexagon DRY (green) and hexagon DRY-WITH-PARKED (amber) → a small grey box: promotion PR — left to you
Footer, small, centred: a finding closes off the verified merge, never off worker memory"""),

m("harden-it", """Title: harden-it — a threat model closed, the fix re-attacked
Row 1: THREAT-MODEL (caption: STRIDE per trust boundary) → AUDIT (caption: security lens, a PoC per P0/P1) → PoC ROUTING (caption: ro / rw / ephemeral sandbox / parked — before any PoC runs) → QUORUM VERIFY (caption: refute false positives, vote table recorded) → FIX (caption: exploit test first, audit the whole class)
Row 2: REVIEW + RUNTIME-PROVE (caption: drive the patched surface) → LAND (caption: merge conductor, one train) → RE-ATTACK (caption: independent worker — original exploit + variants) → RE-AUDIT (caption: full fresh pass) → hexagon CLEAN (green, caption: zero unrefuted P0/P1) and hexagon HARDENED-WITH-OPEN-ITEMS (amber, caption: parked P0/P1 named per item)
Align the rows so that RE-ATTACK on row 2 sits directly beneath PoC ROUTING on row 1. Exactly ONE dashed red arrow in the whole diagram, and it points UP only: it starts at the top edge of RE-ATTACK and ends with its single arrowhead at the bottom edge of PoC ROUTING, labelled: new holes. There is no arrow pointing down from PoC ROUTING. RE-AUDIT forks into the two hexagons, which are stacked one above the other to its right, each hexagon reached by its own solid arrow from RE-AUDIT.
A small amber person icon beside FIX with the caption: secret rotation and auth changes are one-way — done by you, verified dead
Footer, small, centred: HARDENED-WITH-OPEN-ITEMS is never reported as CLEAN"""),

m("speed-it", """Title: speed-it — every journey within budget, on a declared contract
Row 1: DECLARE (caption: metric contract per metric — before any number) → BASELINE (caption: every journey measured to its contract) → RANK (caption: breaches by gap × traffic) → DIAGNOSE (caption: profile, name the one dominant cause) → FIX (caption: PR per hotspot — before → after + CI GUARD)
Row 2: REVIEW + RUNTIME-PROVE (caption: drive the journey end to end) → LAND (caption: merge conductor, one train) → RE-BENCHMARK (caption: to the contract, never a lucky single run) → hexagon WITHIN-BUDGET (green) and hexagon OPTIMIZED-WITH-PARKED (amber, caption: infra or inherent-cost tradeoff, human ref)
Position RE-BENCHMARK on row 2 directly beneath RANK on row 1. Exactly one dashed loop arrow in the whole diagram: it rises vertically from the top of RE-BENCHMARK straight up into the bottom of RANK, labelled: breaches remain. The two hexagons are stacked one above the other to the right of RE-BENCHMARK, each with its own arrow from RE-BENCHMARK; nothing connects the two hexagons to each other. No person icons.
Footer, small, centred: fast but behaviourally wrong is a bug, not a win"""),

m("modernize-it", """Title: modernize-it — dependency currency, CI green at every merge
Row 1: INVENTORY (caption: outdated + advisories, changelog not version delta, reachability triage) → ORDER (caption: compatibility graph — security-reachable → patch/minor groups → majors, one per PR) → UPGRADE (caption: one dep or coherent group per PR, adapt call sites, shims) → a diamond: forces a stateful schema or data change?
From the diamond, branch labelled yes: HANDOFF → migrate-it (caption: parked until its phase evidence returns).  Branch labelled no: REVIEW (caption: build-blind) → RUNTIME-PROVE (caption: drive the real entry points) → LAND (caption: merge conductor, CI green at every merge)
Row 2: both branches join into RE-INVENTORY with a dashed loop arrow back to ORDER labelled: inventory not dry → hexagon CURRENT (green, caption: zero pins) and hexagon CURRENT-WITH-PINNED (amber, caption: every pin has a written reason + a human ref)
No person icons anywhere. Exactly one dashed loop arrow: from RE-INVENTORY back to ORDER, labelled: inventory not dry.
Footer, small, centred: registry-latest is not the truth — a supported older major is already current"""),

m("prove-it", """Title: prove-it — a mutation-audited critical surface
Row 1: MAP (caption: coverage gaps × money / auth / data / external-contract paths) → SCOPE CONFIRM (caption: a human bounds the critical list) with an amber person icon → CHARACTERIZE (caption: assert real behaviour — expected value from an independent source) → a diamond: passes, or reveals a bug?
From the diamond, branch labelled passes: MUTATION AUDIT (caption: flip a boundary, negate a condition — the assertion must die).  Branch labelled bug: SURFACED-BUG SUB-LOOP (caption: fix in-PR, park, or hand to clean-sweep — never assert the bug as correct)
Row 2: both branches join into REVIEW (caption: build-blind) → RUNTIME-PROVE (caption: the asserted behaviour is real at the true entry point) → LAND (caption: merge conductor) → RE-MAP → hexagon COVERED (green) and hexagon COVERED-WITH-PARKED (amber, caption: a bug or path parked needs-human)
Position RE-MAP on row 2 directly beneath CHARACTERIZE on row 1. Exactly one dashed loop arrow in the whole diagram: it rises vertically from the top of RE-MAP straight up into the bottom of CHARACTERIZE, labelled: paths remain. The two hexagons are stacked one above the other to the right of RE-MAP, each with its own arrow from RE-MAP. The only person icon is the one at SCOPE CONFIRM.
Footer, small, centred: a test that survives its mutation proves nothing"""),

m("deflake-it", """Title: deflake-it — flake zero, proven by a streak
Row 1: DETECT (caption: repeat runs, varied seed and order + CI retry history) → a diamond: deterministic — fails N of N?  Branch labelled yes: a dim grey box: route to clean-sweep — a bug, not a flake.  Branch labelled intermittent: DIAGNOSE (caption: build a loop that RAISES the failure rate, then classify) → FIX (caption: the root cause + red-by-revert RATCHET — retry wrappers banned)
Row 2: CLOSE (caption: PR per flake → build-blind review → conductor LAND) → PROVE (caption: GREEN_STREAK consecutive full-suite runs, local AND CI, at one SHA) → then PROVE forks into two alternative terminal hexagons stacked side by side, never in sequence: STABLE (green, caption: zero flakes, zero retry wrappers) and STABLE-WITH-QUARANTINE (amber, caption: human-approved ticket) with an amber person icon
Position PROVE on row 2 directly beneath DETECT on row 1. Exactly ONE dashed red arrow in the whole diagram, pointing UP only: it starts at the top edge of PROVE and ends with its single arrowhead at the bottom edge of DETECT, labelled: any flake resets the streak. The only person icon is the one at STABLE-WITH-QUARANTINE.
Footer, small, centred: one green run is an anecdote — the streak is the contract"""),

m("review-it", """Title: review-it — a read-only, SHA-bound GO / NO-GO
Left: PIN (caption: the fixed point — non-empty diff, spec source named, reviewed_sha recorded)
From PIN, arrows fan out to four parallel boxes stacked vertically in the middle: STANDARDS (caption: repo standards + smell baseline) · SPEC (caption: faithful to the frozen spec or issue?) · TEST-ADEQUACY (caption: would reverting the fix fail a test? judged statically) · RISK LENS (caption: scope-gated — security / perf / a11y / data-migration, only when the diff triggers it). A bracket beside the first three labelled: acceptance review — always, build-blind, isolated fresh sessions
All four arrows converge into AGGREGATE (caption: anti-false-positive gate — every finding quotes its motivating line; severity per finding)
Right: hexagon GO (green) and hexagon NO-GO (red, caption: any Critical or Required finding)
No person icons anywhere — this mission has zero human gates. No loop arrows. The only arrows are PIN → each axis, each axis → AGGREGATE, AGGREGATE → GO and AGGREGATE → NO-GO.
Footer, small, centred: PROFILE=ro — no fix authority, not one byte modified; the verdict is void if the head moves"""),

m("map-it", """Title: map-it — a foggy goal charted into a frozen map
Row 1: NAME THE DESTINATION (caption: past it = out of scope, unsharp = FOG) → CHART THE MAP (caption: decision tickets — sharp questions only) → CLEAR THE FRONTIER, drawn as two parallel boxes stacked: RESEARCH TICKETS (caption: AFK evidence gathering) and DECISION / GRILL TICKETS (caption: HITL — one decision per session) with an amber person icon → FOG CLEARS (caption: graduate newly sharp tickets) with a dashed loop arrow back to CLEAR THE FRONTIER labelled: route still foggy
Row 2: FREEZE THE PLAN (caption: decide-and-freeze — you confirm the spec) with an amber person icon → PREPARE THE DAG (caption: materialize + verify, never dispatch) → hexagon FROZEN MAP + DAG (green) → a dim grey box: handed to ship-it, unchanged
Footer, small, centred: decisions, not deliverables — no production code is written"""),

m("root-cause", """Title: root-cause — a reproduced symptom, one demonstrated cause
Row 1: STOP-THE-LINE (caption: preserve evidence) → RED-CAPABLE LOOP (caption: build it, RUN it, paste command + output) with a dashed loop arrow onto itself labelled: no red loop, no phase 2 → LOCALIZE + REDUCE (caption: layer table · git bisect run · minimize) → 3–5 RANKED HYPOTHESES (caption: falsifiable, shown before testing any) with a small side box: COMPETING-HYPOTHESIS DEBATE (caption: when causes are mutually exclusive)
Row 2: FALSIFY (caption: one variable at a time, DEBUG-tagged instrumentation) → DEMONSTRATE THE SURVIVOR (caption: evidence + a regression test at a correct seam) → hexagon DIAGNOSED (green), with a side hexagon ARCHITECTURE HANDOFF (amber, caption: no correct seam exists) → a dim grey box: FIX HANDOFF BRIEF (caption: separately authorized) with an amber person icon labelled: the one gate — authorizing the fix
Footer, small, centred: diagnosis only — the fix is never merged here"""),

m("oss-contribute", """Title: oss-contribute — upstream PRs on a repo you cannot merge
Row 1: ENUMERATE (caption: two denominators at T0 — open issues AND open PRs, paginated) → SKEPTIC-TRIAGE (caption: reproduce or refute; search code AND open PRs) → a diamond: classify
From the diamond, branch labelled buildable: BUILD ON THE FORK (caption: failing test first) → ACCEPTANCE-REVIEW (caption: build-blind, bounded fix rounds) → OPEN PR (caption: fork head → upstream default) → FOLLOW UP (caption: every review thread answered)
Branch labelled already-has-PR: CONTRIBUTION DECISION with an amber person icon (caption: taste gate) with three small outcomes beneath it: assist — quoted review comment on their PR · alternative PR — only on maintainer invitation · stand-down — externally covered
Branch labelled needs-human: PARK (caption: CLA / DCO / design call — the gate named)
Row 2: everything joins into RE-ENUMERATE (caption: both denominators) with a dashed loop arrow back to SKEPTIC-TRIAGE labelled: new or reclassified issues → hexagon CONTRIBUTED (green) and hexagon CONTRIBUTED-WITH-PARKED (amber)
Footer, small, centred: the maintainer merges, never the fleet — awaiting-maintainer-merge is a normal terminal"""),

m("attest-it", """Title: attest-it — conformance proven, or the gaps named
Row 1: a small input box: standard@version + codebase → FREEZE (caption: the obligation set, enumerated into a DAG, digest-locked) → EVIDENCE (caption: per obligation — ro workers, bound to authoritative state) → RE-DERIVE (caption: independently, in a fresh session) → a diamond: control satisfied?
From the diamond two separate branches leave, drawn as two parallel rows on the right-hand half, one above the other, and nothing connects the two rows to each other:
Upper branch, labelled evidence re-derived: VERIFIED (green outline) → hexagon CONFORMANT (green).
Lower branch, labelled no re-derivable artifact: GAP (caption: named, parked to a human / legal owner) with an amber person icon → hexagon CONFORMANT-WITH-GAPS (amber).
No arrow between VERIFIED and GAP, none between CONFORMANT and VERIFIED, none between the two hexagons. No loop arrows.
Footer, small, centred: no control is marked satisfied on an agent's word — the verdict is a one-way human door"""),

m("access-it", """Title: access-it — WCAG 2.2 AA, oracle-clean, ceiling parked to a human
Row 1: a small input box: surface + WCAG 2.2 AA target → FREEZE (caption: surface × criteria — digest-locked denominator, BASE bootstrapped) → DETECT (caption: at the BASE head — axe-core / Lighthouse, violations to a DAG) → FIX (caption: rw workers, structural items serialized) → REVIEW → LAND (caption: build-blind; one merge train)
Row 2: RE-VERIFY (caption: at the BASE head — oracle clean + revert-to-violation negative control) → PARK CEILING CRITERIA (caption: screen-reader / cognitive → human-AT reviewer) with an amber person icon → hexagon CONFORMANT (green) and hexagon CONFORMANT-WITH-MANUAL-PARKED (amber)
No dashed or looping arrows anywhere in this diagram; the flow is strictly forward. The only person icon is the one at PARK CEILING CRITERIA.
Footer, small, centred: the oracle sees roughly a third of WCAG — its silence is never a pass"""),

m("pin-it", """Title: pin-it — doctrine re-witnessed against the installed binary
Row 1: a small input box: runtime policies + scripts → FREEZE (caption: the claim inventory — digest-locked, CLI version recorded) → BOOTSTRAP BASE (caption: preflight — BASE ≠ default) → LOAD GUIDES (caption: orca skills get — a hypothesis, not proof) → RE-WITNESS (caption: each claim from a live Orca terminal; probes in a scratch worktree + teardown)
Row 2: CLASSIFY (caption: CURRENT · STALE · SUPERSEDED · BLOCKED-BY-SUBSTRATE — from receipts only) → PATCH (caption: rw workers, one claim per unit — a deletion needs a refutation receipt) → REVIEW → LAND (caption: build-blind; every edited line traces to a receipt) → hexagon PINNED (green) and hexagon PINNED-WITH-PARKED (amber, caption: the exact probe it waits on)
No dashed or looping arrows anywhere in this diagram; the flow is strictly forward. No person icons anywhere.
Footer, small, centred: a refuted claim is removed with its receipt archived — never merely closed"""),

m("floor-it", """Title: floor-it — a written, numbered bar that CI enforces
Row 1: DETECT (caption: measure current values, draft the dimensions) → BOOTSTRAP BASE (caption: preflight — BASE ≠ default) → FREEZE (caption: one-way gate — CONSTRAINTS.md is the first commit on BASE; headless runs park here) with an amber person icon → WIRE (caption: one tool per dimension, rw workers) → PROVE-FIRES (caption: throwaway injection → harness RED, revert → GREEN; a harness that stays GREEN never lands)
Row 2: REVIEW → LAND (caption: build-blind) → ENFORCE IN CI (caption: on BASE; a canary PR per gate must go RED, closed unmerged) → GUARD (caption: validator + CI job against bar-lowering diffs) → REFLECT (caption: untoolable dimensions recorded) → hexagon FLOORED (green) and hexagon FLOORED-WITH-PARKED (amber)
No dashed or looping arrows anywhere in this diagram; the flow is strictly forward. The only person icon is the one at FREEZE.
Footer, small, centred: a gate that was never seen RED is a belief, not a control"""),

m("reshape-it", """Title: reshape-it — hot modules deepened, behaviour unchanged
Row 1: a small input box: git history + import graph → SCAN (caption: 90-day window — churn × width, fan-in tiebreak, YAGNI cut) → CONFIRM-SURFACE (caption: one-way gate — a human bounds the target list) with an amber person icon → BOOTSTRAP BASE (caption: preflight — BASE ≠ default) → CHARACTERIZE (caption: the net pinned + mutation-audited BEFORE any restructure)
Row 2: DEEPEN (caption: rw workers, one module per unit — API breaks gated) → REVIEW (caption: build-blind) → LAND (caption: merge conductor) → RE-SCAN (caption: the confirmed surface, same probes — every module deepened or parked) → hexagon RESHAPED (green) and hexagon RESHAPED-WITH-PARKED (amber)
No dashed or looping arrows anywhere in this diagram; the flow is strictly forward. The only person icon is the one at CONFIRM-SURFACE.
Footer, small, centred: the net is green on both sides of every move — the suite staying green is the contract, not the proof"""),

m("field-test-it", """Title: field-test-it — proven on the device, not on the desktop
Row 1: a small input box: device or emulator → PAIR (caption: orca skills get guides; oracle tier + preconditions recorded) → BOOTSTRAP BASE (caption: preflight — BASE ≠ default) → BASELINE (caption: pre-change flows driven on-device, ledgered) → REPRODUCE (caption: per defect — recording / a11y tree / logs)
Row 2: FIX (caption: rw workers, one defect per unit) → REVIEW (caption: build-blind) → LAND (caption: merge conductor) → RE-VERIFY ON-DEVICE (caption: at the head SHA — GREEN + revert-to-red negative control) → SNAPSHOT-LEDGER (caption: post-change baseline recorded) → hexagon FIELD-PROVEN (green) and hexagon FIELD-PROVEN-WITH-PARKED (amber, caption: the exact device and step it waits on)
No dashed or looping arrows anywhere in this diagram; the flow is strictly forward. No person icons anywhere.
Footer, small, centred: the ledgered device session is the oracle — a green desktop run is never device evidence"""),

m("migrate-it", """Title: migrate-it — a data shape moved one deployable phase at a time
Row 1: PLAN (caption: freeze the table set + the phase list, each with its down path) → BOOTSTRAP BASE (caption: preflight — BASE ≠ default) → EXPAND (caption: deploy + bake) → DUAL-WRITE (caption: deploy + bake) → BACKFILL (caption: batched · throttled · resumable) → a diamond: full parity probe — counts + mismatches + sampled hashes, with a dashed loop arrow back to BACKFILL labelled: mismatch
Row 2: SWITCH-READS (caption: deploy + bake) → ZERO-READERS WINDOW (caption: telemetry pasted) → ARCHIVE PARITY (caption: while writes are still dual) → RETIRE-WRITES (caption: deploy + bake) → ZERO-WRITERS WINDOW (caption: telemetry pasted) → CONTRACT (caption: a separate deploy — verify removal) with an amber person icon labelled: one-way human gate → hexagon MIGRATED (green)
Two side hexagons: MIGRATED-WITH-PARKED (amber, caption: no prod telemetry the fleet can query) and ABANDONED (grey, caption: walked back down the exercised down paths)
Footer, small, centred: every phase — up, down, an empty schema diff; old code on the new schema and new code on the old schema both green; one phase of one table in flight"""),

m("oncall-it", """Title: oncall-it — operable, proven by a worker who cannot read the source
Row 1: FREEZE (caption: the path set + 2–4 on-call questions per path) with an amber person icon → BOOTSTRAP BASE (caption: preflight — BASE ≠ default) → INSTRUMENT (caption: events · correlation ID · RED/USE with bounded labels) → ALERT (caption: symptom-based, two severities, a justified threshold) → RUNBOOK (caption: Means / First check / Escalate-to)
Row 2: REVIEW (caption: build-blind) → LAND (caption: merge conductor) → TEST-FIRE (caption: a receipt from the channel) → INDUCE (caption: a failure in staging — a source-blind worker names the component) → a diamond: negative control — instrumentation removed, blind worker RED?  Branch labelled yes: hexagon OPERABLE (green).  Branch labelled no staging / no channel / cost call: hexagon OPERABLE-WITH-PARKED (amber)
No dashed or looping arrows anywhere in this diagram; the flow is strictly forward. The only person icon is the one at FREEZE.
Footer, small, centred: green on the induce without RED on the removal proves only that the failure was guessable"""),

m("absorb-it", """Title: absorb-it — an inbound PR queue drained with credit intact
Row 1: ENUMERATE (caption: at T0 — every open inbound PR, paginated, + linked issues) → CLASSIFY (caption: reproduce the claim on current main) → a diamond: class?
From the diamond, branch labelled absorbable: RECLASSIFY (caption: at the pinned current BASE, initial-main receipt retained) → ABSORB (caption: apply preserving Author: — a fleet amendment is a separate commit) → RECEIPT (caption: regression test RED on the pre-absorption base, GREEN on the absorbed head) → REVIEW (caption: build-blind) → LAND (caption: one PR against BASE) → CLOSE (caption: the inbound PR — landing SHA + credit line)
Branch labelled superseded / duplicate: BATCH GATE (caption: close citing the winning SHA) with an amber person icon.  Branch labelled needs-contributor / design-disagreement: PARK (caption: with a named ask — one follow-up, no nagging)
Row 2: RE-ENUMERATE (caption: the whole queue, paginated, again), with solid arrows coming into it from CLOSE, from BATCH GATE and from PARK. RE-ENUMERATE forks into two hexagons stacked one above the other to its right, each reached by its own solid arrow from RE-ENUMERATE: ABSORBED (green) and ABSORBED-WITH-PARKED (amber); nothing connects the two hexagons to each other. Exactly one dashed arrow in the whole diagram: it starts at RE-ENUMERATE and ends at CLASSIFY, labelled: non-terminal PRs remain.
RE-ENUMERATE is a normal-sized phase box like every other. The only person icon is the one at BATCH GATE. The only dashed arrow is the RE-ENUMERATE → CLASSIFY loop.
Footer, small, centred: the contributor's name stays on the commit — the credit is the outcome"""),

m("document-it", """Title: document-it — every public-surface cell filled, every claim anchored
Row 1: EXTRACT (caption: the public surface — a script at the BASE head, output + SHA pasted) → MAP (caption: coverage per quadrant — reference · how-to · tutorial · explanation; every cell cites file:line) → FREEZE THE GAP LIST (caption: critical = zero coverage; a human bounds tutorial / explanation) with an amber person icon → BOOTSTRAP BASE (caption: preflight — BASE ≠ default) → WRITE (caption: one cell per unit — reference first, from code archaeology)
Row 2: CLAIM-VERIFY (caption: every claim → file:symbol or a run; the rename control must go RED) → REVIEW (caption: build-blind — voice · accuracy · reachable in one hop) → LAND → RE-MAP (caption: at the final head — same extractor, new SHA) → hexagon DOCUMENTED (green, caption: zero critical gaps) and hexagon DOCUMENTED-WITH-PARKED (amber, caption: explanation-needs-author · tutorial-not-warranted · diagram-needs-human)
No dashed or looping arrows anywhere in this diagram; the flow is strictly forward. The only person icon is the one at FREEZE THE GAP LIST.
Footer, small, centred: prose quality is not the oracle — coverage, anchoring and reachability are"""),
]
