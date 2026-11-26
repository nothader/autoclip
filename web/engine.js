// DinkCam engine: first-person toy-world renderer for Dink Dunk.
// Deterministic: renderFrame(t) draws the frame at time t (seconds) and returns a JPEG data URL.
import * as THREE from 'three';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { GTAOPass } from 'three/addons/postprocessing/GTAOPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';
import { SMAAPass } from 'three/addons/postprocessing/SMAAPass.js';
import { ShaderPass } from 'three/addons/postprocessing/ShaderPass.js';
import { BokehPass } from 'three/addons/postprocessing/BokehPass.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { initPeople, makePerson, animatePerson, buildRealHands, poseRealHands, phoneScreenTexture } from './person.js';
import { surface } from './textures.js';

const params = new URLSearchParams(location.search);
const STORY = await (await fetch(params.get('story'))).json();
const W = STORY.width, H = STORY.height, V = H > W;     // V = vertical
const U = Math.min(W, H) / 1080;                          // UI scale
const FILM = STORY.look === 'film';                       // v2 look: humans, IBL, AO, bloom, grade, real hands
const RS = FILM ? (STORY.renderScale || 1) : 1;           // 3D render scale (overlays stay full-res)
const RW = Math.round(W * RS), RH = Math.round(H * RS);

const gl = document.getElementById('gl');
const renderer = new THREE.WebGLRenderer({ canvas: gl, antialias: true, preserveDrawingBuffer: true });
renderer.setPixelRatio(1); renderer.setSize(RW, RH, false);
renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = FILM ? 0.95 : 1.05;
if (FILM) { renderer.shadowMap.type = THREE.PCFSoftShadowMap; }
renderer.outputColorSpace = THREE.SRGBColorSpace;
const out = document.getElementById('out'); out.width = W; out.height = H;
const ctx = out.getContext('2d');

// ───────── helpers ─────────
function rng(seed) { let a = (seed * 2654435761) >>> 0; return () => { a |= 0; a = a + 0x6D2B79F5 | 0; let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
const ease = x => x < 0 ? 0 : x > 1 ? 1 : 1 - Math.pow(1 - x, 3);
const back = x => { x = Math.min(Math.max(x, 0), 1); const c = 1.9; return 1 + (c + 1) * Math.pow(x - 1, 3) + c * Math.pow(x - 1, 2); };
const lerp = (a, b, k) => a + (b - a) * k;
const V3 = a => new THREE.Vector3(a[0], a[1], a[2]);
const D = Math.PI / 180;
const scl = s => Array.isArray(s) ? s : [s, s, s];

const matCache = new Map();
const ROUGH = { glossy: 0.22, metal: 0.3, matte: 0.78, skin: 0.55, fabric: 0.92, hair: 0.62, plastic: 0.4, wood: 0.6, chrome: 0.1, glass: 0.04, paint: 0.7, rubber: 0.9, screen: 0.3, emit: 0.5, leather: 0.5, ceramic: 0.18 };
function mat(color, kind = 'matte', opacity = 1, tex = null) {
  const key = color + kind + opacity + (tex ? tex.kind + tex.rep : '');
  if (matCache.has(key)) return matCache.get(key);
  let m;
  if (kind === 'glow') m = new THREE.MeshBasicMaterial({ color, toneMapped: false, transparent: opacity < 1, opacity });
  else {
    const metal = kind === 'metal' ? 0.85 : kind === 'chrome' ? 1.0 : 0;
    m = new THREE.MeshStandardMaterial({ color, roughness: ROUGH[kind] ?? 0.78, metalness: metal, transparent: opacity < 1 || kind === 'glass',
      opacity: kind === 'glass' ? Math.min(opacity, 0.28) : opacity, side: THREE.DoubleSide });
    if (kind === 'glass') { m.depthWrite = false; m.envMapIntensity = 2.0; }
    if (kind === 'screen' || kind === 'emit') { m.emissive = new THREE.Color(color); m.emissiveIntensity = kind === 'emit' ? 2.2 : 0.9; m.color.set('#111111'); }
    if (kind === 'skin' && FILM) { m.emissive = new THREE.Color(color).multiplyScalar(0.06); }   // cheap subsurface warmth
    if (tex) {
      const sf = surface(tex.kind, color);
      m.map = sf.map.clone(); m.map.needsUpdate = true; m.map.repeat.set(tex.rep[0] / sf.tile, tex.rep[1] / sf.tile);
      m.bumpMap = sf.bump.clone(); m.bumpMap.needsUpdate = true; m.bumpMap.repeat.copy(m.map.repeat); m.bumpScale = 1.2;
      m.color.set('#ffffff');
    }
  }
  matCache.set(key, m); return m;
}
const emojiTexCache = new Map();
function emojiTexture(text) {
  if (emojiTexCache.has(text)) return emojiTexCache.get(text);
  const cv = document.createElement('canvas'); cv.width = cv.height = 256;
  const c2 = cv.getContext('2d'); c2.font = '200px "Noto Color Emoji"'; c2.textAlign = 'center'; c2.textBaseline = 'middle'; c2.fillText(text || '⭐', 128, 140);
  const tx = new THREE.CanvasTexture(cv); tx.colorSpace = THREE.SRGBColorSpace; emojiTexCache.set(text, tx); return tx;
}
// flat text panel (signs, store names, menus, screens with words)
function textTexture(o) {
  const lines = String(o.text || '').split('\n'); const ar = (o.scale?.[0] || 1) / (o.scale?.[1] || 1);
  const Wc = 1024, Hc = Math.max(64, Math.round(1024 / ar));
  const cv = document.createElement('canvas'); cv.width = Wc; cv.height = Hc; const c = cv.getContext('2d');
  c.fillStyle = o.bg || '#ffffff'; c.fillRect(0, 0, Wc, Hc);
  if (o.border) { c.strokeStyle = o.border; c.lineWidth = Hc * 0.06; c.strokeRect(0, 0, Wc, Hc); }
  const fs = Math.min(Hc / (lines.length * 1.25), (o.fontScale || 1) * Wc / Math.max(...lines.map(l => l.length), 1) * 1.6);
  c.fillStyle = o.fg || '#111111'; c.textAlign = 'center'; c.textBaseline = 'middle';
  c.font = `${o.weight || 900} ${fs}px ${o.font || '"Inter", "Noto Color Emoji", sans-serif'}`;
  lines.forEach((l, i) => c.fillText(l, Wc / 2, Hc / 2 + (i - (lines.length - 1) / 2) * fs * 1.2));
  const tx = new THREE.CanvasTexture(cv); tx.colorSpace = THREE.SRGBColorSpace; tx.anisotropy = 4; return tx;
}
const geoCache = new Map();
function geo(key, make) { if (!geoCache.has(key)) geoCache.set(key, make()); return geoCache.get(key); }

function mesh(g, m, shadow = true) { const x = new THREE.Mesh(g, m); x.castShadow = shadow; x.receiveShadow = true; return x; }

// ───────── primitives ─────────
function primitive(o) {
  const s = scl(o.scale ?? 1), c = o.color || '#dddddd', mk = o.material || 'matte', op = o.opacity ?? 1;
  const texOpt = o.tex ? { kind: o.tex, rep: o.texRep || (o.kind === 'plane' ? [s[0], s[1]] : [Math.max(s[0], s[2]), Math.max(s[1], Math.min(s[0], s[2]))]) } : null;
  const M = mat(c, mk, op, texOpt);
  let obj;
  switch (o.kind) {
    case 'box': {
      const r = Math.min(s[0], s[1], s[2]) * 0.18;
      obj = mesh(geo(`rb${s}`, () => new RoundedBoxGeometry(s[0], s[1], s[2], 3, Math.min(r, 0.25))), M); break;
    }
    case 'sphere': obj = mesh(geo('sph', () => new THREE.SphereGeometry(1, 32, 20)), M); obj.scale.set(s[0], s[1], s[2]); break;
    case 'cylinder': obj = mesh(geo('cyl', () => new THREE.CylinderGeometry(0.5, 0.5, 1, 28)), M); obj.scale.set(s[0], s[1], s[2]); break;
    case 'cone': obj = mesh(geo('cone', () => new THREE.ConeGeometry(0.5, 1, 28)), M); obj.scale.set(s[0], s[1], s[2]); break;
    case 'capsule': obj = mesh(geo('cap', () => new THREE.CapsuleGeometry(0.5, 0.5, 8, 20)), M); obj.scale.set(s[0], s[1], s[2]); break;
    case 'torus': obj = mesh(geo('tor', () => new THREE.TorusGeometry(0.5, 0.12, 14, 40)), M); obj.scale.set(s[0], s[1], s[2]); break;
    case 'plane': obj = mesh(geo('pl', () => new THREE.PlaneGeometry(1, 1)), M, false); obj.scale.set(s[0], s[1], 1); break;
    case 'rock': obj = mesh(geo('rock', () => new THREE.DodecahedronGeometry(0.5, 0)), mat(c, 'matte')); obj.scale.set(s[0], s[1] * 0.7, s[2]); break;
    case 'tree': {
      obj = new THREE.Group();
      const tr = mesh(geo('cyl', () => new THREE.CylinderGeometry(0.5, 0.5, 1, 28)), mat('#7a5232')); tr.scale.set(0.18, 0.8, 0.18); tr.position.y = 0.4; obj.add(tr);
      for (let i = 0; i < 3; i++) { const cn = mesh(geo('cone', () => new THREE.ConeGeometry(0.5, 1, 28)), M); cn.scale.set(1.3 - i * 0.32, 0.9, 1.3 - i * 0.32); cn.position.y = 1.0 + i * 0.5; obj.add(cn); }
      obj.scale.set(s[0], s[1], s[2]); break;
    }
    case 'blob_tree': {   // round cartoon tree
      obj = new THREE.Group();
      const tr = mesh(geo('cyl', () => new THREE.CylinderGeometry(0.5, 0.5, 1, 28)), mat('#80593a')); tr.scale.set(0.2, 1.0, 0.2); tr.position.y = 0.5; obj.add(tr);
      const top = mesh(geo('sph', () => new THREE.SphereGeometry(1, 32, 20)), M); top.scale.set(0.75, 0.7, 0.75); top.position.y = 1.4; obj.add(top);
      obj.scale.set(s[0], s[1], s[2]); break;
    }
    case 'flame': {
      obj = new THREE.Group();
      const a = mesh(geo('cone', () => new THREE.ConeGeometry(0.5, 1, 28)), mat('#ff8c2b', 'glow')); a.scale.set(0.5, 1, 0.5); a.position.y = 0.5;
      const b = mesh(geo('cone', () => new THREE.ConeGeometry(0.5, 1, 28)), mat('#ffe066', 'glow')); b.scale.set(0.28, 0.6, 0.28); b.position.y = 0.32;
      obj.add(a, b); obj.scale.set(s[0], s[1], s[2]); obj.userData.flicker = true; break;
    }
    case 'particles': obj = mesh(geo('sph8', () => new THREE.SphereGeometry(1, 8, 6)), M, false); obj.scale.set(s[0], s[0], s[0]); break;
    case 'ring': obj = mesh(geo('ring', () => new THREE.RingGeometry(0.42, 0.5, 48)), M, false); obj.scale.set(s[0], s[1], 1); break;
    case 'bean': obj = bean(o); break;
    case 'person': obj = makePerson(o); break;
    case 'text': {   // sign / label panel with real words
      const m2 = new THREE.MeshStandardMaterial({ map: textTexture(o), roughness: 0.6, side: THREE.DoubleSide, transparent: !!o.transparent });
      if (o.lit) { m2.emissive = new THREE.Color('#ffffff'); m2.emissiveMap = m2.map; m2.emissiveIntensity = o.lit === true ? 0.8 : o.lit; }
      obj = mesh(geo('pl', () => new THREE.PlaneGeometry(1, 1)), m2, false); obj.scale.set(s[0], s[1], 1); break;
    }
    case 'screen': {   // phone/TV/laptop UI (same spec as the phone screen)
      const tx = phoneScreenTexture(o.screen || {});
      const m2 = new THREE.MeshStandardMaterial({ map: tx, emissive: new THREE.Color('#ffffff'), emissiveMap: tx, emissiveIntensity: 0.85, roughness: 0.3 });
      obj = mesh(geo('pl', () => new THREE.PlaneGeometry(1, 1)), m2, false); obj.scale.set(s[0], s[1], 1); break;
    }
    case 'lamp': {   // real light source (point light + glowing bulb). Keep to 1-3 per shot.
      obj = new THREE.Group(); const L = new THREE.PointLight(c, o.intensity ?? 6, o.range ?? 8, 2); obj.add(L);
      if (!o.hidden) { const bulb = mesh(geo('sph', () => new THREE.SphereGeometry(1, 32, 20)), mat(c, 'glow'), false); bulb.scale.setScalar(s[0] * 0.08); obj.add(bulb); }
      break;
    }
    case 'spot': {   // spotlight (stage, interrogation, flashlight)
      obj = new THREE.Group(); const L = new THREE.SpotLight(c, o.intensity ?? 30, o.range ?? 20, (o.angle ?? 25) * D, 0.4, 1.6);
      L.castShadow = !!o.shadow; const tg = new THREE.Object3D(); const to = o.target || [0, 0, -3];
      tg.position.set(to[0] - (o.at?.[0] || 0), to[1] - (o.at?.[1] || 0), to[2] - (o.at?.[2] || 0)); obj.add(L, tg); L.target = tg; break;
    }
    case 'emoji': obj = emojiSprite(o); break;
    default: obj = new THREE.Group();
  }
  return obj;
}

// 3D emoji/text billboard (props drawn with the colour-emoji font: 🐺🍕👑🔥 …)
function emojiSprite(o) {
  const tx = emojiTexture(o.text || '⭐');
  const sp = new THREE.Sprite(new THREE.SpriteMaterial({ map: tx, transparent: true }));
  const s = scl(o.scale ?? 1); sp.scale.set(s[0], s[0], 1); return sp;
}

// ───────── bean people (googly-eyed jelly beans) ─────────
const SKIN_BEANS = true;
function bean(o) {
  const g = new THREE.Group();
  const c = o.color || '#ff8fab', size = o.size || 1;
  const body = mesh(geo('cap', () => new THREE.CapsuleGeometry(0.5, 0.5, 8, 20)), mat(c, 'glossy'));
  body.scale.set(0.62, 0.78, 0.55); body.position.y = 0.62; g.add(body);
  if (o.color2) { const belly = mesh(geo('sph', () => new THREE.SphereGeometry(1, 32, 20)), mat(o.color2, 'glossy')); belly.scale.set(0.22, 0.26, 0.08); belly.position.set(0, 0.48, 0.25); g.add(belly); }
  const face = new THREE.Group(); face.position.set(0, 0.86, 0.255); g.add(face);
  const eyeW = mat('#ffffff', 'glossy'), eyeB = mat('#111111', 'glossy');
  const pupils = [];
  for (const sx of [-1, 1]) {
    const e = mesh(geo('sph', () => new THREE.SphereGeometry(1, 32, 20)), eyeW, false); e.scale.set(0.1, 0.12, 0.06); e.position.set(sx * 0.1, 0.02, 0); face.add(e);
    const p = mesh(geo('sph', () => new THREE.SphereGeometry(1, 32, 20)), eyeB, false); p.scale.set(0.045, 0.05, 0.03); p.position.set(sx * 0.1, 0.0, 0.05); face.add(p); pupils.push(p);
  }
  const brows = [];
  for (const sx of [-1, 1]) { const b = mesh(geo(`rb${[0.11, 0.025, 0.02]}`, () => new RoundedBoxGeometry(0.11, 0.025, 0.02, 2, 0.01)), mat('#2b2b2b'), false); b.position.set(sx * 0.1, 0.16, 0.02); face.add(b); brows.push(b); }
  const mouthSmile = mesh(geo('smile', () => new THREE.TorusGeometry(0.07, 0.016, 8, 20, Math.PI)), mat('#3a1a1a'), false);
  mouthSmile.rotation.z = Math.PI; mouthSmile.position.set(0, -0.11, 0.02);
  const mouthO = mesh(geo('sph', () => new THREE.SphereGeometry(1, 32, 20)), mat('#3a1a1a'), false); mouthO.scale.set(0.05, 0.06, 0.02); mouthO.position.set(0, -0.13, 0.02);
  face.add(mouthSmile, mouthO);
  for (const sx of [-1, 1]) { const bl = mesh(geo('sph', () => new THREE.SphereGeometry(1, 32, 20)), mat('#ff6b8b', 'matte', 0.55), false); bl.scale.set(0.04, 0.025, 0.01); bl.position.set(sx * 0.19, -0.07, -0.005); face.add(bl); }
  const arms = [];
  for (const sx of [-1, 1]) {
    const pivot = new THREE.Group(); pivot.position.set(sx * 0.3, 0.68, 0); g.add(pivot);
    const a = mesh(geo('cap', () => new THREE.CapsuleGeometry(0.5, 0.5, 8, 20)), mat(c, 'glossy')); a.scale.set(0.1, 0.28, 0.1); a.position.set(sx * 0.04, -0.17, 0); pivot.add(a);
    arms.push(pivot);
  }
  for (const sx of [-1, 1]) { const f = mesh(geo('sph', () => new THREE.SphereGeometry(1, 32, 20)), mat(o.shoe || '#333333', 'glossy')); f.scale.set(0.1, 0.06, 0.14); f.position.set(sx * 0.13, 0.04, 0.05); g.add(f); }
  hat(g, o.hat, o.hatColor);
  g.userData.bean = { pupils, brows, mouthSmile, mouthO, arms, body, face, expr: o.expr || 'smile', act: o.act || 'idle', seed: o.seed || 1, talk: o.talk || [] };
  g.scale.setScalar(size * 1.0);
  return g;
}
function hat(g, kind, color) {
  if (!kind) return;
  const top = 1.16;
  const add = (k, s, p, c, m = 'glossy', r) => { const x = primitive({ kind: k, scale: s, color: c, material: m }); x.position.set(...p); if (r) x.rotation.set(r[0] * D, r[1] * D, r[2] * D); g.add(x); return x; };
  if (kind === 'cap') { add('sphere', [0.27, 0.16, 0.27], [0, top - 0.06, 0], color || '#e03131'); add('cylinder', [0.3, 0.02, 0.22], [0, top - 0.08, 0.2], color || '#e03131'); }
  if (kind === 'crown') { add('cylinder', [0.34, 0.12, 0.34], [0, top, 0], '#fcc419', 'metal'); for (let i = 0; i < 5; i++) { const a = i / 5 * Math.PI * 2; add('cone', [0.07, 0.12, 0.07], [Math.sin(a) * 0.15, top + 0.11, Math.cos(a) * 0.15], '#fcc419', 'metal'); } }
  if (kind === 'chef') { add('cylinder', [0.3, 0.2, 0.3], [0, top + 0.02, 0], '#ffffff'); add('sphere', [0.2, 0.13, 0.2], [0, top + 0.16, 0], '#ffffff'); }
  if (kind === 'party') { add('cone', [0.2, 0.32, 0.2], [0.04, top + 0.12, 0], color || '#845ef7', 'glossy', [0, 0, -12]); add('sphere', 0.04, [0.08, top + 0.29, 0], '#ffd43b'); }
  if (kind === 'hair') { for (let i = 0; i < 3; i++) add('sphere', 0.07, [(i - 1) * 0.07, top - 0.02, 0.05], color || '#3b2a1a'); }
  if (kind === 'bun') { add('sphere', 0.11, [0, top + 0.02, -0.05], color || '#ced4da'); }
  if (kind === 'helmet') { add('sphere', [0.34, 0.24, 0.34], [0, top - 0.06, 0], color || '#fab005'); }
  if (kind === 'tophat') { add('cylinder', [0.38, 0.02, 0.38], [0, top - 0.06, 0], '#111'); add('cylinder', [0.24, 0.26, 0.24], [0, top + 0.08, 0], '#111'); }
  if (kind === 'ears') { for (const sx of [-1, 1]) add('cone', [0.1, 0.16, 0.06], [sx * 0.16, top, 0], color || '#868e96', 'matte', [0, 0, -sx * 15]); }
}
const EXPR = {   // brow angle, brow y, mouth: smile|frown|o|flat, pupil scale
  smile: [0, 0.16, 'smile', 1], happy: [-8, 0.18, 'smile', 1], shock: [0, 0.22, 'o', 0.7], sad: [18, 0.15, 'frown', 1],
  angry: [-22, 0.14, 'frown', 1], smirk: [10, 0.16, 'smile', 1], neutral: [0, 0.16, 'flat', 1], love: [0, 0.18, 'smile', 1.2], scared: [20, 0.2, 'o', 0.6],
};
function animateBean(g, t) {
  const b = g.userData.bean; const r = rng(b.seed)(); const ph = r * 6.28;
  const e = EXPR[b.expr] || EXPR.smile;
  b.brows.forEach((br, i) => { br.rotation.z = (i ? -1 : 1) * e[0] * D; br.position.y = e[1]; });
  let talking = b.talk.some(([a, d]) => t >= a && t <= a + d);
  b.mouthSmile.visible = e[2] === 'smile' || e[2] === 'frown' || e[2] === 'flat';
  b.mouthSmile.rotation.z = e[2] === 'frown' ? 0 : Math.PI; b.mouthSmile.scale.y = e[2] === 'flat' ? 0.15 : 1;
  b.mouthO.visible = e[2] === 'o' || talking;
  if (talking) { b.mouthSmile.visible = false; b.mouthO.scale.y = 0.03 + 0.04 * Math.abs(Math.sin(t * 18 + ph)); }
  b.pupils.forEach((p, i) => { p.scale.setScalar(0.045 * e[3]); p.position.x = (i ? 1 : -1) * 0.1 + Math.sin(t * 2.3 + ph) * 0.02; p.position.y = Math.cos(t * 3.1 + ph) * 0.015; });
  const [L, R] = b.arms; let y = 0, rz = 0;
  switch (b.act) {
    case 'idle': y = Math.sin(t * 2 + ph) * 0.015; L.rotation.z = -0.15; R.rotation.z = 0.15; break;
    case 'wave': L.rotation.z = -0.15; R.rotation.z = 2.4 + Math.sin(t * 10) * 0.4; break;
    case 'cheer': y = Math.abs(Math.sin(t * 6 + ph)) * 0.12; L.rotation.z = -2.6 + Math.sin(t * 12) * 0.2; R.rotation.z = 2.6 - Math.sin(t * 12) * 0.2; break;
    case 'point': L.rotation.z = -0.15; R.rotation.x = -1.5; R.rotation.z = 0.1; break;
    case 'scared': rz = Math.sin(t * 40) * 0.03; L.rotation.z = -2.2; R.rotation.z = 2.2; L.rotation.x = R.rotation.x = -0.6; break;
    case 'dance': y = Math.abs(Math.sin(t * 5 + ph)) * 0.1; rz = Math.sin(t * 5 + ph) * 0.18; L.rotation.z = -1.6 + Math.sin(t * 5) * 0.8; R.rotation.z = 1.6 + Math.sin(t * 5) * 0.8; break;
    case 'walk': y = Math.abs(Math.sin(t * 6 + ph)) * 0.04; L.rotation.x = Math.sin(t * 6) * 0.5; R.rotation.x = -Math.sin(t * 6) * 0.5; break;
    case 'run': y = Math.abs(Math.sin(t * 12 + ph)) * 0.08; L.rotation.x = Math.sin(t * 12) * 1.0; R.rotation.x = -Math.sin(t * 12) * 1.0; break;
    case 'jump': y = Math.abs(Math.sin(t * 4 + ph)) * 0.5; L.rotation.z = -2.4; R.rotation.z = 2.4; break;
    case 'facepalm': R.rotation.x = -2.6; R.rotation.z = -0.3; L.rotation.z = -0.15; break;
    case 'shrug': L.rotation.z = -1.1; R.rotation.z = 1.1; y = Math.abs(Math.sin(t * 3)) * 0.03; break;
    case 'sit': y = -0.18; L.rotation.x = R.rotation.x = -0.8; break;
    case 'lie': g.rotation.x = -Math.PI / 2; break;
  }
  b.body.position.y = 0.62 + y; b.face.position.y = 0.86 + y; b.arms.forEach(a => a.position.y = 0.68 + y);
  g.rotation.z = rz;
}

// ───────── first-person hands (mittens) ─────────
const handRig = new THREE.Group();
function buildHands(skin, sleeve) {
  handRig.clear();
  const parts = [];
  for (const sx of [-1, 1]) {
    const arm = new THREE.Group();
    const sl = mesh(geo('cap', () => new THREE.CapsuleGeometry(0.5, 0.5, 8, 20)), mat(sleeve, 'matte')); sl.scale.set(0.11, 0.32, 0.11); sl.rotation.x = Math.PI / 2; sl.position.z = 0.2;
    const hd = mesh(geo('sph', () => new THREE.SphereGeometry(1, 32, 20)), mat(skin, 'matte')); hd.scale.set(0.075, 0.06, 0.085);
    const th = mesh(geo('sph', () => new THREE.SphereGeometry(1, 32, 20)), mat(skin, 'matte')); th.scale.setScalar(0.028); th.position.set(-sx * 0.065, 0.02, -0.02);
    const fi = mesh(geo('cap', () => new THREE.CapsuleGeometry(0.5, 0.5, 8, 20)), mat(skin, 'matte')); fi.scale.set(0.035, 0.07, 0.035); fi.rotation.x = -Math.PI / 2; fi.position.set(0, 0.01, -0.09); fi.visible = false;
    arm.add(sl, hd, th, fi); arm.scale.setScalar(0.72); handRig.add(arm); parts.push({ arm, fi });
  }
  handRig.userData.parts = parts;
}
const HAND = {   // [x, y, z, rx, ry, rz] per hand (camera space), right then left
  idle: [[0.26, -0.36, -0.55, 0.3, 0, 0], [-0.26, -0.36, -0.55, 0.3, 0, 0]],
  point: [[0.16, -0.18, -0.6, 0, 0, 0], [-0.3, -0.42, -0.55, 0.4, 0, 0]],
  reach: [[0.14, -0.16, -0.62, 0, 0, 0], [-0.14, -0.16, -0.62, 0, 0, 0]],
  hold: [[0.1, -0.22, -0.5, 0.2, 0, 0], [-0.1, -0.24, -0.5, 0.2, 0, 0]],
  wave: [[0.24, -0.02, -0.55, -0.4, 0, -0.5], [-0.3, -0.42, -0.55, 0.4, 0, 0]],
  shrug: [[0.4, -0.26, -0.5, 0, 0, -0.8], [-0.4, -0.26, -0.5, 0, 0, 0.8]],
  facepalm: [[0.03, 0.0, -0.22, -0.6, 0, 0], [-0.3, -0.42, -0.55, 0.4, 0, 0]],
  shield: [[0.12, -0.05, -0.42, -0.4, 0, 0.3], [-0.12, -0.05, -0.42, -0.4, 0, -0.3]],
  run: [[0.28, -0.34, -0.5, 0.3, 0, 0], [-0.28, -0.34, -0.5, 0.3, 0, 0]],
  cheer: [[0.3, 0.12, -0.6, -0.6, 0, -0.3], [-0.3, 0.12, -0.6, -0.6, 0, 0.3]],
  none: null,
};
let heldProp = null;
let phoneObj = null, phoneSpec = null;
function poseHands(pose, t, hold, screen) {
  if (handRig.userData.real) {
    poseRealHands(handRig, pose, t);
    if (heldProp) { handRig.remove(heldProp); heldProp = null; }
    if (phoneObj && phoneObj.parent) phoneObj.parent.remove(phoneObj);
    if (pose === 'phone') {   // phone in the right hand, screen toward you
      const key = JSON.stringify(screen || {});
      if (phoneSpec?.key !== key) {
        phoneSpec = { key }; phoneObj = new THREE.Group();
        const body = mesh(geo('phbody', () => new RoundedBoxGeometry(0.078, 0.012, 0.16, 4, 0.006)), mat('#1b1b1f', 'glossy')); body.position.y = -0.024; phoneObj.add(body);
        const sc = new THREE.Mesh(geo('pl', () => new THREE.PlaneGeometry(1, 1)), new THREE.MeshBasicMaterial({ map: phoneScreenTexture(screen || { app: 'Messages' }), toneMapped: false }));
        sc.scale.set(0.071, 0.148, 1); sc.rotation.set(Math.PI / 2, 0, Math.PI); sc.position.y = -0.0312; phoneObj.add(sc);
        phoneObj.position.set(0.0, 0, -0.07);
      }
      handRig.userData.parts[0].palm.add(phoneObj);
    }
    if (hold) {
      heldProp = new THREE.Group(); for (const o of hold) heldProp.add(place(o));
      heldProp.position.set(0, -0.15, -0.5); handRig.add(heldProp);
    }
    return;
  }
  const P = HAND[pose] || HAND.idle;
  handRig.visible = !!P; if (!P) return;
  handRig.userData.parts.forEach((p, i) => {
    const q = P[i]; let bob = Math.sin(t * 2.2 + i) * 0.006;
    if (pose === 'run') bob = Math.sin(t * 12 + i * Math.PI) * 0.06;
    if (pose === 'wave' && i === 0) p.arm.rotation.z = q[5] + Math.sin(t * 12) * 0.35; else p.arm.rotation.z = q[5];
    if (pose === 'cheer') bob = Math.abs(Math.sin(t * 8 + i)) * 0.05;
    p.arm.position.set(q[0] * 1.1, q[1] * 1.05 + bob - 0.03, q[2] * 1.25); p.arm.rotation.x = q[3]; p.arm.rotation.y = q[4];
    p.fi.visible = pose === 'point' && i === 0;
  });
  if (heldProp) { handRig.remove(heldProp); heldProp = null; }
  if (hold) {
    heldProp = new THREE.Group();
    for (const o of hold) heldProp.add(place(o));
    heldProp.position.set(0, -0.15, -0.5); handRig.add(heldProp);
  }
}

// ───────── scene / beats ─────────
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(V ? 62 : 50, W / H, 0.03, 600);
camera.add(handRig); scene.add(camera);
const hemi = new THREE.HemisphereLight('#ffffff', '#8a7a6a', 1.3); scene.add(hemi);
const sun = new THREE.DirectionalLight('#fff3df', 2.4); sun.castShadow = true; sun.shadow.mapSize.set(1536, 1536);
sun.shadow.camera.left = sun.shadow.camera.bottom = -14; sun.shadow.camera.right = sun.shadow.camera.top = 14; sun.shadow.bias = -0.0008; sun.shadow.radius = 4;
scene.add(sun, sun.target);
const fill = new THREE.DirectionalLight('#ffffff', 0); scene.add(fill, fill.target);   // soft key from the camera side (faces read)
initPeople({ mat, geo, mesh, emojiTexture, rng });
let composer = null, gtao = null, bloom = null, grade = null, bokeh = null;
if (FILM) {
  const pm = new THREE.PMREMGenerator(renderer);
  scene.environment = pm.fromScene(new RoomEnvironment(), 0.04).texture;
  sun.shadow.mapSize.set(2048, 2048); sun.shadow.radius = 5; sun.shadow.normalBias = 0.02; sun.shadow.bias = -0.0004;
  const MSAA = STORY.msaa ?? 0;   // MSAA is ~2x slower on the CPU renderer; SMAA after tone mapping is the default
  const rt = new THREE.WebGLRenderTarget(RW, RH, { type: THREE.HalfFloatType, samples: MSAA });
  composer = new EffectComposer(renderer, rt); composer.setPixelRatio(1); composer.setSize(RW, RH);
  composer.addPass(new RenderPass(scene, camera));
  if (STORY.ao !== false) {
    gtao = new GTAOPass(scene, camera, Math.round(RW / 2), Math.round(RH / 2));
    gtao.updateGtaoMaterial({ radius: 0.45, distanceExponent: 1.6, thickness: 1.5, scale: 1.0, samples: STORY.aoSamples ?? 8 });
    gtao.updatePdMaterial({ lumaPhi: 10, depthPhi: 2, normalPhi: 3, radius: 6, rings: 2, samples: STORY.aoDenoise ?? 6 });
    gtao.blendIntensity = 0.9; composer.addPass(gtao);
  }
  bokeh = new BokehPass(scene, camera, { focus: 3, aperture: 0.0012, maxblur: 0.006 }); bokeh.enabled = false; composer.addPass(bokeh);
  bloom = new UnrealBloomPass(new THREE.Vector2(RW / 2, RH / 2), 0.28, 0.5, 0.92); composer.addPass(bloom);
  composer.addPass(new OutputPass());
  if (!MSAA) composer.addPass(new SMAAPass(RW, RH));
  grade = new ShaderPass({
    uniforms: { tDiffuse: { value: null }, time: { value: 0 }, sat: { value: 1.12 }, contrast: { value: 1.06 }, grain: { value: 0.035 }, vig: { value: 0.55 }, ca: { value: 0.0016 },
      tint: { value: new THREE.Vector3(1.02, 1.0, 0.97) }, lift: { value: new THREE.Vector3(0.012, 0.01, 0.02) }, res: { value: new THREE.Vector2(RW, RH) }, mono: { value: 0 } },
    vertexShader: 'varying vec2 vUv; void main(){ vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }',
    fragmentShader: `uniform sampler2D tDiffuse; uniform float time, sat, contrast, grain, vig, ca, mono; uniform vec3 tint, lift; uniform vec2 res; varying vec2 vUv;
      float hash(vec2 p){ return fract(sin(dot(p, vec2(12.9898, 78.233))) * 43758.5453); }
      void main(){ vec2 d = vUv - 0.5; vec3 c;
        c.r = texture2D(tDiffuse, vUv + d * ca).r; c.g = texture2D(tDiffuse, vUv).g; c.b = texture2D(tDiffuse, vUv - d * ca).b;
        float l = dot(c, vec3(0.2126, 0.7152, 0.0722)); c = mix(vec3(l), c, sat * (1.0 - mono));
        c = (c - 0.5) * contrast + 0.5; c = c * tint + lift * (1.0 - c);
        c *= 1.0 - vig * dot(d * vec2(0.8, 1.0), d * vec2(0.8, 1.0)) * 1.4;
        c += (hash(floor(vUv * res) + fract(time * 7.13) * 91.7) - 0.5) * grain;
        gl_FragColor = vec4(clamp(c, 0.0, 1.0), 1.0); }`,
  });
  composer.addPass(grade);
}
let world = new THREE.Group(); scene.add(world);
const extra = new THREE.Group(); scene.add(extra);

function skyTexture(top, bot) {
  const cv = document.createElement('canvas'); cv.width = 4; cv.height = 512; const c2 = cv.getContext('2d');
  const gr = c2.createLinearGradient(0, 0, 0, 512); gr.addColorStop(0, top); gr.addColorStop(1, bot); c2.fillStyle = gr; c2.fillRect(0, 0, 4, 512);
  const tx = new THREE.CanvasTexture(cv); tx.colorSpace = THREE.SRGBColorSpace; return tx;
}

function place(o) {
  const n = o.count || 1, R = rng(o.seed || 1), sp = o.spread || [0, 0, 0];
  const make = (i) => {
    const m = primitive(o);
    const at = o.at || [0, 0, 0];
    const p = n > 1 ? [at[0] + (R() - 0.5) * sp[0], at[1] + (R() - 0.5) * sp[1], at[2] + (R() - 0.5) * sp[2]] : at;
    m.position.set(p[0], p[1], p[2]);
    const rot = o.rotate || [0, 0, 0];
    m.rotation.set(rot[0] * D, (rot[1] + (n > 1 && o.kind === 'bean' ? 0 : 0)) * D, rot[2] * D);
    m.userData.base = { p: m.position.clone(), r: m.rotation.clone(), s: m.scale.clone(), anim: o.animate || [], i, ph: R() * 6.28 };
    if (o.cast === false) m.traverse(c => { c.castShadow = false; });
    if (o.kind === 'bean' && n > 1) { m.userData.bean.seed = (o.seed || 1) * 31 + i; }
    return m;
  };
  if (n === 1) return make(0);
  const g = new THREE.Group(); for (let i = 0; i < n; i++) g.add(make(i)); g.userData.multi = true; return g;
}

function animateObj(m, t, dur) {
  const b = m.userData.base;
  if (b) {
    m.position.copy(b.p); m.rotation.copy(b.r); m.scale.copy(b.s);
    for (const a of b.anim) {
      const sp = a.speed ?? 1, am = a.amount ?? 0.3, k = ease(t / Math.max(dur, 0.01));
      if (a.type === 'spin') m.rotation[a.axis || 'y'] += t * sp;
      if (a.type === 'bob') m.position.y += Math.sin(t * sp * 3 + b.ph) * am;
      if (a.type === 'wobble') m.rotation[a.axis || 'z'] += Math.sin(t * sp * 3 + b.ph) * am;
      if (a.type === 'pulse') m.scale.multiplyScalar(1 + Math.sin(t * sp * 4 + b.ph) * am * 0.5);
      if (a.type === 'move' && a.to) { const d = a.delay || 0, kk = ease((t - d) / Math.max((a.dur || dur) - d, 0.01));         m.position.set(a.rel ? b.p.x + a.to[0] * kk : lerp(b.p.x, a.to[0], kk), a.rel ? b.p.y + a.to[1] * kk : lerp(b.p.y, a.to[1], kk), a.rel ? b.p.z + a.to[2] * kk : lerp(b.p.z, a.to[2], kk)); }
      if (a.type === 'fall') { const tt = Math.max(0, t - (a.delay || 0)); m.position.y = Math.max(a.floor ?? 0, b.p.y - 4.9 * tt * tt); }
      if (a.type === 'drop') { const tt = Math.max(0, t - (a.delay || 0)); const yy = b.p.y - ((tt * (sp * 2)) % (b.p.y - (a.floor ?? 0) + 0.001)); m.position.y = yy; m.rotation.x += tt * 3; }
      if (a.type === 'grow') m.scale.multiplyScalar(lerp(1, am, k));
      if (a.type === 'pop') m.scale.multiplyScalar(back((t - (a.delay || 0)) / 0.35));
      if (a.type === 'hop') m.position.y += Math.abs(Math.sin(t * sp * 5 + b.ph)) * am;
      if (a.type === 'orbit') { m.position.x = b.p.x + Math.cos(t * sp + b.ph) * am; m.position.z = b.p.z + Math.sin(t * sp + b.ph) * am; }
    }
  }
  if (m.userData.flicker) m.scale.y = m.userData.base.s.y * (1 + Math.sin(t * 23) * 0.08 + Math.sin(t * 37) * 0.05);
  if (m.userData.bean) animateBean(m, t);
  if (m.userData.person) animatePerson(m, t, camera);
  if (m.userData.multi) m.children.forEach(c => animateObj(c, t, dur));
}

let built = -1;
function buildBeat(i) {
  const b = STORY.beats[i];
  scene.remove(world); world = new THREE.Group(); scene.add(world);
  const s = b.set || {};
  scene.background = skyTexture(...(s.sky || ['#8ec5ff', '#e6f4ff']));
  scene.fog = s.fog ? new THREE.Fog(s.fog[0], s.fog[1], s.fog[2]) : null;
  hemi.intensity = (s.ambient ?? 1.3) * (FILM ? 0.6 : 1); hemi.color.set(s.skyLight || '#ffffff'); hemi.groundColor.set(s.bounce || '#8a7a6a');
  sun.intensity = s.light ?? 2.4; sun.color.set(s.sunColor || '#fff3df');
  const sd = s.sunDir || [4, 9, 5]; sun.position.set(sd[0], sd[1], sd[2]); sun.target.position.set(0, 0, -3);
  if (FILM) {
    scene.environmentIntensity = s.env ?? 0.55;
    fill.intensity = s.fill ?? 0.9; fill.color.set(s.fillColor || '#fff6ec');
    const c = b.cam || {}; const lk = c.look || [0, 1.2, -3];
    sun.target.position.set(lk[0], 0, lk[2]); sun.position.set(lk[0] + sd[0], sd[1], lk[2] + sd[2]);
    if (bokeh) { bokeh.enabled = !!c.dof; if (c.dof) { const p0 = c.pos || [0, 1.55, 1.6]; bokeh.uniforms.focus.value = typeof c.dof === 'number' ? c.dof : Math.hypot(lk[0] - p0[0], lk[1] - p0[1], lk[2] - p0[2]); bokeh.uniforms.aperture.value = c.aperture ?? 0.0015; } }
    const gr = Object.assign({}, STORY.grade || {}, b.grade || {});
    if (grade) { const u = grade.uniforms; u.sat.value = gr.sat ?? 1.12; u.contrast.value = gr.contrast ?? 1.06; u.grain.value = gr.grain ?? 0.035; u.vig.value = gr.vig ?? 0.55;
      u.mono.value = gr.mono ?? 0; const ti = gr.tint || [1.02, 1.0, 0.97]; u.tint.value.set(ti[0], ti[1], ti[2]); const li = gr.lift || [0.012, 0.01, 0.02]; u.lift.value.set(li[0], li[1], li[2]); }
    if (bloom) bloom.strength = gr.bloom ?? 0.28;
    if (gtao) gtao.blendIntensity = s.ao ?? 0.9;
  }
  for (const o of s.objects || []) world.add(place(o));
  if (FILM) buildRealHands(handRig, STORY.you.skin, STORY.you.sleeve, STORY.you); else buildHands(STORY.you.skin, STORY.you.sleeve);
  built = i;
}

// camera
function placeCamera(b, lt) {
  const c = b.cam || {}; const dur = b.dur;
  const k = FILM ? (c.ease === 'out' ? ease(lt / dur) : 0.5 - 0.5 * Math.cos(Math.PI * Math.min(Math.max(lt / dur, 0), 1))) : ease(lt / dur);
  const p0 = c.pos || [0, 1.55, 1.6], p1 = c.to || p0, l0 = c.look || [0, 1.2, -3], l1 = c.lookTo || l0;
  const p = [lerp(p0[0], p1[0], k), lerp(p0[1], p1[1], k), lerp(p0[2], p1[2], k)];
  const l = [lerp(l0[0], l1[0], k), lerp(l0[1], l1[1], k), lerp(l0[2], l1[2], k)];
  const head = c.head || 'breathe';
  let dy = 0, dx = 0, roll = 0;
  if (head === 'breathe') dy = Math.sin(lt * 1.6) * 0.012;
  if (head === 'walk') { dy = Math.abs(Math.sin(lt * 6)) * 0.05; dx = Math.sin(lt * 3) * 0.03; }
  if (head === 'run') { dy = Math.abs(Math.sin(lt * 11)) * 0.09; dx = Math.sin(lt * 5.5) * 0.05; roll = Math.sin(lt * 5.5) * 0.03; }
  if (head === 'float') { dy = Math.sin(lt * 1.2) * 0.08; roll = Math.sin(lt * 0.9) * 0.08; }
  if (FILM && head !== 'still') {   // gentle handheld drift
    dx += (Math.sin(lt * 1.13) * 0.6 + Math.sin(lt * 2.71) * 0.4) * 0.006; dy += (Math.sin(lt * 1.37 + 1) * 0.6 + Math.sin(lt * 3.1) * 0.4) * 0.005;
    roll += Math.sin(lt * 0.83 + 2) * 0.004;
  }
  camera.position.set(p[0] + dx, p[1] + dy, p[2]);
  camera.up.set(0, 1, 0); camera.lookAt(l[0], l[1], l[2]);
  if (FILM) { fill.position.set(p[0] + 1.2, p[1] + 1.6, p[2] + 1.5); fill.target.position.set(l[0], l[1], l[2]); }
  const fx = b.fx || [];
  if (fx.includes('shake') || head === 'shake') { camera.rotation.z += Math.sin(lt * 47) * 0.02; camera.rotation.x += Math.sin(lt * 39) * 0.012; }
  if (fx.includes('whip') && lt < 0.22) camera.rotateY((1 - ease(lt / 0.22)) * 0.6);
  if (fx.includes('tilt')) camera.rotation.z += 0.08;
  if (fx.includes('dutch')) camera.rotation.z += 0.18;
  camera.rotation.z += roll;
  let fov = c.fov || (V ? 62 : 50);
  if (fx.includes('punch')) fov *= lerp(0.72, 1, ease(lt / 0.3));
  if (fx.includes('zoomin')) fov *= lerp(1, 0.72, ease(lt / dur));
  camera.fov = fov; camera.updateProjectionMatrix();
}

// ───────── 2D overlay ─────────
const ACC = STORY.accent || '#ffd43b';
function roundRect(x, y, w, h, r) { ctx.beginPath(); ctx.moveTo(x + r, y); ctx.arcTo(x + w, y, x + w, y + h, r); ctx.arcTo(x + w, y + h, x, y + h, r); ctx.arcTo(x, y + h, x, y, r); ctx.arcTo(x, y, x + w, y, r); ctx.closePath(); }
function wrap(words, font, maxW) {
  ctx.font = font; const lines = [[]]; let w = 0;
  for (const wd of words) { const ww = ctx.measureText(wd.t + ' ').width; if (w + ww > maxW && lines[lines.length - 1].length) { lines.push([]); w = 0; } lines[lines.length - 1].push(wd); w += ww; }
  return lines;
}
function parseWords(text) { return text.split(/\s+/).filter(Boolean).map(t => ({ hi: /^\*.*\*[.,!?…]*$/.test(t) || t.startsWith('*'), t: t.replace(/\*/g, '') })); }

function caption(text, lt, y) {
  if (!text) return;
  const words = parseWords(text);
  const fs = 74 * U, font = `900 ${fs}px "Montserrat", "Inter Display Black", sans-serif`;
  const lines = wrap(words, font, W * 0.84);
  const per = 0.13; let idx = 0;
  ctx.textBaseline = 'middle'; ctx.lineJoin = 'round';
  lines.forEach((ln, li) => {
    ctx.font = font;
    const total = ln.reduce((a, w) => a + ctx.measureText(w.t.toUpperCase() + ' ').width, 0) - ctx.measureText(' ').width;
    let x = W / 2 - total / 2; const yy = y + li * fs * 1.18;
    for (const w of ln) {
      const s = back((lt - idx * per) / 0.22); idx++;
      const tw = ctx.measureText(w.t.toUpperCase()).width;
      if (s > 0.01) {
        ctx.save(); ctx.translate(x + tw / 2, yy); ctx.scale(s, s); ctx.rotate(w.hi ? -0.03 : 0);
        if (w.hi) { ctx.fillStyle = ACC; roundRect(-tw / 2 - 14 * U, -fs * 0.58, tw + 28 * U, fs * 1.12, 14 * U); ctx.fill(); }
        ctx.font = font; ctx.textAlign = 'center';
        if (!w.hi) { ctx.lineWidth = 14 * U; ctx.strokeStyle = '#111'; ctx.strokeText(w.t.toUpperCase(), 0, 2 * U); }
        ctx.fillStyle = w.hi ? '#111' : '#ffffff'; ctx.fillText(w.t.toUpperCase(), 0, 2 * U);
        ctx.restore();
      }
      x += ctx.measureText(w.t.toUpperCase() + ' ').width;
    }
  });
}

function hook(lt) {
  const H0 = STORY.hook; if (!H0 || lt > (STORY.hookDur || 2.8)) return;
  const fade = lt > (STORY.hookDur || 2.8) - 0.25 ? 1 - ((lt - ((STORY.hookDur || 2.8) - 0.25)) / 0.25) : 1;
  ctx.save(); ctx.globalAlpha = fade; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  let y = V ? H * 0.17 : H * 0.2;
  H0.lines.forEach((line, i) => {
    const big = i === H0.accent; const fs = (big ? 150 : 84) * U;
    const s = back((lt - i * 0.18) / 0.3);
    ctx.save(); ctx.translate(W / 2, y); ctx.scale(s, s); ctx.rotate((i % 2 ? 1 : -1) * 0.025 + (big ? Math.sin(lt * 6) * 0.02 : 0));
    ctx.font = `${fs}px "Anton", sans-serif`; ctx.lineJoin = 'round';
    ctx.lineWidth = 18 * U; ctx.strokeStyle = '#111'; ctx.strokeText(line.toUpperCase(), 0, 0);
    ctx.fillStyle = big ? ACC : '#fff'; ctx.fillText(line.toUpperCase(), 0, 0);
    ctx.restore(); y += fs * 1.02;
  });
  ctx.restore();
}

function project(p) { const v = V3(p).project(camera); return [(v.x + 1) / 2 * W, (1 - v.y) / 2 * H, v.z]; }

function bubble(bb, lt) {
  const d = bb.dur ?? 2.2; if (lt < bb.at || lt > bb.at + d) return;
  const k = back((lt - bb.at) / 0.25), fade = lt > bb.at + d - 0.15 ? (bb.at + d - lt) / 0.15 : 1;
  let [ax, ay, az] = bb.who ? project(bb.who) : [W * (bb.x ?? 0.5), H * (bb.y ?? 0.3), 0];
  if (az > 1) { ax = W / 2; ay = H * 0.3; }
  const fs = 46 * U; ctx.font = `800 ${fs}px "Inter", sans-serif`;
  const lines = wrap(parseWords(bb.text), ctx.font, W * 0.55);
  const lw = Math.max(...lines.map(l => ctx.measureText(l.map(w => w.t).join(' ')).width));
  const bw = lw + 56 * U, bh = lines.length * fs * 1.2 + 40 * U;
  let bx = Math.min(Math.max(ax - bw / 2, 24 * U), W - bw - 24 * U), by = Math.max(ay - bh - 60 * U, 90 * U);
  ctx.save(); ctx.globalAlpha = fade; ctx.translate(ax, ay - 30 * U); ctx.scale(k, k); ctx.translate(-ax, -(ay - 30 * U));
  ctx.fillStyle = bb.color || '#ffffff'; ctx.strokeStyle = '#111'; ctx.lineWidth = 6 * U;
  roundRect(bx, by, bw, bh, 34 * U); ctx.fill(); ctx.stroke();
  ctx.beginPath(); const tx = Math.min(Math.max(ax, bx + 40 * U), bx + bw - 40 * U); ctx.moveTo(tx - 22 * U, by + bh - 3 * U); ctx.lineTo(ax, ay - 20 * U); ctx.lineTo(tx + 22 * U, by + bh - 3 * U); ctx.fill(); ctx.stroke();
  ctx.fillStyle = bb.color || '#ffffff'; ctx.fillRect(tx - 19 * U, by + bh - 9 * U, 38 * U, 8 * U);
  ctx.fillStyle = '#111'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  lines.forEach((l, i) => ctx.fillText(l.map(w => w.t).join(' '), bx + bw / 2, by + 20 * U + fs * 0.6 + i * fs * 1.2));
  if (bb.name) { ctx.font = `900 ${26 * U}px "Inter", sans-serif`; ctx.fillStyle = bb.nameColor || '#e64980'; ctx.textAlign = 'left'; ctx.fillText(bb.name.toUpperCase(), bx + 24 * U, by - 4 * U); }
  ctx.restore();
}

function sticker(st, lt) {
  const d = st.dur ?? 1.8; if (lt < st.at || lt > st.at + d) return;
  const k = back((lt - st.at) / 0.28), fade = lt > st.at + d - 0.15 ? (st.at + d - lt) / 0.15 : 1;
  ctx.save(); ctx.globalAlpha = fade; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  if (st.kind === 'badge') {   // game-style achievement pill sliding from top
    const fs = 40 * U; ctx.font = `900 ${fs}px "Inter", "Noto Color Emoji", sans-serif`;
    const w = ctx.measureText(st.text).width + 70 * U, h = 92 * U, x = W / 2 - w / 2, y = lerp(-h, (V ? 150 : 70) * U, ease((lt - st.at) / 0.3));
    ctx.fillStyle = '#111'; roundRect(x, y, w, h, h / 2); ctx.fill(); ctx.strokeStyle = ACC; ctx.lineWidth = 5 * U; ctx.stroke();
    ctx.font = `900 ${22 * U}px "Inter", sans-serif`; ctx.fillStyle = ACC; ctx.fillText((st.title || 'ACHIEVEMENT UNLOCKED').toUpperCase(), W / 2, y + 26 * U);
    ctx.font = `900 ${fs * 0.85}px "Inter", "Noto Color Emoji", sans-serif`; ctx.fillStyle = '#fff'; ctx.fillText(st.text, W / 2, y + 62 * U);
  } else if (st.kind === 'stamp') {   // big slammed word
    const fs = (st.size || 170) * U; const s = lerp(2.2, 1, ease((lt - st.at) / 0.18));
    ctx.translate(W * (st.x ?? 0.5), H * (st.y ?? 0.42)); ctx.rotate((st.rot ?? -10) * D); ctx.scale(s, s);
    ctx.font = `${fs}px "Anton", "Noto Color Emoji", sans-serif`; ctx.lineJoin = 'round';
    ctx.lineWidth = 20 * U; ctx.strokeStyle = '#111'; ctx.strokeText(st.text.toUpperCase(), 0, 0);
    ctx.fillStyle = st.color || '#ff3b5c'; ctx.fillText(st.text.toUpperCase(), 0, 0);
  } else if (st.kind === 'float') {   // "+500 AURA" floating up
    const fs = (st.size || 64) * U; const y = H * (st.y ?? 0.4) - (lt - st.at) * 90 * U;
    ctx.font = `900 ${fs}px "Inter", "Noto Color Emoji", sans-serif`; ctx.lineJoin = 'round';
    ctx.lineWidth = 12 * U; ctx.strokeStyle = '#111'; ctx.strokeText(st.text, W * (st.x ?? 0.5), y);
    ctx.fillStyle = st.color || '#69db7c'; ctx.fillText(st.text, W * (st.x ?? 0.5), y);
  } else if (st.kind === 'label') {   // pointer label at a world spot
    const [ax, ay] = st.who ? project(st.who) : [W * (st.x ?? 0.5), H * (st.y ?? 0.5)];
    const fs = 40 * U; ctx.font = `900 ${fs}px "Inter", "Noto Color Emoji", sans-serif`;
    const w = ctx.measureText(st.text).width + 40 * U; const lx = ax + (st.side === 'left' ? -w - 60 * U : 60 * U), ly = ay - 80 * U;
    ctx.translate(ax, ay); ctx.scale(k, k); ctx.translate(-ax, -ay);
    ctx.strokeStyle = '#fff'; ctx.lineWidth = 6 * U; ctx.beginPath(); ctx.moveTo(ax, ay); ctx.lineTo(st.side === 'left' ? lx + w : lx, ly + 30 * U); ctx.stroke();
    ctx.fillStyle = st.color || '#fff'; roundRect(lx, ly, w, 60 * U, 14 * U); ctx.fill();
    ctx.fillStyle = '#111'; ctx.fillText(st.text, lx + w / 2, ly + 31 * U);
  } else if (st.kind === 'emoji') {   // big emoji reaction
    const fs = (st.size || 200) * U; ctx.font = `${fs}px "Noto Color Emoji"`;
    ctx.translate(W * (st.x ?? 0.8), H * (st.y ?? 0.3) - Math.sin((lt - st.at) * 5) * 10 * U); ctx.scale(k, k); ctx.rotate(Math.sin((lt - st.at) * 7) * 0.12);
    ctx.fillText(st.text, 0, 0);
  } else if (st.kind === 'meter') {   // horizontal meter filling up
    const x = W * 0.1, y = H * (st.y ?? 0.13), w = W * 0.8, h = 46 * U, f = lerp(st.from ?? 0, st.to ?? 1, ease((lt - st.at) / (d * 0.7)));
    ctx.fillStyle = 'rgba(0,0,0,0.55)'; roundRect(x, y, w, h, h / 2); ctx.fill();
    ctx.fillStyle = st.color || ACC; roundRect(x + 5 * U, y + 5 * U, Math.max((w - 10 * U) * f, h - 10 * U), h - 10 * U, (h - 10 * U) / 2); ctx.fill();
    ctx.font = `900 ${28 * U}px "Inter", "Noto Color Emoji", sans-serif`; ctx.fillStyle = '#fff'; ctx.textAlign = 'left'; ctx.fillText(st.text, x + 10 * U, y - 26 * U);
    ctx.textAlign = 'right'; ctx.fillText(Math.round(f * 100) + '%', x + w - 6 * U, y - 26 * U);
  }
  ctx.restore();
}

function progress(t) {
  const T = STORY.duration; ctx.fillStyle = 'rgba(255,255,255,0.25)'; ctx.fillRect(0, 0, W, 10 * U);
  ctx.fillStyle = ACC; ctx.fillRect(0, 0, W * (t / T), 10 * U);
}

// ───────── frame ─────────
let lastGL = null;
window.renderFrame = function (t) {
  let i = STORY.beats.findIndex(b => t >= b.t0 && t < b.t0 + b.dur); if (i < 0) i = STORY.beats.length - 1;
  const b = STORY.beats[i];
  if (built !== i) buildBeat(i);
  let lt = t - b.t0;
  const fz = b.freeze; let frozen = false;
  if (fz && lt >= fz.at) { frozen = true; }
  const st = frozen ? fz.at : (b.fx || []).includes('slowmo') ? lt * 0.35 : lt;
  placeCamera(b, st);
  poseHands(b.hands || 'idle', st, b.hold, b.screen);
  world.children.forEach(m => animateObj(m, st, b.dur));
  if (composer) { grade.uniforms.time.value = t; composer.render(); } else renderer.render(scene, camera);
  ctx.save();
  if (frozen) ctx.filter = 'grayscale(0.85) contrast(1.15) brightness(0.9)';
  ctx.drawImage(gl, 0, 0, W, H); ctx.filter = 'none';
  // vignette
  if (!FILM) {
    const vg = ctx.createRadialGradient(W / 2, H / 2, Math.min(W, H) * 0.35, W / 2, H / 2, Math.max(W, H) * 0.75);
    vg.addColorStop(0, 'rgba(0,0,0,0)'); vg.addColorStop(1, 'rgba(0,0,0,0.38)'); ctx.fillStyle = vg; ctx.fillRect(0, 0, W, H);
  }
  if ((b.fx || []).includes('flash') && lt < 0.25) { ctx.fillStyle = `rgba(255,255,255,${1 - lt / 0.25})`; ctx.fillRect(0, 0, W, H); }
  if (b.tint) { ctx.fillStyle = b.tint; ctx.fillRect(0, 0, W, H); }
  ctx.restore();
  if (i === 0) hook(lt);
  if (!(i === 0 && lt < (STORY.hookDur || 2.8))) caption(b.caption, lt - (i === 0 ? (STORY.hookDur || 2.8) : 0) - 0.05, V ? H * 0.7 : H * 0.8);
  for (const bb of b.bubbles || []) bubble(bb, st === lt ? lt : lt);
  for (const s2 of b.stickers || []) sticker(s2, lt);
  if (frozen && fz.label) {
    const k = back((lt - fz.at) / 0.3);
    ctx.save(); ctx.translate(W / 2, H * (V ? 0.44 : 0.42)); ctx.scale(k, k); ctx.rotate(-0.04);
    ctx.font = `900 ${84 * U}px "Inter", "Noto Color Emoji", sans-serif`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    const w = ctx.measureText(fz.label).width + 70 * U; ctx.fillStyle = '#fff'; roundRect(-w / 2, -70 * U, w, 140 * U, 22 * U); ctx.fill();
    ctx.fillStyle = '#111'; ctx.fillText(fz.label, 0, 4 * U); ctx.restore();
  }
  progress(t);
  return out.toDataURL('image/jpeg', 0.9);
};
window.READY = true;
