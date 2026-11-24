// VRController: WebXR immersive-vr when available; otherwise Google Cardboard style split-screen + gyroscope head tracking.
import * as THREE from 'three';
import { StereoEffect } from 'three/addons/effects/StereoEffect.js';

const Z = new THREE.Vector3(0, 0, 1);
const Q1 = new THREE.Quaternion(-Math.sqrt(0.5), 0, 0, Math.sqrt(0.5));   // camera looks out the back of the device

export class VRController {
  constructor(sm, cam, move) {
    this.sm = sm; this.cam = cam; this.move = move;
    this.xrSupported = false;
    this.mode = 'off';                 // 'off' | 'xr' | 'stereo'
    this.onModeChange = null;          // (mode) => void
    this.onSelect = null;              // (origin, direction) => void   XR controller trigger
    this._effect = null;
    this._quat = new THREE.Quaternion();
    this._euler = new THREE.Euler();
    this._q0 = new THREE.Quaternion();
    this._orient = { alpha: 0, beta: 0, gamma: 0, ready: false };
    this._alphaOffset = null;
    this._onOrient = (e) => {
      if (e.alpha === null || e.alpha === undefined) return;
      this._orient.alpha = e.alpha; this._orient.beta = e.beta; this._orient.gamma = e.gamma; this._orient.ready = true;
      if (this._alphaOffset === null) this._alphaOffset = -e.alpha;     // first reading = looking straight ahead
    };
    sm.renderer.xr.enabled = true;
    try { sm.renderer.xr.setReferenceSpaceType('local-floor'); } catch (_) { /* older browsers */ }
    sm.onUpdate((dt) => this._update(dt));
    const prevResize = sm.onResize;
    sm.onResize = (w, h) => { if (prevResize) prevResize(w, h); if (this._effect) this._effect.setSize(w, h); };
  }

  async init() {
    try { this.xrSupported = !!(navigator.xr && await navigator.xr.isSessionSupported('immersive-vr')); }
    catch (_) { this.xrSupported = false; }
    return this.xrSupported;
  }

  /** Must be called from a user gesture (button press). */
  async enter() {
    if (this.mode !== 'off') return;
    if (this.xrSupported) {
      try { await this._enterXR(); return; } catch (err) { console.warn('WebXR failed, using Cardboard mode', err); }
    }
    await this._enterStereo();
  }

  async _enterXR() {
    const session = await navigator.xr.requestSession('immersive-vr', { optionalFeatures: ['local-floor', 'bounded-floor'] });
    const xr = this.sm.renderer.xr;
    await xr.setSession(session);
    this.session = session;
    this.mode = 'xr';
    const c = xr.getController(0);
    c.addEventListener('selectstart', () => {
      const o = c.getWorldPosition(new THREE.Vector3());
      const d = new THREE.Vector3(0, 0, -1).applyQuaternion(c.getWorldQuaternion(new THREE.Quaternion()));
      if (this.onSelect) this.onSelect(o, d);
    });
    const line = new THREE.Line(new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(), new THREE.Vector3(0, 0, -6)]),
      new THREE.LineBasicMaterial({ color: 0x00d4ff }));
    c.add(line);
    this.sm.rig.add(c);
    this._xrController = c;
    session.addEventListener('end', () => {
      this.sm.rig.remove(c);
      this.mode = 'off'; this.session = null;
      this.sm.camera.position.set(0, this.cam.eye, 0);
      if (this.onModeChange) this.onModeChange('off');
    });
    if (this.onModeChange) this.onModeChange('xr');
  }

  async _enterStereo() {
    // iOS needs an explicit permission prompt for motion sensors
    if (typeof DeviceOrientationEvent !== 'undefined' && typeof DeviceOrientationEvent.requestPermission === 'function') {
      const r = await DeviceOrientationEvent.requestPermission();
      if (r !== 'granted') throw new Error('Motion sensor permission was denied');
    }
    this._alphaOffset = null;
    this._orient.ready = false;
    window.addEventListener('deviceorientation', this._onOrient, true);
    this._effect = new StereoEffect(this.sm.renderer);
    const w = this.sm.container.clientWidth, h = this.sm.container.clientHeight;
    this._effect.setSize(w, h);
    this.sm.renderFn = () => this._effect.render(this.sm.scene, this.sm.camera);
    this.cam.gyro = { quaternion: this._quat };
    this.mode = 'stereo';
    document.body.classList.add('stereo');
    try { await (this.sm.container.requestFullscreen || this.sm.container.webkitRequestFullscreen).call(this.sm.container); } catch (_) { /* optional */ }
    try { if (screen.orientation && screen.orientation.lock) await screen.orientation.lock('landscape'); } catch (_) { /* optional */ }
    if (this.onModeChange) this.onModeChange('stereo');
  }

  exit() {
    if (this.mode === 'xr' && this.session) { this.session.end(); return; }
    if (this.mode !== 'stereo') return;
    window.removeEventListener('deviceorientation', this._onOrient, true);
    this.sm.renderFn = () => this.sm.renderer.render(this.sm.scene, this.sm.camera);
    this.sm.renderer.setViewport(0, 0, this.sm.container.clientWidth, this.sm.container.clientHeight);
    this.sm.renderer.setScissorTest(false);
    this._effect = null;
    this.cam.gyro = null;
    this.cam.pitch = 0;
    this.sm.camera.rotation.set(0, 0, 0);
    this.mode = 'off';
    document.body.classList.remove('stereo');
    try { if (document.fullscreenElement) document.exitFullscreen(); } catch (_) { /* ignore */ }
    try { if (screen.orientation && screen.orientation.unlock) screen.orientation.unlock(); } catch (_) { /* ignore */ }
    this.sm.resize();
    if (this.onModeChange) this.onModeChange('off');
  }

  recenter() { this._alphaOffset = this._orient.ready ? -this._orient.alpha : null; }

  _update(dt) {
    if (this.mode === 'xr') this.move.xrAxes(dt, this.session);
    if (this.mode !== 'stereo' || !this._orient.ready) return;
    const d2r = Math.PI / 180, o = this._orient;
    const orient = ((screen.orientation && screen.orientation.angle) || window.orientation || 0) * d2r;
    this._euler.set(o.beta * d2r, (o.alpha + (this._alphaOffset || 0)) * d2r, -o.gamma * d2r, 'YXZ');
    this._quat.setFromEuler(this._euler);
    this._quat.multiply(Q1);
    this._quat.multiply(this._q0.setFromAxisAngle(Z, -orient));
  }
}
