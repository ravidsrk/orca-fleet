LIGHT_EDIT = """Recolor this diagram into a LIGHT theme. Keep every shape, box, arrow, icon and position exactly where it is, and keep every character of every label exactly as it is. Change colours only; add nothing — no new borders, strokes, underlines, badges or decorations of any kind.
Background: near-white (#F5F8FF). Node fills: white, with 2px blue (#2F6FEB) outlines and a very soft pale-blue glow. Primary text: dark navy (#0B1220). Secondary captions: grey-blue (#4F5E78). Where the input already uses green, red or amber for an element, keep that element the same hue, slightly darker for contrast on white (#1F9D55, #D93B3B, #C77700); elements that are blue or white in the input stay blue or navy; elements that are grey or dimmed in the input stay grey and dimmed. Copy every word, including the smallest captions, letter for letter, with the same capitalisation — check spelling against the input. Never write colour codes, hex values, or any text that is not already in the input into the image. The faint corner constellation lines: pale blue. The orca signature mark: dark navy. Same aspect ratio as the input."""

def light_variants(specs, ids=None):
    out = []
    for s in specs:
        if s["id"] in ("hero-dark", "hero-light", "social-preview"):
            continue
        if ids and s["id"] not in ids:
            continue
        out.append({"id": s["id"] + "-light", "out": s["out"].replace(".jpg", "-light.jpg"),
                    "aspect": s["aspect"], "dims": s["dims"], "from": s["out"], "prompt": LIGHT_EDIT})
    return out
