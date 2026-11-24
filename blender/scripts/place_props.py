"""Muzium Perang Penang: props and vegetation (run after build_muzium.py).

Poly Haven (CC0) models are scan-quality (up to millions of triangles), so each prop is decimated to a small budget
and placed as linked duplicates. Trees are low-poly stand-ins built here (the Poly Haven trees are 1 to 2 million triangles).
Run inside Blender:  exec(open("/Users/izardy/Documents/virtualtourism/blender/scripts/place_props.py").read())
"""
import bpy, bmesh, math, os, random
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree

ROOT = "/Users/izardy/Documents/virtualtourism"
PH = ROOT + "/blender/assets/polyhaven/models"
random.seed(11)

# ---- clean: remove earlier props, the raw asset import, and the previous template collection
for name in ("PROPS", "ASSETS", "TEMPLATES"):
    c = bpy.data.collections.get(name)
    if c:
        for o in list(c.objects): bpy.data.objects.remove(o, do_unlink=True)
        bpy.data.collections.remove(c)
try: bpy.data.orphans_purge(do_recursive=True)
except Exception: pass
TPL = bpy.data.collections.new("TEMPLATES"); bpy.context.scene.collection.children.link(TPL)
PROPS = bpy.data.collections.new("PROPS"); bpy.context.scene.collection.children.link(PROPS)

def ov(active, objs):
    return bpy.context.temp_override(active_object=active, object=active, selected_objects=objs, selected_editable_objects=objs)

def prep(asset, tris):
    """Import a Poly Haven model, bake it to one mesh, decimate to ~tris, put the origin at bottom centre."""
    gl = [f for f in os.listdir(f"{PH}/{asset}") if f.endswith(".gltf")][0]
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=f"{PH}/{asset}/{gl}")
    new = [o for o in bpy.data.objects if o not in before]
    meshes = [o for o in new if o.type == "MESH"]
    for o in meshes:
        for m in list(o.modifiers):
            if m.type == "ARMATURE": o.modifiers.remove(m)
        mw = o.matrix_world.copy(); o.parent = None; o.matrix_world = mw
    for o in new:
        if o.type != "MESH": 
            try: bpy.data.objects.remove(o, do_unlink=True)
            except Exception: pass
    meshes = [o for o in meshes if o.name in bpy.data.objects]
    with ov(meshes[0], meshes): bpy.ops.object.transform_apply(location=True, rotation=True, scale=True, isolate_users=True)
    if len(meshes) > 1:
        with ov(meshes[0], meshes): bpy.ops.object.join()
    ob = meshes[0]; me = ob.data
    me.calc_loop_triangles(); n0 = len(me.loop_triangles)
    if n0 > tris:
        md = ob.modifiers.new("dec", "DECIMATE"); md.ratio = max(0.001, tris / n0)
        with ov(ob, [ob]): bpy.ops.object.modifier_apply(modifier="dec")
    me = ob.data; me.calc_loop_triangles(); n1 = len(me.loop_triangles)
    zs = [v.co.z for v in me.vertices]; xs = [v.co.x for v in me.vertices]; ys = [v.co.y for v in me.vertices]
    me.transform(Matrix.Translation((-(min(xs) + max(xs)) / 2, -(min(ys) + max(ys)) / 2, -min(zs))))
    for c in list(ob.users_collection): c.objects.unlink(ob)
    TPL.objects.link(ob); ob.name = "tpl_" + asset; ob.location = (0, 0, 0)
    ob["tris"] = n1
    print(f"  {asset}: {n0} -> {n1} tris, size {[round(d, 2) for d in ob.dimensions]}")
    return ob

def put(tpl, x, y, z, rot=0.0, scale=1.0, name=None):
    o = bpy.data.objects.new(name or tpl.name.replace("tpl_", ""), tpl.data)
    o.location = (x, y, z); o.rotation_euler = (0, 0, rot); o.scale = (scale,) * 3
    PROPS.objects.link(o); return o

# ---- terrain raycast
terr = bpy.data.objects["ground_terrain"]
bvh = BVHTree.FromObject(terr, bpy.context.evaluated_depsgraph_get())
def ground_z(x, y):
    hit = bvh.ray_cast((x, y, 200.0), (0, 0, -1))
    return hit[0].z if hit[0] else None

SEA_Z = -36.0
locs = {o.name: o.location.copy() for o in bpy.data.objects if o.name.startswith("loc_")}
def loc(prefix):
    for k, v in locs.items():
        if k.startswith(prefix): return v
    raise KeyError(prefix)

# ---- trees (low poly stand-ins)
def mat_flat(name, col, rough=0.9):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = col; b.inputs["Roughness"].default_value = rough
    try: m.use_backface_culling = False
    except Exception: pass
    return m
M_BARK = mat_flat("mat_bark", (0.22, 0.15, 0.09, 1)); M_LEAF = mat_flat("mat_leaf", (0.07, 0.3, 0.07, 1)); M_LEAF2 = mat_flat("mat_leaf_light", (0.16, 0.38, 0.1, 1))

def tree_template(kind):
    bm = bmesh.new()
    if kind == "broad":
        bmesh.ops.create_cone(bm, cap_ends=True, segments=7, radius1=0.45, radius2=0.2, depth=5.0, matrix=Matrix.Translation((0, 0, 2.5)))
        trunk_faces = len(bm.faces)
        for (dx, dy, dz, r) in ((0, 0, 6.2, 2.6), (1.4, 0.6, 5.2, 1.8), (-1.2, -0.8, 5.6, 1.9)):
            bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r, matrix=Matrix.Translation((dx, dy, dz)) @ Matrix.Diagonal((1, 1, 0.8, 1)))
        trunk_n = trunk_faces
    else:   # palm: thin trunk plus crossed frond planes
        bmesh.ops.create_cone(bm, cap_ends=True, segments=6, radius1=0.28, radius2=0.16, depth=8.0, matrix=Matrix.Translation((0, 0, 4.0)))
        trunk_n = len(bm.faces)
        for k in range(8):
            a = k * math.pi / 4
            v = [bm.verts.new(Vector(p)) for p in ((0, -0.35, 0), (0, 0.35, 0), (2.8, 0.25, -1.4), (2.8, -0.25, -1.4))]
            M = Matrix.Translation((0, 0, 8.0)) @ Matrix.Rotation(a, 4, "Z")
            for vv in v: vv.co = M @ vv.co
            bm.faces.new(v)
            w = [bm.verts.new(vv.co) for vv in v[::-1]]; bm.faces.new(w)      # back face (separate verts)
    me = bpy.data.meshes.new("tree_" + kind); bm.to_mesh(me); bm.free()
    me.materials.append(M_BARK); me.materials.append(M_LEAF)
    for i, p in enumerate(me.polygons): p.material_index = 0 if i < trunk_n else 1
    # simple UVs
    uv = me.uv_layers.new(name="UVMap")
    for p in me.polygons:
        for li in p.loop_indices:
            co = me.vertices[me.loops[li].vertex_index].co; uv.data[li].uv = (co.x * 0.2, co.z * 0.2)
    ob = bpy.data.objects.new("tpl_tree_" + kind, me); TPL.objects.link(ob)
    me.calc_loop_triangles(); ob["tris"] = len(me.loop_triangles)
    return ob

T_BROAD = tree_template("broad"); T_PALM = tree_template("palm")

# ---- exclusion map: structures, paths, roads, spawn
paths = []
for nm in ("floor_paths", "floor_road"):
    o = bpy.data.objects.get(nm)
    if o: paths += [(v.co.x, v.co.y) for v in o.data.vertices]
pts_struct = [(v.x, v.y) for k, v in locs.items()]
spawn = bpy.data.objects["spawn"].location
def blocked(x, y):
    if any((x - a) ** 2 + (y - b) ** 2 < 11 ** 2 for a, b in pts_struct): return True
    if any((x - a) ** 2 + (y - b) ** 2 < 4.5 ** 2 for a, b in paths): return True
    if (x - spawn.x) ** 2 + (y - spawn.y) ** 2 < 14 ** 2: return True
    return False

def scatter(n, tpls, zmin, scale=(0.8, 1.3), tries=3000, region=(-300, 270, -240, 240), name=None):
    placed = 0
    for _ in range(tries):
        if placed >= n: break
        x = random.uniform(region[0], region[1]); y = random.uniform(region[2], region[3])
        if blocked(x, y): continue
        z = ground_z(x, y)
        if z is None or z < zmin: continue
        put(random.choice(tpls), x, y, z - 0.1, random.uniform(0, 6.28), random.uniform(*scale), name); placed += 1
    return placed

print("preparing Poly Haven props:")
A = {}
for asset, tris in (("shrub_02", 300), ("fern_02", 300), ("rock_moss_set_01", 900), ("cannon_01", 2500),
                    ("wooden_military_crate", 600), ("wooden_barrels_01", 900), ("barrel_03", 800),
                    ("metal_jerrycan_green", 400), ("old_military_compressor", 2000), ("vintage_radio_transceiver", 1200),
                    ("old_bed_frame", 1200), ("caged_hanging_light", 500), ("ammo_box", 300), ("large_iron_gate", 1200),
                    ("wooden_ladder", 400), ("tree_stump_01", 400)):
    try: A[asset] = prep(asset, tris)
    except Exception as e: print("  FAILED", asset, e)

n_tree = scatter(100, [T_BROAD, T_BROAD, T_PALM], SEA_Z + 2.0, (0.8, 1.5), name="tree")
n_shrub = scatter(28, [A["shrub_02"]], SEA_Z + 1.5, (0.9, 1.8), name="shrub")
n_fern = scatter(40, [A["fern_02"]], SEA_Z + 1.5, (1.0, 2.0), name="fern")
n_rock = scatter(12, [A["rock_moss_set_01"]], SEA_Z + 0.5, (1.0, 2.2), name="rock")
n_stump = scatter(6, [A["tree_stump_01"]], SEA_Z + 2, (0.8, 1.4), name="stump")
print("scattered:", dict(trees=n_tree, shrubs=n_shrub, ferns=n_fern, rocks=n_rock, stumps=n_stump))

# ---- placed props at map locations (offsets are in metres from the building centre, interiors at floor height)
def at(prefix, dx, dy, dz=0.0, rot=0.0, scale=1.0, key=None):
    if key not in A: return None
    b = loc(prefix); z = b.z + dz
    return put(A[key], b.x + dx, b.y + dy, z + 0.15, rot, scale)

if "cannon_01" in A:   at("loc_36_", 0.0, 0.0, 0.0, 0.0, 1.4, "cannon_01")
if "cannon_01" in A:   at("loc_25_", 0.0, 0.0, 0.0, 0.3, 1.4, "cannon_01")
for dx, dy in ((-2, 0), (0, 0.6), (2, -0.6)): at("loc_35_", dx, dy, 0, random.uniform(0, 1), 1.0, "wooden_military_crate")
at("loc_35_", -3.0, 1.5, 0, 0.3, 1.0, "ammo_box"); at("loc_35_", -2.5, 1.7, 0, 0.1, 1.0, "ammo_box")
for dx in (-3.0, 3.0): at("loc_10_", dx, -1.5, 0, 0.0, 1.0, "wooden_military_crate")
at("loc_12_", -9.0, 4.0, 0, 0.4, 1.0, "wooden_barrels_01"); at("loc_12_", 9.5, 4.0, 0, 0.1, 1.0, "wooden_barrels_01"); at("loc_17_", 3.0, 4.0, 0, 0.2, 1.0, "barrel_03")
at("loc_06_", -2.5, 1.5, 0, 0.0, 1.3, "old_military_compressor"); at("loc_06_", 2.2, -1.8, 0, 0.8, 1.0, "metal_jerrycan_green"); at("loc_06_", 2.6, -1.6, 0, 0.2, 1.0, "metal_jerrycan_green")
at("loc_11_", 0.0, 1.5, 0.85, 0.0, 1.0, "vintage_radio_transceiver")      # on a (missing) table: placeholder height
for dx in (-3.5, 0.0, 3.5): at("loc_20_", dx, -1.0, 0, math.pi / 2, 1.0, "old_bed_frame")
for nm in ("loc_26_", "loc_29_"):
    if "caged_hanging_light" not in A: break
    b = loc(nm); put(A["caged_hanging_light"], b.x + 1.0, b.y, b.z + 2.45, 0, 1.0)     # hung at the portal
at("loc_24_", 0.0, 0.0, 5.2, 0.0, 1.0, "wooden_ladder")
at("loc_fac_ticketing", 11.0, 0.0, 0, math.pi / 2, 1.0, "large_iron_gate")

# ---- report
tot = 0
for o in bpy.data.objects:
    if o.type == "MESH" and o.users_collection and o.users_collection[0].name in ("TEMPLATES",): continue
    if o.type == "MESH":
        me = o.data; me.calc_loop_triangles(); tot += len(me.loop_triangles)
print("total triangles in scene (instances counted):", tot, "| instances:", len(PROPS.objects))
TPL.hide_viewport = True; TPL.hide_render = True
