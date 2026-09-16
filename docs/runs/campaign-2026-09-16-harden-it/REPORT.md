# Run report — harden-it self-run, 2026-09-16 (campaign-2026-09-16-harden-it)

```
RUN: mission=harden-it tier=doctrine-only inventory_at=6a7afaac65e55322f455165e8f2d27f70c5aad0a manifest=docs/runs/campaign-2026-09-16-harden-it/manifest.json verifier=GREEN waves=0
```

| Field | Value |
|---|---|
| Mission | `harden-it` — mission source revision `c46d4b3f3371e41408aed19e54476fa194c20b42`, installed location `skills/harden-it/SKILL.md` (same repo) |
| Tier claimed | `doctrine-only`; run kind: `self-run` (catalog). Recorded history, not a promotion claim (see Catalog proof promotion). |
| Target | orca-fleet itself at origin/main tip `c46d4b3` |
| Fixed point | BASE `-` (no integration base; solo audit-only run, see Deviations) · FORK_POINT `-` · frozen contract `docs/runs/campaign-2026-09-16-harden-it/CONTRACT.md` digest `sha256:de878c52eb609b3bbb28de2078db268ebd4ddafa24080420562746a9e161d09b` |
| Coordinator / workers | solo session `46f45b71` · worker profiles `PROFILE=ro`-equivalent (read-only probes; no mutation outside the run dir) · TASK pack `addy` (one router; gstack never co-mounted) |
| Orca | no live Orca terminal in this session — `run-create` refused `no_active_sender_terminal` (receipt `receipts/run-create-refused.txt`); no workers dispatched |
| Human gates | none opened, none owed |

## Terminal state

**CLEAN with recorded solo-run degradations** (D1–D4 in `LEDGER.md`): every P0/P1
that ever surfaced is refuted or below bar — zero were VERIFIED, so no fix,
re-attack, or merge was owed — and the re-audit confirms zero unrefuted P0/P1.
No open items; no parks filed.

`| task_id | finding | class | VERIFIED | BUILD_DONE | PR_OPEN | BOT | REVIEWED | MERGED | REATTACKED | WT_CLEAN | lighting | park | evidence |`

| task_id | finding | class | VERIFIED | BUILD_DONE | PR_OPEN | BOT | REVIEWED | MERGED | REATTACKED | WT_CLEAN | lighting | park | evidence |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C1 | base_ref run: interpolation (bind-check.yml:27) | ci-injection | BELOW-BAR f | n/a | n/a | n/a | n/a | n/a | n/a | n/a | lit | not-a-finding | AUDIT.md Wave B |
| C2 | gitleaks --no-git 3 hits | secret-scan | REFUTED f | n/a | n/a | n/a | n/a | n/a | n/a | n/a | lit | refuted | receipts/gitleaks-audit.txt |
| C3 | .env.example NC fallback comment | doc-drift | BELOW-BAR f | n/a | n/a | n/a | n/a | n/a | n/a | n/a | lit | not-a-finding | AUDIT.md Wave E |
| C4 | alert-on-failure step-output interpolation | ci-injection | CLEAN f | n/a | n/a | n/a | n/a | n/a | n/a | n/a | lit | not-a-finding | AUDIT.md Wave B |
| C5 | unpinned install (install.sh) | supply-chain | BELOW-BAR f | n/a | n/a | n/a | n/a | n/a | n/a | n/a | lit | not-a-finding | AUDIT.md Wave B |

Readiness: nothing landed (audit-only; branch holds evidence commits only).
Backlog (noticed, not touched — all below the gated bar): C1 env-indirection
hardening, C3 comment refresh, C5 install pinning. OPS queue: empty.

## Convergence proof

- *Every P0/P1 has a terminal disposition.* Zero P0/P1 were VERIFIED; the 5
  candidates carry terminal dispositions in `AUDIT.md` (1 refuted, 1 clean,
  3 below-bar with reasoning). Ledger rows above.
- *Every fix has a recorded RE-ATTACK verdict + class-audit note.* Vacuous: no
  fix was owed. Class sweeps were performed proactively per axis (`AUDIT.md`).
- *A final full re-audit is pasted.* Re-audit mechanical pass (gitleaks git-mode
  clean, sink sweeps clean, pin check by direct read) — `receipts/` + Pipeline
  evidence below. Same-context, not fresh-context (D3) — stated, not hidden.
- *Outcome line CLEAN or HARDENED-WITH-OPEN-ITEMS.* CLEAN with D1–D4.
- *Secret leaks route to ROTATION, never silent deletion.* No live secrets
  found; the only credential-shaped bytes were EXAMPLE fixtures (C2).

## Pipeline evidence (per phase)

| Phase | Command / action | Result | Evidence |
|---|---|---|---|
| THREAT-MODEL | STRIDE per boundary + Always/Ask-First/Never committed | digest `42ddea9b…` | `THREAT-MODEL.md` |
| BOOTSTRAP BASE | deferred: no mutation units; preflight `--mode readonly` | exit 0 | `LEDGER.md` D2 |
| AUDIT waves A–G | tree-wide security lens, 7 waves | 5 candidates, 0 VERIFIED P0/P1 | `AUDIT.md` |
| PoC ROUTING | no executable PoC; C1/C5 routed Never | no execution | `AUDIT.md` |
| VERIFY findings | traced dispositions, self-verified (D3) | 1 refuted / 1 clean / 3 below-bar | `AUDIT.md`, `LEDGER.md` |
| FIX / REVIEW / RUNTIME-PROVE / LAND | not owed (zero VERIFIED) | n/a | — |
| RE-ATTACK | not owed (no fix); deny-hook proactively probed ×27 | 0 bypasses | `receipts/deny-hook-probes.txt` |
| RE-AUDIT | gitleaks git-mode + sink sweeps re-run | clean | Pipeline section |
| REFLECT | compound-learn proposal | 5 bullets, unmerged | `REFLECTION.md` |
| Gates | `scripts/validate.py` | exit 0, 21 missions valid | `receipts/validation.txt` |
| Gates | `python3 -m unittest discover -s tests` | exit 0, 1490 tests OK | `receipts/tests.txt` |

Re-audit transcript (2026-09-16, fixed point unchanged):

```
gitleaks detect --source . → no leaks found (21.07 MB, 2.07s)
shell=True|os.system|eval|exec|pickle.loads sweep → no matches
shell eval sweep → no matches
actions/* pins → all 40-hex SHA (verified by direct read)
```

## Verifier outcome (recorded exactly)

Round 1 went RED (2 invariants: JSON evidence counted as code per #310;
unredacted gitleaks JSON pinned credential-shaped bytes) — transcript kept at
`receipts/verifier-round1-red.txt`. Evidence remediated (prose-only range,
`--redact` capture); round 2 is the graded invocation:

`python3 runtime/scripts/evidence-run.py --label verifier --manifest docs/runs/campaign-2026-09-16-harden-it/manifest.json --artifact docs/runs/campaign-2026-09-16-harden-it/receipts/verifier.txt -- python3 runtime/scripts/verify.py --manifest docs/runs/campaign-2026-09-16-harden-it/manifest.json --contract-source docs/runs/campaign-2026-09-16-harden-it/CONTRACT.md --contract-digest sha256:de878c52eb609b3bbb28de2078db268ebd4ddafa24080420562746a9e161d09b --unit-class report-only`

Output (exit 0, verbatim in `receipts/verifier.txt`):

```
NOTE: --base not given — ancestry check skipped (pre-merge/offline)
NOTE: report-only (unsupervised) — claimed with no signed dispatch record. base_sha..head_sha changes docs/tests only, so the class is consistent with the change, but nothing off-worker authorized it (#310)
verify: OK — all required checks passed
```

A direct re-run on the final manifest bytes (pins added) also exits 0
(`receipts/verifier-final.txt`). No lane flags apply (report-only, lit,
no dispatch record, no NC execution).

## WIP-curve protocol row

Inapplicable: `waves=0` — no Orca dispatch waves ran (no Run namespace, D1; no
mutation units to staff). The run was a solo coordinator audit, so there is no
builder throughput, verification latency, rework, or freshness figure to plot.
No WIP override occurred (`builders=1 reviewers=1` recorded, nothing
dispatched).

## Deviations and lessons (recorded, not hidden)

- Solo session: no Orca Run/workers (D1), no BASE (D2), no independent
  verifiers (D3), no ephemeral sandbox (D4). Each is a recorded degradation on
  the dispositions it touches, never a silent equivalence.
- Report layout follows the task order (`docs/runs/campaign-2026-09-16-harden-it/
  REPORT.md`) rather than the TEMPLATE top-level filename; sections map 1:1.
- Gates ran as direct invocations with transcripts, not through `evidence-run.py`
  (report-only checks do not consume `commands[]`); the verifier invocation uses
  the exact TEMPLATE form.
- The round-1 RED → remediation loop is kept as evidence; nothing was weakened
  to turn it green (verify.py untouched; evidence reformed to prose).

## Run-close integrity inventory (sha256)

| Artifact | sha256 | producer |
|---|---|---|
| `docs/runs/campaign-2026-09-16-harden-it/manifest.json` | `107591481ef0b3652317032abae46ca2772639d52b035bec27699ca3e92f079d` | solo coordinator 2026-09-16 |
| `docs/runs/campaign-2026-09-16-harden-it/CONTRACT.md` | `de878c52eb609b3bbb28de2078db268ebd4ddafa24080420562746a9e161d09b` | solo coordinator 2026-09-16 |
| `docs/runs/campaign-2026-09-16-harden-it/LEDGER.md` | `4292084e9d96cd30ce7aac4a8910639b441c108ff655e0d78534f7bef77a271e` | solo coordinator 2026-09-16 |
| `docs/runs/campaign-2026-09-16-harden-it/THREAT-MODEL.md` | `42ddea9b29d201cef538d6bc6f6a6c5968a95416ae32ea647f03f4d47ae94dfc` | solo coordinator 2026-09-16 |
| `docs/runs/campaign-2026-09-16-harden-it/AUDIT.md` | `f7ac64c501a9f1c320388843799ef652d24c04222796887d17f2574c8e0ff459` | solo coordinator 2026-09-16 |
| `docs/runs/campaign-2026-09-16-harden-it/REFLECTION.md` | `6b2b47ed96f3736e29948650ffcd162f90876b377e3b55cb3a51ef087d9e1173` | solo coordinator 2026-09-16 |
| `docs/runs/campaign-2026-09-16-harden-it/receipts/deny-hook-probes.txt` | `40f812c3c9cb1fbb6306adc5c8c39eb22ff0985ab1b7e8995a4e3a9dd26d704e` | deny-hook.sh probes 2026-09-16 |
| `docs/runs/campaign-2026-09-16-harden-it/receipts/gitleaks-audit.txt` | `31bc34162c62757215a3ffaab6dd2ed3a3179d021f3104956098db02c4584148` | gitleaks --redact 2026-09-16 |
| `docs/runs/campaign-2026-09-16-harden-it/receipts/run-create-refused.txt` | `b86694e766247bcebf7d7335176a9012045b3001db16f19d3670f327852628df` | orca CLI 2026-09-16 |
| `docs/runs/campaign-2026-09-16-harden-it/receipts/tests.txt` | `01722c2db94c1d6325b4f44454c2f25553ca64c5d32db0fec649de3fc3ab2cd7` | unittest 2026-09-16 |
| `docs/runs/campaign-2026-09-16-harden-it/receipts/validation.txt` | `90e1cc04c2301795dbb6306b86320f4cb65d9994187cc9ed7a251176258760a6` | scripts/validate.py 2026-09-16 |
| `docs/runs/campaign-2026-09-16-harden-it/receipts/verifier-round1-red.txt` | `730f04886e244293e7d3a5cef5d9baae470bb935f5232b11063d945b19896d6b` | verify.py round 1 2026-09-16 |
| `docs/runs/campaign-2026-09-16-harden-it/receipts/verifier.txt` | `815dfe31d7669df7715a610728308aad13ad548636227a170582c5902f09360a` | evidence-run.py + verify.py round 2 2026-09-16 |
| `docs/runs/campaign-2026-09-16-harden-it/receipts/verifier-final.txt` | `815dfe31d7669df7715a610728308aad13ad548636227a170582c5902f09360a` | verify.py final bytes 2026-09-16 |

Inventory commands (run after freezing the bytes above):

`python3 runtime/scripts/inventory.py write <report>` (not used — hashes filled by hand from frozen bytes; see below)

`python3 runtime/scripts/inventory.py check docs/runs/campaign-2026-09-16-harden-it/REPORT.md`

`python3 runtime/scripts/inventory.py check docs/runs/campaign-2026-09-16-harden-it/REPORT.md --at 6a7afaac65e55322f455165e8f2d27f70c5aad0a`

## Gates

Project gates at the evidence head (commit `199fe89e`, content-identical for all
non-run paths to the fixed point `c46d4b3` — the run changed only its own dir):

- `python3 scripts/validate.py` → exit 0 (`receipts/validation.txt`)
- `python3 -m unittest discover -s tests` → exit 0, Ran 1490 tests, OK
  (`receipts/tests.txt`)
- `python3 runtime/scripts/proof_status.py --check` → see Catalog proof promotion

## Catalog proof promotion

Not promoted: `harden-it` stays `doctrine-only`. The report binds (RUN header,
manifest in the run's own directory, inventory re-hashing at `inventory_at`,
verifier GREEN matching), but the mission's independence requirements —
independent fresh-context verifier for refutations, independent re-attack worker
per fix — cannot be satisfied in a solo session, and the fix→re-attack loop ran
vacuously (zero VERIFIED findings). Claiming `self-run` on a self-verified audit
with no exercised remediation loop would overstate. No frontmatter touched, no
README row added — per the TEMPLATE, recording alone advances nothing.

## Evidence binding

All run-owned evidence is committed on branch `campaign/harden-it-selftest`
(unpushed, per task orders). `inventory_at=6a7afaac65e55322f455165e8f2d27f70c5aad0a`
holds every artifact above including the graded manifest; `REPORT.md` itself and
the LEDGER terminal update land in the following commit (the report is excluded
from its own inventory by construction).
