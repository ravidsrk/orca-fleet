#!/usr/bin/env python3
"""preflight.py — hard preflight checks for a matt-orchestration run.

Verifies the invariants that, if wrong, silently corrupt a whole run:
    1. `git` and `gh` are on PATH.
    2. The current directory is a git repo with a working `gh` remote.
    3. The integration BASE branch is NOT the default branch (M-5 guardrail — every
       per-finding PR merges into BASE, so `BASE == default` sends fixes straight to
       production, bypassing the anti-inflation gate and the human promotion review).
    4. BASE exists (locally or on origin).
    5. BASE was forked from the run's fork-point (a commit reachable from BASE that is
       also reachable from the default branch); rejects a BASE that was created off an
       unrelated history.
    6. If `--require-gitleaks` is passed (integrator will scan diffs), `gitleaks` must be
       on PATH; otherwise a soft warning is fine.

The BASE/default comparison canonicalizes ref aliases first (D1 remediation):
`origin/main`, `refs/remotes/origin/main`, and `refs/heads/main` all reduce to `main`,
so aliasing the default branch cannot slip past the M-5 guardrail.

Usage:
    preflight.py --base <base-branch> [--default <default-branch>] [--require-gitleaks]
    preflight.py --mode readonly        # read-only fleets: binary checks only, no gh/BASE
    # exit 0 = OK; exit 1 = usage/dependency; exit 2 = invariant violation

Wire it in at Phase 0 of the run (SKILL.md) and inside the integrator preamble before the
first `gh pr create` so a mid-run drift is caught, not tolerated.
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys


def _run(cmd: list[str]) -> tuple[int, str, str]:
    proc = subprocess.run(cmd, capture_output=True, text=True)
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


def _which(name: str) -> bool:
    return shutil.which(name) is not None


def _default_branch_via_gh() -> str | None:
    rc, out, _ = _run(["gh", "repo", "view", "--json", "defaultBranchRef", "-q", ".defaultBranchRef.name"])
    return out if rc == 0 and out else None


def _branch_exists(name: str) -> bool:
    """True only for an actual local or origin BRANCH — tags and raw SHAs resolve
    via rev-parse but are NOT acceptable as an integration BASE."""
    if name.startswith("refs/"):
        rc, _, _ = _run(["git", "show-ref", "--verify", "--quiet", name])
        return rc == 0 and (name.startswith("refs/heads/") or name.startswith("refs/remotes/"))
    for full in (f"refs/heads/{name}", f"refs/remotes/origin/{name}"):
        rc, _, _ = _run(["git", "show-ref", "--verify", "--quiet", full])
        if rc == 0:
            return True
    return False


def _merge_base(a: str, b: str) -> str | None:
    for pair in ((a, b), (f"origin/{a}", f"origin/{b}"), (a, f"origin/{b}"), (f"origin/{a}", b)):
        rc, out, _ = _run(["git", "merge-base", *pair])
        if rc == 0 and out:
            return out
    return None


def _canon_branch(ref: str) -> str:
    """Reduce a ref alias to its canonical branch name.

    `origin/main`, `refs/remotes/origin/main`, and `refs/heads/main` all reduce to
    `main`. Prefers git's own resolution; falls back to prefix stripping when the
    ref does not resolve to a symbolic name (e.g. a raw SHA).
    """
    rc, full, _ = _run(["git", "rev-parse", "--symbolic-full-name", ref])
    if rc == 0 and full:
        if full.startswith("refs/remotes/"):
            rest = full[len("refs/remotes/"):]
            return rest.split("/", 1)[1] if "/" in rest else rest
        if full.startswith("refs/heads/"):
            return full[len("refs/heads/"):]
        return full
    name = ref
    for prefix in ("refs/remotes/", "refs/heads/"):
        if name.startswith(prefix):
            name = name[len(prefix):]
    if name.startswith("origin/"):
        name = name[len("origin/"):]
    return name


def _tip_sha(ref: str) -> str | None:
    for candidate in (ref, f"origin/{ref}"):
        rc, out, _ = _run(["git", "rev-parse", "--verify", "--quiet", candidate])
        if rc == 0 and out:
            return out
    return None


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="preflight.py")
    parser.add_argument("--base", help="The integration BASE branch name (required unless --mode readonly).")
    parser.add_argument("--default", help="Default branch (auto-derived via `gh` if omitted).")
    parser.add_argument(
        "--mode",
        choices=("write", "readonly"),
        default="write",
        help="readonly: binary/repo checks only — for report-only fleets that never open PRs.",
    )
    parser.add_argument(
        "--require-gitleaks",
        action="store_true",
        help="Fail if `gitleaks` isn't on PATH (the integrator will run a scoped secret scan).",
    )
    args = parser.parse_args(argv)

    # Usage errors are exit 1 (contract: 0=OK, 1=usage/dependency, 2=invariant).
    # Do not call parser.error() here — argparse defaults to SystemExit(2), which
    # would collapse usage into the invariant bucket.
    if args.mode == "write" and not args.base:
        print("preflight: ERROR: --base is required unless --mode readonly", file=sys.stderr)
        return 1

    errors: list[str] = []
    warnings: list[str] = []

    # 1. Required binaries. Read-only fleets never touch gh/PRs.
    required = ("git",) if args.mode == "readonly" else ("git", "gh")
    for binary in required:
        if not _which(binary):
            errors.append(f"missing required binary on PATH: {binary}")
    if args.mode == "write":
        if args.require_gitleaks and not _which("gitleaks"):
            errors.append("missing required binary on PATH: gitleaks (--require-gitleaks was set)")
        elif not _which("gitleaks"):
            warnings.append("gitleaks not on PATH — integrator secret scan step will be skipped")

    if errors:
        for e in errors:
            print(f"preflight: ERROR: {e}", file=sys.stderr)
        return 1

    # 2. In a git repo, with a gh-visible remote.
    rc, _, _ = _run(["git", "rev-parse", "--git-dir"])
    if rc != 0:
        print("preflight: ERROR: not inside a git repository", file=sys.stderr)
        return 1

    if args.mode == "readonly":
        print("preflight: OK — mode=readonly (binary + repo checks only; no BASE/PR invariants)")
        return 0

    rc, repo, gh_err = _run(["gh", "repo", "view", "--json", "nameWithOwner", "-q", ".nameWithOwner"])
    if rc != 0 or not repo:
        print(f"preflight: ERROR: `gh repo view` failed: {gh_err or 'no output'}", file=sys.stderr)
        return 1

    # 3. Derive default branch if not given.
    default_branch = args.default or _default_branch_via_gh()
    if not default_branch:
        print("preflight: ERROR: could not derive default branch (pass --default)", file=sys.stderr)
        return 2

    # 4. BASE != DEFAULT_BRANCH (the M-5 guardrail), on CANONICAL names so ref
    #    aliases (`origin/main`, `refs/remotes/origin/main`) cannot slip past.
    canon_base = _canon_branch(args.base)
    canon_default = _canon_branch(default_branch)
    if canon_base == canon_default:
        print(
            f"preflight: ERROR: BASE ({args.base!r} -> {canon_base!r}) is the DEFAULT_BRANCH "
            f"({default_branch!r} -> {canon_default!r}). "
            "Every per-finding PR is merged into BASE; if BASE is the default branch, fixes land "
            "straight on production and bypass both the anti-inflation gate and the human "
            "promotion review. Create a dedicated integration branch (e.g. `<maintainer>/matt-orchestration`) "
            "off the current run's fork point and rerun.",
            file=sys.stderr,
        )
        return 2

    # 5. BASE exists AS A BRANCH (tags and raw SHAs are rejected — a PR base must
    #    be a branch, and accepting any rev would weaken the alias guard above).
    if not _branch_exists(canon_base):
        print(
            f"preflight: ERROR: BASE {args.base!r} is not a local or origin branch "
            "(tags and raw SHAs are not accepted as an integration BASE).",
            file=sys.stderr,
        )
        return 2

    # 6. BASE forks from a commit reachable from DEFAULT_BRANCH (guards against a BASE
    #    created off an unrelated history — e.g. a stale branch someone accidentally reused).
    mb = _merge_base(args.base, default_branch)
    if not mb:
        print(
            f"preflight: ERROR: no merge-base between {args.base!r} and {default_branch!r}; "
            "BASE does not appear to fork from the default branch's history.",
            file=sys.stderr,
        )
        return 2

    # 7. Same-tip advisory: a freshly created integration branch legitimately shares
    #    the default tip, so this is a warning, not a violation.
    tip_base, tip_default = _tip_sha(args.base), _tip_sha(default_branch)
    if tip_base and tip_default and tip_base == tip_default:
        warnings.append(
            f"BASE tip == default tip ({tip_base[:12]}) — expected for a freshly created "
            "integration branch; confirm BASE is not another alias of the default."
        )

    if warnings:
        for w in warnings:
            print(f"preflight: WARN: {w}", file=sys.stderr)

    print(
        f"preflight: OK — repo={repo}, base={args.base}, default={default_branch}, "
        f"fork_point={mb[:12]}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
