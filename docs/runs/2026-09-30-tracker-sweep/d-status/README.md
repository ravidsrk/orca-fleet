# clean-sweep run_fb923397d46a — unit D-STATUS (release-status reconciliation)

Builder record for one documentation unit of the 2026-09-30 tracker sweep. The sweep stops at a
reviewed build/PR: full tracker acceptance stays parked, so this is neither a DRY verdict nor a
proof-tier promotion, and a human release grant is still owed.

- **Base → head:** `e7089cbf` → `8b9627a0` on `codex/reconcile-release-status-20260930`
  (PR base `codex/remaining-issues-2026-09-30`). Four commits: TODOS.md, docs/ops.md,
  runtime/dispatch-lifecycle.md (+ regenerated activation loads), tests.
- **Contract:** [`contract.json`](contract.json), a byte copy of the coordinator's `build-contract.json`
  (`sha256:6903dee998aa2d04d6f61a134f0526fc5936414282a03884f940a266303549b6`), AC-1..AC-3. Later
  coordinator amendments (shard weight, wording feedback) live in its LEDGER, not in this copy.
- **Manifest:** [`manifest.json`](manifest.json) — every command recorded by
  `runtime/scripts/evidence-run.py`, with `wtree` equal to `8b9627a0^{tree}` (`7c7f93a2`).

| AC | Stale claim at base | Now | Guard |
|---|---|---|---|
| AC-1 | TODOS.md: "none of its findings is filed as an issue yet" | label query for #510–#525; #511/#515/#518 open at T0; epic #526 | `TodosPointsAtTheFiledReadinessIssues` |
| AC-2 | ops.md: `.github/workflows/` "contains only" validate/negative-control/alert, no deploy job; poll unfiltered by event/status | merge vs tag-driven `release.yml`/`publish-dist.yml`; poll = main-health's completed main push filter; absent/stale/non-success pages (#528, no monitor claimed) | `OpsRollbackNamesThePublishingWorkflows` |
| AC-3 | dispatch-lifecycle.md: live PIN v1.4.209; v1.4.203 "the live PIN"; "CURRENT at v1.4.209" | live PIN v1.4.215 (`docs/runs/2026-09-28-pin-it-500.md`); older witnesses historical; v1.4.215 park register | `DispatchLifecycleNamesTheCurrentPin` |

## Receipts

- Failing-first: [`red-before-fix.txt`](red-before-fix.txt) (20 failures, all on stale claims).
- Negative control: [`negative-control.txt`](negative-control.txt) — each file reverted from base
  goes RED (6 / 10 / 5 failures; 21 together); seven hand mutants all KILLED; clean head GREEN.
- Gates at head: [`validate.txt`](validate.txt), [`gen-badges-check.txt`](gen-badges-check.txt)
  (empty = fresh), [`focused-tests.txt`](focused-tests.txt), and the full suite as the CI-equivalent
  four shards `scripts/shard-tests.py --shard N --of 4` under `env -u ORCA_TERMINAL_HANDLE`
  (452 + 710 + 639 + 618 = 2419 tests, all exit 0).

## Runner notes

- An earlier full `unittest discover` on pre-commit content (before the coordinator's wording
  feedback) FAILED with 2 failures, for two causes: `test_shard_tests` wanted a `WEIGHTS` entry
  for the new module (added in `scripts/shard-tests.py`, authorized by the coordinator), and
  `test_check_reply.test_reply_argv` read the ambient `ORCA_TERMINAL_HANDLE` of the Orca pane
  (green with it unset; production runtime untouched). The final run uses a clean CI environment.
- **Protocol deviation:** the content commits preceded the final successful suite (the contract asks
  for validate + full suite before any commit). The final records bind to the committed tree; the
  coordinator's clean-clone gates at the report tip are the authority.

## Blocker handoff (from the coordinator LEDGER, T0 2026-09-30T06:10:17Z)

Evidence handoff only, not a completion or tier claim. All ten remain open; re-enumeration at
06:32Z showed no change since T0.

| Issue | Owed (named external gate) |
|---|---|
| [#511](https://github.com/ravidsrk/orca-fleet/issues/511) | Maintainer authorization of the exact 0.7.0 cut (prepared `fda5e4e1`), its tag/push, provenance and historical Releases |
| [#515](https://github.com/ravidsrk/orca-fleet/issues/515) | External ship-it run evidence (README Proof column already covered) |
| [#518](https://github.com/ravidsrk/orca-fleet/issues/518) | Tag-populated `dist`, clean-machine plugin witness, reduced copy |
| [#526](https://github.com/ravidsrk/orca-fleet/issues/526) | Road-to-1.0 epic: authorized 1.0.0 tag and all child evidence |
| [#527](https://github.com/ravidsrk/orca-fleet/issues/527) | Ubuntu mission run driven by `orca-ide`, bound retained bundle |
| [#528](https://github.com/ravidsrk/orca-fleet/issues/528) | External monitor hosting, alert destination, delivered-alert drill |
| [#529](https://github.com/ravidsrk/orca-fleet/issues/529) | Non-maintainer review-it run with retained artifacts |
| [#530](https://github.com/ravidsrk/orca-fleet/issues/530) | Second maintainer with write access and independent approving review |
| [#508](https://github.com/ravidsrk/orca-fleet/issues/508) | Out of scope: quarterly re-pin due 2026-12-28 (or earlier minor/drift trigger) |
| [#235](https://github.com/ravidsrk/orca-fleet/issues/235) | External marketplace aggregator submissions and listing URLs |

## Parked

Independent build-blind review and PR (integrator); #528's external monitor and drill (needs-human);
tracker acceptance of #511/#515/#518/#526. Not verified-CLOSED: no independent approval exists.
