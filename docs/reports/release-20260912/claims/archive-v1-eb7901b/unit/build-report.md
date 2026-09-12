# Claims repair — built for review, 2026-09-12

Completed the three scoped documentation fixes; no merge, release, legal-conformance claim,
independent review or green verifier verdict is claimed. The coordinator explicitly accepted
source-bound walkthrough evidence for this builder completion only (coordinator-direction.txt).

## Identity and authorization

- Integration base: codex/release-audit-20260912.
- Frozen base: 9eb2e6f6171845100b969e2d59e65b0d34ddf86f.
- Base tree: 6209f7b9f291327e9e38a279f412a87acea07e41.
- Builder branch: codex/release-claims-20260912 (fresh branch renamed after clean-status check).
- Head: eb7901be372b6091ed0d239c2c1073caeb2ba405.
- Head tree: 163a4027932403fac9253e5af7d9406a9ad4b951.
- Commit author/committer: Ravindra Kumar <ravidsrk@gmail.com>; no coauthor trailer.
- Contract: docs/reports/release-20260912/claims/contract.json, copied byte-for-byte from
  /tmp/orca-release-audit-20260912/claims-contract.json.
- Contract digest: sha256:71d81d280bd089562ec05396b9d2e3b0b27e5eb7729c5b63672cd1b5627e9b87.
- Lane A, lighting=lit; fixtures and reversible documentation only. No additional agents/packs.

The boundary plan was recorded in this scratch report before implementation: rewrite the legal
mapping as supporting change evidence; distinguish check ownership; align oncall with its actual
mission. Scope was the three frozen docs, with git revert as rollback. Fixtures exercised local
presence checks and hook event handling only; no live alerts, dangerous launches, credentials,
remote writes or deployment actions occurred. Sources/audit reports were treated as data.

## Changes and criterion evidence

Exact old/new source is retained in source-bindings.json and claims.patch; walkthrough.md holds
the pre-fix RED and post-fix GREEN semantic assessments with counterexamples and positive cases.

| Criterion | Correction | Red / green / control |
|---|---|---|
| AC-1 (C8) | Provenance is supporting change evidence; actual logging, retention, marking and disclosures require separate operational evidence. Scoped applicability dates are sourced. | Old guarantee contradicted by real presence-check acceptance with four strings and no logger/marking (probe exit 0 confirms counterexample). Missing retention is rejected; 3 existing provenance tests pass. Corrected copy describes exactly that boundary. Semantic replay unsupported; independent meaning review pending. |
| AC-2 (C11) | Distribution distinguishes deterministic checks, worker-attested records, coordinator-owned reruns and advisory native hooks. | Local Stop without manifest returns 0; TaskCompleted without manifest returns 2. Installing hooks creates no off-worker verifier. Existing run_report source confirms worker-owned ledger/no rerun. Corrected copy retains local-check benefits without claiming independence. 19 navigation tests pass; semantic meaning assessed by walkthrough. |
| AC-3 (C10) | Plan targets bounded staging paths/questions and OPERABLE/OPERABLE-WITH-PARKED, including signals, receipts, induced failure and both fresh blind oracle runs/removal RED. | Executable terminal-state comparison against actual mission declarations fails before fix (exit 1) and passes after (exit 0). Walkthrough rejects an incident resolved using old telemetry and accepts a healthy service needing instrumentation; a failure guessable after removal cannot certify operability. Actual blind-worker mission runs were not performed. |

Official sources independently fetched and read on 2026-09-12:
- https://eur-lex.europa.eu/eli/reg/2024/1689/2026-07-27/eng — Articles 12, 26, 50, 111, 113.
- https://digital-strategy.ec.europa.eu/en/faqs/navigating-ai-act — transparency and applicability.
The consolidated Act separates Chapter III category dates (December 2027/August 2028) from
Article 50's general August 2026 date, with Article 111(4)'s existing-system transition. The
mapping states scope/role/category/exceptions rather than declaring a deployment compliant.
Official-source receipts, raw-fetch hashes and extracted sections are retained; raw HTML remains
in the coordinator scratch directory. The dated index listings were not re-audited.

## Tests and actual verifier outcome

Python 3.13.15, Ruff 0.16.5, Gitleaks 8.30.1. Real commands and exits are recorded through
evidence-run; command-history.json preserves the original observations unchanged, including
scratch artifact locations, commit and tree fingerprints. The manifest maps copied artifacts to
repo-relative hashed paths. No recorded command SHA or tree was rewritten after committing.

| Check | Exit | Result |
|---|---|---|
| Provenance/hook counterexample probes | 0 / 0 | Counterexamples reproduced; valid local rejection controls retained |
| Oncall terminal-state probe before/after | 1 / 0 | Actual RESOLVED mismatch then legal OPERABLE states |
| Existing ProvenanceCheck tests | 0 | 3 passed |
| Existing docs navigation tests | 0 | 19 passed |
| Badge fixture comparison | 0 | Both failing and passing fixtures produce identical “1 passing” badge |
| python3 scripts/validate.py | 0 | Structural floor passes; no generated metadata refresh required |
| Pinned ruff check . | 0 | Passed |
| Pinned python -m unittest discover -s tests | 1 | 1069 tests, exactly 2 preexisting failures, 144.871 seconds |
| Pinned validate.py after commit | 0 | Recorder fingerprint equals head tree |
| verify.py --execute-nc, lit, no waiver | 2 | Unreviewed, pending reviewer mode, and unsupported/surviving semantic control |

Retained baseline failures (not changed by this unit):
- test_verify.EndToEndMutationGreen.test_credential_in_a_commands_artifact_fails_the_unit
- test_verify.EndToEndMutationGreen.test_credential_in_an_artifact_fails_the_unit

The full suite ran once after final production changes and before the commit. Its recorded
working-tree fingerprint equals the committed head tree. No production/test changes followed.
The final artifact-only lint is recorded separately; no redundant full-suite run was made.

The verifier used the repo-relative frozen contract copy and the exact authorized NC command:
/tmp/orca-release-audit-20260912/ci-venv/bin/python scripts/validate.py.
It restored exactly docs/compliance-provenance.md, docs/distribution.md and docs/runs/README.md
from the frozen base in its disposable checkout. That command exited 0: **SURVIVED**, unsupported
for semantic proof. The verifier refused this as TAUTOLOGICAL. Because control remained green,
it did not proceed to its second clean checkout; the separately recorded current validator was
green. No killed semantic mutant or independent verifier success is claimed. verifier-input.json
is the exact input it graded; verifier.txt is its output. The final manifest adds that observation.

GitHub APPROVED review, fresh independent spec/standards assessment and the coordinator's final
clean-checkout verification remain pending. There is no --no-gh waiver and no fabricated review.

## Adjacent triage and limits

The passing-badge issue is VALID: the real generator counts methods then labels them “passing”
and green. Failing/passing fixture bodies yield identical badges. CI does run unittest but neither
workflow publishes this badge from its result, and README reads main's static JSON directly.
See badge-triage.md for source anchors and full disposition. Proposed separate scope:
scripts/gen-badges.py, assets/badges/tests.json, and focused tests/test_validate.py expectations/
fixture tests; use neutral “discovered” inventory wording and preserve freshness checks. A
separate CI status badge would additionally touch README.md. Generator source was not changed.

Nearby older wording remains outside these assigned repairs: runtime/evidence-manifest.md's
optional-provenance rule and verify.py check_provenance docstring still use regulated-audit-record
language; docs/runs/README.md's opening “re-derives everything” remains broader than run_report.py's
stated bindings-only behavior. These require a coordinator scope decision, not silent expansion.
This unit does not certify whole-product public copy, run proof tiers, or deployment conformance.

## Files and evidence handoff

Committed: docs/compliance-provenance.md, docs/distribution.md, docs/runs/README.md, and the identical
contract.json under docs/reports/release-20260912/claims/. No generated/hot metadata files changed.

Other evidence is intentionally untracked in that report directory, with repo-relative SHA-256
entries in manifest.json and inventory.json. The coordinator should retain those bytes before
integration. This report is also stored at /tmp/orca-release-audit-20260912/claims-build-report.md.
The branch's tracked source is clean; built-for-review completion does not settle review/release.
