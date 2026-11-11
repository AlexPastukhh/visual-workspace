import bpy
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SOURCE = Path(__file__).resolve().parent
OUTPUT_GLB = ROOT / "assets" / "car-jump-turn-reverse" / "car.glb"
OUTPUT_BLEND = SOURCE / "car_source.blend"


def material(name, color, metallic=0.0, roughness=0.4):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1.0)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    return mat


def cube(name, location, dimensions, mat, bevel=0.06):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        modifier = obj.modifiers.new("Soft manufactured edges", "BEVEL")
        modifier.width = bevel
        modifier.segments = 3
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.modifier_apply(modifier=modifier.name)
    obj.data.materials.append(mat)
    obj.parent = CAR_ROOT
    return obj


def wheel(name, x, y):
    pivot = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(pivot)
    pivot.location = (x, y, 0.43)
    pivot.parent = CAR_ROOT

    bpy.ops.mesh.primitive_cylinder_add(
        vertices=24, radius=0.42, depth=0.34, location=(x, y, 0.43)
    )
    tire = bpy.context.object
    tire.name = name + "_Tire"
    tire.rotation_euler[1] = math.pi / 2
    tire.data.materials.append(TIRE)
    tire.parent = pivot
    tire.location = (0, 0, 0)
    bevel = tire.modifiers.new("Tire edge", "BEVEL")
    bevel.width = 0.045
    bevel.segments = 2
    bpy.context.view_layer.objects.active = tire
    bpy.ops.object.modifier_apply(modifier=bevel.name)

    bpy.ops.mesh.primitive_cylinder_add(
        vertices=24, radius=0.235, depth=0.36, location=(x, y, 0.43)
    )
    rim = bpy.context.object
    rim.name = name + "_Rim"
    rim.rotation_euler[1] = math.pi / 2
    rim.data.materials.append(METAL)
    rim.parent = pivot
    rim.location = (0, 0, 0)
    return pivot


bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
CAR_ROOT = bpy.data.objects.new("Car", None)
bpy.context.collection.objects.link(CAR_ROOT)

BODY = material("Deep turquoise enamel", (0.025, 0.36, 0.43), 0.72, 0.24)
DARK = material("Graphite trim", (0.018, 0.028, 0.04), 0.25, 0.3)
GLASS = material("Smoked blue glass", (0.035, 0.16, 0.22), 0.45, 0.16)
TIRE = material("Rubber", (0.012, 0.016, 0.02), 0.0, 0.82)
METAL = material("Brushed alloy", (0.52, 0.62, 0.66), 0.85, 0.22)
LIGHT = material("LED white", (0.85, 0.94, 1.0), 0.15, 0.2)
TAIL = material("Tail lamp red", (0.75, 0.025, 0.018), 0.15, 0.24)

# Blender front -Y exports to Godot +Z. Verify using FrontBumper/RearBumper.
cube("Chassis", (0, 0, 0.67), (1.82, 4.05, 0.58), BODY, 0.18)
cube("Hood", (0, -1.32, 0.91), (1.68, 1.28, 0.22), BODY, 0.12)
cube("RearDeck", (0, 1.48, 0.92), (1.65, 0.88, 0.22), BODY, 0.10)
cube("Cabin", (0, 0.12, 1.25), (1.52, 1.92, 0.78), GLASS, 0.18)
cube("Roof", (0, 0.12, 1.68), (1.38, 1.18, 0.12), BODY, 0.08)
cube("FrontBumper", (0, -2.02, 0.48), (1.88, 0.18, 0.22), DARK, 0.06)
cube("RearBumper", (0, 2.02, 0.48), (1.88, 0.18, 0.22), DARK, 0.06)
cube("FrontSplitter", (0, -2.12, 0.34), (1.9, 0.24, 0.08), METAL, 0.025)
cube("RearSpoiler", (0, 1.82, 1.18), (2.05, 0.16, 0.10), DARK, 0.035)
cube("SpoilerLeftPost", (-0.72, 1.72, 1.08), (0.08, 0.10, 0.20), METAL, 0.02)
cube("SpoilerRightPost", (0.72, 1.72, 1.08), (0.08, 0.10, 0.20), METAL, 0.02)

for side in (-1, 1):
    cube("HoodStripe_%s" % side, (side * 0.42, -1.35, 1.025), (0.075, 1.05, 0.018), METAL, 0.008)
    cube("Headlight_%s" % side, (side * 0.61, -1.94, 0.78), (0.34, 0.08, 0.12), LIGHT, 0.035)
    cube("TailLight_%s" % side, (side * 0.62, 1.98, 0.76), (0.32, 0.07, 0.13), TAIL, 0.03)

for x in (-0.98, 0.98):
    for y in (-1.28, 1.28):
        corner = ("L" if x < 0 else "R") + ("F" if y < 0 else "R")
        wheel("Wheel_" + corner, x, y)

# Small side mirrors and visible door handles make the silhouette less block-like.
for side in (-1, 1):
    cube("Mirror_%s" % side, (side * 0.88, -0.48, 1.23), (0.20, 0.25, 0.13), DARK, 0.04)
    cube("DoorHandle_%s" % side, (side * 0.77, 0.38, 1.04), (0.035, 0.22, 0.045), METAL, 0.015)

# Set a clean origin at the vehicle's ground centre and parent every mesh to the export root.
for obj in list(bpy.context.scene.objects):
    if obj is CAR_ROOT:
        continue
    if obj.parent is None:
        obj.parent = CAR_ROOT

bpy.ops.object.select_all(action="DESELECT")
CAR_ROOT.select_set(True)
bpy.context.view_layer.objects.active = CAR_ROOT

OUTPUT_BLEND.parent.mkdir(parents=True, exist_ok=True)
OUTPUT_GLB.parent.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT_BLEND))
bpy.ops.export_scene.gltf(
    filepath=str(OUTPUT_GLB),
    export_format="GLB",
    use_selection=False,
    export_apply=True,
    export_yup=True,
    export_animations=False,
)
print("CAR_ASSET_GENERATED", OUTPUT_BLEND, OUTPUT_GLB)
