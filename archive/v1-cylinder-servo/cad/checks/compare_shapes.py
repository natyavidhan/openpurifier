"""Filament for the square concepts (same estimate as checks/filament.py).

Run:  PYTHONPATH=src cad run checks/compare_shapes.py
"""
import concepts as c

SKIN, INFILL, DENSITY = 0.84, 0.15, 1.24e-3


def grams(shape):
    v = sum(s.volume for s in shape.solids())
    a = sum(s.area for s in shape.solids())
    skin = min(v, a * SKIN)
    return (skin + INFILL * max(0.0, v - skin)) * DENSITY


plates = {k: grams(v) for k, v in c.sq_plates().items()}
for k, g in plates.items():
    print(f"  plate {k:18s} ~{g:5.0f} g")
plates_total = sum(plates.values())
ELECTRONICS = 35.0  # unchanged parts, from checks/filament.py
for name, lower, upper in (
    ("A square enclosure", c.sq_enclosure_lower, c.sq_enclosure_upper),
    ("B square frame", c.sq_frame_lower, c.sq_frame_upper),
):
    gl, gu = grams(lower().shape), grams(upper().shape)
    total = gl + gu + plates_total + ELECTRONICS
    print(f"{name:20s} lower ~{gl:4.0f} g  upper ~{gu:4.0f} g  shell ~{gl + gu:4.0f} g  "
          f"plates ~{plates_total:4.0f} g  TOTAL ~{total:5.0f} g")
