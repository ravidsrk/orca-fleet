# Fix-handoff briefs (root-cause -> separately authorized missions)

Two durable briefs in agent-brief shape: behavioral contracts, no paths, no
line numbers. Neither carries authority; the dispatching mission supplies
autonomy, gates, and budget. Diagnosis-only mission: nothing here is merged
by root-cause.

---

## B1 (diagnostic experiment — the run that catches the writer)

CATEGORY: enhancement
SUMMARY: Catch the next scratch-repo teardown race red-handed in CI and name
the leftover entry plus the runner environment.
CURRENT BEHAVIOUR: When a contract-suite test tears down a scratch git repo
on Linux CI, a rare concurrent creation inside the repo's git directory
defeats the recursive remove with a "directory not empty" OS error AFTER all
assertions passed, reddening an otherwise green run roughly once per hundred
thousand teardowns. The leftover entry's identity is lost (the temp directory
is abandoned unnamed), and the runner's filesystem type, git configuration
origins, git version, and process list are not recorded, so every incident
ends with the writer unidentified.
DESIRED BEHAVIOUR: The teardown helpers used by the temp-repo suites catch a
"directory not empty" failure, enumerate the surviving entries under the
abandoned temp directory (relative names only), capture the process list, and
surface both in the test output without changing pass/fail semantics for any
other outcome; a nightly or weekly scheduled CI job additionally records a
one-time environment dump (temp filesystem type, system and global git
configuration with origins, git version, kernel release, full process list)
and runs the teardown-heavy suites in a bounded stress loop. Edge cases: the
catcher must itself never fail a test (catcher errors degrade to a warning
line); secrets must never be printed (scan the dump for credential shapes
before emitting); the stress job must be bounded in wall time and must not
gate merges (informational only).
KEY INTERFACES: the shared temp-repo test fixtures (the setup/teardown
helpers every temp-repo suite builds on) gain a catching teardown wrapper;
the CI workflow gains a scheduled informational job with an environment-dump
step and a bounded suite stress-loop step; the OS-error branch for "directory
not empty" is the only behavior that changes.
ACCEPTANCE CRITERIA: [ ] a simulated concurrent writer (a background thread
creating a file inside the scratch git directory during teardown) produces a
test output naming the leftover entry [ ] the full contract suite passes
unchanged with the catcher in place and no new warnings [ ] the scheduled job
emits the environment dump with filesystem type, git configuration origins,
git version, kernel, and process list, all free of credential shapes [ ] the
stress loop's bounds (iterations, wall-time cap, informational-only status)
are declared in the workflow itself
OUT OF SCOPE: identifying the writer from old incidents (undetermined by
construction); changing any test assertion or production behavior; making the
stress job merge-gating; a fourth copy of the ignore-cleanup-errors
suppression (that direction is closed pending the catcher's datum).

---

## B2 (hardening — issue #440's acceptance, after or alongside B1)

CATEGORY: bug
SUMMARY: A scratch-repo teardown race must not redden a passing contract-suite
test.
CURRENT BEHAVIOUR: The freshness-check test that builds two commits with the
same tree performs its temp-directory teardown with cleanup errors fatal, so
the rare "directory not empty" race (see B1) fails the suite even though
every assertion passed. Three sibling suites already tolerate cleanup errors
on the same grounds; this test is the odd one out.
DESIRED BEHAVIOUR: The test's teardown tolerates cleanup errors exactly as
its siblings do, with a comment recording the race (unidentified writer,
incidents referenced by date, this diagnosis run referenced by campaign name)
rather than guessing a cause; what the test asserts is byte-for-byte
unchanged, including edge behavior (a real content change still voids the
review; a content-identical move still passes). If B1's catcher has landed,
this test uses the catching teardown so any future hit still names its
leftover.
KEY INTERFACES: the freshness-check test's temp-directory usage (same
tolerance flag its siblings use); the temp-repo teardown contract (cleanup of
a throwaway repo is not a signal and must not gate the build).
ACCEPTANCE CRITERIA: [ ] the test's teardown cannot fail the suite on a busy
runner (stress: fifty consecutive runs green) [ ] no behavior change to what
the test asserts (the pre/post assertion sets are identical) [ ] with the
tolerance in place, a simulated teardown failure degrades to silence while
the body still runs and asserts [ ] the comment names the race as
unidentified-writer and points at this campaign's report, not at gitleaks
OUT OF SCOPE: touching any other test's teardown; changing the verifier's
freshness rule itself; the B1 diagnostic (separate brief, may land first).
