"""Where the electronics modules sit on the deck, and where their M3 x 6 screws go.

Each module is modelled in a local frame: base on z = 0 (the deck top), local +Y points
radially outward, local +X is tangential. It is placed at radius R on the given angle.
"""
import math

from lib.params import BUTTON_POS

# name: (angle_deg, radius_mm, mounting holes in the module's local frame)
MODULES = {
    "mains_cradle": (45.0, 100.0, ((-26.5, 0.0), (26.5, 0.0))),     # WAGOs + fuse
    "psu_box": (135.0, 100.0, ((-25.5, 0.0), (25.5, 0.0))),         # HLK-5M05 230 V -> 5 V
    "esp32_holder": (225.0, 100.0, ((-16.0, 0.0), (16.0, 0.0))),    # ESP32-C3 SuperMini
    "switch_bracket": (315.0, 98.0, ((-29.0, -10.0), (17.0, -10.0))),  # SG90 + toggle
}

__all__ = ["MODULES", "module_xy", "module_rot", "local_to_world", "deck_insert_points", "BUTTON_POS"]


def module_rot(name):
    return MODULES[name][0] - 90.0


def module_xy(name):
    a, r, _ = MODULES[name]
    return (r * math.cos(math.radians(a)), r * math.sin(math.radians(a)))


def local_to_world(name, lx, ly):
    cx, cy = module_xy(name)
    t = math.radians(module_rot(name))
    return (cx + lx * math.cos(t) - ly * math.sin(t), cy + lx * math.sin(t) + ly * math.cos(t))


def deck_insert_points():
    pts = []
    for name, (_, _, holes) in MODULES.items():
        for lx, ly in holes:
            pts.append(local_to_world(name, lx, ly))
    return pts
