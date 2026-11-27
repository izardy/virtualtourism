"""Render close-ups framed on objects whose names start with given prefixes (does not save the .blend).
blender -b file.blend --python render_focus.py -- out_dir prefix1 [prefix2 ...]"""
import bpy, sys, math, os
from mathutils import Vector
a = sys.argv[sys.argv.index("--") + 1:]
out, prefixes = a[0], a[1:]
sc = bpy.context.scene
ld = bpy.data.lights.new("sun", 'SUN'); ld.energy = 3.5; s = bpy.data.objects.new("sun", ld); sc.collection.objects.link(s)
s.rotation_euler = (math.radians(50), 0, math.radians(30))
if sc.world is None: sc.world = bpy.data.worlds.new("W")
sc.world.use_nodes = True
next(n for n in sc.world.node_tree.nodes if n.type == "BACKGROUND").inputs[0].default_value = (0.55, 0.65, 0.78, 1)
sc.render.engine = 'BLENDER_EEVEE'; sc.render.resolution_x, sc.render.resolution_y = 900, 600
try: sc.view_settings.view_transform = 'AgX'
except Exception: pass
cd = bpy.data.cameras.new("c"); cam = bpy.data.objects.new("c", cd); sc.collection.objects.link(cam); cd.lens = 30; sc.camera = cam
bpy.context.view_layer.update()
for pre in prefixes:
    objs = [o for o in sc.objects if o.name.startswith(pre) and o.type in ('MESH', 'FONT')]
    if not objs: print("NONE", pre); continue
    mn = Vector((1e9,) * 3); mx = Vector((-1e9,) * 3)
    for o in objs:
        for c in o.bound_box:
            w = o.matrix_world @ Vector(c); mn = Vector(map(min, mn, w)); mx = Vector(map(max, mx, w))
    ctr = (mn + mx) / 2; rad = max(2.0, (mx - mn).length / 2)
    d = Vector((0.8, -1.0, 0.55)).normalized()
    cam.location = ctr + d * rad * 2.3
    cam.rotation_euler = (ctr - cam.location).to_track_quat('-Z', 'Y').to_euler()
    sc.render.filepath = os.path.join(out, pre.strip("_") + ".png")
    bpy.ops.render.render(write_still=True); print("RENDERED", pre)
