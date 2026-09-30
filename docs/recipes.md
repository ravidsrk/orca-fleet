# Prompt recipes for developers

[Documentation](README.md) · [Mission selector](missions/README.md#choose-by-task)

These are example requests to paste into your **coding-agent session in the target project**.
They are not shell commands or recorded runs. Replace the paths, identifiers and commands with
your project's values. Complete [setup](getting-started.md#prerequisites) first.

A useful request names the target, the expected behavior, the evidence to check, and where the
run should stop. You can supply a known test command; the coordinator still checks the baseline
and confirms the scope required by the mission.

## Review an existing PR

Use [review-it](missions/review-it.md) when you want findings and a verdict.

```text
Review PR <owner/repo>#123 against its description and issue #120.
Check the retry behavior, compatibility and test coverage. Return a GO/NO-GO
verdict bound to the reviewed commit, with a quoted line for each finding.
```

Provide a PR URL or number, its base branch and the spec or issue it implements. `GO` means
the reviewed change has no Critical or Required findings; acting on it is a separate decision.
If a new commit changes the reviewed content, request a fresh review.

## Build a bounded feature

Use [ship-it](missions/ship-it.md) when the requested behavior is clear enough to specify.

```text
Ship this: add GET /healthz to the API using the existing router.
Return version and database connectivity; return 503 when the database is unavailable.
Cover both responses with integration tests. Use pnpm test as the baseline command.
Keep the existing deployment configuration. Stop at the promotion PR.
```

The exact acceptance criteria are frozen before implementation. `PROMOTION_READY` gives you
the reviewed integration work and its promotion PR; it does not claim a deployment.

## Fix a finite set of known defects

Use [clean-sweep](missions/clean-sweep.md) for a tracker or audit with identifiable findings.

```text
Clean-sweep the findings in docs/audits/retry-path.md.
Reproduce each finding, fix the confirmed defects and link each result to its tests.
Keep a named disposition for findings that require an owner decision.
Stop at the promotion PR for the integration branch.
```

Provide the audit path or issue filter and the tests that exercise the affected surface.
`DRY` requires re-enumeration; a list of built fixes with unresolved blockers is a partial result.

## Diagnose one intermittent failure

Use [root-cause](missions/root-cause.md) for an unexplained symptom.

```text
Diagnose duplicate orders during mobile checkout.
The failing request IDs and timestamps are in docs/incidents/duplicate-orders.md.
Use the staging reproduction there. Demonstrate the cause and rule out rival
hypotheses; return the diagnosis and a proposed fix handoff.
```

Provide the environment, observed behavior, relevant logs and a reproduction if one exists.
For repeated flakes across a suite, use [deflake-it](missions/deflake-it.md) instead.

## Improve tests on a critical path

Use [prove-it](missions/prove-it.md) when a green suite may miss real regressions.

```text
Close the test gap on refund authorization and webhook signature verification.
Start from tests/payments and the existing coverage report.
Confirm the critical paths, then show that behavior-changing mutations fail the tests.
```

Name the critical paths and runnable test command. A higher coverage percentage alone is not
the outcome: the tests must detect a changed behavior.

## Update dependencies with a green baseline

Use [modernize-it](missions/modernize-it.md) for package and framework upgrades.

```text
Update the dependencies for this service using its existing lockfile and package manager.
Prioritize reachable security advisories, then supported versions.
Record a reason and owner for any dependency that must remain pinned.
Keep CI green and stop at the promotion PR.
```

Provide the manifests, package manager and compatibility constraints. If the upgrade requires
a persistent data-shape change, the [migrate-it](missions/migrate-it.md) handoff has its own scope
and deployment gates.

## Document a public surface

Use [document-it](missions/document-it.md) to fill missing documentation.

```text
Document the CLI in src/cli for developers integrating it into build scripts.
Cover command syntax, exit codes, configuration and one end-to-end example.
Extract the public surface from code and check each factual claim against its source.
```

Name the intended readers and their task. Existing false claims belong to
[clean-sweep](missions/clean-sweep.md); missing documentation belongs to this coverage mission.

## Make a slow journey measurable

Use [speed-it](missions/speed-it.md) when a user journey exceeds a budget.

```text
Bring checkout submit and order-history load within a p95 budget of 2.5 seconds.
Measure on staging with the seeded dataset and the existing browser harness.
Confirm the measurement conditions before changing code, then remeasure the same journeys.
```

Specify journeys, metrics, budget and environment. Freeze the measurement contract before
using a number as evidence. Use the [mission selector](missions/README.md#choose-by-task) for
device verification, accessibility, data migrations and other goals.
