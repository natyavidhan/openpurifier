"""Fade the shadow catcher's alpha to zero at the image borders, so a render sits on any page
without a visible rectangle.   python cad/render/fade_edges.py docs/images/render_*.png
"""
import sys

import numpy as np
from PIL import Image

MARGIN = 90  # px

for path in sys.argv[1:]:
    if path.endswith("_draft.png"):
        continue
    im = np.asarray(Image.open(path).convert("RGBA")).astype(np.float32)
    h, w = im.shape[:2]
    y = np.minimum(np.arange(h), np.arange(h)[::-1])[:, None]
    x = np.minimum(np.arange(w), np.arange(w)[::-1])[None, :]
    ramp = np.clip(np.minimum(x, y) / MARGIN, 0, 1)
    ramp = ramp * ramp * (3 - 2 * ramp)  # smoothstep
    im[..., 3] *= ramp
    Image.fromarray(im.round().astype(np.uint8)).save(path, optimize=True)
    print("faded", path)
