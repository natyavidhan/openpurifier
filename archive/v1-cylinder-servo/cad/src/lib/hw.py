"""Geometry helpers. Every function builds kernel objects only when called."""
import build123d as bd

from lib.params import INSERT_HOLE_D, M3_CBORE_D, M3_CLEAR_D


def _bottom():
    return (bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)


def cyl(r, h, z0=0.0, x=0.0, y=0.0):
    """Vertical cylinder of radius r from z0 to z0 + h at (x, y)."""
    return bd.Pos(x, y, z0) * bd.Cylinder(r, h, align=_bottom())


def box(sx, sy, sz, cx=0.0, cy=0.0, z0=0.0):
    """Box centred on (cx, cy) in XY, from z0 to z0 + sz."""
    return bd.Pos(cx, cy, z0) * bd.Box(sx, sy, sz, align=_bottom())


def tube(r0, r1, h, z0=0.0):
    return cyl(r1, h, z0) - cyl(r0, h, z0)


def ycyl(r, y0, y1, x=0.0, z=0.0):
    """Cylinder along Y from y0 to y1 at (x, z)."""
    return bd.Pos(x, (y0 + y1) / 2, z) * bd.Rot(90, 0, 0) * bd.Cylinder(r, abs(y1 - y0))


def xcyl(r, x0, x1, y=0.0, z=0.0):
    """Cylinder along X from x0 to x1 at (y, z)."""
    return bd.Pos((x0 + x1) / 2, y, z) * bd.Rot(0, 90, 0) * bd.Cylinder(r, abs(x1 - x0))


def at(shape, deg):
    """Rotate about the world Z axis."""
    return bd.Rot(0, 0, deg) * shape


def radial_block(r0, r1, w, z0, z1):
    """Block from radius r0 to r1 along +X, tangential width w (Y), from z0 to z1."""
    return box(r1 - r0, w, z1 - z0, cx=(r0 + r1) / 2, cy=0.0, z0=z0)


def gusset(r_outer, r_inner, w, z_top):
    """45-degree wedge under a ledge that runs from r_inner to r_outer at z_top (local +X radial).

    Keeps an inward ledge printable on an upright part without supports.
    """
    d = r_outer - r_inner
    tri = bd.Polygon((r_inner, z_top), (r_outer, z_top), (r_outer, z_top - d), align=None)
    return bd.extrude(bd.Plane.XZ * tri, amount=w / 2, both=True)


def revolve_profile(points):
    """Revolve a closed (r, z) polyline 360 degrees about Z."""
    face = bd.Plane.XZ * bd.Polygon(*points, align=None)
    return bd.revolve(face, bd.Axis.Z, 360)


def insert_hole_down(x, y, z_top, depth):
    """Heat-set insert pocket opening at z_top, going down."""
    return cyl(INSERT_HOLE_D / 2, depth, z_top - depth, x, y)


def clear_hole(x, y, z0, z1):
    return cyl(M3_CLEAR_D / 2, z1 - z0, z0, x, y)


def cbore_down(x, y, z_top, total, cbore_depth):
    """M3 clearance hole of length `total` below z_top with a counterbore from z_top."""
    return [
        cyl(M3_CLEAR_D / 2, total + 0.02, z_top - total - 0.01, x, y),
        cyl(M3_CBORE_D / 2, cbore_depth + 0.01, z_top - cbore_depth, x, y),
    ]


def one_solid(shape):
    """Fuse whatever a boolean returned into one solid (and fail loudly if empty)."""
    solids = shape.solids()
    if not solids:
        raise ValueError("boolean removed the whole part")
    if len(solids) == 1:
        return solids[0]
    return solids[0].fuse(*solids[1:])
