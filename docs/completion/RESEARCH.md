# RESEARCH

Fetched 2026-09-01. Category-only outbound queries (R8). No product internals, keys, or verbatim code in queries.

## Confidentiality firewall log

| id | track | query (category) | destination |
|---|---|---|---|
| Q-01 | B | Agent Skills SKILL.md specification frontmatter | https://agentskills.io/specification |
| Q-02 | B | Python 3.13 end of life date PEP | https://devguide.python.org/versions · PEP 719 |
| Q-03 | B | (internal only) git log / issues / distribution.md | repo |
| Q-04 | B | not queried: RBI PA, UPI, PMLA, VDA, Stripe — N/A per A-02 | — |

## Track A — Internal archaeology

**Velocity.** Last coherent milestone: 2026-08-29/30 adversarial-review sweep (#163–#184, PRs #185–#206) plus leftover-comment follow-up #207 (merged 2026-08-30 `6abf548`). Before that, 2026-08-28 ship-it self-run and a large review-hardening train (#134–#162). The repo is *not* abandoned; it is post-sweep, issue tracker empty.

**Abandoned branches.** Local worktree `orca-fleet-pr-comments` still checks out `ravidsrk/address-sweep-pr-comments` whose **remote is gone** (merged). Salvage: nothing (already on main). Delete worktree + local branch (T-01).

**Open issues/PRs.** 0 / 0. 86 closed. Prior plans: `docs/research/2026-08-28-forward-roadmap-and-defensibility-plan.md`, `docs/distribution.md` (unchecked marketplace boxes), `TODOS.md` (one P2 validator grammar). Divergence: the roadmap wants more proof runs and marketplace presence; HEAD has a hardened verifier and an empty tracker.

**Intent delta.** Earliest README intent (outcome-named fleets, verified not asserted, three layers) **matches** current intent. Scope creep is the *mission catalog growing to 13* with only 4 past doctrine-only — which the repo itself treats as honesty, not failure.

**Prior SHIPLOGs.** None under `docs/completion/` (this is the first driver run). Mission run archive: `docs/runs/`.

## Track B — External research

### R-01 Agent Skills spec (table-stakes for a skill pack)

- **URL:** https://agentskills.io/specification
- **Fetched:** 2026-09-01
- **Passage (paraphrased):** A skill is a directory with `SKILL.md`; required frontmatter `name` (lowercase, hyphens, must match directory) and `description` (1–1024, what + when); optional `license`, `compatibility` ≤500, `metadata`, experimental `allowed-tools`. Progressive disclosure: keep main SKILL.md under 500 lines. Validate with `skills-ref validate`.
- **Effect:** **confirms** existing validator (`scripts/validate.py` already enforces name=folder, description length, compatibility ≤500, instruction budgets). **new_gap G-08:** this run did not execute `skills-ref validate` against each mission. Not launch-blocking if our validator is a superset; still a table-stakes independent check.

### R-02 Python runtime lifecycle

- **URL:** https://devguide.python.org/versions (PEP 719 / PEP 602)
- **Fetched:** 2026-09-01
- **Passage (paraphrased):** Python 3.13 first release 2024-10-07, bugfix ~24 months, security fixes until ~2029-10. 3.14 is current bugfix; 3.12 is security-only. CI `python-version: "3.x"` tracks GitHub's latest 3.x, not a pin.
- **Effect:** **new_gap G-03** — pin a supported 3.x in CI (3.13 or 3.12) so catalog gates do not silently move. No EOL emergency (3.13 security until 2029).

### R-03 Distribution / marketplace (table-stakes discoverability)

- **URL:** in-repo `docs/distribution.md` (dated 2026-08-28); not re-submitted this run
- **Fetched:** 2026-09-01 (internal)
- **Passage:** External submissions (community marketplace aggregators, skills indexers, agentskills.io conformance in listings) are **manual follow-ups**, all still `[ ]`.
- **Effect:** **confirms G-07 / H-02**. Agent cannot submit to third-party indexes (R15-adjacent: account rights).

### R-04 Production-readiness references

- OWASP ASVS / Top 10: **no effect** on a no-HTTP stdlib CLI beyond secret hygiene and disclosure (G-02 SECURITY.md).
- SRE PRR: **no effect** beyond CI + fail-closed verifier, already present.
- Payment/app-store go-live: **no effect** (A-02).

### R-05 Operational / legal baselines

- CERT-In incident timelines / DPDP: **no effect** for an OSS repo with no product-side personal data. GitHub is the host; no in-product logging of users.
- Backup/restore: git clone **is** the backup (A-09).
- MIT license: present. No additional filing.

## Track C — Synthesis (definition inputs)

Complete, for this product, means:

1. A stranger can clone, run catalog gates, and reproduce the negative-control demo from README (CF-01, CF-04).
2. Install path (symlink or plugin) yields discoverable missions without breaking `../../playbooks` (CF-02).
3. Independent verifier remains sound (vf-bench 0 false-done) (CF-03).
4. Proof honesty remains machine-checked (CF-06).
5. At least the getting-started first mission can be run when Orca is up (CF-05) — substrate is a Human Action.
6. Security disclosure path exists (SECURITY.md).
7. CI is reproducible (pinned Python).
8. Marketplace listings are a launch *surface* but require H-02; they do not block *catalog* completeness.

Research findings without plan effect: India payments/crypto, PCI, GDPR-as-SaaS, LLM provider ToS (N/A).
