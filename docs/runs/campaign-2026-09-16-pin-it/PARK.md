# Park register — pin-it selftest campaign (2026-09-16, afternoon)

PINNED-WITH-PARKED. This session ran from a plain shell with no sender terminal: every
sender-bound orchestration mutation refuses here (`no_active_sender_terminal` /
`no_active_terminal` — see `receipts/substrate-*.json`), which is BLOCKED-BY-SUBSTRATE — a
precondition verdict, never evidence about the mechanism. Nothing below was reclassified; each
keeps its morning-pin standing, and each names the exact probe it waits on. All are re-owed to
the next re-pin (#427), same as the morning register.

| Park | Probe (from a live Orca terminal, scratch Run, full teardown) |
|---|---|
| B01 Run scope verbs | `run-create --objective` → `run-current` → `run-use --id` on a second terminal; `task-list --run` / `check` honor the scope |
| B02 Consuming check | Mixed-batch `check --wait` → Delivery ≤50 → replay-until-`--ack`; `--types` wakes on other types (dispatch-lifecycle probe 3, first half) |
| B03 Group send | `send --to @all --type merge_ready` in a scratch Run (probe 3, second half) — 1.4.203's guide documents group scoping; replay still owed |
| B04 Task deps | `task-create --deps '["bogus"]'` → archive the refutation (probe 4); failed-dep stuck-pending strand |
| B05 Gates | `gate-create` → `gate-resolve` → `dispatch-show --task --preamble`: is the resolution there? (probe 5; source says the live builder carries none) |
| B06 Worker start roster | `worker-start` per roster agent — `state`, `stage`, `launch.effective`, `turnStart`, host `agentDefaultArgs` mode (probe 1) |
| B07 Inject receipt | `dispatch --inject --json` → `prompt.{requestId, stages}` inspected, never replayed (probe 2); `request_mismatch` on regenerated replay |
| B08 Live ask | `ask` blocks, timeout PENDINGs, `ask --resume <same id>` resumes; `reply --id` answers |
| B09 Release/retain | `worker-release --dispatch` exit contract (`release_unknown`→1, rest→0); `worker-retain` |
| B10 Danger lane | `vm recipe doctor <id>` verdict shapes through `sandbox_doctor.py` (needs a real recipe + placement binding) |

Carried over unchanged from `docs/runs/2026-09-16-pin-it-416/PARK.md` (which itself carries over
`docs/runs/2026-09-13-pin-it-266/PARK.md`): isolated old binary, second datadir,
roster/provider/trust, Windows/Linux hosts, paid/remote — same preconditions, still unmet here.

Substrate proof new in THIS run (both captured post-freeze from the installed 1.4.203 binary):

- `receipts/substrate-run-create.json` — `run-create` → `no_active_sender_terminal`
  ("Could not determine the sender terminal … run the command inside a live Orca terminal with
  `ORCA_TERMINAL_HANDLE` set")
- `receipts/substrate-check-peek.json` — `check --peek` → `no_active_terminal`

Teardown: nothing to tear down — both substrate probes refused before effects (no Run, no
terminal, no worktree created). No `reset`, no global change.
