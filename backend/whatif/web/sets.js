// 自定义布景：按分镜里的 env.set 从基本体和科普道具搭建场景（每个题目都可以长得不一样）。
// 全部是确定性的：随机散布用 seed，动画只依赖本段时间 lt / 进度 frac。
import * as THREE from "three";
import { stars, canvasTex, makeEarth, rng } from "./common.js";
import { Person } from "./people.js";

const SOFT = canvasTex(128, 128, (x) => {
  const g = x.createRadialGradient(64, 64, 0, 64, 64, 64);
  g.addColorStop(0, "rgba(255,255,255,1)"); g.addColorStop(0.4, "rgba(255,255,255,0.35)"); g.addColorStop(1, "rgba(255,255,255,0)");
  x.fillStyle = g; x.fillRect(0, 0, 128, 128);
}, false);

// ---------------------------------------------------------------- 材质 ---
function material(kind, color, opacity = 1) {
  const c = new THREE.Color(color);
  const t = opacity < 1;
  switch (kind) {
    case "glossy": return new THREE.MeshStandardMaterial({ color: c, roughness: 0.25, metalness: 0.05, transparent: t, opacity });
    case "metal": return new THREE.MeshStandardMaterial({ color: c, roughness: 0.32, metalness: 0.75, transparent: t, opacity });
    case "glass": return new THREE.MeshStandardMaterial({ color: c, roughness: 0.08, metalness: 0.1, transparent: true, opacity: Math.min(opacity, 0.32), depthWrite: false, side: THREE.DoubleSide });
    case "glow": return new THREE.MeshBasicMaterial({ color: c, transparent: t, opacity, toneMapped: false });
    case "toon": return new THREE.MeshToonMaterial({ color: c, transparent: t, opacity });
    default: return new THREE.MeshStandardMaterial({ color: c, roughness: 0.85, metalness: 0, transparent: t, opacity });
  }
}
function mesh(geo, mat) {
  const m = new THREE.Mesh(geo, mat);
  m.castShadow = true; m.receiveShadow = true;
  return m;
}
function halo(color, size, opacity = 0.55) {
  const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: SOFT, color, transparent: true, opacity, blending: THREE.AdditiveBlending, depthWrite: false }));
  s.scale.set(size, size, 1);
  return s;
}

// ----------------------------------------------------------- 分子（CPK 配色） ---
const CPK = { H: ["#f4f4f4", 0.32], C: ["#3a3a3a", 0.5], N: ["#3b5bdb", 0.48], O: ["#e03131", 0.46], S: ["#f2c230", 0.58],
  P: ["#f08c00", 0.56], Cl: ["#40c057", 0.56], Na: ["#9775fa", 0.6], Fe: ["#d9480f", 0.6] };
// 常见分子的几何（原子, 位置；键: [i, j, 键级]）
const MOLECULES = {
  N2: { atoms: [["N", [-0.55, 0, 0]], ["N", [0.55, 0, 0]]], bonds: [[0, 1, 3]] },
  O2: { atoms: [["O", [-0.6, 0, 0]], ["O", [0.6, 0, 0]]], bonds: [[0, 1, 2]] },
  H2: { atoms: [["H", [-0.37, 0, 0]], ["H", [0.37, 0, 0]]], bonds: [[0, 1, 1]] },
  CO2: { atoms: [["O", [-1.16, 0, 0]], ["C", [0, 0, 0]], ["O", [1.16, 0, 0]]], bonds: [[0, 1, 2], [1, 2, 2]] },
  H2O: { atoms: [["O", [0, 0, 0]], ["H", [-0.76, -0.59, 0]], ["H", [0.76, -0.59, 0]]], bonds: [[0, 1, 1], [0, 2, 1]] },
  CH4: { atoms: [["C", [0, 0, 0]], ["H", [0.63, 0.63, 0.63]], ["H", [-0.63, -0.63, 0.63]], ["H", [-0.63, 0.63, -0.63]], ["H", [0.63, -0.63, -0.63]]], bonds: [[0, 1, 1], [0, 2, 1], [0, 3, 1], [0, 4, 1]] },
  NH3: { atoms: [["N", [0, 0.2, 0]], ["H", [0.94, -0.2, 0]], ["H", [-0.47, -0.2, 0.81]], ["H", [-0.47, -0.2, -0.81]]], bonds: [[0, 1, 1], [0, 2, 1], [0, 3, 1]] },
  O3: { atoms: [["O", [0, 0.3, 0]], ["O", [-1.1, -0.35, 0]], ["O", [1.1, -0.35, 0]]], bonds: [[0, 1, 2], [0, 2, 1]] },
  NaCl: { atoms: [["Na", [-0.7, 0, 0]], ["Cl", [0.7, 0, 0]]], bonds: [[0, 1, 1]] },
  CO: { atoms: [["C", [-0.56, 0, 0]], ["O", [0.56, 0, 0]]], bonds: [[0, 1, 3]] },
};
function molecule(formula, matKind) {
  const spec = MOLECULES[formula] || MOLECULES[formula.replace(/₂/g, "2")] || MOLECULES.H2O;
  const g = new THREE.Group();
  const pos = spec.atoms.map(([, p]) => new THREE.Vector3(...p));
  spec.atoms.forEach(([el, p]) => {
    const [col, r] = CPK[el] || ["#cccccc", 0.45];
    g.add(mesh(new THREE.SphereGeometry(r, 28, 20), material(matKind === "matte" ? "glossy" : matKind, col)));
    g.children[g.children.length - 1].position.set(...p);
  });
  const bondMat = material("glossy", "#d9dde3");
  for (const [i, j, order] of spec.bonds) {
    const a = pos[i], b = pos[j];
    const len = a.distanceTo(b);
    const mid = a.clone().add(b).multiplyScalar(0.5);
    const dir = b.clone().sub(a).normalize();
    const perp = new THREE.Vector3(0, 0, 1).cross(dir).normalize();
    if (perp.lengthSq() < 0.1) perp.set(0, 1, 0);
    for (let k = 0; k < order; k++) {
      const off = (k - (order - 1) / 2) * 0.16;
      const cyl = mesh(new THREE.CylinderGeometry(0.06, 0.06, len, 10), bondMat);
      cyl.position.copy(mid).addScaledVector(perp, off);
      cyl.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), dir);
      g.add(cyl);
    }
  }
  return g;
}

// --------------------------------------------------------------- 道具 ---
function atom(col, col2, matKind) {
  const g = new THREE.Group();
  const nuc = new THREE.Group();
  const r = rng(5);
  for (let i = 0; i < 12; i++) {
    const s = mesh(new THREE.SphereGeometry(0.22, 16, 12), material("glossy", i % 2 ? col : (col2 || "#868e96")));
    s.position.set((r() - 0.5) * 0.45, (r() - 0.5) * 0.45, (r() - 0.5) * 0.45);
    nuc.add(s);
  }
  g.add(nuc);
  for (let k = 0; k < 3; k++) {
    const orbit = new THREE.Group();
    const ring = new THREE.Mesh(new THREE.TorusGeometry(1.6, 0.012, 6, 96), material("glow", "#9ec5ff", 0.6));
    const e = mesh(new THREE.SphereGeometry(0.09, 12, 10), material("glow", "#9ec5ff"));
    e.position.x = 1.6;
    e.add(halo("#9ec5ff", 0.6));
    orbit.add(ring, e);
    orbit.rotation.set(k * 1.05, k * 0.6, 0);
    orbit.userData.electron = e;
    g.add(orbit);
  }
  g.userData.electrons = true;
  return g;
}

function dna(col, col2) {
  const g = new THREE.Group();
  const n = 40, h = 6, R = 0.9;
  for (let i = 0; i < n; i++) {
    const t = i / n, a = t * Math.PI * 6, y = t * h - h / 2;
    const p1 = new THREE.Vector3(Math.cos(a) * R, y, Math.sin(a) * R);
    const p2 = new THREE.Vector3(Math.cos(a + Math.PI) * R, y, Math.sin(a + Math.PI) * R);
    const s1 = mesh(new THREE.SphereGeometry(0.13, 12, 10), material("glossy", col)); s1.position.copy(p1);
    const s2 = mesh(new THREE.SphereGeometry(0.13, 12, 10), material("glossy", col2 || "#ffd43b")); s2.position.copy(p2);
    g.add(s1, s2);
    if (i % 2 === 0) {
      const rung = mesh(new THREE.CylinderGeometry(0.04, 0.04, R * 2, 6), material("glossy", ["#69db7c", "#ff8787", "#74c0fc", "#ffd8a8"][i % 4]));
      rung.position.set(0, y, 0); rung.rotation.z = Math.PI / 2; rung.rotation.y = -a;
      g.add(rung);
    }
  }
  return g;
}

function cell(col, col2) {
  const g = new THREE.Group();
  g.add(mesh(new THREE.SphereGeometry(1.5, 40, 30), material("glass", col, 0.3)));
  const nuc = mesh(new THREE.SphereGeometry(0.55, 28, 20), material("glossy", col2 || "#7048e8"));
  nuc.position.set(0.2, 0.1, 0);
  g.add(nuc);
  const r = rng(9);
  for (let i = 0; i < 9; i++) {
    const o = mesh(new THREE.CapsuleGeometry(0.1, 0.28, 4, 8), material("glossy", ["#ff922b", "#51cf66", "#fcc419"][i % 3]));
    const d = 0.8 + r() * 0.45, a = r() * Math.PI * 2, b = (r() - 0.5) * 2;
    o.position.set(Math.cos(a) * d, b * 0.6, Math.sin(a) * d);
    o.rotation.set(r() * 3, r() * 3, 0);
    g.add(o);
  }
  return g;
}

function bloodCell(col) {
  const pts = [];
  for (let i = 0; i <= 24; i++) {
    const t = i / 24, r = t * 1.0;
    const y = 0.18 + 0.22 * Math.pow(t, 2) - 0.38 * Math.pow(1 - t, 3) * 0.6;
    pts.push(new THREE.Vector2(r, Math.max(0.05, y) * (1 - Math.pow(t, 8))));
  }
  const top = new THREE.LatheGeometry(pts, 40);
  const g = new THREE.Group();
  const a = mesh(top, material("glossy", col || "#c92a2a"));
  const b = mesh(top, material("glossy", col || "#c92a2a"));
  b.scale.y = -1;
  g.add(a, b);
  return g;
}

function virus(col, col2) {
  const g = new THREE.Group();
  g.add(mesh(new THREE.IcosahedronGeometry(1, 2), material("glossy", col || "#5c7cfa")));
  const spikeMat = material("glossy", col2 || "#ff6b6b");
  const ico = new THREE.IcosahedronGeometry(1, 1).attributes.position;
  const seen = new Set();
  for (let i = 0; i < ico.count; i++) {
    const v = new THREE.Vector3(ico.getX(i), ico.getY(i), ico.getZ(i)).normalize();
    const key = v.toArray().map((x) => x.toFixed(2)).join();
    if (seen.has(key)) continue;
    seen.add(key);
    const st = mesh(new THREE.CylinderGeometry(0.04, 0.04, 0.35, 6), spikeMat);
    st.position.copy(v.clone().multiplyScalar(1.15));
    st.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), v);
    const knob = mesh(new THREE.SphereGeometry(0.1, 10, 8), spikeMat);
    knob.position.copy(v.clone().multiplyScalar(1.35));
    g.add(st, knob);
  }
  return g;
}

function neuron(col) {
  const g = new THREE.Group();
  const m = material("glossy", col || "#fab005");
  g.add(mesh(new THREE.SphereGeometry(0.5, 24, 18), m));
  const r = rng(13);
  const branch = (from, dir, len, depth) => {
    const to = from.clone().addScaledVector(dir, len);
    const curve = new THREE.CatmullRomCurve3([from, from.clone().lerp(to, 0.5).add(new THREE.Vector3((r() - 0.5) * 0.3, (r() - 0.5) * 0.3, (r() - 0.5) * 0.3)), to]);
    g.add(mesh(new THREE.TubeGeometry(curve, 12, 0.06 * (depth + 1) / 3, 6), m));
    if (depth > 0) for (let k = 0; k < 2; k++) {
      const nd = dir.clone().add(new THREE.Vector3((r() - 0.5), (r() - 0.5), (r() - 0.5))).normalize();
      branch(to, nd, len * 0.65, depth - 1);
    }
  };
  for (let k = 0; k < 6; k++) branch(new THREE.Vector3(), new THREE.Vector3(r() - 0.5, r() - 0.5, r() - 0.5).normalize(), 0.9, 2);
  const axon = new THREE.CatmullRomCurve3([new THREE.Vector3(0.4, 0, 0), new THREE.Vector3(2, 0.3, 0), new THREE.Vector3(3.6, -0.2, 0.2), new THREE.Vector3(5, 0.1, 0)]);
  g.add(mesh(new THREE.TubeGeometry(axon, 40, 0.09, 8), m));
  return g;
}

function lungs(col) {
  const g = new THREE.Group();
  const m = material("glossy", col || "#f783ac");
  for (const s of [-1, 1]) {
    const lobe = mesh(new THREE.SphereGeometry(1, 32, 24), m);
    lobe.scale.set(0.75, 1.35, 0.6);
    lobe.position.set(s * 0.95, 0, 0);
    g.add(lobe);
    const bron = mesh(new THREE.CylinderGeometry(0.1, 0.12, 0.9, 10), material("glossy", "#dee2e6"));
    bron.position.set(s * 0.4, 1.0, 0); bron.rotation.z = s * 0.9;
    g.add(bron);
  }
  const tr = mesh(new THREE.CylinderGeometry(0.16, 0.16, 1.4, 14), material("glossy", "#dee2e6"));
  tr.position.y = 1.85;
  g.add(tr);
  g.userData.breathe = true;
  return g;
}

function heart(col) {
  const g = new THREE.Group();
  const m = material("glossy", col || "#e03131");
  for (const s of [-1, 1]) { const b = mesh(new THREE.SphereGeometry(0.6, 28, 20), m); b.position.set(s * 0.42, 0.35, 0); g.add(b); }
  const c = mesh(new THREE.ConeGeometry(0.98, 1.5, 32), m);
  c.rotation.z = Math.PI; c.position.y = -0.5; c.scale.z = 0.7;
  g.add(c);
  g.userData.beat = true;
  return g;
}

function hourglass(col, col2) {
  const g = new THREE.Group();
  const glass = material("glass", "#d0ebff", 0.3);
  const top = mesh(new THREE.ConeGeometry(0.9, 1.4, 32, 1, true), glass); top.rotation.x = Math.PI; top.position.y = 0.72;
  const bot = mesh(new THREE.ConeGeometry(0.9, 1.4, 32, 1, true), glass); bot.position.y = -0.72;
  const wood = material("glossy", col || "#8d5a36");
  for (const y of [-1.5, 1.5]) { const cap = mesh(new THREE.CylinderGeometry(1.15, 1.15, 0.18, 32), wood); cap.position.y = y; g.add(cap); }
  for (let k = 0; k < 3; k++) { const post = mesh(new THREE.CylinderGeometry(0.06, 0.06, 3, 8), wood); const a = k * Math.PI * 2 / 3; post.position.set(Math.cos(a) * 1.0, 0, Math.sin(a) * 1.0); g.add(post); }
  const sandM = material("matte", col2 || "#e9c46a");
  const sandTop = mesh(new THREE.ConeGeometry(0.75, 1.0, 32), sandM); sandTop.rotation.x = Math.PI; sandTop.position.y = 0.9;
  const sandBot = mesh(new THREE.ConeGeometry(0.8, 0.9, 32), sandM); sandBot.position.y = -1.0;
  const stream = mesh(new THREE.CylinderGeometry(0.025, 0.025, 1.3, 6), sandM); stream.position.y = -0.2;
  g.add(top, bot, sandTop, sandBot, stream);
  g.userData.sand = { top: sandTop, bot: sandBot };
  return g;
}

function clock(col, col2) {
  const g = new THREE.Group();
  const face = mesh(new THREE.CylinderGeometry(1.2, 1.2, 0.12, 48), material("glossy", col2 || "#f8f9fa"));
  face.rotation.x = Math.PI / 2;
  const rim = mesh(new THREE.TorusGeometry(1.22, 0.08, 10, 48), material("metal", col || "#495057"));
  g.add(face, rim);
  for (let i = 0; i < 12; i++) {
    const tk = mesh(new THREE.BoxGeometry(0.05, i % 3 ? 0.12 : 0.22, 0.04), material("matte", "#212529"));
    const a = i / 12 * Math.PI * 2;
    tk.position.set(Math.sin(a) * 1.0, Math.cos(a) * 1.0, 0.08); tk.rotation.z = -a;
    g.add(tk);
  }
  const mk = (len, w) => { const p = new THREE.Group(); const h = mesh(new THREE.BoxGeometry(w, len, 0.03), material("matte", "#212529")); h.position.y = len / 2; p.add(h); p.position.z = 0.1; g.add(p); return p; };
  g.userData.hands = { hour: mk(0.6, 0.07), min: mk(0.9, 0.045) };
  return g;
}

function gear(col) {
  const shape = new THREE.Shape();
  const teeth = 12, R = 1, r = 0.82;
  for (let i = 0; i <= teeth * 4; i++) {
    const a = i / (teeth * 4) * Math.PI * 2;
    const rad = [r, R, R, r][i % 4];
    const x = Math.cos(a) * rad, y = Math.sin(a) * rad;
    if (i === 0) shape.moveTo(x, y); else shape.lineTo(x, y);
  }
  const hole = new THREE.Path(); hole.absarc(0, 0, 0.25, 0, Math.PI * 2, true); shape.holes.push(hole);
  const geo = new THREE.ExtrudeGeometry(shape, { depth: 0.25, bevelEnabled: false });
  geo.translate(0, 0, -0.125);
  return mesh(geo, material("metal", col || "#adb5bd"));
}

function flame(col) {
  const g = new THREE.Group();
  for (let i = 0; i < 18; i++) {
    const s = halo(i < 6 ? "#fff3bf" : (col || "#ff922b"), 1, 0.8);
    s.userData.k = i / 18;
    g.add(s);
  }
  g.userData.flame = true;
  return g;
}

function bars(values, col, col2) {
  const g = new THREE.Group();
  const max = Math.max(1e-9, ...values.map(Math.abs));
  values.forEach((v, i) => {
    const h = Math.max(0.05, Math.abs(v) / max * 3);
    const b = mesh(new THREE.BoxGeometry(0.6, h, 0.6), material("glossy", i === values.length - 1 ? (col2 || col) : col));
    b.position.set((i - (values.length - 1) / 2) * 0.85, h / 2, 0);
    b.userData.h = h;
    g.add(b);
  });
  g.userData.bars = true;
  return g;
}

function building(col, r) {
  const h = 3 + r() * 6;
  const g = new THREE.Group();
  const b = mesh(new THREE.BoxGeometry(1.6, h, 1.6), material("matte", col));
  b.position.y = h / 2;
  g.add(b);
  return g;
}

function tree(col) {
  const g = new THREE.Group();
  const tr = mesh(new THREE.CylinderGeometry(0.12, 0.18, 1.6, 6), material("matte", "#6b5240")); tr.position.y = 0.8;
  const top = mesh(new THREE.IcosahedronGeometry(1, 0), new THREE.MeshStandardMaterial({ color: col || "#4f7a3a", flatShading: true, roughness: 0.9 }));
  top.position.y = 2.1;
  g.add(tr, top);
  return g;
}

function arrow(col) {
  const g = new THREE.Group();
  const m = material("glossy", col || "#ffd43b");
  const shaft = mesh(new THREE.CylinderGeometry(0.08, 0.08, 1.6, 12), m); shaft.position.y = 0.8;
  const head = mesh(new THREE.ConeGeometry(0.22, 0.5, 16), m); head.position.y = 1.85;
  g.add(shaft, head);
  return g;
}

function planet(col, col2, matKind, ringed) {
  const g = new THREE.Group();
  g.add(mesh(new THREE.SphereGeometry(1, 48, 32), material(matKind === "matte" ? "glossy" : matKind, col)));
  if (ringed) {
    const ring = new THREE.Mesh(new THREE.RingGeometry(1.4, 2.2, 64), material("glass", col2 || "#e9d8a6", 0.6));
    ring.rotation.x = Math.PI / 2 - 0.4;
    g.add(ring);
  }
  return g;
}

function particles(col, n, spread, size, seed) {
  const r = rng(seed * 31 + 3);
  const geo = new THREE.BufferGeometry();
  const p = new Float32Array(n * 3);
  for (let i = 0; i < n; i++) { p[i * 3] = (r() - 0.5) * spread[0]; p[i * 3 + 1] = (r() - 0.5) * spread[1]; p[i * 3 + 2] = (r() - 0.5) * spread[2]; }
  geo.setAttribute("position", new THREE.BufferAttribute(p, 3));
  const pts = new THREE.Points(geo, new THREE.PointsMaterial({ color: col, size: 0.08 * size, transparent: true, opacity: 0.85, blending: THREE.AdditiveBlending, depthWrite: false }));
  pts.userData.base = p.slice();
  pts.userData.spread = spread;
  return pts;
}

function build(o, r) {
  const c = o.color, c2 = o.color2, mk = o.material;
  switch (o.kind) {
    case "sphere": return mesh(new THREE.SphereGeometry(1, 40, 28), material(mk, c, o.opacity));
    case "box": return mesh(new THREE.BoxGeometry(1, 1, 1), material(mk, c, o.opacity));
    case "cylinder": return mesh(new THREE.CylinderGeometry(0.5, 0.5, 1, 32), material(mk, c, o.opacity));
    case "cone": return mesh(new THREE.ConeGeometry(0.5, 1, 32), material(mk, c, o.opacity));
    case "torus": return mesh(new THREE.TorusGeometry(1, 0.3, 20, 64), material(mk, c, o.opacity));
    case "capsule": return mesh(new THREE.CapsuleGeometry(0.4, 1, 8, 16), material(mk, c, o.opacity));
    case "ring": return mesh(new THREE.RingGeometry(0.8, 1, 64), Object.assign(material(mk, c, o.opacity), { side: THREE.DoubleSide }));
    case "plane": return mesh(new THREE.PlaneGeometry(1, 1), Object.assign(material(mk, c, o.opacity), { side: THREE.DoubleSide }));
    case "icosahedron": return mesh(new THREE.IcosahedronGeometry(1, 0), Object.assign(material(mk, c, o.opacity), { flatShading: true }));
    case "octahedron": case "crystal": return mesh(new THREE.OctahedronGeometry(1, 0), Object.assign(material(o.kind === "crystal" && mk === "matte" ? "glass" : mk, c, o.opacity), { flatShading: true }));
    case "molecule": return molecule(o.formula || "H2O", mk);
    case "atom": return atom(c, c2, mk);
    case "dna": return dna(c, c2);
    case "cell": return cell(c, c2);
    case "blood_cell": return bloodCell(c);
    case "virus": return virus(c, c2);
    case "neuron": return neuron(c);
    case "lungs": return lungs(c);
    case "heart": return heart(c);
    case "hourglass": return hourglass(c, c2);
    case "clock": return clock(c, c2);
    case "gear": return gear(c);
    case "flame": return flame(c);
    case "bubble": return mesh(new THREE.SphereGeometry(1, 32, 24), material("glass", c || "#d0ebff", 0.3));
    case "planet": return planet(c, c2, mk, !!c2);
    case "sun": { const g = new THREE.Group(); g.add(mesh(new THREE.SphereGeometry(1, 40, 28), material("glow", c || "#ffd43b"))); g.add(halo(c || "#ffb703", 5, 0.7)); return g; }
    case "moon": return mesh(new THREE.SphereGeometry(1, 40, 28), material("matte", c || "#adb5bd"));
    case "earth": return makeEarth(1);
    case "tree": return tree(c);
    case "rock": return mesh(new THREE.DodecahedronGeometry(1, 0), Object.assign(material(mk, c, o.opacity), { flatShading: true }));
    case "building": return building(c, r);
    case "arrow": return arrow(c);
    case "bars": return bars(o.values.length ? o.values : [1, 2, 3], c, c2);
    case "person": { const p = new Person(o.outfit, o.color === "#d8d8d8" ? null : o.color, o.seed); p.pose(o.action, 0, 0); return p.root; }
    case "particles": return particles(c, Math.min(4000, o.count * 20), o.spread.map((v) => v || 10), Array.isArray(o.scale) ? o.scale[0] : o.scale, o.seed);
    default: return mesh(new THREE.SphereGeometry(1, 16, 12), material(mk, c));
  }
}

// --------------------------------------------------------------- 布景 ---
export function setEnv(spec) {
  const root = new THREE.Group();
  const items = [];
  // 背景：渐变天空球 / 星空 / 纯色
  let background;
  if (Array.isArray(spec.background)) {
    const [top, bottom] = spec.background;
    const sky = new THREE.Mesh(new THREE.SphereGeometry(900, 32, 16), new THREE.ShaderMaterial({
      uniforms: { top: { value: new THREE.Color(top) }, bottom: { value: new THREE.Color(bottom) } },
      vertexShader: `varying vec3 vP; void main(){ vP=normalize(position); gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0); }`,
      fragmentShader: `uniform vec3 top; uniform vec3 bottom; varying vec3 vP; void main(){ float h=smoothstep(-0.35,0.6,vP.y); gl_FragColor=vec4(mix(bottom,top,h),1.0); }`,
      side: THREE.BackSide, depthWrite: false, fog: false,
    }));
    root.add(sky);
  } else if (spec.background === "stars") {
    background = 0x000000;
    root.add(stars(5000, 800, 17));
  } else background = spec.background === "white" ? 0xf4f4f2 : 0x000000;
  // 地面
  if (spec.ground !== "none") {
    if (spec.ground === "grid") {
      const grid = new THREE.GridHelper(200, 100, new THREE.Color(spec.ground_color).offsetHSL(0, 0, 0.15), new THREE.Color(spec.ground_color).offsetHSL(0, 0, 0.08));
      root.add(grid);
      const base = new THREE.Mesh(new THREE.PlaneGeometry(400, 400), material("matte", spec.ground_color));
      base.rotation.x = -Math.PI / 2; base.position.y = -0.01; base.receiveShadow = true;
      root.add(base);
    } else {
      const kind = spec.ground === "mirror" ? "metal" : spec.ground === "water" ? "glossy" : "matte";
      const plane = new THREE.Mesh(new THREE.PlaneGeometry(400, 400, spec.ground === "water" ? 80 : 1, spec.ground === "water" ? 80 : 1), material(kind, spec.ground_color));
      plane.rotation.x = -Math.PI / 2; plane.receiveShadow = true;
      if (spec.ground === "water") plane.userData.water = plane.geometry.attributes.position.array.slice();
      root.add(plane);
      items.push({ obj: plane, o: { animate: [] }, water: spec.ground === "water" });
    }
  }
  // 物体
  for (const o of spec.objects) {
    const r = rng(o.seed * 7919 + o.kind.length);
    const n = o.kind === "particles" ? 1 : o.count;
    for (let i = 0; i < n; i++) {
      const obj = build(o, r);
      const jitter = n > 1 ? o.spread.map((s) => (r() - 0.5) * s) : [0, 0, 0];
      const base = new THREE.Vector3(o.at[0] + jitter[0], o.at[1] + jitter[1], o.at[2] + jitter[2]);
      obj.position.copy(base);
      const sc = Array.isArray(o.scale) ? o.scale : [o.scale, o.scale, o.scale];
      const vary = n > 1 ? 0.75 + r() * 0.5 : 1;
      obj.scale.set(sc[0] * vary, sc[1] * vary, sc[2] * vary);
      const rot = o.rotate.map((d) => d * Math.PI / 180);
      obj.rotation.set(rot[0] + (n > 1 ? r() * 6 : 0), rot[1] + (n > 1 ? r() * 6 : 0), rot[2]);
      if (o.material === "glow" && o.kind !== "flame" && o.kind !== "particles" && o.kind !== "sun") obj.add(halo(o.color, 3.2, 0.45));
      root.add(obj);
      items.push({ obj, o, base, baseScale: obj.scale.clone(), baseRot: obj.rotation.clone(), phase: r() * Math.PI * 2 });
    }
  }
  const sunDir = [0.6, 1, 0.8];
  return {
    root, outdoor: false, custom: true, static: true, background,
    fog: spec.fog ? new THREE.Fog(spec.fog[0], spec.fog[1], spec.fog[2]) : null,
    light: { sun: spec.light_intensity, hemi: spec.ambient, sunDir, sky: spec.light, ground: 0x30343c },
    focus: spec.focus, zoom: spec.zoom,
    update(fr) {
      const lt = fr.lt || 0, k = fr.frac || 0, t = fr.t || 0;
      for (const it of items) {
        const { obj, o } = it;
        if (it.water) {
          const a = obj.geometry.attributes.position.array, b = obj.userData.water;
          for (let i = 0; i < a.length; i += 3) a[i + 2] = Math.sin(b[i] * 0.3 + t * 1.2) * 0.25 + Math.sin(b[i + 1] * 0.25 - t) * 0.25;
          obj.geometry.attributes.position.needsUpdate = true; obj.geometry.computeVertexNormals();
          continue;
        }
        obj.position.copy(it.base);
        obj.rotation.copy(it.baseRot);
        let s = 1, alpha = 1;
        for (const a of o.animate) {
          const sp = a.speed, am = a.amount;
          switch (a.type) {
            case "spin": obj.rotation[a.axis] += lt * sp; break;
            case "bob": obj.position.y += Math.sin(lt * sp * 2 + it.phase) * am; break;
            case "wobble": obj.rotation.z += Math.sin(lt * sp * 3 + it.phase) * am * 0.5; obj.rotation.x += Math.cos(lt * sp * 2.3 + it.phase) * am * 0.3; break;
            case "orbit": { const ang = lt * sp + it.phase; obj.position.x += Math.cos(ang) * am; obj.position.z += Math.sin(ang) * am; break; }
            case "pulse": s *= 1 + Math.sin(lt * sp * 4 + it.phase) * am * 0.5; break;
            case "grow": s *= Math.min(1, 0.02 + k * 1.15); break;
            case "shrink": s *= Math.max(0.02, 1 - k); break;
            case "fade_in": alpha *= Math.min(1, k * 2.5); break;
            case "fade_out": alpha *= Math.max(0, 1 - k * 1.4); break;
            case "move": if (a.to) obj.position.lerp(new THREE.Vector3(...a.to).add(obj.position.clone().sub(new THREE.Vector3(...o.at))), k * k * (3 - 2 * k)); break;
            case "drift": { const d = (lt * sp + it.phase) % 10 - 5; obj.position[a.axis] += d * am; break; }
          }
        }
        obj.scale.copy(it.baseScale).multiplyScalar(s);
        // 道具自带动画
        const u = obj.userData;
        if (u.breathe) obj.scale.multiplyScalar(1 + Math.sin(t * 2.2) * 0.05);
        if (u.beat) { const b = Math.max(0, Math.sin(t * 7)) ** 8; obj.scale.multiplyScalar(1 + b * 0.08); }
        if (u.electrons) obj.children.forEach((ch, idx) => { if (ch.userData.electron) { const a2 = t * (2 + idx * 0.7); ch.userData.electron.position.set(Math.cos(a2) * 1.6, Math.sin(a2) * 1.6, 0); } });
        if (u.hands) { u.hands.min.rotation.z = -t * 2.5; u.hands.hour.rotation.z = -t * 0.21; }
        if (u.sand) { const q = 0.35 + k * 0.6; u.sand.top.scale.setScalar(Math.max(0.05, 1 - q)); u.sand.bot.scale.setScalar(Math.max(0.1, q)); }
        if (u.flame) obj.children.forEach((sp, j) => { const kk = ((t * 1.6 + sp.userData.k) % 1); sp.position.set(Math.sin(j * 2.3 + t * 3) * 0.15 * (1 - kk), kk * 1.8, Math.cos(j * 1.7) * 0.1); const sc2 = (1.3 - kk) * 0.9; sp.scale.set(sc2, sc2 * 1.4, 1); sp.material.opacity = (1 - kk) * 0.85; });
        if (u.bars) obj.children.forEach((b) => { const g = Math.min(1, 0.05 + k * 1.3); b.scale.y = g; b.position.y = b.userData.h * g / 2; });
        if (obj.isPoints && obj.userData.base) {
          const a = obj.geometry.attributes.position.array, b = obj.userData.base, spd = obj.userData.spread;
          for (let i = 0; i < a.length; i += 3) { a[i] = b[i]; a[i + 1] = ((b[i + 1] + t * 0.4 + spd[1] / 2) % spd[1]) - spd[1] / 2; a[i + 2] = b[i + 2]; }
          obj.geometry.attributes.position.needsUpdate = true;
        }
        if (alpha < 1 || o.animate.some((a) => a.type === "fade_in" || a.type === "fade_out")) {
          obj.traverse((m) => { if (m.material) { m.material.transparent = true; m.material.opacity = (m.userData.op0 ??= m.material.opacity) * alpha; } });
          obj.visible = alpha > 0.01;
        }
      }
    },
  };
}
