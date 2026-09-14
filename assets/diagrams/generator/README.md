# Image generator

Source of every image under `assets/` — the hero banners, the social preview, the concept
diagrams, and one state-machine diagram per mission. The prompts are the diagram source the same
way the mermaid blocks in the README are; edit the prompt, rerun, review the render.

```bash
OPENROUTER_API_KEY=... python3 assets/diagrams/generator/gen.py                     # all 38
OPENROUTER_API_KEY=... python3 assets/diagrams/generator/gen.py --only mission-map  # one
```

- `specs.py` — the shared style block, the brand images, and the concept diagrams.
- `specs_missions.py` — one spec per mission, generated from the mission guide's pipeline.
- Model: Nano Banana Pro (`google/gemini-3-pro-image`) via OpenRouter, 2K output, fitted and
  centre-cropped to each spec's `dims`, saved as progressive JPEG. About $0.14 per image.

Review every render before committing it: the model occasionally misspells a long label, adds a
loop arrow nobody asked for, or puts a person icon on a phase that has no human gate. The
prompts already state "no loops" / "the only person icon is …" where those slips happened; keep
labels short and spell out exact text when you add a diagram.

The key is read from the environment only. It is never written into this tree.
