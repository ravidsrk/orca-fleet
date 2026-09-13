---
name: orca-per-workspace-env
description: >-
  Set up, review, debug, or validate an Orca per-workspace environment recipe: the
  on-demand, disposable runtime (cloud sandbox, VM, SSH host, or local container)
  Orca creates fresh for each workspace. Use to stand up a new recipe end to end,
  fix an `environmentRecipes` entry in `orca.yaml`, scaffold provider lifecycle
  scripts, or resolve an `orca vm recipe doctor` failure. Use `orca-cli` for
  ordinary worktree and workspace creation with no recipe involved.
---

# Per-Workspace Environments

`ORCA` is a placeholder for the executable you resolved in the stub; substitute it before running.
Inside the lifecycle scripts the placeholder does not apply: `orca serve` written there runs on
the remote machine's own binary.

## Autonomy envelope

Without asking again you may read the repo and its `orca.yaml`, detect provider CLIs and their
login state, scaffold and edit files under `scripts/orca-vm/`, and run `ORCA vm recipe doctor`
without `--provision`. Get an explicit OK before each paid step: the base snapshot, the auth
snapshot, and `--provision`. One OK covers the whole `--provision` fix-and-rerun loop. Stop for
the interactive agent login, which you cannot drive; the user runs it and tells you when it is
done. Never create an Orca workspace except for the step-10 test the user asked for. Do not create
Git commits unless asked. Never choose a plan or region, invent a scope, project, or billing id, or
write a credential into a script, `userData`, the state file, or a commit.

Preserve actionable provider errors and the failing command, redact secrets, and clean up resources
created by a failed step.

## The branch that shapes everything

In **Orca-server** mode `create` runs `orca serve` in the environment and emits a `pairingCode`. In
**SSH** mode `create` runs no server and emits a `connection.type:"ssh"` block Orca dials into.
Settle this first; it changes the `create` output and half the templates.

Keep Orca's checkout behavior unchanged by default: omit `checkoutMode`, emit schema version 1, and
let Orca create a linked worktree. Use `checkoutMode: provisioned-root` only when the user
explicitly wants one ephemeral machine to clone the finished workspace itself. That mode requires
direct SSH, an ordinary non-bare and non-sparse primary checkout at `projectRoot`, and schema
version 2.

## 1. Setup workflow

Drive these with the user. The order is fixed: the auth snapshot (step 6) boots from the base
snapshot (step 5), and `create` boots from the authenticated snapshot they produce. A
**[CHECKPOINT]** label marks a step the autonomy envelope stops for.

1. **Inspect the repo** for an existing `environmentRecipes` entry, `scripts/orca-vm/`, a state
   file, or setup notes. If a working recipe already exists, go straight to the doctor loop below
   instead of rebuilding.
2. **Interview the user up front.** Gather these choices and confirm them back before scaffolding
   anything. Do not pick for them and do not guess.
   - **Connection mode:** an Orca server or SSH, as above. Settle it first.
   - **Checkout ownership:** do not ask by default. Only when the user requires the environment to
     create the exact final checkout, confirm `provisioned-root` and direct SSH; otherwise omit it.
   - **Provider:** Vercel Sandbox, Fly, Modal, an existing SSH host, and so on. For a non-obvious
     provider, also ask scope, project, region, and plan limits. Then read that provider's CLI or
     SDK docs, or `<cli> --help`, before scaffolding: you need its exact create, exec, snapshot, and
     remove verbs. If a provider advertises `ssh`, check whether it exposes a real dialable SSH
     target (host, port, user, key or proxy command) or only a provider-mediated interactive shell.
     Orca's SSH mode needs the former.
   - **Coding-agent CLI and account:** which agent runs in the environment (`codex`, `claude`, and
     so on) and that the user has an account for it. It is logged in during step 6.
   - **Git auth:** the token source for cloning a private repo (`GH_TOKEN`, `GITHUB_TOKEN`, or
     `gh auth token`).
3. **Check prerequisites** (section 2) and confirm the items above are in place before any paid
   step.
4. **Scaffold the scripts and state file**, filling in the provider's real commands, and make them
   executable. The per-provider worked examples are in the conditional references below.
5. **[CHECKPOINT] Build the base snapshot** (section 3). Paid and slow.
6. **[CHECKPOINT] Authenticate the agent** (section 4). Interactive; the user follows a URL and code.
7. **Wire the recipe** so `orca.yaml` points create, suspend, resume, and destroy at the scripts.
   Tell the user up front: the composer reads `environmentRecipes` from the primary checkout, so
   a recipe that lives only on a branch never appears as a "Run on" option. The doctor works on
   any branch; the picker needs `orca.yaml` on the primary branch.
8. **Dry-run the doctor** — free and static.
9. **[CHECKPOINT] Live self-test** — run the `--provision` loop until it passes.
10. **[CHECKPOINT] Optional workspace test** — only if asked: create a workspace via the picker,
    then verify sleep, wake, and delete.

## 2. Prerequisites

These are the user's responsibility. Verify what you can, ask for the rest, invent nothing, and
say which items you verified and which the user asserted.

- **Cloud account and plan** that allows sandboxes or VMs. Ask.
- **Provider CLI installed and authenticated** — detect with `command -v <cli>` and check auth (for
  example `vercel whoami`). If it is missing, point at the provider's docs; do not log them in.
- **Scope, project, and region** the environments live under. Ask; this flows into every script via
  state.
- **Plan, timeout, and RAM caps.** Record them. Vercel's Hobby plan, for example, caps sandbox
  timeout at 45 minutes, which limits both the base build and the per-workspace runtime.
- **Git token for private repos** (`GH_TOKEN`, `GITHUB_TOKEN`, or the provider's git auth, falling
  back to `gh auth token`).
- **Coding-agent CLI choice** and an account for it.

## 3. Base snapshot

Build once, snapshot, and every workspace boots from that image in seconds instead of rebuilding.
Provisioning and building often takes 20 to 30 minutes.

- Build the **headless Electron main only**, not the renderer, so it fits in plan RAM.
- Use the environment image's package manager (`apt`, `dnf`, `apk`, per the base distro, not the
  provider brand).
- Clone with the git token via `GIT_ASKPASS` (section 5).
- Trap errors and remove the half-built environment, so a crash does not leave a paid resource
  running.
- **Never snapshot a machine on which the Orca runtime has already run.** The first `orca serve`
  creates the runtime's user-data directory, and everything in it is baked into the image and shared
  by every environment booted from it: the pairing keypair and device-token registry
  (`orca-devices.json`, `orca-e2ee-keypair.json`), `agent-session-authority.key`, and the build
  box's logs, terminal history, and orchestration database. Two VMs from one such snapshot emitted
  identical `deviceToken` and `pairedDeviceId`. Snapshot before the runtime has ever run, or delete
  the resolved user-data directory first:
  `orca_user_data_path="${ORCA_USER_DATA_PATH:-${XDG_CONFIG_HOME:-$HOME/.config}/orca}"`.
  Resolve symlinks and inspect that path before deleting it: it must be an absolute directory
  dedicated to Orca runtime data, never `/`, the home directory, or an ancestor of home. Refuse
  empty or relative paths. Remove only that verified directory, not an unchecked environment value.
  That matches Orca's Linux precedence for custom and default paths; deleting a named file list
  drifts as Orca adds state.
- Snapshot the stopped environment, parse the snapshot id, and write it plus scope, project, port,
  and repo into state.

## 4. Agent-auth snapshot

The base snapshot has the agent CLI installed but not logged in, and per-workspace environments are
ephemeral. Authenticate once and bake it into a second snapshot layer.

1. Boot an environment from the base `snapshotId` in state.
2. Run the agent's login interactively. **On a headless machine this must be the device-auth flow**
   (for example `codex login --device-auth`), never plain `codex login`: the default OAuth login
   starts a loopback callback server on a port the host browser cannot reach, so it hangs.
   Device-auth prints a URL and code the user opens on the host.
3. Verify the login and refuse to snapshot an unauthenticated machine. **Prefer the status command's
   exit code**, because most agent CLIs exit non-zero when unauthenticated. If you match text
   instead, agent status often goes to stderr, so fold stderr first (`... 2>&1 | grep …`) and match
   the agent's exact success line. Never `grep -qi 'logged in'`, which also matches "not logged in"
   and would commit an unauthenticated image.
4. Re-snapshot, parse the new id, overwrite `snapshotId` in state with the authenticated image, and
   record `authSourceSnapshotId`. Remove the auth environment.

Authenticate inside the runtime and snapshot that layer. Do not bind-mount or copy a host agent
home such as `~/.codex`: its sqlite state, hook approvals, caches, and host-specific config break
in the runtime. If the agent's credentials are short-lived, tell the user the snapshot needs
periodic re-auth.

You cannot drive step 2. You have no TTY for `docker exec -it` or `ssh -t`, so the user runs the
login in their own terminal and tells you when it finished. Verify and re-snapshot after that.

> Harness adapter: in Claude Code the user can run that login in the session itself with the bang
> prefix, `! <cmd>`, including the required space after `!`. Other harnesses have no such
> affordance; the portable rule is that the user runs it wherever they have a terminal.

Section 3's rule still applies: if you ran `orca serve` on this machine to smoke-test it, delete
the runtime's user-data directory before re-snapshotting, or every workspace from this image
shares one pairing identity.

## 5. Credentials

- Never commit secrets or put them in `userData`, recipe JSON, comments, docs, or the state file.
- **Git token:** read it from `GH_TOKEN` or `GITHUB_TOKEN`, falling back to `gh auth token`. Pass it
  to the environment only via the provider's ephemeral `--env`. Inside the environment, use a
  `GIT_ASKPASS` helper with `x-access-token` rather than the token in the clone URL, plus
  `GIT_TERMINAL_PROMPT=0` so a missing token fails fast instead of hanging. When you write that
  helper from inside `bash -lc` under `set -u`, escape the positional argument and the token as
  `\$1` and `\$GH_TOKEN` so they land literally and resolve at git-runtime: an unescaped `$1` aborts
  with "unbound variable", and a literal `$GH_TOKEN` keeps the real token out of the written file.
  `rm -f` the helper after the clone or fetch.
- **Provider auth:** rely on the provider CLI's logged-in session, not checked-in keys.
- **Agent auth:** lives in the authenticated snapshot from section 4, never in a file you write.
- State holds only non-secret wiring: snapshot ids, scope, project, port, repo URL and ref.

## 6. State file

A repo-local JSON file such as `scripts/orca-vm/<provider>-state.json` threads non-secret values
between phases. Each script resolves a value as env var, then state, then a built-in fallback, and
merges its outputs back. The base snapshot writes `snapshotId`; the auth snapshot overwrites it with
the authenticated image; per-workspace `create` boots from `snapshotId`.

```json
{
  "baseName": "orca-base",
  "snapshotId": "snap_authenticated_image_id",
  "authSourceSnapshotId": "snap_base_image_id",
  "scope": "<provider-scope>",
  "project": "<provider-project>",
  "port": 7331,
  "repoUrl": "https://host/org/repo.git",
  "repoRef": "main",
  "projectRoot": "/abs/path/on/remote/repo"
}
```

## 7. Script shapes

Scaffold under `scripts/orca-vm/`. These are shapes; fill in the provider's real commands. **Every
script reserves stdout for its final JSON object and sends progress and errors to stderr.** A stray
`echo` on stdout corrupts the result. Give each script a `json_value <key>` and `env_value <NAME>`
reader (env, then state, then fallback).

The local-side scripts (`create`, `suspend`, `resume`, `destroy`, and the hand-run snapshot and auth
scripts) run on the user's desktop, so they must run on that OS: on macOS and Linux,
`#!/usr/bin/env bash`, `set -euo pipefail`, quoted paths. Commands you `exec` inside the Linux
environment are always bash.

### 7a. Base snapshot (`<provider>-base-snapshot.sh`)

```bash
#!/usr/bin/env bash
set -euo pipefail
# resolve base_name/repo_url/repo_ref/project_root/port/scope/project/timeout (env→state→fallback)
# resolve gh token: GH_TOKEN | GITHUB_TOKEN | `gh auth token`
# 1. provision an environment (timeout/vcpus/published port/snapshot retention); trap: remove on error
# 2. remote exec (long timeout): install pkgs + gh + corepack/pnpm + agent CLI;
#    clone with GIT_ASKPASS(token); write headless main-only build config;
#    dev setup; pnpm install; build CLI; build headless electron main; smoke-check tools
# 3. snapshot stopped environment; parse snapshot id (fail if unparseable)
# 4. merge { baseName, snapshotId, projectRoot, repoUrl, repoRef, port, scope, project } into state
# print only the state JSON to stdout
```

You run this by hand, not via `orca.yaml`, after exporting the first-run inputs state does not have
yet: provider scope and project, the repo URL and ref, and a git token. Later runs read them back.

### 7b. Auth (`<provider>-base-auth.sh`)

```bash
#!/usr/bin/env bash
set -euo pipefail
# read source snapshot from state.snapshotId (fail if absent); auth_name="${base_name}-auth"
# 1. boot an environment from the source snapshot; trap: remove on error
# 2. INTERACTIVE/TTY remote exec: agent login with the device-auth flow. The user runs this and
#    reports back when it finishes.
# 3. verify login by exit code, then refuse to snapshot if not logged in
# 4. snapshot; parse new id
# 5. merge { snapshotId:<new>, authSourceSnapshotId:<source> } into state; remove auth environment
# print only the state JSON to stdout
```

### 7c. Create (`<provider>-create.sh`)

```bash
#!/usr/bin/env bash
set -euo pipefail
# read authenticated snapshotId/scope/project/port/repo*/project_root (env→state→fallback)
# fail clearly if snapshotId is missing (point back to the snapshot phases)
# name = orca-${ORCA_RECIPE_ID}-${ORCA_VM_INSTANCE_ID} (sanitized, length-capped)
# 1. boot from snapshotId with a published port; capture the public URL → pairing address
#    (an externally reachable wss:// URL); trap: remove the environment on error
# 2. remote exec: ensure repo at desired commit; rebuild only if commit changed (cache marker)
# 3. Orca-server mode only: remote exec starting orca serve and reading the recipe JSON it writes
# 4. print one recipe-result JSON object to stdout
```

### 7d. Suspend, resume, destroy

```bash
#!/usr/bin/env bash
set -euo pipefail
payload="$(cat)"                       # Orca passes lifecycle JSON on stdin
resource_id="$(node -e 'const d=JSON.parse(process.argv[1]); process.stdout.write(d.recipeResult?.userData?.resourceId ?? "")' "$payload")"
[ -n "$resource_id" ] || { echo "No resource id in lifecycle payload" >&2; exit 1; }
# suspend: provider suspend "$resource_id"
# resume:  provider resume "$resource_id"; then RE-EMIT fresh recipe JSON (pairing may change)
# destroy: provider remove "$resource_id"   (or set destroy: none in orca.yaml)
```

### 7e. State file

Scaffold it with scope, project, and repo filled in and the snapshot ids empty.

## 8. Recipe result contract

Define recipes in `orca.yaml`:

```yaml
environmentRecipes:
  - id: cloud-sandbox
    name: Cloud Sandbox
    create: ./scripts/orca-vm/cloud-sandbox-create.sh
    suspend: ./scripts/orca-vm/cloud-sandbox-suspend.sh
    resume: ./scripts/orca-vm/cloud-sandbox-resume.sh
    destroy: ./scripts/orca-vm/cloud-sandbox-destroy.sh
```

`create` is required, runs locally from the repo root, and prints exactly one JSON object on stdout.
`suspend` and `resume` are optional and read the lifecycle payload on stdin; `resume` must print
fresh recipe JSON because the pairing may have changed. `destroy` may be omitted only with
`destroy: none`. The legacy keys `command` and `cleanup` still map to `create` and `destroy`.

The base result, which is what Orca-server mode prints:

```json
{
  "schemaVersion": 1,
  "pairingCode": "orca-pairing-code-or-url",
  "projectRoot": "/absolute/path/to/repo/on/remote",
  "userData": { "provider": "example", "resourceId": "provider-resource-id" }
}
```

`pairingCode` and `projectRoot` are required; `schemaVersion` (`1`) and `userData` are optional.
Three named deltas change that shape:

- **`orca serve --recipe-json` output** is this same object without `userData`. Merge your own
  `userData` into it rather than rebuilding it.
- **SSH mode** replaces `pairingCode` and `projectRoot` with a `connection` block whose `type` is
  `"ssh"`, and does not run `orca serve`. The exact target shape is in `references/ssh-host.md`.
- **Provisioned root** applies only to direct SSH and only when the user explicitly asked for it. Add
  `checkoutMode: provisioned-root` to the recipe, require `ORCA_RECIPE_RESULT_SCHEMA_VERSION=2`, and
  emit `"schemaVersion": 2` with `"checkoutMode": "provisioned-root"`. Fail if the requested schema
  is not `2` rather than falling back to the ordinary shape. Details are in `references/ssh-host.md`.

### The `orca serve` invocation

Inside the environment, in Orca-server mode, run exactly this. These flags are verified; do not
improvise them.

```bash
orca serve \
  --port "$PORT" \
  --project-root "$ABS_REPO_PATH_ON_REMOTE" \
  --pairing-address "$EXTERNAL_WSS_URL" \
  --recipe-json
```

In an environment built from source, run it as `pnpm exec orca-dev serve …` from the repo root;
`orca-dev` is the in-repo entrypoint. Plain `orca serve …` is the same command when the built CLI is
on that machine's PATH, and the flags and output are identical either way. There is no `--host` flag,
and `--project-root` must be an absolute directory on the remote.

`pairingCode` embeds whatever you passed as `--pairing-address`, so pass the externally reachable
address there and never hand-edit the code. Tunneling and port mapping are the script's job. With
`--recipe-json` the server keeps running, so redirect its stdout to a file and poll until the file
parses as JSON; if the process dies first, dump its stderr log and fail.

## 9. Doctor and the `--provision` loop

`ORCA vm recipe doctor <recipe-id> --repo-path <repo> --json` validates static wiring only; it boots
nothing. It checks local-host execution, the repo path, that the recipe id exists, that the create,
destroy, suspend, and resume command paths resolve, that suspend and resume are paired, and that
each script is executable (the POSIX exec bit, skipped on Windows).

**The free gate is clear only with no `fail` and no `warn`.** A `warn` keeps `ok: true`, so `ok`
alone proves nothing. Resolve each `warn`, or say why you accept it, before spending money on
`--provision`.

`--provision` (or its synonym `--connect`) runs the recipe end to end: `create`, validation of the
returned JSON, then `destroy`. Nothing is left running as long as `destroy` works.

Run it as a loop: read the `provisionTranscript` in the failed result, fix the script, re-run, until
`ok` is `true`. Do not wait for the user to paste errors. How to read the transcript is in
`references/failure-modes.md`.

The self-test sees only what the scripts print, so confirm separately that state holds an
**authenticated** `snapshotId` and that `destroy` is implemented and tested. With `destroy: none`
the self-test tears nothing down and you must clean up by hand.

## Conditional references

This guide covers the interview, the phase order, and the doctor loop on its own. At a gate below,
run `ORCA skills get orca-per-workspace-env --reference references/<file>.md` and read only that
document; `--references` lists the names. Read the reference at the gate, not before. If the CLI
rejects `--reference`, run `ORCA skills get orca-per-workspace-env --full` once instead: it returns
this guide plus every reference from the same CLI build, so read only the named one. If `--full` is
rejected too, keep these rules, use the command's `--help`, and do not guess flags.

| Action gate                                                                               | Bundled reference               |
| ----------------------------------------------------------------------------------------- | ------------------------------- |
| Writing the base-snapshot, auth, or create script for a snapshot-capable cloud provider   | `references/provider-vercel.md` |
| The recipe connects over SSH instead of starting `orca serve`, including provisioned root | `references/ssh-host.md`        |
| The environment is a local Docker container reached over SSH                              | `references/docker-ssh.md`      |
| The user's desktop is Windows and you are scaffolding local-side scripts                  | `references/windows-scripts.md` |
| A doctor, provision, clone, login, or snapshot step failed                                | `references/failure-modes.md`   |

---

# Bundled references

These references belong to the version-matched guide above. Read only the documents named by its action gates.

<!-- bundled-reference: references/docker-ssh.md -->

# Local Docker over SSH

Load this when the environment is a local Docker container reached over SSH. It models an ephemeral
SSH VM without cloud cost: build a base image with `sshd`, tools, repo prerequisites, and the agent
CLI; run an interactive auth container once; then `docker commit` that container as the
authenticated image per-workspace `create` boots from. The emitted result is the SSH shape in
`references/ssh-host.md`.

- Publish container SSH to a random localhost port with `-p 127.0.0.1::22`, and emit
  `connection.type:"ssh"` with `host:"127.0.0.1"`, that port, `username`, `identityFile`, and
  `identitiesOnly:true`.
- Generate a repo-local SSH key if needed, and gitignore the private and public key files.
- Generate unique SSH host keys with `ssh-keygen -A` on each container's first start and retain
  them for that container's lifetime. Remove `/etc/ssh/ssh_host_*` from the base and auth images
  before reuse; never distribute one private host key across workspaces.
- Before connecting, read the container's public host key through trusted local `docker exec` and
  record it under `[127.0.0.1]:<published-port>` in the desktop's `known_hosts`. If a port was reused,
  replace only that endpoint's old entry after verifying the new container identity. Preserve
  entries for other workspaces; never disable host-key checking to bypass a mismatch.
- The auth image is the Docker form of the agent-auth snapshot: the user runs the agent login inside
  the container, configures proxy env and config, approves hooks, and you commit once they report it
  finished.
- Do not bind-mount or copy the host's full agent home into the image. Let each container keep
  writable agent state; only the committed auth image carries reusable authenticated state.
- When committing from an interactive shell, force the runtime entrypoint back to `sshd`:
  `docker commit --change='ENTRYPOINT ["/usr/local/bin/orca-docker-ssh-entrypoint"]' …`.
- `destroy` reads `recipeResult.userData.resourceId` and runs `docker rm -f "$resource_id"`.

## Validation before wiring or live use

```bash
docker image inspect "$auth_image" --format '{{json .Config.Entrypoint}}'
docker run -d --name "$name" -p 127.0.0.1::22 -e "ORCA_SSH_PUBLIC_KEY=$pubkey" "$auth_image"
docker ps -a --filter "name=$name"
docker logs "$name"
ssh -i "$key" -p "$port" -o IdentitiesOnly=yes -o StrictHostKeyChecking=yes user@127.0.0.1 'codex --version'
```

Inspect the auth image entrypoint and do this startup-only `docker run` before the full clone and
install path. If the container exits immediately, read its logs before the cleanup trap removes it;
an image committed from an interactive shell with `ENTRYPOINT ["bash"]` is a common cause.

Validate two containers: their public host keys must differ, and each must match its recorded
endpoint before SSH succeeds. Restarting the same container preserves its key; reusing a deleted
container's port requires verifying and recording the replacement's key. Remove that endpoint's
entry on destroy only if it still matches the destroyed container's recorded key.

<!-- bundled-reference: references/failure-modes.md -->

# Failure modes

Load this when a doctor, provision, clone, login, or snapshot step failed. Each entry maps a
symptom to its cause; the rule that prevents it lives in the guide next to the step.

## Reading a failed `--provision` result

The JSON result carries a `provisionTranscript` with each stage's captured output, so you can
diagnose without asking the user for logs:

```json
{
  "ok": false,
  "checks": [{ "id": "recipe.provision", "status": "fail", "message": "…" }],
  "provisionTranscript": {
    "provision": { "exitCode": 0, "signal": null, "stdout": "…", "stderr": "…", "parseError": "…" },
    "destroy": { "exitCode": 0, "signal": null, "stdout": "…", "stderr": "…" }
  }
}
```

Streams are redacted and capped at both ends, keeping the start and the failure. Two common reads:

- A non-empty `stderr` with `exitCode 0` plus a `parseError` means `create` ran but printed something
  other than the single recipe-result JSON object on stdout. The offending stdout is in the
  transcript; the usual cause is a stray `echo`.
- A non-zero `exitCode` is a provider or script failure, described in `stderr`.

## Build and clone

- **Build exceeds the plan timeout**, for example Vercel Hobby's 45 minutes. Use enough vCPUs and a
  timeout that covers the build, or split the work, or move to a higher plan. The same cap limits
  per-workspace runtime, so surface it to the user.
- **Build exceeds plan RAM.** Building the headless main only, dropping the renderer, is the single
  biggest fit.
- **Private-repo clone hangs or fails.** The token is wrong or missing. `GIT_ASKPASS` plus
  `GIT_TERMINAL_PROMPT=0` makes it fail fast instead of prompting.
- **The `GIT_ASKPASS` helper aborts the clone with `$1: unbound variable`.** The `printf` or heredoc
  that wrote the helper inside `bash -lc` under `set -u` expanded `$1` and `$GH_TOKEN` at write time
  instead of leaving them for git-runtime. The same mistake writes the real token into the file.

## Agent auth

- **The agent verifies as "not logged in" despite a good login.** `codex login status` and similar
  print their success line to stderr, so a check that reads stdout only misses it.
- **A headless agent login hangs.** Plain OAuth `login` started a loopback callback server on a port
  the host browser cannot reach.
- **Agent auth did not persist.** Confirm `snapshotId` points at the authenticated snapshot rather
  than the base, and re-run the auth phase. If the agent's credentials are short-lived, the snapshot
  needs periodic re-auth; warn the user.
- **Agent auth copied from the host breaks.** A bind-mounted or copied host agent home carries sqlite
  files that can be unwritable or host-specific, hooks that need approval again, and config that
  references local-only environment variables. Authenticate inside the runtime and snapshot or commit
  that layer instead.

## Environment lifecycle

- **`known_hosts` mismatch on local Docker.** A new container may reuse an old container's port.
  Read its public key through trusted local Docker access, verify the container identity, then
  replace only that endpoint's recorded key. Never reuse private host keys across workspace images.
- **Snapshot expired or evicted.** `create` hit an unknown snapshot id. Re-run the base and auth
  snapshot phases and update `snapshotId` in state.
- **Docker auth image exits immediately.** Read `docker image inspect … .Config.Entrypoint` and
  `docker logs`. An image committed from an interactive shell keeps that shell as its entrypoint.
- **A paid resource leaked.** A long script created an environment and then failed without a trap
  that removes it.

<!-- bundled-reference: references/provider-vercel.md -->

# Worked example — Vercel Sandbox

Load this when writing the base-snapshot, auth, or `create` script for a snapshot-capable cloud
provider. It fills section 7's skeletons with a real surface, `vercel sandbox
create|exec|snapshot|remove`. Adapt the names and verify every flag against
`vercel sandbox --help` for the user's CLI version.

This is the Orca-server connection mode: the recipe emits a pairing URL. If the user chose SSH in
the interview, use `references/ssh-host.md` instead.

## Snapshot cleanup

The base and auth excerpts each belong to one `set -euo pipefail` script. Include this function
in both scripts and arm the trap before creating their temporary sandbox. Keep it armed through
verification, snapshot creation, and writing state; cleanup failure must remain visible.

```bash
cleanup_snapshot() {
  snapshot_exit=$?
  trap - EXIT
  if ! vercel sandbox remove "$1" "${vercel_args[@]}" >&2; then
    echo "Sandbox cleanup failed for $1; inspect and remove it before continuing" >&2
    snapshot_exit=1
  fi
  exit "$snapshot_exit"
}
```

Use fresh sandbox names for these scripts so cleanup cannot remove an existing environment.

## Base snapshot

Provision, install tools and clone, build headless, then snapshot.

```bash
# provision a fresh build sandbox (retain a couple of snapshots)
trap 'cleanup_snapshot "$base"' EXIT
vercel sandbox create --name "$base" --runtime node24 --timeout 30m --vcpus 4 --publish-port "$port" \
  --snapshot-expiration 30d --keep-last-snapshots 2 "${vercel_args[@]}" >&2
# remote build (long timeout): install pkgs+gh+pnpm+agent CLI, clone with GIT_ASKPASS (the helper's
# \$1/\$GH_TOKEN escaping is load-bearing — see the guide's Credentials section — then
# `rm -f /tmp/askpass.sh`), write the headless main-only build config (drop the renderer), dev setup,
# build CLI + headless main, smoke-check
vercel sandbox exec "$base" "${vercel_args[@]}" --timeout 25m --env "GH_TOKEN=$gh_token" … -- bash -lc '…build…' >&2
# snapshot the STOPPED sandbox and parse the id from CLI output (fail if unparseable)
out="$(vercel sandbox snapshot "$base" --stop --expiration 30d "${vercel_args[@]}" 2>&1)"; printf '%s\n' "$out" >&2
snapshot_id="$(printf '%s\n' "$out" | sed -nE 's/.*(snap_[A-Za-z0-9]+).*/\1/p' | tail -1)"
[ -n "$snapshot_id" ] || { echo "snapshot id missing" >&2; exit 1; }
# merge { baseName, snapshotId, scope, project, port, repoUrl, repoRef, projectRoot } into state; print state JSON
```

## Agent-auth snapshot

Boot the base, let the user log the agent in, verify, then re-snapshot. `codex` here is an example;
substitute the user's chosen agent's login and status verbs.

```bash
trap 'cleanup_snapshot "$auth"' EXIT
vercel sandbox create --name "$auth" --snapshot "$snapshot_id" --timeout 30m --publish-port "$port" "${vercel_args[@]}" >&2
# The USER runs this in their own terminal and completes the URL/code on the HOST.
vercel sandbox exec --interactive --tty "$auth" "${vercel_args[@]}" -- bash -lc 'codex login --device-auth'
```

Verify by exit code. The remote command prints a sentinel instead of relying on the exit code,
because a provider CLI may not propagate remote exit codes:

```bash
verdict="$(vercel sandbox exec "$auth" "${vercel_args[@]}" --timeout 30s \
  -- bash -lc 'if codex login status >/dev/null 2>&1; then echo ORCA_AGENT_LOGGED_IN; else echo ORCA_AGENT_LOGGED_OUT; fi')"
case "$verdict" in
  *ORCA_AGENT_LOGGED_IN*) ;;
  *) echo "agent not logged in; not snapshotting" >&2; exit 1 ;;
esac
```

Fallback for an agent whose `status` exit code says nothing about auth: capture the output with
stderr folded in and match the agent's exact success line. Match a variable, not a pipe, so the
provider process cannot take SIGPIPE:

```bash
status="$(vercel sandbox exec "$auth" "${vercel_args[@]}" --timeout 30s -- bash -lc 'codex login status 2>&1')"
grep -Eq 'Logged in using ChatGPT|Logged in via device' <<<"$status" \
  || { echo "agent not logged in; not snapshotting" >&2; exit 1; }
```

Then re-snapshot and record the new id:

```bash
out="$(vercel sandbox snapshot "$auth" --stop --expiration 30d "${vercel_args[@]}" 2>&1)"; printf '%s\n' "$out" >&2
new_id="$(printf '%s\n' "$out" | sed -nE 's/.*(snap_[A-Za-z0-9]+).*/\1/p' | tail -1)"
[ -n "$new_id" ] || { echo "authenticated snapshot id missing" >&2; exit 1; }
# overwrite state.snapshotId = new_id, record authSourceSnapshotId = snapshot_id; remove the auth sandbox
```

## Per-workspace `create`

```bash
#!/usr/bin/env bash
set -euo pipefail
# resolve from env→state→fallback: snapshot_id, scope, project, port, repo_url, repo_ref, project_root
vercel_args=(); [ -n "$scope" ] && vercel_args+=(--scope "$scope"); [ -n "$project" ] && vercel_args+=(--project "$project")
[ -n "$snapshot_id" ] || { echo "snapshotId missing — build the base and auth snapshots first" >&2; exit 1; }
gh_token="${GH_TOKEN:-${GITHUB_TOKEN:-$(command -v gh >/dev/null 2>&1 && gh auth token 2>/dev/null || true)}}"
recipe_id="${ORCA_RECIPE_ID:-vercel-sandbox}"
recipe_id="${recipe_id//./-}"  # Vercel names forbid dots.
instance_id="${ORCA_VM_INSTANCE_ID:-$(date +%s)}"
max_recipe_id_length=$((128 - ${#instance_id} - 6))  # Preserve the unique instance suffix.
[ "$max_recipe_id_length" -gt 0 ] || { echo "ORCA_VM_INSTANCE_ID is too long for a Vercel sandbox name" >&2; exit 1; }
name="orca-${recipe_id:0:max_recipe_id_length}-${instance_id}"

# Arm cleanup BEFORE create so a failing create can't leak a half-built paid sandbox.
cleanup_on_error() { [ "$?" -ne 0 ] && vercel sandbox remove "$name" "${vercel_args[@]}" >/dev/null 2>&1 || true; }
trap cleanup_on_error EXIT

# 1. boot from the authenticated snapshot, publish the serve port
create_output="$(vercel sandbox create --name "$name" --snapshot "$snapshot_id" \
  --timeout 30m --publish-port "$port" "${vercel_args[@]}" 2>&1)"; printf '%s\n' "$create_output" >&2
# Vercel prints the published https URL; derive the external wss:// pairing address from it
public_url="$(printf '%s\n' "$create_output" | sed -nE 's#.*(https://[^[:space:]]+\.vercel\.run).*#\1#p' | head -1)"
[ -n "$public_url" ] || { echo "no published URL in create output" >&2; exit 1; }
pairing_ws="${public_url/https:\/\//wss://}"

# 2. (remote) ensure the repo is at the right commit; rebuild only if the commit changed (cache marker)
vercel sandbox exec "$name" "${vercel_args[@]}" --timeout 20m \
  --env "GH_TOKEN=$gh_token" --env "ORCA_PROJECT_ROOT=$project_root" \
  --env "ORCA_REPO_URL=$repo_url" --env "ORCA_REPO_REF=$repo_ref" \
  -- bash -lc 'set -euo pipefail; cd "$ORCA_PROJECT_ROOT"; \
    export GIT_TERMINAL_PROMPT=0; \
    # Escaping is load-bearing here: re-test the fetch after any edit to the nested quoting.
    if [ -n "${GH_TOKEN:-}" ]; then \
      printf "%s\n" "#!/usr/bin/env bash" "case \"\$1\" in *Username*) echo x-access-token;; *Password*) echo \"\$GH_TOKEN\";; esac" > /tmp/askpass.sh; \
      chmod 700 /tmp/askpass.sh; export GIT_ASKPASS=/tmp/askpass.sh; fi; \
    git fetch origin "$ORCA_REPO_REF"; \
    git checkout -B "$ORCA_REPO_REF" FETCH_HEAD; \
    rm -f /tmp/askpass.sh; \
    c="$(git rev-parse HEAD)"; [ -f .orca-built ] && [ "$(cat .orca-built)" = "$c" ] || { \
      pnpm install --prefer-offline && pnpm run build:cli && \
      node config/scripts/run-electron-vite-build.mjs --config config/electron-vite.vm-serve.config.ts && \
      printf "%s" "$c" > .orca-built; }' >&2

# 3. (remote) start orca serve in the background, writing recipe JSON to a file; poll until it parses
recipe_json="$(vercel sandbox exec "$name" "${vercel_args[@]}" --timeout 60s \
  --env "ORCA_PORT=$port" --env "ORCA_PROJECT_ROOT=$project_root" --env "ORCA_PAIRING_ADDRESS=$pairing_ws" \
  -- bash -lc 'set -euo pipefail; cd "$ORCA_PROJECT_ROOT"; rm -f /tmp/orca-recipe.json /tmp/orca-serve.log; \
    nohup pnpm exec orca-dev serve --port "$ORCA_PORT" --project-root "$ORCA_PROJECT_ROOT" \
      --pairing-address "$ORCA_PAIRING_ADDRESS" --recipe-json >/tmp/orca-recipe.json 2>/tmp/orca-serve.log </dev/null & \
    pid=$!; for _ in $(seq 1 80); do \
      node -e "JSON.parse(require(\"node:fs\").readFileSync(\"/tmp/orca-recipe.json\",\"utf8\"))" >/dev/null 2>&1 && { cat /tmp/orca-recipe.json; exit 0; }; \
      kill -0 "$pid" 2>/dev/null || { cat /tmp/orca-serve.log >&2; exit 1; }; sleep 0.25; \
    done; cat /tmp/orca-serve.log >&2; echo "serve recipe JSON timed out" >&2; exit 1')"

# 4. print serve's JSON enriched with userData (single object on stdout)
node -e 'const p=JSON.parse(process.argv[1]); console.log(JSON.stringify({...p, schemaVersion:1,
  userData:{...p.userData, provider:"vercel-sandbox", resourceId:process.argv[2], snapshotId:process.argv[3]}}))' \
  "$recipe_json" "$name" "$snapshot_id"
trap - EXIT
```

`suspend`, `resume`, and `destroy` run `vercel sandbox stop|...|remove "$resource_id"`, reading
`userData.resourceId` from the lifecycle payload on stdin.

The `128` in `max_recipe_id_length` is Vercel's sandbox name cap. Confirm it against
`vercel sandbox create --help` or Vercel's docs for the user's CLI version before relying on it; a
wrong cap silently truncates recipe ids in resource names.

<!-- bundled-reference: references/ssh-host.md -->

# SSH connection mode, including provisioned root

Load this when the recipe connects over SSH instead of starting `orca serve`, and when the user has
explicitly asked for `checkoutMode: provisioned-root`.

SSH mode is a different shape, not the Orca-server templates relabeled. `create` runs no
`orca serve` and emits no `pairingCode`. Orca connects over its SSH relay, brings up the git and
filesystem providers, and imports the repo. The script only readies the host and prints the SSH
details Orca dials.

## The result shape

Orca rejects anything else. Required fields only; add optionals from the next section as the
network needs them.

```json
{
  "schemaVersion": 1,
  "connection": {
    "type": "ssh",
    "projectRoot": "/abs/path/to/repo/on/host",
    "target": {
      "label": "my-box",
      "host": "192.0.2.10",
      "port": 22,
      "username": "ubuntu"
    }
  }
}
```

`label`, `host`, `port`, and `username` are required. `projectRoot` is an absolute path on the host.

## Which optional `target` fields to set

These describe how the user's desktop reaches the box; there is no `orca serve` URL in SSH mode.

- A public IP or DNS name, or a Tailscale or VPN address, is the `host`; the SSH port is `port`,
  usually 22.
- Key auth sets `identityFile`. Add `"identitiesOnly": true` when the agent holds many keys.
- A bastion is reached through one of two fields: `jumpHost` takes a `user@host` ProxyJump
  target, and `proxyCommand` takes a full command such as an access proxy. **Set one, never both.** The schema
  accepts both, and the two consumers then disagree: one pushes `-J` and `-o ProxyCommand=` into the
  same argv, the other resolves `proxyCommand` and ignores `jumpHost` entirely.
- A service port the workspace needs is an entry in `portForwards`. Each entry requires
  `localPort`, `remoteHost`, and `remotePort`, and takes an optional `label`. The entry schema is
  strict, so an invented key such as `local` or `remote` fails validation.
- `relayGracePeriodSeconds` bounds how long Orca keeps the SSH relay alive after the workspace
  detaches. **`0` means unbounded**: the relay stays up until something explicitly terminates it, so
  it is the wrong value for a disposable runtime. Any other value must be between 60 and 604800
  seconds. A value between 1 and 59, such as `30`, is rejected and takes the whole recipe result
  with it.
  Omit the field unless the user asked for a specific reconnect grace window.

## Toolchain and agent auth on a persistent host

A persistent host is its own base image. Run the install steps and the agent's device-auth login
over SSH once, by hand, before wiring the recipe. The login is interactive, for example
`ssh -t user@host '<agent> login --device-auth'`, so the user runs it. The host then stays ready
across workspaces.

Use Git credentials already configured on the SSH host. For GitHub HTTPS repos, verify `gh auth
status` on that host and run `gh auth setup-git` there if Git has no credential helper. Installed
`gh` alone is not authentication. SSH URLs use the host's SSH keys; other providers use their own
credential setup. If credentials are missing, have the user configure them on the host. Do not
forward a desktop token in the SSH command.

Before the first connection, verify the host key using the provider console or another trusted
channel and record it in the desktop's `known_hosts`. Do not trust an unverified `ssh-keyscan`
result. The noninteractive script below refuses unknown or changed keys.

## The create script

```bash
#!/usr/bin/env bash
set -euo pipefail
# resolve from env→state→fallback (default unset optionals to ""): ssh_username, host,
#   ssh_port (default 22), identity_file, jump_host, proxy_command, project_root, repo_url, repo_ref
: "${identity_file:=}"; : "${jump_host:=}"; : "${proxy_command:=}"   # avoid set -u aborts on optionals
ssh_target="${ssh_username}@${host}"
if [ -n "$jump_host" ] && [ -n "$proxy_command" ]; then
  echo "set jump_host or proxy_command, not both" >&2; exit 1
fi
ssh_opts=(-p "$ssh_port" -o BatchMode=yes -o StrictHostKeyChecking=yes)
[ -n "$identity_file" ] && ssh_opts+=(-i "$identity_file")
[ -n "$jump_host" ] && ssh_opts+=(-J "$jump_host")
[ -n "$proxy_command" ] && ssh_opts+=(-o "ProxyCommand=$proxy_command")

# 1. ensure the repo is present and at the right commit on the host (NO orca serve here).
#    printf %q quotes every value for the remote shell, so a space or quote in a path or
#    ref cannot break out of the command.
remote_sync='set -euo pipefail
  export GIT_TERMINAL_PROMPT=0
  [ -d "$project_root/.git" ] || git clone "$repo_url" "$project_root"
  cd "$project_root" && git fetch origin "$repo_ref" && git checkout -B "$repo_ref" FETCH_HEAD'
ssh "${ssh_opts[@]}" "$ssh_target" "$(printf \
  'project_root=%q repo_url=%q repo_ref=%q bash -lc %q' \
  "$project_root" "$repo_url" "$repo_ref" "$remote_sync")" >&2

# 2. print the SSH connection block (NO pairingCode, NO orca serve). host/port/username tell Orca's
#    relay how to dial in; identityFile/jumpHost/proxyCommand/portForwards are emitted when set.
node -e 'const [host,port,user,idf,jh,pc,root]=process.argv.slice(1);
  const target={ label:"per-workspace-host", host, port:Number(port), username:user };
  if(idf) target.identityFile=idf; if(jh) target.jumpHost=jh; if(pc) target.proxyCommand=pc;
  // add target.portForwards=[{localPort,remoteHost,remotePort}] here if the workspace needs them
  console.log(JSON.stringify({ schemaVersion:1, connection:{ type:"ssh", projectRoot:root, target } }))' \
  "$host" "$ssh_port" "$ssh_username" "$identity_file" "$jump_host" "$proxy_command" "$project_root"
```

On a persistent host there is usually nothing to tear down, so set `destroy: none` and omit suspend
and resume. Orca still disconnects and reconnects its own SSH relay on sleep, wake, and delete, which
is separate from these scripts.

If the SSH host is instead an ephemeral, snapshot-capable VM — the user's hypervisor, or a cloud VM
with image support — keep the base-image model from `references/provider-vercel.md` for
provisioning, but still emit the `connection.type:"ssh"` block above instead of starting
`orca serve`.

## Provisioned root

For an explicitly requested one-VM-per-workspace checkout, the create script reads
`ORCA_RECIPE_RESULT_SCHEMA_VERSION`, `ORCA_REPO_URL`, `ORCA_REPO_REF`, `ORCA_REPO_REF_HEAD`, and
`ORCA_REPO_BRANCH`. Use `ORCA_REPO_REF` to fetch the selected source, but create `ORCA_REPO_BRANCH`
at the exact `ORCA_REPO_REF_HEAD` commit, because resolving the symbolic ref again can race with an
upstream update. `ORCA_REPO_URL` and `ORCA_REPO_REF` are a matched fetch pair, and the URL is the
remote Orca resolved the base ref against, which is not necessarily named `origin` on the desktop.
Fetch from the URL the pair supplies:

```bash
[ -n "${ORCA_REPO_REF_HEAD:-}" ] || { echo "missing pinned source commit" >&2; exit 1; }
git fetch "$ORCA_REPO_URL" "$ORCA_REPO_REF"
git cat-file -e "${ORCA_REPO_REF_HEAD}^{commit}"
git checkout -B "$ORCA_REPO_BRANCH" "$ORCA_REPO_REF_HEAD"
```

Return that primary checkout at `projectRoot` and emit schema version 2:

```json
{
  "schemaVersion": 2,
  "checkoutMode": "provisioned-root",
  "connection": {
    "type": "ssh",
    "projectRoot": "/abs/repo",
    "target": { "label": "my-box", "host": "192.0.2.10", "port": 22, "username": "ubuntu" }
  }
}
```

## Before declaring an SSH recipe done

The `--provision` self-test only sees what the scripts print, so smoke-test the exact emitted target
as well: dial the host and port with the identity or proxy settings, run `pwd`, verify the repo path,
and check the agent binary. If the recipe created a provider resource, also confirm `destroy`
removes it.

<!-- bundled-reference: references/windows-scripts.md -->

# Windows local-side scripts

Load this when the user's desktop is Windows and you are scaffolding the local-side scripts. A bare
`.sh` will not execute there. Either require WSL or Git Bash and point `orca.yaml` at a launcher such
as `bash ./scripts/orca-vm/<name>.sh` through a `.cmd` file, or scaffold PowerShell equivalents.

The remote-side commands you run inside the Linux environment stay bash regardless of the desktop OS.

```powershell
#requires -Version 5
$ErrorActionPreference = 'Stop'
# resolve env→state→fallback; run the provider CLI / ssh the same way;
# capture provider output; build the result object for the chosen mode and write ONE line of JSON to stdout.
# Orca-server mode: @{ schemaVersion=1; pairingCode=$pairingCode; projectRoot=$projectRoot; userData=@{...} }
# SSH mode:        @{ schemaVersion=1; connection=@{ type="ssh"; projectRoot=$projectRoot;
#                     target=@{ label=$label; host=$host; port=$port; username=$user } } }
($result | ConvertTo-Json -Compress -Depth 6)
# progress/errors → Write-Error / the error stream, never stdout.
```

The doctor's executable-bit check is a POSIX concept and is skipped on Windows, so a script that is
unusable on the user's machine for a different reason still has to be caught by the `--provision`
self-test.
