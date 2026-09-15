# Installing orca-fleet

Two install paths work today and a third does not yet. Which one you pick decides whether the
[completion gate](verify-gate.md) fires by itself: a symlink loads no plugin, so the gate must be
wired by hand; the plugin install wires it by construction. The
[prerequisites](getting-started.md#prerequisites) are the same for every path.

<details>
<summary><b>Symlink individual missions (recommended for trying it out)</b></summary>

```bash
git clone https://github.com/ravidsrk/orca-fleet.git
cd orca-fleet

# Link the missions you want — link, don't copy. A mission names its playbooks and
# runtime policies by bare name and finds them in playbooks/ and runtime/ two levels
# above its own directory (and links ../../ARCHITECTURE.md); a symlink keeps that
# tree intact, a copy breaks it.
mkdir -p ~/.claude/skills
ln -s "$(pwd)/skills/ship-it"     ~/.claude/skills/ship-it
ln -s "$(pwd)/skills/clean-sweep" ~/.claude/skills/clean-sweep

# Then wire the completion gate — a symlink install loads no plugin, so
# hooks/hooks.json (which resolves through ${CLAUDE_PLUGIN_ROOT}) never fires.
sh hooks/print-settings-snippet.sh          # merge into ~/.claude/settings.json
sh hooks/print-settings-snippet.sh --check  # confirm the gate script resolves
```

Without that snippet this install has **no completion gate**: missions still run, but nothing
blocks a unit from being marked done on an unverified manifest. See
[docs/verify-gate.md](verify-gate.md#install-paths-and-which-ones-carry-the-gate).

</details>

<details>
<summary><b>Claude Code plugin (whole catalog)</b></summary>

The repo ships a plugin manifest at [`.claude-plugin/plugin.json`](../.claude-plugin/plugin.json):

```
/plugin marketplace add ravidsrk/orca-fleet
/plugin install orca-fleet
```

A plugin install copies the whole repo, so the bare-name lookups and the `../../ARCHITECTURE.md`
link resolve inside the plugin directory — and it is the one path where the completion gate wires itself, because
`${CLAUDE_PLUGIN_ROOT}` is set. Nothing else to configure.

</details>

<details>
<summary><b>skills CLI (any agent) — with a caveat</b></summary>

The open [skills CLI](https://github.com/vercel-labs/skills) installs into Claude Code, Cursor,
Codex, and 70+ other agents — but **not from this repository, today.** `npx skills add
ravidsrk/orca-fleet` copies `dirname(SKILL.md)` and nothing else, so the `playbooks/` and `runtime/` directories a
mission resolves its bare names against are not there after the install. The mission then reads "Composes
`decide-and-freeze`, `decompose-dag`…" with no file for any of those names, and either invents the
protocol or stops. The command is not shown here as runnable because running it produces that.

What works today is the symlink path or the plugin install, both above. What would make the skills
CLI work is a published `dist/` for it to point at — a release branch or a second repository — which
is [#294](https://github.com/ravidsrk/orca-fleet/issues/294); the bundler that produces that tree
already exists and is CI-checked.

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
can be pointed at a local `dist/` over the network, which is why the CLI path waits on publishing
one. `dist/` is generated and
gitignored: committing a copy of the doctrine tree per mission would make every runtime edit a many-file diff
and the copies would rot between edits.

To check an existing copy install instead, confirm `playbooks/` and `runtime/` sit two levels above
the mission:

```bash
shipit=$(python3 -c 'import os; print(os.path.realpath(os.path.expanduser("~/.claude/skills/ship-it")))')
ls "$(dirname "$(dirname "$shipit")")/playbooks"
```

(`readlink -f` is GNU-only; on stock macOS it fails and a naive fallback tests the wrong directory —
reporting a correct install as broken. `os.path.realpath` is the portable resolver, and python3 is
already a hard requirement of this repo.)

If that fails, the references are broken — bundle, or use the symlink or plugin path above. The
symlink path is verified to preserve them
([`docs/completion/evidence/CF-02-r2-happy-symlink-install.txt`](completion/evidence/CF-02-r2-happy-symlink-install.txt));
the plugin path preserves them by construction — the whole repo is copied — but has no recorded
install transcript yet.

</details>

## Check the install

Ask your agent "which missions are available?" — the outcome-named skills should list; with the
two symlinks above you get `ship-it` and `review-it`. If a mission is visible but stops on start
saying it cannot find a playbook, it was copied rather than linked.
