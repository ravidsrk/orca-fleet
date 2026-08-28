# Run report — ship-it self-run, 2026-08-28

First recorded run of the flagship mission. Mission: **ship-it**, entry = frozen spec
(`decide-and-freeze` validate branch), target: this repo itself. A small-but-non-trivial slice —
`runtime/scripts/proof_status.py`, a proof-posture reporter + `--check` CI lens over the mission
catalog — driven through the canonical pipeline. Proof tier earned: **self-run** (external-run
requires a repo that is not this catalog).

| field       | value |
|-------------|-------|
| coordinator | Claude (interactive session); dispatches + verifies, does not write code |
| BASE        | `ravidsrk/orca-fleet` `ship/proof-status-2026-08` @ `6970ede` (frozen-contract commit) |
| baseline    | `main` @ `62447ba`: validate.py green, 129 tests green |
| runtime     | Orca task dispatch (background workers), git + gh |
| workers     | 2 dispatched: builder (task, rw, own slice branch) · acceptance reviewer (build-blind, ro, instructed-isolation) |
| reviewer_mode | instructed-isolation (fresh agent, no build context; recorded as the weaker guarantee it is vs cross-vendor) |
| terminal    | **PROMOTION_READY** — slice BUILT into BASE, promotion PR (BASE → `main`) open, human-owned |

## Terminal state — all four release states named

| State | Reached? | Evidence / bound |
|-------|----------|------------------|
| `BUILT` | **exercised** | slice merged to BASE, ancestry-verified (`head_sha 932449d` ancestor of `origin/ship/proof-status-2026-08`) |
| `PROMOTION_READY` | **exercised** | promotion PR BASE → `main` open with a traceability table (this run stops here) |
| `RELEASED` | **bounded** | human gate #2 — the fleet never self-merges the promotion; reached when the promotion PR is human-merged to `main` |
| `DEPLOYED_AND_VERIFIED` | **bounded** | no deploy/canary surface exists for a docs+skills catalog — no runtime to promote; explicitly out of reach, not skipped |

## Convergence proof (traceability)

Frozen contract: [`frozen-spec.md`](2026-08-28-ship-it-selfrun/frozen-spec.md) @
`sha256:72219ea…` — the AUTHORITATIVE denominator, supplied by the coordinator, re-derived by the
independent verifier (never the worker's own manifest — the #103 authority model).

| Frozen criterion | Bound test (passes on BASE head) |
|------------------|----------------------------------|
| AC-1 every mission reported with name/tier/evidence/resolves, once | `test_ac1_every_mission_appears_once`, `test_ac1_evidence_resolution` |
| AC-2 coverage rollup counts per tier + total | `test_ac2_rollup_counts` (asserts the zero-count tier too) |
| AC-3 `--check` non-zero iff advanced-tier evidence missing; `--json` records; default exits 0 | `test_ac3_check_nonzero_when_evidence_missing`, `test_ac3_check_zero_when_all_resolve`, `test_ac3_default_report_exits_zero`, `test_ac3_json_records` |

Union of slice contracts (`{AC-1, AC-2, AC-3}`) equals the frozen spec's criterion set — verified at
freeze and here. No unassigned criterion; no criterion without a passing test. Single-slice run, so
the two-level denominator collapses to one unit.

## Pipeline evidence

1. **Validate + freeze** (coordinator): froze the 3-AC contract to `frozen-spec.md`, committed on
   BASE, computed the authoritative digest. Entry route = frozen spec (no grill).
2. **Decompose** (coordinator): one tracer-bullet slice (`proof_status.py` + test); foundation
   already green, nothing to scaffold.
3. **Build** (worker, rw, own branch off BASE): implemented to the ACs, stdlib-only; commit
   `932449d`; evidence manifest [`build-manifest.json`](2026-08-28-ship-it-selfrun/build-manifest.json);
   negative control [`negctrl.txt`](2026-08-28-ship-it-selfrun/negctrl.txt) = inject a
   doctrine-only→self-run mission with a missing `proof_evidence` → `--check` RED (exit 1), revert →
   GREEN (exit 0). 7 unit tests green.
4. **Acceptance review** (worker, build-blind, instructed-isolation): pre-diff expectations written
   from the ACs alone (predicted rollup miscount, presence-not-resolution `--check`, cwd-vs-root
   resolution, tautological test as the failure modes to hunt); none present. **GO** on
   spec-fidelity, standards (stdlib only, shebang, parser ported from validate.py, no scope creep),
   and truth (the negative control genuinely binds); `reviewed_sha = 748b328`. Two non-blocking
   notes: `.is_file()` vs validate.py's `.exists()`, and unparseable-frontmatter tolerance — both
   defensible lens-vs-gate separation.
5. **Runtime-prove + independent verify** (coordinator): re-ran the tests and `--check` on the real
   repo; ran `verify.py` against the manifest with the coordinator's authoritative
   `--contract-source/--contract-digest` (not the worker's) and `--repo`; independently reproduced
   the negative control first-hand (injected `deflake-it`, `--check` exit 1 + `[MISSING]`/`FAIL`,
   reverted to exit 0, tree clean).
6. **Land** (coordinator): merged the slice into BASE (`--no-ff`, BASE tip `9d83f47`); post-merge
   ancestry check passes.

## Verifier outcome (recorded exactly)

`verify.py` (the #103 authority-anchored verifier) on the build slice, against the coordinator's
frozen contract:

- **GREEN**: scope (authoritative `contract.digest` matches; `criteria[]` cover `{AC-1,AC-2,AC-3}`
  exactly), `base_sha`/`head_sha` real commits, reviewed-SHA freshness, negative control (revert →
  RED corroborated by the artifact), post-merge ancestry.
- **RED (bounded)**: the mutation-unit **independent-review gate** — `verify.py` requires an
  APPROVED GitHub review at `head_sha`, looked up on GitHub, not read from the manifest. A solo
  self-run has no second GitHub identity to approve, so this gate cannot be satisfied autonomously.
  The acceptance review was instead performed build-blind by an independent reviewer worker (above),
  and the promotion PR carries Greptile's automated review-assist plus the human merge gate.

**This RED is the finding, not a failure of the run.** The hardened verifier correctly refuses to
grade an unreviewed mutation as done; what a solo fleet cannot manufacture is an *independent
approver*, so a solo run cannot autonomously reach CLOSED on a mutation unit. That is a
completion-gate observation — it does **not** establish the approval step as the fleet's *throughput*
bottleneck (this single non-parallel slice measured no throughput; see the row below). Issue #51.

## WIP-curve protocol row (qualitative first observation — NOT a protocol-compliant data point)

Per `attention-budget.md` §"The WIP-curve protocol", one row for this run's single dispatch wave:

| Metric | Value (this run) |
|--------|------------------|
| WIP setting | `builders=1 reviewers=1` (single-slice run) |
| Builder throughput | not measured to protocol — the protocol counts units reaching verified-CLOSED per hour; this run reached verified-BUILT only, one slice, ~15 min wall-clock (≈ 8 min build + 7 min review) |
| Verification latency | machine verify (`verify.py` + tests + `--check`) < 6 s; acceptance review ≈ 7 min; `worker_done` → verified ≈ 7 min (n=1) |
| Rework rate | 0/1 — the slice passed acceptance review and every machine invariant on first dispatch (no evidence-manifest §2 bounce) |
| Freshness violations | 0 (`reviewed_sha == head_sha`) |

This is **not a protocol-compliant data point** and does not count toward the ≥3-run cap-revision
threshold — not for running at `builders=1` (a legitimate low-WIP setting), but because it reached
verified-BUILT, not the protocol's verified-CLOSED-per-hour throughput unit (no CLOSED-throughput
figure to plot). The caps in `attention-budget.md` stay **ASSERTED**; a curve still needs ≥3 runs at
differing WIP settings (a `builders=1` run counts) measuring verified-CLOSED-per-hour throughput.

## Deviations and lessons (recorded, not hidden)

- **A commit cannot embed its own hash.** `head_sha` in the manifest names the code+test commit
  `932449d`; the manifest itself rides as a following commit `748b328` (the pushed slice tip). Both
  land together at the BASE merge, so `head_sha` is a real, reachable ancestor and the ancestry
  check holds. A cleaner future convention: emit the manifest to an out-of-tree run directory so the
  slice tip *is* `head_sha`.
- **The GitHub-review gate is unreachable in a solo self-run** (above). Bounded here; in a real team
  ship a human/second-vendor approval satisfies it. Recorded as evidence that a solo run cannot
  autonomously clear the independent-approval gate — a completion-gate limit, not a measured
  throughput bottleneck.
- **reviewer_mode = instructed-isolation** is the weakest of the three independence modes; a
  cross-vendor reviewer (as the 2026-07-13 clean-sweep run used) is stronger and preferred when
  available.

## Run-close integrity inventory (sha256)

```
72219eaae5fdfd0b3a4f98af83f6bf284bb568429909ae9247e2fd351cffd088  docs/runs/2026-08-28-ship-it-selfrun/frozen-spec.md
ef01469349304330f4e4937dcdb96a7b1836c762364353950280394fc8207bfd  docs/runs/2026-08-28-ship-it-selfrun/build-manifest.json
059e8d6a891705a30c73c359901f46c6c79464946cbe663e71f65dd3a9fd3ebe  docs/runs/2026-08-28-ship-it-selfrun/negctrl.txt
231d6a79e57f526a34c1a7202c9ec75f81f5466c34f77ba5ab8541ca6b451d9e  runtime/scripts/proof_status.py
6e63e02cbaf3c460e2fbce543598b1e7c32ac2a7a5b7a75504dc18821f7f1ab5  tests/test_proof_status.py
```

## Gates

- FREEZE (human gate #1): n/a — frozen-spec entry, no intent grill.
- BASE → `main` promotion (human gate #2): **open, human-owned** — this run stops at the promotion
  PR. Merging it reaches `RELEASED`; `DEPLOYED_AND_VERIFIED` is bounded (no deploy surface).
