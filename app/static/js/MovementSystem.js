// MovementSystem: WASD / arrows, touch joystick, auto-walk (Cardboard), ground following, wall collisions, teleport.
import * as THREE from 'three';

export class MovementSystem {
  constructor(sm, cam, world) {
    this.sm = sm;
    this.cam = cam;
    this.walkables = world.walkables;
    this.colliders = world.colliders;
    this.pos = new THREE.Vector3();          // feet position (the rig position)
    this.keys = new Set();
    this.joy = { x: 0, y: 0 };               // joystick, -1..1 (y up = forward)
    this.autoWalk = false;
    this.speed = 3.4; this.runSpeed = 6.5;
    this.radius = 0.4;
    this.enabled = true;
    this.onTeleport = null;
    this._ray = new THREE.Raycaster();
    this._tmp = new THREE.Vector3();
    this._tween = null;
    this._frame = 0;

    window.addEventListener('keydown', (e) => { if (!e.repeat) this.keys.add(e.code); if (['ArrowUp', 'ArrowDown', 'Space'].includes(e.code)) e.preventDefault(); });
    window.addEventListener('keyup', (e) => this.keys.delete(e.code));
    window.addEventListener('blur', () => this.keys.clear());
  }

  groundAt(x, z, fromY) {
    this._ray.set(this._tmp.set(x, fromY, z), new THREE.Vector3(0, -1, 0));
    this._ray.far = 40;
    const hit = this._ray.intersectObjects(this.walkables, false)[0];
    return hit ? hit.point.y : null;
  }

  /** Put the visitor on the ground at (x, z); y is found by ray casting from high above. */
  placeAt(x, z, hintY = 30) {
    const y = this.groundAt(x, z, hintY + 60);
    this.pos.set(x, y ?? hintY, z);
    this.sm.rig.position.copy(this.pos);
  }

  /** Smooth teleport to a point on the model (a ray-cast hit point or any x/z). */
  teleportTo(point, { yaw } = {}) {
    const y = this.groundAt(point.x, point.z, point.y + 3) ?? point.y;
    this._tween = { from: this.pos.clone(), to: new THREE.Vector3(point.x, y, point.z), t: 0, yaw };
    if (this.onTeleport) this.onTeleport();
  }

  _blocked(from, dir, dist) {
    if (!this.colliders.length) return false;
    for (const h of [0.45, 1.2]) {
      this._ray.set(this._tmp.set(from.x, from.y + h, from.z), dir);
      this._ray.far = dist + this.radius;
      if (this._ray.intersectObjects(this.colliders, false).length) return true;
    }
    return false;
  }

  _tryMove(dx, dz, dt) {
    const dist = Math.hypot(dx, dz);
    if (dist < 1e-5) return false;
    const dir = new THREE.Vector3(dx / dist, 0, dz / dist);
    if (this._blocked(this.pos, dir, dist)) return false;
    const nx = this.pos.x + dx, nz = this.pos.z + dz;
    const gy = this.groundAt(nx, nz, this.pos.y + 1.1);
    if (gy === null) return false;
    if (gy - this.pos.y > 0.35 + dist * 1.1) return false;        // too steep to climb
    this.pos.x = nx; this.pos.z = nz;
    this._targetY = gy;
    return true;
  }

  update(dt) {
    const { rig } = this.sm;
    if (this._tween) {
      const tw = this._tween; tw.t = Math.min(1, tw.t + dt / 0.35);
      const e = tw.t * tw.t * (3 - 2 * tw.t);
      this.pos.lerpVectors(tw.from, tw.to, e);
      this._targetY = this.pos.y;
      if (tw.yaw !== undefined) this.cam.setYaw(tw.yaw);
      if (tw.t >= 1) this._tween = null;
    } else if (this.enabled) {
      let f = 0, s = 0;
      const k = this.keys;
      if (k.has('KeyW') || k.has('ArrowUp')) f += 1;
      if (k.has('KeyS') || k.has('ArrowDown')) f -= 1;
      if (k.has('KeyD') || k.has('ArrowRight')) s += 1;
      if (k.has('KeyA') || k.has('ArrowLeft')) s -= 1;
      f += this.joy.y; s += this.joy.x;
      if (this.autoWalk) f = 1;
      const mag = Math.hypot(f, s);
      if (mag > 0.05) {
        if (mag > 1) { f /= mag; s /= mag; }
        const fwd = this.cam.flatForward(new THREE.Vector3());
        const right = new THREE.Vector3(-fwd.z, 0, fwd.x);
        const v = (k.has('ShiftLeft') || k.has('ShiftRight')) ? this.runSpeed : this.speed;
        const dx = (fwd.x * f + right.x * s) * v * dt, dz = (fwd.z * f + right.z * s) * v * dt;
        // slide along walls: try the full move, then each axis on its own
        if (!this._tryMove(dx, dz, dt)) { if (!this._tryMove(dx, 0, dt)) this._tryMove(0, dz, dt); }
      }
      if (this._targetY !== undefined) this.pos.y += (this._targetY - this.pos.y) * Math.min(1, dt * 14);
      else { const gy = this.groundAt(this.pos.x, this.pos.z, this.pos.y + 1.5); if (gy !== null) this.pos.y = gy; }
    }
    rig.position.copy(this.pos);
  }

  /** Thumbstick locomotion for WebXR controllers. */
  xrAxes(dt, session) {
    if (!session) return;
    for (const src of session.inputSources) {
      const a = src.gamepad && src.gamepad.axes;
      if (!a || a.length < 4) continue;
      const x = a[2], y = a[3];
      if (src.handedness === 'left' && (Math.abs(x) > 0.15 || Math.abs(y) > 0.15)) { this.joy.x = x; this.joy.y = -y; this._xrJoy = true; }
      else if (src.handedness === 'left' && this._xrJoy) { this.joy.x = this.joy.y = 0; this._xrJoy = false; }
      if (src.handedness === 'right') {
        if (Math.abs(x) > 0.7 && !this._snap) { this.cam.setYaw(this.cam.yaw - Math.sign(x) * Math.PI / 6); this._snap = true; }
        else if (Math.abs(x) < 0.3) this._snap = false;
      }
    }
  }
}
