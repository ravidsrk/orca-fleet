# REFLECTION — modernize-it self-test campaign 2026-09-16 (proposal, human must approve each line)

## Surprises

- The catalog's own "no dependencies" row (runs README field-proof plan, 2026-09-02)
  went stale when #301 landed the hashed CI-tools lockfile (2026-09-11): a mission
  the catalog believed inapplicable self-ran to CURRENT. Doctrine about the absence
  of a surface rots the moment the surface appears.
- `verify.py` genuinely gates a solo lane: it REDded three times on real defects
  (missing fresh proof-command record #352; two unpinned-transcript admissions #267)
  before the executed control ever ran — and the admission gate is what forced the
  evidence into its final shape. The verifier earned its keep.
- The lockfile header's regen recipe (`uv pip compile … -o .github/ci-tools.lock`)
  read literally would delete the hand-written header (the generator emits no
  header). "Regenerate" here is rows-from-generator + header-preserved — a
  procedure the header implies but never states.
- `test_pins.py`'s failure message ("regenerate the lock AND update this test") is
  the call-site adaptation contract for this repo's smallest upgrade unit: the
  mission's "adapt call sites" step for a version bump is that one-line test edit
  plus the living CONTRIBUTING mention — found only by grepping every `0.16.5`.

## Proposed AGENTS.md / GOTCHAS appends (HUMAN MUST APPROVE EACH LINE)

- GOTCHAS: `docs/runs/README.md` field-proof "blocker" rows can go stale — the
  modernize-it row still says "this catalog has no dependencies" after #301 added
  a lockfile. Re-check a row's premise before citing it as a park reason.
- GOTCHAS: regenerating `.github/ci-tools.lock` = generator rows + preserved
  header (`uv pip compile` emits no header; `-o` onto the file would drop it).
- GOTCHAS: a `verify.py --execute-nc` transcript must never be the run's own
  `--artifact` target: the record names a file whose bytes don't exist until the
  run ends, which fails #267 admission and gates the NC legs. Redirect to an
  unnarrated path, pin prior transcripts first.
- STYLE: version bumps in this repo move three places — the lock, `PINNED` in
  `tests/test_pins.py`, the living `CONTRIBUTING.md` line — and never the
  CHANGELOG release entries or archived `docs/reports/*` evidence.
- TEST_STRATEGY: the `modernize-gates.sh` shape (validate.yml replicated locally:
  validate + scrubbed-PATH unittest + eval + proof + bundle + hashed venv install
  + skills-ref + gitleaks + ruff + vf-bench) is the reusable "CI green" oracle for
  dependency-currency work here; keep it next to the run, not in the repo.

## Prompt / playbook tweaks (fleet-side, optional)

- modernize-it SKILL or mission doc: one line on the solo-run evidence order that
  worked — fresh proof-command record via stash-aside, verifier transcript to an
  unnarrated path, pin-then-final-run — filed as backlog, not edited from here.
