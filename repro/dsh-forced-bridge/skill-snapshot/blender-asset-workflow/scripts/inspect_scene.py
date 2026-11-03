"""Blender background script: factual evaluated mesh inventory; no saving."""
import argparse, hashlib, json, math, sys
from pathlib import Path
import bpy

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--report', type=Path, required=True)
p.add_argument('--import-glb', type=Path)
a = p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
if a.report.exists(): raise FileExistsError(a.report)
source = a.import_glb or (Path(bpy.data.filepath) if bpy.data.filepath else None)
source_hash = hashlib.sha256(source.read_bytes()).hexdigest() if source else None
if a.import_glb:
    # Factory-empty state is independent of selection, collection exclusion,
    # visibility and editability in the previously loaded file. Never saved.
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(a.import_glb.resolve()))
deps = bpy.context.evaluated_depsgraph_get(); objects = []; problems = []
for obj in sorted(bpy.context.scene.objects, key=lambda o:o.name):
    if obj.type != 'MESH': continue
    evaluated = obj.evaluated_get(deps); mesh = evaluated.to_mesh()
    try:
        points = [evaluated.matrix_world @ v.co for v in mesh.vertices]
        finite = all(math.isfinite(c) for v in points for c in v)
        if not finite: problems.append(obj.name+': nonfinite coordinates')
        mesh.calc_loop_triangles()
        objects.append({'name':obj.name,'parent':obj.parent.name if obj.parent else None,
          'vertices':len(points),'polygons':len(mesh.polygons),'triangles':len(mesh.loop_triangles),
          'finite':finite,'bounds_min':[min(v[i] for v in points) for i in range(3)] if points and finite else None,
          'bounds_max':[max(v[i] for v in points) for i in range(3)] if points and finite else None,
          'matrix_world':[list(row) for row in evaluated.matrix_world],
          'materials':[m.name if m else None for m in mesh.materials],
          'hide_render':obj.hide_render})
    finally: evaluated.to_mesh_clear()
if not objects or not any(o['vertices'] for o in objects): problems.append('no nonempty mesh objects')
result={'source':str(source) if source else None,'source_sha256':source_hash,
 'blender_version':bpy.app.version_string,'unit_system':bpy.context.scene.unit_settings.system,
 'unit_scale':bpy.context.scene.unit_settings.scale_length,'meshes':objects,
 'basic_data_problems':problems,'scope':'Inventory only; not visual/topology/clearance certification.'}
with a.report.open('x') as f: json.dump(result,f,indent=2,allow_nan=False)
if problems: raise RuntimeError('; '.join(problems))
