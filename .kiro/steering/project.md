# VirtualTourism: The Night Walk Chapter (project context)

Hackathon web app for walking real heritage sites in 3D and VR. First destination: Muzium Perang Penang (Penang War Museum), Malaysia. Entered in **Kiroween 2026, Costume Contest** (polished, haunting UI that supports the app). Deadline: Dec 4, 2026 14:00 Pacific (about 06:00 Malaysia time on Dec 5).

## Sources of truth
- Requirements prompt: `appgenprompt.md`. Longer vision (not MVP): `masterprompt.md`.
- Specs: `.kiro/specs/{core,auth,db,admin,blender,content,ui,user}/` (requirements, design, tasks). Each design.md ends with an "As built" section.
- Chronological record and lessons: `.kiro/steering/process-log.md` (attach with `#process-log`).
- Blender workflow: `.kiro/steering/blender-muzium-perang.md`. Web research prompt: `.kiro/steering/fill-reference-content.md`.

## Stack and layout (as built)
- Flask 3, Flask-SQLAlchemy (SQLite in `instance/virtualtourism.db`), Flask-Login, Authlib, Jinja, compiled TailwindCSS (`app/static/css/app.css`), Three.js r170 vendored in `app/static/js/vendor/`.
- Entry points: `python app.py` (local, `PORT=5055` if 5000 is busy) and `gunicorn wsgi:app --preload` (production). Do not use `gunicorn app:app`: the package `app/` shadows `app.py`.
- Modules in `app/static/js/`: SceneManager, ModelLoader, CameraController, MovementSystem, HotspotManager, VRController, viewer.js.
- 3D model: `app/static/models/muzium_perang.glb` (about 10.8 MB), built by `blender/scripts/` through the Blender MCP. Raw assets are not in git.
- Blender node conventions: walkable `floor_*` / `ground_*`, colliders `struct_*`, `spawn`, `hotspot_<slug>`, `loc_*`. glTF axes: x east, y up, z south.

## Rules for working in this repo
- Secrets only in environment variables (`.env` is git-ignored). Never commit them.
- `.kiro/` must stay in git and out of `.gitignore` (Kiroween rule).
- Third-party media with unclear licences (museum map, vlogs, blog photos, full-size originals) stays git-ignored. Public images need credit in `app/static/images/CREDITS.md`.
- Present ghost stories as folklore. The prisoners' suffering was real; keep the tone respectful.
- Flask caches templates when debug is off: restart the server after template edits.
- After editing templates or viewer scripts, rebuild CSS (the save hook does it): `npx tailwindcss@3 -c tailwind.config.js -i app/static/css/src.css -o app/static/css/app.css --minify`.
- Do not run `gltf-transform optimize`, `flatten`, `join` or `prune` on the model: they delete the empty marker nodes. Use `sh blender/scripts/optimize_glb.sh`.
- Do not add tests unless asked.
- Design: dark mode, Deep Blue `#0A192F`, Cyan `#00D4FF`, White `#FFFFFF`, glassmorphism, spooky night atmosphere.

## Status (2026-11-25)
Built and tested locally in a browser (desktop, touch emulation, Cardboard split-screen). Committed and pushed to GitHub. Not yet verified: OAuth with real keys, a real Android/Cardboard device, deployment on the user's own server. Model positions for memorial, escape route, lookout, Japanese tunnel and bunker are provisional.
