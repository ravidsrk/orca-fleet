# Run submission guide

You ran a mission. This guide turns that run into a promotion: a run bundle
submitted as a PR, machine-checked for binding, then cited by the mission's
`proof:` advance. Start from the [call for runs](call-for-runs.md) to pick a
mission that still needs one.

## Prerequisites

Three hard requirements, same as running any mission
([getting-started](getting-started.md)):

1. **The Orca app + `orca` CLI, running.** `orca status --json` must show the
   runtime `ready`. Record the Orca version your run used; the catalog's
   pinned runtime is the `orca` entry in
   [pins.json](../runtime/pins.json) — if your installed Orca differs, say
   so in the report (a drift NOTE, not a refusal).
2. **`git` and `gh`**, authenticated (`gh auth status` succeeds). Your
   evidence must live in commits in this repository — a run whose artifacts
   were never retained here stays recorded history and supports no tier.
3. **Python 3.13**, stdlib only. The catalog gates and the runtime scripts
   below need no venv.

Plus the mission's own tooling from its `SKILL.md` `compatibility:` field
(gitleaks for harden-it, a measurement path for speed-it, and so on).

## The bundle format

A submission is one PR adding all three parts. Two live under `docs/runs/`
(the bindable core — what the checker checks and what `proof_evidence:`
will cite); one under `docs/reports/` (the envelope — the stable,
mission-addressed summary future runners copy).

| # | Path | What it is |
|---|---|---|
| 1 | `docs/runs/<YYYY-MM-DD>-<mission>-<self-run\|external-run>.md` | The bindable report. Exactly one `RUN:` header, the mission's terminal state and convergence proof, the verifier transcript, and the run-close integrity inventory. Start from [TEMPLATE](runs/TEMPLATE.md). |
| 2 | `docs/runs/<YYYY-MM-DD>-<mission>-<self-run\|external-run>/` | The run's own artifact directory: the graded `manifest.json` (with the `commands[]` ledger), `negctrl.txt`, verifier and gate transcripts. Every file here is hashed by the inventory. |
| 3 | `docs/reports/<mission>-<self-run\|external-run>/` | The envelope: `README.md` (the run's story in one page, the `RUN:` coordinates, a pointer to part 1) plus `negctrl.txt` (the same negative-control transcript as part 2, so the envelope reads standalone). Either tier spelling is accepted (`selfrun` and `self-run` both route); the `RUN:` header itself must use the hyphenated frontmatter spelling. |

Also required: one row in the [run archive](runs/README.md) index table
linking the mission name to the part-1 filename — a test fails the build
if a dated report has no row — and the runner-credit row (below).

The `RUN:` header is the report's identity. One line, every field, no
placeholders:

```text
RUN: mission=<mission> tier=<self-run|external-run> inventory_at=<commit> manifest=docs/runs/<date>-<mission>.../<manifest>.json verifier=<GREEN|RED> waves=<n>
```

`mission=` must name a catalog mission; `tier=` is exactly `self-run` or
`external-run` (a run-together spelling fails the promotion gate);
`inventory_at=` is the commit whose tree holds your frozen evidence;
`manifest=` is the graded manifest inside your run's own directory;
`verifier=` is the outcome you actually recorded (a RED is honest — a solo
run cannot manufacture an independent approver); `waves=` is required for
mutating missions (one WIP-curve row per wave, per the template).

## Step by step

Run commands from the catalog root (`/tmp` fixtures excepted). Replace
`<mission>`, `<tier>`, and `<date>` throughout.

1. **Copy the template.** `cp docs/runs/TEMPLATE.md
   docs/runs/<date>-<mission>-<tier>.md` and
   `mkdir docs/runs/<date>-<mission>-<tier>/`. Fill every section as the
   run produces it; explain any inapplicable section instead of deleting it.
2. **Run the mission** per its `SKILL.md`, keeping evidence in the run
   directory as you go. Record the fixed point (BASE branch and SHA, frozen
   spec digest), the Orca version, and every human gate with who decided it.
3. **Record the verifier through the recorder** — never by hand. A tier
   costs a command execution, not a sentence about one:
   `python3 runtime/scripts/evidence-run.py --label verifier --manifest
   <run-dir>/<manifest>.json --artifact <run-dir>/verifier.txt -- python3
   runtime/scripts/verify.py --manifest <run-dir>/<manifest>.json
   --contract-source <frozen-contract> --contract-digest <digest>
   --unit-class <mutation|report-only|planning>`
   Paste the command and its exit code into the report verbatim, RED
   included. The manifest's `commands[]` ledger now carries the run the
   binder will demand.
4. **Freeze and commit the evidence.**
   `git add <run-dir>/ && git commit -m "run(<mission>): <date> evidence"`.
   Note the commit SHA — that is your `inventory_at=`.
5. **Write the inventory, then re-derive it at the pinned commit.**
   List your artifacts under a `## Run-close integrity inventory (sha256)`
   heading (placeholder hashes are fine — the tool fills them), then:
   `python3 runtime/scripts/inventory.py write docs/runs/<date>-<mission>-<tier>.md`
   and `python3 runtime/scripts/inventory.py check
   docs/runs/<date>-<mission>-<tier>.md --at <inventory_at>`.
   Require zero mismatches, at least one verified path, the graded
   manifest among the hashed paths, and none of your run's own artifacts
   absent there.
6. **Run the intake check locally** (the one verification command — what
   "binding" means is defined in the next section):
   `python3 scripts/bind_check.py --base origin/main`
   It routes every report your branch changed to the binder and fails with
   the binder's output. Green here is green in CI.
7. **Write the envelope** (`docs/reports/<mission>-<tier>/README.md` +
   `negctrl.txt`), add the **run-archive index row**, add the
   **runner-credit row**, commit, and open the PR. CI's `bind-check` job
   re-runs step 6 on the PR range.

## What "binding" means

Binding means the report's claims re-derive from git objects instead of
trusting prose: the `RUN:` header names a commit that exists in this
repository, the graded manifest exists at that commit inside the run's own
directory, the manifest's `commands[]` ledger records `verify.py` actually
running against that manifest (a `cmd_sha256` over its own command line
and a working-tree fingerprint resolving to a real tree object here), the
body shows that same invocation with its exit code, and the integrity
inventory re-hashes every listed artifact — the graded manifest included —
at the named commit with zero mismatches. The checker is
[run_report.py](../runtime/scripts/run_report.py); it does not re-run the
verifier or independently establish its verdict — clean-environment test
reruns and review-authority lookups stay coordinator-owned.

Verify with this one command, run on your submission branch:

```bash
python3 scripts/bind_check.py --base origin/main
```

The single-report form underneath it (mission and tier are the claim the
report is checked against):
`python3 runtime/scripts/run_report.py docs/runs/<date>-<mission>-<tier>.md
--mission <mission> --tier <tier>`

## After you submit

CI's `bind-check` job runs the intake check on the PR range and fails with
the binder's output when the bundle does not bind — fix the report, not
the binder, and push again. When the bundle is green, a maintainer reviews
the run on its evidence and files the promotion: the mission's
`metadata.proof:` advances to your tier with `metadata.proof_evidence:`
citing your part-1 report, which the `validate` workflow re-binds before
merge. Your envelope stays as the mission's worked example, credited per
the convention below.

## Runner credit convention

Every accepted submission earns credit in three places, in this exact
shape. (Credit lives here and not in new `metadata:` keys because the
validator allowlists frontmatter keys — an invented key fails the build.
The report is one hop from `metadata.proof_evidence:`, which cites it.)

1. **The run report**, in the header table next to the coordinator row:
   `| Runner | <Full Name> (@<handle>) · <org, or "independent"> |`
   plus `| Run PR | <this-PR-url> |` once the number exists.
2. **The envelope README**, under a `## Runner credit` heading: the same
   name line, plus one line naming the bindable core filename.
3. **The CHANGELOG promotion entry**, appended to the mission's tier-advance
   line: `run by <Full Name> (@<handle>)`.

The first application is the `## Runner credit` section in the prove-it
envelope (runner unconfirmed — the August demonstration predates the
convention; #410 confirms it). Every later submission carries the rows
above with confirmed values, and Phase-1 promotions adopt them per the
retrofit notes below.

## Retrofit notes for the Phase-1 reports (acceptance: bundle conformance)

The Phase-1 promotion issues (#409, #410, #411) were in flight when this
guide was written — no promotion PRs open, no commits on their branches —
so the bundle format is drafted against the on-disk report directories,
and the deltas below are what conformance costs each one. Verified at
`main` 8784aa9.

Conformance status: **neither on-disk report conforms yet.** Both lack a
`RUN:` header entirely (the binder refuses at its first leg), both lack a
graded manifest (each directory holds only `README.md` + `negctrl.txt`, so
`manifest=` has nothing to point at and the #286 execution leg fails for
want of a `commands[]` ledger), and neither has a bindable
`docs/runs/<date>-<mission>-<tier>.md` core — which promotion additionally
requires, because `scripts/validate.py` only accepts `proof_evidence:`
paths under `docs/runs/`. What already holds: both inventory tables parse
as real inventory entries and re-derive today
(`inventory.py check` reports 1 verified, 0 mismatched, 0 missing on each).

Per report:

- `harden-it` (#409, re-scoped to `self-run` per the #212 plan): author
  a FRESH envelope at `docs/reports/harden-it-selfrun/` (`README.md` +
  `negctrl.txt`) plus the bindable
  `docs/runs/<date>-harden-it-selfrun.md` core — `RUN:` header
  (`mission=harden-it`, `tier=self-run`), the audit → exploit → fix →
  re-attack → clean re-audit loop against `runtime/scripts/` with the
  verifier run through `evidence-run.py` for real, a committed graded
  manifest pinned by the inventory, and the runner-credit row. The
  gitleaks-control transcript carries over as one unit of that run. The
  existing [external-run envelope](reports/harden-it-externalrun/README.md)
  stays the historical scoped-demo record — it is NOT the promotion
  envelope, and a `self-run` core beside it fails intake (the check
  matches normalized core/envelope tiers).
- `prove-it` ([envelope](reports/prove-it-selfrun/README.md), #410): same
  five steps (`mission=prove-it`, `tier=self-run`); the PF-1 pinned mutant
  is likewise one unit of the multi-criterion self-run, and as a mutating
  mission the core needs `waves=` plus one WIP-curve row per wave. The PF-1
  `negctrl.txt` transcript carries over unchanged.
- `clean-sweep` (#411): no envelope exists — author both halves from the
  `docs/runs/2026-09-14-clean-sweep-tracker/` source material per that
  issue, following this guide's steps in order.

Process notes for the Phase-1 branches: fold the runner-credit row into the
promotion PR (convention above); update the
[call for runs](call-for-runs.md) mission list in the same PR (a test holds
that list equal to the doctrine-only set, so a promotion without the list
update fails the build).

## Paraphrase checklist (for the second-person test)

Acceptance for this guide is a reviewer paraphrase: one person who did not
write it reads it once and answers these without asking questions. If any
answer needs the guide re-read twice, the guide — not the reviewer — failed.

1. What three paths does one submission PR add, and which one does
   `proof_evidence:` cite?
2. What command proves your bundle binds before you open the PR?
3. Your `RUN:` header says `tier=selfrun` and the bot goes red. What is the
   fix, in one sentence?
4. Where does your name go when the run is accepted, and why not in the
   mission's frontmatter?
