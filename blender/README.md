# Blender: Muzium Perang Penang model

First build of the 3D site. Layout comes from the museum visitor map (rotated about 180 degrees, so image-up is south), terrain from a coarse 90 m elevation grid and the OSM coastline. Everything is a PROVISIONAL blockout, not a survey.

## Rebuild
1. Open Blender 5.x with the MCP add-on running (or paste the scripts in the Scripting tab).
2. Run, in order (each via `exec(open(path).read())`):
   - `blender/scripts/build_muzium.py`: terrain, sea, 37 map structures plus facilities, paths, road, hotspot and `loc_*` empties, spawn
   - `blender/scripts/place_props.py`: decimated Poly Haven props, low-poly trees, scatter
   - `blender/scripts/export_muzium.py`: writes `blender/out/muzium_perang_raw.glb`
3. `sh blender/scripts/optimize_glb.sh` writes `app/static/models/muzium_perang.glb`.
4. Re-download Poly Haven assets if needed: `python3 blender/scripts/fetch_polyhaven.py`.

## Outputs
- `app/static/models/muzium_perang.glb` (about 10.8 MB, Draco geometry, WebP textures at most 1024 px)
- `blender/out/hotspots.json`: the 10 hotspot positions (Blender and glTF axes, with a provisional flag) for `app/seed_data.py`
- `blender/out/site_points.json`: all 57 map and facility markers (glTF axes) for labels
- `blender/src/muzium_perang.blend`

## Node conventions in the GLB
- Walkable: `ground_terrain`, `floor_floor`, `floor_paths`, `floor_road`, `floor_asphalt`
- `spawn`: start position, faces west through the ticket building
- `hotspot_<slug>` (10), `loc_<n>_<name>` (map points 1 to 37), `loc_fac_*` (facilities), `loc_escape_route_shaft`, `loc_memorial_plaque`
- Axes after export: x east, y up, z south

## Known limitations
- Provisional placements: memorial plaque, escape route (shaft climb is only 3 m instead of 9 m because the DEM hill is not steep enough there), lookout point, Japanese tunnel, underground bunker.
- Building sizes, orientations and interiors are guesses. Windows, furniture and detail textures are missing.
- Terrain uses a 90 m DEM with noise, so slopes are approximate. North-south scale fits (0.27 m per pixel), east-west is compressed on the source map.
- The Poly Haven cannon is a naval-style stand-in. Trees are low-poly stand-ins because the Poly Haven trees are 1 to 2 million triangles.
- The GLB has 39 materials and 95 images, which is heavy for phones. Next steps: share one texture atlas between props, drop unused maps.
- The optimizer step skips `flatten`, `join` and `prune` on purpose, because they delete empty marker nodes.
