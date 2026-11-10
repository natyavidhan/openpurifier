"""Electronics mounts that screw onto the deck (M3 x 6 into 4 mm inserts).

Local frame of every module: base on z = 0 (the deck's top face), +Y points out towards
the corner it sits in, +X runs across. lib.layout places them.

  esp32_holder - ESP32-C3 SuperMini cradle (front-left corner, under the push button)
  psu_box/lid  - HLK-5M05 230 V -> 5 V module, closed box
  relay_box/lid - 1-channel 5 V relay module that switches the fan's live wire, closed box
  mains_cradle - 2 x WAGO 221-413 + inline fuse holder (back-right corner, where the cord comes up)
"""
import build123d as bd
from cad import model

from lib.hw import box, cyl, one_solid, xcyl
from lib.params import M3_CLEAR_D, RELAY_H, RELAY_PCB

PART_COLOR = "#3c4043"


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


# ---- 1-channel relay module box + lid -----------------------------------------------
RELAY_WALL = 2.0
RELAY_LEDGE = 3.0                                   # board rests on side ledges, solder side clear
RELAY_IN = (RELAY_PCB[0] + 0.8, RELAY_PCB[1] + 0.8, RELAY_LEDGE + RELAY_H + 6.0)   # + room for the wires
RELAY_HOLE_X = (RELAY_PCB[0] + 0.8) / 2 + RELAY_WALL + 3.5
RELAY_PAD = (12.0, 12.0)                            # lid pad that holds the module down
RELAY_PAD_X = 6.5                                   # over the relay (screw terminals at +X)


@model
def relay_box():
    """Screw terminals (230 V) at the +X end, input pins (5 V, GND, IN) at the -X end."""
    ix, iy, iz = RELAY_IN
    ox, oy = ix + 2 * RELAY_WALL, iy + 2 * RELAY_WALL
    body = box(ox, oy, iz + RELAY_WALL, z0=0.0).fuse(box(2 * RELAY_HOLE_X + 7.0, 12.0, 3.0, z0=0.0))
    body = body.cut(box(ix, iy, iz + 1.0, z0=RELAY_WALL))                              # cavity
    ledges = [box(ix, 2.0, RELAY_LEDGE, cy=s * (iy / 2 - 1.0), z0=RELAY_WALL - 0.01) for s in (-1, 1)]
    body = body.fuse(*ledges)
    top = iz + RELAY_WALL
    cuts = [cyl(M3_CLEAR_D / 2, 5.0, -1.0, x, 0.0) for x in (-RELAY_HOLE_X, RELAY_HOLE_X)]
    cuts.append(box(RELAY_WALL + 2.0, 14.0, top - 9.0 + 1.0, cx=ox / 2 - RELAY_WALL / 2, z0=9.0))    # 230 V wires
    cuts.append(box(RELAY_WALL + 2.0, 10.0, top - 12.0 + 1.0, cx=-ox / 2 + RELAY_WALL / 2, z0=12.0))  # 5 V wires
    body = one_solid(body.cut(*cuts))
    body.label = "relay_box"
    body.color = PART_COLOR
    return body


@model
def relay_lid():
    """Lid in print orientation: flat face down, press-fit bars and hold-down pad up."""
    ix, iy, iz = RELAY_IN
    ox, oy = ix + 2 * RELAY_WALL, iy + 2 * RELAY_WALL
    lid = box(ox, oy, 2.0, z0=0.0)
    bars = [box(ix - 24.0, 1.6, 2.0, cy=s * (iy / 2 - 0.9), z0=2.0) for s in (-1, 1)]
    pad_h = iz - RELAY_LEDGE - RELAY_H - 0.3                                             # 0.3 above the relay
    pad = box(RELAY_PAD[0], RELAY_PAD[1], pad_h, cx=RELAY_PAD_X, z0=2.0)
    body = one_solid(lid.fuse(*bars, pad))
    body.label = "relay_lid"
    body.color = PART_COLOR
    return body


if __name__ == "__main__":
    esp32_holder()
    psu_box()
    psu_lid()
    relay_box()
    relay_lid()
    mains_cradle()
