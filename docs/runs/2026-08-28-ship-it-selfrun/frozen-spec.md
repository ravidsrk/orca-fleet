# Frozen spec — proof-status reporter (ship-it self-run, 2026-08-28)

Coordinator-frozen acceptance criteria for the build slice. This file is the AUTHORITATIVE
denominator the independent verifier re-derives against (`verify.py --contract-source … --contract-digest …`).
It is supplied by the coordinator (this dispatch record), never edited by the builder.

The slice ships `runtime/scripts/proof_status.py`: a focused proof-posture reporter and CI lens over
the mission catalog, distinct from `scripts/validate.py` (the build gate) — it summarizes tiers and
surfaces evidence-report existence for humans and CI.

- AC-1: `runtime/scripts/proof_status.py` reads every `skills/*/SKILL.md` frontmatter and reports,
  per mission, its `name`, `proof` tier, `proof_evidence` (or `—` when absent), and whether that
  evidence path resolves to an existing file in the repo. Every catalog mission appears exactly once.
- AC-2: The tool prints a coverage rollup — the count of missions in each proof tier
  (`doctrine-only` / `self-run` / `external-run`) and the total mission count.
- AC-3: A `--check` flag makes the process exit non-zero if and only if any mission whose tier is
  above `doctrine-only` has a missing or unresolvable `proof_evidence`; the default report mode exits
  zero. A `--json` flag emits the per-mission records as a machine-readable array.

Out of scope (non-goals): modifying `validate.py`, `gen-badges.py`, badges, or any mission
frontmatter; network access; writing files.
