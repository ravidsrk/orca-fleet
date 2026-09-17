# Audit unit contract — harden-it self-run, campaign-2026-09-16

Unit: harden-it-self-audit. Fixed point: origin/main tip c46d4b3.
The acceptance criteria are the list items below, one per line.

- AC-1: Threat model committed: STRIDE per trust boundary plus Always/Ask-First/Never buckets with one-way gates named.
- AC-2: Tree-wide security audit executed at the fixed point across secrets, CI/supply-chain, injection, trust-boundary, crypto, destructive-path, and LLM/privacy axes, with evidence per axis.
- AC-3: Every audit candidate triaged to a terminal disposition; zero unrefuted P0/P1 remains.
- AC-4: Project gates green at the evidence head: catalog validator and full test suite.
- AC-5: Re-audit mechanical pass confirms the terminal state: zero unrefuted P0/P1.
