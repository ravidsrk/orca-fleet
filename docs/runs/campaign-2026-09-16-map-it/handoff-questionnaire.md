# Human handoff — map-it self-test questionnaire (Q-0..Q-21)

Purpose: resolve the 21 blocked decision tickets + 4 premises + 3 task checklists of the
G-09 field-proof map so it can freeze and a consumer can run it.
Sender: map-it coordinator, run `run_b28a7dacdd9e` (spawned campaign child, 2026-09-16).
Recipient: the human maintainer (repo owner role). First ask if misrouted: who owns G-09 scope?
Answers go to: this file's stubs (or a reply quoting Q-ids); the unparking worker re-derives
VERIFY-COMPLETE per item. Deadline: none set (campaign self-test). Effort: ~30 min.
Partial answers and "I don't know" are explicitly welcome — flag, don't skip.
Context (one paragraph): the map charts proof runs for all 19 doctrine-only missions
(`plan.md` in this dir, freeze-prepared on branch `campaign/map-it-selftest`). Facts are
cleared; every remaining question needs a human call the fleet must not make itself. Answer
in one pass; one decision per follow-up session thereafter.

## Q-0 — FREEZE sign-off (D-0, one-way) + premises P-1..P-4

Do you give an EXPLICIT yes to freeze `plan.md` + the prepared DAG as the G-09 execution
map? (Silence / "looks good" is not a freeze.) And per premise: agree / disagree?
P-1 all-19 scope · P-2 self-runs first · P-3 no production code · P-4 human-owned selections.

> ANSWER (yes + P-1..P-4 agree/disagree):

VERIFY-COMPLETE: a reply line quoting `Q-0` with an explicit `yes` token and four
agree/disagree tokens, recorded in DECISIONS.md with `class=one-way source=human:<who>`.

## Q-1 — Scope (D-1, taste)

All 19 missions in this map, or phase it (wave-1 self-runs only, wave 2 unticketed until
selections land)? Recommendation: all-19 (ideal alternative; default in plan.md).

> ANSWER (all-19 / phased):

## Q-2..Q-11 — External selections (D-2..D-11, taste; one idea each)

- Q-2 (access-it): which repo with a web UI + axe-core baseline? RECOMMENDATION: none — human picks.
- Q-3 (deflake-it): which suite with a known observed flake?
- Q-4 (modernize-it): which repo with a lockfile/dependencies?
- Q-5 (field-test-it): which mobile app + which paired device (see T-2 below)?
- Q-6 (migrate-it): which repo with a real pending migration + data?
- Q-7 (oncall-it): which staging service path set + alert destination (see T-3 below)?
- Q-8 (oss-contribute): which upstream tracker's issues?
- Q-9 (review-it): next real PR in this repo, or a named upstream PR?
- Q-10 (root-cause): wait for a live bug here, or name an OSS bug now?
- Q-11 (absorb-it): this repo's inbound queue once it exists, or a named external queue?

> ANSWERS (repo/choice per Q-id, or "defer"):

## Q-12..Q-18 — Self-run gates (taste/one-way)

- Q-12 (D-12, taste): speed-it wall-clock budget for the catalog-gates journey (e.g. ≤30s)?
- Q-13 (D-13, one-way): floor-it freeze-gate approach — approved as planned?
- Q-14 (D-14, one-way): reshape-it CONFIRM-SURFACE — which modules are in?
- Q-15 (D-15, one-way): harden-it PoC-routing gate — approved for verify.py/dispatch-sign.py/verify-gate.sh?
- Q-16 (D-16, taste): ship-it proof lane — second GitHub identity, or executed-control lane?
- Q-17 (D-17, taste): document-it — freeze which public surface?
- Q-18 (D-18, taste): attest-it — freeze which catalog digest?

> ANSWERS:

## Q-19 — Waves (D-19, taste)

Wave-1 self-runs then wave-2 fan, or interleaved? Recommendation: wave-1 then wave-2 fan.

> ANSWER:

## Q-20 — Task checklists (T-1..T-3 — bounded manual work)

- T-1: paid-provider budget for pin-it paid-trust parks — approved amount/account, or declined
  (parks carry over)? Return: decision + account/amount or decline note.
- T-2: pair the field-test-it device — return: model + host + access path + pairing receipt.
- T-3: oncall-it staging — return: path set + alert destination + test-fire receipt id.

> ANSWERS (facts returned per item):

## Q-21 — pin-it timing (D-20, taste)

pin-it proof run now, or ride the #427 cadence (2026-12-16 / next minor)? Recommendation: now
(target exists; #427 inherits this run's parks either way).

> ANSWER (now / ride-427):

## VERIFY-COMPLETE (all Q-1..Q-21)

A fresh worker checks: this file (or its quoted reply) carries an answer stub per Q-id with
a concrete value (choice / repo / amount / yes / decline-with-reason), and each value is
transcribed to its D/T ticket row in `ledger.md` with status RESOLVED + the human source.
"Owner says done" alone closes nothing. Items still stub-empty stay BLOCKED; the map stays
MAPPED-WITH-BLOCKED until Q-0's explicit yes exists AND every ticket it freezes over is
resolved or explicitly listed blocked.
