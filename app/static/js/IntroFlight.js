// IntroFlight: opening camera move. The view starts high above the fort, looking down on the whole site, then glides
// down along a smooth curve and settles at the entrance, at eye height and facing the way the visitor will start.
// Movement and look controls are off while it plays; any key, tap or the Skip button ends it at once.
import * as THREE from 'three';

const smooth = (a, b, x) => { const t = Math.min(1, Math.max(0, (x - a) / (b - a))); return t * t * (3 - 2 * t); };
const easeInOut = (t) => 0.5 - 0.5 * Math.cos(Math.PI * t);

export class IntroFlight {
  /**
   * @param {SceneManager} sm @param {CameraController} cam @param {MovementSystem} move
   * @param {{centre: THREE.Vector3, duration?: number, onEnd?: Function}} opts  centre = middle of the site on the ground
   */
  constructor(sm, cam, move, opts) {
    this.sm = sm; this.cam = cam; this.move = move;
    this.duration = opts.duration || 11;
    this.onEnd = opts.onEnd || null;
    this.active = false; this.t = 0;

    // end pose: where the visitor stands, at eye height, looking along the start yaw
    const end = move.pos.clone(); end.y += cam.eye;
    const fwd = new THREE.Vector3(-Math.sin(cam.yaw), 0, -Math.cos(cam.yaw));
    const c = opts.centre.clone();
    const toEnd = end.clone().sub(c).setY(0); if (toEnd.lengthSq() < 1) toEnd.set(0, 0, 1); toEnd.normalize();
    // cubic Bezier: high over the site (a little toward the entrance so the view never looks straight down), a wide
    // descent toward the entrance, then a low approach from behind the visitor's start position
    this.p = [
      c.clone().addScaledVector(toEnd, 30).add(new THREE.Vector3(0, 175, 0)),
      c.clone().lerp(end, 0.6).add(new THREE.Vector3(0, 95, 0)),
      end.clone().addScaledVector(fwd, -40).add(new THREE.Vector3(0, 9, 0)),     // low enough to pass under the gate sign
      end,
    ];
    this.lookSite = c;                                           // early: the middle of the fort
    this.lookEnd = end.clone().addScaledVector(fwd, 30);         // late: ahead of the visitor, at eye height
    this._pos = new THREE.Vector3(); this._look = new THREE.Vector3();
  }

  _bezier(t, out) {
    const [a, b, c, d] = this.p, u = 1 - t;
    return out.set(0, 0, 0).addScaledVector(a, u * u * u).addScaledVector(b, 3 * u * u * t).addScaledVector(c, 3 * u * t * t).addScaledVector(d, t * t * t);
  }

  start() {
    this.active = true; this.t = 0; this._t0 = performance.now();
    this._moveWas = this.move.enabled; this._camWas = this.cam.enabled;
    this.move.enabled = false; this.cam.enabled = false;
    this._ffWas = this.sm.fireflies.visible; this.sm.fireflies.visible = false;   // they live on the rig, around the camera
    this._apply(0);
  }

  update(dt) {
    if (!this.active) return;
    if (this.sm.renderer.xr.isPresenting) { this.finish(); return; }
    this.t = (performance.now() - this._t0) / 1000 / this.duration;    // wall-clock time: the same length on slow devices
    if (this.t >= 1) { this.finish(); return; }
    this._apply(this.t);
  }

  _apply(t) {
    const { rig, camera, scene } = this.sm;
    const e = easeInOut(t);
    this._bezier(e, this._pos);
    this._look.copy(this.lookSite).lerp(this.lookEnd, smooth(0.35, 0.95, e));
    rig.position.copy(this._pos); rig.rotation.set(0, 0, 0);
    camera.position.set(0, 0, 0); camera.lookAt(this._look);
    // thin the fog while high up, so the whole site shows; full fog again near the ground
    if (scene.fog && scene.fog.density !== undefined) {
      const base = this.sm.night ? 0.014 : 0.0035;
      scene.fog.density = base * (0.12 + 0.88 * smooth(0.55, 1.0, e));
    }
  }

  finish() {
    if (!this.active) return;
    this.active = false;
    const { rig, camera, scene } = this.sm;
    rig.position.copy(this.move.pos);
    camera.position.set(0, this.cam.eye, 0); camera.rotation.set(this.cam.pitch, 0, 0, 'YXZ');
    if (scene.fog && scene.fog.density !== undefined) scene.fog.density = this.sm.night ? 0.014 : 0.0035;
    this.move.enabled = this._moveWas; this.cam.enabled = this._camWas;
    this.sm.fireflies.visible = this._ffWas;
    if (this.onEnd) { const f = this.onEnd; this.onEnd = null; f(); }
  }
}
