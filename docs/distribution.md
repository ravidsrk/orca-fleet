# Distribution, discoverability & trust

*How orca-fleet reaches users, and what its proof records establish.*

> Trust guidance checked 2026-09-12. Historical index check 2026-09-01 (issue #210).
> Submissions that need a human account remain [H-02](completion/HUMAN_ACTIONS.md).

## State the evidence and who checks it

Listings should link to retained evidence and identify its authority:

- **Deterministic checks:** the validator checks catalog structure, declared autonomy levels,
  generated badge freshness and proof-report bindings. A tier above `doctrine-only` requires
  a retained report with an inventory that re-hashes at its named commit. These checks do not
  establish that a mission achieved its outcome. See the [run archive](runs/).
- **Worker-attested records:** `commands[]`, provenance and recorded verifier outcomes originate
  in the worker's environment. `run_report.py` checks bindings and hashes; it does not rerun
  verification or independently authenticate the worker's ledger.
- **Coordinator-owned reruns:** an independent process must use the frozen contract, inspect
  authoritative git/review state, rerun tests in a clean environment at the exact SHA, and execute
  the applicable negative control. Deploy/review identity also needs a coordinator check when
  shipping. Installing the catalog does not perform these steps.
- **Advisory native hooks:** `Stop`/`TaskCompleted` hooks run in the worker's session, where inputs
  and keys are worker-influenceable. They provide local checks; independence requires execution
  outside that session with coordinator-controlled inputs. See the
  [gate trust boundary](verify-gate.md#trust-boundary).

Badge freshness binds generated counts to repository state. A discovered test count does not
establish that the tests passed; use an actual CI result for execution status. Lead listings with
these specific guarantees and their limits, alongside the available run evidence.

## Install paths (already shipped)

| Path | For | Mechanism |
|---|---|---|
| Plugin marketplace | try the whole catalog | `/plugin marketplace add ravidsrk/orca-fleet` → `/plugin install orca-fleet` (`.claude-plugin/`) |
| Symlink a mission | fork/adapt one outcome | `ln -s .../skills/<mission> ~/.claude/skills/<mission>` (preserves the relative `playbooks/`/`runtime/` refs) |

## Index check (2026-09-13; previous 2026-09-01)

Agent-reachable surfaces. "Listed" means a search returned this repo, not that
a human submitted it.

**Re-run 2026-09-13: nothing moved in twelve days** — with one row that was not re-checked and
says so. buildwithclaude, skills.sh and claudemarketplace.net were re-measured against their live
endpoints and hold. The self-hosted marketplace is the documented install path and
`agentskills validate` is a local check, so neither depends on an indexer.
`anthropics/claude-plugins-official` could NOT be re-checked and carries
`(unverified 2026-09-13)` in the table itself: read its `no` as of 2026-09-01, not today.

Holding is the expected result while #235 (H-02) is unactioned — these surfaces need a human with
submit rights, so an agent re-check can only confirm the gap, never close it. Two details
sharpened:

- buildwithclaude's record still carries `updatedAt` **2026-09-01** — it has not re-indexed
  since the first check — and its blurb reads *"10 outcome-named autonomous fleets"*. That is
  a cache of an older GitHub **About** string, which itself now reads 17, against a catalog of
  **21**. Three different counts are in circulation and none of them is right. The About text
  is a repository setting, not a file in this tree; fixing it is the upstream of this row.
  The text to paste is now checked in at [about.md](about.md) and carries no count at all —
  the same way `plugin.json` and `marketplace.json` already describe this catalog — so a
  re-index after the maintainer applies it cannot reintroduce a number that goes stale.
- claudemarketplace.net returns the literal page text `No results for "orca-fleet"`. The
  string `orca-fleet` does appear three times in that HTML — in the title, the search input's
  `value`, and the no-results line — so grepping the page for the slug reports a hit that is
  only the query echoed back. Match on the result payload, not the page.

`anthropics/claude-plugins-official` could not be re-checked from here: `marketplace.json`
returns HTTP 404 at that path and the repository API returns 403 for this session. Its row is
carried forward from 2026-09-01 and is **unverified at this date** rather than re-confirmed —
said in the row as well as here, because a reader scanning a table dated today will not find a
caveat three paragraphs above it (PR #342 review).

| Surface | Listed? | Evidence |
|---|---|---|
| Self-hosted marketplace | yes | `/plugin marketplace add ravidsrk/orca-fleet` (already the install path) |
| [buildwithclaude.com](https://buildwithclaude.com/api/search?q=orca-fleet) | yes (auto-index) | slug `@ravidsrk/orca-fleet`; 0 installs; description still carries a stale hardcoded catalog count |
| [skills.sh](https://www.skills.sh/api/search?q=ravidsrk) | **no** — indexes the predecessor `ravidsrk/autonomous-fleet` instead | search `ravidsrk/orca-fleet` returns stablyai/orca skills, not this catalog |
| [claudemarketplace.net](https://www.claudemarketplace.net/search?q=orca-fleet) | no | search payload `skills: []`, `mcpServers: []` |
| [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official) | no **(unverified 2026-09-13)** | `marketplace.json` had neither `orca-fleet` nor `ravidsrk` **at 2026-09-01**; not re-checkable from this session — that path now 404s and the repository API returns 403 |
| `agentskills validate` | name/description/compatibility/license pass | extras `proof`/`autonomy`/`proof_evidence` are intentional (issue #211) |

No indexer currently publishes a does-it-load score for this catalog (buildwithclaude
`installs: 0`).

## External submission checklist (H-02)

These still need an account with rights to submit. Do not flip them from a clone:

- [ ] Submit to **anthropics/claude-plugins-official** (their plugin-directory form) and to
      community aggregators that are not GitHub-scraping this repo (claudemarketplace.net;
      get `ravidsrk/orca-fleet` onto skills.sh so the predecessor listing is not the hit).
- [ ] Confirm a green **"does-it-load"** score once an indexer actually scores the pack.
- [ ] On every listing a human files, lead with the **`proof:` trust badge** framing + a
      link to the [run archive](runs/). The buildwithclaude auto-index currently leads with
      a stale catalog-count blurb — replace that copy when a submit form exists.
- [x] `agentskills.io` required fields pass locally; extras documented (issue #211).

## Optional: a proof-status badge

A future `assets/badges/proof.json` (generated by `scripts/gen-badges.py`, checked by
`check_badge_freshness`) could surface the catalog's proof mix as `runtime/scripts/proof_status.py`
reports it — at this writing 0 external-run · 0 self-run · 21 doctrine-only, figures the navigation
test binds to the live rollup so they cannot rot silently — in the README badge row, turning honesty
into a visible summary of retained proof records.
Deferred here to keep this change doc-only; tracked as a follow-up.

## See also

- [Proof over doctrine](../ARCHITECTURE.md) · [run archive](runs/) · [platform-ride & absorption risks](platform-ride.md)
