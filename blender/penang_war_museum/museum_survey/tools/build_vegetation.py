"""Scatter Poly Haven trees and understory across the Penang War Museum site, seated on the terrain.
blender -b --factory-startup --python build_vegetation.py -- <out.blend>

Uses the Poly Haven meshes already packed in the entrance-plaza file (Island Tree 02, Pachira aquatica,
Shrub 04, Fern 02, Calathea orbifolia, Anthurium botany - all CC0). Trees avoid every structure footprint
(survey CSV), the walkway corridor, the entrance gate/plaza and the approach road; near visitor areas they
use the full mesh, further away a decimated LOD (same materials) to keep the site map light.
"""
import bpy, math, os, sys, random, csv
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pwm_lib import reset_scene, ground_z, collection, finish
from terrain import SEA_Z

OUT = sys.argv[sys.argv.index("--") + 1]
BL = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(BL, "site_structures", "penang_war_museum_B03_B04_B06_entrance_plaza.blend")
CSVF = os.path.join(BL, "museum_survey", "penang_war_museum_sitemap_points.csv")
random.seed(2026)
reset_scene()

NAMES = ["PH_IslandTree02", "PH_Pachira_c", "PH_Pachira_d", "PH_Shrub04_a", "PH_Shrub04_b", "PH_Shrub04_c", "PH_Shrub04_d",
         "PH_Fern02_a", "PH_Fern02_b", "PH_Fern02_c", "PH_Calathea_a", "PH_Calathea_c", "PH_Anthurium_a", "PH_Anthurium_b"]
with bpy.data.libraries.load(SRC, link=False) as (s, d):
    d.meshes = [n for n in NAMES if n in s.meshes]
ME = {m.name: m for m in d.meshes if m}
for m in ME.values(): m.use_fake_user = False

# far LOD of the island tree (same materials): keep ~30 % of the leaf cards (each card scaled up so the
# canopy still reads full) and decimate only the trunk/branch geometry. Plain decimation destroys leaf cards.
import bmesh
from mathutils import Vector
src = ME["PH_IslandTree02"]
leaf_idx = {i for i, m in enumerate(src.materials) if m and "leaves" in m.name.lower()}
bm = bmesh.new(); bm.from_mesh(src)
leaf_faces = [f for f in bm.faces if f.material_index in leaf_idx]
seen, islands = set(), []
for f in leaf_faces:
    if f.index in seen: continue
    stack, isl = [f], []
    seen.add(f.index)
    while stack:
        g = stack.pop(); isl.append(g)
        for e in g.edges:
            for h in e.link_faces:
                if h.index not in seen and h.material_index in leaf_idx:
                    seen.add(h.index); stack.append(h)
    islands.append(isl)
kill = []
for isl in islands:
    if random.random() < 0.30:
        vs = {v for f in isl for v in f.verts}; c = sum((v.co for v in vs), Vector()) / len(vs)
        for v in vs: v.co = c + (v.co - c) * 1.45
    else:
        kill += isl
bmesh.ops.delete(bm, geom=kill, context='FACES')
wood = [f for f in bm.faces if f.material_index not in leaf_idx]
far = bpy.data.meshes.new("PH_IslandTree02_LODfar"); bm.to_mesh(far); bm.free()
for m in src.materials: far.materials.append(m)
tmp = bpy.data.objects.new("tmp_lod", far); bpy.context.scene.collection.objects.link(tmp)
bpy.context.view_layer.objects.active = tmp; tmp.select_set(True)
bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='DESELECT')
for i, m in enumerate(far.materials):
    if i not in leaf_idx:
        tmp.active_material_index = i; bpy.ops.object.material_slot_select()
bpy.ops.mesh.decimate(ratio=0.15)
bpy.ops.object.mode_set(mode='OBJECT')
bpy.data.objects.remove(tmp, do_unlink=True)
print("tree faces full", len(src.polygons), "far", len(far.polygons), "leaf islands", len(islands))

# ---------------------------------------------------------------- exclusion zones (model frame)
rows = list(csv.DictReader(open(CSVF, encoding="utf-8")))
zones = []      # (cx, cy, half_x, half_y, rot, margin)
for r in rows:
    x, y = float(r["model_x"]), float(r["model_y"])
    if r["type"] in ("surveyed", "satellite") and r["size_E_m"]:
        zones.append((x, y, float(r["size_E_m"]) / 2, float(r["size_N_m"]) / 2, math.radians(float(r["rot_deg_ccw"] or 0)), 4.0))
    elif r["type"] in ("sketch_relic", "sketch_feature"):
        zones.append((x, y, 9.5, 5.0, math.radians(-154), 4.0))
zones += [(0.0, 5.0, 13.0, 9.0, 0.0, 3.0),          # entrance 1 gate + drive
          (-2.0, 18.0, 15.0, 11.0, 0.0, 3.0),       # entrance 2 plaza (has its own trees)
          (0.0, -45.0, 45.0, 35.0, 0.0, 0.0)]       # approach road, car parks and paintball zone north of the gate
walk = [(float(r["model_x"]), float(r["model_y"])) for r in rows if r["id"].startswith("B09_")]
visitor = [(float(r["model_x"]), float(r["model_y"])) for r in rows if r["type"] == "surveyed"] + walk


def in_zone(x, y):
    for cx, cy, hx, hy, rot, m in zones:
        dx, dy = x - cx, y - cy
        if abs(dx) > hx + m + 15 or abs(dy) > hy + m + 15: continue
        c, s_ = math.cos(-rot), math.sin(-rot); lx, ly = dx * c - dy * s_, dx * s_ + dy * c
        if abs(lx) < hx + m and abs(ly) < hy + m: return True
    return False


def dist_walk(x, y):
    best = 1e9
    for (ax, ay), (bx, by) in zip(walk, walk[1:]):
        vx, vy = bx - ax, by - ay; L2 = vx * vx + vy * vy
        t = max(0.0, min(1.0, ((x - ax) * vx + (y - ay) * vy) / L2))
        best = min(best, math.hypot(x - ax - t * vx, y - ay - t * vy))
    return best


def dist_visitor(x, y):
    return min(dist_walk(x, y), min(math.hypot(x - a, y - b) for a, b in visitor))


top = collection("PWM_V_Vegetation_PolyHaven")
trees = collection("V_Trees", top); under = collection("V_Understory", top)
root = bpy.data.objects.new("V_Vegetation_Root (site coords)", None); top.objects.link(root); root.empty_display_type = 'ARROWS'


def place(col, mesh, name, x, y, scale, rz=None, sink=0.15):
    o = bpy.data.objects.new(name, mesh); col.objects.link(o); o.parent = root
    o.location = (x, y, ground_z(x, y) - sink)
    o.rotation_euler = (random.uniform(-0.04, 0.04), random.uniform(-0.04, 0.04), rz if rz is not None else random.uniform(0, 2 * math.pi))
    o.scale = scale
    return o


# ---------------------------------------------------------------- trees: jittered grid over the hill
X0, X1, Y0, Y1, SP = -175.0, 175.0, -40.0, 235.0, 12.5
nt = nf = 0
y = Y0
while y <= Y1:
    x = X0
    while x <= X1:
        px, py = x + random.uniform(-4.5, 4.5), y + random.uniform(-4.5, 4.5)
        if ground_z(px, py) > SEA_Z + 4.0 and not in_zone(px, py) and dist_walk(px, py) > 5.5 and random.random() < 0.82:
            near = dist_visitor(px, py) < 45
            s = random.uniform(2.3, 3.6); sz = s * random.uniform(0.9, 1.15)
            place(trees, ME["PH_IslandTree02"] if near else far, f"Tree_{'near' if near else 'far'}_{nt + nf:03d}", px, py, (s, s, sz))
            if near: nt += 1
            else: nf += 1
        x += SP
    y += SP
print("trees near", nt, "far", nf)

# ---------------------------------------------------------------- understory near visitor areas (shrubs, pachira, ferns, broad leaves)
UND = [("PH_Pachira_c", (1.0, 1.6)), ("PH_Pachira_d", (1.0, 1.5)), ("PH_Shrub04_a", (5, 8)), ("PH_Shrub04_b", (5, 8)),
       ("PH_Shrub04_c", (5, 8)), ("PH_Shrub04_d", (5, 7)), ("PH_Fern02_a", (1.2, 1.8)), ("PH_Fern02_b", (1.0, 1.6)),
       ("PH_Fern02_c", (1.0, 1.6)), ("PH_Calathea_a", (1.5, 2.2)), ("PH_Calathea_c", (1.5, 2.2)), ("PH_Anthurium_a", (1.6, 2.2)),
       ("PH_Anthurium_b", (1.6, 2.2))]
nu = 0
for k in range(5000):
    px, py = random.uniform(-120, 140), random.uniform(-10, 160)
    d = dist_visitor(px, py)
    if not (2.8 < d < 22) or in_zone(px, py) or dist_walk(px, py) < 2.4 or ground_z(px, py) < SEA_Z + 4: continue
    if random.random() > (1.1 - d / 24): continue          # denser close to paths
    nm, (a, b) = random.choice(UND); s = random.uniform(a, b)
    place(under, ME[nm], f"Understory_{nm[3:]}_{nu:03d}", px, py, (s, s, s), sink=0.05); nu += 1
print("understory", nu)

for prt in (root,): prt.location = (0, 0, 0)
try:
    top.asset_mark(); top.asset_data.description = "Poly Haven trees + understory scattered over the museum site (CC0)"
except Exception as e: print(e)
if os.path.exists(OUT): raise SystemExit("REFUSING to overwrite " + OUT)
bpy.ops.file.pack_all(); bpy.ops.outliner.orphans_purge(do_local_ids=True, do_recursive=True)
bpy.ops.wm.save_as_mainfile(filepath=OUT)
print("SAVED", OUT, len(bpy.data.objects))
