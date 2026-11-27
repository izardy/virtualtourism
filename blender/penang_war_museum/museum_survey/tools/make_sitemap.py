import base64, json, math, os, csv, sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)
SS = os.path.join(OUT, "screenshots")
O_LAT, O_LON = 5.281400, 100.288800
KE, KN = 110847.0, 110574.0

def enu(lat, lon): return ((lon - O_LON) * KE, (lat - O_LAT) * KN)
def ll(E, N): return (O_LAT + N / KN, O_LON + E / KE)

T = json.load(open(os.path.join(HERE, "transform.json")))
ar, ai = T["a"]; br, bi = T["b"]
def sk(x, y):  # sketch pixel -> ENU
    return (ar * x + ai * y + br, ai * x - ar * y + bi)

# ---------------- map frame
EMIN, EMAX, NMIN, NMAX = -170.0, 230.0, -290.0, 110.0
K = 4.3                      # svg px per metre
W, H = (EMAX - EMIN) * K, (NMAX - NMIN) * K
PANEL = 0                    # legend drawn inside the map (empty forest, bottom-left)
def X(E): return (E - EMIN) * K
def Y(N): return (NMAX - N) * K

def b64(path, mime="image/jpeg"):
    return f"data:{mime};base64," + base64.b64encode(open(path, "rb").read()).decode()

# georeferenced satellite screenshots: (file, centre lat, centre lon, metres per screen px, clip box in screen px)
SATS = [("SAT07_context_912m_center_5.2805_100.289.jpg", 5.2805, 100.2890, 0.2667 * 912 / 166, (60, 140, 800, 560)),
        ("SAT01_site_overview_228m.jpg", 5.2809, 100.2893, 0.2667 * 228 / 166, (60, 60, 800, 560))]

# ---------------- surveyed structures (ENU centre, size along E, size along N, rotation deg CCW, kind)
S = [
 ("B01", "Main gate (log-letter WAR MUSEUM, 2013) / block letters (2024)", 0.0, 0.5, 23, 3, 0, "rect", "SV 2013+2024", "±3 m"),
 ("B02", "Gate passage (lattice-truss roof)", 1.0, -5.0, 4.6, 9.5, 0, "rect", "SV 2013", "±3 m"),
 ("B03", "Ticket counter / museum office", -4.0, -18.0, 5, 17, 0, "rect", "SV 2013", "±4 m"),
 ("B04", "Camouflage kiosk (WARMUSEUM plaque)", 12.0, -19.0, 5.4, 3.6, -40, "rect", "SV 2013 + PS 2016", "±5 m"),
 ("B05", "Timber watchtower", 15.0, -12.5, 3, 3, 0, "rect", "PS 2016", "±5 m"),
 ("B06", "Signboard, soldier statue, MALAYA Border Check Point", 14.0, -22.0, 2, 1, -30, "rect", "SV 2013 + PS 2016", "±5 m"),
 ("B07", "Rest area + souvenir/cafe (teal, TIPPNA)", 4.6, -24.3, 10, 5, 0, "rect", "SV 2013", "±4 m"),
 ("B08", "Toilet block (camouflage doors)", 10.0, -31.0, 8, 4, -35, "rect", "SV 2013", "±4 m"),
 ("B10", "Site-map board on walkway", 32.5, -55.0, 2.5, 0.4, -35, "rect", "SV 2013", "±3 m"),
 ("B12", "Vaulted concrete bunker (ammunition store)", 56.5, -71.3, 5, 6, -35, "rect", "SV 2013", "±4 m"),
 ("B13", "Garden huts / miniature models", 47.0, -56.0, 2, 1.5, -35, "rect", "SV 2013", "±6 m"),
 ("B14", "SE courtyard (vine pergola, wooden fort model)", 95.0, -92.0, 20, 15, -35, "rect", "SV 2013", "±5 m"),
 ("B15", "Blue barrack building (bamboo-screened windows)", 2.0, -74.0, 12, 7, 40, "rect", "SV 2013", "±6 m"),
 ("B17", "Coastal gun emplacement (circular gun pit + magazines)", 66.6, -105.6, 9, 9, 0, "circle", "PS 2017", "±3 m"),
 ("S1", "Open clearing / former parade ground", 63.0, -56.5, 25, 25, -35, "rect", "SAT", "±4 m"),
 ("S2", "Small roofed building", 57.4, -93.1, 8, 10, -35, "rect", "SAT", "±4 m"),
 ("S3", "Small white hut", 93.1, -107.8, 3, 3, 0, "rect", "SAT", "±4 m"),
 ("S4", "Small hut (SW, in forest)", 13.5, -112.2, 4, 4, 0, "rect", "SAT", "±4 m"),
 ("S5", "Dark-roof building + grey annex (exhibition hall / cafeteria?)", 25.5, -12.5, 12, 13, 0, "rect", "SAT", "±4 m"),
 ("S6", "Brown-roof building beside SW branch", 13.5, -55.2, 15, 9, 35, "rect", "SAT", "±4 m"),
]
WALKWAY = [(12.0, -33.0), (17.9, -37.8), (26.6, -45.3), (34.7, -53.6), (43.1, -60.6), (59.3, -68.5), (70.7, -73.6), (86.6, -82.6), (91.2, -87.1)]
SV_PATH = [enu(*p) for p in [(5.2814433, 100.2887926), (5.2814104, 100.2888007), (5.281356, 100.288809), (5.2812959, 100.2888158),
                               (5.2812423, 100.2888256), (5.28118, 100.2888414), (5.2811381, 100.2888759), (5.2810579, 100.2889617),
                               (5.2809899, 100.2890402), (5.2809152, 100.2891132), (5.2808523, 100.2891885), (5.2807809, 100.2893346),
                               (5.2807341, 100.2894376), (5.2806819, 100.2895302), (5.2806531, 100.2895817), (5.2806125, 100.2896227)]]
SV_BRANCH = [(14.7, -37.9), (8.0, -52.0), (-1.1, -70.7), (-6.9, -74.7)]
PHOTOS = [("P17", 66.6, -105.6), ("P18", 11.3, -18.8)]

# ---------------- sketch-map items: (no, label, sketch px x, y, matched surveyed id or "")
SK = [
 (1, "Pill box", 940, 462, ""), (2, "Pill box", 370, 705, ""), (3, "Office & R&D", 560, 355, "B03"),
 (4, "Mortuary (JPN)", 578, 322, ""), (5, "Open air theatre", 600, 270, ""), (6, "(barrack)", 667, 262, ""),
 (7, "British other ranks 1", 648, 285, "B15"), (8, "Underground communication centre", 635, 345, ""),
 (9, "Medical infirmary, store, dressing", 648, 408, ""), (10, "British officer 1, 2, dining", 652, 478, ""),
 (11, "Intelligence room", 712, 370, ""), (12, "Cook house", 770, 422, ""), (13, "Indian other ranks 3, 3A", 870, 382, ""),
 (14, "Indian other ranks 4, 4A", 887, 333, ""), (15, "Indian other ranks 1, 1A", 808, 355, ""), (16, "Indian other ranks 2, 2A", 832, 326, ""),
 (17, "Cook house", 873, 286, ""), (18, "Malay other ranks 1, 1A", 814, 229, ""), (19, "Lock-up, cook house", 783, 296, ""),
 (20, "British other ranks 4", 748, 318, ""), (21, "British other ranks 3", 742, 247, ""), (22, "British other ranks 2", 708, 262, ""),
 (23, "Underground water tank", 655, 227, ""), (24, "Observation post", 610, 215, ""), (25, "Canon firing bay", 493, 240, "B17"),
 (26, "Tunnel", 348, 258, ""), (27, "Canon firing bay", 387, 243, ""), (28, "Well", 299, 279, ""), (29, "Tunnel", 490, 292, ""),
 (30, "Anti-aircraft pit", 548, 250, ""), (31, "Booby trap zone", 330, 172, ""), (32, "General Yamashita gallow", 720, 212, ""),
 (33, "Trench route", 553, 202, ""), (34, "Guillotine", 565, 307, ""), (35, "Armoury", 690, 240, ""), (36, "Canon", 400, 350, ""),
 (37, "Pill box", 360, 243, ""),
]
SK_NAMED = [("Information & ticketing", 545, 455, "B03"), ("Souvenir", 560, 400, "B07"), ("Cafeteria", 395, 445, "S5"),
            ("Toilet", 630, 500, "B08"), ("VIP car park", 505, 522, ""), ("Car park", 285, 560, ""),
            ("Generator room (BR) / torture chamber (JPN)", 790, 190, ""), ("Submarine landing bay", 100, 370, ""),
            ("Jetty / maritime museum", 110, 475, ""), ("Generator room (coast)", 205, 520, ""), ("Armoury (coast)", 200, 565, ""),
            ("Water tank (coast)", 220, 600, ""), ("Water tank (road)", 960, 560, ""),
            ("Pill box (coast)", 150, 310, ""), ("Pill box (coast)", 230, 325, ""), ("Pill box (coast)", 210, 395, ""), ("Pill box (coast)", 130, 425, "")]

# ================= SVG
def esc(s): return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
o = []
TW = W + PANEL
o.append(f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{TW:.0f}" height="{H:.0f}" viewBox="0 0 {TW:.0f} {H:.0f}" font-family="Helvetica, Arial, sans-serif">')
o.append(f'<rect width="{TW:.0f}" height="{H:.0f}" fill="#1d2630"/>')
o.append('<defs>')
for i, (f, la, lo, s, (cx0, cy0, cx1, cy1)) in enumerate(SATS):
    Ec, Nc = enu(la, lo)
    o.append(f'<clipPath id="c{i}"><rect x="{X(Ec + (cx0 - 400) * s):.1f}" y="{Y(Nc - (cy0 - 300) * s):.1f}" width="{(cx1 - cx0) * s * K:.1f}" height="{(cy1 - cy0) * s * K:.1f}"/></clipPath>')
o.append('<clipPath id="mapclip"><rect width="%.0f" height="%.0f"/></clipPath>' % (W, H))
o.append('<marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#ffd54a"/></marker>')
o.append('</defs><g clip-path="url(#mapclip)">')
# satellite layers
for i, (f, la, lo, s, _) in enumerate(SATS):
    Ec, Nc = enu(la, lo)
    o.append(f'<image clip-path="url(#c{i})" x="{X(Ec - 400 * s):.1f}" y="{Y(Nc + 300 * s):.1f}" width="{800 * s * K:.1f}" height="{600 * s * K:.1f}" preserveAspectRatio="none" xlink:href="{b64(os.path.join(SS, f))}"/>')
o.append(f'<rect width="{W:.0f}" height="{H:.0f}" fill="#000" opacity="0.18"/>')
# sketch overlay (optional layer, faint) - full similarity transform
A, B, C, D = K * ar, -K * ai, K * ai, K * ar
Ex, Fy = K * (br - EMIN), K * (NMAX - bi)
o.append(f'<g id="sketch-overlay" opacity="0.0"><image width="1200" height="873" transform="matrix({A:.5f},{B:.5f},{C:.5f},{D:.5f},{Ex:.2f},{Fy:.2f})" xlink:href="{b64(os.path.join(HERE, "sketch.jpg"))}"/></g>')
# grid every 20 m
for E in range(int(EMIN // 20 * 20), int(EMAX) + 1, 20):
    o.append(f'<line x1="{X(E):.1f}" y1="0" x2="{X(E):.1f}" y2="{H:.0f}" stroke="#fff" stroke-opacity="{0.35 if E % 100 == 0 else 0.12}" stroke-width="1"/>')
    if E % 40 == 0: o.append(f'<text x="{X(E) + 3:.1f}" y="{H - 6:.0f}" fill="#fff" font-size="12" opacity="0.8">E {E}</text>')
for N in range(int(NMIN // 20 * 20), int(NMAX) + 1, 20):
    o.append(f'<line x1="0" y1="{Y(N):.1f}" x2="{W:.0f}" y2="{Y(N):.1f}" stroke="#fff" stroke-opacity="{0.35 if N % 100 == 0 else 0.12}" stroke-width="1"/>')
    if N % 40 == 0: o.append(f'<text x="4" y="{Y(N) - 3:.1f}" fill="#fff" font-size="12" opacity="0.8">N {N}</text>')
# sketch-to-survey match lines
for no, lab, x, y, m in SK + [(None, l, x, y, m) for l, x, y, m in SK_NAMED]:
    if m:
        se = sk(x, y); t = next(s for s in S if s[0] == m)
        o.append(f'<line x1="{X(se[0]):.1f}" y1="{Y(se[1]):.1f}" x2="{X(t[2]):.1f}" y2="{Y(t[3]):.1f}" stroke="#ffd54a" stroke-width="1.5" stroke-dasharray="5 4" marker-end="url(#arr)"/>')
# street view paths
pts = " ".join(f"{X(e):.1f},{Y(n):.1f}" for e, n in SV_PATH)
o.append(f'<polyline points="{pts}" fill="none" stroke="#3aa0ff" stroke-width="4" stroke-opacity="0.9"/>')
pts = " ".join(f"{X(e):.1f},{Y(n):.1f}" for e, n in SV_BRANCH)
o.append(f'<polyline points="{pts}" fill="none" stroke="#3aa0ff" stroke-width="4" stroke-opacity="0.9" stroke-dasharray="8 5"/>')
# covered walkway footprint (3.2 m wide)
pts = " ".join(f"{X(e):.1f},{Y(n):.1f}" for e, n in WALKWAY)
o.append(f'<polyline points="{pts}" fill="none" stroke="#c98a4b" stroke-width="{3.2 * K:.1f}" stroke-opacity="0.85" stroke-linejoin="round"/>')
o.append(f'<text x="{X(40):.1f}" y="{Y(-48):.1f}" fill="#ffe0b8" font-size="13" transform="rotate(42 {X(40):.1f} {Y(-48):.1f})">B09 covered walkway ≈140 m</text>')
# retaining wall (offset SW of walkway)
pts = " ".join(f"{X(e - 2.2):.1f},{Y(n - 2.8):.1f}" for e, n in WALKWAY[3:8])
o.append(f'<polyline points="{pts}" fill="none" stroke="#b9b6ad" stroke-width="3" stroke-dasharray="2 3"/>')
# surveyed structures
for sid, name, E, N, w, h, rot, kind, src, acc in S:
    col = "#ff4f5e" if sid.startswith("B") else "#ff9f43"
    if kind == "circle":
        o.append(f'<circle cx="{X(E):.1f}" cy="{Y(N):.1f}" r="{w / 2 * K:.1f}" fill="{col}" fill-opacity="0.45" stroke="{col}" stroke-width="2.5"/>')
        o.append(f'<circle cx="{X(E):.1f}" cy="{Y(N):.1f}" r="{1.2 * K:.1f}" fill="none" stroke="#fff" stroke-width="1.5"/>')
    else:
        o.append(f'<rect x="{X(E) - w * K / 2:.1f}" y="{Y(N) - h * K / 2:.1f}" width="{w * K:.1f}" height="{h * K:.1f}" fill="{col}" fill-opacity="0.45" stroke="{col}" stroke-width="2" transform="rotate({-rot} {X(E):.1f} {Y(N):.1f})"/>')
    o.append(f'<text x="{X(E) + 6:.1f}" y="{Y(N) - 6:.1f}" fill="#fff" font-size="14" font-weight="bold" stroke="#000" stroke-width="3" paint-order="stroke">{sid}</text>')
# photo spheres
for pid, E, N in PHOTOS:
    o.append(f'<circle cx="{X(E):.1f}" cy="{Y(N):.1f}" r="5" fill="#3aa0ff" stroke="#fff" stroke-width="1.5"/>')
# sketch relics (approx positions)
for no, lab, x, y, m in SK:
    E, N = sk(x, y)
    o.append(f'<circle cx="{X(E):.1f}" cy="{Y(N):.1f}" r="11" fill="#fff8d6" fill-opacity="0.92" stroke="#c0392b" stroke-width="2"/>')
    o.append(f'<text x="{X(E):.1f}" y="{Y(N) + 4.5:.1f}" fill="#c0392b" font-size="12" font-weight="bold" text-anchor="middle">{no}</text>')
for lab, x, y, m in SK_NAMED:
    E, N = sk(x, y)
    o.append(f'<rect x="{X(E) - 5:.1f}" y="{Y(N) - 5:.1f}" width="10" height="10" fill="#fff8d6" stroke="#c0392b" stroke-width="2" transform="rotate(45 {X(E):.1f} {Y(N):.1f})"/>')
    o.append(f'<text x="{X(E) + 9:.1f}" y="{Y(N) + 4:.1f}" fill="#fff8d6" font-size="11" stroke="#000" stroke-width="2.5" paint-order="stroke">{esc(lab)}</text>')
# origin
o.append(f'<circle cx="{X(0):.1f}" cy="{Y(0):.1f}" r="7" fill="none" stroke="#7CFC00" stroke-width="3"/><line x1="{X(0) - 12:.1f}" y1="{Y(0):.1f}" x2="{X(0) + 12:.1f}" y2="{Y(0):.1f}" stroke="#7CFC00" stroke-width="2"/><line x1="{X(0):.1f}" y1="{Y(0) - 12:.1f}" x2="{X(0):.1f}" y2="{Y(0) + 12:.1f}" stroke="#7CFC00" stroke-width="2"/>')
o.append(f'<text x="{X(0) + 12:.1f}" y="{Y(0) + 24:.1f}" fill="#7CFC00" font-size="13" font-weight="bold" stroke="#000" stroke-width="3" paint-order="stroke">O (0,0) gate front</text>')
o.append('</g>')
# north arrow + scale bar
nx, ny = W - 60, 70
o.append(f'<g><polygon points="{nx},{ny - 40} {nx - 14},{ny + 8} {nx},{ny - 2} {nx + 14},{ny + 8}" fill="#fff"/><text x="{nx}" y="{ny + 28}" fill="#fff" font-size="20" font-weight="bold" text-anchor="middle">N</text></g>')
sx, sy = X(150), Y(-150)
o.append(f'<rect x="{sx - 8}" y="{sy - 26}" width="{50 * K + 30:.0f}" height="40" fill="#000" opacity="0.55" rx="4"/>')
for i in range(5):
    o.append(f'<rect x="{sx + i * 10 * K:.1f}" y="{sy - 8}" width="{10 * K:.1f}" height="8" fill="{"#fff" if i % 2 == 0 else "#333"}" stroke="#fff"/>')
o.append(f'<text x="{sx}" y="{sy - 12}" fill="#fff" font-size="12">0</text><text x="{sx + 50 * K - 14:.0f}" y="{sy - 12}" fill="#fff" font-size="12">50 m</text>')
# title + legend strip (bottom, 3 columns)
top = Y(-163)
o.append(f'<rect x="0" y="{top:.0f}" width="{W:.0f}" height="{H - top:.0f}" fill="#0f151b" opacity="0.9"/>')
def txt(x, y, t, size=13, col="#e8eef5", bold=False):
    o.append(f'<text x="{x:.0f}" y="{y:.0f}" fill="{col}" font-size="{size}"{" font-weight=\"bold\"" if bold else ""}>{esc(t)}</text>')
c1, c2, c3 = 24, 600, 1150
y = top + 34
txt(c1, y, "PENANG WAR MUSEUM - TOP-VIEW SITE MAP", 21, "#fff", True); y += 24
for t in ["Batu Maung fort, Penang. North up. Grid = 20 m.", "Origin O = gate front 5.281400 N, 100.288800 E",
          "Blender model frame: x = -E (west +), y = -N (south +)"]:
    txt(c1, y, t, 13, "#9fb3c8"); y += 18
y += 8
legend = [("rect", "#ff4f5e", "Surveyed structure (Street View / Photo Sphere, ±3-6 m)"),
          ("rect", "#ff9f43", "Satellite-only structure (±4 m)"),
          ("line", "#3aa0ff", "Street View path (solid main, dashed SW branch)"),
          ("dot", "#3aa0ff", "User Photo Sphere"),
          ("thick", "#c98a4b", "Covered walkway B09 (3.2 m wide)"),
          ("wall", "#b9b6ad", "Rubble-stone retaining wall B11"),
          ("circ", "#c0392b", "Sketch-map relic no. (fitted, approx ±30 m)"),
          ("diam", "#c0392b", "Sketch-map named feature (approx)"),
          ("dash", "#ffd54a", "Sketch item -> matched surveyed structure")]
for k, col, lab in legend:
    px = c1
    if k == "rect": o.append(f'<rect x="{px}" y="{y - 12}" width="22" height="14" fill="{col}" fill-opacity="0.5" stroke="{col}" stroke-width="2"/>')
    elif k == "line": o.append(f'<line x1="{px}" y1="{y - 5}" x2="{px + 22}" y2="{y - 5}" stroke="{col}" stroke-width="4"/>')
    elif k == "dot": o.append(f'<circle cx="{px + 11}" cy="{y - 5}" r="5" fill="{col}" stroke="#fff"/>')
    elif k == "thick": o.append(f'<line x1="{px}" y1="{y - 5}" x2="{px + 22}" y2="{y - 5}" stroke="{col}" stroke-width="9"/>')
    elif k == "wall": o.append(f'<line x1="{px}" y1="{y - 5}" x2="{px + 22}" y2="{y - 5}" stroke="{col}" stroke-width="3" stroke-dasharray="2 3"/>')
    elif k == "circ": o.append(f'<circle cx="{px + 11}" cy="{y - 5}" r="9" fill="#fff8d6" stroke="{col}" stroke-width="2"/>')
    elif k == "diam": o.append(f'<rect x="{px + 6}" y="{y - 10}" width="10" height="10" fill="#fff8d6" stroke="{col}" stroke-width="2" transform="rotate(45 {px + 11} {y - 5})"/>')
    elif k == "dash": o.append(f'<line x1="{px}" y1="{y - 5}" x2="{px + 22}" y2="{y - 5}" stroke="{col}" stroke-width="2" stroke-dasharray="5 3"/>')
    txt(px + 32, y, lab, 13); y += 21
fitdeg = math.degrees(math.atan2(ai, ar))
y += 6
for t in [f"Sketch fit: rotation {fitdeg:.0f} deg, {math.hypot(ar, ai):.2f} m per sketch px, residual 6-30 m",
          "(the sketch is a schematic illustration, not to scale).",
          "Imagery: Google / Airbus / Maxar screenshots, reference only."]:
    txt(c1, y, t, 12, "#9fb3c8"); y += 16
y = top + 34
txt(c2, y, "SURVEYED / SATELLITE STRUCTURES", 15, "#fff", True); y += 22
for sid, name, E, N, *_ in S:
    txt(c2, y, f"{sid:<4} {name[:62]}", 12.5); y += 16.5
y = top + 34
txt(c3, y, "SKETCH-MAP RELICS (approx positions)", 15, "#fff", True); y += 22
items = [f"{no:>2}  {lab}" for no, lab, *_ in SK]
half = (len(items) + 1) // 2
for i, t in enumerate(items[:half]): txt(c3, y + i * 16.5, t[:30], 12, "#fff8d6")
for i, t in enumerate(items[half:]): txt(c3 + 290, y + i * 16.5, t[:30], 12, "#fff8d6")
o.append('</svg>')
svg = "\n".join(o)
open(os.path.join(OUT, "penang_war_museum_sitemap_topview.svg"), "w").write(svg)

# comparison version: sketch overlay visible at 55 %
open(os.path.join(HERE, "overlay.svg"), "w").write(svg.replace('id="sketch-overlay" opacity="0.0"', 'id="sketch-overlay" opacity="0.55"'))

# ---------------- CSV for Blender
with open(os.path.join(OUT, "penang_war_museum_sitemap_points.csv"), "w", newline="") as f:
    wr = csv.writer(f)
    wr.writerow(["id", "name", "type", "lat", "lon", "E_m", "N_m", "model_x", "model_y", "size_E_m", "size_N_m", "rot_deg_ccw", "source", "accuracy", "sketch_match"])
    for sid, name, E, N, w, h, rot, kind, src, acc in S:
        la, lo = ll(E, N)
        match = ";".join([f"#{no}" for no, _, _, _, m in SK if m == sid] + [l for l, _, _, m in SK_NAMED if m == sid])
        wr.writerow([sid, name, "surveyed" if sid.startswith("B") else "satellite", f"{la:.7f}", f"{lo:.7f}", f"{E:.1f}", f"{N:.1f}", f"{-E:.1f}", f"{-N:.1f}", w, h, rot, src, acc, match])
    for no, lab, x, y, m in SK:
        E, N = sk(x, y); la, lo = ll(E, N)
        wr.writerow([f"R{no:02d}", lab, "sketch_relic", f"{la:.7f}", f"{lo:.7f}", f"{E:.1f}", f"{N:.1f}", f"{-E:.1f}", f"{-N:.1f}", "", "", "", "sketch map (fitted)", "±30 m", m])
    for lab, x, y, m in SK_NAMED:
        E, N = sk(x, y); la, lo = ll(E, N)
        wr.writerow(["F", lab, "sketch_feature", f"{la:.7f}", f"{lo:.7f}", f"{E:.1f}", f"{N:.1f}", f"{-E:.1f}", f"{-N:.1f}", "", "", "", "sketch map (fitted)", "±30 m", m])
    for i, (e, n) in enumerate(WALKWAY):
        la, lo = ll(e, n)
        wr.writerow([f"B09_{i}", "Covered walkway centreline vertex", "path", f"{la:.7f}", f"{lo:.7f}", f"{e:.1f}", f"{n:.1f}", f"{-e:.1f}", f"{-n:.1f}", 3.2, "", "", "SV 2013", "±3 m", ""])
print("written", W, H)
