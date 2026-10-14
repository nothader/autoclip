// 入口：加载 plan.json，暴露 window.WHATIF.frame(i)（帧号的纯函数，可乱序、多进程渲染）。
import * as THREE from "./vendor/three.module.min.js";
import { World } from "./world.js";
import { Runner, Prop, Effects } from "./actors.js";
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
layout(W);

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(50, W / H, 0.1, 20000);
const world = new World(scene);
const effects = new Effects(scene);

const subjects = new Map();
let currentSubject = null;
let currentKey = null;

function getSubject(spec) {
  const key = `${spec.type}|${spec.color}`;
  if (!subjects.has(key)) {
    const s = spec.type === "runner" ? new Runner(spec.color) : new Prop(spec.type, spec.color);
    s.meshes = [];
    s.root.traverse((o) => { if (o.isMesh && !(o.material && o.material.blending === THREE.AdditiveBlending)) s.meshes.push(o); });
    subjects.set(key, s);
  }
  return [key, subjects.get(key)];
}

function noise1(t, seed) {
  return Math.sin(t * 13.1 + seed) * 0.5 + Math.sin(t * 7.3 + seed * 2.1) * 0.3 + Math.sin(t * 23.7 + seed * 0.7) * 0.2;
}

const CAMS = {
  //            position offset (×scale)      look-at offset          fov
  follow:    { pos: [0.9, 2.1, 6.2],  look: [0, 1.2, -4],   fov: 50 },
  front:     { pos: [0.3, 1.7, -5.6], look: [0, 1.15, 0],   fov: 45 },
  closeup:   { pos: [0.45, 1.65, -2.4], look: [0, 1.35, 0], fov: 38 },
  low_front: { pos: [1.1, 0.45, -4.4], look: [0, 1.15, 0],  fov: 52 },
  side:      { pos: [6.4, 1.45, -0.8], look: [0, 1.0, -0.8], fov: 48 },
  wide:      { pos: [6.5, 8.5, 13],   look: [0, 1.0, -8],   fov: 46 },
  aerial:    { pos: [0, 26, 14],      look: [0, 0, -14],    fov: 48 },
  far:       { pos: [3, 9, 42],       look: [0, 1.5, 0],    fov: 34 },
  orbit:     { pos: [0, 2.2, 6.5],    look: [0, 1.1, 0],    fov: 46 },
};

function placeCamera(name, p, S, fr, beat) {
  const c = CAMS[name] || CAMS.follow;
  const lt = fr.lt || 0;
  let off = new THREE.Vector3(...c.pos).multiplyScalar(S);
  if (name === "orbit") {
    const a = lt * 0.35;
    off = new THREE.Vector3(Math.sin(a) * 6.5, 2.2, Math.cos(a) * 6.5).multiplyScalar(S);
  }
  // 缓慢推拉，避免画面死板
  const drift = 1 - 0.06 * Math.min(1, lt / Math.max(1, beat ? beat.duration : 4));
  off.multiplyScalar(drift);
  camera.position.copy(p).add(off);
  const look = new THREE.Vector3(...c.look).multiplyScalar(S).add(p);
  const fx = beat ? beat.effects : [];
  if (fx.includes("shake")) {
    const amp = 0.04 * S * (1 + 2 * (fr.intensity || 0));
    camera.position.x += noise1(fr.t, 1) * amp;
    camera.position.y += noise1(fr.t, 2) * amp;
  }
  camera.lookAt(look);
  camera.fov = c.fov;
  camera.near = 0.05 * S;
  camera.far = 20000 * Math.max(1, S);
  camera.updateProjectionMatrix();
}

let plan = null;

async function load() {
  plan = await (await fetch("plan.json")).json();
  await document.fonts.ready;
  // 预热字体：让 Source Serif 在第一帧前就可用
  await Promise.all([document.fonts.load("italic 44px WSerif"), document.fonts.load("500 46px WSerif"), document.fonts.load("500 40px Inter")]);
  window.WHATIF_READY = true;
}

function frame(i) {
  const fr = plan.frames[Math.min(i, plan.frames.length - 1)];
  const beat = fr.b !== undefined ? plan.beats[fr.b] : null;
  const sceneName = fr.scene || "void";
  world.use(sceneName);

  const S = fr.scale || 1;
  const p = new THREE.Vector3(0, 0, -(fr.z || 0));
  if (beat && beat.subject && beat.subject.type !== "none") {
    const [key, subj] = getSubject(beat.subject);
    if (key !== currentKey) {
      if (currentSubject) scene.remove(currentSubject.root);
      scene.add(subj.root);
      currentSubject = subj; currentKey = key;
      effects.plasma.clear();
    }
    subj.root.position.copy(p);
    subj.root.scale.setScalar(S * (beat.subject.type === "runner" ? 1 : 1));
    subj.pose(beat.subject.action, fr.ph || 0, fr.t, fr.z || 0);
    subj.root.updateMatrixWorld(true);
  } else if (currentSubject) {
    scene.remove(currentSubject.root);
    currentSubject = null; currentKey = null;
  }

  world.update(fr, p, S);
  if (beat) {
    effects.update(currentSubject, currentSubject ? currentSubject.meshes : null, fr, beat, camera);
    placeCamera(beat.camera, p, S, fr, beat);
  } else {
    effects.update(null, null, fr, null, camera);
    camera.position.set(0, 0, 10); camera.lookAt(0, 0, 0);
  }
  renderer.render(scene, camera);
  drawOverlay(fr, plan);
  return true;
}

window.WHATIF = { frame, get plan() { return plan; } };
load().catch((e) => { window.WHATIF_ERROR = String(e && e.stack || e); });
