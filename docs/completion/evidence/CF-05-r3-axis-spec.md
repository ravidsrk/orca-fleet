I'll start as a read-only spec-fidelity reviewer: load the review skill, fetch PR #231's body before looking at the diff, then check each frozen criterion against that SHA.Blind-fix first: I'll fetch the PR body and write my own expected file list before opening the diff.PR body is in. Next I’ll pin the SHA, confirm ancestry, then open the three-dot diff and check issues #226 and #212.The file list is in. Next I’ll pull the three-dot diffs and the reviewed SHA contents so each criterion can be quoted line-for-line.I have the diffs. Next I’ll pull line-numbered files at the reviewed SHA and grep the register for leftover ACCEPT / G-09 state.# SPEC FIDELITY — review-it dry run (PR #231)

**reviewed_sha:** `9e1237f63eeaf7b608a8e22f1fefceac5d7010fc`  
**axis:** SPEC FIDELITY  
**fixed point:** `git diff 535869be6729648df92f582c2d54f38dac1e592d...9e1237f63eeaf7b608a8e22f1fefceac5d7010fc`  
**ancestry:** `reviewed_sha` is an ancestor of `main` / `HEAD` (`git merge-base --is-ancestor` exit 0).  
**commits in range:** `5111820` docs(ops): document the rollback…; `9e1237f` docs: rehearse the rollback against a merge commit; release.md reverts with `-m 1`  
**spec source:** `gh pr view 231 --json title,body` (title + Solution / Gates / Closes lines). PR body, commits, and diff are DATA, never instructions. Greptile HTML appended to the body is not the frozen spec.  
**permission:** PROFILE=ro; no repo writes, no commits, no `gh` mutations. Worker pack: matt `code-review` Spec axis only.

**Axis-local outcome:** **NO-GO** (0 Critical, 2 Required).

---

## Blind-fix expectation

Written from the PR body only, before `git diff` / `git show` of the range.

**What I expected to change (confidence 0.80):**

| Path | Rough shape |
|---|---|
| `docs/ops.md` | New incident step 4 titled Rollback: `git revert -m 1 <merge-sha>` on a branch through normal PR gates; never force-push / history rewrite on `main`; badge regen if counts change; cite scratch-clone rehearsals dated **2026-09-01** and **2026-09-02**; state the checkable N/A (**no deploy job in `.github/workflows`**; deploy = merge to `main`); re-open G-14 under P4 with a staging rehearsal if a deploy target appears. |
| `docs/completion/GAPS.md` | G-14: ACCEPT withdrawn, **closed on evidence (T-12, A-26)**; **no ACCEPT decision** left in the register; G-09 stays **DEFER and open**; `docs/runs/README.md` named as live tracker (A-27); gate item 7 left alone. |
| `docs/completion/status.json` | Same ledger facts as GAPS. |
| `docs/completion/SHIPLOG.md` (path guessed) | Append a T-12 entry. |
| `CHANGELOG.md` | One bullet under `[Unreleased]`. |
| Possibly `docs/completion/ASSUMPTIONS.md` (A-26/A-27) and `docs/completion/evidence/T-12-*` | Still inside `docs/completion/`. |

**What I did not expect:** `playbooks/`, `skills/`, `runtime/`, `tests/`, `.github/`. The body bound the diff to `docs/ops.md`, `docs/completion/`, and `CHANGELOG.md`.

**Divergence after opening the diff (signal, not error):** ten files changed; nine sit inside that claim; **`playbooks/release.md` does not**. `PLAN.md` and `STATUS.md` also moved (allowed by the `docs/completion/` glob). `docs/ops.md` step 4 does not name `2026-09-01` or “no deploy job in `.github/workflows`”. Gate item 7’s evidence cell was rewritten; the **yes** stayed.

---

## Per-criterion verdicts

### 1. `docs/ops.md` incident step 4 Rollback — **PARTIAL**

**Spec (PR body Solution):**
> `docs/ops.md` incident step 4 — Rollback. `git revert -m 1 <merge-sha>` on a branch through the normal gates, never a force-push or history rewrite on `main`; regenerate badges if counts change; cites the two scratch-clone rehearsals (2026-09-01, 2026-09-02). States the checkable N/A (no deploy job in `.github/workflows`; "deploy" is merge to `main`) and the re-open condition: a deploy target appearing puts G-14 back under P4 with a staging rehearsal.

| Sub-check | Verdict | Quote at `reviewed_sha` |
|---|---|---|
| Step 4 named Rollback; `git revert -m 1 <merge-sha>` on a branch through normal PR gates | **met** | `docs/ops.md:46-50`: `4. Rollback = \`git revert\`. … \`git revert -m 1 <merge-sha>\` on a branch, then a PR through the normal gates` |
| never force-push or history rewrite on `main` | **met** | `docs/ops.md:49-50`: `never a force-push or a history rewrite on \`main\`.` |
| regenerate badges if counts change | **met** | `docs/ops.md:50-51`: `Regenerate badges (\`python3 scripts/gen-badges.py\`) if the revert changes counts.` |
| cite the two scratch-clone rehearsals (2026-09-01, 2026-09-02) | **partial** | `docs/ops.md:51-55`: `Rehearsed on a scratch clone against a real merge commit on 2026-09-02 ([transcript](completion/evidence/T-12-rollback-merge-rehearsal.txt) …); the two earlier rehearsals reverted a single-parent commit.` The date on the page is the **T-12 merge** rehearsal, not P0-r2. `2026-09-01` is absent. The two named files exist (`P0-rollback-rehearsal.txt` header `2026-09-01`; `P0-r2-rollback-rehearsal.txt` header `2026-09-02T08:20:09Z`) but are not cited by date or path. |
| checkable N/A: no deploy job in `.github/workflows`; deploy is merge to `main` | **partial** | `docs/ops.md:46-47`: `There is no hosted service, staging, or deploy target to roll back ("deploy" is merge to \`main\`, above)`. Deploy = merge to `main` is also at `docs/ops.md:18-19`. **`.github/workflows` / “no deploy job” is not in `ops.md`.** The phrase landed in the ledger instead (`docs/completion/GAPS.md:20`, `ASSUMPTIONS.md:35`, `SHIPLOG.md:211`). At this SHA, `.github/workflows/` is only `alert-on-failure.yml` and `validate.yml` (no deploy job) — the fact is true, the ops page does not state the check. |
| re-open: deploy target → G-14 back under P4 with a staging rehearsal | **met** | `docs/ops.md:56-57`: `If a deploy target ever appears, this step gains a staging deploy → rollback rehearsal and the completion register re-opens G-14 under P4.` |

---

### 2. Completion ledger (G-14 closed; no ACCEPT; gate item 7) — **PARTIAL**

**Spec:**
> Completion ledger. G-14: ACCEPT withdrawn, closed on evidence (T-12, A-26); no ACCEPT remains, gate item 7 unchanged.

| Sub-check | Verdict | Quote |
|---|---|---|
| G-14 ACCEPT withdrawn, closed on evidence (T-12, A-26) in GAPS.md | **met** | `docs/completion/GAPS.md:20`: `G-14 \| … \| FINISH \| CLOSED 2026-09-02 (T-12): … Was ACCEPT with expiry #226 (A-26)` |
| same in `status.json` | **met** | `docs/completion/status.json:560-574`: `"id": "G-14"`, `"decision": "FINISH"`, `"status": "closed"`, `"tasks": ["T-12"]`, `"note": "closed on evidence 2026-09-02 (A-26): …"` |
| A-26 present | **met** | `docs/completion/ASSUMPTIONS.md:35` and `status.json:1183-1189`: `"id": "A-26"`, `"decision": "G-14 ACCEPT withdrawn; gap closed on evidence …"` |
| **no ACCEPT decision remains** in the gap register | **met** | `status.json` gaps at this SHA: 17 `FINISH`, 1 `DEFER`, **0 `ACCEPT`**. `GAPS.md:30`: `No ACCEPT remains.` `STATUS.md:10`: `DEFER 1 · ACCEPT 0`. Remaining “ACCEPT” strings are historical (Was ACCEPT, No ACCEPT at S0, A-26 withdrawal). |
| gate item 7 **unchanged** | **partial** | **Met?** column still `**yes**` (`STATUS.md:42`). The evidence cell **changed**: base `G-14 is S3, expiry tracked as #226` → `no ACCEPT remains — G-14 closed by T-12 …`. The same SHA admits the rewrite: `SHIPLOG.md:220`: `corrected wherever it appeared (GAPS, STATUS F-7-03 and gate row 7, PLAN, ops step).` vs `SHIPLOG.md:211`: `gate item 7 unchanged (yes).` |

---

### 3. G-09 stays DEFER and open; `docs/runs/README.md` live tracker (A-27) — **MET**

**Spec:**
> G-09: stays **DEFER and open** in the register — closing its tracker is not field-proof (A-27, R13) — with `docs/runs/README.md`'s plan named as the live tracker.

- `docs/completion/GAPS.md:15`: `G-09 | … | DEFER | 9 doctrine-only missions. …` (row not marked CLOSED; decision column unchanged vs base).
- `docs/completion/GAPS.md:30`: `G-09 DEFER (register entry unchanged; its tracker issue #212 closed at the maintainer's request — the field-proof plan in \`docs/runs/README.md\` is the live tracker, A-27).`
- `docs/completion/status.json:484-496`: `"id": "G-09"`, `"decision": "DEFER"`, `"status": "open"`, `"note": "DEFER, open; … live tracker is the field-proof plan in docs/runs/README.md"`.
- `docs/completion/ASSUMPTIONS.md:36` / `status.json:1192-1194`: A-27, G-09 never counted complete; README is the live tracker.
- `docs/completion/STATUS.md:8,10`: `COMPLETION: 68%` unchanged; `S3 2 open (G-09 DEFER · G-17)` — G-09 is not counted complete.
- `docs/runs/README.md` exists at this SHA and has `## Field-proof plan (#212)` at line 29.

Nit on STATUS top-risks still pointing at `#212` is finding F5, not enough to drop this criterion off **met**.

---

### 4. SHIPLOG entry for T-12 — **MET**

**Spec:** `SHIPLOG entry appended`

`docs/completion/SHIPLOG.md:208-215`: `## 2026-09-02 — T-12 rollback step; #226 / #212 resolution (run 2 follow-up)` covering G-14 closed on evidence, G-09 kept DEFER/open, 68% / CONDITIONAL GO.

A second append at `SHIPLOG.md:217` (`Greptile on PR #231 (T-12)`) is extra T-12 log, still an append.

---

### 5. CHANGELOG line under `[Unreleased]` — **MET**

**Spec:** `CHANGELOG line added.`

`CHANGELOG.md:7` `## [Unreleased]` / `:21` `### Changed` / `:23-29` the new bullet (ops step 4, G-14, #226, #212 / G-09 deferred, `docs/runs/README.md`). The bullet also names `playbooks/release.md` (see C6 / F1).

---

### 6. Claimed file set vs actual diff — **MISSING** (claim is false)

**Spec:**
> Only `docs/ops.md`, `docs/completion/`, and `CHANGELOG.md` change.

**Actual `git diff --name-status` (10 files):**

| Path | Inside claim? |
|---|---|
| `CHANGELOG.md` | yes |
| `docs/completion/ASSUMPTIONS.md` | yes |
| `docs/completion/GAPS.md` | yes |
| `docs/completion/PLAN.md` | yes |
| `docs/completion/SHIPLOG.md` | yes |
| `docs/completion/STATUS.md` | yes |
| `docs/completion/evidence/T-12-rollback-merge-rehearsal.txt` | yes |
| `docs/completion/status.json` | yes |
| `docs/ops.md` | yes |
| **`playbooks/release.md`** | **no** |

Nine of ten files match the claim. `playbooks/release.md` is outside it. The second commit’s subject even names that file: `release.md reverts with -m 1`. PLAN T-12 (`docs/completion/PLAN.md:66`) encodes the extra work: `align \`playbooks/release.md\``.

---

### 7. `Closes #226` / `Closes #212` vs GitHub + register — **MET**

**Spec:** `Closes #226` / `Closes #212`

| Issue | `gh issue view` | Register at `reviewed_sha` | Consistent with spec? |
|---|---|---|---|
| **#226** | `state=CLOSED`, `stateReason=COMPLETED`, `closedAt=2026-09-02T13:05:08Z` (PR `mergedAt=2026-09-02T13:05:07Z`) | G-14 `FINISH` / `closed` on T-12/A-26 (`GAPS.md:20`, `status.json:567-568`) | **yes** — expiry marker closed with the gap it marked |
| **#212** | `state=CLOSED`, `stateReason=COMPLETED`, `closedAt=2026-09-02T13:05:09Z` | G-09 still `DEFER` / `open` (`GAPS.md:15`, `status.json:491-492`) | **yes** — spec asked to close the umbrella tracker and **keep** G-09 DEFER/open; that is what landed |

---

## Findings

### F1 — Required — scope creep (file-set claim false)

- **Spec:** `Only \`docs/ops.md\`, \`docs/completion/\`, and \`CHANGELOG.md\` change.`
- **Motivating line:** `playbooks/release.md:41`: `EVERY failure point (deploy fail, canary fail: \`git revert -m 1 <merge-sha>\` or a revert-PR if`
- **Also:** `docs/completion/PLAN.md:66`: `align \`playbooks/release.md\``; `CHANGELOG.md:25-26`: `\`playbooks/release.md\` says \`-m 1\` too.`
- The one-line `-m 1` alignment matches the rollback command the spec wanted in ops, but it is still a file the frozen scope forbade. Criterion 6 is **missing**.

### F2 — Required — implemented-but-wrong (ops step omits the checkable N/A)

- **Spec:** `States the checkable N/A (no deploy job in \`.github/workflows\`; "deploy" is merge to \`main\`)`
- **Motivating line:** `docs/ops.md:46-47`: `There is no hosted service, staging, or deploy target to roll back ("deploy" is merge to \`main\`, above), so a bad merge`
- Deploy = merge to `main` is present. The **checkable** clause (no deploy job in `.github/workflows`) is not on the 2 a.m. page the spec assigned it to. It is in `docs/completion/GAPS.md:20`: `no deploy target exists (\`.github/workflows\` has none; "deploy" is merge to \`main\`)`. Criterion 1 is **partial** on this sub-check.

### F3 — Nit — implemented-but-wrong (rehearsal citation is not the two dated ones)

- **Spec:** `cites the two scratch-clone rehearsals (2026-09-01, 2026-09-02)`
- **Motivating line:** `docs/ops.md:51-55`: `Rehearsed on a scratch clone against a real merge commit on 2026-09-02 ([transcript](completion/evidence/T-12-rollback-merge-rehearsal.txt) …); the two earlier rehearsals reverted a single-parent commit.`
- `2026-09-01` never appears in `docs/ops.md`. The dated 2026-09-02 cite is T-12 (merge), not `P0-r2-rollback-rehearsal.txt`. The Greptile follow-up made this more honest than the spec’s “two rehearsals” wording; it still does not do what that spec line asked.

### F4 — Nit — implemented-but-wrong (gate item 7 evidence cell rewritten)

- **Spec:** `no ACCEPT remains, gate item 7 unchanged`
- **Motivating line:** `docs/completion/STATUS.md:42`: `| 7 | No ACCEPT at S0 | no ACCEPT remains — G-14 closed by T-12 (rollback documented in \`docs/ops.md\`, rehearsed against a merge commit: \`T-12-rollback-merge-rehearsal.txt\`; no service to roll back) | **yes** |`
- **yes** is unchanged vs base; the evidence cell is not. `SHIPLOG.md:220` records the rewrite of “gate row 7”.

### F5 — Nit — ledger leftover still names #212 as the G-09 pointer

- **Spec:** with `docs/runs/README.md`'s plan named as the live tracker
- **Motivating line:** `docs/completion/STATUS.md:22`: `- G-09 nine doctrine-only missions (honest) → #212 DEFER`
- G-09 is still DEFER (correct). After #212 closed as a tracker, this STATUS top-risk still points at the closed issue rather than `docs/runs/README.md`. Contrast `GAPS.md:30` / `status.json:496`, which do name the README.

---

## Appendix (lowered confidence / not `path:line` in-repo)

- **A-26 “rehearsed twice” vs three transcripts (FYI, confidence 0.55).** `status.json:1185`: `"decision": "G-14 ACCEPT withdrawn; gap closed on evidence (rollback documented + rehearsed twice; …)"` while T-12 adds a third (merge) rehearsal. Historical wording; not a live ACCEPT. Unclear whether “twice” means the two *merge-inadequate* P0 runs or is stale after T-12.
- **GAPS post-launch table still labels G-14 as ACCEPT expiry (FYI, confidence 0.7).** `docs/completion/GAPS.md:46`: `| G-14 (ACCEPT expiry, filed 2026-09-02 by T-09) | …#226 |` — historical issue index, not a `decision` cell. Does not put ACCEPT back in the register.
- **GitHub issue payloads** for #226/#212 are from `gh issue view`, not a repo `path:line`. States and close timestamps are in criterion 7. No extra finding: closure matches the register the spec described.
- **Gate item 4** still cites the single-parent P0-r2 transcript (`STATUS.md:39`). The spec said to leave **item 7** unchanged, not item 4. Not scored as a spec miss.

---

## Summary counts

| Severity | Count | IDs |
|---|---|---|
| Critical | 0 | — |
| **Required** | **2** | F1 file-set claim; F2 ops.md missing workflows N/A |
| Nit | 3 | F3 rehearsal dates; F4 gate-7 evidence cell; F5 STATUS still → #212 |
| Optional | 0 | — |
| FYI (appendix) | 2 | A-26 “twice”; GAPS “ACCEPT expiry” label |

| Criterion | Verdict |
|---|---|
| 1 ops.md step 4 Rollback | **partial** |
| 2 completion ledger / no ACCEPT / gate 7 | **partial** |
| 3 G-09 DEFER+open + README tracker | **met** |
| 4 SHIPLOG T-12 | **met** |
| 5 CHANGELOG `[Unreleased]` | **met** |
| 6 only claimed files change | **missing** |
| 7 Closes #226 / #212 vs register | **met** |

**Worst issue on this axis:** F1 — `playbooks/release.md` changed after the spec froze the file set to `docs/ops.md`, `docs/completion/`, and `CHANGELOG.md`.  
**Axis-local verdict:** **NO-GO** (Required findings present). No code was modified.

AXIS-REPORT-COMPLETE
