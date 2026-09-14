#!/usr/bin/env python3
"""Regenerate this repository's images with Nano Banana Pro through OpenRouter.

    OPENROUTER_API_KEY=... python3 assets/diagrams/generator/gen.py                 # everything
    OPENROUTER_API_KEY=... python3 assets/diagrams/generator/gen.py --only mission-map,ship-it

Prompts live next to this file: specs.py (concept diagrams + brand images), specs_missions.py
(one developer-contract card per mission), specs_new.py (the README and deep-dive visuals) and
specs_light.py, which derives a "-light" variant of every diagram by asking the model to recolor
the finished dark render, so layout and text stay identical. Generate the dark ids first; a light
id reads its dark JPEG from the repo. Each spec names its output path, the
aspect ratio requested from the model, and the final pixel size; the returned PNG is scaled to
cover that size, centre-cropped, and written as a progressive JPEG at the repo path.

Raw PNGs are kept under --raw-dir (a temp dir by default) so an interrupted run resumes with
the finished images skipped; pass --force to redo them. Model: google/gemini-3-pro-image
(override with IMAGE_MODEL). At the 2K size one image costs roughly $0.14.

The API key is read from the environment only. Never write it into this tree.
"""
import argparse
import base64
import concurrent.futures as cf
import io
import json
import os
import pathlib
import sys
import tempfile
import time
import urllib.error
import urllib.request

from PIL import Image

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import specs  # noqa: E402

API = "https://openrouter.ai/api/v1/chat/completions"
MODEL = os.environ.get("IMAGE_MODEL", "google/gemini-3-pro-image")
REPO = HERE.parents[2]


def call(prompt, aspect, size, timeout=420, image_bytes=None, mime="image/jpeg"):
    """One generation. With image_bytes the model edits that image (used for the light variants)."""
    content = prompt
    if image_bytes is not None:
        content = [{"type": "text", "text": prompt},
                   {"type": "image_url", "image_url": {"url": f"data:{mime};base64," + base64.b64encode(image_bytes).decode()}}]
    body = {
        "model": MODEL,
        "messages": [{"role": "user", "content": content}],
        "modalities": ["image", "text"],
        "image_config": {"aspect_ratio": aspect, "image_size": size},
    }
    req = urllib.request.Request(API, data=json.dumps(body).encode(), headers={
        "Authorization": "Bearer " + os.environ["OPENROUTER_API_KEY"],
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/ravidsrk/orca-fleet",
        "X-Title": "orca-fleet image regen",
    })
    with urllib.request.urlopen(req, timeout=timeout) as r:
        data = json.load(r)
    if "error" in data:
        raise RuntimeError("api error: " + json.dumps(data["error"])[:600])
    msg = data["choices"][0]["message"]
    imgs = msg.get("images") or []
    if not imgs:
        raise RuntimeError("no image in response: " + json.dumps(data)[:600])
    url = imgs[0]["image_url"]["url"]
    return base64.b64decode(url.split(",", 1)[1]), data.get("usage")


def fit(img, w, h):
    """Scale to cover (w, h) then centre-crop; never stretch."""
    img = img.convert("RGB")
    scale = max(w / img.width, h / img.height)
    nw, nh = round(img.width * scale), round(img.height * scale)
    img = img.resize((nw, nh), Image.LANCZOS)
    left, top = (nw - w) // 2, (nh - h) // 2
    return img.crop((left, top, left + w, top + h))


def one(spec, size, raw_dir, force, attempts=3):
    sid = spec["id"]
    raw_path = raw_dir / f"{sid}.png"
    out_path = REPO / spec["out"]
    if raw_path.exists() and not force:
        return {"id": sid, "status": "cached", "raw": str(raw_path)}
    err = None
    for i in range(attempts):
        t0 = time.time()
        try:
            src = spec.get("from")  # light variants recolor the finished dark render
            raw, usage = call(spec["prompt"], spec["aspect"], spec.get("size", size),
                              image_bytes=(REPO / src).read_bytes() if src else None)
            raw_path.write_bytes(raw)
            img = Image.open(io.BytesIO(raw))
            w, h = spec["dims"]
            out_path.parent.mkdir(parents=True, exist_ok=True)
            fit(img, w, h).save(out_path, "JPEG", quality=spec.get("q", 86), optimize=True,
                                progressive=True, subsampling=0)
            return {"id": sid, "status": "ok", "raw_size": f"{img.width}x{img.height}",
                    "out": str(out_path.relative_to(REPO)), "bytes": out_path.stat().st_size,
                    "secs": round(time.time() - t0, 1), "cost": (usage or {}).get("cost")}
        except urllib.error.HTTPError as e:
            err = f"HTTP {e.code}: {e.read()[:400]!r}"
        except Exception as e:  # noqa: BLE001 — every failure is retried, then reported
            err = repr(e)[:600]
        time.sleep(8 * (i + 1))
    return {"id": sid, "status": "failed", "error": err}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--only", default="", help="comma-separated spec ids (default: all)")
    ap.add_argument("--size", default="2K", help="model image_size: 1K, 2K or 4K")
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--force", action="store_true", help="regenerate even when a raw PNG exists")
    ap.add_argument("--raw-dir", default=os.path.join(tempfile.gettempdir(), "orca-fleet-image-raw"))
    a = ap.parse_args()
    if not os.environ.get("OPENROUTER_API_KEY"):
        sys.exit("OPENROUTER_API_KEY is not set")
    raw_dir = pathlib.Path(a.raw_dir)
    raw_dir.mkdir(parents=True, exist_ok=True)
    wanted = set(filter(None, a.only.split(",")))
    todo = [s for s in specs.SPECS if not wanted or s["id"] in wanted]
    missing = wanted - {s["id"] for s in todo}
    if missing:
        sys.exit(f"unknown ids: {sorted(missing)}")
    results = []
    with cf.ThreadPoolExecutor(max_workers=a.workers) as ex:
        for res in ex.map(lambda s: one(s, a.size, raw_dir, a.force), todo):
            results.append(res)
            print(json.dumps(res), flush=True)
    bad = [r for r in results if r["status"] == "failed"]
    print(f"\n{len(results) - len(bad)} ok, {len(bad)} failed; raw PNGs in {raw_dir}")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
