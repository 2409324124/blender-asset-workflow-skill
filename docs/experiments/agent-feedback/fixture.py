"""Build the public meter, apply one builder's bpy script, save, or render the opened file."""
import argparse
from pathlib import Path
import runpy
import sys
import bpy
from mathutils import Vector

def material(name,color,metallic=0,roughness=.38):
    m=bpy.data.materials.new(name);m.use_nodes=True
    bs=m.node_tree.nodes.get("Principled BSDF")
    bs.inputs["Base Color"].default_value=(*color,1)
    bs.inputs["Metallic"].default_value=metallic
    bs.inputs["Roughness"].default_value=roughness
    return m

def block(name,xyz,size,r,mat):
    bpy.ops.mesh.primitive_cube_add(size=1,location=xyz)
    o=bpy.context.object;o.name=name;o.dimensions=size
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    bevel=o.modifiers.new("Edge radius","BEVEL");bevel.width=r;bevel.segments=5
    for face in o.data.polygons:face.use_smooth=True
    o.modifiers.new("Planar panels","WEIGHTED_NORMAL")
    o.data.materials.append(mat)
    return o

def asset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    teal=material("Baked enamel",(.032,.155,.14))
    rubber=material("Boot rubber",(.019,.022,.023),roughness=.62)
    block("Instrument housing",(0,0,1.38),(2.12,.60,2.44),.14,teal)
    block("Protective shoe",(0,0,.19),(2.18,.65,.36),.10,rubber)
    for x in (-.56,.56):block("Bail mount",(x,0,2.68),(.16,.17,.32),.065,rubber)
    block("Carry grip",(0,0,2.86),(1.27,.19,.19),.088,rubber)
    scene=bpy.context.scene
    scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=24
    scene.cycles.seed=71;scene.cycles.use_denoising=True
    scene.render.resolution_x=480;scene.render.resolution_y=480;scene.render.resolution_percentage=100
    scene.view_settings.view_transform='AgX';scene.view_settings.look='None';scene.view_settings.exposure=-.4
    scene.world=bpy.data.worlds.new("Gray surround");scene.world.use_nodes=True
    bg=scene.world.node_tree.nodes.get("Background");bg.inputs['Color'].default_value=(.28,.29,.30,1)
    bg.inputs['Strength'].default_value=.55
    center=Vector((0,0,1.48))
    def placed(name,data,position):
        obj=bpy.data.objects.new(name,data);scene.collection.objects.link(obj)
        obj.location=position;obj.rotation_euler=(center-obj.location).to_track_quat('-Z','Y').to_euler()
        return obj
    camera=placed('Meter review',bpy.data.cameras.new('Meter review'),(2.6,-8.8,3.7))
    camera.data.type='ORTHO';camera.data.ortho_scale=3.7;scene.camera=camera
    for name,xyz,power,w,h in [('Key',(-3,-3,5.8),380,3.1,2),('Fill',(3.5,-3.6,2.4),155,2.5,1.45),('Strip',(2.4,2.4,4.6),450,2.8,.65)]:
        l=bpy.data.lights.new(name,'AREA');l.shape='RECTANGLE';l.energy=power;l.size=w;l.size_y=h
        placed(name,l,xyz)
    block('Review floor',(0,0,-.07),(80,80,.15),.005,material('Floor',(.12,.125,.13),roughness=.7))

def main():
    p=argparse.ArgumentParser()
    p.add_argument('mode',choices=('build','render'));p.add_argument('output',type=Path)
    p.add_argument('--builder',type=Path);p.add_argument('--skill',type=Path)
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
    if a.output.exists():raise FileExistsError(a.output)
    if a.mode=='build':
        asset()
        if a.builder:
            if a.skill:sys.path.insert(0,str(a.skill.resolve()/'scripts'))
            runpy.run_path(str(a.builder.resolve()),run_name='__main__')
        bpy.ops.wm.save_as_mainfile(filepath=str(a.output.resolve()))
    else:
        scene=bpy.context.scene;scene.render.filepath=str(a.output.resolve());scene.render.image_settings.file_format='PNG'
        scene.render.image_settings.color_mode='RGB';scene.render.image_settings.color_depth='8'
        bpy.ops.render.render(write_still=True)
if __name__=='__main__':main()
