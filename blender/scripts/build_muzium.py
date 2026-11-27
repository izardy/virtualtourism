"""Muzium Perang Penang: blockout builder (Blender 4.x/5.x).

Run inside Blender:  exec(open("/Users/izardy/Documents/virtualtourism/blender/scripts/build_muzium.py").read())

Coordinates: X = east_m, Y = north_m of the visitor-map frame (image-up = -Y), Z = up. Origin = ticketing building.
Inputs: reference/sitemap/reeaki_layout.json (from extract_reeaki.py: positions, building angles, heights, coast,
paths, roads, trees of the reeaki "Fort Relics" visitor map), site_layout.json (names), blender/assets/polyhaven.
Strict sitemap layout since 2026-11-27: the map is followed as drawn. The map is schematic, so real-world distances and
compass directions are approximate (scale fitted to the museum's own map, about 0.55 x 0.59 m per map pixel).
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
    # strict sitemap layout (2026-11-27): heights come from the reeaki visitor map (extract_reeaki.py): hill outline,
    # summit at the observation post, coastline, beach shelves for the coast items. The DEM is no longer used.
    return _rk_h(e, n) + 0.35 * _noise(e, n)

def _old_dem_h_base(e, n):   # kept for reference: the 90 m DEM + OSM coastline version used up to 2026-11-26
    z = (_interp(e, n) - BASE_ELEV) * RELIEF + _noise(e, n)
    d = coast_x(n) - e                      # >0 on land
    if d < 40:
        z = (SEA_Z - 3) + (z - (SEA_Z - 3)) * smooth(d / 40.0) if d > 0 else SEA_Z - 3
    return z

RK = json.load(open(ROOT + "/reference/sitemap/reeaki_layout.json"))
_RH = RK["height"]; _RZ = np.array(_RH["z"], float).reshape(_RH["nn"], _RH["ne"])
_RCOV = np.array(_RH["cover"], np.uint8).reshape(_RH["nn"], _RH["ne"])
def _rk_h(e, n):
    fx = (e - _RH["e0"]) / _RH["step"]; fy = (n - _RH["n0"]) / _RH["step"]
    fx = min(max(fx, 0.0), _RH["ne"] - 1.001); fy = min(max(fy, 0.0), _RH["nn"] - 1.001)
    i, j = int(fx), int(fy); u, v = fx - i, fy - j
    return float(_RZ[j, i] * (1 - u) * (1 - v) + _RZ[j, i + 1] * u * (1 - v) + _RZ[j + 1, i] * (1 - u) * v + _RZ[j + 1, i + 1] * u * v)

PADS = []   # (x, y, r_flat, r_blend, z)
FOOTPRINTS = []   # (cx, cy, w, d, rot) of every building; map paths that run through one are dropped (white roofs on the map)
def _in_fp(x, y, pad=0.6):
    for (cx, cy, w, d, r) in FOOTPRINTS:
        c_, s_ = math.cos(r), math.sin(r); u = (x - cx) * c_ + (y - cy) * s_; v = -(x - cx) * s_ + (y - cy) * c_
        if abs(u) < w / 2 + pad and abs(v) < d / 2 + pad: return True
    return False
CARVES = []    # (x, y, ang, kind, a, b, c, z): terrain lowered to z inside an octagon (kind "oct", radius a) or a box
               # (kind "box", local u from a to b, |v| < c); used by the sunken type-2 pill boxes (user models)
USER_PLACES = []   # (model, x, y, z_origin, rot): the user's Blender models, baked in by user_models.py
TUNNELS = []   # (x, y, ang, length, z_floor): the terrain is carved below the floor along each tunnel (the earth mound hides the cut)
def h(e, n):
    z = h_base(e, n)
    for (px, py, r, rb, pz) in PADS:
        d = math.hypot(e - px, n - py)
        if d < r + rb:
            w = 1.0 if d <= r else 1 - smooth((d - r) / rb)
            z = z * (1 - w) + pz * w
    for (tx, ty, ta, tl, tz) in TUNNELS:          # without this the hillside can cut through a tunnel running along a slope
        u = (e - tx) * math.cos(ta) + (n - ty) * math.sin(ta); v = abs(-(e - tx) * math.sin(ta) + (n - ty) * math.cos(ta))
        if -1.0 < u < tl and v < 4.0: z = min(z, tz - 0.15)
    for (cx_, cy_, ca, kind, a, b, c, zc) in CARVES:
        du, dv = e - cx_, n - cy_
        if du * du + dv * dv > 36.0: continue
        u = du * math.cos(ca) + dv * math.sin(ca); v = -du * math.sin(ca) + dv * math.cos(ca)
        if kind == "oct": inside = max(abs(u), abs(v), (abs(u) + abs(v)) / 1.41421) < a
        else: inside = a < u < b and abs(v) < c
        if inside: z = min(z, zc)
    return z

def site(x, y, r, rb=9.0):
    """Reserve a flat pad around (x, y) and return its height."""
    z = h_base(x, y)
    PADS.append((x, y, r, rb, z))
    return z

# ---------------------------------------------------------------- materials (shared with twin_build.py)
exec(open(ROOT + "/blender/scripts/scene_lib.py").read(), globals())

# ---------------------------------------------------------------- geometry accumulator
class Geo:
    def __init__(s): s.bm = {}
    def b(s, mat): return s.bm.setdefault(mat, bmesh.new())
    def box(s, mat, cx, cy, z0, sx, sy, sz, rot=0.0):
        M = Matrix.Translation((cx, cy, z0 + sz / 2)) @ Matrix.Rotation(rot, 4, "Z") @ Matrix.Diagonal((sx, sy, sz, 1))
        bmesh.ops.create_cube(s.b(mat), size=1.0, matrix=M)
    def mbox(s, mat, M, sx, sy, sz):
        """Box of size (sx, sy, sz) centred on the origin of matrix M."""
        bmesh.ops.create_cube(s.b(mat), size=1.0, matrix=M @ Matrix.Diagonal((sx, sy, sz, 1)))
    def gable(s, mat, cx, cy, z0, L, W, R, rot=0.0):
        bm = s.b(mat); M = Matrix.Translation((cx, cy, z0)) @ Matrix.Rotation(rot, 4, "Z")
        pts = [(-L/2, -W/2, 0), (L/2, -W/2, 0), (L/2, W/2, 0), (-L/2, W/2, 0), (-L/2, 0, R), (L/2, 0, R)]
        v = [bm.verts.new(M @ Vector(p)) for p in pts]
        for f in ([0, 1, 5, 4], [2, 3, 4, 5], [0, 4, 3], [1, 2, 5], [3, 2, 1, 0]):
            bm.faces.new([v[i] for i in f])
    def mound(s, mat, cx, cy, z0, u0, u1, W, R, rot, a, t, tail=6.0):
        """Earth bank over a tunnel, local x from u0 (portal) to u1 (ridge end), then a sloped tail.
        The portal face has an a-wide (half width) by t-high opening so the tunnel stays visible."""
        bm = s.b(mat); M = Matrix.Translation((cx, cy, z0)) @ Matrix.Rotation(rot, 4, "Z")
        k = W / 2 * (1 - t / R)
        P = {"B0": (u0, -W/2, 0), "B1": (u0, W/2, 0), "FA": (u0, 0, R),
             "C0": (u1 + tail, -W/2, 0), "C1": (u1 + tail, W/2, 0), "RA": (u1, 0, R),
             "H0": (u0, -a, 0), "H1": (u0, -a, t), "H2": (u0, a, t), "H3": (u0, a, 0),
             "L": (u0, -k, t), "Rt": (u0, k, t)}
        v = {n: bm.verts.new(M @ Vector(p)) for n, p in P.items()}
        inside = M @ Vector(((u0 + u1) / 2, 0, R / 3))
        for f in (["B0", "C0", "RA", "FA"], ["B1", "C1", "RA", "FA"], ["C0", "C1", "RA"], ["B0", "B1", "C1", "C0"],
                  ["B0", "H0", "H1", "L"], ["B1", "H3", "H2", "Rt"], ["L", "H1", "H2", "Rt", "FA"]):
            fc = bm.faces.new([v[n] for n in f]); fc.normal_update()
            if fc.normal.dot(fc.calc_center_median() - inside) < 0: fc.normal_flip()
    def ring(s, mat, cx, cy, z0, r_in, r_out, hgt, seg=24, gap_seg=1, a_off=0.0):
        """Ring wall; the first gap_seg segments (starting at angle a_off) are left open."""
        bm = s.b(mat)
        for i in range(seg):
            if i < gap_seg: continue
            a0 = a_off + 2 * math.pi * i / seg; a1 = a_off + 2 * math.pi * (i + 1) / seg
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

def tube(mat, p0, p1, r, seg=8):
    """Round bar / pipe / barrel between two points (x, y, z)."""
    a, b = Vector(p0), Vector(p1); dv = b - a
    if dv.length < 1e-4: return
    M = Matrix.Translation((a + b) / 2) @ dv.to_track_quat("Z", "Y").to_matrix().to_4x4()
    bmesh.ops.create_cone(G.b(mat), cap_ends=True, segments=seg, radius1=r, radius2=r, depth=dv.length, matrix=M)

PATH_PTS = []          # dense points of every footpath, used for ground scuffing
NODES = []     # empties to create: (name, x, y, z, props)

FIXTURES = {"lamps": [], "doors": []}    # written to blender/out/fixtures.json for place_props.py (wall lamps over doors)
_lit = random.Random(5)

def building(mat_wall, cx, cy, w, d, hgt, door_face_x=None, roof="roof", name=None, rot=0.0, floor_mat="floor", z0=None, door_w=1.4, windows=True, bars=False):
    """Single-room building: door gap in the end wall facing door_face_x (+1 / -1 along local x, 2 = both), glazed
    windows with frames and mullions in the long walls, corner pilasters, a plinth, an open wooden door leaf,
    a door step, and a pitched corrugated roof (two sheets with eaves, fascia boards, gutters, downpipes and
    gable end walls) or a flat slab roof."""
    z = site(cx, cy, 0.5 * math.hypot(w, d) + 1.5) if z0 is None else z0
    FOOTPRINTS.append((cx, cy, w, d, rot))
    t = 0.3; dh = 2.3
    G.box(mat_wall, cx, cy, z - 1.5, w, d, 1.5, rot)          # foundation skirt
    G.box(floor_mat, cx, cy, z, w - 0.2, d - 0.2, 0.15, rot)  # floor slab (walkable)
    c, s_ = math.cos(rot), math.sin(rot)
    def at(lx, ly): return cx + lx * c - ly * s_, cy + lx * s_ + ly * c
    R = Matrix.Rotation(rot, 4, "Z")
    def M(lx, ly, zz): x_, y_ = at(lx, ly); return Matrix.Translation((x_, y_, zz)) @ R
    doors = [sx for sx in (-1, 1) if door_face_x is not None and (sx == door_face_x or door_face_x == 2)]
    # long walls (along local x), with window openings
    nwin = max(0, int((w - 2.0) / 3.4)) if (windows and hgt >= 2.8) else 0
    sill, wh, ww = 0.95, 1.25, 1.0
    for sy in (-1, 1):
        x_, y_ = at(0, sy * (d / 2 - t / 2))
        if nwin == 0:
            G.box(mat_wall, x_, y_, z, w, t, hgt, rot); continue
        G.box(mat_wall, x_, y_, z, w, t, sill, rot)                                  # below the windows
        G.box(mat_wall, x_, y_, z + sill + wh, w, t, hgt - sill - wh, rot)             # above the windows
        sp = w / nwin; edges = [-w / 2]
        for k in range(nwin):
            wc = -w / 2 + sp * (k + 0.5); edges += [wc - ww / 2, wc + ww / 2]
        edges.append(w / 2)
        for k in range(0, len(edges), 2):                                              # piers between the windows
            a_, b_ = edges[k], edges[k + 1]
            if b_ - a_ > 0.05:
                px, py = at((a_ + b_) / 2, sy * (d / 2 - t / 2)); G.box(mat_wall, px, py, z + sill, b_ - a_, t, wh, rot)
        for k in range(nwin):
            wc = -w / 2 + sp * (k + 0.5); yo = sy * (d / 2 - t / 2)
            if bars:
                for b_i in range(5):
                    bx, by = at(wc - ww / 2 + 0.12 + b_i * (ww - 0.24) / 4, yo)
                    G.box("grate", bx, by, z + sill, 0.035, 0.035, wh, rot)
            else:                                                                       # glass, a few panes lit at night
                G.mbox("glass_lit" if _lit.random() < 0.18 else "glass", M(wc, yo, z + sill + wh / 2), ww - 0.04, 0.02, wh - 0.04)
                G.mbox("wood", M(wc, yo + sy * 0.02, z + sill + wh / 2), 0.05, 0.06, wh)          # mullion
                G.mbox("wood", M(wc, yo + sy * 0.02, z + sill + wh * 0.55), ww, 0.06, 0.05)       # transom
            fy = sy * (d / 2 + 0.01)                                                        # outer frame and sill
            G.mbox("wood", M(wc, fy, z + sill - 0.03), ww + 0.2, 0.12, 0.07)
            G.mbox("wood", M(wc, fy, z + sill + wh + 0.04), ww + 0.16, 0.08, 0.08)
            for sx2 in (-1, 1): G.mbox("wood", M(wc + sx2 * (ww / 2 + 0.04), fy, z + sill + wh / 2), 0.08, 0.08, wh)
    # end walls (local +/-x); the door face has a gap
    for sx in (-1, 1):
        x_, y_ = at(sx * (w / 2 - t / 2), 0)
        if sx in doors:
            seg = (d - 2 * t - door_w) / 2
            for sy in (-1, 1):
                xx, yy = at(sx * (w / 2 - t / 2), sy * (door_w / 2 + seg / 2 + 0)); G.box(mat_wall, xx, yy, z, t, seg + 0.0, hgt, rot)
            G.box(mat_wall, x_, y_, z + dh, t, door_w + 0.02, hgt - dh, rot)  # lintel
            for sy in (-1, 1):                                                  # wooden door frame
                fx, fy = at(sx * (w / 2 + 0.02), sy * (door_w / 2 + 0.04)); G.box("wood", fx, fy, z, t + 0.06, 0.08, dh, rot)
            fx, fy = at(sx * (w / 2 + 0.02), 0); G.box("wood", fx, fy, z + dh - 0.06, t + 0.06, door_w + 0.16, 0.1, rot)
            # open door leaf: hinged on the -y jamb, swung 90 deg inward so it lies along the inside of the long wall
            G.mbox("wood", M(sx * (w / 2 - t - door_w / 2), -(door_w / 2 - 0.03), z + 0.15 + (dh - 0.2) / 2), door_w - 0.06, 0.05, dh - 0.2)
            # door step (walkable) and the lamp over the door
            sx_, sy_ = at(sx * (w / 2 + 0.35), 0); G.box("floor", sx_, sy_, z - 0.12, 0.7, door_w + 0.6, 0.2, rot)
            lx, ly = at(sx * (w / 2 + 0.07), 0)
            G.mbox("lamp", M(sx * (w / 2 + 0.13), 0, z + dh + 0.45), 0.09, 0.12, 0.16)    # bulb inside the Poly Haven sconce
            FIXTURES["lamps"].append([lx, ly, z + dh + 0.35, rot + (0 if sx > 0 else math.pi)])
            FIXTURES["doors"].append([lx, ly, z])
        else:
            G.box(mat_wall, x_, y_, z, t, d - 2 * t, hgt, rot)
    # corner pilasters (break the flat box silhouette)
    for sx in (-1, 1):
        for sy in (-1, 1):
            G.mbox("conc", M(sx * (w / 2 - 0.12), sy * (d / 2 - 0.12), z + hgt / 2), 0.42, 0.42, hgt)
    # plinth (outside the walls only, so the floor stays clear) on the closed sides
    for sy in (-1, 1):
        px, py = at(0, sy * (d / 2 + 0.07)); G.box("conc", px, py, z - 0.1, w + 0.3, 0.16, 0.5, rot)
    for sx in (-1, 1):
        if sx in doors: continue
        px, py = at(sx * (w / 2 + 0.07), 0); G.box("conc", px, py, z - 0.1, 0.16, d, 0.5, rot)
    # roof
    if roof == "flat":
        G.box("conc", cx, cy, z + hgt, w + 0.8, d + 0.8, 0.25, rot)
        G.box("conc", cx, cy, z + hgt + 0.25, w + 0.9, d + 0.9, 0.12, rot)        # parapet cap
        return z
    rise = min(1.6, d * 0.3); ov = 0.6; L = w + 0.8
    half = d / 2 + ov; slope = math.atan2(rise, d / 2); sheet = half / math.cos(slope)
    for sy in (-1, 1):                         # two corrugated sheets, 5 cm thick, running past the walls as eaves
        mid_y = sy * (d / 2 + ov) / 2; mid_z = z + hgt + rise / 2 - (ov * math.tan(slope)) / 2
        Mx = M(0, mid_y, mid_z) @ Matrix.Rotation(-sy * slope, 4, "X")
        G.mbox("roof", Mx, L, sheet, 0.05)
        ez = z + hgt - ov * math.tan(slope)                                       # eave line
        G.mbox("wood", M(0, sy * (d / 2 + ov - 0.02), ez - 0.08), L, 0.04, 0.2)       # fascia board
        tube("rust", (*at(-L / 2, sy * (d / 2 + ov + 0.08)), ez - 0.1), (*at(L / 2, sy * (d / 2 + ov + 0.08)), ez - 0.1), 0.07, 8)   # gutter
        for sx in (-1, 1):                                                      # downpipes at the corners
            px, py = at(sx * (w / 2 - 0.45), sy * (d / 2 + 0.1))
            tube("rust", (px, py, z - 0.05), (px, py, ez - 0.1), 0.045, 6)
    for sx in (-1, 1):                         # gable end walls (triangles) in the wall material
        bm = G.b(mat_wall); Mg = M(sx * (w / 2 - t / 2), 0, z + hgt)
        v = [bm.verts.new(Mg @ Vector(p)) for p in ((-t / 2, -d / 2, 0), (-t / 2, d / 2, 0), (-t / 2, 0, rise), (t / 2, -d / 2, 0), (t / 2, d / 2, 0), (t / 2, 0, rise))]
        fs = [bm.faces.new([v[i] for i in f]) for f in ((0, 2, 1), (3, 4, 5), (0, 1, 4, 3), (1, 2, 5, 4), (2, 0, 3, 5))]
        bmesh.ops.recalc_face_normals(bm, faces=fs)
    G.mbox("rust", M(0, 0, z + hgt + rise + 0.02), L + 0.1, 0.36, 0.06)          # ridge cap
    return z

def pit(cx, cy, r=3.2, hgt=1.1, mat="conc", gun=True):
    z = site(cx, cy, r + 3)
    G.disc("floor", cx, cy, z + 0.05, r - 0.05)
    G.ring(mat, cx, cy, z, r, r + 0.7, hgt, seg=24, gap_seg=2)
    G.cyl("conc_w", cx, cy, z, 0.35, 0.9)       # central pivot
    if gun:
        ang = 0.9; ca, sa = math.cos(ang), math.sin(ang)
        def P(d, up, side=0.0): return (cx + d * ca - side * sa, cy + d * sa + side * ca, z + up)
        G.cyl("rust", cx, cy, z + 0.9, 0.95, 0.28, 18)                              # traversing platform on the pivot
        tube("rust", P(0, 0.9), P(0, 1.45), 0.34, 10)                               # pedestal
        for sd in (-0.55, 0.55): G.box("rust", *P(0.0, 1.45, sd)[:2], z + 1.3, 0.28, 0.18, 0.9, ang)   # trunnion cheeks
        tube("rust", P(-0.9, 1.75), P(0.7, 1.75), 0.2, 10)                          # breech
        tube("rust", P(0.7, 1.75), P(3.9, 2.35), 0.16, 10)                          # barrel (rising)
        tube("grate", P(3.4, 2.27), P(3.95, 2.37), 0.21, 10)                        # muzzle ring
        G.box("rust", *P(0.55, 1.95)[:2], z + 1.3, 0.08, 1.5, 1.1, ang)             # gun shield
    return z

def text_mesh(txt, mat, size, depth, M):
    cu = bpy.data.curves.new("sign", "FONT"); cu.body = txt; cu.size = size; cu.extrude = depth * 0.5
    cu.align_x = "CENTER"; cu.align_y = "CENTER"; cu.space_character = 1.12
    ob = bpy.data.objects.new("sign", cu); bpy.context.scene.collection.objects.link(ob)
    ev = ob.evaluated_get(bpy.context.evaluated_depsgraph_get()); me = bpy.data.meshes.new_from_object(ev)
    tb = bmesh.new(); tb.from_mesh(me); bmesh.ops.transform(tb, matrix=M, verts=tb.verts); tb.to_mesh(me); tb.free()
    G.b(mat).from_mesh(me)
    bpy.data.objects.remove(ob, do_unlink=True); bpy.data.curves.remove(cu); bpy.data.meshes.remove(me)

def gun_bay(cx, cy, rear, gun=False, board=False, magazine=False):
    """6-inch BL coast gun emplacement as photographed at the museum (reference/photos/weapons-display): an open circular
    pit about 7.5 m across inside a 1.25 m thick, 1.3 m high parapet, open at the rear (angle rear), a holdfast ring of
    bolts in the centre, and ready-use ammunition lockers (steel-framed recesses) in the outer face. Same pattern as the
    1930s Singapore 6-inch batteries (Mk VII gun on a Mk II mounting). The museum's pits are empty; gun=True adds one."""
    r_in, r_out, hgt = 3.75, 5.0, 1.3
    z = site(cx, cy, r_out + 3)
    G.disc("floor", cx, cy, z + 0.05, r_in - 0.05, seg=28)
    gap = 3                                                        # 3 of 28 segments, about 2.7 m opening at the rear
    G.ring("conc_g", cx, cy, z, r_in, r_out, hgt, seg=28, gap_seg=gap, a_off=rear - math.pi * gap / 28)
    G.ring("conc", cx, cy, z + hgt, r_in - 0.05, r_in + 0.35, 0.08, seg=28, gap_seg=gap, a_off=rear - math.pi * gap / 28)   # coping
    G.disc("conc_w", cx, cy, z + 0.07, 1.05, seg=20)                # holdfast ring and bolts
    for k in range(16):
        a = 2 * math.pi * k / 16; G.box("rust", cx + 0.9 * math.cos(a), cy + 0.9 * math.sin(a), z + 0.07, 0.06, 0.06, 0.16)
    for k in range(-2, 3):                                         # lockers on the seaward side (opposite the rear opening)
        a = rear + math.pi + k * 0.42; ca, sa = math.cos(a), math.sin(a)
        G.box("black", cx + (r_out + 0.01) * ca, cy + (r_out + 0.01) * sa, z + 0.12, 0.04, 1.0, 0.8, a)
        for sg in (-1, 1):
            G.box("rust", cx + (r_out + 0.03) * ca - sg * 0.55 * sa, cy + (r_out + 0.03) * sa + sg * 0.55 * ca, z + 0.08, 0.07, 0.08, 0.9, a)
        G.box("rust", cx + (r_out + 0.03) * ca, cy + (r_out + 0.03) * sa, z + 0.92, 0.07, 1.2, 0.08, a)
    c, s_ = math.cos(rear), math.sin(rear)
    if gun:
        ang = rear + math.pi; ca, sa = math.cos(ang), math.sin(ang)
        def P(d, up, side=0.0): return (cx + d * ca - side * sa, cy + d * sa + side * ca, z + up)
        G.cyl("rust", cx, cy, z + 0.2, 0.95, 0.5, 18)                                # mounting on the holdfast
        tube("rust", P(0, 0.7), P(0, 1.45), 0.34, 10)
        for sd in (-0.55, 0.55): G.box("rust", *P(0.0, 1.45, sd)[:2], z + 1.3, 0.28, 0.18, 0.9, ang)
        tube("rust", P(-0.9, 1.75), P(0.7, 1.75), 0.2, 10)                          # breech
        tube("rust", P(0.7, 1.75), P(4.6, 2.1), 0.16, 10)                           # barrel, over the parapet
        tube("grate", P(4.1, 2.06), P(4.65, 2.11), 0.21, 10)
        G.box("rust", *P(0.55, 1.95)[:2], z + 1.0, 0.08, 1.9, 1.3, ang)             # low Mk I shield
    if board:                                                      # "Penang Fortress Battery" picture board beside the opening
        bx, by = cx + c * (r_out + 1.2) - s_ * 3.2, cy + s_ * (r_out + 1.2) + c * 3.2
        for sg in (-1, 1): G.box("rust", bx - s_ * sg * 1.1, by + c * sg * 1.1, z, 0.08, 0.08, 2.4, rear)
        G.box("flag_white", bx, by, z + 1.0, 0.05, 2.6, 1.5, rear)
        MT = Matrix(((0, 0, 1, 0), (1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 0, 1)))       # as the entrance sign: readable from the +x side
        text_mesh("PENANG FORTRESS BATTERY", "black", 0.15, 0.01, Matrix.Translation((bx + c * 0.04, by + s_ * 0.04, z + 2.3)) @ Matrix.Rotation(rear, 4, "Z") @ MT)
        G.box("black", bx + c * 0.04, by + s_ * 0.04, z + 1.35, 0.02, 1.2, 0.5, rear)  # the gun silhouette on the board
    if magazine:                                                   # green retaining wall behind the bay with the magazine's rusty grille door
        ma = rear + 1.35; cm, sm = math.cos(ma), math.sin(ma)                         # to one side of the rear opening, facing the bay
        mx, my = cx + cm * (r_out + 3.5), cy + sm * (r_out + 3.5)
        G.box("conc_g", mx, my, z - 0.2, 0.6, 8.0, 2.6, ma)
        G.box("grate", mx - cm * 0.32, my - sm * 0.32, z, 0.06, 2.0, 2.1, ma)
        G.box("black", mx - cm * 0.305, my - sm * 0.305, z, 0.02, 1.9, 2.05, ma)       # dark passage behind the grille
        G.box("conc", mx, my, z + 2.4, 0.8, 8.2, 0.15, ma)
        node("loc_25_magazine", mx, my, z, label="Magazine entrance (grille door)")
    return z

def lockup(cx, cy, rot, cells=3, cw=3.2, d=4.2, hgt=2.6, door_side=-1):
    """Lock-up block as photographed (reference/photos/prison-area): thick mossy concrete, a flat slab roof, one cell per
    door, heavy steel door frames with a barred transom, low brick walls beside each door, whitewashed cells with chains
    and an iron cage bed. door_side = -1 / +1 picks the long wall (local y) with the doors."""
    w = cells * cw; t = 0.4
    z = site(cx, cy, 0.5 * math.hypot(w, d) + 1.5)
    FOOTPRINTS.append((cx, cy, w, d, rot))
    c, s_ = math.cos(rot), math.sin(rot)
    def at(lx, ly): return cx + lx * c - ly * s_, cy + lx * s_ + ly * c
    G.box("conc_g", cx, cy, z - 1.5, w, d, 1.5, rot)
    G.box("floor", cx, cy, z, w - 0.2, d - 0.2, 0.15, rot)
    yb = -door_side * (d / 2 - t / 2)
    x_, y_ = at(0, yb); G.box("conc_g", x_, y_, z, w, t, hgt, rot)                      # back wall
    for sx in (-1, 1): x_, y_ = at(sx * (w / 2 - t / 2), 0); G.box("conc_g", x_, y_, z, t, d, hgt, rot)
    for k in range(1, cells): x_, y_ = at(-w / 2 + k * cw, 0); G.box("conc_g", x_, y_, z, 0.3, d - 2 * t, hgt, rot)   # cell walls
    dw, dh = 1.0, 2.0; yf = door_side * (d / 2 - t / 2)
    for k in range(cells):
        cx_ = -w / 2 + (k + 0.5) * cw; seg = (cw - dw) / 2
        for sg in (-1, 1):
            x_, y_ = at(cx_ + sg * (dw / 2 + seg / 2), yf); G.box("conc_g", x_, y_, z, seg, t, hgt, rot)
        x_, y_ = at(cx_, yf); G.box("conc_g", x_, y_, z + dh + 0.5, dw, t, hgt - dh - 0.5, rot)
        G.box("grate", x_, y_, z + dh, dw, 0.06, 0.5, rot)                                # barred transom
        for b in range(4): bx, by = at(cx_ - 0.36 + b * 0.24, yf); G.box("rust", bx, by, z + dh, 0.03, t + 0.04, 0.5, rot)
        for sg in (-1, 1): fx_, fy_ = at(cx_ + sg * (dw / 2 + 0.05), door_side * (d / 2 + 0.03)); G.box("black", fx_, fy_, z, 0.12, 0.1, dh + 0.55, rot)
        lx, ly = at(cx_ + dw / 2 - 0.03, door_side * (d / 2 - t - 0.5)); G.box("black", lx, ly, z + 0.15, 0.06, 0.96, dh - 0.1, rot + math.pi / 2)   # steel door, open inward (photo cell-door-1)
        for sg in (-1, 1):                                                                 # low brick walls flanking the approach, set back from the door (photo cell-door-1)
            kx, ky = at(cx_ + sg * (dw / 2 + 0.75), door_side * (d / 2 + 0.8)); G.box("brick", kx, ky, z - 0.2, 0.3, 1.6, 0.6, rot)
        for sg in (-1, 1):                                                                 # whitewashed cell walls (inside)
            x_, y_ = at(cx_ + sg * (cw / 2 - 0.17), 0); G.box("plaster", x_, y_, z + 0.15, 0.02, d - 2 * t - 0.05, hgt - 0.2, rot)
        x_, y_ = at(cx_, yb + door_side * (t / 2 + 0.01)); G.box("plaster", x_, y_, z + 0.15, cw - 0.4, 0.02, hgt - 0.2, rot)
        ux, uy = at(cx_ - 0.3, -door_side * 1.2)                                           # iron cage bed against the back wall
        G.box("grate", ux, uy, z + 0.15, 1.9, 0.8, 0.06, rot); G.box("grate", ux, uy, z + 0.75, 1.9, 0.8, 0.04, rot)
        for sx in (-1, 1):
            for sy in (-1, 1): px, py = at(cx_ - 0.3 + sx * 0.92, -door_side * 1.2 + sy * 0.36); G.box("rust", px, py, z + 0.15, 0.04, 0.04, 0.95, rot)
        for sg in (-1, 1): hx, hy = at(cx_ + sg * 0.9, yb + door_side * 0.25); G.box("rust", hx, hy, z + 1.0, 0.03, 0.03, 1.3, rot)   # hanging chains
        lx, ly = at(cx_, 0); G.box("lamp", lx, ly, z + hgt - 0.18, 0.1, 0.1, 0.12, rot)   # bare bulb
        FIXTURES["doors"].append([*at(cx_, door_side * (d / 2 + 0.07)), z])
    G.box("conc", cx, cy, z + hgt, w + 0.5, d + 0.5, 0.35, rot)                          # thick flat roof slab
    return z

def exhibits(cx, cy, w, d, z, rot, door_face_x, hgt=3.2):
    """Barracks used as exhibition rooms (Island Drum 2022, Malaysia Traveller, The Planet's Journal 2013): framed
    photos and newspaper boards on the closed end wall, free-standing boards and a glass display case, a dim bulb."""
    c, s_ = math.cos(rot), math.sin(rot)
    def at(lx, ly): return cx + lx * c - ly * s_, cy + lx * s_ + ly * c
    back = -1 if door_face_x in (1, None) else (1 if door_face_x == -1 else None)
    if back is not None:                                                                  # board on the closed end wall
        x_, y_ = at(back * (w / 2 - 0.36), 0); G.box("wood", x_, y_, z + 0.9, 0.05, min(d - 1.2, 3.6), 1.5, rot)
        for k in range(3):
            px, py = at(back * (w / 2 - 0.39), (k - 1) * 1.05); G.box("paper", px, py, z + 1.05, 0.02, 0.8, 1.1, rot)
    for k, lx in enumerate((-w * 0.22, w * 0.22)):                                         # two free-standing boards, back to back prints
        x_, y_ = at(lx, -d * 0.18); G.box("wood", x_, y_, z + 0.15, 1.6, 0.06, 1.8, rot)
        for sg in (-1, 1):
            px, py = at(lx, -d * 0.18 + sg * 0.04); G.box("paper", px, py, z + 0.55, 1.3, 0.02, 1.1, rot)
    x_, y_ = at(0, d * 0.18)                                                               # display case: wooden base, glass top
    G.box("wood", x_, y_, z + 0.15, 2.0, 0.8, 0.8, rot); G.box("paper", x_, y_, z + 0.95, 1.9, 0.7, 0.02, rot)
    G.box("glass", x_, y_, z + 0.97, 2.0, 0.8, 0.35, rot)
    G.box("lamp", cx, cy, z + hgt - 0.15, 0.1, 0.1, 0.12, rot)

def pillbox(cx, cy, rot=0.0, kind="type1"):
    """Pill box from the user's Blender models (blender/user_models/penang_pillbox_type1/2.blend), baked in later by
    user_models.py. Type 1: rectangular, 4.4 x 3.0 m, door in the local +x end wall, stands on the ground.
    Type 2: octagonal, 4 m across, sunk 1.3 m into the ground, entrance stairs on the local -x side; the terrain is
    carved for its interior and the stair trench."""
    if kind == "type1":
        z = site(cx, cy, 5)
        USER_PLACES.append(("pillbox_type1", cx, cy, z - 0.1, rot)); FIXTURES.setdefault("zones", []).append([cx, cy, 4.0])
        FOOTPRINTS.append((cx, cy, 4.6, 3.2, rot))
        return z
    z = max(h_base(cx, cy), SEA_Z + 2.0)          # ground level of the model (local z 0.4); on the shore, kept dry
    PADS.append((cx, cy, 5.0, 9.0, z))
    zo = z - 0.4                                   # model origin
    CARVES.append((cx, cy, rot, "oct", 1.9, 0, 0, zo - 0.95))                 # interior (floor at local -0.9)
    CARVES.append((cx, cy, rot, "box", -4.25, -1.85, 0.72, zo - 1.2))        # stair trench
    USER_PLACES.append(("pillbox_type2", cx, cy, zo, rot)); FIXTURES.setdefault("zones", []).append([cx - 1.0, cy, 5.5])
    FOOTPRINTS.append((cx, cy, 4.3, 4.3, rot))
    return z

def tunnel(cx, cy, ang, length=26.0, w=2.2, hgt=2.5, name="tunnel"):
    """Straight tunnel entering the hill from a portal at (cx, cy) in direction ang."""
    z = site(cx, cy, 8, 6)
    c, s_ = math.cos(ang), math.sin(ang)
    mx, my = cx + c * length / 2, cy + s_ * length / 2
    G.box("floor", mx, my, z, length, w, 0.15, ang)
    # whitewashed walls and ceiling with wall lamps every 6 m (reference/photos/japanese-tunnel)
    for sy in (-1, 1):
        G.box("plaster", mx - s_ * sy * (w / 2 + 0.2), my + c * sy * (w / 2 + 0.2), z, length, 0.4, hgt, ang)
    G.box("plaster", mx, my, z + hgt, length, w + 0.8, 0.4, ang)
    for k in range(int(length / 6)):
        u = 3.0 + 6.0 * k; lx, ly = cx + c * u + s_ * (w / 2 - 0.06), cy + s_ * u - c * (w / 2 - 0.06)
        G.box("lamp", lx, ly, z + 1.9, 0.1, 0.12, 0.16, ang)
    # earth mound over the tunnel: open at the portal (just behind the portal wall), sloping down past the inner end
    G.mound("ground", cx, cy, z - 0.8, 0.15, length + 1.0, w + 12, hgt + 3.8, ang, a=w / 2 + 0.4, t=hgt + 0.4 + 0.8)
    TUNNELS.append((cx, cy, ang, length + 1.0, z))
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
# Strict sitemap layout (2026-11-27): every numbered point, facility, building angle, path, road, the hill and the coast
# come from the reeaki "Fort Relics" visitor map through extract_reeaki.py (reference/sitemap/reeaki_layout.json).
# The 55 deg LAYOUT_ROT, the fixed points and the satellite car park of 2026-11-26 are gone: the map is followed as drawn.
PTS = {p["n"]: p for p in SITE["numbered"]}
for _n, _p in PTS.items():
    _r = RK["points"][str(_n)]
    _p["east_m"], _p["north_m"] = _r["east_m"], _r["north_m"]
    _p["rot"] = ((_r["rot"] + math.pi / 2) % math.pi) - math.pi / 2       # long axis; buildings are symmetric end to end
FAC = {k: dict(v, name=k) for k, v in RK["facilities"].items()}
def E(n): return PTS[n]["east_m"], PTS[n]["north_m"]
MAP_PATHS = [[(p[0], p[1]) for p in r["pts"]] for r in RK["roads"] if r["kind"] == "path"]
MAP_ROADS = [[(p[0], p[1]) for p in r["pts"]] for r in RK["roads"] if r["kind"] == "road"]
_PP = [q for ln in MAP_PATHS for a, b in zip(ln, ln[1:]) for q in [(a[0] + (b[0] - a[0]) * t / 4, a[1] + (b[1] - a[1]) * t / 4) for t in range(4)]]
def _dpath(x, y): return min(math.hypot(x - a, y - b) for a, b in _PP) if _PP else 99.0
def face_to_path(x, y, w, rot):
    """+1 / -1: the end wall (local x) nearest a path on the map gets the door."""
    c_, s_ = math.cos(rot), math.sin(rot)
    return +1 if _dpath(x + c_ * w / 2, y + s_ * w / 2) <= _dpath(x - c_ * w / 2, y - s_ * w / 2) else -1
def side_to_path(x, y, d, rot):
    """+1 / -1: the long wall (local y) nearest a path."""
    c_, s_ = math.cos(rot), math.sin(rot)
    return +1 if _dpath(x - s_ * d, y + c_ * d) <= _dpath(x + s_ * d, y - c_ * d) else -1
LAYOUT_ROT = 0.0
def building_n(n, mat, x, y, w, d, hgt, **k):
    rot = PTS[n]["rot"]; fx = face_to_path(x, y, w, rot); PTS[n]["_fx"] = fx
    return building(mat, x, y, w, d, hgt, door_face_x=fx, rot=rot, **k)

def slug(s): return "".join(c.lower() if c.isalnum() else "_" for c in s).strip("_")
def node(name, x, y, z, **props): NODES.append((name, x, y, z, props))

# ---- numbered points
for n, p in sorted(PTS.items()):
    x, y = p["east_m"], p["north_m"]; nm = p["name"]; R_ = p["rot"]
    if n in (1, 2, 37):                 # map pill boxes: the user's type 1, door toward the nearest path
        z = pillbox(x, y, R_ + (0.0 if face_to_path(x, y, 4.4, R_) > 0 else math.pi))
    elif n in (7, 13, 14, 15, 16, 18, 21, 22):     # barracks blocks, now exhibition rooms
        z = building_n(n, "plaster", x, y, 14, 5.5, 3.2); exhibits(x, y, 14, 5.5, z, R_, p["_fx"])
    elif n in (12,):
        z = building_n(n, "brick", x, y, 24, 6, 3.4)
    elif n in (17,):
        z = building_n(n, "brick", x, y, 10, 6, 3.2)
    elif n == 3:
        z = building_n(n, "conc_g", x, y, 9, 6, 3.2); exhibits(x, y, 9, 6, z, R_, p["_fx"])
    elif n == 4:
        z = building_n(n, "conc_w", x, y, 6, 5, 3.0)
    elif n == 6:
        z = building_n(n, "camo", x, y, 9, 6, 3.2)
    elif n == 9:
        z = building_n(n, "plaster", x, y, 10, 6, 3.2); exhibits(x, y, 10, 6, z, R_, p["_fx"])
    elif n == 10:
        z = building_n(n, "plaster", x, y, 12, 6, 3.2); exhibits(x, y, 12, 6, z, R_, p["_fx"])
    elif n == 11:
        z = building_n(n, "conc_g", x, y, 6, 5, 3.0)
    elif n in (19, 20):   # lock-up blocks: doors on the long side that faces the path drawn on the map
        z = lockup(x, y, R_, door_side=side_to_path(x, y, 4.2, R_))
    elif n == 35:
        z = building_n(n, "conc_w", x, y, 8, 5, 3.0)
    elif n == 8:   # underground communication centre: semi-buried bunker under an earth mound
        z = building_n(n, "conc_w", x, y, 12, 6.5, 2.8, roof="flat")
        G.gable("ground", x, y, z + 2.4, 16, 12, 3.2, R_)
    elif n == 23:
        z = site(x, y, 6); G.cyl("conc", x, y, z, 3.0, 0.8, seg=20); G.box("rust", x, y, z + 0.8, 0.9, 0.9, 0.12)
    elif n == 24:   # observation post tower
        z = site(x, y, 8)
        G.box("conc", x, y, z - 1, 4.2, 4.2, 6.2)
        G.box("floor", x, y, z + 5.2, 5.2, 5.2, 0.2)
        for sx, sy in ((1, 1), (1, -1), (-1, 1), (-1, -1)): G.box("rust", x + sx * 2.5, y + sy * 2.5, z + 5.4, 0.1, 0.1, 1.6)
        for s_ in (-1, 1):
            G.box("grate", x, y + s_ * 2.5, z + 5.4, 5.0, 0.04, 1.6)
        G.box("grate", x - 2.5, y, z + 5.4, 0.04, 5.0, 1.6)                       # west rail
        for s_ in (-1, 1):                                                        # east rail with a 1.4 m gap where the stairs arrive
            G.box("grate", x + 2.5, y + s_ * 1.6, z + 5.4, 0.04, 1.8, 1.6)
        G.stairs("floor", x + 10.4, y, math.pi, z, z + 5.2, 1.2)
    elif n == 25:         # canon firing bay: empty 6-inch emplacement, as at the museum, with its sign board and magazine door
        z = gun_bay(x, y, math.atan2(E(30)[1] - y, E(30)[0] - x), board=True, magazine=True)
    elif n == 36:         # canon: the same emplacement with a gun mounted
        eps = 3.0; g = (h_base(x + eps, y) - h_base(x - eps, y), h_base(x, y + eps) - h_base(x, y - eps))
        z = gun_bay(x, y, math.atan2(g[1], g[0]) if (abs(g[0]) + abs(g[1])) > 1e-6 else 0.0, gun=True)
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
        ang0 = math.atan2(g[1], g[0]) if (abs(g[0]) + abs(g[1])) > 1e-6 else 0.0   # uphill
        # the tunnel (26 m, plus 7.5 m crawl and shaft in 29) must not run under another map point or a path:
        # turn it away from uphill by the smallest angle that keeps its far end and the shaft clear
        def _clear(a):
            for t_ in (8.0, 14.0, 20.0, 26.0, 30.0, 34.0):
                qx, qy = x + math.cos(a) * t_, y + math.sin(a) * t_
                if any(math.hypot(qx - q["east_m"], qy - q["north_m"]) < 12.0 for k_, q in PTS.items() if k_ != n and isinstance(k_, int)): return False
                if t_ >= 14.0 and _dpath(qx, qy) < 4.0: return False
            return True
        ang = next((ang0 + d_ for d_ in [math.radians(s_ * k) for k in range(0, 181, 10) for s_ in (1, -1)] if _clear(ang0 + d_)), ang0)
        z, mx, my = tunnel(x, y, ang, 26.0)
        PTS[n]["_tunnel"] = (ang, z)
    elif n == 27:
        z = pillbox(x, y, R_ + (0.0 if face_to_path(x, y, 4.4, R_) > 0 else math.pi))
    else:
        z = site(x, y, 4)
    node(f"loc_{n:02d}_{slug(nm)}", x, y, z + 0.0, map_no=n, label=nm, rot=round(R_, 4), door=int(p.get("_fx", 0)))
    p["_z"] = z

# ---- facilities and outside items
def fac(name): f = FAC[name]; return f["east_m"], f["north_m"]
x, y = fac("Information & Ticketing"); z = building("conc_g", x, y, 14, 8, 3.4, door_face_x=2, name="ticketing"); TICKET_Z = z
G.box("wood", x + 8.6, y, z - 0.05, 3.2, 8, 0.2)                                          # timber deck in front of the east door
# lean-to canopy over the deck: a corrugated sheet sloping away from the wall on four timber posts with a beam
_cs = math.atan2(0.5, 3.4)
G.mbox("roof", Matrix.Translation((x + 8.7, y, z + 3.05)) @ Matrix.Rotation(_cs, 4, "Y"), 3.6, 9.0, 0.05)
for _py in (-4.2, -1.4, 1.4, 4.2): G.box("wood", x + 10.1, y + _py, z, 0.16, 0.16, 2.78)
G.box("wood", x + 10.1, y, z + 2.66, 0.18, 9.0, 0.16)
node("loc_fac_ticketing", x, y, z, label="Information & Ticketing")
x, y = fac("Souvenir shop"); z = building("brick", x, y, 10, 6, 3.2, door_face_x=face_to_path(x, y, 10, 0.0)); node("loc_fac_souvenir", x, y, z, label="Souvenir shop")
x, y = fac("Cafeteria"); z = building("camo", x, y, 16, 10, 3.4, door_face_x=face_to_path(x, y, 16, 0.0)); node("loc_fac_cafeteria", x, y, z, label="Cafeteria")
for k, nm in enumerate(("Toilets 36", "Toilets 17", "Toilets 10")):   # the three toilet icons on the map
    tx, ty = fac(nm); z = building("conc_g", tx, ty, 5, 4, 2.8, door_face_x=face_to_path(tx, ty, 5, 0.0)); node(f"loc_fac_toilet_{k+1}", tx, ty, z, label="Toilets")
for nm, w_, d_ in (("Car Park", 40, 30), ("VIP Car Park", 20, 12)):
    x, y = fac(nm); z = site(x, y, 0.5 * math.hypot(w_, d_) + 2, 10); G.box("asphalt", x, y, z, w_, d_, 0.12)
    node(f"loc_fac_{slug(nm)}", x, y, z, label=nm)
x, y = fac("War Game Park"); z = site(x, y, 20, 10); node("loc_fac_war_game_park", x, y, z, label="War Game Park (open area)")
for k in range(5): G.box("camo", x + random.uniform(-14, 14), y + random.uniform(-14, 14), z, random.uniform(2, 4), 0.4, 1.6, random.uniform(0, 3))
# coast (map frame +x, image-left): barbed wire, well, four pill boxes, slipway, jetty, maritime museum, generator room, tank
x, y = fac("Barbed wire (coast)"); z = site(x, y, 3); post_line(x - 8, y + 6, x + 8, y - 6); node("loc_fac_coast_barbed_wire", x, y, z, label="Barbed wire (coast)")
x, y = fac("Well (coast)"); z = site(x, y, 3); G.ring("rock", x, y, z, 0.8, 1.3, 0.9, seg=14, gap_seg=0); node("loc_fac_coast_well", x, y, z, label="Well (coast)")
for k, key in enumerate("ABCD"):
    x, y = fac(f"Pill Box (coast) {key}"); z = pillbox(x, y, 0.0, kind="type2")      # user's type 2: stairs inland
    node(f"loc_fac_coast_pillbox_{key.lower()}", x, y, z, label="Pill Box (coast)")
x, y = fac("Submarine Landing Bay"); z = site(x, y, 6); G.box("conc", x + 4, y, z, 12, 4, 0.5); node("loc_fac_submarine_landing_bay", x, y, z, label="Submarine Landing Bay (slipway)")
x, y = fac("Maritime Museum"); z = building("brick", x, y, 12, 7, 3.2, door_face_x=1); node("loc_fac_maritime_museum", x, y, z, label="Maritime Museum")
x, y = fac("Jetty"); _mx, _my = fac("Maritime Museum")          # timber deck from the museum's shore out to the jetty dot on the map
_ja = math.atan2(y - _my, x - _mx); _jl = math.hypot(x - _mx, y - _my) + 6.0; _jx, _jy = _mx + math.cos(_ja) * (_jl / 2 + 5), _my + math.sin(_ja) * (_jl / 2 + 5)
G.box("wood", _jx, _jy, SEA_Z + 0.4, _jl, 2.4, 0.2, _ja); node("loc_fac_jetty", x, y, SEA_Z + 0.6, label="Jetty")
for k in range(int(_jl / 4) + 1):
    for sg in (-1, 1):
        _px = _mx + math.cos(_ja) * (5 + 4 * k) - math.sin(_ja) * sg * 1.3; _py = _my + math.sin(_ja) * (5 + 4 * k) + math.cos(_ja) * sg * 1.3
        G.box("wood", _px, _py, SEA_Z - 3.0, 0.25, 0.25, 3.5)
x, y = fac("Generator Room (coast)"); z = building("conc_w", x, y, 6, 5, 3.0, door_face_x=-1); node("loc_fac_coast_generator_room", x, y, z, label="Generator Room (coast)")
for nm, key in (("Water Tank (coast)", "coast_water_tank"), ("Water Tank (road)", "road_water_tank")):
    x, y = fac(nm); z = site(x, y, 4); G.cyl("conc", x, y, z, 2.6, 3.0, seg=16); node(f"loc_fac_{key}", x, y, z, label=nm)
# "WAR MUSEUM" billboard beside pill box 1, facing the road below (drawn on the map)
x, y = fac("War Museum signboard"); z = h_base(x, y)
for sg in (-1, 1): G.box("rust", x + sg * 5.0, y, z - 0.5, 0.25, 0.25, 6.5)
G.box("camo", x, y + 0.15, z + 2.6, 11.0, 0.3, 3.6)
MS = Matrix(((-1, 0, 0, 0), (0, 0, 1, 0), (0, 1, 0, 0), (0, 0, 0, 1)))           # text: x -> -X, y -> +Z, extrusion -> +Y (readable from the road side, +Y)
text_mesh("WAR MUSEUM", "yellow", 1.4, 0.3, Matrix.Translation((x, y + 0.35, z + 4.4)) @ MS)
node("loc_fac_war_museum_signboard", x, y, z, label="War Museum signboard")

# ---- entrance: the user's Blender model (blender/user_models/penang_war_museum_entrance.blend), baked in by
# user_models.py. In the model the front faces -Y and the driveway runs 12 m along +Y through the gate opening (local
# x = 0, the piers at y 0-2.6) under a covered passage that ends at y = 8.6. Turned 90 deg so the front faces east
# (+X, toward the car parks) and the passage ends just before the ticket building's timber deck; the driveway then
# runs on to the ticket building's east door.
TICKET = fac("Information & Ticketing")
ENT_ROT = math.pi / 2
gx, gy = TICKET[0] + 19.5, TICKET[1]
gz = TICKET_Z                                   # same level as the ticket building, so neither pad buries the other
PADS.append((gx - 4.5, gy + 2.3, 9.5, 6.0, gz))
USER_PLACES.append(("entrance", gx, gy, gz, ENT_ROT))
FIXTURES.setdefault("zones", []).append([gx - 4.0, gy + 2.3, 13.0])        # place_props keeps trees out of the entrance
node("loc_fac_entrance_gate", gx, gy, gz, label="Entrance gate")

def lamp_post(x, y, hgt=4.2):
    z = h_base(x, y)
    tube("rust", (x, y, z), (x, y, z + hgt), 0.07, 6); tube("rust", (x, y, z + hgt), (x + 0.5, y, z + hgt + 0.1), 0.05, 6)
    G.box("lamp", x + 0.55, y, z + hgt - 0.12, 0.28, 0.28, 0.22)
LAMP_POINTS = []
for a_pt, b_pt in zip([TICKET] + [E(k) for k in (3, 4, 34, 5)], [E(k) for k in (3, 4, 34, 5, 24)]):
    L_ = math.hypot(b_pt[0] - a_pt[0], b_pt[1] - a_pt[1]); n_ = max(1, int(L_ / 24))
    for i_ in range(n_):
        t_ = (i_ + 0.5) / n_; px, py = a_pt[0] + (b_pt[0] - a_pt[0]) * t_, a_pt[1] + (b_pt[1] - a_pt[1]) * t_
        nx, ny = -(b_pt[1] - a_pt[1]) / L_, (b_pt[0] - a_pt[0]) / L_
        LAMP_POINTS.append((px + nx * 2.6, py + ny * 2.6))
for lp in LAMP_POINTS:
    if not _in_fp(*lp, 0.8) and _dpath(*lp) > 1.6: lamp_post(*lp)
for lp in ((TICKET[0] + 9, TICKET[1] + 7), (TICKET[0] + 9, TICKET[1] - 7), (TICKET[0] - 10, TICKET[1] + 6)): lamp_post(*lp)

# ---- escape route (provisional, inside tunnel 29): 7 m crawl then a 9 m ladder climb
ang29, z29 = PTS[29]["_tunnel"]
c, s_ = math.cos(ang29), math.sin(ang29)
x29, y29 = PTS[29]["east_m"], PTS[29]["north_m"]
ex, ey = x29 + c * 26.0, y29 + s_ * 26.0                      # inner end of tunnel 29
ESC_MOUTH = (ex - c * 0.8, ey - s_ * 0.8)                     # where visitors stand, at the mouth of the crawl
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

# ---- covered walkway: timber posts and a corrugated roof over the first stretch of the main path from the ticket
# building (The Island Drum 2022: "a main covered sidewalk"; vlog sample6: covered wooden walkway with timber trusses)
_a, _b = fac("Information & Ticketing"), E(3)
_L = math.hypot(_b[0] - _a[0], _b[1] - _a[1]); _ux, _uy = (_b[0] - _a[0]) / _L, (_b[1] - _a[1]) / _L; _nx, _ny = -_uy, _ux
_ang = math.atan2(_uy, _ux); _st = [9.0 + 3.0 * k for k in range(int(max(0.0, _L - 16.0) / 3.0) + 1)]
_tops = []
for _d in _st:
    _px, _py = _a[0] + _ux * _d, _a[1] + _uy * _d; _top = max(h(_px + _nx * sg * 1.85, _py + _ny * sg * 1.85) for sg in (-1, 1)) + 2.6
    _tops.append((_px, _py, _top))
    for sg in (-1, 1):
        qx, qy = _px + _nx * sg * 1.85, _py + _ny * sg * 1.85; G.box("wood", qx, qy, h(qx, qy) - 0.3, 0.14, 0.14, _top - h(qx, qy) + 0.3)
for (p0x, p0y, t0), (p1x, p1y, t1) in zip(_tops, _tops[1:]):
    _mxw, _myw, _tm = (p0x + p1x) / 2, (p0y + p1y) / 2, (t0 + t1) / 2
    _pitch = math.atan2(t1 - t0, 3.0)
    Mw = Matrix.Translation((_mxw, _myw, _tm + 0.18)) @ Matrix.Rotation(_ang, 4, "Z") @ Matrix.Rotation(-_pitch, 4, "Y")
    G.mbox("roof", Mw, 3.05, 4.4, 0.05)
    for sg in (-1, 1): G.mbox("wood", Mw @ Matrix.Translation((0, sg * 1.85, -0.12)), 3.05, 0.12, 0.16)   # side beams
    G.mbox("wood", Matrix.Translation((p0x, p0y, t0 + 0.04)) @ Matrix.Rotation(_ang, 4, "Z"), 0.12, 3.9, 0.12)    # cross beam
node("loc_fac_covered_walkway", *_a, h(*_a), label="Covered walkway")

# ---- memorial (provisional location, unconfirmed)
mx, my = (E(34)[0] + E(5)[0]) / 2 + 6.0, (E(34)[1] + E(5)[1]) / 2      # beside the main path between 34 and 05 (not on the map)
z = site(mx, my, 5)
# as photographed (reference/photos/memorial-zone): black granite plaque on a pale stone plinth, a concrete pad, and a
# low chain fence on steel posts (left open at the front so visitors can step up to the plaque)
G.box("floor", mx, my - 0.6, z, 3.6, 3.0, 0.12)
G.box("plaster", mx, my, z + 0.12, 1.9, 0.7, 0.45); G.box("black", mx, my, z + 0.57, 1.7, 0.16, 1.05)
fence = [(-1.6, 0.6), (-1.6, -0.8), (-1.6, -1.9), (-0.7, -1.9)], [(0.7, -1.9), (1.6, -1.9), (1.6, -0.8), (1.6, 0.6)]
for side in fence:
    for (ax, ay) in side: G.box("steel", mx + ax, my + ay, z + 0.12, 0.07, 0.07, 0.75)
    for (ax, ay), (bx_, by_) in zip(side, side[1:]):
        tube("steel", (mx + ax, my + ay, z + 0.75), (mx + bx_, my + by_, z + 0.75), 0.012, 4)
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
    PATH_PTS.extend(dense)
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
# uv_box() comes from scene_lib.py

STEP = 6.0
E0, E1, N0, N1 = -300.0, 246.0, -204.0, 204.0
ne = int((E1 - E0) / STEP) + 1; nn = int((N1 - N0) / STEP) + 1
TB = bmesh.new(); grid = []
for j in range(nn):
    row = []
    for i in range(ne):
        e = E0 + i * STEP; n = N0 + j * STEP; row.append(TB.verts.new((e, n, h(e, n))))
    grid.append(row)
for j in range(nn - 1):
    for i in range(ne - 1): TB.faces.new([grid[j][i], grid[j][i + 1], grid[j + 1][i + 1], grid[j + 1][i]])
# A 6 m grid is too coarse for the 8 m carve band under a diagonal tunnel: a face whose corners straddle the band
# interpolates back up through the tunnel floor (seen in tunnel 29, building-detail pass). Refine the grid to 1.5 m
# around every tunnel and re-sample the height so the carve follows the tunnel.
def _near_tunnel(x, y, pad):
    for (tx, ty, ta, tl, tz) in TUNNELS:
        u = (x - tx) * math.cos(ta) + (y - ty) * math.sin(ta); v = abs(-(x - tx) * math.sin(ta) + (y - ty) * math.cos(ta))
        if -1.0 - pad < u < tl + pad and v < 4.0 + pad: return True
    return False
_edges = {ed for f in TB.faces if _near_tunnel(*f.calc_center_median()[:2], STEP) for ed in f.edges}
bmesh.ops.subdivide_edges(TB, edges=list(_edges), cuts=3, use_grid_fill=True)
for _v in TB.verts:
    if _near_tunnel(_v.co.x, _v.co.y, 2 * STEP): _v.co.z = h(_v.co.x, _v.co.y)
# sunken pill boxes (CARVES): refine the grid to about 0.5 m around them, so the carve follows the walls and the trench
def _near_carve(x, y, r):
    return any((x - c[0]) ** 2 + (y - c[1]) ** 2 < r * r for c in CARVES)
for _r, _cuts in ((10.0, 3), (7.0, 2)):
    _edges = {ed for f in TB.faces if _near_carve(*f.calc_center_median()[:2], _r) for ed in f.edges}
    if _edges: bmesh.ops.subdivide_edges(TB, edges=list(_edges), cuts=_cuts, use_grid_fill=True)
for _v in TB.verts:
    if _near_carve(_v.co.x, _v.co.y, 12.0): _v.co.z = h(_v.co.x, _v.co.y)
TB.normal_update()

# paths on top of the terrain: the white paths of the reeaki map (skeleton, extract_reeaki.py), minus stretches that
# run through a building (the map's white roofs), plus the covered spine from the ticket building to point 3
def _split_free(line):
    dense = []
    for a, b in zip(line, line[1:]):
        L = math.hypot(b[0] - a[0], b[1] - a[1]); k = max(1, int(L / 1.5))
        dense += [(a[0] + (b[0] - a[0]) * i / k, a[1] + (b[1] - a[1]) * i / k) for i in range(k)]
    dense.append(line[-1]); out, cur = [], []
    for q in dense:
        if _in_fp(*q): 
            if len(cur) > 1: out.append(cur)
            cur = []
        else: cur.append(q)
    if len(cur) > 1: out.append(cur)
    return [c for c in out if math.hypot(c[-1][0] - c[0][0], c[-1][1] - c[0][1]) > 3.0 or len(c) > 4]
ribbon([TICKET, E(3)], 3.0, "soil", 0.06, PATH_BM)
for ln in MAP_PATHS:
    for part in _split_free(ln): ribbon(part, 2.6, "soil", 0.06, PATH_BM)
# roads of the map (traced by hand in extract_reeaki.py), 6 m asphalt
for ln in MAP_ROADS: ribbon(ln, 6.0, "asphalt", 0.07, ROAD_BM)

# ---------------------------------------------------------------- write objects
def _macro(x, y):
    return 0.5 + 0.5 * (0.5 * math.sin(x * 0.031 + 1.7) * math.cos(y * 0.027) + 0.3 * math.sin(x * 0.083 + y * 0.071) + 0.2 * math.sin(x * 0.19 - y * 0.17 + 2.0))

WALL_KEYS = {"conc", "conc_g", "conc_w", "plaster", "camo", "brick", "redbrick", "rock"}

def paint(bm, kind):
    """Vertex colours (exported as COLOR_0 and multiplied with the textures): macro variation and shading on the terrain,
    dirt and damp staining low on walls. This breaks up texture repetition at almost no cost."""
    lay = bm.loops.layers.float_color.new("Col")
    pts = [(n[1], n[2]) for n in NODES]
    path_pts = PATH_PTS[::3]
    cache = {}
    def terrain_col(v):
        x, y, z = v.co
        m1 = _macro(x, y); m2 = _macro(x * 1.7 + 40, y * 1.7 - 25)
        k = 0.70 + 0.55 * m1
        steep = max(0.0, min(1.0, (0.93 - v.normal.z) / 0.25))
        r, g, b = k * (0.97 + 0.10 * (1 - m2)), k * (0.90 + 0.20 * m2), k * 0.95
        r, g, b = r * (1 - 0.22 * steep), g * (1 - 0.30 * steep), b * (1 - 0.35 * steep)
        dmin = min([math.hypot(x - px, y - py) for (px, py) in pts] + [99.0])
        ao = 1.0 - 0.38 * (1.0 - smooth(dmin / 9.0))
        dp = min([math.hypot(x - px, y - py) for (px, py) in path_pts] + [99.0])
        scuff = 1.0 - 0.28 * (1.0 - smooth(dp / 3.5))
        return (r * ao * scuff, g * ao * scuff, b * ao * scuff, 1.0)
    for f in bm.faces:
        for lp in f.loops:
            v = lp.vert; x, y, z = v.co
            if kind == "terrain":
                if v.index not in cache: cache[v.index] = terrain_col(v)
                lp[lay] = cache[v.index]
            elif kind == "struct":
                gh = h_base(x, y); fz = max(0.0, min(1.0, (z - gh) / 1.7))
                jit = 0.94 + 0.12 * ((math.sin(x * 12.9898 + y * 78.233 + z * 37.719) * 43758.5453) % 1.0)
                base = (0.50 + 0.50 * fz) * jit
                lp[lay] = (base * 0.98, base, base * 0.96, 1.0)

def to_obj(bm, name, matkey, tile=3.0, kind=None):
    bm.normal_update(); bm.verts.index_update(); uv_box(bm, TILE.get(matkey, tile))
    if kind: paint(bm, kind)
    me = bpy.data.meshes.new(name + "_mesh"); bm.to_mesh(me); bm.free()
    me.materials.append(MATS[matkey]); ob = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(ob)
    for p in me.polygons: p.use_smooth = False
    return ob

to_obj(TB, "ground_terrain", "ground", kind="terrain")
to_obj(PATH_BM, "floor_paths", "soil")
to_obj(ROAD_BM, "floor_road", "asphalt")
for key, bm in G.bm.items():
    nm = ("floor_" if key in FLOOR_MATS else "struct_") + key
    to_obj(bm, nm, key, kind="struct" if key in WALL_KEYS else None)
# the user's Blender models (pill boxes, entrance), placed by pillbox() and the entrance block above
exec(open(ROOT + "/blender/scripts/user_models.py").read(), globals())

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
sp.location = (gx + 5.0, gy, h(gx + 5.0, gy) + 0.1); sp.rotation_euler = (0, 0, math.radians(180)); bpy.context.scene.collection.objects.link(sp)   # outside the entrance gate, facing west through it

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
    "escape-route": ESC_MOUTH,   # the mouth of the crawl at the inner end of tunnel 29 (the crawl is 1 m high)
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
bpy.context.scene["layout_rot"] = LAYOUT_ROT      # read by place_props.py
os.makedirs(ROOT + "/blender/out", exist_ok=True)
json.dump(FIXTURES, open(ROOT + "/blender/out/fixtures.json", "w"))
print("objects:", len(bpy.data.objects), "pads:", len(PADS), "escape climb m:", round(climb, 1), "terrain z range:", round(min(v.co.z for v in bpy.data.objects["ground_terrain"].data.vertices), 1), round(max(v.co.z for v in bpy.data.objects["ground_terrain"].data.vertices), 1))
