"""Real Blender geometry exercises transformed evaluated scene bounds."""
import bpy,importlib.util,sys
from pathlib import Path
p=Path(sys.argv[sys.argv.index('--')+1]);spec=importlib.util.spec_from_file_location('audit',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
bpy.ops.wm.read_factory_settings(use_empty=True)
for name,loc in [('Wall',(0,0,0)),('Furniture',(.75,0,0)),('Touch',(-1,0,0)),('Far',(5,0,0))]:
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);bpy.context.object.name=name
bpy.context.view_layer.update();items=m.scene_items(bpy.context.scene)
r=m.audit(items)
assert any(set(x['objects'])=={'Wall','Furniture'} for x in r['candidates'])
assert any(set(x['objects'])=={'Wall','Touch'} for x in r['contacts'])
assert not any('Far' in x['objects'] for k in ['candidates','contacts'] for x in r[k])
r=m.audit(items,[{'objects':['Wall','Furniture'],'reason':'Fixture intentionally embedded connector'}])
assert len(r['exemptions'])==1 and not r['candidates']
print('Actual mesh candidate/contact/separation/exemption checks passed')
