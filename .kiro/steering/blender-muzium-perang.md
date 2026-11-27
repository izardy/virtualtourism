---
inclusion: fileMatch
fileMatchPattern: '**/*.{glb,gltf,blend}'
---

# Blender workflow: Muzium Perang Penang

Export settings, budgets and loader behavior are defined in #[[file:.kiro/specs/blender/design.md]]. This file covers the working approach and the inputs needed from the user.

## What the agent can and cannot do
- The agent cannot sculpt in the Blender GUI. It writes `bpy` scripts (run with `blender --background --python script.py`) and `gltf-transform` commands.
- Scripted output is an accurate-scale blockout. Detail, texturing and final polish come from the user or a 3D artist.
- Never invent site facts. If layout, dimensions or history are unknown, say so and mark the value as a placeholder.

## Blender MCP (live control)
- Server config: `.kiro/settings/mcp.json` (`mcp-for-blender`, formerly `blender-mcp`). Setup: install `uv`, run `uvx mcp-for-blender install-addon`, enable "MCP for Blender" in Blender add-ons, press N in the 3D viewport > MCP for Blender tab > Start MCP Server.
- When the `blender` MCP tools are available, build and inspect the scene live and verify with viewport/render views. Otherwise fall back to `bpy` scripts.
- The server can run arbitrary Python in Blender. Ask the user to save the `.blend` first, and do not open untrusted files while connected.
- Run only one MCP client against the add-on at a time.
- Assets from Poly Haven, Sketchfab or AI generators need a license check and an entry in `static/images/CREDITS.md` before they ship.

## Workflow
1. Site plan: zones and connections from the user's map, photos and notes.
2. Scripted blockout in meters, Y-up on export: terrain, buildings, walls, tunnels, tower.
3. Naming: walkable meshes `floor_*` / `ground_*`; empty `spawn`; one empty per hotspot named `hotspot_<slug>` (for example `hotspot_japanese-tunnel`).
4. Export hotspot empty positions to JSON and use them for `app/seed_data.py` so database coordinates match the model.
5. Materials and textures: limited material count, textures at most 2048 px (1024 for props), bake AO/lightmaps.
6. Export `.glb`, then `gltf-transform optimize` (Draco, WebP). Targets: under 40 MB (raised from 15 MB for realism), under about 1.1M triangles drawn per view (the scene holds about 2.1M; chunking and fog hiding in the viewer keep the drawn count near 0.6-1.1M).
7. Place at `static/models/muzium_perang.glb`; test on desktop and Android with Cardboard.
8. Read user-supplied material from `reference/` (see `reference/NOTES.md` for credits and measurements) before modelling.
9. Keep scripts in `blender/scripts/` and source `.blend` files in `blender/src/` (not served by Flask).

## Inputs to request from the user (ask for these before modelling)
Priority order:
1. Site map or floor plan (museum brochure, visitor map, annotated satellite screenshot).
2. Own photos: 5 to 10 per hotspot area (Main Entrance, Japanese Tunnel, Command Centre, Observation Tower, Prison Area, Underground Bunker, Memorial Zone, Weapons Display, Lookout Point, Escape Route), wide grounds shots, and close-ups of walls, floors, metal for textures.
3. Key dimensions: tunnel length/width, tower height, building footprints (paced estimates are acceptable).
4. Walkthrough video along the visitor route; drone footage if available.
5. Reference links (official site, heritage pages, historical maps). Check each license before use.
6. Scope decision: whole site, or exterior plus a few key areas for the demo (prefer the smaller scope for a hackathon).
7. Confirmation of permission from the museum to photograph and recreate the site before any public launch.

## Site layout sources (read before blockout)
- `reference/sitemap/MAP_NOTES.md` and `reference/sitemap/site_layout.json` (37 numbered locations, pixel coordinates, provisional scale of about 0.28 m per pixel).
- `reference/video/VIDEO_NOTES.md` for signage and visual style.
- Layout source since 2026-11-27: the reeaki "Fort Relics" visitor map, followed as drawn. `blender/scripts/extract_reeaki.py` writes `reference/sitemap/reeaki_layout.json` (points, building angles, facilities, heights, coast, paths, roads, trees), and `build_muzium.py` / `place_props.py` read it. Re-run the extractor, then the whole pipeline, after changing a marker or a hand-traced road in it. There is no `LAYOUT_ROT` any more (the earlier 55° satellite rotation was dropped on request). After moving anything, re-run `build_tour_paths.py`: it reports hotspots that the move has blocked. Blender X = `east_m`, Y = `north_m` of the map frame (image-up = −Y), Z = up.
- Scope: all 37 map points are modelled; the 10 hotspots are the interactive ones.
- Per-hotspot evidence is in `reference/photos/<slug>/INFO.md`.
- Videos and the museum map are reference only. Never copy them into `app/static/`.

## Rules
- Record the source and license of every image or reference in `static/images/CREDITS.md`.
- Prefer the user's own photos and CC0 textures. Do not use copyrighted images without permission.
- Without user material, build a clearly labeled generic fortress placeholder and say it does not match the real site.
- Re-check size and triangle budgets after every export and report the numbers.

## As built (2026-11-25): status and lessons
- The model exists: `blender/scripts/build_muzium.py` then `place_props.py` then `export_muzium.py` then `build_tour_paths.py` then `export_mobile.py`, then `optimize_glb.sh` and `optimize_glb.sh mobile`, produce `app/static/models/muzium_perang.glb` (desktop, 2k) and `muzium_perang_mobile.glb` (phones, 1k). Building and ground materials are Poly Haven textures in `blender/assets/polyhaven/textures_2k` and `textures_1k`; keep both sizes when adding one. See `blender/README.md` and the "As built" section of `.kiro/specs/blender/design.md`.
- Hotspot positions for the database come from `blender/out/hotspots.json` (glTF axes). Provisional: memorial, escape route, lookout, Japanese tunnel, underground bunker. Never present them as surveyed.
- Poly Haven models are scan quality: decimate every prop (a few hundred to a few thousand triangles). Trees: `island_tree_01/02` go through `thin_tree.py` (keep about 12% of the leaf cards as single quads, drop twigs, decimate the trunk) to 13-18k triangles (background) or about 54k (hero trees near stops); far (8-9% leaves, 11 m or more from paths) and distant tiers (4% leaves, about 3.5k triangles, 32 m or more from paths and buildings) fill the hills; never decimate a tree directly. Place props with `settle_z()` (lowest ground under the footprint), never at the ground height of the centre: on slopes they float. Avoid glass `transmission` in materials: three.js then renders the scene twice (ModelLoader turns it off). Do not import `coast_rocks_*`. Pick single-object Poly Haven assets: `industrial_caged_sconce` is a sheet of variants and breaks when decimated.
- Never run `gltf-transform optimize`, `flatten`, `join` or `prune` on the model: they delete the empty `hotspot_*`, `loc_*` and `spawn` nodes. Use `sh blender/scripts/optimize_glb.sh`.
- Keep meshes merged per material (`struct_*` colliders, `floor_*` walkable) and keep the 40 MB budget (a hook warns on save).
- Edit the scripts, not the `.blend`: the `.blend` is git-ignored and the scripts rebuild the scene.
- When chaining statements with `;` on one line, never append a trailing comment before a later statement: it silently disables them.

- Terrain is a 6 m grid, refined to 1.5 m around tunnels (`_near_tunnel()` in `build_muzium.py`). Any new feature carved into the terrain needs the same refinement, or the hillside interpolates back up through it. Check with a downward ray along the floor; only `floor_*` should be hit.
- Gun bays, lock-ups, exhibits, the memorial and the covered walkway have dedicated builders (`gun_bay()`, `lockup()`, `exhibits()`). Their dimensions are inferred, not measured. Compare a new builder with its reference photo in `reference/photos/<slug>/` before signing off.
