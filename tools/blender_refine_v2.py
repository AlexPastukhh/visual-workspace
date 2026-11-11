"""Second visual iteration: add window trim and door hardware to the saved v1."""
import bpy
import sys
from pathlib import Path
args = sys.argv[sys.argv.index("--") + 1:]
if len(args) != 2:
    raise SystemExit("Usage: blender --background <source.blend> --python blender_refine_v2.py -- <output_dir> <name>")
out_dir = Path(args[0]).resolve(); name = args[1]; out_dir.mkdir(parents=True, exist_ok=True)
scene = bpy.context.scene
if not all(n in bpy.data.objects for n in ("Window", "Window.001", "Door", "PreviewCamera")):
    raise RuntimeError("Expected v1 house objects not found")

def material(name, rgba, metallic=0.0, roughness=0.7):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color = rgba; m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = rgba
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    return m

def box(name, location, dimensions, mat):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    o = bpy.context.object; o.name = name; o.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(mat); return o

trim = material("Fortis | warm ivory window trim", (0.83, 0.76, 0.61, 1.0))
metal = material("Fortis | brushed brass door handle", (0.62, 0.39, 0.12, 1.0), metallic=0.72, roughness=0.28)
for win_name in ("Window", "Window.001"):
    win = bpy.data.objects[win_name]
    cx, cy, cz = win.location
    w, depth, h = win.dimensions
    front = cy - depth / 2 - 0.055
    t = 0.065
    if f"Fortis_{win_name}_Frame_Left" not in bpy.data.objects:
        box(f"Fortis_{win_name}_Frame_Left", (cx-w/2-t/2, front, cz), (t, 0.09, h+2*t), trim)
        box(f"Fortis_{win_name}_Frame_Right", (cx+w/2+t/2, front, cz), (t, 0.09, h+2*t), trim)
        box(f"Fortis_{win_name}_Frame_Top", (cx, front, cz+h/2+t/2), (w+2*t, 0.09, t), trim)
        box(f"Fortis_{win_name}_Frame_Bottom", (cx, front, cz-h/2-t/2), (w+2*t, 0.09, t), trim)
        box(f"Fortis_{win_name}_Mullion_V", (cx, front-0.008, cz), (0.035, 0.095, h), trim)
        box(f"Fortis_{win_name}_Mullion_H", (cx, front-0.009, cz), (w, 0.095, 0.035), trim)

if "Fortis_Door_Handle" not in bpy.data.objects:
    door = bpy.data.objects["Door"]
    y = door.location.y - door.dimensions.y/2 - 0.065
    bpy.ops.mesh.primitive_uv_sphere_add(segments=20, ring_count=12, radius=0.052, location=(0.22, y, 0.72))
    knob = bpy.context.object; knob.name = "Fortis_Door_Handle"
    knob.scale = (1.0, 0.65, 1.0); bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    knob.data.materials.append(metal)
    for face in knob.data.polygons: face.use_smooth = True

scene.render.engine = "CYCLES"; scene.cycles.device = "CPU"; scene.cycles.samples = 16
scene.render.threads_mode = "FIXED"; scene.render.threads = 2
scene.render.resolution_x = 640; scene.render.resolution_y = 480; scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.filepath = str((out_dir / f"{name}.png").resolve())
blend_path = (out_dir / f"{name}.blend").resolve()
bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))
bpy.ops.render.render(write_still=True)
png_path = Path(scene.render.filepath)
assert blend_path.is_file() and blend_path.stat().st_size > 10_000
assert png_path.is_file() and png_path.stat().st_size > 10_000
print("FORTIS_BLENDER_REVISION_OK", bpy.app.version_string, "objects", len(bpy.data.objects), flush=True)
print("BLEND_OUTPUT", blend_path, blend_path.stat().st_size, flush=True)
print("PNG_OUTPUT", png_path, png_path.stat().st_size, flush=True)
