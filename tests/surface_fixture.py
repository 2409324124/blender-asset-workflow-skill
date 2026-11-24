"""Build an original analog bench gauge, then compare controlled native and GLB renders."""
import json
import math
from pathlib import Path
import struct
import sys

import bpy
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills/blender-asset-workflow/scripts"))
from surface_studio import QUALITY, micro_bump, render_still, studio, surface

out = Path(sys.argv[sys.argv.index("--") + 1]).resolve()
out.mkdir(parents=True, exist_ok=True)
if any(out.iterdir()):
    raise FileExistsError("experiment needs an empty output directory")
bpy.ops.wm.read_factory_settings(use_empty=True)
source = bpy.context.scene
asset = bpy.data.collections.new("Bench gauge")
source.collection.children.link(asset)
bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children[asset.name]

paint = surface("Deep enamel", "painted")
alloy = surface("Brushed alloy", "bare_metal")
rubber = surface("Graphite rubber", "rubber")
glass = surface("Lens glass", "glass", roughness=0.025, ior=1.48)
paper = surface("Ivory dial", "painted", color=(0.81, 0.76, 0.61), roughness=0.65)
ink = surface("Scale ink", "painted", color=(0.022, 0.025, 0.029), roughness=0.57)
orange = surface("Vermilion", "painted", color=(0.80, 0.105, 0.024), roughness=0.31)
dark = surface("Graphite enamel", "painted", color=(0.061, 0.074, 0.079), roughness=0.34)


def finish(obj, name, mat, bevel):
    obj.name = name
    obj.data.materials.append(mat)
    if bevel:
        modifier = obj.modifiers.new("Radiused edges", "BEVEL")
        modifier.width, modifier.segments = bevel, 4
        bpy.ops.object.modifier_apply(modifier=modifier.name)
    return obj


def block(name, mat, xyz, dims, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=xyz)
    obj = bpy.context.object
    obj.dimensions = dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    finish(obj, name, mat, bevel)
    if bevel:
        for face in obj.data.polygons:
            face.use_smooth = True
        normals = obj.modifiers.new("Smooth bevels and planar panels", "WEIGHTED_NORMAL")
        bpy.ops.object.modifier_apply(modifier=normals.name)
    return obj


def disk(name, mat, x, y, z, radius, depth, bevel=0.0, vertices=96):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth,
                                        location=(x, y, z), rotation=(math.pi/2, 0, 0))
    obj = finish(bpy.context.object, name, mat, bevel)
    for face in obj.data.polygons:
        face.use_smooth = abs(face.normal.z) < 0.999
    return obj


def lettering(value, x, y, z, size, mat):
    bpy.ops.object.text_add(location=(x, y, z), rotation=(math.pi/2, 0, 0))
    text_obj = bpy.context.object
    text_obj.data.body = value
    text_obj.data.size = size
    text_obj.data.align_x = "CENTER"
    text_obj.data.materials.append(mat)
    bpy.ops.object.convert(target="MESH")
    bpy.context.object.name = "Print " + value


for x in (-1.0, 1.0):
    for y in (-0.26, 0.26):
        block("Isolation foot", rubber, (x, y, 0.08), (0.42, 0.32, 0.16), 0.05)
block("Base rail", dark, (0, 0, 0.23), (2.72, 1.06, 0.19), 0.07)
block("Cast housing", paint, (0, 0, 1.09), (2.65, 0.98, 1.63), 0.115)
for x in (-1.13, 1.13):
    for z in (0.51, 1.67):
        disk("Service screw", alloy, x, -0.495, z, 0.039, 0.025, 0.004, 24)
        slot = block("Recess line", dark, (x, -0.509, z), (0.041, 0.002, 0.006))
        slot.rotation_euler.y = -0.4

cx, cz = -0.38, 1.12
disk("Bezel socket", dark, cx, -0.49, cz, 0.648, 0.08, 0.028)
disk("Metal bezel", alloy, cx, -0.54, cz, 0.610, 0.07, 0.012)
disk("Inner gasket", rubber, cx, -0.579, cz, 0.558, 0.022, 0.006)
disk("Gauge dial", paper, cx, -0.591, cz, 0.530, 0.015)
for n in range(33):
    angle = math.radians(-128 + n * 8)
    length = 0.069 if n % 4 == 0 else 0.031
    r = 0.476 - length / 2
    tick = block("Dial graduation", ink,
                 (cx + r * math.sin(angle), -0.601, cz + r * math.cos(angle)),
                 (0.017 if n % 4 == 0 else 0.008, 0.002, length))
    tick.rotation_euler.y = angle
for angle, value in ((-96, "0"), (-48, "2"), (0, "4"), (48, "6"), (96, "8")):
    a = math.radians(angle)
    lettering(value, cx + 0.365*math.sin(a), -0.604, cz + 0.365*math.cos(a)-0.028, 0.088, ink)
lettering("BAR", cx, -0.603, cz-0.23, 0.082, ink)
a = 0.60
needle = block("Indicator needle", orange, (cx+0.15*math.sin(a), -0.611, cz+0.15*math.cos(a)),
               (0.024, 0.009, 0.50), 0.003)
needle.rotation_euler.y = a
disk("Spindle", dark, cx, -0.622, cz, 0.062, 0.017, 0.006)
disk("Cover lens", glass, cx, -0.643, cz, 0.536, 0.015, 0.005)
block("Setting plate", dark, (0.71, -0.494, 1.10), (0.56, 0.045, 0.94), 0.021)
lettering("TRIM", 0.71, -0.52, 1.40, 0.09, paper)
disk("Knob collar", alloy, 0.71, -0.53, 1.17, 0.218, 0.07, 0.012)
disk("Fluted knob", rubber, 0.71, -0.61, 1.17, 0.173, 0.15, 0.016, 16)
block("Setting index", paper, (0.71, -0.687, 1.24), (0.021, 0.008, 0.113), 0.003)
disk("Pilot surround", alloy, 0.71, -0.527, 0.85, 0.075, 0.029, 0.005)
disk("Pilot jewel", orange, 0.71, -0.548, 0.85, 0.052, 0.028, 0.012)
# The latch rubs on these two faces. Assign substrate to those polygons only.
for x in (-0.72, 0.72):
    catch = block("Top catch", dark, (x, 0.05, 1.93), (0.29, 0.17, 0.076), 0.018)
    catch.data.materials.append(alloy)
    for face in catch.data.polygons:
        if face.normal.z > 0.999:
            face.material_index = 1
block("Carry grip", rubber, (0, 0.05, 2.10), (1.63, 0.16, 0.13), 0.052)
for x in (-0.71, 0.71):
    block("Grip mount", alloy, (x, 0.05, 2.01), (0.14, 0.12, 0.18), 0.026)
bpy.context.view_layer.update()
stage = studio(asset, direction=(1, -2.65, 0.98), exposure=-1.15)
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector
with bpy.context.temp_override(scene=stage, view_layer=stage.view_layers[0]):
    stage.view_layers[0].update()
    footprint = [world_to_camera_view(stage, stage.camera, obj.matrix_world @ Vector(p))
                 for obj in asset.all_objects for p in obj.bound_box]
    assert all(0.025 < uv[i] < 0.975 for uv in footprint for i in (0, 1)), "cropped asset"
gray = surface("Diagnostic clay", "painted", color=(0.42, 0.42, 0.42), roughness=0.54)
render_still(stage, out / "01-gray.png", override=gray)
render_still(stage, out / "02-portable.png")
assert stage.view_layers[0].material_override is None
if "--final" in sys.argv:
    render_still(stage, out / "06-final-native.png", quality="final")
    assert (stage.render.resolution_x, stage.render.resolution_y, stage.cycles.samples) == QUALITY["final"]


def roundtrip(stem):
    path = out / (stem + ".glb")
    bpy.ops.object.select_all(action="DESELECT")
    for obj in asset.all_objects:
        obj.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(path), export_format="GLB", use_selection=True, use_active_scene=True,
                              export_cameras=False, export_lights=False)
    data = path.read_bytes()
    json_size = struct.unpack_from("<I", data, 12)[0]
    document = json.loads(data[20:20 + json_size])
    temp = bpy.data.scenes.new("Empty reimport")
    bpy.context.window.scene = temp
    try:
        bpy.ops.import_scene.gltf(filepath=str(path))
        loaded = bpy.data.collections.new("Imported gauge")
        for obj in temp.objects:
            loaded.objects.link(obj)
        stage.collection.children.unlink(asset)
        stage.collection.children.link(loaded)
        try:
            render_still(stage, out / (stem + ".png"))
        finally:
            stage.collection.children.unlink(loaded)
            stage.collection.children.link(asset)
    finally:
        bpy.context.window.scene = source
    assert all(obj.type == "MESH" for obj in loaded.all_objects)
    assert len(loaded.all_objects) == len(asset.all_objects), (len(loaded.all_objects), len(asset.all_objects))
    assert "KHR_materials_transmission" in document["extensionsUsed"]
    assert len(document["nodes"]) == len(asset.all_objects)
    material_map = {m["name"]: m for m in document["materials"]}
    for material in (paint, alloy, rubber, glass):
        shader = material.node_tree.nodes.get("Principled BSDF")
        spec = material_map[material.name]["pbrMetallicRoughness"]
        for channel, socket in (("metallicFactor", "Metallic"), ("roughnessFactor", "Roughness")):
            assert abs(spec.get(channel, 1) - shader.inputs[socket].default_value) < 1e-5
        assert np.allclose(spec["baseColorFactor"], shader.inputs["Base Color"].default_value[:])
    lens = material_map[glass.name]["extensions"]
    assert abs(lens["KHR_materials_ior"]["ior"] - 1.48) < 1e-5
    assert lens["KHR_materials_transmission"]["transmissionFactor"] == 1
    wear_faces = [[document["materials"][p["material"]]["name"] for p in m["primitives"]]
                  for m in document["meshes"] if len(m["primitives"]) > 1]
    assert wear_faces == [[dark.name, alloy.name], [dark.name, alloy.name]]
    return {"nodes": len(document["nodes"]), "localized_wear_parts": len(wear_faces), "materials": len(document["materials"]),
            "extensions": sorted(document["extensionsUsed"]),
            "image_textures": len(document.get("textures", []))}


portable = roundtrip("03-portable-glb")
# Deliberately strong grain makes the unsupported procedural branch observable at review distance.
micro_bump(paint, frequency=36, distance=0.014, strength=0.72)
render_still(stage, out / "04-grain-native.png")
grain = roundtrip("05-grain-glb")


def pixels(filename):
    image = bpy.data.images.load(str(out / filename), check_existing=False)
    image.colorspace_settings.name = "Non-Color"
    width, height = image.size
    rgba = np.empty(len(image.pixels), dtype=np.float32)
    image.pixels.foreach_get(rgba)
    bpy.data.images.remove(image)
    return rgba.reshape(height, width, 4)[:, :, :3].copy()


def difference(first, second):
    a, b = pixels(first), pixels(second)
    delta = np.abs(a-b) * 255
    return {"mean_absolute_rgb_8bit": round(float(np.mean(delta)), 4),
            "pixel_fraction_any_channel_over_8": round(float(np.mean(delta.max(axis=2) > 8.001)), 5)}


report = {"blender": bpy.app.version_string, "engine": stage.render.engine,
          "view_transform": stage.view_settings.view_transform, "display": stage.display_settings.display_device,
          "look": stage.view_settings.look, "exposure": round(stage.view_settings.exposure, 3),
          "gamma": stage.view_settings.gamma, "resolution": [480, 360], "samples": stage.cycles.samples,
          "seed": stage.cycles.seed, "denoising": stage.cycles.use_denoising,
          "portable_glb": portable, "grain_glb": grain,
          "portable_vs_import": difference("02-portable.png", "03-portable-glb.png"),
          "grain_vs_import": difference("04-grain-native.png", "05-grain-glb.png"),
          "native_grain_effect": difference("02-portable.png", "04-grain-native.png"),
          "imported_grain_effect": difference("03-portable-glb.png", "05-grain-glb.png")}
(out / "metrics.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
