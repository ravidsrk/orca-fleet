"""Verdict-derived merge check (#452): block merge until a GO verdict is posted at the tip.

Branch protection cannot express ``reviewed_sha == head_sha`` natively, so this
script is the custom required check: it passes iff the pull request carries a
GO verdict review whose ``reviewed_sha`` equals the PR's current head SHA. Any
push moves the head and fails the check until a fresh GO is posted.

Verdict convention (posted as a PR review body, any review state)::

    VERDICT: GO
    reviewed_sha: <full 40-hex head sha>

Scope is deliberately one property — SHA binding only. Approval state and
change requests stay enforced by branch protection itself (required approvals,
resolved conversations); this check neither duplicates nor weakens those.
Dismissed and change-requested reviews never count. Short SHAs are rejected:
ambiguity in what was reviewed is exactly the failure mode.
"""

import argparse
import json
import os
import re
import subprocess
import sys

VERDICT_RE = re.compile(r"^VERDICT:\s*GO\s*$", re.IGNORECASE | re.MULTILINE)
SHA_RE = re.compile(r"^reviewed_sha:\s*([0-9a-fA-F]{40})\s*$", re.MULTILINE)

GH_API = "gh api"


def go_reviews_at_tip(reviews, head_sha):
    """Return the submitted (non-dismissed) GO reviews bound to ``head_sha``.

    ``reviews`` is a list of GitHub review objects (``state``, ``body``,
    ``submitted_at`` keys). Matching is case-insensitive on the VERDICT line;
    the SHA comparison is case-insensitive hex but must be a full 40 hex
    digits — short SHAs never match.
    """
    head = head_sha.lower()
    hits = []
    for review in reviews:
        if review.get("state") not in ("APPROVED", "COMMENTED"):
            # DISMISSED never counts; CHANGES_REQUESTED cannot carry a GO —
            # a change request with a GO marker is self-contradictory, and
            # counting it would let a stale GO ride beside an open objection.
            continue
        body = review.get("body") or ""
        if not VERDICT_RE.search(body):
            continue
        match = SHA_RE.search(body)
        if match and match.group(1).lower() == head:
            hits.append(review)
    return hits


def verdict_at_tip(reviews, head_sha):
    """True iff at least one GO verdict review binds the current head SHA."""
    return bool(go_reviews_at_tip(reviews, head_sha))


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
    reviews = _gh_api(f"pulls/{pr_number}/reviews", repo)
    if not isinstance(reviews, list):
        reviews = []
    hits = go_reviews_at_tip(reviews, head_sha)
    return head_sha, reviews, hits


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
        head_sha, reviews, hits = check_pr(args.pr, args.repo)
    except RuntimeError as exc:
        print(f"verdict_check: {exc}", file=sys.stderr)
        return 2
    gos = [r for r in reviews if r.get("state") in ("APPROVED", "COMMENTED")
           and VERDICT_RE.search(r.get("body") or "")]
    print(f"head: {head_sha}")
    print(f"GO verdict reviews: {len(gos)} submitted, {len(hits)} at tip")
    for hit in hits:
        author = (hit.get("user") or {}).get("login", "?")
        print(f"  GO at tip by @{author} submitted_at={hit.get('submitted_at')}")
    if hits:
        print("verdict_check: PASS — GO verdict binds the merge tip")
        return 0
    if gos:
        print("verdict_check: FAIL — GO verdicts exist but none binds the current head "
              "(post a fresh VERDICT: GO with reviewed_sha == head)", file=sys.stderr)
    else:
        print("verdict_check: FAIL — no GO verdict review on this PR", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
