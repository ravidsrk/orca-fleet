I'll treat this as a read-only adversarial review of the run-3 ledger: inspect the FETCH_HEAD diff and cited evidence, then check each claim against the frozen gate.Diff is docs-only under `docs/completion/`. Next I’ll pin the frozen gate and the run-3 ledger files, then check each claim against the cited evidence.Ledger files are in; next I’ll pull SHIPLOG, PLAN, HUMAN_ACTIONS, and the CF-05/P0 evidence so I can cross-check counts, IDs, and cited paths.I have the axis reports and the CF-05 happy-path file. Next I’ll pin dispatch IDs, cold-start counts, and the JSON gap/task records.The dispatch record still shows `dispatched` with null completion. I’ll read the tail and the remaining ledger diffs next.Claim (a) cold-start counts check out. Dispatch IDs match, but the cited “full receipts” file does not show worker settlement — that is the main integrity break.# Adversarial review — completion-driver run 3 ledger

**Profile:** `ro` (this session did not produce the work).  
**Fixed point:** `6671913` (`main`) → `FETCH_HEAD` `7765b7b` (`docs: run 3 — CF-05 re-witnessed…`).  
**Diff:** 22 files, all under `docs/completion/`. `DEFINITION.md` is **not** in the diff (`git diff 6671913 FETCH_HEAD -- docs/completion/DEFINITION.md` is empty).  
**Method:** claims (a)–(d) vs cited evidence at `FETCH_HEAD`; gate table vs frozen `DEFINITION.md`; ledger cross-check; dispatch IDs vs axis aggregates. Axis findings of PR #231 were **not** reranked.

---

## Claim results (before findings)

| Claim | Result |
|---|---|
| **(a)** P0-r3 cold start: exit 0, 329 tests, 0 skips, 13 missions, 9/2/2 proof tiers | **Holds** on the suite/validate/proof files. Two weaker cites: bare `eval.py` recorded `exit=0` on a usage error; `P0-r3-coldstart-tools.txt` is cited for orca and does not mention orca. |
| **(b)** review-it dry run on PR #231 @ `9e1237f`, three ro workers via Orca, closes G-16 and H-07 | **Partial.** Run/task/ctx IDs match across happy-path file, SHIPLOG, and dispatch JSON. Ancestry `9e1237f` ⊂ `6671913` holds. G-16/H-07/T-13 are closed/done in GAPS, HUMAN_ACTIONS, and `status.json`. The happy file’s **settlement** claims (`completed`, `worker_done`, ack, release, `delivery_d198b6afc31b`) are **not** in the cited dispatch record. |
| **(c)** NO-GO, 0 Critical / 3 Required → G-19/G-20/G-21 | **Aggregate holds** (standards 0R + spec 2R + test-adequacy 1R = 3R). Mapping exists. **spec F1 (Required) is filed as G-21 S3 “lesson”.** |
| **(d)** Launch gate re-evaluated **GO** | **Logic is allowed by frozen CF-05** (“GO or NO-GO both count”). Item 8 can go **yes** once H-07 is done. GO still rests on (b)’s dispatch evidence being what the text says it is. |

---

## Findings

| ID | Sev | Finding | Quote at `FETCH_HEAD` |
|---|---|---|---|
| **RV-01** | **S1** | **Dispatch “full receipts” do not show settlement.** Happy-path + SHIPLOG claim three tasks `completed`, each ctx closed by `worker_done`, deliveries acked as `delivery_d198b6afc31b`, workers released. The cited record’s grok dispatches are `"status": "dispatched"`, `"completed_at": null`, and the file ends on a paraphrased `terminal send` — no `worker_done` receipt, no ack, no release. `delivery_d198b6afc31b` occurs **once** in the whole tree (the happy file), one id for three workers. `when: 05:00–05:20Z` does not cover `dispatched_at: 2026-09-09 05:35:06`. IDs themselves **match** (run_7bdde218b205, task_e8fb7d7b6f7d / d854cb862862 / c3b7f4fa2143, ctx_575e99a6648d / 630ff02c7ee2 / ac069f3f25fe). Axis reports exist and support a SHA-bound NO-GO; the **orchestration completion claim** is not in the file labeled “full receipts.” Gate items 2 and 8 cite this bundle. | `docs/completion/evidence/CF-05-r3-happy-review-it.txt:14` `## Dispatch record (full receipts: CF-05-r3-dispatch-record.txt)` · `:19` `… all \`completed\`` · `:20` `… each closed by a valid worker_done … deliveries acked (delivery_d198b6afc31b), workers released` · `:11` `when: 2026-09-09T05:00–05:20Z` · `docs/completion/SHIPLOG.md:246` (same settlement sentence) · `docs/completion/evidence/CF-05-r3-dispatch-record.txt:1158` `"status": "dispatched"` · `:1162` `"completed_at": null` · `:1249` `$ terminal send x3: grok --prompt-file …` |
| **RV-02** | **S2** | **“Filed in S5-C” is written as done; GitHub issues are not.** G-19/G-20/G-21 have `"issue_url": null`. The post-launch table still ends at G-14/#226 and is titled “filed 2026-09-01”. STATUS header still says filing is **next** (`S5-B → S5-C`). Driver Phase 7 step 3 is “every DEFER is a filed issue”; they did not count DEFER as complete (R13), but several docs speak in the past tense. | `docs/completion/GAPS.md:33` `Run 3 adds G-19 / G-20 / G-21 DEFER (filed in S5-C).` · `docs/completion/PLAN.md:95` `new DEFER gaps: 3 (G-19, G-20, G-21 — filed in S5-C)` · `docs/completion/STATUS.md:41` `Open DEFER/S2/S3 items are filed in S5-C` · contrast `:12` `ISSUES: run-3 filing in S5-C` and `:13` `NEXT: S5-B … → S5-C issue filing` · `docs/completion/status.json:653` / `:669` / `:685` `"issue_url": null` |
| **RV-03** | **S2** | **Resume pointers a stranger would follow disagree.** SHIPLOG’s own contract says a zero-context session continues from the header `resume_pointer`. That header is still run-2 `P7/H-07`. Last SHIPLOG line and `status.json` say `P7/GATE`. `run_pr` is still PR **#227** (run 2). T-13 has `"pr": null`. This is the same header-stale trap run 1 already paid for. | `docs/completion/SHIPLOG.md:3` `A future session with zero context continues from \`resume_pointer\`.` · `:13` `resume_pointer: P7/H-07` · `:252` `` `resume_pointer: P7/GATE` `` · `docs/completion/status.json:13` `"resume_pointer": "P7/GATE"` · `:1416` `"run_pr": "https://github.com/ravidsrk/orca-fleet/pull/227"` |
| **RV-04** | **S2** | **A-28 / A-29 / A-30 are split and mislabeled.** `status.json` + STATUS report: A-28 = REPO_PATH, A-29 = claude dir trust, A-30 = grok substrate. Happy file + SHIPLOG call dir-trust **A-28** and grok **A-29**. T-13 note says grok succeeded as **(A-29)**. `ASSUMPTIONS.md` at FETCH_HEAD **ends at A-27** (A-24/A-25 hole already in G-21). R7 says record `A-NN` in `ASSUMPTIONS.md`. | `docs/completion/STATUS.md:27` `A-28 (REPO_PATH=cwd) · A-29 (claude dir trust) · A-30 (grok worker substrate)` · `docs/completion/status.json:1284-1306` (same mapping) · `docs/completion/evidence/CF-05-r3-happy-review-it.txt:21` `worker substrate (A-29): grok 1.0.24` · `:23` `fixed via A-28: trusted the dir` · `docs/completion/SHIPLOG.md:247` `Substrate (A-29): grok` / `A-28; backup` · `docs/completion/status.json:1044` `attempt 4 grok headless succeeded (A-29)` · `docs/completion/ASSUMPTIONS.md:36` last row is A-27 |
| **RV-05** | **S2** | **CF-05 failure “re-confirmed” has no R5 transcript; tools evidence is cited for orca and contains none.** Gate row 2 treats a pre-`orca open` `reachable=false` as run-3 evidence. Frozen CF-05 already says the failure path was captured; the extra “re-confirmed” is a timestamped sentence, not `orca status --json`. SHIPLOG cites `P0-r3-coldstart-tools.txt` for orca CLI + app-not-running; that file is git/python/ruff/greptile/gh/uv/mise/just only. | `docs/completion/STATUS.md:36` `failure path re-confirmed (\`runtime.reachable=false\` before \`orca open\`)` · `docs/completion/evidence/CF-05-r3-happy-review-it.txt:63` `re-confirmed this run before \`orca open\` (… at 2026-09-09T04:38Z)` · `docs/completion/SHIPLOG.md:227` `orca CLI \`/usr/local/bin/orca\`, app not running at start. Evidence \`evidence/P0-r3-coldstart-tools.txt\`.` · `docs/completion/evidence/P0-r3-coldstart-tools.txt:1-26` (no `orca`) · `docs/completion/evidence/P0-r3-coldstart-run.sh:11` toolchain loop omits orca |
| **RV-06** | **S2** | **Bare `eval.py` usage-error recorded as `exit=0`.** Producer pipes through `head -6` then `echo exit=$?`, so the captured status is `head`’s. Run 1 already treated this as an eval-exit lie. SHIPLOG’s `eval.py validate` 37+39 line is separately true (`:9` of the same file). | `docs/completion/evidence/P0-r3-coldstart-eval.txt:2-5` `$ python3 scripts/eval.py (no args = usage)` / `eval.py: error: the following arguments are required: command` / `exit=0` · `docs/completion/evidence/P0-r3-coldstart-run.sh:31` `python3 scripts/eval.py 2>&1 \| head -6; echo "exit=$?"` |
| **RV-07** | **S2** | **One of the three Required findings is registered as S3 “hygiene.”** Aggregate 0C/3R is correct and named (spec F1, spec F2, test-adequacy F1). G-19 ← spec F2 (S2). G-20 ← testadeq F1 (S2). G-21 ← **spec F1 Required** (file-set claim / `playbooks/release.md`) bundled with nits as **S3 DEFER “PR-body file-set lesson.”** Counts are not dropped; weight is. A merged PR body’s false file-set sentence is arguably not a live product defect — the ledger still sells “3 Required → G-19/G-20/G-21” as if they were peer DEFERs. | `docs/completion/evidence/CF-05-r3-happy-review-it.txt:61` `0 Critical, 3 Required … (spec F1, spec F2, test-adequacy F1)` · `docs/completion/evidence/CF-05-r3-axis-spec.md:187` `Required \| **2** \| F1 file-set claim; F2 …` · `docs/completion/GAPS.md:27` `G-21 \| CF-05-r3 spec-F1, standards nits \| … \| S3 \| DEFER \| Ledger hygiene: … PR-body file-set lesson` · `docs/completion/status.json:673-685` G-21 `"severity": "S3"` `"source": ["CF-05-r3 spec-F1", …]` |
| **RV-08** | **S2** | **Angle-1 evidence still points at the superseded run-1 CF-05 file.** CF-05 object correctly names `CF-05-r3-happy-review-it.txt` and says run-1 at `6ad0e87` is superseded. Angle 1’s `evidence[]` still lists only `CF-05-happy-review-it.txt`. P3’s first exit criterion is the same run-1 path. A stranger reading the scorecard, not the CF object, sees the self-review G-16 was opened to replace. | `docs/completion/status.json:38` `"docs/completion/evidence/CF-05-happy-review-it.txt"` · `:346-349` `"happy_evidence": "…/CF-05-r3-happy-review-it.txt"` / `Run-1 evidence at 6ad0e87 superseded.` / `"verified_at": "9e1237f…"` |
| **RV-09** | **S3** | PLAN run-3 P6 line names H-02 and H-04, omits still-open **H-05**. Dispatch record’s successful command is a placeholder (`--task <t>`). P1 JSON cold-start evidence still `P0-coldstart-validate-tests.txt` while PLAN says P1 re-verified via `P0-r3-*` (R4 no-reaudit explains the JSON, not the PLAN/JSON split). | `docs/completion/PLAN.md:84` `H-02 (marketplace), H-04 (About) still human/open` · `docs/completion/HUMAN_ACTIONS.md:20` H-05 `open` · `docs/completion/evidence/CF-05-r3-dispatch-record.txt:1142` `$ orca orchestration dispatch --task <t> --to <shell>` |

---

## What holds (not findings)

- **P0-r3 counts:** `P0-r3-coldstart-tests-run1.txt:24-27` and `…-run2.txt:24-27` — `Ran 329 tests` / `OK` / `exit=0`; no `skipped=` token (unittest would print `OK (skipped=N)`). `P0-r3-coldstart-validate.txt:17-18` — 13 missions, `exit=0`. `P0-r3-coldstart-proof-status.txt:18-22` — doctrine-only 9, self-run 2, external-run 2, total 13, `exit=0`. vf-bench sound false-done `0/11`, valid-control GREEN, `exit=0`. Drift **44/246 = 17.9%** vs `f2e53f4` matches SHIPLOG; R4 no-reaudit is consistent with that arithmetic.
- **0C / 3R arithmetic:** standards summary `0 Critical, 0 Required`; spec `2 Required` (F1, F2); test-adequacy `1 Required` (F1). Happy-path verdict names those three. G-16 closed / H-07 done / T-13 done agree across GAPS, HUMAN_ACTIONS, `status.json` (open gaps: G-09, G-15, G-17, G-19, G-20, G-21 — matches STATUS `:10` S2 3 open / S3 3 open / DEFER 4).
- **Evidence file set:** 11 `P0-r3-*` + 5 `CF-05-r3-*` = 16, as STATUS `:29` says. All 16 exist at `FETCH_HEAD`.
- **H-07 shape:** PR #231 was not authored by run 3; worktree at `6671913`; `review-it` text is post-#225. That is the G-16 re-witness the run-2 fresh review asked for, **if** dispatch settlement is either proven or the overclaim is struck.

---

## Verdict logic vs frozen CF-05 (item 6) — not an R13 rewrite

Frozen line (unchanged; not in the run-3 diff):

> `docs/completion/DEFINITION.md:22` — *With Orca app running: follow getting-started **review-it dry run** to a SHA-bound verdict **(GO or NO-GO both count)**. Happy + one failure (Orca down → documented stop) evidenced. Failure path already captured; **happy path is H-01**.*

Using a **NO-GO** dry run to close CF-05 / H-07 is applying that sentence, not narrowing it. Item 8 is “Orca up + review-it dry run,” not “dry run must be GO.” Required findings were re-entered as G-19/G-20/G-21 and **not** counted complete (STATUS `:41` R13 clause). `DEFINITION.md` was not edited.

**R13:** no lowering of the frozen block. Out-of-scope list, minima, and CF table are the `67c1707` text. Agent-side H-07 (A-30) is a recorded reclassification of *who* starts Orca, not a change to item 8’s action.

**GO vs CONDITIONAL GO:** Phase 7 table is GO iff every gate item is evidenced and no launch-gating Human Action is open. With H-07 `done`, CONDITIONAL GO is the wrong label **if** CF-05 happy-path evidence is accepted. The live defect is RV-01 (the evidence file does not show what the GO reason cites as worker settlement), not a misread of “NO-GO counts.”

---

## Gate table vs frozen items (run-3 rows)

| Frozen # | Run-3 claim | Check |
|---|---|---|
| 1 S0 closed | unchanged **yes** | No S0 in register. |
| 2 every CF happy+failure | CF-05 re-witness **yes** | Happy path = RV-01 bundle. Failure path file still `CF-05-failure-orca-not-running.txt` (allowed by frozen “already captured”); “re-confirmed” is RV-05. |
| 3 fresh clone = CF-01 | P0-r3 **yes** | 329/0-skip/13/9-2-2/exit=0 hold. |
| 4 rollback rehearsal | unchanged **yes** | Not re-run this branch; r2 evidence still on the parent SHA. |
| 5 alert | unchanged **yes** (T-11); frozen text still says “not demonstrated” | Run 2 already treated A-13 as moot without editing DEFINITION. Run 3 did not touch that. |
| 6 Stranger Test | unchanged **yes** | r2 evidence; no re-audit. |
| 7 no ACCEPT at S0 | unchanged **yes** | ACCEPT 0; G-19..21 are DEFER. |
| 8 H-01 / H-07 dry run | H-07 done **yes** | Same RV-01 evidence. |
| minima | unchanged **yes** | Scores not rescored (R4); 68% informational. |

---

run-3 ledger: **8 findings to resolve before sign-off** (RV-01 S1; RV-02..RV-08 S2; RV-09 S3 does not block). Minimum to make GO inspectable: attach actual `worker_done` / task-completed / ack / release receipts (or strike those words), align A-28..A-30 and the SHIPLOG header pointer with `status.json`, and stop saying G-19..G-21 are “filed.”

REVIEW-COMPLETE
