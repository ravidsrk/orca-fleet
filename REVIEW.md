# REVIEW.md — deep review of ravidsrk/orca-fleet

Reviewed SHA: `2a9cb3a7dae6ccac4d6bb426bdbb24d8a8301d27` (`main`, 2026-09-10, merge of PR #277).
Every `file:line` below is at that SHA. Read-only engagement: nothing in the repository was changed
except this file. Every injection ran in a scratch clone; every attack was executed, not reasoned
about. External research was fetched on 2026-09-10 and is listed in §13.

**This file replaces the previous deep review of `af8ea89`/`9afefc6`, which occupied this path.**
That review is preserved in git at `git show 2a9cb3a:REVIEW.md`. Twenty-seven tracked files cite it
as `REVIEW.md §N` / `REVIEW.md A10` — among them `runtime/scripts/verify.py:74,150,430`,
`spawn_worker.sh:206`, `scripts/bundle.py:9`, `tests/test_verify.py`, `evals/routing.json` and
`bench/vf-bench/traps/*.json`. Those anchors now point at a document that no longer sits here.
Re-pointing them is a maintainer edit this engagement has no authority to make; it is P1 item 17.
Attack ids A1–A11, B1–B2, D1, E1–E2 and U1–U5 belong to the predecessor and are not reused: new
ids start at A12, B3, D1b, E3 and U6.

---

## 1. Verdict

**NO-GO for "the claim is checked by mechanism, outside the run that made it"
(`README.md:33-34`) as a claim about the protocol.**
**GO for the three legs that carry it: the frozen denominator, real commits, and a GitHub review
bound to the head tree.**

The predecessor review found the negative control was never executed. It is executed now. The
executor is real: a throwaway worktree at `head_sha`, the control applied, the bound command
required to exit non-zero there and zero clean, fail-closed on a tool it cannot replay. The
positive control passes and the gate is not always-RED.

What it does not do is bind the control to the change. The paths reverted, the diff applied, and
the command run are all chosen by the graded worker, and the ledger that is supposed to constrain
the command is a JSON array the worker writes. Nine attacks landed against the executed control,
five of them in the very lane the README calls the whole oracle, two against the strongest
configuration the repository documents. A unit whose only change is a comment and whose only test
asserts `True` passes. A control that restores the test file instead of the fix passes. A mutant
that makes the module unimportable passes. A "criterion-bound proof command" of `grep -q FIXED
calc.py` passes, and so does `sh -c 'echo … > /outside/file; grep -q FIXED calc.py'`, which the
verifier then executes twice with its own privileges.

The proof-status gate has the same shape one level up. A fabricated `map-it` self-run — seven
files, thirty-two inserted lines, one commit, under fifteen minutes — is reported "bound" by
`run_report.py`, passes `validate.py`, `proof_status.py --check` and all 782 tests. The gate proves
that named artifacts existed at a commit the author made and that the report's prose contains a
plausible command line. `run_report.py:33-38` says plainly that it never re-runs the verifier;
`README.md:150-151` says a tier "is a report that **re-derives**". The second sentence is not true
of the first mechanism.

The catalog's honesty is therefore the maintainer's, not the gate's. Twenty-one missions read
`doctrine-only` because the maintainer refused to claim more, and a maintainer who wanted to claim
more could, cheaply. That is worth saying because the repository's entire thesis is that the
opposite should be true.

Claim the mechanism supports today: *scope frozen against a coordinator-held digest, commits real
on the intended base, review looked up on GitHub and bound to the head tree, and a negative control
whose shape the verifier replays but whose content the worker chooses.*

---

## 2. Executive summary — the five findings that matter

1. **The executed negative control is worker-designed end to end.** `negative_control.paths`, the
   `hand` diff, and the command all come from the manifest; the `commands[]` ledger that is supposed
   to constrain the command is written by the worker too (`verify.py:512-576`, `:596-680`;
   `evidence-run.py:122-141`). Nine of thirteen gaming manifests went GREEN, including a decoy
   revert of the test file, a stillborn mutant, a `grep`, and a tautology unit (§4.1, A12–A22).
2. **A proof tier can still be typed.** B3: a fabricated run report binds, and the three tests that
   noticed were prose-consistency checks satisfied by editing one number, one callout and one index
   row (§4.2). The gate is artifact-existence plus a regex, and `run_report.py` says so; the README
   does not.
3. **Seven runtime mechanisms exist, are tested, pass CI, and are invoked by nothing.**
   `guard_text.py`, `decisions.py`, `floor_guard.py`, `diff_scope.py`, `egress.py`, `deny-hook.sh`,
   `dispatch-sign.py`: zero references across all 21 missions and all 28 playbooks. The commit that
   added them is titled "eight mechanisms the catalog stated only as prose"; the catalog still states
   them only as prose. `guard_text.py:55-56` cites a contract test that does not exist (§3.1, §11.1).
4. **The verifier executes worker-chosen argv on the verifier's host** (`verify.py:537`, `:731`,
   600-second budget), before any other check can refuse the manifest, on exactly the CI, SDK and
   coordinator surfaces the design calls sound — the machines that hold `gh` credentials and, where
   signed dispatch is enabled, the dispatch seed (§4.1 A15, §11.3).
5. **The `danger` sandbox requirement is a `grep`.** `ORCA_SANDBOX_RECIPE=root
   ORCA_SANDBOX_DOCTOR=/etc/passwd` spawns a `danger` worker; a realistic doctor transcript with
   `"failures": []` is refused because the word matches. The recipe is never passed to Orca, so no
   honest transcript places anything in a VM (`spawn_worker.sh:205-237`, `:381`; §11.2).

---

## 3. Rubric and scores

Fourteen criteria, weights summing to 100, each with the pass bar it was scored against. The
grounding for each bar is in §10 (verification literature), §7 (competitive landscape), §9
(agentskills.io spec) and §11.6 (Orca). Score is 0–10.

| # | Criterion | Weight | Pass bar | Score | Evidence |
|---|---|---|---|---|---|
| 1 | Evidence legs are mechanism, not prose | 15 | Every guarantee the README leads with maps to a check that goes RED on the gaming trap | 4 | §3.1: 12 of 31 mechanism, 4 of those qualified; the lead leg is advisory |
| 2 | Negative-control soundness (Lipsitch 2010 U-comparability; pseudo-tested methods; mutant sampling) | 12 | The control is bound to the change: production paths only, a behaviour-preserving mutant, a failure signature from the criterion-bound assertion | 2 | 9 of 13 gaming manifests GREEN (§4.1); no test exercises a decoy path, oracle mutation, stillborn mutant or grep |
| 3 | Verifier independence (Knight–Leveson; AI-control trusted vs untrusted monitoring) | 8 | Deterministic verdict path plus a named mitigation for same-family monitoring (honeypots, redaction, cross-vendor default) | 5 | Deterministic verifier is the right shape and holds; the LLM leg has none of the three mitigations, and the judgment legs are the doctrine ones (§10) |
| 4 | Proof-status honesty is machine-checked | 8 | An unearned tier cannot pass CI without evidence the author could not type | 3 | B3 landed in 15 minutes; `run_report.py` is honest about this, `README.md:150-151` is not |
| 5 | Run-report integrity (SHAs, PRs, hashes resolve) | 6 | Every referenced SHA, PR and hash resolves on a full clone | 7 | All resolve, including 5/5 ship-it hashes at `748b328`; 18 prose errors (§12.3) |
| 6 | Catalog identity test enforced | 7 | Two missions that are the same work fail the build; the test resists paraphrase | 5 | Executable and green, but a one-word edit defeats it for 125 of 126 values (§4.4 D3b); 20 of 21 stand on the merits |
| 7 | Routing clarity (no sibling collision) | 7 | ≥90% on realistic prompts, with a margin that a rewording cannot flip | 6 | 60 of 64 accepted, but 17 decided under 0.05 and the collision gate cannot fire (§5) |
| 8 | agentskills.io conformance | 5 | The reference validator passes; repo claims live under `metadata` | 9 | All 21 pass `skills-ref` 0.1.1, CI runs it; one description has angle brackets (§9.1) |
| 9 | Portability / self-containment | 6 | A mission survives the install path the README recommends | 6 | `bundle.py` is real and CI-checked; `npx skills add` as printed still severs every reference (§9.2) |
| 10 | Instruction budget / progressive disclosure | 5 | One mission loads ≤5,000 tokens with references behind a cue | 4 | Measured, capped and published — at 15,374–33,850, and ~39,800 end to end (§9.3) |
| 11 | Supply-chain drift | 5 | Every hard dependency pinned, with a check that detects drift | 6 | `pins.json` + SHA-pinned actions and gitleaks; nothing compares an installed binary (§11.5) |
| 12 | Security / injection surface | 7 | Untrusted text is fenced by mechanism; privileged lanes require evidence a liar cannot produce | 3 | Fence unwired; danger lane forgeable; verifier runs worker argv (§11) |
| 13 | Doc truthfulness | 5 | Zero false factual claims in the human docs | 5 | 6 new false or misleading claims here, 18 more in the run archive (§12) |
| 14 | Mechanisms are reachable from the missions that need them | 4 | Every shipped mechanism is invoked by the doctrine whose guarantee it carries | 2 | 7 orphans; `preflight.py` (18 refs) and `verify.py` (8) are the exceptions |
| | **Weighted total** | **100** | | **45 / 100** | |

### 3.1 Mechanism vs doctrine — every guarantee the README makes

Four classes, defined so the table can be re-derived by anyone with the tree:

- **Mechanism** — a script, hook, or CI step goes RED when the guarantee is violated, and the input
  it reads is not authored by the party being graded.
- **Advisory** — a check exists, but the graded party authors the input it reads (a worker-written
  ledger, a worker-chosen path or diff, a worker-set environment variable). The check catches honest
  mistakes, not a worker that wants credit.
- **Orphan** — a script exists, has tests, and passes CI, but no mission, playbook, hook, or CI step
  invokes it against a run. The guarantee holds only if a coordinator remembers the script exists.
- **Doctrine** — prose an agent under context pressure can skip.

| # | README guarantee (line at `2a9cb3a`) | Where it lives | Class | Why |
|---|---|---|---|---|
| 1 | Scope frozen against a coordinator-held digest the worker cannot shrink (`README.md:37-38`) | `verify.py:275-307` `check_scope`, `:172-192` `read_source` | **Mechanism**, two holes | Sound when the coordinator supplies `path@ref` off-worker. A16: a criterion written as a table row or after an em dash is invisible to `CRIT_ID_RE` (`:76-77`), so scope shrinks by formatting. A8: a bare path is read from the working tree (`:186-192`) |
| 2 | Commits are real on the intended base (`README.md:38-39`) | `verify.py:314-330`; `:908-917` | **Mechanism** (existence) / **Advisory** (base) | Existence is checked; "on the intended base" is a NOTE unless `--base` is passed, and no mission passes it |
| 3 | Review looked up on GitHub, bound to the head tree (`README.md:39`) | `verify.py:434-494`, `:352-365`, `:368-382` | **Mechanism** | Holds, including author-exclusion and superseded reviews. Waived in the two lanes where the control becomes the whole oracle (row 4) |
| 4 | The negative control is executed: revert or re-apply in a fresh worktree, require RED (`README.md:39-41`, `:328-332`) | `verify.py:683-753`, `:512-576`, `:596-610`, `:636-680` | **Advisory** | The worktree, the two runs and the RED-then-GREEN rule are real. Every input is worker-authored: `paths` (A13), the `hand` diff (A14), the ledger the command must appear in (A12, A15). `--nc-command` binds the command only, never the control (A13b, A14b). Opt-in (`verify.py:1064-1066`; `verify-gate.sh:101`), mandatory only in the waiver lanes, and named by no mission or playbook |
| 5 | Clean-env re-run at head; ≥10% re-execution sample of controls (`README.md:42-43`) | `evidence-manifest.md:119,121`; `ship-it:108-109`; `clean-sweep:92-93` | **Doctrine** | The README says so itself. No script, no ledger field, no run report has ever recorded a sample |
| 6 | Tests really ran on this content (`evidence-manifest.md:118`) | `verify.py:811-848`; `evidence-run.py` | **Advisory** | `{cmd, cmd_sha256, exit, wtree}` in the worker's own manifest; `wtree` is computable by the worker. A24 shows a miscomputed tree is caught; a correctly typed one is indistinguishable from a run — the positive control P1 was produced with a hand-typed ledger |
| 7 | Every mission is one outcome; six-point identity test (`README.md:106-107`, `:222-228`) | `validate.py:731-776` | **Mechanism** (gameable) | Identical tuples fail (D3). Six one-word paraphrases pass (D3b): the threshold defeats "same" at one substituted word for 125 of 126 live values |
| 8 | `autonomy:` validator-enforced (`README.md:135`) | `validate.py:479-483` | **Mechanism** (legality only) | Any of L0–L5 passes; the derivation is prose — and correct prose (§10.4) |
| 9 | A proof tier is "a report that re-derives" (`README.md:149-154`) | `run_report.py:111-221`; `validate.py:445-475`; `validate.yml:39` | **Mechanism** (self-consistency only) | B3. The gate proves artifacts existed at a commit the author made; `run_report.py:33-38` states it never re-runs `verify.py`, and the transcript leg is a regex over prose (`:68-79`) |
| 10 | Coordinator never writes code; workers never coordinate (`README.md:232`) | `sandbox-policy.md`; `spawn_worker.sh` | **Doctrine** | `PROFILE=ro` is a real flag, but no mission names `spawn_worker.sh` |
| 11 | Wrong-base detection, BASE ≠ default; FAQ "No" (`README.md:270-272`, `:545-548`) | `preflight.py`, named in 16 missions | **Mechanism if invoked** | The check is real; invocation is a sentence. Nothing stops an `rw` worker (`--dangerously-skip-permissions`) pushing to the default branch; `deny-hook.sh` could refuse it and is unregistered by construction (row 27). The FAQ's categorical "No" is doctrine |
| 12 | Reviewed-SHA freshness; a rebase voids the review (`README.md:273-274`) | `verify.py:333-344`; `merge-serialization.md:33-37` | **Mechanism** (manifest) / **Doctrine** (conductor) | A5 in the predecessor still holds: forged `reviewed_wtree` is caught because both trees are recomputed |
| 13 | One merge train, arrival order (`README.md:275-276`) | `merge-serialization.md:15-24` | **Doctrine** | The policy says it of itself: "the rule stands on our discipline alone" |
| 14 | Attention budget ≤3 builders (`README.md:277-278`) | `attention-budget.md:8,30` | **Doctrine** | Marked ASSERTED in its own header; zero protocol-compliant rows in six run reports |
| 15 | Liveness and resume re-verify every completed unit against git (`README.md:279-282`) | `liveness-resume.md:149-151` | **Doctrine** | No script performs the cross-verify; `inventory.py check` exists and no mission names it |
| 16 | Gates below the model; one-way doors human, never defaulted (`README.md:283-286`) | `gate-classification.md`; `decisions.py` | **Orphan** | `decisions.py` refuses a one-way line without `source=human:` and blocks reclassification by wording — exactly the mechanism the guarantee needs — and is invoked by 0 missions, 0 playbooks, 0 hooks |
| 17 | Units default lit; dark-eligible narrow (`README.md:285-286`) | `verify.py:943-959`; `gate-classification.md:58-76` | **Mechanism** (legality + swap) / **Doctrine** (eligibility) | The Lane-A / unfakeable-oracle / stop-list conditions are a human gate the verifier never sees |
| 18 | Least-privilege workers; `danger` only in a disposable sandbox (`README.md:287-288`) | `spawn_worker.sh:205-237` | **Advisory** + **Orphan** | The flag map is mechanism on the `ro` lane. The sandbox evidence is a file the coordinator names; the recipe never reaches Orca (§11.2). No mission names `spawn_worker.sh` |
| 19 | Manifest binds every claim to a SHA and an artifact (`README.md:323-337`) | `verify.py:930-940`, `:208-243` | **Mechanism** (presence, pinning) / **Advisory** (truth) | Pinning proves the file did not change after the worker hashed it, not that its content is true |
| 20 | Only `skills/` holds a SKILL.md (`README.md:352-355`) | `validate.py:596-620` | **Mechanism** (tracked files) | D1: five leaks caught. D1b: an untracked one is not (`git ls-files` scope). D2: a playbook given frontmatter passes every gate |
| 21 | Every composition resolves; ≥1 machine-checkable composition; line, byte and load caps (`README.md:493-497`) | `validate.py:512-537`, `:540-570`, `:125-135`, `:636` | **Mechanism** | Holds. The load cap caught a 4-line playbook edit during D2 through the badge check |
| 22 | A symlink install carries the gate once the snippet is merged (`README.md:88-98`) | `print-settings-snippet.sh`; `verify-gate.sh:74-88` | **Mechanism if wired** | E3: the snippet resolves. E1: `Stop` with `ORCA_MANIFEST` unset exits 0 by design, so a worker that never names a manifest ends every turn ungated; `TaskCompleted` blocks (E1b) |
| 23 | Copy installers get a bundled tree (`README.md:412-426`) | `scripts/bundle.py`; `validate.yml:44` | **Mechanism** for `dist/`; the README's own command is broken | `npx skills add ravidsrk/orca-fleet` (`:408-409`) installs from the repository root and severs every reference (§9.2) |
| 24 | One router per worker (`README.md:57-61`, `:539`) | `compatibility:` strings | **Doctrine** | Nothing observes what a worker mounts |
| 25 | Gated sequential chains (`README.md:177-179`) | `mission-chaining.md` | **Doctrine** | No ledger field, no script |
| 26 | Untrusted target-repo text is data, never instructions (`sandbox-policy.md:112-120`) | `guard_text.py` | **Orphan** | The fence exists and is tested; 0 missions, 0 playbooks, `pm.py` and `spawn_worker.sh` invoke it. Every worker reads issue and PR text raw |
| 27 | Read-write workers are denied out-of-worktree writes and the Never list | `deny-hook.sh` | **Orphan** by construction | The script prints a registration a host must paste; nothing registers it and, on the supervised lane, nothing can |
| 28 | Egress receipts; floor guard against bar-lowering diffs; diff-scoped lens gating (`README.md:125`; `risk-review.md:13-20`) | `egress.py`, `floor_guard.py`, `diff_scope.py` | **Orphan** | floor-it describes "`check_constraints`-style validation" (`:85-88`) and never names `floor_guard.py`; risk-review gates lenses by prose and never names `diff_scope.py` |
| 29 | Signed dispatch makes substitution detectable (`docs/verify-gate.md:157-205`) | `verify.py:1005-1061`; `dispatch-sign.py` | **Mechanism off-worker** / **Orphan** in practice | Sound where the key is off-worker, as the doc says. No mission or playbook signs a dispatch; no `.orca/dispatch-pubkey` is committed, so the check never runs |
| 30 | No credential reaches the evidence; secret scan in CI | `verify.py:869-905`; `validate.yml:68-107` | **Mechanism** | Holds; the CI canary is a real negative control on the baseline waiver |
| 31 | "No mission clears that bar today" (`README.md:156`) | `proof_status.py` | **True** | 21 / 0 / 0 at HEAD |

Twelve mechanism (four qualified), five advisory, six orphan, eight doctrine. Of the four legs the
opening paragraph leads with — frozen scope, real commits, GitHub review, executed control — three
hold and the fourth, the one the paragraph calls the edge, is advisory.

---

## 4. Bypass log

Method. A scratch clone at `2a9cb3a` supplied `verify.py`. A separate target repository was built
with a base commit (a bug in `calc.py`, a characterization test asserting the bug), a head commit
(the fix, two criterion tests, one new test module), and a frozen contract committed at base and
passed as `contract.md@<base>` with its real digest. Every manifest field a worker writes was
written by the "worker"; every flag a coordinator passes was passed on the command line, in the lane
the doctrine names. Harness: `scratchpad/harness.py`; results `harness-results.json`.

### 4.1 The executed negative control

All runs use `--contract-source contract.md@<base> --contract-digest <real> --unit-class mutation
--execute-nc` plus the lane flag shown. The positive control ran first.

| ID | Attack | Lane | Outcome | Anchor |
|---|---|---|---|---|
| P1 | Real fix, real criterion test, `revert` control on `calc.py`, ledger typed by hand | dark-eligible | **GREEN (exit 0)** — the gate is not always-RED | `verify.py:683-753` |
| A12 | Worker nominates `grep -q FIXED calc.py` as the criterion-bound command by writing its own `commands[]` record (`exit: 0`, `wtree` = head tree, correct `cmd_sha256`) | dark-eligible | **LANDED** — no test ever runs | `_nc_command` `verify.py:557-569` |
| A13 | `negative_control.paths = ["tests/test_calc.py"]`: the control restores the **test** file, so the old characterization test fails against the fixed code | dark-eligible | **LANDED** — the oracle was mutated, the fix never touched | `_apply_control` `verify.py:639-651` |
| A13b | A13 with the coordinator supplying `--nc-command "python3 -m unittest tests.test_calc"` | dark-eligible + `--nc-command` | **LANDED** — the override binds the command, never the paths | `verify.py:544-555` |
| A14 | `tool: hand`, artifact quotes a diff inserting `sys.exit(1)` at the top of `calc.py` — a stillborn mutant every command dies on | dark-eligible | **LANDED** | `verify.py:668-680`, `_extract_diff:613-633` |
| A14b | `tool: hand`, the quoted diff changes the test's expected value (`4`→`5`), coordinator `--nc-command` supplied | dark-eligible + `--nc-command` | **LANDED** — the "mutant" is in the oracle | same |
| A15 | The nominated command is `sh -c 'echo verifier-ran-my-code > <path outside the worktree>; grep -q FIXED calc.py'` | dark-eligible | **LANDED**, and the file was written: the verifier executed worker-chosen shell with its own privileges | `_run_at` `verify.py:500-509`; `NC_TIMEOUT_S = 600` |
| A21 | Unit whose only production change is a comment and whose only test is `assertTrue(True)` in a **new** module; `revert` with no `paths` (range fallback) | dark-eligible | **LANDED** — the range revert removes the module, the command fails with ImportError, RED "as required" | `verify.py:652-667` |
| A16 | Frozen contract carries `AC-1`, `AC-2` as list items, `AC-3` as a table row, `AC-4` after an em dash; the worker addresses two | dark-eligible | **LANDED** — `extract_criterion_ids` returns two ids | `CRIT_ID_RE` `verify.py:76-77` |
| A22 | `--no-gh` lane: worker-written `review.txt` containing `head_sha`, plus the A12 grep control | `--no-gh` | **LANDED** with a NOTE | `check_review` `verify.py:459-476` |
| A24 | Sanity: ledger record with a wrong `wtree` | dark-eligible | **CAUGHT** exit 2 | `verify.py:579-593` |
| A25 | Lit lane, `gh` absent, `pr.number` set | default | **CAUGHT** exit 2 (fail-closed) | `verify.py:477-484` |
| A26 | dark-eligible with a control that was merely read (no `--execute-nc`) | dark-eligible | **CAUGHT** exit 2 — the 2026-09-10 waiver-lane fix holds against text | `verify.py:427-457` |
| A27 | `tool: mutmut` under `--execute-nc` in the waiver lane | dark-eligible | **CAUGHT** exit 2 — unreplayable tools fail closed | `verify.py:697-701` |
| A28 | Report-only unit: every criterion `addressed: true`, no commands, no artifacts | report-only | **LANDED by design** — source-binding of quoted lines is doctrine | `evidence-manifest.md:146-149` |
| A29 | Planning unit with `head_sha: "HEAD"` | planning | **LANDED by design** — symbolic refs are NOTE-only off the mutation class | `verify.py:314-323` |
| A8 (re-run) | Bare working-tree path as `--contract-source`, contract edited to drop `AC-2` | report-only, worker sets env | **LANDED**, as documented for the in-session lane | `read_source` `verify.py:186-192` |

Tally: 9 LANDED, 2 landed by design, 4 CAUGHT, 1 positive control GREEN. Five of the nine land in
the lane the README calls the whole oracle; two land against the strongest documented configuration;
one is a security hole rather than a soundness gap.

What the pattern says. The executor checks that *something the worker chose* makes *a command the
worker chose* exit non-zero, then zero. It never checks that the thing reverted is the production
change, that the command exercises the criterion, or that the mutant is behaviour-preserving rather
than stillborn. Those are the three conditions the literature names as necessary for a kill to mean
anything (§10), and `prove-it`'s own doctrine names them too — "A revert that breaks compile/imports
proves source-SHAPE dependence, not behavior — does not count" (`skills/prove-it/SKILL.md:58-59`) —
while the mechanism that grades `prove-it` accepts exactly that. The test suite mirrors the gap:
`tests/test_verify.py` has a tautological-control test (`:1141`), a fabricated-diff test (`:1240`)
and an unreplayable-tool test (`:321`), and no test where the control is a decoy path, an oracle
mutation, a stillborn mutant or a grep. The suite's own standard — "every guard must be demonstrably
capable of failing" (`CONTRIBUTING.md:118-120`) — is met for the shapes the predecessor review found
and not for the class the guard exists to refuse.

### 4.2 Proof-status honesty

| ID | Attack | Outcome | Anchor |
|---|---|---|---|
| B3 | Fabricated `docs/runs/2026-09-10-map-it-self-run.md`: a `RUN:` header naming a commit I made, a 6-line `manifest.json` and a 2-line `frozen-map.md` in the run's own directory, an inventory of their real hashes, and a typed transcript (`$ python3 runtime/scripts/verify.py --manifest …` / `verify: OK` / `$ echo $?` / `0`) that was never run; `skills/map-it/SKILL.md` set to `proof: self-run` | **LANDED**: `validate.py` OK, `proof_status.py --check` exit 0 (rollup 20/1/0), `run_report.py` "bound map-it (self-run)", routing 86/86, bundle OK; 3 of 782 tests red, all prose-consistency | `run_report.py:68-79`; `:33-38` |
| B3c | The three prose surfaces edited to agree: one count in `docs/distribution.md`, one Proof callout in the mission guide, one row in the run index | **LANDED**: 782/782 OK, `ruff` clean, every gate in `validate.yml` green. Cost: 7 files, 32 insertions, one commit | — |
| B4 | The same report relabelled `tier=external-run`, `proof: external-run` | **LANDED**: "bound map-it (external-run)"; nothing checks that an external target exists | `run_report.py:129-137` |

What the gate proves: that a report's named artifacts existed, byte for byte, at a commit that
exists in the repository, and that the prose contains the verifier's name with the right argument.
What it cannot prove: that a run happened, that `verify.py` was executed, that its exit code was what
the prose says, or that any worker, worktree or Orca session ever existed.

### 4.3 Doctrine wiring of the verifier itself

`grep -rn -- "--execute-nc|--nc-command|--contract-source|evidence-run.py|--dispatch-record"
skills/ playbooks/` returns nothing. `grep -rn "verify.py" skills/ playbooks/` returns four prose
mentions and no invocation. `ship-it` says "the coordinator verifies each against authoritative state
(evidence-manifest.md) before advancing" (`skills/ship-it/SKILL.md:95-97`); the flags live one hop
away in a 160-line runtime table the coordinator must translate into a command line with nine
optional flags. The one place the invocation is written out is `docs/runs/TEMPLATE.md:61-76`, a
human document. So even where the mechanism is sound, whether it runs at all — and in which lane —
is doctrine.

### 4.4 Three-layer separation and the catalog gates

| ID | Injection | Outcome | Anchor |
|---|---|---|---|
| D1 | Tracked `SKILL.md` at `playbooks/x/`, `docs/`, `skills/ship-it/sub/`, `skills/`, `.claude-plugin/` | **CAUGHT** — all five listed | `validate.py:596-620` |
| D1b | Untracked `playbooks/y/SKILL.md` | **LANDED** locally (scan is `git ls-files`); harmless in CI, live on a symlinked checkout | `validate.py:579-593` |
| D2 | `playbooks/record-decision.md` given `name:`/`description:` frontmatter | **LANDED** — validator OK, 782 tests OK | `AGENTS.md:110-111` |
| D3 | `skills/ship-it-2/` as a verbatim copy | **CAUGHT** — identity, description collision, keyword and eval-name checks, four independent reds | `validate.py:764-769` |
| D3b | The six identity points paraphrased one word at a time (`slice`→`increment`, `landed`→`merged`, …) | **LANDED** past the identity test; still caught by the description cosine | `validate.py:716` |

D3b is the one that matters: the executable identity test is a duplicate-string detector. A real
second mission with its own description and a paraphrased tuple passes, so "two missions declaring
the same six fails the build" (`AGENTS.md:107`) is true only of copy-paste.

### 4.5 The native gate and the install paths

| ID | Probe | Outcome |
|---|---|---|
| E1 | `verify-gate.sh --event stop`, `ORCA_MANIFEST` unset | exit 0 by design — a worker that never names a manifest is never gated on `Stop` (`verify-gate.sh:77-79`) |
| E1b | `--event task`, unset | exit 2 (blocks) |
| E3 | `hooks/print-settings-snippet.sh --check` from a symlinked clone | resolves; the snippet is correct |
| E4 | `npx skills add` of one mission from the repository root | `../../playbooks` and `../../ARCHITECTURE.md` absent after install |
| E5 | `claude plugin install` from the marketplace manifest | the whole repository lands in the plugin cache; references resolve |
| E6 | `skills-ref` 0.1.1 on all 21 frontmatters | valid; an injected top-level `proof:` fails as CI expects |
| E7 | Anthropic `quick_validate.py` (the `package_skill.py` / claude.ai upload path) on a clean `ship-it` | **rejected**: "Description cannot contain angle brackets" — `build me <feature>` (`skills/ship-it/SKILL.md:9`) |

### 4.6 Untestable here

| ID | Guarantee | Why | What would make it testable |
|---|---|---|---|
| U6 | Clean-env suite re-run at `head_sha` | no script, no ledger field, no run-report row | a `commands[]` record written by the coordinator's own runner in a fresh worktree, signed with the dispatch key |
| U7 | ≥10% control re-execution sample | no script, no record in any of the six run reports | a sampled `--execute-nc` invocation recorded per run with its selection seed |
| U8 | Verifier independence (a different session) | needs a live Orca; the shipped hook runs inside the worker's session | a run report whose verifier transcript names the verifying terminal's dispatch id |
| U9 | Deployed revision equals reviewed revision | no deploy surface in the catalog's own runs | — |
| U10 | One pack per worker | nothing records what a worker mounted | a signed `pack:` field in the dispatch record |
| U11 | Attention-budget caps | ASSERTED by their own header; zero protocol rows in six reports | three runs at differing WIP, as the policy specifies |
| U12 | `danger` runs only in an ephemeral sandbox | the doctor transcript is a file the coordinator names (§11.2) | a sandbox id verified live against the recipe at spawn |

---

## 5. Collision matrix and eval results

### 5.1 What the router under test is

`scripts/eval.py` scores a prompt by stemmed TF-IDF cosine against each mission's real
`description` (name ×2, the "Use when" segment ×3, the "Not for" segment ×−0.5, `:317-324`), with an
absolute evidence floor of 0.30 (`:282-284`) that yields `none`, alphabetical tie-break, and a
pairwise description-cosine gate at 0.50 warn / 0.75 error (`:346-359`). The keyword table and the
specialist override the predecessor review criticized are gone. The file says of itself that it is
not the router any host uses (`:3-8`); Claude Code routes by the model reading the same
descriptions. So the score measures lexical separability of the catalog text — a necessary condition
for a model router, not the thing itself.

At HEAD: `eval.py run --suite all` 86/86 (71 positive, 14 negative, 1 none), 63 per-skill evals;
`--threshold 1.0` passes; CI gates on it (`validate.yml:31`). All 36 realistic prompts from the
predecessor review are fixtures (ids 101–136), 13 of them as `expected_any`.

### 5.2 The matrix

Sixty-four prompts: the 44 the brief specified plus 20 written to make siblings collide. Analyst
predictions were written to a file before the router ran (`scratchpad/routing/predictions.json`,
19:01 UTC; first router call 19:02). "Collision" means the top-two margin is under 0.05, where one
word flips the answer.

| # | Prompt | Analyst | Router (score) | Runner-up | Margin | Class |
|---|---|---|---|---|---|---|
| P01 | the README lies | clean-sweep | clean-sweep (0.233) | — | — | OK |
| P02 | why is this flaky | root-cause / deflake-it | deflake-it (0.428) | — | — | OK |
| P03 | make CI strict | floor-it | floor-it (0.283) | deflake-it 0.092 | 0.191 | OK |
| P04 | this breaks on mobile | field-test-it | field-test-it (0.161) | speed-it 0.123 | 0.038 | COLLISION |
| P05 | our tests are flaky and I want to know why | deflake-it / root-cause | deflake-it (0.318) | prove-it 0.142 | 0.175 | OK |
| P06 | the login page is slow on mobile | speed-it | speed-it (0.323) | — | — | OK |
| P07 | review this PR for accessibility problems | review-it | review-it (0.283) | access-it 0.176 | 0.107 | OK |
| P08 | harden the CI pipeline | harden-it / floor-it | harden-it (0.204) | speed-it 0.119 | 0.085 | OK |
| P09 | update the README to match the code | clean-sweep | clean-sweep (0.125) | modernize-it 0.103 | 0.022 | COLLISION |
| P10 | upgrade React and fix what breaks | modernize-it | modernize-it (0.116) | — | — | OK |
| P11 | refactor the payments module safely | reshape-it | reshape-it (0.448) | — | — | OK |
| P12 | add tests before we refactor payments | prove-it | prove-it (0.105) | oncall-it 0.093 | 0.013 | COLLISION |
| P13 | we need SOC 2 evidence for our CI security gates | attest-it | attest-it (0.248) | floor-it 0.186 | 0.062 | OK |
| P14 | make the checkout accessible and fast | chain / access-it / speed-it | speed-it (0.149) | access-it 0.127 | 0.022 | COLLISION |
| P15 | close the open issues about performance | speed-it / clean-sweep | speed-it (0.239) | clean-sweep 0.205 | 0.034 | COLLISION |
| P16 | diagnose why the deploy failed last night | root-cause | root-cause (0.107) | — | — | OK |
| P17 | ship the feature and make sure it works on a real phone | chain / ship-it / field-test-it | field-test-it (0.387) | ship-it 0.251 | 0.136 | OK |
| P18 | our Orca docs are out of date | pin-it / clean-sweep | clean-sweep (0.368) | document-it 0.309 | 0.059 | OK (pin-it 3rd) |
| P19 | plan the migration to the new auth provider | map-it | map-it (0.154) | migrate-it 0.087 | 0.067 | OK |
| P20 | is this branch safe to merge | review-it | review-it (0.096) | — | — | OK |
| P21 | remove the god object in the API layer | reshape-it | reshape-it (0.064) | document-it 0.060 | 0.004 | COLLISION |
| P22 | find and fix all secrets in the repo | harden-it | harden-it (0.106) | root-cause 0.082 | 0.025 | COLLISION |
| P23 | the dependency audit has 40 findings, fix them all | modernize-it / clean-sweep | modernize-it (0.251) | harden-it 0.106 | 0.145 | OK |
| P24 | cover the untested payment paths and fix the bugs you find | prove-it | prove-it (0.192) | root-cause 0.151 | 0.041 | COLLISION |
| P25 | why does the build fail only in CI | root-cause | root-cause (0.181) | ship-it 0.172 | 0.009 | COLLISION |
| P26 | set a coverage floor and enforce it | floor-it | floor-it (0.343) | document-it 0.088 | 0.255 | OK |
| P27 | prove our app meets WCAG for the audit | access-it / attest-it | access-it (0.129) | attest-it 0.116 | 0.013 | COLLISION |
| P28 | submit fixes to the upstream library we depend on | oss-contribute | oss-contribute (0.291) | — | — | OK |
| P29 | make this production-ready | chain | none | — | — | OK (by design) |
| P30 | this test passes locally but fails in CI | root-cause / deflake-it | deflake-it (0.127) | prove-it 0.111 | 0.015 | COLLISION |
| P31 | the API contract drifted from the docs | clean-sweep | clean-sweep (0.408) | document-it 0.398 | 0.010 | COLLISION |
| P32 | kill the retry wrappers and make the suite deterministic | deflake-it | deflake-it (0.352) | — | — | OK |
| P33 | chart a plan for the mobile rewrite | map-it | map-it (0.284) | pin-it 0.079 | 0.206 | OK |
| P34 | our quality bar keeps slipping — fix the bugs it let through | floor-it / clean-sweep | floor-it (0.379) | root-cause 0.101 | 0.278 | OK |
| P35 | Orca updated and the emulator QA flow broke on device | pin-it / field-test-it | field-test-it (0.487) | pin-it 0.076 | 0.411 | OK |
| P36 | red team the checkout on a real device | harden-it / field-test-it | field-test-it (0.402) | harden-it 0.099 | 0.302 | OK |
| P37 | merge the 14 open community PRs | absorb-it | absorb-it (0.325) | oss-contribute 0.182 | 0.143 | OK |
| P38 | the public API has no reference docs | document-it | document-it (0.551) | clean-sweep 0.266 | 0.285 | OK |
| P39 | we had an outage and nobody could tell what was happening | oncall-it | oncall-it (0.132) | root-cause 0.055 | 0.077 | OK |
| P40 | rename the users.email column without downtime | migrate-it | migrate-it (0.329) | — | — | OK |
| P41 | move from Postgres 12 to 16 | modernize-it / migrate-it | **review-it** (0.071) | — | — | **FP** |
| P42 | split the monolith's billing module out behind an interface | reshape-it | reshape-it (0.333) | migrate-it 0.048 | 0.285 | OK |
| P43 | add alerts for the checkout service | oncall-it | oncall-it (0.338) | — | — | OK |
| P44 | the docs say the endpoint returns JSON but it returns XML | clean-sweep | **document-it** (0.161) | clean-sweep 0.122 | 0.039 | **FN** |
| S01 | review and merge the contributor PRs on our fork | absorb-it | absorb-it (0.373) | oss-contribute 0.240 | 0.133 | OK |
| S02 | close every open PR against our repo | absorb-it | **oss-contribute** (0.284) | absorb-it 0.176 | 0.108 | **FN** |
| S03 | send our fixes for the open issues upstream and merge what we can | oss-contribute | oss-contribute (0.575) | clean-sweep 0.160 | 0.415 | OK |
| S04 | the docs are wrong and half the API isn't documented at all | chain / clean-sweep / document-it | document-it (0.318) | clean-sweep 0.194 | 0.124 | OK |
| S05 | write docs for the CLI and fix the ones that are wrong | document-it / clean-sweep | document-it (0.264) | clean-sweep 0.192 | 0.072 | OK |
| S06 | we were blind during the incident — figure out what actually broke | root-cause / oncall-it | oncall-it (0.199) | — | — | OK |
| S07 | the alerts didn't fire during last night's outage, why? | root-cause / oncall-it | oncall-it (0.190) | — | — | OK |
| S08 | migrate the orders table to the new schema | migrate-it | migrate-it (0.441) | document-it 0.069 | 0.372 | OK |
| S09 | get off the deprecated ORM without breaking the schema | modernize-it | **migrate-it** (0.148) | modernize-it 0.068 | 0.080 | **FN** |
| S10 | split the users table without downtime | migrate-it | migrate-it (0.507) | — | — | OK |
| S11 | the coverage gate keeps failing on flaky tests | deflake-it / floor-it | deflake-it (0.249) | prove-it 0.217 | 0.032 | COLLISION |
| S12 | enforce 80% coverage on the money paths | floor-it / prove-it | floor-it (0.193) | prove-it 0.176 | 0.018 | COLLISION |
| S13 | check the new modal for screen reader problems | access-it | access-it (0.181) | document-it 0.070 | 0.111 | OK |
| S14 | is the new checkout diff WCAG compliant? | review-it / access-it | review-it (0.148) | access-it 0.099 | 0.050 | COLLISION |
| S15 | prove our security scanning gates fire for the auditors | attest-it / floor-it | floor-it (0.163) | harden-it 0.101 | 0.062 | OK |
| S16 | audit the supply chain against NIST SSDF | attest-it / harden-it | attest-it (0.320) | harden-it 0.167 | 0.153 | OK |
| S17 | the runtime guides say otherwise — our dispatch docs are wrong | pin-it | pin-it (0.512) | document-it 0.185 | 0.327 | OK |
| S18 | our docs about how dispatch works are stale | pin-it / clean-sweep | pin-it (0.250) | document-it 0.245 | 0.004 | COLLISION |
| S19 | build the camera feature and verify it on hardware | chain / ship-it / field-test-it | ship-it (0.295) | field-test-it 0.126 | 0.169 | OK |
| S20 | the fix works on desktop but not on the emulator, ship it once it works on device | field-test-it / ship-it | field-test-it (0.525) | ship-it 0.125 | 0.400 | OK |

Sixty of 64 in the analyst's accepted set (43 clear, 16 by a hair, 1 `none` by design); 1 false
positive; 3 false negatives. On the predecessor's 36 prompts the description router scores 36/36
against the keyword router's 19/36 — and 12 of those 36 are decided by under 0.05.

### 5.3 What the numbers mean

- **The collision gate cannot fire on this catalog.** The worst description pair is clean-sweep ↔
  document-it at 0.214 against thresholds of 0.50 and 0.75; the median pair is 0.011. Descriptions
  are 100–150 tokens and prompts are 3–10, so two descriptions can be globally dissimilar while
  fighting over the two tokens a prompt contains. The instrument CI gates on measures the wrong
  quantity for the failure it is named for.
- **The catalog's own trigger phrases route to siblings.** Of 119 quoted "Use when" phrases fed back
  one at a time, four route elsewhere: attest-it "conformance" → access-it; clean-sweep "fix this
  broken test" → prove-it; floor-it "stop shipping junk" → ship-it; root-cause "why is this
  happening" → oncall-it (by 0.0006, because `why`, `is`, `this` are stopwords, so the prompt is the
  single stem `happen`). Four more win by under 0.05.
- **One root cause for most fixable rows.** Six descriptions (review-it, root-cause, harden-it,
  map-it, prove-it, clean-sweep) carry exclusions not phrased as "Not for" after a period, so the
  splitter (`eval.py:95`) counts them as triple-weighted triggers. That is P41: review-it wins "move
  from Postgres 12 to 16" on the word *move*, from "an attached request to fix what you find does not
  **move** the verdict", while both analyst missions score 0.0.
- **Structural collisions** — docs wrong vs missing vs stale-mechanics (clean-sweep / document-it /
  pin-it); a flaky failure vs a flaky suite; compound asks that are chains by the repo's own
  doctrine; coverage floor vs coverage proof; "open PRs" as verb vs adjective. A bag of words cannot
  resolve these, and the descriptions already carve them in prose a model can read.
- **Fixture fragility.** Fifteen of the 86 live fixtures are decided by under 0.05 (id 121 by
  0.0036), and on 7 of the 13 `expected_any` rows the second named sibling is not the actual
  runner-up — an unlisted third mission is. A sibling swap on exactly the colliding pairs is
  invisible to CI.

### 5.4 Does "one router per worker" hold?

The claim (`AGENTS.md:79-86`) is about co-mounted upstream pack routers and is not contradicted. The
phenomenon it names — trigger phrases fought over — recurs one level up between the 21 missions, and
the repository has no instrument at the granularity where it happens: routing is asserted at the
pack level, measured at the description level (inert) and at 86 fixed wordings (15 by a hair).
Closing the gap is cheap: a minimum top-two margin on positive fixtures (0.05 flags 15 rows today),
a cap on `expected_any`, a probe of every quoted trigger phrase in `validate` (4 of 119 fail now),
and for the structural pairs a host-level test where the model reads the catalog.

---

## 6. Catalog verdict — 21 missions under the six-point test

### 6.1 Is the test enforced?

Partly, and for the wrong thing. `tests/test_architecture.py` asserts only that each SKILL.md has a
"convergence proof" heading and an `## Anti-patterns` section (`:92-102`); it never mentions
identity. The executable test is `validate.py:731-776`: six declared `metadata:` values per mission,
and a pair scoring Jaccard ≥ 0.85 on all six fails the build, five of six warns. At HEAD all 210
pairs score 0 of 6; the highest single-point Jaccard is 0.375 (clean-sweep vs oss-contribute,
`state_machine`), and the WARN branch is unreachable. So the test certifies that no two tuples are
near-copies. D3b shows what it does not certify: pluralising one word turns a verbatim duplicate
into a legal WARN, a second one-word edit silences the validator, and the arithmetic
(J = (n−r)/(n+r)) means one substituted word defeats "same" for 125 of the 126 live values. The unit
tests exercise identical tuples and whole-sentence replacements, never a paraphrase. The judgment
the test was meant to replace is still editorial; what follows is that judgment, applied against the
repository's own rule that "two workflows that differ ONLY in oracle are one mission with an
`oracle=` source, and they differ as missions only when the oracle changes the convergence proof's
shape or the parking classes" (`ARCHITECTURE.md:42-46`).

### 6.2 The 21, adversarially

| Mission | Unit | Convergence | Oracle | Verdict |
|---|---|---|---|---|
| ship-it | slice of the frozen spec | every slice at the integrated head, at the highest authorized release state | suite + real entry point | stands |
| clean-sweep | one finding (audit / tracker / doc-claims) | re-enumeration dry, final tip green | repo suite, RED on revert | stands (the reference shape) |
| harden-it | one threatened invariant + its class | fresh full audit, zero unrefuted P0/P1 | a working exploit | stands |
| speed-it | one hotspot under a budget | metric contract with confidence | measurement contract | stands |
| modernize-it | one compatibility-graph node | every node current or pinned | suite green at the upgraded tip | stands; its description still says "expand/migrate/contract at the code level" (`README.md:115`) while its declared state machine does not, and it hands forced data migrations to ship-it and never names migrate-it (`SKILL.md:38-42`, `:106`) |
| prove-it | one critical-path behaviour | every path's mutant KILLED | a behaviour-changing mutation | stands |
| deflake-it | one intermittent failure distribution | streak local and CI at one SHA | measured repeat-run rate | stands |
| review-it | one finding at a reviewed SHA | every axis reported, verdict SHA-bound | the diff, read-only | stands |
| map-it | one decision ticket | verified frozen DAG | the frozen map re-verifies | stands |
| root-cause | one falsifiable hypothesis | one survivor with a falsification table | red-capable reproduction | stands |
| oss-contribute | one upstream issue to an opened PR | frozen issues PR-opened-and-followed | upstream CI + maintainers | stands (the proof shape genuinely differs: opened, never merged); its guide still says "five-part mission test" (`docs/missions/oss-contribute.md:30`) |
| attest-it | one obligation from a frozen standard | every obligation dispositioned | an independent re-derivation | stands |
| access-it | one success-criterion violation on a frozen surface | oracle clean on the frozen surface | axe-core, incomplete by construction | stands under point six: the oracle's ~30–40% ceiling makes a standing human-AT park the normal terminal, a parking class clean-sweep lacks, and `CONFORMANT` is "near-unreachable" by its own text |
| field-test-it | one device-observed defect | re-verified on the target at head_sha | the device session, tiered | stands, narrowly: the tier ladder ("never verified on a weaker tier") is a parking dimension clean-sweep lacks |
| pin-it | one runtime-mechanics claim | every claim receipted or refuted | the installed binary | **fold** → `clean-sweep source=runtime-doctrine oracle=orca-binary`, with the enumerate-and-replay recipe as a `re-witness` playbook. `ARCHITECTURE.md:73-77` argues the proof "inverts" because the refutation archive is "a terminal class clean-sweep lacks". It is the same shape with the labels swapped: pin-it's REFUTE is clean-sweep's real-finding path for `source=doc-claims` ("a false claim IS a finding … correct/remove", `skills/clean-sweep/SKILL.md:66-68`), and pin-it's CURRENT-with-receipt is clean-sweep's `refuted` class. Convergence is "every enumerated item dispositioned, re-enumerate" in both. What remains is the oracle and the enumeration source — which is exactly what the repo's own rule calls an `oracle=` source. Keeping it requires amending the rule, not re-arguing the mission |
| floor-it | one constraint dimension | every dimension's gate fails on a deliberate violation | the CI gate, proven by a violation | stands; the "coverage" collision with prove-it is real (§5) and its guard script is an orphan |
| reshape-it | one module-deepening at one seam | every seam deepened, net green before and after | the characterization net | stands as a mission; **refactor**: CHARACTERIZE restates prove-it's mutation recipe inline (`:76-82` vs `prove-it:54-61`) and points at it by a path inside a code block the validator exempts. Two copies of one recipe drift; the three-layer answer is a shared `characterize` playbook both compose — not a chain link, since the repo is right that the net must be live at reshape-it's own head |
| migrate-it | one migration phase of one table | parity probe + zero old-shape readers, per phase | data parity, never the suite | stands (the oracle changes the proof shape) |
| oncall-it | one path × its on-call questions | every question answered by a quoted signal | a source-blind worker locating an induced failure | stands |
| absorb-it | one inbound PR (someone else's diff) | every PR absorbed, refuted, or parked with a named ask | the contributor's claim reproduced | stands (no build-change; a park class addressed to an external human); clean-sweep's nearest sibling on both instruments |
| document-it | one (entity × quadrant) cell | every frozen gap filled, every claim anchored | rename-to-RED claim check | stands (the complement of `clean-sweep source=doc-claims`); the catalog's worst routing pair |

**Verdict: 20 stand, 1 folds (pin-it), 1 refactor (reshape-it's CHARACTERIZE into a shared
playbook), no splits.** The predecessor review called for three merges; the sixth identity point
that `ARCHITECTURE.md` added carries access-it and field-test-it on their parking classes, which is a
real argument. It does not carry pin-it, because pin-it's parking classes map onto clean-sweep's
one for one. ship-it's release machine is already a playbook four missions run once per phase;
`playbooks/release.md:28-31` introduces a "Doc-sync unit" that is not ship-it's declared unit, which
is a wording defect, not a split.

### 6.3 What the catalog's growth is doing

The predecessor warned that 17 would become more; four landed the same day it went to zero proven,
and the identity test became executable as the counter-pressure. §6.1 shows the counter-pressure is
a duplicate detector. The real discipline is the one the README already states and no mechanism
checks: a mission needs a field-proof plan and a run. Eight of 21 have neither (§12.2), including
all four new ones. A test requiring a plan row before a mission may enter `skills/` would cost an
afternoon and do more than the tuple check.

---

## 7. Competitive position

Seven packs cloned on 2026-09-10: mattpocock/skills v1.2.3 `3cca18b`; garrytan/gstack 1.84.1.0
`71f6048e`; addyosmani/agent-skills 0.6.9 `6ca0cd7`; anthropics/skills `41bbe19`; obra/superpowers
6.3.0; boshu2/agentops 3.6.0 `322f94e`; EveryInc/compound-engineering 3.24.0. Every "negative
control", "revert", "fail open" and "fingerprint" hit in each was read, not counted.

### 7.1 The README paragraph, sentence by sentence (`README.md:29-45`)

| Claim | Status today |
|---|---|
| gstack carries a content-hash evidence ledger | Accurate: `bin/gstack-evidence` + `bin/gstack-wtree` — this repo's `evidence-run.py` and `wtree.sh` are credited ports of them |
| cross-model review | Accurate: Codex adversarial review always-on in `/review` and `/ship` (`ship/SKILL.md:616-617`) |
| a Stop gate that fails open | Accurate and unchanged through 2026-09-09: `bin/gstack-verify-gate:9` "Fails open on every absence", `:202` allows after three blocked re-entries, `:213` tells the agent it may drop the declaration; pinned by four tests. Fairness note: it is opt-in with a sha256 trust store and does fail closed on a trusted failing check for three rounds |
| addyosmani ships a floor-guard reference implementation | Accurate, if generous: a ~75-line Node script inside a markdown code block, unwired, self-described as "regex-shallow", adapted and run by the same agent |
| all of it graded inside the run that produced the work | Accurate for the four named items |
| no shipped pack executes a negative control | Accurate across all seven. Not accurate about the ecosystem: mutation-testing agent skills execute mutation controls in-session, and a CI "revert witness" script — restore production from the merge base, require the test to fail — was published on DEV on 2026-09-09, one day before this repo's own executor landed |
| orca-fleet's edge is "harder to copy" | Not supported. The executable core is ~120 lines of a 1,176-line file; the market converged on the revert half independently the same week |
| "landing on this branch — the negative control is executed" | Stale on `main` (`2a946d8` merged), and silent that execution is opt-in (`ORCA_EXECUTE_NC`), which is the same opt-in shape the paragraph faults gstack for |
| Omission | boshu2/agentops v3.6.0 states this repo's thesis almost verbatim ("the context that wrote the code does not get to declare it done"), ships a Go CLI that content-hashes the judged subject, and binds author and validator context ids into a `verdict.v2` artifact. Its gaps are real — model verdict, same-orchestrator dispatch, distinctness attested not enforced, no executed control — but narrower than "graded inside the run". The paragraph reads as a survey and names two packs |

Nothing in the paragraph is false. It is unfair by omission and it over-claims "harder to copy".

### 7.2 What is commoditized

A reviewer or verifier in a context the worker did not author: Claude Code `/code-review` as a
background subagent since 2.1.218, `/ultrareview` in the cloud, `/fork`; Codex cloud PR review, which
runs tests; Codex Auto-review as a separate agent for sandbox actions; agentops `validate`;
Critique's "independent session, reset workspace"; roughly thirty small repositories under the
`agent-verification` and `proof-of-done` topics. Content-hash evidence ledgers and freshness
fingerprints. Cross-model review. Stop-boundary gates — every shipped one defaulting to fail-open or
observe mode, including this repository's `Stop` handler with no manifest named. And the
negative-control idea itself.

### 7.3 What is still a moat

Before this review the defensible sentence was: an executed, command-bound, fail-closed control run
by a verifier the worker did not spawn, composed with a coordinator-held scope digest and a GitHub
review bound to the head tree. After §4, two of those words do not hold. "Command-bound" binds to a
ledger the worker writes. "Fail-closed" is true of the tools the executor refuses and false of the
controls it accepts.

What remains genuinely uncontested is the composition: scope digest plus tree-bound GitHub review
plus a deterministic verifier with no model in the verdict path. agentops has the hashed subject and
a model verdict; invara and axiom have no model and no control. That composition is a few hundred
lines of Python whose specification is public in `runtime/evidence-manifest.md` §2. The honest
positioning is "we bind scope and review by mechanism, and we are making the executed control
unforgeable" — not "harder to copy".

---

## 8. Prioritized backlog

Each item is one agent, one PR, with the file it lands in.

### P0 — the claim is false until these land

1. **Stop executing worker-chosen commands.** In `verify.py:512-576`, refuse `--execute-nc` unless
   `--nc-command` is supplied out of band; delete the "already in the ledger" fallback, which binds
   to a document the worker writes. Add a test that a manifest nominating `sh -c` is RED without
   `--nc-command`. Anchors: `verify.py:557-576`, `verify-gate.sh:101-102`, `docs/verify-gate.md:64-72`.
2. **Bind the control to the change.** `negative_control.paths` must be a subset of the production
   paths changed in `base_sha..head_sha` and must exclude test paths (`diff_scope.py` already
   classifies `SCOPE_TESTS`); a `hand` diff must touch only production files the unit changed and
   must leave the module importable — treat ImportError, SyntaxError and `SystemExit` under the
   control as a stillborn mutant, not a kill; the range-revert fallback must fail closed when the
   unit adds a test module. Require a failure signature: the RED run must name the criterion-bound
   test id and an assertion failure. Anchors: `verify.py:596-610`, `:636-680`, `:683-753`.
3. **Say what the proof-tier gate proves.** Either add a leg that cannot be typed — a
   coordinator-signed `verify.py` transcript checked against a committed key, or a CI job that
   re-runs the verifier from the report's own manifest — or reword `README.md:149-154` to "a tier
   cannot be claimed without artifacts that hash true at a named commit". Anchors:
   `run_report.py:33-38`, `:68-79`.
4. **Reword the lead paragraph and the FAQ.** `README.md:39-41` and `:328-332` must say the
   execution is opt-in and must not imply the control is unforgeable; `:545-548` ("Can a mission
   touch my default branch? No.") is doctrine; name agentops at `:29-33`; drop "harder to copy".
5. **Verify the danger sandbox, do not grep for it.** `spawn_worker.sh:205-237` must run
   `orca vm recipe doctor "$recipe" --provision --json` itself, parse the result, and pass the recipe
   to placement. `sandbox-policy.md:69-74` currently overstates what the script does.

### P1 — mechanisms that exist and are not wired; gates that measure the wrong thing

6. **Wire the seven orphans or delete the claim.** For each of `guard_text.py`, `decisions.py`,
   `floor_guard.py`, `diff_scope.py`, `egress.py`, `deny-hook.sh`, `dispatch-sign.py`: name the
   invocation in the mission or playbook whose guarantee depends on it, and add the contract test
   that greps for the raw form — or remove the sentence that says the guarantee holds.
   `guard_text.py:55-56` cites a contract test that does not exist.
7. **Name the verifier invocation in the missions.** Put the literal command line with its lane flags
   into each mutating mission's pipeline, and wrap the criterion-bound run in `evidence-run.py` in
   `build-change.md`. Today no SKILL.md or playbook names `--execute-nc`, `--nc-command` or
   `evidence-run.py`.
8. **Make a proof tier cost a run.** Require the run's own directory to contain a `commands[]` ledger
   with a record whose `wtree` is the tree of a commit the report names and whose `cmd` is the
   verifier invocation; keep saying it is still self-attested until item 3 lands.
9. **Fix the routing instrument.** Assert a 0.05 minimum top-two margin on positive fixtures; cap or
   justify `expected_any`; probe every quoted trigger phrase in `validate`; move the six unphrased
   exclusions into "Not for" clauses; give modernize-it a platform-major trigger.
10. **Make the identity test resist paraphrase, or stop calling it executable.** Compare lemmatised
    content with a synonym table and require a stated differing point above 0.5 mean Jaccard, or
    rename it a duplicate-tuple detector in `AGENTS.md:107` and `CONTRIBUTING.md:57-59`. Add the
    one-word-paraphrase case to `tests/test_validate.py:877-905`.
11. **Fold pin-it into clean-sweep** as `source=runtime-doctrine oracle=orca-binary` with a
    `re-witness` playbook, or amend `ARCHITECTURE.md:42-46` so the rule admits it. Record the four
    2026-09-10 admissions in `docs/research/REJECTED.md`'s footer; fix "five-part" in
    `docs/missions/oss-contribute.md:30`; make modernize-it name migrate-it.
12. **Extract a shared `characterize` playbook** from `prove-it:54-61` and `reshape-it:76-82`.
13. **Put the solo-run lesson into ship-it's doctrine.** One sentence in `skills/ship-it/SKILL.md`
    and `playbooks/acceptance-review.md`: with no second GitHub identity, record RED and stop at the
    build state, or take the executed-control lane; never self-approve. Today it lives only in the
    run report, the template, the binder and its test (§12.1).
14. **Field-proof plan or no mission.** A test that every `skills/<name>` has a row in the plan;
    eight lack one, including all four added on 2026-09-10.
15. **Fix the run archive and completion ledger** — the 18 factual errors in §12.3, the three "Proof
    tier earned" headers, the 2026-09-09 inventory pinned to the wrong tip, the closed-issue rows in
    `STATUS.md` / `status.json` / `GAPS.md`, `TODOS.md:7`, and the repository's About description.
16. **Fix the `npx` instructions.** Point `npx skills add` at a published `dist/` or remove
    `README.md:408-409`; remove the angle brackets from `skills/ship-it/SKILL.md:9`.
17. **Re-point the 27 `REVIEW.md §N` citations** at the predecessor review's new home, or restate
    the anchors they need. They are in `verify.py`, `spawn_worker.sh`, `bundle.py`,
    `evidence-run.py`, seven test modules, `evals/routing.json`, three vf-bench traps, `validate.yml`,
    `README.md:154`, `ARCHITECTURE.md:56` and `TODOS.md:12`.

### P2 — hardening and hygiene

18. Tighten `extract_criterion_ids` to fail closed on any `[A-Z]+-\d+` token it does not count as a
    criterion (A16), or require JSON contracts with explicit `criterion_ids`.
19. `deny-hook.sh`: resolve the final component after every symlink hop; extend the boundary to
    `NotebookEdit` and to parseable Bash writes; anchor the `rm` and `git push` patterns at any argv
    position; add `orca-ide`.
20. `spawn_worker.sh`: fail closed on an exit-0 receipt with no `state`; fail closed when
    `launch.effective` lacks the profile's flag; anchor the recipe match (`grep -F -x`); parse
    `status` as a token, not a word-split.
21. `pm.py`: escape Unicode `Cf` characters (U+202E and U+200B reach the coordinator's terminal).
22. Add `.orca/` to `.gitignore`; strip the maintainer's e-mail and commit message from
    `.gitleaks-baseline.json`; restrict `alert-on-failure.yml` to same-repository `push` runs.
23. Pin `uv`, `skills-ref` and `ruff` by hash or guard the version strings with a test; add an
    `orca --version` check against `pins.json` and arm pin-it on a mismatch.
24. Absorb the five Orca anchor defects (§11.6) into the next pin-it patch wave.
25. Generate the `ARCHITECTURE.md:163-169` load numbers instead of writing them (they are 150–280
    tokens stale); decide whether the spec's 5,000-token recommendation is a target, and if not stop
    citing it.
26. Delete or re-attribute the quotation at
    `docs/research/2026-08-28-forward-roadmap-and-defensibility-plan.md:72`; the real Osmani sentence
    is in "Software Factories, Light and Dark" (2026-07-22), not the autonomy ladder.
27. Scan untracked SKILL.md placements outside CI; reject frontmatter in `playbooks/` and `runtime/`.
28. Add the four refused control classes — decoy path, oracle mutation, stillborn mutant, grep
    command — to VF-Bench as traps, so "0% false-done" measures the class this review broke.
29. Publish the git tags `docs/releases.json` describes; the file binds nine versions to commits and
    `git tag` is still empty.

---

## 9. Three-layer separation, portability, and the instruction budget

### 9.1 The spec, at today's revision

The agentskills.io specification carries no version number; the current text is
`docs/specification.mdx` at `agentskills/agentskills` `69ef37e` (2026-08-09), last changed
2026-08-04 when `metadata` was clarified to "a map from string keys to string values". Required:
`name`, `description`. Optional: `license`, `compatibility`, `metadata`, `allowed-tools`. `metadata`
is the named extension point and the reference validator (`skills-ref` 0.1.1, `validator.py:14-22`)
hard-rejects any other top-level key; the maintainer's proposal to allow prefixed extras (Discussion
#211) is open and unadopted. The file-reference rule is "relative paths from the skill root … one
level deep"; the spec is silent on `../`, and its client-implementation guide tells hosts to resolve
paths against the skill's directory. Progressive disclosure is three tiers: metadata ~100 tokens,
body "< 5000 tokens recommended", resources on demand, "Keep your main `SKILL.md` under 500 lines."

At HEAD all 21 frontmatters pass `skills-ref`, CI runs it (`validate.yml:45-67`), and the
predecessor's spec finding is closed: the eight repo claims sit under `metadata:` as strings. One
residual: `ship-it`'s description contains `build me <feature>` (`skills/ship-it/SKILL.md:9`), which
Anthropic's `quick_validate.py` — the `package_skill.py` and claude.ai upload path — rejects on the
clean file. The other 20 are clean. `claude plugin validate --strict` passes.

### 9.2 The `../../` bet, measured

| Path | What lands | `../../playbooks` resolves? | Gate |
|---|---|---|---|
| `ln -s` into `~/.claude/skills/` (the README's recommended trial path) | a symlink to the repo tree | yes | none until the settings snippet is merged (E3) |
| `claude plugin install` from `.claude-plugin/marketplace.json` (`source: "./"`) | the whole repository copied to the plugin cache | yes | wired by `hooks/hooks.json` |
| `npx skills add ravidsrk/orca-fleet` (`README.md:408-409`) | `dirname(SKILL.md)` only; `vercel-labs/skills` 1.5.25 copies the skill directory, dereferences symlinks, rewrites nothing | **no** | none |

Blast radius: every copy installer other than the whole-repository plugin, and every zip or upload of
a skill directory. What a user sees mid-mission: the coordinator reads "Composes `decide-and-freeze`,
`decompose-dag`…" (`skills/ship-it/SKILL.md:36-39`), has no file for any of those names, and either
invents the protocol or stops; the mission also invokes `runtime/scripts/preflight.py` by a
repo-root-relative path (`:68`) that does not exist from the skill root.
`docs/getting-started.md:230-232` documents the symptom and prescribes re-installing by symlink.

`scripts/bundle.py` is the right answer and is CI-checked (`validate.yml:44`): it vendors each
mission's composed docs into `references/`, rewrites outbound links, and refuses a link that still
leaves the directory. It is not the README's answer: the README prints the broken command first and
the bundle step after, and `npx skills add` takes a repository, not `dist/`, so a reader following
the page in order installs a half-blind mission. Judgment: self-containment by build step is the
right call — 21 vendored copies of a 53,600-token doctrine tree would rot between edits exactly as
`bundle.py`'s docstring says. The wrong part is shipping install instructions for the path the build
step exists to fix.

### 9.3 What one mission actually costs

`validate.py:652-689` measures activation load as SKILL.md plus every doc the Composes/rides clause
names plus linked root docs, at bytes/4:

| Mission | Activation load (tokens) |
|---|---|
| clean-sweep | 33,850 (cap 34,000) |
| oss-contribute | 33,283 |
| ship-it | 31,558 |
| oncall-it | 31,176 |
| median of 21 | 27,264 |
| root-cause (lightest) | 15,374 |

For ship-it the clause pulls 17 files; the five largest are `runtime/evidence-manifest.md` (4,904),
`runtime/dispatch-lifecycle.md` (3,898), `ARCHITECTURE.md` (3,664), `runtime/liveness-resume.md`
(2,861) and the SKILL.md itself (2,302). End to end a coordinator also loads the eight DEFERRED READS
the mission names for later phases (8,268 tokens) and the three second-hop docs the clause docs point
at (4,951): about 39,800 tokens for a full run and 44,800 for a diligent one, against a spec
recommendation of under 5,000 and the predecessor repository's fatal ~42,000
(`ARCHITECTURE.md:125-127`). The whole doctrine tree is ~53,600 tokens, so ship-it's activation is
59% of it and a full run 74%.

The numbers ARCHITECTURE.md publishes (`:168-169`) are 150–280 tokens stale against a fresh
measurement, and the deferral it describes is an accounting move for a full run: the coordinator
still reads the deferred docs, just later. Progressive disclosure in the spec's sense does not exist
here; the cap is a ratchet set just above the heaviest mission, which the document says of itself.
Two honest options: restructure the 160-line runtime policies into a short contract each mission
rides plus an on-demand reference, or accept the cost and stop citing the spec's recommendation. The
badge check caught a four-line playbook edit during D2 through the load number, so the measurement is
live even where the target is not.

### 9.4 The layer rule

Tracked SKILL.md leaks are caught in all five placements tried. Two gaps: an untracked one passes
because the scan is `git ls-files` (D1b), and a playbook given YAML frontmatter passes every gate
(D2), so "playbooks have no frontmatter and never auto-trigger" (`AGENTS.md:110-111`) is doctrine.
Neither matters on a plugin install; both do on a symlinked checkout a host reads from disk.

---

## 10. Verifier independence against the literature

The design has two verifiers and calls both independent. They are different things.

**The deterministic one** (`verify.py`) is the AI-control "trusted component" (Greenblatt et al.
2024): no model in the verdict path, so it is immune to self-preference (Panickssery et al. 2024),
to preference leakage — strongest on programming and undetectable by the judge itself (Li et al.
2025) — to persuasion by completion language (Advani 2026 measures LLM judges at AUROC ≤ 0.65 on
false success; Wen et al. 2024), to consequence-sensitive verdicts (Lynch et al. 2026: Claude judges
knowingly mislabeled 62–86% of transcripts when the truthful label would be used to train a behaviour
away), and to grader-conditional behaviour (Qi et al. 2026). Its errors are uncorrelated with the
worker's reasoning errors — the Littlewood–Miller "forced diversity" a fresh context window does not
provide. That is why the four legs it owns outright survive §4. It buys what the literature says an
execution-based check buys and no more: it re-derives identity, not quality. in-toto and SLSA match
subjects purely by digest and then layer *expectations* on top; the repo's equivalent expectations —
approver ≠ pusher, reject unrecognised manifest fields — exist for the first and not the second.

**The executed control** is, in Lipsitch et al. 2010's terms, a negative-control outcome whose
validity rests on U-comparability: the reverted worktree must differ from the head only in the causal
variable under test. A13, A14, A14b and A21 are exactly the violations that theory predicts — a
control that lights up through a path unrelated to the behaviour. Niedermayr et al. 2016 and
Vera-Pérez et al. 2018 give the honest reading of a passing control: the test is not pseudo-testing
that location. It says nothing about correctness, and the automated-program-repair literature
quantifies the case it cannot see — coupled test-and-fix overfitting — at 54–90% of plausible patches
(Le et al. 2018; Smith et al. 2015; Qi et al. 2015), with expert manual judgment mislabeling 10.3% of
"correct" ones (Ye et al. 2021). A single worker-pinned mutant is a sample of one from a distribution
where sampling theory wants ~9,600 for tight bounds (Gopinath et al. 2015), 1–4% of mutants are
dominators (Ammann et al. 2014; Kurtz et al. 2016), up to ~45% of survivors may be equivalent
(Schuler & Zeller 2013), and Google surfaces per-diff mutants as review prompts, never certificates
(Petrović & Ivanković 2018). The one published result that directly supports the design is
SWT-Bench (Mündler et al. 2024): fail-before/pass-after generated tests double a repair agent's
precision — a filter, not a proof.

**The LLM verifier** ("a DIFFERENT process/session — never a teammate",
`runtime/evidence-manifest.md:107-111`) is untrusted monitoring: same capability class, usually the
same family, reading the worker's prose. Greenblatt et al. put untrusted monitoring at 79% safety
against 92% for trusted editing, and only with honeypots and paraphrasing; Knight & Leveson 1986,
Eckhardt & Lee 1985 and Ron, Baudry & Monperrus 2026 — 48 agent-written versions, common-mode
failures concentrated where the specification is hard — predict that the second opinion fails where
the first did. The repository mitigates none of the three: no honeypots for the verifier, no
redaction of worker prose before it reads, and `cross-vendor` preferred in one playbook sentence
(`acceptance-review.md:13-14`) while the only recorded run used `instructed-isolation`, the weakest
mode. The legs pushed to this verifier — the ≥10% sample, the binding audit, the clean-env re-run —
are precisely the ones that are still doctrine, so the shared-blind-spot risk is neither mitigated
nor measured.

**What "independent" buys, then:** the scope digest and the review identity, by mechanism; the
RED-then-GREEN shape of a control the worker designed, by mechanism; nothing else. The adjustments
that would change that are P0-2 and P1: a failure signature and a behavioural-hunk revert, a
verifier-chosen mutant, one oracle the worker did not author, and honeypots with a recorded catch
rate.

### 10.1 The autonomy ladder, checked against the source

All 21 missions declare `autonomy: L4`, and the derivation in `docs/concepts.md:319-339` follows
Osmani's text. L4 is "Work across many agents in parallel. Each agent works on an isolated slice of
the task" — near-verbatim in the README — and read-only work is explicitly L4 in the source
("Parallelize read-heavy exploration tasks (autonomy level 4)"), so the read-only and planning
missions belong there. L5's first operative clause is the trigger ("A manager agent will wake up
based on triggers … new issue, new task, clock"), and the source assigns human-handoff intake to
"Level 4 with a dashboard", so placing a human-started coordinator at L4 is the faithful reading.
Two small corrections: the ladder is structural only on its upper rungs — L0–L2 are defined by
supervision, so "The ladder is structural" (`README.md:136`) is over-broad; and the sentence "the
level you can safely reach is exactly the level you can cheaply prove" does not exist in the ladder
post. It was removed from the README and still sits in quotation marks at
`docs/research/2026-08-28-forward-roadmap-and-defensibility-plan.md:72`. The nearest real Osmani
sentence is from a different post: "you can only hand a loop as much autonomy as you can cheaply and
reliably verify, and not one inch more."

---

## 11. Security, supply chain, and the runtime pin

### 11.1 Injection surface

Target-repository text reaches the coordinator raw: `gh issue view`, README, PR bodies, and `pm.py`'s
inbox rendering, which escapes C0/C1 control characters only (`pm.py:34-41`) and passes Unicode
format characters through (U+202E and U+200B confirmed). It reaches a worker verbatim through the
coordinator-typed `task-create --spec` (`playbooks/decompose-dag.md:18-22`); for `clean-sweep
source=tracker` the slice *is* the issue, so title and body land in the spec unfenced. `guard_text.py`
is a real fence — banner, injection-pattern labels, NFKC-folded detection, forged-banner defusal,
argv-only fetch — whose docstring calls it "the only sanctioned path for untrusted text into a task
spec" (`:2`) and cites a contract test that does not exist. It has zero callers.
`spawn_worker.sh` itself does no shell interpolation of untrusted data (a title containing `$( )`,
backticks, `;` and `&&` reached the stub as one argv element; `tests/test_architecture.py:684-699`
forbids `python -c` and `eval` in `runtime/scripts/`).

### 11.2 Sandbox policy

`ro` passes the agent's read-only flag on the unsupervised `terminal create --command` lane and never
takes `worker-start`. `rw` and `danger` take the supervised lane with no command and no flags
(`spawn_worker.sh:381`); the permission mode a worker gets is the Orca host's `agentDefaultArgs`,
which the script prints when the receipt carries it and does not fail on when it is absent. Orca has
no read-only tier for any agent and none of the fleet's `ORCA_COORD_*` or `ORCA_SANDBOX_*` variables
exist in its tree; the three tiers are fleet convention.

`danger` at HEAD requires `ORCA_COORD_ALLOW_DANGER=1`, a recipe id of three or more
`[A-Za-z0-9._-]` characters, and a readable file that mentions the id — an unanchored BRE grep
(`:229`) — and contains no `fail` or `warn` token (`:233`). Reproduced on a scratch copy:
`ORCA_SANDBOX_RECIPE=root ORCA_SANDBOX_DOCTOR=/etc/passwd` spawns a danger worker;
`ORCA_SANDBOX_RECIPE='...'` with a file reading "totally fake transcript" spawns one; a realistic
`orca vm recipe doctor` JSON with `"failures": []` is refused because `failures` matches `fail`. The
recipe is never passed to Orca, so even a genuine transcript places nothing in a VM. The header's
claim that recipe and doctor are "recorded on the spawn line so the ledger carries what the lane
actually ran in" (`:209-210`) names output that does not exist. The predecessor said a boolean was
not evidence of a sandbox; the boolean became a grep.

### 11.3 The verifier as an execution surface

A15 is the security form of §4.1: `verify.py --execute-nc` runs `shlex.split(negative_control.command)`
as argv in a worktree with a 600-second budget and the verifier's identity, wherever `ORCA_NC_COMMAND`
is unset — the documented default — on the surfaces the design calls sound: CI, SDK subprocess, and
the coordinator's machine, which holds `gh` authentication and, where signed dispatch is enabled, the
dispatch seed. The docstring at `:515-525` says the ledger binding leaves "nothing left to invent";
it binds the command to content, not to a trusted author. The control also runs first
(`:1079-1083`), before scope or review can refuse the manifest, so a manifest that is RED on every
other leg still has its command executed twice.

### 11.4 Other findings

- `deny-hook.sh` is unregistered by construction and says so; wired per its `--settings` block it is
  fail-closed on parse errors but silently allows a two-hop symlink write (confirmed: `open()` wrote
  through the chain), `NotebookEdit` outside the boundary, every Bash write, `/bin/rm -rf /`,
  `(rm -rf /)`, `git -C . push --force origin main`, `--force=true`, `-fu`, `find / -delete`, and
  `orca-ide orchestration reset`. Its "freeze boundary for free" (`:64-65`) is not true of Bash.
- `spawn_worker.sh` fails open on an exit-0 receipt it cannot parse (`:397-400`, `:441-447`): an Orca
  that prints a warning on stderr yields `HANDLE= READY=exit0`, exit 0, and the coordinator records a
  worker that may not exist.
- Signed dispatch is dormant: no `.orca/dispatch-pubkey` is committed, no mission or playbook signs,
  and when enabled the seed and the graded worker share a host and UID, where 0600 stops nothing.
- `egress.py` is a sound hash-chained ledger with no caller; its default path `.orca/egress.jsonl`
  is not git-ignored and the chain has no external anchor, so a from-scratch rewrite verifies clean.
- CI is clean: `permissions: contents: read`, no `pull_request_target`, actions SHA-pinned (verified
  by `ls-remote`), gitleaks pinned by version and sha256 with a sound canary on the baseline waiver.
  `uv`, `skills-ref` and `ruff` are version-pinned without hashes and no test guards a pin.
  `alert-on-failure.yml` can be tripped by a fork PR whose branch is named `main` — issue spam only.
- `.env.example` is placeholders only; `.env` and `.secrets/*` are ignored and never in history.
  `hitl-loop.template.sh` is clean.

### 11.5 Supply chain

| Dependency | Pinned where | Drift detected by | Class |
|---|---|---|---|
| Orca CLI | `runtime/pins.json`, commit `28957d6004` v1.4.199, `witness: source` | nothing at runtime: no `orca --version` check; `tests/test_pins.py` checks JSON shape only | Doctrine |
| orchestration + orca-cli skills | not pinned; fetched live by `orca skills get` | none | Doctrine |
| mattpocock / gstack / addyosmani | `runtime/pins.json` by commit | an entry is required per `compatibility:` pack; nothing compares an installed copy | Doctrine |
| gitleaks | CI: version + sha256 | checksum | Mechanism (CI only) |
| skills-ref, uv, ruff | CI: version only | none | Advisory |
| actions/checkout, setup-python | SHA-pinned | GitHub resolves | Mechanism |
| `npx skills add` (`README.md:408-409`) | unpinned | none | Doctrine |

### 11.6 Orca drift: is `pin-it` needed right now?

No, and it is a day or two from being needed. Orca's latest tag is still v1.4.199, the pinned commit;
`main` carries 95 commits past the release branch point, two of them after the pin, neither touching
a CLI spec, handler, guide or orchestration contract. Both skill guides the fleet re-witnesses and
every `src/cli/specs/*` file are byte-identical between the tag and HEAD. The one behaviour change
waiting on `main` — `worker-start` readiness settling on an observed `turn_started`, else
`outcome_unknown` — is already described by the doctrine as "the next release", and `spawn_worker.sh`
v5 already branches on it. Orca ships 3.0 stable releases a week (4.5 over 14 days), median gap 22.5
hours, with a stated 48–72 hour landed-to-released policy, so the release that flips readiness
semantics is due about 2026-09-11/12 and will stale three doctrine files in one shot.

The predecessor's suspect sentence ("receipted sends exist only in upstream's unreleased source") was
true when written at 17:36 UTC on 2026-09-09 and false 22 minutes later when v1.4.199 was tagged; it
has been repaired. Five anchor and wording defects remain, none a mechanic: the doctor rule cited at
the wrong guide lines (`sandbox-policy.md:71`); six refusal codes anchored to a file defining three
(`dispatch-lifecycle.md:26-29`); "(no RO in Orca)" for cursor and grok when Orca has no read-only tier
for any agent (`sandbox-policy.md:29-30`); `decision_gate` listed as a real message type when nothing
on CLI paths writes one (`orca-dag-semantics.md:49-50`); and the time-bounded "next release"
phrasing. Recommendation: arm pin-it on `orca --version ≠ v1.4.199` rather than run it today, and
fold the five into that patch wave.

---

## 12. The run archive, the proof ledger, and doc truthfulness

### 12.1 What resolves

Every ravidsrk/orca-fleet SHA in all six run reports and in `docs/completion/` resolves and is an
ancestor of HEAD; every PR a report calls merged is merged with the stated merge SHA. The ship-it
self-run's five inventory hashes re-derive at `748b328`, recomputed here. The gstack PR the review-it
external run reviewed still has the reviewed SHA as its head and its merge-base resolves (verified by
`git ls-remote` and a fetch of the PR ref; GitHub HTML and API are blocked for that repository by the
session proxy). The chimely PR refs exist; their states could not be verified.

`run_report.py docs/runs/2026-08-28-ship-it-self-run.md --mission ship-it --tier self-run` exits 1:
"verifier=RED but the body shows no verify.py invocation against …/build-manifest.json". That is the
report's own admission (`:153-170`) and it is the right outcome.

**The solo-run lesson lives outside the doctrine it is about.** The report says a solo fleet cannot
manufacture an independent approver, so it cannot autonomously reach a closed mutation unit
(`:87-95`). That lesson appears in `docs/runs/TEMPLATE.md:15-16`, `run_report.py:18-21`,
`tests/test_run_report.py:104-106`, `attention-budget.md:37-39` and `verify.py:20-22`. It appears in
none of `skills/ship-it/SKILL.md`, `docs/missions/ship-it.md`, `playbooks/acceptance-review.md`,
`playbooks/release.md` or `runtime/merge-serialization.md` — zero hits for solo, single identity,
self-approval or independent approver. The closest is "the fleet never self-merges the promotion",
which is the promotion gate, not the per-slice review authority. A coordinator reading ship-it has no
instruction for the situation the flagship run actually hit.

### 12.2 Twenty-one missions, zero bound runs

Six run reports, none binding. The field-proof plan has rows for 13 missions, each with a blocker,
every blocker but one including "Orca". Eight missions have no plan row: absorb-it, document-it,
migrate-it and oncall-it (added 2026-09-10, neither plan nor report), plus clean-sweep, review-it,
oss-contribute and ship-it (reports exist, all bind `no`, no plan for a binding re-run).

The README's framing (`:156-175`) is honest about the count and argues the number went down as the
mechanism got stronger. Two things it does not say: B3 shows the mechanism that produced "0" would
accept a fabricated "1" in fifteen minutes, so the zero measures the maintainer's honesty rather than
the gate's strength; and the catalog grew by four on the same day it reached zero. The ratio worth
publishing is not 21/0 but *21 missions, 0 bound runs, 8 with no path to one*.

### 12.3 Doc truthfulness — a clean-sweep phase-one enumeration

Verified this session, in the human docs:

| Claim | Anchor | Reality |
|---|---|---|
| "The first two run in under a second" | `CONTRIBUTING.md:118` | `validate.py` 212 ms; `unittest discover` **79 seconds**. FALSE |
| "Repository layout" block | `README.md:471-479` | Omits `bench/`, `demo/`, `evals/`, `hooks/` — four of eleven tracked directories, including the two the README elsewhere leans on. INCOMPLETE |
| Requirements table | `README.md:455-468` | Eleven of 21 missions have a tooling row. Ten have none, including access-it, whose oracle is axe-core and which the catalog table names as such. MISLEADING |
| Activation-load figures | `ARCHITECTURE.md:168-169` | 31,400 / 33,000 / 33,600 against measured 31,558 / 33,283 / 33,850. STALE |
| "Thirteen missions are `doctrine-only`" | `docs/runs/README.md:45` | 21 are. FALSE |
| `[Unreleased]` "each is listed below as it lands" | `CHANGELOG.md:9-12` | Zero mentions of migrate-it, oncall-it, absorb-it, document-it, `bundle.py`, `deny-hook`, `egress.py`, `floor_guard`, `guard_text`, `decisions.py`, `evidence-run` or `inventory.py` — the four missions and eight scripts that landed on 2026-09-10. SILENT DRIFT |
| "The catalog reads 21 `doctrine-only`" | `README.md:170` | True today, and a hardcoded catalog count inside a file `check_doc_counts` is supposed to police; `COUNT_LINT_RE` does not match this phrasing. The guard against this exact rot has a hole |
| Demo integrity inventory | `demo/negative-control/README.md:50` | `0b99f489…` matches the committed file. The predecessor's finding is FIXED |
| ship-it inventory re-derives at `748b328` | `README.md:165-168` | 5/5 recomputed MATCH. TRUE |
| "exercised by `tests/test_run_report.py` against real git repositories" | `README.md:174-175` | The fixtures run `git init` and real commits. TRUE |
| "`attention-budget.md` is the exemplar of the Evidence-level rule" | `ARCHITECTURE.md:135` | Its own level is ASSERTED, which is what the sentence now says. The predecessor's finding is FIXED |
| Symlink verified, plugin has no transcript | `README.md:436-439` | Evidence file exists; the plugin path was verified working this session, so the claim is conservative rather than wrong. TRUE |
| `docs/releases.json` binds nine versions | `CHANGELOG.md` / `docs/releases.json` | All nine commits resolve; `git tag` is still empty, and the file's own instructions for publishing the tags have not been run. TRUE but unfinished |

Eighteen further errors sit in the run archive and completion ledger, all verified against git and
the GitHub API. The load-bearing ones: the run index calls the ship-it promotion PR "open" when
#104 merged as `9ed6fe9` on 2026-08-28 — by ship-it's own state machine that is the released state;
the ship-it report says `TEMPLATE.md` "asked for" the verifier transcript when the template was
created five days after the run; it credits PR #137 with changing two files it never touched; it
calls the slice "report-shaped" while its own manifest declares `unit_class: mutation`; three reports
still carry "Proof tier earned" headers their own Evidence-binding sections contradict; the
2026-09-09 tracker inventory names a tip at which 3 of 13 hashes do not match; `STATUS.md:140` says
"13 missions … 0.6.0"; and `status.json`, `GAPS.md` and `TODOS.md:7` list gaps whose tracking issues
closed on 2026-09-09. The repository's GitHub description says "17 outcome-named autonomous fleets"
against a catalog of 21 — the third recurrence of a gap the completion audit closed twice.

### 12.4 The repository against `review-it`'s own doctrine

Running `review-it`'s verdict rule on this repository as the artifact: acceptance axes are standards,
spec fidelity and test adequacy, with risk lenses triggered by the surface. Standards: the catalog's
own rules are followed almost everywhere — the three layers hold, the budgets hold, the frontmatter
is spec-legal. Spec fidelity: the README's claims outrun the mechanism in the four places §3.1 marks
advisory, and the proof-tier sentence is false as written. Test adequacy: 782 tests, and the guard at
the centre of the product has no test for the class of input it exists to refuse. The security lens
is triggered by `runtime/scripts/` and returns two P1 findings. The verdict rule is "any Critical or
any Required → NO-GO", and P0-1 is Required by the repository's own severity language. **NO-GO**, with
the note that `review-it` has no fix authority and this document therefore proposes, never applies.

---

## 13. Sources and method

Repository state: `git rev-list --count HEAD` = 534 at `2a9cb3a`; 475 commits by the maintainer, 50
by `ravidsrk`, 9 by Cursor agents; zero git tags. Local gate at HEAD, all green: `validate.py` OK
(21 missions), `eval.py run --suite all` 86/86 routing and 63 per-skill evals, `unittest discover`
782 OK, `ruff` clean, `proof_status.py --check` 0, `run_report.py` "no mission claims a tier above
doctrine-only", `bundle.py --check` 21 self-contained missions.

Instruments, all under `scratchpad/`: `harness.py` + `harness-results.json` (the §4.1 manifests),
`inject.sh` + `inject-out.txt` (§4.2, §4.4, §4.5, the demo and VF-Bench runs), `routing/` (predictions
written before the router ran, the 64-prompt matrix, pairwise and trigger-phrase probes),
`similarity.py` and the fake-catalog demo (§6.1), plus scratch copies of `spawn_worker.sh`,
`deny-hook.sh` and `verify.py` for the security probes.

External, fetched 2026-09-10:

- agentskills.io specification at `agentskills/agentskills` `69ef37e`; `skills-ref` 0.1.1
  (`validator.py` `ALLOWED_FIELDS`); Discussion #211; Claude Code skills and plugins references;
  `anthropics/skills` `41bbe19` (`quick_validate.py`, `package_skill.py`); `vercel-labs/skills`
  1.5.25 (`src/installer.ts`, `src/skills.ts`).
- garrytan/gstack 1.84.1.0 `71f6048e` (`bin/gstack-verify-gate`, `bin/gstack-evidence`,
  `bin/gstack-wtree`, `ship/SKILL.md`, CHANGELOG 1.79–1.84.1); addyosmani/agent-skills 0.6.9
  `6ca0cd7`; mattpocock/skills v1.2.3 `3cca18b`; obra/superpowers 6.3.0; boshu2/agentops 3.6.0
  `322f94e`; EveryInc/compound-engineering 3.24.0; Claude Code CHANGELOG 2.1.111–2.1.267; OpenAI
  Codex Auto-review and cloud PR review; critique.sh; the DEV "revert witness" post (2026-09-09).
- stablyai/orca, full clone, HEAD `26f9fd8e`, tag v1.4.199 = `28957d6004` (tagged 2026-09-09), its
  release notes, and the 95 `main`-side commits since the release branch point.
- Addy Osmani, "Agentic Autonomy Levels", addyo.substack.com 2026-07-03 and addyosmani.com
  2026-07-02 (byte-compared; no revision since publication); "Software Factories, Light and Dark",
  2026-07-22.
- Verification literature: Papadakis et al. 2019 (mutation survey); Just et al. 2014; Papadakis et
  al. 2018; Chekam et al. 2017; Niedermayr et al. 2016 and Vera-Pérez et al. 2018 (pseudo-tested
  methods); Gopinath et al. 2015/2016; Ammann et al. 2014; Kurtz et al. 2016; Petrović & Ivanković
  2018; Qi et al. 2015; Smith et al. 2015; Le et al. 2018; Ye et al. 2021; Mündler et al. 2024
  (SWT-Bench); Aleithan et al. 2024 (SWE-Bench+); Wang et al. 2025; Lipsitch, Tchetgen Tchetgen &
  Cohen 2010; Shi et al. 2020; Chen et al. 1998 and Segura et al. 2016 (metamorphic testing); Knight
  & Leveson 1986; Eckhardt & Lee 1985; Littlewood & Miller 1989; Ron, Baudry & Monperrus 2026; Kim et
  al. 2025 and Goel et al. 2025 (correlated errors); Panickssery et al. 2024; Li et al. 2025
  (preference leakage); Advani 2026; Wen et al. 2024; Cao et al. 2026; METR 2025; Baker et al. 2025;
  MacDiarmid et al. 2025; Qi et al. 2026 and Lynch et al. 2026 (Anthropic Alignment Science);
  Greenblatt et al. 2024 and Bhatt et al. 2025 (AI control); Manheim & Garrabrant 2018; Skalse et al.
  2022; Chen 2025 (EviBound); Tang et al. 2026; in-toto (Torres-Arias et al. 2019), SLSA v1.0,
  Gerrit label semantics, GitHub stale-review dismissal; Nosek et al. 2018 (preregistration).

Method notes and limits. Everything in §4 was executed; nothing was inferred from reading. The Orca
verdicts are source-witnessed, not binary-witnessed: no `orca` binary exists in this session, which
is the same limitation `pins.json` records for itself with `witness: source`. GitHub HTML and REST
were blocked by the session proxy for every repository except this one, so external PR states were
verified through `git ls-remote` and ref fetches where possible and are marked unverified where not.
The competitive survey read seven packs; it is not exhaustive of a market with thirty-odd
verification repositories.
