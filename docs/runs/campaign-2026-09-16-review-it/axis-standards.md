# Axis — Standards (router: matt)

Scope: repo-documented standards applicable to the diff + Fowler 12-smell
baseline (judgment calls, prose N/A) per hunk. Tooling-enforced items skipped
(validate.py + unittest run pre-commit; see run report). All paths below are
at reviewed_sha `c46d4b3f`, under `docs/reports/chaining-2026-09-16/`.

Repo standards checked: `AGENTS.md`, `ARCHITECTURE.md`, `CONTRIBUTING.md`
(report-format rules: none found — no `docs/reports/` README or schema; prior
reports `clean-sweep-selfrun/`, `prove-it-selfrun/` set the prose+transcript
precedent this diff follows). Commit hygiene (dispatch-lifecycle: maintainer
authorship, no agent trailers, gitleaks before push) is a process property of
the merged PR, not of this diff's content — not graded here.

## Findings

### S-N1 (Nit) — inconsistent JSON manifest formatting within the diff

`leg1/manifest-f3.json`, `manifest-f5.json`, `manifest-f6.json` are each a
single minified line:

> `leg1/manifest-f3.json:1`: `{"artifacts": [{"path": "docs/reports/chaining-2026-09-16/leg1/leg1-f3-tests.txt", "sha256": "9310d484…`

while the rollup `leg1/manifest-leg1.json` is pretty-printed:

> `leg1/manifest-leg1.json:1-3`: `{` / ` "artifacts": [` / `  {`

No repo standard mandates either shape and both parse (hashes re-verified —
see test-adequacy axis), so this is cosmetic only. Suggested fix shape (routes
to clean-sweep/ship-it, not applied here): pretty-print the three unit
manifests to match.

### S-FYI1 (FYI) — inventory comment lines warn under `sha256sum -c`

> `integrity-inventory.txt:1`: `# Integrity inventory — chaining run 2026-09-16 (#417)`

The three `#` header lines print "improperly formatted" warnings; the check
still exits 0 with 27/27 OK. Standard practice, no action.

## Axis verdict

No Critical, no Required. Worst: 1 Nit. (Self-verified — no independent verifier.)
