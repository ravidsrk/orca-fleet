# Needs-human questions (batch gate — one round, three units)

## Q1 · #364 (S1): per-skill behavioral evals — fixtures or downgrade?

Triage (independent worker + coordinator repro of the premises) finds the finding's
proposed fix does not work as specified: the behavioral runner grades the agent's trace
and discards the workspace, so fixture-backed cases would STILL be graded on narration.
The behavioral suite is not in CI (routing only), and the eval tooling's own header says
it is catalog tooling, never proof evidence. The completion-trace rule binds proof, which
never consumes eval output. Recommendation: record the evals explicitly as routing
fixtures (downgrade), and require a post-run workspace-state oracle before any future
fixture program. Needs the maintainer because the issue is S1 and the thread wants
fixtures: fixtures-as-specified (no grading change), fixtures-plus-oracle (larger build),
or downgrade?

## Q2 · #386 (S2): sign the manifest/inventory — key custody + backend choice

Confirmed: the manifest's retention pointer is a placeholder, the run-close inventory is
hash-only, and the cited prerequisite (a signed verifier transcript) was closed without
being built, so the prerequisite is currently untracked. An agent can implement signing
against the existing key scheme and specify a backend on paper, but cannot decide key
custody/role separation (the private key lives out of band by design) or pick the
retention backend (infrastructure with cost/ownership). Needs: the maintainer's key-role
decision, backend choice (concrete store or transparency-log anchor), and whether to
re-open/track the transcript prerequisite — or park the whole unit until decided.

## Q3 · #385-diagrams: four missing mission diagrams — render or park?

Four mission guides have no diagram asset (sixteen others embed one); the diagrams are
generated raster images with no source in the repo, and a past render needed human fixes
for garbled labels. The agent slice (parity test with a known-gap list) proceeds regardless.
Needs: will the maintainer render the four diagrams (agent then drops the known-gap list),
or park the gap as needs-human?
