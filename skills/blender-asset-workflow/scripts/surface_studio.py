"""Optional Blender 4.5 material and review-stage helpers for static mesh assets."""
from math import isfinite
from pathlib import Path
import os
import sys
from tempfile import TemporaryDirectory

_SIBLINGS = str(Path(__file__).resolve().parent)
if _SIBLINGS not in sys.path:
    sys.path.insert(0, _SIBLINGS)

# Base colors are linear RGB, not hex/sRGB swatches.
PROFILES = {
    "painted": ((0.038, 0.215, 0.185), 0.0, 0.32, 1.5, 0.0),
    "bare_metal": ((0.68, 0.71, 0.73), 1.0, 0.25, 1.5, 0.0),
    "rubber": ((0.025, 0.028, 0.033), 0.0, 0.66, 1.5, 0.0),
    "glass": ((0.98, 0.995, 1.0), 0.0, 0.06, 1.5, 1.0),
}
FIELDS = ("color", "metallic", "roughness", "ior", "transmission")
QUALITY = {"preview": (480, 360, 24), "final": (1200, 900, 96)}


def checked_number(value, name, low, high):
    if isinstance(value, bool) or not isinstance(value, (float, int)):
        raise ValueError(f"{name} requires a number")
    if not isfinite(value) or not low <= value <= high:
        raise ValueError(f"{name} must be finite and within [{low}, {high}]")
    return float(value)


def parameters(role, **overrides):
    if role not in PROFILES:
        raise ValueError(f"unknown surface role {role!r}")
    unknown = overrides.keys() - set(FIELDS)
    if unknown:
        raise ValueError(f"unknown parameters {sorted(unknown)}")
    result = dict(zip(FIELDS, PROFILES[role]))
    result.update(overrides)
    color = result["color"]
    if not isinstance(color, (tuple, list)) or len(color) != 3:
        raise ValueError("color requires three linear RGB channels")
    result["color"] = tuple(checked_number(v, "color", 0, 1) for v in color)
    for key in FIELDS[1:]:
        low, high = (1, 3) if key == "ior" else (0, 1)
        result[key] = checked_number(result[key], key, low, high)
    return result


def surface(name, role, **overrides):
    """Return a new material. Assignment and any reference-based wear are explicit."""
    import bpy

    values = parameters(role, **overrides)
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    shader = mat.node_tree.nodes.get("Principled BSDF")
    mat.diffuse_color = (*values["color"], 1)
    shader.inputs["Base Color"].default_value = mat.diffuse_color
    for key, socket in (("metallic", "Metallic"), ("roughness", "Roughness"),
                        ("ior", "IOR"), ("transmission", "Transmission Weight")):
        shader.inputs[socket].default_value = values[key]
    return mat


def micro_bump(material, *, frequency, distance, strength):
    """Optional native object-space noise. Apply scale first. GLB needs a baked normal."""
    frequency = checked_number(frequency, "frequency", 0.0001, 100000)
    distance = checked_number(distance, "distance", 0.000001, 10000)
    strength = checked_number(strength, "strength", 0, 1)
    tree = material.node_tree
    shader = tree.nodes.get("Principled BSDF") if tree else None
    if shader is None or shader.inputs["Normal"].is_linked:
        raise ValueError("expected the new Principled material with an open Normal input")
    coords = tree.nodes.new("ShaderNodeTexCoord")
    noise = tree.nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = frequency
    bump = tree.nodes.new("ShaderNodeBump")
    bump.inputs["Distance"].default_value = distance
    bump.inputs["Strength"].default_value = strength
    tree.links.new(coords.outputs["Object"], noise.inputs["Vector"])
    tree.links.new(noise.outputs["Fac"], bump.inputs["Height"])
    tree.links.new(bump.outputs["Normal"], shader.inputs["Normal"])


def studio(asset, *, direction=(1, -2.5, 1.1), exposure=0.0):
    """Link an asset collection to a new review scene. Source must be the active scene."""
    import bpy
    from mathutils import Vector

    from white_preview import fit_orthographic_camera

    source = bpy.context.scene
    deps = bpy.context.evaluated_depsgraph_get()
    direction = Vector(direction)
    if len(direction) != 3 or not all(isfinite(v) for v in direction) or direction.length == 0:
        raise ValueError("direction requires three finite coordinates and nonzero length")
    exposure = checked_number(exposure, "exposure", -10, 10)
    if asset == source.collection or any(obj.type not in {"MESH", "EMPTY"}
                                         or obj.instance_type != "NONE" for obj in asset.all_objects):
        raise ValueError("use a dedicated collection of static meshes and transform empties")
    points = []
    for obj in asset.all_objects:
        if obj.type != "MESH" or obj.hide_render:
            continue
        if obj.name not in source.objects:
            raise ValueError("asset meshes must be in the active scene")
        evaluated = obj.evaluated_get(deps)
        points.extend(evaluated.matrix_world @ Vector(p) for p in evaluated.bound_box)
    if not points or not all(isfinite(v) for p in points for v in p):
        raise ValueError("asset requires finite static mesh bounds")
    lo, hi = (Vector([fn(p[i] for p in points) for i in range(3)]) for fn in (min, max))
    center, span = (lo + hi) / 2, (hi - lo).length
    if span < 1e-5:
        raise ValueError("asset extent too small for this studio")
    scene = bpy.data.scenes.new("Surface review")
    scene.collection.children.link(asset)
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.seed = 29
    scene.cycles.use_denoising = True
    scene.render.resolution_x, scene.render.resolution_y, scene.cycles.samples = QUALITY["preview"]
    scene.render.resolution_percentage = 100
    scene.view_settings.view_transform = "AgX"
    scene.view_settings.look = "None"
    scene.view_settings.exposure = exposure
    scene.view_settings.gamma = 1
    scene.display_settings.display_device = "sRGB"
    scene.world = bpy.data.worlds.new("Neutral surround")
    scene.world.use_nodes = True
    background = scene.world.node_tree.nodes.get("Background")
    background.inputs["Color"].default_value = (0.45, 0.45, 0.45, 1)
    background.inputs["Strength"].default_value = 0.38

    def place(name, data, offset):
        obj = bpy.data.objects.new(name, data)
        scene.collection.objects.link(obj)
        obj.location = center + Vector(offset) * span
        obj.rotation_euler = (center - obj.location).to_track_quat("-Z", "Y").to_euler()
        return obj

    camera = place("Review camera", bpy.data.cameras.new("Review lens"), direction.normalized() * 2)
    camera.data.clip_start = span * 0.001
    camera.data.clip_end = span * 30
    scene.camera = camera
    # Background scripts can retain the old evaluation context after a window scene switch.
    with bpy.context.temp_override(scene=scene, view_layer=scene.view_layers[0]):
        scene.view_layers[0].update()
        fit_orthographic_camera(scene, camera, points, margin=1.12)
    for name, offset, width, height, power in (
        ("Key softbox", (-0.75, -0.77, 1.18), 0.95, 0.60, 130),
        ("Front fill", (0.80, -1.00, 0.48), 0.72, 0.42, 60),
        ("Rear strip", (0.42, 0.70, 0.84), 0.78, 0.21, 150),
    ):
        light = bpy.data.lights.new(name, "AREA")
        light.shape = "RECTANGLE"
        light.size, light.size_y, light.energy = width * span, height * span, power * span ** 2
        place(name, light, offset)

    floor = bpy.data.meshes.new("Stage floor")
    half = span * 12
    floor.from_pydata([(-half, -half, 0), (half, -half, 0), (half, half, 0),
                       (-half, half, 0)], [], [(0, 1, 2, 3)])
    floor_obj = bpy.data.objects.new("Stage floor", floor)
    scene.collection.objects.link(floor_obj)
    floor_obj.location = (center.x, center.y, lo.z - span * 0.0003)
    floor.materials.append(surface("Floor", "painted", color=(0.11, 0.12, 0.13), roughness=0.62))
    return scene


def render_still(scene, path, *, quality="preview", override=None):
    """Write one PNG in an existing directory, restoring the override and render path."""
    import bpy

    from png_privacy import clean_file

    path = Path(path).absolute()
    if path.suffix.lower() != ".png" or not path.parent.is_dir():
        raise ValueError("supply a PNG path inside an existing directory")
    if path.exists() or path.is_symlink():
        raise FileExistsError(path)
    if quality not in QUALITY:
        raise ValueError(f"unknown quality {quality!r}")
    scene.render.resolution_x, scene.render.resolution_y, scene.cycles.samples = QUALITY[quality]
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.image_settings.color_depth = "8"
    layer = scene.view_layers[0]
    previous = (layer.material_override, scene.render.filepath)
    try:
        layer.material_override = override
        with TemporaryDirectory(prefix=".surface-", dir=path.parent) as directory:
            candidate = Path(directory) / "render.png"
            scene.render.filepath = str(candidate)
            bpy.ops.render.render(scene=scene.name, write_still=True)
            clean_file(candidate)
            # Same-filesystem no-clobber publication, including competing writers.
            os.link(candidate, path)
    finally:
        layer.material_override, scene.render.filepath = previous
