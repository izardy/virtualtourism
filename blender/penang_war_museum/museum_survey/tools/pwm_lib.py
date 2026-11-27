"""Shared helpers for building Penang War Museum structures in Blender (background mode).

Frame: model x = -E (west +), y = -N (south +), z up, origin O = gate front (5.281400 N, 100.288800 E).
Each structure gets a root EMPTY at its surveyed model x/y (rotation from the survey CSV), and all parts
are children of that root, so files line up when linked into the site map.
"""
import bpy, bmesh, math, csv, os
from mathutils import Vector, Matrix, Euler

SURVEY = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV = os.path.join(SURVEY, "penang_war_museum_sitemap_points.csv")


def reset_scene():
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    for c in list(bpy.data.collections):
        bpy.data.collections.remove(c)
    for blocks in (bpy.data.meshes, bpy.data.materials, bpy.data.cameras, bpy.data.lights, bpy.data.curves):
        for b in list(blocks):
            if b.users == 0:
                blocks.remove(b)


def points():
    """id -> row dict from the survey CSV (B/S/R/F rows)."""
    out = {}
    for r in csv.DictReader(open(CSV, encoding="utf-8")):
        key = r["id"] if r["id"] != "F" else "F:" + r["name"]
        k, i = key, 2
        while k in out:
            k = f"{key} #{i}"; i += 1
        out[k] = r
    return out


# ---------------------------------------------------------------- materials
def _bsdf(m):
    return next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")


def M(name, color, rough=0.8, metal=0.0, alpha=1.0):
    m = bpy.data.materials.get(name)
    if m: return m
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = _bsdf(m)
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if alpha < 1:
        b.inputs["Alpha"].default_value = alpha
        try: m.surface_render_method = 'BLENDED'
        except Exception: pass
    m.diffuse_color = (*color, alpha)
    return m


def NM(name, c0, c1, scale=4.0, bump=0.25, rough=0.85, stretch=(1, 1, 1), extra=None, metal=0.0):
    """Procedural noise material (object-space), works without UVs."""
    m = bpy.data.materials.get(name)
    if m: return m
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; N = nt.nodes; L = nt.links.new
    b = _bsdf(m); b.inputs["Roughness"].default_value = rough; b.inputs["Metallic"].default_value = metal
    tc = N.new("ShaderNodeTexCoord"); mp = N.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = stretch
    L(tc.outputs["Object"], mp.inputs["Vector"])
    nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = scale; nz.inputs["Detail"].default_value = 8
    L(mp.outputs[0], nz.inputs["Vector"])
    cr = N.new("ShaderNodeValToRGB")
    cr.color_ramp.elements[0].color = (*c0, 1); cr.color_ramp.elements[1].color = (*c1, 1)
    for pos, col in (extra or []):
        e = cr.color_ramp.elements.new(pos); e.color = (*col, 1)
    L(nz.outputs["Fac"], cr.inputs[0]); L(cr.outputs[0], b.inputs["Base Color"])
    if bump:
        bp = N.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = bump
        L(nz.outputs["Fac"], bp.inputs["Height"]); L(bp.outputs[0], b.inputs["Normal"])
    m.diffuse_color = (*[(a + c) / 2 for a, c in zip(c0, c1)], 1)
    return m


def camo(name="Camouflage"):
    m = bpy.data.materials.get(name)
    if m: return m
    m = NM(name, (0.16, 0.25, 0.09), (0.05, 0.05, 0.035), 2.6, 0.0, 0.7,
           extra=[(0.42, (0.55, 0.44, 0.12)), (0.56, (0.36, 0.2, 0.07))])
    cr = next(n for n in m.node_tree.nodes if n.type == "VALTORGB")
    cr.color_ramp.interpolation = 'CONSTANT'
    for e in cr.color_ramp.elements:
        if e.position > 0.9: e.position = 0.68
    return m


def palette():
    """Material palette from survey section 5."""
    return dict(
        concrete=NM("WeatheredConcrete", (0.36, 0.35, 0.32), (0.58, 0.57, 0.53), 3.5, 0.3, 0.9,
                    extra=[(0.82, (0.24, 0.28, 0.16))]),
        concrete_dark=NM("DarkConcrete", (0.22, 0.22, 0.2), (0.4, 0.4, 0.37), 5, 0.3, 0.9),
        brick=NM("FaceBrick", (0.30, 0.12, 0.07), (0.46, 0.2, 0.11), 18, 0.4, 0.9, stretch=(1, 1, 3.5)),
        rubble=NM("GraniteRubble", (0.32, 0.31, 0.29), (0.55, 0.53, 0.5), 6, 0.9, 0.95),
        timber=NM("DarkTimber", (0.08, 0.05, 0.03), (0.2, 0.12, 0.07), 6, 0.3, 0.75, stretch=(1, 1, 5)),
        timber_light=NM("WeatheredTimber", (0.22, 0.15, 0.09), (0.42, 0.31, 0.2), 6, 0.3, 0.8, stretch=(1, 1, 5)),
        teal=NM("TealRender", (0.17, 0.33, 0.36), (0.26, 0.42, 0.46), 4, 0.15, 0.85),
        bluegrey=NM("BlueGreyRender", (0.27, 0.36, 0.40), (0.36, 0.47, 0.52), 4, 0.15, 0.85),
        blue=NM("BarrackBlue", (0.12, 0.36, 0.48), (0.2, 0.46, 0.58), 4, 0.15, 0.85),
        white=M("PaintWhite", (0.82, 0.82, 0.8), 0.6),
        green_paint=M("SageGreenPaint", (0.21, 0.32, 0.24), 0.6),
        zinc=NM("CorrugatedZinc", (0.38, 0.39, 0.4), (0.55, 0.56, 0.57), 2, 0.05, 0.45, metal=0.6),
        roof_brown=NM("RustyRoofBrown", (0.28, 0.13, 0.07), (0.42, 0.22, 0.12), 3, 0.1, 0.7, metal=0.3),
        translucent=M("TranslucentRoof", (0.85, 0.88, 0.85), 0.3, 0.0, 0.55),
        steel=M("BlackSteel", (0.03, 0.03, 0.03), 0.4, 0.8),
        grille=M("SteelGrille", (0.05, 0.06, 0.05), 0.5, 0.7),
        dark=M("DarkInterior", (0.01, 0.01, 0.01), 0.95),
        asphalt=NM("Asphalt", (0.08, 0.08, 0.08), (0.18, 0.18, 0.17), 25, 0.2, 0.95),
        paving=NM("GreyPaving", (0.33, 0.32, 0.3), (0.5, 0.49, 0.46), 6, 0.15, 0.9),
        red_kerb=M("RedPaintedConcrete", (0.45, 0.1, 0.07), 0.8),
        earth=NM("EarthLeaves", (0.12, 0.08, 0.05), (0.27, 0.19, 0.11), 5, 0.4, 1.0),
        grass=NM("Grass", (0.05, 0.13, 0.03), (0.14, 0.24, 0.06), 5, 0.3, 1.0),
        leaves=NM("Foliage", (0.03, 0.11, 0.02), (0.12, 0.27, 0.05), 3, 0.4, 0.85),
        vine=NM("VineCanopy", (0.04, 0.15, 0.03), (0.2, 0.34, 0.08), 6, 0.6, 0.8),
        attap=NM("AttapThatch", (0.25, 0.18, 0.08), (0.45, 0.35, 0.18), 12, 0.6, 1.0, stretch=(1, 1, 6)),
        sign_yellow=M("SignYellow", (0.85, 0.65, 0.05), 0.5),
        sign_red=M("SignRed", (0.6, 0.05, 0.05), 0.5),
        sign_paper=M("NoticePaper", (0.85, 0.82, 0.7), 0.8),
        photo_banner=NM("PhotoBannerBW", (0.12, 0.12, 0.12), (0.7, 0.7, 0.68), 30, 0.0, 0.7),
        brass=M("BrassLantern", (0.6, 0.42, 0.12), 0.35, 1.0),
        lamp_glow=None,
        rope=M("Rope", (0.45, 0.36, 0.22), 0.9),
        sandbag=NM("Sandbag", (0.35, 0.29, 0.18), (0.48, 0.4, 0.27), 15, 0.4, 0.95),
        shell_black=M("ShellBlack", (0.03, 0.03, 0.03), 0.4, 0.5),
        shell_red=M("ShellNoseRed", (0.55, 0.06, 0.04), 0.5),
        bamboo=NM("BambooScreen", (0.45, 0.35, 0.15), (0.62, 0.5, 0.25), 20, 0.3, 0.7, stretch=(6, 6, 1)),
        camo=camo(),
        placeholder=M("PlaceholderMassing", (0.75, 0.72, 0.66), 0.85),
        placeholder_roof=M("PlaceholderRoof", (0.45, 0.25, 0.15), 0.7),
    )


# ---------------------------------------------------------------- object helpers
def collection(name, parent=None):
    c = bpy.data.collections.get(name) or bpy.data.collections.new(name)
    p = parent or bpy.context.scene.collection
    if c.name not in [x.name for x in p.children]:
        p.children.link(c)
    return c


try:
    from terrain import z_model as _z_model
except Exception:      # terrain data missing -> flat site
    _z_model = None


def ground_z(x, y):
    return _z_model(x, y) if _z_model else 0.0


def root(col, name, x, y, rot_deg=0.0, z=None):
    """Root empty; z defaults to the terrain height at (x, y)."""
    if z is None:
        z = ground_z(x, y)
    e = bpy.data.objects.new(name, None)
    col.objects.link(e)
    e.location = (x, y, z); e.rotation_euler = (0, 0, math.radians(rot_deg))
    e.empty_display_type = 'ARROWS'; e.empty_display_size = 1.5
    return e


class Part:
    """Accumulate primitives into ONE mesh object (local coords of `parent`)."""
    def __init__(self, col, name, mat, parent=None, smooth=False):
        self.col, self.name, self.mat, self.parent, self.smooth = col, name, mat, parent, smooth
        self.bm = bmesh.new()

    def _place(self, verts, loc, rot):
        if rot != (0, 0, 0):
            bmesh.ops.rotate(self.bm, verts=verts, cent=(0, 0, 0), matrix=Euler(rot).to_matrix())
        bmesh.ops.translate(self.bm, vec=loc, verts=verts)

    def box(self, size, loc=(0, 0, 0), rot=(0, 0, 0)):
        r = bmesh.ops.create_cube(self.bm, size=1)
        bmesh.ops.scale(self.bm, vec=size, verts=r["verts"]); self._place(r["verts"], loc, rot); return self

    def boxz(self, size, loc=(0, 0, 0), rot=(0, 0, 0)):
        """box with its base on loc.z"""
        return self.box(size, (loc[0], loc[1], loc[2] + size[2] / 2), rot)

    def cyl(self, r, h, loc=(0, 0, 0), rot=(0, 0, 0), seg=16, r2=None):
        res = bmesh.ops.create_cone(self.bm, cap_ends=True, segments=seg, radius1=r, radius2=r if r2 is None else r2, depth=h)
        self._place(res["verts"], loc, rot); return self

    def beam(self, a, b, w, h=None):
        a, b = Vector(a), Vector(b); d = b - a
        r = bmesh.ops.create_cube(self.bm, size=1)
        bmesh.ops.scale(self.bm, vec=(w, h or w, d.length), verts=r["verts"])
        bmesh.ops.rotate(self.bm, verts=r["verts"], cent=(0, 0, 0), matrix=d.to_track_quat('Z', 'Y').to_matrix())
        bmesh.ops.translate(self.bm, vec=(a + b) / 2, verts=r["verts"]); return self

    def rod(self, a, b, r, seg=8):
        a, b = Vector(a), Vector(b); d = b - a
        res = bmesh.ops.create_cone(self.bm, cap_ends=True, segments=seg, radius1=r, radius2=r, depth=d.length)
        bmesh.ops.rotate(self.bm, verts=res["verts"], cent=(0, 0, 0), matrix=d.to_track_quat('Z', 'Y').to_matrix())
        bmesh.ops.translate(self.bm, vec=(a + b) / 2, verts=res["verts"]); return self

    def prism(self, pts_xz, depth, loc=(0, 0, 0), rot=(0, 0, 0)):
        """Extrude a closed profile in the XZ plane along +Y by depth (centred)."""
        vs = [self.bm.verts.new((x, -depth / 2, z)) for x, z in pts_xz]
        f = self.bm.faces.new(vs)
        ext = bmesh.ops.extrude_face_region(self.bm, geom=[f])
        new = [g for g in ext["geom"] if isinstance(g, bmesh.types.BMVert)]
        bmesh.ops.translate(self.bm, vec=(0, depth, 0), verts=new)
        allv = vs + new
        self._place(allv, loc, rot); return self

    def quad(self, pts):
        vs = [self.bm.verts.new(p) for p in pts]; self.bm.faces.new(vs); return self

    def sphere(self, r, loc=(0, 0, 0), scale=(1, 1, 1), sub=2):
        res = bmesh.ops.create_icosphere(self.bm, subdivisions=sub, radius=r)
        bmesh.ops.scale(self.bm, vec=scale, verts=res["verts"]); self._place(res["verts"], loc, (0, 0, 0)); return self

    def ring(self, r_in, r_out, z0, z1, a0=0.0, a1=360.0, seg=48, loc=(0, 0, 0)):
        """Annular wall segment between angles a0..a1 (deg)."""
        n = max(2, int(seg * (a1 - a0) / 360))
        ring = []
        for i in range(n + 1):
            a = math.radians(a0 + (a1 - a0) * i / n)
            ring.append((math.cos(a), math.sin(a)))
        full = abs(a1 - a0) >= 359.9
        V = [[self.bm.verts.new((loc[0] + c * r, loc[1] + s * r, loc[2] + z)) for (c, s) in ring] for r, z in
             ((r_in, z0), (r_out, z0), (r_out, z1), (r_in, z1))]
        for i in range(n):
            for k in range(4):
                a, b = V[k], V[(k + 1) % 4]
                self.bm.faces.new((a[i], a[i + 1], b[i + 1], b[i]))
        if not full:
            for idx in (0, n):
                self.bm.faces.new([V[k][idx] for k in (range(4) if idx == n else reversed(range(4)))])
        return self

    def done(self):
        bmesh.ops.remove_doubles(self.bm, verts=self.bm.verts, dist=0.0005)
        bmesh.ops.recalc_face_normals(self.bm, faces=self.bm.faces)
        me = bpy.data.meshes.new(self.name); self.bm.to_mesh(me); self.bm.free()
        me.materials.append(self.mat)
        if self.smooth:
            for p in me.polygons: p.use_smooth = True
        o = bpy.data.objects.new(self.name, me); self.col.objects.link(o)
        if self.parent:
            o.parent = self.parent
        return o


def text(col, name, body, size, loc, rot, mat, parent=None, extrude=0.01, align='CENTER'):
    cu = bpy.data.curves.new(name, "FONT"); cu.body = body; cu.size = size; cu.extrude = extrude
    cu.align_x = align; cu.align_y = 'CENTER'
    o = bpy.data.objects.new(name, cu); col.objects.link(o); cu.materials.append(mat)
    o.location = loc; o.rotation_euler = rot
    if parent: o.parent = parent
    return o


def append_mesh(blend_path, mesh_name):
    with bpy.data.libraries.load(blend_path, link=False) as (s, d):
        d.meshes = [mesh_name]
    me = d.meshes[0]; me.use_fake_user = False
    return me


def instance(col, name, mesh, loc, rot_z=0.0, scale=1.0, parent=None):
    o = bpy.data.objects.new(name, mesh); col.objects.link(o)
    if parent: o.parent = parent
    o.location = loc; o.rotation_euler = (0, 0, rot_z)
    o.scale = (scale, scale, scale) if not isinstance(scale, tuple) else scale
    return o


def gable_roof(part, length, width, eave_z, ridge_z, overhang=0.4, thick=0.06):
    """Two sloped roof slabs, ridge along local X."""
    L, Wd = length + 2 * overhang, width / 2 + overhang
    for s in (-1, 1):
        part.quad([(-L / 2, s * Wd, eave_z), (L / 2, s * Wd, eave_z), (L / 2, 0, ridge_z), (-L / 2, 0, ridge_z)])
        part.quad([(-L / 2, s * Wd, eave_z - thick), (-L / 2, 0, ridge_z - thick), (L / 2, 0, ridge_z - thick), (L / 2, s * Wd, eave_z - thick)])
    return part


def gable_ends(part, width, eave_z, ridge_z, x_positions, depth=0.15):
    for x in x_positions:
        part.prism([(-width / 2, eave_z), (width / 2, eave_z), (0, ridge_z)], depth, loc=(x, 0, 0), rot=(0, 0, math.radians(90)))
    return part


def finish(top_col, path, label):
    """Mark the top collection as an asset and save."""
    try:
        top_col.asset_mark(); top_col.asset_data.description = label
    except Exception as e:
        print("asset mark:", e)
    if os.path.exists(path):
        raise SystemExit(f"REFUSING to overwrite existing {path}")
    bpy.ops.file.pack_all()
    bpy.ops.wm.save_as_mainfile(filepath=path)
    print("SAVED", path, len(bpy.data.objects), "objects")


def drape(objects):
    """Add terrain height to every vertex (objects whose root sits at the origin, e.g. the walkway)."""
    for o in objects:
        if o.type != 'MESH': continue
        mw = o.matrix_world
        for v in o.data.vertices:
            w = mw @ v.co
            v.co.z += ground_z(w.x, w.y)
