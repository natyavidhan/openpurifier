"""OpenPurifier - every dimension in one place (millimetres, Z up, z = 0 is the table).

Body: a rounded square, 216 x 216 x 423 mm, in two sections that each print in one piece.
Front of the purifier = -Y. Angles are degrees, CCW from +X; the corners sit at 45/135/225/315.
"Along the diagonal" distances are measured from the centre towards a corner.

Values marked VERIFY come from listings/drawings, not from a caliper. Measure your
parts, change the number here and re-run `cad run src/assembly.py`.
"""
import math

# --------------------------------------------------------------------------------------
# Purchased parts
# --------------------------------------------------------------------------------------
# PANCA filter = clone of Xiaomi M8R-FLH. Xiaomi datasheet: 200 x 200 x 293 mm. Bottom end closed.
FILTER_D = 200.0
FILTER_H = 293.0
FILTER_TOP_ID = 140.0      # VERIFY: top opening is not published (dummy only, seal does not need it)

# HEWA Onyx 150 mm (HEWA "product dimension" image)
FAN_PLATE = 180.0          # front plate 18 x 18 cm
FAN_PLATE_T = 10.0         # VERIFY: plate+grille thickness (95 total depth - 85 collar)
FAN_PLATE_CORNER_R = 3.0   # VERIFY: corner radius of the plate (3 = nearly sharp, worst case)
FAN_COLLAR_OD = 145.0      # rear collar 14.5 cm
FAN_COLLAR_L = 85.0        # collar length behind the plate 8.5 cm

# 1-channel 5 V relay module (SRD-05VDC-SL-C type, optocoupler, H/L trigger jumper)
RELAY_PCB = (50.0, 26.0)   # VERIFY: board size
RELAY_H = 17.0             # VERIFY: board bottom to relay top

# --------------------------------------------------------------------------------------
# Printer: Bambu 256 mm class. Every printed part must fit 250 x 250 x 250 (3 mm margin).
# --------------------------------------------------------------------------------------
BED_LIMIT = 250.0

# --------------------------------------------------------------------------------------
# Fasteners: M3 x 6 and M3 x 10 socket head screws, M3 x 4 mm heat-set brass inserts
# --------------------------------------------------------------------------------------
M3_CLEAR_D = 3.4
M3_CBORE_D = 6.5           # socket head 5.5 mm + clearance
M3_HEAD_H = 3.0
INSERT_HOLE_D = 4.0        # VERIFY against your inserts (4.0 suits ~4.5-5.0 mm knurl OD)
INSERT_L = 4.0

# --------------------------------------------------------------------------------------
# Soft closed-cell foam tape (gaskets / preload). Free -> compressed thickness.
# --------------------------------------------------------------------------------------
FILTER_GASKET_COMP = 3.0   # 10 x 5 mm tape on the transition plate seat, squeezed to 3
FILTER_PAD_COMP = 3.0      # 10 x 5 mm tape ring on the tray, squeezed to 3
FAN_GASKET_COMP = 1.5      # 6 x 3 mm tape under the fan front plate, squeezed to 1.5

# --------------------------------------------------------------------------------------
# Body: rounded square, lower section 0..240 (+ spigot) and upper section 240..top
# --------------------------------------------------------------------------------------
BODY_W = 216.0             # outside width
BODY_R = 20.0              # outside corner radius
WALL = 2.5
HALF_IN = BODY_W / 2 - WALL                    # 105.5: inside half-width (filter Ø200 -> 5.5 mm gap)
CORNER_R_IN = BODY_R - WALL                    # 17.5
CORNER_IN = (HALF_IN - CORNER_R_IN) * math.sqrt(2) + CORNER_R_IN   # 141.9 along the diagonal
CORNERS = (45.0, 135.0, 225.0, 315.0)
FACES = (0.0, 90.0, 180.0, 270.0)
Z_SPLIT = 240.0

SPIGOT_H = 6.0             # on the lower section, along the four flat sides only
SPIGOT_T = 2.2
SPIGOT_GAP = 0.4
SPIGOT_U = 78.0            # half-length along each side; the corners hold the joint columns

SLOT_W = 4.5               # intake slots on the flat sides
SLOT_PITCH = 9.25
SLOT_U = 74.0              # slot centres span -74..74 along each side
LOWER_SLOT_ROWS = ((22.0, 66.0), (72.0, 116.0), (122.0, 166.0), (172.0, 216.0))
UPPER_SLOT_ROWS = ((250.0, 300.0),)

# Corner columns (along the diagonal): feet + twist-lock at the bottom, ring joint at Z_SPLIT,
# transition-plate columns in the upper section, cap bosses at the top.
COL_R0 = 114.0             # inner face of every corner column
COL_W = 28.0               # width across the diagonal
COL_H = 12.0               # feet: the tray's ears rest on them
JOINT_R = 121.0            # ring-joint screw and TP screw: both at this radius ...
JOINT_T = -7.0             # ... the joint screw 7 mm to one side of the diagonal (CW)
TPSCREW_T = 7.0            # ... the TP screw 7 mm to the other side (CCW)
JOINT_TAB_T = 4.0          # floor of the upper section's column the joint screw clamps
JOINT_BOSS_H = 10.0        # lower section's boss under the joint (insert 7 deep)
JOINT_WELL_D = 7.0         # hex-key well above the joint screw

# Twist-lock: tray ears rest on the corner feet. Angles are measured from each corner's diagonal.
LOCK_INSERT_A = -9.0       # ears go up past the feet here ...
LOCK_A = 9.0               # ... and turn 18 deg CCW (seen from above) onto the landing
LAND_R0 = 105.5            # landing starts outside the tray's rim (R 103.5)
LAND_A0, LAND_A1 = 1.0, 17.0
STOP_A0 = 13.5             # 3 mm stop from here to LAND_A1
STOP_H = 3.0
DETENT_A = 4.0             # 1.2 mm ridge the ear clicks over


# --------------------------------------------------------------------------------------
# Vertical stack
# --------------------------------------------------------------------------------------
TRAY_T = 4.0
TRAY_RIM_R0, TRAY_RIM_R1 = 84.0, 103.5         # ring under the filter's closed end
TRAY_LIP_R0 = 101.0                            # centring lip R 101..103.5
TRAY_LIP_H = 6.0
TRAY_HUB_R = 18.0
TRAY_SPOKE_W = 12.0
TRAY_EAR_R0, TRAY_EAR_R1 = 103.0, 117.0
TRAY_EAR_W = 12.0
TRAY_EAR_T = 5.0

Z_TRAY_BOT = COL_H                                    # 12
Z_TRAY_TOP = Z_TRAY_BOT + TRAY_T                      # 16
Z_FILTER_BOT = Z_TRAY_TOP + FILTER_PAD_COMP           # 19
Z_FILTER_TOP = Z_FILTER_BOT + FILTER_H                # 312

# Transition plate (TP): seals the filter top ring below, carries the fan above
TP_T = 10.0
TP_HALF = 104.0            # rounded square 208 x 208, 1.5 mm inside the wall
TP_CORNER_R = 16.0
TRIM_R = 126.5             # TP and deck corners trimmed so they pass the cap bosses going in
TP_SEAT_R = 101.5          # filter seat recess (filter OD 200)
TP_SEAT_DEPTH = 6.0
TP_HOLE_R = 84.0           # clean-air opening, 168 mm

Z_TP_SEAT = Z_FILTER_TOP + FILTER_GASKET_COMP         # 315 (recess floor)
Z_TP_BOT = Z_TP_SEAT - TP_SEAT_DEPTH                  # 309
Z_TP_TOP = Z_TP_BOT + TP_T                            # 319

Z_FAN_FRONT = Z_TP_TOP + FAN_GASKET_COMP              # 320.5
Z_FAN_BACK = Z_FAN_FRONT + FAN_PLATE_T                # 330.5
Z_COLLAR_TOP = Z_FAN_BACK + FAN_COLLAR_L              # 415.5

# Deck: clamps the fan plate onto the TP with 4 posts, carries the electronics
DECK_T = 6.0
DECK_HOLE_R = 74.0         # around the 145 mm collar
DECK_POST_D = 10.0
DECK_POST_X, DECK_POST_Y = 97.5, 40.0          # +X side; the other three are this turned by 90 deg
Z_DECK_BOT = Z_FAN_BACK                               # 330.5
Z_DECK_TOP = Z_DECK_BOT + DECK_T                      # 336.5

# Top cap: sits inside the walls on 4 corner bosses
CAP_T = 5.0
CAP_HALF = 104.5
CAP_CORNER_R = 16.5
CAP_COLLAR_GAP = 2.5
Z_CAP_BOT = Z_COLLAR_TOP + CAP_COLLAR_GAP             # 418
Z_TOP = Z_CAP_BOT + CAP_T                             # 423
CAP_BOSS_R0 = 129.0        # along the diagonal
CAP_BOSS_W = 22.0
CAP_BOSS_H = 13.0
CAP_SCREW_R = 135.0
DUCT_R0, DUCT_R1 = 74.0, 77.0
DUCT_DROP = 12.0           # outlet duct overlaps the collar top
GRILLE_R = 72.0
BUTTON_HOLE_D = 16.2       # 16 mm panel push button, front-left corner of the cap

# Mains cord: PG7 gland low on the back (+Y) wall, cord runs up that wall at x = CORD_X
CORD_X = 72.0
GLAND_Z = 27.0
GLAND_HOLE_D = 12.7
LOWER_ANCHOR_Z = (80.0, 150.0, 205.0)
UPPER_ANCHOR_Z = (262.0,)


# --------------------------------------------------------------------------------------
# Small helpers on numbers only (no kernel objects at module level)
# --------------------------------------------------------------------------------------
def polar(r, deg):
    a = math.radians(deg)
    return (r * math.cos(a), r * math.sin(a))


def corner_point(corner_deg, r, t=0.0):
    """Point r along a corner's diagonal, shifted t across it (positive = CCW side)."""
    a = math.radians(corner_deg)
    return (r * math.cos(a) - t * math.sin(a), r * math.sin(a) + t * math.cos(a))


def deck_posts():
    """The four deck posts: one beside each side of the fan plate, turned by 90 deg each."""
    pts = []
    for k in range(4):
        a = math.radians(90.0 * k)
        x, y = DECK_POST_X, DECK_POST_Y
        pts.append((x * math.cos(a) - y * math.sin(a), x * math.sin(a) + y * math.cos(a)))
    return pts


BUTTON_POS = polar(108.0, 225.0)
