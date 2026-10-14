// 更多环境：suburb / park / fields / forest / mountains / volcano / coast / outback / ancient / interior / globe / map。
// 约定与 world.js 相同：返回 {root, sky?, outdoor, fog, light, defaults?, windowMats?, static?, update(fr, p, beat)}。
import * as THREE from "three";
import {
  std, rng, hash, skyDome, stars, canvasTex, Chunks, palm, lamp, pedestrian, makeCar, CAR_COLORS,
  makeEarth, addOvergrowth, addDebris,
} from "./common.js";

const SOFT = canvasTex(128, 128, (x) => {
  const g = x.createRadialGradient(64, 64, 0, 64, 64, 64);
  g.addColorStop(0, "rgba(255,255,255,1)"); g.addColorStop(1, "rgba(255,255,255,0)");
  x.fillStyle = g; x.fillRect(0, 0, 128, 128);
}, false);

function groundTex(base, specks, seed, scale = 40) {
  const t = canvasTex(512, 512, (x, w, h) => {
    const r = rng(seed);
    x.fillStyle = base; x.fillRect(0, 0, w, h);
    for (let i = 0; i < 5000; i++) { x.fillStyle = specks[Math.floor(r() * specks.length)]; x.globalAlpha = 0.05 + r() * 0.12; x.fillRect(r() * w, r() * h, 2 + r() * 3, 2 + r() * 3); }
    x.globalAlpha = 1;
  });
  t.repeat.set(scale, scale);
  return t;
}

function bigGround(color, tex) {
  const m = new THREE.Mesh(new THREE.PlaneGeometry(6000, 6000), std(tex ? "#ffffff" : color, { map: tex || null, roughness: 1 }));
  m.rotation.x = -Math.PI / 2;
  m.receiveShadow = true;
  return m;
}

const trunkMat = std("#6b5240");
const leafMats = ["#4f7a3a", "#5e8a40", "#3f6a35", "#6f8f45"].map((c) => std(c, { flatShading: true }));
const pineMat = std("#2f5a3a", { flatShading: true });
function roundTree(r, s = 1) {
  const g = new THREE.Group();
  const tr = new THREE.Mesh(new THREE.CylinderGeometry(0.18, 0.26, 2.6, 6), trunkMat);
  tr.position.y = 1.3; tr.castShadow = true;
  const top = new THREE.Mesh(new THREE.IcosahedronGeometry(2, 0), leafMats[Math.floor(r() * leafMats.length)]);
  top.position.y = 3.6; top.scale.set(1, 0.9 + r() * 0.3, 1); top.castShadow = true;
  g.add(tr, top);
  g.scale.setScalar(s);
  return g;
}
function pineTree(r, s = 1, mat = pineMat) {
  const g = new THREE.Group();
  const tr = new THREE.Mesh(new THREE.CylinderGeometry(0.15, 0.22, 2, 6), trunkMat);
  tr.position.y = 1;
  g.add(tr);
  for (let i = 0; i < 3; i++) {
    const c = new THREE.Mesh(new THREE.ConeGeometry(1.8 - i * 0.45, 2.4, 7), mat);
    c.position.y = 2.4 + i * 1.3; c.castShadow = true;
    g.add(c);
  }
  g.scale.setScalar(s * (0.8 + r() * 0.5));
  return g;
}

function roadStrip(g, L, x0, x1, color = "#3b3e44", dashes = true) {
  const road = new THREE.Mesh(new THREE.PlaneGeometry(x1 - x0, L), std(color, { roughness: 0.95 }));
  road.rotation.x = -Math.PI / 2;
  road.position.set((x0 + x1) / 2, 0.01, -L / 2);
  road.receiveShadow = true;
  g.add(road);
  if (dashes) {
    const white = new THREE.MeshBasicMaterial({ color: 0xe9e9e4 });
    for (let d = 0; d < L; d += 10) {
      const m = new THREE.Mesh(new THREE.PlaneGeometry(0.14, 4), white);
      m.rotation.x = -Math.PI / 2;
      m.position.set((x0 + x1) / 2 - 1.75, 0.02, -d - 3);
      g.add(m);
    }
  }
}

function peds(g, r, n, x0, x1, L) {
  for (let i = 0; i < n; i++) {
    const p = pedestrian(r);
    p.position.set(x0 + r() * (x1 - x0), 0.02, -r() * L);
    p.rotation.y = r() < 0.5 ? 0 : Math.PI;
    g.add(p);
  }
}

function cars(g, r, xs, L, density = 0.5) {
  for (const lx of xs) for (let z = r() * 8; z < L - 4; z += 8 + r() * 12) {
    if (r() > density + 0.2) continue;
    const car = makeCar(CAR_COLORS[Math.floor(r() * CAR_COLORS.length)]);
    car.position.set(lx, 0, -z - 2.5);
    if (lx < 0) car.rotation.y = Math.PI;
    car.userData = { tag: "car", rank: r() };
    g.add(car);
  }
}

function chunked(L, make, n, back, ahead, extra) {
  const chunks = new Chunks(L, make, n, back, ahead);
  const root = new THREE.Group();
  root.add(chunks.group);
  return { root, chunks, ...extra };
}

// ----------------------------------------------------------------- suburb ---
const HOUSE = ["#e9d8c4", "#cfe0e8", "#f2e6b8", "#e8c9cf", "#d8e3cf", "#ece9e2", "#c9d1e4"];
const ROOF = ["#5a4a45", "#6b3a33", "#3f4650", "#7a6a5a"];
function house(r) {
  const g = new THREE.Group();
  const w = 7 + r() * 3, d = 8, h = 3 + r() * 3.2;
  const body = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), std(HOUSE[Math.floor(r() * HOUSE.length)]));
  body.position.y = h / 2; body.castShadow = true; body.receiveShadow = true;
  const roofG = new THREE.CylinderGeometry(0.01, w * 0.62, 2.2, 4, 1);
  roofG.rotateY(Math.PI / 4);
  const roof = new THREE.Mesh(roofG, std(ROOF[Math.floor(r() * ROOF.length)], { flatShading: true }));
  roof.scale.set(1, 1, d / w * 1.05);
  roof.position.y = h + 1.1; roof.castShadow = true;
  g.add(body, roof);
  const winM = std("#2d3846", { emissive: 0xffd38a, emissiveIntensity: 0 });
  g.userData.win = winM;
  for (let i = 0; i < 2; i++) for (let j = 0; j < Math.floor(h / 2.6) + 1; j++) {
    const wv = new THREE.Mesh(new THREE.BoxGeometry(1.1, 1.2, 0.08), winM);
    wv.position.set(-w / 4 + i * w / 2, 1.6 + j * 2.4, -d / 2 - 0.02);
    g.add(wv);
  }
  const door = new THREE.Mesh(new THREE.BoxGeometry(1, 2, 0.1), std("#5a3e2e"));
  door.position.set(0, 1, -d / 2 - 0.03);
  g.add(door);
  return g;
}
export function suburbEnv() {
  const L = 44;
  const lawn = std("#7a9a55", { roughness: 1 });
  const walk = std("#b9b6ad");
  const winMats = [];
  const make = (vi) => {
    const r = rng(300 + vi * 17);
    const g = new THREE.Group();
    roadStrip(g, L, -5.25, 3.5);
    for (const [x0, x1] of [[3.5, 6], [-7.75, -5.25]]) {
      const s = new THREE.Mesh(new THREE.BoxGeometry(x1 - x0, 0.15, L), walk);
      s.position.set((x0 + x1) / 2, 0.075, -L / 2); s.receiveShadow = true; g.add(s);
    }
    for (const side of [1, -1]) {
      const ln = new THREE.Mesh(new THREE.PlaneGeometry(20, L), lawn);
      ln.rotation.x = -Math.PI / 2; ln.position.set(side > 0 ? 16 : -17.75, 0.02, -L / 2); ln.receiveShadow = true;
      g.add(ln);
      for (let z = 4; z < L; z += 13 + r() * 3) {
        const h = house(r);
        h.position.set(side > 0 ? 15 : -16.75, 0, -z - 4);
        h.rotation.y = side > 0 ? -Math.PI / 2 : Math.PI / 2;
        winMats.push(h.userData.win);
        g.add(h);
        if (r() < 0.7) { const t = roundTree(r, 0.8 + r() * 0.4); t.position.set(side > 0 ? 8 + r() * 2 : -10 - r() * 2, 0, -z - r() * 6); g.add(t); }
      }
    }
    cars(g, r, [1.75, -1.75, 4.6, -6.4], L, 0.45);
    peds(g, r, 6, 3.7, 5.8, L); peds(g, r, 6, -7.6, -5.4, L);
    addOvergrowth(g, r, -12, 12, L, 30);
    addDebris(g, r, -5, 3, L, 8);
    return g;
  };
  const e = chunked(L, make, 6, 2, 8, {});
  e.root.add(bigGround("#7d9a5a"));
  const sky = skyDome("#6f9fd0", "#d8e6ee", "#b9c7a8");
  e.root.add(sky);
  return {
    ...e, sky, outdoor: true, windowMats: winMats, defaults: { crowd: 0.3, traffic: 0.5 },
    fog: new THREE.Fog(0xcfdde6, 80, 520),
    light: { sun: 2.6, hemi: 1.1, sunDir: [-0.6, 1, 0.3], sky: 0xe6f0ff, ground: 0x6d7a55 },
    update(fr, p) { e.chunks.update(fr.z || 0); e.root.children[1].position.set(p.x, 0, p.z); sky.position.copy(p); },
  };
}

// ------------------------------------------------------------------- park ---
function bench() {
  const g = new THREE.Group();
  const wood = std("#8a6440"), iron = std("#2b2e33");
  const seat = new THREE.Mesh(new THREE.BoxGeometry(1.8, 0.08, 0.5), wood); seat.position.y = 0.5;
  const back = new THREE.Mesh(new THREE.BoxGeometry(1.8, 0.45, 0.06), wood); back.position.set(0, 0.85, 0.24);
  g.add(seat, back);
  for (const x of [-0.8, 0.8]) { const l = new THREE.Mesh(new THREE.BoxGeometry(0.06, 0.5, 0.5), iron); l.position.set(x, 0.25, 0); g.add(l); }
  g.traverse((o) => { if (o.isMesh) o.castShadow = true; });
  return g;
}
function playground(r) {
  const g = new THREE.Group();
  const red = std("#c8462e"), metal = std("#5a6470", { metalness: 0.3 }), yellow = std("#e0b33a");
  for (const x of [-2, 2]) for (const z of [-0.8, 0.8]) {
    const p = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.06, 3.2, 6), red);
    p.position.set(x, 1.5, z); p.rotation.z = (z > 0 ? 1 : -1) * 0; p.rotation.x = z > 0 ? -0.25 : 0.25;
    g.add(p);
  }
  const top = new THREE.Mesh(new THREE.CylinderGeometry(0.07, 0.07, 4.2, 6), red); top.rotation.z = Math.PI / 2; top.position.y = 3.05; g.add(top);
  for (const x of [-1, 1]) {
    const seat = new THREE.Mesh(new THREE.BoxGeometry(0.5, 0.06, 0.25), yellow); seat.position.set(x, 0.6, 0);
    for (const dx of [-0.2, 0.2]) { const ch = new THREE.Mesh(new THREE.CylinderGeometry(0.01, 0.01, 2.4, 3), metal); ch.position.set(x + dx, 1.8, 0); g.add(ch); }
    g.add(seat);
  }
  const slide = new THREE.Mesh(new THREE.BoxGeometry(0.8, 0.08, 4), yellow);
  slide.position.set(5, 1.1, 0); slide.rotation.x = 0.5;
  const tower = new THREE.Mesh(new THREE.BoxGeometry(1.4, 2.2, 1.4), red); tower.position.set(5, 1.1, -2.4);
  g.add(slide, tower);
  g.traverse((o) => { if (o.isMesh) o.castShadow = true; });
  return g;
}
export function parkEnv() {
  const L = 50;
  const gt = groundTex("#6f8f48", ["#5a7a3a", "#86a35a", "#4f6a35"], 21);
  const path = std("#c9b99a", { roughness: 1 });
  const make = (vi) => {
    const r = rng(700 + vi * 29);
    const g = new THREE.Group();
    const pth = new THREE.Mesh(new THREE.PlaneGeometry(4, L), path);
    pth.rotation.x = -Math.PI / 2; pth.position.set(0, 0.02, -L / 2); pth.receiveShadow = true;
    g.add(pth);
    for (let i = 0; i < 16; i++) {
      const side = r() < 0.5 ? -1 : 1;
      const t = r() < 0.7 ? roundTree(r, 0.9 + r() * 0.6) : pineTree(r, 1.1);
      t.position.set(side * (4 + r() * 30), 0, -r() * L);
      g.add(t);
    }
    for (let z = 6; z < L; z += 16) { const b = bench(); b.position.set(2.8, 0, -z); b.rotation.y = -Math.PI / 2; g.add(b); }
    const l = lamp(); l.position.set(-2.6, 0, -L / 2); g.add(l);
    if (vi % 2 === 0) { const pg = playground(r); pg.position.set(-11, 0, -L / 2); g.add(pg); }
    peds(g, r, 10, -12, 12, L);
    addOvergrowth(g, r, -6, 6, L, 26);
    return g;
  };
  const e = chunked(L, make, 4, 2, 6, {});
  const ground = bigGround(null, gt);
  e.root.add(ground);
  const sky = skyDome("#6f9fd0", "#dbe8ee", "#a9c08a");
  e.root.add(sky);
  return {
    ...e, sky, outdoor: true, defaults: { crowd: 0.35, traffic: 0 },
    fog: new THREE.Fog(0xd6e2e6, 60, 420),
    light: { sun: 2.6, hemi: 1.1, sunDir: [-0.4, 1, 0.5], sky: 0xeaf2ff, ground: 0x5f7a40 },
    update(fr, p) { e.chunks.update(fr.z || 0); ground.position.set(p.x, 0, p.z); gt.offset.set(p.x / 150, -p.z / 150); sky.position.copy(p); },
  };
}

// ----------------------------------------------------------------- fields ---
export function fieldsEnv() {
  const L = 60;
  const crop = canvasTex(256, 256, (x, w, h) => {
    x.fillStyle = "#b9a35a"; x.fillRect(0, 0, w, h);
    for (let i = 0; i < 16; i++) { x.fillStyle = i % 2 ? "#a38c48" : "#c7b468"; x.fillRect(i * 16, 0, 9, h); }
  });
  crop.repeat.set(60, 60);
  const dirt = std("#9a7d58", { roughness: 1 });
  const red = std("#8f2f26"), white = std("#e8e2d6"), grey = std("#9aa0a6", { metalness: 0.3 });
  const make = (vi) => {
    const r = rng(1100 + vi * 13);
    const g = new THREE.Group();
    const road = new THREE.Mesh(new THREE.PlaneGeometry(5, L), dirt);
    road.rotation.x = -Math.PI / 2; road.position.set(0, 0.03, -L / 2); road.receiveShadow = true; g.add(road);
    for (const x of [-3.2, 3.2]) for (let z = 0; z < L; z += 4) {
      const post = new THREE.Mesh(new THREE.BoxGeometry(0.12, 1.2, 0.12), std("#7a5a3a")); post.position.set(x, 0.6, -z); g.add(post);
    }
    for (const x of [-3.2, 3.2]) for (const y of [0.5, 1]) {
      const rail = new THREE.Mesh(new THREE.BoxGeometry(0.05, 0.06, L), std("#8a6a48")); rail.position.set(x, y, -L / 2); g.add(rail);
    }
    if (vi % 2 === 0) {
      const side = vi % 4 === 0 ? 1 : -1;
      const barn = new THREE.Group();
      const b = new THREE.Mesh(new THREE.BoxGeometry(10, 6, 14), red); b.position.y = 3; b.castShadow = true;
      const roofG = new THREE.CylinderGeometry(0.01, 7.5, 3.4, 4); roofG.rotateY(Math.PI / 4);
      const roof = new THREE.Mesh(roofG, std("#3f3a38", { flatShading: true })); roof.scale.set(1, 1, 1.4); roof.position.y = 7.7;
      const sil = new THREE.Mesh(new THREE.CylinderGeometry(2.2, 2.2, 12, 14), grey); sil.position.set(8, 6, 0); sil.castShadow = true;
      const dome = new THREE.Mesh(new THREE.SphereGeometry(2.2, 14, 8, 0, Math.PI * 2, 0, Math.PI / 2), grey); dome.position.set(8, 12, 0);
      const trim = new THREE.Mesh(new THREE.BoxGeometry(10.1, 0.3, 14.1), white); trim.position.y = 6;
      barn.add(b, roof, sil, dome, trim);
      barn.position.set(side * 26, 0, -L / 2);
      g.add(barn);
    }
    for (let i = 0; i < 6; i++) { const hay = new THREE.Mesh(new THREE.CylinderGeometry(0.8, 0.8, 1.2, 12), std("#d1b56a")); hay.rotation.z = Math.PI / 2; hay.position.set((r() < 0.5 ? -1 : 1) * (8 + r() * 40), 0.8, -r() * L); hay.castShadow = true; g.add(hay); }
    for (let i = 0; i < 4; i++) { const t = roundTree(r, 1.2); t.position.set((r() < 0.5 ? -1 : 1) * (60 + r() * 40), 0, -r() * L); g.add(t); }
    if (r() < 0.5) { const tr = makeCar("#3f7a3a"); tr.scale.set(1.2, 1.4, 0.9); tr.position.set(12 + r() * 20, 0, -r() * L); tr.rotation.y = 1.3; tr.userData = { tag: "car", rank: r() }; g.add(tr); }
    peds(g, r, 3, -14, 14, L);
    addOvergrowth(g, r, -2.5, 2.5, L, 14);
    return g;
  };
  const e = chunked(L, make, 4, 2, 9, {});
  const ground = bigGround(null, crop);
  e.root.add(ground);
  const sky = skyDome("#5f97d6", "#e3ecf0", "#c9b98a");
  e.root.add(sky);
  return {
    ...e, sky, outdoor: true, defaults: { crowd: 0.2, traffic: 0.3 },
    fog: new THREE.Fog(0xe0e6e2, 120, 1200),
    light: { sun: 2.8, hemi: 1.0, sunDir: [0.5, 1, 0.2], sky: 0xeef4ff, ground: 0x9a8a55 },
    update(fr, p) { e.chunks.update(fr.z || 0); ground.position.set(p.x, 0, p.z); crop.offset.set(p.x / 100, -p.z / 100); sky.position.copy(p); },
  };
}

// ----------------------------------------------------------------- forest ---
export function forestEnv() {
  const L = 40;
  const gt = groundTex("#4a5a35", ["#3a4a2a", "#5a6a3a", "#6a5a40"], 33);
  const trail = std("#7a6448", { roughness: 1 });
  const rock = std("#7d7b74", { flatShading: true });
  const make = (vi) => {
    const r = rng(1500 + vi * 19);
    const g = new THREE.Group();
    const t = new THREE.Mesh(new THREE.PlaneGeometry(2.6, L), trail);
    t.rotation.x = -Math.PI / 2; t.position.set(0, 0.02, -L / 2); g.add(t);
    for (let i = 0; i < 46; i++) {
      const side = r() < 0.5 ? -1 : 1;
      const tr = r() < 0.65 ? pineTree(r, 1.4 + r()) : roundTree(r, 1 + r() * 0.6);
      tr.position.set(side * (2.4 + Math.pow(r(), 1.6) * 40), 0, -r() * L);
      g.add(tr);
    }
    for (let i = 0; i < 6; i++) { const m = new THREE.Mesh(new THREE.DodecahedronGeometry(0.4 + r(), 0), rock); m.position.set((r() - 0.5) * 30, 0.2, -r() * L); m.castShadow = true; g.add(m); }
    peds(g, r, 2, -1, 1, L);
    return g;
  };
  const e = chunked(L, make, 5, 2, 6, {});
  const ground = bigGround(null, gt);
  e.root.add(ground);
  const sky = skyDome("#7f9fbf", "#c9d6d6", "#6a7a5a");
  e.root.add(sky);
  return {
    ...e, sky, outdoor: true, defaults: { crowd: 0, traffic: 0 },
    fog: new THREE.Fog(0xa9b8a8, 20, 160),
    light: { sun: 2.0, hemi: 0.9, sunDir: [-0.3, 1, 0.6], sky: 0xdfe8e0, ground: 0x3a4a2a },
    update(fr, p) { e.chunks.update(fr.z || 0); ground.position.set(p.x, 0, p.z); gt.offset.set(p.x / 150, -p.z / 150); sky.position.copy(p); },
  };
}

// -------------------------------------------------------------- mountains ---
function mountainRing(seed, R0, color, snow = true) {
  const r = rng(seed);
  const g = new THREE.Group();
  const m = std(color, { flatShading: true }), sm = std("#f2f4f6", { flatShading: true });
  for (let i = 0; i < 26; i++) {
    const a = (i / 26) * Math.PI * 2 + r() * 0.1;
    const R = R0 + r() * R0 * 0.4;
    const h = 120 + r() * 260, w = 160 + r() * 200;
    const c = new THREE.Mesh(new THREE.ConeGeometry(w, h, 6 + Math.floor(r() * 3), 1), m);
    c.position.set(Math.cos(a) * R, h / 2 - 5, Math.sin(a) * R);
    c.rotation.y = r() * 6;
    g.add(c);
    if (snow && h > 220) {
      const cap = new THREE.Mesh(new THREE.ConeGeometry(w * 0.3, h * 0.3, 6), sm);
      cap.position.set(c.position.x, h - 5 - h * 0.15 + 1, c.position.z); cap.rotation.y = c.rotation.y;
      g.add(cap);
    }
  }
  return g;
}
export function mountainsEnv() {
  const L = 50;
  const gt = groundTex("#7a8a5a", ["#6a7a4a", "#8a9a6a", "#8a8070"], 44);
  const make = (vi) => {
    const r = rng(1900 + vi * 7);
    const g = new THREE.Group();
    roadStrip(g, L, -3.5, 3.5, "#45474b", false);
    for (let i = 0; i < 14; i++) { const t = pineTree(r, 1.2 + r()); t.position.set((r() < 0.5 ? -1 : 1) * (6 + r() * 40), 0, -r() * L); g.add(t); }
    for (let i = 0; i < 5; i++) { const m = new THREE.Mesh(new THREE.DodecahedronGeometry(1 + r() * 2, 0), std("#8d8a83", { flatShading: true })); m.position.set((r() < 0.5 ? -1 : 1) * (8 + r() * 30), 0.4, -r() * L); g.add(m); }
    cars(g, r, [1.75, -1.75], L, 0.3);
    return g;
  };
  const e = chunked(L, make, 4, 2, 9, {});
  const ground = bigGround(null, gt);
  e.root.add(ground);
  const ring = mountainRing(55, 700, "#6f7a80");
  e.root.add(ring);
  const sky = skyDome("#4f86c6", "#dfeaf2", "#9aa58a");
  e.root.add(sky);
  return {
    ...e, sky, outdoor: true, defaults: { crowd: 0, traffic: 0.3 },
    fog: new THREE.Fog(0xd5e0e8, 150, 1600),
    light: { sun: 2.8, hemi: 1.0, sunDir: [0.4, 1, -0.3], sky: 0xeaf2ff, ground: 0x6a7a4a },
    update(fr, p) { e.chunks.update(fr.z || 0); ground.position.set(p.x, 0, p.z); gt.offset.set(p.x / 150, -p.z / 150); ring.position.set(p.x, 0, p.z); sky.position.copy(p); },
  };
}

// ---------------------------------------------------------------- volcano ---
export function volcanoEnv() {
  const L = 50;
  const gt = groundTex("#5f6a48", ["#4a5238", "#6f7650", "#5a5048"], 66);
  const make = (vi) => {
    const r = rng(2300 + vi * 11);
    const g = new THREE.Group();
    roadStrip(g, L, -3.5, 3.5, "#45474b", false);
    for (let i = 0; i < 16; i++) { const t = pineTree(r, 1.1 + r()); t.position.set((r() < 0.5 ? -1 : 1) * (6 + r() * 40), 0, -r() * L); g.add(t); }
    peds(g, r, 8, -6, 6, L);
    addDebris(g, r, -4, 4, L, 6);
    return g;
  };
  const e = chunked(L, make, 4, 2, 8, {});
  const ground = bigGround(null, gt);
  e.root.add(ground);
  // 火山：截顶圆锥 + 火山口光 + 烟柱（粒子）
  const v = new THREE.Group();
  const cone = new THREE.Mesh(new THREE.CylinderGeometry(60, 300, 260, 18, 4), std("#6a6058", { flatShading: true }));
  cone.position.y = 125;
  const lava = new THREE.Mesh(new THREE.CircleGeometry(56, 24), new THREE.MeshBasicMaterial({ color: 0xff6a1a, fog: false }));
  lava.rotation.x = -Math.PI / 2; lava.position.y = 256;
  const glow = new THREE.Sprite(new THREE.SpriteMaterial({ map: SOFT, color: 0xff7a2a, transparent: true, blending: THREE.AdditiveBlending, depthWrite: false, fog: false }));
  cone.material.fog = false;
  glow.scale.set(420, 260, 1); glow.position.y = 270;
  v.add(cone, lava, glow);
  const plumeN = 140;
  const smokeMat = new THREE.SpriteMaterial({ map: SOFT, color: 0x77716b, transparent: true, depthWrite: false, opacity: 0.85, fog: false });
  const plume = [];
  for (let i = 0; i < plumeN; i++) { const s = new THREE.Sprite(smokeMat.clone()); v.add(s); plume.push(s); }
  e.root.add(v);
  const sky = skyDome("#7f97b3", "#d6d9d6", "#8a8a7a");
  e.root.add(sky);
  return {
    ...e, sky, outdoor: true, defaults: { crowd: 0.2, traffic: 0.2 }, minFogFar: 2600,
    fog: new THREE.Fog(0xc9c9c0, 200, 3200),
    light: { sun: 2.4, hemi: 1.0, sunDir: [-0.4, 1, 0.4], sky: 0xe6eef2, ground: 0x4a5238 },
    update(fr, p, beat) {
      e.chunks.update(fr.z || 0);
      ground.position.set(p.x, 0, p.z); gt.offset.set(p.x / 150, -p.z / 150);
      v.position.set(p.x - 30, -5, p.z - 1600);
      sky.position.copy(p);
      const fx = beat ? beat.effects : [];
      const erupt = fx.includes("smoke") || fx.includes("fire") || fx.includes("earthquake") ? 1 : 0.15;
      glow.material.opacity = 0.35 + 0.6 * erupt;
      for (let i = 0; i < plumeN; i++) {
        const life = 6, age = ((fr.t * (0.6 + erupt) + (i / plumeN) * life) % life) / life;
        const s = plume[i];
        const h = 260 + age * (300 + 1300 * erupt);
        const spread = (20 + age * age * (200 + 900 * erupt));
        const a = i * 2.39996;
        s.position.set(Math.cos(a) * spread * 0.6, h, Math.sin(a) * spread * 0.4);
        const sc = 60 + age * (160 + 600 * erupt);
        s.scale.set(sc, sc, 1);
        s.material.opacity = (1 - age) * (0.35 + 0.5 * erupt);
        s.material.color.setHex(age < 0.08 && erupt > 0.5 ? 0xff8a3a : 0x6f6a64);
      }
    },
  };
}

// ------------------------------------------------------------------ coast ---
export function coastEnv() {
  const root = new THREE.Group();
  const seg = 100, size = 900;
  const geo = new THREE.PlaneGeometry(size, size, seg, seg);
  geo.rotateX(-Math.PI / 2);
  const base = geo.attributes.position.array.slice();
  const water = new THREE.Mesh(geo, std("#22566f", { roughness: 0.25, metalness: 0.15, flatShading: true }));
  water.position.x = -size / 2 + 8;
  root.add(water);
  const sand = new THREE.Mesh(new THREE.PlaneGeometry(400, 3000), std("#d9c49a", { roughness: 1 }));
  sand.rotation.x = -Math.PI / 2; sand.position.set(208, 0.05, 0); sand.receiveShadow = true;
  root.add(sand);
  // 栈桥 + 摩天轮 + 岸边低楼
  const pier = new THREE.Group();
  const deck = new THREE.Mesh(new THREE.BoxGeometry(8, 0.4, 160), std("#7a6248")); deck.position.set(0, 3, 0); deck.receiveShadow = true; pier.add(deck);
  for (let z = -78; z <= 78; z += 6) for (const x of [-3.6, 3.6]) { const post = new THREE.Mesh(new THREE.CylinderGeometry(0.25, 0.25, 6, 6), std("#5a4632")); post.position.set(x, 0, z); pier.add(post); }
  const lights = [];
  for (let z = -76; z <= 76; z += 12) { const l = lamp(); l.position.set(3.6, 3.2, z); l.scale.setScalar(0.8); pier.add(l); }
  const wheel = new THREE.Group();
  const rim = new THREE.Mesh(new THREE.TorusGeometry(14, 0.35, 6, 48), std("#d8d2c8", { emissive: 0xffb36a, emissiveIntensity: 0 }));
  lights.push(rim.material);
  wheel.add(rim);
  for (let i = 0; i < 16; i++) { const sp = new THREE.Mesh(new THREE.BoxGeometry(0.15, 28, 0.15), std("#bdb6aa")); sp.rotation.z = (i / 16) * Math.PI; wheel.add(sp); }
  for (let i = 0; i < 16; i++) { const c = new THREE.Mesh(new THREE.BoxGeometry(1.4, 1.4, 1.4), std(["#d0453a", "#3a7ad0", "#e0b33a"][i % 3])); const a = (i / 16) * Math.PI * 2; c.position.set(Math.cos(a) * 14, Math.sin(a) * 14, 0); wheel.add(c); }
  wheel.position.set(0, 18, -70); wheel.rotation.y = Math.PI / 2;
  pier.add(wheel);
  pier.position.set(-40, 0, -120);
  root.add(pier);
  const r = rng(77);
  const winMats = [];
  for (let i = 0; i < 26; i++) {
    const h = 6 + r() * 14, w = 8 + r() * 10;
    const wm = std(["#e8e0d0", "#d8c8b0", "#c9d0d8", "#e0d0c0"][i % 4], { emissive: 0xffd38a, emissiveIntensity: 0 });
    winMats.push(wm);
    const b = new THREE.Mesh(new THREE.BoxGeometry(14, h, w), wm);
    b.position.set(70 + r() * 30, h / 2, -i * 22 + 200); b.castShadow = true;
    root.add(b);
  }
  for (let i = 0; i < 14; i++) { const p = palm(1 + r() * 0.4); p.position.set(40 + r() * 12, 0, -i * 30 + 180); root.add(p); }
  const sky = skyDome("#5b8fc7", "#d6e2ea", "#2b5d78");
  root.add(sky);
  return {
    root, sky, outdoor: true, static: true, windowMats: winMats.concat(lights), defaults: { crowd: 0.2, traffic: 0 },
    fog: new THREE.Fog(0xc8d6de, 100, 1400),
    light: { sun: 2.6, hemi: 1.0, sunDir: [-0.6, 0.8, -0.4], sky: 0xdcecff, ground: 0x1d4256 },
    update(fr) {
      wheel.rotation.x = fr.t * 0.08;
      const a = geo.attributes.position.array, t = fr.t;
      for (let i = 0; i < a.length; i += 3) {
        const x = base[i], z = base[i + 2];
        a[i + 1] = -0.5 + Math.sin(x * 0.12 + t * 1.1) * 0.35 + Math.sin(z * 0.09 - t * 0.9) * 0.4;
      }
      geo.attributes.position.needsUpdate = true;
      geo.computeVertexNormals();
    },
  };
}

// ---------------------------------------------------------------- outback ---
export function outbackEnv() {
  const L = 60;
  const gt = groundTex("#c0663a", ["#a8552e", "#d07a48", "#8a4a2a"], 77);
  const spin = std("#9a9a52", { flatShading: true });
  const make = (vi) => {
    const r = rng(2700 + vi * 23);
    const g = new THREE.Group();
    for (let i = 0; i < 40; i++) { const m = new THREE.Mesh(new THREE.IcosahedronGeometry(0.4 + r() * 0.6, 0), spin); m.scale.y = 0.5; m.position.set((r() - 0.5) * 120, 0.1, -r() * L); m.castShadow = true; g.add(m); }
    for (let i = 0; i < 3; i++) { const t = roundTree(r, 0.8); t.position.set((r() - 0.5) * 140, 0, -r() * L); g.add(t); }
    for (let i = 0; i < 5; i++) { const m = new THREE.Mesh(new THREE.DodecahedronGeometry(0.3 + r() * 0.8, 0), std("#8a4a30", { flatShading: true })); m.position.set((r() - 0.5) * 80, 0.1, -r() * L); g.add(m); }
    return g;
  };
  const e = chunked(L, make, 4, 2, 8, {});
  const ground = bigGround(null, gt);
  e.root.add(ground);
  const ring = mountainRing(91, 900, "#9a4a2a", false);
  ring.scale.y = 0.35;
  e.root.add(ring);
  const sky = skyDome("#5f97d0", "#e8dcc8", "#c07a50");
  e.root.add(sky);
  return {
    ...e, sky, outdoor: true, defaults: { crowd: 0, traffic: 0 },
    fog: new THREE.Fog(0xe6cdb0, 150, 1500),
    light: { sun: 3.0, hemi: 0.9, sunDir: [0.5, 1, 0.3], sky: 0xfff2e0, ground: 0xa8552e },
    update(fr, p) { e.chunks.update(fr.z || 0); ground.position.set(p.x, 0, p.z); gt.offset.set(p.x / 150, -p.z / 150); ring.position.set(p.x, 0, p.z); sky.position.copy(p); },
  };
}

// ---------------------------------------------------------------- ancient ---
export function ancientEnv() {
  const L = 40;
  const stone = canvasTex(256, 256, (x, w, h) => {
    const r = rng(5);
    x.fillStyle = "#b8a888"; x.fillRect(0, 0, w, h);
    for (let j = 0; j < 8; j++) for (let i = 0; i < 4; i++) {
      const off = (j % 2) * 32;
      x.fillStyle = `hsl(38, ${18 + r() * 10}%, ${58 + r() * 10}%)`;
      x.fillRect(i * 64 + off + 2, j * 32 + 2, 60, 28);
    }
  });
  stone.repeat.set(30, 30);
  const wallTex = canvasTex(256, 256, (x, w, h) => {
    const r = rng(6);
    x.fillStyle = "#c9b896"; x.fillRect(0, 0, w, h);
    for (let j = 0; j < 10; j++) for (let i = 0; i < 5; i++) { x.fillStyle = `hsl(36, ${20 + r() * 12}%, ${62 + r() * 12}%)`; x.fillRect(i * 52 + (j % 2) * 26, j * 26, 50, 24); }
  });
  const wallM = std("#ffffff", { map: wallTex });
  const colM = std("#e6dcc8"), darkM = std("#2a221c");
  const flameMat = new THREE.SpriteMaterial({ map: SOFT, color: 0xffa040, transparent: true, blending: THREE.AdditiveBlending, depthWrite: false });
  const flames = [];
  const make = (vi) => {
    const r = rng(3100 + vi * 31);
    const g = new THREE.Group();
    for (const side of [1, -1]) {
      let z = 0;
      while (z < L) {
        const w = 6 + r() * 6, h = 4 + r() * 7, d = 8;
        const b = new THREE.Mesh(new THREE.BoxGeometry(d, h, w), wallM);
        b.position.set(side * (7 + d / 2), h / 2, -z - w / 2);
        b.castShadow = true; b.receiveShadow = true;
        g.add(b);
        for (let k = 0; k < 2; k++) { const win = new THREE.Mesh(new THREE.BoxGeometry(0.1, 0.9, 0.7), darkM); win.position.set(side * 6.95, h * 0.6, -z - w * (0.3 + k * 0.4)); g.add(win); }
        z += w + 0.4;
      }
      for (let zz = 6; zz < L; zz += 10) {
        const col = new THREE.Mesh(new THREE.CylinderGeometry(0.35, 0.42, 5.5, 12), colM);
        col.position.set(side * 5.6, 2.75, -zz); col.castShadow = true; g.add(col);
      }
      const torch = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.06, 1.2, 6), std("#4a3420"));
      torch.position.set(side * 6.8, 2.6, -L / 2);
      const fl = new THREE.Sprite(flameMat.clone()); fl.position.set(side * 6.8, 3.4, -L / 2); fl.scale.set(0.9, 1.3, 1);
      fl.userData = { tag: "flame", rank: r() };
      g.add(torch, fl);
    }
    if (r() < 0.6) { const p = palm(0.9); p.position.set((r() < 0.5 ? -1 : 1) * 4.6, 0, -r() * L); g.add(p); }
    peds(g, r, 8, -4.5, 4.5, L);
    return g;
  };
  const e = chunked(L, make, 5, 2, 6, {});
  const ground = bigGround(null, stone);
  e.root.add(ground);
  const sky = skyDome("#6f9fd0", "#e6dccb", "#c9b896");
  e.root.add(sky);
  return {
    ...e, sky, outdoor: true, defaults: { crowd: 0.2, traffic: 0 },
    fog: new THREE.Fog(0xe0d6c4, 60, 500),
    light: { sun: 2.8, hemi: 1.0, sunDir: [0.5, 1, 0.3], sky: 0xfff4e0, ground: 0xa89878 },
    update(fr, p) {
      e.chunks.update(fr.z || 0); ground.position.set(p.x, 0, p.z); stone.offset.set(p.x / 200, -p.z / 200); sky.position.copy(p);
      e.root.traverse((o) => { if (o.userData && o.userData.tag === "flame") { const k = 0.85 + 0.25 * Math.sin(fr.t * 17 + o.userData.rank * 40); o.scale.set(0.9 * k, 1.3 * k, 1); } });
    },
  };
}

// --------------------------------------------------------------- interior ---
const ROOM_DIMS = {
  hospital: [16, 22, 4], operating_room: [12, 14, 4], classroom: [14, 16, 3.6], nursery: [12, 14, 3.4], office: [18, 22, 3.4],
  store: [18, 26, 5], home: [10, 12, 3], lab: [14, 18, 3.6], court: [18, 24, 7], hall: [22, 30, 9], bunker: [12, 20, 3],
};
const ROOM_COLORS = {
  hospital: ["#dfe6e8", "#b9c6c9"], operating_room: ["#cfe0e0", "#9db5b5"], classroom: ["#e8e0cf", "#a68a62"],
  nursery: ["#f0e6e0", "#d8cfc4"], office: ["#e2e2df", "#8a8f96"], store: ["#efefe9", "#cfcfc8"], home: ["#e8dccb", "#8a6a4a"],
  lab: ["#e6ecef", "#bfc9cc"], court: ["#c9b38f", "#8a6a48"], hall: ["#b04030", "#d8ccb4"], bunker: ["#8d8f8c", "#5f625f"],
};

function box(w, h, d, color, x, y, z, o = {}) {
  const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), typeof color === "string" ? std(color, o) : color);
  m.position.set(x, y, z);
  m.castShadow = true; m.receiveShadow = true;
  return m;
}

function furnish(g, room, W, D, r) {
  const add = (m) => { g.add(m); return m; };
  const rowsZ = (n, z0, dz) => [...Array(n)].map((_, i) => z0 - i * dz);
  switch (room) {
    case "hospital":
      for (const side of [-1, 1]) for (const z of rowsZ(4, -3, 4.2)) {
        add(box(1.1, 0.12, 2.1, "#e8eef0", side * (W / 2 - 2), 0.75, z));
        add(box(1.0, 0.2, 2.0, "#f6f8f8", side * (W / 2 - 2), 0.9, z));
        add(box(0.6, 0.12, 0.4, "#ffffff", side * (W / 2 - 2), 1.06, z - 0.75));
        add(box(0.06, 1.6, 0.06, "#b0b8bc", side * (W / 2 - 1.2), 0.8, z - 1.1));
        add(box(0.5, 0.4, 0.1, "#1a2228", side * (W / 2 - 0.4), 1.6, z, { emissive: 0x2a8a5a, emissiveIntensity: 0.6 }));
        add(box(0.04, 2.2, 1.9, "#a8c6d0", side * (W / 2 - 3.1), 1.4, z));
      }
      break;
    case "operating_room": {
      add(box(0.9, 0.9, 2.2, "#5a6a74", 0, 0.45, -5));
      add(box(1.0, 0.12, 2.3, "#8fd0c9", 0, 0.96, -5));
      const lampG = new THREE.Mesh(new THREE.CylinderGeometry(1.0, 1.2, 0.3, 24), std("#e6ecef", { emissive: 0xffffff, emissiveIntensity: 0.4 }));
      lampG.position.set(0, 3.1, -5); add(lampG);
      add(box(0.06, 1.2, 0.06, "#b0b8bc", 0, 3.6, -5));
      add(box(1.2, 1.0, 0.6, "#cfd8dc", 2.6, 0.5, -4));
      add(box(0.9, 0.6, 0.1, "#101418", -2.6, 1.8, -6, { emissive: 0x3a9a6a, emissiveIntensity: 0.5 }));
      break;
    }
    case "classroom":
      for (const x of [-4.5, -1.5, 1.5, 4.5]) for (const z of rowsZ(4, -3, 2.4)) {
        add(box(1.2, 0.06, 0.7, "#c9a878", x, 0.75, z));
        for (const dx of [-0.5, 0.5]) add(box(0.05, 0.75, 0.05, "#5a5a5a", x + dx, 0.37, z));
        add(box(0.5, 0.05, 0.5, "#3b6a9a", x, 0.45, z + 0.6));
      }
      add(box(6, 1.6, 0.08, "#f4f6f4", 0, 1.8, -D + 4.3));
      add(box(1.8, 0.8, 0.8, "#8a6a48", 3.5, 0.4, -D + 6));
      break;
    case "nursery":
      for (const x of [-3.6, -1.2, 1.2, 3.6]) for (const z of rowsZ(3, -3, 3)) {
        add(box(1.1, 0.12, 0.7, "#f2ece6", x, 0.75, z));
        for (const [dx, dz] of [[-0.55, 0], [0.55, 0]]) add(box(0.04, 0.5, 0.7, "#e2d8ce", x + dx, 1, z + dz));
        for (let k = 0; k < 6; k++) add(box(0.03, 0.5, 0.03, "#e2d8ce", x - 0.5 + k * 0.2, 1, z + 0.35));
        add(box(0.8, 0.1, 0.5, ["#f5c2c7", "#bfd8f5", "#f5e7b0"][Math.floor(r() * 3)], x, 0.85, z));
      }
      break;
    case "office":
      for (const x of [-5, -1.7, 1.7, 5]) for (const z of rowsZ(4, -3, 3.2)) {
        add(box(1.6, 0.06, 0.8, "#d8d4cc", x, 0.75, z));
        add(box(0.7, 0.45, 0.05, "#1a1d22", x, 1.05, z - 0.25, { emissive: 0x4a7ab0, emissiveIntensity: 0.6 }));
        add(box(0.06, 1.3, 1.0, "#9aa3ab", x + 0.85, 0.65, z));
        add(box(0.5, 0.08, 0.5, "#2b2e33", x, 0.5, z + 0.6));
      }
      break;
    case "store": {
      const prod = ["#d0453a", "#3a7ad0", "#e0b33a", "#3aa06a", "#f2f2f2", "#8a4ab0", "#e07a3a"];
      for (const x of [-6, -2, 2, 6]) {
        add(box(1.2, 2.2, 14, "#e8e8e2", x, 1.1, -9));
        for (const y of [0.5, 1.1, 1.7]) for (let k = 0; k < 18; k++) for (const sx of [-0.64, 0.64]) {
          if (r() < 0.12) continue;
          add(box(0.2, 0.36, 0.6, prod[Math.floor(r() * prod.length)], x + sx, y + 0.22, -2.6 - k * 0.72));
        }
      }
      break;
    }
    case "home":
      add(box(3, 0.7, 1.1, "#5a6a8a", 0, 0.35, -6));
      add(box(3, 0.6, 0.3, "#5a6a8a", 0, 0.9, -6.6));
      add(box(1.6, 0.06, 0.9, "#8a6a48", 0, 0.45, -4.2));
      add(box(2.4, 1.3, 0.08, "#101216", -3.2, 1.5, -7.6, { emissive: 0x3a5a8a, emissiveIntensity: 0.4 }));
      add(box(1.2, 2.0, 0.5, "#8a6a48", 3.4, 1.0, -7.4));
      add(box(0.9, 0.9, 0.04, "#d8cfbf", 0, 1.8, -7.9));
      add(box(4, 0.02, 3, "#b08a6a", 0, 0.01, -5));
      add(box(0.4, 1.6, 0.4, "#d8cfbf", 2.6, 0.8, -6.4, { emissive: 0xffd38a, emissiveIntensity: 0.3 }));
      break;
    case "lab":
      for (const x of [-4, 0, 4]) {
        add(box(1.4, 0.9, 8, "#e6e9ea", x, 0.45, -7));
        add(box(1.5, 0.05, 8.1, "#2b2e33", x, 0.92, -7));
        for (let k = 0; k < 6; k++) {
          const c = new THREE.Mesh(new THREE.CylinderGeometry(0.08, 0.08, 0.35, 10), std(["#7fd3ff", "#9fe0a8", "#f5c2c7"][k % 3], { transparent: true, opacity: 0.8 }));
          c.position.set(x + (r() - 0.5) * 0.8, 1.12, -4 - k * 1.1); add(c);
        }
      }
      break;
    case "court":
      add(box(6, 1.6, 2, "#6a4a30", 0, 0.8, -D + 6));
      add(box(1.2, 2.6, 0.3, "#8a2f2f", 0, 2.6, -D + 5.2));
      for (const z of rowsZ(5, -2, 1.8)) for (const side of [-1, 1]) add(box(5, 0.5, 0.6, "#7a5a3a", side * 4, 0.25, z));
      for (const side of [-1, 1]) for (const z of rowsZ(4, -4, 5)) { const c = new THREE.Mesh(new THREE.CylinderGeometry(0.4, 0.45, 7, 12), std("#e6dcc8")); c.position.set(side * (W / 2 - 1.5), 3.5, z); add(c); }
      break;
    case "hall":
      for (const side of [-1, 1]) for (const z of rowsZ(6, -2, 4.5)) {
        const c = new THREE.Mesh(new THREE.CylinderGeometry(0.6, 0.7, 9, 14), std("#e8dcc4"));
        c.position.set(side * (W / 2 - 3), 4.5, z); c.castShadow = true; add(c);
        add(box(0.1, 4, 1.4, "#9a2420", side * (W / 2 - 0.2), 5, z - 2));
      }
      add(box(4, 0.6, 3, "#c9b896", 0, 0.3, -D + 6));
      add(box(1.4, 2, 1, "#8a6a2a", 0, 1.6, -D + 6));
      break;
    case "bunker":
      for (const z of rowsZ(5, -2, 3)) for (const side of [-1, 1]) {
        add(box(0.9, 0.4, 2, "#5a6a4a", side * (W / 2 - 1.2), 0.5, z));
        add(box(0.8, 0.1, 1.9, "#8a8f7a", side * (W / 2 - 1.2), 0.75, z));
      }
      for (const x of [-W / 2 + 0.3, W / 2 - 0.3]) { const p = new THREE.Mesh(new THREE.CylinderGeometry(0.12, 0.12, D, 8), std("#6a6e70", { metalness: 0.4 })); p.rotation.x = Math.PI / 2; p.position.set(x, 2.6, -D / 2 + 4); add(p); }
      break;
  }
}

export function interiorEnv(room = "office") {
  const [W, D, H] = ROOM_DIMS[room] || ROOM_DIMS.office;
  const [wallC, floorC] = ROOM_COLORS[room] || ROOM_COLORS.office;
  const r = rng(4000 + room.length * 13);
  const root = new THREE.Group();
  const shell = new THREE.Mesh(new THREE.BoxGeometry(W, H, D), [
    std(wallC, { side: THREE.BackSide }), std(wallC, { side: THREE.BackSide }),
    std("#f2f2ef", { side: THREE.BackSide }), std(floorC, { side: THREE.BackSide, roughness: 0.7 }),
    std(wallC, { side: THREE.BackSide }), std(wallC, { side: THREE.BackSide }),
  ]);
  shell.position.set(0, H / 2, -D / 2 + 4);
  shell.receiveShadow = true;
  root.add(shell);
  // 天花板灯带 + 一面墙的窗户（自发光，时段决定亮度/颜色）
  const panelM = std("#ffffff", { emissive: 0xffffff, emissiveIntensity: room === "bunker" ? 0.4 : 0.9 });
  for (let x = -W / 2 + 3; x < W / 2 - 1; x += 4) for (let z = 2; z > -D + 4; z -= 4) {
    const p = new THREE.Mesh(new THREE.BoxGeometry(1.4, 0.04, 0.6), panelM);
    p.position.set(x, H - 0.03, z); root.add(p);
  }
  const winM = new THREE.MeshBasicMaterial({ color: 0xcfe3f2 });
  if (!["bunker", "operating_room", "store"].includes(room)) {
    for (let z = 0; z > -D + 5; z -= 4.5) {
      const w = new THREE.Mesh(new THREE.PlaneGeometry(2.6, Math.min(2, H * 0.5)), winM);
      w.position.set(-W / 2 + 0.02, H * 0.55, z); w.rotation.y = Math.PI / 2; root.add(w);
    }
  }
  furnish(root, room, W, D, r);
  return {
    root, outdoor: false, static: true, interior: true, panelM, winM, defaults: { crowd: 0, traffic: 0 },
    bounds: { x: W / 2 - 0.6, y0: 0.4, y1: H - 0.3, z0: -D + 4.6, z1: 3.4 },
    fog: null, background: 0x101214,
    light: { sun: 0.7, hemi: 1.05, sunDir: [-1, 0.6, 0.2], sky: 0xffffff, ground: 0x8a8a80 },
    update() {},
  };
}

// ------------------------------------------------------------------ globe ---
const FAULTS = [
  // 环太平洋 + 大西洋中脊 + 圣安德烈亚斯 + 喜马拉雅（近似走向）
  [[60, -150], [55, -165], [52, 175], [45, 150], [35, 141], [25, 125], [10, 126], [0, 128], [-10, 120], [-20, 170], [-35, 178], [-45, 168]],
  [[60, -150], [50, -130], [40, -125], [32, -117], [20, -106], [13, -92], [5, -82], [-10, -79], [-30, -72], [-45, -76], [-55, -70]],
  [[65, -20], [50, -30], [35, -38], [15, -45], [0, -18], [-20, -13], [-40, -16], [-55, -5]],
  [[36, 70], [30, 80], [28, 88], [26, 96]],
  [[38, 30], [35, 45], [30, 55], [27, 62]],
];
function latLon(lat, lon, R) {
  const phi = (lon + 180) / 360 * Math.PI * 2, theta = (90 - lat) / 180 * Math.PI;
  return new THREE.Vector3(-Math.cos(phi) * Math.sin(theta) * R, Math.cos(theta) * R, Math.sin(phi) * Math.sin(theta) * R);
}

export function globeEnv(opts = {}) {
  const R = 10;
  const root = new THREE.Group();
  const st = stars(5000, 3000, 3);
  root.add(st);
  const tilt = new THREE.Group();
  root.add(tilt);
  const variant = opts.dry_oceans ? "dry" : (opts.frozen ? "frozen" : "normal");
  const earth = makeEarth(R, variant);
  tilt.add(earth);
  // 标记
  const markers = [];
  for (const m of opts.markers || []) {
    const pos = latLon(m.lat, m.lon, R * 1.012);
    const obj = new THREE.Group();
    obj.position.copy(pos);
    obj.lookAt(pos.clone().multiplyScalar(2));
    const size = R * Math.sin((m.radius || 6) * Math.PI / 180);
    let mesh;
    if (m.kind === "dot") mesh = new THREE.Mesh(new THREE.CircleGeometry(size * 0.25, 20), new THREE.MeshBasicMaterial({ color: 0xff5a3a }));
    else if (m.kind === "glow") mesh = new THREE.Mesh(new THREE.CircleGeometry(size, 32), new THREE.MeshBasicMaterial({ map: SOFT, color: 0xff7a2a, transparent: true, blending: THREE.AdditiveBlending, depthWrite: false }));
    else if (m.kind === "cloud") mesh = new THREE.Mesh(new THREE.CircleGeometry(size, 40), new THREE.MeshStandardMaterial({ map: SOFT, color: 0x7a746c, transparent: true, depthWrite: false }));
    else mesh = new THREE.Mesh(new THREE.RingGeometry(size * 0.82, size, 48), new THREE.MeshBasicMaterial({ color: 0xff5a3a, transparent: true, side: THREE.DoubleSide, depthWrite: false }));
    obj.add(mesh);
    obj.userData = { kind: m.kind, mesh };
    earth.add(obj);
    markers.push(obj);
  }
  // 断层
  const faults = new THREE.Group();
  if (opts.faults) {
    const mat = new THREE.MeshBasicMaterial({ color: 0xffa040, transparent: true, blending: THREE.AdditiveBlending, depthWrite: false });
    for (const line of FAULTS) {
      const pts = line.map(([la, lo]) => latLon(la, lo, R * 1.006));
      const curve = new THREE.CatmullRomCurve3(pts);
      faults.add(new THREE.Mesh(new THREE.TubeGeometry(curve, 80, 0.06, 6, false), mat));
    }
    earth.add(faults);
  }
  // 碎片环
  let ring = null;
  if (opts.ring) {
    const tex = canvasTex(512, 8, (x, w) => {
      const rr = rng(8);
      for (let i = 0; i < w; i++) { x.fillStyle = `rgba(220,214,200,${(0.25 + rr() * 0.6) * Math.sin(i / w * Math.PI)})`; x.fillRect(i, 0, 1, 8); }
    }, false);
    const g = new THREE.RingGeometry(R * 1.7, R * 2.6, 128, 1);
    const pos = g.attributes.position, uv = g.attributes.uv;
    for (let i = 0; i < pos.count; i++) { const d = Math.hypot(pos.getX(i), pos.getY(i)); uv.setXY(i, (d - R * 1.7) / (R * 0.9), 0.5); }
    ring = new THREE.Mesh(g, new THREE.MeshBasicMaterial({ map: tex, transparent: true, side: THREE.DoubleSide, depthWrite: false }));
    ring.rotation.x = Math.PI / 2 - 0.35;
    root.add(ring);
  }
  // 月球
  const moon = new THREE.Group();
  if (opts.moon && opts.moon !== "none") {
    const mm = std("#a9a7a0", { roughness: 1, flatShading: opts.moon === "shattered" });
    if (opts.moon === "whole") moon.add(new THREE.Mesh(new THREE.SphereGeometry(2.7, 40, 28), mm));
    else {
      const rr = rng(12);
      for (let i = 0; i < 9; i++) {
        const c = new THREE.Mesh(new THREE.DodecahedronGeometry(0.7 + rr() * 1.1, 0), mm);
        c.userData.dir = new THREE.Vector3(rr() - 0.5, rr() - 0.5, rr() - 0.5).normalize();
        c.userData.spin = rr() * 2;
        moon.add(c);
      }
    }
    moon.position.set(5.5, 12.5, -10);  // 9:16 画面很窄：放在地球右上方、视野内
    root.add(moon);
  }
  // 朝向：让 focus 经纬度正对镜头（+z）
  let baseY = 0, baseX = 0.35;
  if (opts.focus) {
    const v = latLon(opts.focus[0], opts.focus[1], 1);
    baseY = Math.atan2(-v.x, v.z);
    baseX = opts.focus[0] * Math.PI / 180;
  }
  const spin = opts.spin ?? 0.05;
  return {
    root, outdoor: false, globe: true, static: true, fog: null, background: 0x000000,
    light: opts.night_side
      ? { sun: 3.4, hemi: 0.04, sunDir: [1, 0.15, 0.25], sky: 0x8899bb, ground: 0x000000 }
      : { sun: 2.6, hemi: 0.35, sunDir: [0.5, 0.3, 1], sky: 0x8899bb, ground: 0x000000 },
    update(fr) {
      tilt.rotation.x = baseX;
      earth.rotation.y = baseY + spin * fr.t;
      if (earth.userData.clouds) earth.userData.clouds.rotation.y = fr.t * 0.01;
      const k = fr.frac || 0;
      for (const m of markers) {
        const mesh = m.userData.mesh;
        if (m.userData.kind === "ring") { const s = 0.6 + ((fr.t * 0.6) % 1) * 0.8; mesh.scale.setScalar(s); mesh.material.opacity = 1.2 - s * 0.8; }
        if (m.userData.kind === "cloud") { mesh.scale.setScalar(0.3 + k * 1.2); mesh.material.opacity = 0.85; }
        if (m.userData.kind === "glow") mesh.material.opacity = 0.6 + 0.3 * Math.sin(fr.t * 4);
      }
      faults.children.forEach((f) => { f.material.opacity = 0.55 + 0.45 * Math.sin(fr.t * 5); });
      if (ring) ring.rotation.z = fr.t * 0.02;
      if (opts.moon === "shattered") moon.children.forEach((c) => { c.position.copy(c.userData.dir).multiplyScalar(0.8 + k * 3); c.rotation.set(fr.t * c.userData.spin, fr.t * 0.3, 0); });
    },
  };
}

export function mapEnv() {
  // 地图本身由叠加层（SVG）绘制；3D 层只给一个深色底
  return { root: new THREE.Group(), outdoor: false, static: true, fog: null, background: 0x0d1117,
    light: { sun: 0.5, hemi: 0.3, sunDir: [0, 1, 0], sky: 0x222222, ground: 0 }, update() {} };
}
