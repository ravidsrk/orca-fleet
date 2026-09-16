# Leg 1 — clean-sweep: frozen enumeration (source=audit)

Denominator: the 7 seeded findings named in the issue #417 chain-declaration
comment (posted 2026-09-16T05:54:51Z, BEFORE the run). That comment is the audit
document; this file freezes it as the leg-1 task specs. Frozen 2026-09-16,
BASE `chain417/leg1-cleansweep-base` @ `892eae208b01780a426deecdf9e81380753b30cc`.

| id | finding (criterion) | triage repro | class |
|---|---|---|---|
| F1 | `notes.py`: hardcoded fallback admin token `admin-secret-12345` (SEED-1) | code read: `ADMIN_TOKEN = "admin-secret-12345"` line 16 | real, security → PARKED out-of-scope (harden-it owns secrets) |
| F2 | `notes.py:add_note`: SQL built by `%` string interpolation (SEED-2) | code read lines 30-33 | real, security → PARKED out-of-scope (harden-it owns injection; exploit proof is its unit) |
| F3 | `notes.py:delete_note`: caller passing `None` token deletes (SEED-3) | `delete 1` with no token → `deleted` (exit 0); must be `denied` | real-bug → FIX (deny on None). Timing-`==` aspect noticed-not-touched → carried |
| F4 | `export_notes` crashes on an empty store (SEED-4) | fresh DB export → exit 0, file contains `[]` | REFUTED as stated → close `refuted` with pasted evidence |
| F5 | `hash_body` uses MD5 (SEED-5) | `hash_body('x') == md5('x')`, 32-hex | real-bug-small → FIX (SHA-256) |
| F6 | README claims export is AES-256 encrypted (SEED-6) | export output is verbatim `json.dump` plaintext; `AES` only in README | doc-claim false → FIX doc |
| F7 | README claims delete always requires the admin token (SEED-7) | falsified by F3 repro at triage; becomes TRUE when F3 lands | doc-claim → resolved by F3 fix, verified post-merge |

Out-of-scope rule applied (SKILL anti-patterns: a mission must not own
security findings): F1/F2 park `out-of-scope` with handoff to leg 2. The
`==` timing aspect of F3 is noticed-not-touched and carried as leg-2
enumeration input (triage, never pre-confirmed).
