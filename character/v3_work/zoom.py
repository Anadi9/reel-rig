# zoom.py sheet x0 y0 x1 y1 out [scale] — upscaled crop with sheet-coordinate ticks every 10px (labels every 50)
import sys
from PIL import Image, ImageDraw
p, x0, y0, x1, y1, out = sys.argv[1], *map(int, sys.argv[2:6]), sys.argv[6]
s = int(sys.argv[7]) if len(sys.argv) > 7 else 3
im = Image.open(p).convert("RGB").crop((x0, y0, x1, y1)).resize(((x1-x0)*s, (y1-y0)*s), Image.LANCZOS)
c = Image.new("RGB", (im.width + 40, im.height + 20), "white"); c.paste(im, (40, 20)); d = ImageDraw.Draw(c)
for x in range(x0 - x0 % 10, x1, 10):
    X = 40 + (x - x0) * s; d.line([(X, 20), (X, 20 + (12 if x % 50 == 0 else 5))], fill="red")
    if x % 50 == 0: d.text((X - 8, 4), str(x), fill="red")
for y in range(y0 - y0 % 10, y1, 10):
    Y = 20 + (y - y0) * s; d.line([(40, Y), (40 + (12 if y % 50 == 0 else 5), Y)], fill="red")
    if y % 50 == 0: d.text((2, Y - 5), str(y), fill="red")
c.save(out)
