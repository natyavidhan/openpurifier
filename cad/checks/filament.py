"""Filament estimate for every printed part.

Slicer-like estimate: a 0.84 mm skin (2 walls x 0.42 mm, ~4-5 top/bottom layers) is solid,
the rest gets 15 % infill. Grams at 1.24 g/cm3 (PLA; PETG is ~2 % heavier).

Run:  PYTHONPATH=src cad run checks/filament.py          (smart version)
      PYTHONPATH=src cad run checks/filament.py basic    (basic version)
"""
import sys

import build123d as bd

import core
import electronics as el
import shell

SKIN = 0.84
INFILL = 0.15
DENSITY = 1.24e-3  # g/mm3


def grams(shape):
    v = sum(s.volume for s in shape.solids())
    a = sum(s.area for s in shape.solids())
    skin = min(v, a * SKIN)
    est = skin + INFILL * max(0.0, v - skin)
    return v * DENSITY, est * DENSITY


groups = {
    "shell": {
        "shell_lower": shell.shell_lower,
        "shell_upper": shell.shell_upper,
    },
    "plates": {
        "tray": core.tray,
        "transition_plate": core.transition_plate,
        "deck": core.deck,
        "top_cap": core.top_cap,
    },
    "electronics": {
        "esp32_holder": el.esp32_holder,
        "psu_box": el.psu_box,
        "psu_lid": el.psu_lid,
        "relay_box": el.relay_box,
        "relay_lid": el.relay_lid,
        "mains_cradle": el.mains_cradle,
    },
}

if len(sys.argv) > 1 and sys.argv[1] == "basic":
    groups["plates"]["deck"] = core.deck_basic
    groups["plates"]["top_cap"] = core.top_cap_basic
    groups["electronics"] = {"mains_cradle": el.mains_cradle}

total_solid = total_est = 0.0
for gname, parts in groups.items():
    gs = ge = 0.0
    for name, fn in parts.items():
        solid, est = grams(fn().shape)
        gs += solid
        ge += est
        print(f"  {name:20s} solid {solid:7.0f} g   sliced ~{est:6.0f} g")
    print(f"{gname:22s} solid {gs:7.0f} g   sliced ~{ge:6.0f} g\n")
    total_solid += gs
    total_est += ge
print(f"{'TOTAL':22s} solid {total_solid:7.0f} g   sliced ~{total_est:6.0f} g")
