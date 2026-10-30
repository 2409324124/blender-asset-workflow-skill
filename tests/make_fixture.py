"""Original neutral parented blocks. No historical or task-specific models."""
import bpy, sys
from pathlib import Path
from mathutils import Matrix
out=Path(sys.argv[sys.argv.index('--')+1]);out.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
root=bpy.data.objects.new('ModuleRoot',None);bpy.context.collection.objects.link(root);root.location=(2,3,0)
for name,loc,scale in [('Base',(0,0,.5),(2,1,.5)),('Upright',(.8,0,1.5),(.2,.3,.5))]:
 bpy.ops.mesh.primitive_cube_add(size=2,location=loc);o=bpy.context.object;o.name=name;o.scale=scale
 bpy.context.view_layer.update();world=o.matrix_world.copy();o.parent=root;o.matrix_world=world
bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(out/'fixture.blend'))
bpy.ops.export_scene.gltf(filepath=str(out/'fixture.glb'),export_format='GLB')
