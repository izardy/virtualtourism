// viewer.js: wires the modules together and drives the page UI (loading, hotspot panel, places drawer, night mode, VR).
import * as THREE from 'three';
import { SceneManager } from './SceneManager.js';
import { loadModel } from './ModelLoader.js';
import { CameraController } from './CameraController.js';
import { MovementSystem } from './MovementSystem.js';
import { HotspotManager } from './HotspotManager.js';
import { VRController } from './VRController.js';
import { GuidedTour } from './GuidedTour.js';
import { Ambience } from './Ambience.js';
import { IntroFlight } from './IntroFlight.js';

const $ = (id) => document.getElementById(id);
const D = $('app').dataset;

// phones and tablets get the lighter model (1k textures, cheaper trees) when one exists; ?quality=full or ?quality=lite overrides
function pickModel() {
  const q = new URLSearchParams(location.search).get('quality');
  const phone = window.matchMedia('(pointer: coarse)').matches && Math.min(screen.width, screen.height) <= 900;
  const lite = D.modelLite && (q === 'lite' || (q !== 'full' && phone));
  return lite ? D.modelLite : D.model;
}

function toast(msg, ms = 2600) {
  const t = $('toast'); t.textContent = msg; t.style.opacity = 1;
  clearTimeout(toast._t); toast._t = setTimeout(() => { t.style.opacity = 0; }, ms);
}

function fail(msg) {
  $('load-text').classList.add('hidden');
  const e = $('load-error'); e.textContent = msg; e.classList.remove('hidden');
  $('load-back').classList.remove('hidden');
}

async function main() {
  let sm;
  try { sm = new SceneManager($('stage')); }
  catch (err) { fail('Your browser could not start 3D graphics (WebGL). Try Chrome, Edge, Safari or Firefox.'); return; }

  const dom = sm.renderer.domElement;
  sm.loadEnvironments(D.hdri + 'night.hdr', D.hdri + 'day.hdr');       // sky maps stream in while the model loads
  const cam = new CameraController(sm, dom);

  // fetch hotspot data and the model in parallel
  const apiP = fetch(D.api).then((r) => r.json()).catch(() => ({ hotspots: [] }));
  let world;
  try {
    world = await loadModel(pickModel(), {
      dracoPath: D.draco,
      anisotropy: Math.min(4, sm.renderer.capabilities.getMaxAnisotropy()),
      onProgress: (p) => { $('load-bar').style.width = Math.round(p * 100) + '%'; $('load-text').textContent = 'Loading the 3D model… ' + Math.round(p * 100) + '%'; },
    });
  } catch (err) {
    console.error(err);
    fail('The 3D model could not be loaded. ' + (err.message || ''));
    return;
  }
  const api = await apiP;
  const hotspotData = api.hotspots || [];
  sm.scene.add(world.root);

  // ---------------------------------------------------------------- movement and start position
  const move = new MovementSystem(sm, cam, world);
  const spawn = world.spawn || (hotspotData[0] ? new THREE.Vector3(...hotspotData[0].position) : new THREE.Vector3());
  move.placeAt(spawn.x, spawn.z, spawn.y + 2);
  const entrance = world.hotspotNodes['main-entrance'] || (hotspotData[0] && new THREE.Vector3(...hotspotData[0].position));
  if (entrance) cam.setYaw(Math.atan2(-(entrance.x - spawn.x), -(entrance.z - spawn.z)));
  let intro = null;                                                     // opening flight (IntroFlight), set at the end of main()
  sm.onUpdate((dt) => { if (intro && intro.active) { intro.update(dt); return; } move.update(dt); cam.update(); });

  // hide vegetation chunks the fog already hides (night fog is thick: nothing shows beyond about 150 m)
  const chunkCentre = (world.chunks || []).map((c) => { c.updateMatrixWorld(true); const s = c.boundingSphere.clone().applyMatrix4(c.matrixWorld); return s; });
  let chunkT = 0; const camPos = new THREE.Vector3();
  sm.onUpdate((dt) => {
    chunkT += dt; if (chunkT < 0.3) return; chunkT = 0;
    sm.camera.getWorldPosition(camPos); const reach = intro && intro.active ? 650 : (sm.night ? 170 : 520);
    world.chunks.forEach((c, i) => { const s = chunkCentre[i]; c.visible = camPos.distanceTo(s.center) - s.radius < reach; });
  });

  // ---------------------------------------------------------------- hotspots
  const hs = new HotspotManager(sm);
  hs.setHotspots(hotspotData);
  const progress = $('progress-text');
  const setProgress = (n, total) => { progress.textContent = total ? `Explored ${n} of ${total} stories` : ''; };
  hs.onVisit = setProgress; setProgress(0, hotspotData.length);

  const panel = $('panel'), audioBtn = $('audio-btn');
  let audio = null, clip = null, openIdx = -1, tour = null;
  const titleToIndex = {}; hotspotData.forEach((h, i) => { titleToIndex[h.title] = i; });

  function stopAudio() { if (audio) { audio.pause(); audio = null; } audioBtn.textContent = 'Play narration'; }
  function playAudio(src, onEnd) {
    stopAudio();
    const a = new Audio(src); audio = a;
    a.addEventListener('ended', () => { audioBtn.textContent = 'Play again'; if (audio === a && onEnd) onEnd(); });
    a.play().then(() => { audioBtn.textContent = 'Pause narration'; })
      .catch(() => { audioBtn.textContent = 'Play narration'; if (onEnd) setTimeout(() => { if (audio === a) onEnd(); }, 8000); });
  }
  function stopClip() { if (clip) { clip.pause(); clip = null; } }
  function playClip(src, done) {                       // tour intro / outro
    stopClip();
    const c = new Audio(D.static + src); clip = c;
    const end = () => { if (clip === c) { clip = null; if (done) done(); } };
    c.addEventListener('ended', end);
    c.play().catch(() => setTimeout(end, 4000));
  }
  function pauseAudio() { [audio, clip].forEach((a) => a && a.pause()); }
  function resumeAudio() { [audio, clip].forEach((a) => a && !a.ended && a.play().catch(() => {})); }

  function closePanel(programmatic = false) {
    panel.classList.remove('open'); panel.setAttribute('aria-hidden', 'true'); stopAudio(); openIdx = -1;
    $('vr-caption').querySelectorAll('span').forEach((s) => { s.textContent = ''; });
    if (!programmatic && tour && tour.active && tour.state === 'arrived') tour.skipNarration();   // closing the panel skips the narration
  }
  function openHotspot(i, onDone) {
    const h = hotspotData[i]; if (!h) return null;
    openIdx = i; hs.markVisited(i);
    $('panel-kicker').textContent = `Hotspot ${i + 1} of ${hotspotData.length}`;
    $('panel-title').textContent = h.title;
    $('panel-body').textContent = h.description || '';
    const img = $('panel-img');
    if (h.image) { img.src = D.static + h.image; img.alt = h.title; img.classList.remove('hidden'); } else { img.classList.add('hidden'); img.removeAttribute('src'); }
    const ul = $('panel-facts'); ul.textContent = '';
    (h.facts || []).forEach((f) => { const li = document.createElement('li'); li.textContent = f; ul.appendChild(li); });
    $('panel-facts-h').classList.toggle('hidden', !(h.facts && h.facts.length));
    $('panel-audio').classList.toggle('hidden', !h.audio);
    audioBtn.onclick = () => { if (audio && !audio.paused) { audio.pause(); audioBtn.textContent = 'Resume narration'; } else if (audio && !audio.ended) { audio.play(); audioBtn.textContent = 'Pause narration'; } else playAudio(D.static + h.audio); };
    panel.classList.add('open'); panel.setAttribute('aria-hidden', 'false');
    if (h.audio) playAudio(D.static + h.audio, onDone); else stopAudio();
    $('vr-caption').querySelectorAll('span').forEach((s, k) => { s.textContent = h.title; s.style.left = k ? '50%' : '0'; });
    const words = ((h.description || '') + ' ' + (h.facts || []).join(' ')).split(/\s+/).length;
    return { audio: !!h.audio, seconds: Math.max(6, words / 3) };
  }
  $('panel-close').addEventListener('click', () => closePanel(false));
  window.addEventListener('keydown', (e) => { if (e.key === 'Escape') { closePanel(false); closeDrawer(); if (vr.mode !== 'off') vr.exit(); } });

  // ---------------------------------------------------------------- picking and teleporting
  const ray = new THREE.Raycaster();
  function floorHit(clientX, clientY) {
    const r = dom.getBoundingClientRect();
    ray.setFromCamera(new THREE.Vector2(((clientX - r.left) / r.width) * 2 - 1, -((clientY - r.top) / r.height) * 2 + 1), sm.camera);
    ray.far = 80;
    return ray.intersectObjects(world.walkables, false)[0] || null;
  }
  const reticleMesh = new THREE.Mesh(new THREE.RingGeometry(0.32, 0.46, 32).rotateX(-Math.PI / 2),
    new THREE.MeshBasicMaterial({ color: 0x00d4ff, transparent: true, opacity: 0.85, depthWrite: false, fog: false }));
  reticleMesh.visible = false; sm.scene.add(reticleMesh);
  const flash = $('flash');
  move.onTeleport = () => { flash.style.opacity = 1; setTimeout(() => { flash.style.opacity = 0; }, 160); };

  function teleportAt(x, y) {
    const hit = floorHit(x, y);
    if (!hit) { toast('Nothing to stand on there'); return; }
    if (hit.point.distanceTo(move.pos) > 70) { toast('Too far to teleport'); return; }
    move.teleportTo(hit.point);
  }
  let lastHover = 0;
  cam.onHover = (x, y) => {
    if (tour && tour.active) { reticleMesh.visible = false; return; }
    const now = performance.now(); if (now - lastHover < 60) return; lastHover = now;
    const i = hs.pickScreen(x, y, dom); dom.style.cursor = i >= 0 ? 'pointer' : 'grab';
    const hit = i < 0 ? floorHit(x, y) : null;
    reticleMesh.visible = !!hit && hit.point.distanceTo(move.pos) < 70;
    if (hit) reticleMesh.position.copy(hit.point).y += 0.05;
  };
  cam.onTap = (x, y) => {
    if (tour && tour.active) { if (vr.mode === 'stereo') tour.togglePause(); return; }          // guided: tap pauses in Cardboard, otherwise nothing
    if (vr.mode === 'stereo') { move.autoWalk = !move.autoWalk; toast(move.autoWalk ? 'Walking' : 'Stopped', 1200); return; }
    const i = hs.pickScreen(x, y, dom);
    if (i >= 0) openHotspot(i);
  };
  cam.onDoubleTap = (x, y) => { if (vr.mode === 'off' && !(tour && tour.active)) teleportAt(x, y); };

  // ---------------------------------------------------------------- places drawer
  const drawer = $('drawer'), btnPlaces = $('btn-places');
  function closeDrawer() { drawer.classList.remove('open'); btnPlaces.setAttribute('aria-expanded', 'false'); }
  btnPlaces.addEventListener('click', () => { const o = drawer.classList.toggle('open'); btnPlaces.setAttribute('aria-expanded', o); });
  function goTo(position, lookAt) {
    const to = new THREE.Vector3(position.x, position.y, position.z);
    if (lookAt) {                                           // stand 2.8 m away from a hotspot, facing it
      const back = move.pos.clone().sub(to).setY(0); if (back.lengthSq() < 0.01) back.set(0, 0, 1);
      back.normalize().multiplyScalar(2.8); to.x += back.x; to.z += back.z; to.y -= 1.5;
      const yaw = Math.atan2(-(position.x - to.x), -(position.z - to.z));
      move.teleportTo(to, { yaw });
    } else move.teleportTo(to);
    closeDrawer();
  }
  const lh = $('list-hotspots');
  hotspotData.forEach((h, i) => {
    const li = document.createElement('li'), b = document.createElement('button');
    b.type = 'button'; b.className = 'flex w-full items-center gap-3 rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-left hover:bg-white/10';
    b.innerHTML = '<span class="grid h-6 w-6 flex-none place-items-center rounded-full bg-cyan/20 text-xs text-cyan"></span><span></span>';
    b.children[0].textContent = i + 1; b.children[1].textContent = h.title;
    b.addEventListener('click', () => {
      if (tour && tour.active) { const k = tour.stops.findIndex((st) => st.title === h.title); if (k >= 0) { tour.goTo(k); closeDrawer(); return; } }
      goTo({ x: h.position[0], y: h.position[1], z: h.position[2] }, true); setTimeout(() => openHotspot(i), 450);
    });
    li.appendChild(b); lh.appendChild(li);
  });
  if (api.points_url) {
    fetch(api.points_url).then((r) => r.json()).then((pts) => {
      const ul = $('list-points');
      Object.entries(pts).sort((a, b) => a[0].localeCompare(b[0], undefined, { numeric: true })).forEach(([key, v]) => {
        if (!v.label || key.startsWith('loc_memorial') && false) return;
        const li = document.createElement('li'), b = document.createElement('button');
        b.type = 'button'; b.className = 'w-full rounded-lg px-3 py-2 text-left text-white/80 hover:bg-white/10';
        const m = key.match(/^loc_(\d+)_/); b.textContent = (m ? Number(m[1]) + '. ' : '') + v.label;
        b.addEventListener('click', () => goTo({ x: v.gltf_xyz[0], y: v.gltf_xyz[1], z: v.gltf_xyz[2] }, false));
        li.appendChild(b); ul.appendChild(li);
      });
    }).catch(() => {});
  }

  // ---------------------------------------------------------------- nature ambience (insects, waves, wind)
  const amb = new Ambience(D.static); amb.coastX = spawn.x + 260;       // the shore lies about 260 m east of the ticket building
  const btnSound = $('btn-sound');
  const paintSound = () => { btnSound.textContent = amb.muted ? 'Sound off' : 'Sound on'; btnSound.setAttribute('aria-pressed', !amb.muted); };
  paintSound();
  btnSound.addEventListener('click', () => { amb.start(); amb.setMuted(!amb.muted); paintSound(); });
  const wake = () => { amb.start(); };                                  // browsers need a gesture before audio can start
  ['pointerdown', 'keydown', 'touchstart'].forEach((ev) => window.addEventListener(ev, wake, { once: true, passive: true }));
  let ambT = 0;
  sm.onUpdate((dt) => {
    ambT += dt; if (ambT < 0.25) return; ambT = 0;
    amb.setDuck(((audio && !audio.paused) || (clip && !clip.paused)) ? 0.45 : 1);
    amb.update(sm.camera.getWorldPosition(new THREE.Vector3()).x);
  });

  // ---------------------------------------------------------------- night / day, help, fullscreen
  const btnNight = $('btn-night');
  btnNight.addEventListener('click', () => { sm.setNight(!sm.night); amb.setNight(sm.night); btnNight.textContent = sm.night ? 'Night' : 'Day'; btnNight.setAttribute('aria-pressed', sm.night); $('night-vignette').style.opacity = sm.night ? 1 : 0; });
  const help = $('help');
  const showHelp = () => { help.classList.remove('hidden'); help.classList.add('grid'); };
  const hideHelp = () => { help.classList.add('hidden'); help.classList.remove('grid'); try { localStorage.setItem('vt_help_seen', '1'); } catch (_) { /* private mode */ } };
  $('btn-help').addEventListener('click', showHelp); $('help-close').addEventListener('click', hideHelp);

  // ---------------------------------------------------------------- touch joystick
  let joyEl = null;
  if (window.matchMedia('(pointer: coarse)').matches) {
    const joy = $('joystick'), knob = $('joy-knob'); joy.classList.remove('hidden'); joyEl = joy;
    let id = null;
    const set = (e) => {
      const r = joy.getBoundingClientRect(), cx = r.left + r.width / 2, cy = r.top + r.height / 2, max = r.width / 2 - 8;
      let dx = e.clientX - cx, dy = e.clientY - cy; const d = Math.hypot(dx, dy);
      if (d > max) { dx = dx / d * max; dy = dy / d * max; }
      knob.style.transform = `translate(calc(-50% + ${dx}px), calc(-50% + ${dy}px))`;
      move.joy.x = dx / max; move.joy.y = -dy / max;
    };
    const reset = () => { id = null; move.joy.x = move.joy.y = 0; knob.style.transform = 'translate(-50%, -50%)'; };
    joy.addEventListener('pointerdown', (e) => { id = e.pointerId; joy.setPointerCapture(id); set(e); e.preventDefault(); });
    joy.addEventListener('pointermove', (e) => { if (e.pointerId === id) set(e); });
    joy.addEventListener('pointerup', (e) => { if (e.pointerId === id) reset(); });
    joy.addEventListener('pointercancel', reset);
  }

  // ---------------------------------------------------------------- VR
  const vr = new VRController(sm, cam, move);
  const btnVr = $('btn-vr'), btnExit = $('btn-vr-exit'), reticle = $('reticle');
  vr.onSelect = (origin, dir) => {                                       // WebXR controller trigger
    if (tour && tour.active) { tour.togglePause(); return; }
    const i = hs.pickRay(origin, dir); if (i >= 0) { openHotspot(i); return; }
    ray.set(origin, dir); ray.far = 60;
    const hit = ray.intersectObjects(world.walkables, false)[0];
    if (hit) move.teleportTo(hit.point);
  };
  vr.onModeChange = (mode) => {
    const on = mode !== 'off';
    btnExit.classList.toggle('hidden', !on); btnExit.classList.toggle('no-stereo', false);
    reticle.classList.toggle('hidden', mode !== 'stereo');
    $('hud').classList.toggle('no-stereo', true);
    if (mode === 'stereo') { closePanel(); closeDrawer(); hideHelp(); toast('Slide your phone into the headset. Tap the screen to walk or stop.', 5000); }
    if (mode === 'off') { move.autoWalk = false; reticle.classList.add('hidden'); }
  };
  document.querySelectorAll('#hud, #panel, #drawer, #help').forEach((el) => el.classList.add('no-stereo-hide'));
  btnVr.addEventListener('click', async () => {
    try { await vr.enter(); } catch (err) { console.warn(err); toast(err.message || 'Could not start VR on this device', 4000); }
  });
  btnExit.addEventListener('click', () => vr.exit());
  vr.init().then((ok) => { if (!ok) btnVr.title = 'Split-screen Cardboard mode (WebXR headset not detected)'; });

  // Cardboard gaze: look at a hotspot for 1.4 s to open it
  let gazeIdx = -1, gazeT = 0;
  sm.onUpdate((dt) => {
    if (vr.mode !== 'stereo' || (tour && tour.active)) return;
    const i = hs.pickCenter();
    if (i === gazeIdx && i >= 0) { gazeT += dt; reticle.style.transform = `translate(-50%, -50%) scale(${1 + gazeT * 2})`; if (gazeT > 1.4) { openHotspot(i); gazeT = -4; } }
    else { gazeIdx = i; gazeT = 0; reticle.style.transform = 'translate(-50%, -50%)'; }
  });

  // proximity hint
  let nearIdx = -1;
  setInterval(() => {
    if ((tour && tour.active) || (intro && intro.active)) return;
    const i = hs.nearest(move.pos.clone().setY(move.pos.y + 1.6), 4.5);
    if (i !== nearIdx && i >= 0 && !hs.visited.has(i) && openIdx < 0) toast(`Tap the glowing marker: ${hotspotData[i].title}`, 2600);
    nearIdx = i;
  }, 700);

  // ---------------------------------------------------------------- guided tour
  let tourData = null;
  if (api.tour_url) tourData = await fetch(api.tour_url).then((r) => r.json()).catch(() => null);
  const btnMode = $('btn-mode'), bar = $('tour-bar'), endCard = $('tour-end'), picker = $('mode-picker');
  const lastDone = { n: 0 };
  tour = new GuidedTour(sm, cam, move, {
    playClip, stopClip, pauseAudio, resumeAudio,
    openStop: (idx, done) => {
      const hi = titleToIndex[tour.stops[idx].title];
      return hi >= 0 ? openHotspot(hi, done) : { audio: false, seconds: 5 };
    },
    closeStop: () => closePanel(true),
    onChange: (info) => {
      const stops = tour.stops, s = stops[info.index];
      let label = 'Welcome';
      if (info.paused) label = 'Paused';
      else if (info.state === 'intro') label = 'Welcome to the Night Walk';
      else if (info.state === 'walking') label = `Walking to: ${s ? s.title : ''}`;
      else if (info.state === 'outro') label = 'Goodnight';
      else if (s) label = `Stop ${info.index + 1} of ${stops.length}: ${s.title}`;
      $('tour-label').textContent = label;
      $('tour-pause').textContent = info.paused ? 'Resume' : 'Pause';
      const frac = info.state === 'outro' || info.state === 'finished' ? 1 : (Math.max(0, info.index) + (info.state === 'walking' || info.state === 'blink' ? 0.35 : 0.8)) / stops.length;
      $('tour-progress').style.width = Math.round(Math.min(1, frac) * 100) + '%';
    },
    onActive: (on) => {
      bar.classList.toggle('hidden', !on); bar.classList.toggle('flex', on);
      if (joyEl) joyEl.classList.toggle('hidden', on);
      $('list-points').classList.toggle('hidden', on);
      btnMode.textContent = on ? 'Free walk' : 'Guided tour';
      // keep the tour controls reachable: lift the story panel above the bar while a tour is running
      panel.style.bottom = on ? '4.75rem' : ''; panel.style.maxHeight = on ? 'calc(100svh - 10.5rem)' : ''; panel.style.borderRadius = on ? '1rem' : '';
      if (on) { closeDrawer(); closePanel(true); endCard.classList.add('hidden'); endCard.classList.remove('grid'); const hint = $('tour-hint'); hint.classList.remove('hidden'); setTimeout(() => hint.classList.add('hidden'), 7000); }
      else $('tour-hint').classList.add('hidden');
    },
    onFinish: () => { endCard.classList.remove('hidden'); endCard.classList.add('grid'); },
  });
  tour.vr = vr;
  sm.onUpdate((dt) => tour.update(dt));
  if (tourData && tourData.stops) { tour.load(tourData); btnMode.classList.remove('hidden'); }

  $('tour-prev').addEventListener('click', () => tour.prev());
  $('tour-next').addEventListener('click', () => tour.next());
  $('tour-pause').addEventListener('click', () => tour.togglePause());
  $('tour-exit').addEventListener('click', () => { tour.exit(); toast('You are free to explore'); });
  btnMode.addEventListener('click', () => { if (tour.active) { tour.exit(); toast('You are free to explore'); } else tour.start(tour.index > 0 ? tour.index : 0); });
  $('end-free').addEventListener('click', () => { endCard.classList.add('hidden'); endCard.classList.remove('grid'); tour.exit(); });
  $('end-again').addEventListener('click', () => { endCard.classList.add('hidden'); endCard.classList.remove('grid'); tour.start(0); });

  // ---------------------------------------------------------------- go
  $('loading').style.transition = 'opacity .6s'; $('loading').style.opacity = 0;
  setTimeout(() => $('loading').classList.add('hidden'), 650);
  let seen = false; try { seen = localStorage.getItem('vt_help_seen') === '1'; } catch (_) { /* ignore */ }
  const startFree = () => { picker.classList.add('hidden'); picker.classList.remove('grid'); if (!seen && !(D.mode === 'free')) showHelp(); else if (D.autoVr === '1') toast('Press "Enter VR Experience" to start VR', 6000); };
  const startGuided = () => { picker.classList.add('hidden'); picker.classList.remove('grid'); hideHelp(); tour.start(0); };
  if (D.autoVr === '1') { btnVr.classList.add('animate-pulse'); $('pick-vr-badge').classList.remove('hidden'); }
  const showStart = () => {
    if (!tourData || !tourData.stops) { startFree(); }                                  // no guided tour for this destination
    else if (D.mode === 'free') { startFree(); }                                        // came from "Explore on your own"
    else {                                                                              // a click is needed anyway so narration audio may autoplay
      picker.classList.remove('hidden'); picker.classList.add('grid');
      if (D.mode === 'guided') { $('pick-guided').classList.add('ring-2', 'ring-cyan'); $('pick-guided').focus(); }
      $('pick-guided').addEventListener('click', startGuided);
      $('pick-free').addEventListener('click', startFree);
    }
  };

  // opening flight: from high above the fort down to the entrance, then the mode picker. Skipped for ?intro=0,
  // reduced-motion users and automated browsers (the test scripts drive the camera themselves).
  const qs = new URLSearchParams(location.search);
  const noIntro = qs.get('intro') === '0' || (qs.get('intro') !== '1' && (navigator.webdriver || window.matchMedia('(prefers-reduced-motion: reduce)').matches));
  const nodes = Object.values(world.hotspotNodes || {});
  if (noIntro || !nodes.length) { showStart(); }
  else {
    const centre = nodes.reduce((a, v) => a.add(v), new THREE.Vector3()).multiplyScalar(1 / nodes.length);
    centre.y = nodes.reduce((m, v) => Math.min(m, v.y), Infinity);
    const card = $('intro'), hud = $('hud');
    const endIntro = () => {
      card.style.opacity = 0; setTimeout(() => { card.classList.add('hidden'); card.classList.remove('flex'); }, 1000);
      hud.style.transition = 'opacity .8s'; hud.style.opacity = 1;
      window.removeEventListener('keydown', skipKey); dom.removeEventListener('pointerdown', skip);
      showStart();
    };
    intro = new IntroFlight(sm, cam, move, { centre, duration: 11, onEnd: endIntro });
    const skip = () => intro.finish();
    const skipKey = (e) => { if (e.key !== 'Tab') skip(); };
    $('intro-skip').addEventListener('click', skip);
    window.addEventListener('keydown', skipKey); dom.addEventListener('pointerdown', skip);
    hud.style.opacity = 0;
    card.classList.remove('hidden'); card.classList.add('flex'); requestAnimationFrame(() => { card.style.opacity = 1; });
    intro.start();
  }

  // adaptive quality: drop resolution on slow phones
  setTimeout(() => {
    if (sm.averageFps() < 28) { sm.setQuality(1, false); toast('Performance mode on', 2500); }
  }, 7000);
  window.__vt = { amb, sm, move, hs, cam, vr, world, openHotspot, tour, intro };   // handy for debugging in the console
}

main();
