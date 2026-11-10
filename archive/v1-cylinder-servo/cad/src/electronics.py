"""Electronics mounts that screw onto the deck (M3 x 6 into 4 mm inserts).

Local frame of every module: base on z = 0 (the deck's top face), +Y radially outward,
+X tangential. lib.layout places them.

switch_bracket - SG90 servo whose fork horn flips an MTS-101 toggle switch (fan mains).
                 Servo shaft is horizontal (along Y), 52 mm above the base, straight
                 above the toggle lever; +/-22 deg from centre flips the lever either way.
"""
import build123d as bd
from cad import model

from lib.hw import box, cyl, one_solid, xcyl, ycyl
from lib.params import M3_CLEAR_D

PART_COLOR = "#3c4043"
FORK_COLOR = "#e37400"

# ---- switch bracket geometry -------------------------------------------------------
TG_X, TG_Y = 0.0, 12.0            # toggle bushing axis
PLATE_TOP = 22.0                  # toggle mounting plate top face
PLATE_T = 3.0
TOGGLE_HOLE_D = 6.3               # M6 bushing
SHAFT_Z = 52.0                    # servo output shaft axis (parallel to Y)
SERVO_CX = -5.65                  # SG90 shaft sits 5.65 mm off the case centre
SERVO_Y_OFF = TG_Y - 1.5 - 29.7   # servo-local z (shaft axis) -> bracket y
SERVO_TAB_HOLE_DX = 13.8          # SG90 tab holes, from case centre (VERIFY)
WALL_Y0 = SERVO_Y_OFF + 18.4      # tabs' shaft-side face bears on the wall
WALL_T = 3.0
FORK_Y0 = TG_Y - 1.5              # fork plate on top of the stock horn
FORK_T = 2.5
FORK_TINE_BOTTOM = 35.5         # tines grip only the top 3 mm of the lever: snaps at 13 deg, jams at 19 -> throw 16 deg


def servo_frame(shape):
    """Place something given in SG90-local coordinates into the bracket frame."""
    return bd.Pos(SERVO_CX, SERVO_Y_OFF, SHAFT_Z) * bd.Rot(-90, 0, 0) * shape


def _yz_rib(x0, x1, y_wall, y_far, z_base, z_top):
    """Triangular rib in the YZ plane between x0 and x1, from the wall back to y_far."""
    tri = bd.Polygon((y_wall, z_base), (y_far, z_base), (y_wall, z_top), align=None)
    face = bd.Plane.YZ.offset(x0) * tri
    return bd.extrude(face, amount=x1 - x0)


def switch_bracket_body():
    wall_x0, wall_x1 = -24.0, 12.5
    parts = [
        # base: screw strip + tower foot
        box(54.0, 17.2, 3.0, cx=-6.0, cy=-15.0 + 17.2 / 2, z0=0.0),
        box(21.0, 18.3 + 0.01, 3.0, cx=0.0, cy=(WALL_Y0 + 20.5) / 2, z0=0.0),
        # servo wall
        box(wall_x1 - wall_x0, WALL_T, 61.0, cx=(wall_x0 + wall_x1) / 2, cy=WALL_Y0 + WALL_T / 2, z0=0.0),
        # stiffening ribs behind the wall (clear of the servo case)
        _yz_rib(-24.0, -21.0, WALL_Y0 + 0.01, -15.0, 0.0, 40.0),
        _yz_rib(9.5, 12.5, WALL_Y0 + 0.01, -15.0, 0.0, 40.0),
        # toggle tower: two side walls, back wall, top plate
        box(2.5, 20.5 - WALL_Y0, PLATE_TOP - PLATE_T, cx=-9.25, cy=(WALL_Y0 + 20.5) / 2, z0=0.0),
        box(2.5, 20.5 - WALL_Y0, PLATE_TOP - PLATE_T, cx=9.25, cy=(WALL_Y0 + 20.5) / 2, z0=0.0),
        box(21.0, 2.5, PLATE_TOP - PLATE_T, cx=0.0, cy=19.25, z0=0.0),
        box(21.0, 20.5 - WALL_Y0, PLATE_T, cx=0.0, cy=(WALL_Y0 + 20.5) / 2, z0=PLATE_TOP - PLATE_T),
    ]
    body = parts[0].fuse(*parts[1:])
    win_x0, win_x1 = SERVO_CX - 11.25 - 0.3, SERVO_CX + 11.25 + 0.3
    cuts = [
        box(win_x1 - win_x0, WALL_T + 2.0, 12.2 + 0.6, cx=(win_x0 + win_x1) / 2, cy=WALL_Y0 + WALL_T / 2, z0=SHAFT_Z - 6.4),
        cyl(TOGGLE_HOLE_D / 2, PLATE_T + 2.0, PLATE_TOP - PLATE_T - 1.0, TG_X, TG_Y),
        box(3.0, 10.0, 9.0, cx=-9.25, cy=TG_Y, z0=-0.5),                 # toggle wire exit
    ]
    for dx in (-SERVO_TAB_HOLE_DX, SERVO_TAB_HOLE_DX):                    # servo tab screws (M2 self-tappers)
        cuts.append(ycyl(0.8, WALL_Y0 - 0.5, WALL_Y0 + WALL_T + 0.5, x=SERVO_CX + dx, z=SHAFT_Z))
    for x, y in ((-29.0, -10.0), (17.0, -10.0)):                          # M3 x 6 to the deck
        cuts.append(cyl(M3_CLEAR_D / 2, 5.0, -1.0, x, y))
    return one_solid(body.cut(*cuts))


def fork_horn_body(tine_bottom=None):
    """Fork that sits on the servo's stock single-arm horn (arm pointing UP), in the
    bracket frame. The tines leave 10 mm between them: the 3 mm lever thrown 15 degrees
    reaches x = +/-4.2, so neither end position touches a tine while the servo rests at centre."""
    def plate(sx, sz, cx, z0):
        return bd.Pos(cx, FORK_Y0 + FORK_T / 2, z0 + sz / 2) * bd.Box(sx, FORK_T, sz)

    gap, tine = 10.0, 2.5
    tx = gap / 2 + tine / 2
    tine_top = SHAFT_Z - 8.0
    if tine_bottom is None:
        tine_bottom = FORK_TINE_BOTTOM
    hub = ycyl(7.5, FORK_Y0, FORK_Y0 + FORK_T, x=TG_X, z=SHAFT_Z)
    pieces = [
        plate(9.0, 18.0, TG_X, SHAFT_Z),                    # upper tab over the stock horn arm
        plate(7.0, 8.0, TG_X, SHAFT_Z - 8.0),               # stem
        plate(gap + 2 * tine, 3.0, TG_X, SHAFT_Z - 11.0),   # crossbar, 2.5 mm above the lever tip
        plate(tine, tine_top - tine_bottom, TG_X + tx, tine_bottom),
        plate(tine, tine_top - tine_bottom, TG_X - tx, tine_bottom),
    ]
    body = hub.fuse(*pieces)
    cuts = [ycyl(2.5, FORK_Y0 - 1.0, FORK_Y0 + FORK_T + 1.0, x=TG_X, z=SHAFT_Z)]   # horn screw access
    for dz in (8.0, 14.0):                                                          # horn arm holes
        cuts.append(ycyl(0.75, FORK_Y0 - 1.0, FORK_Y0 + FORK_T + 1.0, x=TG_X, z=SHAFT_Z + dz))
    return one_solid(body.cut(*cuts))


@model
def switch_bracket():
    b = switch_bracket_body()
    b.label = "switch_bracket"
    b.color = PART_COLOR
    return b


@model
def fork_horn():
    """Print flat: the fork laid on its face."""
    f = bd.Rot(90, 0, 0) * fork_horn_body()
    f = bd.Pos(-f.bounding_box().center().X, -f.bounding_box().center().Y, -f.bounding_box().min.Z) * f
    f.label = "fork_horn"
    f.color = FORK_COLOR
    return f


# ---- ESP32-C3 SuperMini cradle -------------------------------------------------------
ESP_W, ESP_D = 22.9, 18.4          # board 22.5 x 18 + clearance


@model
def esp32_holder():
    base = box(40.0, 26.0, 2.0, z0=0.0)
    walls = [
        box(ESP_W + 2.0, 2.0, 3.5, cx=1.0, cy=ESP_D / 2 + 1.0, z0=2.0),
        box(ESP_W + 2.0, 2.0, 3.5, cx=1.0, cy=-ESP_D / 2 - 1.0, z0=2.0),
        box(2.0, ESP_D + 4.0, 3.5, cx=ESP_W / 2 + 1.0, cy=0.0, z0=2.0),   # USB-C end (-X) left open
    ]
    body = base.fuse(*walls)
    cuts = [cyl(M3_CLEAR_D / 2, 4.0, -1.0, x, 0.0) for x in (-16.0, 16.0)]
    cuts += [box(2.0, 4.0, 4.0, cx=x, cy=0.0, z0=-1.0) for x in (-6.0, 6.0)]  # zip tie over the board
    body = one_solid(body.cut(*cuts))
    body.label = "esp32_holder"
    body.color = PART_COLOR
    return body


# ---- HLK-5M05 box + press-fit lid ----------------------------------------------------
PSU_IN = (38.8, 23.8, 21.0)   # HLK 18 tall + 1 clearance + 2 for the lid lip
PSU_WALL = 2.0


@model
def psu_box():
    ix, iy, iz = PSU_IN
    ox, oy = ix + 2 * PSU_WALL, iy + 2 * PSU_WALL
    body = box(ox, oy, iz + PSU_WALL, z0=0.0).fuse(box(59.0, 12.0, 3.0, z0=0.0))   # box + screw tabs
    cuts = [box(ix, iy, iz + 1.0, z0=PSU_WALL)]                                      # cavity last
    cuts += [cyl(M3_CLEAR_D / 2, 5.0, -1.0, x, 0.0) for x in (-25.5, 25.5)]
    cuts.append(box(PSU_WALL + 2.0, 8.0, 8.0, cx=-ox / 2 + PSU_WALL / 2, cy=-5.0, z0=iz + PSU_WALL - 7.0))  # 230 V in
    cuts.append(box(PSU_WALL + 2.0, 8.0, 8.0, cx=ox / 2 - PSU_WALL / 2, cy=5.0, z0=iz + PSU_WALL - 7.0))   # 5 V out
    body = one_solid(body.cut(*cuts))
    body.label = "psu_box"
    body.color = PART_COLOR
    return body


@model
def psu_lid():
    """Lid in print orientation: flat face down, press-fit lip up."""
    ix, iy, _ = PSU_IN
    ox, oy = ix + 2 * PSU_WALL, iy + 2 * PSU_WALL
    lid = box(ox, oy, 2.0, z0=0.0)
    lip = box(ix - 0.2, iy - 0.2, 2.0, z0=2.0) - box(ix - 3.4, iy - 3.4, 2.5, z0=2.0)
    body = one_solid(lid.fuse(lip))
    body.label = "psu_lid"
    body.color = PART_COLOR
    return body


# ---- WAGO 221-413 x 2 + inline fuse holder ------------------------------------------
@model
def mains_cradle():
    base = box(60.0, 32.0, 2.0, z0=0.0)
    pockets = []
    for cx in (-11.5, 11.5):
        outer = box(20.6 + 3.2, 13.7 + 3.2, 7.0, cx=cx, cy=-6.0, z0=2.0)
        inner = box(20.6, 13.7, 7.5, cx=cx, cy=-6.0, z0=2.0)
        pockets.append(outer - inner)
    saddles = []
    for cx in (-16.0, 16.0):
        blk = box(6.0, 14.0, 9.0, cx=cx, cy=9.0, z0=2.0)
        groove = xcyl(6.3, cx - 4.0, cx + 4.0, y=9.0, z=11.0)
        saddles.append(blk - groove)
    body = base.fuse(*pockets, *saddles)
    cuts = [cyl(M3_CLEAR_D / 2, 4.0, -1.0, x, 0.0) for x in (-26.5, 26.5)]
    cuts += [box(2.0, 4.0, 4.0, cx=cx, cy=9.0, z0=-1.0) for cx in (-21.0, 21.0)]  # fuse zip tie
    body = one_solid(body.cut(*cuts))
    body.label = "mains_cradle"
    body.color = PART_COLOR
    return body


if __name__ == "__main__":
    switch_bracket()
    fork_horn()
    esp32_holder()
    psu_box()
    psu_lid()
    mains_cradle()
