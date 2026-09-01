# STATUS — 360° completion audit

**VERDICT: PHASE 4 COMPLETE — execution not yet started**
**COMPLETION: 56%** (baseline `6abf548`) · **GATE: unmet** — CF-05 (first Orca mission) not happy-path evidenced; H-01 outstanding. Angle 5 moved 2→3 after SECURITY.md.
**CRITICAL FLOWS: 6 total · 4 verified happy · 1 install-verified · 1 failure-only (CF-05) · 0 cut**
**GAPS:** see `GAPS.md` · **NEXT: P1/T-01** (stale worktree cleanup)

---

## Baseline freeze (Phase 0)

| Field | Value |
|---|---|
| Time (UTC) | 2026-09-01T13:36:40Z |
| HEAD | `6abf548de4d53b9250e13f3b2cc297f6dd8fdf01` |
| Branch at freeze | `main` (clean), audit worktree `ravidsrk/p0-completion-audit` |
| Remote | `git@github.com:ravidsrk/orca-fleet.git` · default `origin/main` |
| Dirty tree | none on `main` |
| Open PRs | 0 |
| Open issues | 0 (86 closed) |
| Local extra | worktree `/Users/ravindra/projects/orca-fleet-pr-comments` on deleted remote `ravidsrk/address-sweep-pr-comments` |
| Last CI on main | validate **success** 2026-08-30 · https://github.com/ravidsrk/orca-fleet/actions/runs/33296692840 |

### Toolchain (R1)

| Tool | Version |
|---|---|
| git | 2.55.0 |
| python3 | 3.13.15 (mise shim) |
| uv | 0.12.8 |
| mise | 2026.8.16 |
| greptile | 3.4.2 |
| gh | 2.98.0 (auth: ravidsrk) |
| ruff | 0.16.5 (present on machine, **not** invoked by this repo's CI) |
| just | 1.58.0 (present, **no** `justfile` in repo) |
| orca CLI | present; **app running=false, runtime not_running** |

No `pyproject.toml`, `requirements.txt`, `uv.lock`, `.mise.toml`, or `package.json`. Product is stdlib Python 3 + Markdown skills.

### Last 10 commits (at freeze)

```
6abf548 2026-08-30 Merge pull request #207 …
2b2373b 2026-08-30 test: keep the fail-closed review-fetch pin on shallow clones
45402af 2026-08-30 test: address leftover greptile comments from the #163-#184 sweep
32ab268 2026-08-30 Merge pull request #206 …
77be38a 2026-08-30 fix: reject explicit null lighting …
8eda885 2026-08-29 fix: treat missing manifest lighting as lit …
080cd87 2026-08-29 Merge pull request #205 …
c7a64ba 2026-08-29 chore: regenerate test-count badge after rebase
6d4959f 2026-08-29 test: pin the demo's RED to the scope-shrink …
5afbbe6 2026-08-29 test: rename eval-script check …
```

### Cold start

See `evidence/P0-coldstart-validate-tests.txt`, `P0-coldstart-tests-run2.txt`, `P0-coldstart-demo.txt`, `P0-coldstart-tools.txt`, `P0-coldstart-eval-validate.txt`.

| Step | Result |
|---|---|
| Install from lockfile | **N/A — no lockfile** (stdlib) |
| `python3 scripts/validate.py` | exit 0 · 13/13 missions valid |
| `python3 runtime/scripts/proof_status.py --check` | exit 0 |
| `python3 -m unittest discover -s tests` run 1 | 317 OK · 23.4s |
| same, run 2 | 317 OK (no flake observed) |
| `sh demo/negative-control/run.sh` | PASS (self-score GREEN / verify RED) |
| `python3 bench/vf-bench/vfbench.py` | naive 11/11 false-done · sound 0/11 |
| `python3 scripts/eval.py` (no args) | usage error (not a pass) · see `P0-eval-subcommand-note.txt` |
| `python3 scripts/eval.py validate` | All evals valid: 30 routing + 39 per-skill |
| `python3 scripts/gen-badges.py --check` | exit 0 |
| Run a mission on Orca | **FAIL substrate** — `orca status` runtime not_running |

Cold start of the *catalog gates* = **pass**. Cold start of the *fleet runtime path* = **fail** (H-01).

---

## Product inference (A-01)

**orca-fleet** is a MIT-licensed catalog of 13 outcome-named missions (`skills/<name>/SKILL.md`) plus playbooks, runtime policies, and a stdlib independent verifier (`runtime/scripts/verify.py`). Users are developers running [Orca](https://github.com/stablyai/orca) + Claude Code (or another agent host). There is no hosted app, no billing, no end-user PII store.

Plugin version **0.5.0** (`.claude-plugin/plugin.json`). CHANGELOG still has an **Unreleased** block of work landed after 0.5.0 (signed dispatch, #163–#184 sweep, #207).

---

## Critical flows

Derived from README Quick start, Getting started, Validate-and-test, and the demo — not from aspiration.

| id | name | entry | exit | money | observed |
|---|---|---|---|---|---|
| CF-01 | Catalog gates | clone + `python3 scripts/validate.py` + tests + `proof_status.py --check` | 13 missions valid, tests green, proof honest | no | **works** · `evidence/CF-01-happy-catalog-gates.txt` |
| CF-02 | Install a mission | README symlink or `/plugin install` | agent can see outcome-named skills; `../../playbooks` resolves | no | **verified** (symlinks + `playbooks/`/`runtime/` resolve two levels up) · `evidence/CF-02-happy-symlink-install.txt`. Plugin UI path not re-run. |
| CF-03 | Independent verify | `verify.py` / vf-bench | gamed traps RED; valid-control GREEN; false-done 0 | no | **works** · `evidence/CF-03-happy-vfbench.txt` |
| CF-04 | Negative-control demo | `sh demo/negative-control/run.sh` | self-scorer GREEN and verify RED on the same trap | no | **works** · `evidence/CF-04-happy-nc-demo.txt` (this is also the failure-path of a self-scoring gate) |
| CF-05 | First Orca mission | Getting started: `review this PR` with Orca running | SHA-bound review verdict | no | **partial/absent this session** · Orca app not running · `evidence/CF-05-failure-orca-not-running.txt` |
| CF-06 | Proof-honesty | `proof:` frontmatter + `proof_status.py --check` | no mission over-claims; badges fresh | no | **works** · 9 doctrine-only / 2 self-run / 2 external-run |

Written definition of done: per-mission `SKILL.md` convergence proof + `runtime/evidence-manifest.md`. Scope lives in those files + GitHub issues (currently empty).

---

## Angles

RAG: 0–1 R · 2 A · 3–4 G. Score ≥3 requires evidence (R5).

### 1. Product & critical flows — 2/A · weight 8

Findings:
- **F-1-01** Six critical flows named from README/getting-started. Evidence: this section + CF-* files.
- **F-1-02** CF-05 (the actual fleet) is the getting-started "first mission" and was not executed: Orca runtime `not_running`. Impact: a stranger following getting-started past clone/test cannot complete the advertised first mission on this machine today.
- **F-1-03** Nine of thirteen missions remain `doctrine-only` (honest). Impact: catalog is complete as doctrine; field-proof is not.

Evidence: CF-01..06 files. Score 2: catalog-side happy paths work; the runtime path is a listed gap.

### 2. Functional completeness — 2/A · weight 14

- **F-2-01** `TODO`/`FIXME`/`HACK`/`XXX` in product code: essentially none (2 incidental hits in docs: dispatch-lifecycle "todo" lane name; a research "hack" URL). `TODOS.md` has one open P2 (shared validator grammar).
- **F-2-02** No feature flags, no "coming soon" product surfaces, no mocks on non-test paths found.
- **F-2-03** Half-built: `docs/distribution.md` external marketplace checklist is all unchecked. Proof-status badge (`assets/badges/proof.json`) is documented as deferred.
- **F-2-04** Plugin version 0.5.0 vs Unreleased changelog containing post-0.5.0 verifier work — a stranger reading the version badge undercounts HEAD.

Evidence: cold start, TODOS.md, distribution.md, plugin.json.

### 3. Code quality & architecture — 3/G · weight 4

- **F-3-01** Structure matches README three-layer split; `validate.py` enforces it. Evidence: validate 13/13.
- **F-3-02** Largest files: `tests/test_verify.py` 1079, `tests/test_validate.py` 669, `verify.py` 636, `validate.py` 583. Not god-objects relative to their jobs.
- **F-3-03** No ruff/mypy config in repo; CI does not lint. Machine has ruff. Impact: style is social, not gated.
- **F-3-04** No lockfile: acceptable for stdlib-only, but Python version is unpinned (`python-version: "3.x"` in CI).

Evidence: validate output, `wc -l`, `.github/workflows/validate.yml`. Score 3: architecture is tested; lint-in-CI is a listed gap at S3.

### 4. Testing — 3/G · weight 8

- **F-4-01** 317 contract tests, CI on push/PR to main, proof_status --check in CI. Evidence: P0 transcripts + GH run 33296692840 success.
- **F-4-02** Suite run twice this session: both 317 OK. No flake observed.
- **F-4-03** Coverage of *catalog* critical flows is high (validate, verify, vf-bench, demo). Coverage of *Orca-dispatch* critical flow is zero in this repo (by design: Orca is external).
- **F-4-04** Time to green locally ~23s.

Evidence: P0-coldstart-*.txt. Score 3 for the catalog; CF-05 is not this angle's job.

### 5. Security — 2/A · weight 14

- **F-5-01** No HTTP API, no AuthN/AuthZ surface in this repo. N/A for routes. Impact: none.
- **F-5-02** `.gitignore` covers `.env` and `.secrets/*` (keeps `*.pub`). `gen-key` refuse-in-repo shipped in #166. No `.env.example` listing the live `ORCA_*` gate surface (documented in `docs/verify-gate.md` instead).
- **F-5-03** Tracked-file secret-pattern grep: only the documented fake AWS example in `docs/reports/harden-it-externalrun/README.md`.
- **F-5-04** No `SECURITY.md`, no `CODEOWNERS`, no private-vulnerability reporting path.
- **F-5-05** Native completion hook is **advisory** in-session (documented, #112/#135). Soundness is off-worker. Not a silent hole.
- **F-5-06** No third-party Python deps → `pip-audit`/`uv audit` has nothing to run. Vendored ed25519 has canonical/small-order checks (#175).
- **F-5-07** No money paths in this product.
- **F-5-08** Prompt-injection: missions ingest user goals into agent context (the host's problem). `pm.py` sanitizes inbox text (#176). Untrusted-content rule (R3) is this driver's; the pack itself is instruction text for agents — that *is* the product.

Evidence: gitignore, verify-gate.md, harden-it report, test_ed25519, test_pm. Score 2: happy-path secret hygiene works; SECURITY.md and env-example missing.

### 6. Data — N/A

Reason: no application database, migrations, or user-data store in this repository. Orca's SQLite is *outside* this repo (`runtime/liveness-resume.md` describes Orca, not orca-fleet). No PII inventory to keep. Check: `rg postgres|sqlite|sqlalchemy` hits docs/examples only.

### 7. Infra & deploy — 2/A · weight 6

- **F-7-01** "Deploy" = merge to `main` + plugin marketplace copy. CI is the only environment. No IaC, no staging, no containers.
- **F-7-02** CI Python is `"3.x"` (moving). Local is 3.13.15. Reproducibility gap.
- **F-7-03** Rollback = git revert. Not rehearsed this run (A-10).
- **F-7-04** `actions/checkout` and `setup-python` are SHA-pinned. Good.

Evidence: `.github/workflows/validate.yml`, GH run success.

### 8. Reliability — 2/A · weight 5

- **F-8-01** Verifier fail-closed is the reliability story (exit 2 blocks). Evidence: demo + vf-bench.
- **F-8-02** No health endpoints (no server). No runbook for "Orca is down" beyond getting-started troubleshooting.
- **F-8-03** No retries/circuit breakers because there are no outbound product calls except `gh`/`git` inside verify.py (fail-closed).

Score 2.

### 9. Observability — 1/R · weight 4

- **F-9-01** `verify.py` / `validate.py` print human stdout/stderr. No request IDs, no metrics, no error tracker, no alerts besides GitHub Actions email (not proven to fire this run).
- **F-9-02** CI failure is the de-facto alert. Not demonstrated.

Score 1. For an OSS CLI pack this is expected; still not "operable from docs alone" at 2 a.m. without GitHub notification proof.

### 10. Performance & cost — 2/A · weight 5

- **F-10-01** Catalog gates: 23s tests, validate instant. No load test (not a service).
- **F-10-02** No cloud/LLM spend in this repo. Agent-host token cost is the user's.

Evidence: P0 timing. Score 2.

### 11. Integrations — 2/A · weight 5

| Provider | Role | This session |
|---|---|---|
| GitHub | issues, PRs, `gh api` review lookup | authenticated as ravidsrk |
| Orca | hard runtime dependency | **not running** |
| Claude Code plugin marketplace | distribution | not submitted (`docs/distribution.md` checklist open) |
| greptile | review gate | CLI 3.4.2 present |
| agentskills.io | spec | catalog claims conformance; not independently `skills-ref validate`'d this run |

- **F-11-01** Orca down blocks CF-05.
- **F-11-02** Marketplace aggregators unchecked.

### 12. AI / LLM layer — N/A

Reason: this repo does not call an LLM. `rg` of `openai|anthropic|litellm|langchain` in `runtime/scripts` and `scripts/` is empty; remaining hits are research docs. Prompts live in `SKILL.md` as instructions for *host* agents.

### 13. UX & frontend — N/A

Reason: no GUI, no CSS/HTML app. UX is README + getting-started + CLI stderr. Covered under angles 1 and 14.

### 14. Documentation — 3/G · weight 3

- **F-14-01** README + getting-started + ARCHITECTURE + 13 mission guides + CONTRIBUTING. Contract tests bind several doc claims (`tests/test_docs_navigation.py`).
- **F-14-02** Stranger Test of *catalog gates* (clone → validate → tests → demo) succeeded this session in ~1 minute of commands (suite 23s). Target ≤15 min: **pass** for CF-01/04.
- **F-14-03** Stranger Test of *first mission* (CF-05) cannot start without Orca. Getting-started states the prerequisite; still a hole in "from clone to first mission".
- **F-14-04** No `SECURITY.md`.

Evidence: getting-started.md, CF-01, CF-04, CF-05. Score 3 for catalog docs; CF-05 is H-01 not a docs rewrite.

### 15. Legal & compliance — 2/A · weight 5

- **F-15-01** MIT LICENSE present (Copyright 2026 Ravindra Kumar).
- **F-15-02** No Terms/Privacy/DPA — acceptable for a library that does not process customer PII (A-02). Still missing a security-reporting address.
- **F-15-03** `docs/compliance-provenance.md` exists for attest-it doctrine, not for this pack's own operators.
- Domain Appendix D (India payments/crypto): **no effect** (A-02). DPDP: no product-side personal data.

### 16. GTM readiness — 1/R · weight 4

- **F-16-01** Landing = GitHub README (truthful about proof mix). No separate marketing site.
- **F-16-02** No pricing/billing (free OSS).
- **F-16-03** `docs/distribution.md` marketplace checklist all `[ ]`. Version badge 0.5.0 lags HEAD.
- **F-16-04** No support channel documented (GitHub issues is the implicit channel; 0 open).

Score 1.

### 17. Ownership & ops — 2/A · weight 2

- **F-17-01** Bus factor 1 (ravidsrk). CONTRIBUTING is strong. No account inventory (GitHub, plugin marketplace, greptile, agentskills listing).
- **F-17-02** Incident process: not written. 2 a.m. = read getting-started troubleshooting + CI logs.
- **F-17-03** Stale local worktree for a deleted remote branch (ops hygiene).

---

## Completion score (informational)

N/A dropped: 6 (w=8), 12 (w=5), 13 (w=5). Active weight sum = 105 − 18 = **87** (A-04: table sums to 105).

`Σ(w×score/4) = 8×2/4 + 14×2/4 + 4×3/4 + 8×3/4 + 14×2/4 + 6×2/4 + 5×2/4 + 4×1/4 + 5×2/4 + 5×2/4 + 3×3/4 + 5×2/4 + 4×1/4 + 2×2/4`
= 4 + 7 + 3 + 6 + 7 + 3 + 2.5 + 1 + 2.5 + 2.5 + 2.25 + 2.5 + 1 + 1 = **45.25**

**completion_pct = 45.25 / 87 × 100 = 52%**

The gate in `DEFINITION.md` is binding, not this number.

---

## Top risks

1. CF-05 blocked on Orca not running → H-01
2. No SECURITY.md / disclosure path → G-02 / T-03
3. CI Python unpinned `"3.x"` → G-03 / T-04
4. Marketplace / indexer listings unchecked → H-02
5. 9 doctrine-only missions (honest, but GTM story is "4 proven") → DEFER

## Second look (Phase 1)

Changed: refused to give angle 1 a 3 while CF-05 is unwitnessed. No change to N/A set.
