# VirtualTourism: project context

Hackathon-ready web app for exploring tourist sites in 3D and VR. First destination: Muzium Perang Penang, Malaysia.

- Source of truth for requirements: `appgenprompt.md`. Longer product vision: `masterprompt.md` (not in MVP scope).
- Specs: `.kiro/specs/{core,auth,db,admin,blender,content,ui,user}/` each with requirements.md, design.md, tasks.md.
- Stack: Flask, Flask-SQLAlchemy (SQLite `virtualtourism.db`), Flask-Login, Authlib, Jinja, TailwindCSS, Three.js (GLTFLoader, WebXR). Blender for models.
- Must run locally with `pip install -r requirements.txt` and `python app.py`.
- UI: dark mode, Deep Blue `#0A192F`, Cyan `#00D4FF`, White `#FFFFFF`, glassmorphism.
- Priorities: functionality, visual impact, VR, simplicity, mobile. Avoid enterprise architecture.
- Secrets only in environment variables. Never commit them.
- Do not add tests unless asked.
