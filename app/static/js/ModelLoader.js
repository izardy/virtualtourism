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
      for (const m of mats) {
        if (!m) continue;
        if (m.map) m.map.anisotropy = anisotropy;
        if (/leaves/i.test(m.name)) {       // Poly Haven leaf cards: alpha-tested, two-sided, no sorting
          m.transparent = false; m.alphaTest = 0.5; m.side = THREE.DoubleSide; m.depthWrite = true; m.needsUpdate = true;
        }
        if (m.transmission > 0) {           // glass with transmission makes three.js render the whole scene twice per frame
          m.transmission = 0; m.transparent = true; m.opacity = 0.35; m.depthWrite = false; m.needsUpdate = true;
        }
      }
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
  const chunks = chunkInstances(root, 70);
  return { root, walkables, colliders, spawn, hotspotNodes, points, chunks };
}

/**
 * Split each large InstancedMesh (trees, shrubs) into one InstancedMesh per cell of `cell` metres. three.js culls an
 * InstancedMesh as a whole, so without this every tree is drawn even when it is behind the camera.
 * Returns the chunks so the viewer can also hide those beyond the fog.
 */
function chunkInstances(root, cell) {
  const list = [], chunks = [];
  root.traverse((o) => { if (o.isInstancedMesh && o.count > 6 && !o.instanceColor && !/^(floor_|ground_|struct_)/.test(o.name || '')) list.push(o); });
  const m = new THREE.Matrix4(), p = new THREE.Vector3();
  for (const im of list) {
    const buckets = new Map();
    for (let i = 0; i < im.count; i++) {
      im.getMatrixAt(i, m); p.setFromMatrixPosition(m).applyMatrix4(im.matrixWorld);
      const key = Math.floor(p.x / cell) + ',' + Math.floor(p.z / cell);
      if (!buckets.has(key)) buckets.set(key, []);
      buckets.get(key).push(m.clone());
    }
    if (buckets.size < 2) continue;
    for (const mats of buckets.values()) {
      const part = new THREE.InstancedMesh(im.geometry, im.material, mats.length);
      mats.forEach((mm, i) => part.setMatrixAt(i, mm));
      part.name = im.name; part.position.copy(im.position); part.quaternion.copy(im.quaternion); part.scale.copy(im.scale);
      part.frustumCulled = true; part.instanceMatrix.needsUpdate = true;
      part.computeBoundingBox(); part.computeBoundingSphere();
      im.parent.add(part); chunks.push(part);
    }
    im.parent.remove(im);
  }
  return chunks;
}
