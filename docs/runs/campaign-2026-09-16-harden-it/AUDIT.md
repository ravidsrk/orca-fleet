# AUDIT — harden-it self-run against orca-fleet @ c46d4b3 (2026-09-16)

Fixed point: `c46d4b3f3371e41408aed19e54476fa194c20b42` (origin/main tip).
Lens: risk-review security, TREE-WIDE (scope-gating bypassed per harden-it pipeline).
Triage mode: Gated. Worker pack: addy. Verifier status for every candidate below:
**self-verified — no independent verifier** (LEDGER D3).

## Wave A — secrets at rest (B1/B5)

- `gitleaks detect` (repo config, git mode, 994 commits): **no leaks found**.
- `--no-git` capture (`receipts/gitleaks-audit.txt`, `--redact`) shows the 3 known
  `tests/test_decisions.py` fixtures (`AKIA...EXAMPLE`, `api_key=...`), waived by
  fingerprint in `.gitleaksignore` with a documented plant-a-key CI tripwire
  (validate.yml). → Candidate C2, REFUTED (fixture-only, AWS-documented example
  key shape, excluded per triage-findings §2; configured scan clean).
- `.env.example` carries no values. `decisions.py` SECRET_SHAPES + `verify.py`
  check_redaction scan committed evidence (traced, both fail closed).

## Wave B — CI / supply chain (B5/B4/B1)

- All 5 workflows: third-party actions SHA-pinned (checkout v7.0.1, setup-python
  v7.0.0). No `pull_request_target`, no `workflow_call`. Permissions minimal
  (`contents: read`; alert job adds `issues: write` with a same-repo + push-event
  guard against fork issue-spam).
- `alert-on-failure.yml`: untrusted workflow_run fields enter via `env:` (safe
  pattern), consumed quoted; only `run:` interpolations are step outputs
  constrained to digits (`grep -oE '[0-9]+$'`, jq `.number`) or 3 literal action
  strings. → Reviewed clean (C4).
- `bind-check.yml:27`: `run: python3 scripts/bind_check.py --base
  origin/${{ github.base_ref }}` — expression interpolation into `run:` (known
  script-injection pattern). Traced: for `pull_request` events the base must be an
  EXISTING branch of the base repo, so weaponizing it needs push access to create
  an evil-named branch — an actor who already has code execution via push.
  No concrete untrusted-input path → BELOW the gated bar (C1). Hardening note
  (not a finding, no fix): pass the base through `env:` like alert-on-failure.yml.
- `scripts/install.sh`: no network, no curl-pipe, `set -eu`, quoted throughout,
  validates the catalog before linking, refuses non-symlink conflicts, verifies
  resolution post-link. No commit pin / signature check on the clone — exploiting
  it needs control of github.com/the repo itself → below bar (C5).
- Zero third-party runtime deps (no requirements/package.json; `test_repo_hygiene`
  enforces stdlib-only). Upstream pins in `runtime/pins.json`, owned by pin-it /
  upstream-audit cadence (out of scope per threat model, verified present).

## Wave C — shell / command injection (B2)

- Sweep of all `runtime/scripts/*.py` + `scripts/*.py`: **no `shell=True`,
  `os.system`, `os.popen`, `eval`, `exec`, `pickle`, `yaml.load`** (only string
  literals in diff_scope's classifier patterns and a verify.py docstring).
  All 30+ subprocess call sites pass argv lists; verified individually.
- Shell (`spawn_worker.sh`, `verify-gate.sh`, `wtree.sh`, `deny-hook.sh`,
  `hitl-loop.template.sh`, `install.sh`, `print-settings-snippet.sh`): no `eval`
  execution; heredoc python via quoted delimiters with argv-passed values;
  validated enums (agent/profile/effort/recipe id) before interpolation.
- `verify.py` NC execution: shlex-split, coordinator `--nc-command` REQUIRED
  (#279), argv-only `_run_at`, throwaway worktrees with cleanup, fail-closed on
  every git error. `evidence-run.py` runs caller argv by design (transparent
  wrapper), no shell. `guard_text.py --fetch` argv-only.
- `preflight.py`/`inventory.py`/`run_report.py` build `git` argv from report/CLI
  input (`{rev}:{path}`); worst case is a git error → fail-closed (read-only
  verbs only). `verify.py read_source` additionally refuses leading-`-` refs.
- `watchdog.py build_nudge_argv` substitutes ids into a coordinator-owned command
  template as argv elements (no shell) — safe.
- `eval.py` fixture writes bounded by `_fixture_path` (absolute refused, escape
  refused); agent commands from operator env via shlex.
- → Zero candidates. Class swept: every sink enumerated, not sampled.

## Wave D — trust boundary / prompt injection (B3/B1)

- `guard_text.py` (the fence): envelop-always, failed-is-not-data, NFKC+Cf-strip
  detection, forged-banner defusing, label sanitization, argv fetch. Traced clean.
- Raw `gh issue view` outside the fence: none in skills/playbooks/runtime
  (contract test owns this; suite green — see Gates). `gh pr view`/`gh api`
  mentions are structured `--json` field lookups, not free-text ingestion.
- `pm.py` escapes C0/C1 + Cf/Zl/Zp in worker-controlled text (terminal-injection
  sink covered).
- Doctrine sweep of all SKILL/playbook/runtime docs for disable-the-gate
  instructions (`skip verif*`, `bypass review`, bare `--force`, `curl|sh`): only
  hits are prohibitions (anti-pattern lists) or `--force-with-lease` procedure.
- B1 (instructions-as-code): integrity rests on review + branch protection, same
  as any code; no embedded live secrets, no auto-executed payloads (hooks fire
  only when the host registers them; `deny-hook.sh --settings` is explicit).
- → Zero candidates.

## Wave E — crypto / dispatch provenance (B6)

- `ed25519.py`: vendored RFC 8032 reference + documented hardening (S<L,
  canonical-point, small-order-key rejection); RFC test vectors in
  `tests/test_ed25519.py` (suite green). Non-constant-time + non-cofactored
  equation are documented, threat-model-bounded gaps (offline signing of tiny
  provenance records) — not findings.
- `dispatch-sign.py`/`verify.py check_dispatch_provenance`: canonical bytes match
  (cross-tool test), 0600 seed at creation, gen-key refuses unignored in-repo
  paths, replay bound to manifest id, unsigned-field use fail-closed. Traced clean.
- `verify-gate.sh`: in-session lane explicitly ADVISORY, soundness off-worker
  only; env→argv building quoted; fail-closed (exit 2) on missing manifest and
  verifier failure. The one behavioral note: `Stop` with no unit in progress
  allows (documented: nothing to verify) — by design, not a bypass.
- → Zero candidates.

## Wave F — destructive paths / sandbox boundary (B2/B4)

- `deny-hook.sh` HIGH tier + worktree boundary: read in full (1021 lines), then
  probed with 27 adversarial payloads (Bash HIGH shapes, evasive variants,
  boundary writes). All refused shapes denied (incl. `X="a;b" git push --force`,
  compound `; rm -rf /`, `rm "-rf" /`, `-C`/GIT_DIR redirects, `:refs/heads/main`
  deletes, `sudo -n` laundering, `sudo tee` escapes); in-boundary writes allowed;
  malformed JSON and unresolvable boundary fail closed. One precision note (not a
  bypass): `git push --force origin refs/heads/main` denies with the generic
  unleased-force message rather than the default-branch message — same verdict.
  Probe list: `receipts/deny-hook-probes.txt`.
- `wtree.sh`: mktemp + trap cleanup, temp index only, fail-closed outside git.
- No `pull_request_target` checkout of untrusted refs; no DB/cloud teardown code
  in repo (risk-review destructive-target rules have no in-repo subject).
- → Zero candidates.

## Wave G — OWASP LLM Top 10 / privacy / misc

- LLM01 prompt injection: fenced (Wave D). LLM02 insecure output handling: scripts
  emit JSON via serializers, never interpolation (`deny-hook.sh decide()`,
  `--settings` use json.dumps). LLM03 training-data poisoning: N/A (no training).
  LLM04 model DoS: timeouts on all subprocess/gh calls; bounded HITL rounds.
  LLM05 supply chain: Wave B. LLM06 sensitive-info disclosure: Wave A + redaction
  gates. LLM07 insecure plugin design: hooks advisory-in-session, sound off-worker
  (documented). LLM08 excessive agency: Always/Ask-First/Never + one-way gates +
  deny-hook; danger lane unconditionally refused without placement binding
  (`spawn_worker.sh:312`). LLM09 overreliance: evidence-manifest (no trace
  grading). LLM10 unbounded consumption: WIP caps + timeouts + round budgets.
- Privacy lens: no personal-data collection, no telemetry, no logs of user data
  in repo. Rate limiting: N/A (no service). Memory safety: N/A (Python/sh).
- → Zero candidates.

## PoC scenarios (written, NOT executed — there is nothing to prove)

No P0/P1 surfaced, so no exploit PoC is owed. The two below-bar observations have
no executable PoC by construction:

- C1 (base_ref interpolation): exploitation requires pushing a branch named e.g.
  `x";curl evil#` to THIS repo — i.e. the attacker's PoC step 1 is "already have
  push access". Written scenario only; executing it would mean attacking the repo
  itself with credentials no worker holds. NOT executed (Never bucket).
- C5 (unpinned install): exploitation requires control of github.com or the repo.
  No sandbox could make that PoC safe or meaningful. NOT executed.

## PoC ROUTING

No PoC qualifies for execution: the only scenarios are C1/C5 (above), both
routed as **Never — no execution**, with reasoning recorded. No static, rw, or
sandbox PoC was required. No `danger` spawn (unconditionally refused by
`spawn_worker.sh` without placement binding in any case).

## Verification dispositions (triage-findings §4–§5)

| id | candidate | disposition | reason |
|----|-----------|-------------|--------|
| C1 | base_ref interpolation | BELOW BAR (not a finding) | needs push access; no untrusted-input path |
| C2 | gitleaks --no-git hits | REFUTED | EXAMPLE fixtures, waived; git-mode scan clean |
| C3 | .env.example NC fallback comment | BELOW BAR (not a finding) | stale doc, fail-safe direction (gate is stricter) |
| C4 | alert step-output interpolation | REVIEWED CLEAN | digits/literal-constrained, env-indirect rest |
| C5 | unpinned install | BELOW BAR (not a finding) | needs repo-host compromise; no concrete path |

Every disposition above carries the §5 degradation: self-verified, no
independent verifier. No VERIFIED P0/P1. No fix, no re-attack owed.

## Variant analysis (per reported item — none VERIFIED)

Class sweeps performed instead (a VERIFIED finding's variant grep generalizes to
the whole tree when the class is clean): every subprocess call site (C-wave),
every workflow interpolation (B-wave), every sink in the NC/dispatch path
(E-wave), every HIGH-tier shape by probe (F-wave). One confirmed instance with no
variant search would be incomplete; here there are zero instances and the class
searches are recorded above.
