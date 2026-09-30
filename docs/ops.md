# Ops — account inventory and incident process

Bus factor 1: Ravindra Kumar ([`ravidsrk`](https://github.com/ravidsrk),
`ravidsrk@gmail.com`). This page is the inventory of surfaces that can
break the catalog, and what to do at 2 a.m. It is not a product runbook —
missions already have those.

## Account inventory

| Surface | Account / handle | Lives in | Notes |
|---|---|---|---|
| GitHub | `ravidsrk` | [ravidsrk/orca-fleet](https://github.com/ravidsrk/orca-fleet) | source of truth, Actions (`validate` gates + `negative-control-demo` pinned-demo gate; `alert-on-failure` files a `ci-failure` issue when either fails on `main`), private vulnerability reporting |
| Claude plugin marketplace | GitHub self-host + buildwithclaude auto-index | [`.claude-plugin/`](../.claude-plugin/plugin.json) | `/plugin marketplace add ravidsrk/orca-fleet`; official directory + skills.sh still [H-02](completion/HUMAN_ACTIONS.md) |
| greptile | maintainer CLI | [greptile.com](https://greptile.com/) | pre-push review on the maintainer machine; GitHub check on PRs |
| agentskills.io listing | not submitted | local `uvx --from skills-ref agentskills validate` | extra frontmatter (`proof`, `autonomy`, `proof_evidence`) is intentional — [CONTRIBUTING](../CONTRIBUTING.md) |
| Maintainer email | `ravidsrk@gmail.com` | [SECURITY.md](../SECURITY.md) | security reports (72h ack) and ops contact |

No other cloud accounts, registries, or production hosts. "Deploy" is merge
to `main` plus the plugin copy in `.claude-plugin/`.

## Release cut

A release has two commits: the **cut** contains its version, dated changelog and a
`preparing` record; the later **provenance** commit records the cut SHA. Published
rows and historical tag targets remain immutable. A preparing version is not yet
published: green preparation checks validate all historical releases too.

Start on a clean release branch with full history and tags fetched. Set
`RELEASE_VERSION` to the next semantic version and `RELEASE_DATE` to its ISO date
(`export RELEASE_VERSION=0.6.2 RELEASE_DATE=2026-09-12`, for example).
Run each complete block in order. Its subshell stops on any failed command
without depending on error-handling options in your interactive shell.

### Prepare

The following changes the three version surfaces together and marks only the
newest heading as preparing. Regenerate badges if catalog content changed.

<!-- release:prepare -->
```bash
(
set -eu
status=$(git status --porcelain)
test -z "$status"
python3 - <<'PY_RELEASE'
import json, os, re
from datetime import date
from pathlib import Path
version, day = os.environ["RELEASE_VERSION"], os.environ["RELEASE_DATE"]
assert re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", version)
assert date.fromisoformat(day).isoformat() == day
path = Path("docs/releases.json")
data = json.loads(path.read_text())
assert data.get("preparing") is None, "finish the current preparation first"
assert all(tuple(map(int, version.split("."))) > tuple(map(int, r["version"].split(".")))
           for r in data["releases"]), "choose a new version"
changelog = Path("CHANGELOG.md")
text = changelog.read_text()
assert text.count("## [Unreleased]") == 1
changelog.write_text(text.replace("## [Unreleased]", f"## [Unreleased]\n\n## [{version}] - {day}", 1))
for name in ("plugin", "marketplace"):
    manifest = Path(f".claude-plugin/{name}.json")
    value = json.loads(manifest.read_text())
    if name == "plugin": value["version"] = version
    else:
        value["metadata"]["version"] = version
        value["plugins"][0]["version"] = version
    manifest.write_text(json.dumps(value, indent=2) + "\n")
data["preparing"] = {"version": version, "cut_date": day}
path.write_text(json.dumps(data, indent=2) + "\n")
PY_RELEASE
python3 -m unittest tests.test_docs_navigation.TestDocsNavigation tests.test_docs_navigation.EveryReleaseHasTheTagItDescribes
)
```

Run the repository gates, including `python3 scripts/validate.py` and
`python3 -m unittest discover -s tests`, and review the diff before the cut.
Every published heading still needs its commit and annotated tag; only the sole
newest preparing heading has no cut SHA. Green checks do not authorize publication.

<!-- release:cut -->
```bash
(
set -eu
python3 -c 'import json, os; assert json.load(open("docs/releases.json"))["preparing"]["version"] == os.environ["RELEASE_VERSION"]'
git add CHANGELOG.md .claude-plugin/plugin.json .claude-plugin/marketplace.json docs/releases.json
git commit -m "Prepare release $RELEASE_VERSION"
)
```

### Tag and record provenance

The maintainer must authorize the exact cut SHA and version before creating or
publishing its tag. The remaining steps run only after that gate. A fixture
rehearsal may create local tags in its disposable repository without publication.

<!-- release:tag -->
```bash
(
set -eu
status=$(git status --porcelain)
test -z "$status"
python3 -c 'import json, os; assert json.load(open("docs/releases.json"))["preparing"]["version"] == os.environ["RELEASE_VERSION"]'
cut_sha=$(git rev-parse HEAD)
git tag -a "v$RELEASE_VERSION" "$cut_sha" -m "orca-fleet $RELEASE_VERSION"
python3 -m unittest tests.test_docs_navigation.TestDocsNavigation tests.test_docs_navigation.EveryReleaseHasTheTagItDescribes
)
```

Record the existing cut in a **new commit**, keeping the cut and its tag unchanged.
The command rejects a missing tag, a lightweight tag, or a tag at another cut.
Keep `RELEASE_VERSION` set to the authorized version. The same block accepts
its exact recorded inventory on retry, including after the commit succeeded.

<!-- release:record -->
```bash
(
set -eu
python3 - <<'PY_RELEASE'
import json, os, subprocess
from pathlib import Path
def git(*args):
    return subprocess.check_output(["git", *args], text=True).strip()
path = Path("docs/releases.json")
data = json.loads(path.read_text())
tag = "v" + os.environ["RELEASE_VERSION"]
ref = "refs/tags/" + tag
assert git("cat-file", "-t", ref) == "tag", "an annotated tag is required"
cut = git("rev-parse", ref + "^{commit}")
git("merge-base", "--is-ancestor", cut, "HEAD")
# The cut is immutable, so it -- not the working tree -- says what this release records.
at_cut = json.loads(git("show", cut + ":docs/releases.json"))
pending = at_cut.get("preparing")
assert pending and pending["version"] == os.environ["RELEASE_VERSION"], "wrong release cut"
recorded = {**at_cut, "preparing": None,
            "releases": [*at_cut["releases"], {**pending, "tag": tag, "commit": cut}]}
assert data in (at_cut, recorded), "inventory differs from the cut or its exact provenance"
assert not git("status", "--porcelain", "--", ".", ":(exclude)docs/releases.json"), "unrelated changes"
git("diff", "--exit-code", cut, "--", "CHANGELOG.md", ".claude-plugin")
if data != recorded:
    path.write_text(json.dumps(recorded, indent=2) + "\n")
PY_RELEASE
python3 -m unittest tests.test_docs_navigation.TestDocsNavigation tests.test_docs_navigation.EveryReleaseHasTheTagItDescribes
git add docs/releases.json
changes=$(git diff --cached --name-only -- docs/releases.json)
if [ -n "$changes" ]; then
    git commit -m "Record release $RELEASE_VERSION provenance"
fi
)
```

Re-run the repository gates and review the provenance commit before publishing
the approved branch and the single approved tag (`git push origin "v$RELEASE_VERSION"`).
The published state requires `preparing: null` and a row naming the cut, not the
provenance commit. Fresh clones fetch full history and tags before checking it.
The executable rehearsal is `python3 -m unittest tests.test_docs_navigation.ReleaseCutWalkthrough`.

**Recovery:** fetch missing historical tags first; compare each annotated tag's
peeled commit with its existing row. A mismatch stops the release for maintainer
investigation. Preserve published rows and refs; correct a bad release with a new
version. If tagging succeeded but recording failed, resolve the reported Git or
validation error and rerun the entire record block with the same `RELEASE_VERSION`.
Leave the inventory and any staged provenance in place: the block validates them
against the existing tag's cut, completes an interrupted write/stage/commit sequence,
and makes no new commit if recording already succeeded. Investigate a lock's owner
before removing a stale lock; never delete an active process's lock. An inventory
that differs from both expected states stops for investigation. Do not amend the
cut, recreate its tag, or reset published mappings to make a retry pass.

## Publishing Releases

`.github/workflows/release.yml` publishes a GitHub Release with the version's CHANGELOG
section as notes on every `v*` tag push (idempotent; it never creates a tag — the tag is
the authorization step above). The historical tags that predate it get their Releases once,
by hand, from an account with write access:

```bash
for t in v0.1.0 v0.1.1 v0.2.0 v0.2.1 v0.3.0 v0.4.0 v0.5.0 v0.6.0 v0.6.1; do
  gh workflow run release.yml -f tag="$t"
done
gh release list --limit 20     # nine rows once the runs finish
```

`.github/workflows/publish-dist.yml` builds `scripts/bundle.py`'s self-contained tree on the
same tag pushes (a manual run must name an existing `v*` tag; it refuses a branch) and
force-pushes it to the `dist` branch, the target copy installers point at
([docs/install.md](install.md)).

## Incident (2 a.m.)

1. A red `validate` or `negative-control-demo` run on `main` files (or updates) an issue labeled
   [`ci-failure`](https://github.com/ravidsrk/orca-fleet/issues?q=label%3Aci-failure)
   — that issue is the alert; it arrives through normal issue
   notifications, not the opt-in Actions setting. Open the run it links —
   catalog gates (`scripts/validate.py`, `tests/`, `proof_status.py --check`)
   are the only environment; the run summary shows the proof rollup and
   routing score. Close the issue when `main` is green again. To prove the
   path without redding `main`: Actions → `alert-on-failure` → Run workflow
   (a `[drill]` issue is filed and closed by the same run).
   Two shapes that are NOT a red suite: a run whose jobs all ended within
   seconds with no steps and no runner (`runner_id: 0` in the API) is an
   Actions or account-level incident — re-run it, do not debug the tests;
   and when that happens the alert workflow could not run either (it needs
   the same runner), which is how 2026-09-23 and 2026-09-25 went red on
   `main` with nothing filed (#520). The daily `main-health` schedule
   re-reads the latest `validate` conclusion and files the issue when
   Actions is running but nothing was filed; the no-runner case needs a
   check outside Actions — an uptime monitor or a cron on your machine
   polling `gh run list --workflow validate.yml --branch main --event push --status completed --limit 1 --json conclusion,updatedAt`
   (the query `main-health` runs, so an in-progress run never pages) and
   paging you when the result is absent (no completed run), stale
   (`updatedAt` older than a day), or its conclusion is not `success`
   (#528). No such monitor is installed yet — #528 tracks choosing one
   and drilling it.
2. If a clone or plugin load is broken: `plugin.json` `version` must equal
   the latest **dated** [CHANGELOG](../CHANGELOG.md) heading
   (`## [x.y.z] - YYYY-MM-DD`), not `[Unreleased]`. Do not half-cut a
   version bump.
3. Secrets never live in git (`.env`, `.secrets/` are ignored). Dispatch-key
   rotation must update **all three** verifier sources
   ([docs/verify-gate.md](verify-gate.md)):
   unset `ORCA_DISPATCH_PUBKEY`, land a new `.orca/dispatch-pubkey` through a
   reviewed PR, then on every verifier clone `git fetch origin` and confirm
   `git show origin/HEAD:.orca/dispatch-pubkey` equals the newly merged
   `.pub` (an unchecked fetch can leave the old pin). Do not leave a stale
   working-tree copy. Generate the pair with
   `runtime/scripts/dispatch-sign.py gen-key` **off the clone**; discard the
   old private seed. Security reports follow [SECURITY.md](../SECURITY.md).
4. Rollback = `git revert -m 1 <merge-sha>` on a branch, then a PR
   through the normal gates — never a force-push or a history rewrite
   on `main`. There is no hosted service or staging environment. A merge
   to `main` is the "deploy" above: it changes the default-branch tree that
   clones and the marketplace (`source: "./"`) install. Versioned
   publication is separate — `release.yml` (the GitHub Release) and
   `publish-dist.yml` (the `dist` branch) run on a `v*` tag push or a
   manual run naming an existing tag, and a tag exists only for an exact
   cut the maintainer authorized (Tag and record provenance, above). So an
   untagged bad merge is undone by the revert alone; a published bad
   release is never re-tagged or deleted — revert on `main`, then publish
   a new version through that same authorization, whose tag re-runs both
   workflows. A bad merge is undone the way it landed. Regenerate badges
   (`python3 scripts/gen-badges.py`) if the revert changes counts.
   Rehearsed on a scratch clone: 2026-09-01
   ([transcript](completion/evidence/P0-rollback-rehearsal.txt)) and
   2026-09-02
   ([transcript](completion/evidence/P0-r2-rollback-rehearsal.txt))
   (both single-parent reverts), plus the 2026-09-02 merge-shaped rehearsal
   ([transcript](completion/evidence/T-12-rollback-merge-rehearsal.txt) —
   it also shows the plain `git revert <merge-sha>` failure mode).
   If a deploy target ever appears, this step gains a staging deploy →
   rollback rehearsal and the completion register re-opens G-14 under P4.
