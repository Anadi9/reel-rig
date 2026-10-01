#!/usr/bin/env python3
"""
Lip-sync mouth overlays for the full-body pixel character (2px cells).

For every pose × viseme this writes pixel_mouths/<pose>/<viseme>.png: a 540×560
transparent canvas (same as pixel/<pose>.png) with only the mouth cells filled, so
Remotion can stack it on top of the pose and they share every transform.

Visemes match ~/reel-rig/avatar/lipsync.py: rest a1 a2 a3 e1 e2 o1 o2.
"rest" = the pose's own drawn mouth (no overlay file).

The mouth is only ~8×4 cells at this scale, so the 8 visemes read as ~4 families:
closed · open (a1<a2<a3) · wide/teeth (e1,e2) · round (o1,o2).

Run: ~/reel-rig/openvoice/.venv/bin/python3 build_mouths.py   (after build_character.py)
"""
import json
import os
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(os.environ.get("KIT_DIR") or Path(__file__).parent)   # KIT_DIR: build another kit (e.g. v3/) with these scripts
PIX = 2
CW, CH = 540, 560

# Each pose's mouth point (canvas px) and whether it talks come from poses.json (build_character.py).
# Standing poses sit near the shared mouth point; sitting/crouching ones don't. Poses that can't
# lip-sync (mind_blown's drawn "O", back/side views, walking, hand over mouth) get no overlays.
_P = json.loads((HERE / "poses.json").read_text())
MOUTHS = {p: tuple(_P["meta"][p]["mouth"]) for p in _P["poses"]}
SKIP = {p for p in _P["poses"] if not _P["meta"][p]["talks"]}

# Shapes in cells. Row 0 of each shape sits on the upper-lip row (1 cell above centre).
#   L lip · D lip shadow · M mouth interior · T teeth · K tongue · . untouched
SHAPES = {
    "a1": [".LLLLL.",
           "LMMMMML",
           ".DLLLD."],
    "a2": [".LLLLLL.",
           "LTTTTTTL",
           "LMMMMMML",
           ".DLLLLD."],
    "a3": [".LLLLLL.",
           "LTTTTTTL",
           "LMMMMMML",
           "LMMKKMML",
           ".DLLLLD."],
    "e1": ["LLLLLLLL",
           "LTTTTTTL",
           ".DLLLLD."],
    "e2": [".LLLLLLLL.",
           "LTTTTTTTTL",
           "LMMMMMMMML",
           ".DLLLLLLD."],
    "o1": [".LLL.",
           "LMMML",
           ".DLD."],
    "o2": [".LLL.",
           "LMMML",
           "LMMML",
           ".DLD."],
}
VISEMES = ["rest", *SHAPES]

# Same mouth colours as the 128px head avatar (avatar/final/build_final_avatar.py), so the
# two read as one character. The pose palette has no lip tone of its own (lips quantised to
# skin or grey-mauve), so sampling it gave inconsistent lips from pose to pose.
LIP, LIP_DK = (194, 122, 106), (147, 71, 60)
MOUTH_IN, TEETH, TONGUE = (42, 15, 14), (239, 232, 221), (160, 82, 77)
COLS = {"L": LIP, "D": LIP_DK, "M": MOUTH_IN, "T": TEETH, "K": TONGUE}


def build():
    out_root = HERE / "pixel_mouths"
    meta = {}
    for d in out_root.glob("*"):
        if d.is_dir() and (d.name not in MOUTHS or d.name in SKIP):
            for f in d.glob("*.png"):
                f.unlink()
            d.rmdir()
    for pose, (cx, cy) in MOUTHS.items():
        meta[pose] = {"centre": [cx, cy], "overlays": pose not in SKIP}
        if pose in SKIP:
            continue
        d = out_root / pose
        d.mkdir(parents=True, exist_ok=True)
        gx, gy = cx // PIX, cy // PIX
        for name, rows in SHAPES.items():
            g = np.zeros((CH // PIX, CW // PIX, 4), np.uint8)
            w = len(rows[0])
            c0 = gx - w // 2
            for r, row in enumerate(rows):
                for c, ch in enumerate(row):
                    if ch == ".":
                        continue
                    g[gy - 1 + r, c0 + c, :3] = COLS[ch]
                    g[gy - 1 + r, c0 + c, 3] = 255
            Image.fromarray(g, "RGBA").resize((CW, CH), Image.NEAREST).save(d / f"{name}.png", optimize=True)
    (HERE / "mouths.json").write_text(json.dumps({"visemes": VISEMES, "poses": meta}, indent=1))
    print("mouth overlays:", [p for p in MOUTHS if p not in SKIP], "| skipped:", sorted(SKIP))


if __name__ == "__main__":
    build()
