# Installing orca-fleet

[Documentation](README.md) · [First run](getting-started.md) · [Troubleshooting](troubleshooting.md)

Install the catalog once, then invoke missions in the project you want worked on. The catalog
clone and that target project are separate directories. Running missions has additional
[prerequisites](getting-started.md#prerequisites); editing the catalog uses the
[local development setup](development.md#local-setup).

## Choose an install path

| Path | Use it when | Completion gate | Status |
|---|---|---|---|
| [Symlink](#symlink-the-catalog) | You want to evaluate or edit the catalog from a local clone | Merge the settings snippet yourself | Retained clean-install transcript |
| [Claude Code plugin](#claude-code-plugin) | You want the whole catalog managed as a plugin | Declared by the plugin's hooks | Whole-tree packaging; clean-machine witness still tracked |
| [Copy installer / bundle](#copy-installers-and-bundles) | An installer copies individual mission directories | Separate wiring required | Repo-root copy install unsupported; bundled-install witness still needed |

## Symlink the catalog

The installer validates the catalog, links every mission, and checks the gate
snippet is available (prerequisites: `git` + Python ≥ 3.11; the
[pinned table](distribution.md#prerequisites-pinned) names the run substrate too):

```bash
git clone https://github.com/ravidsrk/orca-fleet.git
cd orca-fleet
sh scripts/install.sh
sh scripts/install.sh --check
```

The final command rechecks the symlink install without changing it. Expect a line beginning
`verified` confirming links, skills and the protocol directories are in reach. It does not
confirm your completion-hook settings. The installer also warns (never fails) when `orca status` shows the app down,
unreachable, or unready — start Orca before running missions. The warn stays soft
because headless installs have no app to be ready; hardening it into a gate is a
parked policy decision, not a missing check.

To link only the missions you want by hand instead — link, don't copy. A mission
names its playbooks and runtime policies by bare name and finds them in
playbooks/ and runtime/ two levels above its own directory (and links
../../ARCHITECTURE.md); a symlink keeps that tree intact, a copy breaks it.

```bash
mkdir -p ~/.claude/skills
ln -s "$(pwd)/skills/ship-it"   ~/.claude/skills/ship-it
ln -s "$(pwd)/skills/review-it" ~/.claude/skills/review-it
```

Then wire the completion gate — a symlink install loads no plugin, so
hooks/hooks.json (which resolves through ${CLAUDE_PLUGIN_ROOT}) never fires.

```bash
sh hooks/print-settings-snippet.sh          # merge into ~/.claude/settings.json
sh hooks/print-settings-snippet.sh --check  # confirm the gate script resolves
```

Without that snippet this install has **no completion gate**: missions still run, but nothing
blocks a unit from being marked done on an unverified manifest. See
[docs/verify-gate.md](verify-gate.md#install-paths-and-which-ones-carry-the-gate).

Keep the clone at this path. Moving or deleting it breaks both the links and any hook command
that points to it. The installer replaces symlinks but refuses to overwrite real mission
directories; [troubleshooting](troubleshooting.md#installation-refuses-an-existing-mission-directory)
covers that case.

## Claude Code plugin

The repo ships a plugin manifest at [`.claude-plugin/plugin.json`](../.claude-plugin/plugin.json):

Run these inside a Claude Code session:

```text
/plugin marketplace add ravidsrk/orca-fleet
/plugin install orca-fleet@orca-fleet
```

A plugin install copies the whole repo, so the bare-name lookups and the `../../ARCHITECTURE.md`
link resolve inside the plugin directory — and it is the one path where the completion gate wires itself, because
`${CLAUDE_PLUGIN_ROOT}` resolves the plugin directory. Follow the install UI to choose a scope,
then check the reported activation status. Type `/` and look for skills such as
`/orca-fleet:review-it`. See the upstream [plugin installation guide](https://code.claude.com/docs/en/discover-plugins)
for host-specific scope and activation behavior.

The [plugin-install witness](completion/PLUGIN-INSTALL-WITNESS.md) distinguishes this packaging
mechanism from a retained clean-machine execution. Installing the plugin also does not supply
Orca or the other mission run prerequisites.

## Copy installers and bundles

The open [skills CLI](https://github.com/vercel-labs/skills) installs into Claude Code, Cursor,
Codex, and 70+ other agents — but **not from this repository, today.** `npx skills add
ravidsrk/orca-fleet` copies `dirname(SKILL.md)` and nothing else, so the `playbooks/` and `runtime/` directories a
mission resolves its bare names against are not there after the install. The mission then reads "Composes
`decide-and-freeze`, `decompose-dag`…" with no file for any of those names, and either invents the
protocol or stops. The command is not shown here as runnable because running it produces that.

What works today is the symlink path or the plugin install, both above. What makes the skills
CLI work is a published `dist/` for it to point at. Since #518 the `publish-dist` workflow
(`.github/workflows/publish-dist.yml`) builds that tree with `scripts/bundle.py` on every `v*` tag
and force-pushes it to the **`dist` branch** as one orphan commit per tag, with a
`DIST-PROVENANCE.txt` naming the tag and commit it was built from. The branch appears with the
first tag pushed after that workflow landed (0.7.0). Point a copy installer at the `dist` branch,
never at the repo root — and until an install from it has been witnessed and its transcript
recorded here, the skills CLI stays listed as unsupported
([#294](https://github.com/ravidsrk/orca-fleet/issues/294)).

**Copy installers need a bundled tree.** Every mission resolves its playbooks and runtime
policies two levels above its own directory. An installer that copies skill directories *out* of
the repo tree severs that resolution — one mission or the whole catalog. Build self-contained
missions first:

```bash
python3 scripts/bundle.py           # writes dist/skills/<name>/ with references/ vendored
python3 scripts/bundle.py --check   # verify no reference escapes a mission directory
```

Each bundled mission carries its own `references/` copies of every protocol it names plus the root
docs it links, with its SKILL.md links rewritten to point there and an index at
`references/README.md`. A copy installer must take `dist/`, never the repo root — and no installer
can be pointed at a local `dist/` over the network, which is why the tree is published to the
`dist` branch above rather than left on a laptop. In the repository, `dist/` is generated and
gitignored: committing a copy of the doctrine tree per mission would make every runtime edit a many-file diff
and the copies would rot between edits.

The installed layout depends on the packaging:

- **Source symlink or whole-tree plugin:** the mission resolves `playbooks/` and `runtime/`
  two levels above its real directory.
- **Bundled copy:** the mission carries `references/README.md`, the composed Markdown files,
  and its own `runtime/scripts/`. Follow that generated README to set `ORCA_FLEET_ROOT` and
  invoke the helpers from the target project.

For a source symlink, check the resolved tree from the shell:

```bash
shipit=$(python3 -c 'import os; print(os.path.realpath(os.path.expanduser("~/.claude/skills/ship-it")))')
ls "$(dirname "$(dirname "$shipit")")/playbooks"
```

(`readlink -f` is GNU-only; on stock macOS it fails and a naive fallback tests the wrong directory —
reporting a correct install as broken. `os.path.realpath` is the portable resolver, and python3 is
already a hard requirement of this repo.)

For a bundled copy, inspect the installed mission's `references/README.md` and
`runtime/scripts/verify.py` instead. A directory containing only `SKILL.md` is not a complete
bundle. If the matching layout check fails, reinstall from the symlink or plugin path above,
or from a bundled tree whose install has been verified. The
symlink path is verified to preserve them
([`docs/completion/evidence/CF-02-r2-happy-symlink-install.txt`](completion/evidence/CF-02-r2-happy-symlink-install.txt));
the plugin path preserves them by construction — the whole repo is copied — but has no recorded
install transcript yet. The procedure that produces one, for anyone with a clean machine, is
[the plugin-install witness](completion/PLUGIN-INSTALL-WITNESS.md); its transcript is one of three
parts of #518, beside the first `v*` tag populating the `dist` branch and the receipt trees under
`docs/runs/` and `docs/reports/` shrunk or relocated out of the plugin copy.

## Check the install

Ask your agent "which missions are available?" — the outcome-named skills should list; with the
two symlinks above you get `ship-it` and `review-it`. If a mission is visible but stops on start
saying it cannot find a playbook, it was copied rather than linked.

## Verify the completion gate

For a symlink install, merge the snippet's `Stop` and `TaskCompleted` entries into your existing
settings; preserve other hooks. `print-settings-snippet.sh --check` only checks the clone's files.
Review the registered paths and exercise the gate itself from the catalog root:

```bash
ORCA_MANIFEST=/nonexistent.json sh runtime/scripts/verify-gate.sh --event stop
```

Expected: `BLOCKING (fail-closed)` and exit status 2, because the named manifest is missing.
This tests the gate's failure path; it does not prove an agent event called that gate. Check
the agent's hook registration as well. The [gate reference](verify-gate.md) explains event
behavior and the native advisory trust boundary.

## Update or remove an install

**Symlink install:** update the clone with `git pull --ff-only` once its working tree is clean,
then run `sh scripts/install.sh --check`. If the catalog gained missions, rerun
`sh scripts/install.sh` to link them too. Local edits should be reviewed and committed on their
own branch before you update; use [Development](development.md) for that workflow.

To remove a selected mission, first inspect its symlink target, then unlink only that entry in
`~/.claude/skills/`. For example, after confirming it points to this clone:

```bash
unlink ~/.claude/skills/review-it
```

When removing the catalog entirely, also remove the two completion-hook entries that point to
this clone, preserving unrelated settings. Keeping them after deleting the clone leaves hook
commands that cannot resolve.

**Plugin install:** manage updates and removal through Claude Code's plugin manager; consult
the [upstream instructions](https://code.claude.com/docs/en/discover-plugins#manage-installed-plugins).

Next: [run your first review](getting-started.md#your-first-mission-a-review-it-dry-run), or use
[a developer recipe](recipes.md) for your task.
