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
6. Export `.glb`, then `gltf-transform optimize` (Draco, WebP). Targets: under 15 MB, about 150k triangles.
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
- The map is south-up. Use `east_m` / `north_m` in `site_layout.json` (Blender X = east, Y = north, Z = up). Coast and road context: `reference/sitemap/osm_context.json`.
- Scope: all 37 map points are modelled; the 10 hotspots are the interactive ones.
- Per-hotspot evidence is in `reference/photos/<slug>/INFO.md`.
- Videos and the museum map are reference only. Never copy them into `app/static/`.

## Rules
- Record the source and license of every image or reference in `static/images/CREDITS.md`.
- Prefer the user's own photos and CC0 textures. Do not use copyrighted images without permission.
- Without user material, build a clearly labeled generic fortress placeholder and say it does not match the real site.
- Re-check size and triangle budgets after every export and report the numbers.
