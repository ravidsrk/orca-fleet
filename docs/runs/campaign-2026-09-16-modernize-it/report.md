# Run report — modernize-it self-test campaign, 2026-09-16

RUN: mission=modernize-it tier=doctrine-only inventory_at=PENDING-EVIDENCE-COMMIT manifest=docs/runs/campaign-2026-09-16-modernize-it/manifest-u1.json verifier=GREEN waves=1

Solo-coordinator self-test of the `modernize-it` mission against orca-fleet
itself at origin/main tip `c46d4b3` (Merge PR #445). One outdated node found
(ruff 0.16.5 → 0.16.7), upgraded through the full pipeline with a SHA-bound
manifest, an executed negative control, and a GREEN `verify.py` verdict.
Terminal: **CURRENT**. No proof tier is claimed by this campaign report —
`metadata.proof` stays `doctrine-only`; promotion needs a maintainer PR. The
`RUN:` header above is provenance (it names the evidence commit once closed),
not a binding claim.

| Field | Value |
|---|---|
| Mission | `modernize-it` — SKILL unchanged by this run (BASE fork `c46d4b3`) |
| Tier claimed | `doctrine-only` (no promotion; campaign self-test, evidence retained) |
| Target | this catalog: `.github/ci-tools.lock` + GH Actions pins + gitleaks pin + python pin |
| Fixed point | BASE `campaign/modernize-it-selftest-BASE` · FORK_POINT `c46d4b3f3371` · frozen contract `contract.json` @ `f7d5b13` (digest `sha256:cf631070…`) |
| Coordinator / workers | solo coordinator (Muse Code, workflow-child session, no Orca terminal; `run-create` refused `no_active_sender_terminal`, zero dispatches) · TASK pack: addy (single router; patch bump, no deprecations to route) |
| Orca | `orca status --json` → `runtime.reachable: true` (app 1.4.203, matches pin); reachable-but-unused — no terminal handle, no dispatches |
| Human gates | none taken (no pins, no migrate-it handoff, no promotion). Merge-to-default stays the human gate — this run stops at the campaign branch. |

## Terminal state

**CURRENT** — every dep on a current supported version, zero reachable
unaddressed advisories. Ledger (`ledger.md`, canonical row shape):

`RUN - (solo; run-create refused no_active_sender_terminal) · COORDINATOR workflow-child session 46f45671 · BASE campaign/modernize-it-selftest-BASE · FORK_POINT c46d4b3f3371e41408aed19e54476fa194c20b42 · T0 2026-09-16T12:25:39Z · SOURCE inventory.md @ sha256:161e04fdf5d952f7 · WIP builders=1 reviewers=0`

| task_id | unit | BUILD_DONE | PR_OPEN | BOT | REVIEWED | MERGED | WT_CLEAN | lighting | park | evidence |
|---|---|---|---|---|---|---|---|---|---|---|
| solo-u1 (no Orca dispatch; solo coordinator) | ci-tools ruff 0.16.5→0.16.7 | t (d3ee3f5; test_pins 8 OK; probe GREEN) | n/a (no-gh: local-merge) | n/a (no PR → no bot) | t (dark-eligible waiver + executed NC; self-review GO advisory) | t (77aa73f; ancestry-verified; branch deleted) | n/a (no unit worktree; solo) | dark-eligible | — | manifest-u1.json (verify OK) |

## Convergence proof

Mission `## Convergence proof`, clause by clause:

1. *Every outdated dep upgraded+merged with CI green (green run referenced) OR
   pinned-and-parked with reason + human ref.* The inventory's sole outdated node
   (ruff) upgraded in U1 (`d3ee3f5`), merged (`77aa73f`, ancestry-verified), with
   the green run referenced: `u1-gates.txt` (14/14 steps exit 0, 1490 tests OK,
   ruff 0.16.7 installed) recorded in `manifest-u1.json` commands[] with
   `wtree == head tree`. Zero pins.
2. *Every merge kept CI green (merge commits' checks verified).* One merge
   (`77aa73f`). Green at head (`u1-gates.txt`, FAIL=0) + green clean-env re-run
   at head (`clean-rerun.txt`, 1490 OK in a detached worktree) + green at the
   merged BASE tip (`final-gates.txt`: 13/13 content steps exit 0, 1490 OK; its
   single red step is default-scope gitleaks reading a SIBLING campaign's branch
   — see `gitleaks-scope.txt`; HEAD-scoped re-run at the same tip: no leaks,
   exit 0).
3. *Every upgrade that forced a stateful DB migration has a migrate-it handoff.*
   None forced: `diff_scope.py --strict` on the unit range reports
   `MIGRATIONS=false`, zero unmatched; the repo has no database. No handoff.
4. *Advisory scan re-run clean (or parked with rationale).* Re-scan at the new
   pin 2026-09-16: OSV `vulns: 0` + GH Advisory API `{"count":0}` for ruff
   0.16.7; all other pins unchanged since the clean inventory scan (OSV 0 on all
   six pip pins + gitleaks; GH API 0 on pip + actions + go). Zero advisories;
   nothing parked.
5. *Final inventory pasted.* `inventory.md` §2 (10-row surface table, all
   CURRENT) + §6 (single-node graph, U1 closed). Manifest names CURRENT (here
   and in the ledger row above).

## Pipeline evidence (per phase)

| Phase | Command / action | Result | Evidence |
|---|---|---|---|
| INVENTORY | manifest sweep + PyPI/OSV/GH-API queries + CHANGELOG read at tag | 1 outdated (ruff patch), 0 advisories (2 routes) | `inventory.md`, `ledger.md` SOURCE `sha256:161e04fd…` |
| BOOTSTRAP BASE | `preflight.py --base …-BASE --fork-point c46d4b3…` | exit 0 | ledger header |
| BASELINE | validate.yml replicated locally (11 gates) | FAIL=0, 1490 OK | `baseline-gates.txt` @ `f7d5b13` |
| ORDER | compatibility graph (single node, no chain) | 1 unit: U1 | `inventory.md` §6, `contract.json` AC-1..AC-6 |
| UPGRADE | `uv pip compile` regen + test_pins + CONTRIBUTING | `d3ee3f5` (3 files, 21/21) | unit commit + `u1-gates.txt` FAIL=0 |
| FORCED-MIGRATION CHECK | `diff_scope.py --strict` + repo surface read | NEGATIVE, no handoff | `review-u1.txt` |
| REVIEW | solo self-review (blind expectation first, 3 axes) + security lens | GO round 2; 0 lens findings | `review-u1.txt`, DECISIONS `lens-tally:security 0` |
| RUNTIME-PROVE | fresh-venv hash-pinned install + assert, both directions | GREEN clean / RED AssertionError under revert | `nc-u1.txt`, `nc-probe-green.txt` |
| VERIFY | `verify.py … --lighting dark-eligible --execute-nc --nc-command …` | OK (after 3 admission REDs, retained) | `verifier-u1.txt` (RED history), `verifier-u1-final.txt` (OK) |
| LAND | no-gh conductor: FRESH? → `merge --no-ff` pinned SHA → ancestry VERIFY | `77aa73f` (2 parents, branch deleted) | ledger MERGED |
| RE-INVENTORY | advisory re-scan at 0.16.7 + surface re-check | all CURRENT, 0 advisories | §4 of convergence proof above |
| REFLECT | compound-learn proposal (human approval owed) | — | `REFLECTION.md` |

## Verifier outcome (recorded exactly)

Final invocation (through the recorder; its record is `commands[5]`, exit 0 —
`<R>` = `docs/runs/campaign-2026-09-16-modernize-it`):

`python3 runtime/scripts/evidence-run.py --label verifier --manifest <R>/manifest-u1.json -- python3 runtime/scripts/verify.py --manifest <R>/manifest-u1.json --contract-source <R>/contract.json@f7d5b1375c7898e440245912d0293d8ca9b6f7b6 --contract-digest sha256:cf6310703354fae1599e5af1b19374fced91973e4c7aab95f38ee8aad4e44f45 --unit-class mutation --lighting dark-eligible --base campaign/modernize-it-selftest-BASE --execute-nc --nc-command 'python3 <R>/nc-probe.py'`

Output (verbatim, exit 0 — pinned as `verifier-u1-final.txt`):

```
NOTE: origin/campaign/modernize-it-selftest-BASE not found — ancestry check skipped
NOTE: commands ledger FRESH — 2 exit-0 record(s) bound to head_sha's tree 2a1146fc6ab1. This is the worker's own runner, so the coordinator's clean-env re-run at head_sha still stands as the stronger authority (evidence-manifest.md §2)
NOTE: negative control EXECUTED — with the revert control applied at head_sha the bound command exited 1 on an assertion failure (RED, as required)
NOTE: the same command exits 0 at clean head_sha — the RED above is the control's doing, not a broken suite
NOTE: independent review waived — dark-eligible unit (gate-classification.md); the EXECUTED negative control + tests are the oracle, not a human review
verify: OK — all required checks passed
```

RED history (retained, not hidden): three admission failures preceded GREEN —
#352 (no fresh record of the proof command; repaired with a clean-tree
`nc-probe` record) and two #267 (verifier transcript unpinned; repaired by
pinning prior transcripts and redirecting the final transcript to an unnarrated
path). All three transcripts/commands stay in `verifier-u1.txt` (runs 1–3) and
`manifest-u1.json` commands[] (exits 2,2,2,0). No re-dispatch, no waiver taken
to turn red green — the lane (dark-eligible + executed NC) was frozen in
`contract.json` before the unit branch existed.

## WIP-curve protocol row (mutating self-runs)

One dispatch wave (`waves=1`), solo: no Orca dispatches exist, so latency is
measured build-complete (unit commit `d3ee3f5` 12:35:04Z) → verified-or-parked
(verify-OK record 12:45:42Z) = 638s, labeled as the solo analogue. Wave
wall-clock T0 12:25:39Z → 12:45:42Z = 1203s (0.334h); 1 unit closed.

| Wave | WIP setting | Builder throughput | Verification latency | Rework rate | Freshness violations |
|---|---|---|---|---|---|
| `wave=1` | `builders=1 reviewers=0` | `throughput=3.0/h` | `latency_median=638s latency_max=638s` | `rework=0/1` | `freshness=0` |

## Deviations and lessons (recorded, not hidden)

- Solo lane, no Orca dispatches: `run-create` refused (`no_active_sender_terminal`
  outside any Orca terminal), so `RUN:-` with the reason in the ledger; WIP
  `builders=1 reviewers=0`; review is a same-session self-review (advisory only)
  and the dark-eligible executed-control lane carries the unit — the
  acceptance-review SOLO RUN lane, frozen in the contract pre-branch.
- Task-constrained no-gh local-merge (no PRs/pushes/merges-to-default allowed):
  `PR_OPEN`/`BOT` n/a, conductor merged `--no-ff` with the pinned-SHA guard, and
  the run stops at the campaign branch (promotion PR owed, human).
- `final-gates.txt` FAIL=1 is environmental cross-talk, not a unit regression:
  default-scope gitleaks reads `--all` refs in the shared store and picked up a
  parallel sibling campaign's branch (6/6 findings there; 0 in this run's files
  or history). Binding verdicts: HEAD-scoped re-run at the same tip (no leaks,
  exit 0) + files-only scan of this run's dir (no leaks). Full analysis in
  `gitleaks-scope.txt`. Untouched sibling state; their waiver is theirs.
- Lockfile regen = generator rows + preserved header (`uv pip compile` emits no
  header; the header's literal `-o` recipe would drop it). Hashes never
  hand-edited; non-ruff rows byte-identical to a fresh resolve (AC-4).
- The runs-README field-proof row still claims "this catalog has no
  dependencies" — stale since #301 (2026-09-11). Scope decision + staleness
  evidence in `docs/DECISIONS.md` (`modernize-scope-2026-09-16`).

## Run-close integrity inventory (sha256)

| Artifact | sha256 | producer |
|---|---|---|
| `docs/runs/campaign-2026-09-16-modernize-it/ledger.md` | `0a598b5d68c1947f224c1b7ed6eb7c2e25954f9da93e8728b43e6c4bd5210836` | coordinator 2026-09-16 |
| `docs/runs/campaign-2026-09-16-modernize-it/inventory.md` | `161e04fdf5d952f79927e73f4566f57f49c30cdb2598456e0909f7ed8e594990` | coordinator primary-source reads 2026-09-16 |
| `docs/runs/campaign-2026-09-16-modernize-it/contract.json` | `cf6310703354fae1599e5af1b19374fced91973e4c7aab95f38ee8aad4e44f45` | coordinator frozen 2026-09-16T12:32:01Z |
| `docs/runs/campaign-2026-09-16-modernize-it/nc-probe.py` | `e893ac336d23f05dd882e78ef18783edbcc79068f9284ad0274cc17a7352159e` | coordinator 2026-09-16 |
| `docs/runs/campaign-2026-09-16-modernize-it/baseline-gates.txt` | `f89e4a9016e4476b51ffa8779f2ab4a050d14ef88a1f0318c6326b500e2d23c9` | modernize-gates.sh (validate.yml replication) 2026-09-16 |
| `docs/runs/campaign-2026-09-16-modernize-it/u1-gates.txt` | `d95c8fe45db2c01450d09ca7b893c8565e84e7e8ade18931be49b348208cd7fd` | evidence-run.py + modernize-gates.sh 2026-09-16 |
| `docs/runs/campaign-2026-09-16-modernize-it/final-gates.txt` | `7563c1c8edf83e7d4e40ac9ead97cc6257d57ad251fa7e8a8f4c49b9a282c30e` | modernize-gates.sh at BASE tip 2026-09-16 |
| `docs/runs/campaign-2026-09-16-modernize-it/clean-rerun.txt` | `9efe9c05d71455ff9f523e344244e655532db87efd806e23ae9f00dce95f1b0d` | unittest in detached worktree @ d3ee3f5 2026-09-16 |
| `docs/runs/campaign-2026-09-16-modernize-it/nc-u1.txt` | `4cb311be7b19243537f2b7fd238fb20c02b0dc310985b3a48d554682ad89d516` | observed probe transcripts 2026-09-16 |
| `docs/runs/campaign-2026-09-16-modernize-it/nc-probe-green.txt` | `fe71df5f0b19c07e8cf71c5302cada6c4321b8092b59fc601250e614e4df586c` | evidence-run.py tee 2026-09-16 |
| `docs/runs/campaign-2026-09-16-modernize-it/review-u1.txt` | `2518aff0e4b78ba82ea87f848e0e98e7e98a84de881298d6592377c2900c3bab` | coordinator self-review rounds 1–2 2026-09-16 |
| `docs/runs/campaign-2026-09-16-modernize-it/verifier-u1.txt` | `5e6de2e3e68ec393bacb49b1683f5e96cdd2b9c1c27d9380d68da7f9f51fe849` | evidence-run.py verify.py runs 1–3 (RED history) 2026-09-16 |
| `docs/runs/campaign-2026-09-16-modernize-it/verifier-u1-final.txt` | `b2d541facb1bce8953e2da6557cacca6828b8469066d83fc3abfe32a018d74c3` | verify.py run 4 (OK) 2026-09-16 |
| `docs/runs/campaign-2026-09-16-modernize-it/manifest-u1.json` | `14469a898cc566a9e8077c146e7ee28c11d94ae14644eba707df0cb699c8d09f` | coordinator assembly + evidence-run.py records 2026-09-16 |
| `docs/runs/campaign-2026-09-16-modernize-it/gitleaks-scope.txt` | `58ef6bab8917188e99d5f8f7e6aaedd755744bc4d031fd7a088604b623378b2a` | observed scope comparison 2026-09-16 |
| `docs/runs/campaign-2026-09-16-modernize-it/REFLECTION.md` | `bb5d663efc7522387120f4607aeab896431757ac415a60db3a8e68ad793e35c6` | compound-learn 2026-09-16 |

## Gates

Final-implementation-head validation (BASE tip `55d4561`, content steps):

- `sh /tmp/modernize-gates.sh final-gates` → 13/13 content steps exit 0
  (`final-gates.txt`: validate, 1490-test unittest OK, routing eval,
  proof_status, run_report, bundle, hashed venv install ruff 0.16.7,
  agentskills-validate-all, ruff check, vf-bench PASS); the single red step is
  the environmental default-scope gitleaks read, discharged HEAD-scoped
  (exit 0) in `gitleaks-scope.txt`.
- Clean-env suite at unit head: detached worktree @ `d3ee3f5`,
  `python3 -m unittest discover -s tests` → `Ran 1490 tests … OK`
  (`clean-rerun.txt`).
- `verify.py` GREEN with executed control (§ Verifier outcome above).

## Evidence binding

All run-owned evidence lives in `docs/runs/campaign-2026-09-16-modernize-it/`
on branch `campaign/modernize-it-selftest` (BASE merged in; no push, no PR, no
merge-to-default per task). `RUN: inventory_at` names the evidence commit
carrying the manifest + every artifact above with final bytes; re-check with
`python3 runtime/scripts/inventory.py check <this report> --at <inventory_at>`.
No catalog tier is claimed or advanced by this report.
