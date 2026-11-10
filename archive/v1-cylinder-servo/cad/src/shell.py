"""Outer cylinder: a lower ring (intake, filter bay) and an upper ring (fan + electronics bay).

Each ring is modelled whole, then split on the seam plane into half A (the 22.5..202.5 deg
side, carries the brass inserts) and half B (screw heads). Every half is printed upright,
turned ~45 deg on the bed: a half of the 265 mm ring needs about 227 x 227 mm.
"""
import math

import build123d as bd
from cad import model

from lib.hw import (
    at,
    box,
    cyl,
    gusset,
    insert_hole_down,
    one_solid,
    radial_block,
    revolve_profile,
    tube,
    ycyl,
)
from lib.params import (
    CAP_SCREW_ANGLES,
    CAP_SCREW_R,
    COL_ANGLES,
    COL_H,
    COL_R0,
    COL_W,
    CORD_ANGLE,
    GLAND_HOLE_D,
    GLAND_Z,
    INSERT_HOLE_D,
    JOINT_ANGLES,
    JOINT_R0,
    JOINT_SCREW_R,
    JOINT_TAB_T,
    JOINT_W,
    LIP_R0,
    LIP_T,
    M3_CLEAR_D,
    SEAM_ANGLE,
    SEAM_R0,
    SEAM_SCREW_R,
    SEAM_T_A,
    SEAM_T_B,
    SHELL_R_IN,
    SHELL_R_OUT,
    SPIGOT_GAP,
    SPIGOT_H,
    SPIGOT_T,
    TPCOL_R0,
    TPCOL_SCREW_R,
    TPCOL_W,
    Z_CAP_BOT,
    Z_SPLIT,
    Z_TOP,
    Z_TP_BOT,
)

SHELL_COLOR = "#f2f1ec"
WALL_IN = SHELL_R_IN + 0.5          # internal features overlap the wall by 0.5 mm

LOWER_SLOT_ROWS = ((22.0, 66.0), (72.0, 116.0), (122.0, 166.0), (172.0, 216.0))
UPPER_SLOT_ROWS = ((250.0, 300.0),)
SLOT_W = 4.5
SLOT_PITCH_DEG = 4.0
LOWER_SEAM_SCREW_Z = (30.0, 120.0, 210.0)
UPPER_SEAM_SCREW_Z = (268.0, 345.0, 395.0)


def _ang_dist(a, b):
    d = (a - b) % 360.0
    return min(d, 360.0 - d)


def _shell_tube(z0, z1, chamfer_bottom, chamfer_top):
    """Tube with small outer chamfers (they form a V-groove where the rings meet)."""
    cb, ct = chamfer_bottom, chamfer_top
    return revolve_profile(
        [
            (SHELL_R_IN, z0),
            (SHELL_R_OUT - cb, z0),
            (SHELL_R_OUT, z0 + cb),
            (SHELL_R_OUT, z1 - ct),
            (SHELL_R_OUT - ct, z1),
            (SHELL_R_IN, z1),
        ]
    )


def _seam_frame(shape):
    return at(shape, SEAM_ANGLE)


def _seam_flanges(z0, z1):
    """Flanges on both seam ends. Local frame: seam line on X, half A on +Y."""
    parts = []
    for sign in (1, -1):
        x0, x1 = sorted((sign * SEAM_R0, sign * WALL_IN))
        cx, sx = (x0 + x1) / 2, x1 - x0
        parts.append(box(sx, SEAM_T_A, z1 - z0, cx=cx, cy=SEAM_T_A / 2, z0=z0))
        parts.append(box(sx, SEAM_T_B, z1 - z0, cx=cx, cy=-SEAM_T_B / 2, z0=z0))
    return [_seam_frame(p) for p in parts]


def _seam_holes(zs):
    """Insert pockets in half A (+Y) and clearance holes in half B (-Y) for M3 x 10."""
    holes = []
    for sign in (1, -1):
        x = sign * SEAM_SCREW_R
        for z in zs:
            holes.append(_seam_frame(ycyl(INSERT_HOLE_D / 2, 0.0, 6.0, x=x, z=z)))
            holes.append(_seam_frame(ycyl(M3_CLEAR_D / 2, -SEAM_T_B - 0.5, 0.0, x=x, z=z)))
    return holes


def _seam_plane():
    a = math.radians(SEAM_ANGLE)
    return bd.Plane(origin=(0, 0, 0), x_dir=(math.cos(a), math.sin(a), 0), z_dir=(-math.sin(a), math.cos(a), 0))


def _half(full, side):
    keep = bd.Keep.TOP if side == "a" else bd.Keep.BOTTOM
    return one_solid(bd.split(full, bisect_by=_seam_plane(), keep=keep))


def _in_half(deg, side):
    d = (deg - SEAM_ANGLE) % 360.0
    return (0.0 < d < 180.0) if side == "a" else (180.0 < d < 360.0)


def _slot_tool(z0, z1):
    h = z1 - z0
    face = bd.Plane.YZ.offset(SHELL_R_IN - 1.5) * bd.SlotOverall(h, SLOT_W, rotation=90)
    return bd.Pos(0, 0, (z0 + z1) / 2) * bd.extrude(face, amount=SHELL_R_OUT - SHELL_R_IN + 3.0)


def _slots(rows, side, skips):
    tools = []
    n = int(round(360.0 / SLOT_PITCH_DEG))
    for i in range(n):
        deg = SLOT_PITCH_DEG / 2 + i * SLOT_PITCH_DEG
        if not _in_half(deg, side):
            continue
        if any(_ang_dist(deg, a) < w for a, w in skips):
            continue
        for z0, z1 in rows:
            tools.append(at(_slot_tool(z0, z1), deg))
    return tools


def _tie_anchor(z):
    """Zip-tie anchor on the inner wall: a block with a tangential tunnel near the wall."""
    blk = radial_block(123.5, WALL_IN, 12.0, z, z + 9.0)
    tunnel = box(2.0, 14.0, 3.5, cx=127.0, cy=0.0, z0=z + 2.75)
    return blk - tunnel


# --------------------------------------------------------------------------------------
# Lower ring
# --------------------------------------------------------------------------------------
def lower_ring_full():
    body = _shell_tube(0.0, Z_SPLIT, 1.0, 1.0)
    adds = []
    # Bayonet columns = feet + tray supports. Stop on the CW edge, detent bump near CCW edge.
    for a in COL_ANGLES:
        adds.append(at(radial_block(COL_R0, WALL_IN, COL_W, 0.0, COL_H), a))
        adds.append(at(box(WALL_IN - COL_R0, 3.0, 3.0, cx=(COL_R0 + WALL_IN) / 2, cy=-COL_W / 2 + 1.5, z0=COL_H), a))
        adds.append(at(bd.Pos(120.5, COL_W / 2 - 2.0, COL_H) * bd.Sphere(1.5), a))
    # Ring-joint bosses at the top (inserts point up), with 45-degree gussets.
    for a in JOINT_ANGLES:
        adds.append(at(radial_block(JOINT_R0, WALL_IN, JOINT_W, Z_SPLIT - 8.0, Z_SPLIT), a))
        adds.append(at(gusset(WALL_IN, JOINT_R0, JOINT_W, Z_SPLIT - 8.0), a))
    # Spigot that centres the upper ring; notched where the upper ring has tabs/columns/flanges.
    spig = tube(SHELL_R_IN - SPIGOT_GAP - SPIGOT_T, SHELL_R_IN - SPIGOT_GAP, SPIGOT_H, Z_SPLIT)
    notches = []
    for a in JOINT_ANGLES + COL_ANGLES + (SEAM_ANGLE, SEAM_ANGLE + 180.0):
        notches.append(at(radial_block(120.0, 140.0, 21.0, Z_SPLIT - 1.0, Z_SPLIT + SPIGOT_H + 1.0), a))
    adds.append(spig.cut(*notches))
    adds += _seam_flanges(0.0, Z_SPLIT)
    # Mains cord: flat pad for a PG7 gland + zip-tie anchors up the wall.
    adds.append(at(radial_block(126.0, WALL_IN, 24.0, GLAND_Z - 12.0, GLAND_Z + 12.0), CORD_ANGLE))
    for z in (80.0, 150.0, 205.0):
        adds.append(at(_tie_anchor(z), CORD_ANGLE))
    body = body.fuse(*adds)

    cuts = []
    for a in JOINT_ANGLES:
        x, y = JOINT_SCREW_R * math.cos(math.radians(a)), JOINT_SCREW_R * math.sin(math.radians(a))
        cuts.append(insert_hole_down(x, y, Z_SPLIT, 7.0))
    cuts += _seam_holes(LOWER_SEAM_SCREW_Z)
    gland = bd.Pos(0, 0, GLAND_Z) * bd.Rot(0, 90, 0) * bd.Cylinder(GLAND_HOLE_D / 2, 20.0)
    cuts.append(at(bd.Pos(129.0, 0, 0) * gland, CORD_ANGLE))
    return body.cut(*cuts)


def lower_ring_half(side):
    half = _half(lower_ring_full(), side)
    skips = [(SEAM_ANGLE, 6.0), (SEAM_ANGLE + 180.0, 6.0), (CORD_ANGLE, 7.0)]
    half = one_solid(half.cut(*_slots(LOWER_SLOT_ROWS, side, skips)))
    half.label = f"shell_lower_{side}"
    half.color = SHELL_COLOR
    return half


# --------------------------------------------------------------------------------------
# Upper ring
# --------------------------------------------------------------------------------------
def upper_ring_full():
    body = _shell_tube(Z_SPLIT, Z_TOP, 1.0, 1.5)
    adds = []
    # Tabs that sit on the lower ring's bosses (printed on the bed).
    for a in JOINT_ANGLES:
        adds.append(at(radial_block(JOINT_R0, WALL_IN, JOINT_W, Z_SPLIT, Z_SPLIT + JOINT_TAB_T), a))
    # Columns that carry the transition plate.
    for a in COL_ANGLES:
        adds.append(at(radial_block(TPCOL_R0, WALL_IN, TPCOL_W, Z_SPLIT, Z_TP_BOT), a))
    adds += _seam_flanges(Z_SPLIT, Z_CAP_BOT)
    # Top lip the cap rests on, with a 45-degree underside.
    lip_bot = Z_CAP_BOT - LIP_T
    adds.append(
        revolve_profile(
            [
                (LIP_R0, Z_CAP_BOT),
                (WALL_IN, Z_CAP_BOT),
                (WALL_IN, lip_bot - (WALL_IN - LIP_R0)),
                (LIP_R0, lip_bot),
            ]
        )
    )
    # Inward tabs on the lip for the cap screws.
    for a in CAP_SCREW_ANGLES:
        adds.append(at(radial_block(112.0, LIP_R0 + 0.5, 14.0, lip_bot, Z_CAP_BOT), a))
        adds.append(at(gusset(LIP_R0 + 0.5, 112.0, 14.0, lip_bot), a))
    adds.append(at(_tie_anchor(262.0), CORD_ANGLE))
    body = body.fuse(*adds)

    cuts = []
    for a in JOINT_ANGLES:
        x, y = JOINT_SCREW_R * math.cos(math.radians(a)), JOINT_SCREW_R * math.sin(math.radians(a))
        cuts.append(cyl(M3_CLEAR_D / 2, JOINT_TAB_T + 1.0, Z_SPLIT - 0.5, x, y))
    for a in COL_ANGLES:
        x, y = TPCOL_SCREW_R * math.cos(math.radians(a)), TPCOL_SCREW_R * math.sin(math.radians(a))
        cuts.append(insert_hole_down(x, y, Z_TP_BOT, 7.0))
    for a in CAP_SCREW_ANGLES:
        x, y = CAP_SCREW_R * math.cos(math.radians(a)), CAP_SCREW_R * math.sin(math.radians(a))
        cuts.append(insert_hole_down(x, y, Z_CAP_BOT, 5.0))
    cuts += _seam_holes(UPPER_SEAM_SCREW_Z)
    return body.cut(*cuts)


def upper_ring_half(side):
    half = _half(upper_ring_full(), side)
    skips = [(SEAM_ANGLE, 6.0), (SEAM_ANGLE + 180.0, 6.0), (CORD_ANGLE, 7.0)]
    skips += [(a, 8.0) for a in COL_ANGLES]
    half = one_solid(half.cut(*_slots(UPPER_SLOT_ROWS, side, skips)))
    half.label = f"shell_upper_{side}"
    half.color = SHELL_COLOR
    return half


@model
def shell_lower_a():
    return lower_ring_half("a")


@model
def shell_lower_b():
    return lower_ring_half("b")


@model
def shell_upper_a():
    return upper_ring_half("a")


@model
def shell_upper_b():
    return upper_ring_half("b")


if __name__ == "__main__":
    shell_lower_a()
    shell_lower_b()
    shell_upper_a()
    shell_upper_b()
