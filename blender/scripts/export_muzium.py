"""Export the Muzium Perang scene to GLB (run inside Blender after build_muzium.py and place_props.py).

Writes blender/out/muzium_perang_raw.glb. Optimize afterwards with blender/scripts/optimize_glb.sh.
Excludes: TEMPLATES collection (hidden), preview camera, lights.
"""
import bpy, os

ROOT = "/Users/izardy/Documents/virtualtourism"
OUT = ROOT + "/blender/out/muzium_perang_raw.glb"
os.makedirs(os.path.dirname(OUT), exist_ok=True)

cam = bpy.data.objects.get("prevcam")
if cam: bpy.data.objects.remove(cam, do_unlink=True)

# make sure templates are hidden so they are not exported
t = bpy.data.collections.get("TEMPLATES")
if t:
    t.hide_viewport = True
    for lc in bpy.context.view_layer.layer_collection.children:
        if lc.name == "TEMPLATES": lc.exclude = True

for o in bpy.context.view_layer.objects: o.select_set(False)
bpy.ops.export_scene.gltf(
    filepath=OUT, export_format="GLB", use_visible=True, export_apply=True, export_yup=True,
    export_cameras=False, export_lights=False, export_extras=True,
    export_image_format="JPEG", export_image_quality=80, export_texture_dir="",
    export_materials="EXPORT", export_normals=True, export_texcoords=True,
)
print("exported", OUT, round(os.path.getsize(OUT) / 1e6, 1), "MB")
bpy.ops.wm.save_as_mainfile(filepath=ROOT + "/blender/src/muzium_perang.blend")
