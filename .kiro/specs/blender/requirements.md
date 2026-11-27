# Requirements: Blender Asset Pipeline and Model Loading

## Introduction
3D environments are modelled in Blender, exported as glTF binary (`.glb`) and loaded by the web viewer. Assets must stay light enough to load fast on mobile phones.

## Requirements

### Requirement 1: Supported formats
#### Acceptance Criteria
1. The viewer SHALL load `.glb` and `.gltf` files exported from Blender.
2. The loader SHALL support Draco or meshopt compressed geometry and KTX2/WebP compressed textures when present.

### Requirement 2: Content types
#### Acceptance Criteria
1. The pipeline SHALL support terrain, buildings, museum interiors, historical objects and lighting environments.
2. Lighting SHALL be baked into textures or lightmaps where possible, and the viewer SHALL add fallback ambient/hemisphere lights for unlit scenes.

### Requirement 3: Optimization budgets
#### Acceptance Criteria
1. Each destination model SHOULD be under 40 MB (hard cap 50 MB) and under about 1.1M triangles drawn per view (scene total about 2.1M with distance-culled trees; raised from 15 MB and 150k on 2026-11-25 at the user's request for more realism).
2. Textures SHOULD be at most 2048 px (1024 px for props), with a limited number of materials (target under 30).
3. Models SHOULD use meshes merged by material and instances for repeated objects.

### Requirement 4: Scene conventions
#### Acceptance Criteria
1. Models SHALL use meters, Y-up (glTF default) with the origin at the visitor start position on the ground.
2. Walkable surfaces SHALL be named with the prefix `floor_` or `ground_` so teleport raycasts can target them.
3. An optional empty named `spawn` SHALL define the starting position and orientation.
4. Hotspot coordinates in the database SHALL be in the same coordinate space as the exported model.

### Requirement 5: Loading experience
#### Acceptance Criteria
1. The viewer SHALL show loading progress while the model downloads.
2. The server SHALL serve GLB with gzip or correct caching headers, and the viewer SHALL load the model only on the viewer page.

### Requirement 6: Documentation and placeholder
#### Acceptance Criteria
1. A `docs/blender-export.md` SHALL document modelling conventions, export settings and the optimization workflow.
2. The repo SHALL include a small placeholder GLB for Muzium Perang Penang so the demo works before the final model exists.

## Additional requirements (added during the build)
- The model SHALL be reproducible from scripts in `blender/scripts/` (build, props, export, optimize) without manual sculpting.
- Third-party props SHALL be CC0 (Poly Haven) and decimated to a few hundred to a few thousand triangles; trees are the exception (see the tree tiers in design.md).
- Empty marker nodes (`spawn`, `hotspot_*`, `loc_*`) SHALL survive optimization.
- Placement that is not confirmed (memorial, escape route, lookout, Japanese tunnel, bunker) SHALL be flagged `provisional` in `blender/out/hotspots.json`.
