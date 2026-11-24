"""Original portable compressor study. Run through Blender with -- OUT [--render]."""
import argparse
from math import atan2
from pathlib import Path
import sys

import bmesh
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills/blender-asset-workflow/scripts"))
from png_privacy import clean_file
from section_loft import SectionLoft, perimeter_samples

BASE = .57
ORANGE = (.83, .335, .062, 1)
BLACK = (.061, .076, .089, 1)
RUBBER = (.034, .044, .05, 1)
METAL = (.48, .53, .54, 1)


def name_color(obj, name, color):
    obj.name = name
    obj.color = color
    return obj


def block(name, xyz, dims, color, bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=xyz)
    obj = name_color(bpy.context.object, name, color)
    obj.dimensions = dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        mod = obj.modifiers.new("Cast edges", "BEVEL")
        mod.width = bevel
        mod.segments = 3
        obj.modifiers.new("Faces", "WEIGHTED_NORMAL")
    return obj


def disk(name, center, axis, radius, depth, color, sides=48):
    bpy.ops.mesh.primitive_cylinder_add(vertices=sides, radius=radius, depth=depth, location=center)
    obj = name_color(bpy.context.object, name, color)
    obj.rotation_euler = Vector(axis).to_track_quat('Z', 'Y').to_euler()
    return obj


def route(name, xyz, radius, color, cyclic=False):
    data = bpy.data.curves.new(name, 'CURVE')
    data.dimensions = '3D'
    data.resolution_u = 12
    data.bevel_depth = radius
    data.bevel_resolution = 3
    data.use_fill_caps = True
    spline = data.splines.new('BEZIER')
    spline.bezier_points.add(len(xyz) - 1)
    for anchor, point in zip(spline.bezier_points, xyz):
        anchor.co = point
        anchor.handle_left_type = anchor.handle_right_type = 'AUTO'
    spline.use_cyclic_u = cyclic
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    return name_color(obj, name, color)


def ring(w, h):
    # Keep bevel landmarks at fixed offsets. Corresponding diagonal edges are
    # parallel, so narrowing the ends leaves planar cheeks between stations.
    return [(-w+.08, 0), (w-.08, 0), (w, .095), (w, h-.44),
            (w-.10, h-.18), (w-.30, h), (-w+.30, h), (-w+.10, h-.18),
            (-w, h-.44), (-w, .095)]


def shroud(variant, output):
    if variant == 'before':
        # A fair straight extrusion already has the specified chamfered section.
        stations = [(-1.22, .62, 1.08), (1.28, .62, 1.08)]
    else:
        stations = [(-1.22, .46, .73), (-.86, .58, .96), (-.49, .62, 1.08),
                    (.29, .62, 1.08), (.73, .575, .965), (1.28, .43, .72)]
    solid = SectionLoft([(x, ring(w, h)) for x, w, h in stations])
    verts, faces = solid.mesh()
    mesh = bpy.data.meshes.new("Shroud sections")
    # Local (u, v, station) -> world (station, u, v + base), preserving winding.
    mesh.from_pydata([(s, u, BASE+v) for u, v, s in verts], [], faces)
    mesh.update()
    obj = bpy.data.objects.new("Formed shroud", mesh)
    bpy.context.collection.objects.link(obj)
    name_color(obj, obj.name, ORANGE)
    (output / f'{variant}.svg').write_text(solid.svg(), encoding='utf-8')


def common_parts():
    block("Undertray", (0, 0, .485), (2.67, 1.29, .17), BLACK, .065)
    for sign, label in ((-1, 'L'), (1, 'R')):
        y = sign * .67
        disk("Tire " + label, (-.83, y, .395), (0, 1, 0), .395, .17, RUBBER)
        disk("Pressed rim " + label, (-.83, sign*.767, .395), (0, 1, 0), .237, .04, METAL)
        disk("Wheel center " + label, (-.83, sign*.795, .395), (0, 1, 0), .13, .035, BLACK)
        disk("Axle cap " + label, (-.83, sign*.822, .395), (0, 1, 0), .061, .03, METAL, 12)
        block("Drop foot " + label, (.89, sign*.49, .25), (.16, .13, .4), METAL, .024)
        block("Foot pad " + label, (.89, sign*.49, .063), (.28, .24, .126), RUBBER, .04)
    for sign, label in ((-1, 'L'), (1, 'R')):
        route("Tow upright " + label, [(-1.05, sign*.5, .50), (-1.30, sign*.5, 1.13),
                                      (-1.57, sign*.49, 1.72), (-1.60, sign*.37, 1.79),
                                      (-1.60, sign*.30, 1.79)], .045, BLACK)
    disk("Handle grip", (-1.60, 0, 1.79), (0, 1, 0), .060, .66, RUBBER)
    block("Side access cover", (-.10, -.622, .973), (.73, .038, .40), BLACK, .04)
    for i in range(7):
        block(f"Cover vent {i}", (-.34 + i*.08, -.652, .98), (.032, .027, .20), METAL, .009)
    plate = [(-.30, -.155), (.30, -.155), (.33, -.12), (.33, .12),
             (.30, .155), (-.30, .155), (-.33, .12), (-.33, -.12)]
    for i, ((u, v), (tx, ty)) in enumerate(perimeter_samples(plate, 8, .035)):
        clip = block(f"Cover clip {i}", (-.10+u, -.651, .973+v), (.062, .019, .017), METAL)
        clip.rotation_euler.y = -atan2(ty, tx)
    # Exposed circular outlet grille on the end plane.
    disk("Intake surround", (1.29, 0, .936), (1, 0, 0), .262, .05, BLACK)
    disk("Screen", (1.323, 0, .936), (1, 0, 0), .223, .022, RUBBER)
    for i in range(-3, 4):
        z = i * .054
        width = 2 * (.205**2 - z*z)**.5
        block(f"Grille rib {i+3}", (1.34, 0, .936+z), (.022, width, .017), METAL, .004)
    # Flexible external service hose, supported by the rear handle.
    route("Service hose", [(-1.03, -.54, .53), (-1.35, -.66, .63),
                           (-1.38, -.63, 1.14), (-1.32, -.56, 1.27),
                           (-1.21, -.56, 1.08), (-1.20, -.59, .80)], .024, RUBBER)


def verify_mesh(variant):
    mesh = bpy.data.objects['Formed shroud'].data
    if mesh.validate(verbose=False):
        raise AssertionError('Blender repaired the saved shroud')
    bm = bmesh.new()
    try:
        bm.from_mesh(mesh)
        assert all(edge.is_manifold and edge.is_contiguous for edge in bm.edges)
        assert all(face.calc_area() > 1e-6 for face in bm.faces)
        assert bm.calc_volume(signed=True) > 0
    finally:
        bm.free()
    # Each side strip in this fixture was designed to be planar. Test the
    # actual stored triangle normals on both sides of every internal diagonal.
    sides = list(mesh.polygons)[1:-1]
    for left, right in zip(sides[::2], sides[1::2]):
        assert (left.normal - right.normal).length < 1e-5
    # Inspect world-space endpoints from the saved mesh against the brief.
    for x, expected_z, expected_width in [(1.28, 1.29, .86), (-1.22, 1.30, .92)]:
        section = [v.co for v in mesh.vertices if abs(v.co.x - x) < .00001]
        if variant == 'before':
            expected_z, expected_width = 1.65, 1.24
        assert abs(max(v.z for v in section) - expected_z) < .00001
        assert abs(max(v.y for v in section) - min(v.y for v in section) - expected_width) < .00001


def render(variant, output):
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_WORKBENCH'
    scene.render.resolution_x = 840
    scene.render.resolution_y = 560
    scene.render.resolution_percentage = 100
    shade = scene.display.shading
    shade.light = 'STUDIO'
    shade.color_type = 'OBJECT'
    shade.show_shadows = True
    shade.show_cavity = True
    shade.cavity_type = 'WORLD'
    shade.background_type = 'WORLD'
    scene.world = bpy.data.worlds.new("Neutral ground")
    scene.world.color = (.16, .18, .19)
    data = bpy.data.cameras.new("Review")
    camera = bpy.data.objects.new("Review", data)
    scene.collection.objects.link(camera)
    scene.camera = camera
    data.type = 'ORTHO'
    data.ortho_scale = 4.30
    for view, axis in [('iso', (3.9, -6.7, 3.2)), ('side', (0, -1, 0))]:
        direction = Vector(axis).normalized()
        camera.location = Vector((-.10, 0, .93)) + direction * 8
        camera.rotation_euler = (-direction).to_track_quat('-Z', 'Y').to_euler()
        path = output / f'{variant}-{view}.png'
        scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        clean_file(path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    parser.add_argument('--render', action='store_true')
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=True)
    if any(out.iterdir()):
        parser.error('choose an empty output directory')
    for variant in ('before', 'after'):
        bpy.ops.wm.read_factory_settings(use_empty=True)
        shroud(variant, out)
        common_parts()
        path = out / f'{variant}.blend'
        bpy.ops.wm.save_as_mainfile(filepath=str(path))
        bpy.ops.wm.open_mainfile(filepath=str(path))
        verify_mesh(variant)
        if args.render:
            render(variant, out)


if __name__ == '__main__':
    main()
