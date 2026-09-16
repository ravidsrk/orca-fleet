# Backlog — noticed but not touched (ship-it fixture run, frozen scope intact)

- B1 (Greptile P2 on #448, pages.py:48): malformed form priority returns
  FastAPI's JSON 422 instead of an HTML form re-render. Fixture-tolerable (a
  correct rejection); HTML error rendering is out of frozen scope C2.
- B2 (Greptile P2 on #448, pages.py:143): invalid edits re-render from the
  persisted Issue, losing other valid submitted values. Polish; out of scope.
- (Not backlog — intentional): F2 unlabeled priority select is the frozen
  documented flaw (SPEC C4, access-it signal). Fixes only inside a mission run.

Both B1/B2 are honest future mission fodder (clean-sweep finding material),
not scope drops: no acceptance criterion names them.
