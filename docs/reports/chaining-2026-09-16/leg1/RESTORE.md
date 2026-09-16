# Restore the leg-1 target from the bundle (no original repo needed)

`target-417.bundle` is a `git bundle` of the full leg-1 history
(`chain417/leg1-cleansweep-base`, seed `892eae2` … tip `c5e807c`, 9 commits).
It preserves every cited SHA; `seed-*` + `full-diff.txt` preserve file bytes
only. Verify the bundle's sha256 against `integrity-inventory.txt` first.

```sh
git clone target-417.bundle chaining-target-417 && cd chaining-target-417
git checkout c5e807cf4e05004f338d2c1a722c4000d888334e   # leg-1 tip
uv run --with pytest --no-project python -m pytest test_notes.py -q  # expect 6 passed
git diff 892eae208b01780a426deecdf9e81380753b30cc \
         c5e807cf4e05004f338d2c1a722c4000d888334e | sha256sum
# expect b5d9e400d12cb661200bd24e0927bd223153185f50fdb208dcc0f38b12d8c3f7 (== full-diff.txt)
```

(The `remote HEAD refers to nonexistent ref` warning on clone is cosmetic —
the bundle carries a branch, not a HEAD. The explicit checkout above is the
supported path.)
