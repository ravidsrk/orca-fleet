# DECISIONS — durable auto-resolves (`ts · gate-or-ask-id · class · answer · why · task_id?`)

2026-09-14T15:34Z · takeover-shape · taste · continue as clean-sweep source=tracker on BASE review/2026-09-14-holistic-fixes (reuse, not a new BASE) · the branch is the prior session's integration line with PR #387 open; a second BASE would strand it ·
2026-09-14T15:34Z · finding-source · mechanical · file the 2 pasted PR-review findings as tracker issues (A1 A2) before FREEZE · single source=tracker denominator; repo convention files every review finding; nothing verified yet so the T0 rule is unharmed ·
2026-09-14T15:35Z · stabilize-lane · taste · land the 4 dirty hunks via a worker terminal in the coordinator worktree, no unit PR · the hunks complete prior-run units inside PR #387's own head branch; PR #387's pending independent review is the check; clean-baseline waived with reason in TASK ·
2026-09-14T15:35Z · twin-enumeration · mechanical · query 1 coordinator-now, query 2 first triage worker pre-triage, FREEZE only on agreement · linear-enumeration verbatim ·
2026-09-14T15:45Z · run-adoption · mechanical · run-use --id run_0607bdc681e6 from live coordinator terminal (gen 2) after consumer_fenced on the run-create phantom handle · the binding must be a live terminal; recorded per liveness-resume ·
2026-09-14T15:47Z · exit-5-stop · mechanical · worker-stop ctx_39334916997c, no respawn beside it · spawn_worker.sh exit-5 contract verbatim · task_a6c1dfe46f13
2026-09-14T15:47Z · codex-dead · mechanical · all workers on claude (codex usage-limited to 2026-09-19, pane-verified); reviewer_mode falls back to same-vendor-fresh · provider evidence, no alternative on this host ·
2026-09-14T15:47Z · worker-cmd-lane · taste · WORKER_CMD custom-argv for every spawn with ORCA_COORD_ALLOW_CMD_OVERRIDE=1 (coordinator owns the flag semantics) · supervised lane unprovable on 1.4.201 (no args in launch.effective); 09-09 grok precedent ·
