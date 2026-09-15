# Image generator

Source of every image under `assets/` — the hero banners, the social preview, the concept
diagrams, the README and deep-dive visuals, and one developer-contract card per mission, each
diagram in a dark and a light variant. The prompts are the diagram source the same way the
mermaid blocks in the README are: edit the prompt, rerun, review the render.

```bash
OPENROUTER_API_KEY=... python3 assets/diagrams/generator/gen.py                      # everything
OPENROUTER_API_KEY=... python3 assets/diagrams/generator/gen.py --only ship-it       # one dark
OPENROUTER_API_KEY=... python3 assets/diagrams/generator/gen.py --only ship-it-light # its light variant
python3 assets/diagrams/generator/wire_docs.py .                                     # embed into the docs
```

- `specs.py` — the shared style block, the brand images, and the concept diagrams.
- `specs_missions.py` — one contract card per mission: what you give it, what it interrupts
  you for, what you get back, where it stops. The pipeline stays in each guide's mermaid block.
- `specs_new.py` — the README's you-say table, the negative-control head-to-head, the install
  stack, and the deep-dive visuals (gates, artifacts, handoffs, proof ladder, verify gate,
  mission identity).
- `specs_light.py` — derives a `-light` variant of every diagram by asking the model to recolor
  the finished dark render, so layout and text stay identical. Generate the dark id first.
- `wire_docs.py` — rewrites every embed as a light/dark `<picture>` block, inserts the new
  images at their anchors, and generates each mission card's alt text from its contract fields.
  Every anchor is checked on every run, so a renamed heading fails the rerun rather than the
  next regeneration; `tests/test_wire_docs.py` holds the committed docs to be the script's fixed
  point. It never touches ARCHITECTURE.md: that file counts toward every mission's activation load.
- Model: Nano Banana Pro (`google/gemini-3-pro-image`) via OpenRouter, 2K output, fitted and
  centre-cropped to each spec's `dims`, saved as progressive JPEG. About $0.14 per image.

Review every render before committing it. The model occasionally misspells a small label, adds
a loop arrow or icon nobody asked for, chains alternative terminals in sequence, or repeats a
title as a subtitle; the prompts already carry the guard phrases that stopped each of those, and
the recolor prompt forbids new text after hex codes once leaked into a card. Keep labels short
and spell out exact text when you add a diagram.

The key is read from the environment only. It is never written into this tree.
