# DECISIONS — document-it self-test (run-local mirror; canonical lines appended to docs/DECISIONS.md)

Session kind: spawned (workflow child) → auto-pick recommended per gate-classification;
one-way doors never auto-resolved (none crossed: no push, no default-merge, no deploy).

- 2026-09-16T10:06:08Z · doc-freeze-tutorial-bound · taste · tutorial cells bounded OUT
  for all 29 B/C entities (no per-script/per-config tutorials; getting-started is the
  catalog tutorial) · mission anti-pattern is explicit ("generating a tutorial for
  every entity because the map has a column for it"); internal operator scripts take
  reference (+ explanation where the why is in-tree) · freeze gate
- 2026-09-16T10:06:08Z · doc-freeze-common-expl-defer · taste · explanation cells for
  already-covered B/C entities deferred to backlog (not frozen, not parked) · common
  gaps are the lesser class; the run's denominator pressure is the 16 critical
  entities; a next run may freeze them · freeze gate
- 2026-09-16T10:06:08Z · doc-freeze-expl-attempt · taste · 16 explanation cells frozen
  as FILL-or-PARK: fill where rationale is in-tree, else park
  `explanation-needs-author`; thin utilities with no why beyond purpose bounded out at
  write time with per-cell reason · internal modules take reference + explanation per
  doc-coverage, but an invented why is worse than a blank · freeze gate
- 2026-09-16T10:06:08Z · doc-worker-pack · mechanical · matt is the sole worker-pack
  router for every cell; addy never co-mounted · mission allows one of matt|addy per
  worker; single-router discipline recorded in ledger · coordinator
- 2026-09-16T10:06:08Z · doc-landing-shape · taste · 16 reference sections land in one
  new page docs/runtime-scripts.md (repo-flat-docs convention) as a serialized
  same-file commit chain, one commit per cell, plus a README one-hop link ·
  merge-serialization same-file chain rule; flat docs/ convention over a new
  reference/ dir · coordinator
- 2026-09-16T10:06:08Z · doc-solo-oracle · mechanical · terminal rests on the
  mechanical oracle (claim check + rename-to-RED + re-derived map + reachability
  grep); instructed-isolation self-review recorded per cell and labeled weaker ·
  no second identity exists; prose quality is not the oracle per SKILL.md · coordinator
