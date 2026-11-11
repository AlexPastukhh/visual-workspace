import bpy, sys
from pathlib import Path
from mathutils import Vector
args=sys.argv[sys.argv.index('--')+1:]
mode=args[0]; out=Path(args[1]); out.mkdir(parents=True,exist_ok=True)
def mat(name,rgb):
 m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*rgb,1);m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(*rgb,1);return m
def cube(name,loc,size,material):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
 o=bpy.context.object;o.name=name;o.dimensions=size
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 o.data.materials.append(material);return o
if mode=='create':
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 wall=mat('wall',(0.75,.45,.24));roof=mat('roof',(.64,.15,.15))
 glass=mat('glass',(.1,.53,.7));door=mat('door',(.25,.17,.23))
 cube('House',(0,0,1),(3.6,2.8,2),wall)
 cube('Ground',(0,0,-.16),(11,11,.3),mat('grass',(.23,.38,.25)))
 cube('Door',(0,-1.43,.67),(.7,.12,1.35),door)
 for x in (-1.05,1.05):cube('Window',(x,-1.44,1.40),(.65,.12,.56),glass)
 roofmesh=bpy.data.meshes.new('roofmesh')
 roofmesh.from_pydata([(-2,-1.6,2),(2,-1.6,2),(0,-1.6,3.2),(-2,1.6,2),(2,1.6,2),(0,1.6,3.2)],[],[(0,1,2),(3,5,4),(0,2,5,3),(2,1,4,5)])
 roofobj=bpy.data.objects.new('Roof',roofmesh);bpy.context.collection.objects.link(roofobj);roofobj.data.materials.append(roof)
 bpy.ops.object.camera_add(location=(6,-8,5))
 cam=bpy.context.object;cam.name='PreviewCamera'
 cam.rotation_euler=(Vector((0,0,1.3))-cam.location).to_track_quat('-Z','Y').to_euler()
 cam.data.type='ORTHO';cam.data.ortho_scale=8.5;bpy.context.scene.camera=cam
 bpy.ops.object.light_add(type='AREA',location=(-3,-4,7));bpy.context.object.data.energy=1300
elif mode=='revise':
 for v in bpy.data.objects['Roof'].data.vertices:
  if v.co.z>2.8:v.co.z+=.5
 m=bpy.data.objects['House'].data.materials[0];m.diffuse_color=(.32,.58,.75,1);m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.32,.58,.75,1)
else:raise ValueError('mode must be create/revise')
sc=bpy.context.scene;sc.render.engine='CYCLES';sc.cycles.device='CPU';sc.cycles.samples=8
sc.render.threads_mode='FIXED';sc.render.threads=2
sc.render.resolution_x=480;sc.render.resolution_y=360;sc.render.resolution_percentage=100
sc.render.image_settings.file_format='PNG'
sc.render.filepath=str(out/('preview_v1.png' if mode=='create' else 'preview_v2.png'))
bpy.ops.wm.save_as_mainfile(filepath=str(out/('scene_v1.blend' if mode=='create' else 'scene_v2.blend')))
bpy.ops.render.render(write_still=True)
print('VISUAL_MVP_OK',mode,sc.render.filepath,flush=True)
