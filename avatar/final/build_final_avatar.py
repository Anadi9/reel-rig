#!/usr/bin/env python3
"""
Final avatar: the approved AI portrait (Canva, 1264px, hood + hex shades) as
pixel art, with hand-placed animation overlays so it can talk and react.

Pipeline: edge-preserving smoothing at full resolution → reduce to an N×N grid
→ snap to a ~44-colour palette (median-cut + locked silver / lime accents) →
remove isolated specks → redraw the octagon frames crisply → overlays.

All feature positions are measured in the portrait's 800×800 space, so the grid
size can change (N) and everything still lines up.

Variations are palette swaps of the SAME grid (every variation animates):
    natural (recommended) · retro16 · lime

Run: ~/reel-rig/openvoice/.venv/bin/python3 build_final_avatar.py [N]
Writes avatar_final.json (PixelAvatar format) + PNGs next to this file.
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter

HERE = Path(__file__).parent
SRC = HERE / "source_ai_portrait_full.jpg"
N = int(sys.argv[1]) if len(sys.argv) > 1 else 128
S = N / 800  # portrait 800-space → grid

LIME, SILVER, SILVER_SH = "#D4FF3A", "#D2D6DB", "#8E939A"
MOUTH, TEETH, TONGUE, LIP, LIP_DK = "#2A0F0E", "#EFE8DD", "#A0524D", "#C27A6A", "#93473C"
LASH = "#140C0A"
ACCENTS = [LIME, "#A9CC34", SILVER, SILVER_SH]

hexc = lambda rgb: "#%02X%02X%02X" % tuple(int(v) for v in rgb)
rgbc = lambda h: tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))

# ── measured features (800-space) ──
LENS_L = [(272, 279), (347, 280), (368, 299), (366, 347), (343, 364), (275, 364), (256, 346), (250, 302)]
LENS_R = [(428, 280), (500, 281), (521, 296), (518, 346), (500, 365), (435, 365), (418, 350), (412, 304)]
BRIDGE_Y, BRIDGE_X = 302, (368, 412)
EYES = [(320, 320), (481, 320)]
BROW_BOXES = {"l": (262, 372, 248, 277), "r": (404, 520, 248, 277)}  # x0, x1, y0, y1
LIP_BOX = (334, 434, 414, 474)                                      # x0, x1, y0, y1


def cells(x0, x1, y0, y1):
    """Grid cells whose centres fall inside an 800-space rectangle."""
    return [(r, c) for r in range(N) for c in range(N)
            if x0 <= (c + 0.5) / S < x1 and y0 <= (r + 0.5) / S < y1]


def edge_cells(pts):
    out = set()
    for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1]):
        for t in np.linspace(0, 1, 120):
            out.add((int((y0 + (y1 - y0) * t) * S), int((x0 + (x1 - x0) * t) * S)))
    return out


# ── reduce ──
src = Image.open(SRC).convert("RGB")
smooth = src.filter(ImageFilter.MedianFilter(5)).filter(ImageFilter.MedianFilter(3))
smooth = ImageEnhance.Contrast(smooth).enhance(1.06)
small = smooth.resize((N, N), Image.LANCZOS)
base_q = small.quantize(colors=40, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
pal = list(base_q.getpalette()[:40 * 3])
for h in ACCENTS:
    pal += list(rgbc(h))
pimg = Image.new("P", (1, 1)); pimg.putpalette(pal + [0] * (768 - len(pal)))
grid = np.array(small.quantize(palette=pimg, dither=Image.Dither.NONE).convert("RGB"))
G = [[hexc(grid[r, c]) for c in range(N)] for r in range(N)]

for _ in range(2):  # remove isolated specks
    H2 = [row[:] for row in G]
    for r in range(1, N - 1):
        for c in range(1, N - 1):
            nb = [G[r - 1][c], G[r + 1][c], G[r][c - 1], G[r][c + 1]]
            if G[r][c] not in nb:
                best = max(set(nb), key=nb.count)
                if nb.count(best) >= 3:
                    H2[r][c] = best
    G = H2

# lime rim: snap anything clearly lime in the smoothed source to the exact accent
raw = np.array(small).astype(int)
for r in range(N):
    for c in range(N // 2, N):
        R0, G0, B0 = raw[r, c]
        if G0 > 70 and G0 > R0 * 1.08 and G0 > B0 * 1.5:
            G[r][c] = LIME

# crisp frames: silver upper edges, darker lower edges, silver bridge
for lens in (LENS_L, LENS_R):
    top = min(y for _, y in lens)
    for r, c in edge_cells(lens):
        G[r][c] = SILVER if r <= int((top + 30) * S) else SILVER_SH
for c in range(int(BRIDGE_X[0] * S), int(BRIDGE_X[1] * S) + 1):
    G[int(BRIDGE_Y * S)][c] = SILVER

# ── animation overlays ──
lx0, lx1, ly0, ly1 = LIP_BOX
beard = G[int(488 * S)][int(384 * S)]


def rect(m, x0, x1, y0, y1, col):
    for rc in cells(x0, x1, y0, y1):
        m[rc] = col


def ell(m, cx, cy, rx, ry, col):
    """Grid cells whose centres fall inside an 800-space ellipse."""
    for r in range(int((cy - ry) * S) - 1, int((cy + ry) * S) + 2):
        for c in range(int((cx - rx) * S) - 1, int((cx + rx) * S) + 2):
            x, y = (c + 0.5) / S, (r + 0.5) / S
            if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1:
                m[(r, c)] = col


def curve(m, pts, col, thick=5):
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        for t in np.linspace(0, 1, 40):
            ell(m, x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, thick, thick * 0.8, col)


MX, MY = 384, 438   # mouth centre (800-space)


def mouth(shape):
    if shape == "closed":
        return {}
    # clear only the lip-coloured pixels, refilling each from the beard just below it
    m = {}
    for r, c in cells(lx0, lx1, ly0, ly1):
        R, Gc, B = rgbc(G[r][c])
        if R > 95 and R > Gc * 1.12:
            below = next((G[rr][c] for rr in range(r + 1, min(N, r + 12))
                          if (lambda q: not (q[0] > 95 and q[0] > q[1] * 1.12))(rgbc(G[rr][c]))), beard)
            m[(r, c)] = below
    if shape == "clear":
        return m
    if shape == "small":
        ell(m, MX, MY + 11, 30, 8, LIP); ell(m, MX, MY - 8, 27, 4.5, LIP)
        ell(m, MX, MY, 25, 7, MOUTH)
    elif shape == "open":
        ell(m, MX, MY + 4, 36, 22, LIP); ell(m, MX, MY + 3, 30, 16, MOUTH)
        rect(m, MX - 22, MX + 22, MY - 12, MY - 6, TEETH); ell(m, MX, MY + 13, 15, 5, TONGUE)
    elif shape == "o":
        ell(m, MX, MY + 4, 20, 22, LIP); ell(m, MX, MY + 4, 13, 15, MOUTH)
    elif shape == "smirk":
        curve(m, [(MX - 30, MY + 12), (MX, MY + 11), (MX + 34, MY + 2)], LIP, 6)
        curve(m, [(MX - 34, MY + 4), (MX, MY + 4), (MX + 36, MY - 6)], MOUTH, 3)
    return m


def viseme(kind, level):
    """Speech mouth shapes. kind: a (open "ah"), e (wide "ee"), o (round "oo").
    Levels grow the opening so the mouth can ease open/closed through in-betweens."""
    m = mouth("clear")
    if kind == "a":                                    # levels 1-3
        rx, ry = 23 + 5 * level, 3 + 6.5 * level
        ell(m, MX, MY - ry * 0.55 - 3, rx - 2, 4.5, LIP_DK)        # upper lip
        ell(m, MX, MY + ry * 0.75 + 5, rx + 2, 5 + level, LIP)      # lower lip
        ell(m, MX, MY + 1, rx, ry, MOUTH)
        if level >= 2:
            teeth = {}
            ell(teeth, MX, MY + 1, rx - 1, ry - 1, TEETH)
            for (r, c), col in teeth.items():
                if (r + 0.5) / S < MY + 1 - ry + min(8, ry * 0.5):
                    m[(r, c)] = col
        if level >= 3:
            ell(m, MX, MY + ry * 0.55, rx * 0.5, ry * 0.32, TONGUE)
    elif kind == "e":                                  # levels 1-2
        rx, ry = 34 + 4 * level, 3 + 3 * level
        ell(m, MX, MY + ry + 3, rx - 2, 4, LIP)
        ell(m, MX, MY - ry - 1, rx - 4, 3.5, LIP_DK)
        ell(m, MX, MY + 1, rx, ry, MOUTH)
        teeth = {}
        ell(teeth, MX, MY + 1, rx - 2, ry - 0.5, TEETH)
        for (r, c), col in teeth.items():
            if (r + 0.5) / S < MY + 2:
                m[(r, c)] = col
    elif kind == "o":                                  # levels 1-2
        rx, ry = 10 + 4 * level, 7 + 5 * level
        ell(m, MX, MY + 2, rx + 13, ry + 11, LIP)                 # full, pushed-out lips
        ell(m, MX, MY - ry - 3, rx + 9, 5, LIP_DK)                # upper-lip shadow
        ell(m, MX, MY + 3, rx, ry, MOUTH)
    return m


def brows(sides=("l", "r"), lift=16):
    """Lift the dark brow pixels by ~2% of the face; fill the vacated rows with forehead skin."""
    m = {}
    dr = max(1, round(lift * S))
    for s in sides:
        x0, x1, y0, y1 = BROW_BOXES[s]
        box = cells(x0, x1, y0, y1)
        for r, c in box:
            m[(r, c)] = G[int((y0 - 10) * S)][c]
        for r, c in box:
            if sum(rgbc(G[r][c])) < 200:
                m[(r - dr, c)] = G[r][c]
    return m


def blink():
    m = {}
    for ex, ey in EYES:
        lens_dark = G[int((ey - 18) * S)][int(ex * S)]
        for rc in cells(ex - 34, ex + 34, ey - 16, ey + 14):
            m[rc] = lens_dark
        for rc in cells(ex - 30, ex + 30, ey + 2, ey + 8):
            m[rc] = LASH
    return m


overlay_cells = {
    "mouth_closed": {}, "mouth_small": mouth("small"), "mouth_open": mouth("open"),
    "mouth_o": mouth("o"), "mouth_smirk": mouth("smirk"),
    "brow_raised": brows(), "brow_one": brows(("r",)), "blink": blink(),
    **{f"v_a{l}": viseme("a", l) for l in (1, 2, 3)},
    **{f"v_e{l}": viseme("e", l) for l in (1, 2)},
    **{f"v_o{l}": viseme("o", l) for l in (1, 2)},
}

# ── encode (PixelAvatar format) ──
all_cols = sorted({v for row in G for v in row} | {v for o in overlay_cells.values() for v in o.values()} | {LIME})
keys = [chr(c) for c in range(33, 127) if chr(c) not in "\"\\'`."]
pal_map = {keys[i]: col for i, col in enumerate(all_cols)}
inv = {v: k for k, v in pal_map.items()}
base = ["".join(inv[G[r][c]] for c in range(N)) for r in range(N)]
ov = {name: [[r, c, inv[col]] for (r, c), col in cs.items()] for name, cs in overlay_cells.items()}


def lum(h):
    r, g, b = rgbc(h)
    return 0.299 * r + 0.587 * g + 0.114 * b


def retro16(p):
    cols = list(p.values())
    img = Image.new("RGB", (len(cols), 1)); img.putdata([rgbc(c) for c in cols])
    q = img.quantize(colors=16, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).convert("RGB")
    out = {k: hexc(q.getpixel((i, 0))) for i, k in enumerate(p)}
    for k, v in p.items():
        if v in (LIME, SILVER):
            out[k] = v
    return out


def lime_mono(p):
    ramp = ["#07080A", "#10150B", "#1C2A10", "#2F4814", "#4A7018", "#6E9E22", "#98CC2C", "#D4FF3A", "#F1FFC4"]
    return {k: ramp[min(len(ramp) - 1, int(min(1, lum(v) / 215) * (len(ramp) - 1) + 0.5))] for k, v in p.items()}


palettes = {"natural": pal_map, "retro16": retro16(pal_map), "lime": lime_mono(pal_map)}
(HERE / "avatar_final.json").write_text(json.dumps({"w": N, "h": N, "palettes": palettes, "base": base, "overlays": ov}))
print(f"N={N}, {len(pal_map)} colours; overlays:", {k: len(v) for k, v in ov.items()})


def render(pname, states=(), px=None):
    g = [list(r) for r in base]
    for s in states:
        for r, c, k in ov[s]:
            g[r][c] = k
    p = palettes[pname]
    img = Image.fromarray(np.array([[rgbc(p[k]) for k in row] for row in g], np.uint8))
    return img.resize((N * px, N * px), Image.NEAREST) if px else img


scale = max(1, 1024 // N)
for name in palettes:
    render(name, px=scale).save(HERE / f"avatar_{name}.png")
    order = [(), ("mouth_small",), ("mouth_open",), ("mouth_o",), ("mouth_smirk", "brow_one"), ("blink",)]
    sp = max(1, 400 // N)
    sheet = Image.new("RGB", (len(order) * (N * sp + 8), N * sp), (10, 10, 11))
    for i, st in enumerate(order):
        sheet.paste(render(name, st, sp), (i * (N * sp + 8), 0))
    sheet.save(HERE / f"avatar_{name}_states.png")

# speech-shape sheet (natural)
vis = [(), ("v_a1",), ("v_a2",), ("v_a3",), ("v_e1",), ("v_e2",), ("v_o1",), ("v_o2",)]
sp = max(1, 400 // N)
sheet = Image.new("RGB", (len(vis) * (N * sp + 8), N * sp), (10, 10, 11))
for i, st in enumerate(vis):
    sheet.paste(render("natural", st, sp), (i * (N * sp + 8), 0))
sheet.save(HERE / "avatar_natural_visemes.png")
