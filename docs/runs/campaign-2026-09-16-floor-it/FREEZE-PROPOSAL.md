# FREEZE PROPOSAL — PROPOSED, NOT FROZEN

Status: **PROPOSAL**. No threshold below is frozen. Per floor-it + gate-classification, the freeze
is a ONE-WAY human gate; this headless run PARKS here and freezes nothing. The human freezes by
confirming (explicit yes) the table — as-is or amended — via FREEZE-QUESTIONNAIRE.md; the unparking
run then commits it as `CONSTRAINTS.md` (first change on the integration BASE successor) and
proceeds to WIRE + PROVE-FIRES.

Measured-at-freeze values were taken at `c46d4b3f3371e41408aed19e54476fa194c20b42`
(see DETECT.md; transcripts in `transcripts/`, ledger in `manifest.json`).

## Proposed frozen table (dimension × threshold × tool × gate-job × measured)

| ID | Dimension | Proposed threshold (recommended default) | Tool | Gate job (CI) | Measured at proposal |
|---|---|---|---|---|---|
| D1 | suite-green | `unittest` exit 0 (0 failures, 0 errors) | `python3 -m unittest discover -s tests` | validate.yml `gates` ("contract test suite") | 1490 pass, OK |
| D2 | catalog-valid | `validate.py` exit 0 (21/21 missions, separation holds) | `python3 scripts/validate.py` | validate.yml `gates` ("Validate missions…") | 21/21 ok |
| D3 | lint-clean | `ruff check` 0 findings on `scripts runtime/scripts tests bench demo` | `ruff check` (E9,F63,F7,F82 per ruff.toml) | validate.yml `gates` ("Ruff") | 0 findings |
| D4 | secrets-clean | `gitleaks detect` 0 leaks | pinned gitleaks 8.30.1 (`GITLEAKS_SHA256` in workflow) | validate.yml `gates` ("Secret scan") | 0 leaks / 994 commits |
| D5 | routing-eval | score ≥ 1.0 (`ROUTING_MIN_SCORE`) | `python3 scripts/eval.py run --suite routing --threshold 1.0` | validate.yml `gates` ("Routing eval gate") | 94/94 (100%) |
| D6 | proof-honesty | `proof_status.py --check` AND `run_report.py` exit 0 | both scripts | validate.yml `gates` ("proof-evidence honesty", "Proof tiers bind") | exit 0, 2 bound |
| D7 | bundle-self-contained | `bundle.py --check` exit 0 | `python3 scripts/bundle.py --check` | validate.yml `gates` ("Bundle builds…") | 21/21 |
| D8 | verifier-soundness | vf-bench gate PASS: false-done 0, skipped 0 | `python3 bench/vf-bench/gate.py` | validate.yml `vfbench` | 0/20, 0 skipped |
| D9 | coverage | **OPEN — human decides:** (a) charter a WIRE unit to install `coverage.py` + a threshold (recommended default: line ≥ 80% on `runtime/scripts` + `scripts`, ratchet-only), or (b) PARK as untoolable with a human review gate | TBD at freeze (candidate: coverage.py) | TBD (new CI step if (a)) | UNMEASURED — no runner |
| D10 | perf-budget | **Proposed PARK (not-applicable):** no repo-wide perf surface; vf-bench duration is a gate cost, not a product budget. No threshold, no tool — a vacuous check is refused. | — | — (human gate: perf-sensitive changes reviewed case-by-case) | N/A |
| D11 | a11y | **Proposed PARK (not-applicable):** no UI/render surface in this repo. | — | — (human gate: none needed; re-open if a UI ships) | N/A |
| D12 | ref-validator | **Proposed: fold into D2, not a separate dimension:** `agentskills validate` is CI-only (not installed locally) and duplicates the frontmatter checks D2 already runs. | agentskills (CI) | validate.yml `gates` ("agentskills.io reference validator") | CI-only |

Guard surface (GUARD phase, after freeze): `floor_guard.py` wired in CI on BASE — any diff lowering
a threshold above, or touching a dimension's frozen tool-config surface (`.gitleaksignore`,
`ruff.toml` select, `ROUTING_MIN_SCORE`, eval suite, vf-bench corpus), fails without a recorded
`floor-waiver:<rule>:<path>` DECISIONS grant. The waivers file is `docs/DECISIONS.md`.

## What the human is being asked (one-way, explicit-yes only)

1. Confirm/amend each D1–D8 threshold (defaults = current measured values: the bar freezes where
   the repo stands; tightening later is a new one-way decision, never mechanical).
2. Decide D9: (a) install coverage with threshold X, or (b) park with a named human gate.
3. Confirm D10/D11 parks and D12 fold-in (or promote any to a real dimension with a tool).
4. Confirm the guard surface list (tool-config files that become waiver-gated).

Silence, "looks good", and unanswered questions are NOT a freeze (decide-and-freeze).
Answer in FREEZE-QUESTIONNAIRE.md.
