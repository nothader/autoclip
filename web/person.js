// DinkCam people: stylised human characters (Pixar-ish proportions) with a jointed rig, real eyes, hair,
// outfits, expressions, lip-sync and ~30 acts. Plus realistic first-person hands (5 fingers) and phone screens.
// Conventions: a person faces +z at ry=0 (toward the default camera). Arm "A" sits at -x (the person's right hand),
// arm "B" at +x. Units are metres; an adult is ~1.8 m tall.
import * as THREE from 'three';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';

let H = null;   // helpers from engine.js: { mat, geo, mesh, emojiTexture, rng }
export function initPeople(h) { H = h; }
const D = Math.PI / 180;
const clamp = (x, a, b) => Math.min(Math.max(x, a), b);
const sm = x => { x = clamp(x, 0, 1); return x * x * (3 - 2 * x); };

function shade(hex, k) {   // k<1 darker, k>1 lighter
  const c = new THREE.Color(hex); const hsl = {}; c.getHSL(hsl);
  c.setHSL(hsl.h, hsl.s, clamp(hsl.l * k, 0, 1)); return '#' + c.getHexString();
}

// ── geometry helpers ──
const G = {
  sph: () => H.geo('sph', () => new THREE.SphereGeometry(1, 32, 20)),
  sphLo: () => H.geo('sphLo', () => new THREE.SphereGeometry(1, 16, 10)),
  cap: (th) => H.geo(`scap${th.toFixed(3)}`, () => new THREE.SphereGeometry(1, 32, 16, 0, Math.PI * 2, 0, th)),
  capBot: (t0) => H.geo(`scapb${t0.toFixed(3)}`, () => new THREE.SphereGeometry(1, 28, 12, 0, Math.PI * 2, t0, Math.PI - t0)),
  half: () => H.geo('shalf', () => new THREE.SphereGeometry(1, 24, 12, 0, Math.PI * 2, 0, Math.PI / 2)),
  limb: (r, len) => H.geo(`limb${r.toFixed(4)}_${len.toFixed(4)}`, () => { const g = new THREE.CapsuleGeometry(r, len, 6, 14); g.translate(0, -len / 2, 0); return g; }),
  rbox: (w, h, d, r) => H.geo(`prb${w.toFixed(3)}_${h.toFixed(3)}_${d.toFixed(3)}_${r.toFixed(3)}`, () => new RoundedBoxGeometry(w, h, d, 4, Math.min(r, w / 2 - 0.001, h / 2 - 0.001, d / 2 - 0.001))),
  cyl: () => H.geo('cyl', () => new THREE.CylinderGeometry(0.5, 0.5, 1, 28)),
  cone: () => H.geo('cone', () => new THREE.ConeGeometry(0.5, 1, 28)),
  torusArc: (arc) => H.geo(`tarc${arc.toFixed(3)}`, () => new THREE.TorusGeometry(1, 0.16, 10, 28, arc)),
  ring: () => H.geo('pring', () => new THREE.TorusGeometry(1, 0.12, 10, 32)),
  plane: () => H.geo('pl', () => new THREE.PlaneGeometry(1, 1)),
};
function part(geo, color, kind, pos, scale, parent, shadow = true) {
  const m = H.mesh(geo, H.mat(color, kind), shadow);
  if (pos) m.position.set(pos[0], pos[1], pos[2]);
  if (scale !== undefined) { if (Array.isArray(scale)) m.scale.set(scale[0], scale[1], scale[2]); else m.scale.setScalar(scale); }
  if (parent) parent.add(m);
  return m;
}
function grp(parent, pos) { const g = new THREE.Group(); if (pos) g.position.set(pos[0], pos[1], pos[2]); if (parent) parent.add(g); return g; }

// ── hand-held props for people ──
function heldProp(kind, parent, o) {
  const g = grp(parent, [0, -0.09, 0.02]);
  switch (kind) {
    case 'phone': {
      part(G.rbox(0.075, 0.15, 0.012, 0.01), '#1b1b1f', 'glossy', [0, -0.01, 0.035], 1, g).rotation.x = -0.25;
      const sc = new THREE.Mesh(G.plane(), H.mat(o.phone_screen || '#74c0fc', 'screen')); sc.scale.set(0.066, 0.135, 1); sc.position.set(0, -0.01, 0.0425); sc.rotation.x = -0.25; g.add(sc); break;
    }
    case 'cup': part(G.cyl(), o.cup_color || '#f8f9fa', 'glossy', [0, 0.0, 0.05], [0.08, 0.11, 0.08], g); part(G.cyl(), '#6f4e37', 'matte', [0, 0.05, 0.05], [0.07, 0.01, 0.07], g); break;
    case 'coffee': part(G.cyl(), '#e9dcc9', 'matte', [0, 0.0, 0.05], [0.075, 0.13, 0.075], g); part(G.cyl(), '#ffffff', 'matte', [0, 0.075, 0.05], [0.08, 0.02, 0.08], g); part(G.cyl(), '#8d5b3a', 'matte', [0, 0.0, 0.05], [0.078, 0.04, 0.078], g); break;
    case 'paper': part(G.rbox(0.21, 0.28, 0.004, 0.001), '#ffffff', 'matte', [0, -0.08, 0.05], 1, g).rotation.x = -0.5; break;
    case 'book': part(G.rbox(0.16, 0.22, 0.035, 0.005), o.book_color || '#c92a2a', 'matte', [0, -0.06, 0.06], 1, g).rotation.x = -0.6; break;
    case 'bag': part(G.rbox(0.3, 0.32, 0.16, 0.03), o.bag_color || '#d9b98c', 'matte', [0, -0.25, 0], 1, g); break;
    case 'briefcase': part(G.rbox(0.38, 0.28, 0.1, 0.02), '#3b2a1a', 'glossy', [0, -0.2, 0], 1, g); break;
    case 'card': part(G.rbox(0.085, 0.054, 0.003, 0.004), o.card_color || '#fab005', 'metal', [0, -0.02, 0.05], 1, g).rotation.x = -0.9; break;
    case 'mic': part(G.cyl(), '#212529', 'glossy', [0, 0.02, 0.05], [0.03, 0.16, 0.03], g); part(G.sph(), '#868e96', 'metal', [0, 0.11, 0.05], 0.035, g); break;
    case 'money': part(G.rbox(0.15, 0.07, 0.02, 0.003), '#8ce99a', 'matte', [0, -0.02, 0.05], 1, g).rotation.x = -0.8; break;
    case 'box': part(G.rbox(0.42, 0.32, 0.34, 0.02), '#c8a26b', 'matte', [0, 0.05, 0.2], 1, g); break;
    case 'clipboard': part(G.rbox(0.23, 0.31, 0.01, 0.01), '#a0795a', 'matte', [0, -0.08, 0.06], 1, g).rotation.x = -0.6; part(G.rbox(0.2, 0.26, 0.003, 0.001), '#ffffff', 'matte', [0, -0.085, 0.068], 1, g).rotation.x = -0.6; break;
    case 'keys': part(G.ring(), '#adb5bd', 'metal', [0, -0.03, 0.03], 0.02, g); part(G.rbox(0.012, 0.05, 0.003, 0.001), '#ced4da', 'metal', [0, -0.065, 0.03], 1, g); break;
    case 'bottle': part(G.cyl(), '#4dabf7', 'glass', [0, 0.02, 0.05], [0.065, 0.22, 0.065], g); part(G.cyl(), '#1c7ed6', 'glossy', [0, 0.14, 0.05], [0.035, 0.03, 0.035], g); break;
    default:
      if (kind && kind.startsWith('emoji:')) {
        const sp = new THREE.Sprite(new THREE.SpriteMaterial({ map: H.emojiTexture(kind.slice(6)), transparent: true }));
        sp.scale.set(0.2, 0.2, 1); sp.position.set(0, 0.02, 0.08); g.add(sp);
      }
  }
  return g;
}

// ── build a person ──
export function makePerson(o) {
  const R = H.rng(o.seed || 1);
  const root = new THREE.Group();
  const age = o.age || 'adult';
  const skin = o.skin || '#e0ac69', top = o.top || '#4c6ef5', bottom = o.bottom || '#3b4a5a', shoes = o.shoes || '#2b2b2b';
  const elder = age === 'elder';
  const hairC = o.hair_color || (elder ? '#d9d9d9' : '#2b1d14');
  const outfit = o.outfit || 'tshirt';
  const bw = o.build || 1;
  const fem = !!o.feminine;
  const body = grp(root);                  // body is offset for sitting/jumping
  const hips = grp(body, [0, 0.92, 0]);
  const spine = grp(hips, [0, 0.06, 0]);
  const skinM = 'skin', cloth = 'fabric';
  const dress = outfit === 'dress';
  const longSleeve = ['shirt', 'hoodie', 'suit', 'jacket', 'scrubs', 'sweater', 'coat', 'uniform', 'blazer'].includes(outfit);
  const tank = outfit === 'tank';
  const topC = top, sleeveC = longSleeve ? top : skin;

  // pelvis + chest
  part(G.rbox(0.34 * bw, 0.2, 0.22, 0.07), dress ? topC : bottom, cloth, [0, 0.0, 0], 1, hips);
  const chestW = (fem ? 0.36 : 0.40) * bw;
  part(G.rbox(chestW, 0.5, 0.235, 0.09), topC, cloth, [0, 0.24, 0], 1, spine);
  if (o.belly) part(G.sph(), topC, cloth, [0, 0.12, 0.08], [0.17 * bw, 0.17, 0.14], spine);
  // outfit details on the chest
  const front = 0.118;
  if (outfit === 'suit' || outfit === 'blazer') {
    part(G.rbox(0.1, 0.3, 0.01, 0.004), o.shirt || '#ffffff', cloth, [0, 0.34, front + 0.001], 1, spine);
    if (outfit === 'suit' || o.tie) { part(G.rbox(0.045, 0.24, 0.012, 0.004), o.tie || '#c92a2a', 'glossy', [0, 0.32, front + 0.008], 1, spine); part(G.rbox(0.06, 0.04, 0.016, 0.006), o.tie || '#c92a2a', 'glossy', [0, 0.455, front + 0.008], 1, spine); }
    for (const sx of [-1, 1]) part(G.rbox(0.07, 0.26, 0.012, 0.004), shade(topC, 0.8), cloth, [sx * 0.07, 0.35, front + 0.004], 1, spine).rotation.z = sx * 0.28;
  } else if (outfit === 'shirt' || outfit === 'uniform') {
    for (const sx of [-1, 1]) part(G.rbox(0.09, 0.05, 0.02, 0.008), o.collar || shade(topC, 1.15), cloth, [sx * 0.05, 0.47, 0.1], 1, spine).rotation.z = sx * 0.5;
    for (let i = 0; i < 4; i++) part(G.sphLo(), '#f1f3f5', 'glossy', [0, 0.42 - i * 0.1, front + 0.002], [0.008, 0.008, 0.004], spine, false);
    if (o.tie) part(G.rbox(0.045, 0.26, 0.012, 0.004), o.tie, 'glossy', [0, 0.32, front + 0.008], 1, spine);
    if (outfit === 'uniform') part(G.rbox(0.06, 0.07, 0.01, 0.01), '#fcc419', 'metal', [-0.1 * bw, 0.38, front + 0.004], 1, spine);
  } else if (outfit === 'hoodie') {
    part(G.sph(), shade(topC, 0.9), cloth, [0, 0.48, -0.08], [0.17 * bw, 0.09, 0.1], spine);
    part(G.rbox(0.22 * bw, 0.1, 0.02, 0.02), shade(topC, 0.88), cloth, [0, 0.1, front], 1, spine);
    for (const sx of [-1, 1]) part(G.cyl(), '#f1f3f5', 'matte', [sx * 0.04, 0.36, front + 0.006], [0.008, 0.14, 0.008], spine, false);
  } else if (outfit === 'apron' || o.apron) {
    part(G.rbox(0.3 * bw, 0.62, 0.012, 0.004), o.apron_color || '#f8f9fa', cloth, [0, 0.07, front + 0.004], 1, spine);
  } else if (outfit === 'scrubs') {
    part(G.rbox(0.1, 0.1, 0.01, 0.002), skin, skinM, [0, 0.45, front], 1, spine).rotation.z = Math.PI / 4;
  } else if (outfit === 'jacket' || outfit === 'coat') {
    part(G.rbox(0.12, 0.44, 0.01, 0.004), o.shirt || '#f1f3f5', cloth, [0, 0.25, front + 0.001], 1, spine);
    for (const sx of [-1, 1]) part(G.cyl(), '#adb5bd', 'metal', [sx * 0.065, 0.25, front + 0.004], [0.006, 0.44, 0.006], spine, false);
  } else if (outfit === 'tshirt' || outfit === 'tank' || outfit === 'sweater') {
    part(G.torusArc(Math.PI), shade(topC, 0.85), cloth, [0, 0.49, 0.06], [0.07, 0.07, 0.07], spine).rotation.set(0.3, 0, Math.PI);
  }
  if (o.chest) {   // emoji / logo printed on the shirt
    const pl = new THREE.Mesh(G.plane(), new THREE.MeshStandardMaterial({ map: H.emojiTexture(o.chest), transparent: true, roughness: 0.9 }));
    pl.scale.set(0.13, 0.13, 1); pl.position.set(0, 0.3, front + 0.006); spine.add(pl);
  }
  if (o.lanyard) { part(G.torusArc(Math.PI), '#1c7ed6', 'matte', [0, 0.47, 0.05], [0.1, 0.22, 0.1], spine).rotation.set(0.2, 0, Math.PI); part(G.rbox(0.06, 0.085, 0.006, 0.006), '#ffffff', 'glossy', [0, 0.22, front + 0.01], 1, spine); }
  if (dress) {   // skirt
    const sk = part(H.geo('skirt', () => new THREE.CylinderGeometry(0.17, 0.3, 0.5, 28, 1, true)), topC, cloth, [0, -0.2, 0], [bw, 1, 1], hips);
    sk.material = H.mat(topC, 'fabric');
  }

  // neck + head
  part(G.cyl(), skin, skinM, [0, 0.52, 0], [0.1, 0.12, 0.1], spine);
  const neck = grp(spine, [0, 0.54, 0]);
  const headScale = (o.head || 1) * (age === 'kid' ? 1.3 : age === 'teen' ? 1.08 : 1.0);
  const head = grp(neck, [0, 0.16, 0.01]); head.scale.setScalar(headScale);
  const hr = 0.145, HX = 0.9, HY = 1.06, HZ = 0.98;
  part(G.sph(), skin, skinM, [0, 0, 0], [hr * HX, hr * HY, hr * HZ], head);
  part(G.sph(), skin, skinM, [0, -hr * 0.45, hr * 0.08], [hr * 0.74, hr * 0.56, hr * 0.78], head);   // jaw / cheeks
  const surf = (x, y, k = 1) => { const q = 1 - (x / (hr * HX)) ** 2 - (y / (hr * HY)) ** 2; return Math.sqrt(Math.max(q, 0)) * hr * HZ * k; };
  // ears
  for (const sx of [-1, 1]) part(G.sph(), skin, skinM, [sx * hr * HX * 0.97, -hr * 0.05, -hr * 0.05], [hr * 0.13, hr * 0.24, hr * 0.15], head);
  // eyes
  const eyeC = o.eye_color || '#4a2f1f';
  const eyes = [];
  const ey = hr * 0.08, ex = hr * 0.36, er = hr * (age === 'kid' ? 0.23 : 0.2);
  for (const sx of [-1, 1]) {
    const eg = grp(head, [sx * ex, ey, surf(sx * ex, ey) - er * 0.45]); eg.scale.set(er, er, er * 0.7);
    part(G.sph(), '#fbfbf8', 'glossy', [0, 0, 0], 1, eg, false);
    const iris = grp(eg, [0, 0, 0]);
    part(G.sph(), eyeC, 'glossy', [0, 0, 0.84], [0.52, 0.52, 0.22], iris, false);
    part(G.sph(), '#050505', 'glossy', [0, 0, 0.95], [0.26, 0.26, 0.12], iris, false);
    part(G.sph(), '#ffffff', 'glow', [0.2, 0.22, 1.04], [0.1, 0.1, 0.04], iris, false);
    const lid = part(G.half(), skin, skinM, [0, 0, 0], 1.1, eg, false);
    const lidLo = part(G.half(), skin, skinM, [0, 0, 0], 1.08, eg, false); lidLo.rotation.x = Math.PI + 0.42;   // lower lid (mostly hidden)
    if (o.lashes || fem) part(G.torusArc(Math.PI * 0.8), '#1b1b1b', 'matte', [0, 0.0, 0], [1.12, 1.12, 1.12], lid, false).rotation.set(Math.PI / 2, 0, Math.PI * 0.1);
    eyes.push({ eg, iris, lid, lidLo });
  }
  // brows
  const brows = [];
  for (const sx of [-1, 1]) {
    const bg = grp(head, [sx * ex, ey + hr * 0.36, surf(sx * ex, ey + hr * 0.36) + hr * 0.01]);
    part(G.rbox(hr * 0.42, hr * (fem ? 0.06 : 0.09), hr * 0.07, hr * 0.03), o.brow_color || shade(hairC === '#d9d9d9' ? '#9a9a9a' : hairC, 0.9), 'matte', [0, 0, 0], 1, bg, false);
    brows.push(bg);
  }
  // nose
  part(G.sph(), shade(skin, 0.96), skinM, [0, -hr * 0.16, surf(0, -hr * 0.16) + hr * 0.04], [hr * 0.13, hr * 0.16, hr * 0.14], head, false);
  // mouth
  const my = -hr * 0.48, mz = surf(0, my) + hr * 0.16;
  const mouth = grp(head, [0, my, mz]);
  const lipC = o.lips || shade(skin, 0.62);
  const smile = part(G.torusArc(Math.PI), lipC, 'matte', [0, hr * 0.06, 0], [hr * 0.22, hr * 0.22, hr * 0.22], mouth, false); smile.rotation.z = Math.PI;
  const open = grp(mouth);
  part(G.sph(), '#4a1414', 'matte', [0, 0, -hr * 0.01], [hr * 0.2, hr * 0.13, hr * 0.06], open, false);
  part(G.sph(), '#f8f4ee', 'glossy', [0, hr * 0.07, -hr * 0.005], [hr * 0.15, hr * 0.045, hr * 0.05], open, false);   // teeth
  const flat = part(G.rbox(hr * 0.3, hr * 0.035, hr * 0.03, hr * 0.015), lipC, 'matte', [0, 0, 0], 1, mouth, false);
  if (o.blush || age === 'kid') for (const sx of [-1, 1]) { const b = part(G.sph(), '#ff8787', 'matte', [sx * hr * 0.55, -hr * 0.25, surf(sx * hr * 0.55, -hr * 0.25) - hr * 0.01], [hr * 0.14, hr * 0.08, hr * 0.03], head, false); b.material = H.mat('#ff8787', 'matte', 0.45); }

  // hair
  const hs = o.hair ?? (elder ? 'bald' : 'short');
  const HM = 'hair';
  const capHair = (th, tilt, k = 1.07, c = hairC, sx = 1) => { const m = part(G.cap(th), c, HM, [0, hr * 0.02, -hr * 0.02], [hr * HX * k * sx, hr * HY * k, hr * HZ * k], head); m.rotation.x = tilt; return m; };
  if (hs === 'short' || hs === 'spiky' || hs === 'ponytail' || hs === 'bun' || hs === 'mohawk_short' || hs === 'side') {
    capHair(1.25, -0.55); capHair(1.9, -1.25, 1.04);
    if (hs === 'side') { const f = part(G.sph(), hairC, HM, [hr * 0.25, hr * 0.68, hr * 0.62], [hr * 0.55, hr * 0.22, hr * 0.3], head); f.rotation.z = -0.35; }
    if (hs === 'spiky') for (let i = 0; i < 9; i++) { const a = (i / 9) * Math.PI * 2; const c = part(G.cone(), hairC, HM, [Math.sin(a) * hr * 0.45, hr * 1.02, Math.cos(a) * hr * 0.4 - hr * 0.1], [hr * 0.28, hr * 0.42, hr * 0.28], head); c.rotation.set(Math.cos(a) * 0.5, 0, -Math.sin(a) * 0.5); }
    if (hs === 'ponytail') { const p = part(G.limb(hr * 0.17, hr * 1.2), hairC, HM, [0, hr * 0.35, -hr * 0.95], 1, head); p.rotation.x = 0.35; part(G.sph(), hairC, HM, [0, hr * 0.42, -hr * 0.92], hr * 0.22, head); }
    if (hs === 'bun') part(G.sph(), hairC, HM, [0, hr * 0.95, -hr * 0.45], hr * 0.38, head);
  } else if (hs === 'buzz') { capHair(1.35, -0.5, 1.02); capHair(1.9, -1.2, 1.015); }
  else if (hs === 'bob' || hs === 'long' || hs === 'pigtails') {
    capHair(1.25, -0.6, 1.08); const b = capHair(2.05, -0.95, 1.12); b.scale.x *= 1.04;
    if (hs === 'long') { part(G.rbox(hr * 1.9, hr * 2.6, hr * 0.5, hr * 0.24), hairC, HM, [0, -hr * 0.95, -hr * 0.6], 1, head); for (const sx of [-1, 1]) part(G.rbox(hr * 0.35, hr * 1.9, hr * 0.5, hr * 0.17), hairC, HM, [sx * hr * 0.95, -hr * 0.75, -hr * 0.15], 1, head); }
    if (hs === 'pigtails') for (const sx of [-1, 1]) { const p = part(G.limb(hr * 0.2, hr * 0.9), hairC, HM, [sx * hr * 1.05, hr * 0.1, -hr * 0.3], 1, head); p.rotation.z = sx * 0.5; }
  } else if (hs === 'curly' || hs === 'afro') {
    const big = hs === 'afro' ? 1.5 : 1.12, n = hs === 'afro' ? 26 : 30;
    if (hs === 'afro') part(G.sph(), hairC, HM, [0, hr * 0.38, -hr * 0.18], [hr * 1.32, hr * 1.12, hr * 1.18], head);
    else capHair(1.4, -0.55, 1.05);
    for (let i = 0; i < n; i++) {
      const y = 1 - (i / (n - 1)) * 1.25, rr = Math.sqrt(1 - y * y), a = i * 2.39996;
      const px = Math.cos(a) * rr, pz = Math.sin(a) * rr, py = y;
      if (pz > 0.35 && py < 0.55) continue;
      part(G.sphLo(), hairC, HM, [px * hr * big * 0.95, py * hr * big * 0.95 + hr * 0.12, pz * hr * big * 0.95 - hr * 0.08], hr * (hs === 'afro' ? 0.34 : 0.3), head);
    }
  } else if (hs === 'bald') {
    if (elder) for (const sx of [-1, 1]) part(G.sph(), hairC, HM, [sx * hr * 0.85, hr * 0.05, -hr * 0.35], [hr * 0.2, hr * 0.32, hr * 0.5], head);
  } else if (hs === 'mohawk') {
    capHair(1.9, -1.25, 1.02, shade(hairC, 0.7));
    for (let i = 0; i < 6; i++) part(G.rbox(hr * 0.16, hr * 0.5, hr * 0.32, hr * 0.06), hairC, HM, [0, hr * (0.95 - i * 0.02) + Math.sin(i / 5 * Math.PI) * hr * 0.1, hr * (0.55 - i * 0.3)], 1, head).rotation.x = -0.2 + i * 0.25;
  }
  // facial hair
  if (o.beard === 'full' || o.beard === true) { const bd = part(G.capBot(Math.PI * 0.52), o.beard_color || hairC, HM, [0, -hr * 0.12, hr * 0.06], [hr * HX * 1.04, hr * HY * 1.02, hr * HZ * 1.03], head); bd.rotation.x = 0.35; mouth.position.z += hr * 0.06; }
  if (o.beard === 'stubble') { const bd = part(G.capBot(Math.PI * 0.55), shade(skin, 0.78), skinM, [0, -hr * 0.1, hr * 0.04], [hr * HX * 1.01, hr * HY * 1.0, hr * HZ * 1.01], head); bd.rotation.x = 0.35; }
  if (o.beard === 'mustache' || o.beard === 'full') { const ms = part(G.limb(hr * 0.06, hr * 0.32), o.beard_color || hairC, HM, [hr * 0.16, my + hr * 0.2, mz + hr * 0.02], 1, head); ms.rotation.z = -Math.PI / 2; }
  // glasses
  if (o.glasses) {
    const gc = typeof o.glasses === 'string' ? o.glasses : '#1b1b1f';
    for (const sx of [-1, 1]) { const r = part(G.ring(), gc, 'glossy', [sx * ex, ey, surf(sx * ex, ey) + hr * 0.07], hr * 0.26, head, false); r.scale.z = hr * 0.5; }
    part(G.cyl(), gc, 'glossy', [0, ey + hr * 0.04, surf(0, ey) + hr * 0.06], [hr * 0.03, hr * 0.2, hr * 0.03], head, false).rotation.z = Math.PI / 2;
    if (o.sunglasses) for (const sx of [-1, 1]) part(G.sph(), '#111111', 'glossy', [sx * ex, ey, surf(sx * ex, ey) + hr * 0.06], [hr * 0.25, hr * 0.22, hr * 0.05], head, false);
  }
  // hats
  const hat = o.hat, hatC = o.hat_color;
  if (hat === 'cap') { const c = capHair(1.35, -0.4, 1.12, hatC || '#e03131'); const br = part(G.rbox(hr * 1.2, hr * 0.06, hr * 0.9, hr * 0.03), hatC || '#e03131', 'fabric', [0, hr * 0.58, hr * 1.0], 1, head); br.rotation.x = 0.18; }
  if (hat === 'beanie') { capHair(1.45, -0.35, 1.13, hatC || '#364fc7'); part(G.ring(), shade(hatC || '#364fc7', 0.85), 'fabric', [0, hr * 0.35, -hr * 0.05], [hr * 1.02, hr * 1.02, hr * 2.2], head).rotation.x = Math.PI / 2 + 0.35; }
  if (hat === 'hardhat') { capHair(1.5, -0.25, 1.18, hatC || '#fab005').material = H.mat(hatC || '#fab005', 'glossy'); part(G.cyl(), hatC || '#fab005', 'glossy', [0, hr * 0.42, hr * 0.12], [hr * 2.5, hr * 0.06, hr * 2.6], head); }
  if (hat === 'chef') { part(G.cyl(), '#ffffff', 'fabric', [0, hr * 0.95, -hr * 0.05], [hr * 1.7, hr * 0.7, hr * 1.7], head); part(G.sph(), '#ffffff', 'fabric', [0, hr * 1.45, -hr * 0.05], [hr * 1.05, hr * 0.6, hr * 1.05], head); }
  if (hat === 'headphones') { part(G.torusArc(Math.PI), hatC || '#212529', 'glossy', [0, hr * 0.05, 0], [hr * 1.08, hr * 1.18, hr * 1.1], head); for (const sx of [-1, 1]) part(G.sph(), hatC || '#212529', 'glossy', [sx * hr * 0.98, 0, 0], [hr * 0.2, hr * 0.32, hr * 0.32], head); }
  if (hat === 'party') { const c = part(G.cone(), hatC || '#845ef7', 'glossy', [hr * 0.15, hr * 1.25, 0], [hr * 0.9, hr * 1.2, hr * 0.9], head); c.rotation.z = -0.2; }
  if (hat === 'crown') { part(G.cyl(), '#fcc419', 'metal', [0, hr * 1.0, 0], [hr * 1.3, hr * 0.4, hr * 1.3], head); }
  if (hat === 'grad') { part(G.rbox(hr * 2.4, hr * 0.08, hr * 2.4, hr * 0.02), '#111111', 'matte', [0, hr * 1.12, 0], 1, head).rotation.y = Math.PI / 4; capHair(1.2, -0.3, 1.1, '#111111'); }
  if (hat === 'santa') { const c = part(G.cone(), '#e03131', 'fabric', [0, hr * 1.2, -hr * 0.2], [hr * 1.9, hr * 1.4, hr * 1.9], head); c.rotation.x = -0.4; part(G.ring(), '#ffffff', 'fabric', [0, hr * 0.62, 0], [hr * 0.95, hr * 0.95, hr * 3], head).rotation.x = Math.PI / 2; }
  if (o.earrings) for (const sx of [-1, 1]) part(G.sph(), '#fcc419', 'metal', [sx * hr * 0.95, -hr * 0.35, 0], hr * 0.06, head, false);

  // arms
  const arms = [];
  const shY = 0.44, shX = chestW / 2 + 0.035;
  const ua = 0.27, fa = 0.25, uaR = 0.052 * Math.sqrt(bw), faR = 0.044 * Math.sqrt(bw);
  for (const sx of [-1, 1]) {
    const sh = grp(spine, [sx * shX, shY, 0]); sh.rotation.order = 'ZYX';
    part(G.sph(), tank ? skin : topC, tank ? skinM : cloth, [0, 0, 0], uaR * 1.12, sh);   // shoulder ball
    part(G.limb(uaR, ua), tank ? skin : (outfit === 'tshirt' || dress ? topC : sleeveC), tank ? skinM : cloth, [0, 0, 0], 1, sh);
    if (outfit === 'tshirt' || dress) part(G.limb(uaR * 0.92, ua * 0.45), skin, skinM, [0, -ua * 0.5, 0], 1, sh);   // bare lower upper-arm
    const el = grp(sh, [0, -ua, 0]); el.rotation.order = 'ZYX';
    part(G.limb(faR, fa), longSleeve ? sleeveC : skin, longSleeve ? cloth : skinM, [0, 0, 0], 1, el);
    if (longSleeve) part(G.cyl(), shade(sleeveC, 0.9), cloth, [0, -fa + 0.01, 0], [faR * 2.3, 0.04, faR * 2.3], el);
    if (o.watch && sx === 1) part(G.cyl(), '#212529', 'glossy', [0, -fa + 0.03, 0], [faR * 2.25, 0.025, faR * 2.25], el);
    const wr = grp(el, [0, -fa - 0.01, 0]);
    // hand: palm + mitten fingers + thumb (reads well at distance)
    part(G.rbox(0.075, 0.085, 0.032, 0.014), skin, skinM, [0, -0.04, 0], 1, wr);
    const fing = part(G.rbox(0.072, 0.06, 0.028, 0.013), skin, skinM, [0, -0.095, 0.004], 1, wr);
    const th = part(G.limb(0.013, 0.04), skin, skinM, [-sx * 0.035, -0.02, 0.012], 1, wr); th.rotation.z = -sx * 0.6; th.rotation.x = -0.4;
    arms.push({ sh, el, wr, fing, side: sx });
  }
  // legs
  const legs = [];
  const th = 0.42, sn = 0.4;
  for (const sx of [-1, 1]) {
    const hp = grp(hips, [sx * 0.095 * bw, -0.04, 0]);
    part(G.limb(0.075 * bw, th), dress ? (o.tights || skin) : bottom, dress ? skinM : cloth, [0, 0, 0], 1, hp);
    const kn = grp(hp, [0, -th, 0]);
    part(G.limb(0.058 * Math.sqrt(bw), sn), dress || outfit === 'shorts' ? (o.tights || skin) : bottom, dress || outfit === 'shorts' ? skinM : cloth, [0, 0, 0], 1, kn);
    const an = grp(kn, [0, -sn - 0.02, 0]);
    part(G.rbox(0.11, 0.085, 0.27, 0.035), shoes, 'glossy', [0, -0.02, 0.055], 1, an);
    part(G.rbox(0.115, 0.025, 0.28, 0.01), o.sole || shade(shoes, 1.6), 'matte', [0, -0.055, 0.055], 1, an);
    legs.push({ hp, kn, an, side: sx });
  }
  if (outfit === 'shorts') {
    for (const l of legs) part(G.limb(0.082 * bw, 0.2), bottom, cloth, [0, 0, 0], 1, l.hp);
  }

  // held props: hold = right hand (arm A), hold2 = left (arm B)
  if (o.hold) heldProp(o.hold, arms[0].wr, o);
  if (o.hold2) heldProp(o.hold2, arms[1].wr, o);
  if (!o.hold && ['phone', 'call', 'selfie', 'text'].includes(o.act)) heldProp('phone', arms[0].wr, o);
  if (!o.hold && o.act === 'drink') heldProp('coffee', arms[0].wr, o);

  const ageScale = age === 'kid' ? 0.6 : age === 'teen' ? 0.9 : elder ? 0.95 : 1;
  root.scale.setScalar((o.size || 1) * (o.height || 1) * ageScale);
  root.userData.person = {
    body, hips, spine, neck, head, eyes, brows, smile, open, flat, mouth, arms, legs,
    expr: o.expr || 'smile', act: o.act || 'idle', talk: o.talk || [], seed: o.seed || 1, look: o.look ?? 'you', elder, kid: age === 'kid',
    blinkP: 2.6 + R() * 2.2, blinkO: R() * 3, ph: R() * 6.283, hr,
  };
  return root;
}

// ── expressions: brow tilt (inner up +), brow lift, upper-lid angle (open -), mouth, pupil size ──
const EXPR = {
  smile: [0, 0, -0.9, 'smile', 1], happy: [0.1, 0.012, -0.8, 'grin', 1], grin: [0.05, 0.01, -0.8, 'grin', 1],
  shock: [0.15, 0.03, -1.25, 'o', 0.75], surprised: [0.1, 0.025, -1.15, 'o', 0.85], sad: [0.4, 0.004, -0.6, 'frown', 1],
  angry: [-0.45, -0.012, -0.7, 'grit', 1], smirk: [-0.1, 0.006, -0.75, 'smirk', 1], neutral: [0, 0, -0.85, 'flat', 1],
  love: [0.15, 0.01, -0.8, 'smile', 1.25], scared: [0.45, 0.025, -1.2, 'o', 0.65], tired: [0.1, -0.004, 0.25, 'flat', 1],
  cringe: [0.35, 0.006, -0.55, 'grit', 1], laugh: [0.15, 0.015, 0.25, 'grin', 1], sleep: [0, 0, 1.55, 'flat', 1],
  confused: [0.3, 0.012, -0.8, 'smirk', 1], proud: [-0.05, 0.008, -0.65, 'smile', 1], bored: [0, -0.006, 0.05, 'flat', 1],
  worried: [0.45, 0.012, -0.85, 'frown', 1], disgust: [-0.3, -0.006, -0.5, 'frown', 1], excited: [0.2, 0.025, -1.05, 'grin', 1],
};

const tmpV = new THREE.Vector3(), tmpM = new THREE.Matrix4(), tmpQ = new THREE.Quaternion();
function setArm(a, fwd, out, tw, elb, elbTw = 0) {
  a.sh.rotation.set(-fwd, tw * a.side, out * a.side);
  a.el.rotation.set(-elb, elbTw * a.side, 0);
}
function setLeg(l, fwd, knee, ankle = 0, out = 0) { l.hp.rotation.set(-fwd, 0, out * l.side); l.kn.rotation.set(knee, 0, 0); l.an.rotation.set(ankle - (-fwd + knee) * 0.0, 0, 0); }

export function animatePerson(g, t, camera) {
  const p = g.userData.person; const ph = p.ph;
  const e = EXPR[p.expr] || EXPR.smile;
  const talking = p.talk.some(([a, d]) => t >= a && t <= a + d);
  const [A, B] = p.arms, [LA, LB] = p.legs;
  // defaults: relaxed stance
  let by = 0, brx = 0, brz = 0, bry = 0;                  // body offset / tilt
  let sp = [0.02 + (p.elder ? 0.12 : 0), 0, 0];           // spine x (lean fwd +), y, z
  let hd = [0, 0, 0];                                      // extra head pitch(+down), yaw, roll
  const breathe = Math.sin(t * 1.7 + ph);
  let lookW = 1;                                           // how much the head tracks the look target
  setArm(A, 0.05 + breathe * 0.01, 0.1, 0, 0.18); setArm(B, 0.05 + breathe * 0.01, 0.1, 0, 0.18);
  setLeg(LA, 0, 0.02); setLeg(LB, 0, 0.02);
  const sway = Math.sin(t * 0.9 + ph);
  let hipsX = sway * 0.012, hipsRz = sway * 0.025;
  const act = p.act;
  const w = (f) => Math.sin(t * f + ph);
  switch (act) {
    case 'idle': case 'stand': break;
    case 'talk': {
      const k = w(2.2), k2 = Math.sin(t * 3.1 + ph * 2);
      setArm(B, 0.45 + k * 0.12, 0.25, -0.5 + k2 * 0.15, 1.25 + k * 0.2); setArm(A, 0.25 + k2 * 0.08, 0.15, -0.3, 0.9 + k2 * 0.25);
      hd = [Math.sin(t * 4.3 + ph) * 0.04, 0, k * 0.04]; break;
    }
    case 'walk': case 'run': {
      const run = act === 'run'; const f = run ? 10 : 6.2, a = run ? 0.75 : 0.42; const s = Math.sin(t * f + ph);
      setLeg(LA, s * a, Math.max(0, Math.sin(t * f + ph - 1.3)) * (run ? 1.3 : 0.6) + 0.05);
      setLeg(LB, -s * a, Math.max(0, -Math.sin(t * f + ph - 1.3)) * (run ? 1.3 : 0.6) + 0.05);
      setArm(A, -s * (run ? 0.8 : 0.35), 0.12, 0, run ? 1.4 : 0.3); setArm(B, s * (run ? 0.8 : 0.35), 0.12, 0, run ? 1.4 : 0.3);
      by = Math.abs(Math.cos(t * f + ph)) * (run ? 0.06 : 0.025) - (run ? 0.04 : 0.01); sp[0] += run ? 0.22 : 0.03; sp[1] = s * 0.08; hipsX = 0; hipsRz = 0; break;
    }
    case 'wave': setArm(A, 0.25, 0.9, -1.2 + Math.sin(t * 9) * 0.35, 1.9); setArm(B, 0.05, 0.1, 0, 0.18); hd = [0, 0, 0.08]; break;
    case 'point': setArm(A, 1.45, 0.1, 0, 0.05); hd = [-0.03, 0, 0]; break;
    case 'point_side': setArm(A, 0.2, 1.45, 0, 0.05); hd = [0, -0.3, 0]; break;
    case 'cheer': { const k = Math.abs(Math.sin(t * 7 + ph)); setArm(A, 0.2, 2.55 - k * 0.15, 0, 0.3); setArm(B, 0.2, 2.55 - k * 0.15, 0, 0.3); by = k * 0.08; hd = [-0.15, 0, 0]; break; }
    case 'clap': { const k = Math.sin(t * 14); setArm(A, 0.8, 0.3 + k * 0.07, -0.55, 1.25); setArm(B, 0.8, 0.3 + k * 0.07, -0.55, 1.25); break; }
    case 'facepalm': setArm(A, 0.95, 0.15, -0.85, 2.35); hd = [0.32, 0, 0.05]; sp[0] += 0.08; break;
    case 'cry': setArm(A, 0.95, 0.2, -0.85, 2.3); setArm(B, 0.95, 0.2, -0.85, 2.3); hd = [0.3, 0, 0]; sp[0] += 0.1 + Math.abs(Math.sin(t * 9)) * 0.03; break;
    case 'shrug': { const k = 0.5 + 0.5 * Math.sin(t * 3 + ph); setArm(A, 0.3, 0.35, 0.9, 1.55); setArm(B, 0.3, 0.35, 0.9, 1.55); hd = [0.05, 0, 0.12 * k]; A.sh.position.y = B.sh.position.y = 0.44 + 0.03 * k; break; }
    case 'think': setArm(A, 0.6, 0.15, -0.9, 2.45); setArm(B, 0.45, 0.25, -1.3, 1.6); hd = [-0.12, 0.15, 0.1]; break;
    case 'cross': case 'arms_crossed': setArm(A, 0.75, 0.22, -0.95, 1.45); setArm(B, 0.68, 0.22, -0.95, 1.35); hd = [-0.05, 0, 0]; break;
    case 'hips': case 'angry': setArm(A, -0.12, 0.62, -1.5, 1.65); setArm(B, -0.12, 0.62, -1.5, 1.65); sp[0] += act === 'angry' ? 0.12 : -0.03; if (act === 'angry') { hd = [0.12, 0, 0]; brz = Math.sin(t * 30) * 0.008; } break;
    case 'scared': setArm(A, 1.0, 0.3, -0.6, 1.9); setArm(B, 1.0, 0.3, -0.6, 1.9); sp[0] -= 0.1; brz = Math.sin(t * 38) * 0.02; setLeg(LA, 0.15, 0.3); setLeg(LB, 0.15, 0.3); by = -0.04; break;
    case 'dance': {
      const k = Math.sin(t * 6 + ph), k2 = Math.cos(t * 6 + ph);
      setArm(A, 0.3, 1.2 + k * 1.0, 0, 0.8 + k2 * 0.4); setArm(B, 0.3, 1.2 - k * 1.0, 0, 0.8 - k2 * 0.4);
      by = Math.abs(k) * 0.06 - 0.03; hipsX = k * 0.05; hipsRz = k * 0.12; sp[2] = -k * 0.15; setLeg(LA, 0, 0.2 + Math.max(0, k) * 0.3); setLeg(LB, 0, 0.2 + Math.max(0, -k) * 0.3); break;
    }
    case 'jump': { const k = Math.abs(Math.sin(t * 4.2 + ph)); by = k * 0.5; setLeg(LA, 0.3 * k, 0.7 * k); setLeg(LB, 0.3 * k, 0.7 * k); setArm(A, 0.2, 2.4, 0, 0.3); setArm(B, 0.2, 2.4, 0, 0.3); break; }
    case 'sit': case 'sit_type': case 'sit_phone': case 'sit_talk': case 'sit_eat': case 'sit_sad': {
      setLeg(LA, 1.5, 1.5, 0, 0.06); setLeg(LB, 1.5, 1.5, 0, 0.06); by = -0.43; hipsX = 0; hipsRz = 0;
      if (act === 'sit') { setArm(A, 0.6, 0.1, 0, 0.75); setArm(B, 0.6, 0.1, 0, 0.75); }
      if (act === 'sit_type') { const k = Math.sin(t * 22), k2 = Math.cos(t * 19); setArm(A, 0.55, 0.15, -0.2, 1.25 + k * 0.05); setArm(B, 0.55, 0.15, -0.2, 1.25 + k2 * 0.05); hd = [0.18, 0, 0]; lookW = 0.25; }
      if (act === 'sit_phone') { setArm(A, 0.45, 0.12, -0.5, 1.75); setArm(B, 0.4, 0.12, -0.6, 1.7); hd = [0.38, 0, 0]; lookW = 0; }
      if (act === 'sit_talk') { const k = w(2.2); setArm(B, 0.55 + k * 0.12, 0.2, -0.5, 1.3 + k * 0.2); setArm(A, 0.6, 0.1, 0, 0.75); }
      if (act === 'sit_eat') { const k = Math.max(0, Math.sin(t * 2.6 + ph)); setArm(A, 0.6 + k * 0.2, 0.12, -0.6, 1.3 + k * 0.95); setArm(B, 0.6, 0.1, 0, 0.75); }
      if (act === 'sit_sad') { setArm(A, 0.6, 0.1, 0, 0.75); setArm(B, 0.6, 0.1, 0, 0.75); hd = [0.35, 0, 0]; sp[0] += 0.25; }
      break;
    }
    case 'type': { const k = Math.sin(t * 22), k2 = Math.cos(t * 19); setArm(A, 0.6, 0.15, -0.2, 1.0 + k * 0.05); setArm(B, 0.6, 0.15, -0.2, 1.0 + k2 * 0.05); hd = [0.2, 0, 0]; lookW = 0.25; break; }
    case 'phone': case 'text': { setArm(A, 0.5, 0.12, -0.55, 1.8); if (act === 'text') setArm(B, 0.45, 0.1, -0.65, 1.75); hd = [0.38, 0, 0]; lookW = 0; break; }
    case 'selfie': setArm(A, 1.35, 0.35, 0, 0.35); hd = [-0.05, -0.2, 0.1]; break;
    case 'call': setArm(A, 0.35, 0.45, -0.6, 2.55); hd = [0, 0, 0.12]; break;
    case 'drink': { const k = sm((Math.sin(t * 1.6 + ph) + 0.2) * 1.5); setArm(A, 0.45 + k * 0.3, 0.12, -0.7, 1.3 + k * 1.05); hd = [-0.12 * k, 0, 0]; break; }
    case 'eat': { const k = Math.max(0, Math.sin(t * 2.6 + ph)); setArm(A, 0.5 + k * 0.25, 0.12, -0.6, 1.2 + k * 1.1); break; }
    case 'carry': setArm(A, 0.85, 0.18, 0, 0.75); setArm(B, 0.85, 0.18, 0, 0.75); sp[0] -= 0.06; break;
    case 'push': setArm(A, 1.2, 0.18, 0, 0.35); setArm(B, 1.2, 0.18, 0, 0.35); sp[0] += 0.2; break;
    case 'bow': sp[0] += 0.75; setArm(A, 0.2, 0.05, 0, 0.1); setArm(B, 0.2, 0.05, 0, 0.1); lookW = 0; break;
    case 'laugh': { const k = Math.abs(Math.sin(t * 9)); sp[0] -= 0.18 + k * 0.05; setArm(A, 0.5, 0.25, -1.0, 1.3); setArm(B, 0.1, 0.25, 0, 0.3); hd = [-0.2, 0, 0]; break; }
    case 'stretch': { setArm(A, 0.2, 2.8, 0, 0.2); setArm(B, 0.2, 2.8, 0, 0.2); sp[0] -= 0.1; hd = [-0.25, 0, 0]; break; }
    case 'yawn': { setArm(A, 0.9, 0.2, -0.85, 2.2); hd = [-0.25, 0, 0]; break; }
    case 'lie': case 'sleep': g.rotation.x = -Math.PI / 2; by = 0.13; setArm(A, 0, 0.15, 0, 0.1); setArm(B, 0, 0.15, 0, 0.1); lookW = 0; breathe; break;
    case 'kneel': setLeg(LA, 1.4, 1.5); setLeg(LB, -0.05, 1.55); by = -0.35; break;
    case 'lean': sp[2] = 0.08; hipsX = 0.04; setArm(A, 0, 0.15, 0, 0.1); setArm(B, -0.1, 0.4, 1.2, 1.6); setLeg(LB, 0.05, 0.1, 0, -0.08); break;
    case 'mic': setArm(A, 0.55, 0.1, -0.7, 2.1); setArm(B, 0.3, 0.6, -0.4, 1.0 + Math.sin(t * 3) * 0.3); break;
    case 'gun_fingers': case 'finger_guns': setArm(A, 1.35, 0.2, 0, 0.15); setArm(B, 1.35, 0.2, 0, 0.15); hd = [0, 0, 0.15]; break;
    case 'thumbs_up': setArm(A, 0.6, 0.2, -0.3, 1.5); hd = [0, 0, 0.08]; break;
    case 'flex': setArm(A, 0.0, 1.45, 1.45, 1.95); setArm(B, 0.0, 1.45, 1.45, 1.95); break;
    case 'beg': case 'please': setArm(A, 0.75, 0.15, -0.9, 1.9); setArm(B, 0.75, 0.15, -0.9, 1.9); hd = [-0.05, 0, 0.18]; break;
    case 'panic': { const k = Math.sin(t * 16); setArm(A, 0.5, 1.9 + k * 0.4, 0, 0.5); setArm(B, 0.5, 1.9 - k * 0.4, 0, 0.5); brz = Math.sin(t * 20) * 0.04; break; }
    case 'shake_head': hd = [0, Math.sin(t * 9) * 0.35, 0]; lookW = 0.6; break;
    case 'nod': hd = [Math.sin(t * 8) * 0.15, 0, 0]; break;
  }
  // talking adds small gestures + head bobs
  if (talking && act === 'idle') { const k = w(2.4); setArm(B, 0.35 + k * 0.1, 0.22, -0.45, 1.1 + k * 0.2); hd[0] += Math.sin(t * 4.3 + ph) * 0.04; }
  p.body.position.set(0, by, 0); g.rotation.z = (g.userData.base ? g.userData.base.r.z : 0) + brz;
  p.hips.position.x = hipsX; p.hips.rotation.z = hipsRz;
  p.spine.rotation.set(sp[0] + breathe * 0.008, sp[1], sp[2] - hipsRz * 0.7);
  p.spine.scale.set(1, 1 + breathe * 0.006, 1);
  // head: look at the camera (or a point), within neck limits
  let yaw = 0, pitch = 0;
  if (p.look && lookW > 0 && camera) {
    const target = Array.isArray(p.look) ? tmpV.set(p.look[0], p.look[1], p.look[2]) : tmpV.copy(camera.position);
    p.neck.updateWorldMatrix(true, false);
    tmpM.copy(p.neck.matrixWorld).invert(); target.applyMatrix4(tmpM);
    yaw = clamp(Math.atan2(target.x, target.z), -0.95, 0.95) * lookW;
    pitch = clamp(-Math.atan2(target.y - 0.16, Math.hypot(target.x, target.z)), -0.45, 0.5) * lookW;
  }
  p.neck.rotation.set(pitch + hd[0], yaw + hd[1] + Math.sin(t * 0.7 + ph) * 0.03, hd[2]);
  // face
  const blink = ((t + p.blinkO) % p.blinkP) < 0.13;
  let lid = blink ? 1.55 : e[2];
  if (act === 'sleep') lid = 1.55;
  p.eyes.forEach((ey, i) => {
    ey.lid.rotation.x = lid; ey.lidLo.rotation.x = Math.PI + (e[3] === 'grin' || p.expr === 'laugh' ? 0.08 : 0.42);   // pole down-back: lower lid only covers below the iris
    ey.iris.scale.setScalar(e[4]);
    ey.iris.rotation.set(-pitch * 0.15 + Math.sin(t * 0.6 + ph) * 0.03, yaw * 0.2 + Math.sin(t * 0.45 + ph) * 0.05, 0);
  });
  p.brows.forEach((b, i) => { const sx = i ? 1 : -1; b.rotation.z = -sx * e[0] * 0.6 + (p.expr === 'smirk' && i ? -0.25 : 0); b.position.y = p.hr * 0.08 + p.hr * 0.36 + e[1] + (p.expr === 'smirk' && i ? 0.012 : 0); });
  let m = e[3];
  let jaw = 0;
  if (talking) { jaw = 0.35 + 0.65 * Math.abs(Math.sin(t * 13 + ph) * 0.6 + Math.sin(t * 7.3) * 0.4); m = 'talk'; }
  p.smile.visible = m === 'smile' || m === 'frown' || m === 'smirk';
  p.smile.rotation.z = m === 'frown' ? 0 : Math.PI; p.smile.position.y = m === 'frown' ? -p.hr * 0.16 : p.hr * 0.06;
  p.smile.rotation.y = m === 'smirk' ? 0.0 : 0; p.smile.rotation.x = 0;
  p.smile.scale.set(p.hr * 0.22 * (m === 'smirk' ? 0.8 : 1), p.hr * 0.22 * (m === 'smirk' ? 0.6 : 1), p.hr * 0.22);
  p.smile.position.x = m === 'smirk' ? p.hr * 0.05 : 0;
  p.open.visible = m === 'grin' || m === 'o' || m === 'talk' || m === 'grit';
  p.flat.visible = m === 'flat';
  if (m === 'o') p.open.scale.set(0.7, 1.5, 1);
  else if (m === 'grin') p.open.scale.set(1.15, 1.0 + (p.expr === 'laugh' ? Math.abs(Math.sin(t * 10)) * 0.5 : 0), 1);
  else if (m === 'grit') p.open.scale.set(1.0, 0.45, 1);
  else if (m === 'talk') p.open.scale.set(0.85, 0.25 + jaw * 0.9, 1);
}

// ───────── first-person hands (real fingers) ─────────
// Right hand built palm-down, fingers toward -z; the left hand is mirrored with scale.x = -1.
export function buildRealHands(rig, skin, sleeve, opts = {}) {
  rig.clear();
  const parts = [];
  for (const side of [1, -1]) {   // right, then left
    const arm = new THREE.Group(); arm.scale.set(side, 1, 1);
    const fore = new THREE.Group(); arm.add(fore);
    const tilt = new THREE.Group(); tilt.rotation.x = 0.6; fore.add(tilt);   // forearm runs back AND down, out of frame
    part(H.geo('sleeve2', () => { const g = new THREE.CylinderGeometry(0.05, 0.062, 0.7, 24); g.rotateX(Math.PI / 2); g.translate(0, 0, 0.4); return g; }), sleeve, 'fabric', [0, 0, 0], 1, tilt);
    part(H.geo('cuff', () => { const g = new THREE.CylinderGeometry(0.054, 0.054, 0.035, 24); g.rotateX(Math.PI / 2); return g; }), shade(sleeve, 0.85), 'fabric', [0, 0, 0.06], 1, tilt);
    part(H.geo('wrist2', () => { const g = new THREE.CylinderGeometry(0.031, 0.035, 0.11, 18); g.rotateX(Math.PI / 2); g.translate(0, 0, 0.015); return g; }), skin, 'skin', [0, 0, 0.0], 1, tilt);
    if (opts.watch && side === -1) part(H.geo('watchband', () => { const g = new THREE.CylinderGeometry(0.037, 0.037, 0.025, 20); g.rotateX(Math.PI / 2); return g; }), '#212529', 'glossy', [0, 0, 0.03], 1, tilt);
    part(G.sph(), skin, 'skin', [0, 0, -0.03], [0.036, 0.022, 0.04], fore);   // wrist blend
    const palm = new THREE.Group(); palm.position.set(0, 0, -0.04); fore.add(palm);
    part(G.rbox(0.085, 0.032, 0.095, 0.015), skin, 'skin', [0, 0, -0.045], 1, palm);
    part(G.sph(), skin, 'skin', [0, -0.004, -0.02], [0.044, 0.018, 0.05], palm);   // heel of the hand
    const fingers = [];
    const fx = [-0.031, -0.0105, 0.0105, 0.03], fl = [[0.042, 0.03], [0.047, 0.033], [0.044, 0.031], [0.035, 0.025]];
    for (let i = 0; i < 4; i++) {
      const f1 = grp(palm, [fx[i], 0.002, -0.09]);
      const s1 = part(G.limb(0.0095, fl[i][0]), skin, 'skin', [0, 0, 0], 1, f1); s1.rotation.x = Math.PI / 2;
      const f2 = grp(f1, [0, 0, -fl[i][0]]);
      const s2 = part(G.limb(0.0088, fl[i][1]), skin, 'skin', [0, 0, 0], 1, f2); s2.rotation.x = Math.PI / 2;
      part(G.rbox(0.013, 0.003, 0.012, 0.0014), shade(skin, 1.18), 'glossy', [0, 0.008, -fl[i][1] - 0.002], 1, f2, false);   // nail
      fingers.push([f1, f2]);
    }
    const t1 = grp(palm, [-0.045, -0.004, -0.03]); t1.rotation.set(0, 0.7, 0);
    const ts1 = part(G.limb(0.012, 0.035), skin, 'skin', [0, 0, 0], 1, t1); ts1.rotation.x = Math.PI / 2;
    const t2 = grp(t1, [0, 0, -0.035]);
    const ts2 = part(G.limb(0.011, 0.028), skin, 'skin', [0, 0, 0], 1, t2); ts2.rotation.x = Math.PI / 2;
    part(G.rbox(0.014, 0.003, 0.012, 0.0014), shade(skin, 1.18), 'glossy', [0, 0.009, -0.03], 1, t2, false);
    rig.add(arm); parts.push({ arm, fore, palm, fingers, thumb: [t1, t2], side });
  }
  rig.userData.parts = parts; rig.userData.real = true;
}

// pose: [pos xyz (camera space), rot xyz (of forearm), finger curls [thumb, index, middle, ring, pinky] 0..1.6]
// Vertical frame: at depth d the visible half-width is ~0.33d and half-height ~0.6d, so hands live near x≈±0.1.
const RH = {
  idle: [[0.12, -0.24, -0.36], [0.4, 0.2, 0.3], [0.3, 0.35, 0.45, 0.55, 0.65]],
  point: [[0.065, -0.17, -0.34], [0.05, 0.12, 0.15], [1.0, 0.0, 1.5, 1.5, 1.5]],
  reach: [[0.07, -0.14, -0.36], [0.05, 0.12, 0.15], [0.1, 0.05, 0.08, 0.1, 0.12]],
  hold: [[0.07, -0.18, -0.34], [0.15, 0.25, 0.9], [0.7, 0.9, 1.0, 1.05, 1.1]],
  wave: [[0.09, -0.15, -0.4], [-1.3, 0.1, -0.15], [0.05, 0.0, 0.0, 0.05, 0.1]],
  shrug: [[0.11, -0.21, -0.36], [0.2, 0.2, 2.6], [0.2, 0.15, 0.2, 0.25, 0.3]],
  facepalm: [[0.02, -0.16, -0.2], [-1.4, 0.0, 3.1], [0.2, 0.1, 0.1, 0.15, 0.2]],
  shield: [[0.09, -0.1, -0.36], [-1.35, 0.2, 0.25], [0.1, 0.0, 0.0, 0.05, 0.1]],
  run: [[0.11, -0.22, -0.36], [0.4, 0.2, 0.6], [1.0, 1.3, 1.4, 1.45, 1.5]],
  cheer: [[0.11, -0.02, -0.42], [-1.4, 0.1, -0.25], [1.0, 1.3, 1.4, 1.45, 1.5]],
  thumbsup: [[0.06, -0.16, -0.38], [0.15, 0.1, -1.5], [-1.7, 1.5, 1.55, 1.55, 1.55]],
  fist: [[0.09, -0.17, -0.36], [0.05, 0.15, 0.9], [1.0, 1.5, 1.55, 1.55, 1.55]],
  peace: [[0.08, -0.12, -0.4], [-1.35, 0.1, -0.1], [1.2, 0.0, 0.0, 1.5, 1.5]],
  stop: [[0.06, -0.13, -0.36], [-1.45, 0.0, 0.0], [0.05, 0.0, 0.0, 0.0, 0.0]],
  offer: [[0.07, -0.2, -0.36], [0.2, 0.15, 3.0], [0.3, 0.15, 0.15, 0.2, 0.25]],
  phone: [[0.025, -0.2, -0.3], [-0.95, 0.0, 3.14], [0.3, 0.15, 0.15, 0.2, 0.25]],
  wheel: [[0.13, -0.25, -0.43], [-0.5, 0.35, 1.2], [0.9, 1.2, 1.3, 1.35, 1.4]],
  type: [[0.08, -0.27, -0.36], [0.5, 0.0, 0.1], [0.4, 0.55, 0.6, 0.65, 0.7]],
  grab: [[0.07, -0.14, -0.4], [0.0, 0.2, 0.5], [0.6, 0.8, 0.85, 0.9, 0.95]],
  count: [[0.08, -0.12, -0.4], [-1.35, 0.1, -0.1], [1.2, 0.0, 0.0, 0.0, 1.5]],
  money: [[0.05, -0.17, -0.34], [-0.6, 0.1, 0.0], [0.6, 0.6, 0.65, 0.7, 0.75]],
};
const REST = [[0.13, -0.29, -0.36], [0.4, 0.2, 0.3], [0.3, 0.35, 0.45, 0.55, 0.65]];   // the free hand in one-hand poses
const LH = Object.fromEntries(['point', 'wave', 'facepalm', 'thumbsup', 'peace', 'phone', 'count', 'money', 'stop'].map(k => [k, REST]));
export const REAL_POSES = Object.keys(RH);
export function poseRealHands(rig, pose, t, opts = {}) {
  if (pose === 'none') { rig.visible = false; return; }
  rig.visible = true;
  const P = RH[pose] ? pose : 'idle';
  rig.userData.parts.forEach((h, i) => {
    const Q = (i === 1 && LH[P]) ? LH[P] : RH[P];
    let [x, y, z] = Q[0]; const [rx, ry, rz] = Q[1]; const curl = Q[2];
    let bob = Math.sin(t * 2.0 + i * 1.7) * 0.005, dx = 0;
    if (P === 'run') bob = Math.sin(t * 12 + i * Math.PI) * 0.06;
    if (P === 'cheer') bob = Math.abs(Math.sin(t * 8 + i)) * 0.05;
    if (P === 'type') bob = Math.max(0, Math.sin(t * 20 + i * 2.1)) * 0.01;
    if (P === 'wave' && i === 0) dx = Math.sin(t * 11) * 0.03;
    h.arm.position.set(h.side * (x + dx), y + bob - 0.02, z);
    h.fore.rotation.set(-rx, ry, 0); h.palm.rotation.z = rz;   // roll only the hand, so sleeves keep pointing down-back   // (-rx: negative table values tip the fingers up). The left arm group is mirrored, so poses mirror for free
    if (P === 'wave' && i === 0) h.fore.rotation.z = Math.sin(t * 11) * 0.25;
    h.arm.rotation.set(0, 0, 0);
    const c = curl.map(v => v + (P === 'idle' ? Math.sin(t * 1.3 + i) * 0.04 : 0));
    h.fingers.forEach((f, k) => { const v = c[k + 1]; f[0].rotation.x = -v * 0.9; f[1].rotation.x = -v * 0.85; });
    h.thumb[0].rotation.set(-c[0] * 0.5, 0.7 - c[0] * 0.5, 0); h.thumb[1].rotation.x = -c[0] * 0.6;
  });
}

// ───────── phone screen texture (for hands="phone") ─────────
export function phoneScreenTexture(spec) {
  const cv = document.createElement('canvas'); cv.width = 540; cv.height = 1100; const c = cv.getContext('2d');
  const bg = spec.bg || '#ffffff', fg = spec.fg || '#111111', acc = spec.accent || '#228be6';
  c.fillStyle = bg; c.fillRect(0, 0, 540, 1100);
  c.fillStyle = fg; c.font = '600 30px Inter, sans-serif'; c.textAlign = 'left'; c.fillText(spec.time || '9:41', 40, 60);
  c.textAlign = 'right'; c.fillText('▮▮▮ ◔', 500, 60);
  c.textAlign = 'center';
  if (spec.app) { c.font = '800 44px Inter, sans-serif'; c.fillStyle = fg; c.fillText(spec.app, 270, 150); c.fillStyle = 'rgba(0,0,0,0.08)'; c.fillRect(0, 185, 540, 2); }
  let y = 260;
  if (spec.big) { c.font = '900 120px Inter, "Noto Color Emoji", sans-serif'; c.fillStyle = spec.bigColor || acc; c.fillText(spec.big, 270, y + 90); y += 180; }
  if (spec.sub) { c.font = '600 38px Inter, sans-serif'; c.fillStyle = '#868e96'; c.fillText(spec.sub, 270, y); y += 70; }
  for (const m of spec.messages || []) {   // chat bubbles: [who, text]  who: 'me' | 'them'
    const me = m[0] === 'me'; c.font = '600 36px Inter, "Noto Color Emoji", sans-serif';
    const words = m[1].split(' '); const lines = [''];
    for (const wd of words) { const tl = lines[lines.length - 1] + (lines[lines.length - 1] ? ' ' : '') + wd; if (c.measureText(tl).width > 340) lines.push(wd); else lines[lines.length - 1] = tl; }
    const bw = Math.max(...lines.map(l => c.measureText(l).width)) + 50, bh = lines.length * 46 + 30;
    const x = me ? 500 - bw : 40;
    c.fillStyle = me ? acc : '#e9ecef'; c.beginPath(); c.roundRect(x, y, bw, bh, 30); c.fill();
    c.fillStyle = me ? '#ffffff' : '#111111'; c.textAlign = 'left'; lines.forEach((l, i) => c.fillText(l, x + 25, y + 52 + i * 46)); c.textAlign = 'center';
    y += bh + 22;
  }
  for (const l of spec.lines || []) { c.font = '600 40px Inter, "Noto Color Emoji", sans-serif'; c.fillStyle = fg; c.fillText(l, 270, y); y += 64; }
  if (spec.button) { c.fillStyle = acc; c.beginPath(); c.roundRect(70, 930, 400, 100, 50); c.fill(); c.fillStyle = '#fff'; c.font = '800 40px Inter, sans-serif'; c.fillText(spec.button, 270, 995); }
  const tx = new THREE.CanvasTexture(cv); tx.colorSpace = THREE.SRGBColorSpace; return tx;
}
