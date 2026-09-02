# Ops — account inventory and incident process

Bus factor 1: Ravindra Kumar ([`ravidsrk`](https://github.com/ravidsrk),
`ravidsrk@gmail.com`). This page is the inventory of surfaces that can
break the catalog, and what to do at 2 a.m. It is not a product runbook —
missions already have those.

## Account inventory

| Surface | Account / handle | Lives in | Notes |
|---|---|---|---|
| GitHub | `ravidsrk` | [ravidsrk/orca-fleet](https://github.com/ravidsrk/orca-fleet) | source of truth, Actions (`validate` gates; `alert-on-failure` files a `ci-failure` issue when `validate` fails on `main`), private vulnerability reporting |
| Claude plugin marketplace | GitHub self-host + buildwithclaude auto-index | [`.claude-plugin/`](../.claude-plugin/plugin.json) | `/plugin marketplace add ravidsrk/orca-fleet`; official directory + skills.sh still [H-02](completion/HUMAN_ACTIONS.md) |
| greptile | maintainer CLI | [greptile.com](https://greptile.com/) | pre-push review on the maintainer machine; GitHub check on PRs |
| agentskills.io listing | not submitted | local `uvx --from skills-ref agentskills validate` | extra frontmatter (`proof`, `autonomy`, `proof_evidence`) is intentional — [CONTRIBUTING](../CONTRIBUTING.md) |
| Maintainer email | `ravidsrk@gmail.com` | [SECURITY.md](../SECURITY.md) | security reports (72h ack) and ops contact |

No other cloud accounts, registries, or production hosts. "Deploy" is merge
to `main` plus the plugin copy in `.claude-plugin/`.

## Incident (2 a.m.)

1. A red `validate` run on `main` files (or updates) an issue labeled
   [`ci-failure`](https://github.com/ravidsrk/orca-fleet/issues?q=label%3Aci-failure)
   — that issue is the alert; it arrives through normal issue
   notifications, not the opt-in Actions setting. Open the run it links —
   catalog gates (`scripts/validate.py`, `tests/`, `proof_status.py --check`)
   are the only environment; the run summary shows the proof rollup and
   routing score. Close the issue when `main` is green again. To prove the
   path without redding `main`: Actions → `alert-on-failure` → Run workflow
   (a `[drill]` issue is filed and closed by the same run).
2. If a clone or plugin load is broken: `plugin.json` `version` must equal
   the latest **dated** [CHANGELOG](../CHANGELOG.md) heading
   (`## [x.y.z] - YYYY-MM-DD`), not `[Unreleased]`. Do not half-cut a
   version bump.
3. Secrets never live in git (`.env`, `.secrets/` are ignored). Dispatch-key
   rotation must update **all three** verifier sources
   ([docs/verify-gate.md](verify-gate.md)):
   unset `ORCA_DISPATCH_PUBKEY`, land a new `.orca/dispatch-pubkey` through a
   reviewed PR, then on every verifier clone `git fetch origin` and confirm
   `git show origin/HEAD:.orca/dispatch-pubkey` equals the newly merged
   `.pub` (an unchecked fetch can leave the old pin). Do not leave a stale
   working-tree copy. Generate the pair with
   `runtime/scripts/dispatch-sign.py gen-key` **off the clone**; discard the
   old private seed. Security reports follow [SECURITY.md](../SECURITY.md).
