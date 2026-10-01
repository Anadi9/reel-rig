#!/usr/bin/env python3
"""Old-vs-new board for poses whose v1 art is replaced by v2 (and talk vs present) → replace_board.png"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).parent
V1 = HERE / "_archive/v1_final/pixel"
PAIRS = [("laptop", "laptop"), ("phone", "phone"), ("facepalm", "facepalm"), ("thumbs_up", "thumbs_up"),
         ("shrug", "shrug"), ("talk", "present")]
f = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 26)
W, H = 540, 560
board = Image.new("RGB", (len(PAIRS) * W, 2 * H + 110), (11, 11, 12))
d = ImageDraw.Draw(board)
for i, (old, new) in enumerate(PAIRS):
    x = i * W
    a = Image.open(V1 / f"{old}.png"); b = Image.open(HERE / "pixel" / f"{new}.png")
    board.paste(a, (x, 50), a); board.paste(b, (x, H + 100), b)
    d.text((x + W // 2, 14), f"v1 {old}", fill=(150, 150, 156), font=f, anchor="mt")
    d.text((x + W // 2, H + 64), f"v2 {new}", fill=(212, 255, 58), font=f, anchor="mt")
board.save(HERE / "replace_board.png")
print("wrote replace_board.png", board.size)
