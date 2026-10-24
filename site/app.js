// Crystal Balls — app.js (Bible Part 6)
// ES module. Builds the three nested globes scene, the panel, the modal,
// the list view, and wires up the header controls.

import * as THREE from 'three';
import { OrbitControls } from './assets/vendor/OrbitControls.js';

// ---------------------------------------------------------------------
// State
// ---------------------------------------------------------------------

let scene, camera, renderer, controls, globeGroup, starField;
let countriesMeta = [], countriesByCode = {}, vocabulary = [], vocabByEmoji = {}, groups = {};
let indexData = null, scorecardData = null;
let currentRoundId = null, previousRoundId = null, nextRoundId = null;
let bundleR = null, bundleP = null, bundleNext = null; // bundleNext used for outcomes on R's statements
let sprites = []; // { sprite, code, layer, anchor: Vector3 } — anchor is meaningful only for OUTER (Bible 6.16)
let spritesByCountry = {}; // code -> { 0: entry, 1: entry, 2: entry }
let connectorLine = null;
let hoveredCode = null, selectedCode = null;
let pointerDownPos = null, pointerMoved = false;
let lastInteractionTime = Date.now();
let autoRotateResumeTimer = null;
let webglOK = true;
let outlineLineSegments = []; // for disposal tracking (static, built once)
let imageCache = {}; // twemoji code -> HTMLImageElement

const AUTO_ROTATE_RESUME_MS = 25000;
const EMOJI_DIR = './assets/emoji/';

const LAYER = { INNER: 0, MIDDLE: 1, OUTER: 2 };
const RADIUS = { 2: 1.00, 1: 0.74, 0: 0.50 };
// One clipping plane per globe layer: only the half of each globe that faces the viewer is drawn,
// so the far side (the "dark side of the moon") never shows through. Updated every frame.
const layerClipPlanes = { 2: new THREE.Plane(), 1: new THREE.Plane(), 0: new THREE.Plane() };
const SPRITE_SIZE = { 2: [0.26, 0.235], 1: [0.21, 0.19], 0: [0.17, 0.154] };
const SPRITE_COLOR = { 2: 0xffffff, 1: 0xaaaaaa, 0: 0x585858 };
const HOVER_COLOR = 0xffffff;
const SPRITE_CENTER = 0.5; // Bible 6.16: all cards centered; middle/inner repositioned in screen space each frame.
const RENDER_ORDER = { 0: 10, 1: 20, 2: 30 };

// ---------------------------------------------------------------------
// Small utilities
// ---------------------------------------------------------------------

function clamp(v, lo, hi) { return Math.max(lo, Math.min(hi, v)); }

function latLngToVector3(lat, lng, r) {
  const phi = (90 - lat) * Math.PI / 180;
  const theta = (lng + 180) * Math.PI / 180;
  return new THREE.Vector3(
    -r * Math.sin(phi) * Math.cos(theta),
     r * Math.cos(phi),
     r * Math.sin(phi) * Math.sin(theta)
  );
}

async function fetchJSON(path) {
  const resp = await fetch(path);
  if (!resp.ok) throw new Error(`Failed to fetch ${path}: ${resp.status}`);
  return resp.json();
}

function hasWebGL() {
  try {
    const canvas = document.createElement('canvas');
    return !!(window.WebGLRenderingContext &&
      (canvas.getContext('webgl') || canvas.getContext('experimental-webgl')));
  } catch (e) {
    return false;
  }
}

function emojiSrc(twemoji) { return `${EMOJI_DIR}${twemoji}.png`; }

function loadImage(twemoji) {
  if (imageCache[twemoji]) return imageCache[twemoji];
  const img = new Image();
  img.src = emojiSrc(twemoji);
  imageCache[twemoji] = img;
  return img;
}

function imgReady(img) {
  return new Promise((resolve) => {
    if (img.complete && img.naturalWidth > 0) { resolve(img); return; }
    img.addEventListener('load', () => resolve(img), { once: true });
    img.addEventListener('error', () => resolve(img), { once: true });
  });
}

function firstSentence(text) {
  if (!text) return '';
  const m = text.match(/^[^.!?]*[.!?]/);
  return m ? m[0].trim() : text.trim();
}

function parseHash() {
  const h = window.location.hash.replace(/^#/, '');
  const params = new URLSearchParams(h);
  return { round: params.get('round'), country: params.get('country') };
}

function updateHash(round, country) {
  const params = new URLSearchParams();
  if (round) params.set('round', round);
  if (country) params.set('country', country);
  const newHash = '#' + params.toString();
  if (window.location.hash !== newHash) {
    history.replaceState(null, '', newHash);
  }
}

// ---------------------------------------------------------------------
// Boot
// ---------------------------------------------------------------------

init();

async function init() {
  webglOK = hasWebGL();

  try {
    indexData = await fetchJSON('./data/index.json');
  } catch (e) {
    showError('No forecast rounds published yet. Come back soon.');
    return;
  }
  if (!indexData.rounds || indexData.rounds.length === 0) {
    showError('No forecast rounds published yet. Come back soon.');
    return;
  }

  const metaData = await fetchJSON('./data/meta.json');
  countriesMeta = metaData.countries;
  countriesMeta.forEach(c => { countriesByCode[c.code] = c; });
  vocabulary = metaData.emoji_vocabulary;
  vocabulary.forEach(e => { vocabByEmoji[e.emoji] = e; });
  groups = metaData.groups;

  try {
    scorecardData = await fetchJSON('./data/scorecard.json');
  } catch (e) {
    scorecardData = null;
  }

  setupRoundSelect();
  setupCountrySelect();
  setupScorecardBadge();
  setupListToggle();
  setupMenuButton();
  setupPanelCloseHandlers();

  const hash = parseHash();
  const hashRoundValid = hash.round && indexData.rounds.some(r => r.round === hash.round);
  currentRoundId = hashRoundValid ? hash.round : indexData.latest;

  if (!webglOK) {
    document.getElementById('list-toggle').classList.add('active');
  } else {
    initScene();
    window.addEventListener('resize', onResize);
    window.addEventListener('orientationchange', onResize);
  }

  await loadRound(currentRoundId);
  renderListView();

  if (!webglOK) {
    showListView(true);
    const note = document.createElement('div');
    note.style.cssText = 'text-align:center;color:#9aa6bd;font-size:13px;margin-bottom:16px;';
    note.textContent = 'Your browser does not support WebGL, so here is the list view instead.';
    document.getElementById('list-view').prepend(note);
  }

  if (hash.country && countriesByCode[hash.country]) {
    setTimeout(() => selectCountry(hash.country), 150);
  }

  hideLoadingScreen();
  if (webglOK) animate();
}

function hideLoadingScreen() {
  const el = document.getElementById('loading-screen');
  el.style.opacity = '0';
  setTimeout(() => { el.style.display = 'none'; }, 400);
}

function showError(message) {
  document.getElementById('loading-screen').style.display = 'none';
  const err = document.getElementById('error-screen');
  err.style.display = 'flex';
  document.getElementById('error-message').textContent = message;
}

// ---------------------------------------------------------------------
// Round loading
// ---------------------------------------------------------------------

async function loadRound(roundId) {
  const roundEntry = indexData.rounds.find(r => r.round === roundId);
  if (!roundEntry) return;
  previousRoundId = roundEntry.previous_round;
  nextRoundId = null;
  const idx = indexData.rounds.findIndex(r => r.round === roundId);
  if (idx > 0) nextRoundId = indexData.rounds[idx - 1].round; // rounds sorted newest first

  bundleR = await fetchJSON(`./data/rounds/${roundId}/bundle.json`);
  bundleP = null;
  if (previousRoundId) {
    try { bundleP = await fetchJSON(`./data/rounds/${previousRoundId}/bundle.json`); }
    catch (e) { bundleP = null; }
  }
  bundleNext = null; // fetched lazily only when a modal needs outcomes

  document.getElementById('round-select').value = roundId;

  if (webglOK) {
    await rebuildCards();
  }
  renderListView();
  updateHash(currentRoundId, selectedCode);
}

async function fetchNextBundleLazy() {
  if (bundleNext || !nextRoundId) return bundleNext;
  try { bundleNext = await fetchJSON(`./data/rounds/${nextRoundId}/bundle.json`); }
  catch (e) { bundleNext = null; }
  return bundleNext;
}

// ---------------------------------------------------------------------
// Scene construction (Bible 6.5)
// ---------------------------------------------------------------------

function initScene() {
  const container = document.getElementById('canvas-container');
  const width = window.innerWidth, height = window.innerHeight;

  scene = new THREE.Scene();

  const isNarrow = width < 700;
  camera = new THREE.PerspectiveCamera(38, width / height, 0.1, 100);
  camera.position.set(0, 0, isNarrow ? 3.9 : 3.2);

  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.setSize(width, height);
  renderer.localClippingEnabled = true;
  container.appendChild(renderer.domElement);

  controls = new OrbitControls(camera, renderer.domElement);
  controls.enablePan = false;
  controls.enableDamping = true;
  controls.dampingFactor = 0.06;
  controls.rotateSpeed = 0.6;
  controls.autoRotate = true;
  controls.autoRotateSpeed = 0.35;
  controls.minDistance = 1.9;
  controls.maxDistance = 5.5;
  controls.addEventListener('start', onControlsStart);

  globeGroup = new THREE.Group();
  scene.add(globeGroup);

  buildStarField(isNarrow ? 300 : 600);
  buildGlobeLayers();

  renderer.domElement.addEventListener('pointerdown', onPointerDown);
  renderer.domElement.addEventListener('pointerup', onPointerUp);
  renderer.domElement.addEventListener('pointermove', onPointerMove);
}

function onControlsStart() {
  lastInteractionTime = Date.now();
  controls.autoRotate = false;
  if (autoRotateResumeTimer) clearTimeout(autoRotateResumeTimer);
  scheduleAutoRotateResume();
}

function scheduleAutoRotateResume() {
  if (autoRotateResumeTimer) clearTimeout(autoRotateResumeTimer);
  autoRotateResumeTimer = setTimeout(() => {
    if (!selectedCode) controls.autoRotate = true;
  }, AUTO_ROTATE_RESUME_MS);
}

function buildStarField(count) {
  const positions = new Float32Array(count * 3);
  for (let i = 0; i < count; i++) {
    const v = randomOnSphere(40);
    positions[i * 3] = v.x; positions[i * 3 + 1] = v.y; positions[i * 3 + 2] = v.z;
  }
  const geom = new THREE.BufferGeometry();
  geom.setAttribute('position', new THREE.BufferAttribute(positions, 3));
  const mat = new THREE.PointsMaterial({ color: 0xffffff, size: 1.2, transparent: true, opacity: 0.6, sizeAttenuation: false });
  starField = new THREE.Points(geom, mat);
  scene.add(starField);
}

function randomOnSphere(r) {
  const u = Math.random(), v = Math.random();
  const theta = 2 * Math.PI * u;
  const phi = Math.acos(2 * v - 1);
  return new THREE.Vector3(
    r * Math.sin(phi) * Math.cos(theta),
    r * Math.sin(phi) * Math.sin(theta),
    r * Math.cos(phi)
  );
}

let worldTopology = null;

async function buildGlobeLayers() {
  const layerColors = {
    2: { outline: 0xffffff, outlineOp: 0.85, grat: 0xffffff, gratOp: 0.10, fillOp: 0.10 },
    1: { outline: 0xb9c2cc, outlineOp: 0.55, grat: 0xb9c2cc, gratOp: 0.07, fillOp: 0.08 },
    0: { outline: 0x6b7078, outlineOp: 0.50, grat: 0x6b7078, gratOp: 0.06, fillOp: 0.06 },
  };

  for (const layer of [2, 1, 0]) {
    const r = RADIUS[layer];
    const c = layerColors[layer];

    const fillGeom = new THREE.SphereGeometry(r, 48, 32);
    const fillMat = new THREE.MeshBasicMaterial({ color: 0x0b1220, transparent: true, opacity: c.fillOp, depthWrite: false });
    const fillMesh = new THREE.Mesh(fillGeom, fillMat);
    globeGroup.add(fillMesh);

    const graticule = buildGraticule(r, c.grat, c.gratOp);
    graticule.material.clippingPlanes = [layerClipPlanes[layer]];
    globeGroup.add(graticule);
  }

  try {
    worldTopology = await fetchJSON('./assets/countries-110m.json');
    for (const layer of [2, 1, 0]) {
      const r = RADIUS[layer];
      const c = layerColors[layer];
      const outline = buildCountryOutline(worldTopology, r, c.outline, c.outlineOp);
      if (outline) { outline.material.clippingPlanes = [layerClipPlanes[layer]]; globeGroup.add(outline); outlineLineSegments.push(outline); }
    }
  } catch (e) {
    console.warn('Could not load countries-110m.json, globes will show graticule only:', e);
  }
}

function buildGraticule(r, color, opacity) {
  const positions = [];
  const SEGMENTS = 72;
  // Lines of latitude every 15 degrees.
  for (let lat = -75; lat <= 75; lat += 15) {
    for (let i = 0; i < SEGMENTS; i++) {
      const lng1 = -180 + (360 * i) / SEGMENTS;
      const lng2 = -180 + (360 * (i + 1)) / SEGMENTS;
      const p1 = latLngToVector3(lat, lng1, r);
      const p2 = latLngToVector3(lat, lng2, r);
      positions.push(p1.x, p1.y, p1.z, p2.x, p2.y, p2.z);
    }
  }
  // Lines of longitude every 15 degrees.
  for (let lng = -180; lng < 180; lng += 15) {
    for (let i = 0; i < SEGMENTS; i++) {
      const lat1 = -90 + (180 * i) / SEGMENTS;
      const lat2 = -90 + (180 * (i + 1)) / SEGMENTS;
      const p1 = latLngToVector3(lat1, lng, r);
      const p2 = latLngToVector3(lat2, lng, r);
      positions.push(p1.x, p1.y, p1.z, p2.x, p2.y, p2.z);
    }
  }
  const geom = new THREE.BufferGeometry();
  geom.setAttribute('position', new THREE.BufferAttribute(new Float32Array(positions), 3));
  const mat = new THREE.LineBasicMaterial({ color, transparent: true, opacity });
  return new THREE.LineSegments(geom, mat);
}

function buildCountryOutline(topology, r, color, opacity) {
  if (!window.topojson) { console.warn('topojson global not found'); return null; }
  const mesh = window.topojson.mesh(topology, topology.objects.countries);
  const positions = [];

  function addLineString(coords) {
    for (let i = 0; i < coords.length - 1; i++) {
      const [lng1, lat1] = coords[i];
      const [lng2, lat2] = coords[i + 1];
      const p1 = latLngToVector3(lat1, lng1, r);
      const p2 = latLngToVector3(lat2, lng2, r);
      positions.push(p1.x, p1.y, p1.z, p2.x, p2.y, p2.z);
    }
  }

  if (mesh.type === 'MultiLineString') {
    mesh.coordinates.forEach(addLineString);
  } else if (mesh.type === 'LineString') {
    addLineString(mesh.coordinates);
  } else if (mesh.type === 'GeometryCollection') {
    mesh.geometries.forEach(g => {
      if (g.type === 'LineString') addLineString(g.coordinates);
      else if (g.type === 'MultiLineString') g.coordinates.forEach(addLineString);
    });
  }

  const geom = new THREE.BufferGeometry();
  geom.setAttribute('position', new THREE.BufferAttribute(new Float32Array(positions), 3));
  const mat = new THREE.LineBasicMaterial({ color, transparent: true, opacity });
  return new THREE.LineSegments(geom, mat);
}

function onResize() {
  if (!renderer) return;
  const width = window.innerWidth, height = window.innerHeight;
  camera.aspect = width / height;
  camera.updateProjectionMatrix();
  renderer.setSize(width, height);
}

// ---------------------------------------------------------------------
// Cards (sprites) — Bible 6.6
// ---------------------------------------------------------------------

function buildCardTexture(flagTwemoji, emojiTwemojis) {
  const dpr = Math.min(window.devicePixelRatio || 1, 2);
  const W = 256, H = 232;
  const canvas = document.createElement('canvas');
  canvas.width = W * dpr; canvas.height = H * dpr;
  const ctx = canvas.getContext('2d');
  ctx.scale(dpr, dpr);
  ctx.clearRect(0, 0, W, H);
  ctx.shadowColor = 'rgba(0,0,0,0.6)';
  ctx.shadowBlur = 12;

  const flagImg = loadImage(flagTwemoji);
  const flagSize = 144;
  ctx.drawImage(flagImg, (W - flagSize) / 2, 0, flagSize, flagSize);

  const emojiSize = 72, gap = 8;
  const rowWidth = emojiSize * 3 + gap * 2;
  let x = (W - rowWidth) / 2;
  const y = flagSize + 16;
  emojiTwemojis.forEach(code => {
    const img = loadImage(code);
    ctx.drawImage(img, x, y, emojiSize, emojiSize);
    x += emojiSize + gap;
  });

  const tex = new THREE.CanvasTexture(canvas);
  tex.needsUpdate = true;
  return tex;
}

async function preloadImagesFor(flagCodes, emojiCodes) {
  const all = new Set([...flagCodes, ...emojiCodes]);
  const promises = [];
  all.forEach(code => promises.push(imgReady(loadImage(code))));
  await Promise.all(promises);
}

async function rebuildCards() {
  // Dispose old sprites.
  sprites.forEach(s => {
    globeGroup.remove(s.sprite);
    s.sprite.material.map && s.sprite.material.map.dispose();
    s.sprite.material.dispose();
  });
  sprites = [];
  spritesByCountry = {};
  if (connectorLine) { globeGroup.remove(connectorLine); connectorLine = null; }

  // Preload every flag + emoji PNG we need for this round.
  const flagCodes = countriesMeta.map(c => c.twemoji);
  const emojiCodesNeeded = new Set();
  countriesMeta.forEach(c => {
    const code = c.code;
    const outerCountry = bundleR.countries[code];
    const middleCountry = bundleR.countries[code];
    const innerCountry = bundleP ? bundleP.countries[code] : null;
    (outerCountry && outerCountry.display ? outerCountry.display.emojis : []).forEach(e => emojiCodesNeeded.add(emojiToTwemoji(e)));
    (middleCountry && middleCountry.position ? middleCountry.position.emojis : []).forEach(e => emojiCodesNeeded.add(emojiToTwemoji(e)));
    (innerCountry && innerCountry.position ? innerCountry.position.emojis : []).forEach(e => emojiCodesNeeded.add(emojiToTwemoji(e)));
  });
  await preloadImagesFor(flagCodes, [...emojiCodesNeeded]);

  const layersData = [
    { layer: LAYER.OUTER, getEmojis: (code) => { const c = bundleR.countries[code]; return c && c.display ? c.display.emojis : null; } },
    { layer: LAYER.MIDDLE, getEmojis: (code) => { const c = bundleR.countries[code]; return c && c.position ? c.position.emojis : null; } },
    { layer: LAYER.INNER, getEmojis: (code) => { if (!bundleP) return null; const c = bundleP.countries[code]; return c && c.position ? c.position.emojis : null; } },
  ];

  for (const { layer, getEmojis } of layersData) {
    for (const country of countriesMeta) {
      const emojis = getEmojis(country.code);
      if (!emojis) continue; // country missing on this layer only
      const emojiCodes = emojis.map(emojiToTwemoji);
      const tex = buildCardTexture(country.twemoji, emojiCodes);
      const [w, h] = SPRITE_SIZE[layer];
      const mat = new THREE.SpriteMaterial({
        map: tex, color: SPRITE_COLOR[layer],
        transparent: true, depthWrite: false, depthTest: false,
      });
      const sprite = new THREE.Sprite(mat);
      sprite.scale.set(w, h, 1);
      sprite.center.set(SPRITE_CENTER, SPRITE_CENTER);
      sprite.renderOrder = RENDER_ORDER[layer];

      // Bible 6.16: only the outer card gets a real 3D anchor on its own
      // globe. Middle and inner start at the same local position and are
      // repositioned every frame in screen space by updateCardColumns().
      const anchor = latLngToVector3(country.lat, country.lng, RADIUS[LAYER.OUTER] * 1.015);
      sprite.position.copy(anchor);
      sprite.userData = { code: country.code, layer, anchor, baseColor: SPRITE_COLOR[layer] };

      globeGroup.add(sprite);
      const entry = { sprite, code: country.code, layer, anchor };
      sprites.push(entry);
      (spritesByCountry[country.code] = spritesByCountry[country.code] || {})[layer] = entry;
    }
  }
}

function emojiToTwemoji(emoji) {
  const entry = vocabByEmoji[emoji];
  if (entry) return entry.twemoji;
  return '2753'; // question mark fallback per Bible 2.4
}

// ---------------------------------------------------------------------
// Per-frame update: screen-space column stacking, fading, hover,
// connector line (Bible 6.16, 6.7)
// ---------------------------------------------------------------------

// Half-heights (world units) used for the vertical gaps between cards,
// per Bible 6.16's formula.
const GAP_MIDDLE = SPRITE_SIZE[2][1] * 0.5 + SPRITE_SIZE[1][1] * 0.5 + 0.012;
const GAP_INNER = SPRITE_SIZE[1][1] * 0.5 + SPRITE_SIZE[0][1] * 0.5 + 0.012;

function updateClipPlanes() {
  const toCamera = camera.position.clone().sub(controls.target);
  const dist = toCamera.length();
  toCamera.normalize();
  for (const layer of [2, 1, 0]) {
    const r = RADIUS[layer];
    // keep the points of the globe that are on the camera's side of the horizon circle
    layerClipPlanes[layer].normal.copy(toCamera);
    layerClipPlanes[layer].constant = -(r * r) / dist;
  }
}

function animate() {
  requestAnimationFrame(animate);
  updateClipPlanes();
  controls.update();
  updateCardColumns();
  renderer.render(scene, camera);
}

function worldToScreenScale(worldPoint) {
  const p1 = worldPoint.clone().project(camera);
  const offsetPoint = worldPoint.clone().add(camera.up.clone().normalize().multiplyScalar(0.01));
  const p2 = offsetPoint.clone().project(camera);
  const dyNdc = Math.abs(p2.y - p1.y);
  const dyPx = (dyNdc / 2) * renderer.domElement.clientHeight;
  return dyPx / 0.01; // screen pixels per world unit, at this depth
}

function applyLayerVisibility(entry, d) {
  const { sprite, layer, code } = entry;
  let visible, opacity;
  if (layer === LAYER.OUTER) {
    visible = d > 0.02;
    opacity = clamp((d - 0.02) / 0.25, 0, 1);
  } else if (layer === LAYER.MIDDLE) {
    visible = d > 0.30;
    opacity = clamp((d - 0.30) / 0.25, 0, 1) * 0.95;
  } else {
    visible = d > 0.45;
    opacity = clamp((d - 0.45) / 0.25, 0, 1) * 0.90;
  }
  sprite.visible = visible;

  const isHovered = (hoveredCode === code) || (selectedCode === code);
  if (isHovered) {
    sprite.material.opacity = 1;
    sprite.material.color.setHex(HOVER_COLOR);
  } else {
    const dim = (hoveredCode || selectedCode) ? 0.3 : 1;
    sprite.material.opacity = opacity * dim;
    sprite.material.color.setHex(sprite.userData.baseColor);
  }
}

function updateCardColumns() {
  const camDir = camera.position.clone().normalize();
  const invGlobeMatrix = globeGroup.matrixWorld.clone().invert();
  const ndcPerPx = 2 / renderer.domElement.clientHeight;

  for (const code in spritesByCountry) {
    const group = spritesByCountry[code];
    const outer = group[LAYER.OUTER];
    if (!outer) continue; // no outer card for this country this round

    // Visibility/fading direction d is always computed from the outer
    // card's own 3D anchor, shared by all three layers (Bible 6.16).
    const worldAnchorDir = outer.anchor.clone().applyMatrix4(globeGroup.matrixWorld).normalize();
    const d = worldAnchorDir.dot(camDir);
    applyLayerVisibility(outer, d);

    const outerWorldPos = outer.sprite.position.clone().applyMatrix4(globeGroup.matrixWorld);
    const ndc = outerWorldPos.clone().project(camera);
    const pxPerWorld = worldToScreenScale(outerWorldPos);

    const middle = group[LAYER.MIDDLE];
    if (middle) {
      const targetNdc = new THREE.Vector3(ndc.x, ndc.y - GAP_MIDDLE * pxPerWorld * ndcPerPx, ndc.z);
      const worldPos = targetNdc.unproject(camera);
      middle.sprite.position.copy(worldPos.applyMatrix4(invGlobeMatrix));
      applyLayerVisibility(middle, d);
    }

    const inner = group[LAYER.INNER];
    if (inner) {
      const targetNdc = new THREE.Vector3(ndc.x, ndc.y - (GAP_MIDDLE + GAP_INNER) * pxPerWorld * ndcPerPx, ndc.z);
      const worldPos = targetNdc.unproject(camera);
      inner.sprite.position.copy(worldPos.applyMatrix4(invGlobeMatrix));
      applyLayerVisibility(inner, d);
    }
  }

  updateConnectorLine();
}

function updateConnectorLine() {
  const activeCode = hoveredCode || selectedCode;
  if (connectorLine) { globeGroup.remove(connectorLine); connectorLine.geometry.dispose(); connectorLine.material.dispose(); connectorLine = null; }
  if (!activeCode) return;
  const group = spritesByCountry[activeCode];
  if (!group) return;
  const points = [group[LAYER.OUTER], group[LAYER.MIDDLE], group[LAYER.INNER]]
    .filter(Boolean)
    .map(entry => entry.sprite.position);
  if (points.length < 2) return;
  const geom = new THREE.BufferGeometry().setFromPoints(points);
  const mat = new THREE.LineBasicMaterial({ color: 0x6ee7f9, transparent: true, opacity: 0.8 });
  connectorLine = new THREE.Line(geom, mat);
  connectorLine.renderOrder = 25;
  globeGroup.add(connectorLine);
}

// ---------------------------------------------------------------------
// Raycasting, hover, click (Bible 6.7)
// ---------------------------------------------------------------------

function getPointerNDC(event) {
  const rect = renderer.domElement.getBoundingClientRect();
  return new THREE.Vector2(
    ((event.clientX - rect.left) / rect.width) * 2 - 1,
    -((event.clientY - rect.top) / rect.height) * 2 + 1
  );
}

function raycastSprite(event) {
  const ndc = getPointerNDC(event);
  const raycaster = new THREE.Raycaster();
  raycaster.setFromCamera(ndc, camera);
  const visibleSprites = sprites.filter(s => s.sprite.visible).map(s => s.sprite);
  const hits = raycaster.intersectObjects(visibleSprites);
  if (hits.length === 0) return null;
  const hit = sprites.find(s => s.sprite === hits[0].object);
  return hit || null;
}

function onPointerDown(event) {
  pointerDownPos = { x: event.clientX, y: event.clientY };
  pointerMoved = false;
}

function onPointerMove(event) {
  if (pointerDownPos) {
    const dx = event.clientX - pointerDownPos.x, dy = event.clientY - pointerDownPos.y;
    if (Math.sqrt(dx * dx + dy * dy) > 6) pointerMoved = true;
  }
  if (event.pointerType === 'mouse' || event.pointerType === undefined) {
    const hit = raycastSprite(event);
    const newHover = hit ? hit.code : null;
    if (newHover !== hoveredCode) {
      hoveredCode = newHover;
      renderer.domElement.style.cursor = hoveredCode ? 'pointer' : 'default';
      updateHoverLabel(event, hoveredCode);
    } else if (hoveredCode) {
      updateHoverLabel(event, hoveredCode);
    }
  }
}

function onPointerUp(event) {
  const moved = pointerMoved;
  pointerDownPos = null;
  if (moved) return;
  const hit = raycastSprite(event);
  if (hit) selectCountry(hit.code);
}

function updateHoverLabel(event, code) {
  const label = document.getElementById('hover-label');
  if (!code) { label.classList.remove('visible'); return; }
  const country = countriesByCode[code];
  const countryData = bundleR.countries[code];
  const headline = countryData && countryData.display ? countryData.display.headline : '';
  label.textContent = `${country.name} — ${headline}`;
  label.style.left = event.clientX + 'px';
  label.style.top = event.clientY + 'px';
  label.classList.add('visible');
}

// ---------------------------------------------------------------------
// Selection, camera animation, hash (Bible 6.7)
// ---------------------------------------------------------------------

function selectCountry(code) {
  selectedCode = code;
  controls.autoRotate = false;
  if (autoRotateResumeTimer) clearTimeout(autoRotateResumeTimer);
  updateHash(currentRoundId, code);
  document.getElementById('country-select').value = code;
  if (webglOK) animateCameraToCountry(code);
  openPanel(code);
}

let centerAnimationId = 0;

// Centers a country WITHOUT ever tilting the globe: north stays up, always (the user can look
// left, right, up and down, but never sees the globe lying on its side). The globe only spins
// about its own north-south axis, and the camera moves up or down to the country's latitude.
function animateCameraToCountry(code) {
  const sp = sprites.find(s => s.code === code && s.layer === LAYER.OUTER);
  if (!sp) return;
  const a = sp.anchor.clone().normalize();                 // the country, in the globe's own frame
  const azA = Math.atan2(a.x, a.z);                        // its compass direction on the globe
  const polarTarget = Math.acos(clamp(a.y, -1, 1));        // 0 = north pole, PI = south pole

  const offset = camera.position.clone().sub(controls.target);
  const radius = offset.length();
  const azCam = Math.atan2(offset.x, offset.z);
  const polarStart = Math.acos(clamp(offset.y / radius, -1, 1));

  const yawStart = 2 * Math.atan2(globeGroup.quaternion.y, globeGroup.quaternion.w); // pure spin about Y
  let yawEnd = azCam - azA;                                // spin that puts the country in front of the camera
  while (yawEnd - yawStart > Math.PI) yawEnd -= 2 * Math.PI;   // take the short way round
  while (yawEnd - yawStart < -Math.PI) yawEnd += 2 * Math.PI;

  const myId = ++centerAnimationId;
  const duration = 900;
  const startTime = performance.now();
  const yAxis = new THREE.Vector3(0, 1, 0);
  function step(now) {
    if (myId !== centerAnimationId) return;                // a newer click took over
    const t = clamp((now - startTime) / duration, 0, 1);
    const eased = t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2;
    globeGroup.quaternion.setFromAxisAngle(yAxis, yawStart + (yawEnd - yawStart) * eased);
    const polar = clamp(polarStart + (polarTarget - polarStart) * eased, 0.05, Math.PI - 0.05);
    camera.position.set(
      controls.target.x + radius * Math.sin(polar) * Math.sin(azCam),
      controls.target.y + radius * Math.cos(polar),
      controls.target.z + radius * Math.sin(polar) * Math.cos(azCam));
    controls.update();
    if (t < 1) requestAnimationFrame(step);
  }
  requestAnimationFrame(step);
}

function deselectCountry() {
  selectedCode = null;
  updateHash(currentRoundId, null);
  scheduleAutoRotateResume();
}

// ---------------------------------------------------------------------
// Header controls (Bible 6.9)
// ---------------------------------------------------------------------

function setupRoundSelect() {
  const sel = document.getElementById('round-select');
  sel.innerHTML = '';
  indexData.rounds.forEach(r => {
    const opt = document.createElement('option');
    opt.value = r.round;
    opt.textContent = r.label;
    sel.appendChild(opt);
  });
  sel.addEventListener('change', async () => {
    currentRoundId = sel.value;
    deselectCountry();
    closePanel();
    await loadRound(currentRoundId);
  });
}

function setupCountrySelect() {
  const sel = document.getElementById('country-select');
  sel.innerHTML = '<option value="">Jump to a country...</option>';
  const byGroup = {};
  countriesMeta.forEach(c => { (byGroup[c.group] = byGroup[c.group] || []).push(c); });
  Object.keys(groups).forEach(groupKey => {
    const list = byGroup[groupKey];
    if (!list) return;
    const optgroup = document.createElement('optgroup');
    optgroup.label = groups[groupKey];
    list.forEach(c => {
      const opt = document.createElement('option');
      opt.value = c.code;
      opt.textContent = c.name;
      optgroup.appendChild(opt);
    });
    sel.appendChild(optgroup);
  });
  sel.addEventListener('change', () => {
    if (sel.value) selectCountry(sel.value);
  });
}

function setupListToggle() {
  const btn = document.getElementById('list-toggle');
  btn.addEventListener('click', () => {
    const isActive = btn.classList.toggle('active');
    showListView(isActive);
    btn.textContent = isActive ? 'Globe view' : 'List view';
  });
}

function showListView(active) {
  document.getElementById('list-view').classList.toggle('active', active);
  document.getElementById('canvas-container').style.display = active ? 'none' : 'block';
}

function setupMenuButton() {
  const btn = document.getElementById('menu-button');
  const header = document.getElementById('header');
  btn.addEventListener('click', () => header.classList.toggle('menu-open'));
}

function setupScorecardBadge() {
  const badge = document.getElementById('scorecard-badge');
  updateScorecardBadge();
  badge.addEventListener('click', openScorecardModal);
}

function updateScorecardBadge() {
  const badge = document.getElementById('scorecard-badge');
  const sc = scorecardData;
  if (!sc) { badge.textContent = 'Scorecard starts after the first judged round'; return; }
  if (sc.schema_version === 4) { badge.textContent = scorecardBadgeV4(sc); return; }
  if (sc.schema_version === 2) {
    const m = sc.manual_forecast || {};
    let t = '';
    if (sc.country_rounds_scored > 0) {
      t = `Crystal Balls corrected the plain forecast ${sc.flips || 0} times; ${sc.flips_right || 0} corrections proved right, ${sc.flips_wrong || 0} wrong. Verdict: ${sc.verdict}.`;
    } else {
      t = 'Crystal vs plain scorecard starts after the first judged round.';
    }
    if (m.questions_resolved > 0) {
      t += ` Nir's manual forecasts (Oct 1 and Oct 14): ${m.correct} of ${m.questions_resolved} correct, ${m.questions_unclear} unclear.`;
    }
    badge.textContent = t;
    return;
  }
  if (sc.country_rounds_scored === 0) { badge.textContent = 'Scorecard starts after the first judged round'; return; }
  const total = sc.crystal_wins + sc.naive_wins;
  const pct = sc.crystal_win_rate != null ? Math.round(sc.crystal_win_rate * 100) : 0;
  badge.textContent = `Crystal Balls beat the plain forecast in ${sc.crystal_wins} of ${total} country-weeks (${pct}%)`;
}

function openScorecardModal() {
  const backdrop = document.getElementById('scorecard-modal-backdrop');
  const modal = document.getElementById('scorecard-modal');
  if (!scorecardData) { modal.innerHTML = '<p>No scorecard data yet.</p>'; backdrop.classList.add('open'); return; }
  const sc = scorecardData;
  let html = '';
  if (sc.schema_version === 4) {
    html += scorecardModalV4(sc);
  } else if (sc.schema_version === 2) {
    html += `<p class="baseline">We declare a winner only after at least ${sc.min_disagreements_for_verdict} disagreements, with one side right in at least two thirds of them.</p>`;
    html += `<div class="stat-row"><span>Verdict</span><span>${sc.verdict}</span></div>`;
    html += `<div class="stat-row"><span>Questions checked</span><span>${sc.questions_resolved} (unclear: ${sc.questions_unclear})</span></div>`;
    html += `<div class="stat-row"><span>Crystal correct</span><span>${sc.crystal_correct}</span></div>`;
    html += `<div class="stat-row"><span>Plain forecast correct</span><span>${sc.naive_correct}</span></div>`;
    html += `<div class="stat-row"><span>Disagreements (Crystal won / plain won)</span><span>${sc.disagreements} (${sc.crystal_won_disagreements} / ${sc.naive_won_disagreements})</span></div>`;
    (sc.per_round || []).forEach(pr => {
      html += `<div class="stat-row"><span>${pr.round}</span><span>crystal ${pr.crystal_correct} / plain ${pr.naive_correct} of ${pr.questions_resolved}</span></div>`;
    });
    const m = sc.manual_forecast || {};
    html += `<div class="stat-row"><span>Nir's manual forecasts</span><span>${m.correct || 0} of ${m.questions_resolved || 0} correct, ${m.questions_unclear || 0} unclear</span></div>`;
  } else {
    html += `<p class="baseline">A forecaster who always says 50 percent scores 0.25. Lower is better.</p>`;
    html += `<div class="stat-row"><span>Mean Brier, Crystal</span><span>${fmtNum(sc.mean_brier_crystal)}</span></div>`;
    html += `<div class="stat-row"><span>Mean Brier, plain forecast</span><span>${fmtNum(sc.mean_brier_naive)}</span></div>`;
    (sc.per_round || []).forEach(pr => {
      html += `<div class="stat-row"><span>${pr.round}</span><span>crystal ${pr.crystal_wins} / naive ${pr.naive_wins} / tie ${pr.ties}</span></div>`;
    });
  }
  html += `<p style="margin-top:14px;"><a href="./data/scorecard.json" target="_blank" rel="noopener">View data/scorecard.json</a></p>`;
  html += `<button class="btn" id="scorecard-modal-close" style="margin-top:10px;">Close</button>`;
  modal.innerHTML = html;
  backdrop.classList.add('open');
  document.getElementById('scorecard-modal-close').addEventListener('click', () => backdrop.classList.remove('open'));
  backdrop.addEventListener('click', (e) => { if (e.target === backdrop) backdrop.classList.remove('open'); }, { once: true });
}

function fmtNum(n) { return n == null ? '—' : n.toFixed(3); }

// ---------------------------------------------------------------------
// Part 13 (schema version 4): four things we expect, the judge's marks, the badge
// ---------------------------------------------------------------------

function esc(t) {
  return String(t == null ? '' : t).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

const GRADE_MARK = {
  came_true: ['\u2714', 'came true', 'yes'],
  true_in_direction: ['\u25D0', 'right direction, details changed', 'half'],
  did_not_appear: ['\u2717', 'did not appear', 'no'],
  cannot_establish: ['?', 'cannot establish', 'unknown'],
};
const ITEM_LABEL = { lead: 'Lead', second: 'Second', third: 'Third', fade_call: 'Fade call' };

function v4ItemsHtml(bulletin, armGrades) {
  if (!bulletin) return '<p>No forecast.</p>';
  let html = '';
  ['lead', 'second', 'third'].forEach(k => {
    const it = bulletin[k]; if (!it) return;
    html += v4ItemRow(ITEM_LABEL[k], it.subject, it.expected, it.sign, armGrades && armGrades.items[k]);
  });
  const f = bulletin.fade_call;
  if (f) html += v4ItemRow(ITEM_LABEL.fade_call, f.subject, f.expected, f.sign, armGrades && armGrades.items.fade_call);
  const sp = bulletin.surprise;
  if (sp) html += `<div class="statement-row"><div class="statement-text"><strong>Possible surprise (${esc(sp.chance)} chance):</strong> ${esc(sp.subject)}. ${esc(sp.expected)}</div></div>`;
  return html;
}

function v4ItemRow(label, subject, expected, sign, grade) {
  let mark = '';
  if (grade) {
    const m = GRADE_MARK[grade.grade] || ['?', grade.grade, 'unknown'];
    mark = ` <span class="outcome-mark ${m[2]}" title="${esc(m[1])}">${m[0]} ${esc(m[1])}</span>`;
  }
  let html = `<div class="statement-row"><div class="statement-text"><strong>${label}: ${esc(subject)}.</strong> ${esc(expected)}${mark}</div>`;
  if (sign) html += `<div class="emoji-reason">What you would see: ${esc(sign)}</div>`;
  if (grade && grade.evidence) html += `<div class="evidence-text">${esc(grade.evidence)}</div>`;
  return html + `</div>`;
}

function v4ChangeRow(countryR) {
  const r = countryR.reader || {};
  const devs = r.developments || [];
  const fresh = devs.filter(d => d.direction === 'new').map(d => d.subject);
  const kept = devs.filter(d => d.direction === 'continuing' || d.direction === 'escalating').map(d => d.subject);
  let html = '';
  if (kept.length) html += `<div class="history-row"><span class="dot outer"></span><span class="label">Persisted:</span> ${esc(kept.slice(0, 4).join('; '))}</div>`;
  if ((r.gone || []).length) html += `<div class="history-row"><span class="dot outer"></span><span class="label">Faded:</span> ${esc(r.gone.slice(0, 4).join('; '))}</div>`;
  if (fresh.length) html += `<div class="history-row"><span class="dot outer"></span><span class="label">New:</span> ${esc(fresh.slice(0, 4).join('; '))}</div>`;
  return html || `<div class="history-row"><span class="dot outer"></span><span class="label">Change:</span> no data</div>`;
}

function v4Forecast(countryR) {
  return (countryR.forecasts || {});
}

function v4JudgeFor(nextBundle, code, roundId) {
  if (!nextBundle || !nextBundle.countries[code]) return { main: null, hand: null };
  const n = nextBundle.countries[code];
  const ok = j => j && j.per_arm && !j.unscorable && !j.dry_run && j.graded_round === roundId;
  return { main: ok(n.judgment) ? n.judgment : null, hand: ok(n.judgment_hand_made) ? n.judgment_hand_made : null };
}

function v4VerdictLine(j) {
  if (!j) return '';
  const e = (j.verdicts && j.verdicts[0] || []).find(x => (x.first === 'crystal' && x.second === 'plain') || (x.first === 'plain' && x.second === 'crystal'));
  let who = 'tie';
  if (j.v != null) who = j.v >= 0.5 ? 'Crystal' : (j.v <= -0.5 ? 'plain forecast' : 'tie');
  return `<div class="score-line ${who === 'Crystal' ? 'crystal' : who === 'tie' ? 'tie' : 'naive'}">The judge preferred: ${who}.${e ? ' ' + esc(e.reason) : ''}</div>`;
}

async function openModalV4(code, country, countryR) {
  const display = countryR.display || {};
  const reader = countryR.reader || {};
  const fc = v4Forecast(countryR);
  const nextBundle = await fetchNextBundleLazy();
  const judged = v4JudgeFor(nextBundle, code, currentRoundId);
  const j = judged.main || judged.hand;
  let html = `<div class="panel-header-row">
    <img class="flag" src="${emojiSrc(country.twemoji)}" alt="">
    <h2>${country.name}</h2>
    <button class="close-btn" id="modal-close-x" aria-label="Close">&times;</button>
  </div>`;
  html += `<div class="headline">${esc(display.headline || '')}</div>`;
  if (countryR.forecast_meta && countryR.forecast_meta.hand_made) html += `<p class="baseline">Hand-made forecast (not part of the plain-versus-Crystal scorecard).</p>`;
  html += `<h3>In plain words</h3>`;
  (display.eli5 || display.tldr || '').split('\n\n').filter(p => p.trim()).forEach(p => { html += `<p>${esc(p)}</p>`; });
  html += `<h3>Four things we expect</h3>`;
  html += v4ItemsHtml(fc.crystal, j && j.per_arm && j.per_arm.crystal);
  if (j) html += v4VerdictLine(j);
  if (j && j.per_arm && j.per_arm.crystal) html += `<p class="baseline">Judge's note: ${esc(j.per_arm.crystal.archer_note)}</p>`;
  if (fc.plain) {
    html += `<details><summary>The plain forecast, for comparison</summary>`;
    html += `<p>${esc(fc.plain.summary)}</p>` + v4ItemsHtml(fc.plain, j && j.per_arm && j.per_arm.plain);
    html += `</details>`;
  }
  html += `<h3>What persisted, what faded, what surprised us</h3>` + v4ChangeRow(countryR);
  html += `<h3>What happened this week</h3><p>${esc(reader.summary || '')}</p>`;
  if (reader.key_events && reader.key_events.length) {
    html += `<ul class="bullets">`;
    reader.key_events.forEach(ke => { html += `<li>${ke.date ? esc(ke.date) + ': ' : ''}${esc(ke.event)}</li>`; });
    html += `</ul>`;
  }
  if (reader.unscorable) html += `<p class="baseline">Not scored this round: ${esc(reader.unscorable_reason || '')}</p>`;
  if (bundleR.round && bundleR.round.run_in) html += `<p class="baseline">Run-in round, forecasts generated late: made with headlines up to ${esc(bundleR.round.window_end)}, generated ${esc((countryR.generated_at || '').slice(0, 16).replace('T', ' '))}. Its judged results are not counted in the verdict.</p>`;
  html += `<div class="modal-footer">Model: ${esc(countryR.model || '\u2014')} \u00B7 Generated: ${esc(countryR.generated_at || '\u2014')}</div>`;
  html += `<button class="btn modal-close" id="modal-close-btn">Close</button>`;
  const modal = document.getElementById('modal');
  modal.innerHTML = html;
  document.getElementById('modal-backdrop').classList.add('open');
  document.getElementById('modal-close-x').addEventListener('click', closeModal);
  document.getElementById('modal-close-btn').addEventListener('click', closeModal);
}

function scorecardBadgeV4(sc) {
  if (!sc.judge_validated) return 'Judge not yet validated. Judged country-weeks so far: ' + (sc.judged_country_weeks || 0) + '.';
  const p = x => (x == null ? '' : ` (${x}%)`);
  return `Judged country-weeks: ${sc.judged_country_weeks}. Crystal better: ${sc.crystal_better}${p(sc.crystal_better_pct)}, tie: ${sc.ties}${p(sc.ties_pct)}, plain better: ${sc.plain_better}${p(sc.plain_better_pct)}. Verdict: ${sc.verdict}. Against more-of-the-same: ${sc.verdict_u}.`;
}

function scorecardModalV4(sc) {
  let html = `<p class="baseline">${esc(sc.judge_note || '')}</p>`;
  html += `<div class="stat-row"><span>Verdict (Crystal against plain)</span><span>${esc(sc.verdict)}</span></div>`;
  html += `<div class="stat-row"><span>Verdict against more-of-the-same</span><span>${esc(sc.verdict_u)}</span></div>`;
  html += `<div class="stat-row"><span>Rounds scored (verdict needs ${sc.min_rounds_for_verdict})</span><span>${sc.rounds_scored}</span></div>`;
  html += `<div class="stat-row"><span>Mean verdict, Crystal minus plain (-2 to 2)</span><span>${sc.mean_v == null ? '\u2014' : sc.mean_v}${sc.interval_v ? ' (90% interval ' + sc.interval_v[0] + ' to ' + sc.interval_v[1] + ')' : ''}</span></div>`;
  const nf = sc.noise_floor;
  if (nf && nf.countries_compared) {
    html += `<div class="stat-row"><span>Noise floor (${nf.countries_compared} country-weeks, same lead story / same direction as plain)</span><span>plain run twice: ${nf.plain_repeat_same_subject} / ${nf.plain_repeat_same_direction}; Crystal: ${nf.crystal_same_subject} / ${nf.crystal_same_direction}</span></div>`;
    html += `<p class="baseline">${esc(nf.note || '')}</p>`;
  }
  html += `<div class="stat-row"><span>Judged country-weeks</span><span>${sc.judged_country_weeks}</span></div>`;
  html += `<div class="stat-row"><span>Unscorable country-weeks</span><span>${sc.unscorable} of ${sc.country_rounds}</span></div>`;
  html += `<div class="stat-row"><span>First-listed bulletin won (order bias)</span><span>${sc.first_listed_wins_share == null ? '\u2014' : Math.round(sc.first_listed_wins_share * 100) + '%'} of ${sc.first_listed_nonties}</span></div>`;
  Object.entries(sc.item_grades || {}).forEach(([arm, g]) => {
    html += `<div class="stat-row"><span>Item grades, ${arm}</span><span>${g.came_true || 0} true / ${g.true_in_direction || 0} right direction / ${g.did_not_appear || 0} did not appear / ${g.cannot_establish || 0} cannot establish</span></div>`;
  });
  Object.entries(sc.gap_buckets || {}).forEach(([k, g]) => {
    if (g.n) html += `<div class="stat-row"><span>Gap ${k}</span><span>${g.n} country-weeks, mean ${g.mean_v}</span></div>`;
  });
  html += `<div class="stat-row"><span>Judge validation</span><span>${sc.judge_validated ? 'passed' : 'not yet validated'}</span></div>`;
  (sc.hand_made_forecasts || []).forEach(h => {
    html += `<div class="stat-row"><span>Hand-made forecast, ${esc(h.code)}, graded ${esc(h.round)}${h.partial ? ` (preview, ${h.days_covered} of ${h.days_total} days)` : ''}</span><span>against more-of-the-same: ${h.u == null ? '\u2014' : h.u}</span></div>`;
  });
  return html;
}

// ---------------------------------------------------------------------
// Panel (Bible 6.8)
// ---------------------------------------------------------------------

function setupPanelCloseHandlers() {
  // delegated later via re-render; close button bound each render.
}

function closePanel() {
  const panel = document.getElementById('panel');
  panel.classList.remove('open');
  setTimeout(() => panel.classList.add('hidden'), 260);
  deselectCountry();
}

function winnerClass(winner) {
  if (winner === 'crystal') return 'crystal';
  if (winner === 'tie') return 'tie';
  if (winner === 'naive') return 'naive';
  return '';
}

function openPanel(code) {
  const country = countriesByCode[code];
  const countryR = bundleR.countries[code];
  if (!country || !countryR) return;
  const countryP = bundleP ? bundleP.countries[code] : null;
  const roundEntry = indexData.rounds.find(r => r.round === currentRoundId);

  const panel = document.getElementById('panel');
  panel.classList.remove('hidden');

  const display = countryR.display || {};
  const position = countryR.position || {};
  const velocity = countryR.velocity || null;
  const wind = countryR.wind || null;

  let html = `<div class="panel-pad">`;
  html += `<div class="panel-header-row">
    <img class="flag" src="${emojiSrc(country.twemoji)}" alt="">
    <h2>${country.name}</h2>
    <span class="pill">${groups[country.group] || country.group}</span>
    <button class="close-btn" id="panel-close" aria-label="Close">&times;</button>
  </div>`;

  const roundLabel = roundEntry ? roundEntry.label : currentRoundId;
  const horizonEnd = (countryR.crystal_forecast && countryR.crystal_forecast.horizon_end) || (countryR.forecast_meta && countryR.forecast_meta.horizon_end) || '';
  if (countryR.schema_version === 4 && bundleR.round && !(roundEntry && roundEntry.is_legacy)) {
    const gen = (countryR.generated_at || '').slice(0, 16).replace('T', ' ');
    html += `<div class="round-line">Made with headlines up to ${esc(bundleR.round.window_end)}, generated ${esc(gen)}${bundleR.round.run_in ? ' (run-in round, forecasts generated late)' : ''}</div>`;
  } else if (roundEntry && roundEntry.is_legacy) {
    html += `<div class="round-line">Manual round, ${roundLabel}</div>`;
  } else {
    html += `<div class="round-line">Forecast made ${roundLabel} for ${horizonEnd ? 'the week to ' + horizonEnd : 'the next collection, about 7 days later'}</div>`;
  }

  html += `<div class="headline">${display.headline || ''}</div>`;

  html += `<div class="emoji-row" id="panel-emoji-row">`;
  (display.emojis || []).forEach((e, i) => {
    const meaning = vocabByEmoji[e] ? vocabByEmoji[e].meaning : '';
    html += `<img src="${emojiSrc(emojiToTwemoji(e))}" title="${meaning}" data-reason-idx="${i}">`;
  });
  html += `</div><div class="emoji-reason" id="panel-emoji-reason"></div>`;

  html += `<p class="tldr">${esc(display.tldr || '')}</p>`;

  if (countryR.schema_version === 4) {
    const fc4 = (countryR.forecasts || {}).crystal;
    html += `<h3>Four things we expect</h3>` + v4ItemsHtml(fc4, null);
  }

  html += `<div class="how-we-got-here">`;
  html += historyRow('inner', 'Last week', countryP ? countryP.position : null);
  html += historyRow('middle', 'This week', position);
  html += (countryR.schema_version === 4 ? v4ChangeRow(countryR) : trendRow(velocity));
  html += `</div>`;

  if (wind && wind.questions && wind.winner && wind.winner !== 'none') {
    if (wind.single_forecaster) {
      html += `<div class="score-line tie">Last check of the manual forecast: ${wind.correct} of ${wind.resolved} correct, ${wind.unclear} unclear</div>`;
    } else {
      html += `<div class="score-line ${winnerClass(wind.winner)}">Last week's check: Crystal Balls ${wind.crystal_correct} of ${wind.resolved} correct, plain forecast ${wind.naive_correct} of ${wind.resolved}, ${wind.unclear} unclear</div>`;
    }
  } else if (wind && wind.winner && wind.winner !== 'none' && wind.crystal) {
    const bC = wind.crystal ? wind.crystal.brier : null;
    const bN = wind.naive ? wind.naive.brier : null;
    html += `<div class="score-line ${winnerClass(wind.winner)}">Last week's forecast check: Crystal Balls ${fmtNum(bC)} vs plain forecast ${fmtNum(bN)}, lower is better, winner: ${wind.winner}</div>`;
  }

  html += `<div class="panel-buttons">
    <button class="btn primary" id="panel-readmore">Read more</button>
    <button class="btn" id="panel-copylink">Copy link</button>
    <a class="btn" id="panel-rawjson" href="./data/rounds/${currentRoundId}/countries/${code}.json" target="_blank" rel="noopener">Raw JSON</a>
  </div>`;

  html += `</div>`;
  panel.innerHTML = html;

  requestAnimationFrame(() => panel.classList.add('open'));

  document.getElementById('panel-close').addEventListener('click', closePanel);
  document.getElementById('panel-readmore').addEventListener('click', () => openModal(code));
  document.getElementById('panel-copylink').addEventListener('click', () => {
    navigator.clipboard && navigator.clipboard.writeText(window.location.href).catch(() => {});
  });
  const emojiRow = document.getElementById('panel-emoji-row');
  emojiRow.querySelectorAll('img').forEach(img => {
    img.addEventListener('mouseenter', () => showEmojiReason(display, img.dataset.reasonIdx));
    img.addEventListener('click', () => showEmojiReason(display, img.dataset.reasonIdx));
  });
}

function showEmojiReason(display, idx) {
  const el = document.getElementById('panel-emoji-reason');
  if (!el) return;
  const reasons = display.emoji_reasons || [];
  el.textContent = reasons[idx] || '';
}

function historyRow(dotClass, label, position) {
  if (!position) return `<div class="history-row"><span class="dot ${dotClass}"></span><span class="label">${label}:</span> no data</div>`;
  const emojisHtml = (position.emojis || []).map(e => `<img class="mini-emoji" src="${emojiSrc(emojiToTwemoji(e))}">`).join('');
  return `<div class="history-row"><span class="dot ${dotClass}"></span><span class="label">${label}:</span> ${emojisHtml} ${firstSentence(position.summary)}</div>`;
}

function trendRow(velocity) {
  if (!velocity) return `<div class="history-row"><span class="dot outer"></span><span class="label">Trend:</span> no data</div>`;
  return `<div class="history-row"><span class="dot outer"></span><span class="label">Trend:</span> ${velocity.direction} — ${firstSentence(velocity.summary)}</div>`;
}

// ---------------------------------------------------------------------
// Modal ("Read more") — Bible 6.8
// ---------------------------------------------------------------------

async function openModal(code) {
  const country = countriesByCode[code];
  const countryR = bundleR.countries[code];
  if (!country || !countryR) return;
  if (countryR.schema_version === 4) { return openModalV4(code, country, countryR); }

  const display = countryR.display || {};
  const position = countryR.position || {};
  const velocity = countryR.velocity || null;
  const wind = countryR.wind || null;
  const crystal = countryR.crystal_forecast || {};
  const naive = countryR.naive_forecast || {};

  // Lazily fetch outcomes for this round's statements, if the next round exists.
  let outcomesByCrystalId = {}, outcomesByNaiveId = {}, outcomesByQ = {};
  const nextBundle = await fetchNextBundleLazy();
  if (nextBundle && nextBundle.countries[code] && nextBundle.countries[code].wind) {
    const nextWind = nextBundle.countries[code].wind;
    (nextWind.questions || []).forEach(q => { outcomesByQ[q.id] = q; });
    (nextWind.crystal && nextWind.crystal.statements || []).forEach(s => { outcomesByCrystalId[s.id] = s; });
    (nextWind.naive && nextWind.naive.statements || []).forEach(s => { outcomesByNaiveId[s.id] = s; });
  }

  let html = `<div class="panel-header-row">
    <img class="flag" src="${emojiSrc(country.twemoji)}" alt="">
    <h2>${country.name}</h2>
    <button class="close-btn" id="modal-close-x" aria-label="Close">&times;</button>
  </div>`;
  html += `<div class="headline">${display.headline || ''}</div>`;

  html += `<h3>In plain words</h3>`;
  (display.eli5 || '').split('\n\n').filter(p => p.trim()).forEach(p => { html += `<p>${p}</p>`; });

  if (countryR.questions && countryR.questions.items) {
    const single = !!countryR.single_forecaster;
    html += `<h3>${single ? 'Questions about next week' : 'Eight questions about next week'}</h3>`;
    const nAns = {}, cAns = {};
    ((naive.answers) || []).forEach(a => { nAns[a.id] = a; });
    ((crystal.answers) || []).forEach(a => { cAns[a.id] = a; });
    countryR.questions.items.forEach(q => {
      const n = nAns[q.id] || {}, c = cAns[q.id] || {};
      const differ = !single && n.answer !== c.answer;
      const o = outcomesByQ[q.id];
      let mark = '';
      if (o) mark = o.outcome === 'UNCLEAR' ? ' <span class="pill">unclear</span>' : (o.outcome === c.answer ? ' &#10003;' : ' &#10007;');
      let pills = single
        ? `<span class="pill ans-crystal" title="${(c.reason || '').replace(/"/g, '')}">Forecast: ${c.answer}${q.legacy_probability != null ? ' (' + Math.round(q.legacy_probability * 100) + '%)' : ''}</span>`
        : `<span class="pill ans-crystal" title="${(c.reason || '').replace(/"/g, '')}">Crystal: ${c.answer}</span> <span class="pill ans-plain" title="${(n.reason || '').replace(/"/g, '')}">Plain: ${n.answer}</span>`;
      html += `<div class="statement-row qrow${differ ? ' disagree' : ''}">
        <div class="statement-text">${q.text}</div>
        <div>${pills}${mark}${differ ? ' <span class="pill">Crystal corrected this</span>' : ''}</div>`;
      if (o && o.evidence) html += `<div class="emoji-reason">${o.evidence}</div>`;
      html += `</div>`;
    });
  } else {
    html += `<h3>Five things we are watching</h3>`;
    (crystal.statements || []).forEach(s => { html += statementRow(s, outcomesByCrystalId[s.id]); });
  }

  html += `<h3>Why the Crystal forecast differs from a plain reading</h3><p>${crystal.reasoning || ''}</p>`;

  if (!countryR.single_forecaster) {
    html += `<h3>The plain forecast, for comparison</h3><p>${naive.summary || ''}</p>`;
    if (!countryR.questions) (naive.statements || []).forEach(s => { html += statementRow(s, outcomesByNaiveId[s.id]); });
  }

  html += `<h3>What happened this week</h3><p>${position.summary || ''}</p>`;
  if (position.key_events && position.key_events.length) {
    html += `<ul class="bullets">`;
    position.key_events.forEach(ke => { html += `<li>${ke.date ? ke.date + ': ' : ''}${ke.event}</li>`; });
    html += `</ul>`;
  }

  html += `<h3>What changed since last week</h3>`;
  if (velocity) {
    html += `<p>${velocity.summary}</p>`;
    html += miniList('Rising', velocity.rising);
    html += miniList('Fading', velocity.fading);
    html += miniList('New', velocity.new);
  } else {
    html += `<p>No data yet for this comparison.</p>`;
  }

  if (wind && wind.systematic_error) {
    html += `<h3>Wind: how last week's forecasts missed</h3><p>${wind.systematic_error}</p><p>${wind.correction_hint || ''}</p>`;
  }

  html += `<div class="modal-footer">Model: ${countryR.model || '—'} · Generated: ${countryR.generated_at || '—'}</div>`;
  html += `<button class="btn modal-close" id="modal-close-btn">Close</button>`;

  const modal = document.getElementById('modal');
  modal.innerHTML = html;
  document.getElementById('modal-backdrop').classList.add('open');

  document.getElementById('modal-close-x').addEventListener('click', closeModal);
  document.getElementById('modal-close-btn').addEventListener('click', closeModal);

  // Animate probability bars from zero (Bible 6.14).
  requestAnimationFrame(() => {
    modal.querySelectorAll('.prob-bar-fill').forEach(el => {
      const target = el.dataset.target;
      requestAnimationFrame(() => { el.style.width = target; });
    });
  });
}

function miniList(label, items) {
  if (!items || items.length === 0) return '';
  return `<p><strong>${label}:</strong> ${items.join(', ')}</p>`;
}

function probColor(p) {
  if (p <= 0.5) {
    const t = p / 0.5;
    return lerpColor([248, 113, 113], [251, 191, 36], t);
  } else {
    const t = (p - 0.5) / 0.45;
    return lerpColor([251, 191, 36], [74, 222, 128], clamp(t, 0, 1));
  }
}
function lerpColor(a, b, t) {
  const r = Math.round(a[0] + (b[0] - a[0]) * t);
  const g = Math.round(a[1] + (b[1] - a[1]) * t);
  const bch = Math.round(a[2] + (b[2] - a[2]) * t);
  return `rgb(${r},${g},${bch})`;
}

function statementRow(s, outcomeEntry) {
  const pct = Math.round(s.probability * 100);
  const color = probColor(s.probability);
  let html = `<div class="statement-row">
    <div class="statement-top">
      <div class="prob-bar-track"><div class="prob-bar-fill" data-target="${pct}%" style="background:${color};"></div></div>
      <div class="prob-pct">${pct}%</div>
    </div>
    <div class="statement-top">
      <div class="statement-text">${s.text}</div>
      <span class="pill">${s.domain}</span>
    </div>`;
  if (outcomeEntry && outcomeEntry.outcome !== null && outcomeEntry.outcome !== undefined) {
    const yes = outcomeEntry.outcome === 1;
    html += `<div class="statement-meta">
      <span class="outcome-mark ${yes ? 'yes' : 'no'}">${yes ? '✓ happened' : '✗ did not happen'}</span>
    </div>
    <div class="evidence-text">${outcomeEntry.evidence || ''}</div>`;
  }
  html += `</div>`;
  return html;
}

function closeModal() {
  document.getElementById('modal-backdrop').classList.remove('open');
}

document.getElementById('modal-backdrop').addEventListener('click', (e) => {
  if (e.target.id === 'modal-backdrop') closeModal();
});

// ---------------------------------------------------------------------
// List view (Bible 6.10)
// ---------------------------------------------------------------------

function renderListView() {
  const container = document.getElementById('list-view');
  if (!bundleR) return;
  const byGroup = {};
  countriesMeta.forEach(c => { (byGroup[c.group] = byGroup[c.group] || []).push(c); });

  let html = '';
  Object.keys(groups).forEach(groupKey => {
    const list = byGroup[groupKey];
    if (!list) return;
    html += `<div class="list-group-title">${groups[groupKey]}</div>`;
    list.forEach(c => {
      const countryR = bundleR.countries[c.code];
      if (!countryR) return;
      const display = countryR.display || {};
      const emojisHtml = (display.emojis || []).map(e => `<img src="${emojiSrc(emojiToTwemoji(e))}">`).join('');
      html += `<div class="list-item" data-code="${c.code}">
        <img class="flag" src="${emojiSrc(c.twemoji)}">
        <span class="name">${c.name}</span>
        <span class="emojis">${emojisHtml}</span>
        <span class="headline-text">${display.headline || ''} — ${display.tldr || ''}</span>
      </div>`;
    });
  });
  container.innerHTML = html;
  container.querySelectorAll('.list-item').forEach(item => {
    item.addEventListener('click', () => selectCountry(item.dataset.code));
  });
}
