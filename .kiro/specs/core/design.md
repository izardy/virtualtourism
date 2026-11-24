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
