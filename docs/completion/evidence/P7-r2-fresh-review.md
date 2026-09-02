# Phase 7 fresh-reviewer report (separate context, read-only) — run 2, 2026-09-02, tree at 1286807

Verbatim findings returned by the reviewer. Disposition is logged in SHIPLOG.md ("PHASE 7 fresh-reviewer handoff").

## S1 — verdict-affecting or unsupported claims
- **RV-01 (S1)** A-19's GO rests on reclassifying the H-01 action as non-gating when it recurs as H-07. DEFINITION item 8 names the action "Orca up + review-it dry run" as launch-gating; H-07 is that exact instruction on the current head, and `skills/review-it/SKILL.md` changed in #225 (+10/-3). Fix: H-07 `gates_launch: true`, CF-05 "verified at 6ad0e87 / re-witness pending", verdict CONDITIONAL GO.
- **RV-02 (S1)** "329 OK ×2 · no flake" is not in any run-2 evidence file and a skipped test is never disclosed: the suite is `Ran 329 tests … OK (skipped=1)`; the skip is `tests/test_vfbench.py::test_review_trap_verdict_tracks_review_ok` because this container is a shallow clone (201 commits). Fix: "328 ran + 1 skipped (shallow clone; covered by CI #105 with fetch-depth: 0)"; keep the `Ran N tests` line in captures; caveat under A-09/A-18.
- **RV-03 (S1)** The gate evaluation never checks DEFINITION.md's "Minimum scores" section, and the check is load-bearing (angles 1, 7, 8 rose 2→3 this run; angle 8 cited the substrate-absence file). Fix: explicit minima row per angle with evidence pointers.

## S2 — degraded honesty / evidence quality
- **RV-04 (S2)** DEFINITION.md was edited after its freeze commit (`67c1707` rewrote items 4 and 5 during run 1); "frozen_at: ed6a2f4 / immutable" is false as a content pointer and run 2 said "stays frozen at ed6a2f4". The later text is stricter/more honest and does not change the verdict. Fix: re-stamp or annotate `frozen_at` as `67c1707`; A-19 should cite it.
- **RV-05 (S2)** CF-05's failure evidence was swapped for an environment note (`orca: command not found`); run 1's `CF-05-failure-orca-not-running.txt` (`orca status --json` → reachable:false) is the real "Orca down → documented stop" and is now orphaned. Fix: point back; describe the r2 file as substrate absence; re-justify angle 8.
- **RV-06 (S2)** CF-05's happy evidence never exercised the documented flow (coordinator-authored self-review of PR #208, not spawned read-only workers) and run 2 dropped run 1's caveat. Fix: carry the caveat; H-07 requires the worker-dispatch shape on a PR the reviewing session did not author.
- **RV-07 (S2)** Angle 11 rose 2→3 on a prose summary while Orca and the greptile CLI were less observed than in run 1. Fix: capture the API responses for #225 into evidence, or hold angle 11 at 2.

## S3 — polish
- **RV-08** stranger-test evidence is a 4-line self-report; include the timed command list.
- **RV-09** stale run-1 text not marked historical (PLAN.md P2/P3 rows, "Launch-gating Human Actions: 1 (H-01)", HUMAN_ACTIONS "H-01 is the only launch gate"); GAPS.md rule "S2/S3 → DEFER unless small and on a critical flow" vs G-15/G-17/G-18 FINISH off-flow.
- **RV-10** research id collision: run-1 R-04 (production-readiness refs) vs run-2 "R-04 GitHub Actions notifications" — renumber to R-06.
- **RV-11** "largest ship-it/oss-contribute 129/130" reads as line counts; budget is 130.
- **RV-12** hygiene evidence redacts the grep pattern; record it (it contains no secret).
- **RV-13** ledger cosmetics: `history[2].commit: "pending-t08"`; T-08 `block_signature` stale while done; T-06/T-07 holes unexplained; P7 "Gate evaluated" met=true from run 1 while STATUS said pending; H-06 "flips gate item 5" would mean editing the frozen file; SHIPLOG T-09 entry lacks a `resume_pointer`; PLAN lists T-09 under P7 while SHIPLOG says Phase 5; `19fbad5` is not the run-1 close.
- **RV-14 (process)** A-15 records maintainer authorship with no trailers; agent-written commits should carry trailers or A-15 should cite the maintainer's explicit instruction.

## Launch gate, item by item (reviewer's table)
| # | Item as written | Run-2 evidence | Met as written? |
|---|---|---|---|
| 1 | Every S0 closed | no S0 | yes |
| 2 | Every CF evidenced, happy + failure | CF-01/02/03/04/06 at f2e53f4; CF-05 happy at 6ad0e87 only, failure = run-1 file | on the letter yes; on the run's own rebaseline no (RV-01, RV-06) |
| 3 | Fresh clone reproduces CF-01 | CF-01-r2 — validate 0, tests OK (skipped=1), proof_status 0 | yes (shallow-clone caveat) |
| 4 | git revert on a scratch clone | P0-r2-rollback-rehearsal.txt | yes |
| 5 | "not demonstrated … does not block" | CI #105 success; no failure alert witnessed | not a condition as written (post-freeze wording, RV-04) |
| 6 | Stranger Test ≤15 min | 27s, corroborated by CF timestamps | yes (evidence thin, RV-08) |
| 7 | No ACCEPT at S0 | G-14 S3 ACCEPT, expiry issue #226 | yes |
| 8 | Launch-gating HAs: H-01 | H-01 done; H-07 is the same action on the current head, classified non-gating | contested (RV-01) |
| min | ≥3 on 1–9 (9 ≥1 via A-12), ≥2 on 10–17 | 1–8 = 3, 9 = 1, 10 = 2, 11 = 3, 14 = 3, 15 = 2, 16 = 2, 17 = 3 | yes, but never evaluated (RV-03) |

## Checked, no finding
Arithmetic (59.75/87 = 69%; 56% and 52% match history); status.json vs markdown for G-01..G-18, T-01..T-09, H-01..H-07, phases, resume pointers; all 43 referenced evidence paths exist; independent reruns at HEAD (validate 13/13, proof_status 9/2/2, unittest 329 = 328 ran + 1 skipped); drift 49/216 and 74 since 6abf548 exact; CI pins and rule set confirmed; GitHub About description "10 outcome-named autonomous fleets…" vs 13 skills confirmed; run #105 success; issue #226 open with `post-launch`; SHIPLOG append-only (run-1 entries byte-identical; only header lines changed); every run-2 phase entry has a second look; anti-gaming: DEFINITION.md not edited by run 2, no flow cut/reclassified, N/A reasons checkable, angle 9 held at 1, DEFER/ACCEPT below the line.

## Overall verdict (reviewer)
Accept the audit as honest in substance with three repairs (RV-02, RV-04, RV-05/06). Do not accept GO: it is produced by classifying H-07 non-gating and by never writing out the minima check. CONDITIONAL GO, pending H-07, candidly labeled with the item-5 waiver, is the verdict the evidence supports.
