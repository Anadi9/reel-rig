#!/usr/bin/env python3
"""
Character v3: cut the usable figures out of the two GPT-Image-2 reference sheets
(../v3_reference/) into one flat-background image per pose (sheets/<pose>.png), and write
poses.yaml for build_character.py (grid [1, 1]: every pose is its own sheet).

The reference sheets are collages (panels, labels, faint grid), so each figure is cropped by a
hand-measured box. The "Poses & Actions" row on sheet A is cut off at the knee; those poses get
lower legs + sneakers grafted from the standing turnaround figure (same sheet, same scale):
the donor is aligned on the legs' centre at the cut row and pasted below it.

Mouth points are sheet px, measured on zoomed crops (v3_work/zoom.py).

Run: ~/reel-rig/openvoice/.venv/bin/python3 prep_sheets.py
"""
from pathlib import Path

import numpy as np
import yaml
from PIL import Image

HERE = Path(__file__).parent
REF = HERE.parent / "v3_reference"
SHEETS = {
    "A": np.array(Image.open(REF / "sheet_a_turnaround_poses.webp").convert("RGB")),
    "B": np.array(Image.open(REF / "sheet_b_expressions_lifestyle.webp").convert("RGB")),
}
PAD = 14

# name: sheet, box (x0, y0, x1, y1), mouth (sheet px), talks, head, stance, graft donor (or None)
POSES = {
    "idle":         ("A", (66, 90, 252, 718),    (134, 162), True,  "split", "stand", None),
    "front":        ("A", (281, 92, 394, 434),   (337, 138), True,  "split", "stand", None),
    "side_left":    ("A", (410, 92, 488, 434),   (432, 139), False, "split", "walk",  None),
    "back":         ("A", (494, 92, 609, 434),   (551, 139), False, "fixed", "walk",  None),
    "side_right":   ("A", (617, 92, 694, 434),   (674, 140), False, "split", "walk",  None),
    "relaxed":      ("B", (168, 88, 282, 420),   (220, 134), True,  "split", "stand", None),
    "side_look":    ("B", (272, 99, 363, 417),   (294, 145), False, "split", "walk",  None),
    "arms_crossed": ("B", (364, 87, 477, 422),   (424, 131), True,  "split", "stand", None),
    "back_bag":     ("B", (472, 87, 588, 422),   (524, 131), False, "fixed", "walk",  None),
    "squat":        ("B", (598, 170, 718, 422),  (648, 212), True,  "fixed", "crouch", None),
    "sit":          ("B", (725, 122, 858, 410),  (810, 162), False,  "split", "sit",   None),
    # sheet A pose row (knee-cropped → grafted legs)
    "point_you":    ("A", (377, 562, 472, 774),  (428, 608), True,  "split", "stand", "front"),
    "thumbs_up":    ("A", (473, 562, 580, 774),  (526, 604), True,  "split", "stand", "front"),
    "peace":        ("A", (580, 562, 674, 774),  (626, 603), True,  "split", "stand", "front"),
    "laptop":       ("A", (772, 562, 885, 774),  (822, 619), True,  "split", "stand", "front"),
    "coffee":       ("A", (884, 562, 1003, 774), (942, 610), False, "fixed", "stand", "front"),
    "look_up":      ("A", (1105, 562, 1190, 774), (1152, 599), False, "split", "stand", "side_right"),
}

# Straight-legged, full-length, ungrafted: scaled so the feet land on the baseline (mouth → feet).
# Every other pose is scaled to match their head size (crossed legs, grafts, sitting).
FIT_FEET = {"idle", "front", "arms_crossed"}
# Poses drawn in the same sheet row as a feet-fitted one share its scale (heads turned or tilted
# measure badly). The sheet-A pose row was drawn at the turnaround's size (hips ~73px on both).
SCALE_LIKE = {**{n: "front" for n in ["side_left", "back", "side_right", "point_you", "thumbs_up",
                                      "peace", "laptop", "coffee", "look_up"]},
              **{n: "arms_crossed" for n in ["relaxed", "side_look", "back_bag", "squat", "sit"]}}


def crop(sheet, box):
    x0, y0, x1, y1 = box
    return SHEETS[sheet][y0:y1, x0:x1].astype(int)


def bg_of(im):
    return np.median(np.concatenate([im[:3].reshape(-1, 3), im[:, :3].reshape(-1, 3), im[:, -3:].reshape(-1, 3)]), 0)


def legs_at(im, row, bg):
    """x-extent of the dark (trouser) pixels on one row → (left, right)."""
    dark = np.where((np.abs(im[row] - bg).max(-1) > 60) & (im[row].mean(-1) < 110))[0]
    return float(dark.min()), float(dark.max())


def graft(name, sheet, box, mouth, donor_name):
    """Figure crop + donor's lower legs pasted under the cut row, on a flat background canvas."""
    top = crop(sheet, box)
    bg = bg_of(top)
    dsheet, dbox, *_ = POSES[donor_name]
    donor = crop(dsheet, dbox)
    h, w = top.shape[:2]
    cut = h - 3                                   # last clean row above the panel edge
    l, r = legs_at(top, cut, bg)
    # donor row that matches the cut: same distance below the hoodie hem. Hem = first row under
    # the torso where the dark span narrows to the legs; measured ~ 707 (row A) and 246 (turnaround).
    hem_top, hem_donor = 707 - box[1], 246 - dbox[1]
    drow = hem_donor + (cut - hem_top)
    dl, dr = legs_at(donor, drow, bg_of(donor))
    s = float(np.clip((r - l) / max(dr - dl, 1), 0.85, 1.15))
    dh, dw = donor.shape[:2]
    dim = Image.fromarray(donor.astype(np.uint8)).resize((round(dw * s), round(dh * s)), Image.LANCZOS)
    donor = np.array(dim).astype(int)
    # Graft length: keep this figure's mouth → sole the same as the turnaround's (431 - 138 on
    # sheet A), so the head doesn't jump when the rig switches between standing poses.
    mouth_to_sole = 431 - 138
    sole = (431 - dbox[1]) * s
    drow = int(np.clip(round(sole - (mouth_to_sole - (cut - (mouth[1] - box[1])))), 0, donor.shape[0] - 2))
    dx = round((l + r) / 2 - (dl + dr) / 2 * s)
    below = donor[drow + 1:]
    H = cut + 1 + below.shape[0] + PAD
    W = max(w, dx + donor.shape[1]) - min(0, dx) + 2 * PAD
    ox = PAD - min(0, dx)
    out = np.empty((H + PAD, W, 3), int); out[:] = bg
    out[PAD:PAD + cut + 1, ox:ox + w] = top[:cut + 1]
    seg = below
    x_at = ox + dx
    out[PAD + cut + 1:PAD + cut + 1 + seg.shape[0], x_at:x_at + seg.shape[1]] = seg
    return out.clip(0, 255).astype(np.uint8), (box[0] - ox, box[1] - PAD)


def plain(sheet, box):
    im = crop(sheet, box)
    bg = bg_of(im)
    h, w = im.shape[:2]
    out = np.empty((h + 2 * PAD, w + 2 * PAD, 3), int); out[:] = bg
    out[PAD:PAD + h, PAD:PAD + w] = im
    return out.astype(np.uint8), (box[0] - PAD, box[1] - PAD)


def drop_floor_shadow(img):
    """Soft grey floor shadows join the shoes and survive the cut-out as a white slab. The soles have
    a black outline, so in the foot band everything below a column's lowest dark pixel (sole or
    trouser hem) is floor → background; columns with no dark pixel there (between the feet) too."""
    im = img.astype(int)
    bg = bg_of(im)
    fig = np.where((np.abs(im - bg).max(-1) > 40).any(1))[0]
    top, bot = fig.min(), fig.max()
    band0 = bot - int((bot - top) * 0.12)
    dark = im.mean(-1) < 90
    start = np.array([band0 + np.where(dark[band0:, x])[0].max() + 1 if dark[band0:, x].any() else band0
                      for x in range(im.shape[1])])
    # a sole line that's faint in a few columns mustn't slice a stripe out of the shoe: each column
    # takes the lowest sole row among its neighbours
    from scipy import ndimage as ndi
    start = ndi.maximum_filter1d(start, size=max(5, (bot - top) // 30))
    for x in range(im.shape[1]):
        im[start[x]:, x] = bg
    return im.astype(np.uint8)


def shoe_keep(img):
    """Mask of the sneakers: in the foot band, the strongly drawn parts (outlines, grey shading,
    trouser hems) grown by 2px and hole-filled, minus plain background. The sneakers' whites are
    the background's shade, so without this the cut-out floods into them."""
    from scipy import ndimage as ndi
    im = img.astype(int)
    bg = bg_of(im)
    dist = np.abs(im - bg).max(-1)
    fig = np.where((dist > 40).any(1))[0]
    band0 = fig.max() - int((fig.max() - fig.min()) * 0.12)
    strong = np.zeros(dist.shape, bool); strong[band0:] = dist[band0:] > 25
    keep = ndi.binary_fill_holes(ndi.binary_fill_holes(ndi.binary_dilation(strong, iterations=2)) & (dist > 3))
    keep[:band0] = False
    return keep


(HERE / "sheets").mkdir(exist_ok=True)
manifest = {"sheets": {}, "poses": {}}
for name, (sheet, box, mouth, talks, head, stance, donor) in POSES.items():
    img, (ox, oy) = graft(name, sheet, box, mouth, donor) if donor else plain(sheet, box)
    keep = None
    if stance != "sit":                           # sit: one foot is up on the block
        img = drop_floor_shadow(img)
        keep = shoe_keep(img)
        Image.fromarray((keep * 255).astype(np.uint8)).save(HERE / "sheets" / f"{name}_keep.png")
    Image.fromarray(img).save(HERE / "sheets" / f"{name}.png")
    manifest["sheets"][name] = {"file": f"sheets/{name}.png", "grid": [1, 1], "bg_tol": 12, "inner_bg_min": 250}
    if keep is not None:
        manifest["sheets"][name]["keep"] = f"sheets/{name}_keep.png"
    if name in FIT_FEET:
        manifest["sheets"][name]["fit"] = "feet"
    manifest["poses"][name] = {"sheet": name, "cell": [1, 1], "mouth": [mouth[0] - ox, mouth[1] - oy],
                               "talks": talks, "head": head, "stance": stance}
    if name in SCALE_LIKE:
        manifest["poses"][name]["scale_like"] = SCALE_LIKE[name]
    print(f"{name:13s} {img.shape[1]}x{img.shape[0]}{'  (grafted from ' + donor + ')' if donor else ''}")

hdr = ("# Character v3 pose manifest — GENERATED by prep_sheets.py (edit POSES there, not here).\n"
       "# Same fields as ../poses.yaml; every pose is its own one-cell sheet.\n")
(HERE / "poses.yaml").write_text(hdr + yaml.safe_dump(manifest, sort_keys=False, default_flow_style=None, width=140))
