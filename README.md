<h1 align="center">orca-fleet</h1>

<p align="center">
  <strong>Autonomous fleets for the Orca runtime, named for what they achieve.</strong><br/>
  Ten missions. One outcome each. A SHA-bound evidence definition of done.
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="MIT License"></a>
  <a href="https://agentskills.io/specification"><img src="https://img.shields.io/badge/spec-agentskills.io-orange.svg" alt="agentskills.io spec"></a>
</p>

---

## A fleet is an outcome, not an ingredient

Give a mission a goal, come back to an evidence-based end state. Every mission is named for
what it produces (`ship-it`, `clean-sweep`, `find the root-cause`), never for the pack whose
technique a worker happens to run. There are no `matt-*` or `gstack-*` skills here. The upstream
packs are sources of *recipes* that missions compose; the Orca runtime is the substrate every
mission rides.

Two workflows are the **same mission** only if they share all five of: unit of work, per-unit
state machine, convergence proof, ordering/isolation, and parking/failure semantics. By that
test, closing audit findings, tracker issues, and false doc-claims are one mission
(`clean-sweep`) — but security hardening, perf budgeting, dependency modernization, test-debt
proving, and flake eradication are not; their denominators and proofs differ, so each is its own.

## The ten missions

| Mission | Outcome (definition of done) | Use when |
|---|---|---|
| 🚢 **[ship-it](skills/ship-it/)** | Intent or a frozen spec → a released, verified change, stopped at the highest release state you're authorized to reach (`BUILT` → `PROMOTION_READY` → `RELEASED` → `DEPLOYED_AND_VERIFIED`) | "build and ship this", spec-to-shipped-product |
| 🧹 **[clean-sweep](skills/clean-sweep/)** | A finite backlog exhausted to zero, PR-per-finding, every close backed by a merged SHA + a test that failed pre-fix; re-enumerated until dry | "close every issue", "fix everything in this audit", "the README lies" |
| 🛡️ **[harden-it](skills/harden-it/)** | A threat model closed: audit → exploit → fix → **re-attack the fix** → clean re-audit finds zero unrefuted P0/P1 (or `HARDENED-WITH-OPEN-ITEMS`) | "harden this", "security sweep", "red team" |
| ⚡ **[speed-it](skills/speed-it/)** | A perf budget met against a pre-declared measurement contract: `WITHIN-BUDGET` or `OPTIMIZED-WITH-PARKED` | "the app is slow", "perf budget", "Core Web Vitals" |
| 📦 **[modernize-it](skills/modernize-it/)** | Dependency currency via expand/migrate/contract: `CURRENT` or `CURRENT-WITH-PINNED`, every pin justified | "update the dependencies", "framework migration" |
| 🧪 **[prove-it](skills/prove-it/)** | A mutation-audited critical surface: `COVERED` or `COVERED-WITH-PARKED`, tests that die when the code is mutated | "close the test gap", "cover the critical paths" |
| 🎯 **[deflake-it](skills/deflake-it/)** | Flake eradication to a statistical streak, local **and** CI: `STABLE` or `STABLE-WITH-QUARANTINE` | "kill the flaky tests", "deflake the suite" |
| 🔍 **[review-it](skills/review-it/)** | A trusted, read-only, SHA-bound GO/NO-GO verdict — acceptance always, risk lenses when the diff triggers them. **No fix authority.** | "review this PR", "is this ready to merge" |
| 🗺️ **[map-it](skills/map-it/)** | A foggy multi-session goal resolved into a frozen execution map `ship-it` can consume — decisions, not deliverables | "chart this", "plan this epic", "I don't know the shape yet" |
| 🔬 **[root-cause](skills/root-cause/)** | A reproduced symptom and a demonstrated cause: repro-first → falsify rival hypotheses → one survivor, with evidence; optional fix handoff | "diagnose this", "why is this happening", hard intermittent bug |

## Three layers, strictly separated

```
MISSIONS   (skills/, discoverable)     ← the only user-facing skills. One outcome each.
   │  compose, by reference, →
PLAYBOOKS  (playbooks/, callable)       ← reusable phase protocols. NOT auto-triggering skills.
   │  run on, →
RUNTIME    (runtime/, invisible)        ← Orca primitives + policies. Called, not discovered.
```

> Missions are discoverable. Playbooks are callable. Runtime mechanisms are invisible unless
> directly administered.

Publishing a playbook or a runtime policy as an auto-triggering skill would recreate the exact
routing collisions and ingredient-shaped entry points this repo exists to remove — so only
`skills/` holds a `SKILL.md`. See **[ARCHITECTURE.md](ARCHITECTURE.md)** for the full design.

## The definition of done is an evidence protocol, not trace-grading

A coordinator does not hold its workers' terminal traces, and a trace proves an action was
*attempted*, not that the resulting state is *correct*. So completion is never graded on
narration. Every unit of work emits a **SHA-bound evidence manifest** — base SHA → head SHA,
the exact acceptance criteria addressed, commands with exit codes, artifact paths, a
negative-control result, PR + reviewed SHA — and an **independent verifier** checks those claims
against authoritative state (git, the test runner in a clean env, the runtime, the deploy
target). See **[runtime/evidence-manifest.md](runtime/evidence-manifest.md)**.

This is what made `clean-sweep` and `spec-to-ship` reliable: verify, never trust.

## One router per worker

Missions draw worker methodology from upstream packs — [mattpocock/skills](https://github.com/mattpocock/skills),
[garrytan/gstack](https://github.com/garrytan/gstack), [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills).
Each ships its own router, and they fight when co-mounted. So a worker TASK loads exactly **one**
pack's playbooks. Cross-pack composition happens at the mission level (one worker runs Matt
triage, another runs Addy security), never inside a single worker.

## Requirements

Every mission has a **hard dependency on the Orca runtime + the `orchestration` skill shipped with
the Orca CLI** (not published here). Individual missions add tooling — `git` + `gh`, `gitleaks`
for `harden-it`, a benchmark harness for `speed-it`, and so on — declared in each `SKILL.md`
frontmatter.

## Install

```bash
# Link one mission into Claude Code (link, don't copy)
ln -s "$(pwd)/skills/ship-it" ~/.claude/skills/ship-it

# Or install the whole plugin via the Claude Code marketplace manifest
# (.claude-plugin/plugin.json)
```

## Validate + test

```bash
python3 scripts/validate.py                    # spec + three-layer separation + composition/cross-doc refs
python3 -m unittest discover -s tests -v       # architecture + validator contract tests
```

## License

MIT — see [LICENSE](LICENSE).
