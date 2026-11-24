// HotspotManager: glowing clickable markers, picking (mouse, touch, gaze, XR controller) and visited tracking.
import * as THREE from 'three';

function glowTexture() {
  const c = document.createElement('canvas'); c.width = c.height = 128;
  const g = c.getContext('2d'), grd = g.createRadialGradient(64, 64, 0, 64, 64, 64);
  grd.addColorStop(0, 'rgba(255,255,255,.95)'); grd.addColorStop(0.25, 'rgba(0,212,255,.65)'); grd.addColorStop(1, 'rgba(0,212,255,0)');
  g.fillStyle = grd; g.fillRect(0, 0, 128, 128);
  return new THREE.CanvasTexture(c);
}

function numberTexture(n) {
  const c = document.createElement('canvas'); c.width = c.height = 128;
  const g = c.getContext('2d');
  g.beginPath(); g.arc(64, 64, 52, 0, Math.PI * 2); g.fillStyle = 'rgba(6,16,31,.85)'; g.fill();
  g.lineWidth = 6; g.strokeStyle = '#00D4FF'; g.stroke();
  g.fillStyle = '#fff'; g.font = 'bold 64px system-ui, sans-serif'; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText(String(n), 64, 68);
  return new THREE.CanvasTexture(c);
}

export class HotspotManager {
  constructor(sm) {
    this.sm = sm;
    this.group = new THREE.Group();
    sm.scene.add(this.group);
    this.items = [];
    this.visited = new Set();
    this.onVisit = null;
    this._ray = new THREE.Raycaster();
    this._glow = glowTexture();
    sm.onUpdate((dt, t) => this._animate(t));
  }

  /** hotspots: [{id, title, position:[x,y,z], ...}] in model coordinates. */
  setHotspots(hotspots) {
    hotspots.forEach((h, i) => {
      const g = new THREE.Group();
      g.position.set(h.position[0], h.position[1], h.position[2]);
      const core = new THREE.Mesh(new THREE.SphereGeometry(0.2, 16, 12), new THREE.MeshBasicMaterial({ color: 0x00d4ff, fog: false }));
      const halo = new THREE.Sprite(new THREE.SpriteMaterial({ map: this._glow, color: 0x00d4ff, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, fog: false }));
      halo.scale.setScalar(2.4);
      const beam = new THREE.Mesh(new THREE.CylinderGeometry(0.025, 0.025, 4, 6, 1, true),
        new THREE.MeshBasicMaterial({ color: 0x00d4ff, transparent: true, opacity: 0.35, blending: THREE.AdditiveBlending, depthWrite: false, fog: false }));
      beam.position.y = 2.0;
      const label = new THREE.Sprite(new THREE.SpriteMaterial({ map: numberTexture(i + 1), transparent: true, depthWrite: false, fog: false }));
      label.scale.setScalar(0.7); label.position.y = 0.75;
      const hit = new THREE.Mesh(new THREE.SphereGeometry(1.2, 8, 6), new THREE.MeshBasicMaterial({ visible: false }));
      hit.userData.hotspotIndex = i;
      g.add(core, halo, beam, label, hit);
      this.group.add(g);
      this.items.push({ data: h, group: g, core, halo, beam, label, hit, phase: i * 0.7, baseY: g.position.y });
    });
  }

  _animate(t) {
    for (const it of this.items) {
      const s = 1 + Math.sin(t * 2.2 + it.phase) * 0.12;
      it.halo.scale.setScalar(2.4 * s);
      it.group.position.y = it.baseY + Math.sin(t * 1.4 + it.phase) * 0.08;
    }
  }

  markVisited(i) {
    if (this.visited.has(i)) return;
    this.visited.add(i);
    const it = this.items[i]; if (!it) return;
    it.core.material.color.set(0xbfe9f5); it.halo.material.color.set(0xbfe9f5); it.beam.material.opacity = 0.15;
    if (this.onVisit) this.onVisit(this.visited.size, this.items.length);
  }

  _pickRay(ray) {
    this._ray.set(ray.origin, ray.direction); this._ray.far = 200;
    const hits = this._ray.intersectObjects(this.items.map((i) => i.hit), false);
    return hits.length ? hits[0].object.userData.hotspotIndex : -1;
  }

  /** Pick by screen position (clientX/clientY relative to the canvas). */
  pickScreen(clientX, clientY, dom) {
    const r = dom.getBoundingClientRect();
    const ndc = new THREE.Vector2(((clientX - r.left) / r.width) * 2 - 1, -((clientY - r.top) / r.height) * 2 + 1);
    this._ray.setFromCamera(ndc, this.sm.camera);
    return this._pickRay({ origin: this._ray.ray.origin.clone(), direction: this._ray.ray.direction.clone() });
  }

  /** Pick what the head is looking at (Cardboard gaze). */
  pickCenter() {
    const cam = this.sm.camera;
    const o = cam.getWorldPosition(new THREE.Vector3()), d = cam.getWorldDirection(new THREE.Vector3());
    return this._pickRay({ origin: o, direction: d });
  }

  pickRay(origin, direction) { return this._pickRay({ origin, direction }); }

  nearest(position, maxDist = 6) {
    let best = -1, bd = maxDist;
    this.items.forEach((it, i) => { const d = it.group.position.distanceTo(position); if (d < bd) { bd = d; best = i; } });
    return best;
  }
}
