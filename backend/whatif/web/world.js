// 布景：只有自定义布景（Block POV 格式，按分镜的 env.set 搭建）。这里负责灯光、积雪覆盖和天气粒子。
import * as THREE from "three";
import { stars } from "./common.js";
import { setEnv } from "./sets.js";

const EMPTY_SET = { background: ["#0d1622", "#2a3b52"], ground: "none", ground_color: "#1a2230", light: "#ffffff",
  light_intensity: 2.2, ambient: 0.8, focus: [0, 1, 0], zoom: 1, objects: [], fog: null };

// 积雪 / 落灰覆盖：朝上的面（屋顶、路面、车顶）按 env.cover 变白 / 变灰；全部材质共用一个 uniform
const COVER = { amount: { value: 0 }, color: { value: new THREE.Color(0xf4f7fb) } };
function coverMaterial(m) {
  if (!m || m.userData.cover || !(m.isMeshStandardMaterial || m.isMeshLambertMaterial || m.isMeshPhongMaterial || (m.isMeshBasicMaterial && !m.transparent))) return;
  m.userData.cover = true;
  const prev = m.onBeforeCompile;
  m.onBeforeCompile = (sh, r) => {
    if (prev) prev(sh, r);
    sh.uniforms.uCover = COVER.amount; sh.uniforms.uCoverCol = COVER.color;
    sh.vertexShader = "varying float vUp;\n" + sh.vertexShader.replace("#include <beginnormal_vertex>",
      "#include <beginnormal_vertex>\n  vUp = normalize(mat3(modelMatrix) * objectNormal).y;");
    sh.fragmentShader = "uniform float uCover; uniform vec3 uCoverCol; varying float vUp;\n" + sh.fragmentShader.replace("#include <color_fragment>",
      "#include <color_fragment>\n  float coverK = clamp(uCover * smoothstep(0.3, 0.75, vUp) * 1.15 + uCover * uCover * 0.22, 0.0, 1.0);\n  diffuseColor.rgb = mix(diffuseColor.rgb, uCoverCol, coverK);")
      .replace("#include <emissivemap_fragment>", "#include <emissivemap_fragment>\n  totalEmissiveRadiance += uCoverCol * coverK * 0.22;");   // 雪自己亮一点，暗天也读得出来
  };
  const key = "cover:" + (prev ? prev.toString() : "");
  m.customProgramCacheKey = () => key;
  m.needsUpdate = true;
}

function rnd(i) { const x = Math.sin(i * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); }

class Atmosphere {
  // 天气粒子（雨/雪/灰/尘）、流星、夜空星星；全部是 t 的函数
  constructor(scene) {
    const N = 2400;
    this.N = N;
    const lg = new THREE.BufferGeometry();
    lg.setAttribute("position", new THREE.BufferAttribute(new Float32Array(N * 6), 3));
    this.rain = new THREE.LineSegments(lg, new THREE.LineBasicMaterial({ color: 0xc8d4e0, transparent: true, opacity: 0.45, depthWrite: false }));
    this.rain.frustumCulled = false;
    const pg = new THREE.BufferGeometry();
    pg.setAttribute("position", new THREE.BufferAttribute(new Float32Array(N * 3), 3));
    this.flakes = new THREE.Points(pg, new THREE.PointsMaterial({ color: 0xffffff, size: 0.12, transparent: true, opacity: 0.9, depthWrite: false }));
    this.flakes.frustumCulled = false;
    const M = 40;
    this.M = M;
    const mg = new THREE.BufferGeometry();
    mg.setAttribute("position", new THREE.BufferAttribute(new Float32Array(M * 6), 3));
    this.meteors = new THREE.LineSegments(mg, new THREE.LineBasicMaterial({ color: 0xffe2b0, transparent: true, opacity: 0.9, blending: THREE.AdditiveBlending, depthWrite: false, fog: false }));
    this.meteors.frustumCulled = false;
    this.nightStars = stars(3000, 2500, 21);
    this.nightStars.material.transparent = true;
    scene.add(this.rain, this.flakes, this.meteors, this.nightStars);
  }
  update(spec, fr, cam, outdoor, starsLevel) {
    const w = outdoor ? spec.weather : "clear";
    const t = fr.t, N = this.N;
    this.rain.visible = w === "rain" || w === "storm";
    if (this.rain.visible) {
      const a = this.rain.geometry.attributes.position.array;
      for (let i = 0; i < N; i++) {
        const x = cam.x + (rnd(i) - 0.5) * 60, z = cam.z + (rnd(i + 9) - 0.5) * 60;
        const y = cam.y + 20 - ((t * 28 + rnd(i + 3) * 40) % 40);
        a[i * 6] = x; a[i * 6 + 1] = y; a[i * 6 + 2] = z;
        a[i * 6 + 3] = x + 0.08; a[i * 6 + 4] = y - 0.9; a[i * 6 + 5] = z;
      }
      this.rain.geometry.attributes.position.needsUpdate = true;
    }
    const flaky = { snow: [0xffffff, 1.6, 0.12], ash: [0x8a837b, 1.0, 0.16], dust: [0xc49a68, 0.6, 0.08] }[w];
    this.flakes.visible = !!flaky;
    if (flaky) {
      const a = this.flakes.geometry.attributes.position.array;
      for (let i = 0; i < N; i++) {
        a[i * 3] = cam.x + ((rnd(i) - 0.5) * 50 + Math.sin(t * 0.7 + i) * 0.8);
        a[i * 3 + 1] = cam.y + 15 - ((t * flaky[1] + rnd(i + 3) * 30) % 30);
        a[i * 3 + 2] = cam.z + (rnd(i + 9) - 0.5) * 50 + (w === "dust" ? ((t * 6 + rnd(i) * 50) % 50) - 25 : 0);
      }
      this.flakes.geometry.attributes.position.needsUpdate = true;
      this.flakes.material.color.setHex(flaky[0]);
      this.flakes.material.size = flaky[2];
    }
    this.meteors.visible = spec.sky === "meteors";
    if (this.meteors.visible) {
      const a = this.meteors.geometry.attributes.position.array;
      for (let i = 0; i < this.M; i++) {
        const life = 1.4 + rnd(i) * 1.2;
        const k = ((t + rnd(i + 5) * 10) % life) / life;
        const sx = cam.x + (rnd(i + 1) - 0.3) * 600, sy = cam.y + 180 + rnd(i + 2) * 200, sz = cam.z - 400 - rnd(i + 4) * 300;
        const dx = -260, dy = -320;
        const x = sx + dx * k, y = sy + dy * k;
        a[i * 6] = x; a[i * 6 + 1] = y; a[i * 6 + 2] = sz;
        a[i * 6 + 3] = x - dx * 0.12; a[i * 6 + 4] = y - dy * 0.12; a[i * 6 + 5] = sz;
      }
      this.meteors.geometry.attributes.position.needsUpdate = true;
    }
    this.nightStars.visible = outdoor && starsLevel > 0;
    this.nightStars.material.opacity = starsLevel;
    this.nightStars.position.copy(cam);
  }
}

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
    this.atmo = new Atmosphere(scene);
    this.spec = {};
    this.exposure = 1.0;
  }
  use(name, spec = {}) {
    const key = `custom:${JSON.stringify(spec.set || {})}`;
    this.spec = spec;
    if (this.active === key) return this.envs[key];
    if (this.active) this.scene.remove(this.envs[this.active].root);
    if (!this.envs[key]) this.envs[key] = setEnv(spec.set || EMPTY_SET);
    const env = this.envs[key];
    this.scene.add(env.root);
    this.scene.fog = env.fog;
    this.scene.background = env.background !== undefined ? new THREE.Color(env.background) : null;
    this.active = key;
    return env;
  }
  update(fr, subjPos, scale = 1, beat = null, camPos = null) {
    const env = this.envs[this.active];
    const spec = this.spec || {};
    const cam = camPos || subjPos;
    env.update(fr, subjPos, beat, cam);
    const L = env.light;
    this.sun.color.set(0xffffff);
    this.sun.intensity = L.sun;
    this.hemi.intensity = L.hemi;
    this.hemi.color.set(L.sky);
    this.hemi.groundColor.set(L.ground);
    this.sunDir = new THREE.Vector3(...L.sunDir).normalize();
    if (this.scene.fog !== env.fog) this.scene.fog = env.fog;
    const cv = Array.isArray(spec.cover) ? spec.cover[0] + (spec.cover[1] - spec.cover[0]) * (fr.frac || 0) : (spec.cover || 0);
    if (cv > 0) env.root.traverse((o) => { if (o.isMesh) (Array.isArray(o.material) ? o.material : [o.material]).forEach((m) => coverMaterial(m)); });
    COVER.amount.value = cv;
    COVER.color.value.set(spec.weather === "ash" ? 0x77716a : 0xf4f7fb);
    this.atmo.update(spec, fr, cam, (spec.weather || "clear") !== "clear", 0);
    // 阴影相机跟随主体
    const ext = 30 * Math.max(1, scale);
    const sc = this.sun.shadow.camera;
    sc.left = -ext; sc.right = ext; sc.top = ext; sc.bottom = -ext; sc.near = 1; sc.far = 400 * Math.max(1, scale);
    sc.updateProjectionMatrix();
    this.sun.position.copy(subjPos).addScaledVector(this.sunDir, 150 * Math.max(1, scale));
    this.sun.target.position.copy(subjPos);
  }
  get current() { return this.envs[this.active]; }
}
