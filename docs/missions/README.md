# Mission guides

One deep-dive per mission: what it does, when to reach for it (and when not to), the pipeline
with its phases, terminal states, human gates, convergence proof, and the failure modes it is
built to prevent. The agent-facing contracts live in [`skills/`](../../skills/); these pages are
for the human deciding what to run and what to expect.

<p align="center">
  <img src="../../assets/diagrams/mission-map.jpg" alt="Decision map: a goal to build routes to map-it then ship-it; known problems route to clean-sweep, oss-contribute, absorb-it, harden-it, speed-it, modernize-it, migrate-it, prove-it, deflake-it, floor-it, reshape-it, attest-it, access-it, oncall-it, document-it, or field-test-it; a question routes to review-it or root-cause; drifted tooling routes to pin-it" width="820">
</p>

| Guide | One line |
|-------|----------|
| 🚢 [ship-it](ship-it.md)                 | Intent or a frozen spec → a released, verified change |
| 🧹 [clean-sweep](clean-sweep.md)         | A finite backlog exhausted to zero, PR-per-finding, re-enumerated until dry |
| 🤝 [oss-contribute](oss-contribute.md)   | Upstream issues → open, reviewed, etiquette-correct PRs on a repo you cannot merge |
| 🛡️ [harden-it](harden-it.md)       | A threat model closed: audit → exploit → fix → re-attack → clean re-audit |
| ⚡ [speed-it](speed-it.md)          | Every declared journey within its perf budget, proven to a measurement contract |
| 📦 [modernize-it](modernize-it.md) | Every dependency current or pinned-with-a-reason, CI green the whole way |
| 🧪 [prove-it](prove-it.md)         | A mutation-audited test on every critical path |
| 🎯 [deflake-it](deflake-it.md)     | Flakes eradicated to a consecutive-green streak, local and CI |
| 🔍 [review-it](review-it.md)       | A read-only, SHA-bound GO/NO-GO verdict — no fix authority |
| 🗺️ [map-it](map-it.md)             | A foggy goal resolved into a frozen execution map ship-it can consume |
| 🔬 [root-cause](root-cause.md)     | A reproduced symptom and a demonstrated cause — diagnosis only |
| 📋 [attest-it](attest-it.md)       | Conformance to a frozen standard, independently re-derived: `CONFORMANT` or gaps parked |
| ♿ [access-it](access-it.md)       | A frozen page/flow set driven to WCAG 2.2 AA with a revert-to-violation control |
| 📌 [pin-it](pin-it.md)             | Runtime doctrine re-witnessed against the installed binary — every claim receipted |
| 🧱 [floor-it](floor-it.md)         | A written, numbered quality bar — every dimension tool-enforced and proven to fire |
| 🧬 [reshape-it](reshape-it.md)     | Hot modules deepened behind smaller interfaces, behaviour proven unchanged |
| 📱 [field-test-it](field-test-it.md) | Defects reproduced, fixed, and re-proven on a real device — revert control included |
| 🗄️ [migrate-it](migrate-it.md)     | A stateful shape change landed phase by phase across deploys — parity proven, zero readers before the drop |
| 📟 [oncall-it](oncall-it.md)       | A frozen path set made operable — alerts test-fired, and an induced failure named by a source-blind worker |
| 📥 [absorb-it](absorb-it.md)       | An inbound PR queue drained — landed with authorship and a receipt, refuted, or parked with a named ask |
| 📚 [document-it](document-it.md)   | A public surface covered by quadrant with zero critical gaps — every claim anchored and rename-controlled |

Not sure which one? The [decision flowchart in the README](../../README.md#which-mission-do-i-want)
routes by what you have in hand: a goal, a set of known problems, or a question. For a real run
with its incidents intact, read [Anatomy of a run](../guides/anatomy-of-a-run.md).
