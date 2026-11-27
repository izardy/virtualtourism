// Nature ambience with Web Audio, started after a user gesture.
// Night: two cricket layers that each stop and start at random, an occasional gecko (cicak) and owl.
// Day: crickets fall silent; birds call at random from random directions.
// Always: wind, and waves that get louder toward the east shore. Everything ducks under narration.
const LOOPS = { crickets_a: 'crickets_a', crickets_b: 'crickets_b', waves: 'waves', wind: 'wind' };
const SHOTS = { bird_1: 'bird_1', bird_2: 'bird_2', bird_3: 'bird_3', bird_4: 'bird_4', gecko: 'gecko', owl: 'owl' };
const rnd = (a, b) => a + Math.random() * (b - a);

export class Ambience {
  constructor(staticBase) {
    this.base = staticBase + 'audio/ambient/'; this.ctx = null; this.gains = {}; this.buffers = {}; this.master = null;
    this.muted = false; this.night = true; this.duck = 1; this.coastX = null; this.started = false; this.x = 0;
    this.gate = { crickets_a: 1, crickets_b: 1 };              // 1 = singing, 0 = paused
    this._timers = [];
    try { this.muted = localStorage.getItem('vt_ambience_muted') === '1'; } catch (_) { /* private mode */ }
  }

  async start() {
    if (this.started) { this.resume(); return; }
    const AC = window.AudioContext || window.webkitAudioContext; if (!AC) return;
    this.started = true; this.ctx = new AC();
    this.master = this.ctx.createGain(); this.master.gain.value = this.muted ? 0 : 1; this.master.connect(this.ctx.destination);
    const load = async (name) => {
      try { return await this.ctx.decodeAudioData(await (await fetch(this.base + name + '.mp3')).arrayBuffer()); }
      catch (_) { return null; }                               // a missing file is not fatal
    };
    await Promise.all(Object.entries(LOOPS).map(async ([k, f]) => {
      const buf = await load(f); if (!buf) return;
      const src = this.ctx.createBufferSource(); src.buffer = buf; src.loop = true;
      const g = this.ctx.createGain(); g.gain.value = 0;
      let node = g;
      if (k.startsWith('crickets') && this.ctx.createStereoPanner) {   // the two insects sit left and right of the listener
        const p = this.ctx.createStereoPanner(); p.pan.value = k.endsWith('a') ? -0.45 : 0.5; g.connect(p); node = p;
      }
      src.connect(g); node.connect(this.master);
      src.start(0, Math.random() * buf.duration);              // random start so the layers never line up
      this.gains[k] = g;
    }));
    await Promise.all(Object.entries(SHOTS).map(async ([k, f]) => { this.buffers[k] = await load(f); }));
    this._gateLoop('crickets_a'); this._gateLoop('crickets_b');
    this._every(() => this.night ? null : ['bird_1', 'bird_2', 'bird_3', 'bird_4'][Math.floor(Math.random() * 4)], 1.5, 6, [0.2, 0.55]);
    this._every(() => (Math.random() < 0.5 ? 'bird_1' : 'bird_3'), 9, 20, [0.08, 0.2], () => !this.night);   // distant birds answer
    this._every(() => this.night ? 'gecko' : null, 14, 40, [0.25, 0.5]);
    this._every(() => this.night ? 'owl' : null, 35, 90, [0.15, 0.3]);
    this.update(this.x);
  }

  resume() { if (this.ctx && this.ctx.state === 'suspended') this.ctx.resume(); }
  setNight(n) { this.night = n; this.update(this.x); }
  setMuted(m) {
    this.muted = m; try { localStorage.setItem('vt_ambience_muted', m ? '1' : '0'); } catch (_) { /* ignore */ }
    if (this.master) this.master.gain.setTargetAtTime(m ? 0 : 1, this.ctx.currentTime, 0.2);
  }
  setDuck(d) { this.duck = d; }                                // < 1 while narration plays

  // Each cricket sings for 4-18 s, then pauses for 1.5-9 s (sometimes both stop at once: a nearby step scared them).
  _gateLoop(k) {
    const flip = () => {
      this.gate[k] = this.gate[k] ? 0 : 1;
      const wait = this.gate[k] ? rnd(4, 18) : rnd(1.5, 9);
      this.update(this.x);
      this._timers.push(setTimeout(flip, wait * 1000));
    };
    this._timers.push(setTimeout(flip, rnd(3, 12) * 1000));
  }

  // Play a one-shot every min..max seconds when pick() returns a name; random direction, level and pitch.
  _every(pick, min, max, vol, extra = () => true) {
    const tick = () => {
      const name = extra() ? pick() : null;
      if (name && !this.muted && this.buffers[name] && this.ctx.state === 'running') this._play(name, rnd(vol[0], vol[1]));
      this._timers.push(setTimeout(tick, rnd(min, max) * 1000));
    };
    this._timers.push(setTimeout(tick, rnd(min, max) * 1000));
  }
  _play(name, v) {
    const src = this.ctx.createBufferSource(); src.buffer = this.buffers[name];
    src.playbackRate.value = rnd(0.9, 1.12);
    const g = this.ctx.createGain(); g.gain.value = v * this.duck;
    src.connect(g);
    if (this.ctx.createStereoPanner) { const p = this.ctx.createStereoPanner(); p.pan.value = rnd(-0.9, 0.9); g.connect(p); p.connect(this.master); }
    else g.connect(this.master);
    src.start();
  }

  // x: camera x in glTF metres. Waves swell within about 220 m of the shore.
  update(x) {
    this.x = x;
    if (!this.ctx) return;
    const near = this.coastX == null ? 0.3 : Math.min(1, Math.max(0, 1 - (this.coastX - x) / 220));
    const t = this.ctx.currentTime, d = this.duck, n = this.night;
    const target = {
      crickets_a: n ? 0.5 * this.gate.crickets_a * d : 0,
      crickets_b: n ? 0.4 * this.gate.crickets_b * d : 0,
      waves: (0.08 + 0.55 * near) * d,
      wind: (n ? 0.12 : 0.16) * d,
    };
    for (const k in this.gains) this.gains[k].gain.setTargetAtTime(target[k], t, k.startsWith('crickets') ? 0.7 : 0.8);
  }
}
