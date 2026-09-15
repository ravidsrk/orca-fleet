CATEGORY: bug
SUMMARY: the run-report checker's WIP-curve validation accepts incomplete reports that
the attention-budget protocol refuses.
CURRENT BEHAVIOUR: the checker passes any mutating run report containing at least one
table row naming builder and reviewer counts. A settings-only row passes; a report
covering several dispatch waves with a single row passes; an unrelated row that happens to
carry the two settings passes. The doctrine protocol requires one complete row per dispatch
wave carrying the WIP setting plus every metric the protocol table names (builder
throughput, verification latency as median and max, rework rate, freshness violations).
DESIRED BEHAVIOUR: a defined per-wave row schema (wave identity plus the WIP setting plus
all protocol metrics); the checker requires one complete row per recorded wave; the
protocol prose names the schema so the text and the check cannot drift again; existing
tests that bless incomplete rows are updated to the schema; no live tier claim breaks
(none stands above doctrine-only).
KEY INTERFACES: the checker's WIP validation routine and its row pattern; the
attention-budget protocol section (prose update naming the row schema); the run-report
test module (schema tests replace the blessed-incomplete-row test).
ACCEPTANCE CRITERIA: [ ] a settings-only row is refused [ ] a multi-wave report with
partial or missing wave rows is refused [ ] complete per-wave rows bind [ ] the protocol
prose names the exact schema the checker enforces [ ] the full suite stays green.
OUT OF SCOPE: changing the WIP caps; the multi-run graduation analysis; other report
checks (manifest binding, inventory, invocation).
