# Run report — prove-it self-run, 2026-09-16

RUN: mission=prove-it tier=self-run inventory_at=f5c69f1783804d1f7a38589310499e6754b4abde manifest=docs/runs/2026-09-16-prove-it-selfrun/manifest.json verifier=GREEN waves=1

The header above is what `runtime/scripts/run_report.py` re-derives: mission and tier match the frontmatter claim; the inventory below re-hashes 16/16 at the header commit; the manifest exists at that commit inside this run's own directory and is pinned by the inventory; the manifest's ledger carries the recorded `verify.py` run against itself (exit 0) — the binding record is the promotion-time re-record (D6), whose `wtree` is a pushed commit's tree; and the WIP-curve row records the single dispatch wave. First catalog run to bind: the archive's `Binds?` column reads `yes` for the first time.

Minimal prove-it self-run against this catalog (roadmap issue #410): one critical-surface criterion (PF-2, the `verify.py` oracle-scope kind gate), one characterization test, a 4/4 mutation audit, a build-blind cross-vendor review, and a GREEN executed-control verification. Prior art: the August PF-1 demonstration (`docs/reports/prove-it-selfrun/`) — recorded history that supports no tier; this run's PF-2 complements it.

| Field | Value |
|---|---|
| Mission | `prove-it` — SKILL unchanged by this run (branch point `8784aa9`) |
| Tier claimed | `self-run` (run against this catalog); catalog promotion rides the same PR |
| Target | this catalog: `runtime/scripts/verify.py` `check_oracle_scope` kind gate (lines 988–989) |
| Fixed point | BASE `roadmap/issue-410-prove-promo` @ `5467fd5` (evidence close) · FORK_POINT `8784aa9` · frozen contract `contract.json`: denominator @ scope freeze `eacd4cf`, coords authorized @ `7942be9` (digest `sha256:f17d6eb9…`) |
| Coordinator / workers | solo coordinator (Muse Spark) · builder in-session · reviewer headless (`claude -p`, no build context) · TASK pack: none (solo run; see D1) |
| Orca | `orca status --json` → `runtime.reachable: true` (app 1.4.203) at 2026-09-16 ~05:40Z — reachable but unused (D1); no worker was dispatched through Orca |
| Human gates | scope + dark-eligible lighting authorized by maintainer issue #410 pre-run · promotion-PR human review pending (merge backstop; merge SHA → #410 per AC5) |

## Terminal state

**COVERED** — consummated at merge of the promotion PR carrying this report (pre-merge state: verified-CLOSED, PR open). The single critical-surface path has a mutation-audited test, merged via that PR; no surfaced bugs. Ledger (canonical row shape; solo run, one wave):

`RUN prove-it-2026-09-16 · COORDINATOR solo · BASE roadmap/issue-410-prove-promo · FORK_POINT 8784aa9 · T0 2026-09-16T05:47:42Z (scope freeze) · SOURCE contract PF-2 · WIP builders=1 reviewers=1`

| task_id | unit | BUILD_DONE | PR_OPEN | BOT | REVIEWED | MERGED | WT_CLEAN | lighting | park | evidence |
|---|---|---|---|---|---|---|---|---|---|---|
| n/a (solo) | PF-2 kind gate | `d96e15e` | pending (promotion PR, see #410) | n/a (CI at PR) | blind GO `review.txt` | pending (merge consummates COVERED) | yes at head (proof record wtree == head tree) | dark-eligible | — | `manifest.json` |

## Convergence proof

Mission `## Convergence proof`, clause by clause:

1. *A merged test that fails at its assertion under a behavior-changing, harness-preserving mutation.* `tests/test_verify.py::OracleScopeKindTest` (3 tests, landed `d96e15e`, merged via the promotion PR): under pinned hand mutant m1 (kind-gate deletion, `negctrl.txt`) the bogus-kind case fails at `assertEqual` with `AssertionError` (exit 1, `FAILED (failures=1)`); the harness is intact (module imports, 2/3 pass, collection clean). Supporting mutants m2/m3/m4 kill the same command (failures=3/1/1).
2. *The audit recorded as `negative_control` + `binding_audit`; the verifier re-runs the pinned mutant on a sample — ≥10% rounded up.* Manifest `negative_control` (tool `hand`, pinned diff, RED result, bound command) + `binding_audit` (PF-2 1/1, 4/4 killed). `verify.py --execute-nc` re-applied the pinned mutant in a throwaway worktree at head: exit 1 on an assertion failure, exit 0 clean — sample 1/1 units = 100% ≥ 10%.
3. *Every surfaced bug: fixed-with-test, or parked with a reason, or handed to clean-sweep.* None surfaced (0 bugs). The reviewer's minor gap note (non-dict scope / absent kind unpinned) is a coverage note, not a bug — documented as follow-up (D3).
4. *No assertion weakened to pass (diff-audit).* The test was written once and committed once (`eacd4cf..d96e15e` touches `tests/test_verify.py` only, +39 lines); no weakening edit exists.
5. *Coverage before/after pasted — the pass criterion is the mutation-audit set, not the percent.* Full-suite line coverage (`uvx coverage`, `scripts/` + `runtime/scripts/`): 73% → 73% (`verify.py:989` newly covered; 1439 → 1438 missed of 5308). Pass criterion: the 4/4 mutation audit above.
6. *Manifest names COVERED or COVERED-WITH-PARKED.* Mission terminal COVERED named here and in the ledger above; the unit manifest verifies GREEN (`verify: OK — all required checks passed`).

## Pipeline evidence (per phase)

| Phase | Command / action | Result | Evidence |
|---|---|---|---|
| MAP critical surface | `uvx coverage run --source=scripts,runtime/scripts -m unittest discover -s tests` + call-graph read of the proof machinery | 73% total; `verify.py:989` uncovered and load-bearing → PF-2 | MAP note below |
| HUMAN scope confirm | coordinator froze 1-criterion scope; authorized by #410; PR review backstop | scope frozen pre-wave | `contract.json` @ `eacd4cf` |
| CHARACTERIZE wave 1 | wrote `OracleScopeKindTest` (3 tests asserting real gate behavior) | `Ran 3 tests … OK`, exit 0 | `tests.txt` (recorded) + `d96e15e` |
| Mutation audit | m1 pinned (apply → RED → revert → GREEN) + m2/m3/m4 | 4/4 KILLED, harness intact | `negctrl.txt` + `audit-*.txt` + `audit-m1.diff` |
| build-blind REVIEW | headless agent, blind prompt (criterion + test + mutant only) | GO (minor gap → follow-up) | `review.txt` |
| RUNTIME-PROVE | `verify.py --execute-nc` replays the pinned mutant in throwaway worktrees; full suite at head | exit 1 under control / exit 0 clean; 1384 tests OK | `verifier.txt`, `tests-full.txt` |
| LAND | test `d96e15e`; evidence `5467fd5`; promotion PR | landed on branch; merge pending | commits + PR |
| RE-MAP | net executes `verify.py:989` (targeted coverage) | 989 covered | MAP note below |
| REFLECT | deviations + lessons recorded | — | below |

MAP note: baseline suite at branch point `8784aa9` is 1381 tests OK (285s); MAP coverage run (exit 0) over `scripts/` + `runtime/scripts/` totals 73% (5308 statements, 1439 missed), with `runtime/scripts/verify.py` at 89% (1240 statements, 133 missed) including line 989 — the kind-gate return, taken only when an illegal kind is refused. Call-graph read: that gate decides which shape rules apply to a waived review (characterization must change a test; documentation must change prose only), so an unknown kind slipping past it skips both — the load-bearing uncovered branch of the lane this run rides, hence PF-2. RE-MAP targeted run (`uvx coverage run --source=runtime/scripts -m unittest tests.test_verify.OracleScopeKindTest`): the net executes 148 `verify.py` statements including line 989, the one line it adds to the covered set.

## Verifier outcome (recorded exactly)

Recorded through the recorder (TEMPLATE invocation plus the dispatch's lane flags):

`python3 runtime/scripts/evidence-run.py --label verifier --manifest docs/runs/2026-09-16-prove-it-selfrun/manifest.json --artifact docs/runs/2026-09-16-prove-it-selfrun/verifier.txt -- python3 runtime/scripts/verify.py --manifest docs/runs/2026-09-16-prove-it-selfrun/manifest.json --contract-source docs/runs/2026-09-16-prove-it-selfrun/contract.json@7942be928fc96b66597616690fc3d01edf5c94a6 --contract-digest sha256:f17d6eb9b39caa1719b257fbe609a9b595e4d083ec75d5a106920791ec89b734 --unit-class mutation --lighting dark-eligible --execute-nc --nc-command 'python3 -m unittest tests.test_verify.OracleScopeKindTest'`

Bare verifier invocation (the transcript the RUN header's outcome came from):

python3 runtime/scripts/verify.py --manifest docs/runs/2026-09-16-prove-it-selfrun/manifest.json --contract-source docs/runs/2026-09-16-prove-it-selfrun/contract.json@7942be928fc96b66597616690fc3d01edf5c94a6 --contract-digest sha256:f17d6eb9b39caa1719b257fbe609a9b595e4d083ec75d5a106920791ec89b734 --unit-class mutation --lighting dark-eligible --execute-nc --nc-command 'python3 -m unittest tests.test_verify.OracleScopeKindTest'

Output (verbatim, exit 0):

```
NOTE: --base not given — ancestry check skipped (pre-merge/offline)
NOTE: commands ledger FRESH — 1 exit-0 record(s) bound to head_sha's tree 6c4bcbddc646. This is the worker's own runner, so the coordinator's clean-env re-run at head_sha still stands as the stronger authority (evidence-manifest.md §2)
NOTE: negative control EXECUTED — with the hand control applied at head_sha the bound command exited 1 on an assertion failure (RED, as required)
NOTE: the same command exits 0 at clean head_sha — the RED above is the control's doing, not a broken suite
NOTE: independent review waived — dark-eligible unit (gate-classification.md); the EXECUTED negative control + tests are the oracle, not a human review
verify: OK — all required checks passed
```

(Retained: `verifier.txt`. `--contract-source`, `--contract-digest`, and `--nc-command` are the coordinator's out-of-band inputs; `--lighting dark-eligible` is the dispatch value from the frozen contract's dispatch note, authorized by #410 — the characterization-test-only example `gate-classification.md` names.)

Re-record (promotion-time fixup, D6 — the binding `commands[]` record): the run's close-time verifier invocation above was re-executed for real through `evidence-run.py` from the clean tree at `862b487` (the pins commit), so the record's `wtree c1255e6a…` equals `862b487^{tree}` and resolves on fresh clones:

`python3 runtime/scripts/evidence-run.py --label "verifier re-record 2026-09-16 (run close-time invocation, rerun)" --manifest docs/runs/2026-09-16-prove-it-selfrun/manifest.json --artifact docs/runs/2026-09-16-prove-it-selfrun/verifier-rerecord.txt -- python3 runtime/scripts/verify.py --manifest docs/runs/2026-09-16-prove-it-selfrun/manifest.json --contract-source docs/runs/2026-09-16-prove-it-selfrun/contract.json@7942be928fc96b66597616690fc3d01edf5c94a6 --contract-digest sha256:f17d6eb9b39caa1719b257fbe609a9b595e4d083ec75d5a106920791ec89b734 --unit-class mutation --lighting dark-eligible --execute-nc --nc-command 'python3 -m unittest tests.test_verify.OracleScopeKindTest'`

Output (verbatim, exit 0 — byte-identical to the run-time transcript above, `sha256 37e9cebd…` both files; retained in `verifier-rerecord.txt`, original record and transcript retained alongside):

```
NOTE: --base not given — ancestry check skipped (pre-merge/offline)
NOTE: commands ledger FRESH — 1 exit-0 record(s) bound to head_sha's tree 6c4bcbddc646. This is the worker's own runner, so the coordinator's clean-env re-run at head_sha still stands as the stronger authority (evidence-manifest.md §2)
NOTE: negative control EXECUTED — with the hand control applied at head_sha the bound command exited 1 on an assertion failure (RED, as required)
NOTE: the same command exits 0 at clean head_sha — the RED above is the control's doing, not a broken suite
NOTE: independent review waived — dark-eligible unit (gate-classification.md); the EXECUTED negative control + tests are the oracle, not a human review
verify: OK — all required checks passed
```

## WIP-curve protocol row

Single-unit solo wave: builder in-session, reviewer headless; wall S→verify-GREEN 400s; latency A→verify-GREEN 72s.

| Wave | WIP setting | Builder throughput | Verification latency | Rework rate | Freshness violations | Note |
|---|---|---|---|---|---|---|
| `wave=1` | `builders=1 reviewers=1` | `throughput=9/h` | `latency_median=72s latency_max=72s` | `rework=0/1` | `freshness=0` | solo single-unit wave |

(1 unit verified-CLOSED in 400s of wave wall-clock ⇒ 9/h; worker_done≈landed(A)→verified 72s; 0 §2 bounces with verify GREEN on the first attempt; no reviewed_sha void. First protocol-compliant WIP point in the archive — the caps stay ASSERTED until ≥3 runs at differing WIP settings.)

## Deviations and lessons (recorded, not hidden)

- D1 Solo run, no Orca dispatch (builder in-session; review via headless `claude -p`, not an Orca worker): the unit is one 39-line test — dispatch ceremony disproportionate — and this environment offers no nested-agent channel (the native subagent spawn failed twice before any model contact). Orca was reachable (1.4.203) but unused — recorded, not faked. Independence for the review leg is stronger than the channel is weak: fresh blind context, cross-vendor, prompt and reply retained.
- D2 Single-criterion wave (minimal per #410): the field-proof plan's multi-criterion audit plus builder wave belongs to a full-mission run. `waves=1` is the honest count, not a placeholder.
- D3 Reviewer's minor gap (non-dict scope / absent `kind` unpinned; hardening note on kill sharpness): documented follow-up for the next prove-it run. Rework now would invalidate the reviewed content; the review is GO and the gap is a coverage note, not a bug.
- D4 A `codex exec` review attempt failed before any model contact (usage limit through Sep 19); no review content came from it. The `claude -p` retry succeeded.
- D5 The first recorded validation run exited 1 (stale `assets/badges/tests.json`: 1381 vs 1384 after the 3 new tests) → `scripts/gen-badges.py` → exit 0. Both records retained in the ledger.
- D6 Promotion-time verifier re-record (coordinator Critical on PR #437): the run-time `verifier` record's `wtree 53d3760d…` lived only in the author's object store, so `run_report.py` failed on fresh clones ("binds to nothing"). Fix per sibling #436: pinned the three unpinned `commands[]` artifacts (`verifier.txt`, `validation.txt`, `tests-full.txt` — the `tests.txt` precedent) so the 5-record manifest re-verifies GREEN, then re-executed the run's close-time verifier invocation for real via `evidence-run.py` from the clean tree at `862b487`, appending `verifier re-record 2026-09-16 (run close-time invocation, rerun)` with `wtree = 862b487^{tree}` (exit 0, transcript byte-identical, retained in `verifier-rerecord.txt`). Original record and transcript retained alongside; no run-time transcript byte edited; the re-record is the binding record and the header pins the evidence commit carrying it.
- L1 (reflect): the oracle_scope characterization lane now has fully-executed field evidence (GREEN with an executed hand replay) — no prior catalog run had recorded this lane end to end.
- L2 (reflect): `reviewer_mode` has no honest value without a second context — a solo run must ARRANGE one (a blind headless-agent review works; retain the prompt to evidence the blindness) or record RED, never self-certify a mode.
- L3 (reflect): test-adding runs trip the badge-freshness gate — regenerate badges before run-close validation.

## Run-close integrity inventory (sha256)

| Artifact | sha256 | producer |
|---|---|---|
| `docs/runs/2026-09-16-prove-it-selfrun/manifest.json` | `d47b3869c953fa2ce50d9ecbafd16716b192b5a4e1ffd0b854c851ec65678e0c` | worker assembly + evidence-run.py 2026-09-16 + promotion re-record |
| `docs/runs/2026-09-16-prove-it-selfrun/contract.json` | `f17d6eb9b39caa1719b257fbe609a9b595e4d083ec75d5a106920791ec89b734` | coordinator (frozen scope + authorized coords) 2026-09-16 |
| `docs/runs/2026-09-16-prove-it-selfrun/negctrl.txt` | `33448afa8bfb91f4aea9225c878cf6ecb14cb77c272f011a8c373ee8c944a232` | unittest transcripts + git diff 2026-09-16 |
| `docs/runs/2026-09-16-prove-it-selfrun/review.txt` | `c7c649fd8eda98d80908cda9b70a371570fb920b5c27ef6acd90591e92743fa4` | claude -p (Claude Code 2.1.272) 2026-09-16 |
| `docs/runs/2026-09-16-prove-it-selfrun/tests.txt` | `11b4d660dc96a9e817dba113485e2e25781c647f08fdb946404362b001fd6083` | evidence-run.py unittest 2026-09-16 |
| `docs/runs/2026-09-16-prove-it-selfrun/verifier.txt` | `37e9cebdd5756b5c4bb511f808664c87b122aeb7f7c3e149ee5701a858c65db5` | evidence-run.py verify.py 2026-09-16 |
| `docs/runs/2026-09-16-prove-it-selfrun/verifier-rerecord.txt` | `37e9cebdd5756b5c4bb511f808664c87b122aeb7f7c3e149ee5701a858c65db5` | evidence-run.py verify.py re-record 2026-09-16 (D6) |
| `docs/runs/2026-09-16-prove-it-selfrun/validation.txt` | `90e1cc04c2301795dbb6306b86320f4cb65d9994187cc9ed7a251176258760a6` | evidence-run.py validate.py 2026-09-16 |
| `docs/runs/2026-09-16-prove-it-selfrun/tests-full.txt` | `ab76dbeaea3198bbfe75d54e2c7e6614e6045c9ec9e60bf20e67699a52ed2570` | evidence-run.py unittest 2026-09-16 |
| `docs/runs/2026-09-16-prove-it-selfrun/audit-m1.diff` | `358d4a4045a1d58c0db0cb2f3450e9e1cd6dcaad565acd1419b85c73a1066980` | git diff 2026-09-16 |
| `docs/runs/2026-09-16-prove-it-selfrun/audit-clean.txt` | `9e3618c465353a9e4a6828d5e621fa61c3754bf90d19d768cd975a69fc4289e2` | unittest 2026-09-16 |
| `docs/runs/2026-09-16-prove-it-selfrun/audit-reverted.txt` | `800346069b7c77896a63bf9caf4716560e8342f5599a74f58ff8b74006e44266` | unittest 2026-09-16 |
| `docs/runs/2026-09-16-prove-it-selfrun/audit-m1-red.txt` | `8988fdd1a0600c22688a0dbc3e2d069b8d4c92e146ddf53cffe32364b9c41c40` | unittest 2026-09-16 |
| `docs/runs/2026-09-16-prove-it-selfrun/audit-m2-red.txt` | `ed5109ec4aabe62d8659e731afb81eeaba1e51b1b76c188362c3fe91552df33f` | unittest 2026-09-16 |
| `docs/runs/2026-09-16-prove-it-selfrun/audit-m3-red.txt` | `f524c54872873509f27b766cd52d03c3106f045421e059cb0676f78d4c2272b1` | unittest 2026-09-16 |
| `docs/runs/2026-09-16-prove-it-selfrun/audit-m4-red.txt` | `28363352a48a4236822902b79ec50a463753ddf789806986e2d198c8585c0a1f` | unittest 2026-09-16 |

## Gates

`python3 scripts/validate.py` (recorded on near-final content, exit 0 after badge regen; full transcript retained in `validation.txt`):

```
ok   absorb-it
ok   access-it
ok   attest-it
ok   clean-sweep
ok   deflake-it
ok   document-it
ok   field-test-it
ok   floor-it
ok   harden-it
ok   map-it
ok   migrate-it
ok   modernize-it
ok   oncall-it
ok   oss-contribute
ok   pin-it
ok   prove-it
ok   reshape-it
ok   review-it
ok   root-cause
ok   ship-it
ok   speed-it

All 21 missions valid; three-layer separation holds; evals valid.
```

`python3 -m unittest discover -s tests` (recorded on near-final content, exit 0; full transcript retained in `tests-full.txt`):

```
........................................................
----------------------------------------------------------------------
Ran 1384 tests in 316.596s

OK
```

Final-state re-runs (report + promotion edits on top; pasted, not recorded — the manifest froze at evidence close):

- `python3 scripts/validate.py` → exit 0 (`All 21 missions valid; three-layer separation holds; evals valid.`), with the `self-run` flip and the binding check inside it.
- `python3 -m unittest tests.test_verify.OracleScopeKindTest` → `Ran 3 tests … OK`, exit 0.
- `python3 runtime/scripts/proof_status.py --check` → exit 0 (rollup: doctrine-only 20 · self-run 1 · external-run 0).
- `python3 runtime/scripts/run_report.py` → `bound prove-it (self-run) — docs/runs/2026-09-16-prove-it-self-run.md`, exit 0.
- `python3 -m unittest discover -s tests` → `Ran 1384 tests in 295.145s` + `OK`, exit 0.
