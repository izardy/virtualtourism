"""Build Penang War Museum structures from the survey (run in background Blender).

    blender -b --factory-startup --python build_structures.py -- <target> [<out_dir>]

targets: gun_emplacement, watchtower, bunker, amenities, walkway, courtyard, barrack_blue, satellite, sketch_relics
"""
import bpy, math, os, sys, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pwm_lib import *  # noqa

args = sys.argv[sys.argv.index("--") + 1:]
TARGET = args[0]
OUT = args[1] if len(args) > 1 else os.path.expanduser("~/Desktop/blender/site_structures")
BAKED = args[2] if len(args) > 2 else ""
os.makedirs(OUT, exist_ok=True)
random.seed(7)
reset_scene()
P = points()
pal = palette()
R = math.radians


def loc_of(pid):
    r = P[pid]
    return float(r["model_x"]), float(r["model_y"]), float(r["rot_deg_ccw"] or 0)


def info_board(col, parent, name, loc, rot_z, w=0.8, h=0.6, mat=None):
    p = Part(col, name, pal["timber"], parent)
    x, y, z = loc
    for dx in (-w / 2 - 0.05, w / 2 + 0.05):
        p.boxz((0.08, 0.08, z + h), (x + dx * math.cos(rot_z), y + dx * math.sin(rot_z), 0))
    p.done()
    q = Part(col, name + "_Panel", mat or pal["sign_yellow"], parent)
    q.box((w, 0.04, h), (x, y, z + h / 2), (0, 0, rot_z)); q.done()


# =============================================================== B17 gun emplacement
def gun_emplacement():
    top = collection("PWM_B17_GunEmplacement")
    x, y, rot = loc_of("B17")
    rt = root(top, "B17_GunEmplacement_Root", x, y, rot)
    C = pal["concrete"]
    # apron: square concrete mass (top z=0, bottom -1.5) with the circular gun pit (r 4.25) and a rear trench gap
    apron = Part(top, "B17_Apron_Concrete", C, rt)
    bm = apron.bm; rin, half, z0, z1 = 4.25, (10.0, 8.0), -1.5, 0.0
    gap = (169.0, 191.0)
    angs = sorted(set([i * 360 / 96 for i in range(96)] + [math.degrees(math.atan2(sy * half[1], sx * half[0])) % 360 for sx in (-1, 1) for sy in (-1, 1)] + list(gap)))
    angs = [a for a in angs if not (gap[0] < a < gap[1])]
    i0 = angs.index(gap[1]); angs = angs[i0:] + angs[:i0]          # start right after the gap, end at its start
    def outer(a):
        c, s_ = math.cos(R(a)), math.sin(R(a))
        t = min(half[0] / abs(c) if abs(c) > 1e-6 else 1e9, half[1] / abs(s_) if abs(s_) > 1e-6 else 1e9)
        return (c * t, s_ * t)
    IT = [bm.verts.new((rin * math.cos(R(a)), rin * math.sin(R(a)), z1)) for a in angs]
    OT = [bm.verts.new((*outer(a), z1)) for a in angs]
    IB = [bm.verts.new((rin * math.cos(R(a)), rin * math.sin(R(a)), z0)) for a in angs]
    OB = [bm.verts.new((*outer(a), z0)) for a in angs]
    for k in range(len(angs) - 1):
        bm.faces.new((IT[k], IT[k + 1], OT[k + 1], OT[k])); bm.faces.new((OB[k], OB[k + 1], IB[k + 1], IB[k]))
        bm.faces.new((IB[k], IB[k + 1], IT[k + 1], IT[k])); bm.faces.new((OT[k], OT[k + 1], OB[k + 1], OB[k]))
    for k in (0, len(angs) - 1):
        bm.faces.new((IT[k], OT[k], OB[k], IB[k]))
    # trench side walls + fill between the walls and the gap wedge (trench floor at -1.1)
    for sy in (-1, 1):
        apron.box((5.75, 1.2, 1.5), (-7.125, sy * 1.4, -0.75))
    ap = apron.done()
    # parapet (about 300 deg, open to the rear trench)
    par = Part(top, "B17_Parapet", C, rt, smooth=True)
    par.ring(4.25, 4.85, 0.0, 0.85, 205, 515, seg=96)
    par.ring(4.32, 4.78, 0.85, 0.98, 205, 515, seg=96)       # rounded-ish coping
    par.done()
    # pit floor, pivot plinth, racer ring, holdfast bolts
    fl = Part(top, "B17_PitFloor", pal["concrete_dark"], rt); fl.cyl(4.25, 0.05, (0, 0, -1.125), seg=64); fl.done()
    pv = Part(top, "B17_PivotPlinth", C, rt, smooth=True); pv.cyl(1.2, 0.4, (0, 0, -0.9), seg=48); pv.done()
    st = Part(top, "B17_RacerRing_HoldfastBolts", pal["steel"], rt)
    st.ring(1.95, 2.1, -1.1, -1.03, 0, 360, seg=72)
    for i in range(24):
        a = 2 * math.pi * i / 24
        st.cyl(0.04, 0.14, (1.02 * math.cos(a), 1.02 * math.sin(a), -0.63), seg=8)
    st.done()
    cap = Part(top, "B17_CentralPivotCap", M("RustRed", (0.35, 0.12, 0.06), 0.6, 0.3), rt); cap.cyl(0.28, 0.22, (0, 0, -0.6)); cap.done()
    # ammunition recesses in the pit wall + steel grilles
    rec = Part(top, "B17_AmmoRecesses_dark", pal["dark"], rt)
    gr = Part(top, "B17_AmmoRecess_Grilles", pal["grille"], rt)
    for ang in (35, 80, 125, 280, 325):
        a = R(ang); cx, cy = 4.2 * math.cos(a), 4.2 * math.sin(a)
        rec.box((0.35, 0.9, 0.8), (cx, cy, -0.55), (0, 0, a))
        for k in range(5):
            off = -0.36 + k * 0.18
            gr.box((0.03, 0.025, 0.8), (cx - 0.19 * math.cos(a) - off * math.sin(a), cy - 0.19 * math.sin(a) + off * math.cos(a), -0.55), (0, 0, a))
        gr.box((0.03, 0.9, 0.03), (cx - 0.19 * math.cos(a), cy - 0.19 * math.sin(a), -0.2), (0, 0, a))
    rec.done(); gr.done()
    # rear sunken trench floor + ready-use magazine / shelter block with grilled openings
    tr = Part(top, "B17_RearTrench_Floor", pal["concrete_dark"], rt); tr.box((5.9, 1.7, 0.05), (-7.1, 0, -1.125)); tr.done()
    mag = Part(top, "B17_ReadyMagazine_Block", C, rt)
    mag.box((5.0, 6.0, 2.7), (-12.4, 0, 0.2))
    mag.done()
    mo = Part(top, "B17_ReadyMagazine_Openings", pal["dark"], rt)
    mg = Part(top, "B17_ReadyMagazine_Grilles", pal["grille"], rt)
    for yy in (-1.8, 0, 1.8):
        mo.box((0.1, 1.0, 1.3), (-9.88, yy, -0.25))
        for k in range(6):
            mg.box((0.03, 0.025, 1.3), (-9.82, yy - 0.42 + k * 0.17, -0.25))
    mo.done(); mg.done()
    mound = Part(top, "B17_EarthCover", pal["earth"], rt, smooth=True); mound.sphere(1, (-12.4, 0, 1.4), (2.8, 3.4, 0.9)); mound.done()
    # steps up to the upper terrace, terrace, retaining wall
    stp = Part(top, "B17_Steps", C, rt)
    for i in range(6):
        stp.boxz((1.4, 0.5, 0.3 * (i + 1)), (-2.3, 4.25 + i * 0.5, 0))
    stp.done()
    ter = Part(top, "B17_UpperTerrace", C, rt); ter.boxz((15, 6, 1.8), (-8.5, 9.5, 0)); ter.done()
    rw = Part(top, "B17_RetainingWall_Cracked", C, rt); rw.boxz((10, 0.5, 2.6), (-11, 6.6, 0)); rw.done()
    rail = Part(top, "B17_TerraceRailing", pal["steel"], rt)
    for i in range(9):
        rail.rod((-15 + i * 1.1, 6.6, 1.8), (-15 + i * 1.1, 6.6, 2.8), 0.025)
    rail.rod((-15, 6.6, 2.8), (-6.2, 6.6, 2.8), 0.025); rail.done()
    # timber lookout hut on the terrace
    hut = Part(top, "B17_LookoutHut_Frame", pal["timber"], rt)
    for dx in (-1.4, 1.4):
        for dy in (-1.4, 1.4):
            hut.boxz((0.15, 0.15, 2.4), (-11 + dx, 10 + dy, 1.8))
    hut.box((3.0, 3.0, 0.08), (-11, 10, 1.84)); hut.box((3.0, 0.06, 1.0), (-11, 8.6, 2.3)); hut.box((0.06, 3.0, 1.0), (-12.5, 10, 2.3))
    hut.done()
    hr = Part(top, "B17_LookoutHut_Roof", pal["roof_brown"], rt)
    gable_roof(hr, 3.0, 3.0, 4.2, 5.2, 0.35)
    for o_ in hr.bm.verts: o_.co.x += -11; o_.co.y += 10
    hr.done()
    # inert artillery shell on the parapet + interpretation plate
    sh = Part(top, "B17_DisplayShell_Body", pal["shell_black"], rt, smooth=True); sh.cyl(0.17, 0.8, (2.9, -3.7, 1.35)); sh.done()
    sn = Part(top, "B17_DisplayShell_Nose", pal["shell_red"], rt, smooth=True); sn.cyl(0.17, 0.4, (2.9, -3.7, 1.95), r2=0.03); sn.done()
    pl = Part(top, "B17_InterpretationPlate", pal["sign_yellow"], rt); pl.box((0.6, 0.04, 0.45), (4.88 * math.cos(R(40)), 4.88 * math.sin(R(40)), 0.45), (0, 0, R(40 + 90))); pl.done()
    finish(top, os.path.join(OUT, "penang_war_museum_B17_gun_emplacement.blend"), "B17 Coastal gun emplacement (survey-based)")


# =============================================================== B05 watchtower
def watchtower():
    top = collection("PWM_B05_Watchtower")
    x, y, rot = loc_of("B05")
    rt = root(top, "B05_Watchtower_Root", x, y, rot)
    base = Part(top, "B05_BrickPlinth", pal["brick"], rt); base.boxz((3.8, 3.8, 0.4), (0, 0, 0)); base.done()
    T = Part(top, "B05_TimberFrame", pal["timber"], rt)
    for dx in (-1.4, 1.4):
        for dy in (-1.4, 1.4):
            T.boxz((0.25, 0.25, 7.8), (dx, dy, 0.4))
    for z in (2.4, 4.4, 6.4):        # ring beams + deck at each level
        for s in (-1, 1):
            T.box((3.05, 0.15, 0.2), (0, s * 1.4, z)); T.box((0.15, 3.05, 0.2), (s * 1.4, 0, z))
        T.box((2.8, 1.6, 0.06), (0, 0.6, z + 0.12))       # landing deck (stair opening on the -y side)
    for s in (-1, 1):                 # diagonal bracing on two faces
        T.beam((-1.4, s * 1.4, 0.5), (1.4, s * 1.4, 2.3), 0.1, 0.1)
        T.beam((s * 1.4, -1.4, 2.5), (s * 1.4, 1.4, 4.3), 0.1, 0.1)
    T.box((3.0, 3.0, 0.08), (0, 0, 6.54))                 # top deck
    for s in (-1, 1):                                      # top railing
        T.box((3.0, 0.08, 0.08), (0, s * 1.45, 7.5)); T.box((0.08, 3.0, 0.08), (s * 1.45, 0, 7.5))
        T.box((3.0, 0.05, 0.06), (0, s * 1.45, 7.0)); T.box((0.05, 3.0, 0.06), (s * 1.45, 0, 7.0))
    T.done()
    S = Part(top, "B05_SteelStairs", pal["steel"], rt)
    for f, (z0, sx) in enumerate(((0.4, 1), (2.5, -1), (4.5, 1))):
        y0 = -0.9 if f % 2 == 0 else -0.3
        for side in (-0.45, 0.45):
            S.beam((-1.1 * sx, y0 + side, z0), (1.1 * sx, y0 + side, z0 + 1.95), 0.05, 0.18)
        for k in range(10):
            S.box((0.25, 0.9, 0.04), (-1.1 * sx + sx * (k + 0.5) * 0.22, y0, z0 + (k + 0.5) * 0.195))
        S.rod((-1.1 * sx, y0 - 0.5, z0 + 0.9), (1.1 * sx, y0 - 0.5, z0 + 2.85), 0.02)
    S.done()
    rf = Part(top, "B05_GableRoof", pal["timber_light"], rt)
    gable_roof(rf, 3.0, 3.0, 8.2, 9.2, 0.45, 0.08); rf.done()
    ge = Part(top, "B05_GableEnds", pal["timber"], rt); gable_ends(ge, 3.0, 8.2, 9.15, (-1.5, 1.5), 0.06); ge.done()
    finish(top, os.path.join(OUT, "penang_war_museum_B05_watchtower.blend"), "B05 Timber watchtower (survey-based)")


# =============================================================== B12 bunker
def vault_profile(w, wall_h, seg=24):
    r = w / 2
    pts = [(-r, 0), (r, 0)]
    for i in range(seg + 1):
        a = math.pi * i / seg
        pts.append((r * math.cos(a), wall_h + r * math.sin(a)))
    pts.pop(1)  # (r,0) is first arc point's base -> keep closed outline below
    return [(-r, 0), (r, 0)] + [(r * math.cos(math.pi * i / seg), wall_h + r * math.sin(math.pi * i / seg)) for i in range(seg + 1)][1:-1] + [(-r, wall_h)]


def bunker():
    top = collection("PWM_B12_VaultedBunker")
    x, y, rot = loc_of("B12")
    rt = root(top, "B12_AmmunitionBunker_Root", x, y, rot)
    v = Part(top, "B12_BarrelVault", pal["concrete"], rt, smooth=False)
    prof = [(-2.5, 0), (2.5, 0), (2.5, 0.5)] + [(2.5 * math.cos(math.pi * i / 24), 0.5 + 2.5 * math.sin(math.pi * i / 24)) for i in range(1, 24)] + [(-2.5, 0.5)]
    v.prism(prof, 6.0, (0, 0.2, 0)); v.done()
    fw = Part(top, "B12_FrontFacade", pal["concrete"], rt); fw.box((5.6, 0.35, 3.2), (0, -2.95, 1.6)); fw.done()
    d = Part(top, "B12_CamouflageSteelDoor", pal["camo"], rt); d.box((1.0, 0.06, 2.0), (0, -3.15, 1.0)); d.done()
    s = Part(top, "B12_Sign_AmmunitionStorage", pal["sign_yellow"], rt); s.box((0.8, 0.04, 0.6), (1.6, -3.15, 1.6)); s.done()
    text(top, "B12_SignText", "AMMUNITION\nSTORAGE", 0.09, (1.6, -3.18, 1.62), (R(90), 0, 0), pal["dark"], rt)
    m = Part(top, "B12_EarthMound_Behind", pal["earth"], rt, smooth=True); m.sphere(1, (0, 3.6, 0.2), (3.8, 3.2, 2.8)); m.done()
    info_board(top, rt, "B12_InfoBoard", (-2.2, -5.0, 0.9), 0.0, 1.2, 0.9, pal["sign_paper"])
    finish(top, os.path.join(OUT, "penang_war_museum_B12_bunker.blend"), "B12 Vaulted concrete ammunition bunker (survey-based)")


# =============================================================== B07 + B08 amenities
def amenities():
    top = collection("PWM_B07_B08_Amenities")
    # --- B07 cafe / souvenir + rest area
    x, y, rot = loc_of("B07")
    rt = root(top, "B07_Cafe_Souvenir_Root", x, y, rot)
    w = Part(top, "B07_Walls_Teal", pal["teal"], rt); w.boxz((10, 5, 2.7), (0, 1.5, 0)); w.done()
    rs = Part(top, "B07_RoofSlab", pal["concrete"], rt); rs.box((10.6, 5.6, 0.18), (0, 1.5, 2.79)); rs.done()
    op = Part(top, "B07_Openings", pal["dark"], rt)
    op.box((1.6, 0.06, 2.1), (-2.5, -1.03, 1.05)); op.box((2.6, 0.06, 1.2), (2.0, -1.03, 1.5)); op.done()
    pg = Part(top, "B07_Pergola_Timber", pal["timber"], rt)
    for xx in (-4.8, -2.4, 0, 2.4, 4.8):
        pg.boxz((0.14, 0.14, 2.55), (xx, -4.2, 0)); pg.beam((xx, -4.3, 2.6), (xx, -1.0, 2.75), 0.1, 0.15)
    pg.box((10, 0.14, 0.2), (0, -4.2, 2.58)); pg.done()
    tr = Part(top, "B07_Pergola_TranslucentRoof", pal["translucent"], rt)
    tr.quad([(-5.2, -4.6, 2.7), (5.2, -4.6, 2.7), (5.2, -1.0, 2.88), (-5.2, -1.0, 2.88)]); tr.done()
    bn = Part(top, "B07_TIPPNA_Banner", pal["sign_red"], rt); bn.box((3.0, 0.04, 0.6), (2.5, -1.06, 2.35)); bn.done()
    pn = Part(top, "B07_UnitPennants", M("PennantMix", (0.7, 0.55, 0.1), 0.6), rt)
    for i in range(8): pn.box((0.3, 0.02, 0.4), (-4 + i * 1.1, -4.25, 2.25))
    pn.done()
    rk = Part(top, "B07_BookRack", pal["steel"], rt); rk.boxz((0.6, 0.35, 1.6), (4.4, -1.4, 0)); rk.done()
    tb = Part(top, "B07_PicnicTables", pal["timber_light"], rt)
    lg = Part(top, "B07_LogBenches", NM("LogBark", (0.16, 0.1, 0.06), (0.4, 0.3, 0.22), 14, 0.7, 0.9, stretch=(1, 1, 4)), rt, smooth=True)
    for k, (tx, ty) in enumerate(((-3.0, -7.0), (0.5, -7.3), (3.8, -6.8))):
        tb.box((1.6, 0.8, 0.06), (tx, ty, 0.75)); tb.boxz((0.12, 0.6, 0.72), (tx - 0.6, ty, 0)); tb.boxz((0.12, 0.6, 0.72), (tx + 0.6, ty, 0))
        for s in (-1, 1): lg.cyl(0.18, 1.6, (tx, ty + s * 0.75, 0.2), (0, R(90), 0), seg=12)
    tb.done(); lg.done()
    fr = Part(top, "B07_PhotoBanner_Frame", pal["steel"], rt)
    for xx in (-3, 3): fr.boxz((0.1, 0.1, 5.2), (xx, 3.9, 0))
    fr.done()
    pb = Part(top, "B07_PhotoBanner_WWIISoldiers", pal["photo_banner"], rt); pb.box((6.2, 0.04, 2.0), (0, 3.85, 4.1)); pb.done()
    # --- B08 toilets
    x, y, rot = loc_of("B08")
    r2 = root(top, "B08_ToiletBlock_Root", x, y, rot)
    w = Part(top, "B08_Walls_BlueGrey", pal["bluegrey"], r2); w.boxz((8, 4, 2.6), (0, 0, 0)); w.done()
    rs = Part(top, "B08_FlatRoof", pal["concrete"], r2); rs.box((8.4, 4.4, 0.15), (0, 0, 2.67)); rs.done()
    d = Part(top, "B08_CamouflageDoors", pal["camo"], r2)
    for xx in (-1.8, 1.8): d.box((0.95, 0.06, 2.05), (xx, -2.03, 1.03))
    d.done()
    sg = Part(top, "B08_GenderSigns", pal["sign_red"], r2)
    for xx in (-1.8, 1.8): sg.cyl(0.15, 0.03, (xx, -2.08, 1.7), (R(90), 0, 0))
    sg.done()
    lv = Part(top, "B08_LouvreWindows", pal["timber"], r2)
    for xx in (-3.3, 0, 3.3):
        for k in range(5): lv.box((0.7, 0.05, 0.05), (xx, -2.03, 2.0 + k * 0.08), (R(-30), 0, 0))
    lv.done()
    fr = Part(top, "B08_PhotoBanner_Frame", pal["steel"], r2)
    for xx in (-4, 4): fr.boxz((0.1, 0.1, 5.6), (xx, 1.9, 0))
    fr.done()
    pb = Part(top, "B08_PhotoBanner_POWs", pal["photo_banner"], r2); pb.box((8.2, 0.04, 2.5), (0, 1.85, 4.3)); pb.done()
    pt = Part(top, "B08_PottedPlants", pal["leaves"], r2, smooth=True)
    for xx in (-3.6, -0.6, 0.6, 3.6): pt.sphere(0.35, (xx, -2.5, 0.45), (1, 1, 1.2), 1)
    pt.done()
    finish(top, os.path.join(OUT, "penang_war_museum_B07_B08_amenities.blend"), "B07 cafe/souvenir + B08 toilet block (survey-based)")


# =============================================================== B09-B11, B13 covered walkway
def walkway():
    top = collection("PWM_B09_CoveredWalkway")
    rt = root(top, "B09_Walkway_Root_(site_coords)", 0, 0, 0, z=0.0)
    pts = []
    i = 0
    while f"B09_{i}" in P:
        r = P[f"B09_{i}"]; pts.append(Vector((float(r["model_x"]), float(r["model_y"]), 0))); i += 1
    half, eave, ridge = 1.6, 2.4, 3.4
    deck = Part(top, "B09_ConcreteDeck", pal["paving"], rt)
    pil = Part(top, "B09_ConcretePillars", M("GreenGreyRender", (0.3, 0.36, 0.32), 0.8), rt)
    post = Part(top, "B09_TimberPosts_Frame", pal["timber"], rt)
    roof = Part(top, "B09_RoofSheets", M("DarkCorrugated", (0.12, 0.11, 0.1), 0.6, 0.3), rt)
    par = Part(top, "B09_GardenParapet", pal["concrete"], rt)
    lan = Part(top, "B09_HangingLanterns", pal["brass"], rt, smooth=True)
    wall = Part(top, "B11_RubbleRetainingWall", pal["rubble"], rt)
    total = 0.0; bay = 0
    for si in range(len(pts) - 1):
        a, b = pts[si], pts[si + 1]; d = b - a; Ls = d.length; u = d.normalized(); n = Vector((-u.y, u.x, 0))
        ang = math.atan2(u.y, u.x); mid = (a + b) / 2
        deck.box((Ls + 0.3, 2 * half + 0.2, 0.15), (mid.x, mid.y, 0.075), (0, 0, ang))
        par.box((Ls, 0.2, 0.6), (mid.x + n.x * (half + 0.1), mid.y + n.y * (half + 0.1), 0.3), (0, 0, ang))
        for s in (-1, 1):  # eave beams + roof sheets
            e = Vector((n.x * s * half, n.y * s * half, 0))
            post.beam((a.x + e.x, a.y + e.y, eave), (b.x + e.x, b.y + e.y, eave), 0.12, 0.18)
            o = Vector((n.x * s * (half + 0.35), n.y * s * (half + 0.35), 0))
            roof.quad([(a.x + o.x, a.y + o.y, eave - 0.1), (b.x + o.x, b.y + o.y, eave - 0.1), (b.x, b.y, ridge + 0.08), (a.x, a.y, ridge + 0.08)])
        post.beam((a.x, a.y, ridge), (b.x, b.y, ridge), 0.12, 0.18)
        if 3 <= si <= 6:   # hill-side rubble retaining wall
            off = -(half + 1.0)
            wall.box((Ls + 0.4, 0.6, 2.2), (mid.x + n.x * off, mid.y + n.y * off, 1.1), (0, 0, ang))
        t = (2.4 - total % 2.4) % 2.4
        while t <= Ls:
            p = a + u * t
            for s in (-1, 1):
                q = p + n * s * half
                pil.boxz((0.45, 0.45, 1.0), (q.x, q.y, 0.15), (0, 0, ang))
                post.boxz((0.18, 0.18, eave - 1.15), (q.x, q.y, 1.15), (0, 0, ang))
                post.beam((q.x, q.y, eave), (p.x, p.y, ridge), 0.08, 0.14)
            post.beam((p.x + n.x * half, p.y + n.y * half, eave), (p.x - n.x * half, p.y - n.y * half, eave), 0.08, 0.14)
            if bay % 3 == 1:
                lan.cyl(0.14, 0.32, (p.x, p.y, ridge - 0.55), seg=10); lan.cyl(0.25, 0.04, (p.x, p.y, ridge - 0.36), seg=16)
                post.rod((p.x, p.y, ridge - 0.34), (p.x, p.y, ridge), 0.01)
            bay += 1; t += 2.4
        total += Ls
    for prt in (deck, pil, post, roof, par, lan, wall): prt.done()
    # B11 steps up through the wall near P12 (vertex 6)
    a, b = pts[6], pts[7]; u = (b - a).normalized(); n = Vector((-u.y, u.x, 0)); ang = math.atan2(u.y, u.x)
    st = Part(top, "B11_StepsUpHillside", pal["concrete"], rt)
    for k in range(9):
        q = a + n * -(half + 0.6 + k * 0.32)
        st.box((1.2, 0.32, 0.25 * (k + 1)), (q.x, q.y, 0.125 * (k + 1)), (0, 0, ang))
    st.done()
    # B10 site-map board
    x, y, rot = loc_of("B10")
    r10 = root(top, "B10_SiteMapBoard_Root", x, y, rot)
    info_board(top, r10, "B10_SiteMapBoard", (0, 0, 0.9), 0.0, 2.5, 1.8, NM("PaintedMap", (0.15, 0.4, 0.65), (0.25, 0.5, 0.2), 3, 0.0, 0.5))
    # B13 garden huts (attap) on the garden side
    x, y, rot = loc_of("B13")
    for k, (dx, dy) in enumerate(((0, 0), (-3.5, 2.5))):
        r13 = root(top, f"B13_GardenHut_{k + 1}_Root", x + dx, y + dy, rot + 10 * k)
        h = Part(top, f"B13_GardenHut_{k + 1}_Frame", pal["timber_light"], r13)
        for sx in (-0.9, 0.9):
            for sy in (-0.65, 0.65): h.boxz((0.08, 0.08, 1.3), (sx, sy, 0))
        h.box((1.9, 1.4, 0.06), (0, 0, 0.4)); h.done()
        rf = Part(top, f"B13_GardenHut_{k + 1}_AttapRoof", pal["attap"], r13); gable_roof(rf, 1.9, 1.4, 1.3, 2.0, 0.25, 0.08); rf.done()
    bpy.context.view_layer.update()
    drape([o for o in top.objects if o.parent == rt])
    finish(top, os.path.join(OUT, "penang_war_museum_B09_walkway.blend"), "B09 covered walkway + B10 board + B11 wall/steps + B13 huts")


# =============================================================== B14 courtyard
def courtyard():
    top = collection("PWM_B14_Courtyard")
    x, y, rot = loc_of("B14")
    rt = root(top, "B14_Courtyard_Root", x, y, rot)
    s = Part(top, "B14_AsphaltCourt", pal["asphalt"], rt); s.box((20, 15, 0.06), (0, 0, 0.03)); s.done()
    pg = Part(top, "B14_SteelPergola", pal["steel"], rt)
    for xx in (-7.5, -2.5, 2.5, 7.5):
        for yy in (-5, 0, 5): pg.boxz((0.12, 0.12, 3.6), (xx, yy, 0))
    for yy in (-5, 0, 5): pg.box((15.2, 0.1, 0.12), (0, yy, 3.6))
    for xx in (-7.5, -2.5, 2.5, 7.5): pg.box((0.1, 10.2, 0.12), (xx, 0, 3.6))
    pg.done()
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=60, y_subdivisions=45, size=1)
    v = bpy.context.active_object; v.name = "B14_VineCanopy"
    for c in v.users_collection: c.objects.unlink(v)
    top.objects.link(v); v.parent = rt; v.scale = (17, 12.5, 1); v.location = (0, 0, 3.75)
    v.data.materials.append(pal["vine"])
    tex = bpy.data.textures.new("VineNoise", 'CLOUDS'); tex.noise_scale = 0.3
    dm = v.modifiers.new("Displace", 'DISPLACE'); dm.texture = tex; dm.strength = 0.3
    v.modifiers.new("Thick", 'SOLIDIFY').thickness = 0.15
    fm = Part(top, "B14_WoodenFortModel", pal["timber"], rt)
    fm.boxz((1.5, 1.0, 0.9), (6, 5.5, 0)); fm.boxz((1.2, 0.8, 0.6), (6, 5.5, 0.9)); fm.boxz((0.8, 0.6, 0.5), (6, 5.5, 1.5))
    fm.done()
    fe = Part(top, "B14_FencedExhibit", pal["grille"], rt)
    for xx in (-6.5, -4.5, -2.5):
        for yy in (3.0, 5.5): fe.boxz((0.06, 0.06, 1.5), (xx, yy, 0))
    for yy in (3.0, 5.5): fe.box((4.0, 0.02, 1.4), (-4.5, yy, 0.75))
    for xx in (-6.5, -2.5): fe.box((0.02, 2.5, 1.4), (xx, 4.25, 0.75))
    fe.done()
    info_board(top, rt, "B14_ExhibitSign_Yellow", (-4.5, 2.6, 0.9), 0.0, 0.6, 0.5)
    sw = Part(top, "B14_StoneWall_South", pal["rubble"], rt); sw.box((20, 0.6, 1.6), (0, 7.8, 0.8)); sw.done()
    lb = Part(top, "B14_LogBollards", NM("LogBark", (0.16, 0.1, 0.06), (0.4, 0.3, 0.22), 14, 0.7, 0.9), rt, smooth=True)
    for k in range(7): lb.cyl(0.15, 0.6, (-9.6, -6 + k * 1.6, 0.3), seg=10)
    lb.done()
    bed = Part(top, "B14_PlantingBed", pal["leaves"], rt, smooth=True)
    for k in range(6): bed.sphere(0.6, (-8 + k * 1.2, -6.8, 0.4), (1, 1, 0.8), 1)
    bed.done()
    finish(top, os.path.join(OUT, "penang_war_museum_B14_courtyard.blend"), "B14 south-east courtyard (survey-based)")


# =============================================================== B15 blue barrack + B16 trail
def barrack_blue():
    top = collection("PWM_B15_B16_BlueBarrack_Trail")
    x, y, rot = loc_of("B15")
    rt = root(top, "B15_BlueBarrack_Root", x, y, rot)
    w = Part(top, "B15_Walls_Blue", pal["blue"], rt); w.boxz((12, 7, 3.0), (0, 0, 0)); w.done()
    rs = Part(top, "B15_RoofSlab_Overhang", pal["concrete"], rt); rs.box((13.2, 8.2, 0.25), (0, 0, 3.12)); rs.done()
    rr = Part(top, "B15_CorrugatedRoof", pal["roof_brown"], rt)
    rr.quad([(-6.6, -4.1, 3.3), (6.6, -4.1, 3.3), (6.6, 4.1, 3.75), (-6.6, 4.1, 3.75)]); rr.done()
    fr = Part(top, "B15_WindowFrames_White", pal["white"], rt)
    bb = Part(top, "B15_BambooScreens", pal["bamboo"], rt)
    for xx in (-4.5, -1.5, 3.0, 5.0):
        for (sx, sz, dx, dz) in ((1.15, 0.08, 0, 0.54), (1.15, 0.08, 0, -0.54), (0.08, 1.1, -0.54, 0), (0.08, 1.1, 0.54, 0)):
            fr.box((sx, 0.08, sz), (xx + dx, -3.54, 1.6 + dz))
        for k in range(9): bb.box((0.07, 0.05, 1.0), (xx - 0.44 + k * 0.11, -3.52, 1.6))
    fr.done(); bb.done()
    dr = Part(top, "B15_TimberDoor", pal["timber"], rt); dr.box((1.0, 0.06, 2.1), (1.0, -3.53, 1.05)); dr.done()
    wk = Part(top, "B15_FrontWalkway", pal["timber_light"], rt); wk.box((12.5, 1.3, 0.1), (0, -4.25, 0.35)); wk.done()
    hr = Part(top, "B15_BlackHandrail", pal["steel"], rt)
    for k in range(9): hr.rod((-6 + k * 1.5, -4.85, 0.4), (-6 + k * 1.5, -4.85, 1.3), 0.025)
    hr.rod((-6, -4.85, 1.3), (6, -4.85, 1.3), 0.025); hr.done()
    # B16 jungle trail
    r16 = root(top, "B16_JungleTrail_Root", 8.5, 76.0, -45)   # P16 Street View point (model 6.9, 74.7), trail climbs SW (model +x,+y)
    stp = Part(top, "B16_LogSteps", NM("LogBark", (0.16, 0.1, 0.06), (0.4, 0.3, 0.22), 14, 0.7, 0.9), r16, smooth=True)
    for k in range(8): stp.cyl(0.1, 1.4, (0, k * 0.9, 0.1 + k * 0.18), (0, R(90), 0), seg=8)
    stp.done()
    tr = Part(top, "B16_TrailEarth", pal["earth"], r16); tr.quad([(-0.8, -0.5, 0.02), (0.8, -0.5, 0.02), (0.8, 7.5, 1.5), (-0.8, 7.5, 1.5)]); tr.done()
    rp = Part(top, "B16_RopeFence", pal["rope"], r16)
    pp = Part(top, "B16_FencePosts", pal["timber_light"], r16)
    for k in range(5):
        for s in (-1.1, 1.1): pp.rod((s, k * 1.8, 0.2 + k * 0.33), (s, k * 1.8, 1.1 + k * 0.33), 0.05)
    for s in (-1.1, 1.1): rp.rod((s, 0, 1.0), (s, 7.2, 2.3), 0.015)
    rp.done(); pp.done()
    tk = Part(top, "B16_NooseTree", NM("LogBark", (0.16, 0.1, 0.06), (0.4, 0.3, 0.22), 14, 0.7, 0.9), r16, smooth=True)
    tk.cyl(0.35, 9, (-2.4, 2, 4.5), seg=12); tk.rod((-2.4, 2, 4.0), (0.2, 2, 4.6), 0.12)
    tk.done()
    ns = Part(top, "B16_NooseDisplay_Rope", pal["rope"], r16, smooth=True)
    ns.rod((-0.4, 2, 4.5), (-0.4, 2, 2.6), 0.02); ns.ring(0.14, 0.16, 2.3, 2.6, 0, 360, 24, (-0.4, 2, 0)); ns.done()
    pl = Part(top, "B16_InfoPillar_Concrete", pal["concrete"], r16); pl.boxz((0.5, 0.5, 1.6), (1.7, 3.0, 0)); pl.done()
    sg = Part(top, "B16_InfoPillar_Sign", pal["sign_yellow"], r16); sg.box((0.45, 0.04, 0.35), (1.7, 2.73, 1.3)); sg.done()
    bd = Part(top, "B16_Boulder", pal["rubble"], r16, smooth=True); bd.sphere(1, (-2.6, -1.0, 0.6), (1.6, 1.3, 1.1)); bd.done()
    finish(top, os.path.join(OUT, "penang_war_museum_B15_B16_barrack_trail.blend"), "B15 blue barrack + B16 jungle trail (survey-based)")


# =============================================================== S1-S6 satellite placeholders
def block_building(col, parent, name, L, Wd, H, roof_mat, wall_mat, ridge=1.2, chimney=False):
    w = Part(col, name + "_Walls", wall_mat, parent); w.boxz((L, Wd, H), (0, 0, 0)); w.done()
    r = Part(col, name + "_Roof", roof_mat, parent)
    if ridge > 0:
        gable_roof(r, L, Wd, H, H + ridge, 0.5)
    else:
        r.box((L + 0.6, Wd + 0.6, 0.2), (0, 0, H + 0.1))
    r.done()
    if ridge > 0:
        g = Part(col, name + "_GableEnds", wall_mat, parent); gable_ends(g, Wd, H, H + ridge - 0.05, (-L / 2, L / 2), 0.1); g.done()
    d = Part(col, name + "_Openings", pal["dark"], parent)
    for k in range(max(1, int(L // 3))):
        d.box((0.9, 0.06, 1.0 if k else 2.0), (-L / 2 + 1.5 + k * 3, -Wd / 2 - 0.02, 1.5 if k else 1.0))
    d.done()
    if chimney:
        c = Part(col, name + "_Chimney", pal["brick"], parent); c.boxz((0.8, 0.8, H + ridge + 1.2), (L / 2 - 1.2, 0, 0)); c.done()


def satellite():
    top = collection("PWM_S_SatelliteOnly_Placeholders")
    x, y, rot = loc_of("S1"); r = root(top, "S1_OpenClearing_ParadeGround_Root", x, y, rot)
    g = Part(top, "S1_GrassClearing", pal["grass"], r); g.box((25, 25, 0.04), (0, 0, 0.02)); g.done()
    x, y, rot = loc_of("S2"); r = root(top, "S2_SmallBuilding_Root (placeholder)", x, y, rot)
    block_building(top, r, "S2_SmallBuilding", 8, 10, 3.0, pal["roof_brown"], pal["placeholder"], 1.3)
    x, y, rot = loc_of("S3"); r = root(top, "S3_SmallWhiteHut_Root (placeholder)", x, y, rot)
    block_building(top, r, "S3_SmallWhiteHut", 3, 3, 2.6, pal["white"], pal["placeholder"], 0.8)
    x, y, rot = loc_of("S4"); r = root(top, "S4_ForestHut_Root (placeholder)", x, y, rot)
    block_building(top, r, "S4_ForestHut", 4, 4, 2.6, pal["roof_brown"], pal["placeholder"], 1.0)
    x, y, rot = loc_of("S5"); r = root(top, "S5_ExhibitionHall_Cafeteria_Root (placeholder)", x, y, rot)
    block_building(top, r, "S5_ExhibitionHall", 12, 13, 4.0, M("DarkBrownRoof", (0.18, 0.08, 0.05), 0.7), pal["placeholder"], 2.0)
    ra = root(top, "S5b_GreyAnnex_Root (placeholder)", x - 8, y - 5, rot); ra.parent = None
    block_building(top, ra, "S5b_GreyAnnex", 12, 11, 3.5, pal["zinc"], pal["placeholder"], 1.2)
    x, y, rot = loc_of("S6"); r = root(top, "S6_BrownRoofBuilding_Root (placeholder)", x, y, rot)
    block_building(top, r, "S6_BrownRoofBuilding", 15, 9, 3.2, pal["roof_brown"], pal["placeholder"], 1.6)
    finish(top, os.path.join(OUT, "penang_war_museum_S_satellite_placeholders.blend"), "S1-S6 satellite-only structures (massing placeholders)")


# =============================================================== R01-R37 + named sketch features
def octagon_pillbox(col, parent, name):
    p = Part(col, name + "_Body", pal["concrete"], parent)
    n = 8; r = 2.2
    prof = [(r * math.cos(R(22.5 + 45 * i)), r * math.sin(R(22.5 + 45 * i))) for i in range(n)]
    vs = [p.bm.verts.new((px, py, 0)) for px, py in prof]
    f = p.bm.faces.new(vs); e = bmesh.ops.extrude_face_region(p.bm, geom=[f])
    for v in [g for g in e["geom"] if isinstance(g, bmesh.types.BMVert)]: v.co.z = 1.9
    p.cyl(2.55, 0.3, (0, 0, 2.05), seg=8)
    p.done()
    s = Part(col, name + "_Loopholes", pal["dark"], parent)
    for k in range(7):
        a = R(45 * k); s.box((0.1, 0.6, 0.22), (2.0 * math.cos(a), 2.0 * math.sin(a), 1.3), (0, 0, a))
    s.done()


def portal(col, parent, name, w=2.4, depth=3.0):
    p = Part(col, name + "_ConcretePortal", pal["concrete"], parent)
    prof = [(-w / 2 - 0.4, 0), (w / 2 + 0.4, 0), (w / 2 + 0.4, 2.6), (-w / 2 - 0.4, 2.6)]
    p.prism(prof, 0.5, (0, -depth / 2, 0)); p.done()
    d = Part(col, name + "_DarkOpening", pal["dark"], parent)
    arch = [(-w / 2, 0), (w / 2, 0), (w / 2, 1.4)] + [(w / 2 * math.cos(math.pi * i / 12), 1.4 + w / 2 * math.sin(math.pi * i / 12)) for i in range(1, 12)] + [(-w / 2, 1.4)]
    d.prism(arch, 0.55, (0, -depth / 2 - 0.02, 0)); d.done()
    m = Part(col, name + "_EarthMound", pal["earth"], parent, smooth=True); m.sphere(1, (0, 1.0, 0.3), (w + 1.5, depth + 1.0, 2.4)); m.done()


def gun_bay(col, parent, name):
    p = Part(col, name + "_Parapet", pal["concrete"], parent, smooth=True); p.ring(3.0, 3.6, 0, 1.0, 0, 200, 48); p.done()
    q = Part(col, name + "_Floor_Plinth", pal["concrete_dark"], parent); q.cyl(3.0, 0.1, (0, 0, 0.05), seg=32); q.cyl(0.9, 0.4, (0, 0, 0.2), seg=24); q.done()


def sketch_relics():
    top = collection("PWM_R_SketchMapRelics_Approx")
    cannon = append_mesh(os.path.join(BAKED, "PH_Cannon01.blend"), "PH_Cannon01") if BAKED else None
    crate = append_mesh(os.path.join(BAKED, "PH_WoodenMilitaryCrate.blend"), "PH_WoodenMilitaryCrate") if BAKED else None
    ammo = append_mesh(os.path.join(BAKED, "PH_AmmoBox.blend"), "PH_AmmoBox") if BAKED else None
    ROT = -154.0       # sketch->site rotation from the fit
    barracks = {6, 7, 13, 14, 15, 16, 18, 20, 21, 22}
    ph, rf = pal["placeholder"], pal["placeholder_roof"]
    for key, r in P.items():
        if r["type"] not in ("sketch_relic", "sketch_feature"): continue
        x, y = float(r["model_x"]), float(r["model_y"])
        lab = r["name"].replace("/", "-").replace(",", "")
        if r["type"] == "sketch_relic":
            no = int(key[1:]); nm = f"R{no:02d}_{lab.replace(' ', '_')}"
        else:
            no = 0; nm = "F_" + lab.replace(" ", "_")
            if lab in ("Information & ticketing", "Souvenir", "Cafeteria", "Toilet"):
                continue      # already modelled (entrance2 / amenities / S5)
        rt = root(top, nm + " (approx. sketch position)", x, y, ROT)
        L = lab.lower()
        if no in barracks:
            block_building(top, rt, nm, 18, 6, 3.2, M("BarrackZincRoof", (0.4, 0.38, 0.35), 0.5, 0.4), M("BarrackWhitewash", (0.78, 0.76, 0.7), 0.85), 1.5)
        elif no in (12, 17):
            block_building(top, rt, nm, 14, 7, 3.2, rf, ph, 1.6, chimney=True)
        elif "pill box" in L:
            octagon_pillbox(top, rt, nm)
        elif no in (3, 9, 10):
            block_building(top, rt, nm, 11 if no != 3 else 10, 7, 3.4, rf, ph, 1.5)
        elif no in (4, 11, 19):
            block_building(top, rt, nm, 8, 5, 3.0, pal["concrete"], ph, 0)
            if no == 19:
                gg = Part(top, nm + "_CellBars", pal["grille"], rt)
                for k in range(10): gg.box((0.03, 0.03, 1.2), (-2.5 + k * 0.12, -2.55, 1.5))
                gg.done()
        elif no == 5:
            t = Part(top, nm + "_SeatingTiers", pal["concrete"], rt)
            for k in range(4): t.ring(4 + k * 1.2, 5.2 + k * 1.2, 0, 0.4 * (k + 1), 200, 340, 32)
            t.box((6, 3, 0.5), (0, -2.0, 0.25)); t.done()
        elif no in (8, 23, 26, 29) or "torture" in L:
            portal(top, rt, nm)
            if no == 23:
                h = Part(top, nm + "_TankSlab_Hatch", pal["concrete"], rt); h.box((8, 8, 0.4), (0, 4, 1.2)); h.box((0.8, 0.8, 0.3), (0, 4, 1.55)); h.done()
        elif no == 24:
            o = Part(top, nm + "_ObservationTower", pal["concrete"], rt); o.boxz((3, 3, 5.0), (0, 0, 0)); o.box((3.8, 3.8, 0.3), (0, 0, 5.15)); o.done()
            s = Part(top, nm + "_ViewSlits", pal["dark"], rt)
            for a in range(4): s.box((0.1, 2.0, 0.25), (1.52 * math.cos(R(90 * a)), 1.52 * math.sin(R(90 * a)), 4.3), (0, 0, R(90 * a)))
            s.done()
        elif no in (25, 27):
            gun_bay(top, rt, nm)
        elif no == 28:
            w = Part(top, nm + "_WellRing", pal["rubble"], rt, smooth=True); w.ring(0.8, 1.05, 0, 0.8, 0, 360, 24); w.done()
            f = Part(top, nm + "_WellFrame", pal["timber"], rt); f.boxz((0.12, 0.12, 2.0), (-1.0, 0, 0)); f.boxz((0.12, 0.12, 2.0), (1.0, 0, 0)); f.box((2.2, 0.12, 0.12), (0, 0, 2.0)); f.done()
        elif no == 30:
            s = Part(top, nm + "_SandbagRing", pal["sandbag"], rt, smooth=True); s.ring(2.5, 3.3, 0, 0.9, 0, 360, 40); s.done()
            p = Part(top, nm + "_GunPedestal", pal["steel"], rt); p.cyl(0.35, 1.0, (0, 0, 0.5)); p.done()
        elif no == 31:
            s = Part(top, nm + "_SpikedStakes", pal["timber_light"], rt)
            for k in range(30):
                px, py = random.uniform(-4, 4), random.uniform(-4, 4)
                s.rod((px, py, 0), (px + random.uniform(-0.3, 0.3), py + random.uniform(-0.3, 0.3), random.uniform(0.6, 1.1)), 0.035, 6)
            s.done()
        elif no == 32:
            g = Part(top, nm + "_GallowFrame", pal["timber"], rt)
            g.boxz((2.2, 2.2, 1.3), (0, 0, 0)); g.boxz((0.2, 0.2, 3.2), (-0.9, 0, 1.3)); g.boxz((0.2, 0.2, 3.2), (0.9, 0, 1.3)); g.box((2.2, 0.2, 0.2), (0, 0, 4.5))
            g.beam((-0.9, 0, 3.8), (-0.3, 0, 4.4), 0.1); g.done()
            n = Part(top, nm + "_Rope", pal["rope"], rt); n.rod((0, 0, 4.4), (0, 0, 3.2), 0.02); n.done()
        elif no == 33:
            t = Part(top, nm + "_TrenchSandbags", pal["sandbag"], rt)
            zz = [(-10, 0), (-6, 2), (-2, -1), (2, 2), (6, -1), (10, 1)]
            for (ax, ay), (bx, by) in zip(zz, zz[1:]):
                for s in (-0.8, 0.8): t.beam((ax, ay + s, 0.3), (bx, by + s, 0.3), 0.6, 0.6)
            t.done()
        elif no == 34:
            g = Part(top, nm + "_GuillotineFrame", pal["timber"], rt)
            g.boxz((1.4, 2.4, 0.3), (0, 0, 0)); g.boxz((0.15, 0.15, 3.2), (-0.35, 0, 0.3)); g.boxz((0.15, 0.15, 3.2), (0.35, 0, 0.3)); g.box((0.9, 0.2, 0.15), (0, 0, 3.5)); g.done()
            b = Part(top, nm + "_Blade", pal["steel"], rt); b.box((0.55, 0.05, 0.35), (0, 0, 2.8)); b.done()
        elif no == 35 or "armoury" in L:
            v = Part(top, nm + "_ArmouryVault", pal["concrete"], rt)
            prof = [(-2, 0), (2, 0), (2, 1.0)] + [(2 * math.cos(math.pi * i / 16), 1.0 + 2 * math.sin(math.pi * i / 16)) for i in range(1, 16)] + [(-2, 1.0)]
            v.prism(prof, 5, (0, 0, 0)); v.done()
            d = Part(top, nm + "_SteelDoor", pal["camo"], rt); d.box((1.0, 0.06, 2.0), (0, -2.53, 1.0)); d.done()
            if crate:
                instance(top, nm + "_PH_WoodenMilitaryCrate", crate, (-1.2, -3.4, 0), 0.3, 1.0, rt)
                for k in range(3): instance(top, nm + f"_PH_AmmoBox_{k}", ammo, (0.6 + k * 0.3, -3.3, 0), 0.0, 1.0, rt)
        elif no == 36:
            pad = Part(top, nm + "_ConcretePad", pal["concrete"], rt); pad.box((3.5, 3.5, 0.2), (0, 0, 0.1)); pad.done()
            if cannon:
                instance(top, nm + "_PH_Cannon01", cannon, (0, 0, 0.2 + 0.67), 0.0, 1.0, rt).rotation_euler = (0, math.pi, 0)
        elif "car park" in L:
            p = Part(top, nm + "_AsphaltPad", pal["asphalt"], rt); p.box((18, 12, 0.05), (0, 0, 0.025)); p.done()
        elif "water tank" in L:
            t = Part(top, nm + "_WaterTank", M("TankSteel", (0.55, 0.56, 0.55), 0.5, 0.6), rt, smooth=True); t.cyl(2.0, 3.0, (0, 0, 3.5)); t.done()
            s = Part(top, nm + "_TankStand", pal["steel"], rt)
            for a in range(4): s.rod((1.4 * math.cos(R(45 + 90 * a)), 1.4 * math.sin(R(45 + 90 * a)), 0), (1.4 * math.cos(R(45 + 90 * a)), 1.4 * math.sin(R(45 + 90 * a)), 2.0), 0.08)
            s.done()
        elif "generator" in L:
            block_building(top, rt, nm, 6, 5, 3.0, pal["zinc"], ph, 0.8)
        elif "jetty" in L:
            j = Part(top, nm + "_TimberDeck", pal["timber_light"], rt); j.box((20, 3, 0.2), (0, 0, 1.2))
            for k in range(8):
                for s in (-1.3, 1.3): j.cyl(0.15, 2.6, (-9.5 + k * 2.7, s, 0.1))
            j.done()
        elif "submarine" in L:
            s = Part(top, nm + "_Slipway", pal["concrete"], rt); s.quad([(-3, -5, 0.6), (3, -5, 0.6), (3, 5, -0.8), (-3, 5, -0.8)]); s.done()
        elif "vip" in L:
            p = Part(top, nm + "_AsphaltPad", pal["asphalt"], rt); p.box((12, 8, 0.05), (0, 0, 0.025)); p.done()
        else:
            block_building(top, rt, nm, 8, 6, 3.0, rf, ph, 1.2)
    finish(top, os.path.join(OUT, "penang_war_museum_R_sketch_relics.blend"), "R01-R37 + named features from the museum sketch map (approximate massing)")


{"gun_emplacement": gun_emplacement, "watchtower": watchtower, "bunker": bunker, "amenities": amenities,
 "walkway": walkway, "courtyard": courtyard, "barrack_blue": barrack_blue, "satellite": satellite,
 "sketch_relics": sketch_relics}[TARGET]()
