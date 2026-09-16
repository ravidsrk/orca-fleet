# Run report — prove-it self-run, 2026-09-16

RUN: mission=prove-it tier=self-run inventory_at=4d451d88aaea6a34a082e2724f60f93c03a2212d manifest=docs/runs/2026-09-16-prove-it-selfrun/manifest.json verifier=GREEN waves=2

The header above is what `runtime/scripts/run_report.py` re-derives: mission and tier match the frontmatter claim; the inventory below re-hashes 40/40 at the header commit; the manifest exists at that commit inside this run's own directory and is pinned by the inventory; the manifest's ledger carries the recorded `verify.py` GREEN run against itself (exit 0, executed control) — the binding record is the wave-2 re-record (D7), whose `wtree` is a pushed commit's tree; and the WIP-curve rows record the two dispatch waves (wave 1 solo kept as history, wave 2 orchestrated). First catalog run to bind: the archive's `Binds?` column reads `yes` for the first time.

Minimal prove-it self-run against this catalog (roadmap issue #410): one critical-surface criterion (PF-2, the `verify.py` oracle-scope kind gate), a 4-test characterization net, a 4/4 mutation audit, a build-blind cross-vendor review, and a GREEN executed-control verification — re-executed as an orchestrated wave-2 (D7) after the coordinator's NO-GO on the solo wave-1 substrate. Prior art: the August PF-1 demonstration (`docs/reports/prove-it-selfrun/`) — recorded history that supports no tier; this run's PF-2 complements it.

| Field | Value |
|---|---|
| Mission | `prove-it` — SKILL unchanged by this run (branch point `8784aa9`) |
| Tier claimed | `self-run` (run against this catalog); catalog promotion rides the same PR |
| Target | this catalog: `runtime/scripts/verify.py` `check_oracle_scope` kind gate (lines 988–989) |
| Fixed point | BASE `roadmap/issue-410-prove-promo` @ `4d451d8` (wave-2 evidence close) · FORK_POINT `8784aa9` · frozen contract `contract.json`: denominator @ scope freeze `eacd4cf` (criterion text byte-identical across waves), coords re-authorized @ `3e7109e` for the wave-2 pair (digest `sha256:c69f2ba0…`) |
| Coordinator / workers | coordinator (Muse Spark) · wave 1 solo (history, D1) · wave 2: builder `claude` via Orca (`task_2f6b230aab94`) + blind reviewer `grok-4.6` via Orca (`task_065e9d165753`) · TASK pack: matt (`tdd` builder / `code-review` reviewer — one pack per worker, never co-mounted) |
| Orca | `orca status --json` → `runtime.reachable: true` (app 1.4.203); wave 1 reachable-but-unused (D1, superseded); wave 2 dispatched through Orca — Run `run_1e33949c0db0` (created 2026-09-16T06:52:03Z), unit worktree child of the coordinator checkout, both dispatches `turn_started`/live-observed, both `worker_done` validated against git |
| Human gates | scope + dark-eligible lighting authorized by maintainer issue #410 pre-run · wave-2 rerun dispatched per coordinator verdict exit (a) on PR #437 (no waiver taken) · promotion-PR human review pending (merge backstop; merge SHA → #410 per AC5) |

## Terminal state

**COVERED** — consummated at merge of the promotion PR carrying this report (pre-merge state: verified-CLOSED, PR open). The single critical-surface path has a mutation-audited test, merged via that PR; no surfaced bugs. Ledger (canonical row shape; wave-1 row kept as history, wave-2 row binding):

`RUN run_1e33949c0db0 · COORDINATOR term_64fe1678 (Muse Spark) · BASE roadmap/issue-410-prove-promo · FORK_POINT 8784aa9 · T0 2026-09-16T05:47:42Z (scope freeze; wave-2 dispatch 06:53:11Z) · SOURCE contract PF-2 · WIP builders=1 reviewers=1`

| task_id | unit | BUILD_DONE | PR_OPEN | BOT | REVIEWED | MERGED | WT_CLEAN | lighting | park | evidence |
|---|---|---|---|---|---|---|---|---|---|---|
| n/a (solo wave 1, history) | PF-2 kind gate | `d96e15e` | pending (promotion PR, see #410) | n/a (CI at PR) | blind GO `review.txt` | superseded by wave 2 | yes at the time | dark-eligible | — | `manifest.json` (wave-1 records) |
| `task_2f6b230aab94` (builder, Orca) | PF-2 kind gate | `a466719` (4-test net, pushed FF) | pending (same promotion PR) | Greptile reconciled (both threads answered in-thread) | blind GO `review-rerun.txt` @ `a466719` (`task_065e9d165753`, grok, round 1) | pending (merge consummates COVERED) | pending (unit worktree retires at merge, not at run end) | dark-eligible | — | `manifest.json` (wave-2 records bind) |

## Convergence proof

Mission `## Convergence proof`, clause by clause:

1. *A merged test that fails at its assertion under a behavior-changing, harness-preserving mutation.* `tests/test_verify.py::OracleScopeKindTest` (4 tests, landed `a466719` by the Orca builder, merged via the promotion PR): under pinned hand mutant m1 (kind-gate deletion, `negctrl-rerun.txt`, diff byte-identical to wave 1) the bogus-kind case fails at `assertEqual` with `AssertionError` (exit 1, `FAILED (failures=1, errors=1)` — the non-dict case ERRORs with `AttributeError`, recorded honestly as error-not-failure); the harness is intact (module imports, 2/4 pass, collection clean). Supporting mutants m2/m3/m4 kill the same command (failures=3/1/1).
2. *The audit recorded as `negative_control` + `binding_audit`; the verifier re-runs the pinned mutant on a sample — ≥10% rounded up.* Manifest `negative_control` (tool `hand`, pinned diff, RED result, bound command) + `binding_audit` (PF-2 1/1, 4/4 killed). `verify.py --execute-nc` re-applied the pinned mutant in a throwaway worktree at head: exit 1 on an assertion failure, exit 0 clean — sample 1/1 units = 100% ≥ 10%.
3. *Every surfaced bug: fixed-with-test, or parked with a reason, or handed to clean-sweep.* None surfaced (0 bugs). The wave-1 reviewer's gap note (non-dict scope unpinned, D3) is CLOSED by wave 2 — the 4th test pins it; the wave-2 reviewer's FYI (the non-dict RED is error-shaped, not failure-shaped) is a coverage note, not a bug — the kill is the bogus-case AssertionError and the nc-command stays class-wide.
4. *No assertion weakened to pass (diff-audit).* The wave-1 net was committed once (`eacd4cf..d96e15e`, +39 lines); the wave-2 delta adds one test method plus a docstring line (`f5df568..a466719` touches `tests/test_verify.py` only, +9/−1); no weakening edit exists in either wave.
5. *Coverage before/after pasted — the pass criterion is the mutation-audit set, not the percent.* Full-suite line coverage (`uvx coverage`, `scripts/` + `runtime/scripts/`): 73% → 73% (`verify.py:989` newly covered; 1439 → 1438 missed of 5308; wave-1 MAP, carried — same target, same base). Pass criterion: the 4/4 mutation audit above.
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
| WAVE-2 CHARACTERIZE (Orca builder `task_2f6b230aab94`) | dispatched via `worker-start` (matt `tdd` pack); re-derived net + added non-dict test; `evidence-run.py` GREEN; m1 re-derived byte-identical; full audit | 4/4 OK; m1 `FAILED (failures=1, errors=1)` KILLED; m2/m3/m4 KILLED; pushed `a466719` + `d19efca` FF | `tests-rerun.txt`, `negctrl-rerun.txt`, `audit-rerun-*.txt`, `audit-m1-rerun.diff`, `coverage-rerun.txt`, `builder-task-spec.txt` |
| WAVE-2 REVIEW (Orca reviewer `task_065e9d165753`) | fresh-terminal blind review (matt `code-review` method): blind expectation first, then 3 mission axes, own m1 replay | GO round 1 (1 FYI, appendix empty); pushed `9e8961e` | `review-rerun.txt`, `reviewer-task-spec.txt` |
| WAVE-2 RUNTIME-PROVE | coordinator: re-authorized coords @ `3e7109e`; `verify.py --execute-nc` replays the pinned mutant at head; full suite at evidence tree | exit 1 under control / exit 0 clean; 1385 tests OK; `verify: OK` | `verifier-rerun-green.txt` (+ RED `verifier-rerun.txt` retained), `tests-full-rerun.txt`, `validation-rerun.txt` |
| WAVE-2 LAND | evidence `4d451d8`; report + promotion PR | landed on branch; merge pending | commits + PR |

MAP note: baseline suite at branch point `8784aa9` is 1381 tests OK (285s); MAP coverage run (exit 0) over `scripts/` + `runtime/scripts/` totals 73% (5308 statements, 1439 missed), with `runtime/scripts/verify.py` at 89% (1240 statements, 133 missed) including line 989 — the kind-gate return, taken only when an illegal kind is refused. Call-graph read: that gate decides which shape rules apply to a waived review (characterization must change a test; documentation must change prose only), so an unknown kind slipping past it skips both — the load-bearing uncovered branch of the lane this run rides, hence PF-2. RE-MAP targeted run (`uvx coverage run --source=runtime/scripts -m unittest tests.test_verify.OracleScopeKindTest`): the net executes 148 `verify.py` statements including line 989, the one line it adds to the covered set. Wave-2 RE-MAP (re-executed by the Orca builder, `coverage-rerun.txt`): lines 988–989 both executed by the 4-test net.

## Verifier outcome (recorded exactly)

Wave-1 records below are history (kept, still re-hashable); the binding run is the wave-2 re-record at the end of this section.

Wave-1 run, recorded through the recorder (TEMPLATE invocation plus the dispatch's lane flags):

`python3 runtime/scripts/evidence-run.py --label verifier --manifest docs/runs/2026-09-16-prove-it-selfrun/manifest.json --artifact docs/runs/2026-09-16-prove-it-selfrun/verifier.txt -- python3 runtime/scripts/verify.py --manifest docs/runs/2026-09-16-prove-it-selfrun/manifest.json --contract-source docs/runs/2026-09-16-prove-it-selfrun/contract.json@7942be928fc96b66597616690fc3d01edf5c94a6 --contract-digest sha256:f17d6eb9b39caa1719b257fbe609a9b595e4d083ec75d5a106920791ec89b734 --unit-class mutation --lighting dark-eligible --execute-nc --nc-command 'python3 -m unittest tests.test_verify.OracleScopeKindTest'`

Bare verifier invocation (the transcript wave 1's outcome came from; the header's outcome now comes from the wave-2 run below):

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

Re-record (promotion-time fixup, D6 — wave 1's binding `commands[]` record at the time; the graded binding is now the wave-2 re-record below): the run's close-time verifier invocation above was re-executed for real through `evidence-run.py` from the clean tree at `862b487` (the pins commit), so the record's `wtree c1255e6a…` equals `862b487^{tree}` and resolves on fresh clones:

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

Wave-2 re-record (the binding run — new coords, Orca-built head `a466719`, fresh artifact so the recorder's truncate-at-start cannot race the redaction read of the retained RED transcript):

`python3 runtime/scripts/evidence-run.py --label "verifier rerun 2026-09-16 (wave 2, Orca-built unit)" --manifest docs/runs/2026-09-16-prove-it-selfrun/manifest.json --artifact docs/runs/2026-09-16-prove-it-selfrun/verifier-rerun-green.txt -- python3 runtime/scripts/verify.py --manifest docs/runs/2026-09-16-prove-it-selfrun/manifest.json --contract-source docs/runs/2026-09-16-prove-it-selfrun/contract.json@3e7109e14f6071ab493f158a9d8e91d7196621ae --contract-digest sha256:c69f2ba0fff38089974864bf4f4a05c299720ea4ab42bacddcb60603200d4303 --unit-class mutation --lighting dark-eligible --execute-nc --nc-command 'python3 -m unittest tests.test_verify.OracleScopeKindTest'`

Output (verbatim, exit 0; retained in `verifier-rerun-green.txt`; record `wtree 91d3c673…` equals `e781c3c^{tree}`, pushed):

```
NOTE: --base not given — ancestry check skipped (pre-merge/offline)
NOTE: commands ledger FRESH — 1 exit-0 record(s) bound to head_sha's tree 5746c56318ab. This is the worker's own runner, so the coordinator's clean-env re-run at head_sha still stands as the stronger authority (evidence-manifest.md §2)
NOTE: negative control EXECUTED — with the hand control applied at head_sha the bound command exited 1 on an assertion failure (RED, as required)
NOTE: the same command exits 0 at clean head_sha — the RED above is the control's doing, not a broken suite
NOTE: independent review waived — dark-eligible unit (gate-classification.md); the EXECUTED negative control + tests are the oracle, not a human review
verify: OK — all required checks passed
```

(The first wave-2 attempt went RED, exit 2 — the coordinator's scope pair spanned the wave-1 evidence commits, so the `characterization` lane refused it ("this unit changes production code") and the hand control read as a decoy. Retained verbatim in `verifier-rerun.txt` (pinned); fixed by re-basing the pair to the wave-2 work (`f5df568..a466719`, test-only) and pinning the rerun commands artifacts. See D7.)

## WIP-curve protocol row

Wave 1 (history): single-unit solo wave: builder in-session, reviewer headless; wall S→verify-GREEN 400s; latency A→verify-GREEN 72s. Wave 2 (binding): single-unit orchestrated wave: Orca builder + Orca blind reviewer, sequential; wall dispatch→verify-GREEN 1654s (06:53:11Z→07:20:45Z); legs builder done→accepted 67s, reviewer done→accepted 83s.

| Wave | WIP setting | Builder throughput | Verification latency | Rework rate | Freshness violations | Note |
|---|---|---|---|---|---|---|
| `wave=1` | `builders=1 reviewers=1` | `throughput=9/h` | `latency_median=72s latency_max=72s` | `rework=0/1` | `freshness=0` | solo single-unit wave (history) |
| `wave=2` | `builders=1 reviewers=1` | `throughput=2.2/h` | `latency_median=75s latency_max=83s` | `rework=0/1` | `freshness=0` | orchestrated single-unit wave (binding) |

(Wave 1: 1 unit verified-CLOSED in 400s of wave wall-clock ⇒ 9/h; worker_done≈landed(A)→verified 72s; 0 §2 bounces with verify GREEN on the first attempt; no reviewed_sha void. Wave 2: 1 unit verified-CLOSED in 1654s of dispatch→verify-GREEN wall-clock ⇒ 2.2/h; latency median/max over the two dispatch legs' done→accepted gaps (67s builder, 83s reviewer); 0 §2 bounces — the RED1 verifier attempt was a coordinator self-correction (scope pair) before close, never a unit bounce-back; no reviewed_sha void — `reviewed_sha == head_sha == a466719`. The caps stay ASSERTED until ≥3 runs at differing WIP settings.)

## Deviations and lessons (recorded, not hidden)

- D1 (SUPERSEDED by D7 — the text below is kept verbatim as history; it no longer describes the binding wave) Solo run, no Orca dispatch (builder in-session; review via headless `claude -p`, not an Orca worker): the unit is one 39-line test — dispatch ceremony disproportionate — and this environment offers no nested-agent channel (the native subagent spawn failed twice before any model contact). Orca was reachable (1.4.203) but unused — recorded, not faked. Independence for the review leg is stronger than the channel is weak: fresh blind context, cross-vendor, prompt and reply retained.
- D2 (wave 1; the run now records `waves=2` — the single-criterion scope still holds per wave, see D7) Single-criterion wave (minimal per #410): the field-proof plan's multi-criterion audit plus builder wave belongs to a full-mission run. `waves=1` was the honest count then, not a placeholder.
- D3 Reviewer's minor gap (non-dict scope / absent `kind` unpinned; hardening note on kill sharpness): documented follow-up for the next prove-it run. Rework now would invalidate the reviewed content; the review is GO and the gap is a coverage note, not a bug.
- D4 A `codex exec` review attempt failed before any model contact (usage limit through Sep 19); no review content came from it. The `claude -p` retry succeeded.
- D5 The first recorded validation run exited 1 (stale `assets/badges/tests.json`: 1381 vs 1384 after the 3 new tests) → `scripts/gen-badges.py` → exit 0. Both records retained in the ledger.
- D6 Promotion-time verifier re-record (coordinator Critical on PR #437): the run-time `verifier` record's `wtree 53d3760d…` lived only in the author's object store, so `run_report.py` failed on fresh clones ("binds to nothing"). Fix per sibling #436: pinned the three unpinned `commands[]` artifacts (`verifier.txt`, `validation.txt`, `tests-full.txt` — the `tests.txt` precedent) so the 5-record manifest re-verifies GREEN, then re-executed the run's close-time verifier invocation for real via `evidence-run.py` from the clean tree at `862b487`, appending `verifier re-record 2026-09-16 (run close-time invocation, rerun)` with `wtree = 862b487^{tree}` (exit 0, transcript byte-identical, retained in `verifier-rerecord.txt`). Original record and transcript retained alongside; no run-time transcript byte edited; the re-record is the binding record and the header pins the evidence commit carrying it.
- L1 (reflect): the oracle_scope characterization lane now has fully-executed field evidence (GREEN with an executed hand replay) — no prior catalog run had recorded this lane end to end.
- L2 (reflect): `reviewer_mode` has no honest value without a second context — a solo run must ARRANGE one (a blind headless-agent review works; retain the prompt to evidence the blindness) or record RED, never self-certify a mode.
- L3 (reflect): test-adding runs trip the badge-freshness gate — regenerate badges before run-close validation.
- D7 Orchestrated wave-2 rerun (coordinator verdict exit (a) on PR #437 — the wave-1 NO-GO for the skipped HARD Orca dependency; no waiver taken). Same frozen single-criterion set (PF-2 text byte-identical); only the substrate changed. Builder dispatched as Orca worker `task_2f6b230aab94` (claude, matt `tdd` pack) in a unit worktree child of the coordinator checkout; blind reviewer dispatched as Orca worker `task_065e9d165753` (grok-4.6, matt `code-review` method, fresh terminal, blind expectation before opening the candidate, own m1 replay). REUSED where honestly reusable: the frozen criterion + scope freeze, the wave-1 MAP/coverage read (same target/base), the m1 mutant DEFINITION (re-derived byte-identical — verified by hash, not trusted), the blind prompt+reply retention practice, and all D1–D6/L1–L3 text as history. RE-EXECUTED: characterization (4-test net incl. the D3/Greptile non-dict test), the full mutation audit with fresh transcripts, the blind review, and every binding evidence-run record at pushed trees. Mid-wave events, all retained: the builder's `ask` on untracked setup debris (answered: delete — `wtree.sh` fingerprints untracked files; `orca-coordinator-reply.txt`); codex still usage-limited, so grok served as the cross-vendor reviewer; the first wave-2 verifier attempt went RED (exit 2 — scope pair spanned wave-1 evidence commits, `verifier-rerun.txt`) and the binding GREEN re-record went to a fresh artifact (`verifier-rerun-green.txt`) because the recorder truncates its artifact at start; the 4th test tripped badge freshness again (1385, L3 repeats).
- L4 (reflect): a rerun's scope pair must span the RERUN's work, not the original freeze — a `characterization` oracle_scope over a range containing evidence `.json`/`.diff` files is refused ("changes production code") and the control reads as a decoy. The denominator freeze and the unit pair are different pins.
- L5 (reflect): `worker-start` with an alpha agent adapter can settle `ready/input_accepted` with `turnStart: unsupported` — the `worker-list` liveness projection (`live`/`agent_status`) stays the authority; never resend on silence.
- L6 (reflect): a kill that ERRORS (AttributeError) rather than FAILs is inherent to non-dict JSON scopes and is verifier-clean at class level (failures≥1 + AssertionError present) but stillborn-shaped per-test — the nc-command must stay class-wide, and the audit must say error-not-failure out loud.

## Run-close integrity inventory (sha256)

| Artifact | sha256 | producer |
|---|---|---|
| `docs/runs/2026-09-16-prove-it-selfrun/manifest.json` | `81ff6b765f249e6b8decbb2cb613164e8456671d4376b7ad33b64a5130f9df1e` | worker assembly + evidence-run.py 2026-09-16 + promotion re-record + wave-2 rerun |
| `docs/runs/2026-09-16-prove-it-selfrun/contract.json` | `c69f2ba0fff38089974864bf4f4a05c299720ea4ab42bacddcb60603200d4303` | coordinator (frozen scope + wave-2 re-authorized coords) 2026-09-16 |
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
| `docs/runs/2026-09-16-prove-it-selfrun/tests-rerun.txt` | `ce91d67dca5b2b19515fb6990ca225b786d69be74b18eee30e423131c82d0d3e` | evidence-run.py unittest (Orca builder) 2026-09-16 |
| `docs/runs/2026-09-16-prove-it-selfrun/negctrl-rerun.txt` | `118364738b113205c7fe27d21a6788b1f426f32563ddcf37a6f464de87e47f41` | unittest transcripts + git diff (Orca builder) 2026-09-16 |
| `docs/runs/2026-09-16-prove-it-selfrun/audit-m1-rerun.diff` | `358d4a4045a1d58c0db0cb2f3450e9e1cd6dcaad565acd1419b85c73a1066980` | git diff, re-derived byte-identical (Orca builder) 2026-09-16 |
| `docs/runs/2026-09-16-prove-it-selfrun/audit-rerun-clean.txt` | `7366ce53c393fa42c16131fc375c6d0a0840af99428b01a3d6d096ee49e146d2` | unittest (Orca builder) 2026-09-16 |
| `docs/runs/2026-09-16-prove-it-selfrun/audit-rerun-m1-red.txt` | `4d51489442a0da568f0cffbd8f57184fc59443cff1731711944c72ec407119c4` | unittest (Orca builder) 2026-09-16 |
| `docs/runs/2026-09-16-prove-it-selfrun/audit-rerun-reverted.txt` | `b0cb919dd9e7b3a3111fdcca0f4aeadb37d4aa2266bb816d65d7b2090f85c280` | unittest (Orca builder) 2026-09-16 |
| `docs/runs/2026-09-16-prove-it-selfrun/audit-rerun-m2-red.txt` | `c2ab4761db35f722f5966542648182c4797ad9de34ec819ee0c41d325e6e05f3` | unittest (Orca builder) 2026-09-16 |
| `docs/runs/2026-09-16-prove-it-selfrun/audit-rerun-m3-red.txt` | `588a2256fa03f62de828b5850235b95f5d760ec620062dae693e05191f13895f` | unittest (Orca builder) 2026-09-16 |
| `docs/runs/2026-09-16-prove-it-selfrun/audit-rerun-m4-red.txt` | `f8c39f37b2f552d4698aa065150f900189333efe0ac96dfcd2078eb91682d102` | unittest (Orca builder) 2026-09-16 |
| `docs/runs/2026-09-16-prove-it-selfrun/coverage-rerun.txt` | `f7e56ad1522a8a99902784aaedc6a407c16f41119a468b61fcf161d01cd687e6` | uvx coverage (Orca builder) 2026-09-16 |
| `docs/runs/2026-09-16-prove-it-selfrun/review-rerun.txt` | `de33a0b64c734086ce3e152f6ab39b55d9fccc521a4fe81455f2b47ab8229a15` | grok-4.6 via Orca (blind review) 2026-09-16 |
| `docs/runs/2026-09-16-prove-it-selfrun/builder-task-spec.txt` | `e60db9aabc30436ea776a813dd8b8d4245fecf64fa61197892f7a38e2313cd16` | coordinator TASK prompt 2026-09-16 |
| `docs/runs/2026-09-16-prove-it-selfrun/reviewer-task-spec.txt` | `3921ca3258acc706513bbcd6d527eda6d949ad73ca669e3bc7e787a8994c7388` | coordinator TASK prompt 2026-09-16 |
| `docs/runs/2026-09-16-prove-it-selfrun/orca-run.json` | `b1d609c67b9eb801de76bba8705acbef920a3c6ceb0d2b6532ae0198a7781046` | orca run-show receipt 2026-09-16 |
| `docs/runs/2026-09-16-prove-it-selfrun/orca-tasks.json` | `60180f018964e171b04d2d97df71c3d9223b5cae9734d0f03e71d1973a854bd8` | orca task-list receipt 2026-09-16 |
| `docs/runs/2026-09-16-prove-it-selfrun/orca-builder-start.json` | `81e219c8420a3cd8de1b336b1589304cf188154aa91663f772b1e5c550c7d607` | orca worker-start receipt 2026-09-16 |
| `docs/runs/2026-09-16-prove-it-selfrun/orca-reviewer-start.json` | `9c58a230fb135dec1ca074a6ad325111486c6fdbbaf5cbb7c79d851673f03545` | orca worker-start receipt 2026-09-16 |
| `docs/runs/2026-09-16-prove-it-selfrun/orca-mail.json` | `1282f04b34cd6ee339f42decccb9fed517487d88240b796fcff6b0ffe414931f` | orca check --all history 2026-09-16 |
| `docs/runs/2026-09-16-prove-it-selfrun/orca-coordinator-reply.txt` | `e9bd19e65c17e3987b90dcf364ff2aed9623467668e14a08580fec5fcac6a5d5` | coordinator-transcribed send receipt 2026-09-16 |
| `docs/runs/2026-09-16-prove-it-selfrun/REFLECTION.md` | `be63b7295af6ea67f829e761a116e30265b014d79492113ef3a086b83996f05e` | coordinator compound-learn 2026-09-16 |
| `docs/runs/2026-09-16-prove-it-selfrun/validation-rerun.txt` | `90e1cc04c2301795dbb6306b86320f4cb65d9994187cc9ed7a251176258760a6` | evidence-run.py validate.py 2026-09-16 |
| `docs/runs/2026-09-16-prove-it-selfrun/tests-full-rerun.txt` | `b21f2180bb02c47ad29ca28a76a534646285cc2b3eaed090409021f49f5408ab` | evidence-run.py unittest 2026-09-16 |
| `docs/runs/2026-09-16-prove-it-selfrun/verifier-rerun.txt` | `46e1de9b8d6146c663471332b6d24a6facd8ccf0cdb35e9c8f2f7edd7080d123` | evidence-run.py verify.py RED (retained) 2026-09-16 |
| `docs/runs/2026-09-16-prove-it-selfrun/verifier-rerun-green.txt` | `d2c2f9c2d48bdafb73cf3f463c464042e14344fe22a63609202c6996232c743c` | evidence-run.py verify.py GREEN (binding) 2026-09-16 |

## Gates

`python3 scripts/validate.py` (wave-1 record on near-final content, exit 0 after badge regen; full transcript retained in `validation.txt`; the wave-2 re-record at the `0277bc5` tree is byte-identical, retained in `validation-rerun.txt`):

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

`python3 -m unittest discover -s tests` (wave-1 record on near-final content, exit 0; full transcript retained in `tests-full.txt`):

```
........................................................
----------------------------------------------------------------------
Ran 1384 tests in 316.596s

OK
```

Wave-2 re-record at the `96acc0b` tree (exit 0; full 41-line transcript with fixture noise retained in `tests-full-rerun.txt`; summary lines 23–27):

```
........................................................
----------------------------------------------------------------------
Ran 1385 tests in 254.348s

OK
```

Final-state re-runs (report on top of wave-2 evidence; pasted, not recorded — the manifest froze at evidence close `4d451d8`):

- `python3 scripts/validate.py` → exit 0 (`All 21 missions valid; three-layer separation holds; evals valid.`), with the `self-run` flip and the wave-2 binding check inside it.
- `python3 -m unittest tests.test_verify.OracleScopeKindTest` → `Ran 4 tests … OK`, exit 0.
- `python3 runtime/scripts/proof_status.py --check` → exit 0 (rollup: doctrine-only 20 · self-run 1 · external-run 0).
- `python3 runtime/scripts/run_report.py` → `bound prove-it (self-run) — docs/runs/2026-09-16-prove-it-self-run.md`, exit 0.
- `python3 runtime/scripts/inventory.py check docs/runs/2026-09-16-prove-it-self-run.md --at 4d451d88aaea6a34a082e2724f60f93c03a2212d` → `inventory: 40 verified, 0 mismatched, 0 missing`, exit 0.
- `python3 -m unittest discover -s tests` → `Ran 1385 tests` + `OK`, exit 0 (re-run at the final head; timing varies).
- `ruff check .` → `All checks passed!`. (`ruff format --check` flags 62 repo files — pre-existing drift across untouched files; the wave-2 test addition follows the class's existing style and a format reflow of reviewed bytes is worse than the drift. Left as found.)
