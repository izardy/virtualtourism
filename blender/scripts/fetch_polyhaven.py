#!/usr/bin/env python3
"""Download CC0 assets from Poly Haven (https://polyhaven.com) into blender/assets/polyhaven/.
Usage: python3 blender/scripts/fetch_polyhaven.py   (re-run safe: skips existing files)
"""
import json, os, time, urllib.request

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "polyhaven")
UA = {"User-Agent": "VirtualTourism-hackathon/0.1 (asset fetch script)"}
RES = "1k"

MODELS = [
    # weapons / military props
    "cannon_01", "old_military_crate", "wooden_military_crate", "ammo_box", "metal_jerrycan_green",
    "old_military_compressor", "vintage_radio_transceiver", "wooden_barrels_01", "barrel_03",
    # lighting, doors, fences, misc
    "caged_hanging_light", "industrial_caged_sconce", "hanging_industrial_lamp", "wooden_ladder",
    "old_bed_frame", "modular_chainlink_fence", "large_iron_gate",
    # vegetation and rocks
    "island_tree_01", "island_tree_02", "island_tree_03", "pachira_aquatica_01", "fern_02",
    "shrub_01", "shrub_02", "shrub_03", "boulder_01", "coast_rocks_01", "coast_rocks_02",
    "rock_moss_set_01", "tree_stump_01", "root_cluster_01", "pine_roots",
]
TEXTURES = [
    "concrete_moss", "cracked_concrete_wall", "painted_concrete", "concrete_floor_worn_001",
    "mossy_brick", "rusty_metal_02", "corrugated_iron", "forest_ground_04",
    "red_laterite_soil_stones", "grey_plaster", "rock_wall_08", "rusty_metal_grid",
]
HDRIS = ["fish_hoek_beach"]


def get_json(url):
    return json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60))


def fetch(url, dest):
    if os.path.exists(dest) and os.path.getsize(dest) > 0:
        return
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    for a in range(4):
        try:
            data = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120).read()
            open(dest, "wb").write(data)
            time.sleep(0.3)
            return
        except Exception as e:
            print("  retry", dest, e, flush=True)
            time.sleep(5 * (a + 1))
    print("  FAILED", url, flush=True)


for aid in MODELS:
    try:
        f = get_json(f"https://api.polyhaven.com/files/{aid}")["gltf"][RES]["gltf"]
        base = os.path.join(ROOT, "models", aid)
        fetch(f["url"], os.path.join(base, os.path.basename(f["url"])))
        for rel, inc in f.get("include", {}).items():
            fetch(inc["url"], os.path.join(base, rel))
        print("model ok", aid, flush=True)
    except Exception as e:
        print("model FAIL", aid, e, flush=True)

for aid in TEXTURES:
    try:
        files = get_json(f"https://api.polyhaven.com/files/{aid}")
        for m in ("Diffuse", "nor_gl", "Rough"):
            if m in files and RES in files[m] and "jpg" in files[m][RES]:
                u = files[m][RES]["jpg"]["url"]
                fetch(u, os.path.join(ROOT, "textures", aid, os.path.basename(u)))
        print("texture ok", aid, flush=True)
    except Exception as e:
        print("texture FAIL", aid, e, flush=True)

for aid in HDRIS:
    try:
        u = get_json(f"https://api.polyhaven.com/files/{aid}")["hdri"][RES]["hdr"]["url"]
        fetch(u, os.path.join(ROOT, "hdris", os.path.basename(u)))
        print("hdri ok", aid, flush=True)
    except Exception as e:
        print("hdri FAIL", aid, e, flush=True)
print("DONE", flush=True)
