# Requirements: Core Application and 3D/VR Experience

## Introduction
The core spec covers the Flask application skeleton, public pages (landing, explore, destination details), the Three.js 3D viewer with interactive hotspots, and WebXR/Cardboard VR mode for VirtualTourism. The MVP destination is Muzium Perang Penang, Malaysia. Target devices: Android phone, desktop browser, Google Cardboard.

## Requirements

### Requirement 1: Application bootstrap
**User Story:** As a developer, I want to run the app with two commands, so that I can demo it quickly.

#### Acceptance Criteria
1. WHEN `pip install -r requirements.txt` and `python app.py` are run THEN the system SHALL start a Flask server with SQLite (`virtualtourism.db`) created and seeded automatically.
2. The project SHALL use Flask, Flask-SQLAlchemy, Flask-Login, Authlib, Jinja templates, TailwindCSS and Three.js.
3. The project SHALL follow the structure: `/app` (`/routes`, `/models`, `/templates`, `/static/{css,js,models,images,audio}`) with templates `index.html`, `explore.html`, `destination.html`, `viewer.html`, `profile.html`, `admin.html`.

### Requirement 2: Landing page
**User Story:** As a visitor, I want an immersive landing page, so that I understand the platform and can start.

#### Acceptance Criteria
1. The landing page SHALL show a hero banner, featured destination, about section, VR tourism introduction, call-to-action buttons and login options (Google, Microsoft, GitHub).
2. WHEN the user clicks a call-to-action THEN the system SHALL navigate to Explore or the featured destination.

### Requirement 3: Explore destinations
**User Story:** As a visitor, I want to browse and search destinations, so that I can find a place to explore.

#### Acceptance Criteria
1. The explore page SHALL render a card per destination with thumbnail, name, category, location and an Explore button.
2. WHEN a search term is submitted THEN the system SHALL return destinations whose name contains the term (case-insensitive).
3. IF no destination matches THEN the system SHALL show an empty-state message.

### Requirement 4: Destination details
**User Story:** As a visitor, I want a destination page, so that I can learn about it before entering 3D.

#### Acceptance Criteria
1. The page SHALL show hero image, historical description, photo gallery, featured hotspots and VR availability.
2. The page SHALL provide "Explore in 3D" and "Enter VR Mode" buttons linking to the viewer.
3. IF the destination has no `model_path` THEN the system SHALL mark VR as unavailable and disable both buttons.
4. IF the destination id does not exist THEN the system SHALL return a 404 page.

### Requirement 5: 3D viewer
**User Story:** As a user, I want to walk through the model, so that I feel present at the location.

#### Acceptance Criteria
1. The viewer SHALL load the destination `.glb`/`.gltf` with GLTFLoader and show a loading progress indicator.
2. The viewer SHALL support first-person movement with WASD and mouse look on desktop, touch controls (virtual joystick and drag-look) on mobile, and teleport movement by selecting a floor point.
3. IF model loading fails THEN the system SHALL show an error message and a link back to the destination page.
4. The viewer SHALL target 60 FPS and the scene SHALL be ready in under 5 seconds on a mid-range phone on a typical connection.
5. Assets (audio, images) SHALL be loaded lazily.

### Requirement 6: Interactive hotspots
**User Story:** As a user, I want to tap markers, so that I can learn about each point of interest.

#### Acceptance Criteria
1. The viewer SHALL render a clickable marker at each hotspot's (x, y, z) position.
2. WHEN a marker is clicked or tapped THEN the system SHALL show a panel with title, historical information, image, interesting facts and audio narration controls.
3. WHEN another hotspot is opened or the panel is closed THEN the system SHALL stop the current audio.
4. IF a hotspot has no image or audio THEN the panel SHALL omit that element without error.

### Requirement 7: VR mode
**User Story:** As a Cardboard user, I want stereoscopic VR, so that I can look around naturally.

#### Acceptance Criteria
1. The viewer SHALL show an "Enter VR Experience" button.
2. WHEN WebXR `immersive-vr` is supported THEN the button SHALL start an XR session.
3. IF WebXR is unavailable THEN the system SHALL fall back to split-screen stereoscopic rendering with gyroscope head tracking (requesting DeviceOrientation permission where required).
4. VR mode SHALL work on Android smartphones with Google Cardboard.

### Requirement 8: Reusable Three.js modules
#### Acceptance Criteria
1. The frontend SHALL provide separate ES modules: `SceneManager`, `ModelLoader`, `CameraController`, `MovementSystem`, `HotspotManager`, `VRController`.

### Requirement 9: Deployment
#### Acceptance Criteria
1. The app SHALL be deployable to Render, Railway or PythonAnywhere, with secrets read from environment variables.
2. A README SHALL contain setup instructions.

## Additional requirements (added during the build)

### Requirement 10: Costume Contest theme
**User Story:** As a Kiroween judge, I want a haunting but purposeful interface, so that the design supports the experience.
1. The viewer SHALL default to night mode (dark scene, fog, lantern light, fireflies) with a day toggle.
2. Ghost stories SHALL be labelled as folklore, and sensitive areas SHALL be introduced respectfully.
3. The UI SHALL honour `prefers-reduced-motion`.

### Requirement 11: Judge and demo access
1. WHEN `DEMO_LOGIN=1` THEN the system SHALL offer "Continue as demo visitor" without any OAuth keys.
2. WHEN `DEMO_ADMIN_KEY` is set THEN `/login-demo-admin?key=<key>` SHALL sign in an admin; with no key the route SHALL return 404.

### Requirement 12: Hosting
1. The app SHALL run under gunicorn (`wsgi:app --preload`) behind HTTPS in production; WebXR, device sensors and secure cookies require HTTPS (`localhost` also counts as secure).
2. A live URL and a public GitHub repo with an OSI licence SHALL be available for Kiroween judging.
