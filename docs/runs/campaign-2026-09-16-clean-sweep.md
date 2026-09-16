# Run report — clean-sweep campaign self-test, 2026-09-16

RUN: mission=clean-sweep tier=doctrine-only inventory_at=TBD manifest=- (no unit manifest: 0 units reached BUILD_DONE) verifier=n/a (no unit to verify) waves=0

Campaign self-test of the `clean-sweep` mission against orca-fleet itself
(`source=tracker`, T0 2026-09-16T09:59:44Z, BASE `campaign/clean-sweep-selftest`
from `6390743`). Nine open issues enumerated by twin queries, skeptic-triaged with
repros, frozen to 1 build unit + 8 parks; the unit parked mid-build when the
provisioned regen credential returned HTTP 401. Loop-2 re-enumeration shows the same
9 open with zero mid-run changes. Terminal: **DRY-WITH-PARKED** (degraded).
This report claims no proof tier (see Evidence binding).

| Field | Value |
|---|---|
| Mission | `clean-sweep` — SKILL @ `6390743`, `skills/clean-sweep/SKILL.md` |
| Tier claimed | `doctrine-only` (campaign self-test; not a proof promotion) |
| Target | this repo's own tracker: 9 open at T0 (#235 #386 #407 #408 #409 #417 #427 #434 #440) |
| Fixed point | BASE `campaign/clean-sweep-selftest` · FORK_POINT `6390743815f8f435181fa410cce374587128b30a` · frozen verdicts `docs/runs/campaign-2026-09-16-clean-sweep/triage/verdicts.md` · U434 taskspec `taskspecs/build-434-diagrams.md` (sha256:fc2817c4…) |
| Coordinator / workers | session-a4a0c7e3 (Muse Spark), solo — no Orca dispatch (contract bar) · PROFILE=ro triage / rw-equivalent build, in-session · TASK pack matt (triage + tdd + code-review — one pack) |
| Orca | not used for dispatch this run (solo harness deviation D1); `orca --version` → `1.4.203`, matching the catalog pin |
| Human gates | none taken; parks name their owed gates (gate-batch G1/G2/G3, regen credential, external accounts) |

## Terminal state

**DRY-WITH-PARKED** (degraded): the frozen set is exhausted — every finding is
PARKED in a ledger-legal class — but 0 closed and 4 degraded parks remain.
Never reported as DRY.

| task_id | id | title | CLASS | BUILD_DONE | PR_OPEN | BOT | REVIEWED | MERGED | WT_CLEAN | lighting | park | evidence |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| T434 | #434 | Regenerate proof-ladder diagrams | real-bug | f | f | n/a | f | f | n/a | lit | needs-human (regen key 401) | taskspec; triage/u434-red-attempt.txt; triage/u434-regen-401.txt |
| — | #440 | Flaky wtree_equivalence teardown | out-of-scope | — | — | — | — | — | — | — | out-of-scope → deflake-it | verdicts.md; triage/440-determinism-probe.txt |
| — | #427 | Re-pin Orca contract | out-of-scope | — | — | — | — | — | — | — | out-of-scope → pin-it | verdicts.md |
| — | #417 | Mission-chaining exercise | out-of-scope | — | — | — | — | — | — | — | out-of-scope → chaining run | verdicts.md |
| — | #409 | Promote harden-it to self-run | out-of-scope | — | — | — | — | — | — | — | out-of-scope → harden-it | verdicts.md |
| — | #408 | Settle runway G1-G4 | — | — | — | — | — | — | — | — | needs-human (G1/G2/G3 owed) | gate-batch.json re-read 2026-09-16 |
| — | #407 | Roadmap epic 0.6.1→1.0 | out-of-scope | — | — | — | — | — | — | — | out-of-scope → roadmap children | verdicts.md |
| — | #386 | Sign manifest/inventory | — | — | — | — | — | — | — | — | needs-human (G1 owed + deferred) | gate-batch G1; owner comment |
| — | #235 | Marketplace submissions | — | — | — | — | — | — | — | — | needs-human (external accounts) | distribution.md boxes `[ ]` |

## Convergence proof

Mission `## Convergence proof`, clause by clause:

1. *Full enumeration finds ZERO items not CLOSED-with-evidence or PARKED-allowed.*
   Loop-2 queries agree on the same 9 open (`enumeration-q1-loop2.json`,
   `enumeration-q2-loop2.json`); the loop-2 enumeration output is pasted in the
   ledger loop-log. All 9 carry a PARKED class above; 0 CLOSED (no merges — harness
   rule — and U434 blocked on the 401). No refuted/duplicate closes occurred, so no
   batch gate was owed. `needs-human` parks name their gate/OPS ref (regen
   credential; gate-batch G1/G2/G3; external accounts).
2. *`source=tracker` reconciles created/closed-mid-run issues against T0.*
   `since-t0-loop1.json` and `since-t0-loop2.json` both read `{"total":0}` — nothing
   created, reopened, or closed mid-run; no `externally-resolved`, no next-loop set.
3. *Manifest names DRY or DRY-WITH-PARKED.* This report's Terminal state names
   DRY-WITH-PARKED — the degraded marker is present, not hidden.
4. *DRY also requires the integration TIP green — N/A (not DRY).* Recorded anyway:
   the final head is green (see Gates: validate exit 0, suite 1490 OK exit 0,
   proof_status exit 0).

## Completion audit (per frozen item — no blanket sweep)

| item | mode | verdict | citation |
|---|---|---|---|
| #434 AC-1..AC-4 (regen + alts + captions + gates) | DIFF | NOT DONE | `gen.py` exit 1, HTTP 401 both ids (`triage/u434-regen-401.txt`); spec/alt edits reverted, unlanded test removed — tree intentionally unchanged |
| #434 AC-4 gates half (suite/validate green at tip) | DIFF | DONE | `validation.txt` exit 0; `tests-full.txt` 1490 OK exit 0 |
| #440 teardown fix | DIFF | handed off (out-of-scope → deflake-it) | flake confirmed real but intermittent: 12/12 green locally (`triage/440-determinism-probe.txt`); bare `TemporaryDirectory()` at `tests/test_verify.py:320` |
| #427 re-pin | DIFF (future) | handed off (out-of-scope → pin-it) | no trigger fired: date 2026-12-16 future, installed 1.4.203 == pin, upstream v1.4.204 is a riding patch, no drift sighting |
| #417 chain run | DIFF (report) | handed off (out-of-scope → chaining run) | declaration stands, no `docs/reports/chaining-*`, scratch target absent, branch == main tip; needs a fleet this harness cannot mount |
| #409 harden-it promotion | DIFF | handed off (out-of-scope → harden-it) | re-scoped to self-run loop + human PoC gate (owner comment 2026-09-16); premise verified (`proof: doctrine-only`) |
| #408 G1-G4 answers | EXTERNAL-STATE (human) | owed (needs-human) | G1/G2/G3 `owed`, answers null (`gate-batch.json`); G4 `overtaken` (record-only) |
| #407 epic close | CROSS-ITEM (children) | handed off (out-of-scope → children) | children #410 #411 #412 #413 #414 #415 #416 #418 #419 CLOSED, #408 #409 #417 OPEN — epic cannot close until they do |
| #386 signing | DIFF | owed (needs-human) | gap real (dispatch-sign covers dispatch only) but owner-deferred pending #281 + G1 (comment 2026-09-14); G1 still owed |
| #235 listings | EXTERNAL-STATE (accounts) | owed (needs-human) | `docs/distribution.md:114-118` boxes still `[ ]`; no agent slice remains |

Tally: 1 DONE (gates half) · 1 NOT DONE (U434 fix, negative evidence kept) ·
5 handed off · 3 owed. Prior-run claims re-verified (inflation post-mortem):
#364 #385 #388 #389 #393 still CLOSED, #386 #235 still OPEN — no
green-but-unverified claim entered this enumeration.

## Pipeline evidence (per phase)

| Phase | Command / action | Result | Evidence |
|---|---|---|---|
| SELF-ORIENT | read SKILL + AGENTS + ARCHITECTURE + 5 playbooks + 9 runtime policies | done | (this report) |
| ENUMERATE | `gh issue list --state open --limit 200 --json ...` (q1) + REST GET paginated (q2) | 9 open, q1==q2 | `enumeration-q1.json` (sha256:1ae6477e…), `enumeration-q2.json`, `since-t0-loop1.json` (`total:0`) |
| SKEPTIC-TRIAGE | 9 issues via `guard_text.py --source issue`; repros per issue | 1 real-bug + 8 parks | `triage/issue-*.fenced.txt`, `triage/440-determinism-probe.txt`, `triage/verdicts.md` |
| FREEZE | verdicts frozen; wave-plan assertion (9 ids → 1 unit + 8 parks) | holds | `triage/verdicts.md`, `ledger.md` |
| BOOTSTRAP | `git checkout -b campaign/clean-sweep-selftest`; `preflight.py --base ... --fork-point 6390743...` | OK (fresh-branch WARN noted) | `preflight.txt` |
| PER-FINDING U434 | taskspec frozen (sha256:fc2817c4…); red-first test 3 FAIL/1 ok; spec+alt edits; `gen.py --only proof-ladder,proof-ladder-light` ×2 | 401 both ids, exit 1 → stop clause → revert + park | `taskspecs/build-434-diagrams.md`, `triage/u434-red-attempt.txt`, `triage/u434-regen-401.txt`, DECISIONS `css-u434-park-401` |
| re-ENUMERATE | loop-2 twin queries + since-T0 | same 9, `total:0` — exhausted | `enumeration-q*-loop2.json`, `since-t0-loop2.json`, ledger loop-log |
| FINAL report + compound-learn | this report + REFLECTION.md | done | this file, `REFLECTION.md` |
| VERIFY final tip | `scripts/validate.py`; `unittest discover -s tests`; `proof_status.py --check` | exit 0 / 1490 OK exit 0 / exit 0 | `validation.txt`, `tests-full.txt`, `proof-status.txt` |

Promotion PR + human gates: out of scope per the mission (open-and-stop) and barred
by the harness (no push/PR/merge) — owed, named in Parks register.

## Verifier outcome

Inapplicable — there is no unit manifest to verify: 0 units reached BUILD_DONE
(U434 parked before any content commit; its red-test transcript is triage evidence,
not a proof). No `verify.py` invocation is recorded because inventing one against
no manifest would be narration. The gates that DID run (validate, full suite,
proof_status) are pasted under Gates with true exit codes.

## WIP-curve protocol row

Inapplicable — this run dispatched 0 Orca waves (`waves=0`; solo harness, no
dispatch channel) and completed 0 mutation units, so there is no
verified-CLOSED-per-hour figure to plot. Qualitative observation (not a protocol
point): in a solo+triage-heavy run, wall-clock is dominated by skeptic-triage
repros (9 issues, ~1h) while the single build unit blocked on an external
credential — the caps stay ASSERTED.

## Deviations and lessons (recorded, not hidden)

- D1 Solo run, no Orca dispatch (harness contract forbids recursive/Native-agent
  control): coordinator executed all phases in-session with phase-separated,
  file-bound evidence. Independence is weaker than a dispatched fleet throughout.
- D2 Harness forbids push/PR/merge/tracker writes: no PR_OPEN/MERGED flags, no
  issue closes posted, promotion owed. Terminal DRY-WITH-PARKED, never DRY.
- D3 No second identity exists, so no build-blind review was possible; U434 never
  reached review (parked at build). No independence is claimed anywhere.
- D4 `gh api -f` on a GET endpoint silently POSTs (HTTP 422); q2 re-ran with
  explicit `--method GET` — the failed form is disclosed, not hidden.
- D5 First `EXIT=` readings after pipes reported tail's status; all gate exits in
  this report come from redirect-to-file runs (true codes).
- D6 U434 regen: provisioned key present-but-invalid (HTTP 401 "User not found",
  2 attempts) → identical-error kill, taskspec stop clause, full revert. Lesson:
  probe paid credentials in triage (see REFLECTION.md).

## Run-close integrity inventory (sha256)

| Artifact | sha256 | producer |
|---|---|---|
| `docs/runs/campaign-2026-09-16-clean-sweep/ledger.md` | `c4ca02e9a9a0b6597736c6e407e84458f8c7c31530c58bdd6f74e867918888f6` | coordinator 2026-09-16 |
| `docs/runs/campaign-2026-09-16-clean-sweep/preflight.txt` | `2e53b3f734048e35b478e3a61c4864c176068719617cefa993f6aa4a51830879` | preflight.py 2026-09-16 |
| `docs/runs/campaign-2026-09-16-clean-sweep/enumeration-q1.json` | `1ae6477ec9a54d06a67d2d521aa5dfb8dabd40328a0d50c903c517c19a928526` | gh issue list 2026-09-16 |
| `docs/runs/campaign-2026-09-16-clean-sweep/enumeration-q2.json` | `0a1e66830076feb92c8fbdb8aa9fcad8b3f49c9904e8ce56defb8ca1387e3664` | gh api REST 2026-09-16 |
| `docs/runs/campaign-2026-09-16-clean-sweep/since-t0-loop1.json` | `ad6a90d08b4184f7018a5a73a6eca4ebf15e7b0cc8f022ad677825ea3d1be68d` | gh api search 2026-09-16 |
| `docs/runs/campaign-2026-09-16-clean-sweep/enumeration-q1-loop2.json` | `6efefc81f62bfff6fdccc077d64240b82995e48ebd3d5e82296004891d81590d` | gh issue list 2026-09-16 |
| `docs/runs/campaign-2026-09-16-clean-sweep/enumeration-q2-loop2.json` | `5eef27b88e663a6bb3f58e6d2a271cc67cf85833f235532a4a87839b53423bf9` | gh api REST 2026-09-16 |
| `docs/runs/campaign-2026-09-16-clean-sweep/since-t0-loop2.json` | `ad6a90d08b4184f7018a5a73a6eca4ebf15e7b0cc8f022ad677825ea3d1be68d` | gh api search 2026-09-16 |
| `docs/runs/campaign-2026-09-16-clean-sweep/taskspecs/build-434-diagrams.md` | `fc2817c460e8e5a5f0c0a4b3c33ef7061439045f82086e07033488c484a6b945` | coordinator (frozen) 2026-09-16 |
| `docs/runs/campaign-2026-09-16-clean-sweep/triage/verdicts.md` | `09f70a77810925b77767da553663e7de573ea632ea4ff9bf59ca69e66fa2fea4` | coordinator (frozen) 2026-09-16 |
| `docs/runs/campaign-2026-09-16-clean-sweep/triage/issue-235.fenced.txt` | `2ece08159fec5a3a701c27714dbb6a6c2c9ccce272b41e28228a8ba2c84cc9b0` | guard_text.py 2026-09-16 |
| `docs/runs/campaign-2026-09-16-clean-sweep/triage/issue-386.fenced.txt` | `8b8fef7666ad7a44c8368d4f3151bd8d008c54fb1f17caf17ff6dcd38a684fdd` | guard_text.py 2026-09-16 |
| `docs/runs/campaign-2026-09-16-clean-sweep/triage/issue-407.fenced.txt` | `d2ad19e2e2b6d52c19a8ac14b6ac64290801e3990675a6b460a7e9d49528920c` | guard_text.py 2026-09-16 |
| `docs/runs/campaign-2026-09-16-clean-sweep/triage/issue-408.fenced.txt` | `5f2a40b9ae84ee08f75372fd1322afd1443b78387115d13d8f1f7ff9d99232ae` | guard_text.py 2026-09-16 |
| `docs/runs/campaign-2026-09-16-clean-sweep/triage/issue-409.fenced.txt` | `7d742f0e8d071730e769477dbe3af8c77c0852a44cd59143d44429588faee92f` | guard_text.py 2026-09-16 |
| `docs/runs/campaign-2026-09-16-clean-sweep/triage/issue-417.fenced.txt` | `eed65a3eeccaf19ee5890346a69f7a75cd0c91331378aee7dcf13d1a8533bf18` | guard_text.py 2026-09-16 |
| `docs/runs/campaign-2026-09-16-clean-sweep/triage/issue-417-comments.fenced.txt` | `bd19ea264d5ac179d9e9222e71f8722c3a4956c0f2112522ee2e050128fcdd55` | guard_text.py 2026-09-16 |
| `docs/runs/campaign-2026-09-16-clean-sweep/triage/issue-427.fenced.txt` | `0718c9e19f9bb4ef3824e5638659891ebf295efb31c07a7314fcd8af7371a70a` | guard_text.py 2026-09-16 |
| `docs/runs/campaign-2026-09-16-clean-sweep/triage/issue-434.fenced.txt` | `78d421fc742014c66e6214aa33bb61d58b9483e912b39e2d6d6320c1d4bc898d` | guard_text.py 2026-09-16 |
| `docs/runs/campaign-2026-09-16-clean-sweep/triage/issue-440.fenced.txt` | `724ae9081758cb416034583340b4e018693333c2f311245e6a8a91cfbfb7e7b5` | guard_text.py 2026-09-16 |
| `docs/runs/campaign-2026-09-16-clean-sweep/triage/440-determinism-probe.txt` | `60902a71cd324720073a18b88f941f92cae526220fa1ca87890e851cd92768b7` | unittest 12x 2026-09-16 |
| `docs/runs/campaign-2026-09-16-clean-sweep/triage/u434-red-attempt.txt` | `9b5c579167ee7b6bd36d5134dd84ec795345bde2a5b8592a422ac1bbb04544e0` | unittest (RED) 2026-09-16 |
| `docs/runs/campaign-2026-09-16-clean-sweep/triage/u434-regen-401.txt` | `c7b1415d890a18847fd7d808241e6d026d825c2508181a599686f91dcaabd5e6` | gen.py (exit 1) 2026-09-16 |
| `docs/runs/campaign-2026-09-16-clean-sweep/validation.txt` | `90e1cc04c2301795dbb6306b86320f4cb65d9994187cc9ed7a251176258760a6` | scripts/validate.py 2026-09-16 |
| `docs/runs/campaign-2026-09-16-clean-sweep/tests-full.txt` | `6aa140a9738ca4a21443f15c9abfce02d181e54dd3f041091299d12e6b8c7934` | unittest discover 2026-09-16 |
| `docs/runs/campaign-2026-09-16-clean-sweep/proof-status.txt` | `b1e6e3988e6142ce64be2e21c8dc24faee807d94db29b19a566f0dfcf436c110` | proof_status.py 2026-09-16 |
| `docs/runs/campaign-2026-09-16-clean-sweep/REFLECTION.md` | `f94048f6e74dacda042c0b57dd1c95ef7b7ed2e66efbbcf21e45dde7e4b3ab6d` | coordinator compound-learn 2026-09-16 |

## Gates

`python3 scripts/validate.py` (exit 0; full transcript in `validation.txt`):

```
All 21 missions valid; three-layer separation holds; evals valid.
```

`python3 -m unittest discover -s tests` (exit 0; full transcript in `tests-full.txt`):

```
Ran 1490 tests in 255.671s

OK
```

`python3 runtime/scripts/proof_status.py --check` (exit 0; full transcript in `proof-status.txt`):

```
coverage rollup:
  doctrine-only  19
  self-run       2
  external-run   0
  total          21
```

## Parks register (what the run did not close)

- #434 — `needs-human`, OPEN. Real bug, fully triaged with a frozen taskspec and a
  red-first test (transcript kept). Owed: a working `OPENROUTER_API_KEY` (the
  provisioned one 401s) or maintainer-supplied renders + spend ack; then re-run U434
  from the frozen taskspec (spec edit → regen → wire → caption removal → green).
- #408 — `needs-human`, OPEN. G1/G2/G3 still `owed` in `gate-batch.json`; one
  maintainer round. (G4 `overtaken` — record-only.)
- #386 — `needs-human`, OPEN. G1 owed + owner-deferred pending #281.
- #235 — `needs-human`, OPEN. External accounts/listings; no agent slice remains.
- #440/#427/#417/#409/#407 — `out-of-scope` handed off (deflake-it / pin-it /
  chaining run / harden-it / roadmap children). No batch gate owed (no
  refuted/duplicate closes).

## Evidence binding

Recorded history supporting no proof-tier advance: `tier=doctrine-only`, no unit
manifest exists (0 units reached BUILD_DONE), and no `verify.py` transcript is
claimed. The integrity inventory above covers every artifact this run owns; it is
filled by `inventory.py write` and re-checked with `check --at <inventory_at>`.
`clean-sweep`'s `proof: self-run` citation is untouched by this report.
