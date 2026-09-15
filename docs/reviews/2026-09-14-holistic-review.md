# Fresh holistic review — 2026-09-14 @ eb1a2f1

A from-scratch, file-by-file review of the whole catalog plus online verification of its
external claims. No prior review file (REVIEW.md, docs/reviews/2026-09-10-review.md, the
P7 fresh-review evidence files) was read or consulted by any reviewer; every finding below
was derived from the code at `eb1a2f1`, and the headline items were re-verified by hand
after the review pass.

**Method.** 14 parallel reviewers, each reading its scope in full: top-level scripts,
core verifier scripts, remaining runtime scripts + shell, the 32-file test suite, both
halves of the 21-mission catalog, all 28 playbooks, the 12 runtime policies + 2 JSON
registries, the top-level doc surface, the historical docs (completion ledger, mission
guides, run archive, reports, research), bench + demo, and three online-research tracks
(upstream packs + skill spec, Orca runtime claims, standards + tooling claims). Severity:
P0 = defeats the repo's own doctrine or leaves the build red; P1 = real bug, enforcement
gap, or stale/contradictory doctrine; P2 = drift, clarity, hygiene.

## Baseline gates at eb1a2f1

| Gate | Result |
|---|---|
| `scripts/validate.py` | green — 21 missions, three-layer separation holds |
| `scripts/eval.py run --suite routing --threshold 1.0` | green — 88/88 (100%) |
| `runtime/scripts/proof_status.py --check` | green — 21 doctrine-only, 0 above |
| `runtime/scripts/run_report.py` | green — no binding tier claims |
| `scripts/bundle.py --check` | green — 21 self-contained missions |
| `ruff check` | clean |
| `python3 -m unittest discover -s tests` | **RED — 1241 tests, 1 failure (macOS only)** |

## P0

**1. The test suite is red on macOS main, and the failure is a real fail-closed gap.**
`tests/test_run_report.py::test_the_interpreter_is_read_as_argv_too` fails
deterministically on macOS (reproduced twice on this machine at eb1a2f1).
`runtime/scripts/run_report.py:181-187` resolves `root` but compares the recorded
interpreter token *lexically*: on macOS `/var/folders/…` is a symlink to
`/private/var/folders/…`, so `path.is_relative_to(repo)` never matches and an interpreter
*inside the graded tree* is accepted — the exact #327 evasion (a worker-placed binary
satisfying `verifier_ran` with nothing having run), re-opened by path spelling on the
maintainer's own platform. Linux CI masks it because temp dirs land under `/tmp`, which
the scratch-root rule catches for the wrong reason. Fix: `resolve()` both sides of the
comparison and resolve `_SCRATCH_ROOTS` (`/tmp`→`/private/tmp` etc. escape the same way —
`/private/tmp/python3` passes the refusal today); `.resolve()` the test fixture so the
test pins the mechanism, not the platform. A permanently red suite on the dev platform
re-trains exactly the alarm fatigue this repo exists to prevent.

## P1 — enforcement gaps in code

**2. `bundle.py --out` can delete the source tree.** `scripts/bundle.py:261-263` does
`shutil.rmtree(skills_out)` with no guard on `out_dir`; `--out .` resolves `skills_out`
to the real `skills/` and deletes all 21 missions before rebuilding. Fix: refuse any
`out_dir` whose `skills/` child resolves to `SKILLS_DIR`; add a regression test.

**3. `deny-hook.sh` misses `sudo tee`.** `runtime/scripts/deny-hook.sh:953` matches only
`tee|tee *` after `strip_prefix`, which deliberately *reattaches* `sudo`. Verified:
`cat a | tee /etc/cron.d/x` is denied, `cat a | sudo tee /tmp/outside` is silently
allowed — the #297 write shape the Bash half exists to catch. Fix: add `sudo tee` arms +
regression test. (Mitigated by the hook's declared advisory status.)

**4. `verify.py check_commands` accepts any exit-0 command bound to head's tree.**
`runtime/scripts/verify.py:1580-1629` never checks the command is a *test* command or
that it agrees with `--nc-command` — a ledger record of `true` satisfies "tests really
ran on THIS content" in the gh lane. Doctrine-consistent per evidence-manifest.md:126 and
honestly documented, but the weakest gate relative to its name. Suggest: when
`--nc-command` is supplied, require a matching fresh record.

**5. `gen-badges.py` treats any non-`--check` argument as "write".**
`scripts/gen-badges.py:262-266`: `--chek` (a typo) rewrites both badge files and exits 0.
Use argparse so unknown args fail.

**6. Dead/untested guard branches in `eval.py`.** The `_stem` double-strip bug
(`scripts/eval.py:102-120`) is confirmed live: `flakes`→`flak` vs `flaky`→`flaki`,
`closes`→`clo` vs `close`→`clos` — the docstring's own example is false, and the
plural-"es" gap the stemmer exists to close is unclosed (latent: the live gate is green).
Additionally `_margin_verdict`'s three refusal branches (:423-445),
`validate_trigger_phrases`'s both claimed failure directions (:566-595), and
`_over_broad_expected_any` (:454-470) have zero failing-path tests — mutants deleting
them stay green, the precise defect class this suite elsewhere treats as first-class.

**7. `gen-badges.py`'s guides half has no dropped-call protection.**
`check_architecture` got a mutant guard after a real miss; the identical mutant (drop
`check_guides()` from `check()`) passes everything today.

## P1 — doctrine and contract drift

**8. attest-it has no definition-of-done floor.** `runtime/evidence-manifest.md:148-159`
enumerates 17 mutation missions + report-only (review-it) + planning (map-it,
root-cause) — 20 of 21; **attest-it is in no class**, while
`runtime/mission-scheduling.md:57` classes it report-only. The mission whose product is
audit-grade evidence has no defined negative-control analogue. Fix: add it to §3.

**9. Three missions ship ledger rows that drop canonical flags — including `lighting`.**
absorb-it (:111) drops BUILD_DONE/PR_OPEN/BOT/`lighting`; document-it (:95) and
migrate-it (:112) drop BOT/`lighting`; field-test-it, deflake-it, harden-it define
prose-only rows RESUME cannot read. `ledger-contract.md:31-33` says extend, never drop;
`gate-classification.md:60` mandates `lighting` on every dispatched unit. Systemic fix:
a validator check that mission ledger rows contain the canonical columns.

**10. The "≥10% sample" cites authority that doesn't contain it.** clean-sweep:94,
field-test-it:103-104, ship-it:108, pin-it:102-103 cite a sampling floor that exists in
no runtime policy (grep-confirmed); prove-it:71-72 states no floor at all. Three
different stated rigors for the same verification act. Fix: write the floor into
evidence-manifest.md §3.

**11. harden-it invokes a quorum/vote-table mechanism its playbook never defines.**
`skills/harden-it/SKILL.md:65,80` vs `playbooks/triage-findings.md` (single-verifier
discard; the words "quorum"/"vote" appear nowhere). Align one side with the other.

**12. absorb-it's squash accommodation contradicts merge policy and its own convergence.**
`skills/absorb-it/SKILL.md:56-57` contemplates squash-merge, but merge-serialization.md
says "never squash" and absorb-it's convergence (:100-101) requires ancestry
verification a squash commit cannot pass. Unimplementable as written on a squash-only
target.

**13. map-it's convergence proof contradicts the gate policy it rides.** "every decision
ticket resolved by the HUMAN" (:79-80) vs gate-classification's coordinator auto-resolve
for mechanical tickets. State that decision tickets are human-resolved regardless of
class.

**14. oss-contribute's frontmatter `parking` contradicts its body.** :25 lists
`already-has-PR` (a triage class, not a park) and `stood-down` (never a body class), and
omits the body's real classes. The six identity points feed the #288 paraphrase
comparison, so a wrong parking list corrupts the identity record; no validator check
compares frontmatter to body.

**15. sandbox-policy.md describes a danger lane spawn_worker.sh refuses to open.**
`sandbox-policy.md:75-78` still says the script runs `vm recipe doctor --provision` and
reads the verdict; since #335 the script dropped `--provision` and refuses PROFILE=danger
unconditionally (`spawn_worker.sh:273-309`). Anyone re-pinning from the doctrine
reintroduces the spend.

**16. Per-skill behavioral evals are vacuous as shipped.** Every
`skills/*/evals/evals.json` case has `"files": []` — the behavioral suite runs the agent
in an empty directory and grades only trace prose, the exact "grade on narration"
practice the repo forbids. Routing via TF-IDF is the only check that actually executes.
Fix: at least one fixture-backed behavioral eval per mission, or downgrade these files to
routing-fixture status.

**17. The mandated per-wave WIP row is machine-checked nowhere.**
`attention-budget.md:60,77` mandates it in every mutating run report; `run_report.py`
has zero WIP awareness. By the policy's own logic ("a cap recorded nowhere was never a
cap"), the graduation evidence base can silently never accumulate.

**18. One-way-door enumerations drift across three policies and the JSON registry's
provenance note.** `freeze` is a door in `one-way-doors.json` and
`mission-scheduling.md:55` but absent from the `gate-classification.md:48` list and
sandbox-policy's Ask-First list; the JSON's note misdescribes its source. Enforcement is
intact (`decisions.py` matches the JSON); the drift is doc-level. Fix: single enumerated
list, MD files point at it.

**19. CI action pins hard-break on 2026-09-23.** `.github/workflows/validate.yml:15,18`
pin `actions/checkout@v4.2.2` and `actions/setup-python@v5.6.0` — both run on Node 20,
which GitHub removes from runners on 2026-09-23 (changelog verified online). In ~9 days
every gate this repo advertises stops running. Latest: checkout v7.0.1, setup-python
v7.0.0. Fix: bump SHAs with comments, keeping hash-pin discipline.

**20. `egress.py` landed but no doctrine invokes it.** The content-free off-repo receipt
mechanism — the artifact the upstream audit said attest-it needs for Art-12 operational
logging — is referenced by zero missions, playbooks, or runtime policies (grep-verified).
An uninvoked script rots; name it in the dispatch/ship policies or defer it in a tracked
decision.

## P1 — bench, demo, and ledger honesty

**21. Five vf-bench traps are RED no matter what.** `missing-negative-control`,
`unreviewed-mutation`, `fabricated-negative-control`, `downgraded-class`,
`unclassified-mutation` all set symbolic `"HEAD"` SHAs, which fatal 7–8 unrelated
invariants — deleting the check each trap exists to measure would not move the 0/19
score (verified by direct verify.py runs). The REFUSAL-message pinning built for the
#306/#310 classes needs extending to the 13 legacy classes.

**22. The demo's recorded transcript is stale against current verify.py.**
`demo/negative-control/head-to-head.txt` records one FAIL; a fresh `run.sh` emits two
(the #310 class-downgrade leg fires too), and the README's "differs only in the
timestamp" integrity note is no longer true. The moat claim itself reproduced cleanly.
Also: `run.sh:46`'s PASS condition (`vf == 2` alone) would print PASS even if
`check_scope` were entirely broken.

**23. No trap samples the redaction leg; ~10 other verifier legs can regress silently.**
`check_redaction` (#14) is a required fail-closed security leg with zero bench coverage;
same for stale-`wtree`, `check_intent`, `check_lighting`, `check_reviewer_mode`,
`check_provenance`, `check_dispatch_provenance`, `hidden_criterion_ids`, and the
zero-kill corroboration regexes. At minimum: a redaction trap + a stale-wtree trap + a
documented "unsampled legs" list.

**24. The completion ledger shows five items open that the repo's own tracker closed.**
G-15/G-17/G-19/G-20/G-21 and H-04/H-05 read "open" across `docs/completion/GAPS.md`,
`STATUS.md`, `HUMAN_ACTIONS.md`, and `status.json` — but issues #232-#234/#236/#237 were
closed 2026-09-09 (verified via `gh`), and the ledger's own evidence directory contains
the H-04 receipt. A register that teaches "verify against authoritative state" fails
exactly that check. Mechanical fix: flip the entries with closing SHAs.

**25. README's "Four runs really happened" is stale** — `docs/runs/README.md` lists
eight (adds 2026-09-09 tracker, 2026-09-12 PARTIAL-WITNESS, 2026-09-13
PINNED-WITH-PARKED). The doctrine-only conclusion still holds; the enumeration doesn't.

**26. ARCHITECTURE.md contradicts itself on the mission line cap.** :143 says
"Missions ≤ 130 lines"; :163, AGENTS.md, CONTRIBUTING.md, and the validator all say
110 body + 34 frontmatter. `scripts/validate.py:15-17`'s docstring repeats the stale 130
(and misstates its own exit codes: says 0/1, `main()` returns 2 when `skills/` is
missing).

## P1 — mission guide drift (docs/missions vs SKILL.md)

**27.** pin-it.md:5 says "no recorded run yet" — two runs are now in the archive.
map-it.md:78-79 documents two ticket kinds where SKILL.md:54-63 defines four, and omits
the named terminals. root-cause.md:104-108 omits the `INCONCLUSIVE` degraded terminal.
review-it.md:89 says WCAG 2.1 AA where risk-review.md:61 says 2.2 (and omits `privacy`
from NEVER_GATE). reshape-it.md:57's mermaid shows the median-heuristic loop exit the
SKILL explicitly forbids.

**28. The GitHub About box drifted a third time.** It reads "17 outcome-named…" against
a 21-mission catalog (verified via `gh api`). `docs/about.md` prescribes a count-free
canonical text — written after the second drift — and was never applied.

## P2 highlights (full detail in scope notes; all cheap)

- `runtime/pins.json` — `"witness": "live"` is undefined in `_about` (only `'source'` is
  defined); the orca entry's `commit`+`tag` adjacency reads as "tag points at commit"
  but the pinned commit is on a diverged pre-release line (the run report discloses
  this; the pin file doesn't); `tag` duplicates `version`. Also: `_about` credits pin-it
  with pack-pin maintenance that pin-it's SKILL.md never claims.
- The addyosmani pack pin is 17 commits behind upstream HEAD three days after witness
  (mattpocock and gstack pins equal upstream HEAD today); two touched skills include one
  declared ADOPTED-CURRENT.
- access-it frames "WCAG 2.2 AA (EAA / ADA / Section 508)" — those laws formally
  reference WCAG 2.1/2.0 (EN 301 549 v4.1.1, the 2.2-based version, is published but not
  yet OJ-cited); targeting 2.2 is the right engineering call, the parenthetical conflates
  target with legal reference. The 30-40% axe-core ceiling is supported (Deque coverage
  report) but carries no citation.
- README.md:47's "54–90% of plausible patches" statistic has no source;
  README.md:464's `readlink -f` diagnostic is non-portable to macOS and its fallback
  reports a correct install as broken; runtime/scripts citations of `orchestration.ts`
  are ambiguous upstream (three files; all mean `cli/specs/orchestration.ts`); one-way
  line-citation rot in a playbook (`upstream-contribution.md:58` cites `verify.py:409`,
  a blank line — the repo's own anti-line-rot doctrine).
- Post-1.4.200, five runtime policies still anchor claims "at v1.4.199" with no
  per-claim re-witness status (disclosed debt — the pin-it-266 park register exists, but
  only dispatch-lifecycle records which probes were re-witnessed).
- Test hygiene: tautological loop (test_decisions.py:154-158), permanently vacuous test
  (test_evals.py:262-278), bare `assert` under `-O` (test_verify.py:330), temp-resource
  leaks (test_verify_gate.py:71, test_verify.py:927-931), a misleadingly-named test
  (test_sandbox_doctor.py:47-57), and untested executor failure legs in verify.py
  (worktree-add failure, no-op control, timeout rc=124, clean-phase nonzero).
- evals/routing.json has zero negative fixtures for absorb-it, document-it, floor-it,
  field-test-it; IDs silently skip 33–37.
- Assorted: evidence-run.py append race (no locking), inventory.py path traversal +
  dead `in_fence` state + `--at` report-relative breakage, verify.py non-`-z` diff
  parsing and missing leading-dash guards on manifest SHAs, egress.py UnicodeDecodeError
  off-contract exit, verify-gate.sh `--event` with no value exits 1 off-contract,
  floor_guard.py per-finding re-import, print-settings-snippet.sh unescaped sed
  substitution, duplicated ledger-header sentences in pin-it/reshape-it,
  merge-serialization's mandated payload-JSON shape unacknowledged against
  dispatch-lifecycle's PowerShell warning.

## Online verification results (what held up)

- **Orca pin is current and the mechanics citations are exact.** stablyai/orca v1.4.200
  (tagged 2026-09-11) is still the latest release; ~20 line-precise citations across
  dispatch-lifecycle, orca-dag-semantics, gate-classification, liveness-resume,
  merge-serialization, and sandbox-policy were checked against upstream source at the
  pinned commit — every one landed (schema v40, the three-code refusal contract,
  600s/1800s ask timeouts, nine send types, the v1.4.200 worker-start readiness change
  corroborated by release notes).
- **Upstream pack characterizations are accurate.** mattpocock/skills and garrytan/gstack
  pins equal upstream HEAD today; the TDD refactor split, router-per-pack claim, gstack's
  fail-open Stop gate, review-army, and command-name clashes all verified against current
  sources.
- **agentskills.io spec conformance is total** across all 21 missions (allowlisted keys,
  name/dir match, description/compatibility limits) and machine-enforced by validate.py.
- **EU AI Act claims are accurate post-Digital-Omnibus** (Reg. (EU) 2026/1744 dates
  verified against multiple independent sources), and evidence-manifest.md:112 is
  commendably honest about what the presence check does not establish.
- **The gitleaks pin was re-verified byte-exact**: the pinned sha256 matches the actual
  `gitleaks_8.30.1_linux_x64.tar.gz` asset, and 8.30.1 is the current release. The
  planted-credential canary is a real negative control.
- **No mission-identity paraphrases found.** Measured with the catalog's own scorer, all
  confusable pairs score ≤0.16 against a 0.50 warn bar, and the six-point divergences are
  genuine.

## What is genuinely good

The fail-closed discipline is pervasive and *practiced*, not asserted: admission-before-
execution in verify.py, single-read evidence snapshotting, the gitleaks canary, decoy/
stripped install oracles that test the oracle, planted-mutant guards on the test suite
itself, REFUSAL-reason pinning so a right verdict for a wrong reason scores nothing, and
dormant mechanisms (deny-hook unregistered, egress uncalled, dispatch-sign dormant)
honestly declared and test-pinned rather than oversold. Ed25519 is correct beyond the
reference vectors (canonical-S, small-order rejection). The run archive's binding column
is truthful against the live verifier, including a run that records its own mis-pinned
inventory rather than re-hashing to look clean. Policy↔code fidelity is high where it
matters most: every core safety mechanic claimed in policy exists in a script whose
behavior matches the text.

## Overall assessment

The catalog is in good health and largely lives up to its own bar — the enforcement
chain is real, currently green in CI, and the external claims (Orca mechanics, upstream
packs, spec conformance, compliance dates, tool pins) survived independent online
re-verification to a degree rare for self-describing repos. The defects concentrate at
three seams, all self-inflicted instances of the drift this repo exists to catch:

1. **Platform seam** — the macOS-red suite and the symlink-prefix gap it exposes
   (P0-1), days before the Node-20 CI pins hard-break (P1-19): the two time-critical
   items.
2. **Contract seam** — missions vs runtime policies: the attest-it floor hole, ledger-row
   schema violations, the unsourced ≥10% floor, quorum mechanics that don't exist, and
   evals that grade narration (P1-8 through P1-18).
3. **Evidence seam** — bench traps that don't isolate what they measure, a stale demo
   transcript, and a completion ledger contradicting authoritative state (P1-21 to
   P1-28).

**Suggested fix order:** (1) run_report resolve-both-sides + scratch-root resolution
[un-reds the suite, closes the evasion]; (2) CI action bumps [before 2026-09-23];
(3) bundle.py out-dir guard + deny-hook sudo-tee [blast-radius holes];
(4) evidence-manifest attest-it class + ledger-schema validator check + ≥10% floor
[contract seam]; (5) ledger/About-box/README staleness sweep [mechanical];
(6) bench REFUSAL-map extension + demo transcript re-record [evidence seam].

## Issue index (filed 2026-09-14)

Every finding above is tracked as a GitHub issue: P0-1 → **#349**; P1-2…P1-28 →
**#350…#376** (finding N → issue 348+N); P2 groups → **#377** pins.json hygiene,
**#378** pack-pin freshness, **#379** unsourced/imprecise claims, **#380** citation rot,
**#381** test-suite hygiene, **#382** runtime-script hardening batch, **#383**
mission-layer consistency nits, **#384** bench/demo polish, **#385** historical-docs
polish, **#386** optional manifest-signing hardening. Labels: sev:S0 = P0,
sev:S1 = P1, sev:S2 = P2.
