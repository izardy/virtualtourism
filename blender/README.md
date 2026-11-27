# Blender: Muzium Perang Penang model

First build of the 3D site. Since 2026-11-27 the layout strictly follows the reeaki "Fort Relics" visitor map: `scripts/extract_reeaki.py` turns the map into `reference/sitemap/reeaki_layout.json` (positions, building angles, hill, bay and sand bar, paths, roads, trees), and `build_muzium.py` and `place_props.py` read it. The map is schematic, so distances are approximate (about 0.55 m per map pixel). Everything is a PROVISIONAL blockout, not a survey. Run the extractor (any Python with numpy, Pillow, scipy and scikit-image) before the Blender pipeline whenever it changes.

## Rebuild
1. Open Blender 5.x with the MCP add-on running (or paste the scripts in the Scripting tab).
2. Run, in order (each via `exec(open(path).read())`):
   - `blender/scripts/build_muzium.py`: terrain, sea, 37 map structures plus facilities, paths, road, hotspot and `loc_*` empties, spawn
   - (`build_muzium.py` runs `blender/scripts/user_models.py` itself: it bakes the user's own models in `blender/user_models/`, the type-1 and type-2 pill boxes and the entrance, into the scene)
   - `blender/scripts/place_props.py`: decimated Poly Haven props, low-poly trees, scatter
   - `blender/scripts/build_tour_paths.py`: computes the guided-tour routes on the live scene and writes `app/static/data/muzium_perang_tour.json` (re-run whenever the model or hotspots change)
   - `blender/scripts/export_muzium.py`: writes `blender/out/muzium_perang_raw.glb`
   - `blender/scripts/export_mobile.py`: writes `blender/out/muzium_perang_mobile_raw.glb` (phone version: Poly Haven 1k textures, every tree one tier cheaper, half the distant trees); it restores the scene afterwards
3. `sh blender/scripts/optimize_glb.sh` writes `app/static/models/muzium_perang.glb` (textures capped at 2048 px); `sh blender/scripts/optimize_glb.sh mobile` writes `app/static/models/muzium_perang_mobile.glb` (1024 px). In both, the small Poly Haven props listed in `PROPS` in the script are capped at 512 px; add new small props to that list.
4. Re-download Poly Haven assets if needed: `python3 blender/scripts/fetch_polyhaven.py` (building and ground materials go to `textures_2k/` and `textures_1k/`).

## Outputs
- `app/static/models/muzium_perang.glb`: desktop, 35.0 MB, 2.47M triangles, Draco geometry, WebP textures at most 2048 px
- `app/static/models/muzium_perang_mobile.glb`: phones and tablets, 14.7 MB, about 0.9M triangles, textures at most 1024 px. The viewer picks it when the pointer is coarse and the short screen side is at most 900 px; `?quality=full` or `?quality=lite` overrides.
- `blender/out/hotspots.json`: the 10 hotspot positions (Blender and glTF axes, with a provisional flag) for `app/seed_data.py`
- `blender/out/site_points.json`: all 57 map and facility markers (glTF axes) for labels
- `blender/src/muzium_perang.blend`

## Node conventions in the GLB
- Walkable: `ground_terrain`, `floor_floor`, `floor_paths`, `floor_road`, `floor_asphalt`
- `spawn`: start position, faces west through the ticket building
- `hotspot_<slug>` (10), `loc_<n>_<name>` (map points 1 to 37), `loc_fac_*` (facilities), `loc_escape_route_shaft`, `loc_memorial_plaque`
- Axes after export: x east, y up, z south

## Known limitations
- Provisional placements: memorial plaque, escape route (shaft climb is only 4.4 m instead of 9 m because the DEM hill is not steep enough there), lookout point, Japanese tunnel, underground bunker.
- Building sizes are inferred from photos and the standard 1930s 6-inch coast battery layout (no dimensions are published; see `reference/NOTES.md`, "Building research"). Gun bays, lock-up cells, exhibition rooms, the memorial and the tunnels have interiors built from the reference photos. The office (3), intelligence room (11), communication centre (8), armoury (35), generator room (6) and cook houses (12, 17) are fitted out with Poly Haven furniture and clutter; the other buildings are still empty inside.
- Terrain comes from the reeaki map (`extract_reeaki.py`), so slopes are approximate.
- The Poly Haven cannon is a naval-style stand-in. Trees are Poly Haven island trees thinned by `thin_tree.py` into four tiers (303 trees: 38 background, 6 hero, 135 far, 130 distant) plus a phone tier (`tpl_tree_mob`, about 2k triangles) used only by the phone model.
- The desktop GLB has many materials and images. Phones get the lighter `_mobile` model; a shared texture atlas for props would cut draw calls further.
- The optimizer step skips `flatten`, `join` and `prune` on purpose, because they delete empty marker nodes.
