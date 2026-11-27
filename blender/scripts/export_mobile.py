"""Export the phone version of the Muzium Perang model: blender/out/muzium_perang_mobile_raw.glb.

Run inside Blender after build_muzium.py, place_props.py, export_muzium.py (and build_tour_paths.py).
Then optimize with: sh blender/scripts/optimize_glb.sh mobile

Differences from the desktop model (same layout, hotspots, markers and walkable meshes):
- Building and ground materials use the Poly Haven 1k textures (textures_1k) instead of 2k.
- Every tree drops one tier: hero -> background, background -> far, far and distant -> phone tier (T_MOB),
  and every second distant tree is left out (the hills are mostly in fog at night).
The scene is restored afterwards, so the desktop export can be re-run without rebuilding.
"""
import bpy, os

ROOT = "/Users/izardy/Documents/virtualtourism"
T = lambda n: bpy.data.objects[n].data
DOWN = {   # current template mesh -> phone template mesh
    T("tpl_tree_hero"): T("tpl_tree_island_tree_01"),
    T("tpl_tree_island_tree_01"): T("tpl_tree_far1"),
    T("tpl_tree_island_tree_02"): T("tpl_tree_far2"),
    T("tpl_tree_far1"): T("tpl_tree_mob"),
    T("tpl_tree_far2"): T("tpl_tree_mob"),
    T("tpl_tree_dist"): T("tpl_tree_mob"),
}
props = bpy.data.collections["PROPS"].objects
swapped, hidden = [], []
dist = sorted((o for o in props if o.data == T("tpl_tree_dist")), key=lambda o: o.name)
for o in dist[1::2]:
    o.hide_set(True); hidden.append(o)
for o in props:
    if o.data in DOWN and o not in hidden:
        swapped.append((o, o.data)); o.data = DOWN[o.data]

images = []
for img in bpy.data.images:
    p = img.filepath
    if "/textures_2k/" in p:
        q = p.replace("/textures_2k/", "/textures_1k/").replace("_2k.jpg", "_1k.jpg")
        if os.path.isfile(bpy.path.abspath(q)):
            images.append((img, p)); img.filepath = q; img.reload()

tris = 0
for o in props:
    if o.type == "MESH" and o.visible_get():
        tris += sum(len(p.vertices) - 2 for p in o.data.polygons)
print(f"phone model: {len(swapped)} trees down one tier, {len(hidden)} distant trees left out, {len(images)} textures at 1k, prop triangles {tris}")

try:
    g = {"__name__": "__main__", "EXPORT_OUT": ROOT + "/blender/out/muzium_perang_mobile_raw.glb", "SAVE_BLEND": False}
    exec(open(ROOT + "/blender/scripts/export_muzium.py").read(), g)
finally:   # restore the desktop scene
    for o, d in swapped: o.data = d
    for o in hidden: o.hide_set(False)
    for img, p in images: img.filepath = p; img.reload()
