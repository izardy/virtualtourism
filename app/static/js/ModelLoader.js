// ModelLoader: loads a Blender-exported .glb/.gltf (Draco + WebP supported) and indexes what the viewer needs.
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { DRACOLoader } from 'three/addons/loaders/DRACOLoader.js';

/**
 * @returns {Promise<{root: THREE.Object3D, walkables: THREE.Mesh[], colliders: THREE.Mesh[],
 *   spawn: THREE.Vector3|null, hotspotNodes: Object<string, THREE.Vector3>, points: Array}>}
 */
export async function loadModel(url, { dracoPath, onProgress, anisotropy = 4 } = {}) {
  const loader = new GLTFLoader();
  const draco = new DRACOLoader();
  draco.setDecoderPath(dracoPath);
  loader.setDRACOLoader(draco);

  const gltf = await loader.loadAsync(url, (e) => {
    if (onProgress && e.total) onProgress(e.loaded / e.total);
  }).catch((err) => { throw new Error(err && err.message ? err.message : 'Could not load the 3D model'); });
  draco.dispose();

  const root = gltf.scene;
  root.updateMatrixWorld(true);
  const walkables = [], colliders = [], hotspotNodes = {}, points = [];
  let spawn = null;
  const v = new THREE.Vector3();

  root.traverse((o) => {
    const name = o.name || '';
    if (o.isMesh || o.isInstancedMesh) {
      o.frustumCulled = true;
      const mats = Array.isArray(o.material) ? o.material : [o.material];
      for (const m of mats) { if (m && m.map) m.map.anisotropy = anisotropy; }
      if (/^(floor_|ground_)/.test(name)) walkables.push(o);
      else if (/^struct_/.test(name)) colliders.push(o);
    } else if (name === 'spawn') {
      spawn = o.getWorldPosition(new THREE.Vector3());
    } else if (name.startsWith('hotspot_')) {
      hotspotNodes[name.slice('hotspot_'.length)] = o.getWorldPosition(v.clone());
    } else if (name.startsWith('loc_')) {
      points.push({ name, position: o.getWorldPosition(new THREE.Vector3()) });
    }
  });

  if (!walkables.length) {   // fallback so any model can be explored: every mesh is a floor
    root.traverse((o) => { if (o.isMesh) walkables.push(o); });
  }
  return { root, walkables, colliders, spawn, hotspotNodes, points };
}
