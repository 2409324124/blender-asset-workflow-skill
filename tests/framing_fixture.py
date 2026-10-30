"""Projected fit assertions on original long boxes, multiple aspect ratios."""
import bpy, importlib.util, sys
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
script=Path(sys.argv[sys.argv.index('--')+1])
spec=importlib.util.spec_from_file_location('preview',script);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
bpy.ops.wm.read_factory_settings(use_empty=True);scene=bpy.context.scene
bpy.ops.mesh.primitive_cube_add();obj=bpy.context.object;obj.scale=(15,.7,1.3);obj.rotation_euler.z=.6
bpy.context.view_layer.update();points=[obj.matrix_world @ Vector(c) for c in obj.bound_box]
data=bpy.data.cameras.new('Camera');camera=bpy.data.objects.new('Camera',data);scene.collection.objects.link(camera);scene.camera=camera
for direction in [Vector((1,-1,.8)),Vector((0,-1,0)),Vector((0,0,1))]:
 direction.normalize();camera.location=direction*100;camera.rotation_euler=(-direction).to_track_quat('-Z','Y').to_euler()
 for width,height,px,py in [(1200,400,1,1),(400,1200,1,1),(512,512,1,1),(512,512,4,1),(512,512,1,4)]:
  scene.render.resolution_x=width;scene.render.resolution_y=height;scene.render.pixel_aspect_x=px;scene.render.pixel_aspect_y=py
  module.fit_orthographic_camera(scene,camera,points);bpy.context.view_layer.update()
  for point in points:
   uv=world_to_camera_view(scene,camera,point)
   assert .01 < uv.x < .99 and .01 < uv.y < .99,(width,height,px,py,list(uv))
print('15 projected-fit combinations passed')
