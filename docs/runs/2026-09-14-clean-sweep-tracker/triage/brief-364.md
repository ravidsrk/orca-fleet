CATEGORY: enhancement (S1; direction set by Q1: fixtures + workspace-state oracle)
SUMMARY: make per-mission behavioral evals fixture-backed and graded on workspace state
instead of narration-only.
CURRENT BEHAVIOUR: every mission's behavioral eval cases carry empty file sets flagged
for narration-only grading. The behavioral runner materializes file sets into a temporary
workspace but grades only the agent's trace and discards the workspace — so even
fixture-backed cases would be graded on prose, never on resulting state. The behavioral
suite runs outside CI (only the routing suite gates), and the eval tooling declares
itself catalog tooling, never proof evidence.
DESIRED BEHAVIOUR: at least one fixture-backed behavioral eval per mission covering its
highest-risk behaviour, plus a post-run workspace-state oracle so fixtures change the
verdict: a case passes only when the workspace reaches the asserted state. The routing
suite and its gate are untouched. Existing narration-only labels stay honest where no
fixture exists yet (no silent narration grading returns).
KEY INTERFACES: the eval-case schema (file sets, narration flag); the behavioral
runner's materialize-then-grade flow, which gains the workspace-state check; the per-mission
eval files, which gain fixture-backed cases; the eval test module, which gains oracle +
fixture tests.
ACCEPTANCE CRITERIA: [ ] every mission has >=1 fixture-backed case for its riskiest
behaviour [ ] the oracle grades resulting workspace state, not trace prose (a passing
trace over a wrong workspace fails) [ ] narration-only cases stay explicitly labeled and
bounded [ ] the routing gate still passes at its threshold [ ] the full suite stays green.
OUT OF SCOPE: promoting eval output to proof evidence (the tooling's declaration
stands); touching the routing suite; new missions' eval files beyond the catalog present
at dispatch.
