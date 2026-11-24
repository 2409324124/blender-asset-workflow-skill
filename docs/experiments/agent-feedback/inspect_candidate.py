"""Inspect the added bounds and compare the saved original mesh and camera state."""
import json,sys
from pathlib import Path
import bpy
from mathutils import Vector
def numbers(seq):return tuple(round(float(v),5) for v in seq)
def signature(o):
    s={"type":o.type,"matrix":tuple(numbers(row) for row in o.matrix_world),"hide":(o.hide_render,o.hide_viewport)}
    ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get())
    if o.type=="MESH":
        s["vertices"]=tuple(numbers(v.co) for v in ev.data.vertices)
        s["faces"]=tuple(tuple(p.vertices) for p in ev.data.polygons)
        s["materials"]=[]
        for m in ev.data.materials:
            n=m.node_tree.nodes.get("Principled BSDF")
            s["materials"].append((m.name,numbers(n.inputs["Base Color"].default_value),n.inputs["Metallic"].default_value,n.inputs["Roughness"].default_value))
    if o.type=='CAMERA':s['ortho_scale']=o.data.ortho_scale
    if o.type=='LIGHT':s['light']=(o.data.energy,o.data.size,o.data.size_y)
    return s
args=sys.argv[sys.argv.index('--')+1:]
bpy.ops.wm.open_mainfile(filepath=str(Path(args[0]).resolve()))
original={o.name:signature(o) for o in bpy.context.scene.objects}
bpy.ops.wm.open_mainfile(filepath=str(Path(args[1]).resolve()))
scene=bpy.context.scene
current={o.name:o for o in scene.objects}
changed=[name for name in original if name not in current or signature(current[name])!=original[name]]
deps=bpy.context.evaluated_depsgraph_get()
new=[o for n,o in current.items() if n not in original]
verts=[]
for o in new:
    if o.type not in {'MESH','CURVE','FONT'} or o.hide_render:continue
    e=o.evaluated_get(deps);m=e.to_mesh()
    try:verts.extend(e.matrix_world@v.co for v in m.vertices)
    finally:e.to_mesh_clear()
lo=[min(p[i] for p in verts) for i in range(3)];hi=[max(p[i] for p in verts) for i in range(3)]
within=all(lo[i]>=m-.0001 and hi[i]<=M+.0001 for i,(m,M) in enumerate([(-.84,.84),(-.65,-.28),(.36,2.39)]))
Path(args[2]).write_text(json.dumps({'existing_objects_changed':changed,'added_objects':len(new),'min':numbers(lo),'max':numbers(hi),'bounds_pass':within},indent=2)+'\n')
