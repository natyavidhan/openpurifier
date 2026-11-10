"""The air core: filter tray, transition plate (TP), deck and top cap.

  tray   - open spider under the filter's closed end; its 4 ears twist-lock onto the corner feet
  TP     - seals on the filter's top ring (foam) and carries the fan face-down (foam);
           4 x M3 x 10 into the upper section's corner columns
  deck   - clamps the fan plate onto the TP with 4 posts, carries the electronics
  cap    - outlet grille over the fan collar, push button, 4 x M3 x 6 into the corner bosses

TP and deck corners are trimmed (TRIM_R) so both pass the cap bosses when lowered in from the top.
Modelled where they sit in the purifier (world frame), except the tray (own frame).
Print orientation: tray as modelled; TP, deck and cap upside down (top face on the bed).
"""
import build123d as bd
from cad import model

from lib.hw import at, box, cbore_down, cyl, insert_hole_down, one_solid, radial_block, rsq, rsq_chamfered, tube
from lib.layout import deck_insert_points
from lib.params import (
    BUTTON_HOLE_D,
    BUTTON_POS,
    CAP_CORNER_R,
    CAP_HALF,
    CAP_SCREW_R,
    CAP_T,
    CORD_X,
    CORNERS,
    DECK_HOLE_R,
    DECK_POST_D,
    DECK_T,
    DUCT_DROP,
    DUCT_R0,
    DUCT_R1,
    GRILLE_R,
    JOINT_R,
    TP_CORNER_R,
    TP_HALF,
    TP_HOLE_R,
    TP_SEAT_DEPTH,
    TP_SEAT_R,
    TP_T,
    TPSCREW_T,
    TRAY_EAR_R0,
    TRAY_EAR_R1,
    TRAY_EAR_T,
    TRAY_EAR_W,
    TRAY_HUB_R,
    TRAY_LIP_H,
    TRAY_LIP_R0,
    TRAY_RIM_R0,
    TRAY_RIM_R1,
    TRAY_SPOKE_W,
    TRAY_T,
    TRIM_R,
    Z_CAP_BOT,
    Z_DECK_BOT,
    Z_DECK_TOP,
    Z_TOP,
    Z_TP_BOT,
    Z_TP_TOP,
    corner_point,
    deck_posts,
)

CORE_COLOR = "#d9dbde"
CAP_COLOR = "#f7f7f5"


def _plate(z0, h):
    """Rounded-square plate 1.5 mm inside the walls, corners trimmed to TRIM_R."""
    return rsq(TP_HALF, TP_CORNER_R, z0, z0 + h) & cyl(TRIM_R, h + 2.0, z0 - 1.0)


def _cord_notch(z0, h):
    """Gap at the back edge for the mains cord running up the back wall."""
    return box(12.0, 10.0, h + 1.0, cx=CORD_X, cy=TP_HALF - 3.0, z0=z0 - 0.5)


# --------------------------------------------------------------------------------------
@model
def tray():
    """Filter tray (own frame, bottom at z = 0, ears on the X and Y axes).

    Fit it from below with each ear 9 deg clockwise of a corner (seen from above), lift
    ~2 mm and turn it 18 deg anticlockwise until it stops. The filter's closed end sits on
    the rim on a ring of foam tape; the centring lip keeps it in place."""
    rim = tube(TRAY_RIM_R0, TRAY_RIM_R1, TRAY_T, 0.0)
    lip = tube(TRAY_LIP_R0, TRAY_RIM_R1, TRAY_LIP_H, TRAY_T)
    hub = cyl(TRAY_HUB_R, TRAY_T, 0.0)
    spokes = [at(radial_block(TRAY_HUB_R - 2.0, TRAY_RIM_R0 + 2.0, TRAY_SPOKE_W, 0.0, TRAY_T), 45.0 + 90.0 * k) for k in range(4)]
    ears = [at(radial_block(TRAY_EAR_R0, TRAY_EAR_R1, TRAY_EAR_W, 0.0, TRAY_EAR_T), 90.0 * k) for k in range(4)]
    body = one_solid(rim.fuse(lip, hub, *spokes, *ears))
    body.label = "tray"
    body.color = CORE_COLOR
    return body


# --------------------------------------------------------------------------------------
@model
def transition_plate():
    body = _plate(Z_TP_BOT, TP_T)
    cuts = [
        cyl(TP_SEAT_R, TP_SEAT_DEPTH + 0.01, Z_TP_BOT - 0.01),      # filter seat recess
        cyl(TP_HOLE_R, TP_T + 1.0, Z_TP_BOT - 0.5),                 # clean-air opening
        _cord_notch(Z_TP_BOT, TP_T),
    ]
    for c in CORNERS:
        x, y = corner_point(c, JOINT_R, TPSCREW_T)
        cuts += cbore_down(x, y, Z_TP_TOP, TP_T, 6.0)               # M3 x 10 into the corner column
    for x, y in deck_posts():
        cuts.append(insert_hole_down(x, y, Z_TP_TOP, 6.0))          # deck post screws
    body = one_solid(body.cut(*cuts))
    body.label = "transition_plate"
    body.color = CORE_COLOR
    return body


# --------------------------------------------------------------------------------------
@model
def deck():
    return _deck(None, "deck")


@model
def deck_basic():
    """Deck for the basic version (no electronics): only the WAGO holder's two inserts."""
    return _deck(("mains_cradle",), "deck_basic")


def _deck(modules, label):
    body = _plate(Z_DECK_BOT, DECK_T)
    posts = [cyl(DECK_POST_D / 2, Z_DECK_BOT - Z_TP_TOP + 0.01, Z_TP_TOP, x, y) for x, y in deck_posts()]
    body = body.fuse(*posts)
    cuts = [cyl(DECK_HOLE_R, DECK_T + 1.0, Z_DECK_BOT - 0.5), _cord_notch(Z_DECK_BOT, DECK_T)]
    for a in (0.0, 180.0):                                          # fan-cord notches at the collar
        cuts.append(at(radial_block(DECK_HOLE_R - 1.0, DECK_HOLE_R + 8.0, 10.0, Z_DECK_BOT - 0.5, Z_DECK_TOP + 0.5), a))
    total = Z_DECK_TOP - Z_TP_TOP
    for x, y in deck_posts():
        cuts += cbore_down(x, y, Z_DECK_TOP, total, total - 5.0)   # M3 x 10, 5 mm of post under the head
    for x, y in deck_insert_points(modules):
        cuts.append(insert_hole_down(x, y, Z_DECK_TOP, 5.0))        # electronics, M3 x 6
    body = one_solid(body.cut(*cuts))
    body.label = label
    body.color = CORE_COLOR
    return body


# --------------------------------------------------------------------------------------
@model
def top_cap():
    return _cap(True, "top_cap")


@model
def top_cap_basic():
    """Top cap for the basic version: no push-button hole."""
    return _cap(False, "top_cap_basic")


def _cap(button, label):
    plate = rsq_chamfered(CAP_HALF, CAP_CORNER_R, Z_CAP_BOT, Z_TOP, 0.0, 1.2)
    duct = tube(DUCT_R0, DUCT_R1, DUCT_DROP + 0.01, Z_CAP_BOT - DUCT_DROP)
    body = plate.fuse(duct)
    # Outlet grille: concentric slots with 6 spokes.
    rings = []
    r = 10.0
    while r < GRILLE_R - 0.5:
        r1 = min(r + 5.0, GRILLE_R)
        rings.append(tube(r, r1, CAP_T + 2.0, Z_CAP_BOT - 1.0))
        r += 7.5
    spokes = [at(radial_block(6.0, GRILLE_R + 2.0, 3.0, Z_CAP_BOT - 2.0, Z_TOP + 2.0), 30.0 + 60.0 * k) for k in range(6)]
    cuts = []
    for ring in rings:
        cuts += ring.cut(*spokes).solids()
    if button:
        cuts.append(cyl(BUTTON_HOLE_D / 2, CAP_T + 2.0, Z_CAP_BOT - 1.0, *BUTTON_POS))
    for c in CORNERS:
        x, y = corner_point(c, CAP_SCREW_R)
        cuts += cbore_down(x, y, Z_TOP, CAP_T, 3.0)                 # M3 x 6 into the corner boss
    body = one_solid(body.cut(*cuts))
    body.label = label
    body.color = CAP_COLOR
    return body


if __name__ == "__main__":
    tray()
    transition_plate()
    deck()
    deck_basic()
    top_cap()
    top_cap_basic()
