"""Servo -> toggle linkage: for several tine lengths, sweep the fork and report the angle
window between 'lever pushed past centre (snaps)' and 'lever jammed at its end stop'.

Run:  PYTHONPATH=src cad run checks/check_actuator.py
"""
import build123d as bd
from cad.build123d import overlap_volume

import electronics as el
from lib.hw import box, cyl

bracket = el.switch_bracket().shape
shaft = bd.Axis((el.TG_X, 0, el.SHAFT_Z), (0, 1, 0))
pivot_z = el.PLATE_TOP + 6.0
pivot = bd.Axis((el.TG_X, el.TG_Y, pivot_z), (0, 1, 0))
fixed = bd.Pos(el.TG_X, el.TG_Y, el.PLATE_TOP) * box(13.0, 8.0, 10.0, z0=-13.0).fuse(
    cyl(3.0, 9.0, -3.0), cyl(4.6, 2.0, 0.0))
LEVERS = {phi10 / 10: cyl(1.5, 10.5, pivot_z, el.TG_X, el.TG_Y).rotate(pivot, phi10 / 10)
          for phi10 in range(150, -151, -5)}


def forced_phi(f):
    for phi, lev in LEVERS.items():
        if overlap_volume(f, lev) < 0.05:
            return phi
    return None


for bottom in (31.0, 34.0, 35.5, 37.0):
    fork = el.fork_horn_body(bottom)
    snap, jam, clash = None, None, False
    rows = []
    for t10 in range(0, 301, 5):
        theta = t10 / 10
        f = fork.rotate(shaft, theta)
        if overlap_volume(f, bracket) > 0.05 or overlap_volume(f, fixed) > 0.05:
            clash = True
        phi = forced_phi(f)
        rows.append((theta, phi))
        if snap is None and phi is not None and phi <= -1.0:
            snap = theta
        if snap is not None and jam is None and phi is None:
            jam = theta
    print(f"tine bottom z={bottom:4.1f}: snaps at {snap} deg, jams at {jam} deg, "
          f"window {None if snap is None or jam is None else round(jam - snap, 1)} deg, clash={clash}")
