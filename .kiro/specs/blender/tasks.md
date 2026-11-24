# Tasks: Blender Asset Pipeline and Model Loading

- [x] 1. Documentation
  - [x] 1.1 Write `docs/blender-export.md` (units, naming, `spawn`, export settings, budgets, gltf-transform command)
  - _Requirements: 3, 4, 6_

- [x] 2. Placeholder model
  - [x] 2.1 Produce `static/models/muzium_perang.glb` (ground, simple buildings, tunnel, `floor_*` names, `spawn` empty), via Blender script or a Three.js GLTFExporter script
  - [x] 2.2 Confirm file size is under the 15 MB target
  - _Requirements: 3, 4, 6_

- [x] 3. ModelLoader
  - [x] 3.1 Set up GLTFLoader with Draco, optional KTX2 and meshopt; vendor decoder files locally
  - [x] 3.2 Return `{ scene, walkables, spawn }` with fallbacks
  - [x] 3.3 Progress callback and descriptive errors
  - [x] 3.4 Mobile-oriented settings (anisotropy, no shadows) and dispose on unload
  - _Requirements: 1, 2, 4, 5_

- [x] 4. Delivery
  - [x] 4.1 Ensure GLB is served with proper caching and compression on the target host
  - [x] 4.2 Add default fallback lights in `SceneManager` for unlit models
  - _Requirements: 2, 5_

- [x] 5. Verification
  - [ ] 5.1 Load the placeholder on desktop and Android; check progress, spawn, teleport and FPS
  - [ ] 5.2 Load a Draco-compressed sample to verify decoder setup
  - _Requirements: 1-5_

- [x] 6. As-built pipeline: build, props, export and optimize scripts; model in `app/static/models/`; `blender/README.md`
- [ ] 7. Confirm provisional positions and the 9 m escape climb on site or with museum material
- [ ] 8. Reduce materials and textures (prop atlas) for low-end phones
