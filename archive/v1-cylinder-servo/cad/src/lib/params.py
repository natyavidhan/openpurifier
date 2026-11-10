"""OpenPurifier - every dimension in one place (millimetres, Z up, z = 0 is the table).

Front of the purifier = -Y (the push button side). Angles are degrees, CCW from +X.

Values marked VERIFY come from listings/drawings, not from a caliper. Measure your
parts, change the number here and re-run `cad run src/assembly.py`.
"""

# --------------------------------------------------------------------------------------
# Purchased parts
# --------------------------------------------------------------------------------------
# PANCA filter = clone of Xiaomi M8R-FLH. Xiaomi datasheet: 200 x 200 x 293 mm.
FILTER_D = 200.0
FILTER_H = 293.0
FILTER_TOP_ID = 140.0      # VERIFY: top opening is not published (dummy only, seal does not need it)

# HEWA Onyx 150 mm (HEWA "product dimension" image)
FAN_PLATE = 180.0          # front plate 18 x 18 cm
FAN_PLATE_T = 10.0         # VERIFY: plate+grille thickness (95 total depth - 85 collar)
FAN_PLATE_CORNER_R = 3.0   # VERIFY: corner radius of the plate (3 = nearly sharp, worst case)
FAN_COLLAR_OD = 145.0      # rear collar 14.5 cm
FAN_COLLAR_L = 85.0        # collar length behind the plate 8.5 cm

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
FILTER_GASKET_COMP = 3.0   # 5 mm tape on the transition plate seat, squeezed to 3
FILTER_PAD_COMP = 3.0      # 5 mm pad on the tray, squeezed to 3
FAN_GASKET_COMP = 1.5      # 3 mm tape under the fan front plate, squeezed to 1.5

# --------------------------------------------------------------------------------------
# Shell (outer cylinder), split into a lower and an upper ring, each printed as 2 halves
# --------------------------------------------------------------------------------------
SHELL_R_IN = 130.0
SHELL_WALL = 2.5
SHELL_R_OUT = SHELL_R_IN + SHELL_WALL          # 132.5 -> OD 265
SEAM_ANGLE = 22.5          # the two vertical seams sit at 22.5 and 202.5 deg
Z_SPLIT = 240.0            # lower ring 0..240 (+ spigot), upper ring 240..top

SEAM_R0 = 119.0            # seam flanges span R 119 .. wall
SEAM_T_A = 7.0             # half A flange (carries the inserts)
SEAM_T_B = 5.0             # half B flange (screw heads)
SEAM_SCREW_R = 124.5

SPIGOT_H = 6.0
SPIGOT_T = 2.2
SPIGOT_GAP = 0.4

# --------------------------------------------------------------------------------------
# Vertical stack
# --------------------------------------------------------------------------------------
COL_H = 12.0               # 4 bayonet columns at the bottom = feet + tray supports
COL_R0 = 117.0
COL_W = 24.0
COL_ANGLES = (0.0, 90.0, 180.0, 270.0)

TRAY_T = 4.0
TRAY_R = 112.0
TRAY_EAR_R0, TRAY_EAR_R1 = 108.0, 124.0
TRAY_EAR_W = 17.0
TRAY_EAR_T = 5.0
TRAY_RING_R0, TRAY_RING_R1 = 101.5, 104.5      # filter centring ring
TRAY_RING_H = 6.0

Z_TRAY_BOT = COL_H                                    # 12
Z_TRAY_TOP = Z_TRAY_BOT + TRAY_T                      # 16
Z_FILTER_BOT = Z_TRAY_TOP + FILTER_PAD_COMP           # 19
Z_FILTER_TOP = Z_FILTER_BOT + FILTER_H                # 312

# Transition plate (TP): seals the filter top ring below, carries the fan above
TP_T = 10.0
TP_HALF = 97.0             # square 194 x 194
TP_CORNER_R = 127.0        # corners trimmed to this radius (shell wall at 130)
TP_EAR_R = 123.5
TP_EAR_W = 28.0
TP_SEAT_R = 101.5          # filter seat recess (filter OD 200)
TP_SEAT_DEPTH = 6.0
TP_HOLE_R = 84.0           # clean-air opening, 168 mm

Z_TP_SEAT = Z_FILTER_TOP + FILTER_GASKET_COMP         # 315 (recess floor)
Z_TP_BOT = Z_TP_SEAT - TP_SEAT_DEPTH                  # 309
Z_TP_TOP = Z_TP_BOT + TP_T                            # 319

Z_FAN_FRONT = Z_TP_TOP + FAN_GASKET_COMP              # 320.5
Z_FAN_BACK = Z_FAN_FRONT + FAN_PLATE_T                # 330.5
Z_COLLAR_TOP = Z_FAN_BACK + FAN_COLLAR_L              # 415.5

# Upper-ring columns that carry the TP
TPCOL_R0 = 112.0
TPCOL_W = 16.0
TPCOL_SCREW_R = 117.5

# Deck: clamps the fan plate onto the TP and carries the electronics
DECK_T = 6.0
DECK_EAR_R = 110.0
DECK_EAR_W = 20.0
DECK_HOLE_R = 74.0         # around the 145 mm collar
DECK_POST_R = 104.0        # posts stand on the TP ears
DECK_POST_D = 11.0
Z_DECK_BOT = Z_FAN_BACK                               # 330.5
Z_DECK_TOP = Z_DECK_BOT + DECK_T                      # 336.5

# Top cap
CAP_T = 5.0
CAP_R = 124.5              # 249 mm, sits on the shell's top lip
CAP_COLLAR_GAP = 2.5
Z_CAP_BOT = Z_COLLAR_TOP + CAP_COLLAR_GAP             # 418
Z_TOP = Z_CAP_BOT + CAP_T                             # 423
LIP_R0 = 118.0
LIP_T = 4.0
CAP_SCREW_R = 117.0
CAP_SCREW_ANGLES = (10.0, 100.0, 190.0, 280.0)   # 10 deg off the TP screws so a driver reaches those
DUCT_R0, DUCT_R1 = 74.0, 77.0
DUCT_DROP = 12.0           # outlet duct overlaps the collar top
GRILLE_R = 72.0
BUTTON_HOLE_D = 16.2       # 16 mm panel push button
BUTTON_POS = (0.0, -96.0)

# Lower/upper ring joint
JOINT_ANGLES = (45.0, 135.0, 225.0, 315.0)
JOINT_R0 = 117.0
JOINT_W = 14.0
JOINT_SCREW_R = 123.0
JOINT_TAB_T = 4.0

# Mains cord: PG7 gland low on the back-right, cord runs up the wall at this angle
CORD_ANGLE = 67.5
GLAND_Z = 24.0
GLAND_HOLE_D = 12.7

# --------------------------------------------------------------------------------------
# Small helpers on numbers only (no kernel objects at module level)
# --------------------------------------------------------------------------------------
import math


def polar(r, deg):
    a = math.radians(deg)
    return (r * math.cos(a), r * math.sin(a))
