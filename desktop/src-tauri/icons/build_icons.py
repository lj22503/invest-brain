#!/usr/bin/env python3
"""Build InvestBrain app icon set.

Strategy: rasterize the vector master ONCE at high resolution via Edge headless
(trying 1024 -> 512 -> 256 until one succeeds), then downscale with Pillow to all
required sizes and let Pillow pack the multi-resolution .ico. This avoids Edge's
size-specific hangs when rendering many small sizes directly.
"""
import os, struct, subprocess, tempfile, shutil

EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
ICONS_DIR = os.path.dirname(os.path.abspath(__file__))
SVG = os.path.join(ICONS_DIR, "icon-master.svg")
TMP = tempfile.mkdtemp(prefix="ib_icon_")

PY = r"C:\Users\lj225\.workbuddy\binaries\python\envs\default\Scripts\python.exe"
PIL_SNIP = """
from PIL import Image
import sys
src, out, kind = sys.argv[1], sys.argv[2], sys.argv[3]
im = Image.open(src).convert("RGB")
if kind == "master":
    im = im.resize((1024, 1024), Image.LANCZOS)
    im.save(out)
elif kind == "png":
    s = int(sys.argv[4])
    im.resize((s, s), Image.LANCZOS).save(out)
elif kind == "ico":
    sizes = [(16,16),(24,24),(32,32),(48,48),(64,64),(128,128),(256,256)]
    im.save(out, format="ICO", sizes=sizes)
"""

ICO_SIZES = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
TAURI_PNGS = {32: "32x32.png", 128: "128x128.png", 256: "128x128@2x.png"}
TRY_BASE = [1024, 512, 256]

HTML_TMPL = """<!doctype html><html><head><meta charset="utf-8">
<style>html,body{{margin:0;padding:0;width:{s}px;height:{s}px;overflow:hidden;background:transparent}}
img{{display:block;width:{s}px;height:{s}px}}</style></head>
<body><img src="{svg}"></body></html>"""


def render(size, out_png):
    page = os.path.join(TMP, "page_%d.html" % size)
    with open(page, "w", encoding="utf-8") as f:
        f.write(HTML_TMPL.format(s=size, svg=SVG))
    last = None
    for attempt in range(4):
        ud = os.path.join(TMP, "ud_%d_%d" % (size, attempt))
        if os.path.exists(out_png):
            os.remove(out_png)
        try:
            subprocess.run(
                [EDGE, "--headless=old", "--no-sandbox", "--disable-gpu",
                 "--disable-dev-shm-usage", "--hide-scrollbars",
                 "--no-first-run", "--no-default-browser-check",
                 "--user-data-dir=" + ud,
                 "--window-size=%d,%d" % (size, size),
                 "--screenshot=" + out_png, page],
                check=True, capture_output=True, timeout=60,
            )
        except Exception as e:
            last = e
            shutil.rmtree(ud, ignore_errors=True)
            continue
        if os.path.exists(out_png) and os.path.getsize(out_png) > 0:
            return True
    print("  (skipped %dx%d: %r)" % (size, size, last))
    return False


def main():
    print("Temp dir:", TMP)
    # 1) get a high-res base via Edge
    base_png = None
    base_size = None
    for s in TRY_BASE:
        out = os.path.join(TMP, "base_%d.png" % s)
        print("Rendering base %dx%d ..." % (s, s))
        if render(s, out):
            base_png, base_size = out, s
            break
    if base_png is None:
        raise RuntimeError("Could not render any base size with Edge")

    # 2) Pillow post-processing
    snip = os.path.join(TMP, "pil.py")
    with open(snip, "w") as f:
        f.write(PIL_SNIP)

    def pil(kind, out, extra=None):
        args = [PY, snip, base_png, out, kind]
        if extra is not None:
            args.append(str(extra))
        subprocess.run(args, check=True)

    # icon.png master (1024)
    master = os.path.join(ICONS_DIR, "icon.png")
    pil("master", master)
    print("Wrote icon.png (1024, base was %dx%d)" % (base_size, base_size))

    # Tauri companion PNGs
    for s, name in TAURI_PNGS.items():
        pil("png", os.path.join(ICONS_DIR, name), s)
        print("Wrote %s" % name)

    # icon.ico (multi-res)
    pil("ico", os.path.join(ICONS_DIR, "icon.ico"))
    print("Wrote icon.ico (%d resolutions)" % len(ICO_SIZES))

    shutil.rmtree(TMP, ignore_errors=True)
    print("Done.")


if __name__ == "__main__":
    main()
