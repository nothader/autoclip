// 低多边形人物：服装预设 + 姿势 + 人群烘焙（整群合成一个网格，软件 WebGL 下 draw call 才是瓶颈）。
import * as THREE from "three";
import { mergeGeometries } from "./vendor/BufferGeometryUtils.js";

const matCache = new Map();
function mat(color, rough = 0.85) {
  const k = `${color}|${rough}`;
  if (!matCache.has(k)) matCache.set(k, new THREE.MeshStandardMaterial({ color, roughness: rough, metalness: 0 }));
  return matCache.get(k);
}

function rng(seed) {
  let s = (seed >>> 0) || 1;
  return () => { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; };
}

const SKINS = ["#d6a07a", "#a8714f", "#f0c9a8", "#7a4e33", "#c58c63", "#e8b896"];
const HAIRS = ["#2b2420", "#4a3426", "#151210", "#8a6a45", "#6b6b6b", "#b8893f"];
const CASUAL = ["#d9c27a", "#f2f2f2", "#3b5f8a", "#6b6b6b", "#8a3b3b", "#2f5e4c", "#c96f4a", "#7a6aa8", "#e0e0d8", "#2c3440"];
const PANTS = ["#2c3440", "#3f5a85", "#5a6070", "#2b2b2b", "#7a6a55", "#4a4a52"];

// 服装：上衣、裤子、鞋、附加件
function outfitSpec(outfit, color, r) {
  const pick = (a) => a[Math.floor(r() * a.length)];
  switch (outfit) {
    case "hoodie": return { top: color || "#c8322b", bottom: "#3f5a85", shoe: "#f2f2f2", hood: true };
    case "scrubs": return { top: "#5fb3ad", bottom: "#5fb3ad", shoe: "#f2f2f2", cap: "#5fb3ad", mask: true };
    case "doctor": return { top: "#f4f4f2", bottom: "#3a4250", shoe: "#2b2b2b", coat: "#f4f4f2" };
    case "hivis": return { top: "#e8a53a", bottom: "#2c3440", shoe: "#4a3a2a", vest: "#d6e82f", helmet: "#f2c230" };
    case "suit": return { top: pick(["#2b2f38", "#3a3f48", "#1e2026"]), bottom: "#25282e", shoe: "#151515", tie: pick(["#8a1f2b", "#2f4f7f"]) };
    case "robe": return { top: pick(["#e8dcc4", "#c9b48f", "#d8cfc0", "#9c8466", "#efe9df"]), bottom: null, shoe: "#6b4a2b",
      robe: true, sash: pick(["#8a2f2f", "#3b5f8a", "#a87a2f", "#5a4a7a"]), headcloth: r() < 0.5 ? pick(["#efe9df", "#c9b48f", "#7a5a3a"]) : null };
    case "soldier": return { top: "#9a2420", bottom: "#9a2420", shoe: "#5a3a22", robe: true, armor: "#9c8a5a", helmet: "#b59a5a" };
    case "ranger": return { top: "#8a7a52", bottom: "#4f5a3f", shoe: "#4a3a2a", hat: "#7a6440" };
    case "police": return { top: "#1f2c48", bottom: "#1f2c48", shoe: "#151515", cap: "#141c30" };
    case "child": return { top: color || pick(CASUAL), bottom: pick(PANTS), shoe: pick(["#f2f2f2", "#d23a3a", "#3b5f8a"]), child: true };
    default: return { top: color || pick(CASUAL), bottom: pick(PANTS), shoe: pick(["#f2f2f2", "#2b2b2b", "#7a5a3a"]) };
  }
}

function limb(radius, length, m) {
  const g = new THREE.CapsuleGeometry(radius, length, 4, 10);
  g.translate(0, -length / 2 - radius * 0.3, 0);
  const mesh = new THREE.Mesh(g, m);
  mesh.castShadow = true;
  return mesh;
}

export class Person {
  constructor(outfit = "casual", color = null, seed = 1) {
    const r = rng(seed * 7919 + 13);
    const spec = outfitSpec(outfit, color, r);
    this.spec = spec;
    this.root = new THREE.Group();
    this.body = new THREE.Group();
    this.root.add(this.body);
    const top = mat(spec.top, 0.9);
    const bottom = mat(spec.bottom || spec.top, 0.95);
    const skin = mat(SKINS[Math.floor(r() * SKINS.length)], 0.7);
    const hairM = mat(outfit === "hoodie" ? "#2b2420" : HAIRS[Math.floor(r() * HAIRS.length)], 1);
    const shoe = mat(spec.shoe, 0.6);
    const longHair = outfit !== "hoodie" && outfit !== "soldier" && r() < 0.45;

    this.hips = new THREE.Group();
    this.hips.position.y = 0.98;
    this.body.add(this.hips);
    const pelvis = new THREE.Mesh(new THREE.BoxGeometry(0.34, 0.16, 0.2), bottom);
    pelvis.castShadow = true;
    this.hips.add(pelvis);

    this.spine = new THREE.Group();
    this.spine.position.y = 0.06;
    this.hips.add(this.spine);
    const torsoG = new THREE.CapsuleGeometry(0.19, 0.36, 4, 12);
    torsoG.scale(1.05, 1, 0.68);
    torsoG.translate(0, 0.3, 0);
    const torso = new THREE.Mesh(torsoG, top);
    torso.castShadow = true;
    this.spine.add(torso);
    if (spec.hood) {
      const hood = new THREE.Mesh(new THREE.TorusGeometry(0.12, 0.05, 6, 14, Math.PI * 1.3), top);
      hood.position.set(0, 0.6, 0.06);
      hood.rotation.set(-0.3, 0, Math.PI * 1.15);
      this.spine.add(hood);
      for (const sx of [-0.05, 0.05]) {
        const s = new THREE.Mesh(new THREE.CylinderGeometry(0.008, 0.008, 0.16, 4), mat("#f2f2f2"));
        s.position.set(sx, 0.48, -0.13);
        this.spine.add(s);
      }
    }
    if (spec.vest) {
      const v = new THREE.Mesh(new THREE.CapsuleGeometry(0.2, 0.3, 4, 12), mat(spec.vest, 0.5));
      v.scale.set(1.08, 1, 0.74); v.position.y = 0.3;
      this.spine.add(v);
      const stripe = new THREE.Mesh(new THREE.BoxGeometry(0.44, 0.035, 0.31), mat("#e8e8e8", 0.3));
      stripe.position.y = 0.24;
      this.spine.add(stripe);
    }
    if (spec.coat) {
      const c = new THREE.Mesh(new THREE.CylinderGeometry(0.2, 0.27, 0.62, 12, 1, true), mat(spec.coat, 0.8));
      c.position.y = -0.05; c.material.side = THREE.DoubleSide;
      this.spine.add(c);
    }
    if (spec.tie) {
      const t = new THREE.Mesh(new THREE.BoxGeometry(0.05, 0.26, 0.02), mat(spec.tie));
      t.position.set(0, 0.42, -0.135);
      this.spine.add(t);
    }
    if (spec.armor) {
      const a = new THREE.Mesh(new THREE.CapsuleGeometry(0.2, 0.22, 3, 10), mat(spec.armor, 0.45));
      a.scale.set(1.08, 1, 0.75); a.position.y = 0.36;
      this.spine.add(a);
    }
    if (spec.robe) {
      // 长袍下摆：腿被罩住，走路时下摆轻摆
      this.skirt = new THREE.Mesh(new THREE.CylinderGeometry(0.2, 0.34, 0.86, 14, 1, true), mat(spec.top, 0.95));
      this.skirt.material.side = THREE.DoubleSide;
      this.skirt.position.y = -0.4;
      this.skirt.castShadow = true;
      this.hips.add(this.skirt);
      if (spec.sash) {
        const s = new THREE.Mesh(new THREE.BoxGeometry(0.07, 0.75, 0.3), mat(spec.sash));
        s.position.set(0.09, 0.32, 0); s.rotation.z = 0.5;
        this.spine.add(s);
      }
    }

    this.neck = new THREE.Group();
    this.neck.position.y = 0.66;
    this.spine.add(this.neck);
    const headR = spec.child ? 0.135 : 0.115;
    const head = new THREE.Mesh(new THREE.SphereGeometry(headR, 18, 14), skin);
    head.scale.set(0.92, 1.1, 1);
    head.position.y = 0.14;
    head.castShadow = true;
    this.neck.add(head);
    const hairG = new THREE.SphereGeometry(headR * 1.06, 18, 10, 0, Math.PI * 2, 0, Math.PI * (longHair ? 0.68 : 0.55));
    const hairMesh = new THREE.Mesh(hairG, hairM);
    hairMesh.scale.set(0.94, 1.08, 1.02);
    hairMesh.position.set(0, 0.165, 0.03);
    hairMesh.rotation.x = 0.55;
    if (!spec.helmet && !spec.cap && !spec.hat && !spec.headcloth) this.neck.add(hairMesh);
    if (longHair && !spec.headcloth && !spec.helmet) {
      const back = new THREE.Mesh(new THREE.CapsuleGeometry(0.1, 0.16, 3, 8), hairM);
      back.scale.set(1.15, 1, 0.55); back.position.set(0, 0.05, 0.07);
      this.neck.add(back);
    }
    if (outfit === "robe" && r() < 0.7) {  // 胡子
      const beard = new THREE.Mesh(new THREE.SphereGeometry(0.085, 10, 8, 0, Math.PI * 2, Math.PI * 0.45, Math.PI * 0.55), hairM);
      beard.position.set(0, 0.11, -0.04); beard.scale.set(1, 1.1, 1);
      this.neck.add(beard);
    }
    const eyeM = mat("#1d1a18", 0.4);
    for (const ex of [-0.04, 0.04]) {
      const eye = new THREE.Mesh(new THREE.SphereGeometry(0.014, 8, 6), eyeM);
      eye.position.set(ex, 0.155, -headR + 0.013);
      this.neck.add(eye);
    }
    const nose = new THREE.Mesh(new THREE.ConeGeometry(0.018, 0.04, 6), skin);
    nose.rotation.x = -Math.PI / 2;
    nose.position.set(0, 0.125, -headR - 0.003);
    this.neck.add(nose);
    if (spec.cap) {
      const c = new THREE.Mesh(new THREE.SphereGeometry(headR * 1.1, 14, 8, 0, Math.PI * 2, 0, Math.PI * 0.5), mat(spec.cap));
      c.position.y = 0.17;
      this.neck.add(c);
    }
    if (spec.mask) {
      const m = new THREE.Mesh(new THREE.BoxGeometry(0.15, 0.07, 0.04), mat("#cfe3e6"));
      m.position.set(0, 0.1, -0.1);
      this.neck.add(m);
    }
    if (spec.helmet) {
      const h = new THREE.Mesh(new THREE.SphereGeometry(headR * 1.18, 14, 8, 0, Math.PI * 2, 0, Math.PI * 0.55), mat(spec.helmet, 0.4));
      h.position.y = 0.17;
      this.neck.add(h);
    }
    if (spec.hat) {
      const brim = new THREE.Mesh(new THREE.CylinderGeometry(0.22, 0.22, 0.02, 16), mat(spec.hat));
      brim.position.y = 0.24;
      const crown = new THREE.Mesh(new THREE.CylinderGeometry(0.1, 0.12, 0.12, 12), mat(spec.hat));
      crown.position.y = 0.3;
      this.neck.add(brim, crown);
    }
    if (spec.headcloth) {
      const hc = new THREE.Mesh(new THREE.SphereGeometry(headR * 1.15, 14, 10, 0, Math.PI * 2, 0, Math.PI * 0.62), mat(spec.headcloth, 1));
      hc.position.set(0, 0.16, 0.02); hc.rotation.x = 0.35;
      this.neck.add(hc);
    }

    const sleeve = spec.robe ? top : top;
    const mkArm = (side) => {
      const sh = new THREE.Group();
      sh.position.set(side * 0.235, 0.54, 0);
      this.spine.add(sh);
      sh.add(limb(0.062, 0.24, spec.vest && false ? top : sleeve));
      const el = new THREE.Group();
      el.position.y = -0.31;
      sh.add(el);
      el.add(limb(0.052, 0.22, outfit === "scrubs" || outfit === "hivis" ? skin : sleeve));
      const hand = new THREE.Mesh(new THREE.SphereGeometry(0.05, 10, 8), skin);
      hand.position.y = -0.31;
      hand.castShadow = true;
      el.add(hand);
      return { sh, el, hand };
    };
    const mkLeg = (side) => {
      const hp = new THREE.Group();
      hp.position.set(side * 0.1, -0.05, 0);
      this.hips.add(hp);
      hp.add(limb(0.082, 0.34, bottom));
      const kn = new THREE.Group();
      kn.position.y = -0.44;
      hp.add(kn);
      kn.add(limb(0.07, 0.32, spec.robe ? skin : bottom));
      const ft = new THREE.Group();
      ft.position.y = -0.44;
      kn.add(ft);
      const shoeM = new THREE.Mesh(new THREE.BoxGeometry(0.11, 0.08, 0.25), shoe);
      shoeM.position.set(0, -0.02, -0.06);
      shoeM.castShadow = true;
      ft.add(shoeM);
      return { hp, kn, ft };
    };
    this.armL = mkArm(-1); this.armR = mkArm(1);
    this.legL = mkLeg(-1); this.legR = mkLeg(1);
    if (spec.child) this.body.scale.setScalar(0.62);
    this.height = spec.child ? 1.1 : 1.75;
    // 手机道具（phone 姿势时显示）
    this.phone = new THREE.Mesh(new THREE.BoxGeometry(0.07, 0.14, 0.012), mat("#111418", 0.3));
    this.phone.position.set(0, -0.06, -0.04);
    this.phone.visible = false;
    this.armR.hand.add(this.phone);
  }

  pose(action, ph = 0, t = 0) {
    // 复位
    this.body.rotation.set(0, 0, 0);
    this.body.position.set(0, 0, 0);
    this.phone.visible = false;
    const s = Math.sin(ph), c = Math.cos(ph);
    const A = { idle: 0.0, walk: 0.45, run: 0.85, sprint: 1.1, float: 0.25, fly: 0.0 }[action] ?? 0;
    const lean = { idle: 0, walk: 0.03, run: 0.16, sprint: 0.3, float: 0.1, fly: 1.35 }[action] ?? 0;
    this.hips.rotation.set(0, s * 0.12 * A, 0);
    this.spine.rotation.set(-lean, -s * 0.18 * A, 0);
    this.neck.rotation.set(lean * 0.6, s * 0.1 * A, 0);
    let bob = action === "walk" ? Math.abs(c) * 0.03 : (action === "run" || action === "sprint" ? Math.abs(c) * 0.09 * A : 0);
    if (action === "idle") bob = Math.sin(t * 2) * 0.005;
    if (action === "float") bob = Math.sin(t * 1.3) * 0.08;
    this.hips.position.y = 0.98 + bob - (action === "sprint" ? 0.05 : 0);
    const legSwing = (L, p) => {
      const sp = Math.sin(p);
      L.hp.rotation.set(-sp * 0.75 * A - lean * 0.6, 0, 0);
      const lift = Math.max(0, Math.cos(p));
      L.kn.rotation.set(0.15 + lift * (action === "walk" ? 0.5 : 1.6) * A, 0, 0);
      L.ft.rotation.set(-0.2 * A, 0, 0);
    };
    const armSwing = (R, p, side) => {
      R.sh.rotation.set(Math.sin(p) * 0.9 * A + lean * 0.4, 0, side * (0.12 + 0.05 * A));
      R.el.rotation.set(-(0.25 + 1.15 * A), 0, 0);
    };
    legSwing(this.legL, ph); legSwing(this.legR, ph + Math.PI);
    armSwing(this.armL, ph + Math.PI, -1); armSwing(this.armR, ph, 1);
    if (this.skirt) this.skirt.rotation.set(Math.sin(ph) * 0.06 * A, 0, 0);
    const L = this.legL, R = this.legR, aL = this.armL, aR = this.armR;
    switch (action) {
      case "idle":
        for (const g of [L, R]) { g.hp.rotation.x = 0; g.kn.rotation.x = 0.02; g.ft.rotation.x = 0; }
        for (const g of [aL, aR]) { g.sh.rotation.x = 0.05; g.el.rotation.x = -0.15; }
        break;
      case "float":
        L.hp.rotation.x = -0.3 + Math.sin(t) * 0.15; L.kn.rotation.x = 0.6;
        R.hp.rotation.x = 0.2 + Math.cos(t) * 0.15; R.kn.rotation.x = 0.3;
        aL.sh.rotation.set(0.4, 0, -0.5); aR.sh.rotation.set(-0.3, 0, 0.5);
        break;
      case "fly":
        this.hips.position.y = 1.2;
        this.spine.rotation.x = -1.35;
        aR.sh.rotation.x = 2.9; aR.el.rotation.x = -0.1;
        aL.sh.rotation.x = 0.2; aL.el.rotation.x = -0.3;
        for (const g of [L, R]) { g.hp.rotation.x = -1.4; g.kn.rotation.x = 0.15; }
        break;
      case "sit":
        this.hips.position.y = 0.52;
        for (const g of [L, R]) { g.hp.rotation.x = -1.5; g.kn.rotation.x = 1.5; g.ft.rotation.x = 0; }
        aL.sh.rotation.set(-0.3, 0, -0.1); aR.sh.rotation.set(-0.3, 0, 0.1);
        aL.el.rotation.x = -0.9; aR.el.rotation.x = -0.9;
        this.spine.rotation.x = 0.05 + Math.sin(t * 1.5) * 0.01;
        break;
      case "kneel":
        this.hips.position.y = 0.62;
        L.hp.rotation.x = -1.45; L.kn.rotation.x = 1.5;
        R.hp.rotation.x = 0.1; R.kn.rotation.x = 1.6;
        for (const g of [aL, aR]) { g.sh.rotation.x = -0.4; g.el.rotation.x = -1.2; }
        this.spine.rotation.x = 0.15;
        break;
      case "pray":
        this.hips.position.y = 0.62;
        L.hp.rotation.x = 0.0; L.kn.rotation.x = 1.6; R.hp.rotation.x = 0.0; R.kn.rotation.x = 1.6;
        aL.sh.rotation.set(-0.9, 0, 0.35); aR.sh.rotation.set(-0.9, 0, -0.35);
        aL.el.rotation.x = -1.3; aR.el.rotation.x = -1.3;
        this.spine.rotation.x = 0.2; this.neck.rotation.x = 0.45;
        break;
      case "lie":
        this.body.rotation.x = -Math.PI / 2;
        this.body.position.set(0, 0.2, 0.95);
        for (const g of [L, R]) { g.hp.rotation.x = 0; g.kn.rotation.x = 0.05; }
        for (const g of [aL, aR]) { g.sh.rotation.x = 0.1; g.el.rotation.x = -0.1; }
        break;
      case "fall":
        this.body.rotation.set(-1.2, 0, 0.4);
        this.body.position.set(0, 0.3, 0.6);
        aL.sh.rotation.set(-2.2, 0, -0.4); aR.sh.rotation.set(-2.0, 0, 0.5);
        L.hp.rotation.x = 0.5; R.hp.rotation.x = -0.4;
        break;
      case "point":
        for (const g of [L, R]) { g.hp.rotation.x = 0; g.kn.rotation.x = 0.02; }
        aL.sh.rotation.set(0.05, 0, -0.12); aL.el.rotation.x = -0.15;
        aR.sh.rotation.set(-1.45, 0.3, 0.1); aR.el.rotation.x = -0.1;
        break;
      case "phone":
        for (const g of [L, R]) { g.hp.rotation.x = 0; g.kn.rotation.x = 0.02; }
        aL.sh.rotation.set(0.05, 0, -0.12); aL.el.rotation.x = -0.15;
        aR.sh.rotation.set(-0.5, 0, 0.55); aR.el.rotation.set(-2.3, 0, 0);
        this.phone.visible = true;
        this.neck.rotation.x = 0.1;
        break;
    }
  }
}

// ---------------------------------------------------------------- 烘焙 ---
// 把一个摆好姿势的人物合成一个带顶点色的几何体（相对人物根节点）。
function bakeGeometry(person) {
  person.root.updateMatrixWorld(true);
  const inv = new THREE.Matrix4().copy(person.root.matrixWorld).invert();
  const parts = [];
  person.root.traverse((o) => {
    if (!o.isMesh || !o.visible) return;
    let g = o.geometry.index ? o.geometry.toNonIndexed() : o.geometry.clone();
    for (const k of Object.keys(g.attributes)) if (!["position", "normal"].includes(k)) g.deleteAttribute(k);
    g.applyMatrix4(new THREE.Matrix4().multiplyMatrices(inv, o.matrixWorld));
    const col = new THREE.Color(o.material.color);
    const n = g.attributes.position.count;
    const c = new Float32Array(n * 3);
    for (let i = 0; i < n; i++) { c[i * 3] = col.r; c[i * 3 + 1] = col.g; c[i * 3 + 2] = col.b; }
    g.setAttribute("color", new THREE.BufferAttribute(c, 3));
    parts.push(g);
  });
  return mergeGeometries(parts, false);
}

const CROWD_MAT = new THREE.MeshStandardMaterial({ vertexColors: true, roughness: 0.85 });
const bakeCache = new Map();

// spec: {outfit, count, action, layout, distance}
// 返回 Group：每个人一个烘焙网格（1 个 draw call），userData.rank ∈ [0,1) 用于"逐个消失"。
export function makeCrowd(spec, seed = 1) {
  const r = rng(seed * 104729 + 7);
  const group = new THREE.Group();
  const n = spec.count;
  const d = spec.distance || 6;
  for (let i = 0; i < n; i++) {
    let x, z, rot;
    switch (spec.layout) {
      case "line": x = (i - (n - 1) / 2) * 0.9; z = -d; rot = 0; break;
      case "row": x = (i - (n - 1) / 2) * 1.1; z = -d; rot = 0; break;
      case "around": { const a = (i / n) * Math.PI * 2; x = Math.cos(a) * d * 0.5; z = Math.sin(a) * d * 0.5 - d; rot = -a - Math.PI / 2; break; }
      case "seated": { const cols = Math.max(1, Math.ceil(Math.sqrt(n * 1.5))); x = ((i % cols) - (cols - 1) / 2) * 1.4; z = -d - Math.floor(i / cols) * 1.5; rot = 0; break; }
      case "crowd": x = (r() - 0.5) * d * 1.6; z = -d - r() * d * 1.2; rot = (r() - 0.5) * 0.8; break;
      default: x = (r() - 0.5) * d * 2.2; z = -r() * d * 2 - 1.5; rot = r() * Math.PI * 2;
    }
    // 外观按 (服装, 变体) 缓存：同一群里最多 12 种外观，烘焙成本可控
    const variant = i % 12;
    const ph = r() * Math.PI * 2;
    const key = `${spec.outfit}|${spec.action}|${seed}|${variant}`;
    if (!bakeCache.has(key)) {
      const p = new Person(spec.outfit, null, seed * 31 + variant);
      p.pose(spec.action, ph, variant);
      bakeCache.set(key, bakeGeometry(p));
    }
    const m = new THREE.Mesh(bakeCache.get(key), CROWD_MAT);
    m.castShadow = true;
    m.position.set(x, 0, z);
    m.rotation.y = rot;
    m.userData = { rank: r(), walk: spec.action === "walk" || spec.action === "run", base: [x, z], rot };
    group.add(m);
  }
  return group;
}

// 每帧：行走的人沿朝向前进；vanish ∈ [0,1] 时 rank < vanish 的人消失
export function updateCrowd(group, t, vanish = 0) {
  for (const m of group.children) {
    const u = m.userData;
    m.visible = !(vanish > 0 && u.rank < vanish);
    if (u.walk) {
      const sp = 1.2;
      m.position.x = u.base[0] - Math.sin(u.rot) * sp * t;
      m.position.z = u.base[1] - Math.cos(u.rot) * sp * t;
      m.position.y = Math.abs(Math.sin(t * 6 + u.rank * 9)) * 0.03;
    }
  }
}
