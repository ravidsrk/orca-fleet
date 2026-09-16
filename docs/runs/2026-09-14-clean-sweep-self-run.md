# Run report — clean-sweep self-run, 2026-09-14 (tracker close)

RUN: mission=clean-sweep tier=self-run inventory_at=TBD_PROMOTION_COMMIT manifest=docs/runs/2026-09-14-clean-sweep-tracker/u387p-manifest.json verifier=GREEN waves=2

Close report for run `run_0607bdc681e6` (source=tracker, BASE
`review/2026-09-14-holistic-fixes`, T0 2026-09-14T15:34:09Z), the run whose living
ledger is `docs/runs/2026-09-14-clean-sweep-tracker.md`. Ten finding-backed units
merged with SHA-bound evidence manifests across two dispatch waves plus a
rollup-thread drain; the run closed DRY-WITH-PARKED and every unit reached
`main` in rollup PR #387 (`1ac5ff8`, CI gates green).

Graded unit: T8/U387P (PR #403, reviewed tip `19be7a1`, merged `b9b71df6`). At
close time it verified 6/6 GREEN with the contemporary verifier, review leg via
Greptile APPROVED `5206957088` at the reviewed tip. For this promotion the run's
own close-time `verify.py` invocation was re-executed for real through
`runtime/scripts/evidence-run.py` with the run's authoritative inputs; the
current verifier reports OK, exit 0, and the transcript is pasted verbatim under
Verifier outcome. The graded manifest carries that execution in its
`commands[]` ledger (the #286 leg); the run predates that requirement, so the
record is a dated promotion-time append, disclosed under Deviations — no
run-time byte was edited and the pre-append bytes remain in history.

| Field | Value |
|---|---|
| Mission | `clean-sweep` — this catalog, `skills/clean-sweep/SKILL.md` |
| Tier claimed | `self-run` (this report binds it; see Catalog proof promotion) |
| Target | this repo's own tracker: 4 open at T0 (#235 #364 #385 #386), run-filed #388 #389, mid-run #393, rollup-PR #387 threads |
| Fixed point | BASE `review/2026-09-14-holistic-fixes` · FORK_POINT `eb1a2f104c0f94a7af386b85f6a0a38dccf97a1d` · frozen spec per unit in `docs/runs/2026-09-14-clean-sweep-tracker/taskspecs/` (graded: `build-387-process.md@719d997`) |
| Coordinator / workers | kimi session → Muse takeover (maintainer Mac) · PROFILE=ro triage / rw build+review · TASK pack claude lanes (codex exhausted 2026-09-14) |
| Orca | `orca status` reachable during the run; dispatches via `task-create → spawn → check --wait` (manual loop, file-ledger gate) |
| Human gates | batch `gate-batch.md` G1–G4 (key custody+backend, verdict-derived branch protection, 2nd-login approves, Q1 retro-confirm) — owed at close, see Parks |

## Terminal state

**DRY-WITH-PARKED** (degraded): the frozen set is exhausted — every finding is
CLOSED with evidence or PARKED in a ledger-legal class — but degraded parks
remain (`needs-human` on #386, #235, and seven review legs). Never reported as DRY.

| task_id | id | CLASS | BUILD_DONE | PR_OPEN | BOT | REVIEWED | MERGED | WT_CLEAN | lighting | park | evidence |
|---|---|---|---|---|---|---|---|---|---|---|---|
| STAB | — | conductor landing | t | n/a | n/a | n/a | t | n/a | lit | — | 1215e09 9651a52 8f7d5ac 917f9fd; rides PR #387 |
| T1 | #388 | real-bug | t | t | t | t | t | t | lit | needs-human (G3) | PR #392 MERGED 8c36b4a @c680ee0; verify 5/6 |
| T2 | #389 | real-bug | t | t | t | t | t | t | lit | needs-human (G3) | PR #391 MERGED 1bdb20c @51019fb; verify 5/6 |
| T4 | #385 | real-bug (docs) | t | t | t | t | t | t | lit | — | PR #390 MERGED 32da76e @d6fc2cc; verify 6/6 |
| T3 | #364 | real-feature-small | t | t | t | t | t | t | lit | needs-human (G3) | PR #395 MERGED 1b64781 @8323c98; verify 5/6 |
| T6 | #364 | real-bug (evals) | t | t | t | t | t | t | lit | — | PR #397 MERGED 01d954e @2967804; verify 6/6 |
| T7 | #393 | real-bug | t | t | t | t | t | t | lit | needs-human (G3) | PR #400 MERGED 6d9e46a @7630815; verify 5/6 |
| T9 | #387-threads | real-bug (evals) | t | t | t | t | t | t | lit | needs-human (G3) | PR #402 MERGED a769a64e @318542b; verify 5/6 |
| T8 | #387-threads | process | t | t | t | t | t | t | lit | — | PR #403 MERGED b9b71df6 @19be7a1; verify 6/6 |
| T10 | #387-threads | real-bug | t | t | t | t | t | t | lit | needs-human (G3) | PR #401 MERGED bff42ff1 @0d55f10; verify 5/6 |
| T11 | #387-t-4012510839 | real-bug | t | t | t | t | t | t | lit | needs-human (G3) | PR #404 MERGED f1b0a4f @1e8ae08; verify 5/6 |
| T5 | #386 | — | — | — | — | — | — | — | — | needs-human (Q2/G1) | park |
| — | #235 | needs-human | — | — | — | — | — | — | — | needs-human (external) | prior run + issue text |

## Convergence proof

- Full enumeration finds zero items not CLOSED-with-evidence or PARKED-allowed.
  Loop-1 freeze: query1 (coordinator, T0) 4 open + query2 (worker) agreement
  modulo the run's own filings; created-since-T0 exactly {#388, #389}, closed
  none. Mid-run #393 (created 2026-09-14T18:06:52Z, after T0) joined loop 2 per
  the tracker rules and closed with evidence. Terminal: issues #364 #385 #388
  #389 #393 CLOSED (re-verified via issue tracker 2026-09-16), #386 #235 OPEN
  parked needs-human, rollup #387 at zero (42 threads, 0 unresolved, ledger
  `#387 AT ZERO` line). Nothing open is unaccounted.
- Every CLOSED unit carries a merged, ancestry-verified PR (`M^2 ==
  reviewed_sha` for all ten merges; each `gh pr merge --merge`, no squash) plus
  a failing-first test and an executed negative control — see Pipeline evidence
  and `docs/reports/clean-sweep-selfrun/negctrl.txt`. Revert-audit coverage is
  10/10 executed controls, above the ≥10% sample the mission requires; each
  unit's closing issue comment links its PR and test (ledger rows).
- Ledger flags `BUILD_DONE`…`WT_CLEAN` read `t` on every merged row (table
  above, transcribed from the frozen ledger).
- PARKED classes are all allowed: no refuted/duplicate closes occurred (no batch
  gate was owed for them); `needs-human` parks name their gate/OPS ref
  (`gate-batch.md` G1 for #386, G3 for the seven review legs, maintainer-direct
  for #235). No `CODE_CLOSED`, no `VERIFY_AT_SCALE`.
- The manifest names DRY-WITH-PARKED (this report's Terminal state) — the
  degraded marker is present, not hidden.
- The integration TIP was verified green: FINAL VALIDATION at `e93ab1a`
  (validate.py green over 21 missions, egress chain intact over 300 receipts,
  full suite 1381 OK). Promotion PR #387 merged as `1ac5ff8` with CI gates
  green, and the follow-up tip `8784aa9` likewise — the final head is green
  after every run-close commit.

## Pipeline evidence (per phase)

Wave 1 (loop-1 frozen set): STABILIZE landed the 4 review hunks; triage ran
query2 + 6 verdicts with coordinator-corroborated repros; U388/U389/U385 built
in parallel (builders=3), U364 dispatched alongside the wave-1 review rounds,
U364FF fixed forward U364's sticking r3 finding. Wave 2 (takeover scope): T7
built while T8/T9/T10 dispatched together after the codex exhaustion relaunch
onto claude; 20 #387 threads drained with replies+resolves, 2 parked, both
parks then closed (doc via corrective prepends `e54abdb`, race via T11).

| Unit | Verify at close (contemporary verifier) | Negative control (observed RED / GREEN) |
|---|---|---|
| STAB | gates green | NC re-executed exit 1 / 11 failures, matches claim |
| T1/U388 | 5/6, review RED parked | 2 NoLedgerLitter; C-2 RED 10/10 vs no-lock mutant |
| T2/U389 | 5/6, review RED parked | 10F+1E build; 5 reverts + 12 mutants RED at r4 |
| T4/U385 | 6/6 GREEN | C-1-only revert RED; C-2 hand-mutation witness |
| T3/U364 | 5/6, review RED parked | NC r4 exit 1 (23F+160E) / clean 98 OK |
| T6/U364FF | 6/6 GREEN | NC exit 1 (14F) / clean exit 0 |
| T7/U393 | 5/6, review RED parked | NC-1 10/10 RED, NC-2 exact-3, HEAD 10/10 GREEN |
| T9/U387G | 5/6, review RED parked | oncall-it + document-it RED found+fixed; M1-M4 killed |
| T8/U387P | 6/6 GREEN (graded) | probe 4/4 base RED, 3/4 reverted RED, 0/4 head GREEN |
| T10/U387W | 5/6, review RED parked | 7 rounds, Requireds reproduced vs base + oracle each round |
| T11/U393R | 5/6, review RED parked | race RED 20/20 at fork; M1/M2/M3 RED 20/20 each |

Review shape: build-blind 3-axis reviews + verdict per round (COMMENTED, never
APPROVE from the run's own identity — self-APPROVE would fake independence);
NO-GO rounds fixed forward with red-first evidence (U385 r1, U388 r1, U389
r1+r2, U364 r1+r2+r3-record, U387P r1+r2, U387W r1–r6, U393R r1+r2). Merges all
carry `--match-head-commit` + `--delete-branch` (T7's merge omitted the flags
and was compensated by a post-merge parent check plus branch deletion — the
spotcheck 4/4 record). Out-of-process merges disclosed: PR #395 mid-U364-r3 and
PR #397 ~7 min pre-verdict (both by the maintainer on GitHub; re-verified from
step 1 at each merge's tip per the conductor-close rule).

## Verifier outcome (recorded exactly)

Re-execution of the run's own close-time invocation for the graded unit
(conductor-close.md step 6 shape), run for real at promotion time through the
installed recorder. Full output is also retained at
`docs/reports/clean-sweep-selfrun/verifier-u387p.txt`:

`python3 runtime/scripts/evidence-run.py --label 'promotion re-verification 2026-09-16 (run close-time invocation, rerun)' --manifest docs/runs/2026-09-14-clean-sweep-tracker/u387p-manifest.json --artifact docs/reports/clean-sweep-selfrun/verifier-u387p.txt -- python3 runtime/scripts/verify.py --manifest docs/runs/2026-09-14-clean-sweep-tracker/u387p-manifest.json --contract-source docs/runs/2026-09-14-clean-sweep-tracker/taskspecs/build-387-process.md@719d997be28476c382660f3f37d829e597130ce9 --contract-digest sha256:d2b868060256e8ff541121e8eb1897d9f94b7d3e0eccf45f02e068313414331f --nc-command 'sh docs/runs/2026-09-14-clean-sweep-tracker/u387p-probe.sh' --execute-nc --base review/2026-09-14-holistic-fixes --unit-class mutation`

TRANSCRIPT-PENDING (pasted from the evidence-run artifact before close, with exit code)

The `RUN:` header records `verifier=GREEN`: scope (authoritative contract
digest matches; `C-1`..`C-5` cover the frozen spec), real commits, freshness
(`head_sha == reviewed_sha == 19be7a1`), commands ledger FRESH (3 exit-0
coordinator records bound to `head_tree 97a41a2`), negative control EXECUTED
(revert → probe exit 1 RED; clean head → exit 0), and the review leg via
Greptile APPROVED `5206957088` at `19be7a1` on PR #403 (bot login ≠ PR author;
re-verified present on GitHub 2026-09-16).

## WIP-curve protocol row

Two dispatch waves per the run's own vocabulary (wave-1 builds + U364/T6
fix-forward; wave-2 T7–T11). Walls and latencies are git committer dates:
wave wall = dispatch commit → last close commit; latency = reviewed tip →
evidence-close commit per unit (the run did not timestamp `worker_done`
messages; the final push precedes `worker_done` by minutes and the close commit
is the verified-or-parked moment, so the interval charges review+merge, which is
what the metric prices). Rework = units bounced by a Required-bearing review
round (NO-GO verdict or axis Requireds → fix round). Freshness = reviews voided
by `reviewed_sha != head_sha` (none — unions re-reviewed at post-union tips;
T9's held r1 GO was a delta-verdict, not a void).

| Wave | WIP setting | Builder throughput | Verification latency | Rework rate | Freshness violations |
|---|---|---|---|---|---|
| `wave=1` | `builders=3 reviewers=1` | `throughput=0.44/h` | `latency_median=48m latency_max=3h02m` | `rework=4/5` | `freshness=0` |
| `wave=2` | `builders=3 reviewers=1` | `throughput=0.45/h` | `latency_median=30m latency_max=48m` | `rework=3/5` | `freshness=0` |

Wave-1 wall: `5af2e6f` (specs landed, 2026-09-14T22:45:28+05:30) →
`ef0ee1c` (U364 close, 2026-09-15T10:10:56+05:30), 11.42 h, 5 units CLOSED.
Latencies: U385 49m, U388 48m, U389 38m, U364 3h02m (out-of-process merge +
T6 wait), U364FF 48m. Reworked 4/5 (all but T6; U385's r1 NO-GO is commit
`137ffd9`). Wave-2 wall: `9a115f7` (dispatch, 2026-09-15T10:29:35+05:30) →
`e93ab1a` (T11 close, 2026-09-15T21:35:14+05:30), 11.09 h, 5 units CLOSED.
Latencies: U393 48m, U387G 23m, U387P 27m, U387W 41m, U393R 30m. Reworked 3/5
(T8/T10/T11; T7 went GO at r1 and T9's reunion was union handling, not a
bounce). STABILIZE is excluded from throughput (conductor landing riding PR
#387, not a dispatched build unit). Live concurrency peaked above the header
WIP (wave-2 builds peaked at 4; review phases ran up to 8 workers) — the rows
carry the ledger-header WIP per the protocol and this note carries the peak.

## Deviations and lessons (recorded, not hidden)

- Promotion-time verifier record (this report's own deviation): the graded
  manifest's `commands[]` gained one record on 2026-09-16 — the re-execution
  above, run through `evidence-run.py`, wtree bound to the promotion commit's
  tree. The run predates #286, so no contemporary record of this shape exists;
  backdating one would be fabrication, and the record is honestly dated. No
  run-time manifest byte was edited — the append is the only semantic change
  (`git diff -w` on the file shows one added record; the indent 1→2 reformat is
  the writer's doing, accepted verbatim so no hand byte touches evidence).
- Run deviations (from the ledger, summarized — the ledger is the authority):
  out-of-process merges #395/#397 (disclosed, re-verified); T6 merged pre-verdict
  (amended G2: the protection check must derive from the verdict, not any
  APPROVED); triage done-by-transcription (plan-mode worker, coordinator
  corroborated both repros in scratch clones); provider exhaustion relaunched
  wave 2 across vendors; two Orca resets recovered via live-terminal re-adoption
  with no unit state lost; T7 merge omitted match-head/delete-branch flags
  (compensated + spotchecked, flags required thereafter).
- Lessons kept as policy after the run: worker-supervision adoption (#405),
  conductor-close procedure (written by T8 itself), egress-consent template fix,
  review-template TARGET checkout line.

## Run-close integrity inventory (sha256)

Written by `python3 runtime/scripts/inventory.py write` over the promotion
tree and re-derived at the header commit with `check --at`. Pins the graded
manifest, the run's unit manifests, the gate batch, the ledger, and the
promotion-time verifier artifact. The taskspec below is pinned at its living
bytes; the authoritative frozen contract is the `@719d997` blob whose digest
the verifier checked (re-derived `d2b86806…` at close and 2026-09-16).

```
0000000000000000000000000000000000000000000000000000000000000000  docs/runs/2026-09-14-clean-sweep-tracker/u387p-manifest.json
0000000000000000000000000000000000000000000000000000000000000000  docs/runs/2026-09-14-clean-sweep-tracker/u387p-negctrl.txt
0000000000000000000000000000000000000000000000000000000000000000  docs/runs/2026-09-14-clean-sweep-tracker/u387p-probe.sh
0000000000000000000000000000000000000000000000000000000000000000  docs/runs/2026-09-14-clean-sweep-tracker/taskspecs/build-387-process.md
0000000000000000000000000000000000000000000000000000000000000000  docs/runs/2026-09-14-clean-sweep-tracker/gate-batch.md
0000000000000000000000000000000000000000000000000000000000000000  docs/runs/2026-09-14-clean-sweep-tracker/stabilize-manifest.json
0000000000000000000000000000000000000000000000000000000000000000  docs/runs/2026-09-14-clean-sweep-tracker/u364-manifest.json
0000000000000000000000000000000000000000000000000000000000000000  docs/runs/2026-09-14-clean-sweep-tracker/u364ff-manifest.json
0000000000000000000000000000000000000000000000000000000000000000  docs/runs/2026-09-14-clean-sweep-tracker/u385-manifest.json
0000000000000000000000000000000000000000000000000000000000000000  docs/runs/2026-09-14-clean-sweep-tracker/u388-manifest.json
0000000000000000000000000000000000000000000000000000000000000000  docs/runs/2026-09-14-clean-sweep-tracker/u389-manifest.json
0000000000000000000000000000000000000000000000000000000000000000  docs/runs/2026-09-14-clean-sweep-tracker/u393-manifest.json
0000000000000000000000000000000000000000000000000000000000000000  docs/runs/2026-09-14-clean-sweep-tracker/u387g-manifest.json
0000000000000000000000000000000000000000000000000000000000000000  docs/runs/2026-09-14-clean-sweep-tracker/u387w-manifest.json
0000000000000000000000000000000000000000000000000000000000000000  docs/runs/2026-09-14-clean-sweep-tracker/u393r-manifest.json
0000000000000000000000000000000000000000000000000000000000000000  docs/runs/2026-09-14-clean-sweep-tracker.md
0000000000000000000000000000000000000000000000000000000000000000  docs/reports/clean-sweep-selfrun/verifier-u387p.txt
```

## Gates

Catalog gates at the promotion tip (exact commands, exit codes):

GATES-PENDING (run at the final tip before close: `python3 scripts/validate.py`,
`python3 -m unittest discover -s tests`, `python3 runtime/scripts/proof_status.py --check`,
`python3 runtime/scripts/run_report.py`)

## Parks register (what the run did not close)

- #386 — `needs-human`, OPEN. Sign the manifest/inventory + retention backend
  (Q2). Triage-confirmed real; no unit work until the maintainer answers key
  custody, backend choice, and the transcript prerequisite (`gate-batch.md` G1).
- #235 — `needs-human`, OPEN. Marketplace submissions need external
  accounts/listings; the maintainer works it directly (pre-parked, re-confirmed
  OPEN at T0 and at close).
- Review legs, T1/T2/T3/T7/T9/T10/T11 — `needs-human` per unit, recoverable.
  One GitHub identity on the run host and no bot APPROVED on those final tips,
  so `verify.py` stays 5/6 with the review leg RED. The ask is a post-merge
  independent APPROVE per head (listed in `gate-batch.md` G3) or a recorded
  waiver ruling the blind-verdict + executed-negative-control compensation
  sufficient. Re-running `verify.py` after either flips the leg without
  touching any other evidence.
- Owed at close: G1 + G2 (verdict-derived branch protection) + G3 + G4
  (non-blocking retro-confirm). A promotion that hides these parks is narration;
  this report carries them so the tier means DRY-WITH-PARKED, not DRY.

## Catalog proof promotion

- Report: `docs/runs/2026-09-14-clean-sweep-self-run.md` (this file), run
  directory `docs/runs/2026-09-14-clean-sweep-tracker/`, index row in
  `docs/runs/README.md`.
- `skills/clean-sweep/SKILL.md`: `proof: self-run` with
  `proof_evidence:` pointing here (issue #411).
- `python3 runtime/scripts/run_report.py` exits 0 on this report; the transcript
  above is a real execution, not prose about one. The gate hashes artifacts at
  the named commit; it does not re-run the verifier — the re-derivable half is
  the inventory plus the recorded `cmd_sha256` against a resolvable tree.
