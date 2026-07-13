# Runtime policy — mission chaining (sequential, gated, minimal)

"Make this repo production-ready" spans more than one mission (harden-it, then prove-it, then
ship-it). Chains are how a coordinator runs that — and the predecessor repo proved the failure
mode: a YAML campaign engine with conditional edges where 4 of 8 presets rotted as stubs and
every chain that actually ran was linear with halt-on-blocked. So this policy is deliberately
small. Sequential only. No DAG, no expression language, no preset catalog.

## The chain contract

- **Declare the chain up front**, in the ledger header: the mission sequence AND, per link, the
  set of terminal states allowed to proceed. Example:
  `harden-it[CLEAN] → prove-it[COVERED] → ship-it[PROMOTION_READY]`.
- **The gate between missions is the previous mission's named terminal state, backed by its
  verified evidence** (evidence-manifest.md). An audit GATES the chain — there is no
  "continue anyway" edge. A degraded terminal (`HARDENED-WITH-OPEN-ITEMS`,
  `COVERED-WITH-PARKED`, …) STOPS the chain and parks it; advancing past a degraded state is a
  one-way human gate (gate-classification.md), recorded in the ledger.
- **One mission active per repo at a time.** Each link is a FULL run: its own preflight, its own
  integration BASE, its own convergence proof. Carrying a BASE from one mission into the next is
  an explicit human decision, never a default.
- **Deferral carry:** mission N's parked items, backlog file, and noticed-but-not-touched list
  are handed to mission N+1 as enumeration INPUT — findings to triage, never pre-confirmed work.
  This is the generalization of the existing hard-wired handoffs (map-it's frozen DAG feeding
  ship-it; prove-it's surfaced bugs feeding clean-sweep).
- **Cross-repo chains do not exist.** One coordinator per repo; a program spanning repos is
  separate coordinator sessions a human sequences.

## Completion

The chain report names, per link: the mission, its terminal state, the verification result, and
what was carried forward. A chain that stopped early names the gate it stopped at — a stopped
chain is a correct outcome, not a failure to hide.
