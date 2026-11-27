"""Guided tour routes for Muzium Perang Penang (run inside Blender after build_muzium.py + place_props.py).

For every stop of the tour it runs A* on a 1.5 m grid over the real model (ray casts against the terrain/floors for
height and slope, against struct_* meshes for walls), then straightens the route with line-of-sight checks.
Writes app/static/data/muzium_perang_tour.json in glTF axes (x east, y up, z south).

    exec(open("/Users/izardy/Documents/virtualtourism/blender/scripts/build_tour_paths.py").read())
"""
import bpy, bmesh, math, json, heapq, os
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT = "/Users/izardy/Documents/virtualtourism"
HOT = json.load(open(ROOT + "/blender/out/hotspots.json"))
SC = bpy.context.scene
TWIN = bool(SC.get("twin", False))            # scene from twin_build.py
SEA_Z = float(SC.get("sea_z", -36.0))
STEP = 1.5
X0, Y0, X1, Y1 = tuple(SC["bounds"]) if TWIN else (-330.0, -260.0, 300.0, 260.0)
RADIUS = 0.45

# the order of the story: purpose of the fort, the sea view, the tunnels, the command rooms, the prison, then remembrance
ORDER = [
    ("main-entrance", "Main Entrance"), ("weapons-display", "Weapons Display"), ("lookout-point", "Lookout Point"),
    ("japanese-tunnel", "Japanese Tunnel"), ("escape-route", "Escape Route"), ("observation-tower", "Observation Tower"),
    ("command-centre", "Command Centre"), ("underground-bunker", "Underground Bunker"), ("prison-area", "Prison Area"),
    ("memorial-zone", "Memorial Zone"),
]


def merged_bvh(pred):
    bm = bmesh.new()
    for o in bpy.data.objects:
        if o.type == "MESH" and pred(o.name):
            bm.from_mesh(o.data)
    bvh = BVHTree.FromBMesh(bm)
    bm.free()
    return bvh


GROUND = merged_bvh(lambda n: n == "ground_terrain" or n.startswith("floor_"))
WALLS = merged_bvh(lambda n: n.startswith("struct_"))
DOWN = Vector((0, 0, -1))


def ground_z(x, y, from_z):
    hit = GROUND.ray_cast(Vector((x, y, from_z)), DOWN, 80.0)
    return hit[0].z if hit[0] is not None else None


def blocked(ax, ay, az, bx, by):
    d = math.hypot(bx - ax, by - ay)
    if d < 1e-6:
        return False
    dirv = Vector(((bx - ax) / d, (by - ay) / d, 0))
    for h in (0.45, 1.2):
        if WALLS.ray_cast(Vector((ax, ay, az + h)), dirv, d + RADIUS)[0] is not None:
            return True
    return False


def clearance_cost(x, y, z):
    n = 0
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (0.7, 0.7), (-0.7, 0.7), (0.7, -0.7), (-0.7, -0.7)):
        if WALLS.ray_cast(Vector((x, y, z + 1.0)), Vector((dx, dy, 0)).normalized(), 1.1)[0] is not None:
            n += 1
    return n * 1.2


def step_ok(ax, ay, az, bx, by):
    """Returns the new ground height if the visitor can walk a->b, else None (same rules as the viewer)."""
    gz = ground_z(bx, by, az + 1.1)
    if gz is None or gz < SEA_Z + 0.8:
        return None
    d = math.hypot(bx - ax, by - ay)
    if gz - az > 0.35 + d * 1.1 or az - gz > 1.2:
        return None
    if blocked(ax, ay, az, bx, by):
        return None
    return gz


def los(a, b):
    """Straight walk a->b possible (sampled every 0.5 m)?"""
    d = math.hypot(b[0] - a[0], b[1] - a[1])
    n = max(1, int(d / 0.5))
    px, py, pz = a[0], a[1], a[2]
    for k in range(1, n + 1):
        t = k / n
        x, y = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
        gz = step_ok(px, py, pz, x, y)
        if gz is None:
            return None
        px, py, pz = x, y, gz
    return pz


def cell_xy(i, j): return X0 + i * STEP, Y0 + j * STEP
def to_cell(x, y): return round((x - X0) / STEP), round((y - Y0) / STEP)
NEI = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]


def astar(start, target, ring=(1.8, 4.6), margin=70, limit=80000):
    """start = (x, y, z); target = (x, y, feet_z). Goal = any walkable cell within `ring` metres (horizontally) of the target
    and within 3 m of its height (so the hill above a tunnel does not count).
    Returns (path [(x,y,z)], reached(bool), expansions)."""
    sx, sy, sz = start
    si, sj = to_cell(sx, sy)
    lo_x, hi_x = min(sx, target[0]) - margin, max(sx, target[0]) + margin
    lo_y, hi_y = min(sy, target[1]) - margin, max(sy, target[1]) + margin
    def h(x, y): return max(0.0, math.hypot(x - target[0], y - target[1]) - ring[0])
    openq = [(h(sx, sy), 0.0, si, sj)]
    came, gcost, zs = {(si, sj): None}, {(si, sj): 0.0}, {(si, sj): sz}
    clear = {}
    best, best_d = (si, sj), 1e9
    n = 0
    goal = None
    while openq and n < limit:
        f, g, i, j = heapq.heappop(openq)
        if g > gcost.get((i, j), 1e9) + 1e-9:
            continue
        n += 1
        x, y = cell_xy(i, j)
        z = zs[(i, j)]
        dt = math.hypot(x - target[0], y - target[1])
        dz = abs(z - target[2])
        if ring[0] <= dt <= ring[1] and dz < 3.0:
            goal = (i, j); break
        d3 = math.hypot(dt, dz * 2.0)
        if d3 < best_d:
            best_d, best = d3, (i, j)
        for di, dj in NEI:
            ni, nj = i + di, j + dj
            nx, ny = cell_xy(ni, nj)
            if not (lo_x <= nx <= hi_x and lo_y <= ny <= hi_y and X0 <= nx <= X1 and Y0 <= ny <= Y1):
                continue
            gz = step_ok(x, y, z, nx, ny)
            if gz is None:
                continue
            if (ni, nj) not in clear:
                clear[(ni, nj)] = clearance_cost(nx, ny, gz)
            d = math.hypot(nx - x, ny - y)
            ng = g + d * (1 + 0.5 * abs(gz - z) / d) + clear[(ni, nj)]
            if ng < gcost.get((ni, nj), 1e9):
                gcost[(ni, nj)] = ng; came[(ni, nj)] = (i, j); zs[(ni, nj)] = gz
                heapq.heappush(openq, (ng + h(nx, ny), ng, ni, nj))
    end = goal or best
    path = []
    c = end
    while c is not None:
        path.append((*cell_xy(*c), zs[c])); c = came[c]
    path.reverse()
    return path, goal is not None, n


def straighten(path):
    if len(path) < 3:
        return path
    out = [path[0]]; i = 0
    while i < len(path) - 1:
        j = len(path) - 1
        while j > i + 1:
            z = los(path[i], path[j])
            if z is not None:
                break
            j -= 1
        out.append(path[j]); i = j
    # keep waypoints at most ~6 m apart so the walker can adapt to terrain
    dense = [out[0]]
    for a, b in zip(out, out[1:]):
        d = math.hypot(b[0] - a[0], b[1] - a[1]); k = max(1, int(d / 6))
        for m in range(1, k + 1):
            t = m / k; x, y = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
            gz = ground_z(x, y, max(a[2], b[2]) + 1.1)
            dense.append((x, y, gz if gz is not None else b[2]))
    return dense


def gl(p): return [round(p[0], 2), round(p[2], 2), round(-p[1], 2)]       # blender (x, y, z) -> glTF (x, z, -y)


spawn = bpy.data.objects["spawn"].location
cur = (spawn.x, spawn.y, ground_z(spawn.x, spawn.y, spawn.z + 2) or spawn.z)

# The observation post stairs (1.2 m wide) are narrower than the 1.5 m search grid, so they are routed by hand:
# approach the foot of the stairs with A*, then follow the stairs straight to the platform. The way down is the reverse.
tx, ty, tz = HOT["observation-tower"]["blender_xyz"]
STAIR_FOOT, STAIR_TOP, PLAT = (tx + 10.9, ty), (tx + 2.8, ty), (tx + 1.3, ty)
def at(p, from_z): return (p[0], p[1], ground_z(p[0], p[1], from_z))
ENTER = {"observation-tower": [at((tx + 9.0, ty), tz + 1.0), at((tx + 5.5, ty), tz + 1.0), at(STAIR_TOP, tz + 1.0), at(PLAT, tz + 1.0)]}
LEAVE = {"observation-tower": [at(STAIR_TOP, tz + 1.0), at((tx + 5.5, ty), tz + 1.0), at((tx + 9.0, ty), tz + 1.0), at(STAIR_FOOT, tz + 1.0)]}
if TWIN: ENTER, LEAVE = {}, {}                # the twin's observation post is a placeholder without the stairs

stops, total, prefix = [], 0.0, []
for slug, title in ORDER:
    hx, hy, hz = HOT[slug]["blender_xyz"]
    jump = None
    if slug in ENTER:
        fz = ground_z(STAIR_FOOT[0], STAIR_FOOT[1], hz - 5.0) or cur[2]
        path, reached, n = astar(cur, (STAIR_FOOT[0], STAIR_FOOT[1], fz), ring=(0.0, 2.2))
        path = straighten(path) + ENTER[slug]
        reached = True
    else:
        path, reached, n = astar(cur, (hx, hy, hz - 1.6))
        path = straighten(path)
    path = prefix + path
    prefix = []
    last = path[-1]
    if not reached:        # not walkable all the way: fade-jump to a viewing spot facing the hotspot
        dx, dy = hx - last[0], hy - last[1]; d = math.hypot(dx, dy) or 1
        sx, sy = hx - dx / d * 2.2, hy - dy / d * 2.2
        gz = ground_z(sx, sy, hz + 0.5)
        jump = (sx, sy, gz if gz is not None else hz - 1.6)
        end = jump
    else:
        end = last
    length = sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(path, path[1:]))
    total += length
    yaw = math.atan2(-(hx - end[0]), hy - end[1])                   # camera yaw (glTF space) facing the hotspot
    stops.append({"slug": slug, "title": title, "path": [gl(p) for p in path], "jump": gl(jump) if jump else None,
                  "stand": gl(end), "yaw": round(yaw, 3), "length_m": round(length, 1)})
    print(f"{slug:20s} reached={reached!s:5s} expansions={n:6d} length={length:6.1f} m waypoints={len(path)} jump={'yes' if jump else 'no'}")
    if slug in LEAVE:
        prefix = list(LEAVE[slug]); cur = prefix[-1]
    else:
        cur = end

start = (spawn.x, spawn.y, ground_z(spawn.x, spawn.y, spawn.z + 2) or spawn.z)
out = {"version": 1, "walk_speed_mps": 2.0, "start": gl(start),
       "intro_audio": "audio/tour-intro.mp3", "outro_audio": "audio/tour-outro.mp3",
       "total_length_m": round(total, 1), "stops": stops}
os.makedirs(ROOT + "/app/static/data", exist_ok=True)
json.dump(out, open(ROOT + "/app/static/data/muzium_perang_tour.json", "w"), indent=1)
print("total walking distance:", round(total, 1), "m  -> about", round(total / 2.0 / 60, 1), "min at 2 m/s")
