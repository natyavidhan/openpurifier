"""Fit checks: part-to-part interference in the assembly, and bed fit of every printed part.

Run:  PYTHONPATH=src cad run checks/check_fit.py          (smart version)
      PYTHONPATH=src cad run checks/check_fit.py basic    (basic version: filter + fan only)
"""
import itertools
import math
import sys

import build123d as bd
from cad.build123d import overlap_volume

import core
import electronics as el
import shell
from assembly import assembly, assembly_basic
from lib.params import BED_LIMIT


def world_parts(node, parent=None):
    here = (bd.Location() if parent is None else parent) * node.location
    if node.children:
        for child in node.children:
            yield from world_parts(child, here)
    else:
        yield node.located(here)


def tight_bbox(shape):
    return shape.bounding_box(optimal=True)


def boxes_touch(a, b, tol=0.01):
    return (a.min.X <= b.max.X + tol and b.min.X <= a.max.X + tol and
            a.min.Y <= b.max.Y + tol and b.min.Y <= a.max.Y + tol and
            a.min.Z <= b.max.Z + tol and b.min.Z <= a.max.Z + tol)


# ---------------------------------------------------------------- interference
BASIC = len(sys.argv) > 1 and sys.argv[1] == "basic"
print("variant:", "basic" if BASIC else "smart")
doc = (assembly_basic() if BASIC else assembly()).shape
parts = [p for p in world_parts(doc)]
print(f"parts: {len(parts)}")
boxes = [tight_bbox(p) for p in parts]
xs = [b.min.X for b in boxes] + [b.max.X for b in boxes]
ys = [b.min.Y for b in boxes] + [b.max.Y for b in boxes]
zs = [b.min.Z for b in boxes] + [b.max.Z for b in boxes]
print(f"overall (tight): X {min(xs):.1f}..{max(xs):.1f}  Y {min(ys):.1f}..{max(ys):.1f}  Z {min(zs):.1f}..{max(zs):.1f}")

clashes = []
for (i, a), (j, b) in itertools.combinations(enumerate(parts), 2):
    if not boxes_touch(boxes[i], boxes[j]):
        continue
    vol = 0.0
    for sa in a.solids():
        for sb in b.solids():
            vol += overlap_volume(sa, sb)
    if vol > 0.5:
        clashes.append((vol, a.label, b.label))
clashes.sort(reverse=True)
print(f"interferences > 0.5 mm3: {len(clashes)}")
for vol, la, lb in clashes:
    print(f"  {vol:9.1f} mm3   {la}  <->  {lb}")

# ---------------------------------------------------------------- bed fit
def footprint(shape):
    """Smallest square side over rotations about Z (the part can be turned on the bed)."""
    best = (1e9, 0)
    for deg in range(0, 90, 3):
        bb = tight_bbox(bd.Rot(0, 0, deg) * shape)
        side = max(bb.size.X, bb.size.Y)
        if side < best[0]:
            best = (side, deg)
    return best


def flipped(shape):
    return bd.Rot(180, 0, 0) * shape


printables = {
    "shell_lower": shell.shell_lower().shape,
    "shell_upper": shell.shell_upper().shape,
    "tray": core.tray().shape,
    "transition_plate (flipped)": flipped(core.transition_plate().shape),
    "deck (flipped)": flipped(core.deck().shape),
    "top_cap (flipped)": flipped(core.top_cap().shape),
    "esp32_holder": el.esp32_holder().shape,
    "psu_box": el.psu_box().shape,
    "psu_lid": el.psu_lid().shape,
    "relay_box": el.relay_box().shape,
    "relay_lid": el.relay_lid().shape,
    "mains_cradle": el.mains_cradle().shape,
}
if BASIC:
    printables = {
        "shell_lower": printables["shell_lower"],
        "shell_upper": printables["shell_upper"],
        "tray": printables["tray"],
        "transition_plate (flipped)": printables["transition_plate (flipped)"],
        "deck_basic (flipped)": flipped(core.deck_basic().shape),
        "top_cap_basic (flipped)": flipped(core.top_cap_basic().shape),
        "mains_cradle": printables["mains_cradle"],
    }
for name, shp in printables.items():
    n = len(shp.solids())
    if n != 1:
        print(f"  !! {name} is {n} separate solids")
print(f"bed fit (limit {BED_LIMIT:.0f} mm):")
ok = True
for name, shp in printables.items():
    side, deg = footprint(shp)
    h = tight_bbox(shp).size.Z
    fits = side <= BED_LIMIT and h <= BED_LIMIT
    ok &= fits
    print(f"  {'OK ' if fits else 'NO '} {name:28s} footprint {side:6.1f} (turned {deg:2d} deg)  height {h:6.1f}")
print("ALL FIT" if ok else "SOME PARTS DO NOT FIT")
