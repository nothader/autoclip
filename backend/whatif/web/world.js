// 环境：city / highway / desert / ocean / sky / orbit / deep_space / lab / void。
// 主体沿 -z 前进；地面内容按块（chunk）循环生成，块 k 的内容只由 k 决定（确定性）。
import * as THREE from "./vendor/three.module.min.js";
import { makeCar } from "./actors.js";

const std = (color, o = {}) => new THREE.MeshStandardMaterial({ color, roughness: 0.85, metalness: 0, ...o });

function hash(n) {
  let x = (n | 0) * 374761393 + 668265263;
  x = (x ^ (x >>> 13)) * 1274126177;
  return ((x ^ (x >>> 16)) >>> 0) / 4294967296;
}
function rng(seed) {
  let s = seed >>> 0 || 1;
  return () => { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; };
}

// ------------------------------------------------------------- 天空球 ---
function skyDome(top, mid, bottom, radius = 4000) {
  const g = new THREE.SphereGeometry(radius, 32, 16);
  const m = new THREE.ShaderMaterial({
    uniforms: { top: { value: new THREE.Color(top) }, mid: { value: new THREE.Color(mid) }, bottom: { value: new THREE.Color(bottom) } },
    vertexShader: `varying vec3 vP; void main(){ vP=normalize(position); gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0); }`,
    fragmentShader: `uniform vec3 top; uniform vec3 mid; uniform vec3 bottom; varying vec3 vP;
      void main(){ float h=vP.y; vec3 c = h>0.0 ? mix(mid, top, pow(smoothstep(0.0,0.6,h),0.8)) : mix(mid, bottom, smoothstep(0.0,-0.25,h)); gl_FragColor=vec4(c,1.0); }`,
    side: THREE.BackSide, depthWrite: false, fog: false,
  });
  const s = new THREE.Mesh(g, m);
  s.renderOrder = -10;
  return s;
}

function stars(n = 4000, radius = 3000, seed = 7) {
  const r = rng(seed);
  const p = new Float32Array(n * 3), c = new Float32Array(n * 3);
  for (let i = 0; i < n; i++) {
    const u = r() * 2 - 1, th = r() * Math.PI * 2, s = Math.sqrt(1 - u * u);
    p[i * 3] = s * Math.cos(th) * radius; p[i * 3 + 1] = u * radius; p[i * 3 + 2] = s * Math.sin(th) * radius;
    const b = 0.35 + Math.pow(r(), 3) * 0.65;
    c[i * 3] = b; c[i * 3 + 1] = b; c[i * 3 + 2] = b * (0.9 + r() * 0.2);
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute("position", new THREE.BufferAttribute(p, 3));
  g.setAttribute("color", new THREE.BufferAttribute(c, 3));
  const pts = new THREE.Points(g, new THREE.PointsMaterial({ size: 2.2, sizeAttenuation: false, vertexColors: true, fog: false, depthWrite: false }));
  pts.renderOrder = -9;
  return pts;
}

// ----------------------------------------------------------- 纹理工具 ---
function canvasTex(w, h, draw, repeat = true) {
  const c = document.createElement("canvas");
  c.width = w; c.height = h;
  draw(c.getContext("2d"), w, h);
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  if (repeat) { t.wrapS = t.wrapT = THREE.RepeatWrapping; }
  t.anisotropy = 4;
  return t;
}

function facadeTexture(base, win, seed, storefront) {
  const r = rng(seed);
  return canvasTex(256, 512, (x, w, h) => {
    x.fillStyle = base; x.fillRect(0, 0, w, h);
    // 轻微噪声
    for (let i = 0; i < 900; i++) { x.fillStyle = `rgba(0,0,0,${r() * 0.05})`; x.fillRect(r() * w, r() * h, 3, 3); }
    const cols = 4, rows = 8;
    const cw = w / cols, rh = h / rows;
    for (let i = 0; i < cols; i++) for (let j = 0; j < rows; j++) {
      const lit = r();
      x.fillStyle = lit > 0.85 ? "#e8d9a8" : win;
      x.fillRect(i * cw + cw * 0.18, j * rh + rh * 0.22, cw * 0.64, rh * 0.5);
      x.fillStyle = "rgba(255,255,255,0.10)";
      x.fillRect(i * cw + cw * 0.18, j * rh + rh * 0.22, cw * 0.64, rh * 0.08);
    }
    if (storefront) {
      x.fillStyle = "#26292e"; x.fillRect(0, h - rh * 1.1, w, rh * 1.1);
      x.fillStyle = storefront; x.fillRect(0, h - rh * 1.25, w, rh * 0.18);
      x.fillStyle = "rgba(180,200,220,0.35)";
      for (let i = 0; i < 3; i++) x.fillRect(10 + i * 82, h - rh * 0.95, 66, rh * 0.8);
    }
  });
}

// ----------------------------------------------------------- 块循环器 ---
class Chunks {
  constructor(L, make, nVariants, back, ahead) {
    this.L = L; this.back = back; this.ahead = ahead;
    this.group = new THREE.Group();
    this.variants = [];
    for (let i = 0; i < nVariants; i++) this.variants.push(make(i));
    this.slots = new Map();
  }
  update(dist) {
    const k = Math.floor(dist / this.L);
    const lo = k - this.back, hi = k + this.ahead;
    for (const [kk, obj] of this.slots) {
      if (kk < lo || kk > hi) { this.group.remove(obj); this.slots.delete(kk); }
    }
    for (let kk = lo; kk <= hi; kk++) {
      if (!this.slots.has(kk)) {
        const v = this.variants[Math.floor(hash(kk + 1000) * this.variants.length)];
        const o = v.clone();
        o.position.z = -kk * this.L;
        this.group.add(o);
        this.slots.set(kk, o);
      }
    }
  }
}

// ----------------------------------------------------------------- 道具 ---
const palmTrunk = new THREE.CylinderGeometry(0.16, 0.26, 9, 7);
palmTrunk.translate(0, 4.5, 0);
const frondG = new THREE.PlaneGeometry(0.7, 3.4, 1, 4);
{ // 弯曲的叶片
  const p = frondG.attributes.position;
  for (let i = 0; i < p.count; i++) { const y = p.getY(i) + 1.7; p.setZ(i, -0.12 * y * y); p.setY(i, y); }
  frondG.computeVertexNormals();
}
const palmMats = { trunk: std("#7a6450"), frond: std("#4f6b3a", { side: THREE.DoubleSide }) };
function palm(h = 1) {
  const g = new THREE.Group();
  const t = new THREE.Mesh(palmTrunk, palmMats.trunk);
  t.castShadow = true;
  g.add(t);
  for (let i = 0; i < 9; i++) {
    const f = new THREE.Mesh(frondG, palmMats.frond);
    f.position.y = 9;
    f.rotation.set(-1.05 - (i % 2) * 0.25, (i / 9) * Math.PI * 2, 0, "YXZ");
    f.castShadow = true;
    g.add(f);
  }
  g.scale.setScalar(h);
  return g;
}

const lampMat = std("#3a3d42", { metalness: 0.4, roughness: 0.5 });
function lamp() {
  const g = new THREE.Group();
  const pole = new THREE.Mesh(new THREE.CylinderGeometry(0.07, 0.09, 7, 6), lampMat);
  pole.position.y = 3.5;
  const arm = new THREE.Mesh(new THREE.BoxGeometry(1.6, 0.08, 0.08), lampMat);
  arm.position.set(-0.75, 6.95, 0);
  const head = new THREE.Mesh(new THREE.BoxGeometry(0.5, 0.12, 0.25), std("#e9e6dc", { emissive: 0x333322 }));
  head.position.set(-1.45, 6.88, 0);
  g.add(pole, arm, head);
  pole.castShadow = true;
  return g;
}

const personMats = ["#d9c27a", "#f2f2f2", "#3b5f8a", "#6b6b6b", "#8a3b3b", "#2f5e4c"].map((c) => std(c));
const skinMats = ["#d6a07a", "#a8714f", "#f0c9a8", "#7a4e33"].map((c) => std(c));
function pedestrian(r) {
  const g = new THREE.Group();
  const shirt = personMats[Math.floor(r() * personMats.length)];
  const skin = skinMats[Math.floor(r() * skinMats.length)];
  const legs = new THREE.Mesh(new THREE.CapsuleGeometry(0.15, 0.7, 3, 8), std(r() > 0.5 ? "#2c3440" : "#5a6070"));
  legs.position.y = 0.5;
  const body = new THREE.Mesh(new THREE.CapsuleGeometry(0.2, 0.45, 3, 8), shirt);
  body.position.y = 1.2;
  const head = new THREE.Mesh(new THREE.SphereGeometry(0.12, 10, 8), skin);
  head.position.y = 1.65;
  g.add(legs, body, head);
  g.traverse((o) => { if (o.isMesh) o.castShadow = true; });
  return g;
}

const CAR_COLORS = ["#e8b923", "#f0f0f0", "#b8bcc2", "#2f4f7f", "#8c1f1f", "#2b2b2b", "#e8b923", "#5f7f5f", "#c9c3b5"];

// ------------------------------------------------------------- city ---
function cityEnv(opts = {}) {
  const highway = !!opts.highway;
  const L = 48;
  const lanes = highway ? 4 : 2;            // 每个方向
  const laneW = 3.5;
  const roadL = -laneW * (lanes + 0.5), roadR = laneW * (lanes - 0.5);  // 主体在 x=0 的车道中心
  const roadW = roadR - roadL;
  const asphalt = std("#3b3e44", { roughness: 0.95 });
  const walk = std("#a7a49c", { roughness: 0.95 });
  const curb = std("#c8c5bd");
  const white = new THREE.MeshBasicMaterial({ color: 0xe9e9e4 });
  const yellow = new THREE.MeshBasicMaterial({ color: 0xd9b23a });

  const facadeCols = [
    ["#c9b79a", "#3b4652"], ["#9a5b45", "#2c343c"], ["#b9c0c6", "#33414d"], ["#e0d6c3", "#4b5866"],
    ["#7f8a94", "#25303a"], ["#d8c7a8", "#3d4954"], ["#a88f75", "#2e3842"], ["#cfd3d6", "#516170"],
  ];
  const awnings = ["#2f6e8f", "#9b2c2c", "#2f7a4a", "#d0a032", "#3a3a3a"];
  const facadeMats = [];
  for (let i = 0; i < 8; i++) {
    const [b, w] = facadeCols[i];
    facadeMats.push(facadeTexture(b, w, 100 + i, i % 2 === 0 ? awnings[i % awnings.length] : null));
  }

  const make = (vi) => {
    const r = rng(9000 + vi * 77);
    const g = new THREE.Group();
    const road = new THREE.Mesh(new THREE.PlaneGeometry(roadW, L), asphalt);
    road.rotation.x = -Math.PI / 2;
    road.position.set((roadL + roadR) / 2, 0, -L / 2);
    road.receiveShadow = true;
    g.add(road);
    // 车道线：中间双黄线（主体左侧），同向白色虚线
    for (const dx of [-0.12, 0.12]) {
      const y = new THREE.Mesh(new THREE.PlaneGeometry(0.12, L), yellow);
      y.rotation.x = -Math.PI / 2;
      y.position.set(-laneW / 2 + dx, 0.01, -L / 2);
      g.add(y);
    }
    for (let ln = 1; ln < lanes; ln++) for (const side of [1, -1]) {
      const xLine = side > 0 ? laneW / 2 + (ln - 1) * laneW : -laneW / 2 - ln * laneW;
      for (let d = 0; d < L; d += 12) {
        const m = new THREE.Mesh(new THREE.PlaneGeometry(0.14, 5), white);
        m.rotation.x = -Math.PI / 2;
        m.position.set(xLine, 0.01, -d - 3);
        g.add(m);
      }
    }
    // 斑马线（部分块）
    if (!highway && vi % 3 === 0) {
      for (let x = roadL + 0.6; x < roadR - 0.4; x += 1.2) {
        const m = new THREE.Mesh(new THREE.PlaneGeometry(0.6, 3.2), white);
        m.rotation.x = -Math.PI / 2;
        m.position.set(x, 0.012, -6);
        g.add(m);
      }
    }
    // 人行道 + 路缘
    const sideW = highway ? 3 : 5;
    for (const [x0, x1] of [[roadR, roadR + sideW], [roadL - sideW, roadL]]) {
      const s = new THREE.Mesh(new THREE.BoxGeometry(x1 - x0, 0.18, L), walk);
      s.position.set((x0 + x1) / 2, 0.09, -L / 2);
      s.receiveShadow = true;
      g.add(s);
      const cx = x0 === roadR ? x0 + 0.1 : x1 - 0.1;
      const c = new THREE.Mesh(new THREE.BoxGeometry(0.2, 0.2, L), curb);
      c.position.set(cx, 0.1, -L / 2);
      g.add(c);
    }
    // 楼
    for (const side of [1, -1]) {
      let z = 0;
      const xEdge = side > 0 ? roadR + sideW : roadL - sideW;
      while (z < L) {
        const w = 9 + r() * 9;
        const d = 10 + r() * 10;
        const h = highway ? 6 + r() * 14 : 10 + Math.pow(r(), 1.6) * 55;
        const fi = Math.floor(r() * facadeMats.length);
        const tex = facadeMats[fi].clone();
        tex.needsUpdate = true;
        tex.repeat.set(Math.max(1, Math.round(w / 6)), Math.max(1, Math.round(h / 12)));
        const mat = std("#ffffff", { map: tex });
        const top = std(facadeCols[fi][0]);
        const b = new THREE.Mesh(new THREE.BoxGeometry(d, h, Math.min(w, L - z)), [mat, mat, top, top, mat, mat]);
        b.position.set(xEdge + side * (d / 2 + 0.5), h / 2, -z - Math.min(w, L - z) / 2);
        b.castShadow = true; b.receiveShadow = true;
        g.add(b);
        z += w + (r() < 0.2 ? 3 : 0);
      }
    }
    // 棕榈树、路灯
    for (let z = 4 + r() * 6; z < L; z += 12 + r() * 8) {
      for (const side of [1, -1]) {
        if (r() < 0.75) {
          const p = palm(0.9 + r() * 0.5);
          p.position.set(side > 0 ? roadR + 1.4 : roadL - 1.4, 0.18, -z);
          p.rotation.y = r() * 6;
          g.add(p);
        }
      }
    }
    for (const side of [1, -1]) {
      const l = lamp();
      l.position.set(side > 0 ? roadR + 0.6 : roadL - 0.6, 0.18, -L * 0.5 - r() * 10);
      l.rotation.y = side > 0 ? 0 : Math.PI;
      g.add(l);
    }
    // 行人
    if (!highway) for (let i = 0; i < 7; i++) {
      const p = pedestrian(r);
      const side = r() < 0.5 ? 1 : -1;
      p.position.set(side > 0 ? roadR + 1.5 + r() * 3 : roadL - 1.5 - r() * 3, 0.18, -r() * L);
      p.rotation.y = r() < 0.5 ? 0 : Math.PI;
      g.add(p);
    }
    // 车：主体所在车道之外
    const laneXs = [];
    for (let i = 1; i < lanes; i++) laneXs.push(i * laneW);
    for (let i = 1; i <= lanes; i++) laneXs.push(-i * laneW);
    for (const lx of laneXs) {
      for (let z = r() * 10; z < L - 4; z += 7 + r() * (highway ? 6 : 14)) {
        if (r() < (highway ? 0.8 : 0.55)) {
          const car = makeCar(CAR_COLORS[Math.floor(r() * CAR_COLORS.length)]);
          car.position.set(lx + (r() - 0.5) * 0.4, 0, -z - 2.5);
          if (lx < 0) car.rotation.y = Math.PI;
          g.add(car);
        }
      }
    }
    return g;
  };

  const chunks = new Chunks(L, make, 8, 3, highway ? 9 : 7);
  const root = new THREE.Group();
  root.add(chunks.group);
  // 远处地面兜底
  const ground = new THREE.Mesh(new THREE.PlaneGeometry(4000, 4000), std(highway ? "#8f8a7c" : "#7d7a73"));
  ground.rotation.x = -Math.PI / 2;
  ground.position.y = -0.02;
  root.add(ground);
  const sky = skyDome("#7f97b3", "#c9d3dc", "#a9adb0");
  root.add(sky);
  return {
    root,
    fog: new THREE.Fog(highway ? 0xc6ccd0 : 0xbfc8d0, 60, highway ? 420 : 300),
    light: { sun: 2.4, hemi: 1.1, sunDir: [-0.5, 1, 0.35], sky: 0xdfe8f2, ground: 0x6d6a63 },
    update(fr, subjPos) { chunks.update(fr.z || 0); ground.position.x = subjPos.x; ground.position.z = subjPos.z; sky.position.copy(subjPos); },
  };
}

// ------------------------------------------------------------ desert ---
function desertEnv() {
  const L = 60;
  const sandTex = canvasTex(512, 512, (x, w, h) => {
    const r = rng(42);
    x.fillStyle = "#d4b48a"; x.fillRect(0, 0, w, h);
    for (let i = 0; i < 6000; i++) { const v = r(); x.fillStyle = v > 0.5 ? `rgba(255,240,210,${r() * 0.15})` : `rgba(120,90,50,${r() * 0.12})`; x.fillRect(r() * w, r() * h, 2, 2); }
  });
  sandTex.repeat.set(40, 40);
  const sand = std("#ffffff", { map: sandTex, roughness: 1 });
  const asphalt = std("#45474b", { roughness: 0.95 });
  const white = new THREE.MeshBasicMaterial({ color: 0xe6e3da });
  const yellow = new THREE.MeshBasicMaterial({ color: 0xd2ad44 });
  const poleMat = std("#5a4a3a");
  const rockMat = std("#9a7b5e");
  const brush = std("#7d7a4e");

  const make = (vi) => {
    const r = rng(500 + vi * 31);
    const g = new THREE.Group();
    const road = new THREE.Mesh(new THREE.PlaneGeometry(9, L), asphalt);
    road.rotation.x = -Math.PI / 2;
    road.position.set(1.0, 0.01, -L / 2);
    road.receiveShadow = true;
    g.add(road);
    for (let d = 0; d < L; d += 12) {
      const m = new THREE.Mesh(new THREE.PlaneGeometry(0.15, 5.5), yellow);
      m.rotation.x = -Math.PI / 2; m.position.set(-1.9, 0.02, -d - 3);
      g.add(m);
    }
    for (const x of [-3.3, 5.3]) {
      const m = new THREE.Mesh(new THREE.PlaneGeometry(0.15, L), white);
      m.rotation.x = -Math.PI / 2; m.position.set(x, 0.02, -L / 2);
      g.add(m);
    }
    // 电线杆
    const pole = new THREE.Mesh(new THREE.CylinderGeometry(0.12, 0.15, 9, 6), poleMat);
    pole.position.set(9, 4.5, -L / 2);
    const bar = new THREE.Mesh(new THREE.BoxGeometry(2.2, 0.12, 0.12), poleMat);
    bar.position.set(9, 8.4, -L / 2);
    pole.castShadow = true;
    g.add(pole, bar);
    for (let i = 0; i < 10; i++) {
      const s = 0.3 + r() * 1.4;
      const isRock = r() < 0.4;
      const m = new THREE.Mesh(isRock ? new THREE.DodecahedronGeometry(s, 0) : new THREE.IcosahedronGeometry(s * 0.6, 0), isRock ? rockMat : brush);
      const side = r() < 0.5 ? -1 : 1;
      m.position.set(side * (7 + r() * 40), s * 0.3, -r() * L);
      m.castShadow = true;
      g.add(m);
    }
    return g;
  };
  const chunks = new Chunks(L, make, 6, 2, 9);
  const root = new THREE.Group();
  root.add(chunks.group);
  const ground = new THREE.Mesh(new THREE.PlaneGeometry(5000, 5000), sand);
  ground.rotation.x = -Math.PI / 2;
  ground.receiveShadow = true;
  root.add(ground);
  // 远山 / 沙丘环（跟随主体，形成地平线）
  const dunes = new THREE.Group();
  const duneMat = std("#c7a57a", { roughness: 1 });
  const r = rng(77);
  for (let i = 0; i < 40; i++) {
    const a = (i / 40) * Math.PI * 2;
    const d = new THREE.Mesh(new THREE.SphereGeometry(1, 16, 8, 0, Math.PI * 2, 0, Math.PI / 2), duneMat);
    const R = 700 + r() * 300;
    d.scale.set(120 + r() * 160, 25 + r() * 70, 120 + r() * 120);
    d.position.set(Math.cos(a) * R, -2, Math.sin(a) * R);
    dunes.add(d);
  }
  root.add(dunes);
  const sky = skyDome("#6f9fd0", "#d9e3e8", "#d6c3a3");
  root.add(sky);
  return {
    root,
    fog: new THREE.Fog(0xdcd6c8, 120, 1100),
    light: { sun: 3.0, hemi: 1.0, sunDir: [0.6, 1, 0.2], sky: 0xeaf2ff, ground: 0xb89a70 },
    update(fr, p) {
      chunks.update(fr.z || 0);
      ground.position.set(p.x, 0, p.z);
      sandTex.offset.set(p.x / 125, -p.z / 125);
      dunes.position.set(p.x, 0, p.z);
      sky.position.copy(p);
    },
  };
}

// ------------------------------------------------------------- ocean ---
function oceanEnv() {
  const seg = 120, size = 600;
  const geo = new THREE.PlaneGeometry(size, size, seg, seg);
  geo.rotateX(-Math.PI / 2);
  const base = geo.attributes.position.array.slice();
  const water = new THREE.Mesh(geo, std("#1f5f7d", { roughness: 0.25, metalness: 0.1, flatShading: true }));
  water.receiveShadow = true;
  const root = new THREE.Group();
  root.add(water);
  const sky = skyDome("#5b8fc7", "#cfe0ea", "#2b5d78");
  root.add(sky);
  return {
    root,
    fog: new THREE.Fog(0xbfd3de, 80, 700),
    light: { sun: 2.6, hemi: 1.0, sunDir: [-0.4, 0.8, -0.6], sky: 0xdcecff, ground: 0x1d4256 },
    update(fr, p) {
      water.position.set(p.x, 0, p.z);
      const a = geo.attributes.position.array, t = fr.t;
      for (let i = 0; i < a.length; i += 3) {
        const x = base[i] + p.x, z = base[i + 2] + p.z;
        a[i + 1] = -0.4 + Math.sin(x * 0.15 + t * 1.3) * 0.35 + Math.sin(z * 0.11 - t * 1.1) * 0.45 + Math.sin((x + z) * 0.31 + t * 2.0) * 0.12;
      }
      geo.attributes.position.needsUpdate = true;
      geo.computeVertexNormals();
      sky.position.copy(p);
    },
  };
}

// ---------------------------------------------------------- 云海 / sky ---
function cloudTex() {
  return canvasTex(256, 256, (x, w, h) => {
    const r = rng(3);
    for (let i = 0; i < 40; i++) {
      const cx = w / 2 + (r() - 0.5) * w * 0.5, cy = h / 2 + (r() - 0.5) * h * 0.3, rad = 30 + r() * 60;
      const g = x.createRadialGradient(cx, cy, 0, cx, cy, rad);
      g.addColorStop(0, "rgba(255,255,255,0.55)"); g.addColorStop(1, "rgba(255,255,255,0)");
      x.fillStyle = g; x.fillRect(0, 0, w, h);
    }
  }, false);
}
function skyEnv() {
  const L = 400;
  const tex = cloudTex();
  const mat = new THREE.SpriteMaterial({ map: tex, transparent: true, depthWrite: false, opacity: 0.95 });
  const make = (vi) => {
    const r = rng(800 + vi * 13);
    const g = new THREE.Group();
    for (let i = 0; i < 26; i++) {
      const s = new THREE.Sprite(mat);
      const sc = 80 + r() * 160;
      s.scale.set(sc * 1.8, sc, 1);
      const x = (r() - 0.5) * 1400;
      s.position.set(Math.abs(x) < 120 ? x + Math.sign(x || 1) * 120 : x, -220 - r() * 160, -r() * L);
      g.add(s);
    }
    return g;
  };
  const chunks = new Chunks(L, make, 5, 2, 6);
  const root = new THREE.Group();
  root.add(chunks.group);
  const ground = new THREE.Mesh(new THREE.PlaneGeometry(20000, 20000), std("#6c7f6a"));
  ground.rotation.x = -Math.PI / 2;
  ground.position.y = -1500;
  root.add(ground);
  const sky = skyDome("#2c5f9e", "#a9c6e0", "#9fb2bf");
  root.add(sky);
  return {
    root,
    fog: new THREE.Fog(0xb7cadb, 400, 2600),
    light: { sun: 2.8, hemi: 1.0, sunDir: [0.3, 1, -0.4], sky: 0xe8f1ff, ground: 0x8899aa },
    update(fr, p) { chunks.update(fr.z || 0); ground.position.x = p.x; ground.position.z = p.z; sky.position.copy(p); },
  };
}

// -------------------------------------------------------------- 地球 ---
let earthTexCache = null;
function earthTextures() {
  if (earthTexCache) return earthTexCache;
  const W = 2048, H = 1024;
  // 值噪声 → 大陆
  const r = rng(2024);
  const G = 64, grid = [];
  for (let i = 0; i < G * G; i++) grid.push(r());
  const noise = (x, y) => {
    const xi = Math.floor(x), yi = Math.floor(y), xf = x - xi, yf = y - yi;
    const g = (a, b) => grid[((b % G + G) % G) * G + ((a % G + G) % G)];
    const s = (t) => t * t * (3 - 2 * t);
    const a = g(xi, yi), b = g(xi + 1, yi), c = g(xi, yi + 1), d = g(xi + 1, yi + 1);
    return a + (b - a) * s(xf) + (c - a) * s(yf) + (a - b - c + d) * s(xf) * s(yf);
  };
  const fbm = (x, y) => { let v = 0, amp = 0.5, f = 1; for (let o = 0; o < 5; o++) { v += amp * noise(x * f, y * f); amp *= 0.5; f *= 2; } return v; };
  const color = canvasTex(W, H, (x) => {
    const img = x.createImageData(W, H);
    for (let j = 0; j < H; j++) for (let i = 0; i < W; i++) {
      const u = i / W * 8, v = j / H * 4;
      const n = fbm(u, v);
      const lat = Math.abs(j / H - 0.5) * 2;
      let R, Gc, B;
      if (lat > 0.88) { R = 235; Gc = 240; B = 245; }
      else if (n > 0.53) {
        const dry = fbm(u * 2 + 9, v * 2) > 0.5 && lat < 0.5;
        R = dry ? 176 : 86; Gc = dry ? 150 : 118; B = dry ? 104 : 66;
      } else { const deep = Math.min(1, (0.53 - n) * 5); R = 18 + 20 * (1 - deep); Gc = 52 + 40 * (1 - deep); B = 110 + 40 * (1 - deep); }
      const k = (j * W + i) * 4;
      img.data[k] = R; img.data[k + 1] = Gc; img.data[k + 2] = B; img.data[k + 3] = 255;
    }
    x.putImageData(img, 0, 0);
  });
  const clouds = canvasTex(W, H, (x) => {
    const img = x.createImageData(W, H);
    for (let j = 0; j < H; j++) for (let i = 0; i < W; i++) {
      const n = fbm(i / W * 12 + 50, j / H * 6 + 20);
      const a = Math.max(0, Math.min(1, (n - 0.5) * 3.2));
      const k = (j * W + i) * 4;
      img.data[k] = img.data[k + 1] = img.data[k + 2] = 255; img.data[k + 3] = a * 235;
    }
    x.putImageData(img, 0, 0);
  });
  earthTexCache = { color, clouds };
  return earthTexCache;
}

function makeEarth(R) {
  const { color, clouds } = earthTextures();
  const g = new THREE.Group();
  const e = new THREE.Mesh(new THREE.SphereGeometry(R, 96, 64), std("#ffffff", { map: color, roughness: 0.9 }));
  const c = new THREE.Mesh(new THREE.SphereGeometry(R * 1.008, 96, 64), new THREE.MeshStandardMaterial({ map: clouds, transparent: true, depthWrite: false, roughness: 1 }));
  const atm = new THREE.Mesh(new THREE.SphereGeometry(R * 1.06, 64, 48), new THREE.ShaderMaterial({
    vertexShader: `varying vec3 vN; varying vec3 vV; void main(){ vN=normalize(normalMatrix*normal); vec4 mv=modelViewMatrix*vec4(position,1.0); vV=normalize(-mv.xyz); gl_Position=projectionMatrix*mv; }`,
    fragmentShader: `varying vec3 vN; varying vec3 vV; void main(){ float f=pow(1.0-abs(dot(vN,vV)),2.5); gl_FragColor=vec4(0.35,0.62,1.0,f*1.1); }`,
    side: THREE.BackSide, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, fog: false,
  }));
  e.material.fog = false; c.material.fog = false;
  g.add(e, c, atm);
  g.userData.clouds = c;
  return g;
}

function orbitEnv() {
  const R = 700;
  const root = new THREE.Group();
  const st = stars();
  root.add(st);
  const earth = makeEarth(R);
  root.add(earth);
  return {
    root, fog: null, background: 0x000000,
    light: { sun: 3.2, hemi: 0.25, sunDir: [1, 0.6, 0.3], sky: 0x8899bb, ground: 0x000000 },
    update(fr, p) {
      // 主体在地球上方 ~60 单位处掠过，地球缓慢转动
      // 球心在正下方，任何朝向的镜头都能看到弧形地平线；本段内逐渐远离
      const k = fr.frac || 0;
      const h = 30 + 70 * k;
      earth.position.set(p.x, p.y - R - h, p.z);
      earth.rotation.x = (fr.z || 0) / R * 0.6 + 0.4;
      earth.rotation.y = 0.8;
      earth.userData.clouds.rotation.y = fr.t * 0.003;
      st.position.copy(p);
    },
  };
}

function deepSpaceEnv() {
  const root = new THREE.Group();
  const st = stars(6000, 3000, 11);
  root.add(st);
  const earth = makeEarth(60);
  root.add(earth);
  const moon = new THREE.Mesh(new THREE.SphereGeometry(16, 48, 32), std("#9a9a96", { roughness: 1, fog: false }));
  root.add(moon);
  const sun = new THREE.Sprite(new THREE.SpriteMaterial({ map: canvasTex(128, 128, (x) => {
    const g = x.createRadialGradient(64, 64, 0, 64, 64, 64);
    g.addColorStop(0, "rgba(255,250,235,1)"); g.addColorStop(0.15, "rgba(255,230,180,0.8)"); g.addColorStop(1, "rgba(255,200,120,0)");
    x.fillStyle = g; x.fillRect(0, 0, 128, 128);
  }, false), transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, fog: false }));
  sun.scale.set(500, 500, 1);
  root.add(sun);
  return {
    root, fog: null, background: 0x000000,
    light: { sun: 3.0, hemi: 0.2, sunDir: [1, 0.3, 0.6], sky: 0x8899bb, ground: 0x000000 },
    update(fr, p) {
      const k = fr.frac || 0;
      earth.position.set(p.x - 40, p.y - 30, p.z + 250 + k * 900);   // 地球在身后渐远
      earth.rotation.y = fr.t * 0.05;
      moon.position.set(p.x + 220, p.y + 60, p.z - 900 + k * 500);
      sun.position.set(p.x + 1800, p.y + 900, p.z - 1500);
      st.position.copy(p);
    },
  };
}

function labEnv() {
  const root = new THREE.Group();
  const floor = new THREE.Mesh(new THREE.PlaneGeometry(4000, 4000), std("#e9e9ea", { roughness: 0.9 }));
  floor.rotation.x = -Math.PI / 2;
  floor.receiveShadow = true;
  root.add(floor);
  const grid = new THREE.GridHelper(4000, 800, 0xc9c9cc, 0xd8d8db);
  grid.position.y = 0.01;
  root.add(grid);
  return {
    root, fog: new THREE.Fog(0xf2f2f3, 40, 260), background: 0xf2f2f3,
    light: { sun: 2.2, hemi: 1.4, sunDir: [-0.3, 1, 0.5], sky: 0xffffff, ground: 0xcccccc },
    update(fr, p) {
      floor.position.set(p.x, 0, p.z);
      grid.position.set(p.x - (p.x % 5), 0.01, p.z - (p.z % 5));
    },
  };
}

function voidEnv() {
  const root = new THREE.Group();
  return { root, fog: null, background: 0x000000, light: { sun: 0.5, hemi: 0.3, sunDir: [0, 1, 0], sky: 0x222222, ground: 0 }, update() {} };
}

const BUILDERS = {
  city: () => cityEnv(), highway: () => cityEnv({ highway: true }), desert: desertEnv, ocean: oceanEnv,
  sky: skyEnv, orbit: orbitEnv, deep_space: deepSpaceEnv, lab: labEnv, void: voidEnv,
};

export class World {
  constructor(scene) {
    this.scene = scene;
    this.envs = {};
    this.active = null;
    this.hemi = new THREE.HemisphereLight(0xffffff, 0x444444, 1);
    this.sun = new THREE.DirectionalLight(0xffffff, 2.5);
    this.sun.castShadow = true;
    this.sun.shadow.mapSize.set(2048, 2048);
    this.sun.shadow.bias = -0.0004;
    this.sun.shadow.normalBias = 0.02;
    scene.add(this.hemi, this.sun, this.sun.target);
  }
  use(name) {
    if (this.active === name) return this.envs[name];
    if (this.active) this.scene.remove(this.envs[this.active].root);
    if (!this.envs[name]) this.envs[name] = (BUILDERS[name] || BUILDERS.void)();
    const env = this.envs[name];
    this.scene.add(env.root);
    this.scene.fog = env.fog;
    this.scene.background = env.background !== undefined ? new THREE.Color(env.background) : null;
    const L = env.light;
    this.hemi.color.set(L.sky); this.hemi.groundColor.set(L.ground); this.hemi.intensity = L.hemi;
    this.sun.intensity = L.sun;
    this.sunDir = new THREE.Vector3(...L.sunDir).normalize();
    this.active = name;
    return env;
  }
  update(fr, subjPos, scale = 1) {
    const env = this.envs[this.active];
    env.update(fr, subjPos);
    // 阴影相机跟随主体
    const ext = 30 * Math.max(1, scale);
    const sc = this.sun.shadow.camera;
    sc.left = -ext; sc.right = ext; sc.top = ext; sc.bottom = -ext; sc.near = 1; sc.far = 400 * Math.max(1, scale);
    sc.updateProjectionMatrix();
    this.sun.position.copy(subjPos).addScaledVector(this.sunDir, 150 * Math.max(1, scale));
    this.sun.target.position.copy(subjPos);
  }
}
