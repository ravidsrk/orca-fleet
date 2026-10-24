# Run a paid live arm in the container harness

Every paid live experiment arm runs one way: inside a fresh, disposable Linux container that
[`scripts/live_container.py`](../../scripts/live_container.py) starts, watches and destroys. On a
plain host every paid live path refuses, exit 2, before it reads or reserves anything
([`containment.py`](../runtime-scripts.md#containmentpy)). This page is for the operator who runs
one. It covers building the image, supplying the token, the command for each arm, and what the
receipt proves.

The arms are `wip_curve` (#604), `ablation` (#606), `hint_replay` (#605), `trajectories` (#602) and
`first_run` (#596). Each spends money. Run one only under the spend its owner authorised, with
that arm's own cap flags.

## Why a container

A paid call's processes are found by the `OF_CALL_ID` marker in their environment, so a sweep can
end every one of them, a detached descendant included. On macOS that cannot be proven: `ps -E`
does not show an Apple system binary's environment (`/bin/sh`, `/bin/sleep`), so a shell a worker
detached is invisible. Inside a Linux container `/proc/<pid>/environ` shows every process, so the
strong containment probe passes. Destroying the container is the final backstop. It also ends a
process that escaped in-process containment, including one that cleared its own environment.

## What the harness guarantees, and what it does not

The launcher starts each container with these properties:

- it runs as the image's non-root user (uid 10001), with `--rm`, a pids limit, a memory limit
  (no swap above it) and a CPU limit;
- it has no capability (`--cap-drop ALL`), `no-new-privileges`, no `--privileged`, no host
  namespace, no device and no docker socket;
- it receives the subscription token as a file: your token file, mounted read-only at
  `/run/secrets/claude_token`. The token is never in the container's environment, so
  `docker inspect` does not show it. It is never on a command line, in the receipt or in the saved
  output either: any occurrence in the output is replaced with `[REDACTED]` and counted;
- inside, `claude` on `PATH` is
  [`scripts/live_container_bin/claude`](../../scripts/live_container_bin/claude). It reads that
  file and execs the pinned Claude Code binary with `CLAUDE_CODE_OAUTH_TOKEN` set in that one
  process's environment, and `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB=1`, so the agent's own Bash tool
  does not inherit it. A version query needs no token. A missing, unreadable or malformed token
  file makes it refuse, exit 2, naming the path and never the contents. The container's `PATH`
  starts with the wrapper and leaves out `~/.local/bin`, where the raw binary is installed;
- it sees `/repo`, a read-only, self-contained export of your checkout's `HEAD`. The launcher
  refuses a dirty tree, so the container runs a commit. Nothing it writes reaches your checkout,
  its `.git` or its ignored files, such as a `.env`;
- it sees `/results`, the one read-write directory, which is also its working directory. The spend
  ledger and the evidence outlive the container there;
- it sees the launcher's attestation, read-only. The attestation holds a fresh nonce, the commit,
  the arm and the image. The container is named `of-live-<nonce>`, and the receipt records the
  same nonce;
- it runs under a wall-clock limit. At the limit the launcher kills and removes the container,
  then checks with `docker ps -a --filter id=<id>` that it no longer exists. An in-container
  `timeout` 120 s later is the backstop if the launcher itself dies.

Inside the container a paid entry point lifts its refusal only when three facts hold
(`containment.harness_problem`): a container marker (`/.dockerenv` or `/run/.containerenv`), an
attestation whose nonce matches the container's own hostname, and a passing strong probe. No
environment variable or flag lifts it. On any host without those facts every live path refuses
as before.

**The limit.** This guards against accidents on the host. It does not guard against an operator
who deliberately fakes a container. With root, anyone can write a `/.dockerenv`, an attestation
and a matching hostname on a Linux host. The attestation ties a container to its launch and
receipt; it is not proof against an adversary. Network egress is not restricted: the arm needs
the model API.

## Before you start

- **OrbStack** on macOS, or Docker Engine on Linux. On OrbStack, files the container writes are
  owned by you, and the container's user can read your 0600 token file. On Docker Engine on
  Linux, uid 10001 must be able to write the results directory and read the token file; a 0600
  file you own is unreadable to it, and the wrapper refuses with `cannot read the subscription
  token`.
- A **clean checkout** at the commit you mean to run. `git status` must show nothing, untracked
  files included.
- The arm's **authorised cap**. The harness does not replace any arm's own spend guard.

## 1. Build the image

```bash
python3 scripts/live_container.py build
```

This builds `open-fleet-live:claude-2.1.304` from
[`scripts/live_container.Dockerfile`](../../scripts/live_container.Dockerfile). The base,
`python:3.13.15-slim`, is pinned by digest. The image adds git, and installs Claude Code 2.1.304
with its official installer as the non-root user. The build fails on any other version. This is
the only step that downloads anything. The image carries the Dockerfile's sha256 as a label. A
receipt records whether its image was built from the Dockerfile at that commit.

## 2. Store the token

```bash
mkdir -p ~/of-live && claude setup-token    # copy the token it prints
install -m 600 /dev/null ~/of-live/oauth-token && $EDITOR ~/of-live/oauth-token
```

The file holds the token alone, on one line. The launcher refuses a missing file, a file others can
read, a symbolic link, and an empty file, and it never prints the file's contents. Use
`--token-file` for another path. The launcher mounts this file, read-only, into each container
it starts; nothing copies it anywhere else.

## 3. Run one arm

Each command has the same shape:

```bash
python3 scripts/live_container.py run --arm <arm> --results <host dir> --timeout <seconds> -- <the arm's own arguments>
```

Inside the container the repository is `/repo` and `<host dir>` is `/results`, the working
directory. **Every output path must be under `/results`.** Anything else is destroyed with the
container. A command that names a script runs it as `/repo/scripts/...`. Pass
`--harness-version "2.1.304 (Claude Code)"` where an arm asks for one: that is the container's
harness, not your host's.

**wip_curve** (#604, [pre-registration](../experiments/wip-curve-prereg.md)). Run one scheduled run
per launch, then report inside the harness as well. The report re-runs worker-written oracles:

```bash
python3 scripts/live_container.py run --arm wip_curve --results ~/of-live/wip-curve --timeout 14400 -- \
  run --results /results/experiment --workdir /results/sandboxes --worker live --agent claude \
  --model <pinned model id> --cost-cap-usd <the authorised cap> \
  --reservation-usd <the authorised reservation> --next 1
python3 scripts/live_container.py run --arm wip_curve --results ~/of-live/wip-curve --timeout 3600 -- \
  report --results /results/experiment
```

**ablation** (#606, [pre-registration](../experiments/ablation-prereg.md)):

```bash
python3 scripts/live_container.py run --arm ablation --results ~/of-live/ablation --timeout 43200 -- \
  run --tier live --cost-cap-usd <authorised> --model <model id> --harness-version "2.1.304 (Claude Code)" \
  --harness-cmd 'claude -p --output-format stream-json --permission-mode acceptEdits' --out /results/out
```

For #602's trajectory cells, use
`--harness-cmd 'python3 /repo/scripts/trajectory_harness.py claude -p --verbose --output-format stream-json --permission-mode acceptEdits'`.

**hint_replay** (#605, [`hint_provenance.py`](../runtime-scripts.md#hint_provenancepy)):

```bash
python3 scripts/live_container.py run --arm hint_replay --results ~/of-live/hint-replay --timeout 7200 -- \
  --live --tier live --model sonnet \
  --agent-cmd 'claude -p --model sonnet --output-format json --permission-mode acceptEdits' \
  --budget-usd 40 --per-call-usd 2 --agent-limit-flag=--max-budget-usd \
  --max-runs 18 --attempts 3 --out /results/results.json
```

**trajectories** (#602, [adversarial evals](../adversarial-evals.md#running-the-live-arm)). The
launcher supplies `run --suite trajectories`:

```bash
python3 scripts/live_container.py run --arm trajectories --results ~/of-live/trajectories --timeout 14400 -- \
  --tier live --all-live \
  --agent-cmd 'claude -p --verbose --output-format stream-json --disallowedTools TodoWrite,Task,WebFetch,WebSearch,NotebookEdit' \
  --model <exact model id> --harness-version "2.1.304 (Claude Code)" \
  --cost-cap-usd <authorised USD> --repeats 5 --out /results/out
```

**first_run** (#596, [certification](../certification.md)). Its `--json` receipt goes to the
launcher's saved output, and its `receipt.json` goes to the `--workdir`:

```bash
python3 scripts/live_container.py run --arm first_run --results ~/of-live/first-run --timeout 3600 -- \
  run --worker live --agent claude --profile ro --keep --workdir /results/ro --json
```

To check the setup without spending, run an inert or fixture tier the same way, for example
`--arm first_run -- run --worker inert --workdir /results/inert`.

`--pids-limit` (default 4096), `--memory` (8g) and `--cpus` (4) set the limits. `--receipts`
(default `~/of-live/receipts`) sets where receipts go. It may not overlap the results or the
checkout: the container can write to the results, and the receipt must stay out of its reach.

## 4. Read the receipt

Each launch writes `<receipts>/<UTC stamp>-<arm>-<nonce prefix>.json`, and the container's output
beside it as `.log`. The receipt holds:

| Field | What it records |
|---|---|
| `arm`, `arm_args`, `argv` | The arm, your arguments, and the exact command the container ran |
| `commit` | The checkout's `HEAD`, which `/repo` held |
| `image` | The image's id and digests, its labels, and `from_committed_dockerfile` |
| `nonce`, `hostname` | The attestation's nonce, and the container name derived from it |
| `container` | Its id, user, limits and mounts |
| `started_at`, `ended_at`, `elapsed_s`, `wall_clock_limit_s` | When it ran, against the limit |
| `timed_out`, `interrupted`, `exit_status` | How it ended: the limit, a signal, or the arm's own exit |
| `destroyed` | `verified: true` only when `docker ps -a --filter id=<id>` lists nothing |
| `token`, `token_redactions` | The token file's path and where it was mounted (never its value), and how many times the output carried it |

The receipt proves that one arm ran at that commit, in that image, in a container that no longer
exists. It does not prove the arm's result. That is the arm's own evidence under `/results`, a
`live-unreviewed` tier until a maintainer binds it in a run report under
[`docs/runs/`](../runs/README.md).

The launcher's exit is the arm's exit status once the container is verified destroyed. It exits
2 for a refused start, which creates nothing. It exits 3 when the container could not be verified
destroyed (fail closed: run `docker ps -a --filter label=org.open-fleet.live-harness`), and 124
when the limit ended the run.

## When it refuses

| Message | Fix |
|---|---|
| `the checkout … is dirty` | Commit or remove the listed paths |
| `no image …: build it first` | Run step 1 |
| `a harness container already exists` | One arm runs at a time. Inspect the leftover, then `docker rm -f` it |
| `the token file … is readable by others` | `chmod 600` the file |
| `claude (open-fleet live harness): no subscription token at /run/secrets/claude_token` | `claude` ran in a container this launcher did not start. Run the arm through it |
| `claude (open-fleet live harness): cannot read the subscription token` | On Linux, uid 10001 cannot read the token file (see [Before you start](#before-you-start)) |
| `--receipts … overlaps --results` | Put the receipts outside the results |
| `live runs are disabled outside the container-based live harness` | You ran an arm directly on the host. Run it through this launcher |
