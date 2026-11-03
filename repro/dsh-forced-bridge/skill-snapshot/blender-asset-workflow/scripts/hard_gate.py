"""Minimal hard gate. Run: blender -b scene.blend --python hard_gate.py -- --out gate.json
   [--terrain Island_Terrain] [--ignore Ocean] [--props REGEX] [--tol 0.05]
   [--contact-whitelist a:b,c:d] [--strict-landing]
Exit 0 if export_allowed, 2 otherwise. AABB overlap is never a gate."""
import bpy, sys, json, math, re, argparse
from mathutils import Vector
a=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
p=argparse.ArgumentParser()
p.add_argument('--out',required=True); p.add_argument('--terrain',default='Island_Terrain')
p.add_argument('--ignore',default='Ocean'); p.add_argument('--props',default='.*')
p.add_argument('--tol',type=float,default=0.05); p.add_argument('--contact-whitelist',default='')
p.add_argument('--strict-landing',action='store_true'); o=p.parse_args(a)
ign=set(filter(None,o.ignore.split(',')))|{o.terrain}
wl={tuple(x.split(':')) for x in o.contact_whitelist.split(',') if ':' in x}
health=[]; landing=[]; hints=[]
dg=bpy.context.evaluated_depsgraph_get()
meshes=[ob for ob in bpy.context.scene.objects if ob.type=='MESH']
if not meshes: health.append("no mesh objects in scene")
for ob in meshes:
    me=ob.evaluated_get(dg).to_mesh()
    if len(me.vertices)==0: health.append(f"{ob.name}: empty mesh")
    elif any(not math.isfinite(c) for v in me.vertices for c in v.co): health.append(f"{ob.name}: non-finite vertex")
    if any(abs(s)<1e-6 for s in ob.scale): health.append(f"{ob.name}: zero scale")
    if any(not math.isfinite(c) for c in ob.matrix_world.translation): health.append(f"{ob.name}: non-finite transform")
    if len(me.polygons)==0 and len(me.vertices)>0: hints.append(f"{ob.name}: no faces")
    ob.evaluated_get(dg).to_mesh_clear()
t=bpy.data.objects.get(o.terrain)
if t is None: hints.append(f"terrain '{o.terrain}' not found; landing skipped")
else:
    te=t.evaluated_get(dg); inv=t.matrix_world.inverted()
    for ob in meshes:
        if ob.name in ign or not re.fullmatch(o.props,ob.name): continue
        if (ob.name,o.terrain) in wl or (o.terrain,ob.name) in wl: continue
        me=ob.evaluated_get(dg).to_mesh(); vs=[ob.matrix_world@v.co for v in me.vertices]
        ob.evaluated_get(dg).to_mesh_clear()
        if not vs: continue
        low=min(vs,key=lambda v:v.z)   # ray at lowest vertex XY (not centroid: avoids Palm_3 false flag)
        ok,loc,_,_=te.ray_cast(inv@Vector((low.x,low.y,1e4)),inv.to_3x3()@Vector((0,0,-1)))
        if not ok: landing.append({"object":ob.name,"issue":"no terrain below"}); continue
        gap=round(low.z-(t.matrix_world@loc).z,3)
        if gap>o.tol: landing.append({"object":ob.name,"issue":"floating","gap_m":gap})
if health: verdict="fail"; blocked="inspect health: "+"; ".join(health)
elif landing and o.strict_landing: verdict="fail"; blocked=f"strict landing: {len(landing)} prop(s) floating/unsupported"
elif landing or hints: verdict="degraded"; blocked=None
else: verdict="pass"; blocked=None
r={"verdict":verdict,"export_allowed":blocked is None,"blocked":blocked,
   "checks":{"health":{"hard":True,"issues":health},
             "landing":{"hard":o.strict_landing,"tol_m":o.tol,"issues":landing},
             "contact_whitelist":sorted(map(list,wl)),"aabb_overlap":"not a gate (hint tool only)"},
   "hints":hints,"blend":bpy.data.filepath}
json.dump(r,open(o.out,'w'),indent=1); print("GATE",verdict,"export_allowed=",r["export_allowed"])
sys.stdout.flush(); import os; os._exit(0 if r["export_allowed"] else 2)
