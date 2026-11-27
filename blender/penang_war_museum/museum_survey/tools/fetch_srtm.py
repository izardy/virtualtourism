"""Download a SRTM 30 m elevation grid around the site origin from OpenTopoData into terrain_srtm.json.
python3 fetch_srtm.py  [O_LAT O_LON  E_MIN E_MAX N_MIN N_MAX STEP]
Defaults are the Penang War Museum values. The public API allows 100 points per call and ~1 call/s."""
import json, urllib.request, time, sys, os
a = [float(v) for v in sys.argv[1:]]
O_LAT, O_LON, E0, E1, N0, N1, STEP = a if len(a) == 7 else (5.281400, 100.288800, -350, 450, -330, 245, 25.0)
KE, KN = 110847.0, 110574.0          # metres per degree of lon / lat at ~5.3 N (recompute for other latitudes)
Es = [E0 + i * STEP for i in range(int((E1 - E0) / STEP) + 1)]
Ns = [N0 + j * STEP for j in range(int((N1 - N0) / STEP) + 1)]
pts = [(O_LAT + N / KN, O_LON + E / KE) for N in Ns for E in Es]
elev = []
for k in range(0, len(pts), 100):
    q = "|".join(f"{la:.6f},{lo:.6f}" for la, lo in pts[k:k + 100])
    url = "https://api.opentopodata.org/v1/srtm30m?interpolation=bilinear&locations=" + q
    for attempt in range(4):
        try:
            d = json.load(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "blender-terrain-builder"}), timeout=60)); break
        except Exception as e:
            print("retry", e); time.sleep(3)
    elev += [r["elevation"] for r in d["results"]]
    time.sleep(1.1)
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "terrain_srtm.json")
json.dump({"dataset": "SRTM 30m (OpenTopoData, bilinear)", "origin": [O_LAT, O_LON], "E": Es, "N": Ns,
           "elev_rowsN_colsE": [elev[j * len(Es):(j + 1) * len(Es)] for j in range(len(Ns))]}, open(out, "w"))
vals = [v for v in elev if v is not None]
print("points", len(elev), "none", elev.count(None), "min", min(vals), "max", max(vals), "->", out)
