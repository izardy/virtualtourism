// CameraController: first-person look (mouse drag, touch drag), tap / double-tap detection, gyroscope hand-over.
import * as THREE from 'three';

export class CameraController {
  constructor(sm, dom) {
    this.sm = sm;
    this.dom = dom;
    this.yaw = 0;
    this.pitch = 0;
    this.eye = 1.65;
    this.enabled = true;
    this.gyro = null;                 // set by VRController: { quaternion } while head tracking is active
    this.onTap = null;                // (clientX, clientY) single tap / click without drag
    this.onDoubleTap = null;          // (clientX, clientY)
    this.onHover = null;              // (clientX, clientY) mouse move without buttons
    this.lastLookTime = 0;            // performance.now() of the last drag-look (the guided tour waits before turning the view)
    this._look = null;                // active look pointer
    this._lastTap = { t: 0, x: 0, y: 0 };
    sm.camera.position.set(0, this.eye, 0);

    dom.addEventListener('pointerdown', (e) => this._down(e));
    dom.addEventListener('pointermove', (e) => this._move(e));
    dom.addEventListener('pointerup', (e) => this._up(e));
    dom.addEventListener('pointercancel', (e) => this._up(e, true));
    dom.addEventListener('contextmenu', (e) => e.preventDefault());
  }

  setYaw(y) { this.yaw = y; }

  _down(e) {
    if (!this.enabled || (e.pointerType === 'mouse' && e.button !== 0)) return;
    if (this._look) return;           // one look pointer at a time; the joystick owns the other finger
    this._look = { id: e.pointerId, x: e.clientX, y: e.clientY, sx: e.clientX, sy: e.clientY, t: performance.now(), moved: 0 };
    try { this.dom.setPointerCapture(e.pointerId); } catch (_) { /* ignore */ }
  }

  _move(e) {
    const l = this._look;
    if (!l || e.pointerId !== l.id) { if (e.pointerType === 'mouse' && this.onHover) this.onHover(e.clientX, e.clientY); return; }
    const dx = e.clientX - l.x, dy = e.clientY - l.y;
    l.x = e.clientX; l.y = e.clientY; l.moved += Math.abs(dx) + Math.abs(dy);
    if (l.moved > 6) this.lastLookTime = performance.now();
    if (this.gyro) return;            // head tracking drives the view
    const k = e.pointerType === 'mouse' ? 0.0042 : 0.0052;
    this.yaw -= dx * k;
    this.pitch = Math.max(-1.25, Math.min(1.25, this.pitch - dy * k));
  }

  _up(e, cancelled = false) {
    const l = this._look;
    if (!l || e.pointerId !== l.id) return;
    this._look = null;
    try { this.dom.releasePointerCapture(e.pointerId); } catch (_) { /* ignore */ }
    const quick = performance.now() - l.t < 380;
    const total = Math.hypot(e.clientX - l.sx, e.clientY - l.sy);
    if (cancelled || !quick || total > 9) return;
    const now = performance.now(), lt = this._lastTap;
    if (now - lt.t < 380 && Math.hypot(e.clientX - lt.x, e.clientY - lt.y) < 40) {
      this._lastTap = { t: 0, x: 0, y: 0 };
      if (this.onDoubleTap) this.onDoubleTap(e.clientX, e.clientY);
    } else {
      this._lastTap = { t: now, x: e.clientX, y: e.clientY };
      if (this.onTap) this.onTap(e.clientX, e.clientY);
    }
  }

  /** Called every frame (not in WebXR: the headset owns the camera). */
  update() {
    const { rig, camera, renderer } = this.sm;
    rig.rotation.y = this.yaw;
    if (renderer.xr.isPresenting) return;
    camera.position.y = this.eye;
    if (this.gyro) camera.quaternion.copy(this.gyro.quaternion);
    else camera.rotation.set(this.pitch, 0, 0, 'YXZ');
  }

  /** Horizontal unit vector the user is looking along (works with mouse, gyro and XR). */
  flatForward(out = new THREE.Vector3()) {
    this.sm.camera.getWorldDirection(out);
    out.y = 0;
    if (out.lengthSq() < 1e-6) out.set(-Math.sin(this.yaw), 0, -Math.cos(this.yaw));
    return out.normalize();
  }
}
