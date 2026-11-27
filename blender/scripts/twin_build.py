"""Build the web scene from the Penang War Museum digital twin (blender/penang_war_museum, see blender/reproduce.md).

Replaces build_muzium.py as the first step of the pipeline (2026-11-27). Run in background Blender through
twin_pipeline.py, or inside Blender:
    exec(open("/Users/izardy/Documents/virtualtourism/blender/scripts/twin_build.py").read())

What it does
1. Reads penang_war_museum_sitemap.blend only to learn where each linked structure collection is instanced, and to take
   the calibrated terrain (SRTM + Street View) and the sea plane. The twin's files are never written.
2. Appends the structure collections from site_structures/*.blend (all except the vegetation file and the stand-alone
   pill box studies PB1/PB2), applies the instance placement, and turns everything 180 deg about z: the twin's frame
   is x = -E, y = -N (gate front = origin, model built facing -y); the web scene uses x = E (east), y = N (north),
   z up, so glTF stays x east, y up, z south as the viewer expects.
3. Drops the twin's own heavy vegetation (46M triangles) and the baked Poly Haven trees in the entrance plaza (their
   positions are kept for hero trees); decimates the other heavy plaza assets (potted plants, stumps, cannon).
4. Bakes every mesh (modifiers applied, text converted) and merges faces by role and material:
   floor_twin_* = upward faces within 0.6 m of the ground on objects larger than 2 m2 (walkable),
   struct_twin_* = the rest of large objects (colliders), deco_twin_* = small items, signs, flags, plants.
   Procedural twin materials become the scene's Poly Haven materials by name (concrete, brick, timber, zinc, paving,
   soil, grass, camouflage) with box-mapped UVs; others keep their colour (procedural colour ramps flattened for glTF).
5. Terrain -> ground_terrain with the Poly Haven forest-floor material (the Google satellite drape is not shipped).
6. Writes the markers the app needs: spawn (outside the gate), hotspot_<slug> for the 10 stories, loc_<id> for every
   row of the twin's points CSV, a memorial plaque (not in the twin), blender/out/hotspots.json, site_points.json and
   fixtures.json (tree exclusion zones and the plaza's tree spots for place_props.py).
"""
import bpy, bmesh, csv, json, math, os, glob
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

ROOT = "/Users/izardy/Documents/virtualtourism"
TEX = ROOT + "/blender/assets/polyhaven/textures"
TW = ROOT + "/blender/penang_war_museum"
SITEMAP = TW + "/penang_war_museum_sitemap.blend"
CSV = TW + "/museum_survey/penang_war_museum_sitemap_points.csv"
R180 = Matrix.Rotation(math.pi, 4, "Z")

# ---------------------------------------------------------------- 1. instance placements, terrain and sea from the site map
bpy.ops.wm.read_homefile(use_empty=True)
with bpy.data.libraries.load(SITEMAP, link=False) as (src, dst):
    dst.objects = [n for n in src.objects]
INST, TERR, SEA = {}, None, None
for o in dst.objects:
    if o is None: continue
    if o.type == "EMPTY" and o.instance_type == "COLLECTION" and o.instance_collection:
        INST[o.instance_collection.name.split(".")[0]] = o.matrix_basis.copy()      # (matrix_world is stale until linked)
    elif o.name.startswith("PWM_Terrain"): TERR = o
    elif o.name.startswith("Sea_"): SEA = o
for o in list(bpy.data.objects):
    if o not in (TERR, SEA): bpy.data.objects.remove(o, do_unlink=True)
for c in list(bpy.data.collections): bpy.data.collections.remove(c)
for lib in list(bpy.data.libraries): bpy.data.libraries.remove(lib)
SEA_Z = (SEA.matrix_basis.translation.z if SEA else -68.3)
print("instances in the site map:", sorted(INST), "sea z", round(SEA_Z, 2))

scene = bpy.context.scene
scene["twin"] = True; scene["sea_z"] = SEA_Z; scene["layout_rot"] = 0.0
exec(open(ROOT + "/blender/scripts/scene_lib.py").read(), globals())          # MATS, TILE, uv_box

# ---------------------------------------------------------------- 2. append the structure collections
SKIP_FILES = ("_V_vegetation", "_PB1_", "_PB2_")
STRUCT_OBJS = []
for path in sorted(glob.glob(TW + "/site_structures/*.blend")):
    if any(k in path for k in SKIP_FILES): continue
    with bpy.data.libraries.load(path, link=False) as (src, dst):
        names = [n for n in src.collections if n.split(".")[0] in INST]
        dst.collections = names
    for c in dst.collections:
        M = R180 @ INST.get(c.name.split(".")[0], Matrix())
        scene.collection.children.link(c)
        for o in c.all_objects:
            if o.parent is None: o.matrix_basis = M @ o.matrix_basis
            STRUCT_OBJS.append(o)
    print("appended", os.path.basename(path), [c.name for c in dst.collections])
for o in (TERR, SEA):
    if o:
        scene.collection.objects.link(o); o.matrix_basis = R180 @ o.matrix_basis
bpy.context.view_layer.update()

# ---------------------------------------------------------------- terrain: raycast helper and the walkable ground
dg = bpy.context.evaluated_depsgraph_get()
TERR.data.transform(TERR.matrix_world); TERR.matrix_world = Matrix()
tbm = bmesh.new(); tbm.from_mesh(TERR.data); TBVH = BVHTree.FromBMesh(tbm)
def ground(x, y):
    hit = TBVH.ray_cast(Vector((x, y, 500.0)), Vector((0, 0, -1)), 2000.0)
    return hit[0].z if hit[0] else SEA_Z
uv_box(tbm, TILE["ground"])
tbm.to_mesh(TERR.data); tbm.free()
TERR.data.materials.clear(); TERR.data.materials.append(MATS["ground"]); TERR.name = "ground_terrain"
for p in TERR.data.polygons: p.use_smooth = True
if SEA:
    SEA.name = "sea_water"; SEA.data.materials.clear(); SEA.data.materials.append(MATS["water"])
    SEA.scale = (4.0, 4.0, 1.0)                                         # a wider sea out to the fog
xs = [v.co.x for v in TERR.data.vertices]; ys = [v.co.y for v in TERR.data.vertices]
scene["bounds"] = [min(xs), min(ys), max(xs), max(ys)]

# ---------------------------------------------------------------- 3. vegetation in the plaza: keep spots, drop the meshes
TREE_SPOTS = []
for o in list(STRUCT_OBJS):
    if o.type == "MESH" and any(m and m.name.startswith("island_tree") for m in o.data.materials):
        p = o.matrix_world.translation; TREE_SPOTS.append([round(p.x, 2), round(p.y, 2)])
        STRUCT_OBJS.remove(o); bpy.data.objects.remove(o, do_unlink=True)
print("plaza trees replaced by hero-tree spots:", len(TREE_SPOTS))

# ---------------------------------------------------------------- 4. bake and merge
MATMAP = [  # (substring in the twin material name, lower case) -> scene material; first match wins
    ("weatheredconcrete", "conc_w"), ("greyconcrete", "conc_w"), ("concretepavement", "floor"), ("concrete", "conc_w"),
    ("facebrick", "redbrick"), ("brick", "redbrick"), ("rubble", "rock"), ("stone", "rock"),
    ("weatheredtimber", "wood"), ("darktimber", "wood"), ("timber", "wood"), ("logbark", "wood"), ("driftwood", "wood"),
    ("corrugatedzinc", "roof"), ("zincroof", "roof"), ("zinc", "roof"), ("rustyroof", "roof"),
    ("paving", "floor"), ("asphalt", "asphalt"), ("soil", "soil"), ("grass", "ground"), ("camo", "camo"),
]
KEEP_COLOUR = ("red", "teal", "green", "blue", "white", "black", "sign", "poster", "pennant", "banner", "notice")
def scene_mat(m):
    if m is None: return "conc_w"
    n = m.name.lower().split(".")[0]
    if any(k in n for k in ("_diff", "polyhaven")) or any(nd.type == "TEX_IMAGE" for nd in (m.node_tree.nodes if m.node_tree else [])):
        return m                                                       # Poly Haven asset with image textures: keep
    if "redpaving" in n: return m
    for k, v in MATMAP:
        if k in n: return v
    return m

def flatten(m):
    """glTF keeps only image textures: give a procedural base colour its colour-ramp average and unlink it."""
    if not m.node_tree: return
    bsdf = next((n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
    if not bsdf: return
    for sn in ("Base Color", "Roughness", "Normal"):
        s = bsdf.inputs.get(sn)
        if not s or not s.is_linked or s.links[0].from_node.type == "TEX_IMAGE": continue
        if sn == "Base Color":
            ramp = next((n for n in m.node_tree.nodes if n.type == "VALTORGB"), None)
            if ramp:
                els = ramp.color_ramp.elements; s.default_value = [sum(e.color[i] for e in els) / len(els) for i in range(3)] + [1]
        for l in list(s.links): m.node_tree.links.remove(l)

DECO_WORDS = ("flag", "sign", "board", "banner", "poster", "text", "letter", "pennant", "plaque", "lantern", "mannequin",
              "net", "vine", "bamboo", "plant", "fern", "shrub", "calathea", "anthurium", "pachira", "rock_moss", "lamp",
              "rope", "statue", "flashlight", "binocular", "crate", "box", "barrel", "jerrycan", "bench", "stool", "shell")
BUCKETS = {}
def bucket(role, key):
    k = (role, key)
    if k not in BUCKETS: BUCKETS[k] = bmesh.new()
    return BUCKETS[k]
def add_faces(src_bm, faces, dst_bm):
    uv_s = src_bm.loops.layers.uv.active; uv_d = dst_bm.loops.layers.uv.verify(); vmap = {}
    for f in faces:
        vs = []
        for v in f.verts:
            nv = vmap.get(v)
            if nv is None: nv = dst_bm.verts.new(v.co); vmap[v] = nv
            vs.append(nv)
        try: nf = dst_bm.faces.new(vs)
        except ValueError: continue
        nf.smooth = f.smooth
        if uv_s:
            for ls, ld in zip(f.loops, nf.loops): ld[uv_d].uv = ls[uv_s].uv

for m in {s.material for o in STRUCT_OBJS for s in getattr(o, "material_slots", []) if s.material}:
    if not isinstance(scene_mat(m), str): flatten(m)
bpy.context.view_layer.update(); dg = bpy.context.evaluated_depsgraph_get()
ZONES, n_parts, heavy = [], 0, 0
for o in STRUCT_OBJS:
    if o.type not in ("MESH", "FONT", "CURVE") or o.hide_render or o.display_type in ("WIRE", "BOUNDS"): continue
    me = bpy.data.meshes.new_from_object(o.evaluated_get(dg)); me.transform(o.matrix_world)
    bm = bmesh.new(); bm.from_mesh(me)
    ntri = sum(len(f.verts) - 2 for f in bm.faces)
    if ntri > 8000:                                                      # heavy Poly Haven asset: decimate to ~3000
        bmesh.ops.triangulate(bm, faces=bm.faces[:]); bm.to_mesh(me); bm.free()
        tmp = bpy.data.objects.new("_dec", me); scene.collection.objects.link(tmp)
        md = tmp.modifiers.new("d", "DECIMATE"); md.ratio = 3000 / ntri
        bpy.context.view_layer.update(); me2 = bpy.data.meshes.new_from_object(tmp.evaluated_get(bpy.context.evaluated_depsgraph_get()))
        bpy.data.objects.remove(tmp, do_unlink=True); bpy.data.meshes.remove(me); me = me2
        bm = bmesh.new(); bm.from_mesh(me); heavy += 1
    bm.normal_update()
    if not bm.verts: bm.free(); bpy.data.meshes.remove(me); continue
    lo = Vector([min(v.co[i] for v in bm.verts) for i in range(3)]); hi = Vector([max(v.co[i] for v in bm.verts) for i in range(3)])
    size = hi - lo; area = size.x * size.y
    nm = o.name.lower()
    small = max(size.x, size.y) < 1.2 or size.z < 0.25
    role = "deco" if (small or any(w in nm for w in DECO_WORDS) or o.type == "FONT") else "struct"
    if role == "struct" and size.z < 0.9 and area > 2.0: role = "flat"
    if role in ("struct", "flat") and area > 4.0:
        c = (lo + hi) / 2; ZONES.append([round(c.x, 2), round(c.y, 2), round(0.5 * math.hypot(size.x, size.y) + 2.0, 2)])
    groups = {}
    for f in bm.faces:
        mat = me.materials[f.material_index] if f.material_index < len(me.materials) else None
        key = scene_mat(mat)
        r = "deco" if role == "deco" else "struct"
        if role in ("struct", "flat") and area > 2.0 and f.normal.z > 0.7:
            cz = f.calc_center_median()
            if cz.z - ground(cz.x, cz.y) < 0.6: r = "floor"
        if role == "flat" and r == "struct": r = "deco"                  # kerbs and slabs: walk on top, do not block
        groups.setdefault((r, key), []).append(f)
    for (r, key), fs in groups.items(): add_faces(bm, fs, bucket(r, key))
    bm.free(); bpy.data.meshes.remove(me); n_parts += 1

# remove the appended source objects and collections
for c in list(scene.collection.children): scene.collection.children.unlink(c)
for o in STRUCT_OBJS:
    try: bpy.data.objects.remove(o, do_unlink=True)
    except ReferenceError: pass
for c in list(bpy.data.collections): bpy.data.collections.remove(c)

n_obj = 0
for (role, key), bm in BUCKETS.items():
    if not bm.faces: bm.free(); continue
    mname = key if isinstance(key, str) else key.name.split(".")[0]
    name = {"floor": "floor_twin_", "struct": "struct_twin_", "deco": "deco_twin_"}[role] + mname.lower()
    bm.normal_update()
    if isinstance(key, str): uv_box(bm, TILE.get(key, 3.0))
    me = bpy.data.meshes.new(name + "_mesh"); bm.to_mesh(me); bm.free()
    me.materials.append(MATS[key] if isinstance(key, str) else key)
    ob = bpy.data.objects.new(name, me); scene.collection.objects.link(ob); n_obj += 1
print("twin baked:", n_parts, "parts ->", n_obj, "objects;", heavy, "heavy assets decimated")

# ---------------------------------------------------------------- 6. markers
ROWS = list(csv.DictReader(open(CSV)))
def slug(s): return "".join(c.lower() if c.isalnum() else "_" for c in s).strip("_")[:40]
NODES = []
def node(name, x, y, z, **props):
    e = bpy.data.objects.new(name, None); e.empty_display_type = "PLAIN_AXES"; e.location = (x, y, z)
    for k, v in props.items(): e[k] = v
    scene.collection.objects.link(e); NODES.append((name, x, y, z, props)); return e
POS = {}
for r in ROWS:
    if r["type"] == "path": continue
    x, y = float(r["E_m"]), float(r["N_m"]); z = ground(x, y)
    POS[r["id"]] = (x, y, z)
    key = r["id"] if r["id"] != "F" else "F_" + slug(r["name"])
    node(f"loc_{slug(key)}_{slug(r['name'])}", x, y, z, label=r["name"], source=r["source"], accuracy=r["accuracy"])

# memorial plaque (the twin has none): beside the path between the guillotine (R34) and the theatre (R05), provisional
mx, my = (POS["R34"][0] + POS["R05"][0]) / 2 + 6.0, (POS["R34"][1] + POS["R05"][1]) / 2
mz = ground(mx, my); MB = bmesh.new()
def box(bm_, cx, cy, z0, sx, sy, sz):
    bmesh.ops.create_cube(bm_, size=1.0, matrix=Matrix.Translation((cx, cy, z0 + sz / 2)) @ Matrix.Diagonal((sx, sy, sz, 1)))
for (bmk, mk) in (("floor", "floor"), ("plaster", "plaster"), ("black", "black"), ("steel", "steel")):
    b_ = bmesh.new()
    if mk == "floor": box(b_, mx, my - 0.6, mz - 0.3, 3.6, 3.0, 0.42)
    if mk == "plaster": box(b_, mx, my, mz + 0.12, 1.9, 0.7, 0.45)
    if mk == "black": box(b_, mx, my, mz + 0.57, 1.7, 0.16, 1.05)
    if mk == "steel":
        for ax, ay in ((-1.6, 0.6), (-1.6, -0.8), (-1.6, -1.9), (-0.7, -1.9), (0.7, -1.9), (1.6, -1.9), (1.6, -0.8), (1.6, 0.6)):
            box(b_, mx + ax, my + ay, mz + 0.12, 0.07, 0.07, 0.75)
    uv_box(b_, TILE.get(mk, 1.0)); me = bpy.data.meshes.new("memorial_" + mk); b_.to_mesh(me); b_.free(); me.materials.append(MATS[mk])
    ob = bpy.data.objects.new(("floor_" if mk == "floor" else "deco_") + "memorial_" + mk, me); scene.collection.objects.link(ob)
node("loc_memorial_plaque", mx, my, mz, label="To Our Glorious Dead (provisional location)")

# spawn: on the approach road, 8 m in front of the gate (the gate faces north, toward the road), looking south through it
sp = bpy.data.objects.new("spawn", None); sp.empty_display_type = "ARROWS"
sp.location = (0.0, 8.0, ground(0.0, 8.0) + 0.1); sp.rotation_euler = (0, 0, 0); scene.collection.objects.link(sp)

HOT = {                                    # story -> twin point (see blender/reproduce.md and the survey)
    "main-entrance": "B03", "weapons-display": "B17", "lookout-point": "R37", "japanese-tunnel": "R26",
    "escape-route": "B12", "observation-tower": "R24", "command-centre": "R11", "underground-bunker": "R08",
    "prison-area": "R19", "memorial-zone": None,
}
PROVISIONAL = {"memorial-zone", "escape-route", "lookout-point", "japanese-tunnel", "underground-bunker", "observation-tower",
               "command-centre", "prison-area"}
hot_out = {}
for s, pid in HOT.items():
    x, y, _ = POS[pid] if pid else (mx, my, mz)
    z = ground(x, y) + 1.6
    e = bpy.data.objects.new("hotspot_" + s, None); e.empty_display_type = "SPHERE"; e.location = (x, y, z)
    e["provisional"] = s in PROVISIONAL; e["twin_point"] = pid or "memorial"; scene.collection.objects.link(e)
    hot_out[s] = {"blender_xyz": [round(x, 2), round(y, 2), round(z, 2)], "gltf_xyz": [round(x, 2), round(z, 2), round(-y, 2)],
                  "provisional": s in PROVISIONAL, "twin_point": pid or "memorial"}
os.makedirs(ROOT + "/blender/out", exist_ok=True)
json.dump(hot_out, open(ROOT + "/blender/out/hotspots.json", "w"), indent=1)
json.dump({n: {"label": p.get("label"), "gltf_xyz": [round(x, 2), round(z, 2), round(-y, 2)]} for (n, x, y, z, p) in NODES},
          open(ROOT + "/blender/out/site_points.json", "w"), indent=1)
ZONES.append([0.0, -4.0, 14.0])                                       # the gate and its passage
json.dump({"lamps": [], "doors": [], "zones": ZONES, "tree_spots": TREE_SPOTS}, open(ROOT + "/blender/out/fixtures.json", "w"))

sun = bpy.data.lights.new("sun", "SUN"); sun.energy = 3.0; so = bpy.data.objects.new("sun", sun)
so.rotation_euler = (math.radians(50), 0, math.radians(30)); scene.collection.objects.link(so)
scene.unit_settings.system = "METRIC"
print("objects:", len(bpy.data.objects), "zones:", len(ZONES), "terrain bounds:", [round(v) for v in scene["bounds"]],
      "sea z:", round(SEA_Z, 1))
