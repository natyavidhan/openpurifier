"""OpenPurifier - full assembly (printed parts + stand-ins for everything you buy)."""
import build123d as bd
from cad import model

import core
import electronics as el
import shell
import vendor
from lib.hw import at, box, cyl, tube, ycyl
from lib.layout import module_rot, module_xy
from lib.params import (
    BODY_W,
    BUTTON_POS,
    CORD_X,
    CORNERS,
    FAN_GASKET_COMP,
    FAN_PLATE,
    FILTER_GASKET_COMP,
    FILTER_PAD_COMP,
    GLAND_Z,
    HALF_IN,
    LOCK_A,
    Z_DECK_TOP,
    Z_FAN_FRONT,
    Z_FILTER_BOT,
    Z_FILTER_TOP,
    Z_TOP,
    Z_TP_TOP,
    Z_TRAY_BOT,
    Z_TRAY_TOP,
)

FOAM = "#2f2f2f"
TRAY_TURN = CORNERS[0] + LOCK_A           # ears at 54/144/234/324 deg: locked


def _on_deck(name, shape):
    cx, cy = module_xy(name)
    return bd.Pos(cx, cy, Z_DECK_TOP) * bd.Rot(0, 0, module_rot(name)) * shape


def _label(shape, label):
    shape.label = label
    return shape


def _gaskets():
    pad = tube(86.0, 96.0, FILTER_PAD_COMP, Z_TRAY_TOP)
    ring = tube(86.0, 97.0, FILTER_GASKET_COMP, Z_FILTER_TOP)
    s = FAN_PLATE
    fan = box(s - 1.0, s - 1.0, FAN_GASKET_COMP, z0=Z_TP_TOP) - box(s - 13.0, s - 13.0, FAN_GASKET_COMP + 1.0, z0=Z_TP_TOP - 0.5)
    out = []
    for g, name in ((pad, "tray_foam"), (ring, "filter_gasket"), (fan, "fan_gasket")):
        g.color = FOAM
        out.append(_label(g, name))
    return bd.Compound(children=out, label="foam")


def _gland():
    """PG7 gland in the back wall: dome outside, lock nut against the inner face."""
    dome = ycyl(9.5, BODY_W / 2, BODY_W / 2 + 14.0, x=CORD_X, z=GLAND_Z)
    nut = ycyl(10.0, HALF_IN - 4.0, HALF_IN, x=CORD_X, z=GLAND_Z)
    g = dome.fuse(nut)
    g.color = vendor.BLACK
    return _label(g, "pg7_gland")


def shell_group():
    parts = [
        _label(shell.shell_lower().shape, "shell_lower"),
        _label(shell.shell_upper().shape, "shell_upper"),
    ]
    return bd.Compound(children=parts, label="shell")


def core_group(basic=False):
    tr = bd.Pos(0, 0, Z_TRAY_BOT) * bd.Rot(0, 0, TRAY_TURN) * core.tray().shape
    deck = core.deck_basic() if basic else core.deck()
    cap = core.top_cap_basic() if basic else core.top_cap()
    parts = [
        _label(tr, "tray"),
        _label(core.transition_plate().shape, "transition_plate"),
        _label(deck.shape, "deck_basic" if basic else "deck"),
        _label(cap.shape, "top_cap_basic" if basic else "top_cap"),
    ]
    return bd.Compound(children=parts, label="core")


def purchased_group(basic=False):
    filt = bd.Pos(0, 0, Z_FILTER_BOT) * vendor.filter_dummy()
    fan = bd.Pos(0, 0, Z_FAN_FRONT) * vendor.fan_dummy()
    children = [_label(filt, "filter"), _label(fan, "hewa_fan"), _gaskets(), _gland()]
    if not basic:
        button = bd.Pos(BUTTON_POS[0], BUTTON_POS[1], Z_TOP) * vendor.push_button_16()
        children.append(_label(button, "push_button"))
    return bd.Compound(children=children, label="purchased")


def _mains_junction(fuse=True):
    wagos = [_label(bd.Pos(cx, -6.0, 2.0) * vendor.wago_221_413(), "wago") for cx in (-11.5, 11.5)]
    parts = [_label(el.mains_cradle().shape, "mains_cradle"), *wagos]
    if fuse:
        parts.append(_label(bd.Pos(0, 9.0, 5.0) * vendor.fuse_holder(), "fuse_holder"))
    return bd.Compound(children=parts, label="mains_junction")


def electronics_group():
    esp = bd.Compound(
        children=[_label(el.esp32_holder().shape, "esp32_holder"), _label(bd.Pos(0, 0, 2.0) * vendor.esp32_c3_supermini(), "esp32")],
        label="controller",
    )

    lid = bd.Pos(0, 0, el.PSU_IN[2] + el.PSU_WALL + 2.0) * bd.Rot(180, 0, 0) * el.psu_lid().shape
    psu = bd.Compound(
        children=[
            _label(el.psu_box().shape, "psu_box"),
            _label(bd.Pos(0, 0, el.PSU_WALL) * vendor.hlk_psu(), "hlk_5m05"),
            _label(lid, "psu_lid"),
        ],
        label="power_supply",
    )

    box_top = el.RELAY_IN[2] + el.RELAY_WALL
    rlid = bd.Pos(0, 0, box_top + 2.0) * bd.Rot(180, 0, 0) * el.relay_lid().shape
    relay = bd.Compound(
        children=[
            _label(el.relay_box().shape, "relay_box"),
            _label(bd.Pos(0, 0, el.RELAY_WALL + el.RELAY_LEDGE) * vendor.relay_module(), "relay_module"),
            _label(rlid, "relay_lid"),
        ],
        label="fan_relay",
    )

    return bd.Compound(
        children=[
            _on_deck("esp32_holder", esp),
            _on_deck("psu_box", psu),
            _on_deck("relay_box", relay),
            _on_deck("mains_cradle", _mains_junction()),
        ],
        label="electronics",
    )


@model
def assembly():
    return bd.Compound(
        children=[shell_group(), core_group(), purchased_group(), electronics_group()],
        label="openpurifier",
    )


@model
def assembly_basic():
    """Basic version: filter + fan only. The cord meets the fan's leads in two WAGOs on the deck;
    it's switched at the wall socket."""
    electrics = bd.Compound(children=[_on_deck("mains_cradle", _mains_junction(fuse=False))], label="electrics")
    return bd.Compound(
        children=[shell_group(), core_group(basic=True), purchased_group(basic=True), electrics],
        label="openpurifier_basic",
    )


if __name__ == "__main__":
    assembly()
    assembly_basic()
