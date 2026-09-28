# Release-readiness review — 2026-09-28 @ ad1a0ed

Reviewed SHA: `ad1a0eda74bf6f20517a91ab09322c8218d28f41` (`main`, 2026-09-28, merge of PR #507).
Every `file:line` below is at that SHA unless it names an Orca path. Upstream Orca was cloned
and read at two points: the catalog pin **v1.4.215** (tag `083f583a53`, the build commit
`3eb1adec` in `runtime/pins.json`) and **main HEAD `2f8f4f576d`** (`v1.4.214-163`, 2026-09-28).
Read-only engagement: nothing in the repository changed except this file and the three lines
that link it. Every gate was executed, not read; every upstream claim was checked in Orca source.

The question asked was: *is orca-fleet ready to release to the public, what would it take, and
what should change.* The answer has three tiers, because "release" means three different things
for this repository.

---

## 1. Verdict

**Ready to cut 0.7.0 this week. Not ready to announce that cut as a public beta until the
Tier B items in §8 land. Not ready for the 1.0 the repo's own checklist defines. Not ready to
invite Linux users at all until one bug is fixed.**

The version cut and the announcement are different acts. Cutting 0.7.0 is release hygiene the
tree already supports; announcing it to strangers is what the P0 and P1 findings below gate.

- **As an MIT catalog on GitHub** (which it already is): the engineering bar is unusually high.
  Every frozen gate in `CONSTRAINTS.md` is green in CI at this SHA. Locally, every gate this
  container could run was green once three container artifacts were accounted for (a 3.11
  interpreter on `PATH`, a root uid, and a clone that was shallow when the first suite run
  began); the coverage floor was read from CI only. The verifier scores 0/20 false-done on
  its trap corpus, the secret scan over 1,446 commits is clean, and the three proof reports
  that claim a tier really do re-hash at the commits they name. What is missing is release
  hygiene: the published version is `0.6.1` from 2026-09-09, **1,372 commits behind HEAD**, and
  the repository has **zero GitHub Releases** despite nine annotated tags.
- **As a public beta you tell strangers to install**: four things block an honest announcement,
  and none of them is part of the 0.7.0 cut.
  Every runtime script hardcodes the `orca` command, which on Linux is `orca-ide` (and bare
  `orca` is the GNOME screen reader), so the fleet has never run on the platform most servers
  use. The installer refuses Python below 3.13 while every script compiles and the suite passes
  on 3.11. The only install path that wires the completion gate (the plugin) has never had an
  install transcript recorded. And the README's opening promise ("Come back to an
  evidence-verified end state") is carried by a catalog where 19 of 22 missions are
  `doctrine-only`, zero are `external-run`, and the flagship `ship-it` has never completed a
  bound run.
- **As 1.0** per `docs/release-1.0-checklist.md`: the checklist cannot pass as written. Gate 1's
  own grep returns 0 where it expects 4, Gate 1 requires an issue that is still open and that
  says it does not gate launch, and Gate 2 requires `harden-it` at `external-run` when it is
  `self-run` and the roadmap epic re-scoped it. The epic (#407) was closed as completed with
  those two Definition-of-Done items unmet on the letter.

The single most important thing to internalize: the repository's own doctrine is that a
hand-typed number is a claim with no mechanism, and the review found five such claims stale
(the Orca pin floor in the README, the proof-tier sentence in the README, the opening line of
the call-for-runs page, the schema version in a runtime policy, and the 1.0 checklist's Gate 1
command). None is large. All are exactly the failure the repo says it exists to refuse.

## 2. Method

- Cloned `stablyai/orca` (30,398 files) and checked out both the pin and HEAD. Two delegated
  audits ran against those trees: an inventory of the CLI and orchestration model (§7), and an
  audit of every `orca` invocation the fleet's runtime scripts construct (§6).
- Ran every gate in `CONSTRAINTS.md` plus the negative-control demo, the eval suites and the
  badge check in this container (Debian, Python 3.11.15 on `PATH`, 3.13.12 available, root uid,
  clone shallow at start and unshallowed mid-run). Where the container differs from CI the
  difference is named, never hidden.
- Pulled GitHub state through the API: issues, PRs, releases, tags, and the last ten Actions
  runs of `validate`, `install` and `alert-on-failure` on `main`.
- Walked `docs/release-1.0-checklist.md` gate by gate against live state.
- Read the run archive, the self-test campaign rollup, the chaining report, the completion
  ledger and the two prior reviews so that nothing already closed is re-raised as new.

## 3. Baseline gates at ad1a0ed

| Gate | Command | Result here | CI |
|---|---|---|---|
| D1 suite | `python3 -m unittest discover -s tests` (3.11, shallow at start) | 2,281 ran, 21 failed, 26 skipped, 446 s. 15 failures need full git history (the clone was shallow when the run began: tag/commit checks, `inventory --at`, the release-cut walkthrough); 5 are `install.sh` refusing the `PATH` `python3` (3.11); 1 is the negative-control transcript diff caused by running as root | green at `ad1a0ed` ([run 36389011526](https://github.com/ravidsrk/orca-fleet/actions/runs/36389011526)) |
| D1 suite | same, Python 3.13.12, full history | 2,281 ran, 6 failed, 26 skipped, 477 s. All 6 are container artifacts: 5 are `install.sh` refusing the `PATH` `python3` (still 3.11 even when 3.13 runs the suite; the same five pass with a 3.13 shim, next row) and 1 is the root-uid transcript diff (P2-1). Effectively green | green |
| D1 installer | `tests.test_install_status` with a 3.13 `python3` on `PATH`; then `sh scripts/install.sh` into a scratch `HOME` | 5/5 OK; installer exit 0, 22 symlinks, 2 substrate warnings | install workflow green at `ad1a0ed` |
| D2 catalog | `python3 scripts/validate.py` | 22/22 valid; separation holds; evals valid (2.4 s) | green |
| D3 lint | `ruff check scripts runtime/scripts tests bench demo` (0.15.8; CI pins 0.16.7) | clean | green |
| D4 secrets | gitleaks 8.30.1, sha256-verified download, `detect --source .` on full history | 1,446 commits, no leaks | green |
| D5 routing | `scripts/eval.py run --suite routing --threshold 1.0` | 95/95; `--suite all`: 86 per-skill evals valid | green |
| D6 proof honesty | `proof_status.py --check`; `run_report.py` | 19 doctrine-only, 3 self-run, 0 external-run; 3 reports bind (clean-sweep, harden-it, prove-it) | green |
| D7 bundle | `scripts/bundle.py --check` | 22 self-contained missions | green |
| D8 verifier soundness | `bench/vf-bench/gate.py` | PASS on full history: false-done 0/20, valid 3/3, skipped 0. On the shallow clone it FAILED with one skipped trap, which is the gate refusing correctly | green |
| D9 coverage | `coverage combine && coverage report` (fail_under 80) | not run here (7-minute suite under a tracer); CI `gates` green at this SHA implies the floor holds | green |
| demo | `sh demo/negative-control/run.sh` | PASS: self-scorer GREEN, verify.py RED on the dropped criterion. One extra advisory NOTE line appears under root, which would fail CI's byte diff (§5, P2-1) | green |
| badges | `scripts/gen-badges.py --check` | ok | green |
| syntax floor | `py_compile` of all 97 catalog Python files | 0 failures on 3.10, 3.11, 3.12 and 3.13 | n/a |

CI on `main` was red twice in the week before this SHA, for a reason that is not the code (§5, P1-7).

## 4. The 1.0 checklist, gate by gate

`docs/release-1.0-checklist.md` "DEFINES the release; it does not perform it". Performing it at
`ad1a0ed`:

| Gate | Requirement as written | Live state | Passes? |
|---|---|---|---|
| 0 | tree clean, validate + suite green, CI bound green at the SHA | all true; `validate` run 36389011526 is `success` at `ad1a0ed` | yes |
| 1 | `grep -c '^Status: ANSWERED' …/gate-batch.md` = 4 | **0**. #419 migrated the file to `gate-batch.json` and re-renders answers as `**Answered 2026-09-16:**`; the JSON reads G1 answered, G2 answered, G3 waived, G4 overtaken | **no** (stale command) |
| 1 | #408 CLOSED, #386 CLOSED, #235 CLOSED, PR #406 MERGED | #408 closed, #386 closed, **#235 OPEN** (its own body: "Does **not** gate launch"), #406 not re-checked | **no** |
| 2 | harden-it `external-run`, prove-it `self-run`, clean-sweep `self-run`, all binding | harden-it is **`self-run`** (#409 was re-scoped per #407's table; the checklist was not); the other two hold and all three bind | **no** |
| 3 | vf-bench 0/20, demo PASS, both wired in CI | all true | yes |
| 4 | one-command install in README and distribution.md, install workflow bound green | true; install run 36389011508 `success` at `ad1a0ed` | yes |
| 5 | #416 closed, pin `live` and witnessed ≥ 2026-09-16, #417 closed, chaining report indexed | pin `live` 2026-09-28 (v1.4.215); #417 closed; `docs/reports/chaining-2026-09-16/` exists. The chain ran one leg to `NOT-DRY` with the verifier `UNAVAILABLE` and leg 2 `NOT-STARTED`. Exercised, not proven | yes on the letter |
| 6 | #418, #419 closed; a later run consumes both tools | both closed and merged. No run report records a live `watchdog.py` invocation during supervision; the only `gate-batch.json` is the migrated 2026-09-14 file | "used" unmet |
| mechanics | a 1.0 cut per `docs/ops.md` | no cut since 0.6.1; `docs/releases.json` `preparing: null` | n/a |

Two of the failures are the checklist's, not the product's (the Gate 1 grep, the Gate 2 tier),
and one is a policy contradiction (#235 gates 1.0 here and "does not gate launch" in its own
issue). Reconciling the checklist is a one-hour task, listed in §8.

## 5. Findings

Severity: **P0** blocks a public announcement; **P1** should land before calling it a beta;
**P2** hygiene.

### P0-1. Every runtime script hardcodes `orca`; on Linux the command is `orca-ide`

Eight operator tools call `subprocess.run(["orca", *argv, "--json"])` verbatim
(`runtime/scripts/check_reply.py:154`, `hitl_ask.py:133`, `search_sessions.py:202`,
`send_msg.py:149`, `task_ops.py:129`, `terminal_ops.py:220`, `worker_ops.py:275`,
`worktree_ops.py:123`), and `spawn_worker.sh` calls `orca` at `:157`, `:451-454`, `:529`,
`:778`, `:975` and `:1074`. Nothing under `runtime/scripts/` reads `ORCA_CLI_COMMAND` or knows
the name `orca-ide`; only `scripts/install.sh:54-55` does.

Upstream, the Linux executable is `orca-ide` by construction: `LINUX_CLI_COMMAND_NAME =
'orca-ide'` (`src/main/cli/bundled-cli-launcher-path.ts:4`), `executableName: 'orca-ide'`
(`config/electron-builder.config.cjs:592`), the `.deb`/`.rpm` assets are named `orca-ide_*`
(`config/scripts/verify-release-required-assets.mjs`), and the runtime's own compatibility
resolver returns `'orca-ide'` on Linux (`src/cli/handlers/orchestration/runtime-compatibility.ts:8`).
Orca's shared skill stub says why: "on Linux outside an Orca-managed terminal, use `orca-ide`.
Never run bare `orca` there — outside Orca's terminals it normally resolves to the GNOME Orca
screen reader (`/usr/bin/orca`) and starts speech on the user's machine"
(`skill-stubs/_shared/cli-resolution.md:12-14`). The fleet's doctrine knows this
(`runtime/dispatch-lifecycle.md:72`) and calls the screen-reader rationale "unwitnessed env lore".
It is upstream's stated reason, and the tooling ignores it either way.

Consequence: on a Linux host every operator tool fails with "orca: command not found", or worse
launches a screen reader; every recorded field run is on the maintainer's Mac (the witness
binary is `Orca-1.4.215-arm64-mac.zip`; the pin-it park register defers "a Windows/Linux host"
to other hosts).

Fix: one resolver, used everywhere, in the order upstream documents (`ORCA_CLI_COMMAND` →
`orca-dev` in a dev checkout → `orca-ide` on Linux and WSL → `orca`), plus a contract test that
greps `runtime/scripts/` for a bare `"orca"` argv and fails. Then one recorded `review-it` on an
Ubuntu host driven by `orca-ide serve` (§7 has the recipe) before any Linux user is invited.

### P0-2. The published version is 19 days and 1,372 commits behind, and there are no Releases

`.claude-plugin/plugin.json` says `0.6.1` (cut 2026-09-09). `git rev-list v0.6.1..HEAD` is
1,372 commits. `CHANGELOG.md` `[Unreleased]` carries a 22nd mission, eight new operator tools,
the watchdog, gate-batch tooling, the chaining exercise, the floor gates, the external-run intake
and all three proof promotions. The GitHub Releases page is empty (`list_releases` → `[]`)
although nine annotated tags exist. Every external index (`docs/distribution.md`) is serving
copy that predates this delta; buildwithclaude still shows a 10-mission blurb.

Fix: run the four `docs/ops.md` release blocks with `RELEASE_VERSION=0.7.0`, then publish a
GitHub Release per tag (the release notes are already written: they are the CHANGELOG
sections). Plugin consumers copy the repo at whatever ref the marketplace resolves, so a tagged,
released tree is also what makes "which version did you install" answerable in a bug report.

### P0-3. Five hand-typed claims are stale, in the surfaces strangers read first

| Where | Says | True at `ad1a0ed` |
|---|---|---|
| `README.md:28`, `README.md:117` | Orca floor "v1.4.200" | `runtime/pins.json` is v1.4.215 |
| `docs/distribution.md:50` | "currently v1.4.200 (warn)"; observed 1.4.203 | same |
| `README.md:214` | "Today `clean-sweep` and `prove-it` read `self-run`" | harden-it has read `self-run` since 2026-09-21 |
| `docs/call-for-runs.md:3-5` | "Every mission in this catalog stands at `doctrine-only`" | 19 of 22 do; the list below it is machine-checked, the sentence is not |
| `docs/release-1.0-checklist.md` Gate 1 | `grep -c '^Status: ANSWERED'` = 4 | 0 (format changed in #419) |

`check_doc_counts` already lints catalog counts out of these files. Extend it, or
`gen-badges.py`, to the pin version and the proof rollup, so these sentences are generated the
way the activation-load table is. A test that fails when `README.md` names a version other than
`pins.json`'s is a twenty-line change.

### P0-4. The 2026-09-28 re-pin reported "zero drift" and missed one

`runtime/orca-dag-semantics.md:6` reads "Current schema line: v41 at the pin
(`contract-constants.ts:21`, ee1c5220); HEAD is v42". `ee1c5220` is the **v1.4.209** build
commit. At the new pin, v1.4.215, `SCHEMA_VERSION = 42`
(`src/main/runtime/orchestration/db/contract-constants.ts:22`). The pin advanced; the sentence
anchored to the old pin did not. Small, but it is a runtime-policy claim about the binary that
the run's drift table did not carry a row for, so the "STATIC (20) re-anchored" line in
`docs/runs/2026-09-28-pin-it-500.md` overstates what was re-anchored.

Two upstream changes since the pin are also worth a register row now rather than in December:
commit `7438bc80f5` (#23325) redirects mail addressed to `dispatch:<id>` to `run:<child>` when
that worker now leads a child Run (`recipient_run_bound_redirect`, HEAD
`src/main/runtime/rpc/methods/orchestration/messaging/recipient-routing.ts:20-134`), which
touches the addressing rules in `dispatch-lifecycle.md` and `merge-serialization.md`; and
`45f3512a33` (#22468) adds `dsh` as an agent that `worker-start --agent` accepts, which the
spawn roster does not list. Neither is in a tagged release yet. Both belong in #508's register.

### P1-1. The Python 3.13 floor is an installer policy, not a code requirement

`scripts/install.sh:46-48` dies below 3.13; `README.md:28,124-125`, `docs/getting-started.md:50-52`
and `docs/run-submission-guide.md:19` repeat it. Measured: all 97 catalog Python files
byte-compile on 3.10, 3.11, 3.12 and 3.13; the full suite on 3.11 fails only where `install.sh`
refuses the interpreter or where this container lacks history; `docs/completion/STATUS.md`
already recorded "Cold start of the catalog gates = pass (also on Python 3.11)" on 2026-09-02.
A grep for 3.12+ and 3.13+ features (PEP 695 generics and `type` aliases, `itertools.batched`,
`Path.walk`, `copy.replace`, `warnings.deprecated`, `@override`, `glob.translate`) across
`scripts/`, `runtime/scripts/`, `tests/` and `bench/` finds none; 3.11-only names
(`ExceptionGroup`, `StrEnum`, `datetime.UTC`, `tomllib`) are unused, and the three
`fromisoformat` call sites strip the `Z` themselves. What the code does need is 3.10: PEP 604
`X | None` annotations evaluated at definition time in `scripts/gen-badges.py`,
`scripts/eval.py:133,164,350` and `tests/test_evals.py:75-76`. The two 3.13-conditional spots
(`tests/test_run_report.py:122,139`, `runtime/scripts/run_report.py:268-285`) are guarded.
Nothing in the code needs 3.13; the real floor is 3.10.

Debian 12 ships 3.11, Ubuntu 24.04 ships 3.12, and neither Orca's headless guide nor most
servers put 3.13 on `PATH`. Either lower the floor to what the code needs and add a 3.11/3.12/3.13
matrix to `validate.yml` (cheap: the suite is stdlib-only), or state in one sentence why 3.13 is
required. A floor nobody can justify reads as a bug to a stranger.

*Resolution (#514):* the floor is now **3.11**, not 3.10. The code byte-compiles on 3.10 and the
scripts run there, but the suite has two 3.10-only failures on the test side
(`tests/test_run_report.py` passes `-X frozen_modules`, which 3.11 introduced, and
`tests/test_egress.py` observes a file mode through a pathlib accessor 3.10 lacks), and a floor
the suite cannot prove is not a floor. `install.sh` asks for ≥ 3.11 and `validate.yml` runs the
sharded suite on 3.11 and 3.12 beside the 3.13 lane.

### P1-2. The proof ladder does not yet support the headline

The README leads with "Give a mission a goal. Come back to an evidence-verified end state." At
this SHA: 19 of 22 missions are `doctrine-only`, 0 are `external-run`, and the two missions
`docs/getting-started.md` tells a first user to run are both `doctrine-only`. `ship-it`'s only
recorded run (2026-08-28) reached `PROMOTION_READY` without a verifier transcript; in the
2026-09-16 self-test campaign it "PARKED at entry (no input)". The one chaining exercise stopped
at leg 1 with `verifier=UNAVAILABLE`. Every run in the archive ran on the maintainer's Mac.

None of this is hidden; the repo is unusually honest about it, and the honesty gate works. But a
public reader sees the promise in line 18 and the tier in a guide three clicks away. Two changes:
put the `proof:` tier in the README catalog table as a column (the badge idea `distribution.md`
already sketches), and run **one** `ship-it` on an external repository to a bound `BUILT` before
the announcement. That single run is worth more than the next ten doctrine edits.

### P1-3. The substrate is experimental, daily-moving, and pinned quarterly

- Upstream marks orchestration **Experimental**: "Enable orchestration under Settings →
  Experimental before using these commands" (`docs/site/content/docs/cli/orchestration.mdx:12-15`).
  The runtime gate behind that setting could not be located in source and stays unverified.
- The CLI is a thin RPC client. Every orchestration verb needs a running Orca runtime on a local
  socket or a paired server; with none, `runtime_unavailable` and exit 1
  (`src/cli/runtime/metadata.ts:11-31`, `cli-error.ts:46-51`). On a server that means an
  AppImage plus Xvfb plus the Electron library set (`docs/reference/headless-linux-server.md`).
  The CLI is not on npm and has no standalone artifact.
- Upstream cut 23 stable tags in the 30 days to 2026-09-28 (v1.4.192 → v1.4.215). The fleet's
  re-pin cadence is "each minor or quarterly" (`runtime/orca-pin.md`); the next is 2026-12-28.
  The last two re-pins (2026-09-23, 2026-09-28) ran with the app **not running**, so every
  sender-bound probe is parked, and the maintainer's on-PATH app was 1.4.204 while the pin
  said 1.4.215.
- The CLI surface itself is stable across that range (§7: no spec, flag or gate-state change
  between v1.4.215 and HEAD in `src/cli/specs`), which is the good news.

Recommendation: a cheap nightly drift probe that needs no app (`orca-ide agent-context --json`,
`--help`, and `skills get orchestration --full` diffed against the receipts in
`docs/runs/2026-09-28-pin-it-500/`), and a stated support window in the README ("tested
against v1.4.209 through v1.4.215").

### P1-4. The safety envelope for a stranger's machine is a speed bump, and the README says so only in an FAQ

A `PROFILE=rw` worker launches with the agent's bypass flag (`--dangerously-skip-permissions`
for claude; `runtime/sandbox-policy.md:30-40`). Upstream is explicit that the worktree "is an
isolated checkout, not a security sandbox" (`docs/site/content/docs/agents/supported.mdx:12`)
and `worker-start` has no per-worker permission flag ("there is no flag for it",
`orchestration-worker-specs.ts:41`). The opt-in `ORCA_COORD_ALLOW_AUTONOMOUS_WRITE=1`
(`runtime/scripts/spawn_worker.sh:484-485`) is exported by the coordinator, which is an agent
following the mission text; no human-facing document tells a person to set it. `deny-hook.sh`
is unregistered by construction (#284), the native completion gate is advisory in-session
(`docs/verify-gate.md`), and signed dispatch is dormant because no `.orca/dispatch-pubkey` is
committed.

All of this is documented, and the README FAQ "Can a mission touch my default branch?" is the
most honest paragraph in the repository. For a public release it belongs at the top: a short
"What this will do on your machine" box (bypass-permission workers, PRs on your repo, worktrees
under your checkout, no merge to default) with the recommendation to run the first mission in a
VM or through the `offload-it` recipe.

### P1-5. The only gate-wired install path has never been witnessed

`docs/install.md` says the plugin path "has no recorded install transcript yet". It is the one
path where `hooks/hooks.json` fires (`${CLAUDE_PLUGIN_ROOT}`), and `plugin.json` carries no
`hooks` or `skills` keys, relying on directory convention. A plugin install copies the whole
repository: **54 MB** tracked, of which `docs/reports` is 14 MB, `docs/runs` 15 MB and
`assets/diagrams` 17 MB; the eight largest files are 0.6–1.5 MB JSON receipts under
`docs/reports/release-20260912/pin/`. `scripts/bundle.py` builds a self-contained `dist/`
(2.3 s, CI-checked) that is never published; #294 closed by deleting the `npx` instruction.

Fix: record one plugin install transcript as CF-02b (the claude CLI was absent in this
container, so it could not be done here); publish `dist/` on a release branch or tag so copy
installers have a target; move receipt trees that no navigation reaches out of the tree a
plugin copies, or exclude them if the plugin manifest ever supports it.

### P1-6. The 1.0 checklist and the roadmap disagree with each other

Detailed in §4: Gate 1's command cannot pass after #419, Gate 2 demands a tier #407 re-scoped,
#235 gates 1.0 here and says it gates nothing there, and #407 was closed as completed with
DoD items 1 and 2 unmet on the letter. A checklist that cannot be run is prose. Make it a
script (`scripts/release_check.py`) that runs every gate and prints PASS/FAIL, tested like the
rest, and let `docs/release-1.0-checklist.md` describe that script.

### P1-7. The alert path has no dead man's switch, and it was silent twice this week

`validate` on `main` failed on 2026-09-23 (`0e0ff771`, run 35892449330) and 2026-09-25
(`f78ef91e`, run 36146072394). In both, all four test shards and `vfbench` ended 2 s after
they started with `runner_id: 0` and no steps: no runner was ever assigned, so this is a
GitHub Actions or account-level incident, not a test failure. `alert-on-failure` ran for both
and **also** failed the same way (runs 36146082708, 36146084947, 35892460703, 35892475581), as
did every `alert-on-failure` run from 2026-09-23 15:32 to 2026-09-25 14:13 (#103–#112), including
for green `validate` runs. No `ci-failure` issue was filed; the newest one is #439 from
2026-09-16. `docs/ops.md` step 1 says the issue "is the alert". When Actions cannot start jobs,
there is no alert.

Fix, in two layers because they cover different outages. An in-repository scheduled workflow
that fails when the latest `validate` run on `main` is not `success` covers the narrower case
where Actions runs but a red `main` went unfiled (a broken alert workflow, a filter that did
not match, a `workflow_run` that never fired). It cannot cover the incident above, because it
needs the same runner that was never assigned. The no-runner case needs a check that lives
outside Actions: an external uptime monitor polling the Actions API for `main`'s latest
`validate` conclusion, or a cron on the maintainer's machine doing the same. Both layers plus a
note in `docs/ops.md` that a `failure` with no steps is an Actions incident to re-run, not a red
suite.

### P1-8. Community and legal surface for a public project

- No `CODE_OF_CONDUCT.md`, no `.github/ISSUE_TEMPLATE`, no PR template, no `CODEOWNERS`.
  `.github/` holds only workflows and the tool lock.
- No affiliation statement. The name and every page lean on "Orca"; nothing says the project is
  independent of Stably. One sentence in the README and `docs/about.md` avoids the question.
- The three upstream packs are MIT (LICENSE files fetched 2026-09-28: gstack "Copyright (c)
  2026 Garry Tan"; mattpocock/skills "Copyright (c) 2026 Matt Pocock"; addyosmani/agent-skills
  "Copyright (c) 2025 Addy Osmani"). Every playbook names the recipe it adapts, which is good
  practice, but MIT asks for the notice to travel with substantial portions. A
  `THIRD_PARTY_NOTICES.md` listing the four upstreams (Orca included) and their notices costs
  nothing and pre-empts the question.
- Bus factor 1 is documented in `docs/ops.md`. A public beta can live with it; 1.0 should name a
  second person with write access, even if only for the 2 a.m. path.

### P2-1. The negative-control demo's byte diff depends on the uid

Running `demo/negative-control/run.sh` as root adds `NOTE: authority: advisory (git at
/usr/bin/git is worker-writable)` to the transcript, so `head-to-head.txt` no longer matches and
`test_the_committed_transcript_matches_a_fresh_run_modulo_timestamp` fails. Contributors in
containers hit this; CI does not. Normalize NOTE lines the way the timestamp is normalized.

### P2-2. A first-time user has no idea what a run costs

Nothing states wall-clock or token expectations. The one narrated run
(`docs/guides/anatomy-of-a-run.md`) spans more than 14 hours and five builder panes. A line
per mission guide ("a small ship-it: N worker sessions, M hours, stops at PROMOTION_READY")
is what a reader needs before typing "ship this".

### P2-3. Counts that look like they should agree do not

The test badge says "2116 in source"; `unittest` reports 2,281 ran (subtests and generated
cases). Both are correct by their own definition; a reader compares them. Label the badge
"test functions".

### P2-4. Activation load

Every mission activates at ~33,000 tokens, deliberately, against a 5,000-token community
recommendation (`ARCHITECTURE.md` says so plainly). For a public beta this is a cost the guide
should state next to the number: roughly how much of a 200k context a mission consumes before
the first dispatch.

## 6. Runtime scripts against the real CLI

What the fleet's tooling actually executes, checked verb by verb and flag by flag against the
command specs at v1.4.215 (`src/cli/specs/*.ts`, where every command declares its
`allowedFlags`):

| Script | Orca invocations it constructs | At v1.4.215 |
|---|---|---|
| `task_ops.py` | `orchestration task-create --spec --task-title --display-name --deps --parent --run --from --retry-request`; `task-update --id --status --result --run --from --retry-request` | every verb and flag present (`specs/orchestration.ts`) |
| `worker_ops.py` | `worker-list --run --terminal-state --include-remote --cursor --limit`; `worker-show --dispatch`; `worker-read --dispatch --source --cursor --limit` | present (`orchestration-worker-specs.ts`) |
| `check_reply.py` | `check --terminal --run --ack --unread --peek --all --types --format --wait --timeout-ms --retry-request`; `reply --id --body --run --from --retry-request` | present |
| `hitl_ask.py` | `ask --question` or `--resume`, `--to --run --options --timeout-ms --from --retry-request` | present; `--options` is CSV here and a JSON array on `gate-create`, which the fleet doctrine already warns about |
| `send_msg.py` | `send --to --run --from --subject --body --type --priority --thread-id --payload --task-id --dispatch-id --dispatch-capability --outcome --files-modified --report-path --phase --retry-request` | present, including the typed `--report-path` and `--files-modified` the doctrine prefers over raw `--payload` |
| `terminal_ops.py` | `terminal create --worktree --title --command --shell --focus`; `terminal list --worktree --limit --include-visual-layouts`; `terminal read --terminal --cursor --limit --screen`; `terminal show` | present (`specs/core.ts:196-254`) |
| `worktree_ops.py` | `worktree list --repo --limit`; `worktree show --worktree` | present |
| `search_sessions.py` | `search --query --scope --fresh --limit --cursor --agent --path --since --sort --debug --index-status` | present (`specs/search.ts:12-`) |
| `spawn_worker.sh` | `orca --version`; `vm recipe doctor <recipe> [--provision]`; `orchestration task-list --run --from [--brief]`; `task-create`; `worker-start --task --worktree --name --agent --run --from --on --timeout-ms --retry-of --retry-request [--environment --pairing-code]`; `request-show --request`; `terminal create`; `dispatch --task --to --inject --dry-run --return-preamble`; `terminal wait --terminal --for tui-idle --timeout-ms`; `terminal read --screen` | present; the agent-side flags it appends (`--dangerously-skip-permissions`, `--yolo`, `--sandbox`, `--permission-mode`, `--auto`) are the agents' own, taken from Orca's YOLO map |

So the argv shapes are correct at the pin, which agrees with the 2026-09-28 pin-it drift table.
Two smaller things the table hides: three bare flags (`--brief` on `task-list`, `--peek` and
`--format` on `check`) are not in Orca's boolean-flag set and parse correctly only because the
fleet always follows them with another `--flag` (`src/cli/args.ts:98-101`), which is fragile if
a positional is ever placed after them; and `worker-list`, `worker-stop`, `worker-abandon`,
`worker-release` and `worker-retain` accept no `--from`, which `worker_ops.py` correctly never
passes (a hand receipt from the 1.4.200 witness, `helper-release.json`, shows the exit 1 that
passing it earns). Three things the table cannot show:

- **The command name is wrong on Linux** (P0-1). Every row above spells the executable `orca`.
- **The suite never touches a real binary.** Every operator-tool test puts a shell stub named
  `orca` on `PATH` that logs its argv and `cat`s a canned JSON reply
  (`tests/test_spawn_worker.py:45-47`, `tests/test_worker_ops.py:45`, `tests/test_task_ops.py:34`,
  `tests/test_check_reply.py:38`, `tests/test_terminal_ops.py:42`); there is no `skipUnless`
  lane that runs against an installed Orca. That is the right hermeticity for CI, and it means
  the tests prove the wrapper's argv and its fail-closed parsing, not that Orca accepts the
  call. The only real-binary receipts in the tree are the pin-it captures
  (`docs/runs/2026-09-28-pin-it-500/`: `agent-context-1.4.215.json`, `help-root-1.4.215.txt`,
  the served guides, and probe JSON taken with the app **not** running, so every sender-bound
  verb returned `runtime_unavailable`). The underlying verbs were driven by hand against
  1.4.200 (about a hundred receipts under `docs/reports/release-20260912/pin/receipts/`), and
  `spawn_worker.sh` reached a real binary exactly once there, refusing at its `PROFILE=rw`
  gate after `orca --version`. No operator tool has a recorded live exchange with a running
  runtime, and against v1.4.215 specifically no fleet script has been executed live at all.
- **The security-relevant scripts hold up to a read.** No `shell=True` anywhere under
  `runtime/scripts/` or `scripts/` (the one mention is `verify.py:1014` saying so). The vendored
  `ed25519.py` states that it is the public-domain reference port, not constant-time, verified
  against the RFC 8032 vectors, hardened against `S >= L` malleability, non-canonical points
  and small-order keys, and swappable for libsodium; that is an honest description for a
  scheme that signs a few hundred bytes of dispatch record and is dormant until a public key
  is committed; key handling in `dispatch-sign.py` is careful (`os.urandom`, mode 0600 at
  creation, refusal of unignored in-repo paths, custody re-asserted at use). The verifier's
  custody probe is POSIX-only (`os.geteuid`, `stat` mode bits, an `lstat` symlink walk at
  `verify.py:781-808`), which is why a root uid turns every authority advisory and why none
  of this runs on Windows. `deny-hook.sh` fails closed on unparseable input, a missing
  `python3`, a symlink chain deeper than 32 hops and an unresolvable worktree bound. Both
  scripts were the subject of the 2026-09-21 `harden-it` self-run (six rounds, eleven findings
  closed) and this review did not re-audit them line by line.

## 7. The substrate: what Orca actually is at v1.4.215

Facts a fleet author needs, verified in source (paths under the Orca checkout):

- **Shape.** One desktop Electron app that also runs headless (`orca serve`). The CLI is a
  Node entrypoint executed by the Electron binary (`resources/linux/bin/orca-ide` runs
  `ELECTRON_RUN_AS_NODE=1 <app> app.asar.unpacked/out/cli/index.js`). Every command except
  `help`, `--version`, `agent-context`, `skills list|get|install|update`, `environment *`,
  `host list`, `serve` and `profile state *` is an RPC to the running runtime over a local socket
  or a paired WebSocket (`src/cli/runtime/client.ts:84-175`; the local-only exceptions are named
  in each command's spec notes under `src/cli/specs/`).
- **Orchestration nouns.** Run (namespace + coordinator inbox; never schedules), Task, Dispatch
  (the one authoritative attempt). All verbs live under `orca orchestration`: `run-create|use|
  current|list|show`, `task-create|list|update`, `worker-start|show|read|stop|abandon|release|
  retain|list`, `dispatch`, `dispatch-show`, `send`, `check`, `reply`, `inbox`, `ask`,
  `request-show`, `gate-create|resolve|list`, `reset`; `coordinator-start|stop` and the aliases
  `run|run-stop` are retired no-ops that return recovery text (`src/cli/specs/orchestration.ts`,
  `src/cli/handler-group-manifest.ts:103-138`).
- **Exact state vocabularies.** Task `pending|ready|dispatched|completed|failed|blocked`;
  Dispatch `pending|dispatched|completed|failed|circuit_broken` (breaks after 3 failures); Gate
  `pending|resolved|timeout` (no `unanswered`, which the fleet already corrected); question
  `pending|answered|closed`; worker terminal `active|reclaimable|retained|release_pending|
  release_unknown|released` plus `unsupervised` for inject lanes; liveness `live|unverifiable|
  exited` (`src/main/runtime/orchestration/types.ts`). Message types: `status dispatch
  worker_done merge_ready escalation handoff decision_gate question heartbeat`.
- **Delivery.** A consuming `check` returns the Run's oldest FIFO batch of up to 50 messages and
  replays it until `--ack`; every mutation takes `--retry-request <id>`; `ask` times out into a
  pending question resumed by `--resume <id>`. All of this matches the fleet's
  `orca-dag-semantics.md` and `dispatch-lifecycle.md`.
- **Permissions.** No profiles. Every supported agent launches with its bypass flag
  (`src/shared/tui-agent-permissions.ts:7-34`); the only switch is the global Settings → Agents
  → Yolo|Manual. `worker-start` cannot request a mode. The fleet's `PROFILE=ro` lane therefore
  correctly avoids `worker-start` and uses `terminal create` + `dispatch --inject`.
- **Storage and versions.** SQLite `orchestration.db` under the app's userData; `SCHEMA_VERSION
  = 42` at the pin (`db/contract-constants.ts:22`); `ORCHESTRATION_CONTRACT_VERSION = 1`,
  `RUNTIME_PROTOCOL_VERSION = 3`, additive changes behind about 85 named `*.v1` capabilities
  (`src/shared/protocol-version.ts`). Mixed client/host versions are documented as normal.
- **Distribution.** Release assets are AppImage (x64/arm64), `orca-ide` `.deb`/`.rpm`, a Windows
  installer and macOS zip/dmg; a macOS Homebrew cask and an AUR package exist; nothing on npm.
  Headless Linux: AppImage (or its extraction) + Xvfb + the Electron library set, `serve --port
  --pairing-address`, one `orca_server_ready` JSON line on stdout, a systemd unit
  (`docs/reference/headless-linux-server.md`).
- **Cadence and drift.** 1,113 tags since v1.0.1 (2026-03-19); 23 stable tags in the last 30
  days. `git diff v1.4.215..HEAD -- src/cli skill-guides/orchestration* skills/orchestration
  skill-stubs` touches six files, none of them specs, guides or stubs: no command, flag or
  gate-state change. Server-side, the recipient redirection in P0-4 is the one behavioral change
  a coordinator would notice.
- **Stability markers.** Orchestration is documented as Experimental; `computer` is the only
  CLI area upstream calls "stable enough for skills to build against"; no CHANGELOG file exists
  in the repository (release notes live on GitHub Releases).

Bottom line for the fleet: the contract the doctrine binds to is real, exact and currently
stable, but it is an experimental feature of a product that ships daily, and the fleet's own
re-witness loop runs quarterly, from one machine, without the app running. That gap, not the
doctrine's accuracy, is the substrate risk.

## 8. What it takes to release

Tier A is the version cut. Tier B is what an announcement waits on; a 0.7.0 tag can exist
before Tier B lands, a "public beta" post cannot.

### Tier A — cut 0.7.0 (one to two days, no new runs)

1. P0-3: fix the five stale sentences; add the pin-version and proof-rollup lint so they cannot
   return.
2. P0-4: re-anchor `orca-dag-semantics.md:6`; add the two post-pin upstream changes to #508.
3. P1-6: reconcile `docs/release-1.0-checklist.md` with #407's actual scope (Gate 1 command,
   Gate 2 tier, #235's status).
4. P1-8: `THIRD_PARTY_NOTICES.md`, an affiliation sentence in `README.md` and `docs/about.md`,
   `CODE_OF_CONDUCT.md`, issue and PR templates.
5. P0-2: run the four `docs/ops.md` release blocks as 0.7.0; publish GitHub Releases for all ten
   tags with the CHANGELOG sections as notes.

### Tier B — public beta (one to two weeks)

6. P0-1: the CLI-name resolver in every script, the contract test, and one recorded `review-it`
   on an Ubuntu host driven by `orca-ide serve`. Until this lands, the README should say
   "macOS only; Linux untested".
7. P1-1: decide the Python floor on evidence and add the CI matrix.
8. P1-4: the "What this will do on your machine" box at the top of the README.
9. P1-5: one plugin-install transcript; publish `dist/`; shrink or relocate the receipt trees.
10. P1-7: the in-repository health workflow, the external check for the no-runner case, and
    the ops note.
11. P1-2 (half): the `proof:` column in the README catalog table.

### Tier C — 1.0 (weeks to months, mostly runs)

12. One external-run `ship-it` bound to a `BUILT`, and one external-run `review-it` with retained
    artifacts. These two runs are the release; everything else is packaging.
13. `harden-it` to `external-run`, or the checklist re-scoped to say why `self-run` is the bar.
14. #235 submissions, then a re-index request so the public copy matches the tree.
15. The nightly upstream surface probe (P1-3) and a stated support window.
16. An executable release checklist and a second maintainer in `CODEOWNERS`.

## 9. What is genuinely good

- The verifier is real and adversarially tested: 0/20 false-done on a trap corpus with a valid
  control, a negative-control demo that CI byte-diffs, executed reverts in throwaway worktrees,
  and a trust boundary the docs state more honestly than most security products do.
- The proof-honesty gate cannot be talked past: a tier above `doctrine-only` needs a report that
  re-hashes at the commit it names, and three do.
- The doctrine matches the binary. Of the runtime-mechanics claims spot-checked against Orca
  source (gate states, delivery batching, ack replay, retry-request, ask resume, worker release
  exit codes, the Linux rename, the YOLO map, the absence of sandbox profiles) all were correct
  except the one schema line in P0-4.
- The catalog gates are fast and hermetic: validation in 2 seconds, a stdlib-only suite, CI
  tools pinned by hash, a hash-verified secret scanner with a planted-credential control.
- Every prior review's findings are closed with a mechanism, and the CHANGELOG says what each
  mechanism refuses. That is rarer than the verifier.

## 10. Evidence

Commands run in this container at `ad1a0ed`, in order, with the result each produced:

```
python3 scripts/validate.py                                 # 22/22 valid, 2.4 s
python3 -m unittest discover -s tests                       # 3.11, shallow start: 2281 ran, 21 F, 26 S, 446 s
/usr/bin/python3.13 -m unittest discover -s tests           # full history: see §3
PATH=<3.13 shim>:$PATH python3 -m unittest tests.test_install_status   # 5/5 OK
PATH=<3.13 shim>:$PATH HOME=<scratch> sh scripts/install.sh # exit 0, 22 symlinks, 2 warnings
ruff check scripts runtime/scripts tests bench demo         # clean (0.15.8)
gitleaks detect --redact --no-banner --source .             # 8.30.1, sha256 verified; 1446 commits, no leaks
python3 scripts/eval.py run --suite routing --threshold 1.0 # 95/95
python3 scripts/eval.py run --suite all                     # 86 per-skill evals
python3 runtime/scripts/proof_status.py --check             # 19 / 3 / 0, exit 0
python3 runtime/scripts/run_report.py                       # 3 bound
python3 scripts/bundle.py --check                           # 22 self-contained
python3 bench/vf-bench/gate.py                              # shallow: FAIL (1 skipped); full: PASS 0/20
sh demo/negative-control/run.sh                             # PASS (+1 advisory NOTE under root)
python3 scripts/gen-badges.py --check                       # ok
for v in 3.10 3.11 3.12 3.13: python$v -m py_compile <97 files>   # 0 failures each
git rev-list v0.6.1..HEAD --count                           # 1372
grep -c '^Status: ANSWERED' docs/runs/2026-09-14-clean-sweep-tracker/gate-batch.md   # 0
```

GitHub, read through the API on 2026-09-28: 0 releases; 9 tags; 0 open PRs; 2 open issues (#235,
#508); `validate` run 36389011526 and `install` run 36389011508 `success` at `ad1a0ed`;
`validate` runs 35892449330 and 36146072394 `failure` with no runner assigned; `alert-on-failure`
runs #103–#112 `failure`; newest `ci-failure` issue #439 (2026-09-16).

Orca checkouts: `stablyai/orca` at tag `v1.4.215` (`083f583a53`) and `main` `2f8f4f576d`
(`v1.4.214-163`), both cloned 2026-09-28. Upstream LICENSE files for the three worker packs were
fetched the same day.
