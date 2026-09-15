CATEGORY: bug
SUMMARY: the evidence-run wrapper litters an untracked lockfile that breaks clean-tree
gates and shifts later runs' content fingerprints.
CURRENT BEHAVIOUR: the wrapper serializes ledger appends with an OS file lock held on a
sibling lockfile it creates next to the manifest; the lockfile is never deleted. After the
manifest is committed the lockfile remains as untracked litter, fails clean-tree checks,
and shifts later runs' recorded content fingerprints so they no longer match the committed
tree (reproduced: second run's fingerprint differs from the committed tree). Concurrent
appends land fully today (16 parallel appends yield 16 records) — the lock works and must
stay in some form.
DESIRED BEHAVIOUR: mutual exclusion across concurrent wrapped runs is preserved; no new
file remains beside the manifest after any number of runs, committed or not; a run's
recorded content fingerprint equals the committed tree when the tree is otherwise clean;
concurrent behaviour is covered by an automated test (none exists today).
KEY INTERFACES: the wrapper's append routine and its locking primitive (what is locked,
and where that lock lives); the manifest JSON shape, which does not change; the wrapper's
test module, which gains a concurrency test.
ACCEPTANCE CRITERIA: [ ] sequential wrapped runs leave no new untracked file beside the
manifest [ ] 16 concurrent appends land 16 records [ ] the recorded fingerprint equals the
committed tree on an otherwise-clean tree [ ] no test anywhere asserts the old litter
behaviour [ ] the full suite stays green.
OUT OF SCOPE: manifest schema changes; verifier changes; retention or signing of evidence
(separate findings); the lost-record race's pre-lock history.
