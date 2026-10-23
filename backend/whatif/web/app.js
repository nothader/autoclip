// 入口：加载 plan.json，暴露 window.WHATIF.frame(i)（帧号的纯函数，可乱序、多进程渲染）。
import * as THREE from "three";
import { World } from "./world.js";
import { Prop, Effects } from "./actors.js";
import { Person, makeCrowd, updateCrowd } from "./people.js";
import { drawOverlay, layout } from "./overlay.js";
import { setEarthImage } from "./common.js";
import { Satisfying } from "./satisfying.js";
import { CineFX } from "./fx.js";

const qs = new URLSearchParams(location.search);
const W = +(qs.get("w") || 1080), H = +(qs.get("h") || 1920);

const canvas = document.getElementById("gl");
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, preserveDrawingBuffer: true, powerPreference: "high-performance" });
renderer.setPixelRatio(1);
renderer.setSize(W, H, false);
canvas.style.width = W + "px";
canvas.style.height = H + "px";
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.0;

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(50, W / H, 0.1, 20000);
const world = new World(scene);
const effects = new Effects(scene);
const cinefx = new CineFX(scene);
const lastLook = new THREE.Vector3();

// ---------- 电影感运镜：在基础机位上叠加本段的 move（按本段进度 u 缓动） ----------
const easeIO = (u) => u * u * (3 - 2 * u);
const easeOut = (u) => 1 - (1 - u) ** 3;
function applyMove(move, u, mk, off, look, camPos) {
  const R = off.length() || 1;
  const e = easeIO(u), eo = easeOut(u);
  let roll = 0, yaw = 0;
  const rotY = (v, a) => v.applyAxisAngle(new THREE.Vector3(0, 1, 0), a);
  switch (move) {
    case "swoop_in": {   // 从高远处俯冲进来
      const start = off.clone().multiplyScalar(1 + 1.6 * mk).add(new THREE.Vector3(0, R * 0.9 * mk, 0));
      off.lerpVectors(start, off.clone(), eo); roll = (1 - eo) * 0.1 * mk; break;
    }
    case "swoop_out": {
      const end = off.clone().multiplyScalar(1 + 0.8 * mk).add(new THREE.Vector3(0, R * 0.45 * mk, 0));   // 拉远但主体仍在画面里
      off.lerpVectors(off.clone().multiplyScalar(0.85), end, e); roll = -e * 0.06 * mk; break;
    }
    case "crane_up": off.y += R * mk * (-0.35 + 0.9 * e); break;
    case "crane_down": off.y += R * mk * (0.5 - 0.65 * e); break;
    case "arc_left": rotY(off, (-0.6 + 1.2 * e) * mk); break;
    case "arc_right": rotY(off, (0.6 - 1.2 * e) * mk); break;
    case "push_in": off.multiplyScalar(1 + mk * (0.3 - 0.6 * e)); break;
    case "pull_out": off.multiplyScalar(1 + mk * (-0.3 + 0.7 * e)); break;
    case "whip": yaw = (1 - Math.min(1, u / 0.22)) ** 2 * 1.1 * mk; off.multiplyScalar(1 - 0.15 * e * mk); break;
    case "dutch": roll = (-0.5 + e) * 0.3 * mk; off.multiplyScalar(1 - 0.12 * e); break;
    case "drone_rise": off.y += R * mk * 1.1 * e; off.multiplyScalar(1 + 0.35 * e * mk); look.y += R * 0.12 * e; break;
    case "fly_by": {
      const side = new THREE.Vector3(off.z, 0, -off.x).normalize();
      off.multiplyScalar(0.8).addScaledVector(side, R * mk * (1.1 - 2.2 * e)); roll = (0.5 - e) * 0.12 * mk; break;
    }
    case "spiral": rotY(off, 1.5 * mk * e - 0.4 * mk); off.multiplyScalar(1.3 - 0.5 * e); off.y += R * 0.3 * (1 - e); roll = (1 - e) * 0.08; break;
    default: break;
  }
  return { roll, yaw };
}

const subjects = new Map();
let currentSubject = null;
let currentKey = null;

function getSubject(spec) {
  const human = spec.type === "runner" || spec.type === "person";
  const key = human ? `person|${spec.outfit}|${spec.color}` : `${spec.type}|${spec.color}`;
  if (!subjects.has(key)) {
    const s = human ? new Person(spec.type === "runner" ? "hoodie" : spec.outfit, spec.color, 1) : new Prop(spec.type, spec.color);
    s.meshes = [];
    s.root.traverse((o) => { if (o.isMesh && !(o.material && o.material.blending === THREE.AdditiveBlending)) s.meshes.push(o); });
    subjects.set(key, s);
  }
  return [key, subjects.get(key)];
}

// 每段的人群：按段号缓存
const crowds = new Map();
let activeCrowds = null;
function crowdsFor(beat) {
  if (!crowds.has(beat.i)) {
    const g = new THREE.Group();
    beat.cast.forEach((c, k) => g.add(makeCrowd(c, beat.i * 17 + k + 1)));
    crowds.set(beat.i, g);
  }
  return crowds.get(beat.i);
}

function noise1(t, seed) {
  return Math.sin(t * 13.1 + seed) * 0.5 + Math.sin(t * 7.3 + seed * 2.1) * 0.3 + Math.sin(t * 23.7 + seed * 0.7) * 0.2;
}

const CAMS = {
  //            position offset (×scale)      look-at offset          fov
  follow:      { pos: [0.9, 2.1, 6.2],   look: [0, 1.2, -4],   fov: 50 },
  front:       { pos: [0.3, 1.7, -5.6],  look: [0, 1.15, 0],   fov: 45 },
  closeup:     { pos: [0.45, 1.65, -2.4], look: [0, 1.35, 0],  fov: 38 },
  low_front:   { pos: [1.1, 0.45, -4.4], look: [0, 1.15, 0],   fov: 52 },
  side:        { pos: [6.4, 1.45, -0.8], look: [0, 1.0, -0.8], fov: 48 },
  wide:        { pos: [6.5, 8.5, 13],    look: [0, 1.0, -8],   fov: 46 },
  aerial:      { pos: [0, 26, 14],       look: [0, 0, -14],    fov: 48 },
  far:         { pos: [3, 9, 42],        look: [0, 1.5, 0],    fov: 34 },
  orbit:       { pos: [0, 2.2, 6.5],     look: [0, 1.1, 0],    fov: 46 },
  establishing:{ pos: [3, 13, 34],       look: [0, 7, -40],    fov: 44 },
  pov:         { pos: [0.4, 1.65, 3],    look: [0, 1.5, -10],  fov: 55 },
  top_down:    { pos: [0, 46, 2],        look: [0, 0, -2],     fov: 45 },
  dolly:       { pos: [1.5, 1.9, 9],     look: [0, 1.3, -6],   fov: 48 },
  witness:     { pos: [0, 21, 26],       look: [0, 5, -80],    fov: 52 },   // 固定视角：高处阳台俯看整座城
};

function placeCamera(name, p, S, fr, beat, env) {
  const lt = fr.lt || 0;
  const fx = beat ? beat.effects : [];
  if (env && env.globe) {
    let dist = { closeup: 36, front: 48, wide: 62, far: 84, establishing: 72, aerial: 54 }[name] ?? 50;
    let a = name === "orbit" ? lt * 0.25 : 0.05 * lt, elev = 0.08;
    const u = Math.min(1, fr.frac || 0), mk = beat && beat.mk || 0.7, mv = beat && beat.move;
    if (mv === "swoop_in" || mv === "push_in") dist *= 1 + (mv === "swoop_in" ? 1.4 : 0.35) * mk * (1 - easeOut(u));
    if (mv === "swoop_out" || mv === "pull_out") dist *= 1 + 0.8 * mk * easeIO(u);
    if (mv === "arc_left" || mv === "arc_right" || mv === "spiral") a += (mv === "arc_right" ? -1 : 1) * (easeIO(u) - 0.5) * 0.9 * mk;
    if (mv === "swoop_in") elev += 0.5 * mk * (1 - easeOut(u));
    camera.position.set(Math.sin(a) * dist, dist * elev, Math.cos(a) * dist * (1 - 0.03 * lt));
    camera.lookAt(0, 0, 0);
    lastLook.set(0, 0, 0);
    camera.fov = 40; camera.near = 0.1; camera.far = 20000;
    camera.updateProjectionMatrix();
    return;
  }
  const c = CAMS[name] || CAMS.follow;
  let off = new THREE.Vector3(...c.pos).multiplyScalar(S);
  if (name === "orbit") {
    const a = lt * 0.35;
    off = new THREE.Vector3(Math.sin(a) * 6.5, 2.2, Math.cos(a) * 6.5).multiplyScalar(S);
  }
  const dur = Math.max(1, beat ? beat.duration : 4);
  // 缓慢推拉，避免画面死板
  if (name === "dolly" || name === "pov") off.z -= Math.min(lt, dur) * (name === "pov" ? 1.3 : 1.0) * S;
  else if (name === "witness") { off.x += Math.sin(lt * 0.45) * 0.08 * S; off.y += Math.sin(lt * 0.31 + 1) * 0.05 * S; }
  else if (name === "establishing") off.multiplyScalar(1 - 0.12 * Math.min(1, lt / dur));
  else off.multiplyScalar(1 - 0.06 * Math.min(1, lt / dur));
  const look = new THREE.Vector3(...c.look).multiplyScalar(S).add(p);
  if (name === "dolly" || name === "pov") look.z -= Math.min(lt, dur) * S;
  const mv = beat && beat.move && beat.move !== "none" ? applyMove(beat.move, Math.min(1, fr.frac || 0), beat.mk || 0.7, off, look) : { roll: 0, yaw: 0 };
  camera.position.copy(p).add(off);
  if (mv.yaw) look.sub(camera.position).applyAxisAngle(new THREE.Vector3(0, 1, 0), mv.yaw).add(camera.position);
  if (fx.includes("shake") || fx.includes("earthquake")) {
    const amp = (fx.includes("earthquake") ? 0.16 : 0.04) * S * (1 + 2 * (fr.intensity || 0));
    camera.position.x += noise1(fr.t, 1) * amp;
    camera.position.y += noise1(fr.t, 2) * amp;
    look.x += noise1(fr.t, 5) * amp * 0.5;
  }
  if (env && env.bounds) {  // 室内：镜头留在房间里
    const b = env.bounds;
    camera.position.x = Math.max(-b.x, Math.min(b.x, camera.position.x));
    camera.position.y = Math.max(b.y0, Math.min(b.y1, camera.position.y));
    camera.position.z = Math.max(b.z0, Math.min(b.z1, camera.position.z));
  }
  camera.lookAt(look);
  lastLook.copy(look);
  if (mv.roll) camera.rotateZ(mv.roll);
  if (fx.includes("earthquake")) camera.rotation.z += noise1(fr.t, 9) * 0.02;
  camera.fov = c.fov;
  camera.near = 0.05 * S;
  camera.far = 20000 * Math.max(1, S);
  camera.updateProjectionMatrix();
}

let plan = null;
let STYLE = "calm";
let satisfying = null;
let anchor = null;

// ---------- 前景锚点：镜头下方的小桌 + 咖啡杯 / 饮料，随天气变化 ----------
function buildAnchor(kind) {
  const g = new THREE.Group();
  const m = (c, o = {}) => new THREE.MeshStandardMaterial({ color: c, roughness: 0.55, ...o });
  const ledge = new THREE.Mesh(new THREE.BoxGeometry(4.2, 0.08, 3.2), m("#d9d2c5", { roughness: 0.9 }));
  ledge.position.set(0, -0.04, 1.25);   // 向镜头方向延伸，铺满画面底部
  g.add(ledge);
  const parts = { ledge, ledgeBase: ledge.material.color.clone() };
  if (kind === "drink") {
    const glass = new THREE.Mesh(new THREE.CylinderGeometry(0.075, 0.065, 0.2, 28, 1, true), m("#e7f5ff", { transparent: true, opacity: 0.35, roughness: 0.05 }));
    glass.position.y = 0.1; g.add(glass);
    const liquid = new THREE.Mesh(new THREE.CylinderGeometry(0.068, 0.06, 0.14, 24), m("#f08c00", { transparent: true, opacity: 0.75, roughness: 0.1 }));
    liquid.position.y = 0.075; g.add(liquid); parts.top = liquid;
  } else {
    const saucer = new THREE.Mesh(new THREE.CylinderGeometry(0.16, 0.13, 0.015, 36), m("#f8f9fa", { roughness: 0.25 }));
    saucer.position.y = 0.008; g.add(saucer);
    const cup = new THREE.Mesh(new THREE.CylinderGeometry(0.075, 0.06, 0.085, 32), m("#f8f9fa", { roughness: 0.25 }));
    cup.position.y = 0.058; g.add(cup);
    const handle = new THREE.Mesh(new THREE.TorusGeometry(0.03, 0.009, 8, 16, Math.PI * 1.3), m("#f8f9fa", { roughness: 0.25 }));
    handle.position.set(0.085, 0.06, 0); handle.rotation.z = -Math.PI / 2 + 0.3; g.add(handle);
    const coffee = new THREE.Mesh(new THREE.CircleGeometry(0.068, 28), m("#3b2314", { roughness: 0.2 }));
    coffee.rotation.x = -Math.PI / 2; coffee.position.y = 0.098; g.add(coffee); parts.top = coffee;
    const spoon = new THREE.Mesh(new THREE.BoxGeometry(0.11, 0.005, 0.014), m("#adb5bd", { metalness: 0.8, roughness: 0.2 }));
    spoon.position.set(-0.03, 0.018, 0.1); spoon.rotation.y = 0.5; g.add(spoon);
  }
  // 热气（3 团柔光）、霜 / 雪盖、灰堆
  parts.steam = [0, 1, 2].map(() => { const sp = new THREE.Sprite(new THREE.SpriteMaterial({ color: "#ffffff", transparent: true, opacity: 0, depthWrite: false })); sp.scale.setScalar(0.08); g.add(sp); return sp; });
  parts.cap = new THREE.Mesh(new THREE.SphereGeometry(0.1, 20, 10, 0, Math.PI * 2, 0, Math.PI / 2), m("#ffffff", { roughness: 0.95 }));
  parts.cap.position.y = 0.1; parts.cap.scale.set(1, 0.001, 1); g.add(parts.cap);
  parts.heap = new THREE.Mesh(new THREE.ConeGeometry(1.2, 0.25, 24), m("#6b6560", { roughness: 1 }));
  parts.heap.position.set(0, 0.006, 0.1); parts.heap.scale.set(1, 0.001, 0.4); g.add(parts.heap);
  g.traverse((o) => { if (o.isMesh) { o.castShadow = false; o.receiveShadow = false; } });
  g.userData.parts = parts;
  return g;
}
function updateAnchor(fr, beat) {
  const kind = (plan.theme && plan.theme.anchor) || "none";
  if (kind === "none" || !beat) { if (anchor) anchor.visible = false; return; }
  if (!anchor) { anchor = buildAnchor(kind); camera.add(anchor); if (!camera.parent) scene.add(camera); }
  anchor.visible = true;
  // 放在镜头前下方（镜头坐标系），竖屏 / 横屏各自取景
  const land = W > H;
  anchor.position.set(land ? 0.95 : 0.24, land ? -0.78 : -0.86, land ? -2.0 : -2.2);
  anchor.rotation.set(0.06, -0.25, 0);
  const env = beat.env || {}, w = env.weather || "clear";
  const idx = beat.i ?? 0;
  const count = (pred) => plan.beats.slice(0, idx).filter(pred).length + (pred(beat) ? (fr.frac || 0) : 0);
  const cold = (b) => (b.env && (b.env.weather === "snow" || (b.env.globe && b.env.globe.frozen)));
  const ash = (b) => (b.env && b.env.weather === "ash");
  const p = anchor.userData.parts;
  const snowK = Math.min(1, count(cold) / 3), ashK = Math.min(1, count(ash) / 4);
  p.cap.scale.set(1, 0.001 + 0.45 * Math.max(snowK, ashK), 1);
  p.cap.material.color.set(ashK > snowK ? "#7a736c" : "#f8fbff");
  p.heap.visible = ashK > 0.01;   // 压扁的灰堆会和台面 z-fighting，没灰时直接隐藏
  p.heap.scale.set(1, 0.001 + ashK * 0.9, 0.4);
  p.ledge.material.color.copy(p.ledgeBase).lerp(new THREE.Color(ashK > snowK ? "#7a736c" : "#f4f7fb"), Math.max(snowK, ashK) * 0.9);
  const hot = w !== "snow" && !cold(beat) && ashK < 0.3;
  p.steam.forEach((sp, j) => {
    const ph = ((fr.t || 0) * 0.35 + j / 3) % 1;
    sp.position.set(Math.sin(ph * 6 + j) * 0.02, 0.12 + ph * 0.28, 0);
    sp.material.opacity = hot ? 0.18 * Math.sin(ph * Math.PI) : 0;
    sp.scale.setScalar(0.05 + ph * 0.12);
  });
  // 风暴 / 地震：杯子跟着抖
  const fx = beat.effects || [];
  const shake = (w === "storm" ? 0.012 : 0) + (fx.includes("earthquake") || fx.includes("shake") ? 0.02 : 0);
  anchor.rotation.z = shake ? Math.sin((fr.t || 0) * 37) * shake : 0;
}

// ---------- 风格：调色 / 推镜 / 卡通 / 像素 ----------
const GRADE = {
  calm: "", witness: "saturate(1.08) contrast(1.04)", bold: "saturate(1.32) contrast(1.08)", cinematic: "contrast(1.14) saturate(0.82) sepia(0.14) brightness(0.96)",
  toon: "saturate(1.5) brightness(1.06)", retro: "saturate(1.4) contrast(1.18)",
};
const TOON_GRAD = (() => {
  const t = new THREE.DataTexture(new Uint8Array([70, 70, 70, 255, 160, 160, 160, 255, 255, 255, 255, 255]), 3, 1, THREE.RGBAFormat);
  t.minFilter = t.magFilter = THREE.NearestFilter; t.needsUpdate = true; return t;
})();
const OUTLINE = new THREE.MeshBasicMaterial({ color: 0x15151a, side: THREE.BackSide });
OUTLINE.onBeforeCompile = (sh) => {
  sh.vertexShader = sh.vertexShader.replace("#include <begin_vertex>", "#include <begin_vertex>\n  transformed += normalize(normal) * 0.035;");
};
const toonCache = new Map();
function toonMat(m) {
  // 天空球 / 地球等自定义着色器不能换成卡通材质（换了会丢 uniforms：天空变暗，切到城市场景时报错）
  if (!m || m.isShaderMaterial || m.isMeshToonMaterial || m.isMeshBasicMaterial || m.isPointsMaterial || m.isSpriteMaterial || m.transparent) return m;
  const key = m.uuid;
  if (!toonCache.has(key)) toonCache.set(key, new THREE.MeshToonMaterial({ color: m.color ? m.color.clone() : 0xffffff, map: m.map || null, gradientMap: TOON_GRAD }));
  return toonCache.get(key);
}
function toonify(root) {   // 卡通：平涂三阶光照 + 反向外壳描边（每个网格只处理一次）
  const todo = [];
  root.traverse((o) => { if (o.isMesh && !o.userData.toon && !o.userData.outline && !(o.material && o.material.isShaderMaterial)) todo.push(o); });
  for (const o of todo) {
    o.userData.toon = true;
    const solid = !(o.material && o.material.transparent) && !(o.material && o.material.blending === THREE.AdditiveBlending);
    o.material = Array.isArray(o.material) ? o.material.map(toonMat) : toonMat(o.material);
    if (solid && o.geometry && o.geometry.attributes.normal && !o.isInstancedMesh) {
      const ol = new THREE.Mesh(o.geometry, OUTLINE);
      ol.userData.outline = true; ol.castShadow = false; ol.receiveShadow = false;
      o.add(ol);
    }
  }
}
function styleCamera(fr, beat) {
  const lt = fr.lt || 0;
  let k = 1;
  if (STYLE === "bold" || STYLE === "retro") k = 1 + 0.16 * Math.max(0, 1 - lt / 0.35) ** 2;    // 每次切镜的推镜冲击
  else if (STYLE === "cinematic") k = 1 + 0.07 * Math.min(1, (fr.frac || 0));                  // 缓慢推近
  if (k !== 1) { camera.fov = camera.fov / k; camera.updateProjectionMatrix(); }
}

async function load() {
  plan = await (await fetch("plan.json")).json();
  layout(W, plan);
  STYLE = (plan.theme && plan.theme.style) || "calm";
  if (STYLE === "retro") {   // 8-bit：低分辨率渲染，CSS 最近邻放大
    renderer.setSize(Math.max(64, Math.round(W / 5)), Math.max(64, Math.round(H / 5)), false);
    canvas.style.width = W + "px"; canvas.style.height = H + "px";
    canvas.style.imageRendering = "pixelated";
    renderer.shadowMap.type = THREE.BasicShadowMap;
  }
  if (STYLE === "toon") renderer.toneMapping = THREE.NoToneMapping;
  try {
    const tex = await new THREE.TextureLoader().loadAsync("textures/earth.jpg");
    tex.colorSpace = THREE.SRGBColorSpace;
    tex.anisotropy = 4;
    setEarthImage(tex);
  } catch (e) { /* 没有贴图时退回程序生成的地球 */ }
  await document.fonts.ready;
  // 预热字体：让 Source Serif 在第一帧前就可用
  await Promise.all([document.fonts.load("italic 44px WSerif"), document.fonts.load("500 46px WSerif"), document.fonts.load("500 40px Inter")]);
  window.WHATIF_READY = true;
}

function frame(i) {
  const raw = plan.frames[Math.min(i, plan.frames.length - 1)];
  const P = plan.pace || 1;   // 节奏倍数：画面里的动作（自转、走路、抖动…）同步加快
  const fr = P === 1 ? raw : { ...raw, t: (raw.t || 0) * P, lt: (raw.lt || 0) * P, ph: (raw.ph || 0) * P };
  const beat = fr.b !== undefined ? plan.beats[fr.b] : null;
  const sceneName = fr.scene || "void";
  const env = world.use(sceneName, beat ? beat.env : {});

  let S = fr.scale || 1;
  const p = new THREE.Vector3(0, 0, env.static ? 0 : -(fr.z || 0));
  // 自定义布景：镜头围绕 set.focus，距离乘 set.zoom
  const camPivot = env.custom ? new THREE.Vector3(...env.focus).add(new THREE.Vector3(0, -1.1 * env.zoom, 0)) : p;
  const camScale = env.custom ? env.zoom : S;
  if (beat && beat.subject && beat.subject.type !== "none" && !env.globe && sceneName !== "map") {
    const [key, subj] = getSubject(beat.subject);
    if (key !== currentKey) {
      if (currentSubject) scene.remove(currentSubject.root);
      scene.add(subj.root);
      currentSubject = subj; currentKey = key;
      effects.plasma.clear();
    }
    subj.root.position.copy(p);
    subj.root.scale.setScalar(S);
    subj.pose(beat.subject.action, fr.ph || 0, fr.t, fr.z || 0);
    // 消失效果：主体在本段中途消失
    subj.root.visible = !(beat.effects.includes("vanish") && (fr.frac || 0) > 0.45);
    subj.root.updateMatrixWorld(true);
  } else if (currentSubject) {
    scene.remove(currentSubject.root);
    currentSubject = null; currentKey = null;
    effects.plasma.clear();
  }

  // 人群
  const cg = beat && beat.cast && beat.cast.length && !env.globe ? crowdsFor(beat) : null;
  if (cg !== activeCrowds) {
    if (activeCrowds) scene.remove(activeCrowds);
    if (cg) scene.add(cg);
    activeCrowds = cg;
  }
  if (cg) {
    cg.position.copy(p);
    const vanish = beat.effects.includes("vanish") ? Math.min(1, (fr.frac || 0) * 1.25) : 0;
    for (const g of cg.children) updateCrowd(g, fr.lt || 0, vanish);
  }

  if (beat) { placeCamera(beat.camera, camPivot, camScale, fr, beat, env); styleCamera(raw, beat); updateAnchor(raw, beat); }
  else { camera.position.set(0, 0, 10); camera.lookAt(0, 0, 0); }
  world.update(fr, p, S, beat, camera.position);
  renderer.toneMappingExposure = world.exposure || 1.0;
  effects.update(currentSubject, currentSubject ? currentSubject.meshes : null, fr, beat, camera);
  // 特效中心：自定义布景用 focus（主体所在处），其它场景用镜头注视点
  const fxCenter = env.custom ? new THREE.Vector3(...env.focus) : lastLook;
  const fxFlash = env.globe ? 0 : cinefx.update(fr, beat, fxCenter, env.custom ? camScale : Math.max(1, S), camera);
  const glow = document.getElementById("glow");
  if (glow) glow.style.opacity = beat && beat.effects.includes("bloom") ? (0.55 + 0.15 * Math.sin((raw.t || 0) * 1.3)).toFixed(3) : "0";
  if (STYLE === "toon") toonify(scene);
  const grade = GRADE[STYLE] || "";
  canvas.style.filter = [beat && beat.effects.includes("freeze") ? "saturate(0.45) brightness(1.08) hue-rotate(-12deg)" : "", grade,
    (plan.theme && plan.theme.palette_css) || "", post(raw, beat, fxFlash)].filter(Boolean).join(" ") || "none";
  canvas.style.transform = postTransform(raw, beat);
  const split = plan.theme && plan.theme.layout === "split" && H > W;
  if (split) {
    // 分屏：上半故事、下半解压循环（各自一个视口）
    const sz = renderer.getSize(new THREE.Vector2()), w = sz.x, h = sz.y, hh = Math.round(h / 2);
    camera.aspect = w / hh; camera.updateProjectionMatrix();
    renderer.setScissorTest(true);
    renderer.setViewport(0, h - hh, w, hh); renderer.setScissor(0, h - hh, w, hh);
    renderer.render(scene, camera);
    satisfying ??= new Satisfying();
    satisfying.update(raw.t || 0, w / (h - hh), (plan.theme && plan.theme.accent) || "#ffffff");
    if (STYLE === "toon") toonify(satisfying.scene);
    renderer.setViewport(0, 0, w, h - hh); renderer.setScissor(0, 0, w, h - hh);
    renderer.render(satisfying.scene, satisfying.camera);
    renderer.setScissorTest(false);
  } else {
    if (camera.aspect !== W / H) { camera.aspect = W / H; camera.updateProjectionMatrix(); }
    renderer.render(scene, camera);
  }
  drawOverlay(raw, plan);
  return true;
}

// ---------- 画面后期：转场（甩镜 / 冲推 / 故障）、辉光、闪光 ----------
function glitchCss(seed, amt) {   // RGB 通道错位（SVG 滤镜 #rgbs，偏移量每帧改）+ 色相跳动
  const r = (k) => { const x = Math.sin(seed * 12.9898 + k * 78.233) * 43758.5453; return x - Math.floor(x); };
  const d = Math.round((10 + 30 * amt) * W / 1080);
  const ro = document.getElementById("rgbs-r"), go = document.getElementById("rgbs-gb");
  if (ro && go) { ro.setAttribute("dx", d); ro.setAttribute("dy", Math.round((r(2) - 0.5) * 6)); go.setAttribute("dx", -d); }
  return `url(#rgbs) hue-rotate(${Math.round((r(1) - 0.5) * 70 * amt)}deg) contrast(${(1 + 0.2 * amt).toFixed(2)})`;
}
function glitchOn(fr, beat) {
  if (fr.tr && fr.tr.k === "glitch") return 1 - (fr.tr.out ? 1 - fr.tr.p : fr.tr.p);
  if (beat && beat.effects.includes("glitch")) { const ph = ((fr.lt || 0) * 2.2) % 1; return ph < 0.14 ? 1 - ph / 0.14 : 0; }
  return 0;
}
function post(fr, beat, fxFlash) {
  const out = [];
  const tr = fr.tr;
  if (tr && (tr.k === "whip" || tr.k === "zoom")) {
    const s = tr.out ? tr.p ** 2 : (1 - tr.p) ** 2;
    out.push(`blur(${(s * (tr.k === "whip" ? 26 : 14)).toFixed(1)}px)`);
  }
  const g = glitchOn(fr, beat);
  if (g > 0) out.push(glitchCss(fr.f ?? Math.round((fr.t || 0) * 30), g));
  if (beat && beat.effects.includes("bloom")) out.push("brightness(1.1) saturate(1.25) contrast(1.05)");
  const li = Math.max(fxFlash || 0, fr.lightning ? fr.lightning * 0.6 : 0);
  if (li > 0.01) out.push(`brightness(${(1 + li).toFixed(2)})`);
  return out.join(" ");
}
function postTransform(fr, beat) {
  const tr = fr.tr;
  if (!tr) return "";
  const dir = beat && beat.i % 2 ? -1 : 1;
  if (tr.k === "whip") {
    const s = tr.out ? -(tr.p ** 2) : (1 - tr.p) ** 2;
    return `translateX(${(dir * s * 38).toFixed(2)}%) scale(${(1 + 0.12 * Math.abs(s)).toFixed(3)})`;
  }
  if (tr.k === "zoom") return `scale(${(1 + 0.4 * (tr.out ? tr.p ** 2 : (1 - tr.p) ** 2)).toFixed(3)})`;
  if (tr.k === "flash") return `scale(${(1 + 0.06 * (1 - tr.p)).toFixed(3)})`;
  if (tr.k === "glitch") { const g = glitchOn(fr, beat); return `translateX(${((Math.sin((fr.t || 0) * 97) > 0 ? 1 : -1) * g * 2.5).toFixed(2)}%)`; }
  return "";
}

window.WHATIF = { frame, get plan() { return plan; } };
load().catch((e) => { window.WHATIF_ERROR = String(e && e.stack || e); });
