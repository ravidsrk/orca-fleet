# The repository About description

*The one public description surface that is a setting, not a file.*

GitHub's **About** box — right-hand column of the repository home — is the blurb
that indexers scrape and republish. No badge can generate it and no workflow in
this repo can write it, so it is the only description surface here that drifts
without anything going red.

## Canonical text

Paste this verbatim into **Settings → General → Description**, or the ✎ beside
**About** on the repository home:

```text
Outcome-named autonomous fleets for the Orca runtime — SHA-bound evidence definition of done, best-of-breed worker recipes, one router per worker.
```

Applying it is a maintainer action: repository settings are writable only from an
account with admin rights on this repo, which is why the text lives here as a
handoff rather than in something automated.

While that dialog is open, two adjacent fields are also empty and worth filling
from values this repo already maintains:

- **Website** — `homepage` in `.claude-plugin/plugin.json`.
- **Topics** — the leading entries of `keywords` in the same file
  (`orca`, `autonomous-agents`, `multi-agent`, `orchestration`, `claude-code`,
  `agent-skills`). Topics are how GitHub's own search finds a pack that the
  external indexers in [distribution.md](distribution.md) still miss.

## Why the canonical text carries no catalog count

The text this replaces opened with a hardcoded number, and that number has been
caught stale twice. The first time is on the record in
[`completion/evidence/H-04-repo-description.txt`](completion/evidence/H-04-repo-description.txt):
the box lagged the catalog, a human edited it, and the fix was verified by
re-reading the API. It then lagged again — and a downstream cache is still
serving the value from *before* that repair, so three different numbers have
been in circulation at once for a surface that only ever had one right answer.

Every other description surface in this project already solved that problem by
not stating a number at all:

| Surface | Description text |
|---|---|
| `.claude-plugin/plugin.json` | opens *"Outcome-named autonomous fleets for the Orca runtime…"* |
| `.claude-plugin/marketplace.json` | *"Outcome-named autonomous fleets for the Orca runtime"* |
| README badge | reads the count from `assets/badges/missions.json`, regenerated from the catalog |

That is not a stylistic preference; `check_doc_counts` in `scripts/validate.py`
fails the build if a catalog count reappears in `README.md` or either manifest. The About
box was exempt only because it is not a file — never because the reasoning did
not apply to it. This file closes that gap: it *is* a file, it is linted by the
same rule, and so the canonical text cannot regain a count without CI saying so.

If you would rather the blurb lead with the number anyway, that is a maintainer
call and the trade is explicit: the box then needs a hand-edit on the day every
new mission lands, and it will be wrong in the window before someone does it.
