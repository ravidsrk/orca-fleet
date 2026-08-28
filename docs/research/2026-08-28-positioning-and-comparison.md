# Positioning & comparison — orca-fleet in the 2026 agent-fleet landscape — 2026-08-28

> **Dated snapshot (2026-08-28).** A point-in-time positioning read: where the OSS
> orchestrator market converged in 2026, how the shipping evidence protocols compare, and how
> governance discipline for coding agents lines up with the wider automation field. Not a live
> coverage matrix and not a roadmap — see [ARCHITECTURE.md](../../ARCHITECTURE.md) for current
> catalog state and the same-day
> [competitive scan](2026-08-28-competitive-landscape-differentiation.md) and
> [forward roadmap](2026-08-28-forward-roadmap-and-defensibility-plan.md) for the deep briefs this
> doc distills. Vendor features move weekly; every external claim is cited with an access date, and
> anything unconfirmed is flagged UNVERIFIED rather than guessed. Novelty is always stated as
> *absence of a published counterpart as of 2026-08-28*, never as a bare "first" or "only".

**Status:** MAPPED — three positioning axes (topology · evidence protocol · governance) frozen
**Date:** 2026-08-28
**Base:** `main`
**Method:** Distilled from the two same-day research briefs, with a fresh primary-source web pass
on every external artifact named here (repos, specs, official docs, first-party writeups). Claims
are split VERIFIED / INFERRED / UNVERIFIED in the self-audit at the end.
**Destination:** A linkable positioning surface that says what shape the market took, what
orca-fleet adds on top of it, and where its differentiation is genuinely uncontested — consumable
without re-running the research.

## TL;DR

1. In 2026 multiple independent OSS orchestrators converged on the **same physical shape**:
   worktree-isolated disposable workers, a central git-backed work ledger, and serialized merges
   through one conductor. That topology is now commodity — table stakes, not a moat.
2. orca-fleet does not compete on that shape; it is the **doctrine layer** for it — the runtime
   policies (evidence manifest, independent verification, gate classification) that decide when a
   unit produced by that topology is actually *done*.
3. On the **evidence protocol**, the shipping tools each cover a slice — SHA/signature binding,
   clean-env re-runs, or a mutation negative control — but **no single one combines all six**
   properties orca-fleet's manifest requires. That gap is the honest, absence-of-evidence claim.
4. On **governance**, orca-fleet's one-way/two-way-door gate classification is an instance of a
   pattern the security-automation field converged on independently: keep the enforcing gate
   *below the model*, deterministic and human-owned for irreversible actions.

## Part 1 — The 2026 convergent topology

Through 2026 the "run many coding agents at once" problem was solved, repeatedly and
independently, with the same three primitives. This is convergent evolution, not copying: the
constraints (agents collide on a shared checkout; long-lived agents degrade; parallel PRs race on
one base) force the same answer.

**The converged shape:**

- **Worktree-isolated, disposable workers.** Each task runs in its own `git worktree` so agents
  never touch each other's files, and worker processes are ephemeral while the work is durable in
  git.
- **A central, git-backed ledger.** A single source of truth for work items and status that
  survives crashes and lets a fresh process resume.
- **Serialized merges.** Parallel branches land through one queue/conductor so integration is
  ordered rather than a merge race.

**Independent instances (all verified against primary sources on 2026-08-28):**

| Orchestrator | Isolated workers | Central ledger | Serialized merge | Coordinator role |
|---|---|---|---|---|
| **Gas Town** (Steve Yegge) | worktrees ("hooks"), ephemeral Polecats | **Beads**, a git-backed work ledger | **Refinery** merge queue | the **Mayor** dispatches, does not hand-code the diffs |
| **Overstory** (jayminwest) | worker agents in isolated worktrees | SQLite mail bus + tracker state | `ov merge` with tiered conflict resolution | persistent **coordinator** slings workers |
| **Composio Agent Orchestrator** | one worktree + branch + PR per worker | central dashboard/status ledger | orchestrated PR lifecycle (CI-fix, review, conflict) | planner **orchestrator** spawns/terminates workers |
| **orca-fleet** (this repo) | Orca worktrees per unit, fresh context per worker | the **ledger file** (one row per unit) | **merge train**, one conductor per BASE | coordinator that **never writes code** |

Notes and honest caveats:

- **Gas Town** (Steve Yegge) shipped 2026-01-01, MIT-licensed, Go; the "Mayor / Beads / Refinery /
  Polecats" vocabulary is from Yegge's own writeup and project site. It is explicitly framed as
  "Kubernetes for AI coding agents."
- **Overstory** is real and MIT-licensed but its README now marks it **archived / no longer
  maintained**, with development moved to a successor ("Warren"). Its architecture (worktrees +
  SQLite mail + `ov merge`) is still the cleanest small statement of the converged shape, so it is
  cited as a design data point, not a live product recommendation.
- **Composio Agent Orchestrator** is MIT-licensed and centers the full PR lifecycle (auto CI-fix,
  review-comment handling, conflict resolution) on top of the worktree/ledger shape.
- These are three of several; the same-day competitive scan records more (ccswarm, claude-flow /
  Ruflo, Claude Code agent teams) landing on the identical topology. **No published counterpart
  was found, as of 2026-08-28, that treats this shape as a substrate and layers a separate
  completion-doctrine on top** — which is exactly where orca-fleet sits.

**orca-fleet's position:** the topology is the *body*; orca-fleet is the *doctrine*. It assumes
worktree isolation, a ledger, and a merge train as given (increasingly native Orca/Claude Code
primitives) and adds the layer none of the above ship as an integrated policy set: what counts as
done, who is allowed to certify it, and which decisions a fleet may never make alone. Concretely
that is the coordinator-never-writes-code rule, the disposable fresh-context worker, the
build-blind reviewer, and the single merge conductor
([docs/concepts.md](../concepts.md), [runtime/merge-serialization.md](../../runtime/merge-serialization.md)).

## Part 2 — Evidence-protocol comparison

orca-fleet's [evidence manifest](../../runtime/evidence-manifest.md) defines "done" as a
SHA-bound claim re-derived from authoritative state by an independent session. The table scores
the shipping evidence approaches against the six properties that manifest defines. Several are
scoped by unit class (see the note after the table), and the orca-fleet column is documented
doctrine, not a uniform field-audit. Cells are
filled from primary sources; **UNVERIFIED** marks a property a source neither documents nor
plausibly implies.

Legend: **✓** documented/present · **◐** partial or adjacent analog · **✗** absent by design ·
**UNVERIFIED** could not confirm from primary sources.

| Property | vr.dev | Sigstore-community attestation (SLSA/in-toto + cosign) | AWS CI mutation-testing gate | **orca-fleet evidence-manifest** |
|---|:--|:--|:--|:--|
| **SHA-binding** | ◐ a HARD verifier can assert "commit SHA exists", but there is no manifest binding criteria↔SHA | ✓ subject = artifact digest; provenance records source repo + commit | ✗ runs on the pipeline SHA but binds no completion manifest (UNVERIFIED for explicit binding) | ✓ `base_sha`/`head_sha` required, real commits; contract `source@digest` |
| **Ancestry check** | ✗ no merge-base check | ✗ verifies commit identity, not landing into a base | ✗ | ✓ *(mutation units)* `git merge-base --is-ancestor <head_sha> origin/<base>`; n/a for report-only/planning |
| **Clean-env re-run** | ◐ AGENTIC probes hit real state, but a clean-worktree checkout re-run at a SHA is not documented | ✗ attests that a build happened; does not re-run tests | ✓ CodeBuild runs in an ephemeral container | ✓ checkout `head_sha` in a fresh worktree, run the suite green |
| **Revert-to-red (negative control)** | ✗ `fail_closed` composition ≠ proof-can-fail; no mutation/revert | ✗ | ✓ mutation testing *is* the negative control — a surviving mutant fails the gate | ✓ *unit-class-dependent* — mutation: named tool + pinned mutant KILLED / revert → RED; report-only & planning carry the §3 class analogue |
| **Reviewed-SHA freshness** | ✗ | ✗ not a review concept | ✗ | ✓ *(mutation units)* `pr.reviewed_sha == head_sha`; report-only units bind to `head_sha` with no PR-review step |
| **Independent second-session re-derivation** | ◐ supports a separate-context validator but does **not** enforce it (author confirms the actor may self-run) | ◐ verification is a distinct process (cosign / slsa-verifier) but re-derives *signatures/provenance*, not acceptance criteria | ✗ same pipeline self-scores | ✓ a different session re-derives scope/tests/NC from git before any LLM judgment |

> **Reading the orca-fleet column honestly.** These are the properties the evidence manifest
> *defines*; how much the reference verifier (`verify.py`) actually machine-checks varies by unit
> class, and the column is documented doctrine, not a uniform field-proof. For every unit `verify.py`
> re-derives scope from the frozen contract and checks the SHAs; it checks reviewed-SHA freshness
> whenever a `reviewed_sha` is declared and ancestry whenever a base is supplied (`--base`) — both
> driven by the inputs, not gated on unit class. Its **independent-review** and **negative-control**
> checks are **mutation-only**: for report-only and planning units it *skips* them, and it does not
> machine-check the report-only §3 analogue of the negative control (that stays a human/coordinator
> re-check per the manifest). The manifest *doctrine* is what scopes ancestry and reviewed-SHA to
> mutation units (report-only units bind to `head_sha`); the table cells reflect that doctrine.
> Field-proof so far is thin: the one recorded run (2026-08-28 ship-it self-run) exercised scope,
> SHAs, freshness, and the negative control on a mutation unit but could not clear the
> independent-review leg autonomously. Competitor ✓ marks mean "documented/present", not
> "independently field-audited here".

**What each competitor actually is (primary-source grounded, 2026-08-28):**

- **vr.dev** — an MIT, `pip install vrdev` library of ~38 verifiers across 19 domains in three
  tiers: **HARD** (deterministic probes against DB/files/APIs/git), **SOFT** (LLM rubric, gated
  behind HARD so a failed deterministic check forces score 0.0), **AGENTIC** (active probes via
  browser/IMAP/shell). Philosophy — "check real system state, not agent self-reports" — is close
  kin to orca-fleet's "the trace is never the oracle." The gap: independence is *optional*
  (the Show HN author explicitly notes nothing requires a separate validator), and there is no
  negative control, no ancestry/freshness, no frozen criterion denominator.
- **Sigstore-community attestation** — the SLSA-provenance-as-in-toto-statement + cosign
  sign/verify stack (with slsa-verifier / policy-controller for gates). It is the strongest on
  **SHA/signature binding** and on **independent verification as a distinct process**, and it is
  genuinely tamper-evident. But it answers "was this artifact built from this source by this
  builder", i.e. supply-chain integrity — *not* "does this change satisfy its acceptance
  criteria, proven by a test that can fail". Different question; adjacent, not overlapping.
- **AWS CI mutation-testing gate** — the pattern of a CodeBuild/CodePipeline **test action** that
  fails the pipeline below a mutation-score threshold, using PIT (JVM) or Stryker (JS/TS/.NET) in
  a `break`-at-threshold config. It is the only column that ships a real **negative control**
  (kill-the-mutant) and a **clean-env re-run** (ephemeral build container). Honest scoping: AWS's
  own docs cover the *test-gate mechanism* and a control framework for coding agents; the
  *mutation* tooling itself is community (PIT/Stryker) run on AWS CI — there is **no single
  AWS-authored, mutation-specific gate sample** found as of 2026-08-28 (marked UNVERIFIED where it
  matters). It also binds no manifest, no ancestry, no review freshness, and self-scores in one
  pipeline.

**The honest finding.** Each shipping approach owns one or two columns. **No single evidence
approach found as of 2026-08-28 combines all six** — SHA-binding *and* ancestry *and* clean-env
re-run *and* a revert-to-red negative control *and* reviewed-SHA freshness *and* an enforced
independent second-session re-derivation. That is a statement of absence-of-evidence from the
sources checked below, not a claim that no such tool can exist. The two properties with the
thinnest external prior art are the **mandatory negative control** and the **enforced
independent-session re-derivation from a frozen contract**; both are corroborated as *ideas in the
air* by recent research (Microsoft's "Building to the Test", the "Executive Disposes" executive
model — see the competitive brief) but not, as of this date, as a bundled shipping product.

## Part 3 — One-way / two-way-door governance

orca-fleet classifies every decision a fleet hits *before* anyone answers it
([runtime/gate-classification.md](../../runtime/gate-classification.md)). The core rule:
**governance is below the model — policy is enforced, not requested.**

The classes map cleanly onto Amazon's one-way-vs-two-way-door framing (reversible decisions are
cheap and delegable; irreversible ones are not):

- **Mechanical (two-way door).** One defensible answer exists (tooling with a repo precedent,
  naming, retry-on-transient). The coordinator auto-resolves and logs it. Reversible.
- **Taste (two-way door).** Reasonable disagreement, still reversible (API shape, copy, structure
  within spec). The coordinator picks the recommendation, logs it, a human may veto later.
- **One-way door.** Hard or impossible to reverse, or out of authority: merge to default, deploy,
  rollback, deletion, spend, scope change, secret rotation, real credentials. **Human only —
  never auto-resolved, never defaulted on timeout.**

Two refinements make the boundary load-bearing rather than advisory: **lighting** (`lit` by
default — a human or build-blind reviewer sees the change before it lands; `dark-eligible` only for
reversible testnet/fixtures behind a cheap unfakeable oracle, never for auth/payments/deploys), and
the **user-challenge** rule (when the fleet concludes the user's own direction is wrong, that is
itself a one-way decision — the fleet argues its case and names its blind spots, but never
auto-overrides).

**Independent convergence.** The same "keep the enforcing gate below the model" discipline shows
up in security-operations automation. UnderDefense's 2026 AI-SOC writeups describe a pipeline where
the model detects, enriches, and *recommends* a containment action with a confidence score, but a
**human approval gate sits below the model** for irreversible actions (endpoint isolation, account
disablement), and every playbook step is tagged **deterministic** (safe to auto-execute after
approval) vs **investigative** (needs human interpretation) before agentic containment is enabled.
That is the same architecture as orca-fleet's mechanical/taste/one-way split and its lit-vs-dark
lighting rule, arrived at from a different domain: **deterministic, human-owned gates for
irreversible actions; delegated automation only for the reversible, cheaply-checkable ones.**

Honest scoping on this reference: the UnderDefense material verified on 2026-08-28 is a set of
first-party 2026 blog posts (the flagship "AI SOC automation in 2026" piece and companions), not a
peer-reviewed source; it is cited as *evidence the pattern converged in industry practice*, not as
a formal proof. The underlying one-way/two-way-door vocabulary is Amazon's, widely documented in
the Bezos shareholder letters and treated here as background rather than a load-bearing web
citation. No published counterpart was found, as of 2026-08-28, that applies this
below-the-model gate discipline specifically to a *coding-agent fleet's* completion and merge
decisions the way this repo's runtime policies do.

## Sources — flat list with access dates

All accessed **2026-08-28**.

**Part 1 — convergent topology**

- <https://yegge.ai/gastown> — Gas Town project site; substantiates the Mayor/Beads/Refinery/
  Polecat topology and its "orchestrator for AI coding agents" framing.
- <https://steve-yegge.medium.com/welcome-to-gas-town-4f25ee16dd04> — Yegge's "Welcome to Gas Town"
  (2026-01-01); substantiates release date, MIT/Go, git-worktree isolation + git-backed Beads
  ledger + merge queue.
- <https://github.com/jayminwest/overstory> — Overstory repo (read directly); substantiates
  worktree-isolated workers + SQLite mail ledger + `ov merge`, MIT license, and the **archived /
  successor-is-Warren** status.
- <https://github.com/ComposioHQ/agent-orchestrator> — Composio Agent Orchestrator; substantiates
  one-worktree-branch-PR-per-worker, central dashboard/ledger, and orchestrated PR lifecycle
  (CI-fix, review, conflict), MIT.

**Part 2 — evidence protocols**

- <https://www.vr.dev/> and <https://github.com/vrDotDev/vr-dev> — vr.dev; substantiates the
  HARD/SOFT/AGENTIC verifier tiers, deterministic git/DB/file probes, and MIT `pip install vrdev`.
- <https://news.ycombinator.com/item?id=47322919> — "Show HN: VR.dev" (2026-03-10); substantiates
  the ~38-verifiers/19-domains count, `fail_closed` composition, and the author's own statement
  that independent (separate-context) validation is *not* required by the design.
- <https://slsa.dev/spec/v1.0/provenance> — SLSA provenance spec; substantiates SLSA provenance as
  an in-toto statement binding an artifact digest (subject) to source repo + commit (predicate).
- <https://docs.sigstore.dev/> — Sigstore/cosign docs; substantiates `cosign attest` /
  `cosign verify-attestation` signing and independent verification of in-toto/SLSA attestations.
- <https://github.com/slsa-framework/slsa-verifier> — slsa-verifier; substantiates independent,
  out-of-band verification of provenance against expected source/tag/builder.
- <https://docs.aws.amazon.com/codebuild/latest/userguide/how-to-create-pipeline-add-test.html> —
  AWS CodeBuild test action; substantiates a test stage as a blocking pipeline gate (non-zero exit
  fails the pipeline) in a clean CodeBuild container.
- <https://aws.amazon.com/blogs/security/balancing-speed-and-safety-a-control-framework-for-ai-coding-agents/>
  — AWS security blog; substantiates AWS's own framing of automated gates/controls for AI coding
  agents (context for the "gate below the model" pattern in Part 3, and that AWS treats gates, not
  mutation specifically, as the primitive).
- <https://pitest.org/> — PIT (pitest); substantiates JVM mutation testing with a
  break-at-threshold mutation score.
- <https://stryker-mutator.io/> — Stryker; substantiates JS/TS/.NET mutation testing with a
  `break` threshold that fails CI (the negative-control mechanism referenced in the table).

**Part 3 — governance**

- <https://underdefense.com/blog/ai-soc-automation/> — UnderDefense "AI SOC automation in 2026";
  substantiates the deterministic-vs-investigative step tagging and a human approval gate sitting
  *below* the model for irreversible containment actions (independent convergence on
  gates-below-the-model).
- <https://underdefense.com/blog/ai-soc-implementation-guide/> — UnderDefense implementation
  guide; corroborates the phase-gate / governance-below-autonomy framing.

**Internal (this repo)**

- [runtime/evidence-manifest.md](../../runtime/evidence-manifest.md) — the six-property definition
  of done scored in Part 2.
- [runtime/gate-classification.md](../../runtime/gate-classification.md) — the mechanical/taste/
  one-way classification and lit/dark lighting rule summarized in Part 3.
- [docs/concepts.md](../concepts.md) — coordinator/worker topology, merge train, and the
  human-language rationale.
- [2026-08-28 competitive scan](2026-08-28-competitive-landscape-differentiation.md) and
  [forward roadmap](2026-08-28-forward-roadmap-and-defensibility-plan.md) — the deep briefs this
  doc distills.

## Self-audit — VERIFIED vs INFERRED/UNVERIFIED

- **VERIFIED (fresh primary-source pass, 2026-08-28):** the converged topology of Gas Town,
  Overstory, and Composio (worktrees + git-backed ledger + serialized merge); Overstory's archived
  status; vr.dev's HARD/SOFT/AGENTIC tiers and its optional-independence admission; SLSA/in-toto +
  cosign SHA/signature binding and out-of-band verification; the AWS CodeBuild test-gate mechanism
  and PIT/Stryker break-at-threshold mutation gating; UnderDefense's below-the-model human approval
  gate and deterministic/investigative step tagging.
- **INFERRED (reasoning from primary sources, not lifted verbatim):** the six-column ✓/◐/✗ scoring
  of each competitor — the sources confirm each capability's presence or absence, but the
  compression into this rubric is my judgment; and the claim that "no single approach combines all
  six", which is an absence-of-evidence conclusion over the tools I checked, not a proof of
  universal absence.
- **UNVERIFIED / flagged:** that any AWS-authored, *mutation-specific* completion-gate sample
  exists (none found — AWS ships the gate mechanism, the mutation tooling is community); that
  Sigstore/vr.dev/AWS bind a *completion manifest* (they bind artifacts/state, a related but
  distinct thing); Gas Town's finer internals beyond Yegge's own writeups; and the Amazon
  one-way/two-way-door origin, cited as widely-documented background rather than re-fetched here.
- **Framing discipline:** every novelty statement is phrased as "no published counterpart found as
  of 2026-08-28" with the sources checked; none is a bare "first" or "only". The competitive-scan
  brief this distills carries its own UNVERIFIED caveats (adoption numbers, secondary reporting)
  which are not restated as fact here.
