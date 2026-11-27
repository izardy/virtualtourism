"""Assemble the Penang War Museum site map: links every structure file as collection instances (all share
origin O, so no manual alignment) and lays the georeferenced satellite screenshots under them.
blender -b --factory-startup --python assemble_sitemap.py -- <out.blend>"""
import bpy, bmesh, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pwm_lib import reset_scene

OUT = sys.argv[sys.argv.index("--") + 1]
BL = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SS = os.path.join(BL, "museum_survey", "screenshots")
reset_scene()
sc = bpy.context.scene
if os.path.exists(OUT):
    raise SystemExit("REFUSING to overwrite " + OUT)
bpy.ops.wm.save_as_mainfile(filepath=OUT)      # save first so library paths can be relative

LINK = [(os.path.join("site_structures", "penang_war_museum_B01_B02_entrance_gate.blend"), "WarMuseumEntrance"),
        (os.path.join("site_structures", "penang_war_museum_B03_B04_B06_entrance_plaza.blend"), "WarMuseumEntrance2")]
SKIP = ("B01_B02_entrance_gate", "B03_B04_B06_entrance_plaza", "PB1_pillbox", "PB2_pillbox")
for f in sorted(os.listdir(os.path.join(BL, "site_structures"))):
    if f.endswith(".blend") and not any(s in f for s in SKIP):
        LINK.append((os.path.join("site_structures", f), None))

site = bpy.data.collections.new("PWM_SiteMap"); sc.collection.children.link(site)
for rel, colname in LINK:
    path = os.path.join(BL, rel)
    with bpy.data.libraries.load(path, link=True, relative=True) as (src, dst):
        names = [colname] if colname else [c for c in src.collections if c.startswith("PWM_")]
        dst.collections = names
    for c in dst.collections:
        e = bpy.data.objects.new(c.name, None)
        e.instance_type = 'COLLECTION'; e.instance_collection = c
        site.objects.link(e)
        print("LINKED", rel, c.name)

# ---------------- terrain (SRTM calibrated to Street View) textured with the georeferenced satellite views
import csv
from terrain import z_model, SEA_Z
O_LAT, O_LON = 5.281400, 100.288800
def enu(lat, lon): return ((lon - O_LON) * 110847.0, (lat - O_LAT) * 110574.0)
CSVF = os.path.join(BL, "museum_survey", "penang_war_museum_sitemap_points.csv")
rows = list(csv.DictReader(open(CSVF, encoding="utf-8")))
pads = []   # (cx, cy, half_x, half_y, rot_rad, z)
for r in rows:
    x, y = float(r["model_x"]), float(r["model_y"])
    if r["type"] in ("surveyed", "satellite") and r["size_E_m"]:
        pads.append((x, y, float(r["size_E_m"]) / 2 + 1.0, float(r["size_N_m"]) / 2 + 1.0, math.radians(float(r["rot_deg_ccw"] or 0)), z_model(x, y)))
    elif r["type"] in ("sketch_relic", "sketch_feature"):
        pads.append((x, y, 9.5, 5.0, math.radians(-154), z_model(x, y)))
pads.append((0.0, 5.0, 12.5, 8.0, 0.0, 0.0))                       # entrance 1 forecourt / drive
pads.append((-2.0, 18.0, 14.0, 10.0, 0.0, z_model(-2.0, 18.0)))    # entrance 2 plaza
walk = [(float(r["model_x"]), float(r["model_y"])) for r in rows if r["id"].startswith("B09_")]
BLEND = 6.0
def smooth(t): t = max(0.0, min(1.0, t)); return t * t * (3 - 2 * t)
def height(x, y):
    h = z_model(x, y); best_w, best_z = 0.0, h
    for cx, cy, hx, hy, rot, pz in pads:
        dx, dy = x - cx, y - cy
        if abs(dx) > hx + BLEND + 20 or abs(dy) > hy + BLEND + 20: continue
        c, s_ = math.cos(-rot), math.sin(-rot); lx, ly = dx * c - dy * s_, dx * s_ + dy * c
        d = math.hypot(max(0.0, abs(lx) - hx), max(0.0, abs(ly) - hy))
        w = smooth(1 - d / BLEND)
        if w > best_w: best_w, best_z = w, pz
    for (ax, ay), (bx, by) in zip(walk, walk[1:]):          # walkway corridor follows its own profile
        vx, vy = bx - ax, by - ay; L2 = vx * vx + vy * vy
        t = max(0.0, min(1.0, ((x - ax) * vx + (y - ay) * vy) / L2)); px, py = ax + t * vx, ay + t * vy
        d = max(0.0, math.hypot(x - px, y - py) - 2.6); w = smooth(1 - d / BLEND)
        if w > best_w: best_w, best_z = w, z_model(px, py)
    return h + (best_z - h) * best_w

X0, X1, Y0, Y1, STEP = -450.0, 350.0, -250.0, 330.0, 4.0
nx, ny = int((X1 - X0) / STEP) + 1, int((Y1 - Y0) / STEP) + 1
SATS = {"SAT07": ("SAT07_context_912m_center_5.2805_100.289.jpg", 5.2805, 100.2890, 0.2667 * 912 / 166, (60, 140, 800, 560)),
        "SAT01": ("SAT01_site_overview_228m.jpg", 5.2809, 100.2893, 0.2667 * 228 / 166, (60, 60, 800, 560))}
def uv_for(key, x, y):
    f, la, lo, s, crop = SATS[key]; Ec, Nc = enu(la, lo)
    E, N = -x, -y; px = 400 + (E - Ec) / s; py = 300 - (N - Nc) / s
    inside = crop[0] <= px <= crop[2] and crop[1] <= py <= crop[3]
    return (px / 800.0, 1 - py / 600.0), inside
bm = bmesh.new()
uv7 = bm.loops.layers.uv.new("UV_SAT07"); uv1 = bm.loops.layers.uv.new("UV_SAT01")
mask = bm.loops.layers.float_color.new("SAT01_mask") if hasattr(bm.loops.layers, "float_color") else bm.loops.layers.color.new("SAT01_mask")
V = [[bm.verts.new((X0 + i * STEP, Y0 + j * STEP, height(X0 + i * STEP, Y0 + j * STEP))) for i in range(nx)] for j in range(ny)]
cache = {}
for j in range(ny - 1):
    for i in range(nx - 1):
        f = bm.faces.new((V[j][i], V[j][i + 1], V[j + 1][i + 1], V[j + 1][i]))
        for lp in f.loops:
            x, y = lp.vert.co.x, lp.vert.co.y
            k = (round(x, 2), round(y, 2))
            if k not in cache: cache[k] = (uv_for("SAT07", x, y), uv_for("SAT01", x, y))
            (a7, _), (a1, ins) = cache[k]
            lp[uv7].uv = a7; lp[uv1].uv = a1; lp[mask] = (1.0, 1.0, 1.0, 1.0) if ins else (0.0, 0.0, 0.0, 1.0)
for f in bm.faces:
    if f.normal.z < 0: f.normal_flip()
me = bpy.data.meshes.new("PWM_Terrain"); bm.to_mesh(me); bm.free()
for p in me.polygons: p.use_smooth = True
m = bpy.data.materials.new("Terrain_Satellite"); m.use_nodes = True
nt = m.node_tree; N = nt.nodes; Lk = nt.links.new
out = next(n for n in N if n.type == "OUTPUT_MATERIAL")
for n in list(N):
    if n.type == "BSDF_PRINCIPLED": N.remove(n)
def imgnode(key, uvname):
    t = N.new("ShaderNodeTexImage"); t.image = bpy.data.images.load(os.path.join(SS, SATS[key][0])); t.extension = 'EXTEND'
    u = N.new("ShaderNodeUVMap"); u.uv_map = uvname; Lk(u.outputs[0], t.inputs["Vector"]); return t
t7 = imgnode("SAT07", "UV_SAT07"); t1 = imgnode("SAT01", "UV_SAT01")
at = N.new("ShaderNodeVertexColor"); at.layer_name = "SAT01_mask"
mx = N.new("ShaderNodeMix"); mx.data_type = 'RGBA'
Lk(at.outputs["Color"], mx.inputs[0]); Lk(t7.outputs["Color"], mx.inputs[6]); Lk(t1.outputs["Color"], mx.inputs[7])
bsdf = N.new("ShaderNodeBsdfDiffuse"); em = N.new("ShaderNodeEmission"); em.inputs["Strength"].default_value = 0.55
Lk(mx.outputs[2], bsdf.inputs["Color"]); Lk(mx.outputs[2], em.inputs["Color"])
add = N.new("ShaderNodeAddShader"); Lk(bsdf.outputs[0], add.inputs[0]); Lk(em.outputs[0], add.inputs[1]); Lk(add.outputs[0], out.inputs["Surface"])
me.materials.append(m)
ground = bpy.data.collections.new("PWM_Terrain"); sc.collection.children.link(ground)
terr = bpy.data.objects.new("PWM_Terrain_SRTM_SVcalibrated", me); ground.objects.link(terr)
# sea plane at mean sea level
sm = bpy.data.materials.new("Sea"); sm.use_nodes = True
sb = next(n for n in sm.node_tree.nodes if n.type == "BSDF_PRINCIPLED"); sb.inputs["Base Color"].default_value = (0.05, 0.2, 0.28, 1); sb.inputs["Roughness"].default_value = 0.08
sbm = bmesh.new(); bmesh.ops.create_grid(sbm, x_segments=1, y_segments=1, size=500)
seame = bpy.data.meshes.new("Sea"); sbm.to_mesh(seame); sbm.free(); seame.materials.append(sm)
sea = bpy.data.objects.new("Sea_MeanSeaLevel", seame); ground.objects.link(sea); sea.location = ((X0 + X1) / 2, (Y0 + Y1) / 2, SEA_Z + 0.3); sea.scale = (0.8, 0.58, 1)
# lift the entrance models (built flat) onto the terrain
for o in site.objects:
    if o.name == "WarMuseumEntrance2": o.location.z = z_model(-2.0, 18.0)
print("TERRAIN", nx, "x", ny, "verts; sea z", round(SEA_Z, 1))

# origin marker, sun, cameras
o = bpy.data.objects.new("Origin_O_GateFront_5.281400N_100.288800E", None); sc.collection.objects.link(o); o.empty_display_type = 'ARROWS'; o.empty_display_size = 5
ld = bpy.data.lights.new("Sun", 'SUN'); ld.energy = 3.5; s = bpy.data.objects.new("Sun", ld); sc.collection.objects.link(s)
s.rotation_euler = (math.radians(45), 0, math.radians(-30))
for nm, loc, look, lens, ortho in (("Cam_TopDown_NorthUp", (-40, 50, 500), None, 50, 230),
                                   ("Cam_Oblique_FromNorthEast", (-150, -110, 110), (-35, 55, 0), 35, 0), ("Cam_Oblique_FromSea_SouthEast", (-220, 180, 70), (-30, 60, 0), 30, 0)):
    cd = bpy.data.cameras.new(nm); cd.clip_end = 3000; c = bpy.data.objects.new(nm, cd); sc.collection.objects.link(c); c.location = loc
    if ortho:
        cd.type = 'ORTHO'; cd.ortho_scale = ortho; c.rotation_euler = (0, 0, math.pi)   # north up (model -y = north)
    else:
        from mathutils import Vector
        cd.lens = lens; c.rotation_euler = (Vector(look) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
sc.camera = bpy.data.objects["Cam_Oblique_FromNorthEast"]
w = bpy.data.worlds.new("World"); sc.world = w; w.use_nodes = True
bg = next(n for n in w.node_tree.nodes if n.type == "BACKGROUND"); bg.inputs[0].default_value = (0.6, 0.72, 0.88, 1)
try: sc.view_settings.view_transform = 'AgX'
except Exception: pass
sc.render.resolution_x, sc.render.resolution_y = 1600, 1000
bpy.ops.file.pack_all()
bpy.ops.wm.save_mainfile()
print("SAVED", OUT)
