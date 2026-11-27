"""Turn a Poly Haven scan tree (about 1 million triangles) into a web tree of about 8-10k triangles.

The leaves of the Poly Haven trees are separate small meshes (24 triangles each) textured with an alpha leaf map.
We keep a random fraction of them and replace each kept leaf with one quad: an affine fit from the leaf's UVs to its
3D positions gives the quad corners at the UV bounding box, so the alpha texture still draws the leaf shape.
Kept leaves are scaled up a little to make up for the missing ones. The thin twig meshes are dropped and the trunk is decimated.
Used by place_props.py:  thin_tree(object, keep=0.1, leaf_scale=1.8, wood_tris=3000)
"""
import bpy, bmesh, random
import numpy as np
from mathutils import Vector


def _islands(bm, mat_index):
    seen = set(); out = []
    for f in bm.faces:
        if f.material_index != mat_index or f.index in seen: continue
        stack = [f]; seen.add(f.index); isl = []
        while stack:
            g = stack.pop(); isl.append(g)
            for e in g.edges:
                for h in e.link_faces:
                    if h.index not in seen and h.material_index == mat_index: seen.add(h.index); stack.append(h)
        out.append(isl)
    return out


def thin_tree(ob, keep=0.2, leaf_scale=2.0, wood_tris=4000, seed=3, keep_twigs=0.0):
    rnd = random.Random(seed)
    me = ob.data
    leaf_idx = next(i for i, m in enumerate(me.materials) if "leaves" in m.name)
    bm = bmesh.new(); bm.from_mesh(me); bm.faces.ensure_lookup_table()
    uvl = bm.loops.layers.uv.active
    leaves = _islands(bm, leaf_idx)
    quads = []                                     # (4 positions, 4 uvs)
    for isl in leaves:
        if rnd.random() > keep: continue
        P = []; U = []
        for f in isl:
            for l in f.loops: P.append(tuple(l.vert.co)); U.append(tuple(l[uvl].uv))
        P = np.array(P); U = np.array(U)
        A = np.c_[U, np.ones(len(U))]                # position = [u v 1] @ M   (3x3)
        M, *_ = np.linalg.lstsq(A, P, rcond=None)
        u0, v0 = U.min(0); u1, v1 = U.max(0)
        cuv = [(u0, v0), (u1, v0), (u1, v1), (u0, v1)]
        c = P.mean(0)
        pos = [c + (np.array([u, v, 1.0]) @ M - c) * leaf_scale for u, v in cuv]
        quads.append((pos, cuv))
    # delete all leaf faces and the thin twigs (thousands of tiny meshes the leaves hide anyway); keep trunk and limbs
    twig_idx = next((i for i, m in enumerate(me.materials) if "branches" in m.name), -1)
    kill = [f for f in bm.faces if f.material_index == leaf_idx]
    if twig_idx >= 0:
        for isl in _islands(bm, twig_idx):
            if len(isl) < 200 or rnd.random() > keep_twigs: kill += isl
    bmesh.ops.delete(bm, geom=kill, context="FACES")
    for pos, cuv in quads:
        vs = [bm.verts.new(Vector(p)) for p in pos]
        f = bm.faces.new(vs); f.material_index = leaf_idx; f.smooth = True
        for l, uv in zip(f.loops, cuv): l[uvl].uv = uv
    bm.to_mesh(me); bm.free()
    # decimate wood only: put leaves in a vertex group and invert it in the modifier
    vg = ob.vertex_groups.new(name="leaves")
    vg.add([v for p in me.polygons if p.material_index == leaf_idx for v in p.vertices], 1.0, "REPLACE")
    me.calc_loop_triangles()
    n_wood = sum(1 for t in me.loop_triangles if me.polygons[t.polygon_index].material_index != leaf_idx)
    if n_wood > wood_tris:
        md = ob.modifiers.new("dec", "DECIMATE"); md.ratio = wood_tris / n_wood
        md.vertex_group = "leaves"; md.invert_vertex_group = True
        with bpy.context.temp_override(active_object=ob, object=ob, selected_objects=[ob], selected_editable_objects=[ob]):
            bpy.ops.object.modifier_apply(modifier="dec")
    ob.vertex_groups.clear()
    me.calc_loop_triangles()
    # leaf material: alpha clip, two-sided
    m = me.materials[leaf_idx]
    try: m.use_backface_culling = False
    except Exception: pass
    try: m.surface_render_method = "DITHERED"
    except Exception: pass
    return len(quads), len(me.loop_triangles)
