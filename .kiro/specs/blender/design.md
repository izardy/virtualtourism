# Design: Blender Asset Pipeline and Model Loading

## Overview
Blender is the authoring tool. The web app consumes optimized `.glb` files through Three.js `GLTFLoader`. This spec defines the authoring conventions, export settings, optimization steps and the loader behavior.

## Folders
- `reference/`: user-supplied source material (site map, photos per hotspot, video, `NOTES.md`). Layout is in the core design.
- `blender/src/`: `.blend` files. `blender/scripts/`: `bpy` scripts and optimization commands.
- `app/static/models/`: only the optimized `.glb` served to users.

## Authoring workflow
1. Block out the site (terrain, buildings, interior, tunnels) at real scale in meters.
2. Model low-poly, using normal maps for detail instead of geometry.
3. Name walkable meshes `floor_*` / `ground_*`; add an Empty `spawn`.
4. Bake lighting (AO and light maps) to textures; use a limited material set and texture atlases.
5. Apply transforms and modifiers, delete hidden faces, merge by material, use linked duplicates for repeated props.
6. Export, then optimize.

## Export settings (Blender glTF 2.0)
- Format: glTF Binary (`.glb`), +Y Up, Apply Modifiers on.
- Include: Cameras off, Punctual Lights off (viewer sets its own lights), Custom Properties off.
- Mesh: compression with Draco (level ~6) or optimize afterward with `gltf-transform`.
- Images: WebP or JPEG textures; avoid 4K.
- Animation: off unless needed.

## Post-export optimization
```
sh blender/scripts/optimize_glb.sh   # dedup, instance, weld, simplify, resize 1024, WebP, Draco
```
Do not use `gltf-transform optimize`, `flatten`, `join` or `prune`: they remove empty nodes (hotspot, spawn and loc markers).
Check the result in a glTF viewer and compare size against budgets.

## Loader design (`ModelLoader`)
- `GLTFLoader` with `DRACOLoader` (decoder path in `static/js/vendor/draco/`) and optional `KTX2Loader` and `MeshoptDecoder`.
- `load(url, onProgress)` returns `{ scene, walkables, spawn }`:
  - `walkables`: meshes whose name starts with `floor_` or `ground_` (fallback: all meshes if none found).
  - `spawn`: object named `spawn`, else the origin.
- Sets `frustumCulled = true`, disables shadows by default, and sets texture anisotropy to a low value on mobile.
- On error, rejects with a descriptive message handled by the viewer.

## LOD and performance
- Large scenes may split into interior and exterior GLBs later; for the MVP use one GLB.
- Hotspot markers are lightweight sprites, not part of the GLB.
- Dispose geometries/materials when leaving the page.

## Placeholder asset (superseded)
(Superseded by the as-built model, see the section at the end.) `static/models/muzium_perang.glb`: a simple generated scene (ground plane, a few boxes representing buildings and a tunnel) used until the real model is delivered. Hotspot coordinates are chosen to sit within it.

## Documentation
`docs/blender-export.md` captures the conventions and commands above.

## Testing
Load the placeholder and an optimized sample in desktop Chrome and Android Chrome; confirm progress, spawn placement, teleport onto `floor_*` meshes and FPS.

## As built (2026-11-25)

**Inputs.** `reference/sitemap/site_layout.json` (37 map points, metres from the ticket building; the map is rotated about 180 degrees, so image-up is south), `osm_context.json` (coastline and roads), `elevation_grid.json` (Open-Meteo DEM, smoothed, vertical relief x0.7), Poly Haven textures and models.

**Scripts.**
1. `build_muzium.py`: terrain with flat pads under structures and a shoreline blend, sea, barracks, cook houses, lock-up, tunnels (with earth mounds), gun pits, pill boxes, observation post, guillotine, gallows, trench, booby-trap wire, facilities, paths and OSM road, escape shaft and memorial, `loc_*`, `hotspot_*` and `spawn` empties. Meshes are merged per material (`struct_*` colliders, `floor_*` walkable). UVs are box-projected in world metres; materials use Poly Haven textures with backface culling.
2. `place_props.py`: imports Poly Haven models, bakes and decimates them, scatters low-poly trees, shrubs, ferns, rocks and stumps as linked duplicates, and places props at map locations.
3. `export_muzium.py`: GLB export (JPEG textures, extras on), saves the `.blend`.
4. `optimize_glb.sh`: dedup, instance, weld, simplify, resize to 1024, WebP, Draco. Output `app/static/models/muzium_perang.glb` (about 10.8 MB, 112 nodes, 37 meshes, 39 materials).
5. `fetch_polyhaven.py`: CC0 asset downloader. Outputs for the app: `blender/out/hotspots.json`, `blender/out/site_points.json` (copied to `app/static/data/muzium_perang_points.json`).

**Findings.** Poly Haven trees are 1 to 2 million triangles and `boulder_01` could not be decimated, so trees are procedural and boulders were dropped. `gltf-transform flatten/join/optimize` delete empty nodes. The escape shaft is only 3 m because the DEM hill is not steep enough there. Remaining weight: 39 materials and 95 images; a shared prop texture atlas is the next optimisation.
