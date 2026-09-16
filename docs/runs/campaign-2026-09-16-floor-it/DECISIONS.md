# DECISIONS — floor-it self-test run (run-local; promotion copies grants to docs/DECISIONS.md)

2026-09-16T12:26:37Z · base-selection · taste · BASE=campaign/floor-it-selftest doubles as task delivery branch · satisfies BASE≠default + forks at origin/main tip; separate BASE branch would split evidence from delivery for no gain
2026-09-16T12:26:37Z · worker-pack · mechanical · no TASK pack mounted (zero dispatches) · park precedes WIRE; no worker exists to route, so no router is chosen and none co-mounted
2026-09-16T12:31:00Z · run-namespace · mechanical · RUN:- (no Orca Run created) · run-create refused no_active_sender_terminal (witnessed); borrowing another run's terminal as sender would impersonate it — coordinator-only run instead
2026-09-16T12:31:00Z · freeze-headless · mechanical · PARK at FREEZE, publish proposal only · one-way human gate; auto-freeze/default-on-timeout refused by gate-classification
2026-09-16T12:31:00Z · constraints-placement · mechanical · no repo-root CONSTRAINTS.md written · writing it would present an unfrozen bar as the freeze product; proposal lives in the run dir until a human freezes
2026-09-16T12:31:00Z · d12-fold · taste · PROPOSE folding agentskills-validate into D2 (human confirms) · CI-only duplicate of frontmatter checks D2 already runs; a separate dimension would double-count one property
