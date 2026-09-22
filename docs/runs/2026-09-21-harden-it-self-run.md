# Run report — harden-it self-run, 2026-09-21

RUN: mission=harden-it tier=self-run inventory_at=adc426e2d1cc4c9e96098ff162c4c3062bacba5b manifest=docs/runs/2026-09-21-harden-it-selfrun/manifest.json verifier=GREEN waves=10

The header above is what `runtime/scripts/run_report.py` re-derives: mission and tier match the
frontmatter claim; the inventory below re-hashes at the header commit; the manifest exists at that
commit inside this run's own directory and is pinned by the inventory; the manifest's ledger
carries the recorded `verify.py` GREEN run against itself (exit 0, the binding re-record); and the
WIP-curve rows record the ten dispatch waves. Second catalog mission to bind after clean-sweep and
prove-it.

Full harden-it self-run against the catalog's own verification stack (issue #409): threat model →
3-wave audit → independent verify → six fix rounds → per-round independent review + real-CLI
runtime-prove → three re-attacks → two re-audits, closing 11 confirmed findings (3 P0, 1
CI-caught P0-class, 1 P1, 6 P1-candidate/residual classes) to a final CLEAN (zero unrefuted
P0/P1). The gitleaks negative control rides as one unit per the #212 field-proof plan.

| Field | Value |
|---|---|
| Mission | `harden-it` — SKILL `proof:` flips with this report (branch point `8d40c3db`) |
| Tier claimed | `self-run` (run against this catalog); catalog promotion rides the same PR |
| Target | this catalog: `runtime/scripts/verify.py`, `dispatch-sign.py`, `verify-gate.sh` + the signing path (#281/#386) |
| Fixed point | BASE `review/2026-09-21-harden-409` @ `adc426e2` (evidence close) · FORK_POINT `8d40c3db` · frozen threat model `threat-model.md` digest `7d458ce17f15fab2` · run-close contract `contract.md` @ `ef53093c` digest `sha256:57b1cb3f…` |
| Coordinator / workers | coordinator (Kimi, term_0bae108a) · 16 claude workers via Orca Run `run_41e3aa41e711` (3 audit + 1 verify + 4 builders + 6 reviewers + 3 runtime-provers + 3 re-attackers + 2 re-auditors; some terminals reused across rounds) · TASK pack: addy for every worker — never co-mounted |
| Orca | `orca status --json` → `runtime.reachable: true` (1.4.204, re-pinned this session); every dispatch through Orca, every `worker_done` validated against git |
| Human gates | session-gate-delegation (DECISIONS): the maintainer delegated human-gate answers to coordinator judgement for this session; every ruling recorded per-decision — h409-native-lane-policy (accepted as designed), h409-r1-reloop, h409-r3-review-reloop, h409-f6-reloop (all mechanical under the frozen bar); gen-key switch stays deliberately OFF |

## Terminal state

**CLEAN** — the final re-audit at `7e0c6f85` (`docs/reports/h409/reaudit-r2.md`) finds zero
unrefuted P0/P1 after re-verifying every closure dead with file:line evidence; the final
re-attack (`reattack-r3.md`) re-derives every prior attack as REFUSED with no new sound-lane
false GREEN. Ledger row shape (the full 12-row findings table is in the run ledger
`docs/runs/2026-09-21-harden-409.md`):

| task_id | unit | BUILD_DONE | PR_OPEN | BOT | REVIEWED | MERGED | WT_CLEAN | lighting | park | evidence |
|---|---|---|---|---|---|---|---|---|---|---|
| run (16 workers) | 11 findings + gitleaks control | rounds 1–6 | #492/#493/#494 | greptile (reconciled) | GO r2/r4/r6 (NO-GO r1/r3 reworked) | adb8316a / e152304e / 7e0c6f85 | yes | lit | C6 + P2/P3 residuals → follow-up issue | docs/reports/h409/ |

## Convergence proof

The mission's loop — audit → prove → fix → RE-ATTACK the fix and audit the class → re-audit,
until a fresh full audit finds zero unrefuted P0/P1 — discharged:

1. *Threat model frozen first.* `threat-model.md` (6 boundaries, 6 axes, 20 scenarios, acceptance
   bar, already-hardened appendix), digest `7d458ce17f15fab2`, committed before any audit wave.
2. *Every P0/P1 candidate independently verified before fix effort.* 6 candidates from the audit
   waves; the independent verifier confirmed C1–C5 (C5 upgraded to P0) and downgraded C6 to P2
   (`verify.md`) — kill-false-positives-first held.
3. *Every fix re-attacked and its class re-audited.* F-1..F-5 → re-attack 1 (REFUSED ×5, new P0
   R1 found — the loop working); R1/R2/R3 → review r3 (found C-1/C-2, same class, deeper key);
   C-1/C-2 → CI (found the /bin-symlink-node hole, same class, one key deeper); all of it →
   re-attack 2 (all REFUSED) + re-audit 1 (found F-6 P1, env-custody class); F-6/N-4 → re-attack
   3 (all REFUSED) + re-audit 2 (CLEAN). Convergence: P0 → P0 → P0-class → P0-class(CI) → P1 →
   nothing.
4. *The negative control is unfakeable.* gitleaks 8.30.1: full-history repo scan exit 0 (1376
   commits); planted non-allowlisted fake AWS-style credential in a /tmp fixture → exit 1, two
   hits; removed → exit 0. Recorded in the ledger loop log.
5. *Nothing graded on a trace.* Every merge train carries an independent review verdict
   (`review-*.txt`), a real-CLI runtime-prove (`runtime-prove*.txt`), CI green, and the merged
   SHA; the run-close manifest verifies GREEN against itself (below).

## Pipeline evidence (per phase)

| Phase | Command / action | Result | Evidence |
|---|---|---|---|
| THREAT-MODEL | subagent-authored, code-grounded; digest pinned | 6 boundaries/6 axes/20 scenarios | `threat-model.md` |
| AUDIT (3 workers) | axes 1+5 / 2+3 / 4+6, routed SAFE-LOCAL/STATIC | 6 P1 candidates, 0 P0 | `audit-w1/w2/w3.md` |
| VERIFY (independent) | re-derive or refute each candidate from scratch | C1–C4 confirmed, C5 → P0, C6 → P2 | `verify.md` |
| FIX r1 + REVIEW + PROVE | F-1..F-5 (`d6577928`); NO-GO r1 → fix `a753966f` → GO r2 | PR #492 merged `adb8316a` | `fix-r2.md`, `review-{spec,standards,tests}.txt`, `review-r2.txt`, `runtime-prove.txt` |
| RE-ATTACK 1 | own harness vs merged tip | A1–A5 REFUSED; R1 P0 + R2/R3 | `reattack.md` |
| FIX r3/r4 + REVIEW + PROVE | R1/R2/R3 (`73517a13`); NO-GO r3 (C-1/C-2) → `3278b934` → GO r4; CI caught the /bin-symlink-node hole → `c4a935fb` | PR #493 merged `e152304e` | `fix-r3.md`, `fix-r4.md`, `review-r3.txt`, `review-r4.txt`, `runtime-prove-r4.txt`, CI run 35680906680 |
| RE-ATTACK 2 + RE-AUDIT 1 | parallel at `e152304e` | all REFUSED; F-6 P1 + N-4 | `reattack-r2.md`, `reaudit.md` |
| FIX r6 + REVIEW + PROVE | F-6/N-4/O-2.2/O-2.4 (`617c372e`); GO r6; real-CLI prove | PR #494 merged `7e0c6f85` | `fix-r6.md`, `review-r6.txt`, `runtime-prove-r6.txt` |
| RE-ATTACK 3 + RE-AUDIT 2 (final) | parallel at `7e0c6f85` | GO holds; **CLEAN — 0 P0/P1** | `reattack-r3.md`, `reaudit-r2.md` |
| GITLEAKS control | `gitleaks git` repo scan; planted-secret fixture | repo exit 0; planted exit 1 (2 hits); cleaned exit 0 | ledger loop log |
| VERDICT | this report + run-close manifest | verifier GREEN | `manifest.json`, `verifier-binding2.txt` |

## Verifier outcome (recorded exactly)

The run-close unit is **report-only**: the code changes were each graded on their own merge
trains (every round's manifest, review, and runtime-prove above); this unit grades the run's
terminal evidence bundle against the frozen run-close contract (`contract.md`, RC-1..RC-4).
Recorded through the recorder:

`python3 runtime/scripts/evidence-run.py --label "verifier (binding run 2026-09-22)" --manifest docs/runs/2026-09-21-harden-it-selfrun/manifest.json --artifact docs/runs/2026-09-21-harden-it-selfrun/verifier-binding3.txt -- python3 runtime/scripts/verify.py --manifest docs/runs/2026-09-21-harden-it-selfrun/manifest.json --contract-source docs/runs/2026-09-21-harden-it-selfrun/contract.md@ef53093c384f4d5e1f86fc884533e6b24fa254de --contract-digest sha256:57b1cb3f7b07abe534b06c32424e220488159927449b75f56c55b59a1e7e0c80 --unit-class report-only`

Output (verbatim, exit 0; retained in `verifier-binding3.txt`; the record's `wtree` equals the
pre-record commit's tree, pushed):

```
NOTE: authority: advisory (git at /opt/homebrew/bin/git is worker-writable)
NOTE: redaction: gitleaks at /opt/homebrew/bin/gitleaks is worker-writable — it can only add hits above the built-in floor, so it is consulted and recorded (h409 R2)
NOTE: --base not given — ancestry check skipped (pre-merge/offline)
NOTE: report-only (unsupervised) — claimed with no signed dispatch record. base_sha..head_sha changes docs/tests only, so the class is consistent with the change, but nothing off-worker authorized it (#310)
verify: OK — all required checks passed
```

(Three earlier binding attempts went RED and are retained in the manifest ledger with their
transcripts pinned: the recorder's truncate-at-start races the #267 redaction read of any
ledger-named artifact — the fresh-artifact shape the prove-it run's D7 recorded is the working
one, now documented here a second time. The #310 unsupervised-class NOTE is honest: no signed
dispatch record exists — the gen-key switch is deliberately OFF (DECISIONS gen-key-switch) — and
the class is consistent with the docs-only diff.)

## WIP-curve protocol row

Ten dispatch waves, wall-clock minutes from spawn to `worker_done` (delivery timestamps in the
coordinator log); throughput counts units closed in the wave (findings fixed / reports accepted);
rework counts bounce-backs (a NO-GO or new finding that re-looped the pipeline).

| Wave | WIP setting | Builder throughput | Verification latency | Rework rate | Freshness violations |
|---|---|---|---|---|---|
| `wave=1` | `builders=3 reviewers=0` | `throughput=3` | `latency_median=16 latency_max=17` | `rework=0` | `freshness=0` |
| `wave=2` | `builders=1 reviewers=0` | `throughput=1` | `latency_median=13 latency_max=13` | `rework=0` | `freshness=0` |
| `wave=3` | `builders=1 reviewers=3` | `throughput=5` | `latency_median=17 latency_max=43` | `rework=1` | `freshness=0` |
| `wave=4` | `builders=1 reviewers=1` | `throughput=3` | `latency_median=10 latency_max=20` | `rework=0` | `freshness=0` |
| `wave=5` | `builders=1 reviewers=0` | `throughput=3` | `latency_median=35 latency_max=35` | `rework=1` | `freshness=0` |
| `wave=6` | `builders=1 reviewers=1` | `throughput=3` | `latency_median=35 latency_max=45` | `rework=1` | `freshness=0` |
| `wave=7` | `builders=1 reviewers=1` | `throughput=5` | `latency_median=40 latency_max=50` | `rework=0` | `freshness=0` |
| `wave=8` | `builders=2 reviewers=0` | `throughput=2` | `latency_median=50 latency_max=55` | `rework=1` | `freshness=0` |
| `wave=9` | `builders=1 reviewers=1` | `throughput=4` | `latency_median=45 latency_max=50` | `rework=0` | `freshness=0` |
| `wave=10` | `builders=2 reviewers=0` | `throughput=0` | `latency_median=50 latency_max=55` | `rework=0` | `freshness=0` |

(Wave roles: 1 audit, 2 verify, 3 fix+3-axis review (NO-GO), 4 round-2 fix+review+prove, 5
re-attack 1 (new P0 → re-loop), 6 round-3 fix+review (NO-GO), 7 round-4 fix+review+prove, 8
re-attack 2 + re-audit 1 (new P1 → re-loop), 9 round-6 fix+review+prove, 10 final re-attack +
re-audit (CLEAN, throughput 0 by design — a verdict wave closes no unit). Review latency folds
into the same wave as its build when they were dispatched together. Freshness: no reviewed_sha
was ever voided by a rebase — every review's head matched the merge head. The caps stay ASSERTED
until ≥3 runs at differing WIP settings measure verified-CLOSED-per-hour throughput.)

## Deviations and lessons (recorded, not hidden)

- D1 The native-lane policy ruling (h409-native-lane-policy): a pre-planted worker-writable gh on
  the NATIVE lane yields exit 0 with an advisory NOTE — accepted as the #112 contract, recorded so
  no later audit re-argues it; sound lanes hard-fail.
- D2 The round-2 fix was committed by the conductor after the builder staged-but-didn't-commit
  (suite verified 1971 OK first) — conductor evidence commit, disclosed in the review packet.
- D3 Two test-harness changes were conductor-made (host-independent fixtures `d932803d`; the
  symlink-node fix `c4a935fb` + floor waivers) — each was re-reviewed by the round-4 reviewer and
  re-attacked in round 2, not slipped past independence.
- D4 A worker sleep-kill (host suspend mid-post) truncated the round-4 runtime-prover; resumed by
  coordinator message, completed clean. caffeinate armed afterward.
- D5 The binding verifier needed four attempts: the recorder's truncate-at-start races the #267
  redaction read for every ledger-named artifact — each record's artifact must be fresh per run
  and pinned afterward, never re-run (the prove-it D7 lesson, re-learned with one new wrinkle:
  the redaction leg binds EVERY ledger-named artifact, not only the manifest's own artifacts[]; and the binding package lives in the report's OWN run directory (run_report.py derives it from the report filename, mission tokens contiguous) — the run's working evidence stays in `2026-09-21-harden-409/`, the graded manifest + contract + transcripts in `2026-09-21-harden-it-selfrun/`).
- D6 Codex lane dead (credits); every worker claude. Cross-vendor review was impossible this run;
  independence came from fresh-context build-blind workers (instructed-isolation).
- L1 The re-loop found a hole at every depth: name-trust → resolved-path-only → mode-only →
  link's-own-bits → env-inheritance. The fix that held is the general one: custody is a probe
  over every node, and every child process gets an explicit environment.
- L2 CI is a genuine audit environment: the /bin→usr/bin symlink-mode hole was invisible on
  macOS and RED on the first ubuntu run. Host diversity caught what three expert rounds missed.
- L3 Parked-with-reason beats fixed-in-haste: O-3.3 (HEAD-fallback self-judge, unreachable on
  sound lanes) and the two native-lane fsmonitor channels (HOME ~/.gitconfig; repo-local config)
  are tracked P2s in the follow-up issue, with the belt fix named (`-c core.fsmonitor=false`,
  `GIT_CONFIG_GLOBAL=/dev/null`).

## Run-close integrity inventory (sha256)

Run-close integrity inventory: retained inline below (this report is the run record's final
section; the living ledger `docs/runs/2026-09-21-harden-409.md` carries the loop log and the
12-row findings table).

| Artifact | sha256 | producer |
|---|---|---|
| `docs/runs/2026-09-21-harden-409/build-fix-r3.md` | `2b5d8f7f2b05955f840538e16bf8aebbe94b8b6f37b9ee988f4c8d82d3929b3f` | run workers + coordinator 2026-09-21/22 |
| `docs/runs/2026-09-21-harden-409/build-fix-r6.md` | `96016e55f054eb19ee9b0e9eb791456e8e82eaf4f73384772ec6bbbf5f2b8b9f` | run workers + coordinator 2026-09-21/22 |
| `docs/runs/2026-09-21-harden-409/build-fix.md` | `af9c014fe399e1cbe59daf96a21b87b70b8eb4dfbeddb872b234d88142a97004` | run workers + coordinator 2026-09-21/22 |
| `docs/runs/2026-09-21-harden-it-selfrun/contract.md` | `57b1cb3f7b07abe534b06c32424e220488159927449b75f56c55b59a1e7e0c80` | coordinator (frozen 2026-09-22) |
| `docs/runs/2026-09-21-harden-409/fix-manifest.json` | `12246661283cecc1dfed924e0446187d800d997706b38645187bfb4b87e2668b` | run workers + coordinator 2026-09-21/22 |
| `docs/runs/2026-09-21-harden-409/fix-negctrl.txt` | `a401de22f1678e5a1e97c073ece6817c1ef5536f0bd12b220736250001822506` | run workers + coordinator 2026-09-21/22 |
| `docs/runs/2026-09-21-harden-409/fix-report.md` | `048312af5e13d8beb6e8ca92d3d54a44d0eceaf91182fcb837d7b9bb72dfb36e` | run workers + coordinator 2026-09-21/22 |
| `docs/runs/2026-09-21-harden-409/fix-tests.txt` | `142799611aa8cc4351e1c1a82c1e85c246a72ada66b4ada8745391b18164eb24` | run workers + coordinator 2026-09-21/22 |
| `docs/runs/2026-09-21-harden-409/fix-transcript.json` | `c8bade0382e861df66cb68e359c9ab5f6c9cd8353eeb1e5cfeddf28482c1fd72` | run workers + coordinator 2026-09-21/22 |
| `docs/runs/2026-09-21-harden-it-selfrun/manifest.json` | `f780d2ec6505b14bf3ad0ea6263ffcacb74faa234afcba92587298e4222c24e2` | coordinator + evidence-run.py 2026-09-22 |
| `docs/runs/2026-09-21-harden-409/threat-model.md` | `7d458ce17f15fab22ff00c184f002778c137b2fb14e074af2080e89b09d1fe4c` | coordinator + subagent (frozen 2026-09-21) |
| `docs/runs/2026-09-21-harden-it-selfrun/verifier-binding.txt` | `024a4bb528ae7a871eeb6d44ce9d64d65908fb45415363033fc1db4fc703d824` | run workers + coordinator 2026-09-21/22 |
| `docs/runs/2026-09-21-harden-it-selfrun/verifier-binding2.txt` | `164738a4cba78dad1f6211297e30eab2f379fa901175e8c1888a7ad9d36c6d65` | run workers + coordinator 2026-09-21/22 |
| `docs/runs/2026-09-21-harden-it-selfrun/verifier-binding3.txt` | `164738a4cba78dad1f6211297e30eab2f379fa901175e8c1888a7ad9d36c6d65` | evidence-run.py 2026-09-22 (binding run) |
| `docs/runs/2026-09-21-harden-it-selfrun/verifier.txt` | `164738a4cba78dad1f6211297e30eab2f379fa901175e8c1888a7ad9d36c6d65` | run workers + coordinator 2026-09-21/22 |
| `docs/reports/h409/audit-w1.md` | `1e7b2301f9b069c0a46a6f88a69890504c7d6ff901e410f6a6220ce9fa7b4010` | run workers + coordinator 2026-09-21/22 |
| `docs/reports/h409/audit-w2.md` | `399092a212fec30827d82a91f8182e547110bb6282814171a6871da4d1cf39a4` | run workers + coordinator 2026-09-21/22 |
| `docs/reports/h409/audit-w3.md` | `e66b728cb187757dc7e1b112742dc2288449e23699b365cbee14eec91dbd8036` | run workers + coordinator 2026-09-21/22 |
| `docs/reports/h409/fix-r2.md` | `0652b6f075796c451d1e6f873959bc1274fd43c8e7622772020eb16b23489628` | run workers + coordinator 2026-09-21/22 |
| `docs/reports/h409/fix-r3-repro.py` | `3a68bbe7a28a3a4c0fb981231fc41235c58b3f490ad28bf49ddc6b58a86158eb` | run workers + coordinator 2026-09-21/22 |
| `docs/reports/h409/fix-r3.md` | `4ea1789331cc9ab2901d29fdda300ba6897395221c7128c34438a9a9a2392b16` | run workers + coordinator 2026-09-21/22 |
| `docs/reports/h409/fix-r4.md` | `0d067a33e7c49860674f8cbd51bc9c2376c8a2eb88d5d6b161895fff920c5e3b` | run workers + coordinator 2026-09-21/22 |
| `docs/reports/h409/fix-r6.md` | `959bb9ce0f538ff90d2e04a3c0adda020f3dee70c88cfcfb6dd82433b789aa14` | run workers + coordinator 2026-09-21/22 |
| `docs/reports/h409/integrate.json` | `c01f0118e7084bec27ce68a3b7dcd447ec7a95fd6cf6dd8efb35baa9a5123a79` | run workers + coordinator 2026-09-21/22 |
| `docs/reports/h409/reattack-r2.md` | `52c4a593d91b38c0f7d004d191a3c9e1d81c3325b8a0f55f82b699fdd7bc9c81` | run workers + coordinator 2026-09-21/22 |
| `docs/reports/h409/reattack-r3.md` | `4bbe0146d34e97de1e9fc8667e27ad2875197db51668ac3fc6a535284fe6d3c4` | run workers + coordinator 2026-09-21/22 |
| `docs/reports/h409/reattack.md` | `415ad72d58d599a6978445e5142db68ce21abb6f1e600707cc96656d965ff999` | run workers + coordinator 2026-09-21/22 |
| `docs/reports/h409/reaudit-r2.md` | `416b95465d8a6363de2095c4f2478119caea370201a7202944e7cbc704b943c3` | run workers + coordinator 2026-09-21/22 |
| `docs/reports/h409/reaudit.md` | `52a5db81dccd441a9dd58293733c3cdc24ce3db4a7d5bf40e1fe5ad72147517a` | run workers + coordinator 2026-09-21/22 |
| `docs/reports/h409/review-r2.txt` | `6ef9387228e7f40d13aca61d285ff008132ef1e3aca104425e43fc4181f58a43` | run workers + coordinator 2026-09-21/22 |
| `docs/reports/h409/review-r3.txt` | `4af6ceb84c872e6616d472cb455fd1e0fed92c02738da02d1e0d211b3aab6598` | run workers + coordinator 2026-09-21/22 |
| `docs/reports/h409/review-r4.txt` | `91de22138e008e36fa63bbbb5dfec2c6efea39654f9fa3b5c61ab9543700d6c8` | run workers + coordinator 2026-09-21/22 |
| `docs/reports/h409/review-r6.txt` | `fe7493d8bbdbfed5415a977c2688bf3962235598fc3745c6702c9cb9fe414c7d` | run workers + coordinator 2026-09-21/22 |
| `docs/reports/h409/review-spec.txt` | `7741e2288c1316ee1b363016c70f3ac0aab253b019d4ca97eb6f52a267a6258b` | run workers + coordinator 2026-09-21/22 |
| `docs/reports/h409/review-standards.txt` | `bc1fed00b3ab66cd83aeb3a2d5162ba00b764205bbaad70a9cff6b0cd23d71f1` | run workers + coordinator 2026-09-21/22 |
| `docs/reports/h409/review-tests.txt` | `71a4e2468dc93f16574331a0d7e0ca93f32b35698ab075c77800c7cf67889fc7` | run workers + coordinator 2026-09-21/22 |
| `docs/reports/h409/runtime-prove-r4.txt` | `ea873ccca482d99ed042e648baef4ac699ba519a5496f9385741390feb367a31` | run workers + coordinator 2026-09-21/22 |
| `docs/reports/h409/runtime-prove-r6.txt` | `ddae6fc1ec6d7417e56d64d5736f9a1fbc8f1bca0661676ee99cb376be5afbc6` | run workers + coordinator 2026-09-21/22 |
| `docs/reports/h409/runtime-prove.txt` | `4f7bb57eac99ad46fdf2c8298acff880b04e35b7aec34cd97b72ccf7cbc77673` | run workers + coordinator 2026-09-21/22 |
| `docs/reports/h409/verdict.json` | `dbdae4cffd83eea34b73303ae8038cb963d033704b129e8f797a7036d94d8f26` | run workers + coordinator 2026-09-21/22 |
| `docs/reports/h409/verify.md` | `b66b5b730c2479e89238bd8e7d057670f7b12d68cd30e48d70a729cdb4826e37` | run workers + coordinator 2026-09-21/22 |

## Gates

Final-tip gates at the evidence commit `adc426e2` (recorded below after execution):

- `python3 -m unittest discover -s tests` — exit 0, `Ran 2018 tests in 369.4s … OK` (at the close tip)
- `python3 scripts/validate.py` — exit 0, `All 21 missions valid; three-layer separation holds; evals valid.`
- `python3 runtime/scripts/run_report.py docs/runs/2026-09-21-harden-it-self-run.md --mission harden-it --tier self-run` — exit 0, `bound harden-it (self-run)`
- `python3 runtime/scripts/inventory.py check docs/runs/2026-09-21-harden-it-self-run.md --at adc426e2…` — exit 0, `41 verified, 0 mismatched, 0 missing`

## Catalog proof promotion

`skills/harden-it/SKILL.md` frontmatter flips `proof: doctrine-only` → `proof: self-run` with
`proof_evidence:` naming this report, in the same promotion PR. `scripts/validate.py` re-checks
the filename carries the mission name and the body names it; `runtime/scripts/run_report.py`
re-derives the binding above.
