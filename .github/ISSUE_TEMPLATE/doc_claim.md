---
name: A documented claim is false or stale
about: A number, a version, a tier, or a mechanics claim in the docs does not match the tree or the Orca binary
title: "docs: "
labels: ["documentation"]
assignees: ""
---

## The claim

<!-- Quote it, with file:line. -->

## What is actually true

<!-- The command or file that shows it (for an Orca mechanics claim: the receipt from
`orca <verb> --json`, `orca agent-context --json`, or the upstream source path and version). -->

## Which mechanism should have caught it

<!-- A generator (`scripts/gen-badges.py`), a lint in `scripts/validate.py`, a contract test under
`tests/`, or the pin-it re-witness. If none exists, say so: that is the finding. -->
