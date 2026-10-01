#!/usr/bin/env python3
"""Review board for build_mouths.py: every pose × viseme, face zoomed (mouth_board.png)."""
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).parent
meta = json.loads((HERE / "mouths.json").read_text())
V = meta["visemes"]
Z, S = 5, 44
f = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 18)
poses = list(meta["poses"])
board = Image.new("RGB", (130 + len(V) * S * Z, 40 + len(poses) * S * Z), (12, 12, 14))
d = ImageDraw.Draw(board)
for j, v in enumerate(V):
    d.text((130 + j * S * Z + 8, 10), v, fill=(212, 255, 58), font=f)
for i, p in enumerate(poses):
    cx, cy = meta["poses"][p]["centre"]
    base = Image.open(HERE / "pixel" / f"{p}.png").convert("RGBA")
    d.text((8, 40 + i * S * Z + 8), p, fill=(230, 230, 230), font=f)
    for j, v in enumerate(V):
        im = base.copy()
        ov = HERE / "pixel_mouths" / p / f"{v}.png"
        if v != "rest" and ov.exists():
            im.alpha_composite(Image.open(ov))
        crop = im.crop((cx - S // 2, cy - S // 2 - 6, cx + S // 2, cy + S // 2 - 6)).resize((S * Z, S * Z), Image.NEAREST)
        bg = Image.new("RGB", crop.size, (12, 12, 14)); bg.paste(crop, (0, 0), crop)
        board.paste(bg, (130 + j * S * Z, 40 + i * S * Z))
board.save(HERE / "mouth_board.png")
print("wrote mouth_board.png", board.size)
