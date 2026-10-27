// 第一人称（format=pov，camera="eyes"）：你的眼睛机位 + 画面下方你自己的一双手。
// 手挂在镜头上（镜头坐标系），姿势在段与段之间平滑过渡；全部是帧号的纯函数。
import * as THREE from "three";

const easeIO = (u) => u * u * (3 - 2 * u);
const HALF_PI = Math.PI / 2;
const HIDE = { pos: [0.2, -0.75, -0.45], rot: [0.4, 0.2, 0.3], curl: 0.4, hidden: true };

// 姿势都按右手写（左手由代码按 x 镜像）。pos：镜头坐标（竖屏 fov 74 时 z=-0.5 处可见约 ±0.2 × ±0.37）；
// rot：YXZ 欧拉角（手的局部坐标：手指朝 -z，手心朝 -y）；curl：0 张开 … 1 握拳；index：食指单独的弯曲
const P = (pos, rot, curl, more = {}) => ({ pos, rot, curl, ...more });
const POSES = {
  none: { R: HIDE, L: HIDE },
  idle: { R: P([0.15, -0.34, -0.5], [0.6, 0.3, 0.4], 0.45), L: P([0.15, -0.35, -0.5], [0.6, 0.3, 0.4], 0.45) },
  reach: { R: P([0.055, -0.12, -0.55], [0.12, 0.08, 0.12], 0.12), L: HIDE },
  phone: { R: P([0.03, -0.19, -0.36], [Math.PI / 2 - 0.3, Math.PI, 0.05], 0.0), L: HIDE },
  shield: { R: P([0.085, -0.07, -0.36], [Math.PI / 2 - 0.1, 0.15, -0.12], 0.08), L: P([0.085, -0.07, -0.36], [Math.PI / 2 - 0.1, 0.15, -0.12], 0.08) },
  cover: { R: P([0.05, -0.03, -0.2], [Math.PI / 2, 0.1, -0.08], 0.0), L: P([0.05, -0.03, -0.2], [Math.PI / 2, 0.1, -0.08], 0.0) },
  grab: { R: P([0.085, -0.18, -0.48], [0.25, 0.05, -1.0], 0.55), L: P([0.085, -0.18, -0.48], [0.25, 0.05, -1.0], 0.55) },
  fists: { R: P([0.11, -0.2, -0.42], [0.9, 0.1, -0.5], 1.0), L: P([0.11, -0.2, -0.42], [0.9, 0.1, -0.5], 1.0) },
  point: { R: P([0.065, -0.16, -0.5], [0.22, 0.12, 0.2], 1.0, { index: 0.0 }), L: HIDE },
  torch: { R: P([0.07, -0.17, -0.46], [0.3, 0.15, -0.6], 1.0), L: HIDE },
  wave: { R: P([0.1, -0.05, -0.46], [Math.PI / 2 - 0.2, 0.2, 0], 0.05, { wave: 1 }), L: HIDE },
  hold: { R: P([0.03, -0.2, -0.4], [0.35, 0, Math.PI], 0.5), L: P([0.075, -0.22, -0.42], [0.35, 0, Math.PI], 0.5) },
  float: { R: P([0.14, -0.15, -0.46], [0.15, -0.35, 0.6], 0.2, { drift: 1 }), L: P([0.14, -0.13, -0.46], [0.15, -0.35, 0.6], 0.2, { drift: 1 }) },
};
const HOLD_POSE = { phone: "phone", flashlight: "torch", cup: "hold" };

function mirror(p) {
  return { ...p, pos: [-p.pos[0], p.pos[1], p.pos[2]], rot: [p.rot[0], -p.rot[1], -p.rot[2]] };
}
const UP = new THREE.Vector3(0, 1, 0);

function mat(color, emissive = 0.12, skin = true) {
  // 皮肤：带一点偏红的 sheen，比纯漫反射更像肉而不像木头
  const c = new THREE.Color(color);
  return new THREE.MeshPhysicalMaterial({ color: c, roughness: skin ? 0.5 : 0.8, metalness: 0, emissive: c.clone().multiplyScalar(emissive),
    sheen: skin ? 0.5 : 0, sheenColor: new THREE.Color("#ff8f70"), sheenRoughness: 0.45 });
}

function capsule(r, len, m) {
  const g = new THREE.CapsuleGeometry(r, len, 4, 10);
  g.translate(0, len / 2 + r, 0);
  g.rotateX(-HALF_PI);   // 沿 -z 伸出
  const mesh = new THREE.Mesh(g, m);
  mesh.castShadow = false; mesh.receiveShadow = false;
  return mesh;
}

class Hand {
  constructor(side, skin, sleeve) {
    this.side = side;   // 1 = 右手，-1 = 左手
    this.root = new THREE.Group();
    const sk = mat(skin);
    // 手掌：扁盒 + 椭球垫，边缘圆润
    const palm = new THREE.Mesh(new THREE.BoxGeometry(0.074, 0.022, 0.082), sk);
    palm.geometry.translate(0, 0, -0.046);
    const pad = new THREE.Mesh(new THREE.SphereGeometry(1, 20, 12), sk);
    pad.scale.set(0.045, 0.017, 0.052); pad.position.set(0, -0.002, -0.046);
    const heel = new THREE.Mesh(new THREE.SphereGeometry(1, 16, 10), sk);
    heel.scale.set(0.036, 0.02, 0.03); heel.position.set(0, 0, -0.008);
    this.root.add(palm, pad, heel);
    // 手指：两节（根节 + 指尖），curl 绕 x 轴弯向手心（-y）
    this.fingers = [];
    const fx = [0.028, 0.0095, -0.0095, -0.027], fl = [0.03, 0.034, 0.032, 0.024];
    for (let k = 0; k < 4; k++) {
      const base = new THREE.Group();
      base.position.set(fx[k] * side, 0, -0.088);
      base.add(capsule(0.0108, fl[k], sk));
      const tip = new THREE.Group();
      tip.position.set(0, 0, -(fl[k] + 0.014));
      tip.add(capsule(0.0098, fl[k] * 0.72, sk));
      base.add(tip);
      this.root.add(base);
      this.fingers.push([base, tip]);
    }
    // 拇指：从手掌内侧斜伸出
    this.thumb = new THREE.Group();
    this.thumb.position.set(-0.04 * side, -0.006, -0.025);
    this.thumb.rotation.set(-0.35, 0.38 * side, 0);
    this.thumb.add(capsule(0.0115, 0.028, sk));
    const tt = new THREE.Group(); tt.position.set(0, 0, -0.042); tt.add(capsule(0.0102, 0.02, sk));
    this.thumb.add(tt); this.thumbTip = tt;
    this.root.add(this.thumb);
    // 手腕（前臂在 PovRig 里按镜头坐标单独摆：从手腕伸向画面外的手肘）
    const wrist = new THREE.Mesh(new THREE.SphereGeometry(1, 16, 10), sk);
    wrist.scale.set(0.032, 0.022, 0.04); wrist.position.z = 0.012;
    this.root.add(wrist);
    // 拿着的东西
    this.items = {};
    const phone = new THREE.Group();
    const body = new THREE.Mesh(new THREE.BoxGeometry(0.072, 0.009, 0.15), new THREE.MeshStandardMaterial({ color: "#1b1b1f", roughness: 0.3, metalness: 0.4 }));
    this.screenCanvas = document.createElement("canvas"); this.screenCanvas.width = 256; this.screenCanvas.height = 512;
    this.screenTex = new THREE.CanvasTexture(this.screenCanvas); this.screenTex.colorSpace = THREE.SRGBColorSpace;
    const screen = new THREE.Mesh(new THREE.PlaneGeometry(0.066, 0.142), new THREE.MeshBasicMaterial({ map: this.screenTex, toneMapped: false }));
    screen.rotation.x = HALF_PI; screen.rotation.z = Math.PI; screen.position.y = -0.0047;
    phone.add(body, screen); phone.userData.at = [0, -0.032, -0.105];
    this.items.phone = phone;
    const torch = new THREE.Group();
    const tb = new THREE.Mesh(new THREE.CylinderGeometry(0.016, 0.02, 0.17, 16), new THREE.MeshStandardMaterial({ color: "#2b2d31", roughness: 0.35, metalness: 0.6 }));
    tb.rotation.x = HALF_PI; torch.add(tb);
    const lens = new THREE.Mesh(new THREE.CircleGeometry(0.019, 20), new THREE.MeshBasicMaterial({ color: "#fff8e1", toneMapped: false }));
    lens.position.z = -0.086; lens.rotation.y = Math.PI; torch.add(lens);
    const spot = new THREE.SpotLight("#fff4d6", 60, 40, 0.42, 0.55, 1.2);
    spot.position.set(0, 0, -0.09); spot.target.position.set(0, 0, -5); torch.add(spot, spot.target);
    torch.userData.at = [0, -0.035, -0.1];
    this.items.flashlight = torch;
    const cup = new THREE.Group();
    const cb = new THREE.Mesh(new THREE.CylinderGeometry(0.042, 0.034, 0.1, 24), new THREE.MeshStandardMaterial({ color: "#f1f3f5", roughness: 0.3 }));
    const cf = new THREE.Mesh(new THREE.CircleGeometry(0.038, 20), new THREE.MeshStandardMaterial({ color: "#3b2314", roughness: 0.2 }));
    cf.rotation.x = -HALF_PI; cf.position.y = 0.045; cup.add(cb, cf);
    cup.userData.at = [0, -0.07, -0.05];   // hold 姿势手心朝上，杯子坐在手掌上
    this.items.cup = cup;
    // 物体在镜头坐标里的朝向（每帧用手的旋转反推局部朝向，保证屏幕朝你 / 手电朝前 / 杯子直立）
    this.itemQ = {
      phone: new THREE.Quaternion().setFromEuler(new THREE.Euler(-Math.PI / 2, 0, Math.PI, "ZYX")),
      flashlight: new THREE.Quaternion(),
      cup: new THREE.Quaternion(),
    };
    for (const k in this.items) { this.items[k].visible = false; this.items[k].position.set(...this.items[k].userData.at); this.root.add(this.items[k]); }
    this.root.traverse((o) => { if (o.isMesh) { o.castShadow = false; o.receiveShadow = false; o.frustumCulled = false; } });
    this._q0 = new THREE.Quaternion(); this._q1 = new THREE.Quaternion(); this._e = new THREE.Euler(0, 0, 0, "YXZ");
    this.phoneText = null;
  }

  drawPhone(text, clock) {
    const key = text + "|" + clock;
    if (this.phoneText === key) return;
    this.phoneText = key;
    const c = this.screenCanvas.getContext("2d");
    const g = c.createLinearGradient(0, 0, 0, 512);
    g.addColorStop(0, "#1f2a3d"); g.addColorStop(1, "#0f1218");
    c.fillStyle = g; c.fillRect(0, 0, 256, 512);
    c.fillStyle = "#ffffff"; c.textAlign = "center";
    c.font = "300 64px Inter, sans-serif"; c.fillText(clock, 128, 120);
    if (text) {
      c.fillStyle = "rgba(255,255,255,0.14)";
      c.beginPath(); c.roundRect(18, 190, 220, 150, 22); c.fill();
      c.fillStyle = "#ffffff"; c.font = "600 26px Inter, sans-serif";
      const words = text.split(/\s+/); let line = "", y = 240;
      for (const w of words) {
        const t = line ? line + " " + w : w;
        if (c.measureText(t).width > 196 && line) { c.fillText(line, 128, y); line = w; y += 34; }
        else line = t;
        if (y > 320) break;
      }
      if (line && y <= 320) c.fillText(line, 128, y);
    }
    this.screenTex.needsUpdate = true;
  }

  apply(a, b, k, t, extra) {
    // 位置 / 旋转 / 弯曲在两个姿势之间插值（k: 0 → a，1 → b）
    const lerp = (x, y) => x + (y - x) * k;
    const pos = a.pos.map((v, i) => lerp(v, b.pos[i]));
    this._q0.setFromEuler(this._e.set(...a.rot));
    this._q1.setFromEuler(this._e.set(...b.rot));
    this.root.quaternion.copy(this._q0).slerp(this._q1, k);
    const curl = lerp(a.curl, b.curl);
    const index = lerp(a.index ?? a.curl, b.index ?? b.curl);
    const side = this.side;
    // 呼吸 / 走路的轻微晃动、手抖、挥手、失重漂浮
    const bob = extra.bob || 0;
    pos[1] += Math.sin(t * 1.7 + side) * 0.004 + bob;
    pos[0] += Math.sin(t * 0.9 + side * 2) * 0.003 + (extra.sway || 0) * side;
    const tr = extra.tremble || 0;
    if (tr) { pos[0] += Math.sin(t * 41 + side * 3) * 0.004 * tr; pos[1] += Math.sin(t * 37 + side) * 0.004 * tr; }
    const drift = lerp(a.drift || 0, b.drift || 0);
    if (drift) { pos[1] += Math.sin(t * 0.8 + side) * 0.03 * drift; pos[0] += Math.sin(t * 0.6 + side * 1.7) * 0.02 * drift * side; }
    this.root.position.set(pos[0] * (extra.wide || 1), pos[1], pos[2]);
    const wave = lerp(a.wave || 0, b.wave || 0);
    if (wave) this.root.rotateZ(Math.sin(t * 9) * 0.35 * wave);
    this.fingers.forEach(([base, tip], i) => {
      const c = (i === 0 ? index : curl) + (wave ? 0 : Math.sin(t * 1.3 + i) * 0.02);
      base.rotation.x = -c * 1.45; tip.rotation.x = -c * 1.25;
      base.rotation.y = (i - 1.5) * 0.05 * (1 - c) * side;
    });
    // 拇指：张开时斜伸，握拳时收到手指前面
    this.thumb.rotation.x = -0.35 - curl * 0.75; this.thumb.rotation.y = side * (0.38 - curl * 0.55); this.thumbTip.rotation.x = -curl * 0.9;
    const inv = this.root.quaternion.clone().invert();
    for (const name in this.items) this.items[name].quaternion.copy(inv).multiply(this.itemQ[name]);
  }
}

export class PovRig {
  constructor(camera, opts) {
    this.camera = camera;
    this.group = new THREE.Group();
    camera.add(this.group);
    this.R = new Hand(1, opts.skin || "#c68642", opts.sleeve || "#343a40");
    this.L = new Hand(-1, opts.skin || "#c68642", opts.sleeve || "#343a40");
    this.group.add(this.R.root, this.L.root);
    // 前臂：从手腕连到画面外的手肘（镜头坐标），细一点、略收窄
    const sl = mat(opts.sleeve || "#343a40", 0.08, false);
    this.arms = [1, -1].map(() => {
      const g = new THREE.CapsuleGeometry(0.034, 1, 4, 18);
      g.translate(0, 0.5, 0);
      const m = new THREE.Mesh(g, sl); m.frustumCulled = false;
      this.group.add(m); return m;
    });
    // 手自带一盏柔光（夜景里也看得清自己的手）
    this.group.traverse((o) => { o.userData.thinOutline = true; });   // toon 风格：手和袖子用细描边
    this.fill = new THREE.PointLight("#fff1e0", 0.6, 1.6, 1.5);
    this.fill.position.set(0, 0.1, 0.1);
    this.group.add(this.fill);
  }

  static poseOf(h) {
    if (!h) return POSES.none;
    let name = h.pose;
    if (h.holding !== "none" && (name === "idle" || name === "none" || (h.holding === "flashlight" && name === "point"))) name = HOLD_POSE[h.holding];
    return POSES[name] || POSES.idle;
  }

  update(fr, beat, prevBeat, land, head) {
    const h = beat && beat.hands;
    this.group.visible = !!h;
    if (!h) return;
    const cur = PovRig.poseOf(h);
    const prev = prevBeat && prevBeat.hands && prevBeat.camera === "eyes" ? PovRig.poseOf(prevBeat.hands) : cur;
    const k = easeIO(Math.min(1, (fr.lt || 0) / 0.45));
    const t = fr.t || 0;
    const extra = { tremble: h.tremble, wide: land ? 2.1 : 1, bob: head.handBob || 0, sway: head.handSway || 0 };
    this.R.apply(prev.R, cur.R, k, t, extra);
    this.L.apply(mirror(prev.L), mirror(cur.L), k, t, { ...extra, wide: extra.wide });
    const holding = h.holding !== "none" ? h.holding : (h.pose === "phone" ? "phone" : "none");
    for (const name in this.R.items) this.R.items[name].visible = name === holding;
    if (holding === "phone") {
      const mins = 41 + Math.floor(t / 60);
      this.R.drawPhone(h.phone_text || "", h.phone_time || `9:${String(mins % 60).padStart(2, "0")}`);
    }
    const lHidden = cur.L.hidden && prev.L.hidden;
    this.L.root.visible = !lHidden;
    // 前臂：手腕（手掌后方）→ 手肘（画面外下方、略向外）
    [[this.R, 1], [this.L, -1]].forEach(([hand, side], i) => {
      const arm = this.arms[i];
      arm.visible = hand.root.visible;
      if (!arm.visible) return;
      const wrist = new THREE.Vector3(0, 0, 0.02).applyQuaternion(hand.root.quaternion).add(hand.root.position);
      const elbow = new THREE.Vector3(side * 0.2 * extra.wide, -0.62, -0.1);
      const dir = elbow.clone().sub(wrist);
      arm.position.copy(wrist);
      arm.quaternion.setFromUnitVectors(UP, dir.clone().normalize());
      arm.scale.set(1, dir.length(), 1);
    });
  }
}

// ---------- 眼睛机位：视线（偏航/俯仰）+ 头部运动（呼吸 / 走 / 跑 / 摔倒 / 漂浮 / 发抖） ----------
const SPEED = { walk: 1.25, stumble: 1.0, run: 4.2 };

export function eyesCamera(camera, beat, fr, eye, S, plan, noise1) {
  const lt = fr.lt || 0, u = Math.min(1, fr.frac || 0), t = fr.t || 0;
  const g0 = beat.gaze || [0, 0], g1 = beat.gaze_to || g0;
  const e = easeIO(u);
  let yaw = (g0[0] + (g1[0] - g0[0]) * e) * Math.PI / 180;
  let pitch = (g0[1] + (g1[1] - g0[1]) * e) * Math.PI / 180;
  let roll = 0;
  const pos = eye.clone();
  const head = beat.head || "steady";
  const out = { handBob: 0, handSway: 0 };
  const fwd = new THREE.Vector3(-Math.sin(yaw), 0, -Math.cos(yaw));
  if (head === "breathe") { pos.y += Math.sin(t * 2 * Math.PI / 3.4) * 0.008 * S; pitch += Math.sin(t * 2 * Math.PI / 3.4) * 0.006; }
  if (head === "walk" || head === "stumble" || head === "run") {
    const run = head === "run";
    const f = run ? 2.9 : 1.8;   // 每秒步数 / 2
    pos.addScaledVector(fwd, SPEED[head] * lt * S);
    const step = Math.abs(Math.sin(t * Math.PI * f));
    pos.y += (step * (run ? 0.075 : 0.035) - (run ? 0.04 : 0.015)) * S;
    roll += Math.sin(t * Math.PI * f / 2) * (run ? 0.035 : 0.014);
    yaw += Math.sin(t * Math.PI * f / 2) * (run ? 0.02 : 0.008);
    pitch += (run ? -0.06 : -0.02) + step * (run ? 0.02 : 0.008);
    out.handBob = -step * (run ? 0.03 : 0.012);
    out.handSway = Math.sin(t * Math.PI * f / 2) * (run ? 0.025 : 0.008);
    if (head === "stumble" && u > 0.45 && u < 0.75) {   // 中途绊一下
      const s = Math.sin((u - 0.45) / 0.3 * Math.PI);
      roll += s * 0.22; pitch -= s * 0.35; pos.y -= s * 0.25 * S;
      out.handBob += s * 0.08;
    }
  }
  if (head === "fall") {   // 往下掉：加速下落、低头、翻滚，最后撞地抖一下
    const fu = Math.min(1, u / 0.82);
    pos.y -= (eye.y - 0.25 * S) * fu * fu;
    pitch -= 0.7 * easeIO(fu);
    roll += 0.45 * fu * fu;
    out.handBob = 0.06 * fu;
    if (u > 0.82) { const k = 1 - (u - 0.82) / 0.18; pos.y += noise1(t * 3, 4) * 0.05 * k * S; roll += noise1(t * 3, 7) * 0.08 * k; }
  }
  if (head === "float") {
    pos.y += lt * 0.22 * S; roll += lt * 0.09; yaw += Math.sin(t * 0.4) * 0.12;
  }
  if (head === "shake") {
    pitch += noise1(t * 2.2, 3) * 0.012; yaw += noise1(t * 2.2, 8) * 0.012; roll += noise1(t * 1.4, 5) * 0.01;
  }
  const fx = beat.effects || [];
  if (fx.includes("dizzy")) { roll += Math.sin(t * 1.3) * 0.12; yaw += Math.sin(t * 0.9) * 0.08; pitch += Math.sin(t * 1.7) * 0.04; }
  if (fx.includes("shake") || fx.includes("earthquake")) {
    const amp = fx.includes("earthquake") ? 0.06 : 0.025;
    pos.x += noise1(t, 1) * amp * S; pos.y += noise1(t, 2) * amp * S; roll += noise1(t, 9) * amp * 0.5;
  }
  if (beat.roll || beat.roll_to != null) {
    const r0 = beat.roll || 0, r1 = beat.roll_to != null ? beat.roll_to : r0;
    roll += (r0 + (r1 - r0) * e) * Math.PI / 180;
  }
  camera.position.copy(pos);
  camera.rotation.order = "YXZ";
  camera.rotation.set(pitch, -yaw, roll);
  camera.fov = plan.width > plan.height ? 62 : 74;
  camera.near = 0.02;
  camera.far = 20000 * Math.max(1, S);
  camera.updateProjectionMatrix();
  const look = pos.clone().add(new THREE.Vector3(0, 0, -5).applyEuler(camera.rotation));
  return { look, head: out };
}
