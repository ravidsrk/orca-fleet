STYLE = """Technical diagram for a software project README, flat vector illustration style.
Canvas: deep navy background (#0B1220) with a very faint, thin-lined constellation node-graph pattern in two corners (dim, decorative, never behind text).
Nodes: rounded rectangles with a 2px electric-blue (#4C8DFF) outline, slightly lighter navy fill (#121B2D), and a soft blue outer glow.
Typography: clean monospace font (like JetBrains Mono). Primary labels white, uppercase where written uppercase. Secondary captions smaller, muted grey-blue (#8A9BB8).
Arrows: thin blue lines with small arrowheads. Accent colours: green (#3DDC84) for verified/success, red (#FF5C5C) for void/fail/blocked, amber (#FFB84C) for human gates.
A small white orca silhouette in the bottom-right corner as a signature mark.
Generous spacing, nothing cramped, no photorealism, no stock-icon clutter, no watermark. Do not add a title unless one is given.
Render every label EXACTLY as written below, with the exact spelling and punctuation, and add no other words.

"""

HERO_DARK = """Wide website banner, flat vector illustration, no photorealism, no text other than the two lines given.
Background: deep navy (#0B1220) with a subtle radial glow toward the right and a very faint constellation node-graph (thin lines, small pale-blue dots) woven through the right half.
Right half: a pod of four stylised orcas (killer whales) swimming in formation toward the left, drawn as clean dark-navy shapes with white eye patches, electric-blue (#4C8DFF) rim-light edges and a soft blue glow; a thin horizontal waterline passes behind them.
Left half: the wordmark in large clean monospace type, white, exactly: orca-fleet
Beneath the wordmark, one line in smaller muted grey-blue (#8A9BB8) monospace, exactly: Give a mission a goal. Come back to an evidence-verified end state.
Keep all text at least 6% away from every edge. Calm, premium developer-tool aesthetic."""

HERO_LIGHT = """Wide website banner, flat vector illustration, no photorealism, no text other than the two lines given.
Background: near-white (#F4F7FD) with a very faint pale-blue constellation node-graph (thin lines, small dots) woven through the right half.
Right half: a pod of four stylised orcas (killer whales) swimming in formation toward the left, drawn as clean dark-navy (#0B1220) shapes with white eye patches and electric-blue (#4C8DFF) rim-light edges; a thin horizontal pale-blue waterline passes behind them.
Left half: the wordmark in large clean monospace type, dark navy (#0B1220), exactly: orca-fleet
Beneath the wordmark, one line in smaller muted grey-blue (#5B6B85) monospace, exactly: Give a mission a goal. Come back to an evidence-verified end state.
Keep all text at least 6% away from every edge. Calm, premium developer-tool aesthetic."""

SOCIAL = """Social-media preview card for a software project, flat vector illustration, no photorealism, no text other than the two lines given.
Background: deep navy (#0B1220) with a faint constellation node-graph (thin lines, small pale-blue dots) across the canvas.
One uniform background over the whole canvas — no bands, stripes, borders or colour changes anywhere. Composition centred, everything grouped in the middle two-thirds of the height.
Upper centre: the wordmark in large clean monospace type, white, exactly: orca-fleet
Directly beneath it, smaller muted grey-blue (#8A9BB8) monospace, exactly: Autonomous fleets for the Orca runtime
Lower centre-right: three stylised orcas (killer whales) swimming in formation toward the left, dark navy shapes with white eye patches, electric-blue (#4C8DFF) rim-light edges and a soft blue glow, with a thin horizontal waterline behind them.
Calm, premium developer-tool aesthetic."""

D = dict(aspect="16:9", dims=(1600, 900))

SPECS = [
    {"id": "three-layers", "out": "assets/diagrams/three-layers.jpg", **D, "prompt": STYLE + """Content: three wide horizontal layer boxes stacked vertically, top to bottom, each spanning most of the width, joined by short downward arrows with a caption beside each arrow.
Box 1 (top), large label: MISSIONS   caption beneath it: discoverable — one outcome each   small caption at its right edge: skills/
Arrow 1 caption: compose
Box 2 (middle), large label: PLAYBOOKS   caption: callable phase protocols   small caption at right edge: playbooks/
Arrow 2 caption: run on
Box 3 (bottom), large label: RUNTIME   caption: invisible — policies + primitives   small caption at right edge: runtime/
A thin muted footer line centred under the stack: only skills/ may hold a SKILL.md"""},

    {"id": "fleet-topology", "out": "assets/diagrams/fleet-topology.jpg", **D, "prompt": STYLE + """Content: a left-to-right topology in three columns.
Left column: one box, large label: HUMAN, with a simple person icon, caption: one-way gates — freeze · promotion. A double-headed horizontal arrow between it and the middle column, labelled: gates only.
Middle column: one tall box, large label: COORDINATOR, caption: one terminal · never writes code. Inside it, stacked, two smaller boxes: ledger (caption: one row per unit)  and  verifier (caption: re-derives claims from git).
Right column, header above it: WORKERS — fresh worktree + terminal each. Three boxes stacked vertically: builder (caption: writes the change),  reviewer (caption: build-blind),  conductor (caption: owns every merge).
Arrows: from COORDINATOR a right-pointing arrow to each worker box labelled: dispatch, and from each worker box a left-pointing arrow back to COORDINATOR labelled: evidence manifest. A short downward arrow from reviewer to conductor labelled: reviewed_sha."""},

    {"id": "evidence-protocol", "out": "assets/diagrams/evidence-protocol.jpg", **D, "prompt": STYLE + """Content: a sequence diagram with four vertical dashed lifelines under four header boxes across the top, left to right:
WORKER  ·  COORDINATOR  ·  VERIFIER (caption: fresh session)  ·  AUTHORITATIVE STATE (caption: git · tests · deploy).
Horizontal message arrows, top to bottom, each with its label written just above the arrow:
1. WORKER → COORDINATOR: worker_done + evidence manifest
2. COORDINATOR → VERIFIER: the manifest — a claim, not a fact
3. VERIFIER → AUTHORITATIVE STATE: re-derive the criterion set from the frozen source
4. VERIFIER → AUTHORITATIVE STATE: merge-base --is-ancestor head_sha origin/BASE
5. VERIFIER → AUTHORITATIVE STATE: clean-env test run at head_sha
6. VERIFIER → AUTHORITATIVE STATE: revert or mutate — does the proof go RED?
7. VERIFIER → AUTHORITATIVE STATE: reviewed_sha == head_sha ?
8. VERIFIER → COORDINATOR, a dashed return arrow with two labels: verified — advance (in green)  or  SUSPECT — re-dispatch (in red)
Footer line, small, centred: verify, never trust"""},

    {"id": "decision-gates", "out": "assets/diagrams/decision-gates.jpg", **D, "prompt": STYLE + """Content: three horizontal swim lanes stacked top to bottom, separated by thin lines, each with a bold lane label at the left and a flow running left to right.
Lane 1 label: MECHANICAL   caption: one defensible answer — naming, tooling with precedent, retry-on-transient.  Flow: a straight arrow passing through an open gate into a green-outlined box: auto-resolved + audit line.
Lane 2 label: TASTE   caption: reversible, reasonable people disagree — API shape, copy, structure.  Flow: an arrow into a small stack of three cards labelled: batched into a brief, then the arrow continues into a box: pick the recommendation, keep working — veto later.
Lane 3 label: ONE-WAY   caption: merge to default · deploy · rollback · delete · spend · secret rotation.  Flow: an arrow that stops at a heavy closed vault door with an amber lock and an amber person icon, labelled: HUMAN, ALWAYS, caption: never auto-resolved, never defaulted on timeout.
Footer, small, centred: every unit is lit by default — a reviewer reads the change; dark-eligible is opt-in and narrow"""},

    {"id": "merge-train", "out": "assets/diagrams/merge-train.jpg", **D, "prompt": STYLE + """Content: a single railway track running from the left edge to a station platform at the right labelled: BASE, caption: integration branch — never the default branch.
On the track a train of four rounded cars moving right, labelled from the front: PR #14  ·  PR #13  ·  PR #12  ·  PR #11, each car carrying a small tag: reviewed_sha.
At the front of the train a conductor figure holding a lantern, labelled: CONDUCTOR — one per BASE, with a small checklist beside it: open?  targets BASE?  head == reviewed_sha?  merge-base --is-ancestor.
One car, PR #13, is diverted onto a dashed side track curving away from the main track, with a red tag: STALE — head moved, and a caption on the side track: bounce to re-review, requeue at the back.
Captions along the bottom, small: arrival order, no priority lanes  ·  hot files build in parallel, merge as a chain"""},

    {"id": "attention-budget", "out": "assets/diagrams/attention-budget.jpg", **D, "prompt": STYLE + """Content: a left-to-right funnel composition.
Left: nine small terminal windows in a loose grid, each labelled: builder, headed above by: spawning is cheap.
They converge into a funnel shape. At the funnel's narrow neck a glowing gate labelled: WIP ≤ 3 builders; three lanes pass through it highlighted in blue, the remaining terminals are held back in a group labelled: queued.
At the neck a single person icon labelled: one human — the serial bottleneck, beside a small box: 1 build-blind reviewer per 3 builders.
Right: one calm horizontal outflow line ending in a green-outlined box labelled: merged.
Footer, small, centred: scale to verification capacity, not to the spawn UI"""},

    {"id": "reviewed-sha-freshness", "out": "assets/diagrams/reviewed-sha-freshness.jpg", **D, "prompt": STYLE + """Content: a horizontal git commit graph across the middle of the canvas: a line with three commit circles, left to right.
Commit 1 label: 6f7e3f8, caption: base.
Commit 2 label: 9b06458, with a glowing green circular seal above it reading: APPROVED — reviewed_sha 9b06458.
An arrow from commit 2 to commit 3 labelled: rebase · bot autofix · late push.
Commit 3 label: c41d7a2, caption: new head, with a dashed red circular seal above it reading: VOID — reviewed_sha ≠ head_sha, and a red stamp beside it: merge refused.
A curved loop arrow from commit 3 back up and around toward the seal, labelled: fresh build-blind review of the new head.
Footer, small, centred: "re-ran the gates green" is not a review"""},

    {"id": "liveness-resume", "out": "assets/diagrams/liveness-resume.jpg", **D, "prompt": STYLE + """Content: two horizontal bands, top and bottom, each with a bold label at the far left.
Top band label: WATCH.  A heartbeat ECG line runs left to right, beats regularly, then flatlines into a red X over a small terminal window labelled: worker — no heartbeat past the window. An arrow from it to a fresh glowing terminal window labelled: respawn in a FRESH terminal, with three captions beneath: reflection-before-retry  ·  bounded attempts, then escalate  ·  stuck-pending watchdog.
Bottom band label: RESUME.  A crashed terminal window with a red X labelled: dead coordinator. Beside it a document icon labelled: ledger, with an arrow labelled: seeds, pointing to a fresh glowing terminal labelled: new coordinator, which has three thin arrows to three small boxes labelled: worker, worker, worker, caption: reconnect, scoped to its own run.
Footer, small, centred: every "completed" unit is re-verified against git before it is trusted — git is truth, the ledger is its cache"""},

    {"id": "sandbox-profiles", "out": "assets/diagrams/sandbox-profiles.jpg", **D, "prompt": STYLE + """Content: three containment vessels side by side, left to right, each with a large monospace label above it and a caption below it.
Vessel 1: an open glass dome, label: ro, caption: read-only / plan mode — reviews, audits, report-only work.
Vessel 2: a workbench box with an open front, label: rw, caption: workspace-write — ordinary fix and build work.
Vessel 3: a sealed chamber with a red hazard stripe, label: danger, caption: bypass approvals — opt-in flag required — exploit PoCs, destructive tests. This chamber sits on a separate detached platform labelled: disposable per-workspace sandbox — never your machine. From the chamber an arrow labelled: git push the work branch BEFORE teardown, points to a small box: BASE via PR → review → merge train.
Footer, small, centred: least privilege that does the job — a lane whose sandbox died before the push is a failed lane"""},

    {"id": "one-router-per-worker", "out": "assets/diagrams/one-router-per-worker.jpg", **D, "prompt": STYLE + """Content: four worker desks in a row, each drawn as a small terminal window standing on a desk, with a two-line label beneath each desk in lowercase monospace (the book spines carry NO text).
Desk 1: on it exactly ONE glowing playbook book. Label beneath: worker A — with the second line: mattpocock/skills
Desk 2: on it exactly ONE glowing playbook book. Label beneath: worker B — with the second line: garrytan/gstack
Desk 3: on it exactly ONE glowing playbook book. Label beneath: worker C — with the second line: addyosmani/agent-skills
Desk 4: on it TWO overlapping books colliding, the whole desk struck through with a large red X. Label beneath: never — with the second line: two routers fight — clashing commands, competing routing
The four desks simply stand side by side: no arrows, icons, ticks or crosses between the desks, and no person icons anywhere.
Header, centred at the top, uppercase: ONE WORKER-PLAYBOOK ROUTER PER WORKER
Footer, small, centred, lowercase: compose across packs at the mission level — never inside one worker"""},

    {"id": "mission-chaining", "out": "assets/diagrams/mission-chaining.jpg", **D, "prompt": STYLE + """Content: a horizontal chain of three large chain-link shapes joined by two gate valves, left to right.
Header, centred at the top: "make it production-ready" = harden-it → prove-it → ship-it
Link 1 label: harden-it, glowing green with a check mark, caption beneath: CLEAN.
Valve 1, between link 1 and link 2: an open valve wheel in green, caption: verified terminal → proceed.
Link 2 label: prove-it, glowing green with a check mark, caption beneath: COVERED-WITH-PARKED — degraded.
Valve 2, between link 2 and link 3: a closed valve with a red horizontal bar across the chain and an amber person icon, caption: a degraded terminal stops the chain — advancing is a one-way human gate.
Link 3 label: ship-it, drawn dim and grey, caption beneath: not started.
Footer, small, centred: sequential only · declared up front · each link a full run with its own BASE · a chain that stops early is a correct outcome"""},

    {"id": "first-run", "out": "assets/diagrams/first-run.jpg", **D, "prompt": STYLE + """Every piece of text in this image is set in the same monospace font, including window labels and captions.
Content: a left-to-right composition.
Far left: a single terminal prompt window showing the line: > ship this: add /healthz  with a caption beneath: you — one command, and a small amber marker below it labelled: gate 1 — you confirm the freeze.
From that window arrows fan out to the right into a cluster of EXACTLY SIX small terminal windows arranged in a tidy 2-by-3 grid over a faint node graph. The cluster is headed: THE FLEET — coordinator + workers, each in its own worktree. The six windows are labelled, top row left to right: coordinator, builder, builder; bottom row left to right: builder, reviewer — build-blind, conductor. There is exactly one coordinator, exactly one reviewer and exactly one conductor.
The cluster's arrows converge to the right into one document icon labelled: evidence manifest — SHA-bound, stamped with a large green check mark reading: VERIFIED, caption: git, tests, review re-derived by a fresh session.
Far right: a small amber marker labelled: gate 2 — you merge the promotion PR."""},

    {"id": "mission-map", "out": "assets/diagrams/mission-map.jpg", **D, "prompt": STYLE + """Content: a decision tree, top to bottom, with compact boxes aligned in tidy columns; every mission name in white monospace, every caption small and muted beneath its name.
Title, centred at the top: WHICH MISSION DO I WANT?
Root box centred beneath the title: WHAT DO YOU HAVE?
Four branches fan out from the root into four columns, each headed by a category box.
Column 1 head: A GOAL TO BUILD. Beneath it two boxes joined by a down arrow:  map-it (caption: chart it into a frozen map)  then  ship-it (caption: build → review → release).
Column 2 head: KNOWN PROBLEMS. Beneath it a grid of sixteen boxes, two columns of eight, in this order:
clean-sweep (caption: drain the backlog)
oss-contribute (caption: PRs upstream, fork-only)
absorb-it (caption: drain the inbound PR queue)
harden-it (caption: close the security loop)
speed-it (caption: perf budget green)
modernize-it (caption: upgrade the deps)
migrate-it (caption: move a data shape safely)
prove-it (caption: close the test gap)
deflake-it (caption: flake zero)
floor-it (caption: a bar that fires)
reshape-it (caption: deepen, behaviour unchanged)
attest-it (caption: audit-grade evidence)
access-it (caption: WCAG conformance)
oncall-it (caption: telemetry, alerts, runbooks)
document-it (caption: coverage map, claims anchored)
field-test-it (caption: proof on hardware)
Column 3 head: A QUESTION, NOT A CHANGE. Beneath it two boxes:  review-it (caption: read-only verdict)  and  root-cause (caption: diagnosis only).
Column 4 head: OUR TOOLING DRIFTED. Beneath it one box:  pin-it (caption: re-pin the doctrine).
Footer, small, centred: missions are named for outcomes, never for packs"""},

    {"id": "hero-dark", "out": "assets/hero-dark.jpg", "aspect": "21:9", "dims": (2000, 848), "q": 88, "prompt": HERO_DARK},
    {"id": "hero-light", "out": "assets/hero-light.jpg", "aspect": "21:9", "dims": (2000, 848), "q": 88, "prompt": HERO_LIGHT},
    {"id": "social-preview", "out": "assets/social-preview.jpg", "aspect": "16:9", "dims": (2560, 1280), "q": 88, "prompt": SOCIAL},
]

from specs_missions import MISSIONS  # noqa: E402
SPECS += MISSIONS

SPECS.append({"id": "run-timeline", "out": "assets/diagrams/run-timeline.jpg", **D, "prompt": STYLE + """Content: a timeline of one real fleet run, read left to right.
Across the upper half, six phase boxes joined by arrows:
TRIAGE (caption: 10 issues → 7 build units + 3 parks)
→ BUILD WAVE (caption: 4 builders + 1 respawn — peak 5 live panes) with a small red exclamation badge on its corner
→ VERIFY (caption: "done" is a claim — checked against git)
→ REVIEW ROUNDS (caption: greptile + codex, bounded, SHA-bound)
→ INCIDENT, this box outlined in red with a red glow (caption: a parallel contributor's PRs discovered — openings frozen)
→ PIVOT (caption: 4 review-assist comments + 5 alternative PRs)
→ a green hexagon: DRY-WITH-PARKED (caption: 10 open at T0, 10 at close, 0 new)
Across the lower half, a horizontal timeline axis with tick marks and labels, evenly spread: T0 · +6m · +30m · +75m · +14h · close, aligned under the matching boxes.
Two callout lines from the axis to small notes beneath it: under +30m the note: dual-writer prevented — respawn pane closed;  under +14h the note: the two-denominator rule was born here.
Footer, small, centred: nothing here is illustrative fiction — every incident changed a runtime policy"""})
