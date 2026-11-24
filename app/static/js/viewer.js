// viewer.js: wires the modules together and drives the page UI (loading, hotspot panel, places drawer, night mode, VR).
import * as THREE from 'three';
import { SceneManager } from './SceneManager.js';
import { loadModel } from './ModelLoader.js';
import { CameraController } from './CameraController.js';
import { MovementSystem } from './MovementSystem.js';
import { HotspotManager } from './HotspotManager.js';
import { VRController } from './VRController.js';

const $ = (id) => document.getElementById(id);
const D = $('app').dataset;

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
  const cam = new CameraController(sm, dom);

  // fetch hotspot data and the model in parallel
  const apiP = fetch(D.api).then((r) => r.json()).catch(() => ({ hotspots: [] }));
  let world;
  try {
    world = await loadModel(D.model, {
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
  sm.onUpdate((dt) => { move.update(dt); cam.update(); });

  // ---------------------------------------------------------------- hotspots
  const hs = new HotspotManager(sm);
  hs.setHotspots(hotspotData);
  const progress = $('progress-text');
  const setProgress = (n, total) => { progress.textContent = total ? `Explored ${n} of ${total} stories` : ''; };
  hs.onVisit = setProgress; setProgress(0, hotspotData.length);

  const panel = $('panel'), audioBtn = $('audio-btn');
  let audio = null, openIdx = -1;
  function stopAudio() { if (audio) { audio.pause(); audio = null; } audioBtn.textContent = 'Play narration'; }
  function playAudio(src) {
    stopAudio();
    audio = new Audio(src);
    audio.addEventListener('ended', () => { audioBtn.textContent = 'Play again'; });
    audio.play().then(() => { audioBtn.textContent = 'Pause narration'; }).catch(() => { audioBtn.textContent = 'Play narration'; });
  }
  function closePanel() {
    panel.classList.remove('open'); panel.setAttribute('aria-hidden', 'true'); stopAudio(); openIdx = -1;
    $('vr-caption').querySelectorAll('span').forEach((s) => { s.textContent = ''; });
  }
  function openHotspot(i) {
    const h = hotspotData[i]; if (!h) return;
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
    audioBtn.onclick = () => { if (audio && !audio.paused) { audio.pause(); audioBtn.textContent = 'Resume narration'; } else if (audio) { audio.play(); audioBtn.textContent = 'Pause narration'; } else playAudio(D.static + h.audio); };
    panel.classList.add('open'); panel.setAttribute('aria-hidden', 'false');
    if (h.audio) playAudio(D.static + h.audio);
    $('vr-caption').querySelectorAll('span').forEach((s, k) => { s.textContent = h.title; s.style.left = k ? '50%' : '0'; });
  }
  $('panel-close').addEventListener('click', closePanel);
  window.addEventListener('keydown', (e) => { if (e.key === 'Escape') { closePanel(); closeDrawer(); if (vr.mode !== 'off') vr.exit(); } });

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
    const now = performance.now(); if (now - lastHover < 60) return; lastHover = now;
    const i = hs.pickScreen(x, y, dom); dom.style.cursor = i >= 0 ? 'pointer' : 'grab';
    const hit = i < 0 ? floorHit(x, y) : null;
    reticleMesh.visible = !!hit && hit.point.distanceTo(move.pos) < 70;
    if (hit) reticleMesh.position.copy(hit.point).y += 0.05;
  };
  cam.onTap = (x, y) => {
    if (vr.mode === 'stereo') { move.autoWalk = !move.autoWalk; toast(move.autoWalk ? 'Walking' : 'Stopped', 1200); return; }
    const i = hs.pickScreen(x, y, dom);
    if (i >= 0) openHotspot(i);
  };
  cam.onDoubleTap = (x, y) => { if (vr.mode === 'off') teleportAt(x, y); };

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
    b.addEventListener('click', () => { goTo({ x: h.position[0], y: h.position[1], z: h.position[2] }, true); setTimeout(() => openHotspot(i), 450); });
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

  // ---------------------------------------------------------------- night / day, help, fullscreen
  const btnNight = $('btn-night');
  btnNight.addEventListener('click', () => { sm.setNight(!sm.night); btnNight.textContent = sm.night ? 'Night' : 'Day'; btnNight.setAttribute('aria-pressed', sm.night); $('night-vignette').style.opacity = sm.night ? 1 : 0; });
  const help = $('help');
  const showHelp = () => { help.classList.remove('hidden'); help.classList.add('grid'); };
  const hideHelp = () => { help.classList.add('hidden'); help.classList.remove('grid'); try { localStorage.setItem('vt_help_seen', '1'); } catch (_) { /* private mode */ } };
  $('btn-help').addEventListener('click', showHelp); $('help-close').addEventListener('click', hideHelp);

  // ---------------------------------------------------------------- touch joystick
  if (window.matchMedia('(pointer: coarse)').matches) {
    const joy = $('joystick'), knob = $('joy-knob'); joy.classList.remove('hidden');
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
    if (vr.mode !== 'stereo') return;
    const i = hs.pickCenter();
    if (i === gazeIdx && i >= 0) { gazeT += dt; reticle.style.transform = `translate(-50%, -50%) scale(${1 + gazeT * 2})`; if (gazeT > 1.4) { openHotspot(i); gazeT = -4; } }
    else { gazeIdx = i; gazeT = 0; reticle.style.transform = 'translate(-50%, -50%)'; }
  });

  // proximity hint
  let nearIdx = -1;
  setInterval(() => {
    const i = hs.nearest(move.pos.clone().setY(move.pos.y + 1.6), 4.5);
    if (i !== nearIdx && i >= 0 && !hs.visited.has(i) && openIdx < 0) toast(`Tap the glowing marker: ${hotspotData[i].title}`, 2600);
    nearIdx = i;
  }, 700);

  // ---------------------------------------------------------------- go
  $('loading').style.transition = 'opacity .6s'; $('loading').style.opacity = 0;
  setTimeout(() => $('loading').classList.add('hidden'), 650);
  let seen = false; try { seen = localStorage.getItem('vt_help_seen') === '1'; } catch (_) { /* ignore */ }
  if (!seen) showHelp();
  if (D.autoVr === '1') { btnVr.classList.add('animate-pulse'); toast('Press "Enter VR Experience" to start VR', 6000); }

  // adaptive quality: drop resolution on slow phones
  setTimeout(() => {
    if (sm.averageFps() < 28) { sm.setQuality(1, false); toast('Performance mode on', 2500); }
  }, 7000);
  window.__vt = { sm, move, hs, cam, vr, world, openHotspot };   // handy for debugging in the console
}

main();
