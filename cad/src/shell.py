"""Body: a 216 mm rounded square in two sections. Each prints in one piece, upright.

  shell_lower  0..240 (+ 6 mm spigot): intake slots, corner feet with the filter tray's
               twist-lock, joint bosses at the top corners, PG7 gland and cord anchors
               on the back (+Y) wall
  shell_upper  240..423: intake slots, corner columns that carry the transition plate,
               corner bosses the top cap screws into

The sections join with 4 x M3 x 10 at the corners, driven from the top through wells in
the upper section's columns (before the transition plate goes in).
"""
import build123d as bd
from cad import model

from lib.hw import at, box, cyl, gusset, insert_hole_down, one_solid, radial_block, rsq, rsq_chamfered, sector, ycyl
from lib.params import (
    BODY_R,
    BODY_W,
    CAP_BOSS_H,
    CAP_BOSS_R0,
    CAP_BOSS_W,
    CAP_SCREW_R,
    COL_H,
    COL_R0,
    COL_W,
    CORD_X,
    CORNER_IN,
    CORNER_R_IN,
    CORNERS,
    DETENT_A,
    FACES,
    GLAND_HOLE_D,
    GLAND_Z,
    HALF_IN,
    JOINT_BOSS_H,
    JOINT_R,
    JOINT_T,
    JOINT_TAB_T,
    JOINT_WELL_D,
    LAND_A0,
    LAND_A1,
    LAND_R0,
    LOWER_ANCHOR_Z,
    LOWER_SLOT_ROWS,
    M3_CLEAR_D,
    SLOT_PITCH,
    SLOT_U,
    SLOT_W,
    SPIGOT_GAP,
    SPIGOT_H,
    SPIGOT_T,
    SPIGOT_U,
    STOP_A0,
    STOP_H,
    TPSCREW_T,
    UPPER_ANCHOR_Z,
    UPPER_SLOT_ROWS,
    WALL,
    Z_CAP_BOT,
    Z_SPLIT,
    Z_TOP,
    Z_TP_BOT,
    corner_point,
)

SHELL_COLOR = "#f2f1ec"
R_PAST_WALL = CORNER_IN + 6.0      # corner features run past the wall, then get clipped


def _inside(shape):
    """Clip an internal feature to the outer surface so it merges into the wall."""
    return shape & rsq(BODY_W / 2 - 0.05, BODY_R - 0.05, -10.0, Z_TOP + 10.0)


def _tube(z0, z1, ch_bot, ch_top):
    outer = rsq_chamfered(BODY_W / 2, BODY_R, z0, z1, ch_bot, ch_top)
    return outer - rsq(HALF_IN, CORNER_R_IN, z0 - 1.0, z1 + 1.0)


def _corner_block(c, r0, w, z0, z1):
    return _inside(at(radial_block(r0, R_PAST_WALL, w, z0, z1), c))


def _corner_gusset(c, r0, w, z_top):
    return _inside(at(gusset(R_PAST_WALL, r0, w, z_top), c))


def _slots(rows):
    """Vertical slots on the four flat sides. The back wall keeps a solid strip for the cord."""
    n = int(round(2 * SLOT_U / SLOT_PITCH)) + 1
    tools = []
    for f in FACES:
        for i in range(n):
            u = -SLOT_U + i * SLOT_PITCH
            if f == 90.0 and -u > CORD_X - 14.0:          # back wall: world x = -u
                continue
            for z0, z1 in rows:
                face = bd.Plane.YZ.offset(HALF_IN - 1.5) * bd.SlotOverall(z1 - z0, SLOT_W, rotation=90)
                tools.append(at(bd.Pos(0, u, (z0 + z1) / 2) * bd.extrude(face, amount=WALL + 3.0), f))
    return tools


def _anchor(z):
    """Zip-tie anchor on the back wall at x = CORD_X: block, 45-degree underside, tunnel along X."""
    yw = HALF_IN + 0.5
    blk = box(12.0, 6.5, 9.0, cx=CORD_X, cy=yw - 3.25, z0=z)
    tri = bd.Polygon((yw, z), (yw - 6.5, z), (yw, z - 9.5), align=None)
    wedge = bd.extrude(bd.Plane.YZ.offset(CORD_X - 6.0) * tri, amount=12.0)
    tunnel = box(16.0, 2.0, 3.5, cx=CORD_X, cy=HALF_IN - 1.5, z0=z + 2.75)
    return (blk + wedge) - tunnel


def _detent(c):
    """Radial ridge (1.2 mm tall, 3.2 wide) on a landing; the ear clicks over it."""
    tri = bd.Polygon((-1.6, 0.0), (1.6, 0.0), (0.0, 1.2), align=None)
    ridge = bd.extrude(bd.Plane.YZ.offset(LAND_R0 + 1.0) * tri, amount=11.0)
    return at(bd.Pos(0, 0, COL_H - 0.01) * ridge, c + DETENT_A)


def _spigot():
    """Spigot along each flat side: rises 6 mm into the upper section, tied into the wall
    below with a 45-degree ledge."""
    xi, xo, xw = HALF_IN - SPIGOT_GAP - SPIGOT_T, HALF_IN - SPIGOT_GAP, HALF_IN + 0.6
    z = Z_SPLIT
    prof = bd.Polygon(
        (xi, z + SPIGOT_H), (xo, z + SPIGOT_H), (xo, z), (xw, z), (xw, z - 3.0 - 1.5 * (xw - xi)), (xi, z - 3.0),
        align=None,
    )
    strip = bd.extrude(bd.Plane.XZ * prof, amount=SPIGOT_U, both=True)
    return [at(strip, f) for f in FACES]


# --------------------------------------------------------------------------------------
def lower_section():
    body = _tube(0.0, Z_SPLIT, 1.0, 1.0)
    adds = []
    for c in CORNERS:
        # Feet = twist-lock landings: the tray's ears rest here, a stop at the far end,
        # a detent bump at the near end.
        adds.append(_inside(sector(LAND_R0, R_PAST_WALL, c + LAND_A0, c + LAND_A1, 0.0, COL_H)))
        adds.append(_inside(sector(LAND_R0, R_PAST_WALL, c + STOP_A0, c + LAND_A1, COL_H - 0.01, COL_H + STOP_H)))
        adds.append(_detent(c))
        # Ring-joint boss (insert points up), with a 45-degree gusset under it.
        adds.append(_corner_block(c, COL_R0, COL_W, Z_SPLIT - JOINT_BOSS_H, Z_SPLIT))
        adds.append(_corner_gusset(c, COL_R0, COL_W, Z_SPLIT - JOINT_BOSS_H))
    adds += _spigot()
    adds += [_anchor(z) for z in LOWER_ANCHOR_Z]
    body = body.fuse(*adds)

    cuts = []
    for c in CORNERS:
        x, y = corner_point(c, JOINT_R, JOINT_T)
        cuts.append(insert_hole_down(x, y, Z_SPLIT, 7.0))
    cuts.append(ycyl(GLAND_HOLE_D / 2, HALF_IN - 1.0, BODY_W / 2 + 1.0, x=CORD_X, z=GLAND_Z))
    cuts += _slots(LOWER_SLOT_ROWS)
    return one_solid(body.cut(*cuts))


def upper_section():
    body = _tube(Z_SPLIT, Z_TOP, 1.0, 1.5)
    adds = []
    for c in CORNERS:
        adds.append(_corner_block(c, COL_R0, COL_W, Z_SPLIT, Z_TP_BOT))                       # TP column
        adds.append(_corner_block(c, CAP_BOSS_R0, CAP_BOSS_W, Z_CAP_BOT - CAP_BOSS_H, Z_CAP_BOT))
        adds.append(_corner_gusset(c, CAP_BOSS_R0, CAP_BOSS_W, Z_CAP_BOT - CAP_BOSS_H))
    adds += [_anchor(z) for z in UPPER_ANCHOR_Z]
    body = body.fuse(*adds)

    cuts = []
    for c in CORNERS:
        x, y = corner_point(c, JOINT_R, JOINT_T)
        cuts.append(cyl(M3_CLEAR_D / 2, JOINT_TAB_T + 1.0, Z_SPLIT - 0.5, x, y))           # joint screw
        cuts.append(cyl(JOINT_WELL_D / 2, Z_TP_BOT - Z_SPLIT, Z_SPLIT + JOINT_TAB_T, x, y))  # hex-key well
        x, y = corner_point(c, JOINT_R, TPSCREW_T)
        cuts.append(insert_hole_down(x, y, Z_TP_BOT, 7.0))                                   # TP screw
        x, y = corner_point(c, CAP_SCREW_R)
        cuts.append(insert_hole_down(x, y, Z_CAP_BOT, 5.0))                                  # cap screw
    cuts += _slots(UPPER_SLOT_ROWS)
    return one_solid(body.cut(*cuts))


def _finish(shape, label):
    shape.label = label
    shape.color = SHELL_COLOR
    return shape


@model
def shell_lower():
    return _finish(lower_section(), "shell_lower")


@model
def shell_upper():
    return _finish(upper_section(), "shell_upper")


if __name__ == "__main__":
    shell_lower()
    shell_upper()
