"""Muzium Perang Penang: props and vegetation (run after build_muzium.py).

Poly Haven (CC0) models are scan-quality (up to millions of triangles), so each prop is decimated to a small budget
and placed as linked duplicates. Trees are Poly Haven island trees thinned to about 10k triangles by thin_tree.py.
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

import re as _re
def _variant(name):
    m_ = _re.search(r"_([a-h])(?:_LOD0)?(?:\.\d+)?$", name)
    return m_.group(1) if m_ else ""

def _bake(meshes, tris, name):
    for o in meshes:
        if o.data.users > 1: o.data = o.data.copy()          # variants share meshes; transform_apply needs single users
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
    TPL.objects.link(ob); ob.name = name; ob.location = (0, 0, 0)
    ob["tris"] = n1
    print(f"  {name[4:]}: {n0} -> {n1} tris, size {[round(d, 2) for d in ob.dimensions]}")
    return ob

def prep(asset, tris, variants="join"):
    """Import a Poly Haven model, bake it to one mesh, decimate to ~tris, put the origin at bottom centre.
    Many Poly Haven files hold several variants side by side (suffix _a, _b, ...): variants="split" makes one template
    per variant (returned as a list, each decimated to ~tris), "first" keeps variant a only, "join" bakes everything."""
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
    names = [o.name for o in meshes if o.name in bpy.data.objects]
    groups = {}
    for n_ in names: groups.setdefault(_variant(n_), []).append(bpy.data.objects[n_])
    if variants == "join" or len(groups) == 1:
        return _bake([bpy.data.objects[n_] for n_ in names], tris, "tpl_" + asset)
    keys = sorted(groups)
    if variants == "first":
        for k in keys[1:]:
            for o in groups[k]: bpy.data.objects.remove(o, do_unlink=True)
        return _bake(groups[keys[0]], tris, "tpl_" + asset)
    return [_bake(groups[k], tris, f"tpl_{asset}_{k or 'x'}") for k in keys]

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

# ---- trees: Poly Haven island trees, thinned from 1-2 million triangles to about 10k each (see thin_tree.py)
exec(open(ROOT + "/blender/scripts/thin_tree.py").read())

def tree_template(asset, keep, leaf_scale, wood_tris):
    gl = [f for f in os.listdir(f"{PH}/{asset}") if f.endswith(".gltf")][0]
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=f"{PH}/{asset}/{gl}")
    new = [o for o in bpy.data.objects if o not in before]
    ob = max((o for o in new if o.type == "MESH"), key=lambda o: len(o.data.polygons))
    for o in new:
        if o is not ob: bpy.data.objects.remove(o, do_unlink=True)
    mw = ob.matrix_world.copy(); ob.parent = None; ob.matrix_world = mw
    with ov(ob, [ob]): bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    n_leaves, tris = thin_tree(ob, keep=keep, leaf_scale=leaf_scale, wood_tris=wood_tris)
    # origin at the trunk base (the scanned trees lean, so the bounding-box centre is not above the trunk)
    me = ob.data; leaf_i = next(i for i, m in enumerate(me.materials) if "leaves" in m.name)
    wood = {v for p in me.polygons if p.material_index != leaf_i for v in p.vertices}
    zmin = min(me.vertices[i].co.z for i in wood)
    base = [me.vertices[i].co for i in wood if me.vertices[i].co.z < zmin + 0.25]
    bx = sum(c.x for c in base) / len(base); by = sum(c.y for c in base) / len(base)
    me.transform(Matrix.Translation((-bx, -by, -zmin)))
    ob["base_r"] = max(math.hypot(c.x - bx, c.y - by) for c in base) + 0.05     # trunk footprint radius (m, unscaled)
    for c in list(ob.users_collection): c.objects.unlink(ob)
    TPL.objects.link(ob); ob.name = "tpl_tree_" + asset; ob.location = (0, 0, 0); ob["tris"] = tris
    print(f"  {asset}: {n_leaves} leaf cards, {tris} tris, size {[round(d, 2) for d in ob.dimensions]}")
    return ob

# background trees: about 20% of the leaves, cards 1.9x; hero trees (a few, next to the entrance and main stops): half
# the leaves at near-original size, fuller trunk. Total tree budget about 800k triangles drawn.
T_TREE1 = tree_template("island_tree_01", 0.20, 1.9, 6000)     # 5 m tall as scanned; scaled up 1.6-2.4x when placed
T_TREE2 = tree_template("island_tree_02", 0.22, 1.8, 5000)
T_HERO = tree_template("island_tree_01", 0.50, 1.3, 24000); T_HERO.name = "tpl_tree_hero"
# far trees: only seen from 10 m or more away, so fewer, larger leaf cards (about 7k triangles)
T_FAR1 = tree_template("island_tree_01", 0.08, 2.8, 2500); T_FAR1.name = "tpl_tree_far1"
T_FAR2 = tree_template("island_tree_02", 0.09, 2.7, 2000); T_FAR2.name = "tpl_tree_far2"
# distant trees: 32 m or more from any path or building, very few large cards (about 3.5k triangles); they fill the hillsides
T_DIST = tree_template("island_tree_01", 0.04, 3.6, 1500); T_DIST.name = "tpl_tree_dist"
# phone tier: used only by export_mobile.py for the distant trees of the phone model (about 1.5k triangles)
T_MOB = tree_template("island_tree_01", 0.022, 4.4, 700); T_MOB.name = "tpl_tree_mob"

# ---- exclusion map: structures, paths, roads, spawn
paths = []
for nm in ("floor_paths", "floor_road"):
    o = bpy.data.objects.get(nm)
    if o: paths += [(v.co.x, v.co.y) for v in o.data.vertices]
pts_struct = [(v.x, v.y) for k, v in locs.items()]
spawn = bpy.data.objects["spawn"].location
def blocked(x, y, path_r=4.5, sr=None):
    sr = max(11.0, path_r) if sr is None else sr  # far and distant trees also keep away from buildings and stops
    if any((x - a) ** 2 + (y - b) ** 2 < sr ** 2 for a, b in pts_struct): return True
    if any((x - a) ** 2 + (y - b) ** 2 < path_r ** 2 for a, b in paths): return True
    if (x - spawn.x) ** 2 + (y - spawn.y) ** 2 < 14 ** 2: return True
    for (zx, zy, zr) in ZONES:                     # the user's models (entrance, pill boxes)
        if (x - zx) ** 2 + (y - zy) ** 2 < zr * zr: return True
    for (ax, ay, bx, by, r) in CLEARINGS:          # open ground seen on the satellite image
        t = max(0.0, min(1.0, ((x - ax) * (bx - ax) + (y - ay) * (by - ay)) / ((bx - ax) ** 2 + (by - ay) ** 2)))
        if (x - ax - t * (bx - ax)) ** 2 + (y - ay - t * (by - ay)) ** 2 < r * r: return True
    return False

import json as _jz
ZONES = _jz.load(open(ROOT + "/blender/out/fixtures.json")).get("zones", [])
# strict sitemap layout: no satellite clearings any more; the open lawns of the map (light green) stay free of filler trees
CLEARINGS = []
import json as _json
RK = _json.load(open(ROOT + "/reference/sitemap/reeaki_layout.json")); _RH = RK["height"]
def cover_at(x, y):
    i = int(round((x - _RH["e0"]) / _RH["step"])); j = int(round((y - _RH["n0"]) / _RH["step"]))
    if not (0 <= i < _RH["ne"] and 0 <= j < _RH["nn"]): return 0
    return _RH["cover"][j * _RH["ne"] + i]

TREES_AT = []

def settle_z(x, y, r):
    """Height to put an object at so that its whole footprint (radius r) touches the ground on a slope:
    the lowest terrain point in the footprint, sunk by a further 10% of the radius."""
    zs = [ground_z(x + r * math.cos(a), y + r * math.sin(a)) for a in [i * math.pi / 4 for i in range(8)]] + [ground_z(x, y)]
    zs = [z for z in zs if z is not None]
    return (min(zs) - 0.1 * r - 0.08) if zs else None

def footprint(tpl, scale):
    if "base_r" in tpl: return tpl["base_r"] * scale
    return 0.35 * min(tpl.dimensions.x, tpl.dimensions.y) * scale

def scatter(n, tpls, zmin, scale=(0.8, 1.3), tries=3000, region=(-300, 240, -200, 200), name=None, path_r=4.5, where=None):
    placed = 0
    for _ in range(tries):
        if placed >= n: break
        x = random.uniform(region[0], region[1]); y = random.uniform(region[2], region[3])
        if where and not where(x, y): continue
        if blocked(x, y, path_r): continue
        if name and name.startswith("tree") and any((x - a) ** 2 + (y - b) ** 2 < 6.0 ** 2 for a, b in TREES_AT): continue   # no two trunks closer than 6 m
        tpl = random.choice(tpls); sc = random.uniform(*scale)
        z = settle_z(x, y, footprint(tpl, sc))
        if z is None or z < zmin: continue
        put(tpl, x, y, z, random.uniform(0, 6.28), sc, name); placed += 1
        if name and name.startswith("tree"): TREES_AT.append((x, y))
    return placed

SCONCE_YAW = math.pi / 2       # the wall lamp model sticks out along -Y; this turns it to face local +x (out of the door wall)
print("preparing Poly Haven props:")
A = {}
# files with several variants side by side: one template per variant, or the first one only
VARIANTS = {"old_military_crate": "first", "calathea_orbifolia_01": "split", "anthurium_botany_01": "split",
            "shrub_03": "split", "pachira_aquatica_01": "split", "wooden_crate_02": "first"}
for asset, tris in (("shrub_02", 300), ("fern_02", 300), ("rock_moss_set_01", 900), ("cannon_01", 2500),
                    ("wooden_military_crate", 600), ("wooden_barrels_01", 900), ("barrel_03", 800),
                    ("metal_jerrycan_green", 400), ("old_military_compressor", 2000), ("vintage_radio_transceiver", 1200),
                    ("old_bed_frame", 1200), ("caged_hanging_light", 500), ("ammo_box", 300),
                    ("wooden_ladder", 400), ("tree_stump_01", 400), ("root_cluster_01", 1500),
                    ("industrial_wall_lamp", 1500),
                    # phone-friendly Poly Haven set (2026-11-27): 1k textures, decimated to small budgets
                    ("WoodenTable_01", 500), ("wooden_table_02", 200), ("metal_office_desk", 1200), ("folding_wooden_stool", 500),
                    ("worn_metal_rack", 900), ("wooden_bookshelf_worn", 1000), ("standing_chalkboard_01", 400),
                    ("wooden_crate_01", 600), ("wooden_crate_02", 600), ("old_military_crate", 800), ("oil_tin", 300),
                    ("can_rusted", 300), ("rusted_spade_01", 400), ("picke_dirty_01", 400), ("wooden_bucket_01", 500),
                    ("metal_toolbox", 800), ("wooden_ladder_02", 600), ("hanging_industrial_lamp", 800),
                    ("wooden_picnic_table", 1200), ("metal_trash_can", 900), ("lifebuoy", 800), ("ocean_buoy", 1500),
                    ("anthurium_botany_01", 500), ("calathea_orbifolia_01", 700),
                    ("shrub_04", 900), ("pachira_aquatica_01", 1200),
                    ("shrub_03", 700), ("rock_07", 600), ("rock_face_01", 1500), ("rock_face_02", 1500),
                    ("rock_moss_set_02", 1200), ("tree_stump_02", 800), ("dead_tree_trunk", 1500),
                    ("dry_branches_medium_01", 900)):
    try: A[asset] = prep(asset, tris, VARIANTS.get(asset, "join"))
    except Exception as e: print("  FAILED", asset, e)

# The museum's scale model and the satellite image show closed forest right up to the buildings, so the detailed
# trees and an extra set of far trees go into the fort core (CORE, metres), where visitors walk; the rest fill the hills.
# Trees follow the reeaki map: one tree (or a small group) on every tree drawn on the map, detailed near the paths and
# far-detail elsewhere; then filler trees only on the map's dark-green (wooded) ground and on the hills beyond the map.
n_tree = 0
def near_path_pts(x, y, r): return any((x - a) ** 2 + (y - b) ** 2 < r * r for a, b in paths)
for (te, tn, k) in RK["trees"]:
    for j in range(int(k)):
        for _t in range(12):
            x = te + random.uniform(-3.5, 3.5) * (1 + j); y = tn + random.uniform(-3.5, 3.5) * (1 + j)
            if blocked(x, y, 3.5, 7.5) or any((x - a) ** 2 + (y - b) ** 2 < 5.0 ** 2 for a, b in TREES_AT): continue
            near = near_path_pts(x, y, 25.0)
            tpl = random.choice([T_TREE1, T_TREE1, T_TREE2] if near else [T_FAR1, T_FAR1, T_FAR2]); sc = random.uniform(1.7, 2.4)
            z = settle_z(x, y, footprint(tpl, sc))
            if z is None or z < SEA_Z + 2.0: continue
            put(tpl, x, y, z, random.uniform(0, 6.28), sc, "tree" if near else "tree_far"); TREES_AT.append((x, y)); n_tree += 1; break
print("map trees placed:", n_tree, "of", sum(int(t[2]) for t in RK["trees"]))
CORE = (-185, 120, -135, 60)
wooded = lambda x, y: cover_at(x, y) == 2
offmap = lambda x, y: cover_at(x, y) in (0, 2)
n_tree += scatter(85, [T_FAR1, T_FAR1, T_FAR2], SEA_Z + 2.0, (1.6, 2.5), tries=12000, region=CORE, name="tree_far", path_r=8.0, where=wooded)
n_tree += scatter(50, [T_FAR1, T_FAR1, T_FAR2], SEA_Z + 2.0, (1.6, 2.5), tries=8000, name="tree_far", path_r=11.0, where=offmap)
n_tree += scatter(130, [T_DIST], SEA_Z + 2.0, (1.7, 2.6), tries=15000, name="tree_dist", path_r=32.0, where=offmap)

# hero trees: close to where visitors stand, but off the paths and clear of buildings
def near_path(x, y, r): return any((x - a) ** 2 + (y - b) ** 2 < r * r for a, b in paths)
def near_struct(x, y, r): return any((x - a) ** 2 + (y - b) ** 2 < r * r for a, b in pts_struct)
hero_at = [(spawn.x + 2, spawn.y + 11), (spawn.x + 2, spawn.y - 11)]                     # both sides of the entrance gate
for o in bpy.data.objects:
    if o.name in ("hotspot_weapons-display", "hotspot_prison-area", "hotspot_memorial-zone", "hotspot_command-centre"):
        hero_at.append((o.location.x, o.location.y))
n_hero = 0
for (hx, hy) in hero_at:
    for k in range(48):                                                  # spiral outwards until a free spot is found
        a = k * 2.4; r = 9 + k * 0.35; x = hx + r * math.cos(a); y = hy + r * math.sin(a)
        if near_path(x, y, 4.0) or near_struct(x, y, 8.0): continue
        sc = random.uniform(1.8, 2.1); z = settle_z(x, y, footprint(T_HERO, sc))
        if z is None or z < SEA_Z + 2: continue
        put(T_HERO, x, y, z, random.uniform(0, 6.28), sc, "tree_hero"); n_hero += 1; break
print("hero trees:", n_hero, "of", len(hero_at))
n_shrub = scatter(28, [A["shrub_02"]], SEA_Z + 1.5, (0.9, 1.8), name="shrub")
n_fern = scatter(40, [A["fern_02"]], SEA_Z + 1.5, (1.0, 2.0), name="fern")
n_rock = scatter(12, [A["rock_moss_set_01"]], SEA_Z + 0.5, (1.0, 2.2), name="rock")
n_stump = scatter(6, [A["tree_stump_01"]], SEA_Z + 2, (0.8, 1.4), name="stump")
# phone-friendly Poly Haven understory (2026-11-27): tropical ground plants on the map's wooded ground beside the paths,
# rocks and fallen wood further off, rock faces on the coastal slope
def near_any_path(r): return lambda x, y: cover_at(x, y) == 2 and near_path_pts(x, y, r)
G_ = {}
for key, n_, sc_, r_, w_ in (("calathea_orbifolia_01", 40, (1.6, 2.6), 2.2, near_any_path(9)), ("anthurium_botany_01", 32, (1.4, 2.2), 2.2, near_any_path(9)),
                             ("shrub_04", 24, (2.0, 3.0), 2.5, near_any_path(14)), ("shrub_03", 24, (2.5, 3.5), 3.0, near_any_path(18)),
                             ("pachira_aquatica_01", 16, (1.3, 2.0), 3.5, wooded), ("rock_07", 14, (2.0, 4.0), 3.0, wooded),
                             ("rock_moss_set_02", 8, (0.8, 1.4), 4.0, wooded), ("tree_stump_02", 6, (0.8, 1.2), 5.0, wooded),
                             ("dead_tree_trunk", 6, (0.8, 1.1), 6.0, wooded), ("dry_branches_medium_01", 12, (0.8, 1.3), 3.0, wooded)):
    if key in A: G_[key] = scatter(n_, A[key] if isinstance(A[key], list) else [A[key]], SEA_Z + 1.5, sc_, tries=6000, region=CORE, name=key, path_r=r_, where=w_)
rf = [A[k] for k in ("rock_face_01", "rock_face_02") if k in A]; n_rf = 0
for _ in range(4000):                                    # rock faces along the shore: just above the water, on the slope
    if n_rf >= 14 or not rf: break
    x = random.uniform(100, 230); y = random.uniform(-130, 110); gz = ground_z(x, y)
    if gz is None or not (SEA_Z + 0.6 < gz < SEA_Z + 7.0) or blocked(x, y, 4.0, 9.0): continue
    put(random.choice(rf), x, y, gz - 0.6, random.uniform(0, 6.28), random.uniform(1.0, 1.8), "rock_face"); n_rf += 1
G_["rock_face"] = n_rf
print("Poly Haven understory and rocks:", G_)
print("scattered:", dict(trees=n_tree, shrubs=n_shrub, ferns=n_fern, rocks=n_rock, stumps=n_stump))

# ---- placed props at map locations (offsets are in metres from the building centre, interiors at floor height)
LAYOUT_ROT = bpy.context.scene.get("layout_rot", 0.0)     # 0 since the strict sitemap layout; buildings carry their own "rot"
_locrot = {o.name: float(o.get("rot", 0.0)) for o in bpy.data.objects if o.name.startswith("loc_")}
def at(prefix, dx, dy, dz=0.0, rot=0.0, scale=1.0, key=None):
    if key not in A: return None
    tpl_ = A[key][0] if isinstance(A[key], list) else A[key]
    b = loc(prefix); z = b.z + dz
    br = next((v for k, v in _locrot.items() if k.startswith(prefix)), 0.0)       # offsets turn with the building
    c_, s_ = math.cos(br), math.sin(br); dx, dy = dx * c_ - dy * s_, dx * s_ + dy * c_; rot += br
    return put(tpl_, b.x + dx, b.y + dy, z + 0.15, rot, scale)

# (the guns in the pits are built in build_muzium.py; the Poly Haven cannon lost its shape when decimated)
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
# (the open iron gate leaves of the old scripted gate are gone: the entrance is now the user's model)
for pref, dx, dy, sc in (("loc_24_", 2.6, 2.2, 1.5), ("loc_24_", -2.4, -2.0, 1.3), ("loc_26_", 2.0, 2.5, 1.4), ("loc_29_", -2.0, 2.2, 1.3), ("loc_08_", 6.5, 3.2, 1.5), ("loc_20_", -5.5, 3.0, 1.3), ("loc_35_", 4.2, 2.8, 1.2)):
    at(pref, dx, dy, 0, random.uniform(0, 6.28), sc, "root_cluster_01")

# ---- room fit-out with the phone-friendly Poly Haven set (2026-11-27). Local x runs along the building, the door is in
# the end wall at local x = door * w/2 (door property written by build_muzium.py); B = -door is the back of the room.
_locdoor = {o.name: int(o.get("door", 0)) for o in bpy.data.objects if o.name.startswith("loc_")}
def back(prefix): d_ = next((v for k, v in _locdoor.items() if k.startswith(prefix)), 0); return -d_ if d_ else 1
B = back("loc_03_")    # office & R&D (9 x 6, exhibition case in the middle): officer's desk and a bookcase at the back
at("loc_03_", B * 3.3, 1.8, 0, (0 if B < 0 else math.pi) + math.pi / 2, 1.0, "metal_office_desk")
at("loc_03_", B * 2.6, 2.2, 0, 0.3, 1.0, "folding_wooden_stool")
at("loc_03_", B * 2.8, -2.4, 0, math.pi, 1.0, "wooden_bookshelf_worn")
B = back("loc_11_")    # intelligence room (6 x 5): table under the radio, a desk and a briefing board
at("loc_11_", 0.0, 1.5, 0, 0.0, 1.0, "WoodenTable_01")
at("loc_11_", 0.0, 0.6, 0, 0.0, 1.0, "folding_wooden_stool")
at("loc_11_", B * 1.7, -1.5, 0, math.pi / 2 * (-B), 1.0, "metal_office_desk")
at("loc_11_", B * 2.2, 0.6, 0, (math.pi if B > 0 else 0.0) - math.pi / 2, 1.0, "standing_chalkboard_01")
B = back("loc_08_")    # underground communication centre (12 x 6.5): equipment racks, a work table, a hanging lamp
for dx in (-3.5, 0.0, 3.5): at("loc_08_", dx, -2.6, 0, 0.0, 1.0, "worn_metal_rack")
at("loc_08_", B * 2.0, 1.2, 0, 0.0, 1.0, "wooden_table_02"); at("loc_08_", B * 2.0, 0.4, 0, 0.0, 1.0, "folding_wooden_stool")
at("loc_08_", 0.0, 0.0, 1.55, 0.0, 1.0, "hanging_industrial_lamp")
B = back("loc_35_")    # armoury (8 x 5): a rack and a stack of military crates at the back
at("loc_35_", B * 3.0, -1.7, 0, 0.0, 1.0, "worn_metal_rack")
for k, (dx, dy, dz) in enumerate(((B * 3.0, 1.3, 0.0), (B * 2.1, 1.4, 0.0), (B * 2.55, 1.35, 0.30))): at("loc_35_", dx, dy, dz, 0.1 * k, 1.0, "old_military_crate")
B = back("loc_06_")    # generator room (9 x 6): oil tins, a toolbox and a ladder
at("loc_06_", B * 3.4, 2.2, 0, 0.4, 1.0, "oil_tin"); at("loc_06_", B * 3.0, 2.4, 0, 1.1, 1.0, "oil_tin"); at("loc_06_", B * 3.6, -2.3, 0, 0.2, 1.0, "can_rusted")
at("loc_06_", B * 2.4, -2.3, 0, 0.0, 1.0, "metal_toolbox"); at("loc_06_", B * 4.0, 0.0, 0, math.pi / 2, 1.0, "wooden_ladder_02")
for pref, w_ in (("loc_12_", 24), ("loc_17_", 10)):   # cook houses: tables, buckets, tins
    B = back(pref)
    at(pref, B * (w_ / 2 - 2.5), 1.6, 0, 0.0, 1.0, "WoodenTable_01"); at(pref, B * (w_ / 2 - 4.2), 1.6, 0, 0.0, 1.0, "wooden_table_02")
    at(pref, B * (w_ / 2 - 1.2), -2.2, 0, 0.0, 1.0, "wooden_bucket_01"); at(pref, B * (w_ / 2 - 1.8), -2.3, 0, 0.6, 1.0, "can_rusted")
for pref in ("loc_19_", "loc_20_"):                    # lock-up: a bucket in the first cell
    at(pref, -3.2 + 0.9, 0.0, 0, 0.3, 1.0, "wooden_bucket_01")
for pref in ("loc_23_", "loc_25_"):                    # stores beside the water tank and the gun bay: crates
    at(pref, 5.5, 3.0, 0, 0.2, 1.0, "wooden_crate_01"); at(pref, 6.4, 3.6, 0, 0.9, 1.0, "wooden_crate_02")
for pref in ("loc_26_", "loc_29_"):                    # tools left beside the tunnel portals
    at(pref, -2.2, -3.0, 0, 0.3, 1.0, "picke_dirty_01"); at(pref, -2.6, -3.4, 0, 1.2, 1.0, "rusted_spade_01")
# cafeteria terrace: picnic tables on the side away from the door wall; bins by the toilets and the gate
for dx in (-5.0, 0.0, 5.0): at("loc_fac_cafeteria", dx, -7.5, 0, 0.0, 1.0, "wooden_picnic_table")
for k in (1, 2, 3): at(f"loc_fac_toilet_{k}", 3.4, 2.8, 0, 0.0, 1.0, "metal_trash_can")
at("loc_fac_ticketing", 12.0, -6.5, 0, 0.0, 1.0, "metal_trash_can")
# jetty: a lifebuoy on a post at the shore end, two buoys in the bay
if "lifebuoy" in A:
    mm = loc("loc_fac_maritime_museum"); jt = loc("loc_fac_jetty"); ja = math.atan2(jt.y - mm.y, jt.x - mm.x)
    lx, ly = mm.x + math.cos(ja) * 6.0 - math.sin(ja) * 1.6, mm.y + math.sin(ja) * 6.0 + math.cos(ja) * 1.6
    put(A["lifebuoy"], lx, ly, SEA_Z + 0.6, ja, 1.0, "lifebuoy")
n_buoy = 0
for _ in range(400):
    if n_buoy >= 2 or "ocean_buoy" not in A: break
    x = random.uniform(140, 200); y = random.uniform(-60, 60); gz = ground_z(x, y)
    if gz is not None and gz > SEA_Z - 1.5: continue
    put(A["ocean_buoy"], x, y, SEA_Z - 0.6, random.uniform(0, 6.28), 1.0, "ocean_buoy"); n_buoy += 1

# ---- caged wall lamps over every door (positions written by build_muzium.py)
import json
FIX = json.load(open(ROOT + "/blender/out/fixtures.json"))
if "industrial_wall_lamp" in A:
    for (x, y, z, r) in FIX["lamps"]:
        put(A["industrial_wall_lamp"], x, y, z, r + SCONCE_YAW, 1.0, "wall_lamp")

# ---- check: highest point of ground under each tree trunk must be above the trunk base
worst = 0.0
for o in PROPS.objects:
    if not o.name.startswith("tree"): continue
    tpl = next((t for t in TPL.objects if t.data == o.data), None); r = footprint(tpl, o.scale.x) if tpl else 0.5
    gz = [ground_z(o.location.x + r * math.cos(a), o.location.y + r * math.sin(a)) for a in [i * math.pi / 4 for i in range(8)]]
    worst = max(worst, o.location.z - min(z for z in gz if z is not None))
print("trees: worst trunk-base gap above ground (m, <=0 means buried):", round(worst, 2))

# ---- report
tot = 0
for o in bpy.data.objects:
    if o.type == "MESH" and o.users_collection and o.users_collection[0].name in ("TEMPLATES",): continue
    if o.type == "MESH":
        me = o.data; me.calc_loop_triangles(); tot += len(me.loop_triangles)
print("total triangles in scene (instances counted):", tot, "| instances:", len(PROPS.objects))
TPL.hide_viewport = True; TPL.hide_render = True
