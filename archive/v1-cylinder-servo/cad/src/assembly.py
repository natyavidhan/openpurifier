"""OpenPurifier - full assembly (printed parts + stand-ins for everything you buy)."""
import build123d as bd
from cad import model

import core
import electronics as el
import shell
import vendor
from lib.hw import at, box, cyl, tube, xcyl
from lib.layout import module_rot, module_xy
from lib.params import (
    BUTTON_POS,
    CORD_ANGLE,
    FAN_PLATE,
    FILTER_GASKET_COMP,
    FILTER_PAD_COMP,
    FAN_GASKET_COMP,
    GLAND_Z,
    SHELL_R_OUT,
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


def _on_deck(name, shape):
    cx, cy = module_xy(name)
    return bd.Pos(cx, cy, Z_DECK_TOP) * bd.Rot(0, 0, module_rot(name)) * shape


def _label(shape, label):
    shape.label = label
    return shape


def _gaskets():
    pad = cyl(95.0, FILTER_PAD_COMP, Z_TRAY_TOP)
    ring = tube(86.0, 97.0, FILTER_GASKET_COMP, Z_FILTER_TOP)
    s = FAN_PLATE
    fan = box(s - 1.0, s - 1.0, FAN_GASKET_COMP, z0=Z_TP_TOP) - box(s - 13.0, s - 13.0, FAN_GASKET_COMP + 1.0, z0=Z_TP_TOP - 0.5)
    out = []
    for g, name in ((pad, "tray_pad"), (ring, "filter_gasket"), (fan, "fan_gasket")):
        g.color = FOAM
        out.append(_label(g, name))
    return bd.Compound(children=out, label="foam")


def _gland():
    dome = xcyl(9.5, SHELL_R_OUT, SHELL_R_OUT + 14.0)
    nut = xcyl(10.0, 122.0, 126.0)
    g = dome.fuse(nut)
    g.color = vendor.BLACK
    return _label(at(bd.Pos(0, 0, GLAND_Z) * g, CORD_ANGLE), "pg7_gland")


def shell_group():
    parts = [
        _label(shell.shell_lower_a().shape, "shell_lower_a"),
        _label(shell.shell_lower_b().shape, "shell_lower_b"),
        _label(shell.shell_upper_a().shape, "shell_upper_a"),
        _label(shell.shell_upper_b().shape, "shell_upper_b"),
    ]
    return bd.Compound(children=parts, label="shell")


def core_group():
    tr = bd.Pos(0, 0, Z_TRAY_BOT) * bd.Rot(0, 0, -45) * core.tray().shape
    parts = [
        _label(tr, "tray"),
        _label(core.transition_plate().shape, "transition_plate"),
        _label(core.deck().shape, "deck"),
        _label(core.top_cap().shape, "top_cap"),
    ]
    return bd.Compound(children=parts, label="core")


def purchased_group():
    filt = bd.Pos(0, 0, Z_FILTER_BOT) * vendor.filter_dummy()
    fan = bd.Pos(0, 0, Z_FAN_FRONT) * vendor.fan_dummy()
    button = bd.Pos(BUTTON_POS[0], BUTTON_POS[1], Z_TOP) * vendor.push_button_16()
    return bd.Compound(
        children=[_label(filt, "filter"), _label(fan, "hewa_fan"), _gaskets(), _label(button, "push_button"), _gland()],
        label="purchased",
    )


def electronics_group():
    sw = el.switch_bracket().shape
    servo = el.servo_frame(vendor.servo_sg90())
    toggle = bd.Pos(el.TG_X, el.TG_Y, el.PLATE_TOP) * vendor.toggle_switch()
    fork = el.fork_horn_body()
    fork.color = el.FORK_COLOR
    actuator = bd.Compound(
        children=[_label(sw, "switch_bracket"), _label(servo, "sg90"), _label(toggle, "toggle_switch"), _label(fork, "fork_horn")],
        label="switch_actuator",
    )

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

    wagos = [_label(bd.Pos(cx, -6.0, 2.0) * vendor.wago_221_413(), "wago") for cx in (-11.5, 11.5)]
    fuse = _label(bd.Pos(0, 9.0, 5.0) * vendor.fuse_holder(), "fuse_holder")
    mains = bd.Compound(children=[_label(el.mains_cradle().shape, "mains_cradle"), *wagos, fuse], label="mains_junction")

    return bd.Compound(
        children=[
            _on_deck("switch_bracket", actuator),
            _on_deck("esp32_holder", esp),
            _on_deck("psu_box", psu),
            _on_deck("mains_cradle", mains),
        ],
        label="electronics",
    )


@model
def assembly():
    return bd.Compound(
        children=[shell_group(), core_group(), purchased_group(), electronics_group()],
        label="openpurifier",
    )


if __name__ == "__main__":
    assembly()
