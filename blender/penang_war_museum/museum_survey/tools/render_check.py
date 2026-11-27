"""Render a framed 3/4 preview of every mesh in the opened .blend (does not save the file).
blender -b file.blend --python render_check.py -- out.png [dir_x dir_y dir_z] [lens]"""
import bpy, sys, math
from mathutils import Vector
a = sys.argv[sys.argv.index("--") + 1:]
out = a[0]
d = Vector((float(a[1]), float(a[2]), float(a[3]))) if len(a) >= 4 else Vector((1.0, -1.2, 0.8))
lens = float(a[4]) if len(a) >= 5 else 35
sc = bpy.context.scene
dg = bpy.context.evaluated_depsgraph_get()
mn = Vector((1e9,) * 3); mx = Vector((-1e9,) * 3)
for o in sc.objects:
    if o.type in ('MESH', 'FONT') and not o.hide_render:
        for c in o.bound_box:
            w = o.matrix_world @ Vector(c); mn = Vector(map(min, mn, w)); mx = Vector(map(max, mx, w))
ctr = (mn + mx) / 2; rad = (mx - mn).length / 2
cd = bpy.data.cameras.new("chk"); cam = bpy.data.objects.new("chk", cd); sc.collection.objects.link(cam)
cd.lens = lens; cd.clip_end = 5000
dist = rad / math.tan(math.atan(18 / lens)) * 1.05
cam.location = ctr + d.normalized() * dist
cam.rotation_euler = (ctr - cam.location).to_track_quat('-Z', 'Y').to_euler()
sc.camera = cam
if not any(o.type == 'LIGHT' for o in sc.objects):
    ld = bpy.data.lights.new("sun", 'SUN'); ld.energy = 3.5; s = bpy.data.objects.new("sun", ld); sc.collection.objects.link(s)
    s.rotation_euler = (math.radians(45), 0, math.radians(35))
if sc.world is None: sc.world = bpy.data.worlds.new("W")
sc.world.use_nodes = True
bg = next(n for n in sc.world.node_tree.nodes if n.type == "BACKGROUND"); bg.inputs[0].default_value = (0.55, 0.65, 0.78, 1); bg.inputs[1].default_value = 0.8
try:
    sc.render.engine = 'BLENDER_EEVEE'
except TypeError:
    pass
try: sc.view_settings.view_transform = 'AgX'
except Exception: pass
sc.render.resolution_x, sc.render.resolution_y = 1000, 700
sc.render.filepath = out; sc.render.image_settings.file_format = 'PNG'
bpy.ops.render.render(write_still=True)
print("RENDERED", out, "size", tuple(round(v, 1) for v in (mx - mn)))
