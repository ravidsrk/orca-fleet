# Human actions

Things only Ravindra can do (R15). Agent will verify after you confirm.

| id | instruction | unblocks | gates launch | verification | status |
|---|---|---|---|---|---|
| **H-01** | Start the Orca app on this machine (`orca open` or the GUI). Confirm `orca status --json` shows `runtime.reachable: true`. In a repo with an open PR or a feature branch, run the getting-started **review-it dry run** ("review this PR: is it ready to merge?") and save the verdict. | T-08 / CF-05 happy path | **yes** | Agent re-runs `orca status --json` and attaches the review-it report path under `docs/completion/evidence/CF-05-happy-review-it.txt`. | done |
| **H-02** | Work the remaining `docs/distribution.md` checklist: submit to anthropics/claude-plugins-official and aggregators that do not scrape GitHub (claudemarketplace.net; get this catalog onto skills.sh — the predecessor `autonomous-fleet` is still the hit); replace the stale buildwithclaude blurb; confirm a does-it-load score when one exists; lead listings with the `proof:` framing. | — (G-07 agent slice closed; this is the leftover human work) | no | Agent checks the boxes can be flipped with URLs in `docs/distribution.md`. Index check 2026-09-01 recorded there. | open |
| **H-03** | Cut a version after this completion train (0.5.0 → next): bump `.claude-plugin/plugin.json` + marketplace.json, move CHANGELOG Unreleased → a dated section. | — (G-06 closed) | no | `plugin.json` version equals latest CHANGELOG heading; badges still generate. | done |

*(Run 1.)* H-01 was the only launch gate. Do not start Orca for the agent unless you intend to; the failure path is already evidenced.

## Run 2 (2026-09-02)

**H-07 gates launch** (fresh-reviewer RV-01): it repeats the frozen gate's own item-8 action — the review-it dry run — on a head whose `review-it` skill changed in #225. H-04, H-05, H-06 do not gate.

| id | instruction | unblocks | gates launch | verification | status |
|---|---|---|---|---|---|
| **H-04** | Edit the GitHub repository **About** description: it still reads "10 outcome-named autonomous fleets for the Orca runtime …"; the catalog is 13 (README badge + table). Fix any external listing copy that repeats "10". | G-15 | no | Agent re-reads the repository description through the GitHub API and files it as `evidence/H-04-repo-description.txt`. | open |
| **H-05** | After this run's PR merges, cut the next version (0.6.0 → 0.6.1): bump `.claude-plugin/plugin.json` + `marketplace.json`, move CHANGELOG `[Unreleased]` under a dated heading, regenerate badges. | G-17 | no | `plugin.json` version equals the latest **dated** CHANGELOG heading; `python3 scripts/gen-badges.py --check` exit 0. | open |
| **H-06** | Merge the `alert-on-failure` workflow (T-10, #213). Then either click Actions → `alert-on-failure` → Run workflow, or let the agent dispatch it (T-11): the run files and closes a `[drill]` issue labeled `ci-failure`, which proves the alert path without redding `main`. Enabling failure-only Actions notifications on your account is now optional belt-and-braces. | T-11 → G-10; turns A-13 from a waiver into a demonstration | no | `evidence/T-11-alert-drill.txt` (run url + issue url); the A-13 waiver is then moot (the frozen text is not edited). | open |
| **H-07** | With the Orca app running, re-run the getting-started **review-it dry run** against current `main` (the `review-it` skill text changed in #225: read-only worker profile, human-authorized verdict posting) — on a PR the reviewing session did **not** author, so read-only workers are actually dispatched (run 1's evidence was a coordinator self-review of its own PR #208). | G-16 / CF-05 | **yes** | Agent attaches the report as `evidence/CF-05-r3-happy-review-it.txt` with the reviewed SHA and the worker-dispatch record, closes G-16, and re-evaluates the gate. | open |
