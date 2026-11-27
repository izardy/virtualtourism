#!/usr/bin/env python3
"""Download CC0 PBR materials from ambientCG (https://ambientcg.com) into blender/assets/ambientcg/<id>/ (1K)
or blender/assets/ambientcg2k/<id>/ (2K, used first by build_muzium.py when present).
Re-run safe. Usage: python3 blender/scripts/fetch_ambientcg.py [2K]"""
import io, os, sys, urllib.request, zipfile
RES = sys.argv[1] if len(sys.argv) > 1 else "1K"

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "ambientcg" + ("2k" if RES == "2K" else ""))
UA = {"User-Agent": "VirtualTourism-hackathon/0.1 (asset fetch script)"}
IDS = [
    "Concrete042A", "Concrete044D", "Concrete031", "Concrete032",              # weathered fort concrete, pitted concrete, floors
    "PaintedPlaster009", "PaintedPlaster012", "PaintedPlaster015",             # peeling green paint, olive paint, whitewash
    "Bricks108B", "Rock064",                                                   # mossy stone walls
    "Metal041B", "Metal022", "CorrugatedSteel007B",                            # rusty paint, rusty metal, old roof
    "Ground037", "Ground077", "Ground082S", "Asphalt031", "Planks023A",        # mossy forest floor, laterite path, litter, road, grey planks
]
for aid in IDS:
    d = os.path.join(ROOT, aid)
    if os.path.isdir(d) and any(f.endswith("_Color.jpg") for f in os.listdir(d)):
        continue
    os.makedirs(d, exist_ok=True)
    url = f"https://ambientcg.com/get?file={aid}_{RES}-JPG.zip"
    try:
        data = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120).read()
        zipfile.ZipFile(io.BytesIO(data)).extractall(d)
        print("ok", aid, len(data) // 1024, "KB", flush=True)
    except Exception as e:
        print("FAIL", aid, e, flush=True)
