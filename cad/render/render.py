"""Studio renders of the purifier for the README.

    cad run render.py <smart|basic> <hero|open> [--final]

Reads out/<variant>.glb (export it first, see README in this folder) and writes
../../docs/images/render_<variant>_<shot>.png with a transparent background and a soft shadow.
EEVEE without --final (a draft in seconds), Cycles on the GPU with it.
"""
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

from cad.blender import load

HERE = Path(__file__).resolve().parent
OUT = HERE.parent.parent / "docs" / "images"

variant, shot = sys.argv[1], sys.argv[2]
final = "--final" in sys.argv

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
model = load(HERE / "out" / f"{variant}.glb")
root = "openpurifier" if variant == "smart" else "openpurifier_basic"


def hide(name):
    """Hide every node whose last path segment starts with name (top_cap matches top_cap_basic)."""
    for path, obj in model.objects.items():
        if path.rsplit("/", 1)[-1].startswith(name):
            for o in [obj, *obj.children_recursive]:
                o.hide_render = True


# The body is 216 x 216 x 423: frame on it, not on the cord that pokes out of the bounds.
if shot == "hero":
    target = Vector((0, 0, 0.205))
    direction = Vector((1.0, -0.82, 0.62)).normalized()
    lens, size = 50, (1200, 1500)
    half = 0.31
else:  # open: upper body and cap lifted off to show what sits on the deck
    for p in ("shell_upper", "top_cap", "push_button"):
        hide(p)
    target = Vector((0, 0, 0.24))
    direction = Vector((1.0, -0.85, 0.95)).normalized()
    lens, size = 50, (1200, 1500)
    half = 0.31

scene.render.resolution_x, scene.render.resolution_y = size
aim = bpy.data.objects.new("aim", None)
aim.location = target
camera = bpy.data.objects.new("camera", bpy.data.cameras.new("camera"))
camera.data.lens = lens
view = math.tan(camera.data.angle / 2) * min(1, size[1] / size[0])
camera.location = target + (half / view) * direction
camera.constraints.new("TRACK_TO").target = aim
scene.collection.objects.link(aim)
scene.collection.objects.link(camera)
scene.camera = camera


def area(name, energy, loc, size_m, color=(1, 1, 1)):
    light = bpy.data.objects.new(name, bpy.data.lights.new(name, "AREA"))
    light.data.energy, light.data.size, light.data.color = energy, size_m, color
    light.location = Vector(loc)
    track = light.constraints.new("TRACK_TO")
    track.target = aim
    scene.collection.objects.link(light)


area("key", 34, (1.3, -0.25, 1.0), 0.9, (1.0, 0.97, 0.93))
area("fill", 5, (-1.1, -0.6, 0.6), 1.2, (0.92, 0.96, 1.0))
area("rim", 20, (-0.4, 1.0, 1.0), 0.6)
area("top", 4, (0.0, 0.0, 1.6), 1.0)

# Shadow-catching floor, so the PNG sits on any page colour.
bpy.ops.mesh.primitive_plane_add(size=6, location=(0, 0, 0))
floor = bpy.context.active_object
floor.is_shadow_catcher = True

scene.world = bpy.data.worlds.new("world")
bg = scene.world.node_tree.nodes["Background"]
bg.inputs["Color"].default_value = (0.9, 0.92, 0.95, 1)
bg.inputs["Strength"].default_value = 0.06
scene.render.film_transparent = True
scene.view_settings.view_transform = "AgX"
scene.view_settings.look = "AgX - Medium High Contrast"

if final:
    scene.render.engine = "CYCLES"
    prefs = bpy.context.preferences.addons["cycles"].preferences
    for kind in ("OPTIX", "CUDA", "METAL", "HIP", "ONEAPI"):
        try:
            prefs.compute_device_type = kind
        except TypeError:
            continue
        prefs.get_devices()
        if any(d.type == kind for d in prefs.devices):
            break
    for d in prefs.devices:
        d.use = d.type != "CPU"
    scene.cycles.device = "GPU" if any(d.use for d in prefs.devices) else "CPU"
    print("cycles device:", scene.cycles.device, [d.name for d in prefs.devices if d.use])
    scene.cycles.samples = 160
    scene.cycles.denoising_use_gpu = False
    scene.cycles.use_denoising, scene.cycles.denoiser = True, "OPENIMAGEDENOISE"
else:
    floor.hide_render = True  # EEVEE has no shadow catcher
    scene.render.engine = "BLENDER_EEVEE"
    scene.eevee.taa_render_samples = 64

OUT.mkdir(parents=True, exist_ok=True)
scene.render.filepath = str(OUT / f"render_{variant}_{shot}{'' if final else '_draft'}.png")
bpy.ops.render.render(write_still=True)
print("wrote", scene.render.filepath)
