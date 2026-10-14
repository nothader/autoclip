// 入口：加载 plan.json，暴露 window.WHATIF.frame(i)（帧号的纯函数，可乱序、多进程渲染）。
import * as THREE from "three";
import { World } from "./world.js";
import { Prop, Effects } from "./actors.js";
import { Person, makeCrowd, updateCrowd } from "./people.js";
import { drawOverlay, layout } from "./overlay.js";

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
  establishing:{ pos: [14, 13, 34],      look: [0, 7, -40],    fov: 44 },
  pov:         { pos: [0.4, 1.65, 3],    look: [0, 1.5, -10],  fov: 55 },
  top_down:    { pos: [0, 46, 2],        look: [0, 0, -2],     fov: 45 },
  dolly:       { pos: [1.5, 1.9, 9],     look: [0, 1.3, -6],   fov: 48 },
};

function placeCamera(name, p, S, fr, beat, env) {
  const lt = fr.lt || 0;
  const fx = beat ? beat.effects : [];
  if (env && env.globe) {
    const dist = { closeup: 36, front: 48, wide: 62, far: 84, establishing: 72, aerial: 54 }[name] ?? 50;
    const a = name === "orbit" ? lt * 0.25 : 0.05 * lt;
    camera.position.set(Math.sin(a) * dist, dist * 0.08, Math.cos(a) * dist * (1 - 0.03 * lt));
    camera.lookAt(0, 0, 0);
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
  else if (name === "establishing") off.multiplyScalar(1 - 0.12 * Math.min(1, lt / dur));
  else off.multiplyScalar(1 - 0.06 * Math.min(1, lt / dur));
  camera.position.copy(p).add(off);
  const look = new THREE.Vector3(...c.look).multiplyScalar(S).add(p);
  if (name === "dolly" || name === "pov") look.z -= Math.min(lt, dur) * S;
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
  if (fx.includes("earthquake")) camera.rotation.z += noise1(fr.t, 9) * 0.02;
  camera.fov = c.fov;
  camera.near = 0.05 * S;
  camera.far = 20000 * Math.max(1, S);
  camera.updateProjectionMatrix();
}

let plan = null;

async function load() {
  plan = await (await fetch("plan.json")).json();
  layout(W, plan);
  await document.fonts.ready;
  // 预热字体：让 Source Serif 在第一帧前就可用
  await Promise.all([document.fonts.load("italic 44px WSerif"), document.fonts.load("500 46px WSerif"), document.fonts.load("500 40px Inter")]);
  window.WHATIF_READY = true;
}

function frame(i) {
  const fr = plan.frames[Math.min(i, plan.frames.length - 1)];
  const beat = fr.b !== undefined ? plan.beats[fr.b] : null;
  const sceneName = fr.scene || "void";
  const env = world.use(sceneName, beat ? beat.env : {});

  const S = fr.scale || 1;
  const p = new THREE.Vector3(0, 0, env.static ? 0 : -(fr.z || 0));
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

  if (beat) placeCamera(beat.camera, p, S, fr, beat, env);
  else { camera.position.set(0, 0, 10); camera.lookAt(0, 0, 0); }
  world.update(fr, p, S, beat, camera.position);
  renderer.toneMappingExposure = world.exposure || 1.0;
  effects.update(currentSubject, currentSubject ? currentSubject.meshes : null, fr, beat, camera);
  canvas.style.filter = beat && beat.effects.includes("freeze") ? "saturate(0.45) brightness(1.08) hue-rotate(-12deg)" : "none";
  renderer.render(scene, camera);
  drawOverlay(fr, plan);
  return true;
}

window.WHATIF = { frame, get plan() { return plan; } };
load().catch((e) => { window.WHATIF_ERROR = String(e && e.stack || e); });
