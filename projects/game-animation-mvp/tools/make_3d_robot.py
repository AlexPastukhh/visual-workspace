#!/usr/bin/env python3
"""Build a small rigged game robot and four reusable actions in Blender."""
import bpy
import math
from mathutils import Vector
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "3d"
OUT.mkdir(parents=True, exist_ok=True)
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
for block in bpy.data.materials:
    if block.users == 0: bpy.data.materials.remove(block)

def material(name, color, metallic=0.0, roughness=0.55, emission=0.0):
    m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
    bsdf=m.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value=(*color,1)
    bsdf.inputs["Metallic"].default_value=metallic
    bsdf.inputs["Roughness"].default_value=roughness
    if emission:
        bsdf.inputs["Emission Color"].default_value=(*color,1)
        bsdf.inputs["Emission Strength"].default_value=emission
    return m

teal=material("GameBot | enamel teal",(0.035,0.38,0.36),0.45,0.3)
dark=material("GameBot | graphite",(0.018,0.045,0.065),0.65,0.3)
orange=material("GameBot | signal orange",(1.0,0.28,0.055),0.25,0.32)
ivory=material("GameBot | warm ceramic",(0.78,0.84,0.78),0.12,0.36)
glow=material("GameBot | cyan visor",(0.025,0.55,0.85),0.25,0.22,0.45)
sole=material("GameBot | rubber",(0.025,0.04,0.05),0.05,0.9)

# Build a compact humanoid armature.
arm_data=bpy.data.armatures.new("GameBotRig")
rig=bpy.data.objects.new("GameBotRig",arm_data)
bpy.context.scene.collection.objects.link(rig)
bpy.context.view_layer.objects.active=rig
rig.select_set(True)
bpy.ops.object.mode_set(mode="EDIT")
bones={}
def bone(name, head, tail, parent=None, connected=False):
    b=arm_data.edit_bones.new(name);b.head=head;b.tail=tail
    if parent:b.parent=arm_data.edit_bones[parent];b.use_connect=connected
    bones[name]=b
bone("Root",(0,0,0),(0,0,0.82))
bone("Pelvis",(0,0,0.76),(0,0,1.05),"Root")
bone("Spine",(0,0,1.0),(0,0,1.78),"Pelvis")
bone("Head",(0,0,1.72),(0,0,2.34),"Spine")
for side,sgn in [("L",-1),("R",1)]:
    bone("UpperArm."+side,(sgn*0.34,0,1.61),(sgn*0.59,0,1.28),"Spine")
    bone("Forearm."+side,(sgn*0.59,0,1.28),(sgn*0.62,0,0.94),"UpperArm."+side)
    bone("Thigh."+side,(sgn*0.20,0,0.86),(sgn*0.22,0,0.48),"Pelvis")
    bone("Shin."+side,(sgn*0.22,0,0.48),(sgn*0.22,0,0.14),"Thigh."+side)
    bone("Foot."+side,(sgn*0.22,0,0.14),(sgn*0.22,-0.22,0.06),"Shin."+side)
bpy.ops.object.mode_set(mode="OBJECT")
rig.show_in_front=True
rig.data.display_type="STICK"

parts=[]
def assign_bone(obj,bone_name):
    vg=obj.vertex_groups.new(name=bone_name)
    vg.add(list(range(len(obj.data.vertices))),1.0,"REPLACE")

def box_part(name,center,dims,bone_name,mat,bevel=0.055,rotation=(0,0,0)):
    bpy.ops.mesh.primitive_cube_add(size=1,location=center,rotation=rotation)
    o=bpy.context.object;o.name=name;o.dimensions=dims
    bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
    if bevel:
        mod=o.modifiers.new("Soft manufactured edges","BEVEL");mod.width=bevel;mod.segments=3
        mod2=o.modifiers.new("Weighted corner normals","WEIGHTED_NORMAL")
        bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
        bpy.ops.object.modifier_apply(modifier=mod2.name)
    o.data.materials.append(mat);assign_bone(o,bone_name);parts.append(o);return o

def sphere_part(name,center,scale,bone_name,mat):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=20,ring_count=12,radius=1,location=center)
    o=bpy.context.object;o.name=name;o.scale=scale
    bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
    o.data.materials.append(mat)
    for p in o.data.polygons:p.use_smooth=True
    assign_bone(o,bone_name);parts.append(o);return o

# Core silhouette.
box_part("Torso",(0,0,1.39),(0.72,0.43,0.82),"Spine",teal,0.10)
box_part("ChestPlate",(0,-0.225,1.43),(0.43,0.045,0.38),"Spine",ivory,0.07)
box_part("ChestCore",(0,-0.26,1.43),(0.16,0.035,0.15),"Spine",orange,0.045)
box_part("PelvisShell",(0,0,0.91),(0.49,0.40,0.25),"Pelvis",dark,0.06)
# Head and face details.
box_part("HeadShell",(0,-0.005,2.04),(0.66,0.51,0.55),"Head",ivory,0.13)
box_part("Visor",(0,-0.272,2.05),(0.49,0.055,0.24),"Head",dark,0.075)
for x in (-0.12,0.12):
    sphere_part("EyeGlow_"+str(x),(x,-0.313,2.07),(0.048,0.025,0.055),"Head",glow)
box_part("AntennaStem",(0,0,2.38),(0.065,0.07,0.20),"Head",dark,0.025)
sphere_part("AntennaTip",(0,0,2.49),(0.09,0.09,0.09),"Head",orange)
# Shoulder caps and limbs.
for side,sgn in [("L",-1),("R",1)]:
    sphere_part("Shoulder_"+side,(sgn*0.39,0,1.62),(0.18,0.20,0.18),"UpperArm."+side,orange)
    box_part("UpperArm_"+side,(sgn*0.52,0,1.39),(0.23,0.29,0.43),"UpperArm."+side,teal,0.075,rotation=(0,sgn*math.radians(-7),0))
    sphere_part("Elbow_"+side,(sgn*0.60,0,1.20),(0.12,0.14,0.12),"Forearm."+side,dark)
    box_part("Forearm_"+side,(sgn*0.62,-0.005,1.03),(0.22,0.27,0.36),"Forearm."+side,ivory,0.065)
    sphere_part("Hand_"+side,(sgn*0.63,-0.015,0.84),(0.13,0.14,0.13),"Forearm."+side,orange)
    box_part("Thigh_"+side,(sgn*0.22,0,0.66),(0.27,0.31,0.43),"Thigh."+side,teal,0.075)
    sphere_part("Knee_"+side,(sgn*0.22,-0.005,0.46),(0.14,0.16,0.13),"Shin."+side,orange)
    box_part("Shin_"+side,(sgn*0.22,0,0.28),(0.24,0.29,0.31),"Shin."+side,ivory,0.065)
    box_part("Foot_"+side,(sgn*0.22,-0.105,0.105),(0.32,0.48,0.17),"Foot."+side,dark,0.055)
    box_part("FootStripe_"+side,(sgn*0.22,-0.255,0.15),(0.22,0.035,0.035),"Foot."+side,orange,0.015)

# Join rigidly weighted components into one skinned mesh.
bpy.ops.object.select_all(action="DESELECT")
for o in parts:o.select_set(True)
bpy.context.view_layer.objects.active=parts[0]
bpy.ops.object.join()
mesh=bpy.context.object;mesh.name="GameBotMesh"
mod=mesh.modifiers.new("GameBot skeletal deformation","ARMATURE");mod.object=rig
mesh.parent=rig
mesh.matrix_parent_inverse=rig.matrix_world.inverted()
mesh.select_set(False);rig.select_set(True)
bpy.context.view_layer.objects.active=rig

# Keyframe helpers. Blender 5.x creates the Action slot on first key insertion.
pose_names=[p.name for p in rig.pose.bones]
def set_pose(values):
    for pb in rig.pose.bones:
        pb.rotation_mode="XYZ"
        pb.rotation_euler=(0,0,0)
        pb.location=(0,0,0)
    for name,rot in values.items():
        rig.pose.bones[name].rotation_euler=rot

def make_action(name,frames,poses):
    action=bpy.data.actions.new(name);action.use_fake_user=True
    rig.animation_data_create();rig.animation_data.action=action
    for frame,values in zip(frames,poses):
        set_pose(values)
        for pb in rig.pose.bones:
            pb.keyframe_insert(data_path="rotation_euler",frame=frame,group=pb.name)
            pb.keyframe_insert(data_path="location",frame=frame,group=pb.name)
    for fc in action.fcurves if hasattr(action,"fcurves") else []:
        for kp in fc.keyframe_points:kp.interpolation="BEZIER"
    return action

def rad(x):return math.radians(x)
idle_frames=[1,8,16,24,32]
idle_poses=[
 {"Spine":(rad(-1),0,0),"Head":(rad(1),0,0),"UpperArm.L":(rad(-3),0,rad(-2)),"UpperArm.R":(rad(3),0,rad(2))},
 {"Spine":(rad(1),0,0),"Head":(rad(-1),0,0),"UpperArm.L":(rad(2),0,rad(-2)),"UpperArm.R":(rad(-2),0,rad(2))},
 {"Spine":(rad(-1),0,0),"Head":(rad(1),0,0),"UpperArm.L":(rad(-3),0,rad(-2)),"UpperArm.R":(rad(3),0,rad(2))},
 {"Spine":(rad(1),0,0),"Head":(rad(-1),0,0),"UpperArm.L":(rad(2),0,rad(-2)),"UpperArm.R":(rad(-2),0,rad(2))},
 {"Spine":(rad(-1),0,0),"Head":(rad(1),0,0),"UpperArm.L":(rad(-3),0,rad(-2)),"UpperArm.R":(rad(3),0,rad(2))},
]
walk_frames=[1,5,9,13,17]
walk_poses=[]
for swing in [-28,0,28,0,-28]:
    walk_poses.append({
      "Thigh.L":(rad(swing),0,0),"Thigh.R":(rad(-swing),0,0),
      "Shin.L":(rad(max(0,-swing)*0.65),0,0),"Shin.R":(rad(max(0,swing)*0.65),0,0),
      "UpperArm.L":(rad(-swing*0.72),0,0),"UpperArm.R":(rad(swing*0.72),0,0),
      "Forearm.L":(rad(-12),0,0),"Forearm.R":(rad(-12),0,0),
      "Spine":(rad(2 if swing else -2),0,0)})
run_frames=[1,4,7,10,13]
run_poses=[]
for swing in [-48,0,48,0,-48]:
    run_poses.append({
      "Thigh.L":(rad(swing),0,0),"Thigh.R":(rad(-swing),0,0),
      "Shin.L":(rad(max(0,-swing)*0.9),0,0),"Shin.R":(rad(max(0,swing)*0.9),0,0),
      "UpperArm.L":(rad(-swing*0.85),0,0),"UpperArm.R":(rad(swing*0.85),0,0),
      "Forearm.L":(rad(-30),0,0),"Forearm.R":(rad(-30),0,0),
      "Spine":(rad(6),0,0)})
jump_frames=[1,5,9,15,21,25]
jump_poses=[
 {"UpperArm.L":(rad(-10),0,rad(-5)),"UpperArm.R":(rad(-10),0,rad(5))},
 {"Thigh.L":(rad(-12),0,0),"Thigh.R":(rad(-12),0,0),"Shin.L":(rad(35),0,0),"Shin.R":(rad(35),0,0),"UpperArm.L":(rad(-75),0,rad(-10)),"UpperArm.R":(rad(-75),0,rad(10)),"Spine":(rad(-5),0,0)},
 {"Thigh.L":(rad(-12),0,0),"Thigh.R":(rad(-12),0,0),"Shin.L":(rad(35),0,0),"Shin.R":(rad(35),0,0),"UpperArm.L":(rad(-75),0,rad(-10)),"UpperArm.R":(rad(-75),0,rad(10)),"Spine":(rad(-5),0,0)},
 {"Thigh.L":(rad(8),0,0),"Thigh.R":(rad(8),0,0),"Shin.L":(rad(10),0,0),"Shin.R":(rad(10),0,0),"UpperArm.L":(rad(-25),0,rad(-8)),"UpperArm.R":(rad(-25),0,rad(8))},
 {"Thigh.L":(rad(10),0,0),"Thigh.R":(rad(10),0,0),"UpperArm.L":(rad(15),0,rad(-5)),"UpperArm.R":(rad(15),0,rad(5))},
 {"UpperArm.L":(rad(-10),0,rad(-5)),"UpperArm.R":(rad(-10),0,rad(5))},
]
actions=[
 make_action("Idle",idle_frames,idle_poses),
 make_action("Walk",walk_frames,walk_poses),
 make_action("Run",run_frames,run_poses),
 make_action("Jump",jump_frames,jump_poses),
]
print("ACTIONS_CREATED",[(a.name,tuple(a.frame_range)) for a in actions],flush=True)
print("ACTION_SLOTS",[(a.name,len(a.slots),[s.identifier for s in a.slots]) for a in actions],flush=True)

# Camera and studio stage for a review render.
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-0.015))
floor=bpy.context.object;floor.name="PreviewFloor";floor.data.materials.append(material("Preview | dark slate",(0.025,0.045,0.065),0.15,0.9))
bpy.ops.object.camera_add(location=(3.8,-7.0,3.0))
camera=bpy.context.object;camera.name="PreviewCamera"
target=Vector((0,0,1.22));camera.rotation_euler=(target- camera.location).to_track_quat("-Z","Y").to_euler()
camera.data.lens=55;bpy.context.scene.camera=camera
bpy.ops.object.light_add(type="AREA",location=(1.5,-4.5,5.5));key=bpy.context.object;key.data.energy=650;key.data.shape="DISK";key.data.size=4
key.rotation_euler=(Vector((0,0,1.1))-key.location).to_track_quat("-Z","Y").to_euler()
bpy.ops.object.light_add(type="AREA",location=(-4,1,3.2));fill=bpy.context.object;fill.data.energy=400;fill.data.size=3
fill.rotation_euler=(Vector((0,0,1.1))-fill.location).to_track_quat("-Z","Y").to_euler()
world=bpy.context.scene.world;world.color=(0.06,0.06,0.06)
scene=bpy.context.scene
scene.render.engine="CYCLES";scene.cycles.device="CPU";scene.cycles.samples=24
scene.render.threads_mode="FIXED";scene.render.threads=2
scene.render.resolution_x=640;scene.render.resolution_y=640;scene.render.resolution_percentage=100
scene.render.image_settings.file_format="PNG"
scene.render.filepath=str(OUT/"robot_preview.png")
scene.frame_start=1;scene.frame_end=32;scene.render.fps=24
scene.frame_set(1)
blend_path=OUT/"source"/"gamebot_rigged.blend"
blend_path.parent.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))
# Export only the rig and skinned mesh. Animation actions are retained as GLB clips.
bpy.ops.object.select_all(action="DESELECT")
rig.select_set(True);mesh.select_set(True);bpy.context.view_layer.objects.active=rig
glb_path=OUT/"gamebot_animated.glb"
result=bpy.ops.export_scene.gltf(
 filepath=str(glb_path),export_format="GLB",use_selection=True,
 export_animations=True,export_nla_strips=False,export_force_sampling=True,
 export_skins=True,export_apply=True,export_image_format="AUTO")
print("GLTF_EXPORT",result,flush=True)
# Render a still using the idle pose.
scene.frame_set(1)
bpy.ops.render.render(write_still=True)
assert blend_path.is_file() and blend_path.stat().st_size>20000
assert glb_path.is_file() and glb_path.stat().st_size>10000
assert (OUT/"robot_preview.png").is_file()
print("3D_GAME_ASSET_OK",bpy.app.version_string,flush=True)
print("BLEND",blend_path,blend_path.stat().st_size,flush=True)
print("GLB",glb_path,glb_path.stat().st_size,flush=True)
print("PNG",OUT/"robot_preview.png",(OUT/"robot_preview.png").stat().st_size,flush=True)
