# pin-it for #266 — Orca 1.4.200 live re-pin

**PINNED-WITH-PARKED.** Not PINNED. Installed binary is the oracle.

| | |
|---|---|
| RUN | `run_5378b2e2f926` |
| COORDINATOR | `term_577830b7-5cdb-46f7-ade9-39de699e5605` |
| BASE | `pin-it/266-1.4.200` |
| FORK_POINT | `9c8e5a2a198d16c2e5215f0c31caeecc84d28687` |
| T0 | 2026-09-13T07:22:08Z |
| SOURCE | frozen inventory `docs/reports/release-20260912/pin/` + CLI 1.4.200 `2ecde717b4561cae1701a27615f704434232399a` |
| WIP | builders=0 reviewers=0 |

## Oracle

- CLI `orca --version` → `1.4.200` ([receipt](receipts/installed-version.txt))
- App `CFBundleShortVersionString` 1.4.200; `orca-local-build.json` commit `2ecde717b4561cae1701a27615f704434232399a`
- Guides archived under [guides/](guides/): `orchestration` + 7 references, `orca-cli` + 3 references

This continues the 2026-09-12 inventory (309 parents / 373 unfinished children). The inventory is not shrunk. Previous PARTIAL-WITNESS: `docs/runs/2026-09-12-runtime-repin/`.

## Live classifications this run

| Claim | Receipt | Class |
|---|---|---|
| Installed version vs `runtime/pins.json` | [installed-version.txt](receipts/installed-version.txt) | STALE pin (was v1.4.199 source) → **patched** to v1.4.200 live |
| `worker-list --run <id>` scopes to that Run | [worker-list-bound.json](receipts/worker-list-bound.json) `scope.source=flag`, total 0 | CURRENT |
| Unscoped `worker-list` enumerates runtime history | [worker-list-unscoped.json](receipts/worker-list-unscoped.json) `scope.source=all`, total 299, `hasMore` true (worker rows and `nextCursor` omitted; cursor decoded to a dispatch ID) | CURRENT |
| `worker-list --from` | [worker-list-from-no-run.json](receipts/worker-list-from-no-run.json) `invalid_argument` | CURRENT (flag does not exist on this verb) |
| Receipted-send / `request_mismatch` doctrine | already on `main` at `dispatch-lifecycle.md:35-36` citing 2026-09-12 receipts | CURRENT |
| Original #266 line ("receipted sends exist only in unreleased source") | absent from current `dispatch-lifecycle.md` | SUPERSEDED (already patched before this run) |

`spawn_worker.sh` already NOTES when PATH Orca ≠ `runtime/pins.json` (issue #301 / #266 CI check). After this pin update, a matching 1.4.200 is silent; a later bump arms pin-it again. Contract: `tests/test_spawn_worker.py`.

## Park register

Unfinished children remain those in [CONTINUATION.md](../../reports/release-20260912/pin/CONTINUATION.md) (373). Families that need a second Orca datadir, v1.4.199 isolated binary, Windows/Linux host, paid provider, or owner-approved roster/trust are PARKED with that exact precondition — not classified SUPERSEDED.

Obtainable local fixtures listed there were not all re-run in this session (attention: this run landed the live pin + the #266 dispatch-lifecycle stale pin sentence). They stay unfinished, not closed.

## Teardown

Scratch worktree `pin-it-266-scratch` and coordinator terminal are retired after landing. Run `run_5378b2e2f926` is retained (no run-delete verb).
