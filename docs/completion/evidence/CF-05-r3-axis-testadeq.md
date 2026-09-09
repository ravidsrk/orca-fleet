I'll follow the review-it dry-run protocol: read the review skill and PR #231 body first, write a blind-fix expectation, then inspect tests and the diff without changing the repo.Blind-fix first: I'll fetch the PR spec and pin the SHA, then write an expectation before looking at the diff.PR spec is in. Next I’ll inventory tests and validators that could bind these docs/ledger claims, still without opening the diff.I'll read the tests and validator that could bind ops, CHANGELOG, playbooks, and completion docs—still without opening the PR diff.Blind-fix expectation is set. Opening the three-dot diff and the validator rules that could actually bind it.The diff is in. I'll pull the truncated hunks and check whether any script actually consumes the completion ledger.# TEST-ADEQUACY (static) — PR #231

- **reviewed_sha:** `9e1237f63eeaf7b608a8e22f1fefceac5d7010fc` (ancestor of current `HEAD`; `git merge-base --is-ancestor` holds)
- **axis:** TEST-ADEQUACY (static) — predicted revert, not executed
- **fixed point:** `git diff 535869be6729648df92f582c2d54f38dac1e592d...9e1237f63eeaf7b608a8e22f1fefceac5d7010fc`
- **commits:** `5111820` (ops + G-14 / #212 tracker) → `9e1237f` (merge-shaped rehearsal; `release.md` `-m 1`)
- **tests/validate.py since SHA:** identical (`git diff 9e1237f..HEAD -- tests scripts/validate.py` empty)
- **permission:** PROFILE=ro; no repo writes; no revert executed

---

## Blind-fix expectation (written from `gh pr view 231 --json title,body` before the diff)

**Spec (PR body, treated as data):** document the rollback that exists as `docs/ops.md` incident step 4 (`git revert -m 1 <merge-sha>` via a gated PR, never force-push); close completion gap G-14 on evidence (T-12, A-26) and withdraw ACCEPT; keep G-09 **DEFER and open** with `docs/runs/README.md` as live tracker (A-27, R13); append SHIPLOG + a CHANGELOG line. Claimed gates: `python3 scripts/validate.py`, `python3 -m unittest discover -s tests`, `ruff check scripts runtime/scripts tests bench demo`. Body also says “Only `docs/ops.md`, `docs/completion/`, and `CHANGELOG.md` change.”

**What a test or gate *could* bind (pre-diff):**

| Claimed change | Could bind? | Why |
|---|---|---|
| `docs/ops.md` rollback step | Weakly | `test_ops_doc_names_accounts_and_incident` only pins `GitHub` / `plugin marketplace` / `greptile` / `agentskills` / `Incident`. Adding rollback prose while keeping those tokens → revert stays green. Bind only if those tokens were newly added or deleted. |
| `CHANGELOG.md` bullet | Weakly | `test_plugin_version_matches_changelog_heading` matches the first dated `## [X.Y.Z] - ` heading vs `plugin.json`. An `[Unreleased]` bullet is invisible to that regex. Bind only if a new dated heading became the first match. |
| `playbooks/release.md` (named in the PR’s Greptile summary, denied by the “only …” sentence) | Weakly | `test_promotion_names_accountable_human` (`accountable:`) and `test_per_unit_flag_is_build_done_not_built` (`\bBUILT\b`); `validate.py` playbook line/byte cap (90) and `md_ref_errors`. A `git revert` → `git revert -m 1` edit binds none of those unless it drops the tokens, exceeds 90 lines, or adds a dangling `<name>.md`. |
| `docs/completion/**` (G-14 close, G-09 note, SHIPLOG, GAPS, PLAN, STATUS, `status.json`, T-12 transcript) | No | `tests/` and `scripts/validate.py` never mention `status.json`, GAPS, SHIPLOG, ASSUMPTIONS, G-14, or G-09. |
| `docs/runs/README.md` / `TEMPLATE.md` (named as G-09 live tracker) | Index only | `test_run_archive_index_lists_every_report` links dated `2*.md` reports; it does not assert a field-proof plan table. |
| Claimed gates | Parse-only | `validate.py` checks skills / playbook-runtime refs / evals / instruction budget — not docs claims. `ruff` is Python-only. |

**Confidence:** 0.85 that the claimed content (`-m 1`, G-14 close, G-09 tracker) is UNBOUND and that the listed gates only prove the catalog still parses.

**Post-diff vs expectation:** matched. Divergence (signal, not error): `playbooks/release.md` *is* in the diff (the “only …” sentence was false); a T-12 merge-rehearsal transcript was added; `status.json` grew a `note` key. None of those created a binding.

---

## Per-file bound / unbound

Judged at `reviewed_sha`. “BOUND-BY” means reverting *this hunk* would go red. A test that opens the file and asserts a different token is not a binding.

| File | Verdict | Matters? | Quote |
|---|---|---|---|
| `playbooks/release.md` | **UNBOUND** | **Yes.** Callable playbook. The second commit exists because plain `git revert` is rejected on a merge. | Diff: `EVERY failure point (deploy fail, canary fail: \`git revert -m 1 <merge-sha>\` or a revert-PR if` (`playbooks/release.md:41`). Tests that open the file: `self.assertIn("accountable:", release)` (`tests/test_architecture.py:287`); `self.assertRegex(release, r"\bBUILT\b", …)` (`tests/test_architecture.py:407-408`). Gate: `PLAYBOOK_MAX_LINES = 90` (`scripts/validate.py:93`); file is 48 lines, 1:1 edit. `md_ref_errors` walks playbooks (`scripts/validate.py:426-443`); this hunk adds no `<name>.md` token. Predicted revert of `-m 1` → suite still green. |
| `docs/ops.md` | **UNBOUND** | **Docs claim — normally expected.** Exception: a test already pins this 2 a.m. section and ignores the new step. | Diff: `is undone the way it landed: \`git revert -m 1 <merge-sha>\` on a branch,` (`docs/ops.md:48`). Test: `for tok in ("GitHub", "plugin marketplace", "greptile", "agentskills", "Incident"):` (`tests/test_docs_navigation.py:57-58`). Parent already had `## Incident (2 a.m.)`. Revert of the 12 added lines keeps every token. |
| `CHANGELOG.md` | **UNBOUND** | No. Unreleased prose. | Added under `## [Unreleased]` / `### Changed` (`CHANGELOG.md:7`, `CHANGELOG.md:23-29`). Test: `r"^## \[(\d+\.\d+\.\d+)\] - "` (`tests/test_docs_navigation.py:43`). First dated heading remains `## [0.6.0] - 2026-09-01` (`CHANGELOG.md:85`); `plugin.json` is `0.6.0`. Revert of the bullet does not change the match. |
| `docs/completion/status.json` | **UNBOUND** | **Yes, moderately.** Structured register: G-14 `decision`/`status` flip plus a new `note` key. No Python consumer. | `"id": "G-14"` … `"decision": "FINISH"` … `"status": "closed"` (`docs/completion/status.json:560,567-568`). G-09: `"note": "DEFER, open; tracker issue #212 closed … live tracker is the field-proof plan in docs/runs/README.md"` (`docs/completion/status.json:496`). `rg 'status.json' --glob '*.py'` → no hits. Revert of the close / `note` / T-12 / A-26 / A-27 objects → still green. |
| `docs/completion/GAPS.md` | **UNBOUND** | Same ledger family as `status.json`; prose twin, no parser. | `\| G-14 \| … \| FINISH \| CLOSED 2026-09-02 (T-12): rollback = \`git revert -m 1\` …` (`docs/completion/GAPS.md:20`). `**Below:** … G-14 closed 2026-09-02 (T-12). No ACCEPT remains.` (`docs/completion/GAPS.md:30`). |
| `docs/completion/ASSUMPTIONS.md` | **UNBOUND** | No. Decision log. | A-26 / A-27 rows (`docs/completion/ASSUMPTIONS.md:35-36`). |
| `docs/completion/PLAN.md` | **UNBOUND** | No. | T-12 row (`docs/completion/PLAN.md:66`); count line `Above-the-line gaps: 6 (G-10, G-14..G-18)` (`docs/completion/PLAN.md:72`). |
| `docs/completion/SHIPLOG.md` | **UNBOUND** | No. Append-only narrative. | `## 2026-09-02 — T-12 rollback step…` (`docs/completion/SHIPLOG.md:208`); Greptile follow-up naming the `-m 1` miss (`docs/completion/SHIPLOG.md:219`). |
| `docs/completion/STATUS.md` | **UNBOUND** | No. Human report. | `ACCEPT 0` (`docs/completion/STATUS.md:10`); gate row 7 rewrite (`docs/completion/STATUS.md:42`); F-7-03 now says `git revert -m 1` (`docs/completion/STATUS.md:145`). |
| `docs/completion/evidence/T-12-rollback-merge-rehearsal.txt` | **UNBOUND** | No as a *test* (it is evidence, not a gate). It *is* the negative control the suite never encoded. | `error: commit ea31109fac8628e2aa391b32768deed1d0805a67 is a merge but no -m option was given.` (`docs/completion/evidence/T-12-rollback-merge-rehearsal.txt:37`) `fatal: revert failed` / `exit=128` (`:38-39`). Deleting the file fails nothing; `status.json` lists the path (`:957`) with no existence check. |

**Not in the diff (named by the PR / grep request):**

| Path | Role | Bound? |
|---|---|---|
| `docs/runs/README.md` | Claimed G-09 live tracker (`## Field-proof plan (#212)`, `docs/runs/README.md:29`) | `test_run_archive_index_lists_every_report` only requires `({f.name})` for dated `2*.md` reports (`tests/test_docs_navigation.py:83-87`). Deleting the field-proof table would stay green. `TEMPLATE.md` is linked from that section (`docs/runs/README.md:32`) and is not tested as a G-09 tracker. |

---

## Claimed gates vs this diff

PR body:

```
python3 scripts/validate.py            # All 13 missions valid; three-layer separation holds; evals valid.
python3 -m unittest discover -s tests  # OK (skipped=1: shallow clone; CI runs it)
ruff check scripts runtime/scripts tests bench demo   # All checks passed
```

| Gate | Does it exercise the changed content? |
|---|---|
| `scripts/validate.py` | **No.** Header: “Three things are checked:” (1) mission SKILL.md, (2) three-layer + protocol `<name>.md` refs, (3) evals (`scripts/validate.py:5-37`). `docs/` and `CHANGELOG.md` are outside that walk. The only touched gated file is `playbooks/release.md`: line/byte budget (`scripts/validate.py:444-455`) and `md_ref_errors` (`:442-443`). Predicted revert of `-m 1` trips neither (48 lines, no new `.md` token). A green validate after this PR proves 13 missions still parse, not that rollback is documented. |
| `unittest` | **Opens 3 of 10 files; ignores the delta.** `test_ops_doc_names_accounts_and_incident` (`tests/test_docs_navigation.py:54-59`) does not include `Rollback`, `revert`, or `-m 1`. `test_plugin_version_matches_changelog_heading` (`:42-51`) ignores `[Unreleased]`. `test_architecture.py:287` / `:407-408` ignore the revert command. Zero tests mention `docs/completion`, G-14, G-09, or `git revert`. `rg 'revert -m 1\|git revert' tests/` → no matches. |
| `ruff` | **No.** Diff is Markdown + one `.txt`. Ruff targets (`scripts runtime/scripts tests bench demo`) contain none of the 10 files. |

A green suite on this SHA is **not** test-adequacy evidence for the claimed fixes. It is evidence the catalog still parses.

---

## Findings

### F1 — Required — claimed `-m 1` playbook fix is UNBOUND

Reverting `playbooks/release.md:41` from `` `git revert -m 1 <merge-sha>` `` back to `` `git revert <merge-sha>` `` is predicted to leave `validate.py`, unittest, and ruff green. That line is the fix the second commit was written to land.

Motivating lines:

```
playbooks/release.md:41
EVERY failure point (deploy fail, canary fail: `git revert -m 1 <merge-sha>` or a revert-PR if
```

```
docs/completion/SHIPLOG.md:219
Two findings, both valid and fixed: (1) `playbooks/release.md` still said `git revert <merge-sha>`, which Git rejects on a merge commit — now `-m 1`;
```

```
docs/completion/evidence/T-12-rollback-merge-rehearsal.txt:37-39
error: commit ea31109fac8628e2aa391b32768deed1d0805a67 is a merge but no -m option was given.
fatal: revert failed
exit=128
```

```
tests/test_architecture.py:287
self.assertIn("accountable:", release)
```

The suite already reads this playbook and pins other tokens. The T-12 transcript *is* the negative control (plain revert → exit 128) and was never turned into an assertion. `tests/` contains no `revert` / `-m 1` string.

### F2 — Nit — `ops.md` 2 a.m. step 4 is UNBOUND under the test that already owns that section

Unchecked docs claims are normally fine. Here the file already has a contract test for the 2 a.m. incident surface, and the PR’s own problem statement is that rollback was “documented nowhere a maintainer would look at 2 a.m.” Step 4 was appended; the token list was not.

```
tests/test_docs_navigation.py:54-59
def test_ops_doc_names_accounts_and_incident(self):
    # Issue #215: bus-factor-1 with no inventory and no 2 a.m. paragraph.
    text = (DOCS / "ops.md").read_text(encoding="utf-8")
    for tok in ("GitHub", "plugin marketplace", "greptile", "agentskills",
                "Incident"):
        self.assertIn(tok, text, f"docs/ops.md lost its {tok!r} surface")
```

```
docs/ops.md:48
is undone the way it landed: `git revert -m 1 <merge-sha>` on a branch,
```

Predicted revert of lines 46–57 keeps `Incident` and every other token. The repo’s own rule for this class of test: “A doc surface that presents itself as complete must be machine-checked against repo state, or it silently rots” (`tests/test_docs_navigation.py:5-6`).

### F3 — Nit — completion ledger close of G-14 / G-09 tracker note is UNBOUND

`status.json` is the machine-shaped register. This diff changes G-14 from ACCEPT/open to FINISH/closed, adds a `note` key (schema extension), and records T-12 / A-26 / A-27. Nothing in `tests/` or `scripts/` parses it. GAPS.md / STATUS.md / SHIPLOG.md can diverge from the JSON with a green suite.

```
docs/completion/status.json:567-568
"decision": "FINISH",
"status": "closed",
```

```
docs/completion/status.json:496
"note": "DEFER, open; tracker issue #212 closed at the maintainer's request (A-27) — live tracker is the field-proof plan in docs/runs/README.md"
```

No `*.py` reference to `status.json` exists. This is not a runtime schema, so not Critical/Required; it is more than an unchecked changelog bullet.

### F4 — FYI — claimed gates are parse-coverage, not criterion coverage

```
scripts/validate.py:5-7
Three things are checked:
1. Every mission (skills/<name>/SKILL.md) is a valid agentskills.io skill:
```

None of those three things is “rollback is `-m 1`” or “G-14 is closed.” Unittest skipped=1 is the pre-existing vf-bench shallow-clone skip, unrelated to this diff.

---

## Appendix (lowered confidence)

- **G-09 “live tracker” vs `docs/runs/README.md`:** the plan table exists at `docs/runs/README.md:29` (`## Field-proof plan (#212)`) and was not modified in this PR. No finding that the table is missing. Finding that *claims about it* in the ledger are untested sits in F3. Not a separate defect.
- **PR body “Only `docs/ops.md`, `docs/completion/`, and `CHANGELOG.md` change”** vs a 10-file diff that includes `playbooks/release.md`: spec-axis, not test-adequacy. Noted as blind-fix divergence only.
- **Gate item 4 in STATUS.md still cites the single-parent rehearsal** (`P0-r2-rollback-rehearsal.txt`, `docs/completion/STATUS.md:39`) while F-7-03 was corrected to the merge-shaped T-12. Consistency nit for spec/standards, not a missing test.

No unquotable high-severity claims.

---

## Summary

| | n |
|---|---|
| Files in diff | 10 |
| BOUND-BY for the claimed hunk | **0** |
| UNBOUND | **10** |
| UNBOUND and it matters (playbook command / ledger) | 2 (`playbooks/release.md`, `docs/completion/status.json`) |
| UNBOUND and normal for docs | 8 |
| Critical | 0 |
| Required | **1** (F1) |
| Nit | 2 (F2, F3) |
| Optional | 0 |
| FYI | 1 (F4) |
| Worst on this axis | **Required** — predicted revert of the `-m 1` playbook fix stays green |

Blind-fix held: the gates named in the PR body do not bind the criterion the PR claims to have closed.

AXIS-REPORT-COMPLETE
