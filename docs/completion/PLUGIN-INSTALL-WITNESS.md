# Plugin-install witness — the procedure

The Claude Code plugin is the one install path that wires the completion gate by construction
(`hooks/hooks.json` resolves through `${CLAUDE_PLUGIN_ROOT}`, which Claude Code sets only for
plugin installs), and it has never been witnessed: [install.md](../install.md) says so, and the
2026-09-28 review filed the gap as [#518](https://github.com/ravidsrk/orca-fleet/issues/518).
This page is the procedure a second person runs on a clean machine to produce the transcript
that closes it. It mirrors the symlink witness,
[`evidence/CF-02-r2-happy-symlink-install.txt`](evidence/CF-02-r2-happy-symlink-install.txt):
commands as typed, output as printed, exit codes, one `result:` line, nothing narrated.

## Who and where

- Anyone but the maintainer's daily machine: a VM, a fresh user account, or a container with
  Claude Code installed. The point is a machine that has never held this repository.
- Claude Code at a recorded version; `git`; Python 3.11 or newer for the gate check. The Orca
  app is not needed for the install witness (the gate wiring is static), but record whether it
  is present so the transcript says which claims it can carry.
- Time: about twenty minutes, plus the plugin download.

## Preconditions to record

Before the first install command, prove the machine is clean and say what it is:

```bash
date -u +%Y-%m-%dT%H:%M:%SZ
uname -a
claude --version
python3 --version
ls -la ~/.claude/skills 2>/dev/null || echo "no ~/.claude/skills"
ls ~/.claude/plugins 2>/dev/null || echo "no ~/.claude/plugins"
```

Every line goes into the transcript with its exit code. A machine that already has an
`orca-fleet` symlink or plugin is not clean; remove it and start again, and say so.

## Steps

Each step is one command (or one Claude Code slash command), its output, and `exit=N`. Where
the output is long, keep the first and last ten lines and say how many were cut.

1. **Add the marketplace and install.** In a Claude Code session:

   ```
   /plugin marketplace add ravidsrk/orca-fleet
   /plugin install orca-fleet
   ```

   Capture both outputs verbatim, including any prompt Claude Code shows and what you answered.

2. **Find the plugin root and record what was copied.** The review measured the copy at
   tens of megabytes because the receipt trees under `docs/` ride along; record the size so the
   number stops being hearsay.

   ```bash
   find ~/.claude/plugins -maxdepth 4 -name plugin.json -path '*orca-fleet*'
   ROOT="$(dirname "$(dirname "$(find ~/.claude/plugins -maxdepth 4 -name plugin.json -path '*orca-fleet*' | head -n 1)")")"
   echo "$ROOT"
   du -sh "$ROOT"
   python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["version"])' "$ROOT/.claude-plugin/plugin.json"
   ```

   The version printed must equal the version of the tag you meant to install. If the plugin
   was installed from the default branch tip rather than a tag, say which commit:
   `git -C "$ROOT" rev-parse HEAD` when the copy is a checkout, otherwise the version alone.

3. **Verify the three layers resolve inside the copy** (the symlink witness's own check, run
   against the plugin root instead):

   ```bash
   ls "$ROOT/playbooks" | head -5
   ls "$ROOT/runtime" | head -5
   head -4 "$ROOT/skills/ship-it/SKILL.md"
   ```

4. **Verify the gate is wired, not merely present.** The hook file must name the gate script
   through the variable Claude Code sets for plugins, and the script must be there and
   executable:

   ```bash
   grep -n 'CLAUDE_PLUGIN_ROOT' "$ROOT/hooks/hooks.json"
   test -x "$ROOT/runtime/scripts/verify-gate.sh" && echo "gate script executable"
   ```

   Then, in the Claude Code session, run `/hooks` (or the equivalent that lists registered
   hooks in your version) and capture the lines that name `verify-gate.sh` on the `Stop` and
   `TaskCompleted` events. This is the claim install.md makes and nothing else has ever shown.

5. **Verify the missions load.** In the session, ask exactly:

   ```
   which missions are available?
   ```

   Capture the answer. The outcome-named missions must list. Then start one mission that stops
   at its first human gate without touching a repository, for example `review-it` on a pull
   request the session did not author, and capture its first response: it must read its
   playbooks by bare name from inside the plugin directory, not report a missing file.

6. **Negative control: uninstall and confirm the missions came from the plugin.** The repo's
   habit is a paired failure transcript; here it proves the skills were not a stray symlink.

   ```
   /plugin uninstall orca-fleet
   ```

   Then ask "which missions are available?" again and capture the answer: the outcome-named
   missions must be gone. Reinstall afterwards only if you intend to keep using the catalog.

## The transcript file

- Path: `docs/completion/evidence/CF-02-r3-happy-plugin-install.txt`, and the control as
  `docs/completion/evidence/CF-02-r3-failure-plugin-uninstall.txt`.
- First line: the UTC timestamp, then `CF-02 plugin install on a clean machine (README Install
  → "Claude Code plugin"), HOME=<what it was>`, as the symlink witness does.
- Body: `$ command`, the output, `exit=N`, in the order run. Slash commands go in as
  `> /plugin install orca-fleet` with their output beneath.
- Last line: `result: <one sentence stating what the transcript shows>`. The sentence for a
  passing witness is: "plugin install copies the catalog, its `../../playbooks` and
  `../../runtime` references resolve inside the plugin root, and the completion gate is
  registered on Stop and TaskCompleted through `${CLAUDE_PLUGIN_ROOT}`."
- Redact nothing but tokens; a path that names your user is fine.

## Landing it

One pull request, from anyone:

1. Add the two transcript files.
2. In [install.md](../install.md), replace the sentence that says the plugin path "has no
   recorded install transcript yet" with a link to the transcript, keeping the sentence about
   the symlink path as it is.
3. In [DEFINITION.md](DEFINITION.md), the CF-02 row may name the plugin evidence beside the
   symlink evidence; do not touch frozen rows elsewhere.
4. Reference #518 in the PR body. The remaining half of #518, the first `v*` tag populating the
   `dist` branch, is the maintainer's tag push and is checked separately.

If any step fails, the transcript still lands, as a failure transcript with the failing step's
output, and the PR says so in its title. A failed witness is evidence; a skipped one is not.
