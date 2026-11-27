# Design: Core Application and 3D/VR Experience

## Overview
A monolithic Flask app with server-rendered Jinja templates and a small ES-module Three.js frontend. The Tailwind CSS is compiled with the CLI and committed (`app/static/css/app.css`), so the app has no CDN dependency and needs no Node to run. SQLite for storage, local static files for assets.

## Architecture
```
Browser (Jinja pages + Three.js modules)
   |  HTTP / JSON
Flask app (blueprints: main, auth, user, admin, api)
   |
SQLAlchemy -> virtualtourism.db        static/ (models, images, audio)
```

## Project layout
```
app.py                  # entry point: create_app(), db.create_all(), seed, run
requirements.txt
app/
  __init__.py           # create_app, extensions (db, login_manager, oauth)
  config.py             # env-driven config
  models/               # user.py, destination.py, hotspot.py
  routes/               # main.py, auth.py, user.py, admin.py, api.py
  templates/            # base.html, index, explore, destination, viewer, profile, admin
  static/{css,js,models,images,audio}
  static/js/            # SceneManager, ModelLoader, CameraController,
                        # MovementSystem, HotspotManager, VRController, viewer.js
  seed.py, seed_data.py # seed logic and Muzium Perang Penang content
  services/uploads.py   # admin upload handling
docs/
  blender-export.md     # modelling and export conventions
content/
  narration/<slug>.txt  # narration scripts for each hotspot
blender/                # authoring files, never served by Flask
  src/                  # .blend source files (muzium_perang.blend)
  scripts/              # bpy scripts and gltf-transform commands
reference/              # raw source material, never served by Flask
  sitemap/              # floor plans, visitor map, aerial screenshots
  photos/<slug>/        # one folder per hotspot: main-entrance, japanese-tunnel,
                        # command-centre, observation-tower, prison-area,
                        # underground-bunker, memorial-zone, weapons-display,
                        # lookout-point, escape-route
  photos/grounds/       # wide shots of the whole site
  photos/textures/      # close-ups of walls, floors, metal
  video/                # walkthrough and drone footage
  NOTES.md              # photo credits, measurements, links
```
`reference/` and `blender/` hold full-size originals. Optimized copies go to `app/static/images/` and `app/static/models/` and are the only files the website serves.

## Routes
| Route | Purpose |
|---|---|
| `GET /` | Landing page, featured destination |
| `GET /explore?q=` | Destination cards, name search |
| `GET /destination/<id>` | Details page (404 if missing) |
| `GET /viewer/<id>?vr=1` | 3D viewer; `vr=1` auto-prompts VR entry |
| `GET /api/destinations/<id>/hotspots` | JSON hotspots for the viewer |

## Frontend modules
- **SceneManager**: creates renderer, scene, lights, resize handling, render loop (`renderer.setAnimationLoop` so it works in XR). Caps pixel ratio at 2 for mobile.
- **ModelLoader**: GLTFLoader with DRACOLoader/KTX2Loader optional; reports progress; returns the scene graph plus a list of walkable meshes for teleport raycasts.
- **CameraController**: perspective camera at eye height (1.6 m); mouse look via pointer lock on desktop, drag-look on touch.
- **MovementSystem**: WASD with velocity damping, virtual joystick on touch, teleport via floor raycast with a marker reticle, simple floor-height clamping.
- **HotspotManager**: builds sprite/mesh markers from API data, raycasts on click/tap/gaze, emits `hotspot:open` and renders the info panel (title, description, image, facts, audio player).
- **VRController**: feature-detects `navigator.xr.isSessionSupported('immersive-vr')`. WebXR path uses `renderer.xr`. Fallback path uses `StereoEffect` (split-screen) plus `DeviceOrientationControls`-style gyroscope handling, including `DeviceOrientationEvent.requestPermission()` on iOS.

## Data flow (viewer)
1. Template injects destination id and `model_path`.
2. `viewer.js` fetches hotspots, initializes modules, loads the model with progress.
3. On load the hotspots are placed, the loading overlay is removed, and input handlers are enabled.

## Performance
- Models: low-poly, compressed textures, Draco/meshopt (see blender spec).
- Lazy-load audio/images on hotspot open; `loading="lazy"` for gallery images.
- Three.js loaded as ES modules via importmap; viewer scripts only on the viewer page.

## Error handling
- Model load failure: overlay with message and back link.
- 404 handler template; missing hotspot media omitted.
- WebXR/gyro permission denied: message and fallback to normal 3D mode.

## Configuration
Env vars: `SECRET_KEY`, `DATABASE_URL` (default `sqlite:///virtualtourism.db`), OAuth client IDs/secrets.

## Testing
Manual demo checklist on desktop Chrome and Android Chrome with Cardboard; optional pytest smoke tests for routes.

## As built (2026-11-25)

**Entry points.** `python app.py` for local runs (`PORT=5055` when 5000 is taken by AirPlay). `wsgi.py` exposes `app` for gunicorn because the package `app/` shadows `app.py`. `Procfile` and `render.yaml` use `gunicorn wsgi:app --preload`; `--preload` runs table creation and seeding once before workers fork.

**Routes.** `/`, `/explore?q=`, `/destination/<id>`, `/viewer/<id>[?vr=1]`, `/profile`, `/admin/*`, `/api/destinations`, `/api/destinations/<id>/hotspots` (also returns `points_url` for `static/data/<model>_points.json`), `/login/<provider>`, `/auth/<provider>/callback`, `/login-demo`, `/login-demo-admin`, `/logout`, `/favicon.ico` (redirect).

**Viewer modules (`app/static/js`).**
- SceneManager: renderer, rig (body) and camera (head), night/day atmosphere (fog, moonlight, lantern spotlight, fireflies), adaptive quality (drops pixel ratio below 28 fps).
- ModelLoader: GLTFLoader with Draco; indexes `floor_*`/`ground_*` (walkable), `struct_*` (colliders), `spawn`, `hotspot_*`, `loc_*`.
- CameraController: mouse drag and touch look, tap and double-tap detection, gyroscope hand-over.
- MovementSystem: WASD/arrows/Shift, joystick, auto-walk, ray-cast ground following, wall collision rays with sliding, slope limit, animated teleport, XR thumbstick locomotion.
- HotspotManager: glowing markers with number badges, picking by screen, ray or gaze, visited tracking.
- VRController: WebXR `immersive-vr` with controller teleport; fallback split-screen (`StereoEffect`) with device-orientation head tracking, recenter, gaze dwell of 1.4 s, tap to walk.
- viewer.js: loading screen, hotspot panel (image, facts, narration), places drawer (10 hotspots plus all map locations), help overlay, toasts, progress counter.

**Performance (measured).** Model 10.8 MB; 64 draw calls; about 83k triangles rendered at the start point; loads in about 8 s on a software renderer in headless Edge (a real GPU is faster). Images lazy-load; Three.js and Draco are vendored with a one-day cache header.

**Pitfalls.** Flask caches templates when debug is off. `gunicorn app:app` fails. Gyroscope and WebXR need HTTPS. See `.kiro/steering/process-log.md`.

## As built: guided tour (2026-11-25)
- **Data:** `app/static/data/muzium_perang_tour.json` (version, start, walk speed 2 m/s, intro and outro audio, ten stops with `path`, `stand`, `yaw`, optional `jump`). Exposed to the viewer as `tour_url` by `/api/destinations/<id>/hotspots`. Stops are matched to hotspots by title.
- **Routes:** `blender/scripts/build_tour_paths.py` runs A* on a 1.5 m grid using BVH ray casts against the real model (ground height and slope, wall rays at 0.45 m and 1.2 m with a 0.45 m radius, sea check, clearance penalty near walls), then straightens the route with line-of-sight tests. The observation post stairs (1.2 m wide, narrower than the grid) are routed by hand. Result: 10 legs, 596 m, no fade-jumps; about 8 minutes including narration. Order: Main Entrance, Weapons Display, Lookout Point, Japanese Tunnel, Escape Route, Observation Tower, Command Centre, Underground Bunker, Prison Area, Memorial Zone.
- **GuidedTour.js:** state machine `intro, walking, arrived, lingering, blink, outro, finished`. Walking follows the polyline with ground following and ease in/out, and turns the view toward the route unless the visitor dragged to look within 2.5 s. Arriving opens the hotspot (panel and narration via callbacks) and waits for the audio to end (or a reading time when there is none), then lingers 1.6 s. Comfort mode (WebXR or Cardboard) replaces walking with a fade-out, a teleport to the stop and a fade-in using a black sphere attached to the camera. Prev, Next and the Places drawer jump with the same fade.
- **viewer.js:** mode picker (a click is required anyway so audio can autoplay), HUD toggle, tour bar, end card, free-mode-only features disabled while guided (double-tap teleport, hotspot taps, gaze selection, proximity hints, map locations list). The story panel is lifted above the tour bar during a tour. In Cardboard a tap pauses the tour.
- **Bugs found by testing and fixed:** the movement system kept a stale target height after a walked tour, sinking the visitor under the terrain on exit (now `setPose` on exit); the observation post rail blocked the stairs (a 1.4 m gap was added in the Blender build); the help dialog and the HUD wrapped on a 360 px tall phone.
- **Verified in headless Edge:** all ten stops reached exactly on their stand points at 10x speed, panel and narration opened at each, end card, return to free walking, `?mode=` links, phone landscape layout, Cardboard split-screen with fades, tap-to-pause. Not verified: a real headset or phone.

## As built: rendering cost (2026-11-26)
- **ModelLoader.js:** glass `transmission` is turned off (it made three.js render the scene twice per frame); leaf materials use `alphaTest 0.5`, double-sided, not transparent. `chunkInstances(root, 70)` splits instanced meshes into 70 m grid chunks so each chunk is frustum-culled on its own (skips `floor_*`, `ground_*`, `struct_*` and meshes with `instanceColor`).
- **viewer.js:** every 0.3 s, chunks farther than the fog limit are hidden (170 m at night, 520 m by day). About 570k triangles drawn per view at night with 253 trees in the model.
- **SceneManager.js:** day sky `kloofendal_48d_partly_cloudy_puresky`; day light environment 0.55, hemisphere 0.45, sun 1.9, exposure 0.9, fog `FogExp2(0xa9c4d8, 0.0035)`.
