"""Original small retail shell, fixtures and furniture. No external assets."""
import argparse, importlib.util, json, sys
from pathlib import Path
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
SCRIPTS=ROOT/'skills/blender-asset-workflow/scripts'
def module(name):
 spec=importlib.util.spec_from_file_location(name,SCRIPTS/(name+'.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
preview=module('white_preview')
fit=preview.fit_orthographic_camera
check=module('overlap_audit')
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);out=a.output.resolve()
if not out.is_dir():raise ValueError('runner must reserve output directory first')
if (out/'shop.blend').exists():raise FileExistsError(out/'shop.blend')
bpy.ops.wm.read_factory_settings(use_empty=True);scene=bpy.context.scene
scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
allow=[]
def box(name,loc,dimensions):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);obj=bpy.context.object;obj.name=name;obj.dimensions=dimensions
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);return obj

def exempt(a,b,reason):allow.append({'objects':[a,b],'reason':reason})
box('Floor',(0,0,-.1),(6.4,4.4,.2))
box('WallBack',(0,2,1.5),(6.2,.2,3))
box('WallLeft',(-3,0,1.5),(.2,3.8,3))
box('WallRight',(3,0,1.5),(.2,3.8,3))
box('Roof',(0,0,3.1),(6.4,4.4,.2))
for name,x in [('FrameLeft',-3),('FrameMiddle',.5),('FrameRight',3)]:box(name,(x,-2,1.5),(.14,.14,3))
box('FrameTop',(0,-2,2.95),(6,.16,.1))
for n in ['FrameLeft','FrameMiddle','FrameRight']:exempt(n,'FrameTop','Structural frame corner joint')
box('SignPanel',(-1.25,-2.12,2.7),(3.3,.1,.35))
box('Counter',(-1.65,.45,.5),(1.8,.8,1))
box('CounterTop',(-1.65,.45,1.04),(1.95,.95,.08))
box('Register',(-1.5,.55,1.22),(.35,.3,.28))
# Separate shelf boards and uprights, with explicit named structural joints.
for n,x in [('ShelfPostLeft',-2.35),('ShelfPostRight',.25)]:box(n,(x,1.62,1.1),(.1,.18,2.2))
for k,z in enumerate([.35,1,1.65]):
 shelf='ShelfBoard'+str(k);box(shelf,(-1.05,1.62,z),(2.7,.45,.1))
 for post in ['ShelfPostLeft','ShelfPostRight']:exempt(shelf,post,'Shelf board attaches to upright')
 for j,x in enumerate([-1.85,-1.05,-.25]):box('DisplayBox'+str(k)+'_'+str(j),(x,1.62,z+.2),(.45,.3,.3))
box('DisplayTableTop',(1.8,.8,.85),(1.3,.9,.12))
for k,(x,y) in enumerate([(1.3,.5),(2.3,.5),(1.3,1.1),(2.3,1.1)]):
 n='TableLeg'+str(k);box(n,(x,y,.4),(.1,.1,.8));exempt(n,'DisplayTableTop','Table leg socket into underside')
box('TableDisplay',(1.8,.8,1.06),(.5,.4,.3))
for k,x in enumerate([1.25,2.25]):
 seat='Seat'+str(k);box(seat,(x,-.55,.5),(.6,.6,.1))
 for j,(dx,dy) in enumerate([(-.22,-.22),(.22,-.22),(-.22,.22),(.22,.22)]):
  n='SeatLeg'+str(k)+'_'+str(j);box(n,(x+dx,-.55+dy,.225),(.08,.08,.45))
 box('SeatBack'+str(k),(x,-.83,.85),(.6,.08,.6))
 exempt(seat,'SeatBack'+str(k),'Chair seat/back connection')
bpy.context.view_layer.update()
(out/'allowlist.json').write_text(json.dumps(allow,indent=2))
report=check.audit(check.scene_items(scene),allow)
(out/'overlap-review.json').write_text(json.dumps(report,indent=2))
# Save/export intact native geometry BEFORE temporary visibility/camera changes.
bpy.ops.wm.save_as_mainfile(filepath=str(out/'shop.blend'))
bpy.ops.export_scene.gltf(filepath=str(out/'shop.glb'),export_format='GLB',export_cameras=False,export_lights=False)
scene.render.engine='BLENDER_WORKBENCH';scene.render.resolution_x=960;scene.render.resolution_y=720;scene.render.resolution_percentage=100
shade=scene.display.shading;shade.light='STUDIO';shade.color_type='SINGLE';shade.single_color=(.8,.8,.8);shade.show_shadows=True;shade.show_cavity=True;shade.cavity_type='BOTH'
scene.world=bpy.data.worlds.new('PreviewWorld');scene.world.color=(.12,.12,.12)
data=bpy.data.cameras.new('PreviewCamera');camera=bpy.data.objects.new('PreviewCamera',data);scene.collection.objects.link(camera);scene.camera=camera
data.clip_start=.01;data.clip_end=200

def render(name,center,direction,objects):
 if (out/name).exists():raise FileExistsError(out/name)
 shade.show_shadows=(name=='white-overview.png')
 center=Vector(center);direction=Vector(direction).normalized();camera.location=center+direction*30
 camera.rotation_euler=(-direction).to_track_quat('-Z','Y').to_euler();bpy.context.view_layer.update()
 points=[o.matrix_world@Vector(v) for o in objects for v in o.bound_box]
 fit(scene,camera,points);scene.render.image_settings.file_format='PNG';scene.render.filepath=str(out/name);bpy.ops.render.render(write_still=True);preview.clean_file(out/name)
meshes=[o for o in scene.objects if o.type=='MESH']
render('white-overview.png',(0,0,1),(1,-1,.8),meshes)
bpy.data.objects['Roof'].hide_render=True
render('white-roof-off-top.png',(0,0,0),(0,0,1),[o for o in meshes if not o.hide_render])
# Rear/left cutaway exposes the furniture while retaining the relevant
# right wall and front frame for clearance review. No source save follows.
for name in ['WallBack','WallLeft']:bpy.data.objects[name].hide_render=True
render('white-furniture-closeup.png',(1.65,-.2,1.2),(-.55,1,.9),[o for o in meshes if o.name.startswith(('Seat','DisplayTable','Table')) or o.name in ['FrameRight','FrameMiddle']])
(out/'preview-notes.txt').write_text('Overview: intact shell. Top: roof hidden only in temporary preview memory. Close-up: roof, rear wall and left wall hidden; right wall and front framing remain for clearance inspection. Native/GLB were saved first and retain all geometry. No glass is modeled. AABB candidates are review hints, not true-mesh collision claims.\n')
print('Meshes:',len(meshes),'AABB candidates:',len(report['candidates']))
