"""Every printed part in its print orientation, centred on the bed with its bottom at z = 0.

Export:  cad run src/print_parts.py, then `cad model export <id> part.stl` for each id
(the STLs in print/smart and print/basic come from here).
"""
import build123d as bd
from cad import model

import core
import electronics as el
import shell

PRINT_COLOR = "#f2f1ec"


def _on_bed(shape, label, flip=False):
    if flip:
        shape = bd.Rot(180, 0, 0) * shape
    bb = shape.bounding_box()
    shape = bd.Pos(-(bb.min.X + bb.max.X) / 2, -(bb.min.Y + bb.max.Y) / 2, -bb.min.Z) * shape
    shape.label = label
    shape.color = PRINT_COLOR
    return shape


@model
def p01_shell_lower():
    return _on_bed(shell.shell_lower().shape, "shell_lower")


@model
def p02_shell_upper():
    return _on_bed(shell.shell_upper().shape, "shell_upper")


@model
def p03_tray():
    return _on_bed(core.tray().shape, "tray")


@model
def p04_transition_plate():
    return _on_bed(core.transition_plate().shape, "transition_plate", flip=True)


@model
def p05_deck():
    return _on_bed(core.deck().shape, "deck", flip=True)


@model
def p06_top_cap():
    return _on_bed(core.top_cap().shape, "top_cap", flip=True)


@model
def p07_relay_box():
    return _on_bed(el.relay_box().shape, "relay_box")


@model
def p08_relay_lid():
    return _on_bed(el.relay_lid().shape, "relay_lid")


@model
def p09_psu_box():
    return _on_bed(el.psu_box().shape, "psu_box")


@model
def p10_psu_lid():
    return _on_bed(el.psu_lid().shape, "psu_lid")


@model
def p11_esp32_holder():
    return _on_bed(el.esp32_holder().shape, "esp32_holder")


@model
def p12_mains_cradle():
    return _on_bed(el.mains_cradle().shape, "mains_cradle")


# ---- basic version (filter + fan only): these two replace the deck and the top cap ----
@model
def b05_deck_basic():
    return _on_bed(core.deck_basic().shape, "deck_basic", flip=True)


@model
def b06_top_cap_basic():
    return _on_bed(core.top_cap_basic().shape, "top_cap_basic", flip=True)


if __name__ == "__main__":
    for fn in (
        p01_shell_lower, p02_shell_upper, p03_tray, p04_transition_plate, p05_deck, p06_top_cap,
        p07_relay_box, p08_relay_lid, p09_psu_box, p10_psu_lid, p11_esp32_holder, p12_mains_cradle,
        b05_deck_basic, b06_top_cap_basic,
    ):
        fn()
