// 主体（跑步的人 / 球 / 车 / 方块 / 火箭）与特效（尘土 / 速度线 / 等离子 / 激波 ...）。
// 全部是帧号的纯函数：同一帧在任何 worker 里渲染出来都一样。
import * as THREE from "three";

const std = (color, o = {}) => new THREE.MeshStandardMaterial({ color, roughness: 0.75, metalness: 0.0, ...o });

function limb(radius, length, mat) {
  // 以顶端为原点向下长的胶囊
  const g = new THREE.CapsuleGeometry(radius, length, 4, 10);
  g.translate(0, -length / 2 - radius * 0.3, 0);
  const m = new THREE.Mesh(g, mat);
  m.castShadow = true;
  return m;
}

export class Runner {
  constructor(color = "#c8322b") {
    this.root = new THREE.Group();
    const hoodie = std(color, { roughness: 0.9 });
    const jeans = std("#3f5a85", { roughness: 0.95 });
    const skin = std("#d6a07a", { roughness: 0.7 });
    const hair = std("#2b2420", { roughness: 1 });
    const shoe = std("#f2f2f2", { roughness: 0.6 });
    this.materials = [hoodie, jeans, skin, hair, shoe];

    this.hips = new THREE.Group();
    this.hips.position.y = 0.98;
    this.root.add(this.hips);

    const pelvis = new THREE.Mesh(new THREE.BoxGeometry(0.34, 0.16, 0.2), jeans);
    pelvis.castShadow = true;
    this.hips.add(pelvis);

    this.spine = new THREE.Group();
    this.spine.position.y = 0.06;
    this.hips.add(this.spine);
    const torsoG = new THREE.CapsuleGeometry(0.19, 0.36, 4, 12);
    torsoG.scale(1.05, 1, 0.68);
    torsoG.translate(0, 0.3, 0);
    const torso = new THREE.Mesh(torsoG, hoodie);
    torso.castShadow = true;
    this.spine.add(torso);
    // 帽兜 + 抽绳
    const hood = new THREE.Mesh(new THREE.TorusGeometry(0.12, 0.05, 6, 14, Math.PI * 1.3), hoodie);
    hood.position.set(0, 0.6, 0.06);
    hood.rotation.set(-0.3, 0, Math.PI * 1.15);
    this.spine.add(hood);
    const strG = new THREE.CylinderGeometry(0.008, 0.008, 0.16, 4);
    for (const sx of [-0.05, 0.05]) {
      const s = new THREE.Mesh(strG, std("#f2f2f2"));
      s.position.set(sx, 0.48, -0.13);
      this.spine.add(s);
    }

    this.neck = new THREE.Group();
    this.neck.position.y = 0.66;
    this.spine.add(this.neck);
    const head = new THREE.Mesh(new THREE.SphereGeometry(0.115, 18, 14), skin);
    head.scale.set(0.92, 1.1, 1);
    head.position.y = 0.14;
    head.castShadow = true;
    this.neck.add(head);
    const hairM = new THREE.Mesh(new THREE.SphereGeometry(0.122, 18, 10, 0, Math.PI * 2, 0, Math.PI * 0.55), hair);
    hairM.scale.set(0.94, 1.08, 1.02);
    hairM.position.set(0, 0.165, 0.03);
    hairM.rotation.x = 0.55;   // 发际线往后倾，露出脸（脸朝 -z）
    this.neck.add(hairM);
    const eyeM = std("#1d1a18", { roughness: 0.4 });
    for (const ex of [-0.04, 0.04]) {
      const eye = new THREE.Mesh(new THREE.SphereGeometry(0.014, 8, 6), eyeM);
      eye.position.set(ex, 0.155, -0.102);
      this.neck.add(eye);
    }
    const nose = new THREE.Mesh(new THREE.ConeGeometry(0.018, 0.04, 6), skin);
    nose.rotation.x = -Math.PI / 2;
    nose.position.set(0, 0.125, -0.115);
    this.neck.add(nose);
    const neckM = new THREE.Mesh(new THREE.CylinderGeometry(0.045, 0.05, 0.08, 8), skin);
    neckM.position.y = 0.03;
    this.neck.add(neckM);

    const mkArm = (side) => {
      const sh = new THREE.Group();
      sh.position.set(side * 0.235, 0.54, 0);
      this.spine.add(sh);
      sh.add(limb(0.062, 0.24, hoodie));
      const el = new THREE.Group();
      el.position.y = -0.31;
      sh.add(el);
      el.add(limb(0.052, 0.22, hoodie));
      const hand = new THREE.Mesh(new THREE.SphereGeometry(0.05, 10, 8), skin);
      hand.position.y = -0.31;
      hand.castShadow = true;
      el.add(hand);
      return { sh, el };
    };
    const mkLeg = (side) => {
      const hp = new THREE.Group();
      hp.position.set(side * 0.1, -0.05, 0);
      this.hips.add(hp);
      hp.add(limb(0.082, 0.34, jeans));
      const kn = new THREE.Group();
      kn.position.y = -0.44;
      hp.add(kn);
      kn.add(limb(0.07, 0.32, jeans));
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
    this.height = 1.75;
  }

  pose(action, ph, t) {
    const s = Math.sin(ph), c = Math.cos(ph);
    const A = { idle: 0.0, walk: 0.45, run: 0.85, sprint: 1.1, float: 0.25, fly: 0.0 }[action] ?? 0.8;
    const lean = { idle: 0, walk: 0.03, run: 0.16, sprint: 0.3, float: 0.1, fly: 1.35 }[action] ?? 0.15;
    this.hips.rotation.set(0, s * 0.12 * A, 0);
    this.spine.rotation.set(-lean, -s * 0.18 * A, 0);
    this.neck.rotation.set(lean * 0.6, s * 0.1 * A, 0);
    let bob = action === "walk" ? Math.abs(c) * 0.03 : (action === "run" || action === "sprint" ? Math.abs(c) * 0.09 * A : 0);
    if (action === "idle") bob = Math.sin(t * 2) * 0.005;
    if (action === "float") bob = Math.sin(t * 1.3) * 0.08;
    this.hips.position.y = 0.98 + bob - (action === "sprint" ? 0.05 : 0);
    const legSwing = (L, p) => {
      const sp = Math.sin(p);
      L.hp.rotation.x = -sp * 0.75 * A - lean * 0.6;
      const lift = Math.max(0, Math.cos(p));
      L.kn.rotation.x = (0.15 + lift * (action === "walk" ? 0.5 : 1.6) * A);
      L.ft.rotation.x = -0.2 * A;
    };
    const armSwing = (R, p, side) => {
      R.sh.rotation.x = Math.sin(p) * 0.9 * A + lean * 0.4;
      R.sh.rotation.z = side * (0.12 + 0.05 * A);
      R.el.rotation.x = -(0.25 + 1.15 * A);
    };
    legSwing(this.legL, ph); legSwing(this.legR, ph + Math.PI);
    armSwing(this.armL, ph + Math.PI, -1); armSwing(this.armR, ph, 1);
    if (action === "idle") {
      for (const L of [this.legL, this.legR]) { L.hp.rotation.x = 0; L.kn.rotation.x = 0.02; L.ft.rotation.x = 0; }
      for (const R of [this.armL, this.armR]) { R.sh.rotation.x = 0.05; R.el.rotation.x = -0.15; }
    }
    if (action === "float") {
      this.legL.hp.rotation.x = -0.3 + Math.sin(t) * 0.15; this.legL.kn.rotation.x = 0.6;
      this.legR.hp.rotation.x = 0.2 + Math.cos(t) * 0.15; this.legR.kn.rotation.x = 0.3;
      this.armL.sh.rotation.x = 0.4; this.armL.sh.rotation.z = -0.5;
      this.armR.sh.rotation.x = -0.3; this.armR.sh.rotation.z = 0.5;
    }
    if (action === "fly") {
      this.hips.position.y = 1.2;
      this.root.rotation.x = 0;
      this.spine.rotation.x = -1.35;
      this.armR.sh.rotation.x = 2.9; this.armR.el.rotation.x = -0.1;
      this.armL.sh.rotation.x = 0.2; this.armL.el.rotation.x = -0.3;
      for (const L of [this.legL, this.legR]) { L.hp.rotation.x = -1.4; L.kn.rotation.x = 0.15; }
    }
  }
}

export class Prop {
  constructor(type, color) {
    this.root = new THREE.Group();
    this.type = type;
    this.spin = new THREE.Group();
    this.root.add(this.spin);
    const col = color || "#c8322b";
    if (type === "ball") {
      const tex = stripeTexture(col);
      const m = new THREE.Mesh(new THREE.SphereGeometry(0.6, 32, 20), std("#ffffff", { map: tex, roughness: 0.5 }));
      m.castShadow = true;
      this.spin.add(m);
      this.spin.position.y = 0.6;
      this.radius = 0.6;
      this.height = 1.2;
    } else if (type === "cube") {
      const m = new THREE.Mesh(new THREE.BoxGeometry(1.2, 1.2, 1.2), std(col, { roughness: 0.4 }));
      m.castShadow = true;
      this.spin.add(m);
      this.spin.position.y = 0.6;
      this.height = 1.2;
    } else if (type === "rocket") {
      const body = new THREE.Mesh(new THREE.CylinderGeometry(0.35, 0.35, 2.4, 20), std("#e9e9ec", { metalness: 0.3, roughness: 0.4 }));
      const nose = new THREE.Mesh(new THREE.ConeGeometry(0.35, 0.9, 20), std(col));
      nose.position.y = 1.65;
      const g = new THREE.Group();
      g.add(body, nose);
      for (let i = 0; i < 4; i++) {
        const fin = new THREE.Mesh(new THREE.BoxGeometry(0.05, 0.6, 0.5), std(col));
        fin.position.set(Math.cos(i * Math.PI / 2) * 0.4, -1.0, Math.sin(i * Math.PI / 2) * 0.4);
        fin.rotation.y = -i * Math.PI / 2;
        g.add(fin);
      }
      this.flame = new THREE.Mesh(new THREE.ConeGeometry(0.28, 1.4, 16, 1, true),
        new THREE.MeshBasicMaterial({ color: 0xffb347, transparent: true, opacity: 0.85, blending: THREE.AdditiveBlending, depthWrite: false }));
      this.flame.rotation.x = Math.PI;
      this.flame.position.y = -1.9;
      g.add(this.flame);
      g.rotation.x = -Math.PI / 2;  // 头朝 -z（前进方向）
      g.position.y = 1.2;
      g.traverse((o) => { if (o.isMesh) o.castShadow = true; });
      this.spin.add(g);
      this.height = 2.4;
    } else { // car
      this.spin.add(makeCar(col, 1.0, true));
      this.height = 1.5;
    }
  }
  pose(action, ph, t, z) {
    if (this.type === "ball") this.spin.rotation.x = -z / (this.radius || 0.6);
    if (this.type === "cube") { this.spin.rotation.y = t * 0.6; this.spin.rotation.x = t * 0.4; this.spin.position.y = 0.9 + Math.sin(t * 1.5) * 0.15; }
    if (this.type === "rocket" && this.flame) this.flame.scale.set(1, 0.85 + 0.3 * Math.abs(Math.sin(t * 37)), 1);
    if (this.type === "car") this.spin.traverse((o) => { if (o.userData.wheel) o.rotation.x = -z / 0.34; });
  }
}

function stripeTexture(col) {
  const c = document.createElement("canvas");
  c.width = 256; c.height = 128;
  const x = c.getContext("2d");
  x.fillStyle = "#f4f4f4"; x.fillRect(0, 0, 256, 128);
  x.fillStyle = col;
  for (let i = 0; i < 4; i++) x.fillRect(i * 64, 0, 28, 128);
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  return t;
}

const carMats = new Map();
function carMat(c) {
  if (!carMats.has(c)) carMats.set(c, std(c, { roughness: 0.45, metalness: 0.1 }));
  return carMats.get(c);
}
const glassMat = std("#1d2733", { roughness: 0.2, metalness: 0.2 });
const tireMat = std("#151515", { roughness: 0.9 });
const lightMat = new THREE.MeshBasicMaterial({ color: 0xff3030 });
const headMat = new THREE.MeshBasicMaterial({ color: 0xfff3d6 });
const wheelG = new THREE.CylinderGeometry(0.34, 0.34, 0.24, 14);
wheelG.rotateZ(Math.PI / 2);

export function makeCar(color, scale = 1, detailed = false) {
  const g = new THREE.Group();
  const body = new THREE.Mesh(new THREE.BoxGeometry(1.8, 0.62, 4.2), carMat(color));
  body.position.y = 0.66;
  const cabin = new THREE.Mesh(new THREE.BoxGeometry(1.62, 0.55, 2.2), glassMat);
  cabin.position.set(0, 1.22, 0.25);
  const roof = new THREE.Mesh(new THREE.BoxGeometry(1.64, 0.08, 1.9), carMat(color));
  roof.position.set(0, 1.5, 0.3);
  g.add(body, cabin, roof);
  for (const [x, z] of [[-0.82, 1.35], [0.82, 1.35], [-0.82, -1.35], [0.82, -1.35]]) {
    const w = new THREE.Mesh(wheelG, tireMat);
    w.position.set(x, 0.34, z);
    w.userData.wheel = true;
    g.add(w);
  }
  for (const x of [-0.62, 0.62]) {
    const tl = new THREE.Mesh(new THREE.BoxGeometry(0.36, 0.12, 0.04), lightMat);
    tl.position.set(x, 0.78, 2.11);
    const hl = new THREE.Mesh(new THREE.BoxGeometry(0.34, 0.12, 0.04), headMat);
    hl.position.set(x, 0.78, -2.11);
    g.add(tl, hl);
  }
  g.traverse((o) => { if (o.isMesh) { o.castShadow = true; } });
  g.scale.setScalar(scale);
  return g;
}

// ------------------------------------------------------------------ 特效 ---
function rnd(i) { // 确定性伪随机 [0,1)
  const x = Math.sin(i * 127.1 + 311.7) * 43758.5453;
  return x - Math.floor(x);
}

function softSprite(inner = "rgba(255,255,255,1)", outer = "rgba(255,255,255,0)") {
  const c = document.createElement("canvas");
  c.width = c.height = 128;
  const x = c.getContext("2d");
  const gr = x.createRadialGradient(64, 64, 0, 64, 64, 64);
  gr.addColorStop(0, inner); gr.addColorStop(1, outer);
  x.fillStyle = gr; x.fillRect(0, 0, 128, 128);
  const t = new THREE.CanvasTexture(c);
  return t;
}
const SOFT = softSprite();

export class Effects {
  constructor(scene) {
    this.group = new THREE.Group();
    scene.add(this.group);

    // 尘土：附着在主体脚下向后飞散的粒子
    const N = 260;
    this.dustN = N;
    const dg = new THREE.BufferGeometry();
    dg.setAttribute("position", new THREE.BufferAttribute(new Float32Array(N * 3), 3));
    dg.setAttribute("alpha", new THREE.BufferAttribute(new Float32Array(N), 1));
    this.dust = new THREE.Points(dg, new THREE.ShaderMaterial({
      uniforms: { map: { value: SOFT }, color: { value: new THREE.Color(0xd9c3a0) }, size: { value: 90 } },
      vertexShader: `attribute float alpha; varying float vA; uniform float size;
        void main(){ vA=alpha; vec4 mv=modelViewMatrix*vec4(position,1.0); gl_PointSize=size/(-mv.z); gl_Position=projectionMatrix*mv; }`,
      fragmentShader: `uniform sampler2D map; uniform vec3 color; varying float vA;
        void main(){ vec4 t=texture2D(map,gl_PointCoord); gl_FragColor=vec4(color, t.a*vA*0.32); }`,
      transparent: true, depthWrite: false,
    }));
    this.dust.frustumCulled = false;
    this.group.add(this.dust);

    // 速度线：主体周围高速掠过的细线
    const L = 160;
    this.lineN = L;
    const lg = new THREE.BufferGeometry();
    lg.setAttribute("position", new THREE.BufferAttribute(new Float32Array(L * 6), 3));
    this.lines = new THREE.LineSegments(lg, new THREE.LineBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.5, blending: THREE.AdditiveBlending, depthWrite: false }));
    this.lines.frustumCulled = false;
    this.group.add(this.lines);

    // 等离子 / 热：包裹主体的橙色辉光
    this.plasmaMat = new THREE.ShaderMaterial({
      uniforms: { time: { value: 0 }, strength: { value: 1 }, color: { value: new THREE.Color(0xff7a2e) } },
      vertexShader: `varying vec3 vN; varying vec3 vV; varying vec3 vP;
        void main(){ vN=normalize(normalMatrix*normal); vec4 mv=modelViewMatrix*vec4(position,1.0); vV=normalize(-mv.xyz); vP=position; gl_Position=projectionMatrix*mv; }`,
      fragmentShader: `uniform float time; uniform float strength; uniform vec3 color; varying vec3 vN; varying vec3 vV; varying vec3 vP;
        void main(){ float f=pow(1.0-abs(dot(vN,vV)),1.6); float n=0.65+0.35*sin(vP.y*23.0+time*31.0)*sin(vP.x*17.0-time*23.0);
          gl_FragColor=vec4(color*(0.9+f), (0.06+f*0.75)*n*strength); }`,
      transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, side: THREE.DoubleSide,
    });
    this.plasma = new THREE.Group();
    this.group.add(this.plasma);
    this.trail = new THREE.Sprite(new THREE.SpriteMaterial({ map: SOFT, color: 0xff8a3c, transparent: true, blending: THREE.AdditiveBlending, depthWrite: false }));
    this.group.add(this.trail);

    // 光晕
    this.halo = new THREE.Sprite(new THREE.SpriteMaterial({ map: SOFT, color: 0xbfdcff, transparent: true, opacity: 0.4, blending: THREE.AdditiveBlending, depthWrite: false }));
    this.group.add(this.halo);

    // 激波锥（Prandtl–Glauert 雾）
    const cone = new THREE.ConeGeometry(1.4, 2.6, 40, 1, true);
    cone.rotateX(Math.PI / 2);
    this.vapor = new THREE.Mesh(cone, new THREE.ShaderMaterial({
      uniforms: { a: { value: 0 } },
      vertexShader: `varying vec3 vN; varying vec3 vV; varying float vZ; void main(){ vN=normalize(normalMatrix*normal); vec4 mv=modelViewMatrix*vec4(position,1.0); vV=normalize(-mv.xyz); vZ=position.z; gl_Position=projectionMatrix*mv; }`,
      fragmentShader: `uniform float a; varying vec3 vN; varying vec3 vV; varying float vZ; void main(){ float f=1.0-abs(dot(vN,vV)); float fade=smoothstep(1.3,-0.4,vZ); gl_FragColor=vec4(vec3(1.0), f*a*fade*0.9); }`,
      transparent: true, depthWrite: false, side: THREE.DoubleSide,
    }));
    this.group.add(this.vapor);

    // 火 / 烟 / 余烬：放在场景焦点（主体或镜头前方）
    this.fireN = 60;
    this.fire = [];
    const fireMat = new THREE.SpriteMaterial({ map: SOFT, color: 0xff7a20, transparent: true, blending: THREE.AdditiveBlending, depthWrite: false });
    for (let i = 0; i < this.fireN; i++) { const s = new THREE.Sprite(fireMat.clone()); this.group.add(s); this.fire.push(s); }
    this.smokeN = 70;
    this.smoke = [];
    const smokeMat = new THREE.SpriteMaterial({ map: SOFT, color: 0x4a4744, transparent: true, depthWrite: false });
    for (let i = 0; i < this.smokeN; i++) { const s = new THREE.Sprite(smokeMat.clone()); this.group.add(s); this.smoke.push(s); }
    const eg = new THREE.BufferGeometry();
    eg.setAttribute("position", new THREE.BufferAttribute(new Float32Array(300 * 3), 3));
    this.embers = new THREE.Points(eg, new THREE.PointsMaterial({ color: 0xffa040, size: 0.08, transparent: true, blending: THREE.AdditiveBlending, depthWrite: false }));
    this.embers.frustumCulled = false;
    this.group.add(this.embers);
    this.fireLight = new THREE.PointLight(0xff7a30, 0, 30, 1.6);
    this.group.add(this.fireLight);

    // 冲击波环
    this.ring = new THREE.Mesh(new THREE.RingGeometry(0.85, 1.0, 64), new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0, side: THREE.DoubleSide, depthWrite: false }));
    this.group.add(this.ring);
  }

  // subj: {root, height, meshes}, fr: frame, beat: plan beat
  update(subj, subjectMeshes, fr, beat, cam) {
    const fx = new Set(beat ? beat.effects : []);
    const t = fr.t;
    const lt = fr.lt || 0;
    const S = fr.scale || 1;
    const pos = subj ? subj.root.position : new THREE.Vector3();
    const I = Math.max(0.15, fr.intensity || 0);

    // dust
    this.dust.visible = fx.has("dust");
    if (this.dust.visible) {
      const p = this.dust.geometry.attributes.position.array, a = this.dust.geometry.attributes.alpha.array;
      for (let i = 0; i < this.dustN; i++) {
        const life = 1.1;
        const age = ((t + rnd(i) * life) % life) / life;
        const spread = (rnd(i + 7) - 0.5) * 2;
        p[i * 3] = pos.x + spread * (0.4 + age * 2.5) * S;
        p[i * 3 + 1] = pos.y + (0.05 + age * age * 1.4 * rnd(i + 3)) * S;
        p[i * 3 + 2] = pos.z + (0.3 + age * (4 + 10 * I)) * S;
        a[i] = (1 - age) * 0.9;
      }
      this.dust.geometry.attributes.position.needsUpdate = true;
      this.dust.geometry.attributes.alpha.needsUpdate = true;
      this.dust.material.uniforms.size.value = 140 * S;
      this.dust.material.uniforms.color.value.set(beat && beat.scene === "city" ? 0xb8b2a6 : 0xd9c3a0);
    }

    // speedlines：以主体为中心的圆柱体里、沿 z 高速掠过
    this.lines.visible = fx.has("speedlines");
    if (this.lines.visible) {
      const p = this.lines.geometry.attributes.position.array;
      const range = 60 * S, len = (3 + 14 * I) * S;
      for (let i = 0; i < this.lineN; i++) {
        const ang = rnd(i) * Math.PI * 2, r = (1.2 + rnd(i + 11) * 7) * S;
        const zz = ((rnd(i + 5) * range + t * (90 + 260 * I) * S) % range) - range * 0.5;
        const x = pos.x + Math.cos(ang) * r, y = pos.y + 1 * S + Math.sin(ang) * r * 0.7;
        p[i * 6] = x; p[i * 6 + 1] = y; p[i * 6 + 2] = pos.z + zz;
        p[i * 6 + 3] = x; p[i * 6 + 4] = y; p[i * 6 + 5] = pos.z + zz + len;
      }
      this.lines.geometry.attributes.position.needsUpdate = true;
      this.lines.material.opacity = 0.18 + 0.4 * I;
    }

    // plasma / heat：给主体每个网格叠一层 fresnel 辉光外壳
    const plasmaOn = fx.has("plasma") || fx.has("heat");
    const strength = fx.has("plasma") ? 0.8 : 0.35;
    if (plasmaOn && subjectMeshes && this.plasma.children.length === 0) {
      for (const m of subjectMeshes || []) {
        const shell = new THREE.Mesh(m.geometry, this.plasmaMat);
        shell.userData.src = m;
        shell.scale.setScalar(1.18);
        this.plasma.add(shell);
      }
    }
    this.plasma.visible = plasmaOn;
    this.trail.visible = fx.has("plasma");
    if (plasmaOn) {
      this.plasmaMat.uniforms.time.value = t;
      this.plasmaMat.uniforms.strength.value = strength * Math.min(1, lt / 0.4 + 0.2);
      for (const shell of this.plasma.children) {
        const src = shell.userData.src;
        src.updateWorldMatrix(true, false);
        shell.matrixAutoUpdate = false;
        shell.matrix.copy(src.matrixWorld).multiply(new THREE.Matrix4().makeScale(1.16, 1.12, 1.16));
        shell.matrixWorld.copy(shell.matrix);
      }
      // 加热时主体本身也发橙
      for (const m of subjectMeshes || []) {
        if (m.material.emissive) { m.material.emissive.set(0xff6a1a); m.material.emissiveIntensity = 0.18 * strength; }
      }
      this.trail.position.set(pos.x, pos.y + 1.0 * S, pos.z + 1.6 * S);
      this.trail.scale.set(3.2 * S, 3.6 * S, 1);
      this.trail.material.opacity = 0.35 * strength;
    } else if (subjectMeshes) {
      for (const m of subjectMeshes) if (m.material.emissive) m.material.emissiveIntensity = 0;
    }

    this.halo.visible = fx.has("glow");
    if (this.halo.visible) {
      this.halo.position.set(pos.x, pos.y + 1 * S, pos.z);
      this.halo.scale.set(4.5 * S, 4.5 * S, 1);
      this.halo.material.opacity = 0.32 + 0.05 * Math.sin(t * 3);
    }

    this.vapor.visible = fx.has("vapor_cone");
    if (this.vapor.visible) {
      const a = lt < 0.25 ? lt / 0.25 : Math.max(0, 1 - (lt - 0.25) / 1.6);
      this.vapor.material.uniforms.a.value = a;
      this.vapor.position.set(pos.x, pos.y + 1.0 * S, pos.z + 0.5 * S);
      this.vapor.scale.setScalar(S * (1 + lt * 0.4));
    }

    // 火 / 烟 / 余烬
    const focus = subj ? pos.clone() : (cam ? new THREE.Vector3(cam.position.x, 0, cam.position.z - 9) : new THREE.Vector3());
    if (subj) focus.z -= 3 * S;
    const fireOn = fx.has("fire");
    for (let i = 0; i < this.fireN; i++) {
      const sp = this.fire[i];
      sp.visible = fireOn;
      if (!fireOn) continue;
      const life = 0.9;
      const age = ((t * 1.3 + rnd(i) * life) % life) / life;
      const ox = (rnd(i + 1) - 0.5) * 6, oz = (rnd(i + 2) - 0.5) * 3;
      sp.position.set(focus.x + ox * (1 - age * 0.5), focus.y + age * 3.2, focus.z + oz);
      const sc = (1.6 - age) * 1.4;
      sp.scale.set(sc, sc * 1.4, 1);
      sp.material.opacity = (1 - age) * 0.8;
      sp.material.color.setHex(age < 0.3 ? 0xffd27a : 0xff6a1a);
    }
    this.fireLight.intensity = fireOn ? 40 + 12 * Math.sin(t * 23) : 0;
    this.fireLight.position.set(focus.x, focus.y + 1.5, focus.z);
    const smokeOn = fx.has("smoke") || fireOn;
    for (let i = 0; i < this.smokeN; i++) {
      const sp = this.smoke[i];
      sp.visible = smokeOn;
      if (!smokeOn) continue;
      const life = 5;
      const age = ((t + rnd(i + 7) * life) % life) / life;
      sp.position.set(focus.x + (rnd(i) - 0.5) * 4 + age * 6, focus.y + 2 + age * 22, focus.z + (rnd(i + 3) - 0.5) * 4);
      const sc = 2 + age * 12;
      sp.scale.set(sc, sc, 1);
      sp.material.opacity = (1 - age) * 0.55;
    }
    this.embers.visible = fx.has("embers") || fireOn;
    if (this.embers.visible) {
      const a = this.embers.geometry.attributes.position.array;
      for (let i = 0; i < 300; i++) {
        const age = ((t * 0.5 + rnd(i + 11)) % 1);
        a[i * 3] = focus.x + (rnd(i) - 0.5) * 10 + Math.sin(t * 2 + i) * 0.5;
        a[i * 3 + 1] = focus.y + age * 12;
        a[i * 3 + 2] = focus.z + (rnd(i + 5) - 0.5) * 8;
      }
      this.embers.geometry.attributes.position.needsUpdate = true;
    }

    this.ring.visible = fx.has("shockwave") && lt < 1.6;
    if (this.ring.visible) {
      const k = lt / 1.6;
      const r = (0.5 + k * 14) * S;
      this.ring.scale.set(r, r, r);
      this.ring.position.set(pos.x, pos.y + 1 * S, pos.z + 0.5);
      this.ring.material.opacity = (1 - k) * 0.6;
    }
  }
}
