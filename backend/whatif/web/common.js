// 场景公共工具：材质、随机数、天空球、星空、画布纹理、分块循环器、道具、地球。
import * as THREE from "three";
import { makeCar } from "./actors.js";
export { makeCar };

export const std = (color, o = {}) => new THREE.MeshStandardMaterial({ color, roughness: 0.85, metalness: 0, ...o });

export function hash(n) {
  let x = (n | 0) * 374761393 + 668265263;
  x = (x ^ (x >>> 13)) * 1274126177;
  return ((x ^ (x >>> 16)) >>> 0) / 4294967296;
}
export function rng(seed) {
  let s = seed >>> 0 || 1;
  return () => { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; };
}

// ------------------------------------------------------------- 天空球 ---
export function skyDome(top, mid, bottom, radius = 4000) {
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

export function stars(n = 4000, radius = 3000, seed = 7) {
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

// ---------------------------------------------------------- 有生气的天空 ---
// 太空不再是纯黑：深蓝底 + 程序生成的星云（两种颜色）+ 斜穿的银河带 + 星点
const NEBULA_PALETTES = [["#7b2ff7", "#00c2c7"], ["#ff5d8f", "#3a86ff"], ["#ff9f1c", "#8338ec"], ["#2ec4b6", "#e71d36"]];
export function spaceSky(radius = 900, seed = 3) {
  const g = new THREE.Group();
  const [c1, c2] = NEBULA_PALETTES[Math.abs(seed) % NEBULA_PALETTES.length];
  const mat = new THREE.ShaderMaterial({
    uniforms: { c1: { value: new THREE.Color(c1) }, c2: { value: new THREE.Color(c2) }, sd: { value: (seed % 17) * 1.37 } },
    vertexShader: `varying vec3 vP; void main(){ vP=normalize(position); gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0); }`,
    fragmentShader: `uniform vec3 c1; uniform vec3 c2; uniform float sd; varying vec3 vP;
      float h(vec3 p){ return fract(sin(dot(p, vec3(127.1, 311.7, 74.7))) * 43758.5453); }
      float n(vec3 p){ vec3 i=floor(p), f=fract(p); f=f*f*(3.0-2.0*f);
        return mix(mix(mix(h(i),h(i+vec3(1,0,0)),f.x),mix(h(i+vec3(0,1,0)),h(i+vec3(1,1,0)),f.x),f.y),
                   mix(mix(h(i+vec3(0,0,1)),h(i+vec3(1,0,1)),f.x),mix(h(i+vec3(0,1,1)),h(i+vec3(1,1,1)),f.x),f.y),f.z); }
      float fbm(vec3 p){ float a=0.5, s=0.0; for(int k=0;k<5;k++){ s+=a*n(p); p*=2.03; a*=0.5; } return s; }
      void main(){
        vec3 d = normalize(vP);
        float band = exp(-pow((d.y - 0.35 * d.x) * 3.2, 2.0));
        float a = fbm(d * 2.6 + sd), b = fbm(d * 4.1 - sd + 3.0);
        vec3 col = vec3(0.025, 0.035, 0.075) + vec3(0.03, 0.03, 0.06) * (1.0 - abs(d.y));
        col += c1 * smoothstep(0.48, 0.85, a) * 0.55;
        col += c2 * smoothstep(0.52, 0.9, b) * 0.45;
        col += vec3(0.55, 0.52, 0.62) * band * (0.18 + 0.45 * b);
        gl_FragColor = vec4(col, 1.0);
      }`,
    side: THREE.BackSide, depthWrite: false, fog: false,
  });
  const sphere = new THREE.Mesh(new THREE.SphereGeometry(radius, 48, 24), mat);
  sphere.renderOrder = -10;
  g.add(sphere, stars(5000, radius * 0.9, seed + 17));
  return g;
}

// 白天天空上的软云（远处一圈 sprite），颜色带一点地平线的色调
let CLOUD_TEX = null;
export function skyClouds(radius = 800, tint = "#ffffff", seed = 5, n = 16) {
  CLOUD_TEX ??= canvasTex(256, 128, (x) => {
    for (let k = 0; k < 7; k++) {
      const cx = 50 + k * 26 + Math.sin(k * 2.3) * 10, cy = 70 + Math.cos(k * 1.7) * 12, r = 34 + (k % 3) * 10;
      const gr = x.createRadialGradient(cx, cy, 0, cx, cy, r);
      gr.addColorStop(0, "rgba(255,255,255,0.95)"); gr.addColorStop(1, "rgba(255,255,255,0)");
      x.fillStyle = gr; x.fillRect(0, 0, 256, 128);
    }
  }, false);
  const r = rng(seed), g = new THREE.Group();
  const col = new THREE.Color("#ffffff").lerp(new THREE.Color(tint), 0.25);
  for (let i = 0; i < n; i++) {
    const az = r() * Math.PI * 2, el = (4 + r() * 26) * Math.PI / 180;
    const sp = new THREE.Sprite(new THREE.SpriteMaterial({ map: CLOUD_TEX, color: col, transparent: true, opacity: 0.55 + r() * 0.35, depthWrite: false, fog: false }));
    sp.position.set(Math.cos(az) * Math.cos(el) * radius, Math.sin(el) * radius, Math.sin(az) * Math.cos(el) * radius);
    const w = 160 + r() * 220;
    sp.scale.set(w, w * 0.45, 1);
    sp.renderOrder = -8;
    g.add(sp);
  }
  return g;
}

// ----------------------------------------------------------- 纹理工具 ---
export function canvasTex(w, h, draw, repeat = true) {
  const c = document.createElement("canvas");
  c.width = w; c.height = h;
  draw(c.getContext("2d"), w, h);
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  if (repeat) { t.wrapS = t.wrapT = THREE.RepeatWrapping; }
  t.anisotropy = 4;
  return t;
}

export function facadeTexture(base, win, seed, storefront) {
  // 返回立面贴图；tex.userData.glow 是对应的"亮灯窗户"自发光贴图（夜景用）
  const r = rng(seed);
  const lit = [];
  const tex = canvasTex(256, 512, (x, w, h) => {
    x.fillStyle = base; x.fillRect(0, 0, w, h);
    for (let i = 0; i < 900; i++) { x.fillStyle = `rgba(0,0,0,${r() * 0.05})`; x.fillRect(r() * w, r() * h, 3, 3); }
    const cols = 4, rows = 8;
    const cw = w / cols, rh = h / rows;
    for (let i = 0; i < cols; i++) for (let j = 0; j < rows; j++) {
      const on = r();
      x.fillStyle = on > 0.85 ? "#e8d9a8" : win;
      x.fillRect(i * cw + cw * 0.18, j * rh + rh * 0.22, cw * 0.64, rh * 0.5);
      x.fillStyle = "rgba(255,255,255,0.10)";
      x.fillRect(i * cw + cw * 0.18, j * rh + rh * 0.22, cw * 0.64, rh * 0.08);
      if (on > 0.45) lit.push([i * cw + cw * 0.18, j * rh + rh * 0.22, cw * 0.64, rh * 0.5]);
    }
    if (storefront) {
      x.fillStyle = "#26292e"; x.fillRect(0, h - rh * 1.1, w, rh * 1.1);
      x.fillStyle = storefront; x.fillRect(0, h - rh * 1.25, w, rh * 0.18);
      x.fillStyle = "rgba(180,200,220,0.35)";
      for (let i = 0; i < 3; i++) x.fillRect(10 + i * 82, h - rh * 0.95, 66, rh * 0.8);
    }
  });
  tex.userData.glow = canvasTex(256, 512, (x, w, h) => {
    x.fillStyle = "#000"; x.fillRect(0, 0, w, h);
    for (const [a, b, c, d] of lit) { x.fillStyle = r() < 0.5 ? "#ffd38a" : "#fff0c8"; x.fillRect(a, b, c, d); }
    if (storefront) { x.fillStyle = "#ffe2a8"; for (let i = 0; i < 3; i++) x.fillRect(10 + i * 82, h - h / 8 * 0.95, 66, h / 8 * 0.8); }
  });
  return tex;
}

// ----------------------------------------------------------- 块循环器 ---
export class Chunks {
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
export const palmTrunk = new THREE.CylinderGeometry(0.16, 0.26, 9, 7);
palmTrunk.translate(0, 4.5, 0);
export const frondG = new THREE.PlaneGeometry(0.7, 3.4, 1, 4);
{ // 弯曲的叶片
  const p = frondG.attributes.position;
  for (let i = 0; i < p.count; i++) { const y = p.getY(i) + 1.7; p.setZ(i, -0.12 * y * y); p.setY(i, y); }
  frondG.computeVertexNormals();
}
export const palmMats = { trunk: std("#7a6450"), frond: std("#4f6b3a", { side: THREE.DoubleSide }) };
export function palm(h = 1) {
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

export const lampMat = std("#3a3d42", { metalness: 0.4, roughness: 0.5 });
export function lamp() {
  const g = new THREE.Group();
  const pole = new THREE.Mesh(new THREE.CylinderGeometry(0.07, 0.09, 7, 6), lampMat);
  pole.position.y = 3.5;
  const arm = new THREE.Mesh(new THREE.BoxGeometry(1.6, 0.08, 0.08), lampMat);
  arm.position.set(-0.75, 6.95, 0);
  const head = new THREE.Mesh(new THREE.BoxGeometry(0.5, 0.12, 0.25), std("#e9e6dc", { emissive: 0x333322 }));
  head.position.set(-1.45, 6.88, 0);
  g.add(pole, arm, head);
  head.userData.tag = "lamp";
  pole.castShadow = true;
  return g;
}

export const personMats = ["#d9c27a", "#f2f2f2", "#3b5f8a", "#6b6b6b", "#8a3b3b", "#2f5e4c"].map((c) => std(c));
export const skinMats = ["#d6a07a", "#a8714f", "#f0c9a8", "#7a4e33"].map((c) => std(c));
export function pedestrian(r) {
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
  g.userData = { tag: "ped", rank: r() };
  return g;
}

export const CAR_COLORS = ["#e8b923", "#f0f0f0", "#b8bcc2", "#2f4f7f", "#8c1f1f", "#2b2b2b", "#e8b923", "#5f7f5f", "#c9c3b5"];


export function cloudTex() {
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

// -------------------------------------------------------------- 地球 ---
const earthTexCache = new Map();
let realEarth = null;
// 真实地球贴图（NASA Blue Marble，公有领域）；app 在第一帧前预加载
export function setEarthImage(tex) { realEarth = tex; }
export function earthTextures(variant = "normal") {
  if (earthTexCache.has(variant)) return earthTexCache.get(variant);
  if (variant === "normal" && realEarth && earthTexCache.has("_clouds")) {
    const res = { color: realEarth, clouds: earthTexCache.get("_clouds") };
    earthTexCache.set(variant, res);
    return res;
  }
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
      } else if (variant === "dry") { const deep = Math.min(1, (0.53 - n) * 5); R = 120 - 50 * deep; Gc = 104 - 46 * deep; B = 86 - 40 * deep; }
      else { const deep = Math.min(1, (0.53 - n) * 5); R = 18 + 20 * (1 - deep); Gc = 52 + 40 * (1 - deep); B = 110 + 40 * (1 - deep); }
      if (variant === "frozen") { const m = 0.72; R = R * (1 - m) + 225 * m; Gc = Gc * (1 - m) + 236 * m; B = B * (1 - m) + 246 * m; }
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
  const res = { color, clouds };
  earthTexCache.set("_clouds", clouds);
  if (variant === "normal" && realEarth) { res.color = realEarth; }
  earthTexCache.set(variant, res);
  return res;
}

export function makeEarth(R, variant = "normal") {
  const { color, clouds } = earthTextures(variant);
  const g = new THREE.Group();
  const e = new THREE.Mesh(new THREE.SphereGeometry(R, 96, 64), std("#ffffff", { map: color, roughness: 0.9 }));
  const c = new THREE.Mesh(new THREE.SphereGeometry(R * 1.008, 96, 64), new THREE.MeshStandardMaterial({ map: clouds, transparent: true, depthWrite: false, roughness: 1 }));
  const atm = new THREE.Mesh(new THREE.SphereGeometry(R * 1.06, 64, 48), new THREE.ShaderMaterial({
    vertexShader: `varying vec3 vN; varying vec3 vV; void main(){ vN=normalize(normalMatrix*normal); vec4 mv=modelViewMatrix*vec4(position,1.0); vV=normalize(-mv.xyz); gl_Position=projectionMatrix*mv; }`,
    fragmentShader: `varying vec3 vN; varying vec3 vV; void main(){ float f=pow(1.0-abs(dot(vN,vV)),2.5); gl_FragColor=vec4(0.35,0.62,1.0,f*1.1); }`,
    side: THREE.BackSide, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, fog: false,
  }));
  e.material.fog = false; c.material.fog = false;
  if (realEarth && color === realEarth) c.material.opacity = 0.28;  // 真实贴图自带云，程序云层只做淡淡一层
  g.add(e, c, atm);
  g.userData.clouds = c;
  return g;
}


// ------------------------------------------------------- 荒废 / 损毁 ---
const grassMat = std("#5f7d3a", { roughness: 1 });
const bushMat = std("#46652f", { roughness: 1 });
const rubbleMat = std("#8d8a83", { roughness: 1 });
const grassG = new THREE.ConeGeometry(0.35, 0.9, 5);
grassG.translate(0, 0.45, 0);
const bushG = new THREE.IcosahedronGeometry(0.9, 0);
const treeTop = new THREE.IcosahedronGeometry(2.2, 0);
const trunkG = new THREE.CylinderGeometry(0.15, 0.22, 3, 6);
trunkG.translate(0, 1.5, 0);
export function addOvergrowth(g, r, x0, x1, L, n = 40) {
  for (let i = 0; i < n; i++) {
    const k = r();
    let m;
    if (k < 0.6) m = new THREE.Mesh(grassG, grassMat);
    else if (k < 0.9) { m = new THREE.Mesh(bushG, bushMat); m.scale.setScalar(0.6 + r()); }
    else {
      m = new THREE.Group();
      const tr = new THREE.Mesh(trunkG, std("#6b5240"));
      const tp = new THREE.Mesh(treeTop, bushMat); tp.position.y = 3.6;
      tp.castShadow = true; m.add(tr, tp);
    }
    m.position.set(x0 + r() * (x1 - x0), 0.05, -r() * L);
    m.rotation.y = r() * 6;
    m.userData = { tag: "green", rank: r() };
    g.add(m);
  }
}
export function addDebris(g, r, x0, x1, L, n = 14) {
  for (let i = 0; i < n; i++) {
    const s = 0.4 + r() * 1.6;
    const m = new THREE.Mesh(new THREE.BoxGeometry(s * (1 + r()), s * 0.5, s), rubbleMat);
    m.position.set(x0 + r() * (x1 - x0), s * 0.2, -r() * L);
    m.rotation.set(r() * 0.6, r() * 6, r() * 0.6);
    m.castShadow = true;
    m.userData = { tag: "debris", rank: r() };
    g.add(m);
  }
}

