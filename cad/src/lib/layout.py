"""Where the electronics modules sit on the deck, and where their M3 x 6 screws go.

Each module is modelled in a local frame: base on z = 0 (the deck top), local +Y points
out towards the corner it sits in, local +X runs across. It is placed at distance R along
that corner's diagonal. The corners keep clear of the collar, the 4 deck posts and the
mains-cord notch at the back.
"""
import math

from lib.params import BUTTON_POS

# name: (corner_deg, radius_mm, mounting holes in the module's local frame)
MODULES = {
    "mains_cradle": (45.0, 96.0, ((-26.5, 0.0), (26.5, 0.0))),      # back-right: WAGOs + fuse, cord arrives here
    "psu_box": (135.0, 96.0, ((-25.5, 0.0), (25.5, 0.0))),          # back-left: HLK-5M05 230 V -> 5 V
    "esp32_holder": (225.0, 96.0, ((-16.0, 0.0), (16.0, 0.0))),     # front-left: ESP32-C3, under the button
    "relay_box": (315.0, 96.0, ((-30.9, 0.0), (30.9, 0.0))),        # front-right: relay switching the fan
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


def deck_insert_points(names=None):
    """Insert positions for the given modules (all of them by default)."""
    pts = []
    for name, (_, _, holes) in MODULES.items():
        if names is not None and name not in names:
            continue
        for lx, ly in holes:
            pts.append(local_to_world(name, lx, ly))
    return pts
