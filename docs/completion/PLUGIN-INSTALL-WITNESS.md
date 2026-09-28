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
   matches="$(find ~/.claude/plugins -name plugin.json -path '*orca-fleet*' 2>/dev/null)"
   printf '%s\n' "$matches"
   test "$(printf '%s\n' "$matches" | grep -c .)" = 1 || echo "STOP: expected exactly one orca-fleet manifest"
   ROOT="$(dirname "$(dirname "$matches")")"
   grep -q '"name": "orca-fleet"' "$ROOT/.claude-plugin/plugin.json" && echo "root verified: $ROOT"
   du -sh "$ROOT"
   python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["version"])' "$ROOT/.claude-plugin/plugin.json"
   ```

   The search has no depth limit and must find exactly one manifest: zero means the install
   did not land where Claude Code keeps plugins (record the `/plugin` output and stop), more
   than one means a stale copy is present (remove it, or name the one you verify and say why).
   `ROOT` is only used once its manifest names `orca-fleet`. The version printed must equal
   the version of the tag you meant to install, and a version is not an identity: two copies
   can both say `0.7.0` and differ in every receipt tree. Every transcript therefore records
   the commit its copy came from, established one of three ways, tried in order:

   ```bash
   git -C "$ROOT" rev-parse HEAD 2>/dev/null                       # the copy is a checkout
   for d in $(find ~/.claude/plugins -maxdepth 3 -name .git -type d 2>/dev/null); do
     echo "$d: $(git -C "$(dirname "$d")" rev-parse HEAD)"; done       # the marketplace clone that fed it
   ```

   When neither prints a commit, fingerprint the copy's tree and match it against the tree of
   the commit you intended, extracted from a clone of the repository into a scratch directory:

   ```bash
   fp() { (cd "$1" && find . -type f -not -path './.git/*' -print0 | sort -z | xargs -0 sha256sum | sha256sum); }
   fp "$ROOT"
   git clone -q https://github.com/ravidsrk/orca-fleet "$TMPDIR/orca-fleet-src"
   mkdir -p "$TMPDIR/orca-fleet-tag" && git -C "$TMPDIR/orca-fleet-src" archive v0.7.0 | tar -x -C "$TMPDIR/orca-fleet-tag"
   fp "$TMPDIR/orca-fleet-tag"
   ```

   Equal fingerprints identify the copy as that tag's tree; unequal ones mean the install came
   from another commit, and the transcript says so and names the closest commit it can (the
   default-branch tip at install time, from the clone's `git rev-parse origin/HEAD`). The
   `du -sh` above is a measurement of the copy this commit identity names, and of nothing else.

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

   Capture the answer. The outcome-named missions must list. Then prove the bare-name lookups
   resolve inside the copy, which needs no Orca and no repository. First the machine check:
   the catalog validator, run from the plugin root, resolves every playbook and runtime
   policy a mission composes:

   ```bash
   cd "$ROOT" && python3 scripts/validate.py; echo "exit=$?"
   ```

   Record the whole output (first and last ten lines if it is long) and the exit line: the
   validator's own exit code is the verdict, and a failure's detail lines are the evidence,
   so nothing is piped through `tail`. A pass ends with "three-layer separation holds; evals
   valid." and `exit=0`. Then the in-session check:
   ask exactly

   ```
   read the playbooks that map-it composes and list their first headings
   ```

   and capture the answer: it must quote headings from files under the plugin's `playbooks/`
   directory, not report a missing file. A mission run is not part of this witness: every
   mission needs the Orca app and a target repository, and `review-it` has no human gate
   inside its run. If Orca is running and you want the extra evidence, start `review-it` on a
   pull request the session did not author and capture its first turn as a separate file
   named for what it shows; it neither adds to nor substitutes for the checks above.

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
3. Do not edit [DEFINITION.md](DEFINITION.md): its binding text is frozen (R6 / R13), and the
   CF-02 row there stays as written. Record the witness outside the frozen block, as a new
   row in [HUMAN_ACTIONS.md](HUMAN_ACTIONS.md) in that page's H-row format (id, instruction,
   what it unblocks, whether it gates launch, verification naming the two transcript files,
   status), the way H-07 records the CF-05 re-witness.
4. Reference #518 in the PR body. The transcript is one part of #518; the others, the first
   `v*` tag populating the `dist` branch and the receipt trees under `docs/runs/` and
   `docs/reports/` shrunk or relocated out of the plugin copy (review P1-5), are the
   maintainer's and are checked separately. The `du -sh` in step 2 measures the copy at the
   one commit the transcript identifies (by checkout, by the marketplace clone, or by the tree
   fingerprint matched against the intended tag); a shrink is shown by running step 2 again on
   a clean machine with the copy identified as the shrunk tag's tree, so the two transcripts
   carry the before and after sizes, each tied to a commit and never only to a version string.
   One measurement is a size, not a reduction; two measurements without commit identities are
   two sizes of unknown things.

If any step fails, the transcript still lands, as a failure transcript with the failing step's
output, and the PR says so in its title. A failed witness is evidence; a skipped one is not.
