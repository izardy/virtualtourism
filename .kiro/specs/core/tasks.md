# Tasks: Core Application and 3D/VR Experience

- [x] 1. Project scaffolding
  - [x] 1.1 Create folder structure, `requirements.txt` (Flask, Flask-SQLAlchemy, Flask-Login, Authlib, python-dotenv, requests), `app.py`, `app/__init__.py` with `create_app` and `app/config.py`
  - [x] 1.2 Add `base.html` layout with Tailwind, nav, flash messages and 404 template
  - _Requirements: 1, 9_

- [x] 2. Public pages
  - [x] 2.1 Implement `main` blueprint routes `/`, `/explore`, `/destination/<id>`
  - [x] 2.2 Build `index.html` (hero, featured destination, about, VR intro, CTAs, login buttons)
  - [x] 2.3 Build `explore.html` with cards and name search plus empty state
  - [x] 2.4 Build `destination.html` (hero, description, gallery, hotspots, VR availability, 3D/VR buttons)
  - _Requirements: 2, 3, 4_

- [x] 3. Hotspot API and viewer route
  - [x] 3.1 Add `/viewer/<id>` and `/api/destinations/<id>/hotspots`
  - [x] 3.2 Build `viewer.html` with canvas, loading overlay, info panel and VR button
  - _Requirements: 5, 6, 7_

- [x] 4. Three.js modules (`static/js`)
  - [x] 4.1 `SceneManager` (renderer, lights, loop, resize)
  - [x] 4.2 `ModelLoader` (GLTFLoader, progress, error handling, walkable mesh list)
  - [x] 4.3 `CameraController` (mouse look, touch look)
  - [x] 4.4 `MovementSystem` (WASD, joystick, teleport)
  - [x] 4.5 `HotspotManager` (markers, raycast click, info panel, audio control)
  - [x] 4.6 `VRController` (WebXR session, stereo split-screen fallback, gyroscope)
  - [x] 4.7 `viewer.js` wiring all modules
  - _Requirements: 5, 6, 7, 8_

- [x] 5. Performance pass
  - [ ] 5.1 Lazy-load media, cap pixel ratio, verify load under 5 s and ~60 FPS on a mid-range Android phone
  - _Requirements: 5.4, 5.5_

- [x] 6. Documentation and deployment
  - [x] 6.1 Write README setup instructions and `.env.example`
  - [x] 6.2 Add deployment notes/Procfile for Render, Railway, PythonAnywhere
  - _Requirements: 9_

- [x] 7. Demo verification
  - [ ] 7.1 Walk through the full flow on desktop and Android Cardboard

- [x] 8. Night atmosphere and Costume Contest polish (fog, lantern, fireflies, flicker headline, wisps)
  - _Requirements: 10_
- [x] 9. Deployment preparation
  - [x] 9.1 `wsgi.py`, `Procfile`, `render.yaml`, `.env.example`, MIT `LICENSE`, `.gitignore` that keeps `.kiro/`
  - [x] 9.2 Fresh-database start under gunicorn with two workers (`--preload`)
  - [x] 9.3 Commit and push to a public GitHub repository
  - _Requirements: 9, 12_
- [ ] 10. Deploy on the user's own server behind HTTPS (nginx or Caddy, systemd), then smoke-test the live URL
- [ ] 11. Test on a real Android phone with Cardboard (`adb reverse` or an HTTPS tunnel for sensors)
- [ ] 12. Record the 3 minute demo video and write the Kiro usage description

- [x] 13. Two ways to explore
  - [x] 13.1 Compute tour routes in Blender (A*) and write `muzium_perang_tour.json`
  - [x] 13.2 `GuidedTour.js` state machine, comfort fades, intro and outro narration
  - [x] 13.3 Mode picker, HUD toggle, tour bar, end card, `?mode=` links on landing and destination pages
  - [x] 13.4 Browser test of the whole tour at 10x speed, phone landscape and Cardboard
  - [ ] 13.5 Try the guided tour on a real Android phone in Cardboard and on a WebXR headset
  - _Requirements: 13_
