# VirtualTourism: The Night Walk Chapter

Walk real heritage sites in 3D and VR. First destination: **Muzium Perang Penang** (the Penang War Museum), a 1930s British coastal fort that locals call *Bukit Hantu*, Ghost Hill. Built for **Kiroween 2026, Costume Contest** (a polished, haunting UI that supports the app), with Kiro.

Explore on a phone, in a desktop browser, or through a Google Cardboard headset (WebXR where available). Night mode with a lantern, fireflies and fog is on by default; a day toggle is in the HUD.

> The 3D tour is an **unofficial, provisional reconstruction** from the museum's public visitor map, licensed photos and open data. It is not affiliated with the museum. Ghost stories are presented as folklore; the prisoners' suffering was real and the site is treated as a memorial.

## Run it

```bash
python3 -m venv .venv && source .venv/bin/activate    # optional
pip install -r requirements.txt
python app.py                                          # http://localhost:5000  (PORT=5055 python app.py if 5000 is busy)
```

On first start it creates `instance/virtualtourism.db` (SQLite) and seeds Muzium Perang Penang with 10 hotspots. No Node is needed to run; the compiled CSS and the vendored Three.js are committed.

Sign in: with no OAuth keys configured, use **Continue as demo visitor**. To open the admin panel as a judge, set `DEMO_ADMIN_KEY=<secret>` and visit `/login-demo-admin?key=<secret>`.

## Features

| Area | What you get |
|---|---|
| Pages | Landing, explore with name search, destination details with gallery and VR badge, 3D viewer, profile, admin |
| Two ways to explore | **Explore on your own** (full control) or the **Guided night tour** (about 8 minutes): a narrator walks a computed route through all ten stories and you only look around. Switch any time from the HUD. Best for VR |
| 3D viewer | First-person walking (WASD or arrows, Shift to run), mouse look, touch joystick plus drag-look, double-click or double-tap teleport, wall collisions, ground following |
| Hotspots | 10 glowing markers with story, photo, facts and spoken narration; progress counter; "Places" drawer teleports to any hotspot or any of the 57 map locations |
| VR | `Enter VR Experience`: WebXR immersive-vr (controllers: trigger to teleport or select, thumbsticks to move) or split-screen Cardboard mode with gyroscope head tracking, gaze selection and tap-to-walk |
| Auth | Google, Microsoft, GitHub via Authlib (shown only when keys are set), plus demo login. Users auto-register |
| Admin | Add or edit destinations, upload GLB models, images and audio, create hotspots, CSRF-protected |
| Performance | 37 MB Draco+WebP model (2K textures), about 64 draw calls, adaptive pixel ratio, lazy images |

Guided tour: pick it on the start screen or open `/viewer/1?mode=guided` (free mode: `?mode=free`, VR: add `&vr=1`). Outside VR the guide walks at 2 m/s and turns the view toward the route unless you are looking around; in VR (WebXR or Cardboard) it hops between stops with soft fades for comfort. Prev, Pause and Next sit at the bottom; the story panel and narration open at every stop. Tap the screen in Cardboard to pause.

Controls hint: double-tap the ground to teleport; tap a glowing marker to open its story.

## OAuth setup (optional)
Create an OAuth app per provider and set the redirect URI to `https://<host>/auth/<provider>/callback` (use `http://localhost:5000/...` locally), then put the keys in `.env` (see `.env.example`). Microsoft uses the multi-tenant `common` endpoint. The OAuth code paths could not be exercised without real credentials during development; the demo login and all app flows were tested in a browser.

## Deploy (Render / Railway / PythonAnywhere)
`Procfile` runs `gunicorn wsgi:app`. Set `SECRET_KEY`, `COOKIE_SECURE=1`, optional `ADMIN_EMAILS`, `DEMO_LOGIN`, `DEMO_ADMIN_KEY` and OAuth keys. SQLite lives in `instance/`; use a persistent disk or set `DATABASE_URL` to Postgres for durable data. Admin uploads go to `app/static/` (also needs a persistent disk).

## Project layout
```
app.py, requirements.txt, Procfile, .env.example
app/            Flask package: models, routes (main, auth, user, admin, api), services/uploads.py, seed_data.py
app/templates/  base, index, explore, destination, viewer, profile, admin, 404
app/static/     css (Tailwind source + build), js (SceneManager, ModelLoader, CameraController, MovementSystem,
                HotspotManager, VRController, GuidedTour, viewer.js; vendor/ = three.js r170 + Draco), models/, images/, audio/, data/
blender/        scripts that build and export the 3D model (see blender/README.md); raw assets are not in the repo
content/        narration scripts and `make_narration.py` (Kokoro voice); reference/ holds research notes (large third-party media is git-ignored)
.kiro/          specs, steering, hooks and MCP config used to build this project
```

Rebuild the CSS after template changes: `npx tailwindcss@3 -c tailwind.config.js -i app/static/css/src.css -o app/static/css/app.css --minify` (a Kiro hook does this on save).

## Built with Kiro
- **Specs:** `.kiro/specs/{core,auth,db,admin,blender,content,ui,user}` hold requirements, design and tasks for each part.
- **Steering:** project context (always on), Blender workflow (loads when working on model files), a reusable web-research prompt (manual).
- **MCP:** a live Blender connection built the 3D model and checked it visually; an OpenStreetMap server was used for geocoding.
- **Hooks:** rebuild Tailwind CSS on save; warn when the exported GLB exceeds the 40 MB budget.
- **Agentic research:** licensed photos, map data and elevation data were gathered and credited by the agent; see `reference/NOTES.md` and `app/static/images/CREDITS.md`.

## Credits and licences
Code: MIT (`LICENSE`). Photos: Wikimedia Commons, CC BY 4.0 / CC BY-SA 4.0 (`app/static/images/CREDITS.md`). 3D props and textures: Poly Haven (CC0). Terrain: Open-Meteo / Copernicus DEM. Coastline and roads: OpenStreetMap contributors (ODbL). Three.js: MIT. Narration audio: synthetic speech from Kokoro-82M (Apache-2.0), voice `bf_emma`, generated from `content/narration/` by `content/make_narration.py`.

## Regenerating the guided tour
The route is computed from the real 3D model: run `blender/scripts/build_tour_paths.py` in Blender after `build_muzium.py` and `place_props.py`. It writes `app/static/data/muzium_perang_tour.json` (A* on a 1.5 m grid with wall, slope and sea checks; the observation post stairs are routed by hand). Re-run it whenever the model or hotspot positions change. Intro and outro narration live in `content/narration/tour-intro.txt` and `tour-outro.txt`.
