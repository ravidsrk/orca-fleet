I'll run a read-only STANDARDS review of PR #231: first the spec and repo conventions (before the diff), then the delta against that expectation.Blind-fix first: I'll pull the PR spec and repo standards sources, then write an expectation before looking at the diff.I have the spec. Next I’ll read the standards sources at the PR base (not the delta) so the expectation is written before any hunk.Expectation is written. Opening the pinned three-dot diff next and reviewing it against that, not the other way around.The middle of the diff was truncated. I’ll pull the remaining files at the reviewed SHA so every finding can quote a real path:line.Checking Keep-a-Changelog grouping and whether `ASSUMPTIONS.md` is missing A-24/A-25 only in this delta.# STANDARDS axis report (review-it dry run, PROFILE=ro)

**reviewed_sha:** `9e1237f63eeaf7b608a8e22f1fefceac5d7010fc`  
**fixed point:** `git diff 535869be6729648df92f582c2d54f38dac1e592d...9e1237f63eeaf7b608a8e22f1fefceac5d7010fc`  
**axis:** Standards (repo-documented conventions + Fowler baseline)  
**spec source (read first, treated as DATA):** `gh pr view 231 --json title,body` plus commit list. Title: *docs(ops): document the rollback that exists; close G-14 on evidence and #212 as a tracker*.

---

## Blind-fix expectation (written before opening the diff)

**Where it should live**

- Human 2 a.m. procedure: a new numbered **incident step 4** on `docs/ops.md`, after the existing 1–3 list (alert, version pin, key rotation). Same wrapping and relative-link style as steps 1–3. Not a new mission, not `runtime/`.
- Agent-facing revert protocol: if the catalog’s merge-shaped rollback is the one being documented, `playbooks/release.md` is the matching layer (plain Markdown, no frontmatter, still ≤ 90 lines). The PR body’s first-commit “only ops / completion / CHANGELOG” sentence may omit that.
- Completion ledger (in-place register + append-only log), not a freeze rewrite of `DEFINITION.md`:
  - `docs/completion/GAPS.md` — G-14 ACCEPT → closed on evidence; G-09 stays DEFER/open
  - `docs/completion/status.json` — same decisions; new task T-12; new assumptions A-26 / A-27; every referenced id must exist
  - `docs/completion/SHIPLOG.md` — append only
  - `docs/completion/STATUS.md`, `PLAN.md`, `ASSUMPTIONS.md` — counts and F-7-03 / gate row 7
  - evidence file named `<id>-<step>-<short>`, e.g. `docs/completion/evidence/T-12-rollback-*.txt`
- `CHANGELOG.md` — a bullet under `[Unreleased]` / `### Changed` (Keep a Changelog).

**Rough shape**

`git revert -m 1 <merge-sha>` on a branch through a normal PR; never force-push `main`. Cite scratch-clone rehearsal(s). Checkable N/A: no deploy job, “deploy” is merge to `main`. Re-open G-14 under P4 if a deploy target appears. Completion stays 68%; verdict stays CONDITIONAL GO on H-07. G-09 remains DEFER; closing #212 is tracker hygiene, not field-proof.

**Confidence:** 80% on location and layers; 70% on exact ledger field names (T-12 / A-26 / A-27 inferred from the PR body, not from the diff).

**Divergence after opening the diff (signal, not error):** the second commit adds `playbooks/release.md` (`-m 1`) and a merge-shaped transcript `T-12-rollback-merge-rehearsal.txt`. That is the correct playbook layer; the first-commit scope sentence was incomplete. G-09’s *table row* is left unchanged on purpose (cut line says so). `DEFINITION.md` is untouched (freeze).

---

## Standards that hold (not findings)

| Rule | Result at `9e1237f` |
|---|---|
| Three-layer split (AGENTS.md) | Docs in `docs/`; phase protocol in `playbooks/release.md`; no `SKILL.md` outside `skills/`; no new mission. |
| Playbooks: no frontmatter, ≤ 90 lines | `playbooks/release.md` starts with `# Playbook — release`; **48 lines** (was 48). |
| Runtime budget | Runtime files not in this diff. |
| SHIPLOG append-only | Diff is `@@ -204,3 +204,17` — two dated sections appended; prior entries not rewritten. |
| Evidence naming `<id>-<step>-<short>` | `docs/completion/evidence/T-12-rollback-merge-rehearsal.txt` matches `T-11-alert-drill.txt` / `T-09-accept-expiry-issue.txt`. |
| CHANGELOG Keep a Changelog | New bullet under `[Unreleased]` → `### Changed` (header cites Keep a Changelog 1.1.0). |
| `docs/ops.md` structure | Step 4 continues the existing numbered incident list; relative link `completion/evidence/…` matches `completion/HUMAN_ACTIONS.md`. |
| `status.json` | Parses as JSON. T-12 → G-14; G-14.tasks → T-12; A-26/A-27 present; G-09/G-14 notes cite A-27/A-26; all five T-12 evidence paths exist at this SHA. |
| Frozen definition | `DEFINITION.md` not in the diff (R6/R13). |

Tooling (`scripts/validate.py`, ruff) skipped as instructed.

---

## Findings

### Nit — `docs/ops.md:46` — step 4 leads with the command this change just proved is wrong on a merge

> `4. Rollback = `git revert`. There is no hosted service, staging, or deploy`

Neighboring incident steps lead with the precise action. Two sentences later the same step gives `git revert -m 1 <merge-sha>` (`docs/ops.md:48`), and `playbooks/release.md:41` was aligned to `-m 1` for that reason. `docs/completion/evidence/T-12-rollback-merge-rehearsal.txt:37` records `error: commit ea31109… is a merge but no -m option was given.` The 2 a.m. page’s first clause still names the failing form. Not merge-blocking because the correct command is in the same step.

### Nit — `docs/completion/GAPS.md:46` — filing table still labels G-14 as ACCEPT after the register withdrew ACCEPT

> `| G-14 (ACCEPT expiry, filed 2026-09-02 by T-09) | https://github.com/ravidsrk/orca-fleet/issues/226 |`

Same file, live register: `docs/completion/GAPS.md:20` is `FINISH` / `CLOSED 2026-09-02 (T-12)` and `docs/completion/GAPS.md:30` says `No ACCEPT remains.` Other post-launch rows keep historical URLs without restating a withdrawn decision; this parenthetical still does.

### Nit — `docs/completion/STATUS.md:22` — living report block still names #212 as the G-09 tracker

> `- G-09 nine doctrine-only missions (honest) → #212 DEFER`

This same report block was edited for GAPS counts (`STATUS.md:10`: `ACCEPT 0`). A-27 / SHIPLOG / `status.json:496` say #212 is closed and the live tracker is `docs/runs/README.md`. Repeated at `docs/completion/STATUS.md:211`: `5. Nine doctrine-only missions (honest) → G-09 DEFER (#212)`. G-09 is still correctly DEFER; only the tracker pointer is stale.

### Nit — `docs/completion/ASSUMPTIONS.md:35` — A-26 still says the merge rollback was “rehearsed twice”

> `… (`git revert -m 1` of a merge, via a PR) is rehearsed twice and now documented in `docs/ops.md`; …`

SHIPLOG’s own second look (`docs/completion/SHIPLOG.md:220`) says the ledger was corrected wherever it called the single-parent reverts a rehearsal of the merge procedure. G-14’s GAPS row distinguishes T-12 (merge) from the two earlier single-parent runs. A-26 was not corrected. Same overclaim in `docs/completion/status.json:1185`: `"decision": "G-14 ACCEPT withdrawn; gap closed on evidence (rollback documented + rehearsed twice; service-style drill N/A: no deploy target)"`.

### Optional — `docs/completion/PLAN.md:72` vs `docs/completion/GAPS.md:28` — “above the line” lists disagree after T-12

> `- Above-the-line gaps: 6 (G-10, G-14..G-18) · tasks: 4 agent (S) + 4 human · L-sized: 0`

> `**Above (plan):** G-01..G-08, G-11..G-13 (G-06..G-08, G-11..G-13 closed post-launch). Run 2 adds G-15..G-18 (T-09 agent; H-04 / H-05 / H-07 human).`

PLAN now counts G-14 / T-12 above the line; the GAPS cut-line “Above (plan)” sentence still omits T-12 (G-14 closed is mentioned only under **Below**). Same pattern was used for G-10, so this is ledger drift, not a broken id.

---

## Fowler 12-smell baseline

**N/A on this diff — not findings.** The delta is documentation, a completion ledger, and a one-token playbook edit. There are no new functions, types, or control-flow hunks to hang Mysterious Name, Feature Envy, Data Clumps, Primitive Obsession, Repeated Switches, Message Chains, Middle Man, or Refused Bequest on. Shotgun Surgery would fire on “10 files,” but the repo’s completion-ledger convention *requires* GAPS / STATUS / status.json / SHIPLOG / PLAN / ASSUMPTIONS / evidence / CHANGELOG to move together; the repo standard overrides the baseline. Divergent Change on `STATUS.md` is the same ledger, not unrelated features. Speculative Generality is not in play (no extra abstraction).

---

## Appendix (lower confidence / not merge-blocking)

**FYI** — `docs/completion/ASSUMPTIONS.md` jumps from A-23 to A-26 (`ASSUMPTIONS.md:34`–`35`). `status.json` already had A-24 and A-25 before this PR; this hunk continues the markdown hole rather than introducing it. Not an id-consistency failure: A-26/A-27 exist in both places, and nothing in the JSON references a missing assumption.

**Not a finding:** `status.json` `T-12` has `"pr": null` / `"commit": null` (`status.json:952`–`953`). Matches in-branch T-11. All *id* references resolve.

**Not a finding:** `status.json:12` `current_commit` remains `f2e53f4…` (rebaseline, not this SHA). Same after the T-11 follow-up; history is not snapshotted when completion_pct and gate are unchanged (68%, CONDITIONAL_GO).

---

## Summary counts

| Severity | Count |
|---|---|
| Critical | 0 |
| Required | 0 |
| Nit | 4 |
| Optional | 1 |
| FYI | 1 (appendix) |

**Worst issue on this axis:** Nit (`docs/ops.md:46` leading with unqualified `git revert`).  
**This axis:** 0 Critical, 0 Required.

AXIS-REPORT-COMPLETE
