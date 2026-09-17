# INVENTORY — modernize-it self-test, orca-fleet @ origin/main tip

Read 2026-09-16. Target: this repo at `c46d4b3f3371e41408aed19e54476fa194c20b42`
(Merge PR #445). Method: primary sources only (PyPI JSON/Simple APIs, `git ls-remote`
tags, OSV API, GitHub Advisory API, upstream CHANGELOG at the release tag).

## 1. Dependency surface (complete enumeration)

Manifest search (all depths, excl `.git`): no `package.json`, `requirements*.txt`,
`pyproject.toml`, `Pipfile`, `setup.py`, `go.mod`, `Cargo.toml`, `Gemfile`, `pom.xml`,
`Dockerfile`, `.nvmrc`, or `.python-version`. All first-party Python (`scripts/`,
`runtime/scripts/`, `tests/`, `hooks/`, `bench/`, `demo/`) imports stdlib only
(verified by import sweep 2026-09-16; full list in the run transcript).

The ENTIRE third-party surface is CI/platform pins:

| # | Surface | Pinned | File |
|---|---|---|---|
| 1 | `ruff` (direct, hashed) | `0.16.5` | `.github/ci-tools.lock` |
| 2 | `skills-ref` (direct, hashed) | `0.1.1` | `.github/ci-tools.lock` |
| 3 | `click` (via skills-ref) | `8.5.0` | `.github/ci-tools.lock` |
| 4 | `strictyaml` (via skills-ref) | `1.7.3` | `.github/ci-tools.lock` |
| 5 | `python-dateutil` (via strictyaml) | `2.9.0.post0` | `.github/ci-tools.lock` |
| 6 | `six` (via python-dateutil) | `1.17.0` | `.github/ci-tools.lock` |
| 7 | `actions/checkout` (SHA pin) | `3d3c42e` = v7.0.1 | `.github/workflows/*.yml` (5 uses) |
| 8 | `actions/setup-python` (SHA pin) | `5fda3b9` = v7.0.0 | `.github/workflows/*.yml` (5 uses) |
| 9 | `gitleaks` (version + sha256) | `8.30.1` | `.github/workflows/validate.yml` |
| 10 | `python` (CI + ruff target) | `3.13` | workflows + `ruff.toml` (`py313`) |

Explicitly OUT of this mission's scope (different unit/oracle, owned elsewhere):
`runtime/pins.json` (`orca` v1.4.203 + `gstack`/`addyosmani`/`mattpocock` pack pins) —
owned by `pin-it` (runtime mechanics re-witness) and the upstream-adoption audit
cadence, per the pins.json `_about` field. Bumping it here would cross the
mission-identity line (ARCHITECTURE.md).

## 2. Currency vs the "current supported" authority

Authority order per SKILL: (1) explicit project constraint, (2) the dependency's own
support/EOL policy, (3) registry-latest only when neither exists.

| Dep | Pinned | Registry-latest (source, read 2026-09-16) | Authority + verdict |
|---|---|---|---|
| ruff | 0.16.5 | **0.16.7** (PyPI JSON) | (3) Astral publishes no LTS/EOL for ruff 0.x; project sets no ruff constraint → latest is truth → **OUTDATED (patch)** |
| skills-ref | 0.1.1 | 0.1.1 (PyPI JSON); not yanked; requires_python >=3.11; uploaded 2026-01-10 | (3) at latest → **CURRENT** |
| click | 8.5.0 | 8.5.0 (PyPI) | (3) at latest → **CURRENT** |
| strictyaml | 1.7.3 | 1.7.3 (PyPI) | (3) at latest → **CURRENT** |
| python-dateutil | 2.9.0.post0 | 2.9.0.post0 (PyPI) | (3) at latest → **CURRENT** |
| six | 1.17.0 | 1.17.0 (PyPI) | (3) at latest → **CURRENT** |
| actions/checkout | v7.0.1 (`3d3c42e`) | v7.0.1 = `v7` tip (`git ls-remote`, same SHA) | (2) GitHub's supported major is v7 (Node 24; Node 20 left runners 2026-09-23, #367) → **CURRENT** |
| actions/setup-python | v7.0.0 (`5fda3b9`) | v7.0.0 = `v7` tip (`git ls-remote`, same SHA) | (2) same → **CURRENT** |
| gitleaks | 8.30.1 | v8.30.1 = newest tag (`git ls-remote`) | (3) at latest → **CURRENT** |
| python | 3.13 | 3.13/3.14 line current (project pins 3.13 deliberately, G-03) | (1) project constraint 3.13 + 3.13 in support → **CURRENT** (registry-latest is not the truth) |

## 3. The one outdated node: ruff 0.16.5 → 0.16.7 (changelog, not version delta)

Source: `https://raw.githubusercontent.com/astral-sh/ruff/0.16.7/CHANGELOG.md` (read
2026-09-16; releases 0.16.6 on 2026-09-03, 0.16.7 on 2026-09-10).

- **0.16.6**: preview-only features (pytest/autofix/isort), bug fixes (incl. a `match`
  panic fix B031, unary-expression parse validation), one display-only rule fix
  (PTH208), docs. No config-format change, no stable-rule removals.
- **0.16.7**: preview-only features (RUF077, `re.prefixmatch`), bug fixes (incl.
  ISC003 fix-safety, TID254 multi-member skip), rule changes (D211/D203 diagnostic,
  pyupgrade UP035, Python 3.15 parser updates), perf, docs, shell-installer checksums.
- This repo consumes ruff as `ruff check` with `select = ["E9", "F63", "F7", "F82"]`
  (`ruff.toml`) — none of the changed rules intersect that set; no CLI-flag or
  exit-semantics change in either release. requires-python `>=3.7` ⊇ project 3.13.
- **Adaptation verdict (addy router)**: patch bump, no deprecations touch this repo —
  nothing to expand/migrate/contract, no shims. Two version-tracking call sites move
  with it: `tests/test_pins.py` `PINNED` map (its own failure message sanctions
  "regenerate the lock AND update this test") and the living `CONTRIBUTING.md`
  mention. Historical mentions stay untouched: the CHANGELOG `[0.6.0]` release
  entry, `docs/completion/*`, and archived `docs/reports/*` evidence.

Provenance (no registry/maintainer change, so the hard gate does not trigger;
corroborated anyway): tag `0.16.7` exists in `astral-sh/ruff` (`b5dba86`); GitHub
release `0.16.7` published 2026-09-10, not draft/prerelease; neither version yanked;
PyPI project unchanged. PEP 740 attestations: not advertised in the Simple API for
0.16.7 files (recorded as absent, not as failed). Integrity enforcement is the
regenerated-hash lock + `pip install --require-hashes` (replayed in the NC probe).

## 4. Advisory scan (two independent routes, 2026-09-16)

| Pinned version | OSV (`/v1/query`) | GitHub Advisory API (`/advisories?ecosystem&affects`) |
|---|---|---|
| ruff 0.16.5 | 0 | 0 |
| skills-ref 0.1.1 | 0 | 0 |
| click 8.5.0 | 0 | 0 |
| strictyaml 1.7.3 | 0 | 0 |
| python-dateutil 2.9.0.post0 | 0 | 0 |
| six 1.17.0 | 0 | 0 |
| actions/checkout 7.0.1 | N/A — see control note | 0 |
| actions/setup-python 7.0.0 | N/A — see control note | 0 |
| gitleaks v8.30.1 (Go module) | 0 | 0 |

Control note: OSV `"ecosystem": "GitHub Actions"` returned `{}` even for the
known-compromised `tj-actions/changed-files@45` — the ecosystem does not resolve
that way, so an OSV `{}` for actions pins is UNINFORMATIVE, not clean. Actions
advisories are covered by the GitHub route instead (0 affecting either pin; the
`actions` ecosystem itself resolves, 30 total advisories). No `audit fix --force`
anywhere; nothing to force.

## 5. Reachability triage

This repo ships no runtime application: product code is stdlib-only scripts plus
doctrine. Every third-party dep executes ONLY in CI (lint gate, skills validator,
checkout/setup, secret scan). Reachability verdict: **reachable-in-CI**
(supply-chain: a compromised release executes on every PR / push-to-main) —
genuine currency surface, ordered below any production-path advisory (of which
there are none: zero advisories on both routes).

## 6. Compatibility graph + ORDER

Nodes: exactly one outdated node — `ruff` (declares zero dependencies; shares the
generated lockfile with skills-ref's subtree, which resolves unchanged).

```
[ruff 0.16.5 → 0.16.7]   (sole node; lockfile regenerated by `uv pip compile`)
```

Order per SKILL (security-critical-reachable → patch/minor groups → majors):
no advisories → no security wave; ONE patch unit; zero majors. No chain (single
writer to the lockfile), no ecosystem grouping needed (the skills-ref subtree is
already current and must resolve byte-identical — AC-4 asserts it).

Units: **U1** `ci-tools: ruff 0.16.5 → 0.16.7 + lockfile regen`
(denominator frozen in `contract.json`).
