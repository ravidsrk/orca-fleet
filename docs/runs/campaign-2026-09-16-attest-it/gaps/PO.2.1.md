# Gap handoff — PO.2.1 (SDLC roles and responsibilities)

- Obligation: NIST-SP-800-218@1.0.0 PO.2.1 — "Create new roles and alter responsibilities for existing roles as needed to encompass all parts of the SDLC. Periodically review and maintain the defined roles and responsibilities, updating them as needed."
- Missing evidence: a written SDLC roles/responsibilities record (roles, holders, review cadence). Searched at 6390743: no CODEOWNERS, no roles doc; only the bus-factor-1 maintainer inventory (docs/ops.md:3).
- Recipient: Ravindra Kumar (ravidsrk@gmail.com), Maintainer.
- Ask (Task item): write and commit a short ROLES record (suggested path: docs/roles.md) naming each SDLC role the project needs (development, review, testing/assurance, release, incident response), who holds it today, and the next review date. For a solo project, one person may hold every role — the record is what is missing, not headcount.
- Verify-complete (a fresh worker checks this, not the reply): `git show HEAD:docs/roles.md` (or the recorded path) exists and its bytes name ≥3 SDLC roles with holders and a review date; re-run `python3 docs/runs/campaign-2026-09-16-attest-it/rederive/rederive.py` with an added PO.2.1 quote check and it exits 0.
- Run ref: evidence/PO.2.1.md. Park class: needs-human (one-way policy decision).
