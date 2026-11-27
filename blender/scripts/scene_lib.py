"""Shared scene materials for the Muzium Perang builders (exec'd by build_muzium.py and twin_build.py).
Needs ROOT and TEX in the caller's globals. Poly Haven (CC0) and ambientCG (CC0) PBR materials, the tile sizes used by
uv_box(), and uv_box() itself (box-projected UVs in metres)."""
import bpy, os

# ---------------------------------------------------------------- materials
ACG = ROOT + "/blender/assets/ambientcg"
ACG2 = ROOT + "/blender/assets/ambientcg2k"      # 2K sets (fetch_ambientcg.py 2K); used when present
PH2 = ROOT + "/blender/assets/polyhaven/textures_2k"   # Poly Haven building/ground materials at 2k (fetch_polyhaven.py);
                                                        # export_mobile.py swaps them for the textures_1k copies

def make_mat(name, folder=None, tint=None, rough=0.9, color=(0.5, 0.5, 0.5, 1), metal=0.0, emit=None):
    """PBR material from a Poly Haven folder (textures_2k/<id> or textures/<id>) or an ambientCG folder (ambientcg/<id>); or a flat colour."""
    m = bpy.data.materials.new(name)
    try: m.use_nodes = True
    except Exception: pass
    try: m.use_backface_culling = True
    except Exception: pass
    nt = m.node_tree
    for n in list(nt.nodes): nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial"); bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    bsdf.inputs["Roughness"].default_value = rough; bsdf.inputs["Metallic"].default_value = metal
    if folder:
        acg = os.path.isdir(os.path.join(ACG, folder)) or os.path.isdir(os.path.join(ACG2, folder))
        if acg: d = os.path.join(ACG2, folder) if os.path.isdir(os.path.join(ACG2, folder)) else os.path.join(ACG, folder)
        else: d = os.path.join(PH2, folder) if os.path.isdir(os.path.join(PH2, folder)) else os.path.join(TEX, folder)
        fs = sorted(os.listdir(d))
        def tex(ph_key, acg_key, nonc):
            keys = ("_diff_", "_diffuse_") if ph_key == "diff" else ("_%s_" % ph_key,)
            f = next((x for x in fs if (x.endswith("_%s.jpg" % acg_key) if acg else any(k in x for k in keys))), None)
            if not f: return None
            n = nt.nodes.new("ShaderNodeTexImage"); n.image = bpy.data.images.load(os.path.join(d, f), check_existing=True)
            if nonc: n.image.colorspace_settings.name = "Non-Color"
            return n
        dn = tex("diff", "Color", False)
        if dn:
            if tint:
                mix = nt.nodes.new("ShaderNodeMix"); mix.data_type = "RGBA"; mix.blend_type = "MULTIPLY"
                mix.inputs[0].default_value = 1.0; mix.inputs[7].default_value = tint
                nt.links.new(dn.outputs["Color"], mix.inputs[6]); nt.links.new(mix.outputs[2], bsdf.inputs["Base Color"])
            else:
                nt.links.new(dn.outputs["Color"], bsdf.inputs["Base Color"])
        rn = tex("rough", "Roughness", True)
        if rn: nt.links.new(rn.outputs["Color"], bsdf.inputs["Roughness"])
        nn = tex("nor_gl", "NormalGL", True)
        if nn:
            nm = nt.nodes.new("ShaderNodeNormalMap"); nt.links.new(nn.outputs["Color"], nm.inputs["Color"]); nt.links.new(nm.outputs["Normal"], bsdf.inputs["Normal"])
    else:
        bsdf.inputs["Base Color"].default_value = color
    if emit:
        bsdf.inputs["Emission Color"].default_value = (emit[0], emit[1], emit[2], 1); bsdf.inputs["Emission Strength"].default_value = emit[3]
    return m

MATS = {
    "ground":   make_mat("mat_ground_moss", "forest_leaves_02"),
    "soil":     make_mat("mat_laterite_path", "red_laterite_soil_stones"),
    "conc":     make_mat("mat_concrete", "concrete_wall_006"),
    "conc_g":   make_mat("mat_paint_green", "worn_mossy_plasterwall", tint=(0.70, 0.82, 0.62, 1)),
    "conc_w":   make_mat("mat_concrete_pitted", "concrete_layers_02"),
    "floor":    make_mat("mat_floor", "concrete_floor_02"),
    "brick":    make_mat("mat_stone", "mossy_stone_wall"),
    "redbrick": make_mat("mat_red_brick", "brick_4"),          # Poly Haven brick_4: the user's entrance model (Brick)
    "rust":     make_mat("mat_rust_paint", "rusty_metal_02", metal=0.5),
    "roof":     make_mat("mat_corrugated_roof", "corrugated_iron", metal=0.15, tint=(0.85, 0.78, 0.70, 1)),
    "glass":    make_mat("mat_window_glass", color=(0.03, 0.045, 0.05, 1), rough=0.08, metal=0.6),
    "glass_lit": make_mat("mat_window_lit", color=(0.9, 0.7, 0.4, 1), rough=0.3, emit=(1.0, 0.72, 0.38, 1.6)),
    "plaster":  make_mat("mat_whitewash", "worn_plaster_wall"),
    "rock":     make_mat("mat_mossy_rock", "mossy_rock"),
    "grate":    make_mat("mat_rusty_metal", "rusty_metal_03", metal=0.6),
    "wood":     make_mat("mat_planks", "weathered_planks"),
    "black":    make_mat("mat_black_granite", color=(0.02, 0.02, 0.02, 1), rough=0.25),
    "steel":    make_mat("mat_steel", color=(0.62, 0.63, 0.65, 1), rough=0.35, metal=0.9),
    "paper":    make_mat("mat_exhibit_print", color=(0.78, 0.74, 0.64, 1), rough=0.8),
    "asphalt":  make_mat("mat_asphalt", "asphalt_02"),
    "water":    make_mat("mat_sea", color=(0.03, 0.2, 0.32, 1), rough=0.08, metal=0.0),
    "camo":     make_mat("mat_paint_olive", "worn_mossy_plasterwall", tint=(0.62, 0.64, 0.45, 1)),
    "yellow":   make_mat("mat_sign_yellow", color=(0.95, 0.72, 0.08, 1), rough=0.45, emit=(0.95, 0.7, 0.1, 0.35)),
    "lamp":     make_mat("mat_lamp_glow", color=(1, 0.9, 0.6, 1), emit=(1.0, 0.85, 0.5, 6.0)),
    "flag_red": make_mat("mat_flag_red", color=(0.75, 0.05, 0.08, 1), rough=0.9),
    "flag_blue": make_mat("mat_flag_blue", color=(0.05, 0.12, 0.55, 1), rough=0.9),
    "flag_white": make_mat("mat_flag_white", color=(0.9, 0.9, 0.88, 1), rough=0.9),
}
FLOOR_MATS = {"floor", "asphalt"}      # these become floor_* objects (walkable)
# metres per texture repeat = the real-world size Poly Haven gives for each texture
TILE = {"ground": 3.0, "soil": 2.0, "water": 50.0, "asphalt": 3.0, "conc": 2.0, "conc_g": 1.8, "conc_w": 2.0, "camo": 1.8, "plaster": 1.8,
        "floor": 2.0, "brick": 2.0, "redbrick": 2.0, "rock": 3.0, "rust": 1.0, "roof": 1.12, "glass": 1.0, "glass_lit": 1.0, "grate": 1.35, "wood": 2.0, "black": 1.0}


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
