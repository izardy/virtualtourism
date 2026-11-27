"""Turn the reeaki "Fort Relics" visitor map into layout data for build_muzium.py (strict sitemap layout, 2026-11-27).

Source image: https://i0.wp.com/reeaki.com/wp-content/uploads/2021/03/photo_2021-03-24_12-51-55.jpg (1242x577), kept
private in reference/inbox/reeaki_map.jpg (git-ignored). Run with any Python that has numpy, Pillow, scipy and
scikit-image (not Blender):   python blender/scripts/extract_reeaki.py
Writes reference/sitemap/reeaki_layout.json (derived numbers only) and reference/sitemap/reeaki_preview.png (git-ignored).

Frame: the same map frame as site_layout.json (origin = Information & Ticketing, X = "east_m", Y = "north_m", image-up
= -Y). Pixel -> metres is the affine transform that best fits the 37 numbered markers of this map onto their positions
on the museum's own 2048 px map (site_layout.json), then re-anchored on this map's ticketing building. So every position,
road, path, hill and coast line below comes from the reeaki map; the older map only fixes the overall scale.
"""
import json, math, os
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
from skimage.morphology import skeletonize

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
IMG = ROOT + "/reference/inbox/reeaki_map.jpg"
OUT = ROOT + "/reference/sitemap/reeaki_layout.json"

# ---- numbered markers, read by eye from 3x zoom crops with a 20 px grid (+/- 2 px)
MARKERS = {1: (1067, 277), 2: (601, 466), 3: (753, 187), 4: (784, 168), 5: (791, 125), 6: (847, 113), 7: (826, 134),
           8: (818, 188), 9: (826, 232), 10: (826, 286), 11: (876, 181), 12: (926, 245), 13: (1030, 225), 14: (1048, 185),
           15: (983, 206), 16: (1002, 181), 17: (1012, 133), 18: (963, 88), 19: (935, 146), 20: (908, 163), 21: (901, 108),
           22: (877, 115), 23: (831, 87), 24: (799, 86), 25: (708, 99), 26: (578, 113), 27: (616, 101), 28: (537, 135),
           29: (703, 138), 30: (744, 108), 31: (585, 71), 32: (887, 74), 33: (752, 69), 34: (787, 153), 35: (860, 93),
           36: (668, 185), 37: (595, 98)}
# where the structure itself is drawn, when it is not under the marker (the marker sits beside the drawing)
DRAWN = {12: (947, 262), 17: (1005, 143), 18: (980, 112), 1: (1055, 289), 2: (602, 482), 31: (585, 82)}
# facilities and coast items (red dots / icons on the map)
FAC = {"Information & Ticketing": (740, 275), "Souvenir shop": (758, 242), "Cafeteria": (617, 270),
       "Toilets 36": (693, 177), "Toilets 17": (1038, 158), "Toilets 10": (823, 312),
       "Car Park": (522, 362), "VIP Car Park": (700, 312), "War Game Park": (950, 52),
       "Barbed wire (coast)": (473, 111), "Well (coast)": (454, 131),
       "Pill Box (coast) A": (449, 149), "Pill Box (coast) B": (522, 171), "Pill Box (coast) C": (476, 217), "Pill Box (coast) D": (411, 249),
       "Submarine Landing Bay": (430, 172), "Jetty": (422, 308), "Maritime Museum": (473, 302), "Generator Room (coast)": (492, 333),
       "Water Tank (coast)": (504, 425), "Water Tank (road)": (1086, 337), "War Museum signboard": (1141, 296)}
# long axis of the drawn buildings (two pixels along the ridge); others are drawn square to the image
AXES = {12: ((880, 250), (1010, 278)), 7: ((820, 152), (862, 148)), 21: ((890, 137), (930, 117)), 22: ((862, 128), (898, 112)),
        19: ((913, 150), (947, 130)), 20: ((893, 168), (925, 150)), 15: ((962, 210), (985, 190)), 16: ((985, 186), (1003, 166)),
        13: ((1028, 228), (1040, 205)), 14: ((1040, 195), (1050, 172)), 17: ((985, 143), (1022, 143)), 18: ((948, 112), (1010, 112))}
# pixel boxes to drop from the road mask: icons, labels on land, white roofs (x0, y0, x1, y1)
NOT_ROAD = [(680, 164, 707, 192), (1024, 144, 1052, 172), (808, 298, 838, 328), (598, 230, 638, 266), (585, 258, 648, 298),
            (760, 258, 786, 282), (718, 248, 768, 302), (878, 230, 1016, 294), (982, 124, 1026, 154), (944, 98, 1014, 128),
            (1080, 264, 1204, 328), (1044, 278, 1082, 300), (584, 470, 622, 492), (1093, 325, 1176, 347), (688, 312, 742, 336),
            (516, 344, 554, 362), (472, 282, 532, 312), (460, 163, 520, 180), (480, 210, 538, 226), (428, 322, 494, 350),
            (1015, 396, 1148, 416), (740, 220, 780, 262)]

im = np.asarray(Image.open(IMG).convert("RGB")).astype(float)
H_, W_ = im.shape[:2]
r, g, b = im[..., 0], im[..., 1], im[..., 2]
mx, mn = im.max(-1), im.min(-1)
sea_px = (b > r + 35) & (b > g - 5)
bg_px = (r > 190) & (g > 170) & (b < 170) & (r - b > 40)
green_px = (g > r + 5) & (g > b + 5) & ~bg_px
white_px = (mn > 165) & (mx - mn < 40)
YY, XX = np.mgrid[:H_, :W_]

# ---- pixel -> metres
SITE = json.load(open(ROOT + "/reference/sitemap/site_layout.json"))
OLD = {p["n"]: (p["east_m"], p["north_m"]) for p in SITE["numbered"]}
A_ = np.array([[x, y, 1.0] for n, (x, y) in sorted(MARKERS.items())]); B_ = np.array([OLD[n] for n in sorted(MARKERS)])
M, *_ = np.linalg.lstsq(A_, B_, rcond=None)                     # 3x2
res = A_ @ M - B_
t0 = np.array([*FAC["Information & Ticketing"], 1.0]) @ M
M[2] -= t0                                                       # ticketing -> (0, 0)
LIN = M[:2]                                                      # rows: d/dx, d/dy
def P(x, y): v = np.array([x, y, 1.0]) @ M; return float(v[0]), float(v[1])
def ang_px(a, b_):
    d = np.array(b_, float) - np.array(a, float); v = d @ LIN; return float(math.atan2(v[1], v[0]))
INV = np.linalg.inv(np.vstack([M.T, [0, 0, 1]]))                # metres -> px
print("affine m/px:", np.round(LIN, 3).tolist(), "fit residual m: mean", round(float(np.hypot(*res.T).mean()), 1), "max", round(float(np.hypot(*res.T).max()), 1))

# ---- pixel masks
land_px = ndi.binary_fill_holes(ndi.binary_closing(green_px | white_px, iterations=3)) & (YY < 532)
lab, n = ndi.label(land_px); sizes = ndi.sum(land_px, lab, range(1, n + 1)); land_px = lab == (1 + int(np.argmax(sizes)))
land_px = ndi.binary_fill_holes(land_px)
hill_px = ndi.binary_fill_holes(ndi.binary_closing(land_px, iterations=6)) & (YY < 532)
# the far crest of the plateau is the drawing's top edge: the hill goes on behind it, so extend it 40 px up there
top = np.full(W_, -1)
cols = np.where(hill_px.any(0))[0]
for x in cols: top[x] = int(np.argmax(hill_px[:, x]))
for x in cols:
    if 500 < x < 1150 and top[x] < 200: hill_px[max(0, top[x] - 110):top[x], x] = True
# shore: the map's coast items (red dots) sit on a thin strip of beach just outside the drawn green
_d_land = ndi.distance_transform_edt(~land_px)
shore_px = ~land_px & ~sea_px & (_d_land < 16) & (XX < 620)
# sea: blue water plus everything west (image-left) of the land, as on the map
west = np.full(H_, W_)
rows = np.where(land_px.any(1))[0]
for y in rows: west[y] = int(np.argmax(land_px[y]))
for y in range(H_):
    if west[y] == W_: west[y] = west[rows[np.argmin(np.abs(rows - y))]]
sea_full = ((sea_px & (XX < 560)) | (~land_px & (XX < west[:, None]) & (XX < 560))) & ~shore_px
# the white sand bar in the bay (with the jetty, the ship and a pill box on it) is land on the map
_sb = white_px & ~land_px & (XX > 380) & (XX < 520) & (YY > 225) & (YY < 320)
_lab, _n = ndi.label(_sb); _szs = ndi.sum(_sb, _lab, range(1, _n + 1))
SANDBAR_px = np.isin(_lab, 1 + np.where(_szs >= 150)[0])
sea_full &= ~SANDBAR_px

# ---- metric grids (2 m) over the map
STEP = 2.0
corners = [P(0, 0), P(W_, 0), P(0, H_), P(W_, H_)]
E0 = math.floor(min(c[0] for c in corners) / 10) * 10 - 40; E1 = math.ceil(max(c[0] for c in corners) / 10) * 10 + 40
N0 = math.floor(min(c[1] for c in corners) / 10) * 10 - 40; N1 = math.ceil(max(c[1] for c in corners) / 10) * 10 + 40
es = np.arange(E0, E1 + 1e-6, STEP); ns = np.arange(N0, N1 + 1e-6, STEP)
EE, NN = np.meshgrid(es, ns)
PX = INV[0, 0] * EE + INV[0, 1] * NN + INV[0, 2]; PY = INV[1, 0] * EE + INV[1, 1] * NN + INV[1, 2]
inside = (PX >= 0) & (PX < W_) & (PY >= 0) & (PY < H_)
ix = np.clip(PX.astype(int), 0, W_ - 1); iy = np.clip(PY.astype(int), 0, H_ - 1)
def S(mask_px, outside=False): m_ = mask_px[iy, ix]; m_[~inside] = outside; return m_
hill = ndi.binary_fill_holes(S(hill_px) | (~inside & (PY < 0) & (PY > -110) & (PX > 500) & (PX < 1150))); land = S(land_px)
# the plateau rim above the drawn buildings has dark icons and outlines that are neither green nor white: close them
hill = ndi.binary_fill_holes(ndi.binary_closing(hill, iterations=6, border_value=1))
sea = S(sea_full) | (~inside & (PX < 420) & ~land)
_landm = ndi.binary_opening(~sea, iterations=2, border_value=1)    # removes thin slivers of land in the water
sea = ~_landm
_lab, _nl = ndi.label(~sea)                                       # drop specks of land; the main land and the sand bar stay
if _nl > 1:
    _sz = ndi.sum(~sea, _lab, range(1, _nl + 1)); sea = ~np.isin(_lab, 1 + np.where(_sz >= 150)[0])
# ---- heights (model units, ticketing = 0, sea level -36 as before)
SEA_Z, Z_LOW = -36.0, -24.0
s = ndi.distance_transform_edt(hill) * STEP - ndi.distance_transform_edt(~hill) * STEP
f = np.clip((s + 10.0) / 70.0, 0, 1); f = f * f * (3 - 2 * f)
f = ndi.gaussian_filter(f, 3.0)
tx, ty = int(round((0 - E0) / STEP)), int(round((0 - N0) / STEP))
Z_TOP = 2.0
z = Z_LOW + (Z_TOP - Z_LOW) * f
# summit: the observation post (24) and the gun bays stand on the highest ground of the fort; the plateau falls gently
# from there towards the entrance and the barracks
_se, _sn = P(*MARKERS[24]); _se2, _sn2 = P(*MARKERS[30])
dsum = np.hypot(EE - (_se + _se2) / 2, NN - (_sn + _sn2) / 2)
z += 9.0 * np.exp(-(dsum / 85.0) ** 2) * f
z -= z[ty, tx]                                                 # ticketing = 0 (before the coast, so sea level stays at SEA_Z)
dsea = ndi.distance_transform_edt(~sea) * STEP
wc = np.clip((dsea - 4.0) / 22.0, 0, 1); wc = wc * wc * (3 - 2 * wc)
z = (SEA_Z + 1.2) + (z - (SEA_Z + 1.2)) * wc                  # a beach about 1 m above the water along the shore
z[sea] = SEA_Z - 3.0
z = ndi.gaussian_filter(z, 1.5)
z = np.where(~sea, np.maximum(z, SEA_Z + 0.8), z)                # narrow land (the sand bar) must stay above the water after smoothing
z -= z[ty, tx]                                                 # smoothing moved the ticket cell by a few cm
# coast items (red dots): the map draws them a few metres off its own shoreline. Each one moves to the nearest land and
# then inland until it is 5 m from the water, on a beach shelf just above sea level. The jetty stays on the water and
# keeps the shore point it starts from.
COASTAL = [k for k in FAC if any(w_ in k for w_ in ("coast", "Submarine", "Maritime", "Jetty"))]
def _drop_islands(z):
    lab_, n_ = ndi.label(z > SEA_Z)
    if n_ > 1:
        sz_ = ndi.sum(z > SEA_Z, lab_, range(1, n_ + 1)); z = np.where((lab_ > 0) & ~np.isin(lab_, 1 + np.where(sz_ >= 120)[0]), SEA_Z - 3.0, z)
    return z
z = _drop_islands(z)
sea = z <= SEA_Z
_dsea = ndi.distance_transform_edt(~sea) * STEP
_, _near = ndi.distance_transform_edt(sea, return_indices=True)
FACM = {k: P(*v) for k, v in FAC.items()}; SHORE = {}
def _cell(e_, n_): return int(round((n_ - N0) / STEP)), int(round((e_ - E0) / STEP))
for _k in COASTAL:
    _e, _n = FACM[_k]; j, i = _cell(_e, _n)
    if sea[j, i]: j, i = int(_near[0][j, i]), int(_near[1][j, i])
    SHORE[_k] = (float(es[i]), float(ns[j]))
    if _k == "Jetty": continue
    for _ in range(12):                                          # climb the distance-to-sea field
        if _dsea[j, i] >= 5.0: break
        nb_ = [(j + dj, i + di) for dj in (-1, 0, 1) for di in (-1, 0, 1)]
        j, i = max(nb_, key=lambda q: _dsea[q])
    FACM[_k] = (float(es[i]), float(ns[j]))
    _d = np.hypot(EE - FACM[_k][0], NN - FACM[_k][1])
    _w = np.clip(1 - (_d - 5.0) / 6.0, 0, 1); _w = _w * _w * (3 - 2 * _w)
    _zs = SEA_Z + 1.4
    z = np.where(z < _zs, z * (1 - _w) + _zs * _w, z)
z = _drop_islands(z)
print("height grid", z.shape, "range", round(float(z.min()), 1), round(float(z.max()), 1))

# ---- ground cover classes (for trees): 0 sea/background, 1 lawn (light green), 2 forest floor (dark green), 3 road
L_ = im.mean(-1); mloc = ndi.uniform_filter(L_, 9)
dark_px = green_px & (g < 118) & land_px
cover = np.zeros(EE.shape, np.uint8)
cover[land & ~sea] = 1
cover[S(ndi.binary_opening(dark_px, iterations=2)) & land] = 2

# ---- roads and paths: skeleton of the white areas on land (1 m grid for the skeleton)
road_px = (mn > 140) & (mx - mn < 50) & land_px & (YY < 528)
# the drawing has a pale glow along the hill's outline at the top and the right: not a road
_out_d = ndi.distance_transform_edt(land_px)
road_px &= ~((_out_d < 9) & ((YY < 330) | ((XX > 1180) & (YY < 380))))
for (x0, y0, x1, y1) in NOT_ROAD: road_px[y0:y1, x0:x1] = False
RS = 1.0
es1 = np.arange(E0, E1 + 1e-6, RS); ns1 = np.arange(N0, N1 + 1e-6, RS); E1g, N1g = np.meshgrid(es1, ns1)
PX1 = INV[0, 0] * E1g + INV[0, 1] * N1g + INV[0, 2]; PY1 = INV[1, 0] * E1g + INV[1, 1] * N1g + INV[1, 2]
in1 = (PX1 >= 0) & (PX1 < W_) & (PY1 >= 0) & (PY1 < H_)
rm = road_px[np.clip(PY1.astype(int), 0, H_ - 1), np.clip(PX1.astype(int), 0, W_ - 1)] & in1
rm = ndi.binary_closing(rm, iterations=1)
lab, n = ndi.label(rm); sizes = ndi.sum(rm, lab, range(1, n + 1))
rm = np.isin(lab, 1 + np.where(sizes >= 150)[0])
dist = ndi.distance_transform_edt(rm) * RS
sk = skeletonize(rm)
# graph tracing
pts = set(zip(*np.where(sk)))
def nb(p): return [(p[0] + dy, p[1] + dx) for dy in (-1, 0, 1) for dx in (-1, 0, 1) if (dy or dx) and (p[0] + dy, p[1] + dx) in pts]
deg = {p: len(nb(p)) for p in pts}
nodes = {p for p, d in deg.items() if d != 2}
seen = set(); edges = []
for nd in nodes:
    for q in nb(nd):
        if (nd, q) in seen: continue
        path = [nd, q]; seen.add((nd, q)); seen.add((q, nd)); prev, cur = nd, q
        while cur not in nodes:
            nxt = [w for w in nb(cur) if w != prev and w not in path[-3:]]
            if not nxt: break
            prev, cur = cur, nxt[0]; seen.add((prev, cur)); seen.add((cur, prev)); path.append(cur)
        edges.append(path)
loops = pts - {p for e in edges for p in e}           # closed loops without a junction
def plen(pth): return sum(math.hypot(a[0] - b_[0], a[1] - b_[1]) for a, b_ in zip(pth, pth[1:])) * RS
# prune spurs: edges with a free end shorter than 12 m (repeat twice)
for _ in range(2):
    cnt = {}
    for e in edges:
        for p in (e[0], e[-1]): cnt[p] = cnt.get(p, 0) + 1
    edges = [e for e in edges if not ((cnt[e[0]] == 1 or cnt[e[-1]] == 1) and plen(e) < 12.0)]
def rdp(pp, eps):
    if len(pp) < 3: return pp
    a, b_ = np.array(pp[0], float), np.array(pp[-1], float); d = b_ - a; L = np.hypot(*d) or 1.0
    ds = [abs(d[0] * (p[1] - a[1]) - d[1] * (p[0] - a[0])) / L for p in pp[1:-1]]
    i = int(np.argmax(ds)) + 1
    if ds[i - 1] > eps: return rdp(pp[:i + 1], eps)[:-1] + rdp(pp[i:], eps)
    return [pp[0], pp[-1]]
ROADS = []
core_px = ndi.binary_erosion(hill_px, iterations=5)
for e in edges:
    if plen(e) < 6.0: continue
    wmed = float(np.median([dist[q] for q in e])) * 2.0
    if wmed >= 7.5: continue                                     # wide roads are traced by hand below
    mid = e[len(e) // 2]
    pv_ = INV @ np.array([es1[mid[1]], ns1[mid[0]], 1.0])
    if not core_px[int(np.clip(pv_[1], 0, H_ - 1)), int(np.clip(pv_[0], 0, W_ - 1))]: continue   # paths are on the hill only
    simp = rdp(e, 1.2)
    line = []
    for (yy, xx) in simp:
        k_ = e.index((yy, xx)); w = float(np.median([dist[q] for q in e[max(0, k_ - 3):k_ + 4]])) * 2.0
        line.append([round(float(es1[xx]), 2), round(float(ns1[yy]), 2), round(w, 2)])
    ROADS.append({"kind": "path", "map_width_m": round(wmed, 1), "pts": line})
# wide roads: centre lines traced by eye on 2-3x zoom crops (the map draws them 15-25 m wide; built at 6 m)
ROADS_HAND = {
    "To War Museum (upper road)": [(1242, 318), (1160, 345), (1100, 352), (1040, 332), (1000, 322), (950, 335), (910, 360), (860, 400), (810, 425), (760, 442), (700, 462), (650, 478), (600, 492)],
    "Jln Permatang Damar Laut": [(1242, 372), (1110, 430), (1010, 452), (910, 480), (810, 505), (740, 522), (600, 492), (560, 505), (520, 515)],
    "Car park road": [(600, 492), (565, 448), (583, 416), (558, 387), (522, 369), (547, 319), (579, 301), (610, 290)],
    "VIP car park road": [(583, 416), (625, 400), (668, 350), (700, 312), (722, 290)],
    "Coast road": [(522, 369), (490, 372), (460, 385), (430, 400)],
}
for nm_, pp in ROADS_HAND.items():
    ROADS.append({"kind": "road", "name": nm_, "map_width_m": 6.0, "pts": [[round(P(x, y)[0], 2), round(P(x, y)[1], 2), 6.0] for x, y in pp]})
print("road/path polylines:", len(ROADS), "roads", sum(1 for r_ in ROADS if r_["kind"] == "road"), "loops left out px:", len(loops))

# ---- trees: textured light-green canopies
sd = np.sqrt(np.maximum(ndi.uniform_filter(L_ * L_, 9) - mloc * mloc, 0))
light = (g > 115) & (g > r + 15) & (g > b + 40) & (r > 60)
tex = ndi.binary_closing(ndi.binary_opening(light & (sd > 16), iterations=2), iterations=3)
lab, n = ndi.label(tex); TREES = []
for i, sl in enumerate(ndi.find_objects(lab)):
    m_ = lab[sl] == i + 1; a = int(m_.sum())
    if a < 60: continue
    cy, cx = ndi.center_of_mass(m_); cy += sl[0].start; cx += sl[1].start
    if not land_px[int(cy), int(cx)] or road_px[int(cy), int(cx)]: continue
    e_, n_ = P(cx, cy); TREES.append([round(e_, 1), round(n_, 1), max(1, round(a / 380))])
print("map trees:", len(TREES))

out = {
    "source": "reeaki.com 'Fort Relics' visitor map (photo_2021-03-24_12-51-55.jpg, 1242x577); private copy reference/inbox/reeaki_map.jpg",
    "frame": "metres, origin = Information & Ticketing on this map, X = east_m, Y = north_m of site_layout.json (map frame, image-up = -Y)",
    "affine_px_to_m": [[round(float(v), 6) for v in row] for row in M.tolist()],
    "fit_residual_m": {"mean": round(float(np.hypot(*res.T).mean()), 1), "max": round(float(np.hypot(*res.T).max()), 1)},
    "points": {str(n_): {"px": list(MARKERS[n_]), "drawn_px": list(DRAWN.get(n_, MARKERS[n_])),
                         "east_m": round(P(*DRAWN.get(n_, MARKERS[n_]))[0], 2), "north_m": round(P(*DRAWN.get(n_, MARKERS[n_]))[1], 2),
                         "rot": round(ang_px(*AXES[n_]), 4) if n_ in AXES else round(ang_px((0, 0), (1, 0)), 4)} for n_ in sorted(MARKERS)},
    "facilities": {k: dict({"px": list(v), "east_m": round(FACM[k][0], 2), "north_m": round(FACM[k][1], 2),
                            "map_east_m": round(P(*v)[0], 2), "map_north_m": round(P(*v)[1], 2)},
                           **({"shore_east_m": round(SHORE[k][0], 2), "shore_north_m": round(SHORE[k][1], 2)} if k in SHORE else {})) for k, v in FAC.items()},
    "image_x_rot": round(ang_px((0, 0), (1, 0)), 4),
    "height": {"e0": float(E0), "n0": float(N0), "step": STEP, "ne": int(len(es)), "nn": int(len(ns)), "sea_z": SEA_Z,
               "z": [round(float(v), 2) for v in z.ravel()], "cover": [int(v) for v in cover.ravel()]},
    "roads": ROADS,
    "trees": TREES,
}
json.dump(out, open(OUT, "w"), separators=(",", ":"))
print("wrote", OUT, round(os.path.getsize(OUT) / 1e6, 2), "MB; extent E", E0, E1, "N", N0, N1)

# ---- preview (private: derived from the map artwork)
sc = 2.0
pv = Image.new("RGB", (int(len(es) * STEP * sc / 2), int(len(ns) * STEP * sc / 2)))
zn = (z - z.min()) / (z.max() - z.min())
rgb = np.stack([zn * 120 + 40, zn * 150 + 60, zn * 80 + 30], -1)
rgb[sea] = [30, 60, 160]; rgb[cover == 2] *= 0.75
pv = Image.fromarray(rgb.astype(np.uint8)).resize((len(es) * 2, len(ns) * 2), Image.NEAREST); d = ImageDraw.Draw(pv)
def Q(e_, n_): return ((e_ - E0) / STEP * 2, (n_ - N0) / STEP * 2)
for r_ in ROADS:
    d.line([Q(p[0], p[1]) for p in r_["pts"]], fill=(240, 240, 240) if r_["kind"] == "road" else (230, 160, 90), width=4 if r_["kind"] == "road" else 2)
for t_ in TREES: x_, y_ = Q(t_[0], t_[1]); d.ellipse([x_ - 3, y_ - 3, x_ + 3, y_ + 3], fill=(0, 90, 0))
for k, v in out["points"].items(): x_, y_ = Q(v["east_m"], v["north_m"]); d.ellipse([x_ - 4, y_ - 4, x_ + 4, y_ + 4], fill=(220, 30, 30)); d.text((x_ + 5, y_ - 5), k, fill=(255, 255, 0))
for k, v in out["facilities"].items(): x_, y_ = Q(v["east_m"], v["north_m"]); d.rectangle([x_ - 3, y_ - 3, x_ + 3, y_ + 3], fill=(0, 200, 255)); d.text((x_ + 5, y_ - 5), k[:14], fill=(0, 255, 255))
pv.save(ROOT + "/reference/sitemap/reeaki_preview.png")

# ---- check overlay on the map itself (private)
ov_ = Image.open(IMG).convert("RGB").resize((W_ * 2, H_ * 2)); d = ImageDraw.Draw(ov_)
def QP(e_, n_): v = INV @ np.array([e_, n_, 1.0]); return (v[0] * 2, v[1] * 2)
for r_ in ROADS:
    d.line([QP(p[0], p[1]) for p in r_["pts"]], fill=(0, 0, 255) if r_["kind"] == "road" else (255, 0, 255), width=3)
for t_ in TREES: x_, y_ = QP(t_[0], t_[1]); d.ellipse([x_ - 5, y_ - 5, x_ + 5, y_ + 5], outline=(255, 255, 0), width=2)
ov_.save(ROOT + "/reference/sitemap/reeaki_check.jpg", quality=85)
