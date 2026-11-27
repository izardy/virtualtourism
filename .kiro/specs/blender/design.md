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
4. `optimize_glb.sh`: dedup, instance, weld, simplify, resize to 2048, WebP, Draco. Output `app/static/models/muzium_perang.glb` (about 37 MB since the realism pass).
5. `fetch_polyhaven.py`: CC0 asset downloader. Outputs for the app: `blender/out/hotspots.json`, `blender/out/site_points.json` (copied to `app/static/data/muzium_perang_points.json`).

**Findings.** Poly Haven trees are 1 to 2 million triangles and `boulder_01` could not be decimated, so trees are procedural and boulders were dropped. `gltf-transform flatten/join/optimize` delete empty nodes. The escape shaft is only 3 m because the DEM hill is not steep enough there. Remaining weight: 39 materials and 95 images; a shared prop texture atlas is the next optimisation.

## As built: tour routes (2026-11-25)
`build_tour_paths.py` (run after `build_muzium.py` and `place_props.py` on the live scene) merges the ground meshes (`ground_terrain`, `floor_*`) and the colliders (`struct_*`) into two BVH trees and writes `app/static/data/muzium_perang_tour.json`. The runtime movement rules are mirrored exactly (slope limit 0.35 m + 1.1 per metre, wall rays, sea level) so that every route is walkable in the viewer. The goal test also checks height (within 3 m) so that the hill above a tunnel does not count as reaching a shaft. The observation post gained a 1.4 m gap in its east rail so that the stairs lead onto the platform. Re-run the script after any model change.

## As built: realism pass 2 (2026-11-25)
- Budget raised to 40 MB at the user's request; textures now 2K (ambientCG 2K sets in `blender/assets/ambientcg2k/`, `fetch_ambientcg.py 2K`), `optimize_glb.sh` resizes to 2048. Result 37 MB, about 760k triangles with instances.
- `building()`: two-sheet corrugated roof with eaves, fascia boards, gutters, downpipes and gable end walls; glazed windows with frames, mullion and transom (about 18% lit warm at night); corner pilasters; open door leaf inside; walkable door step; a bulb and a Poly Haven `industrial_wall_lamp` over each door (positions in `blender/out/fixtures.json`).
- Ticket building: lean-to canopy on timber posts. The entrance gate no longer reserves its own terrain pad (it buried the ticket building's east door); the Poly Haven iron gate leaves stand open beside the pillars.
- Trees: Poly Haven `island_tree_01/02` thinned by `thin_tree.py`. 38 background trees keep about 20% of the leaves (cards 1.9x, 13-18k triangles); 6 hero trees by the entrance gate and the weapons, prison, memorial and command-centre stops keep 50% (cards 1.3x) and a 24k-triangle trunk (54k triangles each). About 1.05M triangles drawn in total. ModelLoader forces leaf materials to alpha test and double-sided.
- ModelLoader turns off glass `transmission` (Poly Haven lamp and compressor glass): it made three.js render the whole scene twice per frame (2.07M to 1.03M triangles).
- Not available as CC0 without login: realistic WW2 buildings. Kenney and Quaternius kits are CC0 but stylised low-poly, so they were not used; Poly Haven `modular_fort_01` is a 17th-century stone fort style and does not match.

## As built: more trees (2026-11-26)
- Tree tiers in `place_props.py` (all from `island_tree_01/02` through `thin_tree.py`, placed with `settle_z()`, trunks at least 6 m apart):

  | Tier | Count | Template (keep, leaf_scale, wood_tris) | Placement |
  |---|---|---|---|
  | Background | 38 | `T_TREE1` (0.20, 1.9, 6000), `T_TREE2` (0.22, 1.8, 5000) | normal scatter |
  | Hero | 6 | `T_HERO` (0.50, 1.3, 24000), about 54k triangles | entrance and main stops |
  | Far | 85 | `T_FAR1` (0.08, 2.8, 2500), `T_FAR2` (0.09, 2.7, 2000) | at least 11 m from paths |
  | Distant | 130 | `T_DIST` (0.04, 3.6, 1500), about 3.5k triangles | at least 32 m from paths and buildings |

- Scene total 2.13M triangles in 402 instances; GLB 37.8 MB.
- Viewer side: `ModelLoader.chunkInstances(root, 70)` splits instanced meshes (not `floor_*`, `ground_*`, `struct_*`, not meshes with `instanceColor`) into 70 m chunks so frustum culling works; `viewer.js` hides chunks beyond the fog (170 m night, 520 m day). About 570k triangles drawn per view at night.
- Day HDRI: `kloofendal_48d_partly_cloudy_puresky` (replaces `fish_hoek_beach`, which showed buildings and a person).

## As built: layout match (2026-11-26)
- User request: match building and tree positions to the real site (top view of the scale model `site-model.jpg`; reeaki.com map photo as a further reference).
- `build_muzium.py`: `LAYOUT_ROT = 55°` counter-clockwise around the ticket building, applied on top of the earlier 180° reading of the visitor map. `rot_xy()` moves the PTS entries (originals kept in `map_east_m`/`map_north_m`), and `building_r()` rotates the footprints, gables, grates, pill boxes, souvenir shop, cafeteria and toilets. Door faces are still chosen in the map frame. Kept fixed because they are tied to real features: `FIXED_PTS={2}` (pill box by the access road) and `FIXED_FAC` (ticketing, coast items, jetty, road water tank).
- Evidence for 55°: the OSM footway from the ticket building runs at a bearing of about 145°, while the map spine (ticket → 3 → 5) ran at about 200°. The scale model shows the barracks south and the gun bays south-east of the entrance. After the rotation the core sits on the OSM peak "Bukit Batu Maung" (about 15 m W, 98 m S of the origin) instead of 20 m down the west slope.
- Car park at (22, 40), rotated 90° (`CARPARK_ROT`): the gravel area north of the ticket building on satellite imagery.
- Memorial fixed at (30, -76): the rotated position fell inside tunnel 29.
- Tunnels: `TUNNELS` carves the terrain below each tunnel floor (the hillside cut through tunnel 29, which runs along the slope). The earth cover is now `G.mound()`: it opens at the portal (the old gable's end face hid the opening) and slopes down 6 m past the inner end.
- Escape-route hotspot at `ESC_MOUTH`, the mouth of the crawl. Escape climb is now 4.4 m (real: about 9 m).
- `place_props.py`: reads `scene["layout_rot"]`, rotates `loc_<n>` prop offsets (not `loc_02_`). Tree density matches the satellite image and scale model (closed forest up to the buildings): all 38 background trees plus 50 extra far trees scatter inside `CORE=(-150,175,-215,75)`, with `CLEARINGS` for the ridge track and car park. 303 trees, 2.47M triangles, 454 instances, GLB 38.2 MB.
- Tree positions match density, not individual trees. Hotspots re-synced into `app/seed_data.py` and the DB. Tour routes: all 10 stops reachable, 540 m.

## As built: Poly Haven materials and phone model (2026-11-26)
- User request: source Poly Haven textures suitable for phones (1K and 2K) and keep the polygon count low.
- Materials: the 17 ambientCG sets are replaced by 14 Poly Haven materials, picked by eye on contact sheets against the old ones. `fetch_polyhaven.py` `MATERIALS` downloads each at 1k (`textures_1k/`) and 2k (`textures_2k/`). `make_mat()` reads `textures_2k`, and accepts Poly Haven's `_diffuse_` file names. `TILE` now equals each texture's real-world size from the Poly Haven API (1.0–3.0 m). Green and olive paint are `worn_mossy_plasterwall` with a multiply tint. ambientCG is still a fallback in `make_mat()`, but no material uses it.

  | Key | Poly Haven id |
  |---|---|
  | ground | forest_leaves_02 |
  | soil | red_laterite_soil_stones |
  | conc | concrete_wall_006 |
  | conc_g, camo | worn_mossy_plasterwall (tinted) |
  | conc_w | concrete_layers_02 |
  | floor | concrete_floor_02 |
  | brick | mossy_stone_wall |
  | rust | rusty_metal_02 |
  | grate | rusty_metal_03 |
  | roof | corrugated_iron (tinted) |
  | plaster | worn_plaster_wall |
  | rock | mossy_rock |
  | wood | weathered_planks |
  | asphalt | asphalt_02 |

- Two models from one scene:
  - Desktop `muzium_perang.glb`: 2k textures, 2.47M triangles, 34.9 MB (was 38.2 MB).
  - Phone `muzium_perang_mobile.glb`: written by `export_mobile.py` and `optimize_glb.sh mobile`. It uses the 1k texture files, so the 1k images come from Poly Haven itself rather than being downscaled. Its trees are one tier cheaper: hero → background, background → far, far and distant → `tpl_tree_mob` (2.2% leaves, about 2k triangles), and every second distant tree is left out. About 0.89M triangles, 14.7 MB.
- Viewer: `main.viewer` passes `model_lite` when `<model>_mobile.glb` exists. `viewer.js pickModel()` loads it on coarse-pointer devices whose short screen side is at most 900 px; `?quality=full|lite` overrides.
- Measured in headless Edge at night from the spawn point, in four directions:

  | View | Triangles drawn (thousands) |
  |---|---|
  | Desktop | 557 / 857 / 1067 / 827 |
  | Phone | 251 / 358 / 476 / 369 |

- Not yet measured on a real phone. If a phone still stutters, the next steps are the hero and background tiers of the phone model, then the shrub and fern counts.

### As built: building detail pass (2026-11-26)
Request: "search from the web more info on the buildings at muzium perang penang, the dimension if possible, the interior, try to copy as close as possible".

- Finding: no measured drawings or building dimensions are published online. Sizes come from the 22 reference photos (door height, brick courses, people for scale) and from the standard 1930s British 6-inch BL coast battery layout. The Axis History Forum notes that Penang's forts follow the Singapore Naval Base pattern; Pasir Laba and Heugh batteries (two emplacements with a magazine between them) were the templates. Sources are listed in `reference/NOTES.md`, "Building research (2026-11-26)".
- `gun_bay()` replaces `pit(gun=True)` at points 25 and 36. It is a circular concrete emplacement: floor radius 3.75 m, parapet outer radius 5.0 m and 1.3 m high, with a coping, open at the rear (3 of 28 segments). It has a holdfast ring with 16 bolts and 5 ready-use lockers in the parapet on the seaward side. Point 25 is an empty pit, as at the museum today. It has a "PENANG FORTRESS BATTERY" board and a magazine wall with a grille to one side of the rear opening. Point 36 has the gun mounted, with its rear facing uphill.
- `lockup()` replaces the barred `building_r()` at points 19 and 20. Each block has 3 cells, each 3.2 m wide, and is 4.2 m deep and 2.6 m high under a thick slab roof. Each cell has a black steel door frame with a barred transom, a steel door opened inward and low brick walls flanking the approach (photo `cell-door-1.jpg`). Inside, the cells are whitewashed and hold an iron cage bed against the back wall, chains and a bulb.
- `exhibits()` fits out the barracks and exhibition rooms (points 3, 7, 9, 10, 13–16, 18, 21, 22) with a board of prints on the end wall, two free-standing boards, a display case and a bulb. The Island Drum (2022) describes dim exhibition rooms off a hallway.
- Memorial at (30, −76): concrete pad, pale plaster plinth, black plaque and a chain fence on steel posts, open at the front.
- Tunnels: walls and ceiling are whitewashed plaster (as photographed) with wall lamps every 6 m.
- Covered walkway from Information & Ticketing toward point 3: timber posts every 3 m starting 9 m out, 1.85 m either side of the path, with a corrugated roof 2.6 m above the ground.
- Terrain fix: the 6 m terrain grid let the hillside rise through the inner 10 m of tunnel 29. A grid face whose corners straddle the 8 m carve band interpolates back up. The terrain is now subdivided to 1.5 m around every tunnel and re-sampled. A ray check along tunnel 29 finds only floor.
- Results: desktop 35.0 MB, phone 14.7 MB, 2.47M triangles. Tour routes are all reachable. The float, door, chunk, tour and mobile browser checks pass, and the hotspots did not move.
- Inferred, not measured: every dimension above, the number of cells per lock-up, the locker count and the walkway length. The positions of the memorial, escape route, lookout, Japanese tunnel and bunker are still provisional.

### As built: strict sitemap layout (2026-11-27)
Request: "strictly follow guideline based on the sitemap from https://i0.wp.com/reeaki.com/wp-content/uploads/2021/03/photo_2021-03-24_12-51-55.jpg?w=1242&ssl=1".

- Source: the reeaki.com photo of the museum's "Fort Relics" visitor map (1242×577), byte-identical to the private copy `reference/inbox/reeaki_map.jpg`. It has the same 37 numbers as the museum's own map (`map-visitor-2048.jpeg`).
- New script `blender/scripts/extract_reeaki.py` (plain Python with numpy, Pillow, scipy and scikit-image; not Blender) turns the map into `reference/sitemap/reeaki_layout.json`:
  - Points: the 37 markers, read by eye from 3× zoom crops on a 20 px grid (±2 px). Where the marker sits beside its drawing (12, 17, 18, 1, 2, 31), the drawing's position is used.
  - Building angles: the long axis of 12 drawn buildings (barracks rows 13–22, cook houses 12 and 17), measured as two pixels along the ridge.
  - Facilities: ticketing, souvenir shop, cafeteria, three toilets, car park, VIP car park, War Game Park, the coast red dots (barbed wire, well, four pill boxes, submarine landing bay, jetty, maritime museum, generator room, water tank), the road water tank and the WAR MUSEUM billboard.
  - Scale: an affine fit of the 37 markers onto their metre positions from the museum's map, anchored at the ticketing building. That gives about 0.55 m per pixel across and 0.59 m per pixel down; the mean residual is 4.5 m and the worst is 17.5 m. The frame is the old map frame (X = `east_m`, Y = `north_m`, image-up = −Y).
  - Heights (2 m grid): the drawn hill outline as a plateau that ramps down over 70 m, a 9 m rise around the observation post (24) and the anti-aircraft pit (30), the bay coastline from the blue water, a 1 m beach shelf, and the sand bar in the bay. The ticketing building is at 0 and sea level is −36, as before. The 90 m DEM and the OSM coastline are no longer used (`_old_dem_h_base()` is kept for reference).
  - Paths: the skeleton of the white paths on the hill, pruned of short spurs and simplified.
  - Roads: the wide roads, traced by hand: To War Museum, Jln Permatang Damar Laut, and the car park, VIP car park and coast roads.
  - Trees: 83 tree groups, found as textured light-green canopies.
  - Ground classes: lawn versus wooded (dark green).
  - Checks: `reeaki_check.jpg` (paths, roads and trees drawn over the map) and `reeaki_preview.png`, both git-ignored.
- `build_muzium.py`:
  - Removed: `LAYOUT_ROT` (55°), `FIXED_PTS`, `FIXED_FAC`, the satellite car park and the OSM access road.
  - Placement: every point and facility comes from `reeaki_layout.json`. Each building turns to its own map angle (`PTS[n]["rot"]`, also written as the `rot` property on its `loc_` empty).
  - Doors: each door faces the nearest map path (`face_to_path()`, `side_to_path()` for the lock-ups).
  - Paths and roads: map paths are 2.6 m soil ribbons, cut where they cross a building footprint (white roofs on the map). Map roads are 6 m asphalt.
  - Tunnels: tunnels 26 and 29 start uphill and turn by the smallest angle that keeps them 12 m from other points and off the paths.
  - Coast: four coast pill boxes (the map shows four). The jetty is a deck from the maritime museum out to the sand bar. The coast armoury was removed because the reeaki map does not show it. A WAR MUSEUM billboard stands beside pill box 1.
  - Memorial: now beside the main path between 34 and 05, still provisional.
  - Terrain: −300 to 246 m east and −204 to 204 m north.
- `place_props.py`: one tree, or a small group, stands on each tree drawn on the map (80 of 88 placed; the rest are blocked by paths or buildings). Detailed trees go within 25 m of a path, far-detail trees elsewhere. Filler trees grow only on the map's wooded ground and on the hills beyond the map, not on its open lawns. The satellite clearings are gone. Prop offsets turn with each building's own `rot`.
- Coast items: the map draws them a few metres off its own shoreline. Each one is moved to the nearest land, then inland until it is 5 m from the water. Pill Box (coast) D moved 10 m, the submarine landing bay 5.6 m and the maritime museum 5.1 m; the others moved 2.3 m or less.
- Results:
  - Desktop model: 34.9 MB, 2.99M triangles, 345 trees.
  - Phone model: 14.7 MB.
  - Tour: all 10 stops reachable, about 578 m in total.
  - Tunnels: the downward ray check along both tunnels hits only floor.
  - Browser checks: float, door, chunk, the tour (all 10 stops and the end card) and phone/desktop/lite all pass with no console errors.
  - Hotspots: moved, and re-synced to `app/seed_data.py` and the DB.
- Limits:
  - The map is schematic, so absolute distances and compass directions are approximate. In particular, the satellite-based 55° rotation was dropped on purpose.
  - The escape climb is 3 m (the minimum) because tunnel 29 now lies under a flat plateau.
  - Drawn triangles on the phone rose to about 600k per view.

### As built: more Poly Haven models for phones (2026-11-27)
Request: "if possible use as much models source from polyhaven which suitable for mobile phone 1K or 2K textures or with log polygon count".

- Selection: I searched the Poly Haven API catalogue (522 models) for models with a low polygon count that fit a 1930s–40s fort on a tropical hill.
  - Downloaded: 44 models at 1k (`fetch_polyhaven.py`).
  - Dropped after a thumbnail review: 14.
    - Modern-looking: school chair, plastic barrel, cement bag, yellow sledgehammer, floral oil lamp, wall clock, hand truck, hazard-label drum, car tyre, steel shelves.
    - Only a few centimetres high in the scans: wood sorrel, weed, nettle, pebble.
  - Now used: 30 new models, plus 4 that were already downloaded but unused.
- `place_props.py`:
  - `prep()` now handles files that hold several variants side by side (`_a`, `_b`, ...). `split` makes one template per variant (calathea, anthurium, shrub_03, pachira); `first` keeps variant a (old_military_crate, wooden_crate_02). Shared meshes are made single-user before baking.
  - Room fit-out, placed from the door side (the new `door` property on `loc_` empties):
    - Office 3: steel desk, stool, bookcase.
    - Intelligence room 11: table under the radio, stool, desk, chalkboard.
    - Communication centre 8: three equipment racks, table, stool, hanging lamp.
    - Armoury 35: rack and a stack of military crates.
    - Generator room 6: oil tins, toolbox, ladder.
    - Cook houses 12 and 17: tables, a bucket, tins.
    - Lock-ups 19 and 20: a bucket in the first cell.
  - Outdoors:
    - Crates by points 23 and 25.
    - A pick and a spade by the tunnel portals.
    - Three picnic tables at the cafeteria.
    - Bins by the toilets and the gate.
    - A lifebuoy at the jetty and two buoys in the bay.
  - Nature:
    - Understory beside the paths on the map's wooded ground: 40 calathea, 32 anthurium, 24 shrub_04, 24 shrub_03.
    - Wooded ground further off: 16 pachira saplings, 14 rocks, 8 moss-rock sets, 6 stumps, 6 fallen trunks, 12 dry branch piles.
    - Coastal slope: 14 rock faces.
- `optimize_glb.sh`: a second `resize` pass caps the textures of the small Poly Haven props (glob list `PROPS`) at 512 px in both models. The island trees keep 1k, and building and ground materials keep 2k on desktop and 1k on the phone.
- Results:
  - Sizes: desktop 34.8 MB (was 34.9), phone 14.6 MB (was 14.7).
  - Scene: 3.19M triangles in 739 instances (was 2.99M in 493).
  - Phone emulation draws 453k–688k triangles per view.
  - Checks: all 10 tour stops reachable; float, door, chunk, tour, phone and lite checks pass with no console errors. Hotspots did not move.
- Lessons:
  1. Poly Haven plant scans are life-size and often tiny (wood sorrel is about 5 cm). Check the imported dimensions before scattering.
  2. Many files are variant sheets. Joining every mesh gives a row of plants, so split them per variant.
  3. Extra assets cost texture size, not triangles. Capping small-prop textures at 512 px paid for 34 more models.

### As built: the user's pill boxes and entrance (2026-11-27)
Request: "replace the 2 pillbox in our map with this one, also substitute the entrance with the [one] in blender folder at desktop/blender", then "use penang_war_museum_entrance1".

- **Source files:** copied from `~/Desktop/blender` to `blender/user_models/`: `penang_pillbox_type1.blend`, `penang_pillbox_type2.blend`, `penang_war_museum_entrance1.blend`. They are read only, never modified.
- **New `blender/scripts/user_models.py`,** exec'd by `build_muzium.py` after the scene meshes are written:
  - **Import:** appends each file and applies its boolean modifiers. It leaves out hidden cutters, lights, cameras and the files' own ground (`Ground`, `Terrain`).
  - **Placement:** every entry in `USER_PLACES` places one copy of the model.
  - **Roles:** faces are merged by role and material.
    - `floor_user_*` (walkable): upward faces below a per-model height (type 1 0.5 m, type 2 0.2 m, entrance 0.45 m).
    - `struct_user_*` (colliders): the rest of the named structure parts, and the entrance's `BrickWalls` and `Ground` collections.
    - `deco_user_*` (drawn only): weapons, furniture, signs and displays.
  - **Materials:** concrete, brick, paving, timber, zinc roof and lamp glass become the scene's Poly Haven materials with box UVs. Brick became the new Poly Haven `brick_4` (`redbrick`). The other user materials keep their colours; procedural colour ramps are flattened to their average for glTF.
- **Pill boxes** (`pillbox(..., kind)`):
  - Type 1 stands at map points 1, 2, 27 and 37. The door (local +x) faces the nearest map path, and the model sits 0.1 m into the pad.
  - Type 2 stands at the four coast pill boxes, with the entrance stairs inland (local −x).
  - Type 2 is sunk 1.3 m. Its pad is kept at least 2 m above the sea, and `CARVES` lowers our terrain in an octagon (r 1.9 m) for the interior and a box for the stair trench. `h()` applies the carves. The terrain grid is refined to about 0.5 m within 7–10 m of each carve.
- **Entrance:**
  - Placement: turned 90° so the front faces east toward the car parks, origin 19.5 m east of the ticket building, on a pad at the ticket building's level.
  - Passage and driveway: the covered passage ends just before the ticket deck, and the driveway runs on to the east door.
  - Removed: the scripted gate (pillars, sign, flags, planters) and the Poly Haven iron gate leaves.
  - Spawn: moved 5 m outside the gate, facing west.
  - Trees: `FIXTURES["zones"]` keeps them out of the entrance and the pill boxes.
- **Results:**
  - Sizes: desktop 37.8 MB (was 34.8), phone 15.3 MB (was 14.6).
  - Tour: all 10 stops are reachable. The entrance route is now 21 m from the new spawn.
  - Checks: float, door, chunk, the full tour, phone and the opening flight pass with no console errors. Hotspots did not move.
  - Screenshots confirm both pill box interiors and the type-2 stairs are reachable.
- **Assumption, not confirmed by the user:** type 1 is used on the hill and type 2 on the coast.

### As built: web model from the digital twin (2026-11-27)
Request: "copy reproduce.md and other folder there and paste it into our virtualtourism blender folder, then implement option 1 and evaluate if the old approach that build our current sitemap is still needed".

- **Copied files:** `~/Desktop/blender/reproduce.md` → `blender/reproduce.md`, and `~/Desktop/blender/penang_war_museum/` → `blender/penang_war_museum/` (278 MB).
  - Committed: the guide, the survey and gap markdown, the points CSV, the tools and their derived JSON.
  - Git-ignored: the .blend files (large, with Google satellite imagery packed), the Street View, satellite and visitor screenshots, the renders, the site-map PNG/SVG and the museum sketch.
- **`blender/scripts/twin_pipeline.py`:** runs the whole build in background Blender (`Blender -b --factory-startup`), so it never touches a file open in the user's Blender: `twin_build.py` → `place_props.py` → `export_muzium.py` → `build_tour_paths.py` → `export_mobile.py`. Then run `optimize_glb.sh`, desktop and mobile.
- **`twin_build.py`:**
  - **Inputs:** reads only the instance placements, the calibrated terrain and the sea from `penang_war_museum_sitemap.blend`.
  - **Structures:** appends the structure collections from `site_structures/` (all except vegetation and the PB1/PB2 studies) and turns everything 180° about z. The twin's frame is x = −E, y = −N; the web frame is x = E, y = N, so glTF stays x east, z south.
  - **Vegetation:** drops the twin's own vegetation (46M triangles) and the 6 baked plaza trees (322k triangles each); their spots become hero-tree spots. Decimates 47 heavy plaza assets to about 3,000 triangles each.
  - **Roles and materials:** bakes and merges faces by role and material (`floor_twin_*`, `struct_twin_*`, `deco_twin_*`), using the same rules as `user_models.py` plus "flat" objects (walk on top, no collision). Procedural materials map to the scene's Poly Haven materials by name; others are flattened to their colour.
  - **Terrain and sea:** the terrain keeps the twin's SRTM data calibrated against Street View, as `ground_terrain` with Poly Haven forest floor. The Google satellite drape is not shipped. The sea is at the real height (z −68.3; the gate is z 0).
  - **Markers:** a `loc_*` for every CSV row, a memorial plaque (not in the twin; provisional, beside R34/R05), the spawn 8 m north of the gate, and 10 hotspots: main-entrance B03, weapons-display B17, lookout R37, Japanese tunnel R26, escape route B12 (#29 tunnel entrance), observation post R24, command centre R11, bunker R08, prison R19, memorial.
  - **Outputs:** `hotspots.json`, `site_points.json`, and `fixtures.json` (200 tree-exclusion zones and the tree spots).
- **Shared code:** the materials, `TILE` and `uv_box()` moved from `build_muzium.py` into the new `scene_lib.py`, which both builders exec.
- **Twin mode** (`scene["twin"]`):
  - `place_props.py`:
    - Trees are planted on a jittered 20 m grid over the terrain, in three tiers by distance to the walkable surfaces (at most 60 detailed trees), plus hero trees at the plaza spots.
    - Sea level and bounds come from the scene, and room fit-outs whose `loc_` names do not exist are skipped.
  - `build_tour_paths.py`: takes the bounds and sea level from the scene and drops the old observation-post stair route.
- **Results:**
  - Sizes: desktop 31.0 MB (was 37.8), phone 14.0 MB (was 15.3).
  - Scene: 3.06M triangles, 388 trees.
  - Tour: all 10 stops reachable, 543 m in total.
  - Checks:
    - The float, chunk, full-tour, phone, desktop and opening-flight checks pass with no console errors.
    - A new gate walk check (`door_twin.mjs`) walks from the spawn through the gate passage to 13.5 m inside.
- **Evaluation of the old approach (`build_muzium.py` + `extract_reeaki.py` + `user_models.py`):** no longer needed to build the app's model.
  - **Better in the twin:** the surveyed positions (±3–6 m), the calibrated terrain and the hand-modelled entrance (the same model as the user's) replace the sketch-map layout and the sketch-derived heights.
  - **Still needed:** `place_props.py`, `thin_tree.py`, `scene_lib.py`, `export_muzium.py`, `export_mobile.py`, `build_tour_paths.py`, `optimize_glb.sh` and `fetch_polyhaven.py`.
  - **Only in the old build:**
    - building interiors (exhibits, lock-up cells, fitted-out rooms), the escape shaft and the tunnel interiors;
    - the user's type-1/type-2 pill boxes, which the twin keeps as stand-alone PB1/PB2 studies (its pill boxes are sketch placeholders);
    - the reeaki-specific coast items: the jetty, the submarine bay and the sand bar.
  - **Recommendation:** keep the old scripts as a fallback until the twin is accepted, then move them to `blender/scripts/legacy/`. Port the pill boxes (PB1/PB2 at R01, R02, R37 and the coast pill boxes) and the interiors into twin mode if they are wanted.
