import sys, numpy as np
from PIL import Image
from scipy import ndimage as ndi
path, x0, y0, x1, y1 = sys.argv[1], *map(int, sys.argv[2:6])
im = np.array(Image.open(path).convert("RGB")).astype(int)[y0:y1, x0:x1]
bg = np.median(im[:4].reshape(-1, 3), 0)
fg = (np.abs(im - bg).max(-1) > 28)
fg = ndi.binary_opening(fg, iterations=1)
lab, n = ndi.label(ndi.binary_dilation(fg, iterations=3))
print("bg", bg)
for sl in ndi.find_objects(lab):
    h, w = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
    if h > 60:
        print(f"box x {x0+sl[1].start}-{x0+sl[1].stop}  y {y0+sl[0].start}-{y0+sl[0].stop}  ({w}x{h})")
