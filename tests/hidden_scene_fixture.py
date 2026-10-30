"""A stale scene whose meshes cannot all be removed by select/delete."""
import bpy, sys
from pathlib import Path
out=Path(sys.argv[sys.argv.index('--')+1])
bpy.ops.wm.read_factory_settings(use_empty=True)
for name,kind in [('HiddenStale','hidden'),('UnselectableStale','unselectable'),('ExcludedStale','excluded')]:
 bpy.ops.mesh.primitive_cube_add(location=(1000,1000,1000));obj=bpy.context.object;obj.name=name
 if kind=='hidden':obj.hide_set(True);obj.hide_viewport=True
 elif kind=='unselectable':obj.hide_select=True
 else:
  collection=bpy.data.collections.new('Excluded');bpy.context.scene.collection.children.link(collection)
  for old in list(obj.users_collection):old.objects.unlink(obj)
  collection.objects.link(obj)
  bpy.context.view_layer.layer_collection.children['Excluded'].exclude=True
bpy.ops.wm.save_as_mainfile(filepath=str(out))
