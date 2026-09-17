# Lenses — Risk review, scope-gated (router: addy)

Scope signals from `diff_scope.py --json --strict` (exit 0, `unmatched: []`;
transcript `transcripts/diff-scope.json`). Tally check: zero `lens-tally:`
lines in `docs/DECISIONS.md` — no auto-gate streak anywhere. Every lens below
is ran or recorded gate-off; NEVER_GATE lenses (security, privacy,
data-migration) all ran.

## Security (NEVER_GATE — ran, bounded) — CLEAN

Threat model first: the diff adds report prose, seed fixtures, and one git
bundle under `docs/`; it crosses no trust boundary, ships no dependency, auth
path, route, or executable config, and reaches no live system. STRIDE over
that surface: no spoofing/tampering/repudiation/info-disclosure/DoS/elevation
vector beyond "malicious content in the report", addressed below.

- Secret scan: `gitleaks detect --no-git --source docs/reports/chaining-2026-09-16/`
  → "no leaks found" (~59.77 KB scanned); plus a credential-shape grep over
  added lines (AWS keys, `ghp_`/`github_pat_`, private-key blocks,
  assigned password/secret values, Slack/Live/API keys) → zero hits. Transcript
  `transcripts/secret-scan.txt`.
- Bundle safety: `git bundle verify` → "is okay … complete history". Bundles
  carry refs/objects only — no hooks, no config execution on clone. The
  observed `remote HEAD refers to nonexistent ref` warning on clone is the
  cosmetic one RESTORE.md already documents.
- Seed fixtures (`seed-notes.py`, `seed-test_notes.py`) deliberately contain
  vulnerable patterns (SQL `%` interpolation, MD5, hardcoded token). Each is
  labeled in-file as seeded PoC material for the exercise:

  > `seed-notes.py:14-15`: `# SEED-1 (harden-it PoC material): hardcoded fallback admin token.` / `ADMIN_TOKEN = "admin-secret-12345"`

  Triage hard exclusion applies: test fixtures imported by no production code
  (repo-wide import grep: zero importers; the dashed filename is not even
  importable; `pytest`/`unittest` collection unaffected — see run-report
  gates). Discarded as vulnerability candidates with this reason, not silently.
- Quoted seed token in report prose (`handoff-log.md:11`,
  `enumeration.md:10`, `seed-notes.py:15`): scratch-seed PoC material,
  documented as the finding itself. Variant analysis (triage §6): repo-wide
  grep confines `admin-secret-12345` to these 3 new files; absent at the fixed
  point. No exploit scenario exists — no live system, no reachable call — so
  per the lens rules no security finding is filed.

### SEC-FYI1 (FYI) — quoted seed credential in committed prose

Accepted: scratch-only, labeled, gitleaks-clean, variant-confined. Recorded
so a future scanner hit on the string resolves to this verdict instead of a
fresh incident.

## Privacy (NEVER_GATE — ran) — CLEAN

No personal-data field added, moved, stored, logged, exported, or forwarded.
The only human identifier in the diff is the operator username inside pytest
tmp paths pasted into NC transcripts:

> `leg1/nc-f3-red.txt:5`: `tmp_path = PosixPath('/private/var/folders/65/nfjkpf196n5_xrwbkyrrgqrc0000gn/T/pytest-of-ravindra/…`

That is the repo maintainer's own public handle (commit authorship across the
repo), not third-party PII — considered and dropped with this reason
(recorded as PRI-FYI1, informational only).

## Data-migration (NEVER_GATE — ran as N/A)

Script `MIGRATIONS=false`; inspection confirms: no schema, migration, or
data-store change anywhere in the 28 files. Recorded N/A with evidence (the
value of a NEVER_GATE lens is the miss it would catch — there is nothing to
miss here).

## Performance (script-flagged — ran bounded) — CLEAN

`diff_scope` flagged PERF on keyword hits only: embedded `index <sha>`
header lines inside the quoted `full-diff.txt` transcript plus prose
("permissions" matched no perf pattern; the hits are the three `index …`
lines). Inspected: no render, query, cache, throttle, or code-bundle surface
exists in the diff (`target-417.bundle` is a git bundle artifact, not a
shipped code bundle). With no baseline reachable and no code shipping to
production, there is no measured or potential-impact finding to file. The
flag is recorded here as keyword noise with its trigger lines cited, not
hidden.

## API-contract — recorded gate-off

Script `API=false`; no public route, interface, or contract change in the
diff (docs-only). Lens not dispatched, with this reason recorded.

## Accessibility — recorded gate-off

Script `A11Y=false`; markdown prose and transcripts only, no component or
markup surface. Lens not dispatched, with this reason recorded. No WCAG 2.2
item arises, so nothing parks to `access-it`.

## Simplification (advisory) — no findings

Every new file serves a stated criterion: `seed-*` + `full-diff.txt` +
bundle + `RESTORE.md` serve AC-5 / gap G4 / the Greptile P1 re-derivability
fix; manifests + transcripts serve AC-2/AC-3; `gaps.md` serves AC-4. No
unrequested abstraction, helper, or speculative structure. No advisory items.

## Lens tally

`security:0 privacy:0 data-migration:0(n/a) perf:0 api-contract:gate-off a11y:gate-off simplification:0` —
appended to `lens-tally.md` (run-local equivalent; `docs/DECISIONS.md` itself
untouched per the report-only boundary — recorded deviation).

(Self-verified — no independent verifier.)
