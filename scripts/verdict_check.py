"""Verdict-derived merge check (#452): block merge until a GO verdict is posted at the tip.

Branch protection cannot express ``reviewed_sha == head_sha`` natively, so this
script is the custom required check: it passes iff the pull request carries a
GO verdict review whose ``reviewed_sha`` equals the PR's current head SHA. Any
push moves the head and fails the check until a fresh GO is posted.

Verdict convention (posted as the body of an APPROVING review, or a COMMENTED
review by the PR author or a collaborator)::

    VERDICT: GO
    reviewed_sha: <full 40-hex head sha>

A GO counts from an APPROVED review (GitHub restricts Approve to collaborators
with write access), or from a COMMENTED review whose author is the PR author
(the coordinator binding its own verdict — the normal fleet flow, since GitHub
forbids approving your own PR) or whose author_association is OWNER / MEMBER /
COLLABORATOR. A drive-by COMMENTED GO from anyone else never counts (PR #460
review, P1). Approval policy beyond that (how many, from whom, conversations
resolved) stays enforced by branch protection itself; this check adds SHA
binding, not a second approval rule. Dismissed and change-requested reviews
never count. Short SHAs are rejected: ambiguity in what was reviewed is
exactly the failure mode. The marker is case-SENSITIVE (exact `VERDICT: GO`):
machine-read verdicts must not have case variants, and the CI job gate matches
the same literal (PR #465 review, P1).

CI trigger contract (see verdict-check.yml): the workflow evaluates GO-marker
reviews and dismissals only — never pushes, so a transient no-GO state cannot
fail-poison the head (a FAILED conclusion on the head SHA sticks past a newer
SUCCESS; only a re-run clears it). Post a new review per verdict.
"""

import argparse
import json
import os
import re
import subprocess
import sys

VERDICT_RE = re.compile(r"^VERDICT:\s*GO\s*$", re.MULTILINE)
SHA_RE = re.compile(r"^reviewed_sha:\s*([0-9a-fA-F]{40})\s*$", re.MULTILINE)

GH_API = "gh api"


# GitHub-computed review author trust tiers that may carry a COMMENTED GO.
TRUSTED_ASSOCIATIONS = frozenset({"OWNER", "MEMBER", "COLLABORATOR"})


def _author_trusted(review, pr_author):
    login = (review.get("user") or {}).get("login", "")
    if pr_author and login == pr_author:
        return True
    return review.get("author_association") in TRUSTED_ASSOCIATIONS


def go_reviews_at_tip(reviews, head_sha, pr_author=None):
    """Return the trusted GO reviews bound to ``head_sha``.

    ``reviews`` is a list of GitHub review objects (``state``, ``body``,
    ``user.login``, ``author_association``, ``submitted_at`` keys).
    The VERDICT line matches the exact uppercase literal; the SHA comparison
    is case-insensitive hex but must be a full 40 hex digits — short SHAs
    never match.
    """
    head = head_sha.lower()
    hits = []
    for review in reviews:
        state = review.get("state")
        if state == "APPROVED":
            pass  # Approve is collaborator-only; the state is the signal.
        elif state == "COMMENTED" and _author_trusted(review, pr_author):
            pass  # own-PR verdict or trusted tier (PR #460 P1 + self-approval).
        else:
            # DISMISSED never counts; CHANGES_REQUESTED with a GO marker is
            # self-contradictory; COMMENTED from an untrusted author is a
            # drive-by and must not satisfy a required check.
            continue
        body = review.get("body") or ""
        if not VERDICT_RE.search(body):
            continue
        match = SHA_RE.search(body)
        if match and match.group(1).lower() == head:
            hits.append(review)
    return hits


def verdict_at_tip(reviews, head_sha, pr_author=None):
    """True iff at least one trusted GO verdict review binds the head SHA."""
    return bool(go_reviews_at_tip(reviews, head_sha, pr_author))


def _gh_api(path, repo):
    cmd = ["gh", "api", "--paginate", "-H", "Accept: application/vnd.github+json",
           f"repos/{repo}/{path.lstrip('/')}"]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        raise RuntimeError(f"{GH_API} {path} failed: {proc.stderr.strip()}")
    out = proc.stdout.strip()
    if not out:
        return []
    try:
        return json.loads(out)
    except json.JSONDecodeError:
        # --paginate concatenates one JSON array per page; merge them.
        merged = []
        for line in out.splitlines():
            line = line.strip()
            if line:
                merged.extend(json.loads(line))
        return merged


def check_pr(pr_number, repo):
    """Fetch the PR head SHA + reviews and evaluate the verdict rule."""
    pr = _gh_api(f"pulls/{pr_number}", repo)
    if isinstance(pr, list):  # paginated single-object response
        pr = pr[0] if pr else {}
    head_sha = (pr.get("head") or {}).get("sha", "")
    pr_author = (pr.get("user") or {}).get("login", "")
    reviews = _gh_api(f"pulls/{pr_number}/reviews", repo)
    if not isinstance(reviews, list):
        reviews = []
    hits = go_reviews_at_tip(reviews, head_sha, pr_author)
    return head_sha, reviews, hits, pr_author


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pr", required=True, help="pull request number")
    parser.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY", ""),
                        help="owner/repo (default: $GITHUB_REPOSITORY)")
    args = parser.parse_args(argv)
    if not args.repo or "/" not in args.repo:
        print("verdict_check: need --repo owner/repo (or $GITHUB_REPOSITORY)", file=sys.stderr)
        return 2
    try:
        head_sha, reviews, hits, pr_author = check_pr(args.pr, args.repo)
    except RuntimeError as exc:
        print(f"verdict_check: {exc}", file=sys.stderr)
        return 2
    gos = [r for r in reviews if VERDICT_RE.search(r.get("body") or "")]
    print(f"head: {head_sha} (PR author: @{pr_author})")
    print(f"GO verdict reviews: {len(gos)} submitted, {len(hits)} trusted at tip")
    for hit in hits:
        author = (hit.get("user") or {}).get("login", "?")
        print(f"  GO at tip by @{author} [{hit.get('state')}] "
              f"submitted_at={hit.get('submitted_at')}")
    if hits:
        print("verdict_check: PASS — GO verdict binds the merge tip")
        return 0
    trusted = [r for r in gos
               if r.get("state") == "APPROVED"
               or (r.get("state") == "COMMENTED" and _author_trusted(r, pr_author))]
    if trusted:
        print("verdict_check: FAIL — GO verdicts exist but none binds the current head "
              "(post a fresh VERDICT: GO with reviewed_sha == head)", file=sys.stderr)
    elif gos:
        print("verdict_check: FAIL — GO markers exist only from untrusted authors "
              "(drive-by COMMENTED reviews never count)", file=sys.stderr)
    else:
        print("verdict_check: FAIL — no GO verdict review on this PR", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
