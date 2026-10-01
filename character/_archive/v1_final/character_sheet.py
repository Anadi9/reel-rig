#!/usr/bin/env python3
"""Reference sheet of the final character: all 12 poses (2px pixel), labelled → character_sheet.png"""
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).parent
poses = json.loads((HERE / "poses.json").read_text())["poses"]
f = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 26)
W, H, COLS = 540, 560, 6
sheet = Image.new("RGB", (COLS * W // 2 * 2, 2 * (H + 50)), (11, 11, 12))
d = ImageDraw.Draw(sheet)
for i, p in enumerate(poses):
    x, y = (i % COLS) * W, (i // COLS) * (H + 50)
    sheet.paste(Image.open(HERE / "pixel" / f"{p}.png"), (x, y + 40), Image.open(HERE / "pixel" / f"{p}.png"))
    d.text((x + W // 2, y + 12), p.replace("_", " "), fill=(212, 255, 58), font=f, anchor="mt")
sheet.save(HERE / "character_sheet.png")
print("wrote character_sheet.png", sheet.size)
