"""Twist-lock check: the tray goes up past the feet, turns onto the landings, stops, and
can't turn back without being lifted over the detent.

Run:  PYTHONPATH=src cad run checks/check_tray.py
"""
import build123d as bd
from cad.build123d import overlap_volume

import core
import shell
from lib.params import CORNERS, COL_H, LOCK_A, LOCK_INSERT_A

lower = shell.shell_lower().shape
tray = core.tray().shape
INSERT = CORNERS[0] + LOCK_INSERT_A        # ears 9 deg clockwise of the corners
LOCK = CORNERS[0] + LOCK_A                 # ears 9 deg anticlockwise of the corners
LIFT = COL_H + 1.2 + 0.3                   # ears just clear the detent ridge


def clash(z, deg):
    t = bd.Pos(0, 0, z) * bd.Rot(0, 0, deg) * tray
    return sum(overlap_volume(a, b) for a in t.solids() for b in lower.solids())


ok = True
print("1. straight up at the insert angle")
for z in (-30.0, 0.0, 6.0, COL_H, LIFT):
    v = clash(z, INSERT)
    ok &= v < 0.01
    print(f"   z {z:5.1f}: {v:7.2f} mm3")
print("2. turning at the lifted height")
deg = INSERT
while deg <= LOCK + 0.01:
    v = clash(LIFT, deg)
    ok &= v < 0.01
    print(f"   {deg - CORNERS[0]:+5.1f} deg from the corner: {v:7.2f} mm3")
    deg += 3.0
print("3. locked and resting on the landings")
v = clash(COL_H, LOCK)
ok &= v < 0.01
print(f"   {v:7.2f} mm3")
print("4. turned 3 deg too far (the stop should block)")
v = clash(LIFT, LOCK + 3.0)
ok &= v > 0.5
print(f"   {v:7.2f} mm3")
print("5. turned back 3 deg without lifting (the detent should block)")
v = clash(COL_H, LOCK - 3.0)
ok &= v > 0.05
print(f"   {v:7.2f} mm3")
print("TWIST-LOCK OK" if ok else "TWIST-LOCK PROBLEM")
