"""Conservative world-AABB review hints, NOT a mesh collision detector."""
import argparse, itertools, json, math, sys
from pathlib import Path


def classify_bounds(a, b, tolerance=1e-5):
    if not math.isfinite(tolerance) or tolerance < 0:
        raise ValueError('tolerance must be finite and nonnegative')
    for bound in (a,b):
        if len(bound)!=2 or any(len(v)!=3 for v in bound):
            raise ValueError('bounds must contain min/max 3-vectors')
        if not all(math.isfinite(v) for row in bound for v in row):
            raise ValueError('nonfinite bounds')
        if any(bound[0][i]>bound[1][i] for i in range(3)):
            raise ValueError('inverted bounds')
    overlap=[min(a[1][i],b[1][i])-max(a[0][i],b[0][i]) for i in range(3)]
    if min(overlap)<-tolerance:return 'separated',overlap
    if min(overlap)<=tolerance:return 'contact_or_near_contact',overlap
    return 'candidate',overlap


def audit(items, allowlist=(), tolerance=1e-5):
    if not math.isfinite(tolerance) or tolerance < 0:
        raise ValueError('tolerance must be finite and nonnegative')
    names={x['name'] for x in items}
    if len(names)!=len(items):raise ValueError('object names must be unique')
    exemptions={}
    for entry in allowlist:
        pair=entry.get('objects',[]);reason=entry.get('reason','')
        if len(pair)!=2 or pair[0]==pair[1] or not all(n in names for n in pair) or not reason.strip():
            raise ValueError('allowlist needs two existing distinct object names and a reason')
        key=tuple(sorted(pair))
        if key in exemptions:raise ValueError('duplicate allowlist pair')
        exemptions[key]=reason
    result={'candidates':[],'contacts':[],'exemptions':[],'separated_pairs':0,
      'method':'World-space axis-aligned bounding boxes; broad-phase hints only, not mesh penetration.',
      'tolerance_scene_units':tolerance,'objects':len(items)}
    for a,b in itertools.combinations(items,2):
        kind,depth=classify_bounds(a['bounds'],b['bounds'],tolerance)
        key=tuple(sorted((a['name'],b['name'])))
        if kind=='separated':result['separated_pairs']+=1;continue
        row={'objects':list(key),'axis_overlap_scene_units':depth}
        if key in exemptions:
            row.update(reason=exemptions[key],raw_classification=kind);result['exemptions'].append(row)
        elif kind=='candidate':result['candidates'].append(row)
        else:result['contacts'].append(row)
    return result


def scene_items(scene):
    import bpy
    deps=bpy.context.evaluated_depsgraph_get();items=[]
    # Include all mesh objects, even hidden roofs/walls: this is the saved asset,
    # not the currently convenient preview visibility state.
    for obj in scene.objects:
        if obj.type!='MESH':continue
        e=obj.evaluated_get(deps);mesh=e.to_mesh()
        try:
            points=[e.matrix_world@v.co for v in mesh.vertices]
            if points:
                items.append({'name':obj.name,'bounds':[[min(v[i] for v in points) for i in range(3)],
                                                       [max(v[i] for v in points) for i in range(3)]]})
        finally:e.to_mesh_clear()
    return items


def main():
    import bpy
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--report',type=Path,required=True);p.add_argument('--allowlist',type=Path)
    p.add_argument('--tolerance',type=float,default=1e-5)
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    if a.report.exists():raise FileExistsError(a.report)
    policy=json.loads(a.allowlist.read_text()) if a.allowlist else []
    result=audit(scene_items(bpy.context.scene),policy,a.tolerance)
    with a.report.open('x') as f:json.dump(result,f,indent=2,allow_nan=False)
    print('Review candidates:',len(result['candidates']))

if __name__=='__main__':main()
