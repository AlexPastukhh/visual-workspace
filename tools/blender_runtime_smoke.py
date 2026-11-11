"""First real Fortis Repo Blender iteration: open, edit, save, render."""
import bpy
import sys
from pathlib import Path

args = sys.argv[sys.argv.index("--") + 1:]
if len(args) != 2:
    raise SystemExit("Usage: blender --background <source.blend> --python blender_runtime_smoke.py -- <output_dir> <name>")
out_dir = Path(args[0]).resolve()
name = args[1]
out_dir.mkdir(parents=True, exist_ok=True)
scene = bpy.context.scene

# Verify we opened the existing editable project rather than creating a substitute.
required = {"House", "Roof", "Door", "PreviewCamera"}
missing = required.difference(bpy.data.objects.keys())
if missing:
    raise RuntimeError(f"Expected source scene objects are missing: {sorted(missing)}")

# Add a small, editable brick chimney and a front doorstep as a visible revision.
def add_box(obj_name, location, dimensions, material):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    obj = bpy.context.object
    obj.name = obj_name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(material)
    return obj

brick = bpy.data.materials.new("Fortis | warm chimney brick")
brick.diffuse_color = (0.34, 0.105, 0.065, 1.0)
brick.use_nodes = True
bsdf = brick.node_tree.nodes.get("Principled BSDF")
bsdf.inputs["Base Color"].default_value = (0.34, 0.105, 0.065, 1.0)
bsdf.inputs["Roughness"].default_value = 0.82

stone = bpy.data.materials.new("Fortis | pale doorstep stone")
stone.diffuse_color = (0.48, 0.43, 0.35, 1.0)
stone.use_nodes = True
stone.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.48, 0.43, 0.35, 1.0)

# Roof ridge is at x=0; the chimney intersects the right roof slope and rises above it.
if "Fortis_Chimney" not in bpy.data.objects:
    add_box("Fortis_Chimney", (1.12, 0.28, 3.03), (0.43, 0.43, 1.18), brick)
    add_box("Fortis_Chimney_Cap", (1.12, 0.28, 3.66), (0.55, 0.55, 0.13), brick)
if "Fortis_Doorstep" not in bpy.data.objects:
    add_box("Fortis_Doorstep", (0.0, -1.66, 0.075), (1.02, 0.42, 0.15), stone)

# Deterministic CPU-only render; no GPU, window server or user interaction required.
scene.render.engine = "CYCLES"
scene.cycles.device = "CPU"
scene.cycles.samples = 12
scene.render.threads_mode = "FIXED"
scene.render.threads = 2
scene.render.resolution_x = 640
scene.render.resolution_y = 480
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.filepath = str((out_dir / f"{name}.png").resolve())
scene.render.film_transparent = False

blend_path = (out_dir / f"{name}.blend").resolve()
bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))
bpy.ops.render.render(write_still=True)

png_path = Path(scene.render.filepath)
if not blend_path.is_file() or blend_path.stat().st_size < 10_000:
    raise RuntimeError("Blend project was not saved correctly")
if not png_path.is_file() or png_path.stat().st_size < 10_000:
    raise RuntimeError("PNG render was not produced correctly")
print("FORTIS_BLENDER_CYCLE_OK", flush=True)
print("BLENDER_VERSION", bpy.app.version_string, flush=True)
print("SCENE_OBJECTS", len(bpy.data.objects), flush=True)
print("BLEND_OUTPUT", blend_path, blend_path.stat().st_size, flush=True)
print("PNG_OUTPUT", png_path, png_path.stat().st_size, flush=True)
