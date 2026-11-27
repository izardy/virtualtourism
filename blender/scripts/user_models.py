"""Bake the user's own Blender models into the Muzium Perang scene (exec'd by build_muzium.py, shares its globals).

Models (copied from ~/Desktop/blender into blender/user_models/):
- penang_pillbox_type1.blend: rectangular pill box with a cupola, steel door, loophole shutters and a furnished interior
  (Vickers and Bren guns, Boys rifle, rifle rack, telephone, lamp). Used for map pill boxes 1, 2, 27 and 37.
- penang_pillbox_type2.blend: octagonal pill box sunk into the ground, with entrance stairs and the same interior kit.
  Used for the four coast pill boxes. Its own terrain and cutter objects are left out (build_muzium carves our terrain).
- penang_war_museum_entrance1.blend: the WAR MUSEUM entrance (brick piers and walls, log letters, pennants, boards,
  displays, covered passage, driveway). Replaces the scripted gate.

For every placement in USER_PLACES the visible meshes are evaluated (boolean modifiers applied), moved into place and
merged by role and material:
- floor_user_*: upward faces of the structure near floor level (walkable: plinths, floors, stairs, driveway, kerbs)
- struct_user_*: the rest of the structure (colliders: walls, piers, roof slabs)
- deco_user_*: furniture, weapons, signs, plants (drawn only)
Large concrete, brick, timber and roof surfaces get the scene's Poly Haven materials (box-mapped UVs) so they match
the rest of the fort; the other materials keep the user's colours (procedural colour ramps flattened for glTF).
The source files are only read, never modified.
"""
import bpy, bmesh, math, os
from mathutils import Matrix

UM = ROOT + "/blender/user_models/"
SPECS = {
    "pillbox_type1": dict(file="penang_pillbox_type1.blend", floor_below=0.5,
                          skip={"Ground"}, struct={"PillboxBody", "Plinth", "Cupola", "SteelDoor", "DoorFrame"}),
    "pillbox_type2": dict(file="penang_pillbox_type2.blend", floor_below=0.2,
                          skip={"Terrain"}, struct={"Type2_Walls", "Type2_RoofSlab", "EntranceStairs", "MGTable"}),
    "entrance": dict(file="penang_war_museum_entrance1.blend", floor_below=0.45, skip=set(),
                     struct_collections={"BrickWalls", "Ground"},
                     struct={"Roof_PassagePosts", "LampPost-1", "LampPost1", "InfoPost13.05", "InfoPost13.95",
                             "InfoPost-9.35", "InfoPost-8.45"} | {f"GreenPost{k}" for k in range(8)}),
}
# user material (name without .001 suffix) -> scene material key
MATMAP = {"WeatheredConcrete": "conc_w", "WarmGreyConcrete": "conc_w", "InteriorConcrete": "conc", "Brick": "redbrick",
          "Paving": "floor", "ZincRoof": "roof", "WeatheredTimber": "wood", "Wood": "wood", "LampGlass": "lamp"}


def _base(name):
    return name.split(".")[0]


def _flatten_for_gltf(m):
    """glTF keeps only image textures: replace a procedural base colour (noise -> colour ramp) by its average colour."""
    if not m or not m.use_nodes:
        return
    bsdf = next((n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
    if not bsdf:
        return
    for sock_name in ("Base Color", "Roughness", "Normal"):
        sock = bsdf.inputs.get(sock_name)
        if not sock or not sock.is_linked:
            continue
        src = sock.links[0].from_node
        if src.type == "TEX_IMAGE":
            continue
        if sock_name == "Base Color":
            ramp = src if src.type == "VALTORGB" else next((n for n in m.node_tree.nodes if n.type == "VALTORGB"), None)
            if ramp:
                els = ramp.color_ramp.elements
                sock.default_value = [sum(e.color[i] for e in els) / len(els) for i in range(3)] + [1.0]
        for l in list(sock.links):
            m.node_tree.links.remove(l)


def _load(spec):
    with bpy.data.libraries.load(UM + spec["file"], link=False) as (src, dst):
        dst.objects = list(src.objects); dst.collections = list(src.collections)
    tmp = bpy.data.collections.new("_user_tmp"); bpy.context.scene.collection.children.link(tmp)
    spec["_cols"] = {}
    for c in dst.collections:
        for o in c.objects: spec["_cols"].setdefault(o.name, set()).add(_base(c.name))
    for o in dst.objects:
        tmp.objects.link(o)
    bpy.context.view_layer.update()
    return tmp, list(dst.objects), list(dst.collections)


def _role(o, spec):
    if o.name in spec["struct"]:
        return "struct"
    if spec["_cols"].get(o.name, set()) & spec.get("struct_collections", set()):
        return "struct"
    return "deco"


BUCKETS = {}     # (role, matkey or material) -> bmesh


def _bucket(role, mat):
    k = (role, mat)
    if k not in BUCKETS:
        BUCKETS[k] = bmesh.new()
    return BUCKETS[k]


def _add_faces(src_bm, faces, dst_bm):
    """Copy the given faces of src_bm (with UVs) into dst_bm."""
    uv_s = src_bm.loops.layers.uv.active
    uv_d = dst_bm.loops.layers.uv.verify()
    vmap = {}
    for f in faces:
        vs = []
        for v in f.verts:
            nv = vmap.get(v)
            if nv is None:
                nv = dst_bm.verts.new(v.co); vmap[v] = nv
            vs.append(nv)
        try:
            nf = dst_bm.faces.new(vs)
        except ValueError:
            continue
        nf.smooth = f.smooth
        if uv_s:
            for ls, ld in zip(f.loops, nf.loops):
                ld[uv_d].uv = ls[uv_s].uv


n_parts = 0
for model, spec in SPECS.items():
    places = [p for p in USER_PLACES if p[0] == model]
    if not places:
        continue
    if not os.path.isfile(UM + spec["file"]):
        print("user model missing:", spec["file"]); continue
    tmp, objs, cols = _load(spec)
    dg = bpy.context.evaluated_depsgraph_get()
    for m in {s.material for o in objs for s in getattr(o, "material_slots", []) if s.material}:
        if _base(m.name) not in MATMAP:
            _flatten_for_gltf(m)
    for (_, px, py, pz, prot) in places:
        Mp = Matrix.Translation((px, py, pz)) @ Matrix.Rotation(prot, 4, "Z")
        for o in objs:
            if o.type not in ("MESH", "FONT", "CURVE") or o.name in spec["skip"]:
                continue
            if o.hide_render or o.display_type in ("WIRE", "BOUNDS"):     # boolean cutters and helpers
                continue
            ev = o.evaluated_get(dg)
            me = bpy.data.meshes.new_from_object(ev)
            me.transform(Mp @ o.matrix_world)
            bm = bmesh.new(); bm.from_mesh(me); bm.normal_update()
            role = _role(o, spec)
            groups = {}
            for f in bm.faces:
                mat = me.materials[f.material_index] if f.material_index < len(me.materials) else None
                key = MATMAP.get(_base(mat.name), mat) if mat else "conc"
                r = role
                if role == "struct" and f.normal.z > 0.7 and f.calc_center_median().z - pz < spec["floor_below"]:
                    r = "floor"
                groups.setdefault((r, key), []).append(f)
            for (r, key), fs in groups.items():
                _add_faces(bm, fs, _bucket(r, key))
            bm.free(); bpy.data.meshes.remove(me); n_parts += 1
    for o in objs:
        bpy.data.objects.remove(o, do_unlink=True)
    for c in cols:
        bpy.data.collections.remove(c)
    bpy.data.collections.remove(tmp)
for c in list(bpy.data.collections):          # collections that came with the appended files and are now empty
    if not c.objects and not c.children and c.users <= 1 and c.name not in {x.name for x in bpy.context.scene.collection.children}:
        bpy.data.collections.remove(c)

# write the merged objects
n_obj = 0
for (role, key), bm in BUCKETS.items():
    if not bm.faces:
        bm.free(); continue
    mname = key if isinstance(key, str) else _base(key.name)
    name = {"floor": "floor_user_", "struct": "struct_user_", "deco": "deco_user_"}[role] + mname.lower()
    if isinstance(key, str):                                  # scene material: box-mapped UVs, weathering colours
        ob = to_obj(bm, name, key, kind="struct" if (key in WALL_KEYS and role != "floor") else None)
    else:
        bm.normal_update()
        me = bpy.data.meshes.new(name + "_mesh"); bm.to_mesh(me); bm.free()
        me.materials.append(key); ob = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(ob)
    n_obj += 1
print("user models:", {m: sum(1 for p in USER_PLACES if p[0] == m) for m in SPECS}, "parts", n_parts, "objects", n_obj)
