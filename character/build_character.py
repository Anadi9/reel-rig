#!/usr/bin/env python3
"""
Full-body character kit (v2) from the pose sheets listed in poses.yaml.

  1. cut each figure out of its sheet by grid cell (sheetcut.py: flood from the sheet edges,
     so white trousers/sneakers inside the silhouette are kept)
  2. put every pose on one canvas with the feet on the same baseline:
       stand poses   scaled about the feet so the mouth lands on MOUTH_AT, then shifted sideways;
                     the shift splits the difference between keeping the head still and keeping
                     the feet still (head moves at most MAX_HEAD_SHIFT px), so switches don't slide
       walk/sit/crouch  scaled so the head (crown → mouth) matches the standing poses
  3. export two styles:
       illustrated/<pose>.png   smooth cut-outs (the art as generated)
       pixel/<pose>.png         THE FINAL STYLE: 2px cells (270×280 grid), shared palette,
                                selective outline, lime rim on dark right edges
  4. poses.json: pose list + per-pose landmarks (canvas px) for the mouths, heads and Remotion

Run via ./build.sh (also builds the mouths and syncs Remotion), or directly:
    ~/reel-rig/openvoice/.venv/bin/python3 build_character.py        # 2px → pixel/
    ~/reel-rig/openvoice/.venv/bin/python3 build_character.py 2 1 3  # + pixel_1px/, pixel_3px/ alternates
"""
import json
import os
from pathlib import Path

import numpy as np
import yaml
from PIL import Image
from scipy import ndimage as ndi

from sheetcut import SheetMask

HERE = Path(os.environ.get("KIT_DIR") or Path(__file__).parent)   # KIT_DIR: build another kit (e.g. v3/) with these scripts
MANIFEST = yaml.safe_load((HERE / "poses.yaml").read_text())
POSE_NAMES = list(MANIFEST["poses"])
CW, CH, BASE = 540, 560, 548          # common canvas + feet baseline (illustrated px)
OUTLINE, RIM = (10, 9, 10), (212, 255, 58)
MOUTH_AT = (270, 121)
MAX_HEAD_SHIFT = 6                    # px the head may move sideways to keep the feet planted


def opaque(a):
    return a[..., 3] > 128


def feet_x(rgba):
    """Centre x of the lowest few rows of the silhouette (the shoes)."""
    ys, xs = np.where(opaque(rgba))
    lo = ys.max() - int((ys.max() - ys.min()) * 0.15)   # deep enough to catch a raised heel
    sel = xs[ys >= lo]
    return float(np.percentile(sel, 3) + np.percentile(sel, 97)) / 2   # midway between the two shoes


def crown_y(rgba, mx):
    """Top of the hood: first opaque row in a narrow band above the mouth."""
    band = opaque(rgba[:, max(0, mx - 6): mx + 7])
    return int(np.where(band.any(1))[0].min())


def paste_scaled(rgba, s, ox):
    """Scale the cut-out by s (premultiplied, no dark fringe) and stand it on the baseline at x=ox."""
    h, w = rgba.shape[:2]
    im = Image.fromarray(rgba, "RGBA").convert("RGBa")
    im = im.resize((max(1, round(w * s)), max(1, round(h * s))), Image.LANCZOS).convert("RGBA")
    out = Image.new("RGBA", (CW, CH))
    out.paste(im, (ox, BASE - im.height))
    return np.array(out), BASE - im.height


sheets = {k: (SheetMask(HERE / v["file"], v.get("bg_tol", 14), v.get("inner_bg_min", 0),
                        HERE / v["keep"] if "keep" in v else None), tuple(v["grid"]))
          for k, v in MANIFEST["sheets"].items()}
cuts = {}
for name, p in MANIFEST["poses"].items():
    fg, grid = sheets[p["sheet"]]
    rgba, _, (x0, y0) = fg.cut(grid, tuple(p["cell"]))
    cuts[name] = rgba
    p["mouth"] = [p["mouth"][0] - x0, p["mouth"][1] - y0]   # sheet px → cut-out px

# scale. v1 sheets (s1, s2): mouth → feet, as before (mouth lands on MOUTH_AT's row).
# Newer sheets: by head size (hood top → mouth) against the v1 head, using the median over a sheet
# row's standing poses (the generator draws each row at one size; crossed legs make a figure
# shorter, so feet-based scaling would inflate its head). A row with no standing pose → per pose.
# a sheet can opt in with `fit: feet` (v3 does for its full-length standing figures)
V1 = {"s1", "s2"} | {k for k, v in MANIFEST["sheets"].items() if v.get("fit") == "feet"}
def head(name):
    mx, my = MANIFEST["poses"][name]["mouth"]
    return my - crown_y(cuts[name], mx)
scale = {}
for name, p in MANIFEST["poses"].items():
    if p["sheet"] in V1:
        scale[name] = (BASE - MOUTH_AT[1]) / (cuts[name].shape[0] - p["mouth"][1])
REF_HEAD = float(np.median([scale[n] * head(n) for n in scale]))
row_head = {}
for name, p in MANIFEST["poses"].items():
    if p["sheet"] not in V1 and p["stance"] == "stand":
        row_head.setdefault((p["sheet"], p["cell"][0]), []).append(head(name))
for name, p in MANIFEST["poses"].items():
    if name not in scale:
        hs = row_head.get((p["sheet"], p["cell"][0]))
        scale[name] = REF_HEAD / (float(np.median(hs)) if hs else head(name))

# scale_like: <pose> — drawn at the same size as that pose on the source sheet (same row), so take
# its scale instead of measuring a tilted or side-on head
for name, p in MANIFEST["poses"].items():
    if "scale_like" in p:
        scale[name] = scale[p["scale_like"]] * p.get("scale_ratio", 1.0)

ref_feet = MOUTH_AT[0] + (feet_x(cuts["idle"]) - MANIFEST["poses"]["idle"]["mouth"][0]) * scale["idle"]

ill_dir = HERE / "illustrated"; pix_dir = HERE / "pixel"
ill_dir.mkdir(exist_ok=True); pix_dir.mkdir(exist_ok=True)
for d in (ill_dir, pix_dir):
    for f in d.glob("*.png"):
        if f.stem not in MANIFEST["poses"]:
            f.unlink()                # drop sprites of poses that left the manifest
placed, LAND = {}, {}
print(f"  {'pose':14s} scale  head dx  feet dx   (vs idle)")
for name, p in MANIFEST["poses"].items():
    rgba, s = cuts[name], scale[name]
    mx, my = p["mouth"]
    if p["stance"] == "stand":
        ox = MOUTH_AT[0] - mx * s
        feet = ox + feet_x(rgba) * s
        ox += float(np.clip((ref_feet - feet) / 2, -MAX_HEAD_SHIFT, MAX_HEAD_SHIFT))
    elif p["stance"] == "walk":
        ox = MOUTH_AT[0] - rgba.shape[1] * s / 2
    else:
        ox = MOUTH_AT[0] - mx * s
    ox = int(round(ox))
    c, top = paste_scaled(rgba, s, ox)
    mouth = [int(round(ox + mx * s)), int(round(top + my * s))]
    fdx = ox + feet_x(rgba) * s - ref_feet
    print(f"  {name:14s} {s:.3f} {mouth[0] - MOUTH_AT[0]:+6d} {fdx:+8.1f}   {p['stance']}")
    placed[name] = c
    LAND[name] = {"mouth": mouth, "talks": p["talks"], "head": p["head"], "stance": p["stance"],
                  "scale": round(s, 4)}
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

print("poses:", list(placed), "| pixel grid", GW, "x", GH)

(HERE / "poses.json").write_text(json.dumps({"poses": POSE_NAMES, "canvas": [CW, CH], "grid": [GW, GH], "mouth": MOUTH_AT, "meta": LAND}, indent=1))
