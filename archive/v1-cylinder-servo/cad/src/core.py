"""The air core: filter tray, transition plate (TP), deck and top cap.

  tray   - twist-lock tray under the filter; rests on the shell's 4 feet columns
  TP     - seals on the filter's top ring (foam) and carries the fan face-down (foam)
  deck   - clamps the fan plate onto the TP with 4 posts, carries the electronics
  cap    - outlet grille over the fan collar, push button, 4 screws into the shell lip

All parts are modelled where they sit in the purifier (world frame).
Print orientation: tray as modelled; TP, deck and cap upside down (top face on the bed).
"""
import math

import build123d as bd
from cad import model

from lib.hw import at, box, cbore_down, cyl, insert_hole_down, one_solid, radial_block, revolve_profile, tube
from lib.layout import deck_insert_points
from lib.params import (
    BUTTON_HOLE_D,
    BUTTON_POS,
    CAP_R,
    CAP_SCREW_ANGLES,
    CAP_SCREW_R,
    CAP_T,
    COL_ANGLES,
    DECK_EAR_R,
    DECK_EAR_W,
    DECK_HOLE_R,
    DECK_POST_D,
    DECK_POST_R,
    DECK_T,
    DUCT_DROP,
    DUCT_R0,
    DUCT_R1,
    GRILLE_R,
    TP_CORNER_R,
    TP_EAR_R,
    TP_EAR_W,
    TP_HALF,
    TP_HOLE_R,
    TP_SEAT_DEPTH,
    TP_SEAT_R,
    TP_T,
    TPCOL_SCREW_R,
    TRAY_EAR_R0,
    TRAY_EAR_R1,
    TRAY_EAR_T,
    TRAY_EAR_W,
    TRAY_R,
    TRAY_RING_H,
    TRAY_RING_R0,
    TRAY_RING_R1,
    TRAY_T,
    Z_CAP_BOT,
    Z_DECK_BOT,
    Z_DECK_TOP,
    Z_TOP,
    Z_TP_BOT,
    Z_TP_TOP,
)

CORE_COLOR = "#d9dbde"
CAP_COLOR = "#f7f7f5"


def _xy(r, deg):
    return (r * math.cos(math.radians(deg)), r * math.sin(math.radians(deg)))


def _trimmed_square(z0, h):
    """194 x 194 square with its corners trimmed to clear the shell wall."""
    return box(2 * TP_HALF, 2 * TP_HALF, h, z0=z0) & cyl(TP_CORNER_R, h, z0)


# --------------------------------------------------------------------------------------
@model
def tray():
    """Filter tray (own frame, bottom at z = 0). Install: insert from below with the ears
    between the feet, lift ~2 mm, turn clockwise 45 deg until it stops."""
    body = cyl(TRAY_R, TRAY_T, 0.0)
    ears = [at(radial_block(TRAY_EAR_R0, TRAY_EAR_R1, TRAY_EAR_W, 0.0, TRAY_EAR_T), 45.0 + 90.0 * k) for k in range(4)]
    ring = tube(TRAY_RING_R0, TRAY_RING_R1, TRAY_RING_H, TRAY_T)
    body = body.fuse(*ears, ring)
    grips = [at(radial_block(106.0, TRAY_R + 1.0, 30.0, -1.0, TRAY_T + 1.0), a) for a in (0.0, 180.0)]
    body = one_solid(body.cut(*grips))
    body.label = "tray"
    body.color = CORE_COLOR
    return body


# --------------------------------------------------------------------------------------
@model
def transition_plate():
    body = _trimmed_square(Z_TP_BOT, TP_T)
    ears = [at(radial_block(TP_HALF - 1.0, TP_EAR_R, TP_EAR_W, Z_TP_BOT, Z_TP_TOP), a) for a in COL_ANGLES]
    body = body.fuse(*ears)
    cuts = [
        cyl(TP_SEAT_R, TP_SEAT_DEPTH + 0.01, Z_TP_BOT - 0.01),      # filter seat recess
        cyl(TP_HOLE_R, TP_T + 1.0, Z_TP_BOT - 0.5),                 # clean-air opening
    ]
    for a in COL_ANGLES:
        x, y = _xy(TPCOL_SCREW_R, a)
        cuts += cbore_down(x, y, Z_TP_TOP, TP_T, 6.0)               # M3 x 10 into the shell column
        x, y = _xy(DECK_POST_R, a)
        cuts.append(insert_hole_down(x, y, Z_TP_TOP, 6.0))          # insert for the deck post
    body = one_solid(body.cut(*cuts))
    body.label = "transition_plate"
    body.color = CORE_COLOR
    return body


# --------------------------------------------------------------------------------------
@model
def deck():
    body = _trimmed_square(Z_DECK_BOT, DECK_T)
    adds = [at(radial_block(TP_HALF - 1.0, DECK_EAR_R, DECK_EAR_W, Z_DECK_BOT, Z_DECK_TOP), a) for a in COL_ANGLES]
    for a in COL_ANGLES:
        x, y = _xy(DECK_POST_R, a)
        adds.append(cyl(DECK_POST_D / 2, Z_DECK_BOT - Z_TP_TOP + 0.01, Z_TP_TOP, x, y))
    body = body.fuse(*adds)
    cuts = [cyl(DECK_HOLE_R, DECK_T + 1.0, Z_DECK_BOT - 0.5)]
    for a in (0.0, 180.0):                                          # fan-cord notches at the collar
        cuts.append(at(radial_block(DECK_HOLE_R - 1.0, DECK_HOLE_R + 8.0, 10.0, Z_DECK_BOT - 0.5, Z_DECK_TOP + 0.5), a))
    for a in COL_ANGLES:
        x, y = _xy(DECK_POST_R, a)
        total = Z_DECK_TOP - Z_TP_TOP
        cuts += cbore_down(x, y, Z_DECK_TOP, total, total - 5.0)   # M3 x 10, 5 mm under the head
    for x, y in deck_insert_points():
        cuts.append(insert_hole_down(x, y, Z_DECK_TOP, 5.0))        # electronics, M3 x 6
    body = one_solid(body.cut(*cuts))
    body.label = "deck"
    body.color = CORE_COLOR
    return body


# --------------------------------------------------------------------------------------
@model
def top_cap():
    disk = revolve_profile([(0.0, Z_CAP_BOT), (CAP_R, Z_CAP_BOT), (CAP_R, Z_TOP - 1.2), (CAP_R - 1.2, Z_TOP), (0.0, Z_TOP)])
    duct = tube(DUCT_R0, DUCT_R1, DUCT_DROP + 0.01, Z_CAP_BOT - DUCT_DROP)
    body = disk.fuse(duct)
    # Outlet grille: concentric slots with 6 spokes.
    rings = []
    r = 10.0
    while r < GRILLE_R - 0.5:
        r1 = min(r + 5.0, GRILLE_R)
        rings.append(tube(r, r1, CAP_T + 2.0, Z_CAP_BOT - 1.0))
        r += 7.5
    spokes = [at(radial_block(6.0, GRILLE_R + 2.0, 3.0, Z_CAP_BOT - 2.0, Z_TOP + 2.0), 30.0 + 60.0 * k) for k in range(6)]
    slots = [ring.cut(*spokes) for ring in rings]
    cuts = []
    for s in slots:
        cuts += s.solids()
    cuts.append(cyl(BUTTON_HOLE_D / 2, CAP_T + 2.0, Z_CAP_BOT - 1.0, *BUTTON_POS))
    for a in CAP_SCREW_ANGLES:
        x, y = _xy(CAP_SCREW_R, a)
        cuts += cbore_down(x, y, Z_TOP, CAP_T, 3.0)                 # M3 x 6 into the shell lip
    body = one_solid(body.cut(*cuts))
    body.label = "top_cap"
    body.color = CAP_COLOR
    return body


if __name__ == "__main__":
    tray()
    transition_plate()
    deck()
    top_cap()
