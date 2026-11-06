// Block POV 的方块人：方块身体、画出来的脸（圆点眼、细眉、线条嘴），按 seed 换发型 / 帽子 / 衣服 / 肤色。
import * as THREE from "three";

function rng(seed) {
  let s = (seed >>> 0) || 1;
  return () => { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; };
}
const pick = (r, a) => a[Math.floor(r() * a.length) % a.length];


// ------------------------------------------------------------------ 配色
const PAL = {
  bright: ["#ff6b6b", "#ffa94d", "#ffd43b", "#69db7c", "#4dabf7", "#9775fa", "#f783ac", "#3bc9db"],
  pastel: ["#ffc9c9", "#ffd8a8", "#fff3bf", "#d3f9d8", "#d0ebff", "#e5dbff", "#fcc2d7", "#c5f6fa"],
  earth: ["#8d6e57", "#a47148", "#6b8e3a", "#c2a878", "#7a6a55", "#5c4a3a"],
  metal: ["#adb5bd", "#868e96", "#ced4da", "#495057"],
  wood: ["#8d6e57", "#a0785a", "#6b4f3a", "#c69c6d"],
  skin: ["#f1c27d", "#e0ac69", "#c68642", "#8d5524", "#5c3a21", "#ffdbac", "#d4a373", "#a0522d", "#7b4b2a", "#f5d0b0"],
  hair: ["#2b2420", "#4a3426", "#151210", "#8a6a45", "#b8893f", "#d9c27a", "#6b6b6b", "#e8e6e0", "#a33b2b", "#3b2a6b"],
};

// ------------------------------------------------------------------ 方块人
const HAIR = ["flat", "spiky", "long", "bun", "mohawk", "bald", "afro", "bob", "ponytail", "buzz", "sidepart", "curly", "braids", "pigtails", "fringe"];
const HATS = ["none", "none", "none", "none", "none", "cap", "beanie", "headphones"];   // 普通人的打扮：大多不戴帽子
const OUTFITS = ["hoodie", "tee", "suit", "puffer", "uniform", "lab", "dress", "overalls", "tee", "hoodie"];
const EXPRS = ["neutral", "smile", "shock", "sad", "angry", "smirk"];

// block 风格的脸：画出来的（圆点眼 + 高光、细眉、小鼻子、线条嘴、淡淡腮红），不是像素
function drawnFace(skin, expr, eye, hair) {
  const S = 128, cv = document.createElement("canvas"); cv.width = cv.height = S;
  const x = cv.getContext("2d");
  x.fillStyle = skin; x.fillRect(0, 0, S, S);
  x.fillStyle = hair; x.fillRect(0, 0, S, 10);
  const eyeY = expr === "shock" ? 54 : 58, er = expr === "shock" ? 7 : 5.5;
  for (const ex of [40, 88]) {
    x.fillStyle = eye; x.beginPath(); x.ellipse(ex, eyeY, er, expr === "smile" ? er * 0.55 : er * 1.15, 0, 0, Math.PI * 2); x.fill();
    if (expr !== "smile") { x.fillStyle = "rgba(255,255,255,0.9)"; x.beginPath(); x.arc(ex + 1.8, eyeY - 2, 1.6, 0, Math.PI * 2); x.fill(); }
  }
  x.strokeStyle = hair; x.lineWidth = 3.2; x.lineCap = "round";
  const brow = { neutral: [0, 0], smile: [-1, -1], shock: [-5, -5], sad: [3, -3], angry: [-3, 4], smirk: [0, -3] }[expr] || [0, 0];
  for (const [ex, sd] of [[40, -1], [88, 1]]) {
    x.beginPath(); x.moveTo(ex - 9, 42 + (sd < 0 ? brow[0] : brow[1])); x.lineTo(ex + 9, 42 + (sd < 0 ? brow[1] : brow[0])); x.stroke();
  }
  x.fillStyle = "rgba(0,0,0,0.13)"; x.fillRect(60, 66, 8, 10);                                      // 鼻子
  x.fillStyle = "rgba(255,120,120,0.16)"; for (const cx of [30, 98]) { x.beginPath(); x.ellipse(cx, 78, 9, 5, 0, 0, Math.PI * 2); x.fill(); }
  x.strokeStyle = "#5c2a24"; x.lineWidth = 3;
  x.beginPath();
  if (expr === "smile") { x.arc(64, 82, 14, 0.15 * Math.PI, 0.85 * Math.PI); x.stroke(); }
  else if (expr === "shock") { x.fillStyle = "#4a1f1a"; x.ellipse(64, 92, 7, 9, 0, 0, Math.PI * 2); x.fill(); }
  else if (expr === "sad") { x.arc(64, 102, 12, 1.2 * Math.PI, 1.8 * Math.PI); x.stroke(); }
  else if (expr === "angry") { x.moveTo(52, 94); x.lineTo(76, 92); x.stroke(); }
  else if (expr === "smirk") { x.moveTo(56, 92); x.quadraticCurveTo(70, 94, 78, 86); x.stroke(); }
  else { x.moveTo(55, 92); x.lineTo(73, 92); x.stroke(); }
  const t = new THREE.CanvasTexture(cv);
  t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 4;
  return t;
}

const mBox = (w, h, d, c) => { const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), new THREE.MeshStandardMaterial({ color: c, roughness: 0.8, flatShading: true })); m.castShadow = true; return m; };

export class BlockPerson {
  constructor(seed = 1, look = {}) {
    const r = rng(seed * 2654435761 + 7);
    this.skin = look.skin || pick(r, PAL.skin);
    this.hairC = look.hair || pick(r, PAL.hair);
    this.top = look.top || pick(r, PAL.bright.concat(PAL.earth, ["#212529", "#f8f9fa", "#495057"]));
    this.pants = look.pants || pick(r, ["#2c3440", "#3f5a85", "#5a6070", "#212529", "#7a6a55", "#c2a878", "#e9ecef"]);
    this.hairStyle = look.hairStyle || pick(r, HAIR);
    this.hat = look.hat || pick(r, HATS);
    this.outfit = look.outfit || pick(r, OUTFITS);
    this.eye = pick(r, ["#212529", "#3b2a1e", "#2f4a6b", "#2b5a2b"]);
    this.expr = look.expression && look.expression !== "auto" ? look.expression : null;
    this.root = new THREE.Group();
    this.body = new THREE.Group(); this.root.add(this.body);
    const U = 0.11;                                  // 一个"像素"的尺寸
    const LEG = 8, TOR = 7.2, ARM = 6.4;   // 腿和身子偏长、头稍小（@weirdsecret_ 式比例）
    const shoeC = pick(r, ["#212529", "#f8f9fa", "#e03131", "#8d6e57"]);
    // 腿
    this.legs = [-1, 1].map((sd) => {
      const g = new THREE.Group(); g.position.set(sd * 2 * U, LEG * U, 0); this.body.add(g);
      const leg = mBox(3.6 * U, LEG * U, 3.6 * U, this.outfit === "dress" ? this.skin : this.pants); leg.position.y = -LEG / 2 * U; g.add(leg);
      const sh = mBox(3.8 * U, 1.2 * U, 4.4 * U, shoeC); sh.position.set(0, -(LEG - 0.4) * U, -0.3 * U); g.add(sh);
      return g;
    });
    // 躯干
    this.torso = new THREE.Group(); this.torso.position.y = LEG * U; this.body.add(this.torso);
    const tw = this.outfit === "puffer" ? 9 : 8, td = this.outfit === "puffer" ? 5.2 : 4.4;
    const t = mBox(tw * U, TOR * U, td * U, this.top); t.position.y = TOR / 2 * U; this.torso.add(t);
    const deco = (w, h, d, c, x, y, z) => { const m = mBox(w * U, h * U, d * U, c); m.position.set(x * U, y * U, z * U); this.torso.add(m); };
    if (this.outfit === "hoodie") { deco(0.4, 3, 0.2, "#f8f9fa", -1, 4, -td / 2 - 0.1); deco(0.4, 3, 0.2, "#f8f9fa", 1, 4, -td / 2 - 0.1); deco(5, 1.4, 0.2, this.top, 0, 1.2, -td / 2 - 0.15); }
    if (this.outfit === "puffer") for (const y of [1.5, 3.2, 4.9]) deco(tw + 0.2, 0.3, td + 0.2, "rgba(0,0,0,0)" === "" ? this.top : new THREE.Color(this.top).multiplyScalar(0.85).getStyle(), 0, y, 0);
    if (this.outfit === "suit") { deco(2.4, 6.4, 0.2, "#f8f9fa", 0, 3.2, -td / 2 - 0.1); deco(0.8, 4.5, 0.25, pick(r, ["#c92a2a", "#1c7ed6", "#212529"]), 0, 2.2, -td / 2 - 0.2); }
    if (this.outfit === "dress") deco(tw + 1.6, 3.4, td + 1.4, this.top, 0, -1.6, 0);
    if (this.outfit === "overalls") { deco(tw + 0.1, 3.5, td + 0.1, this.pants, 0, 0, 0); deco(1, 3, 0.2, this.pants, -2.5, 3.5, -td / 2 - 0.1); deco(1, 3, 0.2, this.pants, 2.5, 3.5, -td / 2 - 0.1); }
    if (this.outfit === "jersey") deco(2.4, 2.6, 0.2, "#ffffff", 0, 3, -td / 2 - 0.1);
    if (this.outfit === "lab") deco(tw + 0.4, 6.8, td + 0.3, "#f8f9fa", 0, 2.6, 0);
    if (this.outfit === "uniform") { deco(tw + 0.1, 0.8, td + 0.1, "#212529", 0, 0.4, 0); deco(1.2, 1.2, 0.2, "#fab005", -2, 4.6, -td / 2 - 0.1); }
    if (this.outfit === "stripes") for (const y of [1, 3, 5]) deco(tw + 0.1, 0.8, td + 0.1, "#f8f9fa", 0, y, 0);
    // 手臂（肩部转轴）
    this.arms = [-1, 1].map((sd) => {
      const g = new THREE.Group(); g.position.set(sd * (tw / 2 + 1.6) * U, (TOR - 0.5) * U, 0); this.torso.add(g);
      const arm = mBox(3 * U, ARM * U, 3 * U, this.outfit === "tee" || this.outfit === "jersey" ? this.skin : this.top); arm.position.y = -ARM / 2 * U; g.add(arm);
      const hand = mBox(3 * U, 1.6 * U, 3 * U, this.skin); hand.position.y = -(ARM + 0.8) * U; g.add(hand);
      return g;
    });
    // 头（大头：像参考那样）
    this.head = new THREE.Group(); this.head.position.y = TOR * U; this.torso.add(this.head);
    const H = 7.4;
    const mats = Array.from({ length: 6 }, () => new THREE.MeshStandardMaterial({ color: this.skin, roughness: 0.75, flatShading: true }));
    mats[5].emissive = new THREE.Color("#ffffff"), mats[5].emissiveIntensity = 0.12;   // 脸稍微自发光：逆光时也看得清表情
    this.faceMat = mats[5];                                            // -z 面朝前（与 Person 一致）
    this.headMesh = new THREE.Mesh(new THREE.BoxGeometry(H * U, H * U, H * U), mats);
    this.headMesh.position.y = H / 2 * U; this.headMesh.castShadow = true; this.head.add(this.headMesh);
    this.setExpression(this.expr || "neutral", true);
    const hb = (w, h, d, x, y, z, c = this.hairC) => { const m = mBox(w * U, h * U, d * U, c); m.position.set(x * U, y * U, z * U); this.head.add(m); return m; };
    const hs = this.hat !== "none" && this.hat !== "headphones" && this.hat !== "headband" ? "flat" : this.hairStyle;
    switch (hs) {
      case "bald": break;
      case "buzz": hb(H + 0.2, 0.6, H + 0.2, 0, H, 0); break;
      case "spiky": hb(H + 0.4, 1.4, H + 0.4, 0, H, 0.2); for (let i = -3; i <= 3; i += 2) hb(1.4, 1.6, 1.4, i, H + 1.4, 0); break;
      case "mohawk": hb(1.6, 3.2, H, 0, H, 0); break;
      case "afro": hb(H + 3, 4, H + 3, 0, H - 1.5, 0.5); break;
      case "long": hb(H + 0.6, 1.6, H + 0.6, 0, H, 0.2); hb(H + 0.8, H, 1.6, 0, 0, H / 2 + 0.4); hb(1, H - 2, H, -H / 2 - 0.4, 1, 0.6); hb(1, H - 2, H, H / 2 + 0.4, 1, 0.6); break;
      case "bob": hb(H + 0.6, 1.6, H + 0.6, 0, H, 0); hb(1.2, H / 2 + 1, H, -H / 2 - 0.5, H / 2 - 1, 0.4); hb(1.2, H / 2 + 1, H, H / 2 + 0.5, H / 2 - 1, 0.4); hb(H + 0.6, H / 2 + 1, 1.2, 0, H / 2 - 1, H / 2 + 0.4); break;
      case "bun": hb(H + 0.4, 1.2, H + 0.4, 0, H, 0); hb(3, 3, 3, 0, H + 1.2, 1.5); break;
      case "ponytail": hb(H + 0.4, 1.4, H + 0.4, 0, H, 0); hb(2, 6, 2, 0, 0, H / 2 + 1.2); break;
      case "pigtails": hb(H + 0.4, 1.4, H + 0.4, 0, H, 0); hb(2, 5, 2, -H / 2 - 1, 2, 1); hb(2, 5, 2, H / 2 + 1, 2, 1); break;
      case "braids": hb(H + 0.4, 1.4, H + 0.4, 0, H, 0); for (const sx of [-1, 1]) for (let i = 0; i < 3; i++) hb(1.6, 1.6, 1.6, sx * (H / 2 - 1), 3 - i * 1.8, H / 2 + 0.6); break;
      case "curly": hb(H + 1.6, 2.2, H + 1.6, 0, H - 0.6, 0.3); for (const [x, z] of [[-3, -3], [3, -3], [0, -4]]) hb(2, 1.6, 1.6, x, H + 1, z); break;
      case "sidepart": hb(H + 0.4, 1.4, H + 0.4, 0, H, 0); hb(H / 2, 1, 1, -H / 4, H - 0.8, -H / 2 - 0.3); break;
      case "fringe": hb(H + 0.4, 1.4, H + 0.4, 0, H, 0); hb(H + 0.4, 1.6, 1, 0, H - 1.2, -H / 2 - 0.3); break;
      default: hb(H + 0.4, 1.4, H + 0.4, 0, H, 0.1);
    }
    const hatC = pick(r, ["#e03131", "#1c7ed6", "#212529", "#ffd43b", "#40c057", "#f8f9fa", "#9775fa", "#ff922b"]);
    switch (this.hat) {
      case "beanie": hb(H + 1, 3.6, H + 1, 0, H - 1, 0, hatC); hb(2, 1.2, 2, 0, H + 2.6, 0, "#f8f9fa"); break;
      case "cap": hb(H + 0.8, 2.4, H + 0.8, 0, H, 0, hatC); hb(H, 0.6, 4, 0, H, -H / 2 - 2, hatC); break;
      case "cowboy": hb(H + 6, 0.6, H + 6, 0, H + 0.4, 0, "#8d6e57"); hb(H, 3, H, 0, H + 1, 0, "#8d6e57"); break;
      case "crown": for (const [x, z] of [[-3, -3], [3, -3], [-3, 3], [3, 3], [0, -3], [0, 3]]) hb(1.6, 3, 1.6, x, H, z, "#fab005"); hb(H + 0.6, 1, H + 0.6, 0, H, 0, "#fab005"); break;
      case "chef": hb(H, 2, H, 0, H, 0, "#ffffff"); hb(H + 2, 3, H + 2, 0, H + 2, 0, "#ffffff"); break;
      case "tophat": hb(H + 3, 0.6, H + 3, 0, H, 0, "#212529"); hb(H - 1, 5, H - 1, 0, H + 0.6, 0, "#212529"); hb(H - 0.9, 1, H - 0.9, 0, H + 1, 0, "#c92a2a"); break;
      case "headphones": hb(1.6, 3, 3, -H / 2 - 0.8, H / 2 - 1, 0, "#212529"); hb(1.6, 3, 3, H / 2 + 0.8, H / 2 - 1, 0, "#212529"); hb(H + 3, 0.8, 1.2, 0, H + 0.6, 0, hatC); break;
      case "helmet": hb(H + 1.2, 3, H + 1.2, 0, H - 1, 0, "#fab005"); hb(H + 1.2, 0.6, 2, 0, H - 1, -H / 2 - 1, "#fab005"); break;
      case "party": for (let i = 0; i < 4; i++) hb(5 - i * 1.2, 1.4, 5 - i * 1.2, 0, H + i * 1.4, 0, i % 2 ? "#ffd43b" : "#f783ac"); break;
      case "bucket": hb(H + 1, 3, H + 1, 0, H - 0.4, 0, hatC); hb(H + 3, 0.5, H + 3, 0, H - 0.6, 0, hatC); break;
      case "headband": hb(H + 0.4, 1.2, H + 0.4, 0, H - 2, 0, hatC); break;
    }
    this.height = 1.8;
    this.body.scale.setScalar(1.8 / ((LEG + TOR + H + 1.0) * U));        // 头顶 ≈ 1.8 m
  }

  setExpression(e, force = false) {
    if (!force && this.faceExpr === e) return;
    this.faceExpr = e;
    this.faceMat.map = drawnFace(this.skin, e, this.eye, this.hairC);
    this.faceMat.color.set("#ffffff");
    this.faceMat.emissiveMap = this.faceMat.map;
    this.faceMat.needsUpdate = true;
  }

  pose(action, ph = 0, t = 0) {
    const s = Math.sin(ph), c = Math.cos(ph);
    if (!this.expr) this.setExpression({ scared: "shock", fall: "shock", run: "shock", sprint: "shock", cheer: "smile", wave: "smile", jump: "smile",
                                         point: "smirk", think: "neutral", sit: "neutral", swim: "smile", kneel: "sad" }[action] || "neutral");
    this.body.position.set(0, 0, 0); this.body.rotation.set(0, 0, 0);
    for (const L of this.legs) L.rotation.set(0, 0, 0);
    for (const A of this.arms) A.rotation.set(0, 0, 0);
    this.head.rotation.set(0, 0, 0);
    const sw = { walk: 0.5, run: 0.9, sprint: 1.1, swim: 0.3 }[action] || 0;
    if (sw) {
      this.legs[0].rotation.x = s * sw; this.legs[1].rotation.x = -s * sw;
      this.arms[0].rotation.x = -s * sw; this.arms[1].rotation.x = s * sw;
      this.body.position.y = Math.abs(c) * 0.04 * sw;
    }
    switch (action) {
      case "idle": this.arms[0].rotation.z = -0.05; this.arms[1].rotation.z = 0.05; this.head.rotation.y = Math.sin(t * 0.7) * 0.12; break;
      case "cheer": this.arms[0].rotation.z = -2.6 + Math.sin(t * 6) * 0.2; this.arms[1].rotation.z = 2.6 - Math.sin(t * 6) * 0.2; this.body.position.y = Math.abs(Math.sin(t * 5)) * 0.15; break;
      case "wave": this.arms[1].rotation.z = 2.5 + Math.sin(t * 8) * 0.35; break;
      case "point": this.arms[1].rotation.x = -1.5; this.head.rotation.y = -0.2; break;
      case "scared": this.arms[0].rotation.set(-1.9, 0, -0.4); this.arms[1].rotation.set(-1.9, 0, 0.4); this.body.position.x = Math.sin(t * 30) * 0.01; break;
      case "jump": this.body.position.y = Math.abs(Math.sin(t * 4)) * 0.6; this.arms[0].rotation.z = -2.4; this.arms[1].rotation.z = 2.4; break;
      case "think": this.arms[1].rotation.set(-2.2, 0, 0.6); this.head.rotation.z = 0.12; break;
      case "phone": this.arms[1].rotation.set(-1.9, 0, 0.3); this.head.rotation.x = 0.35; break;
      case "sit": this.legs[0].rotation.x = -1.5; this.legs[1].rotation.x = -1.5; this.body.position.y = -0.55; break;
      case "kneel": this.legs[0].rotation.x = -1.5; this.legs[1].rotation.x = 0.3; this.body.position.y = -0.4; break;
      case "lie": this.body.rotation.x = -Math.PI / 2; this.body.position.y = 0.25; break;
      case "fall": case "float": case "fly": this.body.rotation.x = action === "fly" ? -1.35 : Math.sin(t * 2) * 0.3; this.arms[0].rotation.z = -2.2 + Math.sin(t * 7) * 0.4; this.arms[1].rotation.z = 2.2 - Math.sin(t * 7) * 0.4; this.legs[0].rotation.x = Math.sin(t * 6) * 0.5; this.legs[1].rotation.x = -Math.sin(t * 6) * 0.5; break;
      case "swim": this.body.rotation.x = -1.3; this.arms[0].rotation.x = -2 + s; this.arms[1].rotation.x = -2 - s; break;
      case "pray": this.arms[0].rotation.set(-1.4, 0, 0.5); this.arms[1].rotation.set(-1.4, 0, -0.5); break;
    }
  }
}

export const PEOPLE_COUNTS = () => ({ hair: HAIR.length, hats: HATS.length, outfits: OUTFITS.length, skins: PAL.skin.length, expressions: EXPRS.length });
