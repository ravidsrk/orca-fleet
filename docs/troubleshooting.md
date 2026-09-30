# Troubleshooting

[Documentation](README.md) · [Install](install.md) · [Development](development.md)

Start with the symptom below. Run catalog scripts from your **orca-fleet clone**; run project
tests from the **target repository**. Agent prompts and `/plugin` commands go into the coding
agent, rather than your shell.

## The catalog installs, but a mission cannot start

Installation and live execution have different prerequisites. The installer needs Git and
Python 3.11 or newer; it warns about missing or unready run tools. A successful install with
warnings is not a successful runtime check.

From a shell, check:

```bash
python3 --version
git --version
gh auth status
orca status --json
```

On Linux outside an Orca terminal, use `orca-ide` where these examples say `orca`.
If the app is stopped, start it with `orca open` and check status again. The app must be running,
and its runtime reachable and `ready`. The catalog's minimum witnessed version lives in
[`runtime/pins.json`](../runtime/pins.json); [the prerequisites table](distribution.md#prerequisites-pinned)
explains which checks are hard requirements and which are warnings.

Local docs editing and catalog tests have their own [setup](development.md#local-setup).

## The mission is missing from the agent

For a symlink install, run `sh scripts/install.sh --check` from the clone. It verifies every
mission link points into that clone and that playbooks and runtime policies are reachable.
For a deliberately selected subset, inspect the particular link instead:

```bash
python3 - <<'PY'
from pathlib import Path
mission = Path.home() / '.claude/skills/review-it'
print('symlink:', mission.is_symlink())
print('target:', mission.resolve())
print('skill exists:', (mission / 'SKILL.md').is_file())
PY
```

For a plugin install, inspect the agent's installed-plugin list and its reported load errors.
Follow [plugin setup](install.md#claude-code-plugin) to confirm activation and the skill namespace.

## Playbooks or architecture links cannot be found

A source mission needs the rest of the catalog tree. Copying only `skills/<mission>/` removes
the files its bare-name references resolve to. Reinstall using the
[symlink or plugin path](install.md#choose-an-install-path). A copy installer needs the
self-contained output of `scripts/bundle.py`, with `references/` inside each mission;
[bundle packaging](install.md#copy-installers-and-bundles) explains the current support status.

## Installation refuses an existing mission directory

`scripts/install.sh` refuses a destination that is a real directory instead of a symlink.
Inspect that directory and preserve any local edits before moving it out of the way. Then rerun
the installer. It can also install into a separate skills directory with
`--skills-dir=/absolute/path`; supply the same directory when using `--check`.

## The settings snippet says “ok”, but completion is not checked

`sh hooks/print-settings-snippet.sh --check` checks files in the clone. It does not read your
Claude Code settings or prove the hook is active. Merge the printed entries into the existing
settings, preserving other hooks, and confirm both `Stop` and `TaskCompleted` point to the clone.
The [install guide](install.md#verify-the-completion-gate) includes the missing-manifest check.

## The gate blocks a turn or task

Read the gate's failure output. A task needs a manifest and the coordinator's contract source
and digest. A named manifest that is missing, invalid or fails a required check blocks completion.
The `Stop` event permits a turn with no unit in progress; `TaskCompleted` requires a manifest.
Use the [gate reference](verify-gate.md#native-path--plugin-hooks-set-claude_plugin_root) to
diagnose the failing input. The gate's native execution is advisory; its
[trust boundary](verify-gate.md#trust-boundary) still applies.

## Preflight refuses BASE

Mutation missions use an integration branch distinct from the default branch. Supply or let
the coordinator create that branch from the intended fork point. Check which repository and
branch your agent opened before retrying. A read-only review uses its read-only preflight;
it does not need a new mutation BASE.

## The baseline suite is already failing

Run the project's failing command outside the fleet and retain its output. A deterministic
failure is a defect to fix; intermittent suite failures fit [deflake-it](missions/deflake-it.md).
A first feature run needs a baseline it can distinguish from its own regressions.

For this catalog's suite, missing historical commits or tags usually indicate an incomplete
clone. A fixture sender-identity error in an agent terminal may need
`env -u ORCA_TERMINAL_HANDLE` for the test process. See [development checks](development.md#everyday-checks).

## A worker appears idle or the coordinator restarts

Use the run's ledger and scoped runtime state to identify its task and dispatch before taking
action. An idle terminal alone does not establish failure. The policies for
[worker supervision](../runtime/worker-supervision.md) and
[resume](../runtime/liveness-resume.md) define recovery, bounded retries and re-verification.
Keep the ledger and evidence available to the resumed coordinator.

## Tests passed, but a PR is still blocked

Inspect the PR's current head, required checks, review state and conversations:

```bash
gh pr view 123 --repo owner/repo --json headRefOid,baseRefName,mergeStateStatus,reviews
gh pr checks 123 --repo owner/repo --required
```

Replace `123` and `owner/repo`. A local test pass does not establish a fresh review or satisfy
every branch protection rule. A content-changing rebase or late push needs a fresh review;
see [reviewed-SHA freshness](../runtime/reviewed-sha-freshness.md).

## Report a problem with enough context to reproduce it

Include the catalog commit/version, agent and Python versions, install path, operating system,
mission, exact command or prompt, expected result and actual failure output. For a stopped run,
include its task/dispatch identifiers and the relevant ledger row. Remove credentials and private
project data from a public report.

Use the [bug template](../.github/ISSUE_TEMPLATE/bug_report.md) for behavior and the
[doc-claim template](../.github/ISSUE_TEMPLATE/doc_claim.md) for inaccurate documentation.
Send security reports through the private route in [SECURITY.md](../SECURITY.md).
