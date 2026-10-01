"""
Cut figures out of a pose sheet (flat grey background) by grid cell.

    fg = SheetMask(path)                     # background flood + labelled foreground
    rgba, hx, (x0, y0) = fg.cut(grid=(8, 3), cell=(1, 5))   # cols×rows grid, 1-based (row, col)

The figure in a cell is the largest foreground piece whose centre lies in that cell, plus any
other sizeable pieces (detached hands, props) in the same cell that sit next to it. The cleanup
(halo peel, notch fill, contour smoothing) is the one the v1 build used for the whole sheet.
"""
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage as ndi


class SheetMask:
    def __init__(self, path: Path, bg_tol: int = 14, inner_bg_min: int = 0, keep: Path | None = None):
        self.path = Path(path)
        im = np.array(Image.open(path).convert("RGB")).astype(int)
        self.im = im
        self.bg = np.median(np.concatenate([im[:6].reshape(-1, 3), im[-6:].reshape(-1, 3)]), 0)
        self.dist = np.abs(im - self.bg).max(-1)
        self.chroma = im.max(-1) - im.min(-1)
        # bg_tol: how far from the background grey still counts as background. The v1 sheets need
        # 14; cleaner sheets can go lower so off-white sneakers aren't flooded away with the grey.
        bgish = (self.dist < bg_tol) & (self.chroma < 10)
        lab, _ = ndi.label(bgish)
        edge_ids = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
        self.background = np.isin(lab, list(edge_ids))
        # inner_bg_min: also treat enclosed background-coloured pockets of at least this many px as
        # background — the gap between the legs when a floor shadow joins the two shoes (v3 sheets)
        if inner_bg_min:
            sizes = np.bincount(lab.ravel())
            big = [i for i in range(1, len(sizes)) if sizes[i] >= inner_bg_min]
            self.background |= np.isin(lab, big)
        # keep: optional mask image (non-zero = figure) that is never background, e.g. white sneakers
        # the same shade as the background (v3 prep_sheets.py writes these)
        self.keep = np.array(Image.open(keep).convert("L")) > 0 if keep else np.zeros(im.shape[:2], bool)
        self.background &= ~self.keep
        fg = ndi.binary_opening(~self.background, iterations=1)
        self.lab, n = ndi.label(fg)
        idx = np.arange(1, n + 1)
        self.sizes = ndi.sum(fg, self.lab, idx)
        self.centres = np.array(ndi.center_of_mass(fg, self.lab, idx)) if n else np.zeros((0, 2))

    def _pieces(self, grid, cell):
        cols, rows = grid
        r, c = cell
        H, W = self.im.shape[:2]
        y0, y1 = (r - 1) * H / rows, r * H / rows
        x0, x1 = (c - 1) * W / cols, c * W / cols
        cy, cx = self.centres[:, 0], self.centres[:, 1]
        inside = np.where((cy >= y0) & (cy < y1) & (cx >= x0) & (cx < x1) & (self.sizes > 150))[0]
        if len(inside) == 0:
            raise ValueError(f"{self.path.name}: no figure in cell r{r}c{c} of a {cols}x{rows} grid")
        main = inside[np.argmax(self.sizes[inside])]
        m = self.lab == main + 1
        near = ndi.binary_dilation(m, iterations=12)
        for j in inside:
            if j != main and (near & (self.lab == j + 1)).any():
                m |= self.lab == j + 1
        return m

    def _clean(self, m):
        im, bg, dist, chroma, background = self.im, self.bg, self.dist, self.chroma, self.background
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
        # big ones — the paper, trousers, sneakers — are kept. Halos are thin rims, so a patch
        # only goes if it mostly vanishes when shrunk by 2px: on smaller-drawn sheets a sneaker or
        # lower leg split off by a dark ankle/knee line is under 900px but solid, and must stay.
        # Solid patches the colour of the background (grey trapped between a finger and the body) go.
        light = m & (chroma < 18) & (im.mean(-1) > bg.mean() - 22)
        ll, nl = ndi.label(light)
        outside = ndi.binary_dilation(~m, iterations=2)
        for j in range(1, nl + 1):
            comp = ll == j
            n = comp.sum()
            thin = ndi.binary_erosion(comp, iterations=2).sum() < 0.25 * n
            bg_grey = np.median(dist[comp]) < 10          # a pocket of trapped background, not a shoe
            if n < 900 and (comp & outside).any() and (thin or bg_grey):
                m &= ~comp
        m = ndi.binary_opening(m, iterations=1)
        # fill notches where grey trouser shading matched the background, then smooth the contour
        m = ndi.binary_closing(np.pad(m, 6), iterations=5)[6:-6, 6:-6]
        m = ndi.gaussian_filter(m.astype(float), 1.6) > 0.5
        # drop specks (generator dust under the feet); real detached parts like a foot are far bigger
        lab, n = ndi.label(m)
        if n > 1:
            sizes = ndi.sum(m, lab, range(1, n + 1))
            m = np.isin(lab, [i + 1 for i, s in enumerate(sizes) if s >= 0.004 * sizes.max()])
        return m | self.keep

    def cut(self, grid, cell):
        """→ (rgba crop of the figure, head-centre x inside the crop, crop origin (x0, y0) on the sheet)."""
        m = self._clean(self._pieces(grid, cell))
        ys, xs = np.where(m)
        y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
        rgba = np.zeros((y1 - y0, x1 - x0, 4), np.uint8)
        rgba[..., :3] = self.im[y0:y1, x0:x1]
        alpha = ndi.gaussian_filter(m[y0:y1, x0:x1].astype(float), 0.6)   # soft 1px edge
        rgba[..., 3] = (np.clip(alpha * 1.3, 0, 1) * 255).astype(np.uint8)
        # head centre: mean x of the top 12% of the silhouette
        top = m[y0:y0 + int((y1 - y0) * 0.12), x0:x1]
        hx = np.where(top)[1].mean()
        return rgba, hx, (int(x0), int(y0))
