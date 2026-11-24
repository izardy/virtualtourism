# Design: Blender Asset Pipeline and Model Loading

## Overview
Blender is the authoring tool. The web app consumes optimized `.glb` files through Three.js `GLTFLoader`. This spec defines the authoring conventions, export settings, optimization steps and the loader behavior.

## Folders
- `reference/`: user-supplied source material (site map, photos per hotspot, video, `NOTES.md`). Layout is in the core design.
- `blender/src/`: `.blend` files. `blender/scripts/`: `bpy` scripts and optimization commands.
- `app/static/models/`: only the optimized `.glb` served to users.

## Authoring workflow
1. Block out the site (terrain, buildings, interior, tunnels) at real scale in meters.
2. Model low-poly, using normal maps for detail instead of geometry.
3. Name walkable meshes `floor_*` / `ground_*`; add an Empty `spawn`.
4. Bake lighting (AO and light maps) to textures; use a limited material set and texture atlases.
5. Apply transforms and modifiers, delete hidden faces, merge by material, use linked duplicates for repeated props.
6. Export, then optimize.

## Export settings (Blender glTF 2.0)
- Format: glTF Binary (`.glb`), +Y Up, Apply Modifiers on.
- Include: Cameras off, Punctual Lights off (viewer sets its own lights), Custom Properties off.
- Mesh: compression with Draco (level ~6) or optimize afterward with `gltf-transform`.
- Images: WebP or JPEG textures; avoid 4K.
- Animation: off unless needed.

## Post-export optimization
```
npx gltf-transform optimize in.glb out.glb --compress draco --texture-compress webp --texture-size 2048
```
Check the result in a glTF viewer and compare size against budgets.

## Loader design (`ModelLoader`)
- `GLTFLoader` with `DRACOLoader` (decoder path in `static/js/vendor/draco/`) and optional `KTX2Loader` and `MeshoptDecoder`.
- `load(url, onProgress)` returns `{ scene, walkables, spawn }`:
  - `walkables`: meshes whose name starts with `floor_` or `ground_` (fallback: all meshes if none found).
  - `spawn`: object named `spawn`, else the origin.
- Sets `frustumCulled = true`, disables shadows by default, and sets texture anisotropy to a low value on mobile.
- On error, rejects with a descriptive message handled by the viewer.

## LOD and performance
- Large scenes may split into interior and exterior GLBs later; for the MVP use one GLB.
- Hotspot markers are lightweight sprites, not part of the GLB.
- Dispose geometries/materials when leaving the page.

## Placeholder asset
`static/models/muzium_perang.glb`: a simple generated scene (ground plane, a few boxes representing buildings and a tunnel) used until the real model is delivered. Hotspot coordinates are chosen to sit within it.

## Documentation
`docs/blender-export.md` captures the conventions and commands above.

## Testing
Load the placeholder and an optimized sample in desktop Chrome and Android Chrome; confirm progress, spawn placement, teleport onto `floor_*` meshes and FPS.
