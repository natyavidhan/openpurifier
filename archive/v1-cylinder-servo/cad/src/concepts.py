"""Concept bodies for comparing a rounded-square purifier with the cylinder.

Simplified models (no screw details), close enough to compare filament use and looks:
  A  square enclosure - the cylinder's layout in a 216 mm rounded square with slotted walls
  B  square frame     - the same outline, but the filter shows through four big windows;
                        the box is closed only around the fan and the electronics

Both split at Z_SPLIT into a lower and an upper piece. Each piece prints whole (216 mm square),
so there are no seam halves. The plates are the current ones trimmed to the square.
"""
import build123d as bd
from cad import model

import core
import vendor
from lib.hw import at, gusset, radial_block
from lib.params import Z_CAP_BOT, Z_FAN_FRONT, Z_FILTER_BOT, Z_SPLIT, Z_TOP, Z_TP_BOT, Z_TRAY_BOT

W = 216.0                 # outside width
R = 20.0                  # outside corner radius
T = 2.5                   # wall
POST_T = 4.0              # frame posts (concept B)
HALF_IN = W / 2 - T       # 105.5
CORNERS = (45.0, 135.0, 225.0, 315.0)
FACES = (0.0, 90.0, 180.0, 270.0)
SHELL_COLOR = "#f2f1ec"

SLOT_W = 4.5
SLOT_PITCH = 9.25         # same open ratio as the cylinder's 4-degree pitch
LOWER_SLOT_ROWS = ((22.0, 66.0), (72.0, 116.0), (122.0, 166.0), (172.0, 216.0))
UPPER_SLOT_ROWS = ((250.0, 300.0),)

WINDOW_W = 140.0
WINDOW_Z = (30.0, 300.0)  # below the transition plate, so the fan and electronics stay enclosed


def rsq(w, r, z0, z1):
    return bd.extrude(bd.Plane.XY.offset(z0) * bd.RectangleRounded(w, w, r), amount=z1 - z0)


def rsq_tube(t, z0, z1):
    return rsq(W, R, z0, z1) - rsq(W - 2 * t, R - t, z0 - 1.0, z1 + 1.0)


def _inside(shape):
    """Clip an internal feature to the outer surface."""
    return shape & rsq(W - 0.2, R - 0.1, -10.0, Z_TOP + 10.0)


def _face_slots(rows):
    tools = []
    n = int(150.0 // SLOT_PITCH) + 1
    for zf in FACES:
        for i in range(n):
            u = (i - (n - 1) / 2) * SLOT_PITCH
            for z0, z1 in rows:
                face = bd.Plane.YZ.offset(HALF_IN - 1.5) * bd.SlotOverall(z1 - z0, SLOT_W, rotation=90)
                tools.append(at(bd.Pos(0, u, (z0 + z1) / 2) * bd.extrude(face, amount=T + 3.0), zf))
    return tools


def _windows():
    z0, z1 = WINDOW_Z
    face = bd.Plane.YZ.offset(HALF_IN - 4.0) * bd.RectangleRounded(WINDOW_W, z1 - z0, 14.0)
    return [at(bd.Pos(0, 0, (z0 + z1) / 2) * bd.extrude(face, amount=POST_T + 8.0), zf) for zf in FACES]


def _lower_features():
    adds = []
    for a in CORNERS:
        adds.append(_inside(at(radial_block(118.0, 146.0, 24.0, 0.0, 12.0), a)))          # feet / bayonet
        adds.append(_inside(at(radial_block(126.0, 146.0, 14.0, Z_SPLIT - 8.0, Z_SPLIT), a)))  # joint boss
        adds.append(_inside(at(gusset(140.0, 126.0, 14.0, Z_SPLIT - 8.0), a)))
    return adds


def _upper_features():
    adds = []
    for a in CORNERS:
        adds.append(_inside(at(radial_block(122.0, 146.0, 16.0, Z_SPLIT, Z_TP_BOT), a)))   # TP columns
    # Top lip the cap rests on, with a 45-degree underside.
    lip_w = 12.0
    outer = 2 * HALF_IN + 0.5
    chamfer = bd.loft(
        [
            bd.Plane.XY.offset(Z_CAP_BOT - 4.0 - lip_w) * bd.RectangleRounded(outer - 2 * lip_w, outer - 2 * lip_w, 6.0),
            bd.Plane.XY.offset(Z_CAP_BOT - 4.0) * bd.RectangleRounded(outer, outer, R - T + 0.25),
        ]
    )
    lip = chamfer + rsq(outer, R - T + 0.25, Z_CAP_BOT - 4.0, Z_CAP_BOT)
    lip -= rsq(outer - 2 * lip_w, 6.0, Z_CAP_BOT - 30.0, Z_CAP_BOT + 1.0)
    adds.append(lip)
    return adds


def _finish(shape, label):
    shape.label = label
    shape.color = SHELL_COLOR
    return shape


# ------------------------------------------------------------------ A: square enclosure
@model
def sq_enclosure_lower():
    body = rsq_tube(T, 0.0, Z_SPLIT).fuse(*_lower_features())
    spigot = rsq(W - 2 * T - 0.8, R - T - 0.4, Z_SPLIT, Z_SPLIT + 6.0) - rsq(W - 2 * T - 5.2, R - T - 2.6, Z_SPLIT - 1, Z_SPLIT + 7)
    body = body.fuse(spigot).cut(*_face_slots(LOWER_SLOT_ROWS))
    return _finish(body, "sq_enclosure_lower")


@model
def sq_enclosure_upper():
    body = rsq_tube(T, Z_SPLIT, Z_TOP).fuse(*_upper_features()).cut(*_face_slots(UPPER_SLOT_ROWS))
    return _finish(body, "sq_enclosure_upper")


# ------------------------------------------------------------------ B: square frame
@model
def sq_frame_lower():
    body = rsq_tube(POST_T, 0.0, Z_SPLIT).fuse(*_lower_features()).cut(*_windows())
    return _finish(body, "sq_frame_lower")


@model
def sq_frame_upper():
    body = rsq_tube(T, Z_SPLIT, Z_TOP).fuse(rsq_tube(POST_T, Z_SPLIT, WINDOW_Z[1] + 2.0), *_upper_features())
    return _finish(body.cut(*_windows()), "sq_frame_upper")


# ------------------------------------------------------------------ plates trimmed to the square
def _trim(shape, label):
    out = shape & rsq(2 * HALF_IN - 2.0, R - T - 1.0, -50.0, Z_TOP + 50.0)
    out.label = label
    return out


def sq_plates():
    return {
        "tray": _trim(core.tray().shape, "tray_sq"),
        "transition_plate": _trim(core.transition_plate().shape, "tp_sq"),
        "deck": _trim(core.deck().shape, "deck_sq"),
        "top_cap": _trim(core.top_cap().shape, "cap_sq"),
    }


def _concept(lower, upper, label):
    plates = sq_plates()
    plates["tray"] = bd.Pos(0, 0, Z_TRAY_BOT) * plates["tray"]
    for p, c in zip(plates.values(), ("#d8d6cf", "#cfd8d6", "#cfd8d6", SHELL_COLOR)):
        p.color = c
    filt = bd.Pos(0, 0, Z_FILTER_BOT) * vendor.filter_dummy()
    fan = bd.Pos(0, 0, Z_FAN_FRONT) * vendor.fan_dummy()
    return bd.Compound(children=[lower, upper, *plates.values(), filt, fan], label=label)


@model
def concept_square_enclosure():
    return _concept(sq_enclosure_lower().shape, sq_enclosure_upper().shape, "concept_square_enclosure")


@model
def concept_square_frame():
    return _concept(sq_frame_lower().shape, sq_frame_upper().shape, "concept_square_frame")


if __name__ == "__main__":
    concept_square_enclosure()
    concept_square_frame()
