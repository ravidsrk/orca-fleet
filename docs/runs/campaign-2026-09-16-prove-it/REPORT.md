# Run report — prove-it campaign self-test, 2026-09-16

RUN: mission=prove-it tier=self-run inventory_at=12028cf159142d9e7f5b722b0c335011afb52163 manifest=docs/runs/campaign-2026-09-16-prove-it/manifest.json verifier=GREEN waves=1

The header above is what this report's inventory re-derives: the manifest exists
inside this run's own directory at the header commit; the inventory below
re-hashes every listed artifact at that commit; the manifest's ledger carries
the recorded `verify.py` GREEN run with an executed control. Tier note: this
run claims NO catalog promotion — `prove-it` already stands at `self-run`
(`docs/runs/2026-09-16-prove-it-self-run.md`, still bound); this is a second,
confirmatory field run under the campaign layout, which `run_report.py` does
not read (D6).

Second prove-it run against this catalog: one critical-surface criterion (PF-3,
the `verify.py` oracle-scope characterization gate at line 1012), a 3-test
characterization net, a 3/3 mutation audit, a build-blind two-phase cross-vendor
review (GO round 1), and a GREEN executed-control verification — all solo with
an arranged headless second context (D1).

| Field | Value |
|---|---|
| Mission | `prove-it` — SKILL unchanged by this run (branch point `c46d4b3f`) |
| Tier claimed | `self-run` (run kind; no promotion — already self-run, D6) |
| Target | this catalog: `runtime/scripts/verify.py` `check_oracle_scope` characterization gate (line 1012) |
| Fixed point | BASE `campaign/prove-it-selftest` @ `fc84a46d` (evidence ckpt 1) · FORK_POINT `c46d4b3f3371e41408aed19e54476fa194c20b42` · frozen contract `contract.json` @ scope freeze `2026-09-16T13:17:19Z` (criterion text byte-identical in manifest; coords authorized post-mutant-inspection, digest `sha256:8d66ecd2…`) |
| Coordinator / workers | coordinator (Muse Spark, workflow-child session) · builder in-session · blind reviewer headless `claude -p` (claude-opus-5) · TASK pack: matt (`tdd` builder / `code-review` reviewer — one pack, never co-mounted) |
| Orca | `orca status --json` → `runtime.reachable: true` (app 1.4.203); reachable-but-unused — no dispatch: the run contract bars recursive agent control (D1) |
| Human gates | scope + dark-eligible lighting authorized by the delegating campaign task (spawned session); interactive human scope confirm NOT obtained — backstop: no push, no PRs, no merge in this run; any promotion rides a human-reviewed PR (D3) |

## Terminal state

**COVERED** — consummated at the promotion merge carrying this branch
(pre-merge state: verified-CLOSED, branch holds the commits, no PR per the task
brief). The single critical-surface path has a mutation-audited test committed
test-only as `18ee8633`; no surfaced bugs (0). Ledger (canonical row shape):

`RUN - (solo, D1) · COORDINATOR workflow-child 46f15471 (Muse Spark) · BASE campaign/prove-it-selftest · FORK_POINT c46d4b3f · T0 2026-09-16T13:17:19Z (scope freeze) · SOURCE contract PF-3 sha256:9c1ff325… (frozen) / sha256:8d66ecd2… (with authorized coords) · WIP builders=1 reviewers=1`

| task_id | unit | BUILD_DONE | PR_OPEN | BOT | REVIEWED | MERGED | WT_CLEAN | lighting | park | evidence |
|---|---|---|---|---|---|---|---|---|---|---|
| n/a (solo) | PF-3 characterization gate (verify.py:1012-1013) | t (`18ee8633`) | n/a (no-gh: task forbids PRs/push/merge — local commits only) | n/a (no PR) | t (blind GO round 1 @ `18ee8633`) | n/a (no merge per task; branch holds the commits) | n/a (solo worktree) | dark-eligible | — | `docs/runs/campaign-2026-09-16-prove-it/manifest.json` |

## Convergence proof

Mission `## Convergence proof`, clause by clause:

1. *A merged test that fails at its assertion under a behavior-changing,
   harness-preserving mutation.* `tests/test_verify.py::OracleScopeCharacterizationGateTest`
   (3 tests, landed test-only `18ee8633`): under pinned hand mutant m1
   (gate-condition deletion, `negctrl.txt`, raw `audit-m1.diff`) both refusal
   cases fail at `assertEqual` with `AssertionError` (exit 1,
   `FAILED (failures=2)`); the harness is intact (module imports, 1/3 passes,
   collection clean). Supporting mutants m2 (inversion, failures=3) and m3
   (misroute, failures=2) kill the same command. Pre-merge state: committed on
   the campaign branch, promotion merge owed (terminal caveat above).
2. *The audit recorded as `negative_control` + `binding_audit`; the verifier
   re-runs the pinned mutant on a sample — ≥10% rounded up.* Manifest
   `negative_control` (tool `hand`, pinned diff, RED result, bound command) +
   `binding_audit` (PF-3 1/1, 3/3 killed). `verify.py --execute-nc` re-applied
   the pinned mutant in a throwaway worktree at head: exit 1 on an assertion
   failure, exit 0 clean — sample 1/1 units = 100% ≥ 10%.
3. *Every surfaced bug: fixed-with-test, or parked with a reason, or handed to
   clean-sweep.* None surfaced (0 bugs). The full-suite RED1 (2 failures) was
   badge staleness from the 3 new tests (D4), fixed by deterministic regen —
   run hygiene, not a target bug. The reviewer's G1 (no kind-swap control) is a
   coverage note for the sibling documentation-gate wave, not a bug; T1 is
   answered by m2's kill of the admit case.
4. *No assertion weakened to pass (diff-audit).* The net was committed once
   (`c46d4b3f..18ee8633`, +54 lines, `tests/test_verify.py` only); no
   weakening edit exists — the first full-suite failure was met with a badge
   regen, never a test edit.
5. *Coverage before/after pasted — the pass criterion is the mutation-audit
   set, not the percent.* Full-suite line coverage (`uvx coverage`,
   `scripts/` + `runtime/scripts/`): 74% at MAP (6142 statements, 1625
   missed); targeted RE-MAP executes `verify.py:1012-1013` (both absent from
   the Missing column; 1011 and 1015 present). Pass criterion: the 3/3
   mutation audit above.
6. *Manifest names COVERED or COVERED-WITH-PARKED.* Mission terminal COVERED
   named here and in the ledger above; the unit manifest verifies GREEN
   (`verify: OK — all required checks passed`).

## Pipeline evidence (per phase)

| Phase | Command / action | Result | Evidence |
|---|---|---|---|
| MAP critical surface | `uvx coverage run --source=scripts,runtime/scripts -m unittest discover -s tests` + call-graph/test-file read of the proof machinery | 74% total; oracle-scope tail (997–1024) confirmed untested and load-bearing → PF-3 | `MAP.md`, `map-coverage-missing.txt`, `map-coverage.json`, `map-tests*.txt` |
| HUMAN scope confirm | coordinator froze 1-criterion scope under explicit host delegation; interactive human confirm pending with merge backstop | scope frozen pre-wave | `contract.json` (frozen part) |
| BOOTSTRAP integration BASE | `preflight.py --base campaign/prove-it-selftest --fork-point c46d4b3f…` | exit 0, OK | report §Gates |
| CHARACTERIZE | wrote `OracleScopeCharacterizationGateTest` (3 tests asserting real gate behavior) | `Ran 3 tests … OK`, exit 0 | `tests.txt` (recorded, binding) + `18ee8633` |
| Mutation audit | m1 pinned (apply → RED → revert → GREEN) + m2/m3 | 3/3 KILLED, harness intact | `negctrl.txt` + `audit-*.txt` + `audit-*.diff` |
| build-blind REVIEW | two-phase headless blind review (expectation → judgment), prompt+reply retained | GO round 1 (G1→follow-up, T1→answered) | `review.txt` |
| RUNTIME-PROVE | `verify.py --execute-nc` replays the pinned mutant in throwaway worktrees; clean-env re-run at head; full suite at tree | exit 1 under control / exit 0 clean; 3/3 OK clean-env; 1493 OK full | `verifier.txt`, `clean-env.txt`, `tests-full-green.txt` |
| LAND | test `18ee8633`; evidence ckpt `fc84a46d`; badges `d3bd2fea`; evidence close + report | landed on branch; merge pending (task forbids) | commits on `campaign/prove-it-selftest` |
| RE-MAP | net executes `verify.py:1012-1013` (targeted coverage) | 1012-1013 covered | `remap-coverage.txt`, `remap-tests.txt` |
| REFLECT | deviations + lessons recorded; proposal only, no AGENTS.md mutation | — | `REFLECTION.md`, below |

## Verifier outcome (recorded exactly)

Recorded through the recorder (TEMPLATE invocation plus the dispatch's lane flags):

`python3 runtime/scripts/evidence-run.py --label verifier --manifest docs/runs/campaign-2026-09-16-prove-it/manifest.json --artifact docs/runs/campaign-2026-09-16-prove-it/verifier.txt -- python3 runtime/scripts/verify.py --manifest docs/runs/campaign-2026-09-16-prove-it/manifest.json --contract-source docs/runs/campaign-2026-09-16-prove-it/contract.json@fc84a46d95ba8b9f68b60a17999749592ee620c9 --contract-digest sha256:8d66ecd290c727de4b89beeb54d1584fe7fe3a5f30a6b3df10e1f8a15b90c807 --unit-class mutation --lighting dark-eligible --execute-nc --nc-command 'python3 -m unittest tests.test_verify.OracleScopeCharacterizationGateTest'`

Output (verbatim, exit 0; retained in `verifier.txt`):

```
NOTE: --base not given — ancestry check skipped (pre-merge/offline)
NOTE: commands ledger FRESH — 1 exit-0 record(s) bound to head_sha's tree dd57b4dd3b4b. This is the worker's own runner, so the coordinator's clean-env re-run at head_sha still stands as the stronger authority (evidence-manifest.md §2)
NOTE: negative control EXECUTED — with the hand control applied at head_sha the bound command exited 1 on an assertion failure (RED, as required)
NOTE: the same command exits 0 at clean head_sha — the RED above is the control's doing, not a broken suite
NOTE: independent review waived — dark-eligible unit (gate-classification.md); the EXECUTED negative control + tests are the oracle, not a human review
verify: OK — all required checks passed
```

(`--contract-source`, `--contract-digest`, and `--nc-command` are the
coordinator's out-of-band inputs; `--lighting dark-eligible` is the dispatch
value from the frozen contract's dispatch note — the characterization-test-only
example `gate-classification.md` names. A blind cross-vendor review ALSO exists
(`review.txt`, GO round 1) as defense-in-depth; the waived leg is not the
oracle either way. A final bare re-run on the close-time manifest bytes is
also GREEN — see §Gates.)

## WIP-curve protocol row

Single-unit solo wave: builder in-session, reviewer headless two-phase;
wall scope-freeze→verify-GREEN 643s; latency test-commit→verify-GREEN 543s
(single leg, includes the blind review + manifest assembly).

| Wave | WIP setting | Builder throughput | Verification latency | Rework rate | Freshness violations | Note |
|---|---|---|---|---|---|---|
| `wave=1` | `builders=1 reviewers=1` | `throughput=5.6/h` | `latency_median=543s latency_max=543s` | `rework=0/1` | `freshness=0` | solo single-unit wave, arranged headless second context |

(1 unit verified-CLOSED in 643s of wave wall-clock ⇒ 5.6/h; 0 §2 bounces —
verify GREEN on the first attempt; no reviewed_sha void —
`reviewed_sha == head_sha == 18ee8633`. The RED1 full-suite run was badge
hygiene (D4), never a unit bounce-back. The caps stay ASSERTED.)

## Deviations and lessons (recorded, not hidden)

- D1 Solo run, no Orca dispatch (builder in-session; review via two-phase
  headless `claude -p`, not an Orca worker): the run contract bars recursive
  agent control, which rules out `worker-start` from this session. Orca was
  reachable (1.4.203) but unused — recorded, not faked. The review leg is
  stronger than the channel is weak: fresh blind context, cross-vendor,
  both prompts and both replies retained verbatim, blind expectation before
  judgment. The HARD Orca dependency is therefore the run's one unmet
  mission dependency — named here, not waived.
- D2 Single-criterion wave (minimal): the oracle-scope tail holds several
  untested sibling gates; each is one more single-criterion wave, named in
  MAP.md. `waves=1` is the honest count, not a placeholder.
- D3 Scope authorized by the delegating campaign task (spawned session,
  explicit "run the mission for real"); interactive human scope confirm NOT
  obtained. Backstop: the task itself forbids push/PR/merge, so nothing lands
  without a later human-reviewed promotion. Same shape as the prior run's
  #410 pre-authorization + promotion-PR backstop, stated plainly.
- D4 The first full-suite run exited 1 (2 failures, both badge freshness:
  1490 vs 1493 after the 3 new tests) → `scripts/gen-badges.py` + separate
  badge commit → rerun exit 0. Both records retained in the ledger
  (`tests-full.txt` RED1, `tests-full-green.txt`).
- D5 The GREEN full-suite re-record went to a fresh artifact
  (`tests-full-green.txt`) because the recorder truncates its artifact at
  start — the D7 lesson of the prior run, applied pre-emptively. No
  transcript byte was moved or edited after its run.
- D6 Campaign layout (`docs/runs/campaign-2026-09-16-prove-it/` + `REPORT.md`
  inside) per the delegating brief, not the TEMPLATE's
  `<date>-<mission>-<kind>.md` + sibling-dir shape — so `run_report.py` does
  not read this run and no catalog-promotion binding is claimed or possible
  from it. `prove-it` stays self-run on the prior run's binding (still GREEN).
- L1 (reflect): traced coverage over-claims gaps for subprocess-tested CLIs
  (`guard_text.py` reads 0% with 32 contract tests). MAP must intersect
  coverage with test-file inspection — the `×` in the mission's formula is
  load-bearing, not decorative. See REFLECTION.md.
- L2 (reflect): the `reviewer_mode` field has no honest solo value without an
  arranged second context (repo L2, re-confirmed) — but a two-phase headless
  review (expectation → judgment) satisfies both the letter (blind-fix-first)
  and the field, single-shot-cli limits notwithstanding.
- L3 (reflect): the binding record's clean tree can be staged with
  stash-record-pop (fingerprint-before-run makes it sound) — no second
  worktree needed. See REFLECTION.md.

## Run-close integrity inventory (sha256)

| Artifact | sha256 | producer |
|---|---|---|
| `docs/runs/campaign-2026-09-16-prove-it/manifest.json` | `feaf4d9d8a3ecfce6c093c299b06788ae5064e4f7dc51583c6d337b475857870` | worker assembly + evidence-run.py 2026-09-16 |
| `docs/runs/campaign-2026-09-16-prove-it/contract.json` | `8d66ecd290c727de4b89beeb54d1584fe7fe3a5f30a6b3df10e1f8a15b90c807` | coordinator (frozen scope + post-inspection coords) 2026-09-16 |
| `docs/runs/campaign-2026-09-16-prove-it/negctrl.txt` | `04a10bc5e606bce43556a0a60b14359298a23bd75dd7113e6207a2dfea30496e` | unittest transcripts + git diff 2026-09-16 |
| `docs/runs/campaign-2026-09-16-prove-it/review.txt` | `0542fb4feb6c86f5b7cc18f8581ad492684bda238be26742346335b7f1c112d4` | claude -p (Claude Code 2.1.273, claude-opus-5) 2026-09-16 |
| `docs/runs/campaign-2026-09-16-prove-it/tests.txt` | `cf9d1b470ff096c937e755f96c792ca3a6ddd57f699e7c25397e8a9a1026391e` | evidence-run.py unittest 2026-09-16 |
| `docs/runs/campaign-2026-09-16-prove-it/verifier.txt` | `c1e4e82d8b98117eade5963a5cc3d962953ab5b0eba7f4f566f51f5331e63edb` | evidence-run.py verify.py 2026-09-16 |
| `docs/runs/campaign-2026-09-16-prove-it/validation.txt` | `90e1cc04c2301795dbb6306b86320f4cb65d9994187cc9ed7a251176258760a6` | evidence-run.py validate.py 2026-09-16 |
| `docs/runs/campaign-2026-09-16-prove-it/tests-full.txt` | `8d297fcf5662cac6022c4fcb2753ddee368cd701641e8bca2b7b242da2fd86ad` | evidence-run.py unittest RED1 (badge hygiene) 2026-09-16 |
| `docs/runs/campaign-2026-09-16-prove-it/tests-full-green.txt` | `08e50776d1c25917f35144b4289105b12443f5f612a1fc164d86e669a458068e` | evidence-run.py unittest rerun 2026-09-16 |
| `docs/runs/campaign-2026-09-16-prove-it/clean-env.txt` | `f8129822e9221b5e613e851e17d3e574b336cf1c80139cb5bd108974055581bd` | fresh-worktree unittest at head_sha 2026-09-16 |
| `docs/runs/campaign-2026-09-16-prove-it/audit-m1.diff` | `9684200b8e61f6a5cb16dfff40a0c145d8c990422e479eafbc6dcbcfc163dc74` | git diff 2026-09-16 |
| `docs/runs/campaign-2026-09-16-prove-it/audit-m2.diff` | `edd2237aba5c0121d1ed5e35532163839a6a64ec9d23773c84c3f63cd4f4faae` | git diff 2026-09-16 |
| `docs/runs/campaign-2026-09-16-prove-it/audit-m3.diff` | `455f9ca009391470a793f7a3579cd83571e47491105a251d0f508a1768002ba6` | git diff 2026-09-16 |
| `docs/runs/campaign-2026-09-16-prove-it/audit-clean.txt` | `e02e72962f0d6085e965760bc81b4a479137ab62f762fb95139733475a59bf76` | unittest 2026-09-16 |
| `docs/runs/campaign-2026-09-16-prove-it/audit-m1-red.txt` | `ce73b33363dd298aa5f2b425e9f72e215964a78a931c1518fdfca379a40651a0` | unittest 2026-09-16 |
| `docs/runs/campaign-2026-09-16-prove-it/audit-m2-red.txt` | `2e93deba323b7eee01cffe6dd98570083c67e89c46d806f45145e5ccf7c8ff80` | unittest 2026-09-16 |
| `docs/runs/campaign-2026-09-16-prove-it/audit-m3-red.txt` | `acdb781872f2ee2a0f69d6cb72c291bac74bb584be9fb024e95e76a7a01dcd6a` | unittest 2026-09-16 |
| `docs/runs/campaign-2026-09-16-prove-it/audit-reverted.txt` | `77209dd734c81cb898fd705f85179e1c906b92b03027dac3132e08cef9423360` | unittest 2026-09-16 |
| `docs/runs/campaign-2026-09-16-prove-it/MAP.md` | `2140de552d8df024fd435c8ecbed9304ec4b220e6af76750a491e9236133e529` | coordinator 2026-09-16 |
| `docs/runs/campaign-2026-09-16-prove-it/ledger.md` | `15dca963c0bf3c4fbc0b07993227c0a0bc6b71715026f4d7129fb9a6e7a0d6d3` | coordinator 2026-09-16 |
| `docs/runs/campaign-2026-09-16-prove-it/REFLECTION.md` | `b64c79df356025245410850ae5c3f61ef510712ca0d05ec91e2779013639f005` | coordinator compound-learn 2026-09-16 |
| `docs/runs/campaign-2026-09-16-prove-it/map-coverage.txt` | `447e0e541c8f1441a63ded59efdf88d54ec66308d8e06152a3308f6f09107e67` | uvx coverage 2026-09-16 |
| `docs/runs/campaign-2026-09-16-prove-it/map-coverage-missing.txt` | `c42da86dd07c20cc95d96ecc4d51095992bff55096e584ce3bf4e3daa4aaa013` | uvx coverage 2026-09-16 |
| `docs/runs/campaign-2026-09-16-prove-it/map-coverage.json` | `e03bcfd43f7f5877132668c64519c2d0be531a4ee96feb2e542adebe6fe5a6fb` | uvx coverage 2026-09-16 |
| `docs/runs/campaign-2026-09-16-prove-it/map-tests.txt` | `c7a43f3929c06e71b916842d94cc0248876e8162d954c16c4873a4ef1fee1ae8` | uvx coverage unittest 2026-09-16 |
| `docs/runs/campaign-2026-09-16-prove-it/map-tests2.txt` | `24d9bfd6089d9502a4b9655f1ea86ea3f16dea69e5d93f3777b1f6b3d8f3bb2b` | uvx coverage unittest 2026-09-16 |
| `docs/runs/campaign-2026-09-16-prove-it/remap-coverage.txt` | `484d21591d96cc751404e20391328b6f00d6a7f570ba3e448cf0bc05aa9ff46a` | uvx coverage 2026-09-16 |
| `docs/runs/campaign-2026-09-16-prove-it/remap-tests.txt` | `585477c6f3578873d8ada8cd9a628ae2a8419c82c3d2c6f02bcf195f87dd336b` | uvx coverage unittest 2026-09-16 |

## Gates

`python3 scripts/validate.py` (recorded, exit 0 after badge regen; full
transcript retained in `validation.txt`):

```
All 21 missions valid; three-layer separation holds; evals valid.
```

`python3 -m unittest discover -s tests` (recorded rerun at the evidence tree,
exit 0; full transcript retained in `tests-full-green.txt`):

```
Ran 1493 tests in 269.421s

OK
```

(The first recorded full run exited 1 on badge freshness — D4 — retained in
`tests-full.txt`; the rerun above is the binding GREEN.)

Final-state re-runs (report on top of evidence close; pasted, not recorded —
the manifest froze at evidence close):

- `python3 scripts/validate.py` → exit 0 (`All 21 missions valid; three-layer separation holds; evals valid.`)
- `python3 -m unittest tests.test_verify.OracleScopeCharacterizationGateTest` → `Ran 3 tests … OK`, exit 0
- `python3 runtime/scripts/verify.py` (close-time invocation, same flags as §Verifier outcome) → `verify: OK — all required checks passed`, exit 0
- `python3 runtime/scripts/proof_status.py --check` → exit 0 (rollup: self-run 2 · external-run 0 · total 21)
- `python3 runtime/scripts/run_report.py` → exit 0 (prior two bindings intact; this campaign layout unread by design, D6)
- `python3 runtime/scripts/inventory.py check <report> --at 12028cf159142d9e7f5b722b0c335011afb52163` → `inventory: 28 verified, 0 mismatched, 0 missing`, exit 0
- `ruff check .` → `All checks passed!` (whole repo, including the touched test file)
- `gitleaks detect` over the evidence dir and over `c46d4b3f..HEAD` → `no leaks found`
