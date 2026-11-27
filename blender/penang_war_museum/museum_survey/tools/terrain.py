"""Terrain height model for the Penang War Museum site (pure Python, usable inside Blender).

ground_asl(E, N): SRTM 30 m (bilinear) corrected toward ground-truth Street View altitudes.
z_model(x, y):    height in the Blender model frame (x = -E, y = -N), 0 at the gate front O.

SRTM is a surface model: under the forest canopy it reads ~5-12 m too high. Street View camera
altitudes (URL "NNa" value, camera ~2 m above ground) along the visitor paths give the ground truth;
their residuals are spread with inverse-distance weighting and fade to a default canopy correction.
"""
import json, math, os

HERE = os.path.dirname(os.path.abspath(__file__))
D = json.load(open(os.path.join(HERE, "terrain_srtm.json")))
ES, NS, G = D["E"], D["N"], D["elev_rowsN_colsE"]
STEP = ES[1] - ES[0]
CAM_H = 2.0
# (E, N, Street View camera altitude) from the survey walk
SV = [(-0.8, 4.8, 72), (0.1, 1.1, 71), (1.0, -4.9, 71), (1.8, -11.5, 72), (2.8, -17.4, 72), (4.6, -24.3, 73),
      (8.4, -29.0, 73), (17.9, -37.8, 72), (26.6, -45.3, 72), (34.7, -53.6, 71), (43.1, -60.6, 71),
      (59.3, -68.5, 69), (65.5, -71.1, 69), (70.7, -73.6, 68), (75.6, -76.0, 67), (81.0, -79.4, 67),
      (86.6, -82.6, 66), (91.2, -87.1, 65), (-1.1, -70.7, 76), (-6.9, -74.7, 76)]
DEFAULT_CORR = -10.0           # mean canopy over-read measured on the forested Street View points
R_INFL = 60.0                  # metres over which a Street View residual fades to the default


def srtm(E, N):
    fx = (E - ES[0]) / STEP; fy = (N - NS[0]) / STEP
    i = max(0, min(len(ES) - 2, int(math.floor(fx)))); j = max(0, min(len(NS) - 2, int(math.floor(fy))))
    tx = min(1, max(0, fx - i)); ty = min(1, max(0, fy - j))
    a, b = G[j][i], G[j][i + 1]; c, d = G[j + 1][i], G[j + 1][i + 1]
    return (a * (1 - tx) + b * tx) * (1 - ty) + (c * (1 - tx) + d * tx) * ty


RES = [(e, n, (alt - CAM_H) - srtm(e, n)) for e, n, alt in SV]


def correction(E, N):
    num = den = 0.0; near = 1e9
    for e, n, r in RES:
        d = math.hypot(E - e, N - n); near = min(near, d)
        w = 1.0 / (d * d + 25.0)
        num += w * r; den += w
    idw = num / den
    blend = max(0.0, min(1.0, near / R_INFL))
    return idw * (1 - blend) + DEFAULT_CORR * blend


def ground_asl(E, N):
    s = srtm(E, N)
    if s <= 0.5:
        return s                                   # sea / shoreline: leave at sea level
    corr = correction(E, N) * min(1.0, s / 12.0)   # fade correction out toward the coast
    return max(0.0, s + corr)


GATE_ASL = ground_asl(0.0, 0.0)   # pin the gate front O to z = 0


def z_model(x, y):
    return ground_asl(-x, -y) - GATE_ASL


SEA_Z = -GATE_ASL

if __name__ == "__main__":
    for e, n, alt in SV:
        print(f"SV ({e:6.1f},{n:6.1f}) ground {alt - CAM_H:5.1f}  model {ground_asl(e, n):5.1f}  srtm {srtm(e, n):5.1f}")
    for nm, E, N in (("O gate", 0, 0), ("B17 gun", 66.6, -105.6), ("B15 barrack", -2, -74), ("summit area", -60, -120)):
        print(nm, "ASL", round(ground_asl(E, N), 1), "z", round(ground_asl(E, N) - GATE_ASL, 1))
