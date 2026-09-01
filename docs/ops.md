# Ops — account inventory and incident process

Bus factor 1: Ravindra Kumar ([`ravidsrk`](https://github.com/ravidsrk),
`ravidsrk@gmail.com`). This page is the inventory of surfaces that can
break the catalog, and what to do at 2 a.m. It is not a product runbook —
missions already have those.

## Account inventory

| Surface | Account / handle | Lives in | Notes |
|---|---|---|---|
| GitHub | `ravidsrk` | [ravidsrk/orca-fleet](https://github.com/ravidsrk/orca-fleet) | source of truth, Actions (`validate` workflow), private vulnerability reporting |
| Claude plugin marketplace | not submitted | [`.claude-plugin/`](../.claude-plugin/plugin.json) | local install path works; community aggregators are [H-02](completion/HUMAN_ACTIONS.md) / [G-07](https://github.com/ravidsrk/orca-fleet/issues/210) |
| greptile | maintainer CLI | [greptile.com](https://greptile.com/) | pre-push review on the maintainer machine; GitHub check on PRs |
| agentskills.io listing | not submitted | local `uvx --from skills-ref agentskills validate` | extra frontmatter (`proof`, `autonomy`, `proof_evidence`) is intentional — [CONTRIBUTING](../CONTRIBUTING.md) |
| Maintainer email | `ravidsrk@gmail.com` | [SECURITY.md](../SECURITY.md) | security reports (72h ack) and ops contact |

No other cloud accounts, registries, or production hosts. "Deploy" is merge
to `main` plus the plugin copy in `.claude-plugin/`.

## Incident (2 a.m.)

1. Open the latest GitHub Actions `validate` run on `main` — catalog gates
   (`scripts/validate.py`, `tests/`, `proof_status.py --check`) are the
   only environment.
2. If a clone or plugin load is broken: `plugin.json` `version` vs the
   latest [CHANGELOG](../CHANGELOG.md) heading; do not half-cut a version
   bump.
3. Secrets never live in git (`.env`, `.secrets/` are ignored). Rotate
   `ORCA_DISPATCH_*` with `runtime/scripts/dispatch-sign.py gen-key` and
   update the verifier's trusted pubkey. Security reports follow
   [SECURITY.md](../SECURITY.md).
