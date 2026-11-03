"""Read-only, scene-specific surface-crossing evidence for experiment C.

Run in Blender against the saved C scene. This is an experiment audit, not a
general collision certificate or a change to the installed modeling skill.
"""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import sys

import bpy
from mathutils.bvhtree import BVHTree
from mathutils.geometry import intersect_ray_tri


def crosses_edge(triangle, start, end, epsilon):
    normal = (triangle[1] - triangle[0]).cross(triangle[2] - triangle[0])
    if normal.length < epsilon * epsilon:
        return False
    normal.normalize()
    first = normal.dot(start - triangle[0])
    second = normal.dot(end - triangle[0])
    # Only strict transverse crossings; tangency/coplanarity remain unresolved.
    if not ((first > epsilon and second < -epsilon) or
            (second > epsilon and first < -epsilon)):
        return False
    direction = end - start
    length = direction.length
    if length <= epsilon:
        return False
    hit = intersect_ray_tri(*triangle, direction / length, start, True)
    if hit is None:
        return False
    position = (hit - start).dot(direction / length)
    return epsilon < position < length - epsilon


def crosses_triangles(first, second, epsilon):
    for triangle, edges in ((first, second), (second, first)):
        for index in range(3):
            if crosses_edge(triangle, edges[index], edges[(index + 1) % 3], epsilon):
                return True
    return False


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    if args.report.exists():
        parser.error('report already exists')
    epsilon = 1e-6
    frames = ('Window_Arch_Frame', 'Window_Arch_OuterTrim', 'Window_Crossbar')
    pillows = ('Pillow_Back_L', 'Pillow_Back_R', 'Pillow_Front_L', 'Pillow_Front_R')
    pairs = [(a, b) for a in ('Curtain_Left', 'Curtain_Right') for b in frames]
    pairs += [(a, b) for a in ('Bunny_Body', 'Bunny_Head')
              for b in ('Pillow_Back_R', 'Pillow_Front_R')]
    pairs += list(itertools.combinations(pillows, 2))
    scene = Path(bpy.data.filepath)
    before = hashlib.sha256(scene.read_bytes()).hexdigest()
    bpy.context.view_layer.update()
    graph = bpy.context.evaluated_depsgraph_get()
    geometry = {}
    for name in sorted({name for pair in pairs for name in pair}):
        obj = bpy.data.objects[name]
        evaluated = obj.evaluated_get(graph)
        mesh = evaluated.to_mesh()
        try:
            mesh.calc_loop_triangles()
            vertices = [evaluated.matrix_world @ vertex.co for vertex in mesh.vertices]
            triangles = [tuple(face.vertices) for face in mesh.loop_triangles]
            tree = BVHTree.FromPolygons(vertices, triangles, all_triangles=True, epsilon=0.0)
            geometry[name] = (obj.type, vertices, triangles, tree)
        finally:
            evaluated.to_mesh_clear()
    results = []
    for first, second in pairs:
        fa, va, ta, ba = geometry[first]
        fb, vb, tb, bb = geometry[second]
        candidates = ba.overlap(bb)
        confirmed = 0
        for ia, ib in candidates:
            a = [va[index] for index in ta[ia]]
            b = [vb[index] for index in tb[ib]]
            confirmed += int(crosses_triangles(a, b, epsilon))
        results.append({'objects': [first, second], 'original_types': [fa, fb],
                        'candidate_triangle_pairs': len(candidates),
                        'transverse_triangle_pairs': confirmed,
                        'surface_crossing_confirmed': confirmed > 0})
    assert hashlib.sha256(scene.read_bytes()).hexdigest() == before
    report = {
        'scene_sha256': before,
        'blender': bpy.app.version_string,
        'method': 'World-space evaluated triangles, including converted curves; BVH candidates verified by strict edge/triangle crossing.',
        'epsilon_scene_units': epsilon,
        'scope': '16 explicitly selected pairs in the saved C scene; no rendering or scene save.',
        'limitations': 'Positive results confirm surface crossing, not penetration depth or visual severity. Negative results do not exclude containment, coplanar contact or untested pairs. Triangle counts are not defect counts. Intended joints need semantic review.',
        'pairs': results,
    }
    with args.report.open('x', encoding='utf-8') as output:
        json.dump(report, output, ensure_ascii=False, indent=2)
        output.write('\n')
    print('SELECTED_SURFACE_AUDIT', sum(row['surface_crossing_confirmed'] for row in results),
          'positive pairs of', len(results), 'scene_sha256', before)


if __name__ == '__main__':
    main()
