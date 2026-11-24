---
inclusion: manual
---

# Process log: VirtualTourism, The Night Walk Chapter (from prompt to deployment)

Use `#process-log` to give Kiro the history, decisions and pitfalls. Also the basis for the Kiroween "How Kiro was used" write-up.

## 1. Specs first (2026-11-23)
`appgenprompt.md` was split into eight specs (core, auth, db, admin, blender, content, ui, user), each with requirements, design and tasks. Steering files were added: always-on project context, a Blender workflow that loads when `.glb/.gltf/.blend` files are touched, and a manual web-research prompt.

## 2. Research and reference material
- Agent research (web search and fetch) gathered facts, licensed photos (Wikimedia Commons CC BY / CC BY-SA), OSM coastline and roads, a 90 m elevation grid (Open-Meteo), and a museum visitor map supplied by the user.
- The visitor map is rotated about 180 degrees (image-up = south). Found by comparing the OSM coastline (east of the museum pin) with the map's sea (image-left). All 37 numbered map points were transcribed to `reference/sitemap/site_layout.json` with real-world metres.
- User-supplied vlogs were used only as visual reference (frames, OCR for signs). Transcripts were low quality and were not used as sources. They are git-ignored, as are the museum map and blog photos.
- Evidence and confidence per hotspot live in `reference/photos/<slug>/INFO.md`, `reference/NOTES.md`, `reference/sitemap/MAP_NOTES.md`.

## 3. Tooling via MCP
- Blender MCP (`mcp-for-blender`) controlled a live Blender 5.3: build, inspect with rendered views, save, export.
- OpenStreetMap MCP needs `uvx --with "mcp<2" osm-mcp-server` (mcp 2.x breaks it). Only reverse geocoding worked; nearby-places returned HTTP 406. Geometry came from the Overpass API directly.
- Poly Haven assets (CC0) were fetched with `blender/scripts/fetch_polyhaven.py`.

## 4. 3D model pipeline (`blender/scripts/`)
`build_muzium.py` (terrain from DEM and OSM coast, 37 map structures, facilities, paths, road, hotspot and loc empties, spawn) then `place_props.py` (Poly Haven props decimated to a few hundred to a few thousand triangles, low-poly trees, scatter) then `export_muzium.py` then `optimize_glb.sh` (dedup, instance, weld, simplify, resize 1024, WebP, Draco). Result: 10.8 MB GLB, 57 `loc_*` markers, 10 hotspots, 5 walkable meshes.
Lessons: Poly Haven models are scan quality (trees 1-2 million triangles), so use them only for small props and build trees procedurally. `gltf-transform optimize/flatten/join` prune empty nodes and delete all markers. A comment swallowing a `;`-chained line removed the spawn link once.

## 5. App build
Flask app, models, OAuth (Google, Microsoft, GitHub, plus demo login and a judge admin key), admin panel with CSRF and safe uploads, seed with 10 hotspots, generated narration (macOS `say` Daniel voice), web-sized licensed images, vendored Three.js with Draco, compiled Tailwind. Viewer: night atmosphere with lantern, fireflies and fog; walking, touch joystick, teleport, collisions; hotspots with panel, facts, audio; places drawer; WebXR plus Cardboard split-screen with gyroscope and gaze selection.

## 6. Verification done
- Route, login, admin, CSRF, upload and cascade-delete checks with the Flask test client.
- Headless Edge (SwiftShader): no console errors; viewer loads in about 8 s on a software renderer; 64 draw calls; walking, hotspot panel, touch joystick, Cardboard split-screen rendered.
- Bugs found by running it: help dialog unreachable on a landscape phone (fixed); `.hud-btn` CSS overrode `hidden` (fixed); gunicorn could not import `app:app` (added `wsgi.py`); two workers could race the first seed (added `--preload`).
- Repo hygiene: 149 files, about 17 MB, `.kiro` tracked, no secrets, no unlicensed media.

## 7. Hooks
`rebuild-tailwind-on-save` (PostFileSave on templates, `src.css`, viewer scripts) and `glb-size-budget` (PostFileSave on `app/static/models/*.glb`, warns above 15 MB).

## 8. Hackathon decisions
Category: Costume Contest (immersive, spooky UI; "Ghost Hill after dark"). Skeleton Crew was possible but needed a second destination. Rules summary (AWS blog, Oct 31): public GitHub repo with OSI licence and `/.kiro` untouched by `.gitignore`; live app URL; demo video under 3 minutes on YouTube; Kiro-usage write-up; judged on impact, Kiro implementation, design, innovation, presentation (20% each).

## 9. Open items
- Deploy on the user's own server (HTTPS needed for WebXR, gyroscope, OAuth cookies). Render config exists as a fallback (`render.yaml`).
- Test OAuth with real keys; test on Android with Cardboard (`adb reverse tcp:5055 tcp:5055` gives a secure `localhost` for sensors).
- Confirm provisional positions (memorial, escape route, lookout, Japanese tunnel, bunker) and the 9 m escape climb (currently 3 m).
- Fact-check hotspot text against more sources; ask the museum for permission and photos.
- Record the demo video; write the Kiro-usage description; request free Kiro credits before Dec 1 12:00 Pacific.
