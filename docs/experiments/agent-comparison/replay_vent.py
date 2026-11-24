"""Create the civilian fixture or install and render a mesh submission in Blender 4.5.

Use the build operation under --factory-startup. Reopen its saved candidate.blend
with the render operation in a fresh Blender process. Each operation writes to a
new directory. An omitted mesh submission builds the blank baseline.
"""
import argparse
import json
import math
from pathlib import Path
import sys

import bpy
from mathutils import Vector


ANCHOR = Vector((0, -.231, 1.16))
EXTENT = Vector((.70, .70, .15))


def make_material(name, rgb, roughness, metallic=0):
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    surface = material.node_tree.nodes.get('Principled BSDF')
    surface.inputs['Base Color'].default_value = (*rgb, 1)
    surface.inputs['Roughness'].default_value = roughness
    surface.inputs['Metallic'].default_value = metallic
    material.diffuse_color = (*rgb, 1)
    return material


def make_box(name, location, dimensions, material):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    obj.data.materials.append(material)


def build_fixture():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    enamel = make_material('Enamel', (.16, .29, .30), .45)
    graphite = make_material('Graphite', (.055, .067, .07), .7)
    make_box('Housing', (0, 0, 1.16), (1.66, .46, 1.68), enamel)
    make_box('Plinth', (0, 0, .15), (1.90, .65, .30), graphite)
    for x in (-.58, .58):
        make_box('Pedestal', (x, 0, .32), (.22, .36, .22), graphite)


def install(path):
    if path.stat().st_size > 10 * 1024 * 1024:
        raise ValueError('Mesh submission exceeds 10 MiB')
    parts = json.loads(path.read_text())['parts']
    if not isinstance(parts, list) or len(parts) > 100:
        raise ValueError('Expected at most 100 parts')
    for index, part in enumerate(parts):
        vertices, faces, rgb = part['v'], part['f'], part['rgb']
        roughness, metallic = part['rough'], part['metal']
        if not (3 <= len(vertices) <= 2400 and 1 <= len(faces) <= 2400):
            raise ValueError('Part exceeds vertex/face limits')
        if len(rgb) != 3 or not all(0 <= x <= 1 for x in [*rgb, roughness, metallic]):
            raise ValueError('Invalid material parameter')
        world = []
        for x, y, depth in vertices:
            if not (all(math.isfinite(v) for v in (x, y, depth)) and
                    max(abs(x), abs(y)) <= 1.005 and -.051 <= depth <= 1.005):
                raise ValueError('Vertex outside the allowed patch')
            world.append((ANCHOR.x + x * EXTENT.x, ANCHOR.y - depth * EXTENT.z,
                          ANCHOR.z + y * EXTENT.y))
        for face in faces:
            if not (3 <= len(face) <= 100 and all(type(j) is int and 0 <= j < len(world) for j in face)):
                raise ValueError('Invalid face indices')
        name = f'Study {index:03d}'
        mesh = bpy.data.meshes.new('Study surface')
        mesh.from_pydata(world, [], faces)
        mesh.update()
        obj = bpy.data.objects.new(name, mesh)
        bpy.context.scene.collection.objects.link(obj)
        obj.data.materials.append(make_material(name, rgb, roughness, metallic))


def render(output, clean_file):
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = 4
    scene.cycles.use_denoising = True
    scene.render.threads_mode = 'FIXED'
    scene.render.threads = 3
    scene.render.resolution_x, scene.render.resolution_y = 420, 320
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = False
    scene.render.image_settings.file_format = 'PNG'
    scene.render.use_stamp = False
    scene.world = bpy.data.worlds.new('Study world')
    scene.world.use_nodes = True
    background = scene.world.node_tree.nodes['Background']
    background.inputs[0].default_value = (.32, .32, .32, 1)
    background.inputs[1].default_value = .8
    radius = .70
    for position, energy, size in [((-2, -3, 4), 190, 2.5), ((3, -2, 1), 85, 2)]:
        location = ANCHOR + Vector(position) * radius
        bpy.ops.object.light_add(type='AREA', location=location)
        light = bpy.context.object
        light.rotation_euler = (ANCHOR - location).to_track_quat('-Z', 'Y').to_euler()
        light.data.energy = energy * radius**2
        light.data.shape = 'DISK'
        light.data.size = size * radius
    scene.view_settings.view_transform = 'AgX'
    scene.view_settings.exposure, scene.view_settings.gamma = 0, 1
    clay = make_material('Neutral studio', (.44, .44, .44), .65)
    views = [('front', (0, -1, .015)), ('oblique', (.60, -1, .28)), ('context', (.35, -1, .18))]
    for name, direction in views:
        local = name != 'context'
        center = ANCHOR if local else Vector((0, 0, .95))
        scale = radius if local else 1.
        axis = Vector(direction).normalized()
        bpy.ops.object.camera_add(location=center + axis * max(1., scale * 5))
        camera = bpy.context.object
        camera.rotation_euler = (-axis).to_track_quat('-Z', 'Y').to_euler()
        camera.data.type = 'ORTHO'
        camera.data.ortho_scale = scale * (2.90 if local else 3.2)
        camera.data.clip_start = .001
        scene.camera = camera
        for layer in scene.view_layers:
            layer.material_override = clay if name == 'oblique' else None
        image = output / f'{name}.png'
        scene.render.filepath = str(image)
        bpy.ops.render.render(write_still=True)
        # Blender can store the source file path even when the visible stamp is off.
        clean_file(image)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=['build', 'render'])
    parser.add_argument('output', type=Path)
    parser.add_argument('--mesh', type=Path)
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    if args.operation == 'build':
        build_fixture()
        if args.mesh:
            install(args.mesh)
        bpy.context.preferences.filepaths.save_version = 0
        bpy.ops.wm.save_as_mainfile(filepath=str(output / 'candidate.blend'), compress=True)
    else:
        sys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'skills/blender-asset-workflow/scripts'))
        from png_privacy import clean_file
        render(output, clean_file)
