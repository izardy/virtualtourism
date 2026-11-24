// SceneManager: renderer, camera rig, lights, night/day atmosphere, render loop.
import * as THREE from 'three';

export class SceneManager {
  constructor(container) {
    this.container = container;
    this.isMobile = /Android|iPhone|iPad|iPod|Mobi/i.test(navigator.userAgent) || (('ontouchstart' in window) && Math.min(screen.width, screen.height) < 900);
    this.maxPixelRatio = this.isMobile ? 1.5 : 2;

    this.renderer = new THREE.WebGLRenderer({ antialias: !this.isMobile, powerPreference: 'high-performance' });
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, this.maxPixelRatio));
    this.renderer.outputColorSpace = THREE.SRGBColorSpace;
    this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
    this.renderer.toneMappingExposure = 1.05;
    container.appendChild(this.renderer.domElement);

    this.scene = new THREE.Scene();
    this.camera = new THREE.PerspectiveCamera(72, 1, 0.1, 700);
    // rig = the player's body (position + yaw). camera = the head (pitch, eye height, XR pose).
    this.rig = new THREE.Group();
    this.rig.add(this.camera);
    this.scene.add(this.rig);

    this.hemi = new THREE.HemisphereLight(0x9fb8ff, 0x1c2a1c, 0.6);
    this.sun = new THREE.DirectionalLight(0xbfd8ff, 1.0);
    this.sun.position.set(-80, 140, 60);
    this.torch = new THREE.SpotLight(0xffdfb0, 0, 30, Math.PI / 4, 1.0, 1.6);   // the visitor's lantern
    this.torch.position.set(0.15, -0.1, 0);
    this.torch.target.position.set(0, -0.2, -6);
    this.camera.add(this.torch, this.torch.target);
    this.scene.add(this.hemi, this.sun);

    this.fireflies = this._makeFireflies();
    this.rig.add(this.fireflies);

    this.updaters = [];
    this.clock = new THREE.Clock();
    this.renderFn = () => this.renderer.render(this.scene, this.camera);
    this.night = true;
    this.setNight(true);
    this.resize();
    window.addEventListener('resize', () => this.resize());
    window.addEventListener('orientationchange', () => setTimeout(() => this.resize(), 250));
    this.renderer.setAnimationLoop(() => this._tick());

    // simple frame-time statistics for the adaptive quality check
    this.frameTimes = [];
  }

  onUpdate(fn) { this.updaters.push(fn); }

  resize() {
    const w = this.container.clientWidth || window.innerWidth, h = this.container.clientHeight || window.innerHeight;
    this.renderer.setSize(w, h);
    this.camera.aspect = w / h;
    this.camera.updateProjectionMatrix();
    if (this.onResize) this.onResize(w, h);
  }

  setQuality(pixelRatio, fireflies) {
    this.renderer.setPixelRatio(pixelRatio);
    this.fireflies.visible = fireflies;
    this.resize();
  }

  setNight(on) {
    this.night = on;
    if (on) {
      this.scene.background = new THREE.Color(0x050b16);
      this.scene.fog = new THREE.FogExp2(0x0a1626, 0.016);
      this.hemi.intensity = 0.9; this.hemi.color.set(0x8fa8e8);
      this.sun.intensity = 0.9; this.sun.color.set(0x9fc0ff);   // moonlight
      this.torch.intensity = 85;
      this.renderer.toneMappingExposure = 1.15;
    } else {
      this.scene.background = new THREE.Color(0x8ec7e6);
      this.scene.fog = new THREE.FogExp2(0xb9dcee, 0.0035);
      this.hemi.intensity = 1.25; this.hemi.color.set(0xdff1ff);
      this.sun.intensity = 2.4; this.sun.color.set(0xfff2d6);
      this.torch.intensity = 0;
      this.renderer.toneMappingExposure = 1.0;
    }
    this.fireflies.material.opacity = on ? 0.9 : 0;
  }

  _makeFireflies() {
    const n = 90, pos = new Float32Array(n * 3);
    this._ffSeed = [];
    for (let i = 0; i < n; i++) {
      this._ffSeed.push({ a: Math.random() * 6.28, r: 3 + Math.random() * 24, y: 0.4 + Math.random() * 3.2, s: 0.2 + Math.random() * 0.5 });
    }
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.BufferAttribute(pos, 3));
    const c = document.createElement('canvas'); c.width = c.height = 32;
    const ctx = c.getContext('2d'); const grd = ctx.createRadialGradient(16, 16, 0, 16, 16, 16);
    grd.addColorStop(0, 'rgba(210,245,255,1)'); grd.addColorStop(0.4, 'rgba(0,212,255,.5)'); grd.addColorStop(1, 'rgba(0,212,255,0)');
    ctx.fillStyle = grd; ctx.fillRect(0, 0, 32, 32);
    const m = new THREE.PointsMaterial({ size: 0.45, map: new THREE.CanvasTexture(c), transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, opacity: 0.9 });
    const pts = new THREE.Points(g, m);
    pts.frustumCulled = false;
    return pts;
  }

  _updateFireflies(t) {
    if (!this.fireflies.visible || !this.night) return;
    const p = this.fireflies.geometry.attributes.position;
    for (let i = 0; i < this._ffSeed.length; i++) {
      const s = this._ffSeed[i], a = s.a + t * s.s * 0.3;
      p.setXYZ(i, Math.cos(a) * s.r, s.y + Math.sin(t * s.s + i) * 0.5, Math.sin(a) * s.r);
    }
    p.needsUpdate = true;
  }

  _tick() {
    const dt = Math.min(this.clock.getDelta(), 0.1), t = this.clock.elapsedTime;
    this.frameTimes.push(dt); if (this.frameTimes.length > 240) this.frameTimes.shift();
    for (const fn of this.updaters) fn(dt, t);
    this._updateFireflies(t);
    this.renderFn();
  }

  averageFps() {
    if (this.frameTimes.length < 30) return 60;
    return 1 / (this.frameTimes.reduce((a, b) => a + b, 0) / this.frameTimes.length);
  }
}
