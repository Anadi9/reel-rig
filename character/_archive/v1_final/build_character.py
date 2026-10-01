#!/usr/bin/env python3
"""
Full-body character kit from the two Canva pose sheets (1536×1024, 3×2 each).

  1. cut each figure out of the flat grey background (flood from the sheet edges,
     so white trousers/sneakers inside the silhouette are kept)
  2. align all 12 poses on one canvas: feet on the same baseline, and each pose scaled
     slightly about the feet so the mouth lands on the same point — so swapping poses
     in a reel doesn't make the head jump
  3. export two styles:
       illustrated/<pose>.png   smooth cut-outs (the art as generated)
       pixel/<pose>.png         THE FINAL STYLE: 2px cells (270×280 grid), shared palette,
                                selective outline, lime rim on dark right edges

Run via ./build.sh (also builds the mouths and syncs Remotion), or directly:
    ~/reel-rig/openvoice/.venv/bin/python3 build_character.py        # 2px → pixel/
    ~/reel-rig/openvoice/.venv/bin/python3 build_character.py 2 1 3  # + pixel_1px/, pixel_3px/ alternates
"""
import json
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage as ndi

HERE = Path(__file__).parent
SHEETS = [HERE / "sheets/sheet1_full.jpg", HERE / "sheets/sheet2_full.jpg"]
POSES = [
    ["idle", "talk", "point_up", "hold_paper", "point_down", "wave"],
    ["laptop", "phone", "facepalm", "shrug", "mind_blown", "thumbs_up"],
]
CW, CH, BASE = 540, 560, 548          # common canvas + feet baseline (illustrated px)
OUTLINE, RIM = (10, 9, 10), (212, 255, 58)


def cutouts(path):
    im = np.array(Image.open(path).convert("RGB")).astype(int)
    bg = np.median(np.concatenate([im[:6].reshape(-1, 3), im[-6:].reshape(-1, 3)]), 0)
    dist = np.abs(im - bg).max(-1)
    chroma = im.max(-1) - im.min(-1)
    bgish = (dist < 14) & (chroma < 10)
    lab, _ = ndi.label(bgish)
    edge_ids = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    background = np.isin(lab, list(edge_ids))
    fg = ~background
    fg = ndi.binary_opening(fg, iterations=1)
    fl, n = ndi.label(fg)
    sizes = ndi.sum(fg, fl, range(1, n + 1))
    keep = [i + 1 for i in np.argsort(sizes)[::-1][:6]]
    figs = []
    for k in keep:
        m = fl == k
        m = ndi.binary_fill_holes(m) & (m | ~background)
        m = ndi.binary_erosion(m, iterations=1)          # trim the grey fringe from the old background
        # peel away leftover background-coloured halo pixels along the edge (e.g. around hands);
        # bright whites (trousers, sneakers, paper) are brighter than the grey and survive
        halo = (dist < 24) & (chroma < 14) & (im.mean(-1) < bg.mean() + 10)
        # upper body only: also peel the brighter whitish rim the generator left around hands
        ys_, _ = np.where(m)
        upper = np.zeros_like(m); upper[: int(ys_.min() + (ys_.max() - ys_.min()) * 0.55)] = True
        halo |= upper & (chroma < 16) & (im.mean(-1) > bg.mean() - 22)
        for _ in range(3):
            edge = m & ~ndi.binary_erosion(m)
            m = m & ~(edge & halo)
        # drop small light, colourless patches that touch the outside (generator halos);
        # big ones — the paper, trousers, sneakers — are kept
        light = m & (chroma < 18) & (im.mean(-1) > bg.mean() - 22)
        ll, nl = ndi.label(light)
        outside = ndi.binary_dilation(~m, iterations=2)
        for j in range(1, nl + 1):
            comp = ll == j
            if comp.sum() < 900 and (comp & outside).any():
                m &= ~comp
        m = ndi.binary_opening(m, iterations=1)
        # fill notches where grey trouser shading matched the background, then smooth the contour
        m = ndi.binary_closing(np.pad(m, 6), iterations=5)[6:-6, 6:-6]
        m = ndi.gaussian_filter(m.astype(float), 1.6) > 0.5
        ys, xs = np.where(m)
        figs.append((xs.mean(), ys.mean(), m))
    # order: row by y, then column by x
    figs.sort(key=lambda f: (int(f[1] >= im.shape[0] / 2), f[0]))
    out = []
    for _, _, m in figs:
        ys, xs = np.where(m)
        y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
        rgba = np.zeros((y1 - y0, x1 - x0, 4), np.uint8)
        rgba[..., :3] = im[y0:y1, x0:x1]
        # soft 1px edge
        alpha = ndi.gaussian_filter(m[y0:y1, x0:x1].astype(float), 0.6)
        rgba[..., 3] = (np.clip(alpha * 1.3, 0, 1) * 255).astype(np.uint8)
        # head centre: mean x of the top 12% of the silhouette
        top = m[y0:y0 + int((y1 - y0) * 0.12), x0:x1]
        hx = np.where(top)[1].mean()
        out.append((rgba, hx))
    return out


def place(rgba, hx):
    canvas = np.zeros((CH, CW, 4), np.uint8)
    h, w = rgba.shape[:2]
    ox = int(round(CW / 2 - hx))
    oy = BASE - h
    xs0, ys0 = max(0, ox), max(0, oy)
    xs1, ys1 = min(CW, ox + w), min(CH, oy + h)
    canvas[ys0:ys1, xs0:xs1] = rgba[ys0 - oy:ys1 - oy, xs0 - ox:xs1 - ox]
    return canvas


# Face alignment: the sheets draw the head at different heights/offsets per pose, so heads
# jumped on pose switches. Each pose is scaled about the feet (baseline stays put) so its
# mouth lands on MOUTH_AT, then shifted sideways. Mouth centres below were measured on the
# unaligned place() output (see build_mouths.py for how).
MOUTH_AT = (270, 121)
MOUTH_RAW = {
    "idle": (270, 121), "talk": (269, 121), "point_up": (270, 121), "hold_paper": (283, 136),
    "point_down": (269, 133), "wave": (277, 136), "laptop": (265, 120), "phone": (266, 122),
    "facepalm": (272, 129), "shrug": (265, 127), "mind_blown": (267, 135), "thumbs_up": (266, 136),
}


def align(c, mx, my):
    s = (BASE - MOUTH_AT[1]) / (BASE - my)
    im = Image.fromarray(c, "RGBA").convert("RGBa")          # premultiplied → no dark fringe
    im = im.resize((round(CW * s), round(CH * s)), Image.LANCZOS).convert("RGBA")
    ox, oy = round(MOUTH_AT[0] - mx * s), round(BASE - BASE * s)
    out = Image.new("RGBA", (CW, CH))
    out.paste(im, (ox, oy))
    return np.array(out), s, ox


ill_dir = HERE / "illustrated"; pix_dir = HERE / "pixel"
ill_dir.mkdir(exist_ok=True); pix_dir.mkdir(exist_ok=True)
placed = {}
for sheet, names in zip(SHEETS, POSES):
    for (rgba, hx), name in zip(cutouts(sheet), names):
        c, s, ox = align(place(rgba, hx), *MOUTH_RAW[name])
        print(f"  {name:11s} scale {s:.3f}  shift {ox:+d}px")
        placed[name] = c
        Image.fromarray(c, "RGBA").save(ill_dir / f"{name}.png")

# ── pixel art v2 ──
import sys
PIXES = [int(a) for a in sys.argv[1:]] or [2]
assert 2 in PIXES, "pixel/ (and the mouth overlays) are the 2px build — always include 2"
BLACKS = [(10, 10, 12), (20, 20, 23), (30, 30, 34), (44, 44, 50), (62, 62, 70)]
WHITES = [(246, 246, 244), (228, 228, 226), (204, 204, 206), (172, 172, 178), (140, 140, 148)]
LENS_DK, LENS, LENS_HI, SILVER = (8, 8, 10), (26, 26, 32), (120, 130, 145), (196, 200, 206)


def lum(c):
    return 0.299 * c[..., 0] + 0.587 * c[..., 1] + 0.114 * c[..., 2]


def find_lenses(c):
    rgb = c[..., :3].astype(float); al = c[..., 3] > 140
    ys, _ = np.where(al)
    top, h = ys.min(), ys.max() - ys.min()
    head = np.zeros_like(al); head[top: top + int(h * 0.2)] = True
    R, G, B = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    skin = head & al & (R > 110) & (R > G * 1.08) & (G > B * 1.02)
    if skin.sum() < 200:
        return None
    sy, sx = np.where(skin)
    y0, y1, x0, x1 = sy.min(), sy.max(), sx.min(), sx.max()
    face = np.zeros_like(al); face[y0: y0 + int((y1 - y0) * 0.55), x0:x1] = True
    dark = face & al & (lum(rgb) < 55)
    lab, nl = ndi.label(dark)
    blobs = []
    for j in range(1, nl + 1):
        yy, xx = np.where(lab == j)
        if 60 <= len(yy) <= 1500:
            blobs.append((len(yy), xx.mean(), yy.mean(), (xx.max() - xx.min()) / 2))
    blobs = sorted(blobs, reverse=True)[:2]
    if len(blobs) < 2 or abs(blobs[0][2] - blobs[1][2]) > 10:
        return None
    return [(bx, by, br) for _, bx, by, br in blobs]


LENSES = {}  # auto shade redraw disabled: unreliable, and 2px cells already render the shades cleanly



def pixelate(pix, out_dir):
    out_dir.mkdir(exist_ok=True)
    gw, gh = CW // pix, CH // pix
    # 1. edge-preserving smoothing at full res so clusters come out clean
    smooth = {}
    for n, c in placed.items():
        im = Image.fromarray(c, "RGBA")
        rgb = im.convert("RGB").filter(ImageFilter.MedianFilter(3 if pix <= 2 else 5)) if pix > 1 else im.convert("RGB")
        rgb = ImageEnhance.Contrast(rgb).enhance(1.12)
        rgba = rgb.convert("RGBA"); rgba.putalpha(im.getchannel("A"))
        smooth[n] = rgba.resize((gw, gh), Image.BOX)
    # 2. shared palette: median-cut for skin/props + hand-set ramps for blacks and whites
    stack = np.concatenate([np.array(v)[..., :3][np.array(v)[..., 3] > 140] for v in smooth.values()])
    q = Image.fromarray(stack.reshape(-1, 1, 3).astype(np.uint8)).quantize(colors=22, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    pal = np.vstack([np.array(q.getpalette()[:22 * 3]).reshape(-1, 3), BLACKS, WHITES])
    for n, v in smooth.items():
        a = np.array(v).astype(int)
        rgb, al = a[..., :3], a[..., 3] > 140
        g = pal[((rgb[:, :, None, :] - pal[None, None]) ** 2).sum(-1).argmin(-1)].astype(np.uint8)
        # colourless light pixels (drawstrings, trousers, sneakers, paper) → the neutral ramp
        W_ = np.array(WHITES)
        neutral = al & ((rgb.max(-1) - rgb.min(-1)) < 16) & (lum(rgb.astype(float)) > 120)
        g[neutral] = W_[((rgb[neutral][:, None, :] - W_[None]) ** 2).sum(-1).argmin(-1)]
        # speck cleanup (vectorised): a pixel unlike all 4 neighbours, where ≥3 neighbours agree
        code = (g[..., 0].astype(np.int64) << 16) | (g[..., 1].astype(np.int64) << 8) | g[..., 2]
        for _ in range(2):
            up, dn = np.roll(code, 1, 0), np.roll(code, -1, 0)
            lf, rt = np.roll(code, 1, 1), np.roll(code, -1, 1)
            nbs = np.stack([up, dn, lf, rt])
            lonely = (nbs != code).all(0) & al
            best = np.zeros_like(code); ok = np.zeros_like(al)
            for k in range(4):
                agree = (nbs == nbs[k]).sum(0)
                pick = (agree >= 3) & ~ok
                best[pick] = nbs[k][pick]; ok |= pick
            fix = lonely & ok
            code[fix] = best[fix]
        g = np.stack([(code >> 16) & 255, (code >> 8) & 255, code & 255], -1).astype(np.uint8)

        # 3. crisp shades, found on the full-res art: two lens-sized dark blobs inside the face
        lens = LENSES.get(n)
        if lens:
            for fx, fy, fr in lens:
                cy, cx, rad = fy / pix, fx / pix, max(fr / pix, 2.2)
                for r in range(int(cy - rad - 1), int(cy + rad + 2)):
                    for c in range(int(cx - rad - 1), int(cx + rad + 2)):
                        d = ((r + 0.5 - cy) ** 2 + (c + 0.5 - cx) ** 2) ** 0.5
                        if d <= rad and al[r, c]:
                            g[r, c] = LENS_DK if r + 0.5 < cy else LENS
                        elif d <= rad + 0.9 and r + 0.5 <= cy and al[r, c]:
                            g[r, c] = SILVER
                g[int(cy - rad * 0.45), int(cx - rad * 0.45)] = LENS_HI
        out = np.zeros((gh, gw, 4), np.uint8)
        out[al, :3] = g[al]; out[al, 3] = 255
        # 4. selective outline: each outline pixel = darkened neighbour colour
        ring = ndi.binary_dilation(al) & ~al
        gf = g.astype(float) * al[..., None]
        cnt = ndi.uniform_filter(al.astype(float), 3)
        avg = np.stack([ndi.uniform_filter(gf[..., i], 3) for i in range(3)], -1) / np.maximum(cnt[..., None], 1e-6)
        sel = np.clip(avg * 0.45, 0, 255)
        out[ring, :3] = sel[ring].astype(np.uint8); out[ring, 3] = 255
        # 5. lime rim only where the silhouette is dark (hoodie, hair) on its right side
        shifted = np.zeros_like(al); shifted[:, 1:] = al[:, :-1]
        rim = ring & shifted & (lum(avg) < 70)
        out[rim, :3] = RIM
        Image.fromarray(out, "RGBA").resize((gw * pix, gh * pix), Image.NEAREST).save(out_dir / f"{n}.png")
    return gw, gh


from PIL import ImageEnhance, ImageFilter
for pix in PIXES:
    gw, gh = pixelate(pix, pix_dir if pix == 2 else HERE / f"pixel_{pix}px")
    print(f"pixel grid {gw}x{gh} ({pix}px cells)")
GW, GH = CW // 2, CH // 2

(HERE / "poses.json").write_text(json.dumps({"poses": [p for row in POSES for p in row], "canvas": [CW, CH], "grid": [GW, GH], "mouth": MOUTH_AT}))
print("poses:", list(placed), "| pixel grid", GW, "x", GH)
