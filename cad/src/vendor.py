"""Simplified stand-ins for the purchased parts (not printed): used for fit checks and the
assembly view only. Dimensions come from lib.params and the parts' listings."""
import math

import build123d as bd

from lib.hw import box, cyl, tube, xcyl, ycyl
from lib.params import (
    FAN_COLLAR_L,
    FAN_COLLAR_OD,
    FAN_PLATE,
    FAN_PLATE_CORNER_R,
    FAN_PLATE_T,
    FILTER_D,
    FILTER_H,
    FILTER_TOP_ID,
    RELAY_H,
    RELAY_PCB,
)

IVORY = "#e9dfc4"
FILTER_GREY = "#6b6f73"
WHITE = "#f4f4f2"
BLACK = "#202124"


def filter_dummy():
    """Xiaomi-type cylindrical filter, bottom at z = 0: pleat pack + white end caps."""
    r = FILTER_D / 2
    pack = tube(FILTER_TOP_ID / 2 - 5, r - 0.5, FILTER_H - 8, 4)
    pack.color = FILTER_GREY
    top = tube(FILTER_TOP_ID / 2, r, 4, FILTER_H - 4)
    top.color = WHITE
    bottom = cyl(r, 4, 0)
    bottom.color = WHITE
    pack.label, top.label, bottom.label = "media", "top_ring", "closed_end"
    return bd.Compound(children=[pack, top, bottom], label="filter")


def fan_dummy():
    """HEWA Onyx 150: front face at z = 0 facing down (-Z), collar pointing up."""
    s = FAN_PLATE
    plate = bd.Pos(0, 0, 0) * bd.extrude(
        bd.RectangleRounded(s, s, FAN_PLATE_CORNER_R), amount=FAN_PLATE_T
    )
    plate = plate - cyl(74.0, FAN_PLATE_T + 1, -0.5)
    plate.color = IVORY
    collar = tube(FAN_COLLAR_OD / 2 - 2.5, FAN_COLLAR_OD / 2, FAN_COLLAR_L, FAN_PLATE_T)
    collar.color = IVORY
    hub = cyl(28.0, 30.0, FAN_PLATE_T + 2)
    blades = [
        bd.Rot(0, 0, i * 360 / 7) * bd.Pos(45, 0, FAN_PLATE_T + 12) * bd.Rot(25, 0, 0) * bd.Box(36, 22, 1.5)
        for i in range(7)
    ]
    rotor = hub.fuse(*blades)
    rotor.color = "#d8cfb2"
    plate.label, collar.label, rotor.label = "front_plate", "collar", "rotor"
    return bd.Compound(children=[plate, collar, rotor], label="hewa_fan")


def relay_module():
    """1-channel 5 V relay module (SRD-05VDC-SL-C on a board with optocoupler).
    Local: board bottom z = 0, long axis X, screw terminals at +X, input pins at -X.
    Size from common listings (VERIFY: RELAY_PCB, RELAY_H)."""
    L, W = RELAY_PCB
    pcb = box(L, W, 1.6)
    pcb.color = "#1f3a93"
    relay = box(19.0, 15.5, RELAY_H - 1.6, cx=6.5, z0=1.6)
    relay.color = "#2b6cb0"
    terminal = box(7.6, 15.2, 10.0, cx=L / 2 - 3.8, z0=1.6)
    terminal.color = "#3a7bd5"
    pins = box(2.5, 7.6, 8.5, cx=-L / 2 + 2.0, z0=1.6)
    pins.color = BLACK
    pcb.label, relay.label, terminal.label, pins.label = "pcb", "relay", "screw_terminal", "input_pins"
    return bd.Compound(children=[pcb, relay, terminal, pins], label="relay_module")


def esp32_c3_supermini():
    """ESP32-C3 SuperMini, board bottom at z = 0, USB-C at -X end."""
    pcb = box(22.5, 18.0, 1.0)
    pcb.color = "#1f3a93"
    usb = box(7.4, 9.0, 3.2, cx=-22.5 / 2 + 3.2, z0=1.0)
    usb.color = "#b0b0b0"
    chip = box(9.0, 9.0, 1.5, cx=3.0, z0=1.0)
    chip.color = BLACK
    pcb.label, usb.label, chip.label = "pcb", "usb_c", "soc"
    return bd.Compound(children=[pcb, usb, chip], label="esp32_c3_supermini")


def hlk_psu():
    """Hi-Link HLK-5M05 230 VAC -> 5 V 1 A module (VERIFY 38 x 23 x 18)."""
    b = box(38.0, 23.0, 18.0)
    b.color = BLACK
    b.label = "hlk_5m05"
    return b


def push_button_16():
    """16 mm panel push button with LED ring. Local: panel top face z = 0, axis Z."""
    bezel = cyl(9.5, 2.0, 0.0)
    bezel.color = "#c9ccd1"
    body = cyl(8.0, 30.0, -30.0)
    nut = cyl(10.0, 3.0, -5.0 - 3.0)
    lugs = box(8.0, 6.0, 6.0, z0=-36.0)
    rest = body.fuse(nut, lugs)
    rest.color = "#8a8f96"
    bezel.label, rest.label = "bezel", "body"
    return bd.Compound(children=[bezel, rest], label="push_button")


def wago_221_413():
    w = box(20.2, 13.3, 16.0)
    w.color = "#e8e8e8"
    w.label = "wago_221_413"
    return w


def fuse_holder():
    f = xcyl(6.0, -27.5, 27.5, z=6.0)
    f.color = BLACK
    f.label = "inline_fuse_holder"
    return f


def pg7_gland():
    """PG7 cable gland on +X axis: outside dome beyond x = 0, lock nut inside x < 0."""
    outside = xcyl(9.5, 0.0, 14.0)
    nut = xcyl(10.0, -5.0, -1.0)
    g = outside.fuse(nut)
    g.color = BLACK
    g.label = "pg7_gland"
    return g
