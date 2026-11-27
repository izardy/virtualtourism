// GuidedTour: an automatic walking tour. The visitor cannot move but can look around freely (mouse, touch, gyroscope, headset).
// Routes come from static/data/<model>_tour.json (computed in Blender with A* over the real model).
//
// Outside VR the guide walks along the route and turns the view toward the direction of travel (unless the visitor is
// looking around). In VR (WebXR or Cardboard) it hops between stops with a fade, which is much more comfortable.
import * as THREE from 'three';

const TAU = Math.PI * 2;
function angDiff(a, b) { let d = (b - a) % TAU; if (d > Math.PI) d -= TAU; if (d < -Math.PI) d += TAU; return d; }

export class GuidedTour {
  /**
   * ui: { playClip(src, done), stopClip(), openStop(index, done) -> {audio: bool, seconds: number}, closeStop(),
   *       pauseAudio(), resumeAudio(), onChange(info), onActive(bool), onFinish() }
   */
  constructor(sm, cam, move, ui) {
    this.sm = sm; this.cam = cam; this.move = move; this.ui = ui;
    this.vr = null;                 // set by the viewer: VRController (comfort mode when in VR)
    this.data = null;
    this.active = false;
    this.paused = false;
    this.state = 'idle';            // idle | intro | walking | arrived | lingering | blink | outro | finished
    this.index = -1;
    this.speedScale = 1;
    this._fade = null;
    this._wait = 0;
    this._read = null;
    this.fadeMat = new THREE.MeshBasicMaterial({ color: 0x000000, side: THREE.BackSide, transparent: true, opacity: 0, depthTest: false, depthWrite: false, fog: false });
    this.fade = new THREE.Mesh(new THREE.SphereGeometry(0.6, 16, 12), this.fadeMat);
    this.fade.renderOrder = 9999; this.fade.visible = false; this.fade.frustumCulled = false;
    sm.camera.add(this.fade);
  }

  load(data) { this.data = data; }
  get stops() { return this.data ? this.data.stops : []; }
  get comfort() { return !!(this.vr && this.vr.mode !== 'off'); }
  get userLooking() { return performance.now() - (this.cam.lastLookTime || 0) < 2500; }

  info() {
    const s = this.stops[this.index];
    return { state: this.state, index: this.index, total: this.stops.length, title: s ? s.title : '', paused: this.paused, active: this.active };
  }
  _notify() { this.ui.onChange(this.info()); }

  // ------------------------------------------------------------------ control
  start(from = 0) {
    if (!this.data) return;
    this.active = true; this.paused = false; this.move.enabled = false;
    this.ui.onActive(true);
    if (from <= 0) {
      const st = this.data.start;
      this.move.setPose(st[0], st[1], st[2]);
      const p = this.stops[0].path[1] || this.stops[0].path[0];
      this.cam.setYaw(Math.atan2(-(p[0] - st[0]), -(p[2] - st[2])));
      this.index = -1; this.state = 'intro'; this._notify();
      this.ui.playClip(this.data.intro_audio, () => { if (this.active && this.state === 'intro') this._beginLeg(0); });
    } else this._blinkTo(Math.min(from, this.stops.length - 1));
  }

  exit() {
    this.active = false; this.state = 'idle'; this.paused = false; this._fade = null; this._read = null;
    this.fadeMat.opacity = 0; this.fade.visible = false;
    this.ui.stopClip(); this.ui.closeStop();
    const p = this.move.pos;                                  // re-seat on the ground (also resets the movement system's target height)
    this.move.setPose(p.x, this.move.groundAt(p.x, p.z, p.y + 2) ?? p.y, p.z);
    this.move.enabled = true;
    this.ui.onActive(false); this._notify();
  }

  pause() { if (!this.active || this.paused) return; this.paused = true; this.ui.pauseAudio(); this._notify(); }
  resume() { if (!this.active || !this.paused) return; this.paused = false; this.ui.resumeAudio(); this._notify(); }
  togglePause() { this.paused ? this.resume() : this.pause(); }

  skipNarration() { this._narrationDone(); }
  next() { if (this.active) this._jump(this.index + 1); }
  prev() { if (this.active) this._jump(Math.max(0, this.index - 1)); }
  goTo(i) { if (this.active) this._jump(i); }

  _jump(i) {
    this.ui.stopClip(); this.ui.closeStop(); this._read = null; this.paused = false;
    if (i >= this.stops.length) { this._outro(); return; }
    this._blinkTo(i);
  }

  // ------------------------------------------------------------------ state machine
  _beginLeg(i) {
    this.index = i; this.ui.closeStop();
    if (this.comfort) { this._blinkTo(i); return; }
    const stop = this.stops[i];
    const here = this.move.pos;
    this.pts = [[here.x, here.y, here.z], ...stop.path.slice(1)];
    this.cum = [0];
    for (let k = 1; k < this.pts.length; k++) this.cum.push(this.cum[k - 1] + Math.hypot(this.pts[k][0] - this.pts[k - 1][0], this.pts[k][2] - this.pts[k - 1][2]));
    this.len = this.cum[this.cum.length - 1]; this.dist = 0;
    this.state = this.len < 0.2 ? 'arrived' : 'walking';
    if (this.state === 'arrived') this._arrive(); else this._notify();
  }

  _blinkTo(i) {
    this.index = i; this.state = 'blink'; this._notify();
    const stop = this.stops[i], to = stop.stand;
    this._startFade(1, 0.35, () => {
      this.move.setPose(to[0], to[1], to[2]);
      if (!this.comfort || true) this.cam.setYaw(stop.yaw);
      this._startFade(0, 0.45, () => { if (this.active) this._arrive(); });
    });
  }

  _startFade(to, dur, cb) { this._fade = { from: this.fadeMat.opacity, to, dur, t: 0, cb }; this.fade.visible = true; }

  _arrive() {
    this.state = 'arrived'; this._notify();
    const r = this.ui.openStop(this.index, () => this._narrationDone());
    this._read = r && !r.audio ? r.seconds : null;
  }

  _narrationDone() {
    if (!this.active || (this.state !== 'arrived')) return;
    this._read = null; this.state = 'lingering'; this._wait = 1.6; this._notify();
  }

  _outro() {
    this.state = 'outro'; this._notify(); this.ui.closeStop();
    this.ui.playClip(this.data.outro_audio, () => this._finish());
  }

  _finish() { this.state = 'finished'; this.ui.stopClip(); this._notify(); this.ui.onFinish(); }

  // ------------------------------------------------------------------ per frame
  update(dt) {
    if (this._fade) {
      const f = this._fade; f.t += dt;
      const k = Math.min(1, f.t / f.dur);
      this.fadeMat.opacity = f.from + (f.to - f.from) * k;
      this.fade.visible = this.fadeMat.opacity > 0.01;
      if (k >= 1) { this._fade = null; if (f.cb) f.cb(); }
    }
    if (!this.active || this.paused) return;
    if (this.state === 'walking') this._walk(dt);
    else if (this.state === 'arrived' || this.state === 'lingering') {
      this._turnTo(this.stops[this.index].yaw, dt, 1.4);
      if (this.state === 'arrived' && this._read !== null) { this._read -= dt; if (this._read <= 0) this._narrationDone(); }
      if (this.state === 'lingering') {
        this._wait -= dt;
        if (this._wait <= 0) {
          this.ui.closeStop();
          if (this.index >= this.stops.length - 1) this._outro(); else this._beginLeg(this.index + 1);
        }
      }
    }
  }

  _turnTo(yaw, dt, rate) {
    if (this.comfort || this.userLooking) return;
    this.cam.yaw += angDiff(this.cam.yaw, yaw) * Math.min(1, dt * rate);
  }

  _pointAt(d) {
    const c = this.cum; let k = 1;
    while (k < c.length - 1 && c[k] < d) k++;
    const a = this.pts[k - 1], b = this.pts[k], seg = c[k] - c[k - 1] || 1, t = Math.max(0, Math.min(1, (d - c[k - 1]) / seg));
    return [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t];
  }

  _walk(dt) {
    const base = (this.data.walk_speed_mps || 2.0) * this.speedScale;
    const remaining = this.len - this.dist;
    const ease = Math.max(0.25, Math.min(1, this.dist / 1.5 + 0.25, remaining / 3));
    this.dist = Math.min(this.len, this.dist + base * ease * dt);
    const [x, wy, z] = this._pointAt(this.dist);
    const gy = this.move.groundAt(x, z, this.move.pos.y + 1.4);
    const pos = this.move.pos;
    pos.x = x; pos.z = z;
    pos.y += ((gy ?? wy) - pos.y) * Math.min(1, dt * 10);
    const ahead = this._pointAt(Math.min(this.len, this.dist + 3));
    if (Math.hypot(ahead[0] - x, ahead[2] - z) > 0.3) this._turnTo(Math.atan2(-(ahead[0] - x), -(ahead[2] - z)), dt, 2.2);
    if (this.dist >= this.len - 0.01) this._arrive();
  }
}
