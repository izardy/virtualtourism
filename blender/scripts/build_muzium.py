"""Muzium Perang Penang: blockout builder (Blender 4.x/5.x).

Run inside Blender:  exec(open("/Users/izardy/Documents/virtualtourism/blender/scripts/build_muzium.py").read())

Coordinates: X = east (m), Y = north (m), Z = up. Origin = ticketing building (about the OSM museum pin).
Inputs: reference/sitemap/site_layout.json, osm_context.json, elevation_grid.json, blender/assets/polyhaven/textures.
Everything here is a PROVISIONAL blockout: layout from the museum map (rotated ~180 deg), heights from a 90 m DEM.
Walkable meshes are named floor_* / ground_* (see .kiro/specs/blender/design.md).
"""
import bpy, bmesh, json, math, os, random
from mathutils import Vector, Matrix
import numpy as np

ROOT = "/Users/izardy/Documents/virtualtourism"
TEX = ROOT + "/blender/assets/polyhaven/textures"
SITE = json.load(open(ROOT + "/reference/sitemap/site_layout.json"))
OSM = json.load(open(ROOT + "/reference/sitemap/osm_context.json"))
DEM = json.load(open(ROOT + "/reference/sitemap/elevation_grid.json"))
RELIEF = 0.7          # vertical exaggeration factor applied to the DEM (<1 flattens the hill)
BASE_ELEV = 68.0      # DEM elevation (m) at the ticketing building
SEA_Z = -36.0         # sea level in model units
random.seed(7)

# ---------------------------------------------------------------- reset scene
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.images, bpy.data.cameras, bpy.data.lights):
    for b in list(coll):
        if b.users == 0 or True:
            try: coll.remove(b)
            except Exception: pass

# ---------------------------------------------------------------- terrain function
_es = np.array(DEM["east"], float); _ns = np.array(DEM["north"], float)
_H = np.array(DEM["elev"], float).reshape(len(_ns), len(_es))
for _ in range(3):  # smooth with [1 2 1] filter, edges padded
    P = np.pad(_H, 1, mode="edge")
    _H = (P[:-2, 1:-1] + 2 * P[1:-1, 1:-1] + P[2:, 1:-1]) / 4
    P = np.pad(_H, 1, mode="edge")
    _H = (P[1:-1, :-2] + 2 * P[1:-1, 1:-1] + P[1:-1, 2:]) / 4

def _interp(e, n):
    e = min(max(e, _es[0]), _es[-1]); n = min(max(n, _ns[0]), _ns[-1])
    i = min(int((e - _es[0]) / 45), len(_es) - 2); j = min(int((n - _ns[0]) / 45), len(_ns) - 2)
    fe = (e - _es[i]) / 45; fn = (n - _ns[j]) / 45
    return (_H[j, i] * (1 - fe) * (1 - fn) + _H[j, i + 1] * fe * (1 - fn) + _H[j + 1, i] * (1 - fe) * fn + _H[j + 1, i + 1] * fe * fn)

# coastline x (east) as function of north: smallest east among coast points per 15 m bin
_c = OSM["coastline_within_420m"]
_bins = {}
for (ce, cn) in _c:
    k = round(cn / 15)
    _bins[k] = min(_bins.get(k, 1e9), ce)
_ck = sorted(_bins)
def coast_x(n):
    k = n / 15
    if k <= _ck[0]: return _bins[_ck[0]]
    if k >= _ck[-1]: return _bins[_ck[-1]]
    for a, b in zip(_ck, _ck[1:]):
        if a <= k <= b:
            t = (k - a) / (b - a); return _bins[a] * (1 - t) + _bins[b] * t

def _noise(e, n):
    return (math.sin(e * 0.045 + 1.3) * math.cos(n * 0.052) * 1.4 + math.sin(e * 0.11 + n * 0.09) * 0.6 + math.sin(n * 0.2 + 2.0) * 0.25)

def smooth(t): t = max(0.0, min(1.0, t)); return t * t * (3 - 2 * t)

def h_base(e, n):
    z = (_interp(e, n) - BASE_ELEV) * RELIEF + _noise(e, n)
    d = coast_x(n) - e                      # >0 on land
    if d < 40:
        z = (SEA_Z - 3) + (z - (SEA_Z - 3)) * smooth(d / 40.0) if d > 0 else SEA_Z - 3
    return z

PADS = []   # (x, y, r_flat, r_blend, z)
def h(e, n):
    z = h_base(e, n)
    for (px, py, r, rb, pz) in PADS:
        d = math.hypot(e - px, n - py)
        if d < r + rb:
            w = 1.0 if d <= r else 1 - smooth((d - r) / rb)
            z = z * (1 - w) + pz * w
    return z

def site(x, y, r, rb=9.0):
    """Reserve a flat pad around (x, y) and return its height."""
    z = h_base(x, y)
    PADS.append((x, y, r, rb, z))
    return z

# ---------------------------------------------------------------- materials
def make_mat(name, folder=None, tint=None, rough=0.9, color=(0.5, 0.5, 0.5, 1), metal=0.0):
    m = bpy.data.materials.new(name)
    try: m.use_nodes = True
    except Exception: pass
    nt = m.node_tree
    for n in list(nt.nodes): nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial"); bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    try: m.use_backface_culling = True
    except Exception: pass
    bsdf.inputs["Roughness"].default_value = rough; bsdf.inputs["Metallic"].default_value = metal
    if folder:
        d = os.path.join(TEX, folder); fs = os.listdir(d)
        def tex(key, nonc):
            f = next((x for x in fs if "_" + key + "_" in x), None)
            if not f: return None
            n = nt.nodes.new("ShaderNodeTexImage"); n.image = bpy.data.images.load(os.path.join(d, f), check_existing=True)
            if nonc: n.image.colorspace_settings.name = "Non-Color"
            return n
        dn = tex("diff", False)
        if dn:
            if tint:
                mix = nt.nodes.new("ShaderNodeMix"); mix.data_type = "RGBA"; mix.blend_type = "MULTIPLY"
                mix.inputs[0].default_value = 1.0; mix.inputs[7].default_value = tint
                nt.links.new(dn.outputs["Color"], mix.inputs[6]); nt.links.new(mix.outputs[2], bsdf.inputs["Base Color"])
            else:
                nt.links.new(dn.outputs["Color"], bsdf.inputs["Base Color"])
        rn = tex("rough", True)
        if rn: nt.links.new(rn.outputs["Color"], bsdf.inputs["Roughness"])
        nn = tex("nor_gl", True)
        if nn:
            nm = nt.nodes.new("ShaderNodeNormalMap"); nt.links.new(nn.outputs["Color"], nm.inputs["Color"]); nt.links.new(nm.outputs["Normal"], bsdf.inputs["Normal"])
    else:
        bsdf.inputs["Base Color"].default_value = color
    return m

MATS = {
    "ground":   make_mat("mat_ground", "forest_ground_04", tint=(0.55, 0.78, 0.38, 1)),
    "soil":     make_mat("mat_soil", "red_laterite_soil_stones"),
    "conc":     make_mat("mat_concrete_moss", "concrete_moss"),
    "conc_g":   make_mat("mat_concrete_green", "painted_concrete", tint=(0.55, 0.75, 0.62, 1)),
    "conc_w":   make_mat("mat_concrete_cracked", "cracked_concrete_wall"),
    "floor":    make_mat("mat_floor_worn", "concrete_floor_worn_001"),
    "brick":    make_mat("mat_brick_moss", "mossy_brick"),
    "rust":     make_mat("mat_rust", "rusty_metal_02", metal=0.4),
    "roof":     make_mat("mat_corrugated_roof", "corrugated_iron", metal=0.3),
    "plaster":  make_mat("mat_plaster", "grey_plaster"),
    "rock":     make_mat("mat_rock_wall", "rock_wall_08"),
    "grate":    make_mat("mat_rust_grid", "rusty_metal_grid", metal=0.4),
    "wood":     make_mat("mat_wood", color=(0.32, 0.2, 0.1, 1), rough=0.8),
    "black":    make_mat("mat_black_granite", color=(0.02, 0.02, 0.02, 1), rough=0.25),
    "asphalt":  make_mat("mat_asphalt", color=(0.12, 0.12, 0.13, 1), rough=0.95),
    "water":    make_mat("mat_sea", color=(0.04, 0.28, 0.42, 1), rough=0.12),
    "camo":     make_mat("mat_camo_green", "painted_concrete", tint=(0.35, 0.5, 0.3, 1)),
}
FLOOR_MATS = {"floor", "asphalt"}      # these become floor_* objects (walkable)
TILE = {"ground": 5.0, "soil": 3.0, "water": 50.0, "asphalt": 20.0}

# ---------------------------------------------------------------- geometry accumulator
class Geo:
    def __init__(s): s.bm = {}
    def b(s, mat): return s.bm.setdefault(mat, bmesh.new())
    def box(s, mat, cx, cy, z0, sx, sy, sz, rot=0.0):
        M = Matrix.Translation((cx, cy, z0 + sz / 2)) @ Matrix.Rotation(rot, 4, "Z") @ Matrix.Diagonal((sx, sy, sz, 1))
        bmesh.ops.create_cube(s.b(mat), size=1.0, matrix=M)
    def gable(s, mat, cx, cy, z0, L, W, R, rot=0.0):
        bm = s.b(mat); M = Matrix.Translation((cx, cy, z0)) @ Matrix.Rotation(rot, 4, "Z")
        pts = [(-L/2, -W/2, 0), (L/2, -W/2, 0), (L/2, W/2, 0), (-L/2, W/2, 0), (-L/2, 0, R), (L/2, 0, R)]
        v = [bm.verts.new(M @ Vector(p)) for p in pts]
        for f in ([0, 1, 5, 4], [2, 3, 4, 5], [0, 4, 3], [1, 2, 5], [3, 2, 1, 0]):
            bm.faces.new([v[i] for i in f])
    def ring(s, mat, cx, cy, z0, r_in, r_out, hgt, seg=24, gap_seg=1):
        bm = s.b(mat)
        for i in range(seg):
            if i < gap_seg: continue
            a0 = 2 * math.pi * i / seg; a1 = 2 * math.pi * (i + 1) / seg
            def P(r, a, z): return bm.verts.new((cx + r * math.cos(a), cy + r * math.sin(a), z))
            io0, io1, oo0, oo1 = P(r_in, a0, z0), P(r_in, a1, z0), P(r_out, a0, z0), P(r_out, a1, z0)
            it0, it1, ot0, ot1 = P(r_in, a0, z0 + hgt), P(r_in, a1, z0 + hgt), P(r_out, a0, z0 + hgt), P(r_out, a1, z0 + hgt)
            bm.faces.new([ot0, ot1, it1, it0])          # top (faces up)
            bm.faces.new([oo0, oo1, ot1, ot0])          # outer wall (faces out)
            bm.faces.new([io1, io0, it0, it1])          # inner wall (faces the pit)
    def disc(s, mat, cx, cy, z, r, seg=24):
        bm = s.b(mat); c = bm.verts.new((cx, cy, z)); ring = [bm.verts.new((cx + r * math.cos(2 * math.pi * i / seg), cy + r * math.sin(2 * math.pi * i / seg), z)) for i in range(seg)]
        for i in range(seg): bm.faces.new([c, ring[i], ring[(i + 1) % seg]])
    def cyl(s, mat, cx, cy, z0, r, hgt, seg=16):
        bm = s.b(mat)
        bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r, radius2=r, depth=hgt, matrix=Matrix.Translation((cx, cy, z0 + hgt / 2)))
    def stairs(s, mat, x, y, ang, z_from, z_to, width, steps=None):
        """Solid stepped ramp from (x,y) in direction ang; tops go from z_from to z_to."""
        n = steps or max(2, int(abs(z_to - z_from) / 0.2)); run = 0.3; dz = (z_to - z_from) / n
        base = min(z_from, z_to) - 0.1
        for i in range(n):
            px = x + math.cos(ang) * (i + 0.5) * run; py = y + math.sin(ang) * (i + 0.5) * run
            zt = z_from + dz * (i + 1)
            s.box(mat, px, py, base, run * 1.02, width, zt - base, ang)

G = Geo()
NODES = []     # empties to create: (name, x, y, z, props)

def building(mat_wall, cx, cy, w, d, hgt, door_face_x=None, roof="roof", name=None, rot=0.0, floor_mat="floor", z0=None, door_w=1.4):
    """Hollow single-room building with a door gap in the wall facing door_face_x (+1 / -1 along local x)."""
    z = site(cx, cy, 0.5 * math.hypot(w, d) + 1.5) if z0 is None else z0
    t = 0.3; dh = 2.3
    G.box(mat_wall, cx, cy, z - 1.5, w, d, 1.5, rot)          # foundation skirt
    G.box(floor_mat, cx, cy, z, w - 0.2, d - 0.2, 0.15, rot)  # floor slab (walkable)
    c, s_ = math.cos(rot), math.sin(rot)
    def at(lx, ly): return cx + lx * c - ly * s_, cy + lx * s_ + ly * c
    # long walls (along local x)
    for sy in (-1, 1):
        x_, y_ = at(0, sy * (d / 2 - t / 2)); G.box(mat_wall, x_, y_, z, w, t, hgt, rot)
    # end walls (local +/-x); the door face has a gap
    for sx in (-1, 1):
        x_, y_ = at(sx * (w / 2 - t / 2), 0)
        if door_face_x is not None and (sx == door_face_x or door_face_x == 2):
            seg = (d - 2 * t - door_w) / 2
            for sy in (-1, 1):
                xx, yy = at(sx * (w / 2 - t / 2), sy * (door_w / 2 + seg / 2 + 0)); G.box(mat_wall, xx, yy, z, t, seg + 0.0, hgt, rot)
            G.box(mat_wall, x_, y_, z + dh, t, door_w + 0.02, hgt - dh, rot)  # lintel
        else:
            G.box(mat_wall, x_, y_, z, t, d - 2 * t, hgt, rot)
    # roof
    if roof == "flat":
        G.box("roof", cx, cy, z + hgt, w + 0.8, d + 0.8, 0.25, rot)
    else:
        G.gable("roof", cx, cy, z + hgt, w + 0.8, d + 1.2, min(1.6, d * 0.3), rot)
    return z

def pit(cx, cy, r=3.2, hgt=1.1, mat="conc", gun=True):
    z = site(cx, cy, r + 3)
    G.disc("floor", cx, cy, z + 0.05, r - 0.05)
    G.ring(mat, cx, cy, z, r, r + 0.7, hgt, seg=24, gap_seg=2)
    G.cyl("conc_w", cx, cy, z, 0.35, 0.9)       # central pivot
    if gun:
        G.box("rust", cx + 1.0, cy, z + 0.9, 2.6, 0.2, 0.2, 0.0)   # barrel stand-in
    return z

def pillbox(cx, cy, rot=0.0):
    z = site(cx, cy, 5)
    G.box("conc", cx, cy, z - 0.6, 4.2, 3.2, 2.6, rot)
    G.box("floor", cx, cy, z + 2.0, 4.6, 3.6, 0.2, rot)
    c, s_ = math.cos(rot), math.sin(rot)
    G.box("black", cx + 2.12 * c, cy + 2.12 * s_, z + 0.9, 0.06, 1.4, 0.35, rot)   # firing slit stand-in
    return z

def tunnel(cx, cy, ang, length=26.0, w=2.2, hgt=2.5, name="tunnel"):
    """Straight tunnel entering the hill from a portal at (cx, cy) in direction ang."""
    z = site(cx, cy, 8, 6)
    c, s_ = math.cos(ang), math.sin(ang)
    mx, my = cx + c * length / 2, cy + s_ * length / 2
    G.box("floor", mx, my, z, length, w, 0.15, ang)
    for sy in (-1, 1):
        G.box("conc_w", mx - s_ * sy * (w / 2 + 0.2), my + c * sy * (w / 2 + 0.2), z, length, 0.4, hgt, ang)
    G.box("conc_w", mx, my, z + hgt, length, w + 0.8, 0.4, ang)
    # earth mound over the tunnel
    G.gable("ground", mx, my, z - 0.8, length + 2, w + 12, hgt + 3.8, ang)
    # portal wall with opening
    px, py = cx - c * 0.2, cy - s_ * 0.2
    G.box("conc", px - s_ * (w / 2 + 1.6), py + c * (w / 2 + 1.6), z, 0.6, 3.2, hgt + 1.8, ang)
    G.box("conc", px + s_ * (w / 2 + 1.6), py - c * (w / 2 + 1.6), z, 0.6, 3.2, hgt + 1.8, ang)
    G.box("conc", px, py, z + hgt, 0.6, w + 0.6, 1.8, ang)
    return z, mx, my

def post_line(x0, y0, x1, y1, mat="rust", gap=3.0, hgt=1.4, wire=True):
    L = math.hypot(x1 - x0, y1 - y0); n = max(1, int(L / gap)); ang = math.atan2(y1 - y0, x1 - x0)
    for i in range(n + 1):
        t = i / n; px = x0 + (x1 - x0) * t; py = y0 + (y1 - y0) * t; zz = h_base(px, py)
        G.box(mat, px, py, zz, 0.1, 0.1, hgt)
    if wire:
        for k in (0.4, 0.9, 1.3):
            zz = h_base((x0 + x1) / 2, (y0 + y1) / 2)
            G.box("grate", (x0 + x1) / 2, (y0 + y1) / 2, zz + k, L, 0.03, 0.03, ang)

# ---------------------------------------------------------------- layout data
PTS = {p["n"]: p for p in SITE["numbered"]}
FAC = {f["name"]: f for f in SITE["facilities_and_outside"]}
def E(n): return PTS[n]["east_m"], PTS[n]["north_m"]
SPINE_X = -27.0   # approx. east_m of the main path
def face(x): return +1 if x < SPINE_X else -1      # door faces the spine; local +x means east when rot=0

def slug(s): return "".join(c.lower() if c.isalnum() else "_" for c in s).strip("_")
def node(name, x, y, z, **props): NODES.append((name, x, y, z, props))

# ---- numbered points
for n, p in sorted(PTS.items()):
    x, y = p["east_m"], p["north_m"]; nm = p["name"]
    if n in (1, 2, 37):
        z = pillbox(x, y)
    elif n in (7, 13, 14, 15, 16, 18, 21, 22):
        z = building("plaster", x, y, 14, 5.5, 3.2, door_face_x=face(x))
    elif n in (12,):
        z = building("brick", x, y, 24, 6, 3.4, door_face_x=face(x))
    elif n in (17,):
        z = building("brick", x, y, 10, 6, 3.2, door_face_x=face(x))
    elif n == 3:
        z = building("conc_g", x, y, 9, 6, 3.2, door_face_x=face(x))
    elif n == 4:
        z = building("conc_w", x, y, 6, 5, 3.0, door_face_x=face(x))
    elif n == 6:
        z = building("camo", x, y, 9, 6, 3.2, door_face_x=face(x))
    elif n == 9:
        z = building("plaster", x, y, 10, 6, 3.2, door_face_x=face(x))
    elif n == 10:
        z = building("plaster", x, y, 12, 6, 3.2, door_face_x=face(x))
    elif n == 11:
        z = building("conc_g", x, y, 6, 5, 3.0, door_face_x=face(x))
    elif n in (19, 20):
        z = building("conc_g", x, y, 10, 5, 3.0, door_face_x=face(x))
        for k in range(3):   # cell bars stand-ins
            G.box("grate", x + (1 if face(x) < 0 else -1) * 0 + (k - 1) * 2.4, y + 1.1, z, 0.1, 0.1, 2.3)
    elif n == 35:
        z = building("conc_w", x, y, 8, 5, 3.0, door_face_x=face(x))
    elif n == 8:   # underground communication centre: semi-buried bunker under an earth mound
        z = building("conc_w", x, y, 12, 6.5, 2.8, door_face_x=face(x), roof="flat")
        G.gable("ground", x, y, z + 2.4, 16, 12, 3.2)
    elif n == 23:
        z = site(x, y, 6); G.cyl("conc", x, y, z, 3.0, 0.8, seg=20); G.box("rust", x, y, z + 0.8, 0.9, 0.9, 0.12)
    elif n == 24:   # observation post tower
        z = site(x, y, 8)
        G.box("conc", x, y, z - 1, 4.2, 4.2, 6.2)
        G.box("floor", x, y, z + 5.2, 5.2, 5.2, 0.2)
        for sx, sy in ((1, 1), (1, -1), (-1, 1), (-1, -1)): G.box("rust", x + sx * 2.5, y + sy * 2.5, z + 5.4, 0.1, 0.1, 1.6)
        for s_ in (-1, 1):
            G.box("grate", x + s_ * 2.5, y, z + 5.4, 0.04, 5.0, 1.6); G.box("grate", x, y + s_ * 2.5, z + 5.4, 5.0, 0.04, 1.6)
        G.stairs("floor", x + 10.4, y, math.pi, z, z + 5.2, 1.2)
    elif n in (25, 36):
        z = pit(x, y, r=3.4, gun=True)
    elif n == 30:
        z = pit(x, y, r=2.8, gun=False)
    elif n == 28:
        z = site(x, y, 4); G.ring("rock", x, y, z, 0.8, 1.3, 0.9, seg=14, gap_seg=0)
    elif n == 31:   # booby trap zone: wire lines + stakes
        z = site(x, y, 12)
        post_line(x - 12, y - 6, x + 12, y - 6); post_line(x - 12, y + 6, x + 12, y + 6); post_line(x - 12, y - 6, x - 12, y + 6)
        for k in range(10): G.box("wood", x - 9 + 2 * k, y + random.uniform(-4, 4), h_base(x, y), 0.08, 0.08, 0.9, random.uniform(0, 3))
    elif n == 32:   # gallows frame
        z = site(x, y, 5)
        G.box("wood", x - 1.4, y, z, 0.3, 0.3, 3.6); G.box("wood", x + 1.4, y, z, 0.3, 0.3, 3.6); G.box("wood", x, y, z + 3.4, 3.4, 0.3, 0.3)
        G.box("wood", x, y, z, 2.6, 2.2, 0.4)
    elif n == 34:   # guillotine frame
        z = site(x, y, 4)
        G.box("wood", x - 0.5, y, z, 0.18, 0.18, 2.6); G.box("wood", x + 0.5, y, z, 0.18, 0.18, 2.6); G.box("wood", x, y, z + 2.5, 1.2, 0.18, 0.18); G.box("rust", x, y, z + 1.8, 0.8, 0.05, 0.4)
        G.box("conc", x, y, z, 2.0, 1.6, 0.25)
    elif n == 5:    # open air theatre: stage plus curved seating steps
        z = site(x, y, 12)
        G.box("floor", x, y, z, 8, 4, 0.5)
        for k in range(4): G.box("conc", x - 0.0, y - 3.5 - 1.1 * k, z + 0.1 * k, 9 + k, 0.9, 0.35 + 0.1 * k)
    elif n == 33:   # trench route: two low walls along a short zig-zag
        z = site(x, y, 14)
        pts = [(x - 12, y - 4), (x - 4, y + 3), (x + 4, y - 3), (x + 12, y + 4)]
        for a, b in zip(pts, pts[1:]):
            ang = math.atan2(b[1] - a[1], b[0] - a[0]); L = math.hypot(b[0] - a[0], b[1] - a[1]); mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
            for sg in (-1, 1): G.box("conc_w", mx - math.sin(ang) * sg * 1.0, my + math.cos(ang) * sg * 1.0, z, L, 0.3, 1.3, ang)
    elif n == 26 or n == 29:
        eps = 3.0
        g = (h_base(x + eps, y) - h_base(x - eps, y), h_base(x, y + eps) - h_base(x, y - eps))
        ang = math.atan2(g[1], g[0]) if (abs(g[0]) + abs(g[1])) > 1e-6 else 0.0   # uphill
        z, mx, my = tunnel(x, y, ang, 26.0)
        PTS[n]["_tunnel"] = (ang, z)
    elif n == 27:
        z = pillbox(x, y)
    else:
        z = site(x, y, 4)
    node(f"loc_{n:02d}_{slug(nm)}", x, y, z + 0.0, map_no=n, label=nm)
    p["_z"] = z

# ---- facilities and outside items
def fac(name): f = FAC[name]; return f["east_m"], f["north_m"]
x, y = fac("Information & Ticketing"); z = building("conc_g", x, y, 14, 8, 3.4, door_face_x=2, name="ticketing")
G.box("wood", x + 7.5, y, z, 3, 8, 0.2); G.box("roof", x + 8.0, y, z + 3.2, 4.0, 9, 0.2)     # canopy (towards the car park side)
node("loc_fac_ticketing", x, y, z, label="Information & Ticketing")
x, y = fac("Souvenir shop"); z = building("brick", x, y, 10, 6, 3.2, door_face_x=1); node("loc_fac_souvenir", x, y, z, label="Souvenir shop")
x, y = fac("Cafeteria"); z = building("camo", x, y, 16, 10, 3.4, door_face_x=-1); node("loc_fac_cafeteria", x, y, z, label="Cafeteria")
for k, (tx, ty) in enumerate([(-45.0, 4.0), (-60, -55), (-130, -10)]):
    z = building("conc_g", tx, ty, 5, 4, 2.8, door_face_x=1); node(f"loc_fac_toilet_{k+1}", tx, ty, z, label="Toilets")
for nm, w_, d_ in (("Car Park", 40, 24), ("VIP Car Park", 20, 12)):
    x, y = fac(nm); z = site(x, y, 0.5 * math.hypot(w_, d_) + 2, 10); G.box("asphalt", x, y, z, w_, d_, 0.12)
    node(f"loc_fac_{slug(nm)}", x, y, z, label=nm)
x, y = fac("War Game Park"); z = site(x, y, 20, 10); node("loc_fac_war_game_park", x, y, z, label="War Game Park (open area)")
for k in range(5): G.box("camo", x + random.uniform(-14, 14), y + random.uniform(-14, 14), z, random.uniform(2, 4), 0.4, 1.6, random.uniform(0, 3))
# coast side (east): barbed wire, wells, pill boxes, slipway, jetty, generator, armoury, tank
x, y = fac("Barbed wire (coast)"); z = site(x, y, 3); post_line(x, y - 10, x, y + 10); node("loc_fac_coast_barbed_wire", x, y, z, label="Barbed wire (coast)")
x, y = fac("Well (coast)"); z = site(x, y, 3); G.ring("rock", x, y, z, 0.8, 1.3, 0.9, seg=14, gap_seg=0); node("loc_fac_coast_well", x, y, z, label="Well (coast)")
x, y = fac("Pill Boxes (coast, 3)")
for k in range(3):
    zz = pillbox(x, y + (k - 1) * 18, 0.4 * k); 
node("loc_fac_coast_pillboxes", x, y, h_base(x, y), label="Pill Boxes (coast, 3)")
x, y = fac("Submarine Landing Bay"); z = site(x, y, 6); G.box("conc", x, y, z, 10, 4, 0.5); node("loc_fac_submarine_landing_bay", x, y, z, label="Submarine Landing Bay (slipway)")
x, y = fac("Maritime Museum / Jetty"); z = building("brick", x, y, 12, 7, 3.2, door_face_x=1); node("loc_fac_maritime_museum_jetty", x, y, z, label="Maritime Museum / Jetty")
G.box("wood", x + 14, y, SEA_Z + 0.4, 18, 2.2, 0.2)
x, y = fac("Generator Room (coast)"); z = building("conc_w", x, y, 6, 5, 3.0, door_face_x=1); node("loc_fac_coast_generator_room", x, y, z, label="Generator Room (coast)")
x, y = fac("Armoury (coast)"); z = building("conc_w", x, y, 7, 5, 3.0, door_face_x=1); node("loc_fac_coast_armoury", x, y, z, label="Armoury (coast)")
for nm, key in (("Water Tank (coast)", "coast_water_tank"), ("Water Tank (road)", "road_water_tank")):
    x, y = fac(nm); z = site(x, y, 4); G.cyl("conc", x, y, z, 2.6, 3.0, seg=16); node(f"loc_fac_{key}", x, y, z, label=nm)

# ---- escape route (provisional, inside tunnel 29): 7 m crawl then a 9 m ladder climb
ang29, z29 = PTS[29]["_tunnel"]
c, s_ = math.cos(ang29), math.sin(ang29)
x29, y29 = PTS[29]["east_m"], PTS[29]["north_m"]
ex, ey = x29 + c * 26.0, y29 + s_ * 26.0                      # inner end of tunnel 29
# crawl: 7 m long, 1.0 m high, continues along the tunnel direction
cx_, cy_ = ex + c * 3.5, ey + s_ * 3.5
G.box("floor", cx_, cy_, z29, 7, 1.0, 0.15, ang29)
for sg in (-1, 1): G.box("conc_w", cx_ - s_ * sg * 0.7, cy_ + c * sg * 0.7, z29, 7, 0.4, 1.1, ang29)
G.box("conc_w", cx_, cy_, z29 + 1.0, 7, 1.8, 0.4, ang29)
sx_, sy_ = ex + c * 7.5, ey + s_ * 7.5                        # base of the shaft
top = h_base(sx_, sy_); climb = max(3.0, min(9.0, top - z29 - 0.6))
for sg in (-1, 1):
    G.box("conc_w", sx_ - s_ * sg * 0.75, sy_ + c * sg * 0.75, z29, 0.4, 0.4, climb + 0.6, ang29)
    G.box("conc_w", sx_ + c * sg * 0.75, sy_ + s_ * sg * 0.75, z29, 0.4, 0.4, climb + 0.6, ang29 + math.pi / 2)
for k in range(int(climb / 0.3)): G.box("rust", sx_ - c * 0.5, sy_ - s_ * 0.5, z29 + 0.3 * k + 0.2, 0.05, 0.5, 0.05, ang29)   # rungs
node("loc_escape_route_shaft", sx_, sy_, z29 + 0.5, label="Escape route (provisional: location unconfirmed)", climb_m=round(climb, 1), crawl_m=7.0)
PTS["escape"] = {"east_m": sx_, "north_m": sy_, "_z": z29}

# ---- memorial (provisional location, unconfirmed)
mx, my = 10.0, -75.0
z = site(mx, my, 5)
G.box("conc_w", mx, my, z, 1.8, 0.7, 0.3); G.box("black", mx, my, z + 0.3, 1.6, 0.16, 1.1)
node("loc_memorial_plaque", mx, my, z, label="To Our Glorious Dead (provisional location)")
PTS["memorial"] = {"east_m": mx, "north_m": my, "_z": z}

# ---------------------------------------------------------------- paths (floor_path) from the map route
ROUTES = [[None, 3, 4, 34, 5, 24], [5, 30, 25, 29, 26, 28, 37, 27], [4, 7, 22, 19, 21, 18, 6, 32], [8, 11, 12, 15, 16, 17], [9, 10], [24, 35, 23, 33]]
TICKET = fac("Information & Ticketing")
def ribbon(points, width, mat, z_off, bmx):
    dense = []
    for a, b in zip(points, points[1:]):
        L = math.hypot(b[0] - a[0], b[1] - a[1]); k = max(1, int(L / 3))
        for i in range(k): dense.append((a[0] + (b[0] - a[0]) * i / k, a[1] + (b[1] - a[1]) * i / k))
    dense.append(points[-1]); prev = None
    for i, p in enumerate(dense):
        q = dense[min(i + 1, len(dense) - 1)]; r = dense[max(i - 1, 0)]
        dx, dy = q[0] - r[0], q[1] - r[1]; L = math.hypot(dx, dy) or 1; nx, ny = -dy / L, dx / L
        l = (p[0] + nx * width / 2, p[1] + ny * width / 2); rr = (p[0] - nx * width / 2, p[1] - ny * width / 2)
        vl = bmx.verts.new((l[0], l[1], h(l[0], l[1]) + z_off)); vr = bmx.verts.new((rr[0], rr[1], h(rr[0], rr[1]) + z_off))
        if prev: bmx.faces.new([prev[0], prev[1], vr, vl])
        prev = (vl, vr)

PATH_BM = bmesh.new(); ROAD_BM = bmesh.new()
# terrain is built after pads, but paths sample h() so build the terrain first
# ---------------------------------------------------------------- terrain mesh
def uv_box(bm, tile):
    uv = bm.loops.layers.uv.verify()
    for f in bm.faces:
        n = f.normal
        for lp in f.loops:
            co = lp.vert.co
            if abs(n.z) >= max(abs(n.x), abs(n.y)): u, v = co.x, co.y
            elif abs(n.x) >= abs(n.y): u, v = co.y, co.z
            else: u, v = co.x, co.z
            lp[uv].uv = (u / tile, v / tile)

STEP = 6.0
E0, E1, N0, N1 = -330.0, 300.0, -260.0, 260.0
ne = int((E1 - E0) / STEP) + 1; nn = int((N1 - N0) / STEP) + 1
TB = bmesh.new(); grid = []
for j in range(nn):
    row = []
    for i in range(ne):
        e = E0 + i * STEP; n = N0 + j * STEP; row.append(TB.verts.new((e, n, h(e, n))))
    grid.append(row)
for j in range(nn - 1):
    for i in range(ne - 1): TB.faces.new([grid[j][i], grid[j][i + 1], grid[j + 1][i + 1], grid[j + 1][i]])
TB.normal_update()

# paths on top of the terrain
spine = [TICKET, E(3), E(4), E(34), E(5), E(24)]
ribbon(spine, 3.0, "soil", 0.06, PATH_BM)
for r in ROUTES[1:]:
    pts = [E(k) for k in r]
    if r[0] == 5: pts[0] = E(5)
    ribbon(pts, 2.2, "soil", 0.06, PATH_BM)
# access road (OSM) from the museum entrance to the north-west, wider
road = [tuple(p) for p in OSM["roads"]["Jalan Muzium Perang"]]
ribbon(road, 6.0, "asphalt", 0.07, ROAD_BM)

# ---------------------------------------------------------------- write objects
def to_obj(bm, name, matkey, tile=3.0):
    bm.normal_update(); uv_box(bm, TILE.get(matkey, tile))
    me = bpy.data.meshes.new(name + "_mesh"); bm.to_mesh(me); bm.free()
    me.materials.append(MATS[matkey]); ob = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(ob)
    for p in me.polygons: p.use_smooth = False
    return ob

to_obj(TB, "ground_terrain", "ground")
to_obj(PATH_BM, "floor_paths", "soil")
to_obj(ROAD_BM, "floor_road", "asphalt")
for key, bm in G.bm.items():
    nm = ("floor_" if key in FLOOR_MATS else "struct_") + key
    to_obj(bm, nm, key)
# sea
sb = bmesh.new(); sz = SEA_Z
for (a, b, c_, d) in [(-500, -500, 600, 500)]:
    v = [sb.verts.new(p) for p in ((a, b, sz), (c_, b, sz), (c_, d, sz), (a, d, sz))]; sb.faces.new(v)
to_obj(sb, "sea_water", "water")

# empties: map points, spawn
for (name, x, y, z, props) in NODES:
    e = bpy.data.objects.new(name, None); e.empty_display_type = "PLAIN_AXES"; e.empty_display_size = 1.0
    e.location = (x, y, z); bpy.context.scene.collection.objects.link(e)
    for k, v in props.items(): e[k] = v
sp = bpy.data.objects.new("spawn", None); sp.empty_display_type = "ARROWS"
sp.location = (TICKET[0] + 16.0, TICKET[1], h(TICKET[0] + 16.0, TICKET[1]) + 0.1); sp.rotation_euler = (0, 0, math.radians(180)); bpy.context.scene.collection.objects.link(sp)   # faces west, through the ticket building

# hotspot empties (10 required hotspots)
HOT = {
    "main-entrance": (TICKET[0], TICKET[1]),
    "japanese-tunnel": E(26),
    "command-centre": E(11),
    "observation-tower": E(24),
    "prison-area": E(20),
    "underground-bunker": E(8),
    "memorial-zone": (mx, my),
    "weapons-display": E(25),
    "lookout-point": E(37),
    "escape-route": (sx_, sy_),
}
PROVISIONAL = {"memorial-zone", "escape-route", "lookout-point", "japanese-tunnel", "underground-bunker"}
hot_out = {}
for slug_, (x, y) in HOT.items():
    zbase = {"observation-tower": PTS[24]["_z"] + 5.2, "escape-route": z29, "underground-bunker": PTS[8]["_z"]}.get(slug_, h(x, y))
    z = zbase + 1.6 if slug_ != "observation-tower" else zbase + 1.6
    e = bpy.data.objects.new("hotspot_" + slug_, None); e.empty_display_type = "SPHERE"; e.empty_display_size = 1.2
    e.location = (x, y, z); e["provisional"] = slug_ in PROVISIONAL; bpy.context.scene.collection.objects.link(e)
    hot_out[slug_] = {"blender_xyz": [round(x, 2), round(y, 2), round(z, 2)], "gltf_xyz": [round(x, 2), round(z, 2), round(-y, 2)], "provisional": slug_ in PROVISIONAL}
os.makedirs(ROOT + "/blender/out", exist_ok=True)
json.dump(hot_out, open(ROOT + "/blender/out/hotspots.json", "w"), indent=1)
json.dump({n: {"label": props.get("label"), "gltf_xyz": [round(x, 2), round(z, 2), round(-y, 2)]} for (n, x, y, z, props) in NODES}, open(ROOT + "/blender/out/site_points.json", "w"), indent=1)

# sun + view settings
sun = bpy.data.lights.new("sun", "SUN"); sun.energy = 3.0; so = bpy.data.objects.new("sun", sun); so.rotation_euler = (math.radians(50), 0, math.radians(30)); bpy.context.scene.collection.objects.link(so)
bpy.context.scene.unit_settings.system = "METRIC"
print("objects:", len(bpy.data.objects), "pads:", len(PADS), "escape climb m:", round(climb, 1), "terrain z range:", round(min(v.co.z for v in bpy.data.objects["ground_terrain"].data.vertices), 1), round(max(v.co.z for v in bpy.data.objects["ground_terrain"].data.vertices), 1))
