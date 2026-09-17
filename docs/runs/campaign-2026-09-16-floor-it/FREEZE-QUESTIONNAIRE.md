# FREEZE questionnaire — floor-it self-test (headless park OPS-1)

- Purpose: freeze the quality-bar table (dimension × threshold × tool × gate-job) for orca-fleet.
- Sender: floor-it self-test run, `docs/runs/campaign-2026-09-16-floor-it/` on branch
  `campaign/floor-it-selftest` (fork point `c46d4b3`).
- Recipient: the repo maintainer who can approve the bar and its promotion (whoever owns the
  BASE→default promotion review). If that is not you, the first ask is: who?
- Where answers go: reply in this file's answer stubs (or a comment pointing at it); the unparking
  run commits the frozen table as repo-root `CONSTRAINTS.md` and proceeds to WIRE + PROVE-FIRES.
- Effort: ~15 minutes against FREEZE-PROPOSAL.md. Deadline: none (the run is parked, nothing burns).
- Partial answers and "I don't know" are explicitly welcome — flag rather than skip.

Context: the run measured the repo's own counters at the fork point (1490 tests green, validate
21/21, ruff/gitleaks/routing/bundle/vf-bench all green; coverage runner absent; no perf or a11y
surface) and drafted a 12-row bar freezing each dimension where the repo stands. Thresholds are a
one-way door, so a headless run cannot freeze them — that is this questionnaire.

## Q1 — D1–D8 thresholds (the measured eight)

Do you freeze each proposed threshold as written (bar = current measurement), or amend any?
(One line per amended row; unmentioned rows freeze as proposed — only if you also answer Q5 yes.)

- D1 suite-green (unittest exit 0):
- D2 catalog-valid (validate.py exit 0):
- D3 lint-clean (ruff 0 findings):
- D4 secrets-clean (gitleaks 0 leaks):
- D5 routing-eval (≥ 1.0):
- D6 proof-honesty (proof_status + run_report exit 0):
- D7 bundle-self-contained (bundle --check exit 0):
- D8 verifier-soundness (vf-bench false-done 0, skipped 0):

Answer:

## Q2 — D9 coverage (no tool exists today)

(a) Charter a WIRE unit to install `coverage.py` with threshold ___ on scope ___ (recommended
default: line ≥ 80% on `runtime/scripts` + `scripts`, ratchet-only)? Or (b) PARK coverage as
untoolable with human gate ___ (e.g. "coverage reviewed on each PR by a human")?

Answer:

## Q3 — D10/D11 parks + D12 fold-in

Confirm the perf + a11y not-applicable parks and folding the agentskills check into D2 — or promote
any to a real dimension (name its tool + threshold + gate job).

Answer:

## Q4 — Guard surface

Confirm the waiver-gated tool-config surface (`.gitleaksignore`, `ruff.toml` select,
`ROUTING_MIN_SCORE`, eval suite, vf-bench corpus, `CONSTRAINTS.md` numbers) — additions/removals?

Answer:

## Q5 — The freeze (explicit yes required)

Do you FREEZE the table as answered above? Write exactly: `FREEZE: yes — <your name/handle> — <date>`.
Anything else (including silence) leaves the run PARKED.

Answer:

---

VERIFY-COMPLETE (checked by the unparking worker in a fresh session, never closed on assertion):
`test -f CONSTRAINTS.md` at the repo root on the BASE successor AND `git log --oneline -1 --
CONSTRAINTS.md` non-empty AND a `docs/DECISIONS.md` line with `class=one-way`, `source=human:<who>`
naming this freeze AND every Q1–Q5 stub above answered. Command form:
`test -f CONSTRAINTS.md && git log --oneline -1 -- CONSTRAINTS.md && grep -c 'floor-freeze' docs/DECISIONS.md`
(all three non-empty).
Q1: human — FREEZE all eight as written (D1..D8 at current-standings; no amendments).
Q2: human — CHARTER the coverage.py WIRE unit (line >=80%% on runtime/scripts + scripts, ratchet-only).
Q3: human — CONFIRM parks (D10 perf + D11 a11y not-applicable) and D12 agentskills fold into D2.
Q4: human — CONFIRM guard surface as listed.
Q5: human — FREEZE: yes. Recorded 2026-09-16, interactive gate session, reporter Ravindra (explicit).
