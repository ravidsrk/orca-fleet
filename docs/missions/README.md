# Mission guides

One deep-dive per mission: what it does, when to reach for it (and when not to), the pipeline
with its phases, terminal states, human gates, convergence proof, and the failure modes it is
built to prevent. The agent-facing contracts live in [`skills/`](../../skills/); these pages are
for the human deciding what to run and what to expect.

| Guide | One line |
|-------|----------|
| 🚢 [ship-it](ship-it.md)           | Intent or a frozen spec → a released, verified change |
| 🧹 [clean-sweep](clean-sweep.md)   | A finite backlog exhausted to zero, PR-per-finding, re-enumerated until dry |
| 🛡️ [harden-it](harden-it.md)       | A threat model closed: audit → exploit → fix → re-attack → clean re-audit |
| ⚡ [speed-it](speed-it.md)          | Every declared journey within its perf budget, proven to a measurement contract |
| 📦 [modernize-it](modernize-it.md) | Every dependency current or pinned-with-a-reason, CI green the whole way |
| 🧪 [prove-it](prove-it.md)         | A mutation-audited test on every critical path |
| 🎯 [deflake-it](deflake-it.md)     | Flakes eradicated to a consecutive-green streak, local and CI |
| 🔍 [review-it](review-it.md)       | A read-only, SHA-bound GO/NO-GO verdict — no fix authority |
| 🗺️ [map-it](map-it.md)             | A foggy goal resolved into a frozen execution map ship-it can consume |
| 🔬 [root-cause](root-cause.md)     | A reproduced symptom and a demonstrated cause — diagnosis only |

Not sure which one? The [decision flowchart in the README](../../README.md#which-mission-do-i-want)
routes by what you have in hand: a goal, a set of known problems, or a question.
