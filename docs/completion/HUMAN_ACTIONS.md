# Human actions

Things only Ravindra can do (R15). Agent will verify after you confirm.

| id | instruction | unblocks | gates launch | verification | status |
|---|---|---|---|---|---|
| **H-01** | Start the Orca app on this machine (`orca open` or the GUI). Confirm `orca status --json` shows `runtime.reachable: true`. In a repo with an open PR or a feature branch, run the getting-started **review-it dry run** ("review this PR: is it ready to merge?") and save the verdict. | T-08 / CF-05 happy path | **yes** | Agent re-runs `orca status --json` and attaches the review-it report path under `docs/completion/evidence/CF-05-happy-review-it.txt`. | open |
| **H-02** | Work the `docs/distribution.md` checklist: submit to community plugin marketplace aggregators; confirm a green does-it-load score on skills indexers; lead listings with the `proof:` framing. | G-07 | no | Agent checks the boxes can be flipped with URLs in `docs/distribution.md`. | open |
| **H-03** | Cut a version after this completion train (0.5.0 → next): bump `.claude-plugin/plugin.json` + marketplace.json, move CHANGELOG Unreleased → a dated section. | G-06 | no | `plugin.json` version equals latest CHANGELOG heading; badges still generate. | open |

H-01 is the only launch gate. Do not start Orca for the agent unless you intend to; the failure path is already evidenced.
