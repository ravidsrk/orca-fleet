# Park register — pin-it #416 (2026-09-16)

PINNED-WITH-PARKED. This session ran from a plain shell: every sender-bound
orchestration mutation refuses here (`no_active_terminal` / `Could not determine the
sender terminal`), which is BLOCKED-BY-SUBSTRATE — a precondition verdict, never
evidence about the mechanism. Nothing below was reclassified; each keeps its 1.4.200
live receipt where one exists, and each names the exact probe it waits on. All are
re-owed to the next re-pin (#427).

| Park | Probe (from a live Orca terminal, scratch Run, full teardown) |
|---|---|
| Run scope verbs | `run-create --objective` → `run-current` → `run-use --id` on a second terminal; `task-list --run` / `check` honor the scope |
| Consuming check | Mixed-batch `check --wait` → Delivery ≤50 → replay-until-`--ack`; `--types` wakes on other types (dispatch-lifecycle probe 3, first half) |
| Group send | `send --to @all --type merge_ready` in a scratch Run (probe 3, second half) — 1.4.203's guide now documents group scoping; replay the doctrine against it |
| Task deps | `task-create --deps '["bogus"]'` → archive the refutation (probe 4); failed-dep stuck-pending strand |
| Gates | `gate-create` → `gate-resolve` → `dispatch-show --task --preamble`: is the resolution there? (probe 5; source says the live builder carries none) |
| Worker start roster | `worker-start` per roster agent — `state`, `stage`, `launch.effective`, `turnStart`, host `agentDefaultArgs` mode (probe 1) |
| Inject receipt | `dispatch --inject --json` → `prompt.{requestId, stages}` inspected, never replayed (probe 2); `request_mismatch` on regenerated replay |
| Live ask | `ask` blocks, timeout PENDINGs, `ask --resume <same id>` resumes; `reply --id` answers |
| Release/retain | `worker-release --dispatch` exit contract (`release_unknown`→1, rest→0); `worker-retain` |
| Danger lane | `vm recipe doctor <id>` verdict shapes through `sandbox_doctor.py` (needs a real recipe + placement binding) |

Carried over unchanged from docs/runs/2026-09-13-pin-it-266/PARK.md: isolated old
binary, second datadir, roster/provider/trust, Windows/Linux hosts, paid/remote —
same preconditions, still unmet here.
