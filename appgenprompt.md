Build a complete, functional hackathon-ready web application called "VirtualTourism".

VirtualTourism is an immersive VR tourism platform that allows users to explore real-world tourist attractions through high-quality 3D virtual environments created in Blender.

The platform should provide a Google Earth-inspired experience but focused on individual tourist attractions, museums, cultural heritage sites, and historical landmarks.

The first destination is:

Muzium Perang Penang, Malaysia

Users should be able to explore the location through a mobile phone, desktop browser, or Google Cardboard VR headset.

====================================================
OBJECTIVE
====================================================

Create a visually impressive prototype suitable for a hackathon demo.

Prioritize:

- Functionality
- Visual impact
- VR experience
- Simplicity
- Fast deployment
- Mobile compatibility

Avoid unnecessary enterprise architecture.

====================================================
TECH STACK
====================================================

Backend:
- Python Flask
- Flask-SQLAlchemy
- Flask-Login
- Authlib

Frontend:
- Flask Jinja Templates
- HTML5
- TailwindCSS
- JavaScript

3D Engine:
- Three.js
- GLTFLoader
- WebXR

3D Modelling:
- Blender

Database:
- SQLite

Database File:
virtualtourism.db

File Storage:
- Local storage
- Static folder structure

Deployment:
- Render
- Railway
- PythonAnywhere

====================================================
AUTHENTICATION
====================================================

Implement OAuth2 Login using:

- Google Login
- Microsoft Login
- GitHub Login

Users should be able to:

- Register automatically
- Login
- Logout
- View Profile

Store:

users
- id
- email
- username
- avatar_url
- provider
- provider_id
- created_at

====================================================
DATABASE STRUCTURE
====================================================

users
- id
- email
- username
- avatar_url
- provider
- provider_id
- created_at

destinations
- id
- name
- description
- location
- category
- thumbnail
- hero_image
- model_path

hotspots
- id
- destination_id
- title
- description
- x_position
- y_position
- z_position
- image_path
- audio_path

====================================================
CORE FEATURES
====================================================

1. Landing Page

Modern immersive landing page containing:

- Hero banner
- Featured destination
- About the platform
- VR tourism introduction
- Call-to-action buttons
- Login options

====================================================

2. Explore Destinations Page

Display destination cards.

Each card includes:

- Thumbnail
- Destination Name
- Category
- Location
- Explore Button

Search functionality:

- Search destination names

====================================================

3. Destination Details Page

Display:

- Hero image
- Historical description
- Photo gallery
- Featured hotspots
- VR availability

Buttons:

- Explore in 3D
- Enter VR Mode

====================================================

4. 3D Experience Viewer

Implement Three.js scene.

Load Blender exported .glb models.

Features:

- First person movement
- Mobile touch controls
- WASD movement
- Mouse look around
- Teleport movement

====================================================

5. Interactive Hotspots

Clickable markers inside the 3D scene.

When clicked:

Display:

- Historical information
- Image
- Audio narration
- Interesting facts

Example hotspots:

- Main Entrance
- Japanese Tunnel
- Command Centre
- Observation Tower
- Prison Area
- Underground Bunker
- Memorial Zone
- Weapons Display
- Lookout Point
- Escape Route

====================================================

6. VR MODE

Implement WebXR support.

Features:

- Google Cardboard compatibility
- Split-screen stereoscopic rendering
- Gyroscope support
- Head tracking

VR Button:

"Enter VR Experience"

Must work on Android smartphones.

====================================================
BLENDER INTEGRATION
====================================================

Support loading:

- .glb
- .gltf

Files exported from Blender.

Model optimization:

- Low polygon count
- Compressed textures
- Fast mobile loading

Should support:

- Terrain
- Buildings
- Museum interiors
- Historical objects
- Lighting environments

====================================================
MVP CONTENT
====================================================

Preload one destination:

Muzium Perang Penang

Include:

- Full destination profile
- Historical information
- 10 interactive hotspots
- Sample narration content
- Sample images

====================================================
USER PROFILE PAGE
====================================================

Display:

- User Avatar
- Username
- Login Provider
- Joined Date

====================================================
ADMIN PANEL
====================================================

Create lightweight admin panel.

Admin can:

- Add destinations
- Upload GLB models
- Create hotspots
- Edit descriptions
- Upload images
- Upload audio narrations

====================================================
UI DESIGN
====================================================

Style:

- Modern
- Premium
- Tourism-focused
- Apple Vision Pro inspired
- Dark Mode

Primary Colors:

- Deep Blue (#0A192F)
- Cyan (#00D4FF)
- White (#FFFFFF)

Design Elements:

- Glassmorphism cards
- Smooth animations
- Modern navigation
- Mobile responsive layouts

====================================================
PERFORMANCE TARGETS
====================================================

- Load in less than 5 seconds
- Mobile friendly
- 60 FPS target
- Optimized Blender assets
- Lazy loading of assets

====================================================
PROJECT STRUCTURE
====================================================

/app
/routes
/models
/templates
/static
/css
/js
/models
/images
/audio

/templates
index.html
explore.html
destination.html
viewer.html
profile.html
admin.html

====================================================
THREE.JS MODULES
====================================================

Generate reusable modules:

- SceneManager
- ModelLoader
- CameraController
- MovementSystem
- HotspotManager
- VRController

====================================================
DELIVERABLES
====================================================

Generate complete source code including:

- Flask Backend
- SQLite Integration
- OAuth Authentication
- Database Models
- Routes
- Templates
- Tailwind CSS
- Three.js Viewer
- WebXR VR Mode
- Admin Dashboard
- Seed Data for Muzium Perang Penang
- Setup Instructions

The final application should run locally with:

pip install -r requirements.txt
python app.py

and provide a fully functional hackathon MVP demonstration.
