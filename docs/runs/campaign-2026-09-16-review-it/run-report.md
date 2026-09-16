# Run report — review-it self-run, 2026-09-16 (campaign self-test)

Self-test of the `review-it` mission against orca-fleet itself: a read-only,
SHA-bound verdict on PR #445 (the `origin/main` tip at run time). Evidence in
this run's own `docs/runs/campaign-2026-09-16-review-it/` directory. Placed
inside the run directory per the campaign brief (deviation from TEMPLATE.md's
sibling-`.md` placement, recorded in Deviations).

```
RUN: mission=review-it tier=doctrine-only inventory_at=fa97fcf7c1152b8949892ae8f26a466b588ee8f4 manifest=docs/runs/campaign-2026-09-16-review-it/manifest.json verifier=RED waves=1
```

| Field | Value |
|---|---|
| Mission | `review-it` — mission source revision `c46d4b3f` (`skills/review-it/SKILL.md` @ the reviewed tip), installed location: this repo (self-run) |
| Tier claimed | `doctrine-only`; run kind: `self-run` (catalog). No proof promotion claimed or applied (frontmatter untouched). |
| Target | `ravidsrk/orca-fleet` PR #445 "docs(#417): mission-chaining exercise report (stopped chain, published)", MERGED |
| Fixed point | fp `6390743815f8f435181fa410cce374587128b30a` ... reviewed `c46d4b3f3371e41408aed19e54476fa194c20b42` (origin/main tip; wtree `3d39ff3709a3e95c1ba7b535d6f2dc6858ed3055`); frozen spec `criteria.md` (issue #417 AC-1..AC-5) digest `911b464d…9c7febb2` |
| Coordinator / workers | workflow child (solo session, Muse Spark) · worker profiles `PROFILE=ro` (no workers dispatched — recursive dispatch forbidden; sequential same-session passes) · TASK pack `matt` (acceptance axes) + `addy` (risk lenses), never co-mounted |
| Orca | `orca status --json` → app `running: true`, `orca --version` = `1.4.203`; orchestration dispatch not used (see Deviations) |
| Human gates | outward verdict post (one-way gate): NO grant sought or given → nothing posted |

## Terminal state

Mission terminal: **GO** (zero Critical, zero Required). Per-axis worst:
Standards 1 Nit; Spec FYI; Test-adequacy FYI; Security CLEAN; Privacy CLEAN;
Data-migration N/A; Perf CLEAN; API-contract + a11y gate-off; Simplification
none. Full verdict: `verdict.md`. (review-it has no BUILD/PR/BOT ledger rows;
the verdict bound to `reviewed_sha` is the terminal.)

## Convergence proof

| Mission clause | Evidence |
|---|---|
| verdict at a named fixed point | fp + reviewed_sha pinned in `pin.md`; `verdict.md` binds to `c46d4b3f` |
| every axis reported, no cross-rerank | `axis-standards.md`, `axis-spec.md`, `axis-test-adequacy.md` (matt); `lens-risk.md` (addy: security/privacy/data-migration ran, perf ran bounded, api/a11y gate-off recorded) |
| every finding quotes its line + severity | triage anti-FP gate: 1 Nit + 6 FYIs, all line-quoted (`triage.md`); nothing below the gated bar reported |
| evidence manifest, report-only fields | `manifest.json` (verdict binds to `head_sha`; NC class analogue = source-binding re-check) |
| no code modified | `git status` at run close shows only the new run directory untracked-then-committed; target files untouched; preflight `--mode readonly` OK |

## Pipeline evidence (per phase)

| Phase | Command / action | Result | Evidence |
|---|---|---|---|
| PIN | checkout `campaign/review-it-selftest` @ `origin/main`; preflight readonly; fp=merge-base, reviewed=tip; non-empty diff check (28 files, 828+) | OK | `transcripts/pin.txt`, `pin.md` |
| SPEC SOURCE | search order → originating issue #417 AC (first hit); PR body corroboration; both fetched via `guard_text.py` | AC-1..AC-5 frozen | `criteria.md`, `transcripts/declaration.txt` |
| ACCEPTANCE-REVIEW | 3 sequential isolated passes (matt): standards / spec / test-adequacy (static; blind-fix expectation pre-written) | 1 Nit, 3 FYIs | `axis-*.md` |
| RISK-REVIEW | `diff_scope.py --json --strict` (exit 0, no unmatched); NEVER_GATE lenses + bounded perf (addy); gate-offs recorded | CLEAN / N/A | `lens-risk.md`, `transcripts/diff-scope.json`, `transcripts/secret-scan.txt` |
| TRIAGE | gated mode; hard exclusions; active verification by reads; variant greps | 1 Nit + 6 FYIs; 0 unverified | `triage.md` |
| AGGREGATE + VERDICT | side-by-side, no rerank, no boosts; GO bound to reviewed_sha | GO | `verdict.md` |
| RE-DERIVATION | inventory re-hash; bundle verify + SHA/wtree/diff/seed checks in `/tmp` clone (reads only, no execution) | 12/12 claims re-derive | `transcripts/inventory-rehash.txt`, `transcripts/after-restore.txt` |

## Verifier outcome (recorded exactly)

Actual invocation (same manifest; coordinator's authoritative contract inputs):

`python3 runtime/scripts/verify.py --manifest docs/runs/campaign-2026-09-16-review-it/manifest.json --contract-source docs/runs/campaign-2026-09-16-review-it/criteria.md --contract-digest 911b464dd825891d25826d6def894940a797d1b470f6a47f60589c6a9c7febb2 --unit-class report-only`

Output and exit code (verbatim, RED kept RED; full text also in
`transcripts/verifier.txt`):

```
FAIL: report-only unit changed code ['docs/reports/chaining-2026-09-16/leg1/manifest-f3.json', 'docs/reports/chaining-2026-09-16/leg1/manifest-f5.json', 'docs/reports/chaining-2026-09-16/leg1/manifest-f6.json', 'docs/reports/chaining-2026-09-16/leg1/manifest-leg1.json', 'docs/reports/chaining-2026-09-16/leg1/seed-notes.py', 'docs/reports/chaining-2026-09-16/leg1/seed-test_notes.py', 'docs/reports/chaining-2026-09-16/leg1/target-417.bundle'] and carries no signed dispatch record. unit_class arrives from the environment the worker controls, so this single value drops the negative control, the intent packet, lighting legality and reviewer_mode from a unit that changed behaviour. Verify it as a mutation, or have the coordinator sign the downgrade (#310)
verify: 1 invariant(s) failed — unit is NOT done
NOTE: --base not given — ancestry check skipped (pre-merge/offline)
```

exit code: 2.

Reading: every leg passes except check 14 (class-downgrade). That check diffs
`base_sha..head_sha` and refuses non-prose suffixes — but for a review, that
range is the REVIEWED subject, and PR #445's subject legitimately contains
its own JSON manifests, seed `.py` fixtures, and the `.bundle` artifact. The
check reads reviewed-range files as unit-changed code. This run itself
changed no code (its own files are docs-only; `git status` at close shows
only the new run directory). Scope, SHAs, redaction, and source-binding legs
all pass. An earlier invocation also failed redaction on this run's own
`lens-risk.md` (my prose documenting the grep pattern self-tripped
`inline-credential`); that evidence was re-emitted clean and the re-run is
the one pasted above.

The RED is the honest machine outcome for an unsupervised report-only unit
whose reviewed subject contains non-prose files; it does not alter the review
verdict (GO), which is bound to the reviewed SHA by evidence, not by this
gate. No waiver was selected to make the run green.

## WIP-curve protocol row (mutating self-runs)

Inapplicable: report-only mission, no builders/reviewers/WIP to measure
(`attention-budget` requires the curve only for mutating self-runs). `waves=1`
(one solo pass sequence).

## Deviations and lessons (recorded, not hidden)

- Solo run, no Orca workers: the workflow-child execution contract forbids
  recursive agent dispatch, so acceptance axes and risk lenses ran as
  sequential same-session passes (matt/addy routers kept separate by phase,
  never co-mounted) instead of isolated fresh-context `PROFILE=ro` workers.
  Recorded as `reviewer_mode=instructed-isolation` + "self-verified — no
  independent verifier" on every finding (triage §5). Authorship independence
  holds (reviewer wrote none of PR #445); session independence does not.
- `docs/DECISIONS.md` lens-tally lines NOT appended (report-only boundary);
  run-local equivalent kept in `lens-tally.md`.
- This report lives inside the run directory per the campaign brief, not as a
  `docs/runs/*.md` sibling per TEMPLATE.md.
- Nothing was posted to PR #445 (the run's one outward action is a one-way
  gate; no human grant exists). Permission boundary held.
- Lesson: `verify.py` check 14 models `base_sha..head_sha` as unit-changed
  code; for a review whose subject includes fixtures/artifacts (`.py`,
  `.bundle`), an unsupervised report-only manifest goes RED through no fault
  of the run. A coordinator-signed dispatch record (or a reviewed-range
  exemption) is the way through — filed as review feedback, not applied here.

## Run-close integrity inventory (sha256)

| Artifact | sha256 | producer |
|---|---|---|
| `docs/runs/campaign-2026-09-16-review-it/axis-spec.md` | `8fe002637545b09fded03a862161f9692fce36bdfe269834df66d7d921bf5365` | workflow child 2026-09-16 |
| `docs/runs/campaign-2026-09-16-review-it/axis-standards.md` | `fb5ab9a456fa79688b4cfcaa88296ab0bcf772ab271682d63c85976af56b6827` | workflow child 2026-09-16 |
| `docs/runs/campaign-2026-09-16-review-it/axis-test-adequacy.md` | `d150d96883c1100eb6c0245564af4e5a2daf7d6d3c7c48d7e26a4bbfb47ed803` | workflow child 2026-09-16 |
| `docs/runs/campaign-2026-09-16-review-it/criteria.md` | `911b464dd825891d25826d6def894940a797d1b470f6a47f60589c6a9c7febb2` | workflow child 2026-09-16 |
| `docs/runs/campaign-2026-09-16-review-it/lens-risk.md` | `b1f0796b5605591970105d2e36d7b6eb8e6edd11ee7d8cbaf3ef7036e890b86b` | workflow child 2026-09-16 |
| `docs/runs/campaign-2026-09-16-review-it/lens-tally.md` | `00870551cbd738e7227d138a8bd0ecc2e1dd37c910c444fb28897611edd17537` | workflow child 2026-09-16 |
| `docs/runs/campaign-2026-09-16-review-it/manifest.json` | `ca5ff9bd536c6ff2d25cea7e0eb76b3f7bfc37f136f2f69db50c75d39c314eb4` | workflow child 2026-09-16 |
| `docs/runs/campaign-2026-09-16-review-it/pin.md` | `ff9c7eb1607ac608ec21d1e8a7c1dfd4a77ba7f758e1b568a068108b8646d95f` | workflow child 2026-09-16 |
| `docs/runs/campaign-2026-09-16-review-it/transcripts/after-restore.txt` | `9f44cb98b79cb091e0f824b4cabd8f859469315b5a925dea656a11135fec1006` | workflow child 2026-09-16 |
| `docs/runs/campaign-2026-09-16-review-it/transcripts/declaration.txt` | `51d642cabb7f64a95c9fab533b91692bb63e094f57c582469e8a9449dfa84bad` | workflow child 2026-09-16 |
| `docs/runs/campaign-2026-09-16-review-it/transcripts/diff-scope.json` | `0f7f337e160caf7569de7dbcb490cd75663e4c31c80f472e9e39c9933917afc9` | workflow child 2026-09-16 |
| `docs/runs/campaign-2026-09-16-review-it/transcripts/followups.txt` | `c141839f36812e2d8eabc8308aa7031e67c527d3c26fa9e61cd3f743772f57dd` | workflow child 2026-09-16 |
| `docs/runs/campaign-2026-09-16-review-it/transcripts/gates.txt` | `cea8fd01578444b306f22a8abd16bf040e72c9d8a5a7b0e266af035a0ef3c4d5` | workflow child 2026-09-16 |
| `docs/runs/campaign-2026-09-16-review-it/transcripts/inventory-rehash.txt` | `455bf4a279cb92489a87d4fc2b6c70867c9572eb013f7455ddf60e23e01ad962` | workflow child 2026-09-16 |
| `docs/runs/campaign-2026-09-16-review-it/transcripts/pin.txt` | `cbe0db8a685458c97d769af4766416b7fc74d43c045730a4ba8417c36ac36881` | workflow child 2026-09-16 |
| `docs/runs/campaign-2026-09-16-review-it/transcripts/recorded-bundle-verify.txt` | `e3d9efd006cd3a35bb590c638febe438b177ea5df6050bd3d62288e4265f10d2` | workflow child 2026-09-16 |
| `docs/runs/campaign-2026-09-16-review-it/transcripts/recorded-scope.json` | `80fd58241c166a26e9dceec40c0a647bf934de22ea0838577185b1f776ea418b` | workflow child 2026-09-16 |
| `docs/runs/campaign-2026-09-16-review-it/transcripts/recorded-secret-scan.txt` | `c8f1b024066aa3320f0b4457337418cf9413240c24ef08a45722766daca9e611` | workflow child 2026-09-16 |
| `docs/runs/campaign-2026-09-16-review-it/transcripts/secret-scan.txt` | `1ad3c81a17a2e611553d91fb31e7e44fcd02ae98b863e17d956364498f182628` | workflow child 2026-09-16 |
| `docs/runs/campaign-2026-09-16-review-it/transcripts/verifier.txt` | `d483132c8498d5a06672325e6cdaf2bbb655b5808bce6d13ddfd862d50b05f53` | workflow child 2026-09-16 |
| `docs/runs/campaign-2026-09-16-review-it/triage.md` | `43dd52d7faf31fcf43737f7bb09ac1cd0bf5f7481465f0de9af673f2b32c134b` | workflow child 2026-09-16 |
| `docs/runs/campaign-2026-09-16-review-it/verdict.md` | `daad407adda0079a763c0b0228d873404b389726f2f7db120d7bfb4257d8922e` | workflow child 2026-09-16 |

`python3 runtime/scripts/inventory.py write <this report>`
`python3 runtime/scripts/inventory.py check <this report>`
`python3 runtime/scripts/inventory.py check <this report> --at <inventory_at>`

Require zero mismatches, ≥1 verified path, none of this run's artifacts
absent; the graded manifest among the hashed paths.

## Gates

Project gates at the final head (recorded with exact output/exits in
`transcripts/gates.txt`):

`python3 scripts/validate.py`
`python3 -m unittest discover -s tests`
`python3 runtime/scripts/proof_status.py --check`

## Catalog proof promotion

Not attempted. `review-it` stays `doctrine-only`; its frontmatter is
untouched. This report is recorded history in the campaign branch. (Per #417's
own out-of-scope pattern, promotions go through the intake.)

## Evidence binding

Tier `doctrine-only` by choice (no promotion claimed). `inventory_at` names
the evidence commit on branch `campaign/review-it-selftest` (unpushed, per
brief: no push, no PRs, no merge). The manifest lives in this run's own
directory; the inventory re-hashes at `inventory_at`.
