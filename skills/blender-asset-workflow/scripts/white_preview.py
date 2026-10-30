"""Cheap Workbench overview, without writing any blend file."""
import argparse, sys, math
from pathlib import Path
import bpy
from mathutils import Vector

def fit_orthographic_camera(scene, camera, points, margin=1.12):
    """Fit world-space points in the actual frame, including pixel aspect ratio."""
    # Rotation/translation are set by caller. view_frame accounts for Blender's
    # sensor-fit convention, resolution and non-square pixel aspect.
    camera.data.type = 'ORTHO'
    camera.data.ortho_scale = 1.0
    bpy.context.view_layer.update()
    local = [camera.matrix_world.inverted() @ point for point in points]
    frame = camera.data.view_frame(scene=scene)
    half_x = max(abs(v.x) for v in frame)
    half_y = max(abs(v.y) for v in frame)
    camera.data.ortho_scale = margin * max(
        max(abs(v.x) for v in local) / half_x,
        max(abs(v.y) for v in local) / half_y,
        1e-6)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--view',choices=['iso','front','side','top'],default='iso')
    p.add_argument('--size',type=int,default=1000)
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    if a.output.exists(): raise FileExistsError(a.output)
    if not 64 <= a.size <= 4096: p.error('size must be 64..4096')
    scene=bpy.context.scene; deps=bpy.context.evaluated_depsgraph_get(); points=[]
    for obj in scene.objects:
        if obj.type=='MESH' and obj.visible_get() and not obj.hide_render:
            e=obj.evaluated_get(deps)
            points.extend(e.matrix_world @ Vector(corner) for corner in e.bound_box)
    if not points or not all(math.isfinite(x) for v in points for x in v): raise ValueError('no finite visible mesh bounds')
    lo=Vector([min(v[i] for v in points) for i in range(3)]); hi=Vector([max(v[i] for v in points) for i in range(3)])
    center=(lo+hi)/2; diameter=(hi-lo).length
    if diameter <= 0: raise ValueError('zero extent')
    direction=Vector({'iso':(1,-1,.8),'front':(0,-1,0),'side':(1,0,0),'top':(0,0,1)}[a.view]).normalized()
    camera_data=bpy.data.cameras.new('PreviewCamera'); camera=bpy.data.objects.new('PreviewCamera',camera_data)
    scene.collection.objects.link(camera); camera.location=center+direction*diameter*2
    camera.rotation_euler=(-direction).to_track_quat('-Z','Y').to_euler()
    camera_data.type='ORTHO'
    camera_data.clip_start=max(diameter/10000,.0001); camera_data.clip_end=diameter*10
    scene.camera=camera; scene.render.engine='BLENDER_WORKBENCH'
    scene.render.resolution_x=a.size; scene.render.resolution_y=a.size; scene.render.resolution_percentage=100
    fit_orthographic_camera(scene, camera, points)
    shade=scene.display.shading; shade.light='STUDIO'; shade.color_type='SINGLE'; shade.single_color=(.8,.8,.8)
    shade.show_shadows=True; shade.show_cavity=True; shade.cavity_type='BOTH'; shade.background_type='WORLD'
    scene.world=scene.world or bpy.data.worlds.new('PreviewWorld'); scene.world.color=(.12,.12,.12)
    scene.render.image_settings.file_format='PNG'; scene.render.filepath=str(a.output.resolve())
    bpy.ops.render.render(write_still=True)

if __name__ == '__main__':
    main()
