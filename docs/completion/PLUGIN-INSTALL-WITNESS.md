# Plugin-install witness — the procedure

The [install transcript](evidence/CF-02b-plugin-install.txt) and
[uninstall control](evidence/CF-02b-plugin-uninstall.txt) record a clean Ubuntu 24.04.4
container with Claude Code 2.1.285, bound to the `v0.7.0` cut. This is a packaging and
registration witness: all 22 missions are discovered, the two hook events are present, the
copied source files match, and uninstall removes the mission registrations. It is not an
Orca mission run or proof that a real agent event invoked the completion gate.

Use this procedure to repeat it. Record commands, output and exit codes; finish with a
`result:` stating exactly what was observed. Retain failures too. Do not edit the frozen
[DEFINITION](DEFINITION.md) to record a later witness.

## Who and where

Use a fresh VM, user account or container that has no catalog install. Install Claude Code
from its official source, plus Git and Python 3.11 or newer. Record whether Orca is present;
it is not required for these install checks. An authenticated Claude account is needed for
model responses, but native plugin management and component inventory do not require one.

Before installing, retain:

```bash
date -u +%Y-%m-%dT%H:%M:%SZ
uname -a
claude --version
python3 --version
ls -la ~/.claude/skills
ls -la ~/.claude/plugins
```

Missing directories are expected on a clean account: record their nonzero exits. A prior
orca-fleet plugin or symlink means this is not a clean first install.

## Install and inspect the host's inventory

Run the native CLI, or the equivalent `/plugin` commands in a Claude session:

```bash
claude plugin marketplace add ravidsrk/orca-fleet
claude plugin install orca-fleet@orca-fleet
claude plugin list --json
claude plugin details orca-fleet@orca-fleet
```

Retain install output, version, scope, enabled status and `installPath`. In 2.1.285, `details`
prints a component inventory with 22 skills and `TaskCompleted`/`Stop` hooks; it does not
accept `--json`. This inventory is a host observation, rather than a model's description
of files. In a session, `/hooks` can additionally show the registered commands.

Find the one installed manifest under the cache, not the marketplace's source checkout:

```bash
find ~/.claude/plugins/cache -name plugin.json -path '*orca-fleet*'
```

Require exactly one matching installed manifest. Set `PLUGIN_ROOT` to its grandparent only
after confirming its `.claude-plugin/plugin.json` names `orca-fleet`. Record:

```bash
du -sh "$PLUGIN_ROOT"
python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["version"])' "$PLUGIN_ROOT/.claude-plugin/plugin.json"
ls "$PLUGIN_ROOT/playbooks" | head -5
ls "$PLUGIN_ROOT/runtime" | head -5
head -4 "$PLUGIN_ROOT/skills/ship-it/SKILL.md"
grep -n 'CLAUDE_PLUGIN_ROOT' "$PLUGIN_ROOT/hooks/hooks.json"
test -x "$PLUGIN_ROOT/runtime/scripts/verify-gate.sh"
```

The hooks must name the executable gate through `${CLAUDE_PLUGIN_ROOT}` on both events.
Inventory plus path checks establish discovery and wiring; do not describe them as an
observed event invoking the gate.

## Bind the copy to source and validate the source

A version string is not a commit identity. First record the marketplace checkout's HEAD:

```bash
git -C ~/.claude/plugins/marketplaces/orca-fleet rev-parse HEAD
```

If that layout differs, find the marketplace checkout through the plugin manager and
record its actual path. Call the observed commit `INSTALL_COMMIT`. Clone full history into
a separate scratch directory and check out that commit:

```bash
INSTALL_COMMIT="$(git -C ~/.claude/plugins/marketplaces/orca-fleet rev-parse HEAD)"
SOURCE_ROOT="$(mktemp -d)/source"
git clone https://github.com/ravidsrk/orca-fleet.git "$SOURCE_ROOT"
git -C "$SOURCE_ROOT" checkout --detach "$INSTALL_COMMIT"
cd "$SOURCE_ROOT"
python3 scripts/validate.py
```

**Run the validator in the full-history source checkout, not in the plugin cache.** Claude
copies files into its cache and shallow-clones marketplaces. The validator checks bound
proof reports against historical Git objects; a cache or shallow checkout cannot provide
those objects. The retained transcript shows that failure and the successful full-history
check. Do not disable the proof checker or downgrade metadata to make a cache pass.

Fingerprint every tracked source path in both trees. The retained transcript includes the
complete Python fingerprint command: sorted paths, a NUL separator and each file's SHA256,
then SHA256 of that inventory. Require identical fingerprints and list any untracked files
separately; host bookkeeping or Python bytecode is not part of the source inventory.
Missing or changed source paths fail the copy check. Combined with the source validator,
this proves the copied mission/protocol files resolve to the validated tree.

If witnessing an immutable release, also require `INSTALL_COMMIT` to equal that tag's
peeled commit. A marketplace install normally follows its tracked branch, so a later install
may contain post-release commits while showing the same version: name the observed commit,
not a tag it does not match. A size reduction requires two measurements, each bound to its
own source commit. One `du` output is only a footprint.

## Session discovery and negative control

For session-level evidence, retain Claude's initialization inventory as well as its response:

```bash
claude -p --verbose --output-format stream-json --include-hook-events 'which missions are available?'
```

The `system/init` event lists loaded skills and plugins. An unauthenticated session may
emit that event, then fail with `authentication_failed`: record exit 1 and do not claim a
model response. Our witness compares these actual initialization events before and after
uninstall. Optional authenticated prompts can ask the agent to read map-it's composed
playbooks and quote their first headings; retain the file paths it actually read.

Exercise the gate's missing-manifest control and require exit 2:

```bash
ORCA_MANIFEST=/nonexistent.json "$PLUGIN_ROOT/runtime/scripts/verify-gate.sh" --event stop
```

Then uninstall through the native plugin manager:

```bash
claude plugin uninstall orca-fleet@orca-fleet
claude plugin list --json
claude -p --verbose --output-format stream-json --include-hook-events 'which missions are available?'
```

The installed plugin must be absent and the next initialization must contain no
`orca-fleet:` skills. Keep the control separate from the install transcript. Reinstall only
if you intend to retain the catalog.

## Landing the witness

Add the transcript and control under `docs/completion/evidence/`, link them from
[install.md](../install.md), and add an H-row to [HUMAN_ACTIONS](HUMAN_ACTIONS.md) with the
observed limits. Reference #518. Its other acceptance checks are the published `dist`
target and an explicit receipt-packaging decision; [install.md](../install.md#copy-installers-and-bundles)
records both. No install witness changes mission proof tiers or substitutes for the Linux
Orca-runtime run required by #527.
