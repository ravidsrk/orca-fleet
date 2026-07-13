# Runtime policy — sandbox / danger profile

Worker permission is least-privilege by default. `spawn_worker.sh` PROFILE:
- `ro`  → codex --sandbox read-only / claude --permission-mode plan (report-only / audit work)
- `rw`  → codex --sandbox workspace-write / claude --permission-mode acceptEdits (default fix work)
- `danger` → bypass flags, ONLY with `ORCA_COORD_ALLOW_DANGER=1`.

## Danger belongs in an ephemeral sandbox, never on the host

`danger` profile (bypass approvals/sandbox) on your own machine violates least privilege no matter
how careful the prompt. The sanctioned home is a disposable per-workspace environment
(`orca-per-workspace-env` recipes: create/suspend/resume/destroy, `orca serve --recipe-json`
pairing, validated by `vm recipe doctor --provision`).

Lane contract: N sandboxes for N parallel danger lanes; harvest work OFF the mortal disk via
`git push` to the lane's own work branch BEFORE teardown (never straight to BASE — sandbox work
enters BASE through the normal PR + review + merge-train pipeline); DESTROY per lane and verify;
record `lane · sandbox · pushed branch@sha · destroyed ts` in the ledger. A lane whose sandbox died
before the push is a FAILED lane.

When a governance policy (a run's careful/freeze grant) is active, even sandbox danger needs an
explicit recorded human grant.
