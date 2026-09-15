CATEGORY: bug (documentation, agent slice of a split finding)
SUMMARY: finish the machine-checkable remainder of the historical-docs polish: the stale
snapshot pointer and the unenforced guide-diagram parity.
CURRENT BEHAVIOUR: most polish already landed on the branch (snapshot banners, backfilled
assumptions, corrected counts, correction notes, one embedded diagram). Two gaps remain for
an agent: the machine-readable completion status record still names a snapshot commit that
predates the fixes it describes, and no automated check enforces that every mission guide
embeds its diagram asset (sixteen guides do; four have no asset at all).
DESIRED BEHAVIOUR: the status record names the commit the snapshot actually describes; an
automated parity check asserts every mission guide embeds its diagram asset, with an
explicit known-gap list naming the four missing diagrams until they exist.
KEY INTERFACES: the completion status record's snapshot-commit field; the mission guides
and their diagram assets; the docs-navigation test module, which gains the parity test
with its known-gap list.
ACCEPTANCE CRITERIA: [ ] the status commit field matches the tree the snapshot describes
[ ] the parity test fails if any listed guide loses its diagram reference [ ] the
known-gap list names exactly the four missing diagrams, no more [ ] the full suite stays
green.
OUT OF SCOPE: rendering the four missing diagrams (human-authored raster with no in-repo
source — a separate human question); any other completion-docs prose.
